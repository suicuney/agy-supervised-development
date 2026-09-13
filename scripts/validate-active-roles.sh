#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo 'usage: validate-active-roles.sh <file> [...]' >&2
  exit 2
fi

failed=0
for file in "$@"; do
  [[ -f "$file" ]] || { echo "ACTIVE_ROLE_CHECK_MISSING:$file" >&2; failed=1; continue; }
  while IFS= read -r match; do
    line=${match%%:*}; text=${match#*:}; lower=$(printf '%s' "$text" | tr '[:upper:]' '[:lower:]')
    if [[ "$lower" =~ (removed|legacy|histor|migration|no[[:space:]]+default|not[[:space:]]+part[[:space:]]+of|does[[:space:]]+not[[:space:]]+use|without|没有默认|不再|不属于默认) ]]; then
      continue
    fi
    printf 'ACTIVE_ROLE_FORBIDDEN:%s:%s:%s\n' "$file" "$line" "$text" >&2; failed=1
  done < <(grep -Ein 'Luna[[:space:]]+(supervises|supervisor|reviews|verifies|dispatches)|gpt-5\.6-luna|codex-supervisor-handoff|resources/supervisor\.md|resources/verification\.md|Sol[[:space:]]+plan[[:space:]]+review.*default|Three-Axis[[:space:]]+Review' "$file" || true)
done

[[ $failed -eq 0 ]] || exit 1
printf 'ACTIVE_ROLE_VALID\n'
