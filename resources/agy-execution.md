# AGY Execution — Herdr Only

AGY is the writer/test executor and every AGY execution goes through Herdr.

```text
ASTRA Contract/review/test-plan → Herdr → AGY → repository/evidence
```

Herdr owns runtime identity/lifecycle. It never decides code-review PASS, changes Contract scope, or weakens frozen test metrics.

## Preflight and identity

Run `scripts/check-herdr.sh` before worker start. `HERDR_ENVIRONMENT_READY` proves only its explicit local prerequisites, not AGY auth, task execution or acceptance.

Create/reuse a task-owned workspace on the chosen checkout/worktree and validate returned IDs with `jq -er`; null/missing IDs are invalid. Herdr workspace is runtime isolation, not Git isolation.

Before every prompt establish that the prior worker round is not still executing. Tag orders with task/round and track:

```text
NOT_SENT → SENT → SETTLED
        ↘ SEND_UNKNOWN
```

Timeout/ambiguous delivery means read/investigate first. Never automatically resend `SEND_UNKNOWN` and never start a second writer while the old writer may still write.

## Phase A — IMPLEMENT / IMPLEMENT_REWORK

Default order says:

```text
IMPLEMENT ONLY.
Do not execute the formal frozen Test Plan or full acceptance gates.
Do not declare task completion.
```

AGY may run only diagnostics preauthorized by the current Contract, such as a minimal reproduction, targeted unit test, typecheck or compile feedback. Keep it within the authorized scope, record purpose/result in Run State with `formal_acceptance=false`, and never reuse diagnostic green as final Test Plan PASS. A repository rule that mandates TDD/testing during implementation remains binding and must be represented in Contract diagnostics/constraints rather than silently violated.

Implementation/rework report lists changed behavior/files, decisions, known risks, unresolved items, and diagnostics actually run. After a complete bounded repair AGY **stops** and returns control to Astra code review; it does not continue into formal tests.

## Phase B — TEST

TEST entry is allowed only by a successful deterministic transition:

```bash
scripts/validate-run-state.sh transition ... --to TEST ...
```

AGY executes the exact frozen machine-readable Test Plan. Each check attempt gets its own evidence/log, attempt id/number, actual argv/observation, timestamps, measured values and before/after deliverable digests. Preserve all attempts; do not combine a failed attempt's logs with a later pass.

Retry only within frozen `max_attempts`. Environment/auth/dependency failures are `BLOCKED`; do not change code, Contract or thresholds just to get green.

If a formal test exposes a code defect:

1. Persist the failed result/evidence.
2. Confirm the test worker is stopped.
3. Call `validate-run-state invalidate` to mark review/plan stale and enter `TEST_REWORK`.
4. Dispatch AGY for one bounded complete repair within the Contract.
5. AGY stops; return to Astra full deliverable code review.
6. Astra freezes a fresh/current Test Plan; formal testing restarts.

Test source, assertion, fixture, golden/snapshot, config, lockfile and generated-source changes count as deliverable changes exactly like production code. Only predeclared evidence output under the approved evidence root avoids code-review invalidation.

## Blocked/recovery

Persist blockers with `validate-run-state block`, including reason, source phase and resume action. On resume validate current repository/worktree, Contract, plan where applicable and worker identity; phase names alone never skip gates.

If exact Herdr/native identity is lost, do not guess another conversation. Inspect Run State/Git, prove the previous writer cannot still write, then and only then start a replacement Herdr-managed AGY with current phase context.

`Herdr idle/done != code review PASS != formal test completion`.
