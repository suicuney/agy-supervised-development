#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/agy-role-docs.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/legal.md" <<'EOF'
# Migration note
4.1 removed the old Luna supervisor and the legacy `resources/supervisor.md` path.
EOF
python3 "$root/scripts/validate_active_roles.py" "$tmp/legal.md" >/dev/null

cat > "$tmp/illegal.md" <<'EOF'
# Current workflow
Astra freezes the Contract.
Luna supervises AGY and verifies delivery.
EOF
if python3 "$root/scripts/validate_active_roles.py" "$tmp/illegal.md" >"$tmp/out" 2>"$tmp/err"; then
  echo 'expected active Luna dependency to fail' >&2
  exit 1
fi
grep -q 'illegal.md:3: active Luna responsibility' "$tmp/err"

printf 'DOC_ROLE_BEHAVIOR_TESTS_PASS\n'
