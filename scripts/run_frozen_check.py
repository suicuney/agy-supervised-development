#!/usr/bin/env python3
import argparse, datetime as dt, fcntl, json, os, shutil, subprocess, sys, time, uuid
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from workflow_common import canonical_digest, compare_value, json_field, load_json, resolve_under, sha256_file, atomic_json_write
from snapshot_code_state import snapshot

ROOT=Path(__file__).resolve().parents[1]

def validate(schema_name,obj):
    schema=load_json(ROOT/'schemas'/schema_name)
    errs=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(obj),key=lambda e:list(e.path))
    if errs:
        e=errs[0]; loc='.'.join(str(x) for x in e.absolute_path) or '<root>'
        raise ValueError(f'SCHEMA_INVALID:{schema_name}:{loc}:{e.message}')

def iso_now(): return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')

def typed(value,kind):
    if kind=='boolean':
        if type(value) is not bool: raise ValueError('expected boolean')
    elif kind=='integer':
        if type(value) is not int: raise ValueError('expected integer')
    elif kind=='number':
        if isinstance(value,bool) or not isinstance(value,(int,float)): raise ValueError('expected number')
        import math
        if not math.isfinite(value): raise ValueError('non-finite number')
    elif kind=='string':
        if not isinstance(value,str): raise ValueError('expected string')
    return value

def read_source(repo, spec):
    path=resolve_under(repo,spec['path'],must_exist=True); obj=load_json(path); value=typed(json_field(obj,spec['json_path']),spec['value_type']); return path,value

def evidence_copy(src, attempt_dir, typ, summary):
    src=Path(src); name=f'{len(list(attempt_dir.glob("evidence-*")))+1:02d}-{src.name}'; dst=attempt_dir/name; shutil.copy2(src,dst)
    return {'type':typ,'path':name,'sha256':sha256_file(dst),'summary':summary}

def expand_argv(argv,repo,attempt_dir): return [x.replace('{repo_root}',str(repo)).replace('{attempt_dir}',str(attempt_dir)) for x in argv]

def next_attempt(results,check_id,max_attempts):
    nums=[x['attempt_number'] for x in results.get('attempts',[]) if x['check_id']==check_id]; n=max(nums,default=0)+1
    if n>max_attempts: raise ValueError('MAX_ATTEMPTS_EXCEEDED')
    return n

