#!/usr/bin/env python3
import argparse, base64, datetime as dt, fcntl, json, os, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from workflow_common import canonical_digest, load_json, resolve_under, sha256_file, atomic_json_write
from snapshot_code_state import snapshot, verify_snapshot_dir

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS={
    'state':'run-state.schema.json',
    'contract':'development-contract.schema.json',
    'policy':'snapshot-policy.schema.json',
    'plan':'test-plan.schema.json',
    'results':'test-results.schema.json',
}
ALLOWED={
    'CONTRACT':{'IMPLEMENT','BLOCKED'},
    'IMPLEMENT':{'CODE_REVIEW','BLOCKED'},
    'CODE_REVIEW':{'IMPLEMENT_REWORK','TEST_PLAN','BLOCKED'},
    'IMPLEMENT_REWORK':{'CODE_REVIEW','BLOCKED'},
    'TEST_PLAN':{'TEST','BLOCKED'},
    'TEST':{'BLOCKED'},
    'TEST_REWORK':{'CODE_REVIEW','BLOCKED'},
    'BLOCKED':set(),
    'COMPLETE':set(),
}

class Reject(Exception):
    def __init__(self,code,message):
        super().__init__(message); self.code=code; self.message=message

def reject(code,message):
    raise Reject(code,message)

def validate(kind,obj):
    schema=load_json(ROOT/'schemas'/SCHEMAS[kind])
    errors=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(obj),key=lambda e:list(e.path))
    if errors:
        e=errors[0]; loc='.'.join(str(x) for x in e.absolute_path) or '<root>'
        reject('SCHEMA_INVALID',f'{kind}:{loc}:{e.message}')

def parse_time(value):
    try:
        return dt.datetime.fromisoformat(value.replace('Z','+00:00'))
    except Exception:
        reject('TIME_INVALID',f'invalid timestamp: {value}')

def require_runtime_version(kind,obj,expected):
    if obj.get('schema_version')!=expected:
        reject('MIGRATION_REQUIRED',f'{kind} schema_version={obj.get("schema_version")} is incompatible; rebuild the current run evidence for schema {expected}')

def read_identity(state,contract_path,policy_path,plan_path=None,results_path=None):
    contract=load_json(contract_path); policy=load_json(policy_path)
    validate('contract',contract); validate('policy',policy)
    cd=canonical_digest(contract); policy_digest=canonical_digest(policy)
    if state['contract_id']!=contract['contract_id'] or state['contract_revision']!=contract['revision']:
        reject('CONTRACT_IDENTITY_MISMATCH','Contract id/revision mismatch')
    if state['contract_digest']!=cd:
        reject('CONTRACT_DIGEST_MISMATCH','Contract content changed without a matching current Run State binding')
    if state['snapshot_policy']['digest']!=policy_digest:
        reject('POLICY_DIGEST_MISMATCH','snapshot policy content differs from Run State binding')
    if state['baseline']['policy_digest']!=policy_digest:
        reject('BASELINE_POLICY_STALE','baseline was captured with a different snapshot policy; rebuild the current run baseline')

    plan=results=None; plan_digest=None
    if plan_path:
        plan=load_json(plan_path); require_runtime_version('Test Plan',plan,3); validate('plan',plan); plan_digest=canonical_digest(plan)
        for key,value in (
            ('task_id',state['task_id']),('contract_id',state['contract_id']),('contract_revision',state['contract_revision']),
            ('contract_digest',cd),('policy_digest',policy_digest)):
            if plan[key]!=value: reject('PLAN_IDENTITY_MISMATCH',f'Test Plan {key} mismatch')
    if results_path:
        results=load_json(results_path); require_runtime_version('Test Results',results,3); validate('results',results)
        if plan is None: reject('PLAN_REQUIRED','results validation requires Test Plan')
        for key,value in (
            ('task_id',state['task_id']),('contract_id',state['contract_id']),('contract_revision',state['contract_revision']),
            ('contract_digest',cd),('policy_digest',policy_digest),('plan_id',plan['plan_id']),
            ('plan_revision',plan['plan_revision']),('plan_digest',plan_digest)):
            if results[key]!=value: reject('RESULTS_IDENTITY_MISMATCH',f'Test Results {key} mismatch')
    return contract,policy,cd,policy_digest,plan,plan_digest,results

