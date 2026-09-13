---
name: agy-supervised-development
description: Astra defines/reviews; Herdr-managed AGY implements and runs frozen checks; local evidence decides completion.
version: 4.1.0-alpha.3
---

# AGY Supervised Development

Read `../../SKILL.md`; it is the canonical router.

```text
Astra: Contract
→ AGY/Herdr: Implement
→ Astra: Code review only
→ Astra: Freeze machine Test Plan
→ AGY/Herdr: run frozen checks
→ validate-run-state: Complete or reject
```

Rules:
- Astra owns `WHAT / BOUNDARY / DONE`, code review, and frozen test criteria; AGY owns ordinary `HOW`.
- Contract-preauthorized diagnostics may run during implementation but never count as formal acceptance.
- Astra code review runs no tests and is bound to the current deliverable digest.
- AGY cannot weaken a frozen plan; any deliverable change after review invalidates review/plan/formal evidence.
- Every AGY execution is Herdr-managed; preserve baseline/user changes and dispatch safety.
- No default Luna supervisor, Sol plan review, or second Astra test-review stage.
- Default readiness validates code/workflow logic and wiring only; Python fixture execution is not a release gate.
