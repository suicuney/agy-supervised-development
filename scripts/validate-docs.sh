#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

readme="$root/README.md"
plugin_skill="$root/skills/agy-supervised-development/SKILL.md"
kernel="$root/SKILL.md"
architect="$root/resources/architect.md"
contract="$root/resources/development-contract.md"
supervisor="$root/resources/supervisor.md"
escalation="$root/resources/escalation.md"
verification="$root/resources/verification.md"
agy_execution="$root/resources/agy-execution.md"
failure_modes="$root/resources/failure-modes.md"

require_contains() {
  local file="$1" pattern="$2" label="$3"
  grep -Eq -- "$pattern" "$file" || { printf 'Documentation validation failed: %s\n' "$label" >&2; exit 1; }
}

require_contains "$readme" '4\.0\.0-alpha\.1' 'README version'
require_contains "$readme" 'codex/agy-supervised-v4-astra-skill' '4.0 branch install command'
require_contains "$readme" 'ASTRA ARCHITECT' 'README architect stage'
require_contains "$readme" 'LUNA SUPERVISOR' 'README supervisor stage'
require_contains "$readme" 'CONTRACT FROZEN' 'README contract freeze'
require_contains "$readme" 'AGY SELF-REVIEW' 'README AGY self review'
require_contains "$readme" 'Sol High Plan Review.*不再属于默认主流程|不再属于默认主流程' 'Sol review is optional'
require_contains "$readme" 'check-herdr\.sh' 'Herdr preflight'

require_contains "$plugin_skill" 'Read `\.\./\.\./SKILL\.md`' 'plugin routes to workflow kernel'
require_contains "$plugin_skill" 'Development Contract' 'plugin contract routing'
require_contains "$plugin_skill" 'Luna supervises' 'plugin supervisor role'
require_contains "$plugin_skill" 'Every AGY execution must be Herdr-managed' 'plugin Herdr-only rule'
require_contains "$plugin_skill" 'Legacy Sol High plan review is not part of the default path' 'plugin legacy Sol boundary'

require_contains "$kernel" 'Astra frames\. Luna supervises\. AGY builds\. Git tells the truth\.' 'kernel slogan'
require_contains "$kernel" 'architect owns `WHAT / WHY / BOUNDARY / DONE`' 'architect ownership boundary'
require_contains "$kernel" 'AGY owns normal implementation planning' 'AGY implementation autonomy'
require_contains "$kernel" 'Luna may supervise' 'Luna supervision authority'
require_contains "$kernel" 'Escalate to Astra only' 'strong-model escalation rule'
require_contains "$kernel" 'Every AGY invocation runs through Herdr' 'Herdr-only runtime rule'
require_contains "$kernel" 'Do not preload all resources' 'progressive disclosure rule'
require_contains "$kernel" 'pointer-over-copy' 'context economy rule'

require_contains "$architect" 'WHAT / WHY / BOUNDARY / DONE' 'architect contract ownership'
require_contains "$architect" 'Do not perform a full repository read by default' 'architect context budget'
require_contains "$architect" 'CONTRACT FROZEN' 'architect exit boundary'

require_contains "$contract" 'Development Contract' 'contract resource title'
require_contains "$contract" 'CONTRACT FROZEN' 'contract freeze semantics'
require_contains "$contract" 'Contract Patch' 'contract patch semantics'
require_contains "$contract" 'Luna may request an escalation' 'supervisor cannot patch contract'

require_contains "$supervisor" 'lower-cost' 'supervisor cost role'
require_contains "$supervisor" 'diff-first review' 'supervisor diff-first policy'
require_contains "$supervisor" 'Do not escalate routine failures' 'supervisor escalation discipline'
require_contains "$supervisor" 'AGY self-review is useful evidence, not acceptance' 'independent review boundary'

require_contains "$escalation" 'Architecture conflict' 'architecture escalation'
require_contains "$escalation" 'Repeated core failure' 'repeated failure escalation'
require_contains "$escalation" 'Do Not Escalate For' 'negative escalation rules'
require_contains "$escalation" 'CONTRACT_PATCH' 'contract patch result'

require_contains "$verification" 'evidence-driven review' 'verification evidence strategy'
require_contains "$verification" 'narrowest relevant verification seam first' 'targeted verification rule'
require_contains "$verification" 'PASS.*REWORK.*ESCALATE.*BLOCKED|PASS' 'verification outcomes'

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
  exit 1
fi

printf 'Documentation validation passed.\n'
