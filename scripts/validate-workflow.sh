#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/agy-supervised-v4.XXXXXX")"
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

# Pre-existing user state: staged + unstaged + untracked.
printf 'user-staged\n' >> tracked.txt
git add tracked.txt
printf 'user-unstaged\n' >> tracked.txt
printf 'user-untracked\n' > user-note.txt

baseline="$tmp/baseline"
bash "$root/scripts/snapshot-code-state.sh" "$baseline" "$baseline_commit" >/dev/null
[[ "$(cat "$baseline/head.txt")" == "$baseline_commit" ]]
grep -q 'user-note.txt' "$baseline/untracked.sha256"
baseline_digest="$(cat "$baseline/code-state.sha256")"

# Task adds another untracked file; digest must change without committing it.
printf 'task-new-content\n' > task-new.txt
after="$tmp/after"
bash "$root/scripts/snapshot-code-state.sh" "$after" "$baseline_commit" >/dev/null
after_digest="$(cat "$after/code-state.sha256")"
[[ "$baseline_digest" != "$after_digest" ]]
grep -q 'task-new.txt' "$after/untracked.sha256"

# A staged mutation must also invalidate the prior digest.
printf 'task-staged\n' >> tracked.txt
git add tracked.txt
after2="$tmp/after2"
bash "$root/scripts/snapshot-code-state.sh" "$after2" "$baseline_commit" >/dev/null
[[ "$after_digest" != "$(cat "$after2/code-state.sha256")" ]]

# A clean task commit after a baseline must appear in the committed-delta artifact.
repo2="$tmp/repo-committed"
mkdir -p "$repo2"
cd "$repo2"
git init -q
git config user.email test@example.invalid
git config user.name test
printf 'before\n' > committed.txt
git add committed.txt
git commit -qm base
base2="$(git rev-parse HEAD)"
printf 'after\n' > committed.txt
git add committed.txt
git commit -qm task
committed_snapshot="$tmp/committed-snapshot"
bash "$root/scripts/snapshot-code-state.sh" "$committed_snapshot" "$base2" >/dev/null
grep -q '^+after$' "$committed_snapshot/diff-baseline-to-head.patch"

# jq extraction used by the Herdr runbook must fail closed on null/empty IDs.
printf '%s' '{"result":{"workspace":{"workspace_id":"w1"},"root_pane":{"pane_id":"p1"}}}' \
  | jq -er '.result.workspace.workspace_id | strings | select(length > 0)' >/dev/null
if printf '%s' '{"result":{"workspace":{"workspace_id":null},"root_pane":{"pane_id":"p1"}}}' \
  | jq -er '.result.workspace.workspace_id | strings | select(length > 0)' >/dev/null 2>&1; then
  echo 'null workspace id must fail' >&2; exit 1
fi

# Run State template must use honest non-started defaults.
python3 - "$root/templates/run-state.json" "$root/evals/scenarios.json" <<'PY'
import json, sys
s=json.load(open(sys.argv[1], encoding='utf-8'))
e=json.load(open(sys.argv[2], encoding='utf-8'))
assert s['supervisor']['handoff_status']=='NOT_SPAWNED'
assert s['supervisor']['model_status']=='NOT_STARTED'
assert s['dispatch_state']=='NOT_SENT'
assert 'baseline_artifacts' in s
required={
 'no-fake-luna-handoff','requested-model-unverified','protect-user-changes',
 'review-untracked-content','review-staged-and-committed','project-gates-remain-binding',
 'worker-report-not-proof','evidence-invalidated-by-code-change','no-progress-escalates',
 'environment-blocker-bounded','busy-worker-no-duplicate-dispatch','unknown-send-no-resend',
 'recovery-does-not-guess-session','cannot-accept-incomplete','contract-patch-authority'
}
ids={c['id'] for c in e['cases']}
assert required <= ids
PY

printf 'DETERMINISTIC_WORKFLOW_TESTS_PASS\n'
