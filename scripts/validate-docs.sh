#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
grep -q '4.1.0-alpha.3' "$root/README.md" || { echo 'DOC_LOGIC_MISSING:version' >&2; exit 1; }
grep -q 'run-frozen-check' "$root/SKILL.md" || { echo 'DOC_LOGIC_MISSING:runner' >&2; exit 1; }
grep -q 'contract_digest' "$root/resources/development-contract.md" || { echo 'DOC_LOGIC_MISSING:contract_digest' >&2; exit 1; }
grep -q 'Business applicability' "$root/resources/testing.md" || { echo 'DOC_LOGIC_MISSING:applicability' >&2; exit 1; }
"$root/scripts/validate-active-roles.sh" \
  "$root/SKILL.md" "$root/README.md" \
  "$root/resources/development-contract.md" "$root/resources/run-state.md" \
  "$root/resources/agy-execution.md" "$root/resources/code-review.md" "$root/resources/testing.md" \
  "$root/skills/agy-supervised-development/SKILL.md"
"$root/scripts/test-doc-role-validation.sh"
printf 'STATIC_DOC_LOGIC_VALID\n'
