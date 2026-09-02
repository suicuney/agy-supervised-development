# Runtime Verification — Capability Negotiation and Browser Adapter

AGY Supervised Development keeps workflow governance separate from runtime tools. Browser automation is therefore an optional **Codex-owned verification capability**, not an AGY writer capability.

## 1. Purpose

Use this resource when a task may require evidence from a real browser runtime: UI behavior, browser-side integration, authentication flows, forms, routing, storage, Chrome extensions, frontend/backend interaction, console errors, network failures, or browser performance.

Primary provider in v3.2 Alpha 2:

```text
Chrome DevTools MCP
```

It may support two bounded purposes:

```text
Runtime Diagnosis      # why is the browser-observable behavior failing?
Runtime Verification   # is the delivered behavior actually correct in a real browser?
```

It does not become the implementation writer and it does not decide ACCEPTED.

## 2. Capability Detection

After INTAKE/SIZE and before SPEC freeze, Codex determines applicability.

Typical signals include:

```text
Web UI / SPA / SSR
browser interaction or routing
authentication/session behavior
forms or upload/download flows
frontend ↔ backend integration
browser storage/cookies
Chrome Extension / manifest.json
console/runtime JavaScript errors
network/API behavior observable from the browser
browser performance requirements
```

Pure backend, CLI, SQL, batch, library, or JVM-only tasks normally mark Browser Runtime as `N/A` unless the stated acceptance path explicitly requires a browser.

Do not ask about Chrome DevTools MCP for every task mechanically.

## 3. Runtime Capability Negotiation

If Browser Runtime is applicable and no effective preference already exists, ask the user **before SPEC freeze** whether Chrome DevTools MCP may participate.

User-facing choices should be simple:

```text
Enable
Disable
Auto-decide
```

Recommended wording:

> This task has browser-runtime behavior. Enable Chrome DevTools MCP for diagnosis and/or final runtime verification? I recommend enabling it for this task.

Do not turn the question into a long MCP configuration interview.

## 4. Effective Preference

Resolve preferences in this order:

```text
current-task override
> project preference
> global/default preference
```

Supported semantic modes:

```text
enabled      # may use when applicable
disabled     # do not use this provider
auto         # Codex decides based on verification value and cost
unset        # ask when applicable
```

The workflow may also record separate permissions:

```yaml
runtime_verification:
  provider: chrome-devtools-mcp
  mode: enabled
  diagnosis: allowed
  final_verification: required_when_applicable
```

This is a semantic contract, not a required physical config-file format.

If a repository already has a project preference mechanism, reuse it instead of inventing `.agy/config.yaml` unprompted. Persist a new project preference only when the user explicitly asks to remember the choice.

## 5. SPEC Integration

When applicable, record the resolved runtime decision in the Spec:

```text
Runtime Verification
- Applicability: YES / NO / N/A
- Provider: Chrome DevTools MCP / fallback / none
- Mode: enabled / disabled / auto
- Diagnosis: allowed / disallowed
- Final Verification: required / optional / N/A
- Primary Journey / Verification Seam
- Expected runtime evidence
```

The decision must be frozen before implementation when it materially changes the Verification Seam, acceptance evidence, or bug diagnosis method.

## 6. Ownership Boundary

The default ownership model is:

```text
AGY = Primary Writer
Codex = Reviewer / QA / Runtime Verifier / Acceptance Authority
Chrome DevTools MCP = Codex-owned Runtime Verification Adapter
```

Do not let AGY's own browser self-check replace Codex Independent Verification.

AGY may receive runtime findings through a Rework Contract, but the authoritative runtime verdict remains Codex-owned.

## 7. Diagnosis Hook

For complex browser-observable bugs, Chrome DevTools MCP may participate during DIAGNOSE when `diagnosis: allowed`.

Useful evidence includes:

```text
reproducible user journey
console errors / stack evidence
network request status and response evidence
runtime state or browser-visible side effects
performance trace when performance is the symptom
```

Use it to tighten the feedback loop, not to replace hypothesis discipline.

No first code guess becomes root cause merely because a browser tool was available.

## 8. Independent Runtime Verification Hook

Only after Three-Axis Review PASS should Codex perform final runtime verification, unless runtime evidence is required earlier for diagnosis.

Recommended verification layers:

```text
V1 Static       lint / typecheck / compile / build
V2 Automated    unit / integration / contract / existing E2E
V3 Runtime      real browser journey when applicable
V4 Regression   original repro + critical sibling flow as required
```

Chrome DevTools MCP primarily implements V3.

A browser verification should normally combine the relevant subset of:

```text
Navigate
Interact
Assert observable behavior
Inspect Console
Inspect unexpected Network 4xx/5xx or contract failures
Verify persistence/state after reload when relevant
Performance evidence only when required
Screenshot only when it is meaningful evidence
```

A screenshot alone is not sufficient proof of functional correctness.

## 9. Runtime Findings

Verification failures become normal `V*` findings.

Example:

```text
V1
Source: Browser Runtime Verification
Issue: Saving the dimension produces HTTP 500.
Evidence: POST /api/articles/332/tags → 500; UI remains unsaved after reload.
Expected: HTTP success and persisted dimension after reload.
Required Change: Fix the persistence path without widening scope.
Re-run: Original browser journey plus relevant automated tests.
```

Flow:

```text
VERIFYING
→ V* finding
→ REWORK_REQUIRED
→ AGY
→ THREE-AXIS REVIEW AGAIN
→ VERIFY AGAIN
```

Do not skip the renewed Three-Axis Review just because the browser journey becomes green.

## 10. Provider Unavailable

Chrome DevTools MCP is optional infrastructure, not a universal hard dependency.

If the selected provider is unavailable:

```text
1. Record TOOL_UNAVAILABLE honestly.
2. Attempt a previously approved equivalent seam when one exists
   (existing E2E, API integration test, curl/Newman, manual browser evidence, etc.).
3. Do not silently weaken a required acceptance criterion.
```

If Browser Runtime Verification was explicitly required and no equivalent seam can prove it, `CODE_VERIFIED` must not be issued.

If runtime verification was optional, report the skipped/partial evidence precisely and continue only when the remaining Spec permits it.

## 11. Security Boundary

A DevTools-connected browser may expose sensitive page state, cookies, request headers, responses, authenticated sessions, or executable runtime context.

Therefore:

```text
prefer a dedicated test browser/profile
avoid personal or production-authenticated sessions unless explicitly required and authorized
do not treat MCP access as permission for production mutation
do not expose credentials in logs or final reports
respect existing one-way/external-side-effect rules
```

Runtime verification does not override AGY Supervised Development safety and authorization boundaries.

## 12. Chrome Extension Applicability

For Chrome Extension tasks (for example a repository containing `manifest.json`), Browser Runtime Verification is normally highly applicable.

Typical journey:

```text
build extension
→ load/reload test extension when tooling permits
→ open target page
→ trigger extension action
→ inspect browser/extension console and network
→ verify downstream persisted result
```

The exact journey must come from the task's Spec, not from this generic example.

## 13. Core Rule

```text
Repository Evidence + Runtime Evidence
```

is stronger than either alone for browser-facing work.

But the governance remains unchanged:

```text
Chrome runtime green != REVIEW PASS
Chrome runtime green != CODE_VERIFIED by itself
Chrome runtime green != ACCEPTED
```

Only Codex can integrate repository, review, automated-test, runtime, regression, closeout, baseline, and side-effect evidence into final acceptance.
