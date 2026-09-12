# Run State, Baseline, and Recovery

Run State is operational state, separate from the Development Contract. Runtime JSON uses `schemas/run-state.schema.json`; old pre-v2 Run State is not silently upgraded to PASS. Rebuild/revalidate the current phase when migration evidence is incomplete.

## Location

Store task state/evidence under Git-private storage or outside the worktree:

```bash
run_dir="$(git rev-parse --git-path "agy-supervised/runs/$task_id")"
mkdir -p "$run_dir/evidence"
chmod 700 "$run_dir" "$run_dir/evidence"
```

Do not store credentials, full chat history or unrelated environment dumps.

## Baseline and snapshots

Before AGY first writes:

```bash
baseline_commit="$(git rev-parse HEAD)"
scripts/snapshot-code-state.sh "$run_dir/baseline" "$baseline_commit"
```

The snapshot is captured from repository root even when invoked from a subdirectory and is atomically published only after two observed manifests match. This detects changes during the capture window; it is **not** OS-level write isolation.

Two identities are intentionally separate:

- `deliverable_digest` — path/type/content/link target/executable identity for tracked and non-ignored untracked deliverable files. `git add` alone does not change it.
- `ownership_digest` — HEAD/baseline/status/index ownership identity used for recovery/attribution; staging or HEAD changes may change it.

Git evidence also retains NUL-delimited porcelain state and binary diffs for baseline→HEAD, index, worktree and HEAD, so committed/staged/unstaged changes, deletes, renames and mode/binary changes remain inspectable.

## Untracked and special content

Untracked regular-file original bytes are archived locally as mode-0600 content-addressed blobs under the snapshot directory, so baseline content can be reconstructed. The manifest uses base64 path encoding plus stable ordering for spaces/newlines/Unicode. Symlinks record target bytes only and are never followed; dangling-link target changes change the deliverable digest.

Sensitive-looking untracked files (`.env`, keys, credentials, etc.) fail closed unless an exact path is explicitly allowed with `--allow-sensitive-untracked`. Ignored acceptance inputs require exact `--include-ignored` coverage and should also appear as Test Plan `input_paths`. Unsupported special file types and submodules fail closed in this version when they enter the captured deliverable; do not issue valid evidence by silently skipping them.

Snapshot output may not live in the worktree because it would recursively pollute itself. Use Git-private storage or an external directory.

## State transitions

The semantic validator owns legal transition checks:

```text
CONTRACT → IMPLEMENT → CODE_REVIEW
CODE_REVIEW → IMPLEMENT_REWORK → CODE_REVIEW
CODE_REVIEW → TEST_PLAN → TEST
TEST → TEST_REWORK → CODE_REVIEW
any active phase → BLOCKED → validated resume phase
TEST → COMPLETE only via deterministic completion check
```

Use:

```bash
scripts/validate-run-state.sh transition ...
scripts/validate-run-state.sh block ...
scripts/validate-run-state.sh invalidate ...
scripts/validate-run-state.sh complete ...
```

Writes use a sidecar file lock, `state_version` optimistic check, fsync and atomic replace. This prevents lost updates among cooperating local processes; it is not claimed as a sandbox against arbitrary filesystem writers.

## BLOCKED

A persisted blocker records `reason`, `blocked_from_phase`, `resume_action`, and related execution identity. Resume requires the writer stopped, repository/worktree identity still matching, current Contract still matching, and a fresh snapshot. Phase name alone never authorizes skipping review/test validation.

## Recovery

On resume:

1. Read current Git state and Run State from disk.
2. Validate schema and current Contract id/revision.
3. Recheck repository/worktree and baseline identity/relationship.
4. Check the recorded Herdr/AGY worker before replacing it.
5. Never guess a lost session or replay a side-effecting command whose send/result is uncertain.
6. Never start a second writer until the prior writer is confirmed stopped/unrecoverable with no parallel-write risk.
7. Restore only current-phase context: Contract + diagnostics/findings for implementation, or the exact frozen plan for TEST.

`SEND_UNKNOWN` is investigated, never auto-resent. `Herdr idle/done` remains runtime lifecycle only.
