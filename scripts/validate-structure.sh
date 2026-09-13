#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
files=(
 .codex-plugin/plugin.json SKILL.md README.md CHANGELOG.md requirements-validation.txt
 skills/agy-supervised-development/SKILL.md
 resources/development-contract.md resources/run-state.md resources/agy-execution.md resources/code-review.md resources/testing.md
 schemas/development-contract.schema.json schemas/snapshot-policy.schema.json schemas/run-state.schema.json schemas/test-plan.schema.json schemas/test-receipt.schema.json schemas/test-results.schema.json
 templates/development-contract.json templates/snapshot-policy.json templates/run-state.json templates/test-plan.json templates/test-results.json templates/test-plan.md
 scripts/workflow_common.py scripts/snapshot_code_state.py scripts/snapshot-code-state.sh scripts/run_frozen_check.py scripts/run-frozen-check.sh scripts/validate_run_state.py scripts/validate-run-state.sh scripts/validate-active-roles.sh scripts/test-doc-role-validation.sh scripts/validate-docs.sh scripts/validate-workflow.sh scripts/test-readiness.sh
 evals/scenarios.json
)
for f in "${files[@]}"; do [[ -f "$root/$f" ]] || { echo "STRUCTURE_MISSING:$f" >&2; exit 1; }; done

command -v jq >/dev/null 2>&1 || { echo 'STRUCTURE_TOOL_MISSING:jq' >&2; exit 2; }
for f in "$root/.codex-plugin/plugin.json" "$root/schemas/"*.json "$root/templates/"*.json "$root/evals/scenarios.json"; do
  jq -e . "$f" >/dev/null || { echo "JSON_INVALID:${f#$root/}" >&2; exit 1; }
done

for f in snapshot-code-state.sh run-frozen-check.sh validate-run-state.sh validate-active-roles.sh test-doc-role-validation.sh validate-docs.sh validate-workflow.sh test-readiness.sh; do
  bash -n "$root/scripts/$f" || { echo "SHELL_SYNTAX_INVALID:scripts/$f" >&2; exit 1; }
done

plugin_version="$(jq -r '.version // empty' "$root/.codex-plugin/plugin.json")"
eval_version="$(jq -r '.version // empty' "$root/evals/scenarios.json")"
[[ "$plugin_version" == '4.1.0-alpha.3' ]] || { echo "VERSION_MISMATCH:plugin:$plugin_version" >&2; exit 1; }
[[ "$eval_version" == "$plugin_version" ]] || { echo "VERSION_MISMATCH:eval:$eval_version:$plugin_version" >&2; exit 1; }
grep -q '^version: 4\.1\.0-alpha\.3$' "$root/SKILL.md" || { echo 'VERSION_MISMATCH:SKILL.md' >&2; exit 1; }
grep -q '^version: 4\.1\.0-alpha\.3$' "$root/skills/agy-supervised-development/SKILL.md" || { echo 'VERSION_MISMATCH:skill-entry' >&2; exit 1; }
if jq -e '.keywords | index("luna") != null' "$root/.codex-plugin/plugin.json" >/dev/null; then
  echo 'ACTIVE_ROLE_FORBIDDEN:plugin keyword luna' >&2; exit 1
fi
printf 'STATIC_STRUCTURE_LOGIC_VALID\n'
