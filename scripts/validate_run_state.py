#!/usr/bin/env python3
import argparse, datetime as dt, fcntl, json, math, os, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from workflow_common import canonical_digest, compare_value, json_field, load_json, resolve_under, sha256_file, atomic_json_write
from snapshot_code_state import snapshot, verify_snapshot_dir

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS={
 'state':'run-state.schema.json','contract':'development-contract.schema.json','policy':'snapshot-policy.schema.json','plan':'test-plan.schema.json','receipt':'test-receipt.schema.json','results':'test-results.schema.json'
}
ALLOWED={
 'CONTRACT':{'IMPLEMENT','BLOCKED'},'IMPLEMENT':{'CODE_REVIEW','BLOCKED'},'CODE_REVIEW':{'IMPLEMENT_REWORK','TEST_PLAN','BLOCKED'},'IMPLEMENT_REWORK':{'CODE_REVIEW','BLOCKED'},'TEST_PLAN':{'TEST','BLOCKED'},'TEST':{'BLOCKED'},'TEST_REWORK':{'CODE_REVIEW','BLOCKED'},'BLOCKED':set(),'COMPLETE':set(),
}

class Reject(Exception):
    def __init__(self,code,message): super().__init__(message); self.code=code; self.message=message

def reject(code,message): raise Reject(code,message)

def validate(kind,obj):
    schema=load_json(ROOT/'schemas'/SCHEMAS[kind]); errors=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(obj),key=lambda e:list(e.path))
    if errors:
        e=errors[0]; loc='.'.join(str(x) for x in e.absolute_path) or '<root>'; reject('SCHEMA_INVALID',f'{kind}:{loc}:{e.message}')

def parse_time(v):
    try: return dt.datetime.fromisoformat(v.replace('Z','+00:00'))
    except Exception: reject('TIME_INVALID',f'invalid timestamp: {v}')

def read_identity(state,contract_path,policy_path,plan_path=None,results_path=None):
    contract=load_json(contract_path); policy=load_json(policy_path); validate('contract',contract); validate('policy',policy); cd=canonical_digest(contract); pold=canonical_digest(policy)
    if state['contract_id']!=contract['contract_id'] or state['contract_revision']!=contract['revision']: reject('CONTRACT_IDENTITY_MISMATCH','Contract id/revision mismatch')
    if state['contract_digest']!=cd: reject('CONTRACT_DIGEST_MISMATCH','same revision has different Contract content or Run State is stale')
    if state['snapshot_policy']['digest']!=pold: reject('POLICY_DIGEST_MISMATCH','snapshot policy content differs from Run State binding')
    plan=results=None; pd=None
    if plan_path:
        plan=load_json(plan_path); validate('plan',plan); pd=canonical_digest(plan)
        for k,v in (('task_id',state['task_id']),('contract_id',state['contract_id']),('contract_revision',state['contract_revision']),('contract_digest',cd),('policy_digest',pold)):
            if plan[k]!=v: reject('PLAN_IDENTITY_MISMATCH',f'Test Plan {k} mismatch')
    if results_path:
        results=load_json(results_path); validate('results',results)
        if not plan: reject('PLAN_REQUIRED','results validation requires plan')
        for k,v in (('task_id',state['task_id']),('contract_id',state['contract_id']),('contract_revision',state['contract_revision']),('contract_digest',cd),('policy_digest',pold),('plan_id',plan['plan_id']),('plan_revision',plan['plan_revision']),('plan_digest',pd)):
            if results[k]!=v: reject('RESULTS_IDENTITY_MISMATCH',f'test results {k} mismatch')
    return contract,policy,cd,pold,plan,pd,results

