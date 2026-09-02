# Runtime Verification — Browser Capability

Browser runtime verification is an optional **Codex-owned** capability. It does not change the core workflow and Chrome DevTools MCP never becomes part of the AGY writer runtime.

## Applicability

Use it only when the task contains browser-observable behavior, for example:

```text
Web UI / routing / forms
authentication or browser session behavior
frontend ↔ backend integration
browser storage or cookies
Chrome Extension
console/runtime JavaScript errors
browser-observable network failures
browser performance requirements
```

Pure backend, CLI, SQL, batch, library, or JVM-only work is normally `N/A` unless the acceptance path explicitly requires a browser.

Do not ask about Chrome DevTools MCP mechanically for every task.

## Capability Negotiation

When browser runtime is applicable and no effective preference exists, ask the user **before Spec freeze**:

```text
Enable
Disable
Auto-decide
```

Keep the question short. Do not turn it into MCP configuration setup.

Preference order:

```text
current task
> project preference
> global/default preference
```

Semantic modes:

```text
enabled
disabled
auto
unset
```

Persist a project preference only when the user explicitly asks to remember it.

## Ownership

```text
AGY = Primary Writer
Codex = Reviewer / QA / Runtime Verifier / Acceptance Authority
Chrome DevTools MCP = optional Codex verification adapter
```

AGY may receive browser findings through a Rework Contract, but AGY's own browser self-check never replaces Codex Independent Verification.

## Two Hooks

Chrome DevTools MCP has only two workflow hooks:

```text
Complex browser bug
→ DIAGNOSE
→ optional browser evidence

Three-Axis Review PASS
→ CODEX INDEPENDENT VERIFY
→ optional/required browser verification
```

For browser verification, use only the evidence needed by the Spec:

```text
navigate / interact
assert observable behavior
console errors
unexpected network 4xx/5xx or contract failures
persistence/state after reload when relevant
performance evidence only when required
```

A screenshot alone is not functional proof.

## Failure Flow

Browser verification failures are normal `V*` findings:

```text
VERIFYING
→ V* finding
→ REWORK_REQUIRED
→ AGY
→ THREE-AXIS REVIEW AGAIN
→ VERIFY AGAIN
```

Do not skip renewed Review because the browser journey becomes green.

## Provider Unavailable

If Chrome DevTools MCP is unavailable:

```text
record TOOL_UNAVAILABLE
→ use an already-approved equivalent verification seam when one exists
→ never silently weaken a required acceptance criterion
```

If browser verification is required and no equivalent seam can prove it, do not issue `CODE_VERIFIED`.

## Security

Prefer a dedicated test browser/profile. Do not treat browser access as permission for production mutation, and do not expose credentials or sensitive session data in reports.

## Core Rule

For browser-facing work:

```text
Repository Evidence + Runtime Evidence
```

is stronger than either alone.

But:

```text
browser green != REVIEW PASS
browser green != CODE_VERIFIED by itself
browser green != ACCEPTED
```

Only Codex can issue final acceptance.
