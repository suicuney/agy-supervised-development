# Sol High Plan Review

Use this gate only before implementation.

```text
Codex = Plan Owner
Sol High = Independent Plan Reviewer
Chrome DevTools MCP / approved Chrome session = Browser Transport
User = Product / One-way Decision Authority
```

## Default

Plan review is enabled by default.

If the user explicitly says to skip Sol review / skip plan review / execute directly, skip this gate and freeze the Codex plan without opening ChatGPT Web.

## Dependency Preflight

Run this before opening ChatGPT Web:

```bash
scripts/check-sol-plan-review.sh
```

The check uses the versioned `resources/sol-plan-review-manifest.json` and returns:

```text
0  COMPLETE
10 MISSING
11 INCOMPLETE
12 INVALID_MANIFEST
```

`SKILL.md` alone is not enough. If the result is `MISSING`, install the private source with the explicit helper and check again:

```bash
scripts/install-sol-plan-review.sh
scripts/check-sol-plan-review.sh
```

The installer uses a full checkout, refuses to overwrite an existing destination, prints the source revision, and retains and reports a partial destination on failure. Do not treat an incomplete install as available and do not copy the private skill into this repository.

If the result is `INCOMPLETE`, keep the directory for inspection and report it; after the user confirms it is the failed installer artifact, move it aside and rerun the installer. The helper intentionally refuses to overwrite or silently delete an existing destination.

## Input

Codex first completes the executable plan from the current Shape / Spec / Slice work.

The review packet should contain only the needed truth:

```text
User Requirement
Repository Facts
Resolved Decisions
Executable Plan
Acceptance Criteria
Execution Slices
Verification Strategy
Risks / One-way Decisions
Codex Local Judgment
```

Use the installed `sol-high-plan-review` Skill for packet and browser details.

## Browser Runbook

Use the approved Chrome browser surface and keep the semantic contract in the installed `sol-high-plan-review` Skill. When the user explicitly asks for an already-open Chrome session:

1. Discover the current user tabs from live browser state. Do not guess tab IDs or send input to unrelated tabs.
2. Reuse a ChatGPT tab only when its current identity is verified. Otherwise create a new ChatGPT tab in the same Chrome session; leave the user's other tabs untouched.
3. If ChatGPT is not authenticated, stop at the login handoff and ask the user to sign in. Never inspect or export cookies, passwords, session databases, or auth tokens.
4. Read a fresh visible snapshot before every consequential action. Open the model/reasoning menu and verify `GPT-5.6 Sol` is selected and `High` is selected; do not infer either value from a default label.

For Codex desktop, the reliable sequence is: select the Chrome browser binding → list user tabs → claim only an exact verified ChatGPT tab or create a new tab in that same browser → navigate to ChatGPT Web → snapshot after each action. A fresh unauthenticated page is a login state, not a failed model state and not permission to switch browsers.

Record the actual browser transport, selected model, and reasoning level as part of the evidence. Do not silently switch to an in-app browser, another browser controller, another model, or another reasoning level.

## Packet and Send State

Automate everything that does not submit externally: build the packet, run the packet-safety check, verify the model state, and fill the draft. The final browser Send remains an action-time confirmation.

Track only:

```text
NOT_SENT → SENT
NOT_SENT → UNKNOWN
```

If the result around Send is ambiguous, keep `UNKNOWN` terminal until the same conversation visibly proves whether it was sent. Never resend automatically.

After Send, wait for assistant generation to finish, then read the same conversation. A review is complete only when the required sentinel is present and the response contains exactly one of `PASS`, `REVISE`, or `USER_DECISION_REQUIRED`.

## Loop

```text
Codex Plan
→ Sol High Review
→ Codex Adopt / Reject / Modify
→ Revised Plan
→ optional next round
```

Maximum Sol review rounds:

```text
3
```

Three is a limit, not a target. Stop early when the plan has converged.

Sol verdicts:

```text
PASS
REVISE
USER_DECISION_REQUIRED
```

Continue only when a blocking finding remains and another round can materially improve the plan.

Non-blocking suggestions and backlog ideas do not keep the loop open.

## User Escalation

Stop the model loop immediately when a real product/architecture/compatibility/security/cost/destructive trade-off needs user authority.

If round 3 still has unresolved blocking disagreement, stop and present a compact user decision brief. Never start round 4.

When a round returns `REVISE`, continue the same verified conversation with a complete revised packet. Record each blocking finding as `Adopt`, `Reject`, or `Modify` before sending the next round. If the browser or connection becomes ambiguous, stop rather than opening a duplicate conversation.

## Freeze Boundary

When Codex records:

```text
PLAN FROZEN
```

Sol High exits the task.

Do not use Sol High during:

```text
AGY Build
Three-Axis Review
Rework
Independent Verification
Browser Runtime Verification
Closeout
Acceptance
```

After freeze, implementation and runtime evidence—not another model opinion—drive delivery decisions.

## Failure

If Chrome DevTools MCP, ChatGPT login, GPT-5.6 Sol, or High is unavailable, do not silently substitute another model or transport.

Report the capability failure. The user may fix the capability or explicitly disable plan review for the task.

Common capability states:

```text
skill missing/incomplete → install/check before browser work
ChatGPT unauthenticated  → user login handoff
wrong model or reasoning → correct it and re-verify visibly
Send state UNKNOWN        → no retry; recover the same conversation
sentinel/verdict missing  → review failed; do not infer PASS
```