def verify_repo(state):
    work=Path(state['working_directory']).resolve(); repo=Path(state['repo_root']).resolve()
    if not work.exists(): reject('WORKDIR_MISSING','working directory missing')
    import subprocess
    p=subprocess.run(['git','-C',str(work),'rev-parse','--show-toplevel'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if p.returncode or Path(p.stdout.strip()).resolve()!=repo:
        reject('REPO_IDENTITY_MISMATCH','working directory no longer matches repo_root')
    return repo,work

def current_manifest(state):
    repo,work=verify_repo(state)
    git_tmp=repo/'.git'/'agy-supervised'/'tmp'; git_tmp.mkdir(parents=True,exist_ok=True)
    import tempfile, shutil
    td=tempfile.mkdtemp(prefix='validate.',dir=git_tmp); out=Path(td)/'snapshot'
    try:
        return snapshot(out,state['baseline']['commit'],state['snapshot_policy']['path'],work)
    except Exception as e:
        reject('CURRENT_SNAPSHOT_FAILED',str(e))
    finally:
        shutil.rmtree(td,ignore_errors=True)

def verify_baseline(state):
    try:
        manifest=verify_snapshot_dir(state['baseline']['snapshot_ref'])
    except Exception as e:
        reject('BASELINE_INVALID',str(e))
    for key in ('deliverable_digest','ownership_digest','policy_digest'):
        if manifest[key]!=state['baseline'][key]:
            reject('BASELINE_BINDING_MISMATCH',f'baseline {key} mismatch')
    return manifest

def validate_review_current(state,contract_digest,manifest):
    review=state['code_review']
    if review['status']!='PASS': reject('REVIEW_NOT_PASS','current Contract lacks PASS code review')
    if review['contract_revision']!=state['contract_revision'] or review['contract_digest']!=contract_digest:
        reject('REVIEW_CONTRACT_STALE','review Contract binding is stale')
    if review['reviewed_deliverable_digest']!=manifest['deliverable_digest']:
        reject('REVIEW_DIGEST_STALE','code review digest is stale')

def validate_plan_shape(plan):
    ids=[check['id'] for check in plan['checks']]
    if len(ids)!=len(set(ids)): reject('PLAN_CHECK_DUPLICATE','Test Plan check ids must be unique')
    if plan['checks'] and plan['no_checks_acceptance'] is not None:
        reject('PLAN_CONTRADICTION','no_checks_acceptance is only valid when checks is empty')
    if not plan['checks'] and plan['no_checks_acceptance'] is None and not plan.get('manual_confirmation_required'):
        reject('NO_CHECK_ACCEPTANCE_REQUIRED','empty Test Plan requires explicit no-check acceptance evidence unless it is waiting for human confirmation')

def validate_plan_inputs(plan,manifest):
    manifest_paths={base64.b64decode(item['path_b64']) for item in manifest['files']}
    for check in plan['checks']:
        for value in check.get('input_paths',[]):
            if os.fsencode(value) not in manifest_paths:
                reject('PLAN_INPUT_MISSING',f'{check["id"]}:{value} is not covered by the frozen snapshot policy/current deliverable')

def validate_test_entry(state,contract_digest,policy_digest,plan,plan_digest,manifest):
    if state['writer']['status']!='STOPPED': reject('WRITER_NOT_STOPPED','writer must be STOPPED before TEST entry')
    if state['dispatch_state'] not in ('SETTLED','NOT_SENT'):
        reject('DISPATCH_UNSETTLED','dispatch must be SETTLED/NOT_SENT before TEST entry')
    validate_review_current(state,contract_digest,manifest)
    validate_plan_shape(plan); validate_plan_inputs(plan,manifest)
    bound=state['test_plan']
    if bound['status']!='FROZEN' or bound['plan_id']!=plan['plan_id'] or bound['plan_revision']!=plan['plan_revision'] or bound['plan_digest']!=plan_digest:
        reject('PLAN_BINDING_STALE','frozen Test Plan binding mismatch')
    if bound['contract_digest']!=contract_digest or bound['policy_digest']!=policy_digest or bound['reviewed_deliverable_digest']!=manifest['deliverable_digest']:
        reject('PLAN_BINDING_STALE','frozen Test Plan input binding stale')
    if plan['reviewed_deliverable_digest']!=manifest['deliverable_digest']:
        reject('PLAN_REVIEW_DIGEST_STALE','Test Plan reviewed digest is stale')

def evidence_path(root,ref):
    try:
        return resolve_under(root,ref,True)
    except Exception as e:
        reject('EVIDENCE_PATH_INVALID',str(e))

def verify_attempt(attempt,check,current_digest,evidence_root,used_evidence):
    if attempt['cwd']!=check['cwd']: reject('CWD_MISMATCH',attempt['attempt_id'])
    if attempt['argv']!=check['argv']: reject('ARGV_MISMATCH',attempt['attempt_id'])
    if parse_time(attempt['ended_at']) < parse_time(attempt['started_at']): reject('TIME_ORDER_INVALID',attempt['attempt_id'])
    if attempt['deliverable_digest_before']!=current_digest or attempt['deliverable_digest_after']!=current_digest:
        reject('RESULT_DIGEST_STALE',attempt['attempt_id'])
    for ref in attempt['evidence']:
        if ref['path'] in used_evidence: reject('EVIDENCE_REUSED_ACROSS_ATTEMPTS',ref['path'])
        path=evidence_path(evidence_root,ref['path'])
        if sha256_file(path)!=ref['sha256']: reject('EVIDENCE_HASH_MISMATCH',ref['path'])
        used_evidence.add(ref['path'])
    if attempt['timed_out'] and attempt['status']=='PASS': reject('TIMEOUT_STATUS_MISMATCH',attempt['attempt_id'])
    if attempt['status']=='PASS':
        if attempt['exit_code'] not in check['expected_exit_codes']:
            reject('EXIT_CODE_MISMATCH',attempt['attempt_id'])
    elif attempt['status']=='FAIL' and not attempt['timed_out'] and attempt['exit_code'] is None:
        reject('EXIT_CODE_MISSING',attempt['attempt_id'])

def validate_no_checks(state,plan,results):
    if results['attempts']:
        reject('UNEXPECTED_ATTEMPTS','no-check plan cannot contain command attempts')
    if plan.get('manual_confirmation_required'):
        reject('MANUAL_CONFIRMATION_REQUIRED','task is waiting for explicit human confirmation')
    record=plan['no_checks_acceptance']
    path=evidence_path(state['evidence_root'],record['evidence_path'])
    if sha256_file(path)!=record['evidence_sha256']:
        reject('NO_CHECK_EVIDENCE_HASH_MISMATCH',record['evidence_path'])

def validate_results(state,plan,results,current_digest):
    validate_plan_shape(plan)
    if plan.get('manual_confirmation_required'):
        reject('MANUAL_CONFIRMATION_REQUIRED','task is waiting for explicit human confirmation')
    if not plan['checks']:
        validate_no_checks(state,plan,results); return

    checks={check['id']:check for check in plan['checks']}
    grouped={key:[] for key in checks}; attempt_ids=set(); used_evidence=set()
    for attempt in results['attempts']:
        cid=attempt['check_id']
        if cid not in checks: reject('UNKNOWN_RESULT_CHECK',cid)
        if attempt['attempt_id'] in attempt_ids: reject('ATTEMPT_ID_DUPLICATE',attempt['attempt_id'])
        attempt_ids.add(attempt['attempt_id']); grouped[cid].append(attempt)

    for cid,check in checks.items():
        rows=grouped[cid]
        if not rows: reject('RESULT_MISSING',cid)
        numbers=[row['attempt_number'] for row in rows]
        if len(numbers)!=len(set(numbers)): reject('ATTEMPT_DUPLICATE',cid)
        if sorted(numbers)!=list(range(1,max(numbers)+1)): reject('ATTEMPT_SEQUENCE_INVALID',cid)
        if max(numbers)>check['max_attempts']: reject('MAX_ATTEMPTS_EXCEEDED',cid)
        ordered=sorted(rows,key=lambda row:row['attempt_number'])
        for attempt in ordered:
            verify_attempt(attempt,check,current_digest,state['evidence_root'],used_evidence)
        latest=ordered[-1]
        if latest['status']!='PASS': reject('CHECK_NOT_PASS',f'{cid}:{latest["status"]}')

def with_lock(state_path):
    lock_path=Path(str(state_path)+'.lock'); lock_path.parent.mkdir(parents=True,exist_ok=True)
    return open(lock_path,'a+')

def load_state_locked(path,expected):
    state=load_json(path)
    require_runtime_version('Run State',state,4); validate('state',state)
    if state['state_version']!=expected:
        reject('STATE_VERSION_CONFLICT',f'expected {expected}, found {state["state_version"]}')
    return state

def ensure_mutable(state):
    if state['phase']=='COMPLETE': reject('COMPLETE_TERMINAL','COMPLETE is terminal; start a new run to reopen work')

def commit_state(path,state,expected):
    state['state_version']=expected+1
    atomic_json_write(path,state)

def apply_test_rework(state,reason,version):
    state['phase']='TEST_REWORK'
    state['code_review']['status']='STALE'
    state['test_plan']['status']='STALE'
    state['test_results_path']=None
    state['dispatch_state']='NOT_SENT'
    state['findings'].append({'id':f'test-rework-{version}','status':'OPEN','category':'TEST_DEFECT','reason':reason})

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    def common(parser):
        parser.add_argument('--run-state',required=True); parser.add_argument('--contract',required=True); parser.add_argument('--policy',required=True); parser.add_argument('--expected-state-version',type=int,required=True)
    p=sub.add_parser('validate'); p.add_argument('--run-state',required=True); p.add_argument('--contract',required=True); p.add_argument('--policy',required=True)
    p=sub.add_parser('transition'); common(p); p.add_argument('--to',required=True); p.add_argument('--test-plan')
    p=sub.add_parser('review-pass'); common(p); p.add_argument('--review-id',required=True)
    p=sub.add_parser('freeze-plan'); common(p); p.add_argument('--test-plan',required=True)
    p=sub.add_parser('invalidate'); common(p); p.add_argument('--reason',required=True)
    p=sub.add_parser('block'); common(p); p.add_argument('--reason-code',required=True); p.add_argument('--reason',required=True); p.add_argument('--resume-action',required=True)
    p=sub.add_parser('resume'); common(p); p.add_argument('--test-plan')
    p=sub.add_parser('writer'); common(p); p.add_argument('--status',choices=['STOPPED','RUNNING','UNKNOWN'],required=True); p.add_argument('--task-round')
    p=sub.add_parser('dispatch'); common(p); p.add_argument('--state',choices=['NOT_SENT','SENT','SEND_UNKNOWN','SETTLED'],required=True)
    p=sub.add_parser('finding-resolve'); common(p); p.add_argument('--finding-id',required=True)
    p=sub.add_parser('contract-update'); common(p); p.add_argument('--reason',required=True)
    p=sub.add_parser('complete'); common(p); p.add_argument('--test-plan',required=True); p.add_argument('--results',required=True)
    args=ap.parse_args(); state_path=Path(args.run_state).resolve()

    try:
        if args.cmd=='validate':
            state=load_json(state_path); require_runtime_version('Run State',state,4); validate('state',state)
            read_identity(state,args.contract,args.policy); verify_baseline(state)
            print('RUN_STATE_VALID'); return 0

        with with_lock(state_path) as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            state=load_state_locked(state_path,args.expected_state_version); ensure_mutable(state); version=state['state_version']

            if args.cmd=='contract-update':
                contract=load_json(args.contract); policy=load_json(args.policy); validate('contract',contract); validate('policy',policy)
                cd=canonical_digest(contract); policy_digest=canonical_digest(policy); plan=plan_digest=results=None
                if state['snapshot_policy']['digest']!=policy_digest:
                    reject('POLICY_DIGEST_MISMATCH','policy must not change implicitly with Contract update')
                if contract['contract_id']!=state['contract_id'] or contract['revision']<=state['contract_revision']:
                    reject('CONTRACT_REVISION_INVALID','Contract update must keep id and increment revision')
            else:
                contract,policy,cd,policy_digest,plan,plan_digest,results=read_identity(
                    state,args.contract,args.policy,getattr(args,'test_plan',None),getattr(args,'results',None))
            verify_baseline(state)

            if args.cmd=='review-pass':
                if state['phase']!='CODE_REVIEW': reject('ILLEGAL_TRANSITION','review-pass requires CODE_REVIEW')
                if state['writer']['status']!='STOPPED' or state['dispatch_state'] not in ('SETTLED','NOT_SENT'):
                    reject('WRITER_OR_DISPATCH_UNSETTLED','review-pass requires stopped writer and settled dispatch')
                manifest=current_manifest(state)
                state['code_review']={'status':'PASS','review_id':args.review_id,'contract_revision':state['contract_revision'],'contract_digest':cd,'reviewed_deliverable_digest':manifest['deliverable_digest'],'finding_ids':[]}
                state['phase']='TEST_PLAN'

            elif args.cmd=='freeze-plan':
                if state['phase']!='TEST_PLAN': reject('ILLEGAL_TRANSITION','freeze-plan requires TEST_PLAN')
                manifest=current_manifest(state); validate_plan_shape(plan); validate_plan_inputs(plan,manifest)
                validate_review_current(state,cd,manifest)
                if plan['reviewed_deliverable_digest']!=manifest['deliverable_digest'] or plan['contract_digest']!=cd or plan['policy_digest']!=policy_digest:
                    reject('PLAN_BINDING_STALE','plan does not bind current reviewed state')
                state['test_plan']={'status':'FROZEN','path':str(Path(args.test_plan).resolve()),'plan_id':plan['plan_id'],'plan_revision':plan['plan_revision'],'plan_digest':plan_digest,'contract_revision':state['contract_revision'],'contract_digest':cd,'policy_digest':policy_digest,'reviewed_deliverable_digest':manifest['deliverable_digest']}

            elif args.cmd=='transition':
                if state['phase']=='BLOCKED': reject('RESUME_REQUIRED','BLOCKED may only leave through resume')
                if args.to not in ALLOWED[state['phase']]: reject('ILLEGAL_TRANSITION',f'{state["phase"]}->{args.to}')
                if args.to=='TEST':
                    if plan is None: reject('PLAN_REQUIRED','TEST transition requires Test Plan')
                    manifest=current_manifest(state); validate_test_entry(state,cd,policy_digest,plan,plan_digest,manifest)
                    state['dispatch_state']='NOT_SENT'
                state['phase']=args.to

            elif args.cmd=='invalidate':
                if state['phase']!='TEST': reject('INVALIDATE_SOURCE_INVALID','invalidate allowed only from TEST')
                if state['writer']['status']!='STOPPED': reject('WRITER_NOT_STOPPED','stop worker before invalidate')
                apply_test_rework(state,args.reason,version)

            elif args.cmd=='block':
                if state['writer']['status']=='RUNNING': reject('WRITER_RUNNING','cannot persist BLOCKED while writer is RUNNING')
                source=state['blocked']['blocked_from_phase'] if state['phase']=='BLOCKED' and state['blocked'] else state['phase']
                state['phase']='BLOCKED'
                state['blocked']={'reason_code':args.reason_code,'reason':args.reason,'blocked_from_phase':source,'resume_action':args.resume_action,'related_identity':state['writer'].get('task_round')}

            elif args.cmd=='resume':
                if state['phase']!='BLOCKED' or not state['blocked']: reject('NOT_BLOCKED','resume requires BLOCKED')
                if state['writer']['status']!='STOPPED': reject('WRITER_NOT_STOPPED','resume requires stopped writer')
                if state['dispatch_state'] in ('SENT','SEND_UNKNOWN'): reject('DISPATCH_UNSETTLED','resolve dispatch before resume')
                target=state['blocked']['blocked_from_phase']; manifest=current_manifest(state)
                if target=='TEST':
                    if plan is None: reject('PLAN_REQUIRED','resuming TEST requires the frozen Test Plan')
                    validate_test_entry(state,cd,policy_digest,plan,plan_digest,manifest)
                elif target=='TEST_PLAN':
                    validate_review_current(state,cd,manifest)
                state['blocked']=None; state['phase']=target

            elif args.cmd=='writer':
                if args.status=='RUNNING':
                    if state['phase']=='BLOCKED' or state['writer']['status']!='STOPPED' or state['dispatch_state'] in ('SENT','SEND_UNKNOWN'):
                        reject('WRITER_START_UNSAFE','cannot start writer while phase/worker/dispatch is uncertain')
                state['writer']['status']=args.status; state['writer']['task_round']=args.task_round
                state['writer']['last_observed_at']=dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')

            elif args.cmd=='dispatch':
                if args.state=='SENT' and (state['phase']=='BLOCKED' or state['writer']['status']=='UNKNOWN'):
                    reject('DISPATCH_START_UNSAFE','cannot dispatch while blocked or writer identity is unknown')
                old=state['dispatch_state']; new=args.state
                valid={('NOT_SENT','SENT'),('SENT','SETTLED'),('SENT','SEND_UNKNOWN'),('SEND_UNKNOWN','SETTLED'),('SETTLED','NOT_SENT')}
                if old!=new and (old,new) not in valid: reject('DISPATCH_TRANSITION_INVALID',f'{old}->{new}')
                state['dispatch_state']=new

            elif args.cmd=='finding-resolve':
                matches=[item for item in state['findings'] if item['id']==args.finding_id]
                if not matches: reject('FINDING_NOT_FOUND',args.finding_id)
                matches[0]['status']='RESOLVED'

            elif args.cmd=='contract-update':
                state['contract_revision']=contract['revision']; state['contract_digest']=cd
                if state['code_review']['status']!='NOT_RUN': state['code_review']['status']='STALE'
                if state['test_plan']['status']!='NOT_CREATED': state['test_plan']['status']='STALE'
                state['test_results_path']=None
                if state['phase'] not in ('CONTRACT','IMPLEMENT'): state['phase']='IMPLEMENT_REWORK'
                state['findings'].append({'id':f'contract-update-{contract["revision"]}','status':'OPEN','category':'CONTRACT_CHANGE','reason':args.reason})
                state['dispatch_state']='NOT_SENT'

            elif args.cmd=='complete':
                if state['phase']!='TEST': reject('COMPLETE_SOURCE_INVALID','COMPLETE only from TEST')
                if state['writer']['status']!='STOPPED': reject('WRITER_NOT_STOPPED','writer must be stopped before COMPLETE')
                if state['dispatch_state']!='SETTLED': reject('DISPATCH_UNSETTLED','dispatch must be SETTLED before COMPLETE')
                if state['blocked'] is not None: reject('BLOCKED_UNRESOLVED','blocked state remains')
                if any(item['status']=='OPEN' for item in state['findings']): reject('OPEN_FINDINGS','open findings remain')
                manifest=current_manifest(state); validate_test_entry(state,cd,policy_digest,plan,plan_digest,manifest)
                validate_results(state,plan,results,manifest['deliverable_digest'])
                if canonical_digest(load_json(args.contract))!=cd: reject('ARTIFACT_CHANGED_DURING_VALIDATION','Contract changed')
                if canonical_digest(load_json(args.policy))!=policy_digest: reject('ARTIFACT_CHANGED_DURING_VALIDATION','policy changed')
                if canonical_digest(load_json(args.test_plan))!=plan_digest: reject('ARTIFACT_CHANGED_DURING_VALIDATION','plan changed')
                if canonical_digest(load_json(args.results))!=canonical_digest(results): reject('ARTIFACT_CHANGED_DURING_VALIDATION','results changed')
                state['test_results_path']=str(Path(args.results).resolve()); state['phase']='COMPLETE'

            commit_state(state_path,state,version)
            print(json.dumps({'decision':'OK','phase':state['phase'],'state_version':state['state_version']},sort_keys=True)); return 0

    except Reject as e:
        print(json.dumps({'decision':'REJECTED','reason_code':e.code,'reason':e.message},sort_keys=True),file=sys.stderr); return 1
    except Exception as e:
        print(json.dumps({'decision':'REJECTED','reason_code':'UNEXPECTED_ERROR','reason':str(e)},sort_keys=True),file=sys.stderr); return 1

if __name__=='__main__':
    raise SystemExit(main())
