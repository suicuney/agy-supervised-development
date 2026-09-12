---
name: agy-supervised-development
description: Delegate repository implementation to AGY through Herdr while Codex preserves task boundaries, supervision, escalation, and delivery verification.
version: 4.0.0-alpha.1
---

# AGY Supervised Development 4.0

This is the plugin entrypoint. Read `../../SKILL.md` as the canonical workflow router.

```text
USER INTENT
→ ASTRA ARCHITECT
→ DEVELOPMENT CONTRACT
→ CONTRACT FROZEN
→ LUNA SUPERVISOR
→ AGY BUILD                # Herdr only
→ AGY SELF-REVIEW
→ LUNA REVIEW / VERIFY
→ ACCEPTED
```

> Astra frames. Luna supervises. AGY builds. Git tells the truth.

## Entry Rules

1. Use the strongest reasoning role for contract-level analysis and a lower-cost reliable role for routine supervision.
2. The architect defines `WHAT / WHY / BOUNDARY / DONE`; AGY decides normal implementation `HOW`.
3. Freeze a compact Development Contract before AGY writes.
4. Do not create a detailed supervisor-owned implementation itinerary by default.
5. Luna supervises through evidence: frozen contract, Git diff/status, AGY report, and targeted test/runtime output.
6. Luna may request bounded rework but may not silently redesign the frozen contract.
7. Escalate back to Astra only for architecture conflict, material requirement ambiguity, scope explosion, repeated core failure, or a one-way decision.
8. Every AGY execution must be Herdr-managed. Run `../../scripts/check-herdr.sh` before AGY build.
9. Use `../../resources/agy-execution.md` for workspace identity, `--kind agy`, prompt/wait/read, blocked interaction, and session continuity.
10. AGY self-review never substitutes for Luna independent review and verification.
11. Prefer diff-first targeted verification; broaden only when evidence or risk requires it.
12. Legacy Sol High plan review is not part of the default path. Use it only as an explicitly justified guarded escalation capability.
13. Run `../../scripts/test-readiness.sh` when local execution is available before treating the plugin as release-ready.

## Progressive Disclosure

Read only what the current stage needs:

```text
../../resources/architect.md
../../resources/development-contract.md
../../resources/supervisor.md
../../resources/escalation.md
../../resources/agy-execution.md
../../resources/verification.md
```

Do not preload all workflow resources into context.

## Acceptance Boundary

```text
CONTRACT FROZEN != implementation complete
Herdr done != REVIEW PASS
AGY SUCCESS != REVIEW PASS
AGY SELF-REVIEW != INDEPENDENT REVIEW
REVIEW PASS != VERIFIED
```

Acceptance requires contract fidelity, independent review, relevant verification, an explainable final diff, and no unresolved escalation.
