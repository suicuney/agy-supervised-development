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

cat > "$tmp/bin/herdr" <<'SH'
#!/usr/bin/env bash
case "$*" in
  '--version') printf '%s\n' "${FAKE_HERDR_VERSION:-herdr 0.8.2}" ;;
  'api schema --json') printf '%s\n' "${FAKE_SCHEMA:-{\"protocol\":20}}" ;;
  'status server')
    [[ "${FAKE_HERDR_SERVER_DOWN:-0}" == 1 ]] && exit 1
    printf '%s\n' "${FAKE_SERVER_STATUS:-{\"running\":true,\"compatible\":true}}"
    ;;
  'integration status') printf '%s\n' "${FAKE_INTEGRATION_STATUS:-Antigravity CLI current v2}" ;;
  *) printf 'unexpected fake herdr args: %s\n' "$*" >&2; exit 2 ;;
esac
SH
chmod +x "$tmp/bin/herdr"

run_check() { PATH="$tmp/bin:$PATH" "$root/scripts/check-herdr.sh"; }

out="$(run_check)"
grep -q '^HERDR_ENVIRONMENT_READY$' <<<"$out"
grep -q '^HERDR_PROTOCOL=20$' <<<"$out"

expect_fail() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf 'Expected failure: %s\n' "$label" >&2
    exit 1
  fi
}

expect_fail 'missing Antigravity integration' env FAKE_INTEGRATION_STATUS='Claude Code current v7' bash -c 'PATH="'$tmp'/bin:$PATH" "'$root'/scripts/check-herdr.sh"'
expect_fail 'outdated Antigravity integration' env FAKE_INTEGRATION_STATUS='Antigravity CLI outdated v2' bash -c 'PATH="'$tmp'/bin:$PATH" "'$root'/scripts/check-herdr.sh"'
expect_fail 'unknown integration state' env FAKE_INTEGRATION_STATUS='Antigravity CLI v2' bash -c 'PATH="'$tmp'/bin:$PATH" "'$root'/scripts/check-herdr.sh"'
expect_fail 'server unavailable' env FAKE_HERDR_SERVER_DOWN=1 bash -c 'PATH="'$tmp'/bin:$PATH" "'$root'/scripts/check-herdr.sh"'
expect_fail 'server malformed' env FAKE_SERVER_STATUS='not-json' bash -c 'PATH="'$tmp'/bin:$PATH" "'$root'/scripts/check-herdr.sh"'
expect_fail 'schema malformed' env FAKE_SCHEMA='{}' bash -c 'PATH="'$tmp'/bin:$PATH" "'$root'/scripts/check-herdr.sh"'
expect_fail 'empty version' env FAKE_HERDR_VERSION='unknown' bash -c 'PATH="'$tmp'/bin:$PATH" "'$root'/scripts/check-herdr.sh"'

printf 'Herdr runtime contract tests passed.\n'
