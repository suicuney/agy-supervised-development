---
name: agy-supervised-development
description: Pluginized entrypoint for AGY Supervised Development v3.3. Codex owns the plan and acceptance; Herdr is the only AGY runtime; AGY implements bounded work; Git and independent verification prove delivery.
version: 3.3.0-alpha.2
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
3. Before the first Sol High Send, show a concise Chinese plan summary (`目标 / 计划 / 重点风险`). The preview is semantically faithful to the executable plan. Do not ask for confirmation.
4. After displaying the preview and passing packet safety and ego-browser preflight gates (`GPT-5.6 Sol` + `High`), send automatically exactly once.
5. The plugin kernel and entrypoint own interaction and send policy; the paired `sol-high-plan-review` skill supplies packet structure and verdict semantics only and cannot reintroduce a manual confirmation gate or override transport.
6. Send state machine is `NOT_SENT → SENT | UNKNOWN`; `SENT` requires visible same-conversation evidence; `UNKNOWN` is terminal with no retry transition (never automatically resend).
7. Preserve hard stops: credential-like packet findings, `AUTH_REQUIRED`, `USER_CONTROLLING`, `MODEL_MISMATCH`, `USER_DECISION_REQUIRED`, or any genuine blocker.
8. Later `REVISE` rounds continue automatically in the same verified conversation after Codex applies `Adopt / Reject / Modify` unless Sol returns `USER_DECISION_REQUIRED` or another genuine blocker occurs.
9. When Sol review converges, show the concise Chinese final execution plan, do not ask for a second confirmation, record `PLAN FROZEN`, and continue.
10. Run `../../scripts/check-sol-plan-review.sh` before Sol browser work and use `../../resources/sol-plan-review.md` and `../../resources/ego-browser-runbook.md` for the review loop. ego-browser / ego-lite is the sole browser transport. Maximum three rounds.
11. `PLAN FROZEN` is a hard boundary: Sol High never participates in Build, Review, Rework, Verification, Closeout or Acceptance.
12. Every AGY invocation in this workflow must be Herdr-managed. Run `../../scripts/check-herdr.sh` before AGY BUILD.
13. Use `../../resources/agy-execution.md` for workspace creation, returned pane identity, `--kind agy`, prompt/wait/read, blocked interaction and native session restore boundaries.
14. Herdr lifecycle state is runtime evidence only. `done` or `idle` never bypasses repository Review.
15. Rework reuses the same Herdr-managed AGY worker while its exact session remains valid.
16. Use `../../resources/review-gates.md` for Three-Axis Review and `../../resources/runtime-verification.md` together with `../../resources/ego-browser-runbook.md` for browser runtime verification when applicable.
17. Run `../../scripts/test-readiness.sh` when local execution is available before treating the plugin as release-ready.

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
