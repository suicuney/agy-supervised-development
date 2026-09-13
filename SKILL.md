---
name: agy-supervised-development
description: Astra defines/reviews; Herdr-managed AGY implements and runs frozen checks; a deterministic local gate decides completion.
version: 4.1.0-alpha.3
---

# AGY Supervised Development 4.1

> **Astra plans. AGY builds. Astra reviews code. AGY runs frozen tests. Local evidence decides COMPLETE.**

## Default flow

```text
ASTRA: compact Contract + acceptance scenarios + optional diagnostics
→ AGY via HERDR: IMPLEMENT / IMPLEMENT_REWORK
→ ASTRA: CODE REVIEW ONLY
   ├─ REWORK → AGY fix → ASTRA review
   └─ PASS
→ ASTRA: freeze machine Test Plan
→ validate-run-state TEST-entry gate
→ AGY via HERDR: run-frozen-check
→ local completion gate
   ├─ COMPLETE
   ├─ BLOCKED
   └─ code defect → invalidate → TEST_REWORK → ASTRA review → new plan → retest
```

No default Luna supervisor, Sol plan review, second Astra test-review, or file-level implementation ceremony.

## Hard rules

- Astra freezes `WHAT / BOUNDARY / DONE`; AGY owns ordinary `HOW`.
- Every AGY implementation, repair and formal test execution goes through Herdr.
- `Herdr done/idle` is lifecycle state, never acceptance.
- Implementation may run only Contract-preauthorized minimal diagnostics. Diagnostic evidence always has `formal_acceptance=false` and cannot satisfy final checks.
- Astra code review inspects code/delta only; it does not execute formal checks.
- The frozen Test Plan is JSON source of truth. AGY may not alter required checks, applicability, environment prerequisites, thresholds or max attempts.
- Formal command checks use `scripts/run-frozen-check.sh`; AGY does not hand-author exit codes or measured values.
- `scripts/validate-run-state.sh complete` is the only normal path to `COMPLETE`.
- Contract content, snapshot policy, review, plan, receipts and current deliverable are digest-bound. Same revision + changed Contract text is invalid.
- Business non-applicability may produce `NOT_APPLICABLE`; missing browser/auth/dependency is `BLOCKED`, not N/A.
- Any reviewed deliverable change, including tests/fixtures/goldens/config/lockfiles/generated source, invalidates review/plan/results. Git-private logs/reports are evidence, not deliverable.
- Preserve user staged/unstaged/untracked content; never auto-stash/reset/clean.
- Never guess sessions, duplicate uncertain sends, or start a second writer while the first may still write.

## Progressive disclosure

Load only the current phase resource:

- `resources/development-contract.md`
- `resources/run-state.md`
- `resources/agy-execution.md`
- `resources/code-review.md`
- `resources/testing.md`

Python files implement the local snapshot/runner/completion runtime. Default readiness checks their wiring and workflow logic only; Python fixture execution is not a release gate. Real runtime correctness is established by actual task/smoke evidence, not by static readiness.
