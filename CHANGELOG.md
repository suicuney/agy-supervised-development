# Changelog

All notable changes to this Skill are documented here.

## [4.1.0-alpha.2] - 2026-09-13

### Reliability

- Replaced the principle-only completion formula with structured Development Contract, Test Plan, Test Result and Run State schemas plus `scripts/validate-run-state.sh` semantic gates for TEST entry, invalidation, BLOCKED persistence and COMPLETE.
- Added Contract-level observable acceptance scenarios/counterexamples and optional bounded diagnostics. Diagnostic results are explicitly non-formal evidence and cannot satisfy final acceptance.
- Added structured Test Plan checks with command/observation types, frozen objective applicability, accepted exit codes, evidence types, timeout/max attempts and whitelist metrics (`eq/ge/le`).
- Added independent per-attempt Test Result evidence with actual execution data, measured values, evidence hashes and before/after deliverable digests. Latest bounded attempt is authoritative; evidence cannot be spliced across attempts.
- Completion now re-reads disk/current Git state and rejects stale Contract/review/plan/digest, incomplete/duplicate/unknown checks, bad evidence/log hashes, invalid N/A, failed metrics, open findings, active writers or unsettled/unknown dispatch.
- Run State v2 uses explicit BLOCKED recovery metadata plus cooperating-process file lock, optimistic `state_version`, fsync and atomic replace; it does not claim OS-level isolation.

### Baseline / identity

- Reworked `snapshot-code-state.sh` around a fail-closed Python collector that normalizes Git collection to repository root, publishes atomically outside the worktree/Git-private storage, and fails on collection/stability errors instead of swallowing them.
- Split `deliverable_digest` from Git `ownership_digest`, so staging unchanged content does not cause code-review churn while HEAD/index/status changes remain visible to recovery.
- Added stable path encoding/order, binary/executable identity, symlink target identity without following links, committed/index/worktree binary diffs, recoverable local archives for untracked original bytes, and explicit sensitive/ignored/unsupported/submodule policy.
- Deliverable identity includes production and test sources/assertions/fixtures/goldens, config, lockfiles and generated sources; only predeclared evidence output outside the deliverable avoids review invalidation.

### Validation

- Replaced the broad removed-role grep with a targeted active-role validator plus positive migration-note and negative active-Luna regression fixtures that report file/line/reason.
- Declared `jsonschema` as a required static-validation dependency rather than silently skipping schema checks.
- Added temporary-repository behavior tests for baseline preservation, special paths, symlink/binary/mode/rename changes, staging-only ownership changes, fail-closed snapshots, structured completion/rejection paths, applicability, attempt isolation, stale evidence, BLOCKED state and concurrency/version protection.
- Historical Luna/4.0 wording remains allowed only as migration/history; active execution cannot depend on removed roles.

## [4.1.0-alpha.1] - 2026-09-13

### Architecture

- Replaced the 4.0 Astra → Luna → AGY supervision topology with a simpler staged workflow: **Astra plans → AGY implements → Astra reviews code → Astra freezes tests/metrics → AGY tests → metrics decide completion**.
- Removed Luna/model-handoff from the default execution path. `resources/codex-supervisor-handoff.md`, `resources/supervisor.md`, and the generic `resources/verification.md` are no longer active resources.
- Kept the compact Development Contract and AGY ownership of ordinary implementation `HOW`.
- Kept Herdr as the only AGY runtime and retained Git baseline/recovery protections.

### Phase separation

- AGY implementation and code-review rework are explicitly `IMPLEMENT ONLY`: formal test plans and project acceptance gates are deferred.
- Astra code review is explicitly code-only. It inspects the complete task delta and applicable repository rules but does not execute tests/builds/quality gates.
- `CODE_REVIEW_PASS` is bound to the reviewed code-state digest and becomes stale after any later production/task-code change.
- Only after code review passes does Astra freeze a Test Plan with required checks and measurable acceptance metrics.
- AGY executes the frozen test plan and cannot weaken thresholds, remove required checks, or redefine PASS.
- When all required checks/metrics pass on the current code state, the task completes without a second Astra test-review pass.
- If AGY changes code while fixing a test failure, the workflow returns to Astra code review and then refreshes the test plan.

### Runtime state and evidence

- Simplified Run State around `IMPLEMENT | CODE_REVIEW | IMPLEMENT_REWORK | TEST_PLAN | TEST | BLOCKED | COMPLETE`.
- Removed supervisor/model identity fields from Run State; retained Herdr identity, baseline, code-review digest, frozen test-plan binding, per-check test results, and dispatch/recovery safety.
- Preserved fail-closed Herdr preflight, duplicate-dispatch protection, bounded waits, and no automatic resend after uncertain delivery.

### Tests and evals

- Added `resources/code-review.md` and `resources/testing.md`.
- Reworked the AGY worker order so implementation/rework does not silently run formal tests.
- Replaced 4.0 Luna-supervisor semantic scenarios with 4.1 scenarios covering phase separation, code-review rework, frozen metrics, no second Astra test review, stale review/test evidence after code changes, Herdr-only AGY execution, recovery, and current-digest completion.
- Real end-to-end flow verification remains separate from static/mock validation.

## [4.0.0-alpha.4] - 2026-09-12

- Made the prior Astra/Luna/AGY design executable with Codex Multi-Agent supervisor handoff, Git-private Run State, baseline/digest evidence, fail-closed Herdr preflight, bounded rework/recovery, and 4.0 evals.
- This topology is superseded by 4.1 and remains available through Git history.

## [4.0.0-alpha.3] - 2026-09-12

- Added observable routing semantics: runtime evidence is required for role/model handoff claims; unavailable exact model identity is reported honestly.

## [4.0.0-alpha.2] - 2026-09-12

- Simplified the 4.0 kernel around a compact Development Contract, evidence supervision, AGY implementation autonomy, progressive disclosure, and exceptional architect escalation.

## [4.0.0-alpha.1] - 2026-09-12

- Introduced the 4.0 model-tiered direction with architect Contract decisions, routine supervision, AGY-owned implementation planning, Herdr-only execution, and Git-backed evidence.

## Historical 3.x and earlier

See repository history before 4.0 for the complete earlier changelog.
