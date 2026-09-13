# AGY Execution — Herdr Only

Every AGY implementation, repair and formal check runs through Herdr. `done/idle` is runtime state, not acceptance.

Implementation may use only Contract-preauthorized minimal diagnostics; each diagnostic is recorded separately with `formal_acceptance=false`. Formal checks are deferred until Astra review PASS and frozen Test Plan.

Formal command checks are invoked by AGY with `scripts/run-frozen-check.sh`. The runner, not AGY prose, captures argv, cwd, timestamps, timeout, exit status, before/after snapshot, stdout/stderr, structured reports and immutable per-attempt receipt.

Before a new dispatch, old writer must be STOPPED and dispatch must not be `SENT`/`SEND_UNKNOWN`. Unknown send is investigated, never blindly resent. Test defect repair uses `invalidate` → `TEST_REWORK`; AGY completes the repair then stops for Astra re-review.
