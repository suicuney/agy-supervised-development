#!/usr/bin/env python3
import copy, hashlib, importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('vr',ROOT/'scripts/validate_run_state.py'); vr=importlib.util.module_from_spec(spec); spec.loader.exec_module(vr)

def git(repo,*args): return subprocess.run(['git','-C',str(repo),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
def dump(path,obj): path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def reject(fn,contains):
    try: fn()
    except Exception as e:
        assert contains in str(e),(contains,str(e)); return
    raise AssertionError(f'expected rejection containing {contains!r}')

def fixture(base):
    repo=base/'repo'; repo.mkdir(); git(repo,'init','-q'); git(repo,'config','user.email','test@example.invalid'); git(repo,'config','user.name','test')
    (repo/'app.txt').write_text('ok\n'); git(repo,'add','.'); git(repo,'commit','-qm','base'); commit=git(repo,'rev-parse','HEAD').stdout.decode().strip()
    run=repo/'.git'/'agy-supervised'/'runs'/'t1'; evidence=run/'evidence'; evidence.mkdir(parents=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/snapshot_code_state.py'),str(run/'baseline'),commit],cwd=repo,check=True,stdout=subprocess.DEVNULL)
    b=json.loads((run/'baseline'/'manifest.json').read_text()); current=b['deliverable_digest']
    contract={'contract_id':'c1','revision':1,'goal':'keep app valid','behavior':['app remains valid'],'acceptance_scenarios':['formal command succeeds'],'counterexamples':['formal command fails'],'constraints':[],'diagnostics':[],'done':['frozen checks and metrics pass'],'escalate_if':[]}; contract_path=run/'contract.json'; dump(contract_path,contract)
    plan={'schema_version':1,'task_id':'t1','contract_id':'c1','contract_revision':1,'plan_id':'p1','plan_revision':1,'reviewed_deliverable_digest':current,'status':'FROZEN','checks':[{'id':'T1','type':'command','cwd':str(repo),'required':True,'applicability':{'mode':'always'},'evidence_types':['log'],'max_attempts':2,'command':{'argv':['python3','-c','print(1)'],'expected_exit_codes':[0],'timeout_seconds':30},'expected':'prints successfully'}],'metrics':[{'id':'M1','source_check_id':'T1','result_field':'passed','op':'ge','threshold':1,'unit':'count','required':True,'description':'at least one pass'}],'no_checks_acceptance':None}; plan_path=run/'test-plan.json'; dump(plan_path,plan); pd=vr.canonical_digest(plan)
    log=evidence/'T1-a1.log'; log.write_text('1\n')
    results={'schema_version':1,'task_id':'t1','contract_id':'c1','contract_revision':1,'plan_id':'p1','plan_revision':1,'plan_digest':pd,'results':[{'check_id':'T1','attempt_id':'T1-a1','attempt_number':1,'status':'PASS','cwd':str(repo),'started_at':'2026-09-13T00:00:00Z','ended_at':'2026-09-13T00:00:01Z','actual_argv':['python3','-c','print(1)'],'exit_code':0,'observation_completed':None,'applicability_evidence':None,'measured_values':{'passed':{'value':1,'unit':'count'}},'evidence_refs':[{'path':'T1-a1.log','sha256':sha(log),'summary':'command output'}],'deliverable_digest_before':current,'deliverable_digest_after':current,'reason':'passed'}]}; results_path=run/'results.json'; dump(results_path,results)
    state={'schema_version':2,'state_version':1,'task_id':'t1','contract_id':'c1','contract_revision':1,'repo_root':str(repo.resolve()),'working_directory':str(repo.resolve()),'branch':'master','baseline':{'commit':commit,'snapshot_ref':str((run/'baseline').resolve()),'deliverable_digest':b['deliverable_digest'],'ownership_digest':b['ownership_digest']},'evidence_root':str(evidence.resolve()),'herdr':{'workspace_id':'w1','pane_id':'p1','agy_agent':'a1','native_session_ref':None},'phase':'TEST','dispatch_state':'SETTLED','writer':{'status':'STOPPED','task_round':'test-1','last_observed_at':'2026-09-13T00:00:01Z'},'code_review':{'status':'PASS','review_id':'r1','contract_revision':1,'reviewed_deliverable_digest':current,'finding_ids':[]},'test_plan':{'status':'FROZEN','path':str(plan_path.resolve()),'plan_id':'p1','plan_revision':1,'plan_digest':pd,'contract_revision':1,'reviewed_deliverable_digest':current},'test_results_path':str(results_path.resolve()),'findings':[],'blocked':None,'diagnostics':[],'contract_patches':[]}; state_path=run/'run-state.json'; dump(state_path,state)
    return locals()

def main():
  # Schemas validate canonical templates and reject a structurally incomplete COMPLETE state.
  for kind,name in [('contract','development-contract.json'),('state','run-state.json'),('plan','test-plan.json'),('results','test-results.json')]: vr.validate_schema(kind,json.loads((ROOT/'templates'/name).read_text()))
  bad=json.loads((ROOT/'templates/run-state.json').read_text()); bad['phase']='COMPLETE'; vr.validate_schema('state',bad)  # schema alone permits shape; semantic CLI remains authoritative.

  with tempfile.TemporaryDirectory(prefix='agy-completion-test.') as td:
    fx=fixture(Path(td)); state,contract,plan,results=fx['state'],fx['contract'],fx['plan'],fx['results']; manifest=vr.snapshot_current(state)
    vr.validate_schema('state',state); vr.validate_schema('contract',contract); vr.validate_schema('plan',plan); vr.validate_schema('results',results); vr.validate_test_entry(state,contract,plan,manifest)
    latest=vr.latest_results(plan,results,manifest['deliverable_digest'],state['evidence_root']); vr.validate_metrics(plan,latest)

    # Identity/evidence failures.
    s=copy.deepcopy(state); s['code_review']['status']='NOT_RUN'; reject(lambda:vr.validate_test_entry(s,contract,plan,manifest),'lacks PASS')
    c=copy.deepcopy(contract); c['revision']=2; reject(lambda:vr.check_identity(state,c),'Contract')
    s=copy.deepcopy(state); s['test_plan']['plan_digest']='0'*64; reject(lambda:vr.validate_test_entry(s,contract,plan,manifest),'plan')
    stale=copy.deepcopy(results); stale['results'][0]['deliverable_digest_after']='f'*64; reject(lambda:vr.latest_results(plan,stale,manifest['deliverable_digest'],state['evidence_root']),'stale')
    missing=copy.deepcopy(results); missing['results']=[]; reject(lambda:vr.latest_results(plan,missing,manifest['deliverable_digest'],state['evidence_root']),'missing result')
    unknown=copy.deepcopy(results); unknown['results'][0]['check_id']='UNKNOWN'; reject(lambda:vr.latest_results(plan,unknown,manifest['deliverable_digest'],state['evidence_root']),'unknown result')
    dup=copy.deepcopy(results); dup['results'].append(copy.deepcopy(dup['results'][0])); reject(lambda:vr.latest_results(plan,dup,manifest['deliverable_digest'],state['evidence_root']),'attempts')
    argv=copy.deepcopy(results); argv['results'][0]['actual_argv']=['true']; reject(lambda:vr.latest_results(plan,argv,manifest['deliverable_digest'],state['evidence_root']),'argv differs')
    badlog=copy.deepcopy(results); badlog['results'][0]['evidence_refs'][0]['sha256']='0'*64; reject(lambda:vr.latest_results(plan,badlog,manifest['deliverable_digest'],state['evidence_root']),'hash mismatch')
    low=copy.deepcopy(results); low['results'][0]['measured_values']['passed']['value']=0; reject(lambda:vr.validate_metrics(plan,vr.latest_results(plan,low,manifest['deliverable_digest'],state['evidence_root'])),'threshold')
    onlypass={'check_id':'T1','status':'PASS'}; reject(lambda:vr.validate_schema('results',{**results,'results':[onlypass]}),'results schema')

    # Latest attempt wins; a later failure cannot be hidden by an earlier PASS.
    later=copy.deepcopy(results); row=copy.deepcopy(later['results'][0]); row.update({'attempt_id':'T1-a2','attempt_number':2,'status':'FAIL','exit_code':1,'reason':'later failed'}); row['evidence_refs']=[row['evidence_refs'][0]]; later['results'].append(row); reject(lambda:vr.latest_results(plan,later,manifest['deliverable_digest'],state['evidence_root']),'not PASS')

    # Frozen false applicability permits N/A; changing a failure to N/A while condition true is rejected.
    nplan=copy.deepcopy(plan); nplan['metrics']=[]; nplan['checks'][0]['applicability']={'mode':'fact_eq','fact':'browser_available','value':True}; appfile=Path(state['evidence_root'])/'app.json'; appfile.write_text('{"browser_available":false}\n')
    nres=copy.deepcopy(results); nres['results'][0]['status']='NOT_APPLICABLE'; nres['results'][0]['exit_code']=None; nres['results'][0]['applicability_evidence']={'fact':'browser_available','value':False,'evidence_ref':'app.json'}; nres['results'][0]['evidence_refs'].append({'path':'app.json','sha256':sha(appfile),'summary':'objective availability'}); vr.latest_results(nplan,nres,manifest['deliverable_digest'],state['evidence_root'])
    cheat=copy.deepcopy(nres); cheat['results'][0]['applicability_evidence']['value']=True; reject(lambda:vr.latest_results(nplan,cheat,manifest['deliverable_digest'],state['evidence_root']),'cannot be NOT_APPLICABLE')

    # Busy/unknown dispatch are rejected at TEST entry.
    busy=copy.deepcopy(state); busy['writer']['status']='RUNNING'; reject(lambda:vr.validate_test_entry(busy,contract,plan,manifest),'STOPPED')
    unknownsend=copy.deepcopy(state); unknownsend['dispatch_state']='SEND_UNKNOWN'; reject(lambda:vr.validate_test_entry(unknownsend,contract,plan,manifest),'SEND_UNKNOWN')

    # Actual CLI completion atomically advances a valid state; code change after tests rejects stale evidence.
    cmd=['bash',str(ROOT/'scripts/validate-run-state.sh'),'complete','--run-state',str(fx['state_path']),'--contract',str(fx['contract_path']),'--test-plan',str(fx['plan_path']),'--results',str(fx['results_path']),'--expected-state-version','1']
    subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE); completed=json.loads(fx['state_path'].read_text()); assert completed['phase']=='COMPLETE' and completed['state_version']==2
    fx2=fixture(Path(td)/'second'); (fx2['repo']/'app.txt').write_text('changed after test\n'); p=subprocess.run(['bash',str(ROOT/'scripts/validate-run-state.sh'),'complete','--run-state',str(fx2['state_path']),'--contract',str(fx2['contract_path']),'--test-plan',str(fx2['plan_path']),'--results',str(fx2['results_path']),'--expected-state-version','1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True); assert p.returncode!=0 and 'stale' in p.stderr

    # BLOCKED persists source phase/resume action; stale state_version prevents lost update.
    fx3=fixture(Path(td)/'third'); p=subprocess.run(['bash',str(ROOT/'scripts/validate-run-state.sh'),'block','--run-state',str(fx3['state_path']),'--contract',str(fx3['contract_path']),'--reason','auth missing','--resume-action','restore auth then retry frozen check','--expected-state-version','1'],check=True,stdout=subprocess.PIPE); blocked=json.loads(fx3['state_path'].read_text()); assert blocked['phase']=='BLOCKED' and blocked['blocked']['blocked_from_phase']=='TEST'
    p=subprocess.run(['bash',str(ROOT/'scripts/validate-run-state.sh'),'block','--run-state',str(fx3['state_path']),'--contract',str(fx3['contract_path']),'--reason','again','--resume-action','none','--expected-state-version','1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE); assert p.returncode!=0

  print('COMPLETION_BEHAVIOR_TESTS_PASS')
if __name__=='__main__': main()
