#!/usr/bin/env bash
set -euo pipefail

out_dir="${1:-}"
baseline_commit="${2:-}"
[[ -n "$out_dir" ]] || { echo 'usage: snapshot-code-state.sh <output-dir> [baseline-commit]' >&2; exit 2; }
repo_root="$(git rev-parse --show-toplevel)"
mkdir -p "$out_dir"

head="$(git rev-parse HEAD 2>/dev/null || true)"
branch="$(git symbolic-ref --short -q HEAD || true)"
printf '%s\n' "$repo_root" > "$out_dir/repo-root.txt"
printf '%s\n' "$head" > "$out_dir/head.txt"
printf '%s\n' "$branch" > "$out_dir/branch.txt"
printf '%s\n' "$baseline_commit" > "$out_dir/baseline-commit.txt"

git status --porcelain=v2 --branch > "$out_dir/status.porcelain-v2"
git diff --binary HEAD > "$out_dir/diff-head.patch" || true
git diff --cached --binary > "$out_dir/diff-cached.patch" || true
git diff --binary > "$out_dir/diff-worktree.patch" || true

: > "$out_dir/diff-baseline-to-head.patch"
if [[ -n "$baseline_commit" ]]; then
  git rev-parse --verify "${baseline_commit}^{commit}" >/dev/null 2>&1 || {
    printf 'Invalid baseline commit: %s\n' "$baseline_commit" >&2
    exit 2
  }
  git diff --binary "$baseline_commit"..HEAD > "$out_dir/diff-baseline-to-head.patch"
fi

git ls-files --others --exclude-standard -z > "$out_dir/untracked.zlist"
: > "$out_dir/untracked.sha256"
while IFS= read -r -d '' path; do
  if [[ -f "$repo_root/$path" ]]; then
    hash="$(shasum -a 256 "$repo_root/$path" | awk '{print $1}')"
    printf '%s  %s\n' "$hash" "$path" >> "$out_dir/untracked.sha256"
  else
    printf 'NON_REGULAR  %s\n' "$path" >> "$out_dir/untracked.sha256"
  fi
done < "$out_dir/untracked.zlist"

{
  printf 'HEAD=%s\n' "$head"
  cat "$out_dir/diff-cached.patch"
  cat "$out_dir/diff-worktree.patch"
  cat "$out_dir/untracked.sha256"
} | shasum -a 256 | awk '{print $1}' > "$out_dir/code-state.sha256"

printf 'CODE_STATE_SNAPSHOT=%s\n' "$out_dir"
printf 'CODE_STATE_DIGEST=%s\n' "$(cat "$out_dir/code-state.sha256")"
