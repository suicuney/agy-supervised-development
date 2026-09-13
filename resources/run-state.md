# Run State, Baseline, and Recovery

Run State tracks the current workflow phase and bindings. It does not replace the Contract or test result files.

Current format is `schema_version: 4`. Older extended formats are not auto-migrated to PASS; rebuild the current run evidence when incompatible.

## Baseline / snapshot policy

Before the first AGY write, capture baseline with the frozen snapshot policy. The policy contains only exact ignored inputs and exact sensitive-untracked authorizations. TEST-entry and completion reuse the same policy digest.

Policy paths are normalized before hashing, so equivalent entries such as `./path` and `path`, or different list ordering, bind to the same policy identity. The `--policy` argument must resolve to the same policy file recorded in Run State; later snapshots do not silently switch policy sources.

Relative runtime paths in Run State are resolved from `repo_root`; absolute paths remain supported for Git-private worktree metadata locations.

The snapshot keeps separate identities:

- `deliverable_digest` — actual delivered path/type/content/link target/executable state;
- `ownership_digest` — Git HEAD/index/status attribution used for recovery.

It preserves untracked original content locally and supports binary files, symlinks and executable bits. Existing snapshot output is never overwritten.

Snapshot storage uses Git's reported management directory rather than assuming `<repo>/.git`, so linked worktrees are supported. Detached HEAD is valid and records `branch: null`. Baseline validation checks that the baseline snapshot belongs to the same repository and was captured with `head == baseline_commit == state.baseline.commit`; current HEAD may legitimately advance during the task.

## Phases

```text
CONTRACT → IMPLEMENT → CODE_REVIEW
CODE_REVIEW → IMPLEMENT_REWORK → CODE_REVIEW
CODE_REVIEW → TEST_PLAN → TEST
TEST --invalidate--> TEST_REWORK → CODE_REVIEW
active phase --block--> BLOCKED --resume--> original phase
TEST → COMPLETE
```

`COMPLETE` is terminal. `BLOCKED` is entered only through the `block` command, which records the original phase and recovery action. TEST_REWORK is entered only through the invalidate path so review/plan/results are invalidated consistently.

## Recovery safety

- Resume from BLOCKED only to the recorded original phase.
- Resuming TEST requires the same current frozen Test Plan and valid review/deliverable binding.
- Writer must be STOPPED before resume; `SENT`/`SEND_UNKNOWN` must be resolved first.
- Contract updates require a stopped writer and resolved dispatch; update is rejected while BLOCKED.
- Invalidate/reset for a new work round never hides `SENT` or `SEND_UNKNOWN` dispatch state.
- Do not guess sessions or start another writer while prior writer identity is uncertain.
- Cooperative state writes keep the existing lock, `state_version` check and atomic replace; this is not OS-level isolation.
