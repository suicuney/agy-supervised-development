#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run_check() {
  local label="$1"; shift
  printf '==> %s\n' "$label"
  "$@"
}

run_check 'Validate structure' "$root/scripts/validate-structure.sh"
run_check 'Validate documentation' "$root/scripts/validate-docs.sh"
run_check 'Validate Herdr runtime contract' "$root/scripts/validate-runtime.sh"

# Legacy Sol review helpers are retained as an optional guarded capability.
# Validate them when present, but they are no longer a prerequisite of the default 4.0 path.
if [[ -x "$root/scripts/test-sol-plan-review.sh" ]]; then
  run_check 'Validate optional Sol plan-review helper' "$root/scripts/test-sol-plan-review.sh"
fi

printf 'AGY Supervised Development v4.0 readiness checks passed.\n'
