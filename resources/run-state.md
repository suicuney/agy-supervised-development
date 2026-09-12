# Run State and Recovery

Run State is operational state. It is not part of the user-facing Development Contract.

## Location

Store each task under Git-private storage so it cannot be accidentally committed:

```bash
run_dir="$(git rev-parse --git-path "agy-supervised/runs/$task_id")"
mkdir -p "$run_dir"
state_file="$run_dir/run-state.json"
```

Do not store credentials, environment dumps, full chat history, or unrelated source content.

## Minimum state

Record:

- `task_id`
- `contract_id`, `contract_revision`
- `repo_root`, `working_directory`, `branch`, `baseline_commit`
- baseline artifact references for initial status/staged/unstaged/untracked state
- supervisor task identity and requested/runtime model evidence
- Herdr `workspace_id`, `pane_id`, AGY agent name; native session id only when actually returned
- `current_round`, finding ids and progress counters
- dispatch state: `NOT_SENT | SENT | SEND_UNKNOWN | SETTLED`
- `current_status`
- current code-state digest
- verification results with evidence binding

Use `schemas/run-state.schema.json` and `templates/run-state.json` as the portable shape.

## Contract patches

A material Contract patch is authorized only by the user or architect. Record:

```text
previous revision
new revision
changed fields
reason
actor
```

The supervisor may request a patch but may not silently perform one.

## Baseline

Before the first AGY write, capture enough state to attribute later changes:

```bash
git rev-parse HEAD
git status --porcelain=v2 --branch
git diff --binary HEAD
git diff --cached --binary
git diff --binary
# plus contents/hashes for untracked files
```

`scripts/snapshot-code-state.sh <output-dir>` provides a deterministic capture. Preserve the baseline artifacts in the task run directory.

A baseline with user changes is valid. Do not auto-stash, reset, clean, or rewrite it.

## Direct checkout vs worktree

Use the current checkout when it is clean enough for single-writer execution and no parallel writer exists.

Prefer a task worktree when existing user changes, parallel writers, or explicit isolation make attribution unsafe. A Herdr workspace does not isolate Git files.

If the task depends on uncommitted changes, a clean worktree from HEAD is insufficient. Preserve the prerequisite content explicitly (for example by creating the worktree from a task commit only with authority, or by applying a captured patch/content deliberately). Never silently drop those prerequisites.

## Code-state digest

Verification must bind to the actual deliverable, not only `HEAD`. `snapshot-code-state.sh` records a digest over:

- HEAD identity
- staged diff
- unstaged diff
- untracked file path + content hash

If any relevant code changes after a verification, mark affected evidence stale and rerun only the checks whose validity depended on the changed surface.

## Recovery

On resume/recovery:

1. Read current Git state and Run State.
2. Confirm `repo_root`, working directory, branch/worktree, Contract revision and baseline identity match.
3. Confirm whether the recorded supervisor and Herdr worker still exist before creating replacements.
4. Never guess another host session or native AGY conversation.
5. Never replay a command whose side-effect status is unknown.
6. Start a replacement worker only after the prior worker is confirmed stopped/unrecoverable and no parallel write risk remains.
7. Give replacements: Contract, project rules, current code state, unresolved findings, and still-valid verification evidence.

A mismatch becomes `RECOVERY_BLOCKED` until investigated; do not silently reconstruct state from assumptions.
