#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/agy-supervised-runtime.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/bin" "$tmp/repo"

cat > "$tmp/bin/agy" <<'SH'
#!/usr/bin/env bash
printf '%s\n' "$@"
SH
chmod +x "$tmp/bin/agy"
git -C "$tmp/repo" init -q

run() { PATH="$tmp/bin:$PATH" "$root/scripts/agy-run.sh" "$@"; }

out="$(run --repo "$tmp/repo" --timeout 12m 'Implement bounded unit')"
grep -q -- '-p' <<<"$out"
grep -q -- 'Implement bounded unit' <<<"$out"
grep -q -- '--output-format' <<<"$out"
grep -q -- 'stream-json' <<<"$out"
grep -q -- '--print-timeout' <<<"$out"
grep -q -- '12m' <<<"$out"

out="$(run --repo "$tmp/repo" --mode consult --conversation conv-123 --add-dir /tmp/extra 'Review risk')"
grep -q -- 'Read-only consultation' <<<"$out"
grep -q -- '--conversation' <<<"$out"
grep -q -- 'conv-123' <<<"$out"
grep -q -- '--add-dir' <<<"$out"
grep -q -- '/tmp/extra' <<<"$out"

if run --repo "$tmp/repo" --mode invalid test >/dev/null 2>&1; then
  printf 'Invalid mode should fail.\n' >&2
  exit 1
fi

printf 'Runtime validation passed.\n'
