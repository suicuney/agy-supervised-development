# Sol High Plan Review

Use this gate only before implementation.

```text
Codex = Plan Owner
Sol High = Independent Plan Reviewer
Chrome DevTools MCP = Browser Transport
User = Product / One-way Decision Authority
```

## Default

Plan review is enabled by default.

If the user explicitly says to skip Sol review / skip plan review / execute directly, skip this gate and freeze the Codex plan without opening ChatGPT Web.

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
