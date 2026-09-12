---
name: agy-supervised-development
description: Astra plans and reviews code; AGY implements and executes Astra-defined tests through Herdr.
version: 4.1.0-alpha.1
---

# AGY Supervised Development

Read `../../SKILL.md`; it is the canonical router.

```text
Astra: Plan
→ AGY: Implement only
→ Astra: Code review only
→ Astra: Freeze test plan + metrics
→ AGY: Test
→ Metrics pass: Complete
```

Rules:
- Astra freezes `WHAT / BOUNDARY / DONE`; AGY owns normal `HOW`.
- Implementation/rework AGY runs do not execute the formal test plan or project acceptance gates.
- Astra code review does not run tests.
- After code review PASS, Astra freezes test checks and measurable acceptance criteria.
- AGY executes tests and cannot weaken the frozen metrics.
- If test-stage code changes, return to Astra code review before completion.
- Every AGY execution is Herdr-managed.
- Preserve baseline/user changes and load supporting resources only for the current phase.
