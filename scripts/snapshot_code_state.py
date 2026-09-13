#!/usr/bin/env python3
import argparse, base64, hashlib, json, os, shutil, stat, subprocess, sys, tempfile
from pathlib import Path
from workflow_common import canonical_digest, load_json, safe_relpath, sha256_file, atomic_json_write

SENSITIVE_NAMES={'.env','.env.local','.npmrc','.pypirc','id_rsa','id_ed25519','credentials.json','service-account.json'}
SENSITIVE_SUFFIXES={'.pem','.key','.p12','.pfx'}

def git(repo,*args,text=False):
    p=subprocess.run(['git','-C',str(repo),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=text)
    if p.returncode:
        raise RuntimeError(f'git {" ".join(args)} failed: {(p.stderr if text else p.stderr.decode(errors="replace")).strip()}')
    return p.stdout

def repo_info(cwd=None):
    cwd=Path(cwd or Path.cwd())
    root=Path(git(cwd,'rev-parse','--show-toplevel',text=True).strip()).resolve()
    gitdir_text=git(root,'rev-parse','--git-dir',text=True).strip()
    gitdir=(root/gitdir_text).resolve() if not os.path.isabs(gitdir_text) else Path(gitdir_text).resolve()
    return root,gitdir

def decode_z(data): return [x for x in data.split(b'\0') if x]
def b64(data): return base64.b64encode(data).decode('ascii')
def path_b64(rel): return b64(os.fsencode(rel))
def rel_from_bytes(raw): return os.fsdecode(raw)

def validate_policy(policy, root):
    if policy.get('schema_version')!=1: raise ValueError('unsupported snapshot policy schema')
    out={'schema_version':1,'include_ignored':[],'allow_sensitive_untracked':[]}
    for key in ('include_ignored','allow_sensitive_untracked'):
        seen=set()
        for value in policy.get(key,[]):
            norm=safe_relpath(value)
            if norm=='.': raise ValueError(f'{key} cannot contain repository root')
            if norm in seen: raise ValueError(f'duplicate {key} path: {norm}')
            seen.add(norm); out[key].append(norm)
        out[key].sort(key=lambda s:os.fsencode(s))
    return out

def default_policy(): return {'schema_version':1,'include_ignored':[],'allow_sensitive_untracked':[]}

def is_sensitive(rel):
    p=Path(rel); lower=p.name.lower()
    return lower in SENSITIVE_NAMES or p.suffix.lower() in SENSITIVE_SUFFIXES or any(tok in lower for tok in ('secret','credential','token'))

def index_entries(root):
    raw=git(root,'ls-files','-z','--stage'); entries={}; submodules=[]
    for rec in decode_z(raw):
        meta,path=rec.split(b'\t',1); mode,oid,stage=meta.split(b' ',2); rel=rel_from_bytes(path)
        if mode==b'160000': submodules.append(rel)
        entries[rel]={'index_mode':mode.decode(),'oid':oid.decode(),'stage':int(stage)}
    if submodules: raise RuntimeError('submodules unsupported: '+', '.join(submodules))
    return entries

def exact_ignored(root, policy):
    out=[]
    for rel in policy['include_ignored']:
        p=root/rel; chk=subprocess.run(['git','-C',str(root),'check-ignore','-q','--',rel])
        if chk.returncode!=0: raise RuntimeError(f'policy include_ignored path is not ignored: {rel}')
        if not os.path.lexists(p): raise RuntimeError(f'policy include_ignored path missing: {rel}')
        out.append(rel)
    return out

def actual_untracked(root): return [rel_from_bytes(x) for x in decode_z(git(root,'ls-files','--others','--exclude-standard','-z'))]

def file_record(root,rel,tracked,index_meta,archive_dir,archive_untracked):
    full=root/rel
    try: st=os.lstat(full)
    except FileNotFoundError: return None
    record={'path_b64':path_b64(rel),'tracked':tracked,'index_mode':index_meta.get('index_mode') if index_meta else None,'kind':None,'executable':bool(st.st_mode & stat.S_IXUSR),'archive_blob':None}
    if stat.S_ISLNK(st.st_mode):
        target=os.readlink(full); raw=os.fsencode(target)
        record.update({'kind':'symlink','target_b64':b64(raw),'content_sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)})
    elif stat.S_ISREG(st.st_mode):
        digest=sha256_file(full); record.update({'kind':'file','content_sha256':digest,'size':st.st_size})
        if archive_untracked:
            archive_dir.mkdir(parents=True,exist_ok=True); blob=archive_dir/digest
            if not blob.exists():
                with open(full,'rb') as src, open(blob,'xb') as dst: shutil.copyfileobj(src,dst); dst.flush(); os.fsync(dst.fileno())
                os.chmod(blob,0o600)
            record['archive_blob']=str(Path('archive')/digest)
    elif stat.S_ISDIR(st.st_mode): return None
    else: raise RuntimeError(f'unsupported file type: {rel}')
    return record

def deliverable_view(records):
    out=[]
    for r in records:
        item={'path_b64':r['path_b64'],'kind':r['kind'],'executable':r['executable'],'content_sha256':r['content_sha256']}
        if r['kind']=='symlink': item['target_b64']=r['target_b64']
        out.append(item)
    return out

def capture_manifest(root, policy, archive_dir):
    idx=index_entries(root); tracked=sorted(idx.keys(),key=lambda s:os.fsencode(s)); untracked=sorted(set(actual_untracked(root)+exact_ignored(root,policy)),key=lambda s:os.fsencode(s)); allowed_sensitive=set(policy['allow_sensitive_untracked'])
    records=[]; absent=[]
    for rel in tracked:
        rec=file_record(root,rel,True,idx[rel],archive_dir,False)
        if rec is None: absent.append({'path_b64':path_b64(rel),'index_mode':idx[rel]['index_mode']})
        else: records.append(rec)
    for rel in untracked:
        if is_sensitive(rel) and rel not in allowed_sensitive: raise RuntimeError(f'sensitive untracked path requires exact policy authorization: {rel}')
        rec=file_record(root,rel,False,None,archive_dir,True)
        if rec is None: raise RuntimeError(f'untracked path disappeared during snapshot: {rel}')
        records.append(rec)
    records.sort(key=lambda r:base64.b64decode(r['path_b64'])); absent.sort(key=lambda r:base64.b64decode(r['path_b64']))
    return records,absent,canonical_digest(deliverable_view(records))

def status_digest(root, head, records, absent, policy_digest):
    cached=git(root,'diff','--cached','--binary'); worktree=git(root,'diff','--binary'); status=git(root,'status','--porcelain=v2','-z','--untracked-files=all')
    obj={'head':head,'policy_digest':policy_digest,'cached_sha256':hashlib.sha256(cached).hexdigest(),'worktree_sha256':hashlib.sha256(worktree).hexdigest(),'status_sha256':hashlib.sha256(status).hexdigest(),'tracked_absent':absent,'index':[{'path_b64':r['path_b64'],'index_mode':r['index_mode']} for r in records if r['tracked']]}
    return canonical_digest(obj),cached,worktree,status

def ensure_safe_output(out, root, gitdir):
    out=Path(out)
    if out.exists() or out.is_symlink(): raise RuntimeError(f'snapshot output already exists: {out}')
    raw_abs=Path(os.path.abspath(out)); parent=out.parent.resolve(); candidate=(parent/out.name).resolve(strict=False)
    if candidate==root or candidate==gitdir: raise RuntimeError('dangerous snapshot output path')
    try:
        lexical_in_repo=os.path.commonpath([str(root),str(raw_abs)])==str(root); lexical_in_git=os.path.commonpath([str(gitdir),str(raw_abs)])==str(gitdir)
    except ValueError: lexical_in_repo=lexical_in_git=False
    try:
        resolved_in_repo=os.path.commonpath([str(root),str(candidate)])==str(root); resolved_in_git=os.path.commonpath([str(gitdir),str(candidate)])==str(gitdir)
    except ValueError: resolved_in_repo=resolved_in_git=False
    if lexical_in_repo and not resolved_in_repo: raise RuntimeError('snapshot output escapes repository through symlink')
    if lexical_in_git and not resolved_in_git: raise RuntimeError('snapshot output escapes Git private root through symlink')
    if resolved_in_repo and not resolved_in_git: raise RuntimeError('snapshot output inside working tree is forbidden')
    if parent.exists() and parent.is_symlink(): raise RuntimeError('snapshot output parent may not be a symlink')
    parent.mkdir(parents=True,exist_ok=True)
    return candidate

def write_bytes(path,data):
    with open(path,'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())

def snapshot(out, baseline_commit='', policy_path=None, repo_cwd=None):
    root,gitdir=repo_info(repo_cwd); out=ensure_safe_output(out,root,gitdir)
    policy=validate_policy(load_json(policy_path) if policy_path else default_policy(),root); pd=canonical_digest(policy); head=git(root,'rev-parse','HEAD',text=True).strip()
    if baseline_commit: git(root,'rev-parse','--verify',f'{baseline_commit}^{{commit}}')
    tmp=Path(tempfile.mkdtemp(prefix=out.name+'.tmp.',dir=out.parent)); os.chmod(tmp,0o700)
    try:
        archive=tmp/'archive'; records1,absent1,deliver1=capture_manifest(root,policy,archive); owner1,cached,worktree,status=status_digest(root,head,records1,absent1,pd)
        records2,absent2,deliver2=capture_manifest(root,policy,archive); owner2,_,_,_=status_digest(root,head,records2,absent2,pd)
        if deliver1!=deliver2 or owner1!=owner2 or records1!=records2 or absent1!=absent2: raise RuntimeError('repository changed during snapshot')
        branch=git(root,'symbolic-ref','--short','-q','HEAD',text=True).strip()
        manifest={'schema_version':2,'repo_root':str(root),'head':head,'branch':branch or None,'baseline_commit':baseline_commit or None,'policy':policy,'policy_digest':pd,'deliverable_digest':deliver1,'ownership_digest':owner1,'files':records1,'tracked_absent':absent1}
        atomic_json_write(tmp/'manifest.json',manifest); write_bytes(tmp/'manifest.sha256',(sha256_file(tmp/'manifest.json')+'\n').encode()); write_bytes(tmp/'diff-cached.patch',cached); write_bytes(tmp/'diff-worktree.patch',worktree); write_bytes(tmp/'status.porcelain-v2.z',status)
        write_bytes(tmp/'diff-baseline-to-head.patch',git(root,'diff','--binary',f'{baseline_commit}..HEAD') if baseline_commit else b'')
        os.rename(tmp,out); dfd=os.open(out.parent,os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
        return manifest
    except Exception:
        shutil.rmtree(tmp,ignore_errors=True); raise

def verify_snapshot_dir(path):
    path=Path(path); manifest=load_json(path/'manifest.json'); recorded=(path/'manifest.sha256').read_text().strip()
    if sha256_file(path/'manifest.json')!=recorded: raise RuntimeError('snapshot manifest hash mismatch')
    for r in manifest.get('files',[]):
        blob=r.get('archive_blob')
        if blob:
            bp=path/blob
            if not bp.is_file(): raise RuntimeError(f'snapshot archive missing: {blob}')
            if sha256_file(bp)!=r['content_sha256']: raise RuntimeError(f'snapshot archive corrupt: {blob}')
    return manifest

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('output'); ap.add_argument('baseline_commit',nargs='?',default=''); ap.add_argument('--policy'); args=ap.parse_args()
    try:
        m=snapshot(args.output,args.baseline_commit,args.policy); print('SNAPSHOT_OK'); print('DELIVERABLE_DIGEST='+m['deliverable_digest']); print('OWNERSHIP_DIGEST='+m['ownership_digest']); print('POLICY_DIGEST='+m['policy_digest']); return 0
    except Exception as e:
        print(f'SNAPSHOT_REJECTED: {e}',file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
