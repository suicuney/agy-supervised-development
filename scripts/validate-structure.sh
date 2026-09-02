#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require_file() { [[ -f "$1" ]] || { printf 'Missing required file: %s\n' "$1" >&2; exit 1; }; }
require_exec() { [[ -x "$1" ]] || { printf 'Script is not executable: %s\n' "$1" >&2; exit 1; }; }

files=(
  "$root/.agents/plugins/marketplace.json"
  "$root/.codex-plugin/plugin.json"
  "$root/skills/agy-supervised-development/SKILL.md"
  "$root/SKILL.md"
  "$root/resources/agy-execution.md"
  "$root/resources/agy-consult.md"
  "$root/resources/review-convergence.md"
  "$root/scripts/agy-run.sh"
  "$root/scripts/validate-structure.sh"
  "$root/scripts/validate-docs.sh"
  "$root/scripts/validate-runtime.sh"
  "$root/scripts/test-readiness.sh"
)
for file in "${files[@]}"; do require_file "$file"; done
for script in "$root/scripts/agy-run.sh" "$root/scripts/validate-structure.sh" "$root/scripts/validate-docs.sh" "$root/scripts/validate-runtime.sh" "$root/scripts/test-readiness.sh"; do require_exec "$script"; done

python3 -m json.tool "$root/.agents/plugins/marketplace.json" >/dev/null
python3 -m json.tool "$root/.codex-plugin/plugin.json" >/dev/null
bash -n "$root/scripts/agy-run.sh"
bash -n "$root/scripts/validate-docs.sh"
bash -n "$root/scripts/validate-runtime.sh"
bash -n "$root/scripts/test-readiness.sh"

python3 - "$root/.agents/plugins/marketplace.json" "$root/.codex-plugin/plugin.json" <<'PY'
import json, sys
marketplace=json.load(open(sys.argv[1], encoding='utf-8'))
plugin=json.load(open(sys.argv[2], encoding='utf-8'))
assert marketplace['name']=='agy-supervised-development'
assert marketplace['plugins'][0]['name']=='agy-supervised-development'
assert marketplace['plugins'][0]['source']['path']=='.'
assert plugin['name']=='agy-supervised-development'
assert plugin['version'].startswith('3.2.')
assert plugin['skills']=='./skills/'
PY

printf 'Structure validation passed.\n'
