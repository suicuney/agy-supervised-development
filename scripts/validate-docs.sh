#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

require_contains() {
  grep -Eq -- "$2" "$1" || { printf 'Documentation validation failed: %s\n' "$3" >&2; exit 1; }
}

readme="$root/README.md"
kernel="$root/SKILL.md"
entry="$root/skills/agy-supervised-development/SKILL.md"
contract="$root/resources/development-contract.md"
supervisor="$root/resources/supervisor.md"
verification="$root/resources/verification.md"
execution="$root/resources/agy-execution.md"

require_contains "$readme" '4\.0\.0-alpha\.3' 'README version'
require_contains "$readme" 'ASTRA: CONTRACT' 'simple flow'
require_contains "$readme" 'LUNA: SUPERVISE' 'supervisor flow'
require_contains "$readme" 'model=UNVERIFIED' 'unverified model visibility'
require_contains "$kernel" 'Routing proves itself' 'observable routing principle'
require_contains "$kernel" 'runtime exposes evidence' 'runtime handoff evidence'
require_contains "$kernel" 'UNVERIFIED' 'no fabricated model identity'
require_contains "$kernel" 'WHAT / BOUNDARY / DONE' 'architect boundary'
require_contains "$kernel" 'Every AGY run goes through Herdr' 'Herdr-only execution'
require_contains "$kernel" 'Do not preload' 'progressive disclosure'
require_contains "$entry" 'canonical router' 'entry routes to kernel'
require_contains "$contract" 'CONTRACT FROZEN' 'contract freeze'
require_contains "$contract" 'AGY owns normal `HOW`' 'worker autonomy'
require_contains "$supervisor" 'PASS \| REWORK \| ESCALATE' 'supervisor outcomes'
require_contains "$supervisor" 'does not re-plan' 'supervisor boundary'
require_contains "$verification" 'targeted tests or runtime evidence' 'targeted verification'
require_contains "$execution" 'herdr workspace create' 'Herdr workspace'
require_contains "$execution" 'agent start.*agy|--kind agy' 'Herdr AGY start'

printf 'Documentation validation passed.\n'
