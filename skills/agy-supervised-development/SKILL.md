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
3. Use `../../resources/sol-plan-review.md` for the Sol High review loop. Maximum three Sol review rounds; stop early on convergence.
4. Sol High uses the installed `sol-high-plan-review` Skill and Chrome DevTools MCP to reach ChatGPT Web with GPT-5.6 Sol + High.
5. `PLAN FROZEN` is a hard boundary: never call Sol High during AGY Build, Three-Axis Review, Rework, Verification, Closeout, or Acceptance.
6. Prefer `../../scripts/agy-run.sh` as the thin AGY invocation adapter.
7. Use `../../resources/review-gates.md` for Three-Axis Review, finding severity, and convergence.
8. Use `../../resources/runtime-verification.md` only when browser-runtime behavior is applicable. Chrome DevTools MCP remains Codex-owned verification tooling.
9. Use tty7 only when AGY interaction is genuinely required.
10. Run `../../scripts/test-readiness.sh` when local execution is available before treating the plugin as release-ready.

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
