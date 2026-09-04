---
name: agy-supervised-development
description: Pluginized entrypoint for AGY Supervised Development v3.2. Codex owns the executable plan, converges it with optional/default Sol High review before freeze, delegates bounded implementation to AGY, then independently reviews and verifies repository/runtime evidence.
version: 3.2.0-alpha.3
---

# AGY Supervised Development 3.2

This is the Codex Plugin entrypoint.

Read `../../SKILL.md` as the current workflow kernel.

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
→ SOL HIGH PLAN REVIEW
→ PLAN FROZEN
→ BUILD
→ THREE-AXIS REVIEW
→ VERIFY
→ CLOSEOUT
→ ACCEPTED
```

> Codex shapes and proves. AGY builds. Git tells the truth.

## Rules

1. Codex is the executable-plan owner and final acceptance authority.
2. Plan review is enabled by default unless the user explicitly opts out.
3. Run `../../scripts/check-sol-plan-review.sh` before browser work; use the opt-in full-checkout helper when the dependency is missing, and treat incomplete installs as unavailable.
4. Use `../../resources/sol-plan-review.md` for the Sol High review loop. Maximum three Sol review rounds; stop early on convergence.
5. Sol High uses the installed `sol-high-plan-review` Skill and the approved Chrome browser surface to reach ChatGPT Web with GPT-5.6 Sol + High. Preserve unrelated user tabs and verify model state visibly.
6. `PLAN FROZEN` is a hard boundary: never call Sol High during AGY Build, Three-Axis Review, Rework, Verification, Closeout, or Acceptance.
7. Prefer `../../scripts/agy-run.sh` as the thin AGY invocation adapter.
8. Use `../../resources/review-gates.md` for Three-Axis Review, finding severity, and convergence.
9. Use `../../resources/runtime-verification.md` only when browser-runtime behavior is applicable. Browser runtime verification remains Codex-owned.
10. Use tty7 only when AGY interaction is genuinely required, and follow the minimal fallback in `../../resources/tty7-supervision.md`.
11. Run `../../scripts/test-readiness.sh` when local execution is available before treating the plugin as release-ready.

## Runtime Boundary

```text
Codex frozen plan
→ Execution Unit
→ agy-run.sh
→ official AGY CLI
→ Repository
→ Codex Three-Axis Review
→ Codex Independent Verification
→ Knowledge Closeout
```

## Acceptance Boundary

```text
Sol High PASS != PLAN ownership transfer
PLAN FROZEN != implementation complete
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
browser green != ACCEPTED
CODE_VERIFIED != ACCEPTED
```

Only Codex may mark `ACCEPTED`.
