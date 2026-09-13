#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/agy-role-check.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/good.md" <<'DOC'
# Migration
4.1 removed the old Luna supervisor from the default workflow.
DOC
"$root/scripts/validate-active-roles.sh" "$tmp/good.md" >/dev/null

cat > "$tmp/bad.md" <<'DOC'
# Current workflow
Luna supervises AGY and verifies delivery.
DOC
if "$root/scripts/validate-active-roles.sh" "$tmp/bad.md" >"$tmp/out" 2>"$tmp/err"; then
  echo 'expected active Luna dependency rejection' >&2
  exit 1
fi
grep -q "ACTIVE_ROLE_FORBIDDEN:$tmp/bad.md:2:" "$tmp/err"
printf 'DOC_ROLE_LOGIC_CHECKS_PASS\n'
