#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$root/scripts/validate-structure.sh"
"$root/scripts/validate-docs.sh"
"$root/scripts/validate-runtime.sh"

printf 'AGY Supervised Development v4.0 readiness checks passed.\n'
