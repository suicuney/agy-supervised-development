#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require_file() { [[ -f "$1" ]] || { printf 'Missing required file: %s\n' "$1" >&2; exit 1; }; }
require_exec() { [[ -x "$1" ]] || { printf 'Script is not executable: %s\n' "$1" >&2; exit 1; }; }
forbid_path() { [[ ! -e "$1" ]] || { printf 'Removed legacy path still exists: %s\n' "$1" >&2; exit 1; }; }

files=(
  "$root/.agents/plugins/marketplace.json"
  "$root/.codex-plugin/plugin.json"
  "$root/skills/agy-supervised-development/SKILL.md"
  "$root/SKILL.md"
  "$root/resources/agy-execution.md"
  "$root/resources/failure-modes.md"
  "$root/resources/sol-plan-review.md"
  "$root/resources/sol-plan-review-manifest.json"
  "$root/resources/review-gates.md"
  "$root/resources/runtime-verification.md"
  "$root/templates/browser-verification.md"
  "$root/scripts/check-herdr.sh"
  "$root/scripts/check-sol-plan-review.sh"
  "$root/scripts/install-sol-plan-review.sh"
  "$root/scripts/test-sol-plan-review.sh"
  "$root/scripts/validate-structure.sh"
  "$root/scripts/validate-docs.sh"
  "$root/scripts/validate-runtime.sh"
  "$root/scripts/test-readiness.sh"
)

for file in "${files[@]}"; do require_file "$file"; done
for script in "$root/scripts/check-herdr.sh" "$root/scripts/check-sol-plan-review.sh" "$root/scripts/install-sol-plan-review.sh" "$root/scripts/test-sol-plan-review.sh" "$root/scripts/validate-structure.sh" "$root/scripts/validate-docs.sh" "$root/scripts/validate-runtime.sh" "$root/scripts/test-readiness.sh"; do require_exec "$script"; done

forbid_path "$root/scripts/agy-run.sh"
forbid_path "$root/resources/tty7-supervision.md"

python3 -m json.tool "$root/.agents/plugins/marketplace.json" >/dev/null
python3 -m json.tool "$root/.codex-plugin/plugin.json" >/dev/null
python3 -m json.tool "$root/resources/sol-plan-review-manifest.json" >/dev/null
bash -n "$root/scripts/check-herdr.sh"
bash -n "$root/scripts/check-sol-plan-review.sh"
bash -n "$root/scripts/install-sol-plan-review.sh"
bash -n "$root/scripts/test-sol-plan-review.sh"
bash -n "$root/scripts/validate-docs.sh"
bash -n "$root/scripts/validate-runtime.sh"
bash -n "$root/scripts/test-readiness.sh"

python3 - "$root/.agents/plugins/marketplace.json" "$root/.codex-plugin/plugin.json" <<'PY'
import json, re, sys
marketplace=json.load(open(sys.argv[1], encoding='utf-8'))
plugin=json.load(open(sys.argv[2], encoding='utf-8'))
assert marketplace['name']=='agy-supervised-development'
assert marketplace['plugins'][0]['name']=='agy-supervised-development'
assert marketplace['plugins'][0]['source']['path']=='.'
assert plugin['name']=='agy-supervised-development'
assert re.fullmatch(r'3\.3\.0-alpha\.2(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?', plugin['version'])
assert plugin['skills']=='./skills/'
assert 'herdr' in plugin['keywords']
PY

printf 'Structure validation passed.\n'
