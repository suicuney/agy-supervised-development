#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
check_environment=0
[[ "${1:-}" == '--environment' || "${AGY_CHECK_ENVIRONMENT:-0}" == 1 ]] && check_environment=1

"$root/scripts/validate-structure.sh"
"$root/scripts/validate-docs.sh"
"$root/scripts/validate-workflow.sh"
printf 'STATIC_LOGIC_VALID=PASS\n'

if [[ $check_environment == 1 ]]; then
  "$root/scripts/check-herdr.sh"
  printf 'ENVIRONMENT_READY=PASS\n'
else
  printf 'ENVIRONMENT_READY=NOT_CHECKED\n'
fi
printf 'FLOW_VERIFIED=NOT_RUN\n'
printf 'SEMANTIC_EVALS=NOT_EXECUTED\n'
