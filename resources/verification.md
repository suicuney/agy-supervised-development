# Verification and Acceptance

AGY self-reviews; Luna independently verifies the actual delivery state.

## Project rules first

Read applicable `AGENTS.md` files and Contract-referenced constraints before choosing verification. Repository-required gates remain authoritative. "Cheapest decisive check first" defines order, not permission to skip required checks.

Example adaptation: a repository may require OpenAPI/client/traceability updates for public API changes or exclude a parked worker from default builds. Those are repository rules, not global defaults.

## Full task delta

Final review must account for all task-attributed changes relative to baseline:

```text
committed task changes after baseline
+ staged changes
+ unstaged changes
+ untracked file contents
+ deletions / renames
+ relevant binary changes
```

Do not rely only on plain `git diff`. For untracked text files, inspect actual content; for binary/unreadable files, inspect path/type/size/hash and any task-relevant metadata. Separate baseline user changes from task-introduced changes.

Use `scripts/snapshot-code-state.sh` to capture a reproducible evidence bundle and digest.

## Verification result

Every material check records:

```text
contract_revision
method / command
working_directory
exit_code (when a command ran)
result = PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE
summary
log_ref
code_state_digest
```

Rules:

- A command that did not run is never `PASS`.
- Missing auth/dependency/permission is normally `BLOCKED` or `NOT_RUN`, not `FAIL` unless the gate itself defines that condition as failure.
- `NOT_APPLICABLE` requires a reason.
- AGY saying "tests passed" is only an index; independent evidence is required for acceptance.

## Evidence invalidation

Verification is bound to the actual code state, including uncommitted changes. If code changes after a check, compare the affected surface and mark dependent evidence stale. Rerun the checks that could have been invalidated; do not mechanically rerun unrelated checks.

Before final acceptance, confirm the worker has stopped writing and capture a final code-state digest matching the accepted evidence.

## Verification order

Start narrow, then satisfy applicable project gates:

1. original repro / focused test / static check that can fail fast;
2. required repository checks for the affected surface;
3. integration/runtime/browser checks only when behavior requires them;
4. broader checks when risk, rules, or failures justify them.

Also check missing propagation: callers, consumers, schemas/contracts, generated artifacts, config, persistence/migrations, tests, and documentation when required by behavior or repository rules.

## Acceptance

`ACCEPTED` requires current evidence for the current Contract revision and code state, no unresolved blocker/finding, explainable final delta, and preserved baseline user work.
