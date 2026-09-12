#!/usr/bin/env python3
import argparse, re, sys
from pathlib import Path

FORBIDDEN=[
    (re.compile(r'\bLUNA\s*:'), 'active Luna stage'),
    (re.compile(r'→\s*LUNA\b', re.I), 'active Luna handoff'),
    (re.compile(r'\bLuna\s+(supervises|receives|reviews|verifies|starts|dispatches|may request)\b', re.I), 'active Luna responsibility'),
    (re.compile(r'gpt-5\.6-luna', re.I), 'active Luna model binding'),
    (re.compile(r'resources/(codex-supervisor-handoff|supervisor|verification)\.md'), 'removed 4.0 resource dependency'),
    (re.compile(r'Plan review is enabled by default', re.I), 'default Sol review'),
    (re.compile(r'Three-Axis Review', re.I), 'legacy mandatory review ceremony')]
MIGRATION=re.compile(r'legacy|histor|migration|migrat|removed|remove|superseded|previous|old flow|旧|历史|迁移|移除|已删除|不属于|不再|no default',re.I)

def scan(path):
    text=path.read_text(encoding='utf-8'); section=''
    findings=[]
    for number,line in enumerate(text.splitlines(),1):
        if line.startswith('#'): section=line
        migration=bool(MIGRATION.search(section) or MIGRATION.search(line))
        for pattern,reason in FORBIDDEN:
            if pattern.search(line) and not migration:
                findings.append(f'{path}:{number}: {reason}: {line.strip()}')
    return findings

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='+'); args=ap.parse_args(); findings=[]
    for raw in args.paths:
        path=Path(raw)
        if path.is_dir():
            for child in sorted(path.rglob('*')):
                if child.is_file() and child.suffix.lower() in ('.md','.json'): findings.extend(scan(child))
        elif path.is_file(): findings.extend(scan(path))
    if findings:
        print('Active-role validation failed:',file=sys.stderr)
        for item in findings: print(item,file=sys.stderr)
        return 1
    print('ACTIVE_ROLE_VALID')
    return 0
if __name__=='__main__': raise SystemExit(main())
