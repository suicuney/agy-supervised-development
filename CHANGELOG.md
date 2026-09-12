# Changelog

All notable changes to this Skill are documented here.

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
- Preserved full task-delta capture across committed, staged, unstaged, untracked, deletion/rename, and relevant binary changes.
- Preserved fail-closed Herdr preflight, duplicate-dispatch protection, bounded waits, and no automatic resend after uncertain delivery.

### Tests and evals

- Added `resources/code-review.md` and `resources/testing.md`.
- Reworked the AGY worker order so implementation/rework does not silently run formal tests.
- Replaced 4.0 Luna-supervisor semantic scenarios with 4.1 scenarios covering phase separation, code-review rework, frozen metrics, no second Astra test review, stale review/test evidence after code changes, Herdr-only AGY execution, recovery, and current-digest completion.
- Updated deterministic/static validators to reject active Luna/supervisor references and verify the new stage boundaries.
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
