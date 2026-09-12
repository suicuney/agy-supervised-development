#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require_contains() { grep -Eq -- "$2" "$1" || { printf 'Documentation validation failed: %s\n' "$3" >&2; exit 1; }; }

readme="$root/README.md"
changelog="$root/CHANGELOG.md"
kernel="$root/SKILL.md"
entry="$root/skills/agy-supervised-development/SKILL.md"
contract="$root/resources/development-contract.md"
handoff="$root/resources/codex-supervisor-handoff.md"
runstate="$root/resources/run-state.md"
supervisor="$root/resources/supervisor.md"
verification="$root/resources/verification.md"
execution="$root/resources/agy-execution.md"
evals="$root/evals/scenarios.json"
paper_example="$root/examples/project-rules-paper-info-web.md"

require_contains "$readme" '4\.0\.0-alpha\.4' 'README version'
require_contains "$changelog" '\[4\.0\.0-alpha\.4\]' 'CHANGELOG version'
require_contains "$readme" 'STATIC_VALID' 'readiness levels'
require_contains "$readme" 'FLOW_VERIFIED' 'flow verification distinction'
require_contains "$kernel" 'WHAT / BOUNDARY / DONE' 'compact contract boundary'
require_contains "$kernel" 'fork_turns: "none"' 'minimal-context supervisor handoff'
require_contains "$kernel" 'Every AGY execution goes through Herdr' 'Herdr-only rule'
require_contains "$entry" 'canonical router' 'entry routes to kernel'
require_contains "$contract" 'revision: 1' 'versioned contract'
require_contains "$contract" 'architect or user' 'patch authority'
require_contains "$handoff" 'spawn_agent' 'real host handoff'
require_contains "$handoff" 'REQUESTED_UNVERIFIED' 'honest model evidence'
require_contains "$handoff" 'NOT_SPAWNED' 'missing handoff distinction'
require_contains "$runstate" 'git rev-parse --git-path' 'git-private run state'
require_contains "$runstate" 'Never replay' 'recovery side-effect safety'
require_contains "$supervisor" 'Two consecutive no-progress rounds' 'bounded rework'
require_contains "$supervisor" 'SEND_UNKNOWN' 'duplicate dispatch safety'
require_contains "$verification" 'committed task changes after baseline' 'committed delta review'
require_contains "$verification" 'untracked file contents' 'untracked content review'
require_contains "$verification" 'PASS \| FAIL \| BLOCKED \| NOT_RUN \| NOT_APPLICABLE' 'verification result taxonomy'
require_contains "$execution" 'jq -er' 'validated Herdr ids'
require_contains "$execution" 'SEND_UNKNOWN' 'Herdr send uncertainty'
require_contains "$evals" 'SCENARIOS_DEFINED_NOT_EXECUTED' 'semantic eval honesty'
require_contains "$paper_example" 'contracts/openapi\.yaml' 'paper-info OpenAPI authority'
require_contains "$paper_example" 'Browser Worker' 'paper-info parked worker rule'
require_contains "$paper_example" 'Maven|mvn|pnpm' 'paper-info quality gates'

# Historical/migration notes may name 3.x concepts, but active instructions must not
# re-enable their default gates or old planning/review contracts.
if grep -REn --exclude-dir=legacy -- \
  'Plan review is enabled by default|PLAN FROZEN|After rework, perform the full Three-Axis Review again|Codex first completes the executable plan from the current Shape|Source Spec:|Change Shape: vertical-slice' \
  "$root/SKILL.md" "$root/README.md" "$root/resources" "$root/templates" "$root/examples" "$root/evals" "$root/skills" >/dev/null; then
  printf 'Documentation validation failed: legacy 3.3 default behavior remains active.\n' >&2
  exit 1
fi

printf 'STATIC_DOCS_VALID\n'
