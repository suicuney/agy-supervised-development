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
run_check 'Validate Sol plan-review helper' "$root/scripts/test-sol-plan-review.sh"

printf 'AGY Supervised Development v3.3 readiness checks passed.\n'
