---
name: agy-supervised-development
description: Pluginized entrypoint for AGY Supervised Development v3.2. Use when Codex should shape/spec/slice work, delegate bounded implementation to official AGY CLI, independently review and verify repository evidence and applicable browser-runtime evidence, and close out knowledge before acceptance.
version: 3.2.0-alpha.2
---

# AGY Supervised Development 3.2 — Pluginized Runtime

This is the Codex Plugin entrypoint for the repository's supervised-development workflow.

## Canonical workflow

Read `../../SKILL.md` as the workflow kernel, then apply the v3.2 additions below. The root kernel remains the canonical workflow definition; v3.2 adds plugin/runtime capability layers without changing the AGY-writer / Codex-reviewer governance boundary.

> Codex shapes and proves. AGY builds. Git tells the truth.

## v3.2 additions

1. Prefer `../../scripts/agy-run.sh` as the thin official-AGY invocation adapter when it is available and validated.
2. Keep runtime and governance separate. The wrapper standardizes invocation only; it is not a custom harness, run store, session database, reviewer, or acceptance authority.
3. Use `../../resources/review-convergence.md` to classify review findings as BLOCKING, NON_BLOCKING, or BACKLOG. `NO_BLOCKING_FINDINGS` is only a convergence signal; it never means `ACCEPTED`.
4. Use `../../resources/agy-consult.md` for optional read-only second opinions. AGY consultation is advisory evidence and cannot replace Codex Three-Axis Review, independent verification, or acceptance.
5. Use `../../resources/runtime-verification.md` for browser-runtime applicability, user capability negotiation, diagnosis hooks, and Codex-owned runtime verification. Chrome DevTools MCP is an optional Runtime Verification Adapter, never the AGY writer or acceptance authority.
6. Use `../../templates/browser-verification.md` when Browser Runtime Verification is selected for the task.
7. Before treating this plugin as release-ready, run `../../scripts/test-readiness.sh` when local execution is available.

## Runtime Capability Negotiation

After repository INTAKE/SIZE and before SPEC freeze, determine whether browser-runtime evidence is applicable.

Typical applicable work includes:

```text
Web UI / browser interaction
authentication/session flows
forms / routing / browser storage
frontend ↔ backend integration
Chrome Extension behavior
browser Console / Network failures
browser performance requirements
```

If Browser Runtime is not applicable, continue without asking about Chrome DevTools MCP.

If Browser Runtime is applicable and there is no effective current-task/project preference, ask the user before SPEC freeze:

```text
Enable
Disable
Auto-decide
```

Keep the user-facing question simple. Explain that enabling allows Codex to use a real Chrome runtime for relevant diagnosis and/or final verification. Recommend enabling when it materially strengthens evidence.

Preference precedence:

```text
current-task override
> project preference
> global/default preference
```

Do not persist a new project preference unless the user explicitly asks to remember the choice.

Record the resolved decision in the Spec when applicable:

```text
Runtime Verification
- Applicability
- Provider
- Mode
- Diagnosis permission
- Final Verification requirement
- Critical Journey / Verification Seam
- Expected runtime evidence
```

## Browser Runtime Ownership

Default ownership is fixed:

```text
AGY = Primary Writer
Codex = Reviewer / QA / Runtime Verifier / Final Acceptance
Chrome DevTools MCP = Codex-owned optional Runtime Verification Adapter
```

There are two valid hooks:

```text
Complex Bug DIAGNOSE
  └─ Runtime Diagnosis Adapter when allowed

CODEX INDEPENDENT VERIFY
  └─ Browser Runtime Verification when applicable
```

AGY may receive browser findings through a normal Rework Contract, but AGY self-testing never replaces Codex Independent Verification.

## Verification layering

When relevant, Codex may reason about verification as:

```text
V1 Static       lint / typecheck / compile / build
V2 Automated    unit / integration / contract / existing E2E
V3 Runtime      real browser journey via selected adapter
V4 Regression   original repro / critical sibling flows
```

Chrome DevTools MCP primarily implements V3 and may assist DIAGNOSE for complex browser-observable bugs.

A valid browser verification should exercise the applicable subset of:

```text
Navigate
Interact
Assert observable behavior
Inspect Console
Inspect unexpected Network failures / contract evidence
Verify persisted state after reload when relevant
Performance evidence only when required
```

A screenshot alone is not functional proof.

Runtime verification failures become `V*` findings and follow the existing loop:

```text
VERIFYING
→ REWORK_REQUIRED
→ AGY
→ THREE-AXIS REVIEW AGAIN
→ VERIFY AGAIN
```

If the selected browser provider is unavailable, record `TOOL_UNAVAILABLE` honestly and use an already-approved equivalent verification seam when possible. Do not silently weaken a required Browser Runtime acceptance criterion; if no equivalent proof exists, do not issue `CODE_VERIFIED`.

## Runtime boundary

Default writer path:

```text
Codex → Execution Unit → agy-run.sh → official AGY CLI / stream-json → Repository → Codex Review
```

Optional verification path:

```text
Codex → Runtime Verification Adapter → Chrome DevTools MCP → Browser evidence
```

Interactive writer fallback remains:

```text
Codex → tty7 → AGY TUI
```

Only use tty7 when interaction is genuinely required, such as login, permissions, manual approval, resume pickers, or TUI-only behavior.

## Non-negotiable acceptance boundary

```text
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
BROWSER RUNTIME GREEN != CODE_VERIFIED by itself
NO_BLOCKING_FINDINGS != ACCEPTED
CODE_VERIFIED != ACCEPTED
```

Only Codex may mark the task `ACCEPTED` after Three-Axis Review, independent verification (including required runtime seams), knowledge closeout, baseline preservation, and side-effect checks all pass.
