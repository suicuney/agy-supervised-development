#!/usr/bin/env bash
set -euo pipefail

fail() { printf '%s\n' "$1" >&2; exit 1; }

command -v herdr >/dev/null 2>&1 || fail 'HERDR_MISSING'
command -v agy >/dev/null 2>&1 || fail 'AGY_MISSING'
command -v jq >/dev/null 2>&1 || fail 'JQ_MISSING'

version="$(herdr --version 2>/dev/null)" || fail 'HERDR_UNUSABLE'
[[ "$version" =~ ^herdr[[:space:]][0-9]+\.[0-9]+\.[0-9]+ ]] || fail 'HERDR_VERSION_UNKNOWN'

# Prefer Herdr's supported structured status. Unknown/null/incompatible state fails closed.
server="$(herdr status server --json 2>/dev/null)" || fail 'HERDR_SERVER_STATUS_FAILED'
printf '%s' "$server" | jq -e '
  type == "object" and
  .status == "running" and
  .running == true and
  (.protocol | type == "number") and
  .protocol > 0 and
  .compatible == true
' >/dev/null || fail 'HERDR_SERVER_UNREADY'

# Schema availability is a capability sanity check; do not infer readiness from arbitrary text.
schema="$(herdr api schema --json 2>/dev/null)" || fail 'HERDR_SCHEMA_UNAVAILABLE'
printf '%s' "$schema" | jq -e 'type == "object" and length > 0' >/dev/null || fail 'HERDR_SCHEMA_INVALID'

integration_status="$(herdr integration status 2>&1)" || fail 'HERDR_INTEGRATION_STATUS_FAILED'
antigravity_line="$(printf '%s\n' "$integration_status" | grep -Ei 'antigravity([ -]?cli)?' | head -n 1 || true)"
[[ -n "$antigravity_line" ]] || fail 'ANTIGRAVITY_INTEGRATION_MISSING'
printf '%s\n' "$antigravity_line" | grep -Eiq '\bcurrent\b' || fail 'ANTIGRAVITY_INTEGRATION_NOT_CURRENT'
printf '%s\n' "$antigravity_line" | grep -Eiq 'v[1-9][0-9]*' || fail 'ANTIGRAVITY_INTEGRATION_VERSION_UNKNOWN'

# Environment readiness only: no claim about AGY auth, task execution, model handoff, or delivery.
printf 'HERDR_ENVIRONMENT_READY\n'
printf 'HERDR_VERSION=%s\n' "$version"
printf 'HERDR_PROTOCOL=%s\n' "$(printf '%s' "$server" | jq -r '.protocol')"
printf 'HERDR_COMPATIBLE=true\n'
printf 'ANTIGRAVITY_INTEGRATION=%s\n' "$antigravity_line"
