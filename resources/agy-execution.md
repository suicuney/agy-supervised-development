# AGY Execution — Herdr Only

AGY is the only writer and every AGY execution goes through Herdr.

```text
Luna supervisor
→ Herdr
→ AGY
→ repository
→ Git + independent verification
```

Herdr owns runtime identity and lifecycle. It does not own Contract decisions or acceptance.

## Preflight

Before starting a worker:

```bash
scripts/check-herdr.sh
```

`HERDR_ENVIRONMENT_READY` means only that the local Herdr/AGY integration preconditions checked by the script are ready. It does **not** prove AGY authentication, a successful task run, or end-to-end delivery.

Never install/reinstall hooks or integrations automatically during task execution.

## Workspace and IDs

Create a task workspace on the chosen code working directory (current checkout or task worktree):

```bash
created="$(herdr workspace create --cwd "$working_directory" --label "$task_id" --no-focus)"
```

Read IDs only from returned structured data and validate both type and value:

```bash
workspace_id="$(printf '%s' "$created" | jq -er '.result.workspace.workspace_id | strings | select(length > 0)')"
pane_id="$(printf '%s' "$created" | jq -er '.result.root_pane.pane_id | strings | select(length > 0)')"
```

A JSON `null`, empty value, missing field, or non-string is invalid. Record valid IDs in Run State.

Herdr workspace creation is terminal/runtime setup, not Git isolation.

## Start worker

Use one stable task-local AGY name and record it:

```bash
herdr agent start "$agy_agent" --kind agy --pane "$pane_id"
```

Before every round, inspect the worker state/output enough to establish that it is not still executing the previous round. Do not stack duplicate prompts onto a busy worker.

## Dispatch

Each prompt includes `task_id`, `round`, Contract revision, applicable repository rules, and the bounded work/finding for that round.

Track dispatch state in Run State:

```text
NOT_SENT → SENT → SETTLED
        ↘ SEND_UNKNOWN
```

Use a bounded wait:

```bash
herdr agent prompt "$agy_agent" "$worker_order" \
  --wait --until idle --until done --until blocked --timeout "$timeout_ms"
```

Herdr help warns that a wait can match the end of existing work rather than prove a particular prompt round completed. Therefore correlate completion with the round marker in worker output plus repository evidence; do not use lifecycle state alone.

If prompt delivery/return is ambiguous, set `SEND_UNKNOWN`, read state/output and investigate. Never automatically resend an uncertain prompt.

A timeout means `WAIT_TIMEOUT`, not failure and not permission to resend. Read the worker first.

## Blocked / interaction

When blocked:

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 160
```

Classify the reason before interaction:

- reversible implementation choice inside Contract → supervisor may continue;
- environment/auth/dependency issue → `BLOCKED`, do not rewrite business requirements to bypass it;
- product, architecture, destructive or one-way decision → escalate to architect/user as required.

Do not blindly send keys based on `blocked` status.

## Worker completion report

AGY reports:

```text
task_id / round / contract_revision
changed behavior + files
tests/checks actually run + exit status
NOT_RUN / BLOCKED checks
known limitations
unresolved findings
self-review summary
```

The report is an index into evidence, not independent proof.

## Rework

Reuse the same worker when safe. A rework prompt contains only the Contract reference plus bounded finding/evidence/required outcome. Increment the round and finding progress counters.

Two consecutive rounds without substantive progress on the same finding default to `ESCALATE`. A configurable policy may lower/raise that threshold, but never allow unbounded rework.

## Session loss and replacement

If exact Herdr/native session identity can be restored, reuse it. If it cannot:

- do not guess another conversation;
- inspect Run State and current Git state;
- confirm the old worker is stopped/unrecoverable and cannot write in parallel;
- only then start a replacement Herdr-managed AGY;
- pass Contract + project rules + current code state + unresolved findings + valid verification state.

Never replay a command with unknown side effects simply because the session disappeared.

## Close

Close only Herdr workspaces created for this task and only after the worker is confirmed no longer writing:

```bash
herdr workspace close "$workspace_id"
```

`Herdr done/idle != delivery accepted`.
