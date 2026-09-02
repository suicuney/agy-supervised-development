#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

readme="$root/README.md"
plugin_skill="$root/skills/agy-supervised-development/SKILL.md"

require_contains() {
  local file="$1" pattern="$2" label="$3"
  grep -Eq -- "$pattern" "$file" || { printf 'Documentation validation failed: %s\n' "$label" >&2; exit 1; }
}

# Check only stable routing/version contracts. Do not validate prose wording.
require_contains "$readme" '3\.2\.0-alpha\.2' 'README version'
require_contains "$readme" 'codex plugin marketplace add' 'plugin install command'
require_contains "$plugin_skill" 'Read `\.\./\.\./SKILL\.md`' 'plugin routes to workflow kernel'
require_contains "$plugin_skill" 'review-gates\.md' 'review rules routing'
require_contains "$plugin_skill" 'runtime-verification\.md' 'runtime verification routing'

printf 'Documentation validation passed.\n'
