---
name: agy-supervised-development
description: Pluginized entrypoint for AGY Supervised Development v3.2. Codex shapes/specs/slices work, delegates bounded implementation to official AGY CLI, independently reviews and verifies repository/runtime evidence, then closes out knowledge before acceptance.
version: 3.2.0-alpha.2
---

# AGY Supervised Development 3.2

This is the Codex Plugin entrypoint.

Read `../../SKILL.md` as the current workflow kernel. Keep the workflow simple:

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
→ BUILD
→ THREE-AXIS REVIEW
→ VERIFY
→ CLOSEOUT
→ ACCEPTED
```

> Codex shapes and proves. AGY builds. Git tells the truth.

## v3.2 Runtime Rules

1. Prefer `../../scripts/agy-run.sh` as the thin AGY invocation adapter when available.
2. AGY remains the primary writer. Codex remains reviewer, verifier, and final acceptance authority.
3. Use `../../resources/review-gates.md` for Three-Axis Review, finding severity, and convergence.
4. Use `../../resources/runtime-verification.md` only when browser-runtime behavior is applicable. If no effective preference exists, ask `Enable / Disable / Auto-decide` before Spec freeze.
5. Chrome DevTools MCP is an optional **Codex-owned** diagnosis/verification adapter, never an AGY writer dependency.
6. Use `../../resources/agy-consult.md` only for optional read-only second opinions.
7. Use tty7 only when interaction is genuinely required: login, permissions, manual approval, resume picker, or TUI-only behavior.
8. Run `../../scripts/test-readiness.sh` when local execution is available before treating the plugin as release-ready.

## Runtime Boundary

```text
Codex
→ Execution Unit
→ agy-run.sh
→ official AGY CLI
→ Repository
→ Codex Three-Axis Review
→ Codex Independent Verification
→ Knowledge Closeout
```

Optional browser evidence:

```text
Codex
→ Chrome DevTools MCP
→ diagnosis / runtime verification
```

## Acceptance Boundary

```text
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
NO_BLOCKING_FINDINGS != ACCEPTED
browser green != ACCEPTED
CODE_VERIFIED != ACCEPTED
```

Only Codex may mark `ACCEPTED` after Review, Verification, Closeout, baseline preservation, and side-effect checks pass.
