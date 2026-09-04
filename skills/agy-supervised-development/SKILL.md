---
name: agy-supervised-development
description: Pluginized entrypoint for AGY Supervised Development v3.3. Codex owns the plan and acceptance; Herdr is the only AGY runtime; AGY implements bounded work; Git and independent verification prove delivery.
version: 3.3.0-alpha.1
---

# AGY Supervised Development 3.3

This is the Codex Plugin entrypoint. Read `../../SKILL.md` as the canonical workflow kernel.

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
→ SOL HIGH PLAN REVIEW
→ PLAN FROZEN
→ BASELINE
→ AGY BUILD          # Herdr only
→ THREE-AXIS REVIEW
→ VERIFY
→ CLOSEOUT
→ ACCEPTED
```

> Codex governs. Herdr runs. AGY builds. Git tells the truth.

## Rules

1. Codex is the executable-plan owner and final acceptance authority.
2. Plan review is enabled by default unless the user explicitly opts out.
3. Run `../../scripts/check-sol-plan-review.sh` before Sol browser work and use `../../resources/sol-plan-review.md` for the review loop. Maximum three rounds.
4. `PLAN FROZEN` is a hard boundary: Sol High never participates in Build, Review, Rework, Verification, Closeout or Acceptance.
5. Every AGY invocation in this workflow must be Herdr-managed. Run `../../scripts/check-herdr.sh` before AGY BUILD.
6. Use `../../resources/agy-execution.md` for workspace creation, returned pane identity, `--kind agy`, prompt/wait/read, blocked interaction and native session restore boundaries.
7. Herdr lifecycle state is runtime evidence only. `done` or `idle` never bypasses repository Review.
8. Rework reuses the same Herdr-managed AGY worker while its exact session remains valid.
9. Use `../../resources/review-gates.md` for Three-Axis Review and `../../resources/runtime-verification.md` for browser runtime verification when applicable.
10. Run `../../scripts/test-readiness.sh` when local execution is available before treating the plugin as release-ready.

## Runtime Boundary

```text
Codex frozen plan
→ Execution Unit
→ Herdr workspace / Agent API
→ Antigravity CLI (AGY)
→ Repository
→ Codex Three-Axis Review
→ Codex Independent Verification
→ Knowledge Closeout
```

## Acceptance Boundary

```text
Sol High PASS != PLAN ownership transfer
PLAN FROZEN != implementation complete
Herdr done != REVIEW PASS
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
browser green != ACCEPTED
CODE_VERIFIED != ACCEPTED
```

Only Codex may mark `ACCEPTED`.
