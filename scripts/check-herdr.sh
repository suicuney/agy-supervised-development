#!/usr/bin/env bash
set -euo pipefail

fail() { printf '%s\n' "$1" >&2; exit 1; }

command -v herdr >/dev/null 2>&1 || fail 'HERDR_MISSING'
command -v agy >/dev/null 2>&1 || fail 'AGY_MISSING'
command -v jq >/dev/null 2>&1 || fail 'JQ_MISSING'

version="$(herdr --version 2>/dev/null)" || fail 'HERDR_UNUSABLE'
[[ "$version" =~ ^herdr[[:space:]][0-9]+\.[0-9]+\.[0-9]+ ]] || fail 'HERDR_VERSION_UNKNOWN'

schema="$(herdr api schema --json 2>/dev/null)" || fail 'HERDR_SCHEMA_UNAVAILABLE'
printf '%s' "$schema" | jq -e 'type == "object" and (.protocol | type == "number") and .protocol > 0' >/dev/null \
  || fail 'HERDR_SCHEMA_INVALID'

server="$(herdr status server 2>/dev/null)" || fail 'HERDR_SERVER_UNAVAILABLE'
printf '%s' "$server" | jq -e 'type == "object" and length > 0' >/dev/null \
  || fail 'HERDR_SERVER_STATUS_INVALID'

integration_status="$(herdr integration status 2>&1)" || fail 'HERDR_INTEGRATION_STATUS_FAILED'
antigravity_line="$(printf '%s\n' "$integration_status" | grep -Ei 'antigravity([ -]?cli)?' | head -n 1 || true)"
[[ -n "$antigravity_line" ]] || fail 'ANTIGRAVITY_INTEGRATION_MISSING'
printf '%s\n' "$antigravity_line" | grep -Eiq '\bcurrent\b' || fail 'ANTIGRAVITY_INTEGRATION_NOT_CURRENT'
printf '%s\n' "$antigravity_line" | grep -Eiq 'v[1-9][0-9]*' || fail 'ANTIGRAVITY_INTEGRATION_VERSION_UNKNOWN'

# This preflight proves environment readiness only. It does not prove AGY auth,
# a successful worker launch, model handoff, or end-to-end workflow delivery.
printf 'HERDR_ENVIRONMENT_READY\n'
printf 'HERDR_VERSION=%s\n' "$version"
printf 'HERDR_PROTOCOL=%s\n' "$(printf '%s' "$schema" | jq -r '.protocol')"
printf 'ANTIGRAVITY_INTEGRATION=%s\n' "$antigravity_line"
