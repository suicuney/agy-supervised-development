#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
require_contains() { grep -Eq -- "$2" "$1" || { printf 'Documentation validation failed: %s: %s\n' "$1" "$3" >&2; exit 1; }; }

readme="$root/README.md"; kernel="$root/SKILL.md"; entry="$root/skills/agy-supervised-development/SKILL.md"
contract="$root/resources/development-contract.md"; execution="$root/resources/agy-execution.md"; review="$root/resources/code-review.md"; testing="$root/resources/testing.md"; runstate="$root/resources/run-state.md"

require_contains "$readme" '4\.1\.0-alpha\.2' 'version mismatch'
require_contains "$kernel" 'pre-authorized|preauthorized' 'bounded implementation diagnostics missing'
require_contains "$kernel" 'deterministic' 'mechanical completion gate missing'
require_contains "$entry" 'Astra: Code review only' 'entry flow missing'
require_contains "$contract" 'acceptance_scenarios|acceptance scenarios' 'observable acceptance scenarios missing'
require_contains "$contract" 'formal_acceptance=false' 'diagnostic evidence boundary missing'
require_contains "$execution" 'SEND_UNKNOWN' 'uncertain dispatch safety missing'
require_contains "$execution" 'TEST_REWORK' 'test repair handoff missing'
require_contains "$review" 'Any subsequent deliverable change' 'review invalidation missing'
require_contains "$testing" 'validate-run-state.sh complete' 'deterministic completion command missing'
require_contains "$testing" 'NOT_APPLICABLE|applicability' 'applicability contract missing'
require_contains "$runstate" 'deliverable_digest' 'deliverable identity missing'
require_contains "$runstate" 'ownership_digest' 'ownership identity missing'

python3 "$root/scripts/validate_active_roles.py" \
  "$root/SKILL.md" "$root/README.md" "$root/resources" "$root/templates" "$root/examples" "$root/evals" "$root/skills"
bash "$root/scripts/test-doc-role-validation.sh"
printf 'STATIC_DOCS_VALID\n'
