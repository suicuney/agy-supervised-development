# Run State and Recovery

Run State is operational state, separate from the Development Contract.

## Location

Store it under Git-private storage:

```bash
run_dir="$(git rev-parse --git-path "agy-supervised/runs/$task_id")"
mkdir -p "$run_dir"
state_file="$run_dir/run-state.json"
```

Do not store credentials, full chat history, or unrelated environment dumps.

## Minimum state

Record:

- `task_id`, `contract_id`, `contract_revision`
- `repo_root`, `working_directory`, `branch`, `baseline_commit`
- baseline artifact references and current code-state digest
- current phase: `IMPLEMENT | CODE_REVIEW | IMPLEMENT_REWORK | TEST_PLAN | TEST | BLOCKED | COMPLETE`
- Herdr `workspace_id`, `pane_id`, AGY agent name; native session ref only when actually returned
- implementation/rework round and open code-review finding IDs
- last `CODE_REVIEW_PASS` digest/revision or null
- frozen `test_plan_id`, plan revision and reviewed code-state digest or null
- per-check test results and evidence refs
- dispatch state: `NOT_SENT | SENT | SEND_UNKNOWN | SETTLED`

Use `schemas/run-state.schema.json` and `templates/run-state.json`.

## Baseline

Before AGY's first write:

```bash
baseline_commit="$(git rev-parse HEAD)"
baseline_dir="$run_dir/baseline"
bash scripts/snapshot-code-state.sh "$baseline_dir" "$baseline_commit"
```

Preserve existing user changes. Do not auto-stash, reset, clean, or overwrite them.

Use current checkout when single-writer attribution is safe. Prefer a task worktree for concurrent writers or isolation needs. If the task depends on uncommitted content, preserve that prerequisite deliberately rather than silently creating a clean worktree that omits it.

## State transitions

```text
CONTRACT FROZEN
→ IMPLEMENT
→ CODE_REVIEW
   ├─ REWORK → IMPLEMENT_REWORK → CODE_REVIEW
   └─ PASS → TEST_PLAN → TEST
                    ├─ metrics pass → COMPLETE
                    ├─ environment blocker → BLOCKED
                    └─ code changes → CODE_REVIEW
```

Astra's code-review PASS is bound to a code-state digest. A frozen Test Plan is bound to that same reviewed code state.

If production/task code changes after review PASS:

```text
code_review_pass = STALE
frozen_test_plan = STALE
affected test results = STALE
```

Return to `CODE_REVIEW`; never mechanically continue to completion using stale evidence.

## Recovery

On resume:

1. Read current Git state and Run State.
2. Verify repository/worktree, Contract revision, phase, baseline and current code-state relationship.
3. Check whether the recorded Herdr/AGY worker still exists before replacing it.
4. Never guess another session or replay side-effecting commands whose send/result state is uncertain.
5. Start a replacement writer only after the previous writer is confirmed stopped/unrecoverable with no parallel-write risk.
6. Restore only the context for the current phase: implementation findings for code work, or frozen Test Plan for test work.

A mismatch that cannot be safely reconciled becomes `BLOCKED` until investigated.
