#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

readme="$root/README.md"
plugin_skill="$root/skills/agy-supervised-development/SKILL.md"
kernel="$root/SKILL.md"
sol_plan="$root/resources/sol-plan-review.md"
agy_execution="$root/resources/agy-execution.md"
failure_modes="$root/resources/failure-modes.md"

require_contains() {
  local file="$1" pattern="$2" label="$3"
  grep -Eq -- "$pattern" "$file" || { printf 'Documentation validation failed: %s\n' "$label" >&2; exit 1; }
}

require_contains "$readme" '3\.3\.0-alpha\.1' 'README version'
require_contains "$readme" 'codex/agy-supervised-v3\.3-herdr-runtime' '3.3 branch install command'
require_contains "$readme" 'check-herdr\.sh' 'Herdr preflight'
require_contains "$readme" 'integration install antigravity-cli' 'Antigravity integration setup'
require_contains "$plugin_skill" 'Read `\.\./\.\./SKILL\.md`' 'plugin routes to workflow kernel'
require_contains "$plugin_skill" 'check-herdr\.sh' 'plugin routes Herdr preflight'
require_contains "$plugin_skill" 'agy-execution\.md' 'plugin routes AGY execution'
require_contains "$plugin_skill" 'review-gates\.md' 'review rules routing'
require_contains "$kernel" 'Every AGY execution runs through Herdr' 'Herdr-only runtime rule'
require_contains "$kernel" 'git diff --binary' 'baseline evidence capture'
require_contains "$sol_plan" 'NOT_SENT' 'Sol send state machine'
require_contains "$sol_plan" 'GPT-5\.6 Sol' 'Sol model truth gate'
require_contains "$agy_execution" 'herdr workspace create' 'Herdr workspace creation'
require_contains "$agy_execution" '\.result\.root_pane\.pane_id' 'returned root pane identity'
require_contains "$agy_execution" 'agent start.*agy|--kind agy' 'AGY launch through Herdr'
require_contains "$agy_execution" 'agent prompt' 'Herdr prompt primitive'
require_contains "$agy_execution" 'agent read' 'read-before-interaction primitive'
require_contains "$failure_modes" 'Herdr done != REVIEW PASS' 'runtime state is not review verdict'

active=(
  "$readme"
  "$plugin_skill"
  "$kernel"
  "$agy_execution"
  "$failure_modes"
  "$root/examples"
  "$root/evals"
)

if grep -REn -- 'agy-run\.sh|tty7' "${active[@]}" >/dev/null; then
  printf 'Documentation validation failed: legacy AGY runtime reference remains in active docs/evals.\n' >&2
  grep -REn -- 'agy-run\.sh|tty7' "${active[@]}" >&2 || true
  exit 1
fi

printf 'Documentation validation passed.\n'
