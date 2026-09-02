#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: agy-run.sh [--repo PATH] [--mode build|consult] [--timeout DURATION] [--conversation ID] [--add-dir PATH]... PROMPT

Options must appear before PROMPT. Arguments after the first prompt token are joined into the prompt text.
EOF
}

repo=""
mode="build"
timeout="30m"
conversation=""
add_dirs=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      repo="$2"; shift 2 ;;
    --mode)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      mode="$2"; shift 2 ;;
    --timeout|--print-timeout)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      timeout="$2"; shift 2 ;;
    --conversation)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      conversation="$2"; shift 2 ;;
    --add-dir)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      add_dirs+=("$2"); shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    --)
      shift; break ;;
    -*)
      printf 'Unknown option: %s\n' "$1" >&2
      usage; exit 2 ;;
    *)
      break ;;
  esac
done

[[ "$mode" == "build" || "$mode" == "consult" ]] || { printf 'Invalid mode: %s\n' "$mode" >&2; exit 2; }
[[ $# -ge 1 ]] || { usage; exit 2; }
command -v agy >/dev/null 2>&1 || { printf 'agy was not found on PATH.\n' >&2; exit 127; }
command -v git >/dev/null 2>&1 || { printf 'git was not found on PATH.\n' >&2; exit 127; }

if [[ -z "$repo" ]]; then
  repo="$(git rev-parse --show-toplevel 2>/dev/null || true)"
fi
[[ -n "$repo" ]] || { printf 'Unable to resolve repository root. Pass --repo PATH.\n' >&2; exit 2; }
repo="$(cd "$repo" && pwd)"
git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1 || { printf 'Not a Git repository: %s\n' "$repo" >&2; exit 2; }
repo_root="$(git -C "$repo" rev-parse --show-toplevel)"
cd "$repo_root"

prompt="$*"
if [[ "$mode" == "consult" ]]; then
  prompt="Read-only consultation. Do not modify files, run write commands, apply patches, commit, push, merge, deploy, or mutate external systems. Return findings/advice only. ${prompt}"
fi

args=(-p "$prompt" --output-format stream-json --print-timeout "$timeout")
if [[ -n "$conversation" ]]; then
  args+=(--conversation "$conversation")
fi
for dir in "${add_dirs[@]}"; do
  args+=(--add-dir "$dir")
done

exec agy "${args[@]}"
