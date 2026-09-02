---
name: agy-supervised-development
description: Pluginized entrypoint for AGY Supervised Development v3.2. Use when Codex should shape/spec/slice work, delegate bounded implementation to official AGY CLI, independently review and verify repository evidence, and close out knowledge before acceptance.
version: 3.2.0-alpha.1
---

# AGY Supervised Development 3.2 — Pluginized Runtime

This is the Codex Plugin entrypoint for the repository's supervised-development workflow.

## Canonical workflow

Read `../../SKILL.md` as the workflow kernel, then apply the v3.2 additions below. The root kernel remains the canonical definition of SIZE → SHAPE → SPEC → SLICE → BUILD → THREE-AXIS REVIEW → VERIFY → CLOSEOUT → ACCEPTED.

> Codex shapes and proves. AGY builds. Git tells the truth.

## v3.2 additions

1. Prefer `../../scripts/agy-run.sh` as the thin official-AGY invocation adapter when it is available and validated.
2. Keep runtime and governance separate. The wrapper standardizes invocation only; it is not a custom harness, run store, session database, reviewer, or acceptance authority.
3. Use `../../resources/review-convergence.md` to classify review findings as BLOCKING, NON_BLOCKING, or BACKLOG. `NO_BLOCKING_FINDINGS` is only a convergence signal; it never means `ACCEPTED`.
4. Use `../../resources/agy-consult.md` for optional read-only second opinions. AGY consultation is advisory evidence and cannot replace Codex Three-Axis Review, independent verification, or acceptance.
5. Before treating this plugin as release-ready, run `../../scripts/test-readiness.sh` when local execution is available.

## Runtime boundary

Default writer path:

```text
Codex → Execution Unit → agy-run.sh → official AGY CLI / stream-json → Repository → Codex Review
```

Interactive fallback remains:

```text
Codex → tty7 → AGY TUI
```

Only use tty7 when interaction is genuinely required, such as login, permissions, manual approval, resume pickers, or TUI-only behavior.

## Non-negotiable acceptance boundary

```text
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
NO_BLOCKING_FINDINGS != ACCEPTED
CODE_VERIFIED != ACCEPTED
```

Only Codex may mark the task `ACCEPTED` after Three-Axis Review, independent verification, knowledge closeout, baseline preservation, and side-effect checks all pass.
