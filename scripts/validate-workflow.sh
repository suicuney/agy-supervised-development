#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Machine-contract checks only; wording changes in Markdown should not decide readiness.
jq -e '.properties.contract_digest' "$root/schemas/run-state.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_MISSING:run-state.contract_digest' >&2; exit 1; }
jq -e '.properties.snapshot_policy.properties.digest' "$root/schemas/run-state.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_MISSING:run-state.policy_digest' >&2; exit 1; }
jq -e '.properties.checks and (.properties.metrics | not)' "$root/schemas/test-plan.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_INVALID:test-plan.commands-only' >&2; exit 1; }
jq -e '.properties.checks.items."$ref" == "#/$defs/commandCheck"' "$root/schemas/test-plan.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_INVALID:test-plan.command-check' >&2; exit 1; }
jq -e '.properties.attempts and (.properties.measured_values | not)' "$root/schemas/test-results.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_INVALID:test-results.attempts' >&2; exit 1; }
jq -e '.properties.phase.enum | index("BLOCKED") != null and index("COMPLETE") != null' "$root/schemas/run-state.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_INVALID:run-state.phases' >&2; exit 1; }

grep -q 'snapshot_code_state.py' "$root/scripts/snapshot-code-state.sh" || { echo 'WORKFLOW_ENTRYPOINT_INVALID:snapshot' >&2; exit 1; }
grep -q 'validate_run_state.py' "$root/scripts/validate-run-state.sh" || { echo 'WORKFLOW_ENTRYPOINT_INVALID:gate' >&2; exit 1; }

printf 'WORKFLOW_LOGIC_VALID\n'
