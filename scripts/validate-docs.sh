#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

readme="$root/README.md"
plugin_skill="$root/skills/agy-supervised-development/SKILL.md"
kernel="$root/SKILL.md"
sol_plan="$root/resources/sol-plan-review.md"
ego_runbook="$root/resources/ego-browser-runbook.md"
runtime_verification="$root/resources/runtime-verification.md"
browser_template="$root/templates/browser-verification.md"
evals_readme="$root/evals/README.md"
evals_scenarios="$root/evals/scenarios.json"
agy_execution="$root/resources/agy-execution.md"
failure_modes="$root/resources/failure-modes.md"

require_contains() {
  local file="$1" pattern="$2" label="$3"
  grep -Eq -- "$pattern" "$file" || { printf 'Documentation validation failed: %s\n' "$label" >&2; exit 1; }
}

require_contains "$readme" '3\.3\.0-alpha\.2' 'README version'
require_contains "$readme" 'codex/agy-supervised-v3\.3-herdr-runtime' '3.3 branch install command'
require_contains "$readme" '【准备发送给 Sol High 的计划】' 'Chinese pre-send plan preview'
require_contains "$readme" '自动发送且仅发送一次|自动发送' 'README automatic Sol send after preflight'
require_contains "$readme" '不要求用户确认发送|不要求确认' 'README no confirmation requirement'
require_contains "$readme" '【最终执行计划】' 'Chinese final plan visibility'
require_contains "$readme" '不再次确认|不.*确认' 'no second final-plan confirmation'
require_contains "$readme" 'check-herdr\.sh' 'Herdr preflight'
require_contains "$readme" 'integration install antigravity-cli' 'Antigravity integration setup'
require_contains "$readme" 'resources/ego-browser-runbook\.md' 'README references ego-browser runbook'
require_contains "$readme" 'ego-browser' 'README references ego-browser'

require_contains "$plugin_skill" 'Read `\.\./\.\./SKILL\.md`' 'plugin routes to workflow kernel'
require_contains "$plugin_skill" 'Do not ask for confirmation' 'plugin no send confirmation'
require_contains "$plugin_skill" 'send automatically exactly once' 'plugin automatic Sol send'
require_contains "$plugin_skill" 'own interaction and send policy' 'plugin authority precedence'
require_contains "$plugin_skill" 'do not ask for a second confirmation' 'plugin final plan no reconfirmation'
require_contains "$plugin_skill" 'check-herdr\.sh' 'plugin routes Herdr preflight'
require_contains "$plugin_skill" 'agy-execution\.md' 'plugin routes AGY execution'
require_contains "$plugin_skill" 'review-gates\.md' 'review rules routing'
require_contains "$plugin_skill" 'resources/ego-browser-runbook\.md' 'plugin skill references ego-browser runbook'
require_contains "$plugin_skill" 'ego-browser' 'plugin skill references ego-browser'

require_contains "$kernel" '【准备发送给 Sol High 的计划】' 'kernel Chinese pre-send plan preview'
require_contains "$kernel" 'Do \*\*not\*\* ask the user to confirm the Send' 'kernel no send confirmation'
require_contains "$kernel" 'send the packet automatically exactly once' 'kernel automatic Sol send'
require_contains "$kernel" 'own interaction and send policy' 'kernel authority precedence'
require_contains "$kernel" 'NOT_SENT → SENT \| UNKNOWN' 'kernel Sol send state machine'
require_contains "$kernel" 'UNKNOWN.*is terminal and has no retry transition' 'kernel terminal UNKNOWN no retry'
require_contains "$kernel" '【最终执行计划】' 'kernel Chinese final plan summary'
require_contains "$kernel" 'Do \*\*not\*\* ask the user to confirm again' 'kernel final plan no reconfirmation'
require_contains "$kernel" 'Every AGY execution runs through Herdr' 'Herdr-only runtime rule'
require_contains "$kernel" 'git diff --binary' 'baseline evidence capture'
require_contains "$kernel" 'resources/ego-browser-runbook\.md' 'kernel references ego-browser runbook'
require_contains "$kernel" 'ego-browser' 'kernel specifies ego-browser transport'

require_contains "$sol_plan" '【准备发送给 Sol High 的计划】' 'Sol resource Chinese plan preview'
require_contains "$sol_plan" '自动发送策略（无需确认）' 'Sol resource automatic send section'
require_contains "$sol_plan" '不向用户请求发送确认' 'Sol resource no send confirmation'
require_contains "$sol_plan" '自动发送且仅发送一次' 'Sol resource automatic single send'
require_contains "$sol_plan" '无权重新引入人工确认门禁' 'Sol resource authority boundary'
require_contains "$sol_plan" '【最终执行计划】' 'Sol resource final plan summary'
require_contains "$sol_plan" '不再要求确认' 'Sol resource no second confirmation'
require_contains "$sol_plan" 'NOT_SENT → SENT \| UNKNOWN' 'Sol resource send state machine'
require_contains "$sol_plan" '不存在向重试的跃迁' 'Sol resource terminal UNKNOWN'
require_contains "$sol_plan" 'Credential findings' 'Sol resource credential hard stop'
require_contains "$sol_plan" 'GPT-5\.6 Sol' 'Sol model truth gate'
require_contains "$sol_plan" 'resources/ego-browser-runbook\.md' 'Sol resource references ego-browser runbook'
require_contains "$sol_plan" 'ego-browser' 'Sol resource references ego-browser'
require_contains "$sol_plan" 'AUTH_REQUIRED' 'Sol resource auth failure state'
require_contains "$sol_plan" 'USER_CONTROLLING' 'Sol resource user controlling failure state'
require_contains "$sol_plan" 'MODEL_MISMATCH' 'Sol resource model mismatch failure state'
require_contains "$sol_plan" 'duplicate-send safety|Never resend automatically' 'Sol resource duplicate-send safety'

