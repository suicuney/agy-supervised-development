#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -c 'import jsonschema' >/dev/null 2>&1 || { echo 'Missing required Python dependency: jsonschema' >&2; exit 2; }
python3 "$root/scripts/test-snapshot-behavior.py"
python3 "$root/scripts/run-completion-behavior-test.py"
bash "$root/scripts/test-doc-role-validation.sh"
printf 'DETERMINISTIC_WORKFLOW_TESTS_PASS\n'
