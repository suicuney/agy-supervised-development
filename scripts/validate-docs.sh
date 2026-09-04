#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

readme="$root/README.md"
plugin_skill="$root/skills/agy-supervised-development/SKILL.md"
kernel="$root/SKILL.md"
sol_plan="$root/resources/sol-plan-review.md"
agy_execution="$root/resources/agy-execution.md"
tty7_manual="$root/resources/tty7-supervision.md"
failure_modes="$root/resources/failure-modes.md"

require_contains() {
  local file="$1" pattern="$2" label="$3"
  grep -Eq -- "$pattern" "$file" || { printf 'Documentation validation failed: %s\n' "$label" >&2; exit 1; }
}

require_contains "$readme" '3\.2\.0-alpha\.3' 'README version'
require_contains "$readme" 'codex plugin marketplace add' 'plugin install command'
require_contains "$readme" 'check-sol-plan-review\.sh' 'Sol dependency preflight'
require_contains "$readme" 'install-sol-plan-review\.sh' 'Sol full-checkout install path'
require_contains "$readme" 'UNKNOWN' 'duplicate-send state'
require_contains "$readme" 'init\.cwd' 'AGY cwd verification'
require_contains "$plugin_skill" 'Read `\.\./\.\./SKILL\.md`' 'plugin routes to workflow kernel'
require_contains "$plugin_skill" 'check-sol-plan-review\.sh' 'plugin routes Sol preflight'
require_contains "$plugin_skill" 'sol-plan-review\.md' 'Sol plan review routing'
require_contains "$plugin_skill" 'tty7-supervision\.md' 'tty7 fallback routing'
require_contains "$plugin_skill" 'review-gates\.md' 'review rules routing'
require_contains "$plugin_skill" 'runtime-verification\.md' 'runtime verification routing'
require_contains "$kernel" 'git diff --binary' 'baseline evidence capture'
require_contains "$sol_plan" 'NOT_SENT' 'Sol send state machine'
require_contains "$sol_plan" 'GPT-5\.6 Sol' 'Sol model truth gate'
require_contains "$agy_execution" 'init\.cwd == repo_root' 'AGY init cwd check'
require_contains "$agy_execution" '(command|命令).*cwd' 'AGY command cwd check'
require_contains "$tty7_manual" 'send.*--key enter' 'tty7 approval syntax'
require_contains "$failure_modes" '半安装' 'Sol incomplete-install failure mode'

printf 'Documentation validation passed.\n'
