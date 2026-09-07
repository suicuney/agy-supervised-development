#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf '%s\n' "$1" >&2
  exit 1
}

command -v herdr >/dev/null 2>&1 || fail 'HERDR_MISSING'
command -v agy >/dev/null 2>&1 || fail 'AGY_MISSING'
command -v jq >/dev/null 2>&1 || fail 'JQ_MISSING'

herdr --version >/dev/null 2>&1 || fail 'HERDR_UNUSABLE'
herdr status server >/dev/null 2>&1 || fail 'HERDR_SERVER_UNAVAILABLE'

integration_status="$(herdr integration status 2>&1)" \
  || fail 'HERDR_INTEGRATION_STATUS_FAILED'

antigravity_line="$(printf '%s\n' "$integration_status" | grep -Ei 'antigravity([ -]?cli)?' | head -n 1 || true)"
[[ -n "$antigravity_line" ]] || fail 'ANTIGRAVITY_INTEGRATION_MISSING'

if printf '%s\n' "$antigravity_line" | grep -Eiq 'not[ -]?installed|missing|invalid|legacy|outdated'; then
  fail 'ANTIGRAVITY_INTEGRATION_UNREADY'
fi

printf 'HERDR_READY\n'
