---
name: agy-supervised-development
description: Astra plans/reviews/freezes tests; Herdr-managed AGY implements and tests; deterministic validation completes.
version: 4.1.0-alpha.2
---

# AGY Supervised Development

Read `../../SKILL.md`; it is the canonical router.

```text
Astra: Contract + acceptance scenarios + optional diagnostics
→ AGY: Implement / bounded diagnostics
→ Astra: Code review only
→ Astra: Freeze machine Test Plan + metrics
→ AGY: Formal test
→ deterministic completion gate
```

Rules:
- Astra owns `WHAT / BOUNDARY / DONE`, code review, and frozen formal test criteria; AGY owns normal `HOW`.
- Contract-preauthorized diagnostics may run during implementation but never count as formal acceptance.
- Astra code review runs no tests and is bound to the current deliverable digest.
- AGY cannot weaken a frozen plan; any deliverable change after review invalidates review/plan/formal evidence.
- `bash scripts/validate-run-state.sh` controls TEST entry and COMPLETE; AGY prose cannot complete the task.
- Every AGY execution is Herdr-managed; preserve baseline/user changes and dispatch safety.
- No default Luna supervisor, Sol plan review, or second Astra test-review stage.
