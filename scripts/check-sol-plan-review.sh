#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="${SOL_HIGH_PLAN_REVIEW_MANIFEST:-$root/resources/sol-plan-review-manifest.json}"
skill_root="${SOL_HIGH_PLAN_REVIEW_ROOT:-${CODEX_HOME:-$HOME/.codex}/skills/sol-high-plan-review}"

python3 - "$manifest" "$skill_root" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path, PurePosixPath


COMPLETE = 0
MISSING = 10
INCOMPLETE = 11
INVALID_MANIFEST = 12


def invalid(message: str) -> int:
    print(f"status=INVALID_MANIFEST\nmessage={message}")
    return INVALID_MANIFEST


manifest_path = Path(sys.argv[1])
skill_path = Path(sys.argv[2]).expanduser()

if not manifest_path.is_file():
    raise SystemExit(invalid(f"manifest not found: {manifest_path}"))

try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    raise SystemExit(invalid(f"cannot read manifest: {exc}"))

if not isinstance(manifest, dict):
    raise SystemExit(invalid("manifest root must be an object"))
if manifest.get("manifest_version") != 1:
    raise SystemExit(invalid("manifest_version must be 1"))
if manifest.get("skill_name") != "sol-high-plan-review":
    raise SystemExit(invalid("skill_name must be sol-high-plan-review"))

required_paths = manifest.get("required_paths")
if not isinstance(required_paths, list) or not required_paths:
    raise SystemExit(invalid("required_paths must be a non-empty list"))

normalized_paths: list[str] = []
seen: set[str] = set()
for raw_path in required_paths:
    if not isinstance(raw_path, str) or not raw_path:
        raise SystemExit(invalid("required_paths must contain non-empty strings"))
    if "\\" in raw_path:
        raise SystemExit(invalid(f"backslash path is not allowed: {raw_path}"))
    path = PurePosixPath(raw_path)
    if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
        raise SystemExit(invalid(f"path must be relative and confined: {raw_path}"))
    normalized = path.as_posix()
    if normalized in seen:
        raise SystemExit(invalid(f"duplicate required path: {raw_path}"))
    seen.add(normalized)
    normalized_paths.append(normalized)

if not skill_path.exists():
    print(f"status=MISSING\nskill_root={skill_path}")
    raise SystemExit(MISSING)
if not skill_path.is_dir():
    print(f"status=INCOMPLETE\nskill_root={skill_path}\nmessage=skill root is not a directory")
    raise SystemExit(INCOMPLETE)

missing_paths = []
for relative_path in normalized_paths:
    candidate = skill_path / Path(relative_path)
    current = skill_path
    symlinked = False
    for component in Path(relative_path).parts:
        current = current / component
        if current.is_symlink():
            symlinked = True
            break
    if symlinked or not candidate.is_file():
        missing_paths.append(relative_path)

if missing_paths:
    print("status=INCOMPLETE")
    print(f"skill_root={skill_path}")
    print("missing_paths=" + ",".join(missing_paths))
    raise SystemExit(INCOMPLETE)

revision = ""
try:
    result = subprocess.run(
        ["git", "-C", str(skill_path), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        revision = result.stdout.strip()
except OSError:
    pass

print("status=COMPLETE")
print(f"skill_root={skill_path}")
print(f"required_paths={len(normalized_paths)}")
if revision:
    print(f"source_revision={revision}")
else:
    print("source_revision=unavailable")
PY