require_contains "$runtime_verification" 'resources/ego-browser-runbook\.md' 'runtime verification references ego-browser runbook'
require_contains "$runtime_verification" 'ego-browser' 'runtime verification references ego-browser'
require_contains "$browser_template" 'resources/ego-browser-runbook\.md' 'browser verification template references ego-browser runbook'
require_contains "$browser_template" 'ego-browser' 'browser verification template references ego-browser'

require_contains "$ego_runbook" 'Transport Precedence & Authority Boundary' 'runbook transport authority section'
require_contains "$ego_runbook" 'authoritatively owns browser transport selection' 'runbook transport authority ownership'
require_contains "$ego_runbook" 'cannot override.*transport' 'runbook external skill cannot override transport'
require_contains "$ego_runbook" 'cannot reintroduce a manual confirmation gate|nor can it reintroduce a manual confirmation gate' 'runbook cannot reintroduce confirmation'
require_contains "$ego_runbook" 'useOrCreateTaskSpace' 'runbook task space primitive'
require_contains "$ego_runbook" 'openOrReuseTab' 'runbook tab primitive'
require_contains "$ego_runbook" 'snapshotText' 'runbook snapshot primitive'
require_contains "$ego_runbook" 'completeTaskSpace' 'runbook complete cleanup primitive'
require_contains "$ego_runbook" 'GPT-5\.6 Sol' 'runbook Sol model truth gate'
require_contains "$ego_runbook" 'Reasoning[[:space:]]*=[[:space:]]*High' 'runbook Sol reasoning gate'
require_contains "$ego_runbook" 'Duplicate-Send Safety' 'runbook duplicate-send safety'
require_contains "$ego_runbook" 'Never automatically resend' 'runbook no auto-resend'
require_contains "$ego_runbook" 'NOT_SENT → SENT \| UNKNOWN' 'runbook send state machine'
require_contains "$ego_runbook" 'no retry transition' 'runbook terminal UNKNOWN no retry'
require_contains "$ego_runbook" 'AUTH_REQUIRED' 'runbook auth required failure state'
require_contains "$ego_runbook" 'USER_CONTROLLING' 'runbook control conflict failure state'
require_contains "$ego_runbook" 'MODEL_MISMATCH' 'runbook model mismatch failure state'
require_contains "$ego_runbook" 'handOffTaskSpace' 'runbook handoff primitive'
require_contains "$ego_runbook" 'takeOverTaskSpace' 'runbook takeover primitive'

require_contains "$evals_readme" 'ego-browser' 'evals README references ego-browser'
require_contains "$evals_readme" 'resources/ego-browser-runbook\.md' 'evals README references runbook'
require_contains "$evals_readme" 'First Sol Send executes automatically after preflight without confirmation' 'evals README automatic send'
require_contains "$evals_scenarios" 'resources/ego-browser-runbook\.md' 'evals scenarios reference runbook'
require_contains "$evals_scenarios" 'browser-transport-precedence-runbook' 'evals transport precedence scenario'
require_contains "$evals_scenarios" 'sol-send-duplicate-safety-unknown' 'evals duplicate-send safety scenario'
require_contains "$evals_scenarios" 'sol-pre-send-three-failure-states' 'evals three failure states scenario'
require_contains "$evals_scenarios" 'sol-first-send-chinese-plan-automatic-send' 'evals automatic send scenario'
require_contains "$evals_scenarios" 'sol-interaction-authority-precedence' 'evals authority precedence scenario'

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
  "$root/resources"
  "$root/templates"
  "$root/examples"
  "$root/evals"
)

if grep -REn -- 'agy-run\.sh|tty7|agy -p|--conversation[[:space:]]+<real-conversation-id>' "${active[@]}" >/dev/null; then
  printf 'Documentation validation failed: removed AGY runtime path remains in active docs/templates/evals.\n' >&2
  grep -REn -- 'agy-run\.sh|tty7|agy -p|--conversation[[:space:]]+<real-conversation-id>' "${active[@]}" >&2 || true
  exit 1
fi

if grep -REn -- 'Chrome DevTools|DevTools MCP|chrome-devtools|approved Chrome session' "${active[@]}" >/dev/null; then
  printf 'Documentation validation failed: stale active Chrome transport terms remain in active docs/templates/evals.\n' >&2
  grep -REn -- 'Chrome DevTools|DevTools MCP|chrome-devtools|approved Chrome session' "${active[@]}" >&2 || true
  exit 1
fi

if grep -REn -- 'one confirmation only|confirm the \*\*first Send once\*\*|confirm the first Send once|ask for one Send confirmation|ask for one confirmation|First Sol Send asks for confirmation|confirmed once|只确认.*一次|确认一次|用户确认一次|首轮发送只确认一次|用户确认第一轮发送|第一轮已经确认后|一次确认' "${active[@]}" >/dev/null; then
  printf 'Documentation validation failed: stale first-Send confirmation wording remains in active docs/templates/evals.\n' >&2
  grep -REn -- 'one confirmation only|confirm the \*\*first Send once\*\*|confirm the first Send once|ask for one Send confirmation|ask for one confirmation|First Sol Send asks for confirmation|confirmed once|只确认.*一次|确认一次|用户确认一次|首轮发送只确认一次|用户确认第一轮发送|第一轮已经确认后|一次确认' "${active[@]}" >&2 || true
  exit 1
fi

printf 'Documentation validation passed.\n'
