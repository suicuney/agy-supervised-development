#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$root/resources/sol-plan-review-manifest.json"
check="$root/scripts/check-sol-plan-review.sh"
installer="$root/scripts/install-sol-plan-review.sh"
tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/sol-plan-review-fixture.XXXXXX")"
trap 'rm -rf "$tmp_root"' EXIT

expect_status() {
  local expected="$1"
  shift
  local output actual
  set +e
  output="$("$@" 2>&1)"
  actual=$?
  set -e
  if [[ "$actual" -ne "$expected" ]]; then
    printf 'Expected exit %s, got %s\n%s\n' "$expected" "$actual" "$output" >&2
    exit 1
  fi
}

skill_root="$tmp_root/skill"
expect_status 10 env SOL_HIGH_PLAN_REVIEW_ROOT="$skill_root" "$check"

mkdir -p "$skill_root"
printf 'fixture\n' > "$skill_root/SKILL.md"
expect_status 11 env SOL_HIGH_PLAN_REVIEW_ROOT="$skill_root" "$check"

python3 - "$manifest" "$skill_root" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
root = Path(sys.argv[2])
for relative_path in manifest["required_paths"]:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("fixture\n", encoding="utf-8")
PY
expect_status 0 env SOL_HIGH_PLAN_REVIEW_ROOT="$skill_root" "$check"

invalid_manifest="$tmp_root/invalid.json"
printf '%s\n' '{"manifest_version":1,"skill_name":"sol-high-plan-review","required_paths":["/absolute"]}' > "$invalid_manifest"
expect_status 12 env SOL_HIGH_PLAN_REVIEW_ROOT="$skill_root" SOL_HIGH_PLAN_REVIEW_MANIFEST="$invalid_manifest" "$check"
printf '%s\n' '{"manifest_version":1,"skill_name":"sol-high-plan-review","required_paths":["a","a"]}' > "$invalid_manifest"
expect_status 12 env SOL_HIGH_PLAN_REVIEW_ROOT="$skill_root" SOL_HIGH_PLAN_REVIEW_MANIFEST="$invalid_manifest" "$check"
printf '%s\n' '{"manifest_version":1,"skill_name":"sol-high-plan-review","required_paths":["../escape"]}' > "$invalid_manifest"
expect_status 12 env SOL_HIGH_PLAN_REVIEW_ROOT="$skill_root" SOL_HIGH_PLAN_REVIEW_MANIFEST="$invalid_manifest" "$check"
printf '%s\n' '{"manifest_version":1,"skill_name":"sol-high-plan-review","required_paths":[]}' > "$invalid_manifest"
expect_status 12 env SOL_HIGH_PLAN_REVIEW_ROOT="$skill_root" SOL_HIGH_PLAN_REVIEW_MANIFEST="$invalid_manifest" "$check"

existing_root="$tmp_root/existing"
mkdir -p "$existing_root"
expect_status 12 env SOL_HIGH_PLAN_REVIEW_ROOT="$existing_root" "$installer"

source_root="$tmp_root/source"
mkdir -p "$source_root"
python3 - "$manifest" "$source_root" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
root = Path(sys.argv[2])
for relative_path in manifest["required_paths"]:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("fixture\n", encoding="utf-8")
PY
git -C "$source_root" init -q -b main
git -C "$source_root" add .
git -C "$source_root" -c user.name=fixture -c user.email=fixture@example.invalid commit -qm fixture

installed_root="$tmp_root/installed"
install_output="$(env SOL_HIGH_PLAN_REVIEW_REPO="$source_root" SOL_HIGH_PLAN_REVIEW_REF=main SOL_HIGH_PLAN_REVIEW_ROOT="$installed_root" "$installer")"
grep -q '^status=COMPLETE$' <<<"$install_output"
grep -q '^source_revision=' <<<"$install_output"
[[ ! -e "$installed_root/.git" ]]

printf 'Sol plan-review dependency fixture checks passed.\n'
