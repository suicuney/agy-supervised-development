#!/usr/bin/env python3
import argparse, fcntl, hashlib, json, math, os, subprocess, sys, tempfile
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS={'state':ROOT/'schemas/run-state.schema.json','contract':ROOT/'schemas/development-contract.schema.json','plan':ROOT/'schemas/test-plan.schema.json','results':ROOT/'schemas/test-results.schema.json'}
ALLOWED={'CONTRACT':{'IMPLEMENT','BLOCKED'},'IMPLEMENT':{'CODE_REVIEW','BLOCKED'},'CODE_REVIEW':{'IMPLEMENT_REWORK','TEST_PLAN','BLOCKED'},'IMPLEMENT_REWORK':{'CODE_REVIEW','BLOCKED'},'TEST_PLAN':{'TEST','BLOCKED'},'TEST':{'TEST_REWORK','BLOCKED'},'TEST_REWORK':{'CODE_REVIEW','BLOCKED'},'BLOCKED':{'IMPLEMENT','CODE_REVIEW','TEST_PLAN','TEST','TEST_REWORK'},'COMPLETE':set()}

def load(path):
    with open(path,encoding='utf-8') as f:return json.load(f)

def canonical_digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def validate_schema(kind,obj):
    schema=load(SCHEMAS[kind]); errors=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(obj),key=lambda e:list(e.path))
    if errors:
        e=errors[0]; loc='.'.join(str(x) for x in e.absolute_path) or '<root>'
        raise ValueError(f'{kind} schema: {loc}: {e.message}')

def resolve_under(root,ref):
    root=Path(root).resolve(); path=Path(ref); path=(root/path).resolve() if not path.is_absolute() else path.resolve()
    if os.path.commonpath([str(root),str(path)])!=str(root):raise ValueError(f'evidence path escapes evidence_root: {ref}')
    if not path.exists() or not path.is_file():raise ValueError(f'evidence file missing: {ref}')
    return path

