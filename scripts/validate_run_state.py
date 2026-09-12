#!/usr/bin/env python3
import argparse, fcntl, hashlib, json, math, os, subprocess, sys, tempfile
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS={'state':ROOT/'schemas/run-state.schema.json','contract':ROOT/'schemas/development-contract.schema.json','plan':ROOT/'schemas/test-plan.schema.json','results':ROOT/'schemas/test-results.schema.json'}
ALLOWED={'CONTRACT':{'IMPLEMENT','BLOCKED'},'IMPLEMENT':{'CODE_REVIEW','BLOCKED'},'CODE_REVIEW':{'IMPLEMENT_REWORK','TEST_PLAN','BLOCKED'},'IMPLEMENT_REWORK':{'CODE_REVIEW','BLOCKED'},'TEST_PLAN':{'TEST','BLOCKED'},'TEST':{'TEST_REWORK','BLOCKED'},'TEST_REWORK':{'CODE_REVIEW','BLOCKED'},'BLOCKED':{'IMPLEMENT','CODE_REVIEW','TEST_PLAN','TEST','TEST_REWORK'},'COMPLETE':set()}

def load(p):
    with open(p,encoding='utf-8') as f:return json.load(f)
def canonical_digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def validate_schema(kind,obj):
    schema=load(SCHEMAS[kind]); errs=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(obj),key=lambda e:list(e.path))
    if errs:
        e=errs[0]; loc='.'.join(str(x) for x in e.absolute_path) or '<root>'; raise ValueError(f'{kind} schema: {loc}: {e.message}')
def resolve_under(root,ref):
    root=Path(root).resolve(); p=Path(ref); p=(root/p).resolve() if not p.is_absolute() else p.resolve()
    if os.path.commonpath([str(root),str(p)])!=str(root): raise ValueError(f'evidence path escapes evidence_root: {ref}')
    if not p.exists() or not p.is_file(): raise ValueError(f'evidence file missing: {ref}')
    return p
