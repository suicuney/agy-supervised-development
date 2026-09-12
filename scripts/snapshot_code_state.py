#!/usr/bin/env python3
import argparse, base64, hashlib, json, os, shutil, stat, subprocess, sys, tempfile
from pathlib import Path

SENSITIVE_NAMES={'.env','.env.local','.env.production','credentials.json','secrets.json'}
SENSITIVE_SUFFIXES={'.pem','.key','.p12','.pfx'}

def run_git(repo,*args,text=False,allow_empty=False):
    p=subprocess.run(['git','-C',str(repo),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode!=0:
        if allow_empty and p.returncode==1 and not p.stdout:
            return '' if text else b''
        raise RuntimeError(f"git {' '.join(args)} failed ({p.returncode}): {p.stderr.decode('utf-8','replace').strip()}")
    return p.stdout.decode('utf-8','strict') if text else p.stdout

def sha256_bytes(data): return hashlib.sha256(data).hexdigest()
def b64(raw): return base64.b64encode(raw).decode('ascii')
def path_record(raw): return {'path_b64':b64(raw),'path_display':os.fsdecode(raw).encode('unicode_escape').decode('ascii')}

def suspicious(raw):
    base=os.path.basename(os.fsdecode(raw).lower())
    return base in SENSITIVE_NAMES or any(base.endswith(s) for s in SENSITIVE_SUFFIXES) or any(k in base for k in ('credential','secret','private-key','api-key'))

def repo_root(cwd):
    p=subprocess.run(['git','-C',cwd,'rev-parse','--show-toplevel'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode!=0: raise RuntimeError('not inside a Git worktree')
    return Path(p.stdout.decode().strip()).resolve()

def git_dir(repo):
    p=Path(run_git(repo,'rev-parse','--git-dir',text=True).strip())
    return (repo/p).resolve() if not p.is_absolute() else p.resolve()

def list_paths(repo):
    raw=run_git(repo,'ls-files','-z','--cached','--others','--exclude-standard')
    return sorted(set(x for x in raw.split(b'\0') if x))

def index_modes(repo):
    raw=run_git(repo,'ls-files','--stage','-z'); out={}
    for rec in [x for x in raw.split(b'\0') if x]:
        meta,path=rec.split(b'\t',1); mode,_,stage=meta.split(b' ',2)
        if stage==b'0': out[path]=mode.decode('ascii')
    return out

def ignored_exact(repo,raw):
    return subprocess.run(['git','-C',str(repo),'check-ignore','-q','--',os.fsdecode(raw)],check=False).returncode==0

def read_regular_stable(path):
    before=os.lstat(path)
    if not stat.S_ISREG(before.st_mode): raise RuntimeError('not regular')
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    try:
        fst=os.fstat(fd); chunks=[]
        while True:
            chunk=os.read(fd,1024*1024)
            if not chunk: break
            chunks.append(chunk)
        after_fd=os.fstat(fd)
    finally: os.close(fd)
    after=os.lstat(path)
    sig=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns)
    if sig(before)!=sig(after) or sig(fst)!=sig(after_fd): raise RuntimeError('file changed during snapshot')
    return b''.join(chunks),before

def deliverable_projection(records):
    projected=[]
    for rec in records:
        item={'path_b64':rec['path_b64'],'type':rec['type'],'executable':rec['executable']}
        if rec['type']=='file':
            item['sha256']=rec['sha256']; item['size']=rec['size']
        elif rec['type']=='symlink':
            item['target_b64']=rec['target_b64']; item['target_sha256']=rec['target_sha256']
        projected.append(item)
    return projected

def capture_manifest(repo,include_ignored,allow_sensitive,archive_dir=None):
    modes=index_modes(repo); paths=list_paths(repo)
    for raw in include_ignored:
        if raw not in paths:
            if not ignored_exact(repo,raw): raise RuntimeError(f'include-ignored path not found/ignored: {os.fsdecode(raw)}')
            paths.append(raw)
    paths=sorted(set(paths)); records=[]; tracked=set(modes)
    if archive_dir: (archive_dir/'untracked-blobs').mkdir(parents=True,exist_ok=True)
    for raw in paths:
        if modes.get(raw)=='160000': raise RuntimeError(f'submodule unsupported for snapshot: {os.fsdecode(raw)}')
        full=repo/os.fsdecode(raw)
        try: st=os.lstat(full)
        except FileNotFoundError: raise RuntimeError(f'file disappeared during snapshot: {os.fsdecode(raw)}')
        rec=path_record(raw); rec['tracked']=raw in tracked; rec['index_mode']=modes.get(raw)
        if stat.S_ISLNK(st.st_mode):
            target_raw=os.fsencode(os.readlink(full))
            rec.update({'type':'symlink','target_b64':b64(target_raw),'target_sha256':sha256_bytes(target_raw),'executable':False})
        elif stat.S_ISREG(st.st_mode):
            data,stable=read_regular_stable(full); digest=sha256_bytes(data)
            rec.update({'type':'file','sha256':digest,'size':len(data),'executable':bool(stable.st_mode&stat.S_IXUSR)})
            if raw not in tracked:
                if suspicious(raw) and raw not in allow_sensitive:
                    raise RuntimeError(f'sensitive-looking untracked file requires explicit allow: {os.fsdecode(raw)}')
                rec['archive_blob']=f'untracked-blobs/{digest}'
                if archive_dir:
                    blob=archive_dir/'untracked-blobs'/digest
                    if not blob.exists():
                        fd=os.open(blob,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
                        with os.fdopen(fd,'wb') as f: f.write(data)
        else:
            raise RuntimeError(f'unsupported file type: {os.fsdecode(raw)}')
        records.append(rec)
    payload=json.dumps(deliverable_projection(records),sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
    return records,sha256_bytes(payload)

def capture(args):
    repo=repo_root(os.getcwd()); gd=git_dir(repo); out=Path(args.output)
    if not out.is_absolute(): out=(Path.cwd()/out).resolve()
    try: in_repo=os.path.commonpath([str(out),str(repo)])==str(repo)
    except ValueError: in_repo=False
    in_git=os.path.commonpath([str(out),str(gd)])==str(gd)
    if in_repo and not in_git: raise RuntimeError('snapshot output must be outside worktree or under Git-private directory')
    out.parent.mkdir(parents=True,exist_ok=True); os.chmod(out.parent,0o700)
    tmp=Path(tempfile.mkdtemp(prefix='snapshot.tmp.',dir=out.parent)); os.chmod(tmp,0o700)
    try:
        include=[os.fsencode(p) for p in args.include_ignored]; allow={os.fsencode(p) for p in args.allow_sensitive_untracked}
        records1,digest1=capture_manifest(repo,include,allow,tmp)
        head=run_git(repo,'rev-parse','HEAD',text=True).strip()
        branch=run_git(repo,'symbolic-ref','--short','-q','HEAD',text=True,allow_empty=True).strip()
        baseline=args.baseline_commit or ''
        if baseline: run_git(repo,'rev-parse','--verify',f'{baseline}^{{commit}}')
        artifacts={
          'status.porcelain-v2.z':run_git(repo,'status','--porcelain=v2','-z','--branch'),
          'diff-cached.patch':run_git(repo,'diff','--binary','--find-renames','--cached'),
          'diff-worktree.patch':run_git(repo,'diff','--binary','--find-renames'),
          'diff-head.patch':run_git(repo,'diff','--binary','--find-renames','HEAD'),
          'diff-baseline-to-head.patch':run_git(repo,'diff','--binary','--find-renames',f'{baseline}..HEAD') if baseline else b''}
        for name,data in artifacts.items(): (tmp/name).write_bytes(data)
        records2,digest2=capture_manifest(repo,include,allow,None)
        if digest1!=digest2 or records1!=records2: raise RuntimeError('repository changed during snapshot stability window')
        ownership_payload=b'HEAD='+head.encode()+b'\nBRANCH='+branch.encode()+b'\nBASELINE='+baseline.encode()+b'\n'+artifacts['status.porcelain-v2.z']
        manifest={'format_version':2,'repo_root':str(repo),'head':head,'branch':branch or None,'baseline_commit':baseline or None,'deliverable_digest':digest2,'ownership_digest':sha256_bytes(ownership_payload),'files':records2,'stability_check':'two observed manifests matched; this detects changes during the capture window but is not OS-level isolation','ignored_policy':'ignored files are excluded unless passed with --include-ignored; acceptance inputs must be explicitly included'}
        (tmp/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
        (tmp/'deliverable.sha256').write_text(digest2+'\n'); (tmp/'ownership.sha256').write_text(manifest['ownership_digest']+'\n')
        if out.exists(): shutil.rmtree(out)
        os.replace(tmp,out)
        print(f'SNAPSHOT_READY={out}'); print(f'DELIVERABLE_DIGEST={digest2}'); print(f'OWNERSHIP_DIGEST={manifest["ownership_digest"]}')
    except Exception:
        shutil.rmtree(tmp,ignore_errors=True); raise

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('output'); ap.add_argument('baseline_commit',nargs='?',default='')
    ap.add_argument('--include-ignored',action='append',default=[]); ap.add_argument('--allow-sensitive-untracked',action='append',default=[])
    args=ap.parse_args()
    try: capture(args)
    except Exception as e:
        print(f'SNAPSHOT_FAILED: {e}',file=sys.stderr); return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
