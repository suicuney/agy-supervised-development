#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -c 'import jsonschema' >/dev/null 2>&1 || {
  echo 'Missing required Python dependency: jsonschema (install requirements-validation.txt)' >&2
  exit 2
}
exec python3 "$root/scripts/validate_run_state.py" "$@"