def verify_repo(state):
    work=Path(state['working_directory']).resolve(); repo=Path(state['repo_root']).resolve()
    if not work.exists(): reject('WORKDIR_MISSING','working directory missing')
    import subprocess
    p=subprocess.run(['git','-C',str(work),'rev-parse','--show-toplevel'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if p.returncode or Path(p.stdout.strip()).resolve()!=repo: reject('REPO_IDENTITY_MISMATCH','working directory no longer matches repo_root')
    return repo,work

def current_manifest(state):
    repo,work=verify_repo(state); policy_path=state['snapshot_policy']['path']; git_tmp=os.path.join(repo,'.git','agy-supervised','tmp'); Path(git_tmp).mkdir(parents=True,exist_ok=True)
    import tempfile, shutil
    td=tempfile.mkdtemp(prefix='validate.',dir=git_tmp); out=Path(td)/'snapshot'
    try: return snapshot(out,state['baseline']['commit'],policy_path,work)
    except Exception as e: reject('CURRENT_SNAPSHOT_FAILED',str(e))
    finally: shutil.rmtree(td,ignore_errors=True)

def verify_baseline(state):
    try: manifest=verify_snapshot_dir(state['baseline']['snapshot_ref'])
    except Exception as e: reject('BASELINE_INVALID',str(e))
    for key in ('deliverable_digest','ownership_digest','policy_digest'):
        if manifest[key]!=state['baseline'][key]: reject('BASELINE_BINDING_MISMATCH',f'baseline {key} mismatch')
    return manifest

def scenario_coverage(contract,plan):
    required={x['id'] for x in contract['acceptance_scenarios']+contract['counterexamples'] if x['required']}; all_ids={x['id'] for x in contract['acceptance_scenarios']+contract['counterexamples']}; covered=set()
    for c in plan['checks']: covered.update(c['covers'])
    if not plan['checks'] and plan['no_checks_acceptance']: covered.update(plan['no_checks_acceptance']['covers'])
    unknown=covered-all_ids
    if unknown: reject('UNKNOWN_SCENARIO_COVERAGE','plan covers unknown scenario ids: '+','.join(sorted(unknown)))
    missing=required-covered
    if missing: reject('SCENARIO_COVERAGE_MISSING','required scenarios not mapped: '+','.join(sorted(missing)))

def validate_test_entry(state,contract,policy,cd,pold,plan,pd,manifest):
    if state['writer']['status']!='STOPPED': reject('WRITER_NOT_STOPPED','writer must be STOPPED before TEST entry')
    if state['dispatch_state'] not in ('SETTLED','NOT_SENT'): reject('DISPATCH_UNSETTLED','dispatch must be SETTLED/NOT_SENT before TEST entry')
    r=state['code_review']
    if r['status']!='PASS': reject('REVIEW_NOT_PASS','current Contract lacks PASS code review')
    if r['contract_revision']!=state['contract_revision'] or r['contract_digest']!=cd: reject('REVIEW_CONTRACT_STALE','review Contract binding is stale')
    if r['reviewed_deliverable_digest']!=manifest['deliverable_digest']: reject('REVIEW_DIGEST_STALE','code review digest is stale')
    tp=state['test_plan']
    if tp['status']!='FROZEN' or tp['plan_id']!=plan['plan_id'] or tp['plan_revision']!=plan['plan_revision'] or tp['plan_digest']!=pd: reject('PLAN_BINDING_STALE','frozen Test Plan binding mismatch')
    if tp['contract_digest']!=cd or tp['policy_digest']!=pold or tp['reviewed_deliverable_digest']!=manifest['deliverable_digest']: reject('PLAN_BINDING_STALE','frozen Test Plan input binding stale')
    if plan['reviewed_deliverable_digest']!=manifest['deliverable_digest']: reject('PLAN_REVIEW_DIGEST_STALE','Test Plan reviewed digest is stale')
    scenario_coverage(contract,plan)

def receipt_path(evidence_root,ref):
    try: return resolve_under(evidence_root,ref,True)
    except Exception as e: reject('EVIDENCE_PATH_INVALID',str(e))

def read_fact(repo,spec):
    p=resolve_under(repo,spec['path'],True); obj=load_json(p)
    try: v=json_field(obj,spec['json_path'])
    except Exception: reject('FACT_FIELD_MISSING',f'{spec["path"]}:{spec["json_path"]}')
    kind=spec['value_type']
    if kind=='boolean' and type(v) is not bool: reject('FACT_TYPE_MISMATCH','expected boolean')
    if kind=='integer' and type(v) is not int: reject('FACT_TYPE_MISMATCH','expected integer')
    if kind=='number' and (isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v)): reject('FACT_TYPE_MISMATCH','expected finite number')
    if kind=='string' and not isinstance(v,str): reject('FACT_TYPE_MISMATCH','expected string')
    return v

def check_plan_receipt(plan_check,receipt,repo,current_digest,receipt_dir):
    if receipt['check_id']!=plan_check['id']: reject('RECEIPT_CHECK_MISMATCH','receipt check_id mismatch')
    if parse_time(receipt['ended_at']) < parse_time(receipt['started_at']): reject('TIME_ORDER_INVALID','receipt ended_at precedes started_at')
    if receipt['deliverable_digest_before']!=current_digest or receipt['deliverable_digest_after']!=current_digest: reject('RECEIPT_DIGEST_STALE','receipt does not bind current deliverable')
    types=set()
    for ev in receipt['evidence']:
        p=resolve_under(receipt_dir,ev['path'],True)
        if sha256_file(p)!=ev['sha256']: reject('EVIDENCE_HASH_MISMATCH',ev['path'])
        types.add(ev['type'])
    applicable=True; app=plan_check['applicability']
    if app['mode']=='fact_eq':
        actual=read_fact(repo,app['source']); applicable=(type(actual) is type(app['expected']) and actual==app['expected'])
        if receipt['applicability'].get('actual')!=actual or receipt['applicability'].get('applicable')!=applicable: reject('APPLICABILITY_EVIDENCE_CONTRADICTION','receipt applicability contradicts source fact')
    if not applicable:
        if receipt['status']!='NOT_APPLICABLE': reject('N_A_STATUS_MISMATCH','business-inapplicable check must be NOT_APPLICABLE')
        if 'applicability' not in types: reject('EVIDENCE_TYPE_MISSING','NOT_APPLICABLE requires applicability evidence')
        return 'NOT_APPLICABLE',{}
    if receipt['status']=='NOT_APPLICABLE': reject('INVALID_NOT_APPLICABLE','applicable check cannot be NOT_APPLICABLE')
    env_map={x['id']:x for x in receipt['environment']}
    for pre in plan_check['environment_prerequisites']:
        actual=read_fact(repo,pre['source']); ok=compare_value(actual,pre['op'],pre['expected']); row=env_map.get(pre['id'])
        if not row or row.get('actual')!=actual or row.get('satisfied')!=ok: reject('ENVIRONMENT_EVIDENCE_CONTRADICTION',pre['id'])
        if not ok:
            if receipt['status']!='BLOCKED': reject('ENVIRONMENT_NOT_BLOCKED',pre['id'])
            return 'BLOCKED',{}
    missing=set(plan_check['evidence_types'])-types
    if missing and receipt['status']!='BLOCKED': reject('EVIDENCE_TYPE_MISSING','missing evidence types: '+','.join(sorted(missing)))
    measured={}
    if plan_check['type']=='command':
        expected_spec=plan_check['command']['argv']; actual=receipt['actual_argv'] or []
        if len(actual)!=len(expected_spec): reject('ARGV_MISMATCH','receipt argv length differs from frozen plan')
        for spec_token,actual_token in zip(expected_spec,actual):
            spec_token=spec_token.replace('{repo_root}',str(repo))
            if '{attempt_dir}' in spec_token:
                pre,post=spec_token.split('{attempt_dir}',1); allowed_prefix=pre+str(receipt_dir.parent)+os.sep
                if not actual_token.startswith(allowed_prefix) or not actual_token.endswith(post): reject('ARGV_MISMATCH','receipt argv differs from frozen plan')
            elif actual_token!=spec_token: reject('ARGV_MISMATCH','receipt argv differs from frozen plan')
        if receipt['timed_out'] and receipt['status']!='FAIL': reject('TIMEOUT_STATUS_MISMATCH','timeout must fail')
        if not receipt['timed_out'] and receipt['status']=='PASS' and receipt['exit_code'] not in plan_check['command']['expected_exit_codes']: reject('EXIT_CODE_MISMATCH','PASS exit code not accepted by plan')
        reports=[x for x in receipt['evidence'] if x['type']=='structured_report']
        for spec in plan_check.get('structured_reports',[]):
            candidates=[x for x in reports if Path(x['path']).name.endswith(Path(spec['path']).name)]
            if not candidates: reject('STRUCTURED_REPORT_MISSING',spec['id'])
            obj=load_json(resolve_under(receipt_dir,candidates[-1]['path'],True))
            for field in spec['fields']:
                try: val=json_field(obj,field['json_path'])
                except Exception: reject('REPORT_FIELD_MISSING',field['json_path'])
                kind=field['value_type']
                if kind=='boolean' and type(val) is not bool: reject('REPORT_TYPE_MISMATCH',field['name'])
                if kind=='integer' and type(val) is not int: reject('REPORT_TYPE_MISMATCH',field['name'])
                if kind=='number' and (isinstance(val,bool) or not isinstance(val,(int,float)) or not math.isfinite(val)): reject('REPORT_TYPE_MISMATCH',field['name'])
                if kind=='string' and not isinstance(val,str): reject('REPORT_TYPE_MISMATCH',field['name'])
                measured[f'{spec["id"]}.{field["name"]}']={'value':val,'unit':field.get('unit')}
        if measured!=receipt['measured_values']: reject('MEASURED_VALUES_MISMATCH','receipt metrics do not match structured report')
    else:
        actual=read_fact(repo,plan_check['observation']['source']); ok=compare_value(actual,plan_check['observation']['op'],plan_check['observation']['expected'])
        if receipt['status']=='PASS' and not ok: reject('OBSERVATION_MISMATCH','observation PASS contradicts structured source')
        measured={'observation.value':{'value':actual,'unit':None}}
    return receipt['status'],measured

def validate_results(state,contract,policy,cd,pold,plan,pd,results,current_digest):
    repo,_=verify_repo(state); checks={c['id']:c for c in plan['checks']}; grouped={k:[] for k in checks}
    for ref in results['attempts']:
        if ref['check_id'] not in checks: reject('UNKNOWN_RESULT_CHECK',ref['check_id'])
        rp=receipt_path(state['evidence_root'],ref['receipt_path'])
        if sha256_file(rp)!=ref['receipt_sha256']: reject('RECEIPT_HASH_MISMATCH',ref['receipt_path'])
        receipt=load_json(rp); validate('receipt',receipt)
        for k,v in (('task_id',state['task_id']),('contract_id',state['contract_id']),('contract_revision',state['contract_revision']),('contract_digest',cd),('policy_digest',pold),('plan_id',plan['plan_id']),('plan_revision',plan['plan_revision']),('plan_digest',pd),('check_id',ref['check_id']),('attempt_id',ref['attempt_id']),('attempt_number',ref['attempt_number'])):
            if receipt[k]!=v: reject('RECEIPT_IDENTITY_MISMATCH',f'{ref["attempt_id"]}:{k}')
        grouped[ref['check_id']].append((ref,receipt,rp.parent))
    latest={}
    for cid,check in checks.items():
        rows=grouped[cid]
        if not rows: reject('RESULT_MISSING',cid)
        nums=[r[0]['attempt_number'] for r in rows]
        if len(nums)!=len(set(nums)): reject('ATTEMPT_DUPLICATE',cid)
        if sorted(nums)!=list(range(1,max(nums)+1)): reject('ATTEMPT_SEQUENCE_INVALID',cid)
        if max(nums)>check['max_attempts']: reject('MAX_ATTEMPTS_EXCEEDED',cid)
        validated=[]
        for ref,receipt,rdir in sorted(rows,key=lambda x:x[0]['attempt_number']): validated.append((receipt,*check_plan_receipt(check,receipt,repo,current_digest,rdir)))
        latest[cid]=validated[-1]; status=validated[-1][1]
        if check['required'] and status not in ('PASS','NOT_APPLICABLE'): reject('REQUIRED_CHECK_NOT_PASS',f'{cid}:{status}')
    for metric in plan['metrics']:
        if metric['source_check_id'] not in latest: reject('METRIC_SOURCE_UNKNOWN',metric['id'])
        receipt,status,measured=latest[metric['source_check_id']]
        if status=='NOT_APPLICABLE': continue
        if status!='PASS':
            if metric['required']: reject('REQUIRED_METRIC_SOURCE_NOT_PASS',metric['id'])
            continue
        if metric['result_field'] not in measured: reject('METRIC_FIELD_MISSING',metric['id'])
        raw=measured[metric['result_field']]; value=raw['value']
        if raw.get('unit')!=metric['unit']: reject('METRIC_UNIT_MISMATCH',metric['id'])
        kind=metric['value_type']
        if kind=='boolean' and type(value) is not bool: reject('METRIC_TYPE_MISMATCH',metric['id'])
        if kind=='integer' and type(value) is not int: reject('METRIC_TYPE_MISMATCH',metric['id'])
        if kind=='number' and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value)): reject('METRIC_TYPE_MISMATCH',metric['id'])
        if kind=='string' and not isinstance(value,str): reject('METRIC_TYPE_MISMATCH',metric['id'])
        ok=compare_value(value,metric['op'],metric['threshold'])
        if metric['required'] and not ok: reject('METRIC_THRESHOLD_FAILED',metric['id'])
    if not plan['checks']:
        if results['attempts']: reject('NO_CHECK_RESULTS_FORBIDDEN','no-check plan cannot contain attempts')
        rec=plan['no_checks_acceptance']
        if not rec: reject('NO_CHECK_ACCEPTANCE_MISSING','empty plan lacks frozen acceptance evidence')
        ep=receipt_path(state['evidence_root'],rec['evidence_path'])
        if sha256_file(ep)!=rec['evidence_sha256']: reject('NO_CHECK_EVIDENCE_HASH_MISMATCH',rec['evidence_path'])

