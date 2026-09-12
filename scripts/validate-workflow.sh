#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/agy-supervised-v41.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
repo="$tmp/repo"
mkdir -p "$repo"
cd "$repo"
git init -q
git config user.email test@example.invalid
git config user.name test
printf 'base\n' > tracked.txt
git add tracked.txt
git commit -qm base
baseline_commit="$(git rev-parse HEAD)"

printf 'user-staged\n' >> tracked.txt
git add tracked.txt
printf 'user-unstaged\n' >> tracked.txt
printf 'user-untracked\n' > user-note.txt
baseline="$tmp/baseline"
bash "$root/scripts/snapshot-code-state.sh" "$baseline" "$baseline_commit" >/dev/null
grep -q 'user-note.txt' "$baseline/untracked.sha256"
base_digest="$(cat "$baseline/code-state.sha256")"

printf 'task-new\n' > task-new.txt
after="$tmp/after"
bash "$root/scripts/snapshot-code-state.sh" "$after" "$baseline_commit" >/dev/null
[[ "$base_digest" != "$(cat "$after/code-state.sha256")" ]]
grep -q 'task-new.txt' "$after/untracked.sha256"

python3 - "$root/templates/run-state.json" "$root/evals/scenarios.json" <<'PY'
import json, sys
s=json.load(open(sys.argv[1], encoding='utf-8'))
e=json.load(open(sys.argv[2], encoding='utf-8'))
assert s['phase']=='IMPLEMENT'
assert s['code_review']['result']=='NOT_RUN'
assert s['test_plan']['status']=='NOT_CREATED'
required={
 'implementation-does-not-formally-test','astra-code-review-runs-no-tests',
 'code-review-rework-loop','test-plan-after-code-review','agy-cannot-weaken-test-metrics',
 'no-second-astra-test-review','code-change-during-test-invalidates-review',
 'protect-user-changes','review-complete-delta','project-rules-shape-review-and-tests',
 'herdr-only-agy','busy-worker-no-duplicate-dispatch','unknown-send-no-resend',
 'recovery-does-not-guess-session','environment-blocker-does-not-change-metrics',
 'completion-requires-current-digest'
}
ids={c['id'] for c in e['cases']}
assert required <= ids
assert e['version']=='4.1.0-alpha.1'
PY

# Active docs must encode phase separation and must not depend on Luna.
grep -q 'IMPLEMENT ONLY' "$root/resources/agy-execution.md"
grep -q 'does not run tests' "$root/SKILL.md"
grep -q 'Astra does not execute the tests' "$root/resources/testing.md"
grep -q 'Any subsequent production-code change invalidates this pass' "$root/resources/code-review.md"

printf 'DETERMINISTIC_WORKFLOW_TESTS_PASS\n'
