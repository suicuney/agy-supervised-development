# AGY Execution — Herdr Only

AGY is the writer/test executor and every AGY execution goes through Herdr.

```text
ASTRA plan/review/test-plan
→ Herdr
→ AGY
→ repository / test evidence
```

Herdr owns runtime identity and lifecycle. It never decides code-review PASS or changes frozen test metrics.

## Preflight

Before starting a worker:

```bash
scripts/check-herdr.sh
```

`HERDR_ENVIRONMENT_READY` proves only the checked local runtime prerequisites. It does not prove AGY auth, successful work, code quality, or test success.

## Workspace and identity

Create/reuse a task-owned Herdr workspace on the selected code checkout/worktree and validate returned IDs with `jq -er`; never treat null/missing values as valid.

```bash
created="$(herdr workspace create --cwd "$working_directory" --label "$task_id" --no-focus)"
workspace_id="$(printf '%s' "$created" | jq -er '.result.workspace.workspace_id | strings | select(length > 0)')"
pane_id="$(printf '%s' "$created" | jq -er '.result.root_pane.pane_id | strings | select(length > 0)')"
herdr agent start "$agy_agent" --kind agy --pane "$pane_id"
```

Herdr workspace is runtime isolation, not Git isolation.

## Phase A — IMPLEMENT

The first worker order explicitly contains:

```text
mode = IMPLEMENT
IMPLEMENT ONLY.
Do not execute the formal test plan, test suites, builds used as quality gates,
linters used as acceptance gates, integration/E2E checks, or other project verification gates.
Do not declare task completion.
```

AGY may inspect source/config/docs and use ordinary edit/navigation/static-inspection tooling. If a test-like command is truly necessary to diagnose an unknown implementation fact, AGY must report that need rather than silently turning implementation into the formal test phase.

Implementation report:

```text
task_id / round / contract_revision
changed behavior + files
implementation decisions
known risks / unresolved items
formal_tests_run = none   # or explicitly report any diagnostic exception
```

After AGY stops writing, Astra performs code-only review.

## Code-review rework

For `CODE_REVIEW_REWORK`, reuse the worker when safe. Send only Contract reference plus bounded findings. Keep `mode = IMPLEMENT_REWORK` and continue to prohibit formal test execution.

Before each prompt, establish that the worker is not still executing the previous round. Tag every order with `task_id` + `round`. Track:

```text
NOT_SENT → SENT → SETTLED
        ↘ SEND_UNKNOWN
```

A timeout or ambiguous send is investigated with `herdr agent read`; never automatically resend.

## Phase B — TEST

Only after Astra records `CODE_REVIEW_PASS` and freezes a Test Plan may AGY enter:

```text
mode = TEST
```

AGY executes the frozen checks exactly as defined, captures command/method, cwd, exit code, measured values, result and evidence reference, and does not weaken acceptance criteria.

If tests expose a code defect, AGY may diagnose/fix code within the frozen Contract. Any production/task code write immediately ends the current test-validity path: report `CODE_CHANGED_DURING_TEST`, stop claiming completion, and return control for Astra code review before testing can be considered final.

## Wait / blocked safety

Use bounded waits:

```bash
herdr agent prompt "$agy_agent" "$worker_order" \
  --wait --until idle --until done --until blocked --timeout "$timeout_ms"
```

Herdr idle/done can match lifecycle settlement and is never proof that the requested round, code review, or tests passed. Correlate task/round markers, worker output and Git/evidence state.

On blocked state, read first. Environment/auth/dependency failures remain `BLOCKED`; do not edit business code or acceptance metrics merely to bypass them.

## Recovery

If exact Herdr/native identity is unavailable:

- never guess another conversation;
- read Run State and Git state;
- confirm the previous writer cannot still write;
- only then start a replacement Herdr-managed AGY;
- pass the current Contract, phase, project rules, code state, open review findings or frozen Test Plan as appropriate.

Never replay a command with uncertain side effects just because its response was lost.

Close only task-owned Herdr resources after the worker is confirmed stopped.

`Herdr done/idle != code review PASS != test metrics PASS`.
