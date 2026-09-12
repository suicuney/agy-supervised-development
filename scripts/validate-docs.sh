#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
require_contains() { grep -Eq -- "$2" "$1" || { printf 'Documentation validation failed: %s\n' "$3" >&2; exit 1; }; }

readme="$root/README.md"
kernel="$root/SKILL.md"
entry="$root/skills/agy-supervised-development/SKILL.md"
execution="$root/resources/agy-execution.md"
review="$root/resources/code-review.md"
testing="$root/resources/testing.md"
runstate="$root/resources/run-state.md"

require_contains "$readme" '4\.1\.0-alpha\.1' 'README version'
require_contains "$kernel" 'AGY via HERDR: IMPLEMENT ONLY' 'implementation-only phase'
require_contains "$kernel" 'ASTRA: CODE REVIEW ONLY' 'Astra code review phase'
require_contains "$kernel" 'TEST PLAN \+ ACCEPTANCE METRICS' 'Astra test planning phase'
require_contains "$kernel" 'Astra does not perform a second test-review pass' 'no Astra test review'
require_contains "$entry" 'AGY: Implement only' 'entry flow'
require_contains "$execution" 'mode = IMPLEMENT' 'AGY implementation mode'
require_contains "$execution" 'mode = TEST' 'AGY test mode'
require_contains "$review" 'This stage is intentionally code-only' 'code-only review rule'
require_contains "$review" 'Any subsequent production-code change invalidates this pass' 'review invalidation'
require_contains "$testing" 'AGY may not remove required checks' 'metric freeze'
require_contains "$testing" 'No second Astra test-review is required' 'mechanical completion'
require_contains "$runstate" 'TEST_PLAN' 'phase state'
require_contains "$runstate" 'code_review_pass = STALE' 'stale review state'

if grep -REn --exclude-dir=legacy -- 'Luna supervises|Luna supervisor|gpt-5\.6-luna|codex-supervisor-handoff|resources/supervisor\.md|resources/verification\.md|Plan review is enabled by default|Three-Axis Review' \
  "$root/SKILL.md" "$root/README.md" "$root/resources" "$root/templates" "$root/examples" "$root/evals" "$root/skills" >/dev/null; then
  printf 'Documentation validation failed: removed supervisor/legacy default behavior remains active.\n' >&2
  exit 1
fi

printf 'STATIC_DOCS_VALID\n'
