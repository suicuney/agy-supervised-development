#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_repo="${SOL_HIGH_PLAN_REVIEW_REPO:-https://github.com/suicuney/sol-consult-skill.git}"
source_ref="${SOL_HIGH_PLAN_REVIEW_REF:-main}"
skill_root="${SOL_HIGH_PLAN_REVIEW_ROOT:-${CODEX_HOME:-$HOME/.codex}/skills/sol-high-plan-review}"

if [[ -e "$skill_root" || -L "$skill_root" ]]; then
  printf 'Refusing to overwrite existing destination: %s\n' "$skill_root" >&2
  exit 12
fi

command -v git >/dev/null 2>&1 || { printf 'git was not found on PATH.\n' >&2; exit 127; }
command -v python3 >/dev/null 2>&1 || { printf 'python3 was not found on PATH.\n' >&2; exit 127; }

tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/sol-high-plan-review.XXXXXX")"
cleanup() { rm -rf "$tmp_root"; }
trap cleanup EXIT

source_dir="$tmp_root/source"
if ! git clone --depth 1 --branch "$source_ref" "$source_repo" "$source_dir"; then
  printf 'Full checkout failed; destination was not created: %s\n' "$skill_root" >&2
  exit 1
fi

source_revision="$(git -C "$source_dir" rev-parse HEAD 2>/dev/null || true)"
mkdir -p "$(dirname "$skill_root")"
mkdir "$skill_root"

if ! python3 - "$source_dir" "$skill_root" <<'PY'
from __future__ import annotations

import shutil
import sys
from pathlib import Path


source = Path(sys.argv[1])
destination = Path(sys.argv[2])

for entry in source.iterdir():
    if entry.name == ".git":
        continue
    if entry.is_symlink():
        raise SystemExit(f"source contains unsupported symlink: {entry.name}")
    target = destination / entry.name
    if entry.is_dir():
        shutil.copytree(entry, target)
    else:
        shutil.copy2(entry, target)
PY
then
  printf 'Install incomplete; partial destination retained: %s\n' "$skill_root" >&2
  exit 1
fi

if ! SOL_HIGH_PLAN_REVIEW_ROOT="$skill_root" "$script_dir/check-sol-plan-review.sh"; then
  printf 'Install incomplete; partial destination retained: %s\n' "$skill_root" >&2
  exit 1
fi

printf 'Installed complete sol-high-plan-review skill at %s\n' "$skill_root"
if [[ -n "$source_revision" ]]; then
  printf 'source_revision=%s\n' "$source_revision"
else
  printf 'source_revision=unavailable\n'
fi
