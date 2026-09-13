#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require() {
  local file="$1" pattern="$2" code="$3"
  grep -Eq -- "$pattern" "$file" || { printf 'WORKFLOW_LOGIC_MISSING:%s:%s\n' "$code" "${file#$root/}" >&2; exit 1; }
}

require "$root/SKILL.md" 'ASTRA: CODE REVIEW' 'astra-code-review-stage'
require "$root/SKILL.md" 'Test Plan|TEST PLAN' 'frozen-test-plan-stage'
require "$root/SKILL.md" 'run-frozen-check' 'runner-stage'
require "$root/resources/agy-execution.md" 'formal_acceptance[[:space:]]*=[[:space:]]*false|formal_acceptance=false' 'diagnostic-not-acceptance'
require "$root/resources/code-review.md" 'code-only|CODE_REVIEW_PASS' 'code-only-review'
require "$root/resources/testing.md" 'Contract digest|contract_digest' 'contract-binding'
require "$root/resources/testing.md" 'snapshot-policy digest|policy_digest' 'policy-binding'
require "$root/resources/testing.md" 'Business applicability' 'business-applicability'
require "$root/resources/testing.md" 'environment|Environment' 'environment-blocking'
require "$root/resources/run-state.md" 'COMPLETE' 'terminal-complete'
require "$root/resources/run-state.md" 'SEND_UNKNOWN' 'unknown-send-safety'
require "$root/resources/run-state.md" 'TEST_REWORK' 'test-rework-state'

jq -e '.properties.contract_digest' "$root/schemas/run-state.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_MISSING:run-state.contract_digest' >&2; exit 1; }
jq -e '.properties.snapshot_policy.properties.digest' "$root/schemas/run-state.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_MISSING:run-state.snapshot_policy.digest' >&2; exit 1; }
jq -e '.properties.contract_digest' "$root/schemas/test-plan.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_MISSING:test-plan.contract_digest' >&2; exit 1; }
jq -e '.properties.policy_digest' "$root/schemas/test-plan.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_MISSING:test-plan.policy_digest' >&2; exit 1; }
jq -e '.properties.attempt_id' "$root/schemas/test-receipt.schema.json" >/dev/null || { echo 'WORKFLOW_SCHEMA_MISSING:test-receipt.attempt_id' >&2; exit 1; }

grep -q 'snapshot_code_state.py' "$root/scripts/snapshot-code-state.sh" || { echo 'WORKFLOW_ENTRYPOINT_INVALID:snapshot' >&2; exit 1; }
grep -q 'run_frozen_check.py' "$root/scripts/run-frozen-check.sh" || { echo 'WORKFLOW_ENTRYPOINT_INVALID:runner' >&2; exit 1; }
grep -q 'validate_run_state.py' "$root/scripts/validate-run-state.sh" || { echo 'WORKFLOW_ENTRYPOINT_INVALID:gate' >&2; exit 1; }

printf 'WORKFLOW_LOGIC_VALID\n'