def snapshot_current(state):
    work=Path(state['working_directory']).resolve(); repo=Path(state['repo_root']).resolve()
    if not work.exists(): raise ValueError('working_directory missing')
    actual=subprocess.run(['git','-C',str(work),'rev-parse','--show-toplevel'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if actual.returncode or Path(actual.stdout.strip()).resolve()!=repo: raise ValueError('repository/worktree identity mismatch')
    gd=subprocess.run(['git','-C',str(work),'rev-parse','--git-path','agy-supervised/tmp'],stdout=subprocess.PIPE,text=True,check=True).stdout.strip()
    gdpath=Path(gd); gdpath=(work/gdpath).resolve() if not gdpath.is_absolute() else gdpath.resolve(); gdpath.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='completion.',dir=gdpath) as td:
        out=Path(td)/'snapshot'
        p=subprocess.run([sys.executable,str(ROOT/'scripts/snapshot_code_state.py'),str(out),state['baseline']['commit']],cwd=work,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if p.returncode: raise ValueError(f'current snapshot failed: {p.stderr.strip()}')
        return load(out/'manifest.json')
def validate_baseline(state):
    ref=Path(state['baseline']['snapshot_ref'])
    if not ref.is_absolute(): ref=(Path(state['working_directory'])/ref).resolve()
    manifest=ref/'manifest.json'
    if not manifest.exists(): raise ValueError('baseline snapshot manifest missing')
    data=load(manifest)
    if data.get('repo_root')!=str(Path(state['repo_root']).resolve()): raise ValueError('baseline repository identity mismatch')
    if data.get('baseline_commit')!=state['baseline']['commit'] or data.get('head')!=state['baseline']['commit']: raise ValueError('baseline commit identity mismatch')
    if data.get('deliverable_digest')!=state['baseline']['deliverable_digest'] or data.get('ownership_digest')!=state['baseline']['ownership_digest']: raise ValueError('baseline snapshot digest mismatch')

def check_identity(state,contract,plan=None):
    if state['contract_id']!=contract['contract_id'] or state['contract_revision']!=contract['revision']: raise ValueError('current Contract id/revision mismatch')
    if plan:
        for k,a,b in [('task_id',plan['task_id'],state['task_id']),('contract_id',plan['contract_id'],state['contract_id']),('contract_revision',plan['contract_revision'],state['contract_revision'])]:
            if a!=b: raise ValueError(f'Test Plan {k} mismatch')
def plan_checks(plan):
    d={}
    for c in plan['checks']:
        if c['id'] in d: raise ValueError(f'duplicate check id in plan: {c["id"]}')
        d[c['id']]=c
    mids=set()
    for m in plan['metrics']:
        if m['id'] in mids: raise ValueError(f'duplicate metric id: {m["id"]}')
        mids.add(m['id'])
        if m['source_check_id'] not in d: raise ValueError(f'metric {m["id"]} references unknown check')
    return d
def verify_evidence(root,refs):
    for r in refs:
        p=resolve_under(root,r['path'])
        if sha_file(p)!=r['sha256']: raise ValueError(f'evidence hash mismatch: {r["path"]}')
def get_field(obj,path):
    cur=obj
    for seg in path.split('.'):
        if not isinstance(cur,dict) or seg not in cur: raise ValueError(f'missing measured field: {path}')
        cur=cur[seg]
    return cur
def compare_metric(metric,raw):
    unit=metric.get('unit')
    if unit is not None:
        if not isinstance(raw,dict) or raw.get('unit')!=unit or 'value' not in raw: raise ValueError(f'metric {metric["id"]} unit/value mismatch')
        raw=raw['value']
    if isinstance(raw,float) and math.isnan(raw): raise ValueError(f'metric {metric["id"]} is NaN')
    op,t=metric['op'],metric['threshold']
    if op in ('ge','le') and (isinstance(raw,bool) or isinstance(t,bool) or not isinstance(raw,(int,float)) or not isinstance(t,(int,float))): raise ValueError(f'metric {metric["id"]} requires numeric values')
    return raw==t if op=='eq' else raw>=t if op=='ge' else raw<=t

def validate_test_entry(state,contract,plan,manifest):
    check_identity(state,contract,plan); validate_baseline(state); checks=plan_checks(plan); pd=canonical_digest(plan)
    if state['writer']['status']!='STOPPED': raise ValueError('writer must be STOPPED before TEST')
    if state['dispatch_state']=='SEND_UNKNOWN': raise ValueError('SEND_UNKNOWN must be resolved before TEST')
    cr=state['code_review']
    if not cr.get('review_id'): raise ValueError('PASS code review lacks review_id')
    if cr['status']!='PASS' or cr['contract_revision']!=state['contract_revision']: raise ValueError('current Contract lacks PASS code review')
    if cr['reviewed_deliverable_digest']!=manifest['deliverable_digest']: raise ValueError('code review digest is stale')
    tp=state['test_plan']
    if tp['status']!='FROZEN' or tp['plan_id']!=plan['plan_id'] or tp['plan_revision']!=plan['plan_revision'] or tp['plan_digest']!=pd or tp.get('contract_revision')!=state['contract_revision']: raise ValueError('frozen Test Plan identity/digest mismatch')
    if plan['reviewed_deliverable_digest']!=manifest['deliverable_digest'] or tp['reviewed_deliverable_digest']!=manifest['deliverable_digest']: raise ValueError('Test Plan reviewed digest is stale')
    import base64
    manifest_paths={x['path_b64'] for x in manifest['files']}
    for c in checks.values():
        for p in c.get('input_paths',[]):
            if base64.b64encode(os.fsencode(p)).decode() not in manifest_paths: raise ValueError(f'check {c["id"]} input path absent from deliverable snapshot: {p}')
    return pd

def latest_results(plan,results,current_digest,evidence_root):
    checks=plan_checks(plan); grouped={k:[] for k in checks}
    for r in results['results']:
        if r['check_id'] not in checks: raise ValueError(f'unknown result check id: {r["check_id"]}')
        grouped[r['check_id']].append(r)
    latest={}
    for cid,c in checks.items():
        rows=grouped[cid]
        if not rows: raise ValueError(f'missing result for check {cid}')
        nums=[r['attempt_number'] for r in rows]
        if len(nums)!=len(set(nums)) or sorted(nums)!=list(range(1,max(nums)+1)): raise ValueError(f'check {cid} attempts must be unique and contiguous from 1')
        if max(nums)>c['max_attempts']: raise ValueError(f'check {cid} exceeded max_attempts')
        attempt_ids=[row['attempt_id'] for row in rows]
        if len(attempt_ids)!=len(set(attempt_ids)): raise ValueError(f'check {cid} attempt_id values must be unique')
        r=max(rows,key=lambda x:x['attempt_number']); latest[cid]=r
        if r['cwd']!=c['cwd']: raise ValueError(f'check {cid} cwd differs from frozen plan')
        if r['deliverable_digest_before']!=current_digest or r['deliverable_digest_after']!=current_digest: raise ValueError(f'check {cid} evidence is stale for current deliverable')
        verify_evidence(evidence_root,r['evidence_refs'])
        app=c['applicability']; applicable=True
        if app['mode']=='fact_eq':
            ae=r.get('applicability_evidence')
            if not ae: raise ValueError(f'check {cid} applicability is unknown')
            resolve_under(evidence_root,ae['evidence_ref'])
            if ae['evidence_ref'] not in {ref['path'] for ref in r['evidence_refs']}: raise ValueError(f'check {cid} applicability evidence is not part of attempt evidence')
            if ae['fact']!=app['fact']: raise ValueError(f'check {cid} applicability fact mismatch')
            applicable=(ae['value']==app['value'])
        if not applicable:
            if r['status']!='NOT_APPLICABLE': raise ValueError(f'check {cid} must be NOT_APPLICABLE when frozen condition is false')
            continue
        if r['status']=='NOT_APPLICABLE': raise ValueError(f'applicable check {cid} cannot be NOT_APPLICABLE')
        if c['required'] and r['status']!='PASS': raise ValueError(f'required check {cid} is {r["status"]}, not PASS')
        if r['status']=='PASS':
            if c['type']=='command':
                if r.get('actual_argv')!=c['command']['argv']: raise ValueError(f'check {cid} executed argv differs from frozen plan')
                if r.get('exit_code') not in c['command']['expected_exit_codes']: raise ValueError(f'check {cid} exit code does not satisfy frozen plan')
            elif r.get('observation_completed') is not True: raise ValueError(f'observation check {cid} lacks completed observation')
    return latest

def validate_metrics(plan,latest):
    for m in plan['metrics']:
        r=latest.get(m['source_check_id'])
        if not r: raise ValueError(f'metric {m["id"]} has no source result')
        if r['status']=='NOT_APPLICABLE': continue
        if r['status']!='PASS': raise ValueError(f'metric {m["id"]} source check is not PASS')
        val=get_field(r['measured_values'],m['result_field'])
        if not compare_metric(m,val): raise ValueError(f'metric {m["id"]} threshold not satisfied')
def no_checks(plan,evidence_root):
    n=plan.get('no_checks_acceptance')
    if not n: raise ValueError('empty Test Plan requires frozen no_checks_acceptance')
    p=resolve_under(evidence_root,n['evidence_ref'])
    if sha_file(p)!=n['evidence_sha256']: raise ValueError('no-check acceptance evidence hash mismatch')

def atomic_update(path,state,expected):
    path=Path(path); lock=path.with_suffix(path.suffix+'.lock'); lock.parent.mkdir(parents=True,exist_ok=True)
    with open(lock,'a+') as lf:
        fcntl.flock(lf,fcntl.LOCK_EX); cur=load(path)
        if cur['state_version']!=expected: raise ValueError(f'state_version changed: expected {expected}, found {cur["state_version"]}')
        state['state_version']=expected+1
        fd,tmp=tempfile.mkstemp(prefix=path.name+'.tmp.',dir=path.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(state,f,indent=2,sort_keys=True); f.write('\n'); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    for name in ('validate','transition','complete','invalidate','block'):
        q=sub.add_parser(name); q.add_argument('--run-state',required=True); q.add_argument('--contract',required=True)
        if name in ('transition','complete'): q.add_argument('--test-plan')
        if name=='complete': q.add_argument('--results',required=True)
        if name=='transition': q.add_argument('--to',required=True,choices=sorted({x for s in ALLOWED.values() for x in s}))
        if name in ('transition','complete','invalidate','block'): q.add_argument('--expected-state-version',required=True,type=int)
        if name in ('invalidate','block'): q.add_argument('--reason',required=True)
        if name=='block': q.add_argument('--resume-action',required=True)
    a=p.parse_args()
    try:
        state=load(a.run_state); contract=load(a.contract); validate_schema('state',state); validate_schema('contract',contract); check_identity(state,contract); validate_baseline(state)
        if a.cmd=='validate': print('RUN_STATE_VALID'); return 0
        if a.cmd=='transition':
            if a.to not in ALLOWED[state['phase']]: raise ValueError(f'illegal transition {state["phase"]} -> {a.to}')
            if a.to=='TEST':
                if not a.test_plan: raise ValueError('--test-plan required for TEST transition')
                if state['test_plan'].get('path') and Path(state['test_plan']['path']).resolve()!=Path(a.test_plan).resolve(): raise ValueError('Test Plan path differs from Run State')
                plan=load(a.test_plan); validate_schema('plan',plan); manifest=snapshot_current(state); validate_test_entry(state,contract,plan,manifest)
            if state['phase']=='BLOCKED':
                if state['blocked'] is None: raise ValueError('BLOCKED phase lacks blocked metadata')
                if state['writer']['status']!='STOPPED': raise ValueError('cannot resume while writer is not stopped')
                snapshot_current(state); state['blocked']=None
            state['phase']=a.to; atomic_update(a.run_state,state,a.expected_state_version); print(f'TRANSITION_OK={a.to}'); return 0
        if a.cmd=='invalidate':
            if state['writer']['status']!='STOPPED': raise ValueError('cannot invalidate/enter rework until writer stop is established')
            state['phase']='TEST_REWORK'; state['code_review']['status']='STALE'; state['test_plan']['status']='STALE'; state['findings'].append({'id':f'test-rework-{state["state_version"]}','status':'OPEN','category':'TEST_DEFECT','reason':a.reason}); atomic_update(a.run_state,state,a.expected_state_version); print('INVALIDATED_FOR_REWORK'); return 0
        if a.cmd=='block':
            if state['writer']['status']=='RUNNING': raise ValueError('writer must not remain RUNNING when persisting BLOCKED')
            prev=state['phase']; state['phase']='BLOCKED'; state['blocked']={'reason':a.reason,'blocked_from_phase':prev,'resume_action':a.resume_action,'related_identity':state['writer'].get('task_round')}; atomic_update(a.run_state,state,a.expected_state_version); print('BLOCKED_SAVED'); return 0
        if a.cmd=='complete':
            if state['phase']!='TEST': raise ValueError('COMPLETE is only valid from TEST')
            if state['writer']['status']!='STOPPED': raise ValueError('writer must be STOPPED before COMPLETE')
            if state['dispatch_state']!='SETTLED': raise ValueError('dispatch must be SETTLED before COMPLETE')
            if state['blocked'] is not None: raise ValueError('blocked state unresolved')
            if any(f['status']=='OPEN' for f in state['findings']): raise ValueError('open findings remain')
            if not a.test_plan: raise ValueError('--test-plan required for completion')
            if state['test_plan'].get('path') and Path(state['test_plan']['path']).resolve()!=Path(a.test_plan).resolve(): raise ValueError('Test Plan path differs from Run State')
            plan=load(a.test_plan); results=load(a.results); validate_schema('plan',plan); validate_schema('results',results); manifest=snapshot_current(state); pd=validate_test_entry(state,contract,plan,manifest)
            if results['task_id']!=state['task_id'] or results['contract_id']!=state['contract_id'] or results['contract_revision']!=state['contract_revision'] or results['plan_id']!=plan['plan_id'] or results['plan_revision']!=plan['plan_revision'] or results['plan_digest']!=pd: raise ValueError('test results identity/plan digest mismatch')
            if state.get('test_results_path') and Path(state['test_results_path']).resolve()!=Path(a.results).resolve(): raise ValueError('results path differs from Run State current attempt set')
            if plan['checks']:
                latest=latest_results(plan,results,manifest['deliverable_digest'],state['evidence_root']); validate_metrics(plan,latest)
            else: no_checks(plan,state['evidence_root'])
            state['phase']='COMPLETE'; atomic_update(a.run_state,state,a.expected_state_version); print(json.dumps({'decision':'COMPLETE','deliverable_digest':manifest['deliverable_digest'],'plan_digest':pd},sort_keys=True)); return 0
    except Exception as e:
        print(json.dumps({'decision':'REJECTED','reason':str(e)},sort_keys=True),file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
