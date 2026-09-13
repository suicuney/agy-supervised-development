#!/usr/bin/env python3
import hashlib, json, math, os, re, tempfile
from pathlib import Path

HEX64=re.compile(r'^[0-9a-f]{64}$')

def canonical_json_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')

def canonical_digest(obj): return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()

def load_json(path):
    with open(path, encoding='utf-8') as f: return json.load(f)

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def ensure_hex64(value, label='digest'):
    if not isinstance(value,str) or not HEX64.fullmatch(value): raise ValueError(f'{label} must be sha256 hex')

def safe_relpath(value):
    if not isinstance(value,str) or not value or '\x00' in value: raise ValueError('path must be a non-empty string')
    p=Path(value)
    if p.is_absolute() or '..' in p.parts: raise ValueError(f'unsafe relative path: {value}')
    norm=os.path.normpath(value)
    if norm in ('.',''): return '.'
    if norm.startswith('../') or norm=='..': raise ValueError(f'unsafe relative path: {value}')
    return norm

def resolve_under(root, rel, must_exist=False):
    root=Path(root).resolve(); rel=safe_relpath(rel); path=(root/rel).resolve(strict=False)
    try: common=os.path.commonpath([str(root),str(path)])
    except ValueError: raise ValueError(f'path escapes root: {rel}')
    if common!=str(root): raise ValueError(f'path escapes root: {rel}')
    if must_exist and not path.exists(): raise ValueError(f'path missing: {rel}')
    return path

def json_field(obj, path):
    current=obj
    if path.startswith('$.'): path=path[2:]
    elif path=='$': return current
    for part in path.split('.') if path else []:
        if not isinstance(current,dict) or part not in current: raise KeyError(path)
        current=current[part]
    return current

def strict_equal(a,b):
    if type(a) is not type(b): return False
    if isinstance(a,float) and (math.isnan(a) or math.isinf(a)): return False
    if isinstance(b,float) and (math.isnan(b) or math.isinf(b)): return False
    return a==b

def compare_value(actual, op, expected):
    if isinstance(actual,float) and (math.isnan(actual) or math.isinf(actual)): raise ValueError('actual value is not finite')
    if isinstance(expected,float) and (math.isnan(expected) or math.isinf(expected)): raise ValueError('expected value is not finite')
    if op=='eq': return strict_equal(actual, expected)
    if op in ('ge','le'):
        if isinstance(actual,bool) or isinstance(expected,bool) or not isinstance(actual,(int,float)) or not isinstance(expected,(int,float)): raise ValueError(f'{op} requires numeric non-boolean values')
        return actual>=expected if op=='ge' else actual<=expected
    raise ValueError(f'unsupported op: {op}')

def atomic_json_write(path,obj,mode=0o600):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name+'.tmp.',dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(obj,f,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path); dfd=os.open(path.parent, os.O_RDONLY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
