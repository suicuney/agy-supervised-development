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
run_check 'Validate runtime adapter' "$root/scripts/validate-runtime.sh"

printf 'AGY Supervised Development v3.2 readiness checks passed.\n'