def snapshot_current(state):
    work=Path(state['working_directory']).resolve(); repo=Path(state['repo_root']).resolve()
    if not work.exists():raise ValueError('working_directory missing')
    actual=subprocess.run(['git','-C',str(work),'rev-parse','--show-toplevel'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if actual.returncode or Path(actual.stdout.strip()).resolve()!=repo:raise ValueError('repository/worktree identity mismatch')
    git_tmp=subprocess.run(['git','-C',str(work),'rev-parse','--git-path','agy-supervised/tmp'],stdout=subprocess.PIPE,text=True,check=True).stdout.strip()
    parent=Path(git_tmp); parent=(work/parent).resolve() if not parent.is_absolute() else parent.resolve(); parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='completion.',dir=parent) as td:
        out=Path(td)/'snapshot'
        p=subprocess.run([sys.executable,str(ROOT/'scripts/snapshot_code_state.py'),str(out),state['baseline']['commit']],cwd=work,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if p.returncode:raise ValueError(f'current snapshot failed: {p.stderr.strip()}')
        return load(out/'manifest.json')

def check_identity(state,contract,plan=None):
    if state['contract_id']!=contract['contract_id'] or state['contract_revision']!=contract['revision']:raise ValueError('current Contract id/revision mismatch')
    if plan:
        for key,a,b in [('task_id',plan['task_id'],state['task_id']),('contract_id',plan['contract_id'],state['contract_id']),('contract_revision',plan['contract_revision'],state['contract_revision'])]:
            if a!=b:raise ValueError(f'Test Plan {key} mismatch')

def plan_checks(plan):
    checks={}
    for check in plan['checks']:
        if check['id'] in checks:raise ValueError(f'duplicate check id in plan: {check["id"]}')
        checks[check['id']]=check
    metrics=set()
    for metric in plan['metrics']:
        if metric['id'] in metrics:raise ValueError(f'duplicate metric id: {metric["id"]}')
        metrics.add(metric['id'])
        if metric['source_check_id'] not in checks:raise ValueError(f'metric {metric["id"]} references unknown check')
    return checks

def verify_evidence(root,refs):
    for ref in refs:
        path=resolve_under(root,ref['path'])
        if sha_file(path)!=ref['sha256']:raise ValueError(f'evidence hash mismatch: {ref["path"]}')

def get_field(obj,path):
    current=obj
    for segment in path.split('.'):
        if not isinstance(current,dict) or segment not in current:raise ValueError(f'missing measured field: {path}')
        current=current[segment]
    return current

def compare_metric(metric,raw):
    unit=metric.get('unit')
    if unit is not None:
        if not isinstance(raw,dict) or raw.get('unit')!=unit or 'value' not in raw:raise ValueError(f'metric {metric["id"]} unit/value mismatch')
        raw=raw['value']
    if isinstance(raw,float) and math.isnan(raw):raise ValueError(f'metric {metric["id"]} is NaN')
    op,threshold=metric['op'],metric['threshold']
    if op in ('ge','le') and (isinstance(raw,bool) or isinstance(threshold,bool) or not isinstance(raw,(int,float)) or not isinstance(threshold,(int,float))):raise ValueError(f'metric {metric["id"]} requires numeric values')
    return raw==threshold if op=='eq' else raw>=threshold if op=='ge' else raw<=threshold

def validate_test_entry(state,contract,plan,manifest):
    check_identity(state,contract,plan); checks=plan_checks(plan); plan_digest=canonical_digest(plan)
    if state['writer']['status']!='STOPPED':raise ValueError('writer must be STOPPED before TEST')
    if state['dispatch_state']=='SEND_UNKNOWN':raise ValueError('SEND_UNKNOWN must be resolved before TEST')
    review=state['code_review']
    if review['status']!='PASS' or review['contract_revision']!=state['contract_revision']:raise ValueError('current Contract lacks PASS code review')
    if review['reviewed_deliverable_digest']!=manifest['deliverable_digest']:raise ValueError('code review digest is stale')
    recorded=state['test_plan']
    if recorded['status']!='FROZEN' or recorded['plan_id']!=plan['plan_id'] or recorded['plan_revision']!=plan['plan_revision'] or recorded['plan_digest']!=plan_digest:raise ValueError('frozen Test Plan identity/digest mismatch')
    if plan['reviewed_deliverable_digest']!=manifest['deliverable_digest'] or recorded['reviewed_deliverable_digest']!=manifest['deliverable_digest']:raise ValueError('Test Plan reviewed digest is stale')
    import base64
    manifest_paths={item['path_b64'] for item in manifest['files']}
    for check in checks.values():
        for path in check.get('input_paths',[]):
            if base64.b64encode(os.fsencode(path)).decode() not in manifest_paths:raise ValueError(f'check {check["id"]} input path absent from deliverable snapshot: {path}')
    return plan_digest

def latest_results(plan,results,current_digest,evidence_root):
    checks=plan_checks(plan); grouped={key:[] for key in checks}
    for result in results['results']:
        if result['check_id'] not in checks:raise ValueError(f'unknown result check id: {result["check_id"]}')
        grouped[result['check_id']].append(result)
    latest={}
    for check_id,check in checks.items():
        rows=grouped[check_id]
        if not rows:raise ValueError(f'missing result for check {check_id}')
        numbers=[row['attempt_number'] for row in rows]
        if len(numbers)!=len(set(numbers)) or sorted(numbers)!=list(range(1,max(numbers)+1)):raise ValueError(f'check {check_id} attempts must be unique and contiguous from 1')
        if max(numbers)>check['max_attempts']:raise ValueError(f'check {check_id} exceeded max_attempts')
        result=max(rows,key=lambda x:x['attempt_number']); latest[check_id]=result
        if result['deliverable_digest_before']!=current_digest or result['deliverable_digest_after']!=current_digest:raise ValueError(f'check {check_id} evidence is stale for current deliverable')
        verify_evidence(evidence_root,result['evidence_refs'])
        applicability=check['applicability']; applicable=True
        if applicability['mode']=='fact_eq':
            evidence=result.get('applicability_evidence')
            if not evidence:raise ValueError(f'check {check_id} applicability is unknown')
            resolve_under(evidence_root,evidence['evidence_ref'])
            if evidence['fact']!=applicability['fact']:raise ValueError(f'check {check_id} applicability fact mismatch')
            applicable=evidence['value']==applicability['value']
        if not applicable:
            if result['status']!='NOT_APPLICABLE':raise ValueError(f'check {check_id} must be NOT_APPLICABLE when frozen condition is false')
            continue
        if result['status']=='NOT_APPLICABLE':raise ValueError(f'applicable check {check_id} cannot be NOT_APPLICABLE')
        if check['required'] and result['status']!='PASS':raise ValueError(f'required check {check_id} is {result["status"]}, not PASS')
        if result['status']=='PASS':
            if check['type']=='command':
                if result.get('actual_argv')!=check['command']['argv']:raise ValueError(f'check {check_id} executed argv differs from frozen plan')
                if result.get('exit_code') not in check['command']['expected_exit_codes']:raise ValueError(f'check {check_id} exit code does not satisfy frozen plan')
            elif result.get('observation_completed') is not True:raise ValueError(f'observation check {check_id} lacks completed observation')
    return latest

def validate_metrics(plan,latest):
    for metric in plan['metrics']:
        result=latest.get(metric['source_check_id'])
        if not result:raise ValueError(f'metric {metric["id"]} has no source result')
        if result['status']=='NOT_APPLICABLE' and not metric['required']:continue
        if result['status']!='PASS':raise ValueError(f'metric {metric["id"]} source check is not PASS')
        value=get_field(result['measured_values'],metric['result_field'])
        if not compare_metric(metric,value):raise ValueError(f'metric {metric["id"]} threshold not satisfied')

def validate_no_checks(plan,evidence_root):
    record=plan.get('no_checks_acceptance')
    if not record:raise ValueError('empty Test Plan requires frozen no_checks_acceptance')
    path=resolve_under(evidence_root,record['evidence_ref'])
    if sha_file(path)!=record['evidence_sha256']:raise ValueError('no-check acceptance evidence hash mismatch')

def atomic_update(path,state,expected):
    path=Path(path); lock=path.with_suffix(path.suffix+'.lock'); lock.parent.mkdir(parents=True,exist_ok=True)
    with open(lock,'a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX); current=load(path)
        if current['state_version']!=expected:raise ValueError(f'state_version changed: expected {expected}, found {current["state_version"]}')
        state['state_version']=expected+1
        fd,tmp=tempfile.mkstemp(prefix=path.name+'.tmp.',dir=path.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as output:
                json.dump(state,output,indent=2,sort_keys=True); output.write('\n'); output.flush(); os.fsync(output.fileno())
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)

def main():
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest='cmd',required=True)
    for name in ('validate','transition','complete','invalidate','block'):
        command=sub.add_parser(name); command.add_argument('--run-state',required=True); command.add_argument('--contract',required=True)
        if name in ('transition','complete'):command.add_argument('--test-plan')
        if name=='complete':command.add_argument('--results',required=True)
        if name=='transition':command.add_argument('--to',required=True,choices=sorted({x for values in ALLOWED.values() for x in values}))
        if name in ('transition','complete','invalidate','block'):command.add_argument('--expected-state-version',required=True,type=int)
        if name in ('invalidate','block'):command.add_argument('--reason',required=True)
        if name=='block':command.add_argument('--resume-action',required=True)
    args=parser.parse_args()
    try:
        state=load(args.run_state); contract=load(args.contract); validate_schema('state',state); validate_schema('contract',contract); check_identity(state,contract)
        if args.cmd=='validate':print('RUN_STATE_VALID'); return 0
        if args.cmd=='transition':
            if args.to not in ALLOWED[state['phase']]:raise ValueError(f'illegal transition {state["phase"]} -> {args.to}')
            if args.to=='TEST':
                if not args.test_plan:raise ValueError('--test-plan required for TEST transition')
                plan=load(args.test_plan); validate_schema('plan',plan); manifest=snapshot_current(state); validate_test_entry(state,contract,plan,manifest)
            if state['phase']=='BLOCKED':
                if state['blocked'] is None:raise ValueError('BLOCKED phase lacks blocked metadata')
                if state['writer']['status']!='STOPPED':raise ValueError('cannot resume while writer is not stopped')
                snapshot_current(state); state['blocked']=None
            state['phase']=args.to; atomic_update(args.run_state,state,args.expected_state_version); print(f'TRANSITION_OK={args.to}'); return 0
        if args.cmd=='invalidate':
            if state['writer']['status']!='STOPPED':raise ValueError('cannot invalidate/enter rework until writer stop is established')
            state['phase']='TEST_REWORK'; state['code_review']['status']='STALE'; state['test_plan']['status']='STALE'; state['findings'].append({'id':f'test-rework-{state["state_version"]}','status':'OPEN','category':'TEST_DEFECT','reason':args.reason}); atomic_update(args.run_state,state,args.expected_state_version); print('INVALIDATED_FOR_REWORK'); return 0
        if args.cmd=='block':
            if state['writer']['status']=='RUNNING':raise ValueError('writer must not remain RUNNING when persisting BLOCKED')
            previous=state['phase']; state['phase']='BLOCKED'; state['blocked']={'reason':args.reason,'blocked_from_phase':previous,'resume_action':args.resume_action,'related_identity':state['writer'].get('task_round')}; atomic_update(args.run_state,state,args.expected_state_version); print('BLOCKED_SAVED'); return 0
        if args.cmd=='complete':
            if state['phase']!='TEST':raise ValueError('COMPLETE is only valid from TEST')
            if state['writer']['status']!='STOPPED':raise ValueError('writer must be STOPPED before COMPLETE')
            if state['dispatch_state']!='SETTLED':raise ValueError('dispatch must be SETTLED before COMPLETE')
            if state['blocked'] is not None:raise ValueError('blocked state unresolved')
            if any(finding['status']=='OPEN' for finding in state['findings']):raise ValueError('open findings remain')
            if not args.test_plan:raise ValueError('--test-plan required for completion')
            plan=load(args.test_plan); results=load(args.results); validate_schema('plan',plan); validate_schema('results',results); manifest=snapshot_current(state); plan_digest=validate_test_entry(state,contract,plan,manifest)
            if results['task_id']!=state['task_id'] or results['contract_id']!=state['contract_id'] or results['contract_revision']!=state['contract_revision'] or results['plan_id']!=plan['plan_id'] or results['plan_revision']!=plan['plan_revision'] or results['plan_digest']!=plan_digest:raise ValueError('test results identity/plan digest mismatch')
            if state.get('test_results_path') and Path(state['test_results_path']).resolve()!=Path(args.results).resolve():raise ValueError('results path differs from Run State current attempt set')
            if plan['checks']:
                latest=latest_results(plan,results,manifest['deliverable_digest'],state['evidence_root']); validate_metrics(plan,latest)
            else:validate_no_checks(plan,state['evidence_root'])
            state['phase']='COMPLETE'; atomic_update(args.run_state,state,args.expected_state_version); print(json.dumps({'decision':'COMPLETE','deliverable_digest':manifest['deliverable_digest'],'plan_digest':plan_digest},sort_keys=True)); return 0
    except Exception as error:
        print(json.dumps({'decision':'REJECTED','reason':str(error)},sort_keys=True),file=sys.stderr); return 1
if __name__=='__main__':raise SystemExit(main())