def load_state_locked(path,expected=None):
    state=load_json(path); validate('state',state)
    if expected is not None and state['state_version']!=expected: reject('STATE_VERSION_CONFLICT',f'expected {expected}, found {state["state_version"]}')
    return state

def commit_state(path,state,expected):
    if state['state_version']!=expected: reject('STATE_VERSION_CONFLICT','state changed before commit')
    state['state_version']=expected+1; atomic_json_write(path,state)

def with_lock(state_path):
    lock=Path(str(state_path)+'.workflow.lock'); lock.parent.mkdir(parents=True,exist_ok=True); return open(lock,'a+')

def ensure_mutable(state):
    if state['phase']=='COMPLETE': reject('COMPLETE_TERMINAL','COMPLETE is terminal; start a new run to reopen')

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    common=lambda p:(p.add_argument('--run-state',required=True),p.add_argument('--contract',required=True),p.add_argument('--policy',required=True),p.add_argument('--expected-state-version',type=int,required=True))
    p=sub.add_parser('validate'); p.add_argument('--run-state',required=True); p.add_argument('--contract',required=True); p.add_argument('--policy',required=True)
    p=sub.add_parser('transition'); common(p); p.add_argument('--to',required=True); p.add_argument('--test-plan')
    p=sub.add_parser('review-pass'); common(p); p.add_argument('--review-id',required=True)
    p=sub.add_parser('freeze-plan'); common(p); p.add_argument('--test-plan',required=True)
    p=sub.add_parser('invalidate'); common(p); p.add_argument('--reason',required=True)
    p=sub.add_parser('block'); common(p); p.add_argument('--reason-code',required=True); p.add_argument('--reason',required=True); p.add_argument('--resume-action',required=True)
    p=sub.add_parser('resume'); common(p)
    p=sub.add_parser('writer'); common(p); p.add_argument('--status',choices=['STOPPED','RUNNING','UNKNOWN'],required=True); p.add_argument('--task-round')
    p=sub.add_parser('dispatch'); common(p); p.add_argument('--state',choices=['NOT_SENT','SENT','SEND_UNKNOWN','SETTLED'],required=True)
    p=sub.add_parser('finding-resolve'); common(p); p.add_argument('--finding-id',required=True)
    p=sub.add_parser('contract-update'); p.add_argument('--run-state',required=True); p.add_argument('--contract',required=True); p.add_argument('--policy',required=True); p.add_argument('--expected-state-version',type=int,required=True); p.add_argument('--reason',required=True)
    p=sub.add_parser('complete'); common(p); p.add_argument('--test-plan',required=True); p.add_argument('--results',required=True)
    args=ap.parse_args(); state_path=Path(args.run_state).resolve()
    try:
        if args.cmd=='validate':
            state=load_json(state_path); validate('state',state); read_identity(state,args.contract,args.policy); verify_baseline(state); print('RUN_STATE_VALID'); return 0
        with with_lock(state_path) as lf:
            fcntl.flock(lf,fcntl.LOCK_EX); state=load_state_locked(state_path,args.expected_state_version); ensure_mutable(state); expected=state['state_version']
            if args.cmd=='contract-update':
                contract=load_json(args.contract); policy=load_json(args.policy); validate('contract',contract); validate('policy',policy); cd=canonical_digest(contract); pold=canonical_digest(policy); plan=pd=results=None
                if state['snapshot_policy']['digest']!=pold: reject('POLICY_DIGEST_MISMATCH','policy must not change implicitly with Contract patch')
                if contract['contract_id']!=state['contract_id'] or contract['revision']<=state['contract_revision']: reject('CONTRACT_REVISION_INVALID','Contract update must keep id and increment revision')
            else:
                contract,policy,cd,pold,plan,pd,results=read_identity(state,args.contract,args.policy,getattr(args,'test_plan',None),getattr(args,'results',None))
            verify_baseline(state)
            if args.cmd=='review-pass':
                if state['phase']!='CODE_REVIEW': reject('ILLEGAL_TRANSITION','review-pass requires CODE_REVIEW')
                if state['writer']['status']!='STOPPED' or state['dispatch_state'] not in ('SETTLED','NOT_SENT'): reject('WRITER_OR_DISPATCH_UNSETTLED','review-pass requires stopped writer and settled dispatch')
                m=current_manifest(state); state['code_review']={'status':'PASS','review_id':args.review_id,'contract_revision':state['contract_revision'],'contract_digest':cd,'reviewed_deliverable_digest':m['deliverable_digest'],'finding_ids':[]}; state['phase']='TEST_PLAN'
            elif args.cmd=='freeze-plan':
                if state['phase']!='TEST_PLAN': reject('ILLEGAL_TRANSITION','freeze-plan requires TEST_PLAN')
                m=current_manifest(state); scenario_coverage(contract,plan)
                if plan['reviewed_deliverable_digest']!=m['deliverable_digest'] or plan['contract_digest']!=cd or plan['policy_digest']!=pold: reject('PLAN_BINDING_STALE','plan does not bind current reviewed state')
                if state['code_review']['status']!='PASS' or state['code_review']['reviewed_deliverable_digest']!=m['deliverable_digest']: reject('REVIEW_DIGEST_STALE','review not valid for current deliverable')
                state['test_plan']={'status':'FROZEN','path':str(Path(args.test_plan).resolve()),'plan_id':plan['plan_id'],'plan_revision':plan['plan_revision'],'plan_digest':pd,'contract_revision':state['contract_revision'],'contract_digest':cd,'policy_digest':pold,'reviewed_deliverable_digest':m['deliverable_digest']}
            elif args.cmd=='transition':
                if args.to=='TEST_REWORK': reject('INVALIDATE_REQUIRED','TEST_REWORK requires invalidate command')
                if state['phase']=='BLOCKED': reject('RESUME_REQUIRED','BLOCKED may only leave through resume')
                if args.to not in ALLOWED[state['phase']]: reject('ILLEGAL_TRANSITION',f'{state["phase"]}->{args.to}')
                if args.to=='TEST':
                    if not args.test_plan: reject('PLAN_REQUIRED','TEST transition requires Test Plan')
                    m=current_manifest(state); validate_test_entry(state,contract,policy,cd,pold,plan,pd,m); state['dispatch_state']='NOT_SENT'
                state['phase']=args.to
            elif args.cmd=='invalidate':
                if state['phase']!='TEST': reject('INVALIDATE_SOURCE_INVALID','invalidate allowed only from TEST')
                if state['writer']['status']!='STOPPED': reject('WRITER_NOT_STOPPED','stop worker before invalidate')
                state['phase']='TEST_REWORK'; state['code_review']['status']='STALE'; state['test_plan']['status']='STALE'; state['test_results_path']=None
                state['findings'].append({'id':f'test-rework-{expected}','status':'OPEN','category':'TEST_DEFECT','reason':args.reason}); state['dispatch_state']='NOT_SENT'
            elif args.cmd=='block':
                if state['writer']['status']=='RUNNING': reject('WRITER_RUNNING','cannot persist BLOCKED while writer still running')
                source=state['blocked']['blocked_from_phase'] if state['phase']=='BLOCKED' and state['blocked'] else state['phase']
                state['phase']='BLOCKED'; state['blocked']={'reason_code':args.reason_code,'reason':args.reason,'blocked_from_phase':source,'resume_action':args.resume_action,'related_identity':state['writer'].get('task_round')}
            elif args.cmd=='resume':
                if state['phase']!='BLOCKED' or not state['blocked']: reject('NOT_BLOCKED','resume requires BLOCKED')
                if state['writer']['status']!='STOPPED': reject('WRITER_NOT_STOPPED','resume requires stopped writer')
                if state['dispatch_state'] in ('SENT','SEND_UNKNOWN'): reject('DISPATCH_UNSETTLED','resolve dispatch before resume')
                target=state['blocked']['blocked_from_phase']; current_manifest(state); state['blocked']=None; state['phase']=target
            elif args.cmd=='writer':
                if args.status=='RUNNING' and (state['writer']['status']!='STOPPED' or state['dispatch_state'] in ('SENT','SEND_UNKNOWN')): reject('WRITER_START_UNSAFE','cannot start writer while prior writer/dispatch uncertain')
                state['writer']['status']=args.status; state['writer']['task_round']=args.task_round; state['writer']['last_observed_at']=dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')
            elif args.cmd=='dispatch':
                old=state['dispatch_state']; new=args.state; valid={('NOT_SENT','SENT'),('SENT','SETTLED'),('SENT','SEND_UNKNOWN'),('SEND_UNKNOWN','SETTLED'),('SETTLED','NOT_SENT')}
                if old!=new and (old,new) not in valid: reject('DISPATCH_TRANSITION_INVALID',f'{old}->{new}')
                state['dispatch_state']=new
            elif args.cmd=='finding-resolve':
                match=[x for x in state['findings'] if x['id']==args.finding_id]
                if not match: reject('FINDING_NOT_FOUND',args.finding_id)
                match[0]['status']='RESOLVED'
            elif args.cmd=='contract-update':
                oldrev=state['contract_revision']; state['contract_revision']=contract['revision']; state['contract_digest']=cd; state['contract_patches'].append({'from_revision':oldrev,'to_revision':contract['revision'],'reason':args.reason})
                if state['code_review']['status']!='NOT_RUN': state['code_review']['status']='STALE'
                if state['test_plan']['status']!='NOT_CREATED': state['test_plan']['status']='STALE'
                state['test_results_path']=None
                if state['phase'] not in ('CONTRACT','IMPLEMENT'): state['phase']='IMPLEMENT_REWORK'
                state['findings'].append({'id':f'contract-patch-{contract["revision"]}','status':'OPEN','category':'CONTRACT_PATCH','reason':args.reason}); state['dispatch_state']='NOT_SENT'
            elif args.cmd=='complete':
                if state['phase']!='TEST': reject('COMPLETE_SOURCE_INVALID','COMPLETE only from TEST')
                if state['writer']['status']!='STOPPED': reject('WRITER_NOT_STOPPED','writer must be stopped before COMPLETE')
                if state['dispatch_state']!='SETTLED': reject('DISPATCH_UNSETTLED','dispatch must be SETTLED before COMPLETE')
                if state['blocked'] is not None: reject('BLOCKED_UNRESOLVED','blocked state remains')
                if any(x['status']=='OPEN' for x in state['findings']): reject('OPEN_FINDINGS','open findings remain')
                m=current_manifest(state); validate_test_entry(state,contract,policy,cd,pold,plan,pd,m); validate_results(state,contract,policy,cd,pold,plan,pd,results,m['deliverable_digest'])
                if canonical_digest(load_json(args.contract))!=cd or canonical_digest(load_json(args.policy))!=pold or canonical_digest(load_json(args.test_plan))!=pd or canonical_digest(load_json(args.results))!=canonical_digest(results): reject('ARTIFACT_CHANGED_DURING_VALIDATION','identity artifact changed during validation')
                state['phase']='COMPLETE'
            commit_state(state_path,state,expected); print(json.dumps({'decision':'OK','phase':state['phase'],'state_version':state['state_version']},sort_keys=True)); return 0
    except Reject as e:
        print(json.dumps({'decision':'REJECTED','reason_code':e.code,'reason':e.message},sort_keys=True),file=sys.stderr); return 1
    except Exception as e:
        print(json.dumps({'decision':'REJECTED','reason_code':'UNEXPECTED_ERROR','reason':str(e)},sort_keys=True),file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
