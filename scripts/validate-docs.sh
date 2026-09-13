#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$root/scripts/validate-active-roles.sh" \
  "$root/SKILL.md" "$root/README.md" \
  "$root/resources/development-contract.md" "$root/resources/run-state.md" \
  "$root/resources/agy-execution.md" "$root/resources/code-review.md" "$root/resources/testing.md" \
  "$root/skills/agy-supervised-development/SKILL.md"

if grep -REn -- \
  'run-frozen-check|test-receipt\.schema|templates/test-plan\.md|templates/experiment-record\.md|templates/closeout-contract\.md|templates/rework-contract\.md' \
  "$root/SKILL.md" "$root/README.md" "$root/resources" "$root/skills" "$root/examples" >/dev/null; then
  echo 'DOC_RETIRED_REFERENCE_PRESENT' >&2
  exit 1
fi

printf 'STATIC_DOC_LOGIC_VALID\n'
