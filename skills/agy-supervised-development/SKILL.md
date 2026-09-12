---
name: agy-supervised-development
description: Contract-first supervised coding with Astra decisions, Luna evidence supervision, and AGY through Herdr.
version: 4.0.0-alpha.4
---

# AGY Supervised Development

Read `../../SKILL.md`; it is the canonical router.

```text
Astra: Contract → Luna: Supervise → AGY/Herdr: Build → Luna: Verify
```

Rules:
- Astra freezes compact `WHAT / BOUNDARY / DONE`; AGY owns normal `HOW`.
- Spawn an independent supervisor only through real host capability; requested and verified model identity are separate facts.
- Luna uses Contract + repository rules + Run State + Git/test evidence, and cannot silently rewrite the Contract.
- Every AGY execution is Herdr-managed; Herdr lifecycle state is not acceptance.
- Preserve baseline user changes; use worktrees only when isolation is actually needed.
- Verification covers committed, staged, unstaged and untracked task changes and is bound to current code state.
- Load supporting resources only when the current stage needs them.
- Legacy Sol/browser review is not part of the default 4.0 path.
