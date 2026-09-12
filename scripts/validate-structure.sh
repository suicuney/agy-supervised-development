#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require_file() { [[ -f "$1" ]] || { printf 'Missing required file: %s\n' "$1" >&2; exit 1; }; }
require_exec() { [[ -x "$1" ]] || { printf 'Script is not executable: %s\n' "$1" >&2; exit 1; }; }
forbid_file() { [[ ! -e "$1" ]] || { printf 'Legacy active file must be removed: %s\n' "$1" >&2; exit 1; }; }

files=(
  "$root/.agents/plugins/marketplace.json"
  "$root/.codex-plugin/plugin.json"
  "$root/skills/agy-supervised-development/SKILL.md"
  "$root/SKILL.md"
  "$root/README.md"
  "$root/CHANGELOG.md"
  "$root/legacy/README.md"
  "$root/resources/development-contract.md"
  "$root/resources/codex-supervisor-handoff.md"
  "$root/resources/run-state.md"
  "$root/resources/supervisor.md"
  "$root/resources/verification.md"
  "$root/resources/agy-execution.md"
  "$root/schemas/development-contract.schema.json"
  "$root/schemas/run-state.schema.json"
  "$root/templates/run-state.json"
  "$root/templates/execution-unit.md"
  "$root/templates/rework-contract.md"
  "$root/templates/review-report.md"
  "$root/templates/closeout-contract.md"
  "$root/templates/experiment-record.md"
  "$root/evals/scenarios.json"
  "$root/examples/project-rules-paper-info-web.md"
  "$root/examples/real-smoke-test.md"
  "$root/scripts/check-herdr.sh"
  "$root/scripts/snapshot-code-state.sh"
  "$root/scripts/validate-workflow.sh"
  "$root/scripts/validate-structure.sh"
  "$root/scripts/validate-docs.sh"
  "$root/scripts/validate-runtime.sh"
  "$root/scripts/test-readiness.sh"
)
for file in "${files[@]}"; do require_file "$file"; done
for script in "$root/scripts/check-herdr.sh" "$root/scripts/validate-structure.sh" "$root/scripts/validate-docs.sh" "$root/scripts/validate-runtime.sh" "$root/scripts/test-readiness.sh"; do require_exec "$script"; done

for legacy in \
  "$root/resources/sol-plan-review.md" \
  "$root/resources/ego-browser-runbook.md" \
  "$root/resources/shaping.md" \
  "$root/resources/spec-contract.md" \
  "$root/resources/execution-slicing.md" \
  "$root/resources/review-gates.md" \
  "$root/scripts/check-sol-plan-review.sh" \
  "$root/scripts/install-sol-plan-review.sh" \
  "$root/scripts/test-sol-plan-review.sh"; do
  forbid_file "$legacy"
done

python3 -m json.tool "$root/.agents/plugins/marketplace.json" >/dev/null
python3 -m json.tool "$root/.codex-plugin/plugin.json" >/dev/null
python3 -m json.tool "$root/schemas/development-contract.schema.json" >/dev/null
python3 -m json.tool "$root/schemas/run-state.schema.json" >/dev/null
python3 -m json.tool "$root/templates/run-state.json" >/dev/null
python3 -m json.tool "$root/evals/scenarios.json" >/dev/null
for script in check-herdr.sh snapshot-code-state.sh validate-workflow.sh validate-docs.sh validate-runtime.sh test-readiness.sh; do
  bash -n "$root/scripts/$script"
done

python3 - "$root/.codex-plugin/plugin.json" "$root/evals/scenarios.json" <<'PY'
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
e=json.load(open(sys.argv[2], encoding='utf-8'))
assert p['name']=='agy-supervised-development'
assert p['version']=='4.0.0-alpha.4'
assert p['skills']=='./skills/'
assert {'herdr','astra','luna'} <= set(p['keywords'])
assert e['version']=='4.0.0-alpha.4'
assert e['execution_status']=='SCENARIOS_DEFINED_NOT_EXECUTED'
ids=[c['id'] for c in e['cases']]
assert len(ids)==len(set(ids)) and len(ids)>=17
PY

printf 'STATIC_STRUCTURE_VALID\n'
