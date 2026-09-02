#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readme="$root/README.md"
plugin_skill="$root/skills/agy-supervised-development/SKILL.md"

require_contains() {
  local file="$1" pattern="$2" label="$3"
  grep -Eq -- "$pattern" "$file" || { printf 'Documentation validation failed: %s\n' "$label" >&2; exit 1; }
}

require_contains "$readme" '3\.2\.0-alpha\.1' 'README version'
require_contains "$readme" 'codex plugin marketplace add' 'plugin marketplace install command'
require_contains "$readme" 'codex plugin add agy-supervised-development@agy-supervised-development' 'plugin install command'
require_contains "$readme" 'NO_BLOCKING_FINDINGS' 'review convergence contract'
require_contains "$readme" 'AGY Consult' 'consult sidecar'
require_contains "$readme" 'scripts/test-readiness\.sh' 'readiness validator'
require_contains "$plugin_skill" 'Read `\.\./\.\./SKILL\.md` as the workflow kernel' 'plugin skill routes to canonical kernel'
require_contains "$plugin_skill" 'NO_BLOCKING_FINDINGS != ACCEPTED' 'acceptance boundary preserved'
require_contains "$plugin_skill" 'agy-run\.sh' 'thin runtime adapter documented'

printf 'Documentation validation passed.\n'
