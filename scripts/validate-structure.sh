#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
require_file(){ [[ -f "$1" ]] || { echo "Missing required file: $1" >&2; exit 1; }; }
forbid_file(){ [[ ! -e "$1" ]] || { echo "Removed active file still exists: $1" >&2; exit 1; }; }

files=(
 "$root/.agents/plugins/marketplace.json" "$root/.codex-plugin/plugin.json" "$root/SKILL.md" "$root/README.md" "$root/CHANGELOG.md"
 "$root/skills/agy-supervised-development/SKILL.md" "$root/requirements-validation.txt"
 "$root/resources/development-contract.md" "$root/resources/run-state.md" "$root/resources/agy-execution.md" "$root/resources/code-review.md" "$root/resources/testing.md"
 "$root/schemas/development-contract.schema.json" "$root/schemas/run-state.schema.json" "$root/schemas/test-plan.schema.json" "$root/schemas/test-results.schema.json"
 "$root/templates/development-contract.json" "$root/templates/run-state.json" "$root/templates/test-plan.json" "$root/templates/test-results.json" "$root/templates/test-plan.md"
 "$root/scripts/snapshot-code-state.sh" "$root/scripts/snapshot_code_state.py" "$root/scripts/validate-run-state.sh" "$root/scripts/validate_run_state.py"
 "$root/scripts/validate_active_roles.py" "$root/scripts/test-doc-role-validation.sh" "$root/scripts/test-snapshot-behavior.py" "$root/scripts/test-completion-behavior.py"
 "$root/scripts/validate-workflow.sh" "$root/scripts/validate-docs.sh" "$root/scripts/validate-runtime.sh" "$root/scripts/test-readiness.sh" "$root/evals/scenarios.json"
)
for f in "${files[@]}"; do require_file "$f"; done
for f in "$root/resources/codex-supervisor-handoff.md" "$root/resources/supervisor.md" "$root/resources/verification.md" "$root/resources/sol-plan-review.md"; do forbid_file "$f"; done

python3 -c 'import jsonschema' >/dev/null 2>&1 || { echo 'Missing required Python dependency: jsonschema; install requirements-validation.txt' >&2; exit 2; }
for f in "$root/.agents/plugins/marketplace.json" "$root/.codex-plugin/plugin.json" "$root/schemas/"*.json "$root/templates/"*.json "$root/evals/scenarios.json"; do python3 -m json.tool "$f" >/dev/null; done
for f in check-herdr.sh snapshot-code-state.sh validate-run-state.sh test-doc-role-validation.sh validate-workflow.sh validate-docs.sh validate-runtime.sh test-readiness.sh; do bash -n "$root/scripts/$f"; done
python3 -m py_compile "$root/scripts/snapshot_code_state.py" "$root/scripts/validate_run_state.py" "$root/scripts/validate_active_roles.py" "$root/scripts/test-snapshot-behavior.py" "$root/scripts/test-completion-behavior.py"

python3 - "$root" <<'PY'
import json,sys
from pathlib import Path
from jsonschema import Draft202012Validator
r=Path(sys.argv[1])
for schema_name,template_name in [
 ('development-contract.schema.json','development-contract.json'),('run-state.schema.json','run-state.json'),('test-plan.schema.json','test-plan.json'),('test-results.schema.json','test-results.json')]:
 schema=json.load(open(r/'schemas'/schema_name)); data=json.load(open(r/'templates'/template_name)); Draft202012Validator(schema).validate(data)
p=json.load(open(r/'.codex-plugin/plugin.json')); e=json.load(open(r/'evals/scenarios.json'))
assert p['version']=='4.1.0-alpha.2'; assert e['version']=='4.1.0-alpha.2'; assert 'luna' not in p['keywords']
PY
printf 'STATIC_STRUCTURE_VALID\n'