def initial_results(state,contract,plan,plan_digest):
    return {'schema_version':2,'task_id':state['task_id'],'contract_id':contract['contract_id'],'contract_revision':contract['revision'],'contract_digest':canonical_digest(contract),'policy_digest':state['snapshot_policy']['digest'],'plan_id':plan['plan_id'],'plan_revision':plan['plan_revision'],'plan_digest':plan_digest,'attempts':[]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run-state',required=True); ap.add_argument('--contract',required=True); ap.add_argument('--test-plan',required=True); ap.add_argument('--check-id',required=True); args=ap.parse_args()
    try:
        state_path=Path(args.run_state).resolve(); lock=state_path.with_suffix('.workflow.lock'); lock.parent.mkdir(parents=True,exist_ok=True)
        with open(lock,'a+') as lf:
            fcntl.flock(lf,fcntl.LOCK_EX)
            state=load_json(state_path); contract=load_json(args.contract); plan=load_json(args.test_plan)
            validate('run-state.schema.json',state); validate('development-contract.schema.json',contract); validate('test-plan.schema.json',plan)
            cd=canonical_digest(contract); pd=canonical_digest(plan)
            if state['phase']!='TEST': raise ValueError('PHASE_NOT_TEST')
            if state['contract_digest']!=cd or plan['contract_digest']!=cd: raise ValueError('CONTRACT_DIGEST_MISMATCH')
            if state['snapshot_policy']['digest']!=plan['policy_digest']: raise ValueError('POLICY_DIGEST_MISMATCH')
            if state['test_plan']['status']!='FROZEN' or state['test_plan']['plan_digest']!=pd: raise ValueError('PLAN_DIGEST_MISMATCH')
            checks={c['id']:c for c in plan['checks']}
            if args.check_id not in checks: raise ValueError('UNKNOWN_CHECK_ID')
            check=checks[args.check_id]
            evidence_root=Path(state['evidence_root']).resolve(); evidence_root.mkdir(parents=True,exist_ok=True)
            results_path=Path(state['test_results_path']).resolve() if state['test_results_path'] else evidence_root/'test-results.json'
            results=load_json(results_path) if results_path.exists() else initial_results(state,contract,plan,pd); validate('test-results.schema.json',results)
            n=next_attempt(results,check['id'],check['max_attempts']); attempt_id=f'{check["id"]}-a{n}-{uuid.uuid4().hex[:8]}'; attempt_parent=evidence_root/'attempts'/check['id']; attempt_parent.mkdir(parents=True,exist_ok=True); final_dir=attempt_parent/attempt_id
            if final_dir.exists(): raise ValueError('ATTEMPT_ALREADY_EXISTS')
            tmp=Path(os.path.join(attempt_parent,'.'+attempt_id+'.tmp')); tmp.mkdir(mode=0o700)
            repo=Path(state['working_directory']).resolve(); policy=state['snapshot_policy']['path']; before=snapshot(tmp/'snapshot-before',state['baseline']['commit'],policy,repo)
            if before['policy_digest']!=state['snapshot_policy']['digest']: raise ValueError('POLICY_DIGEST_MISMATCH')
            evidence=[]; env_rows=[]; applicability={'mode':check['applicability']['mode'],'applicable':True}; status='FAIL'; reason='UNSET'; actual_argv=None; exit_code=None; timed_out=False; measured={}; started=iso_now(); t0=time.monotonic()
            if check['applicability']['mode']=='fact_eq':
                src,val=read_source(repo,check['applicability']['source']); expected=check['applicability']['expected']; applicable=(type(val) is type(expected) and val==expected); applicability.update({'applicable':applicable,'actual':val,'expected':expected}); evidence.append(evidence_copy(src,tmp,'applicability','business applicability source'))
            blocked=False
            for pre in check['environment_prerequisites']:
                try:
                    src,val=read_source(repo,pre['source']); ok=compare_value(val,pre['op'],pre['expected']); evidence.append(evidence_copy(src,tmp,'environment',f'environment prerequisite {pre["id"]}'))
                except Exception:
                    val=None; ok=False
                env_rows.append({'id':pre['id'],'satisfied':ok,'actual':val,'expected':pre['expected']}); blocked = blocked or not ok
            if not applicability['applicable']: status='NOT_APPLICABLE'; reason='BUSINESS_NOT_APPLICABLE'
            elif blocked: status='BLOCKED'; reason='ENVIRONMENT_PREREQUISITE_UNMET'
            elif check['type']=='observation':
                src,val=read_source(repo,check['observation']['source']); ok=compare_value(val,check['observation']['op'],check['observation']['expected']); evidence.append(evidence_copy(src,tmp,'observation','structured observation source')); measured['observation.value']={'value':val,'unit':None}; status='PASS' if ok else 'FAIL'; reason='OBSERVATION_MATCH' if ok else 'OBSERVATION_MISMATCH'
            else:
                cwd=resolve_under(repo,check['cwd'],must_exist=True); actual_argv=expand_argv(check['command']['argv'],repo,tmp); outp=tmp/'stdout.log'; errp=tmp/'stderr.log'; env=os.environ.copy(); env['AGY_ATTEMPT_DIR']=str(tmp); env['AGY_REPO_ROOT']=str(repo)
                with open(outp,'wb') as out, open(errp,'wb') as err:
                    proc=subprocess.Popen(actual_argv,cwd=cwd,stdout=out,stderr=err,env=env)
                    try: exit_code=proc.wait(timeout=check['command']['timeout_seconds'])
                    except subprocess.TimeoutExpired: timed_out=True; proc.kill(); exit_code=proc.wait()
                evidence.append({'type':'stdout','path':'stdout.log','sha256':sha256_file(outp),'summary':'captured stdout'}); evidence.append({'type':'stderr','path':'stderr.log','sha256':sha256_file(errp),'summary':'captured stderr'}); report_error=False
                for report in check['structured_reports']:
                    source=tmp/report['path']
                    if not source.is_file(): report_error=True; reason='STRUCTURED_REPORT_MISSING'; continue
                    evidence.append(evidence_copy(source,tmp,'structured_report',f'structured report {report["id"]}')); obj=load_json(source)
                    for field in report['fields']:
                        val=typed(json_field(obj,field['json_path']),field['value_type']); measured[f'{report["id"]}.{field["name"]}']={'value':val,'unit':field.get('unit')}
                if timed_out: status='FAIL'; reason='COMMAND_TIMEOUT'
                elif report_error: status='FAIL'
                elif exit_code not in check['command']['expected_exit_codes']: status='FAIL'; reason='EXIT_CODE_REJECTED'
                else: status='PASS'; reason='COMMAND_ACCEPTED'
            ended=iso_now(); duration=(time.monotonic()-t0)*1000; after=snapshot(tmp/'snapshot-after',state['baseline']['commit'],policy,repo)
            if before['deliverable_digest']!=after['deliverable_digest']: status='FAIL'; reason='DELIVERABLE_CHANGED_DURING_CHECK'
            present_types={x['type'] for x in evidence}; missing=[x for x in check['evidence_types'] if x not in present_types]
            if missing and status=='PASS': status='FAIL'; reason='EVIDENCE_TYPE_MISSING'
            receipt={'schema_version':1,'task_id':state['task_id'],'contract_id':contract['contract_id'],'contract_revision':contract['revision'],'contract_digest':cd,'policy_digest':state['snapshot_policy']['digest'],'plan_id':plan['plan_id'],'plan_revision':plan['plan_revision'],'plan_digest':pd,'check_id':check['id'],'attempt_id':attempt_id,'attempt_number':n,'status':status,'reason_code':reason,'cwd':str(resolve_under(repo,check['cwd'],must_exist=True)),'started_at':started,'ended_at':ended,'duration_ms':duration,'timed_out':timed_out,'actual_argv':actual_argv,'exit_code':exit_code,'deliverable_digest_before':before['deliverable_digest'],'deliverable_digest_after':after['deliverable_digest'],'evidence':evidence,'measured_values':measured,'applicability':applicability,'environment':env_rows}
            validate('test-receipt.schema.json',receipt); atomic_json_write(tmp/'receipt.json',receipt); os.rename(tmp,final_dir); receipt_path=final_dir/'receipt.json'; rel=os.path.relpath(receipt_path,evidence_root)
            results['attempts'].append({'check_id':check['id'],'attempt_id':attempt_id,'attempt_number':n,'receipt_path':rel,'receipt_sha256':sha256_file(receipt_path)}); validate('test-results.schema.json',results); atomic_json_write(results_path,results)
            if state['test_results_path'] is None: state['test_results_path']=str(results_path); state['state_version']+=1; atomic_json_write(state_path,state)
            print(json.dumps({'check_id':check['id'],'attempt_id':attempt_id,'status':status,'reason_code':reason},sort_keys=True)); return 0 if status in ('PASS','NOT_APPLICABLE') else 2
    except Exception as e:
        print(json.dumps({'decision':'REJECTED','reason_code':'RUNNER_ERROR','reason':str(e)},sort_keys=True),file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
