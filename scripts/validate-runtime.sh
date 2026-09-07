#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/agy-supervised-herdr.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/bin"

cat > "$tmp/bin/agy" <<'SH'
#!/usr/bin/env bash
exit 0
SH
chmod +x "$tmp/bin/agy"

cat > "$tmp/bin/jq" <<'SH'
#!/usr/bin/env bash
exit 0
SH
chmod +x "$tmp/bin/jq"

cat > "$tmp/bin/herdr" <<'SH'
#!/usr/bin/env bash
case "${1:-} ${2:-} ${3:-}" in
  '--version  ')
    printf 'herdr 0.8.2\n'
    ;;
  'status server ')
    [[ "${FAKE_HERDR_SERVER_DOWN:-0}" == 1 ]] && exit 1
    printf '{"ok":true}\n'
    ;;
  'integration status ')
    printf '%s\n' "${FAKE_INTEGRATION_STATUS:-Antigravity CLI current v1}"
    ;;
  *)
    printf 'unexpected fake herdr args: %s\n' "$*" >&2
    exit 2
    ;;
esac
SH
chmod +x "$tmp/bin/herdr"

run_check() {
  PATH="$tmp/bin:$PATH" "$root/scripts/check-herdr.sh"
}

out="$(run_check)"
[[ "$out" == 'HERDR_READY' ]]

if FAKE_INTEGRATION_STATUS='Claude Code current v7' run_check >/dev/null 2>&1; then
  printf 'Missing Antigravity integration should fail.\n' >&2
  exit 1
fi

if FAKE_INTEGRATION_STATUS='Antigravity CLI outdated v0' run_check >/dev/null 2>&1; then
  printf 'Outdated Antigravity integration should fail.\n' >&2
  exit 1
fi

if FAKE_HERDR_SERVER_DOWN=1 run_check >/dev/null 2>&1; then
  printf 'Unavailable Herdr server should fail.\n' >&2
  exit 1
fi

printf 'Herdr runtime validation passed.\n'
