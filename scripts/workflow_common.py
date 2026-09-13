#!/usr/bin/env python3
import hashlib, json, os, re, tempfile
from pathlib import Path

HEX64=re.compile(r'^[0-9a-f]{64}$')

def canonical_json_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')

def canonical_digest(obj):
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()

def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def safe_relpath(value):
    if not isinstance(value,str) or not value or '\x00' in value:
        raise ValueError('path must be a non-empty string')
    p=Path(value)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError(f'unsafe relative path: {value}')
    norm=os.path.normpath(value)
    if norm in ('.',''):
        return '.'
    if norm.startswith('../') or norm=='..':
        raise ValueError(f'unsafe relative path: {value}')
    return norm

def resolve_under(root, rel, must_exist=False):
    root=Path(root).resolve()
    rel=safe_relpath(rel)
    path=(root/rel).resolve(strict=False)
    try:
        common=os.path.commonpath([str(root),str(path)])
    except ValueError:
        raise ValueError(f'path escapes root: {rel}')
    if common!=str(root):
        raise ValueError(f'path escapes root: {rel}')
    if must_exist and not path.exists():
        raise ValueError(f'path missing: {rel}')
    return path

def atomic_json_write(path,obj,mode=0o600):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+'.tmp.',dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(obj,f,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)
            f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
        dfd=os.open(path.parent, os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
