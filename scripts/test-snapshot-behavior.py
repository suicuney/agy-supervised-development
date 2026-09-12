#!/usr/bin/env python3
import importlib.util, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('snapshot',ROOT/'scripts/snapshot_code_state.py'); snap=importlib.util.module_from_spec(spec); spec.loader.exec_module(snap)

def git(repo,*args,check=True): return subprocess.run(['git','-C',str(repo),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check)
def init_repo(base):
    repo=base/'repo'; repo.mkdir(parents=True); git(repo,'init','-q'); git(repo,'config','user.email','test@example.invalid'); git(repo,'config','user.name','test')
    (repo/'tracked.txt').write_text('base\n'); git(repo,'add','tracked.txt'); git(repo,'commit','-qm','base'); return repo
def capture(repo,out,baseline='',extra=None):
    argv=['snapshot_code_state.py',str(out)]+([baseline] if baseline else [])+(extra or []); old=os.getcwd(); os.chdir(repo); oldargv=sys.argv
    try: sys.argv=argv; rc=snap.main()
    finally: sys.argv=oldargv; os.chdir(old)
    if rc: raise AssertionError(f'snapshot failed: {argv}')
    return json.loads((out/'manifest.json').read_text())
def must_fail(repo,out,extra=None):
    argv=['snapshot_code_state.py',str(out)]+(extra or []); old=os.getcwd(); os.chdir(repo); oldargv=sys.argv
    try: sys.argv=argv; rc=snap.main()
    finally: sys.argv=oldargv; os.chdir(old)
    assert rc!=0

def main():
  with tempfile.TemporaryDirectory(prefix='agy-snapshot-test.') as td:
    base=Path(td); repo=init_repo(base); baseline=git(repo,'rev-parse','HEAD').stdout.decode().strip(); gitdir=repo/'.git'/'agy-supervised'; gitdir.mkdir()

    # Dirty user baseline is attributable and untracked original bytes are recoverable.
    (repo/'tracked.txt').write_text('base\nstaged\n'); git(repo,'add','tracked.txt'); (repo/'tracked.txt').write_text('base\nstaged\nunstaged\n')
    special='sp ace-\u96ea-\nname.bin'; (repo/special).write_bytes(b'\x00\xffuser')
    bcap=capture(repo,gitdir/'baseline',baseline); rec=next(x for x in bcap['files'] if os.fsdecode(__import__('base64').b64decode(x['path_b64']))==special)
    assert rec['tracked'] is False and rec['archive_blob']; assert (gitdir/'baseline'/rec['archive_blob']).read_bytes()==b'\x00\xffuser'
    (repo/'task.txt').write_text('task\n'); git(repo,'add','task.txt'); git(repo,'commit','-qm','task','--','task.txt')
    acap=capture(repo,gitdir/'after',baseline); assert (gitdir/'after'/'diff-baseline-to-head.patch').stat().st_size>0
    status=(gitdir/'after'/'status.porcelain-v2.z').read_bytes(); assert b'tracked.txt' in status and os.fsencode(special) in status

    # Content identity catches dangling symlink target, binary, rename and executable mode.
    os.symlink('missing-a',repo/'link'); d1=capture(repo,gitdir/'s1')['deliverable_digest']; (repo/'link').unlink(); os.symlink('missing-b',repo/'link'); d2=capture(repo,gitdir/'s2')['deliverable_digest']; assert d1!=d2
    (repo/'bin.dat').write_bytes(b'\x00A'); d3=capture(repo,gitdir/'s3')['deliverable_digest']; (repo/'bin.dat').write_bytes(b'\x00B'); d4=capture(repo,gitdir/'s4')['deliverable_digest']; assert d3!=d4
    (repo/'mode.sh').write_text('#!/bin/sh\n'); d5=capture(repo,gitdir/'s5')['deliverable_digest']; os.chmod(repo/'mode.sh',0o755); d6=capture(repo,gitdir/'s6')['deliverable_digest']; assert d5!=d6
    (repo/'rename-a').write_text('x'); d7=capture(repo,gitdir/'s7')['deliverable_digest']; os.rename(repo/'rename-a',repo/'rename-b'); d8=capture(repo,gitdir/'s8')['deliverable_digest']; assert d7!=d8

    # Root/subdir are identical; git add changes ownership but not deliverable identity.
    (repo/'sub').mkdir(); (repo/'sub'/'new.txt').write_text('same'); rootcap=capture(repo,gitdir/'root')
    old=os.getcwd(); os.chdir(repo/'sub')
    try: subcap=capture(repo/'sub',gitdir/'subcap')
    finally: os.chdir(old)
    assert rootcap['deliverable_digest']==subcap['deliverable_digest']
    before_deliverable=rootcap['deliverable_digest']; before_owner=rootcap['ownership_digest']; git(repo,'add','sub/new.txt'); staged=capture(repo,gitdir/'staged')
    assert staged['deliverable_digest']==before_deliverable and staged['ownership_digest']!=before_owner

    # Evidence under Git-private storage does not pollute deliverable; real test/source changes do.
    evidence=gitdir/'evidence'; evidence.mkdir(); (evidence/'report.log').write_text('report'); same=capture(repo,gitdir/'evidence-cap'); assert same['deliverable_digest']==staged['deliverable_digest']
    (repo/'test_assertions.py').write_text('assert 1 == 1\n'); changed=capture(repo,gitdir/'source-cap'); assert changed['deliverable_digest']!=same['deliverable_digest']

    # Ignored input is explicit; sensitive/worktree-output/unsupported submodule fail closed.
    (repo/'.gitignore').write_text('ignored.txt\n'); (repo/'ignored.txt').write_text('input'); default=capture(repo,gitdir/'ignored-default'); included=capture(repo,gitdir/'ignored-included',extra=['--include-ignored','ignored.txt']); assert default['deliverable_digest']!=included['deliverable_digest']
    (repo/'.env').write_text('SECRET=x'); must_fail(repo,gitdir/'sensitive'); assert capture(repo,gitdir/'sensitive-ok',extra=['--allow-sensitive-untracked','.env']); (repo/'.env').unlink()
    must_fail(repo,repo/'snapshot-inside-worktree')
    head=git(repo,'rev-parse','HEAD').stdout.decode().strip(); git(repo,'update-index','--add','--cacheinfo',f'160000,{head},submodule-placeholder'); must_fail(repo,gitdir/'submodule'); git(repo,'rm','--cached','-q','submodule-placeholder')

    # Concurrency/stability detection rejects publication when observed manifests differ.
    original=snap.capture_manifest; calls={'n':0}
    def unstable(*args,**kwargs):
        records,digest=original(*args,**kwargs); calls['n']+=1; return records,(digest if calls['n']==1 else '0'*64)
    snap.capture_manifest=unstable
    try: must_fail(repo,gitdir/'unstable')
    finally: snap.capture_manifest=original
    assert not (gitdir/'unstable').exists()

  print('SNAPSHOT_BEHAVIOR_TESTS_PASS')
if __name__=='__main__': main()
