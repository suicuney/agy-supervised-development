---
name: agy-supervised-development
description: Codex-supervised development workflow. Codex shapes, specifies, slices, owns the executable plan, optionally converges that plan with GPT-5.6 Sol High before freeze, then delegates bounded implementation to AGY and independently reviews/verifies delivery evidence.
version: 3.2.0-alpha.3
---

# AGY Supervised Development 3.2

> **Codex shapes and proves. AGY builds. Git tells the truth.**

Use this workflow when Codex should supervise implementation performed by AGY.

## Core Flow

```text
INTAKE
→ SIZE
→ SHAPE
→ SPEC
→ SLICE
→ SOL HIGH PLAN REVIEW      # default enabled; max 3 rounds
→ PLAN FROZEN
→ BASELINE
→ AGY BUILD
→ THREE-AXIS REVIEW
→ CODEX VERIFY
→ CLOSEOUT
→ ACCEPTED
```

Explicit user opt-out:

```text
SLICE
→ PLAN FROZEN
→ BASELINE
→ AGY BUILD
```

Optional runtime hook:

```text
Browser-facing verification → Chrome DevTools MCP
```

## Roles

```text
User     = product / one-way decision authority
Codex    = supervisor / plan owner / reviewer / verifier / acceptance authority
Sol High = pre-implementation plan reviewer only
AGY      = primary writer
Git      = repository source of truth
```

Chrome DevTools MCP is a Codex-owned browser tool. It may transport Sol High plan review before freeze and provide runtime verification after implementation, but it never owns workflow decisions.

## Non-Negotiable Boundaries

1. Only Codex may mark `ACCEPTED`.
2. Codex remains the authoritative executable-plan owner.
3. Sol High only reviews the plan before `PLAN FROZEN`.
4. `AGY SUCCESS != REVIEW PASS`.
5. `REVIEW PASS != CODE_VERIFIED`.
6. `CODE_VERIFIED != ACCEPTED`.
7. Repository state is authoritative delivery evidence.
8. AGY does not decide unresolved product or architecture trade-offs.
9. One-way decisions require explicit user authority.
10. Do not push, merge, release, deploy, mutate production, or perform irreversible deletion unless explicitly authorized.
11. Do not use `--dangerously-skip-permissions` as a normal workaround.
12. Preserve user pre-existing changes.

## 1. INTAKE

Read repository facts before planning:

```text
AGENTS.md / CLAUDE.md / README.md
relevant code / schema / API / tests
CI / build / e2e conventions
Git state
```

Facts that can be inspected should be inspected by Codex rather than asked back to the user.

## 2. SIZE

Classify the task as `Small | Medium | Large` using decisions, contracts, propagation, verification, risk and worker context.

Small tasks use compact Shape/Spec and normally one execution unit. Medium/Large tasks use multiple verifiable slices.

See `resources/task-sizing.md`.

## 3. SHAPE

Resolve only the decisions needed for implementation:

```text
Goal / Destination
Resolved Decisions
Open Decisions
Not Yet Specified
Out of Scope
One-way Decisions
```

Repository fact → Codex inspects.
External fact → Codex researches when needed.
Real product/architecture trade-off → user decides.

See `resources/shaping.md`.

## 4. SPEC

Freeze the intended behavior into a testable contract:

```text
Problem
Expected Behavior
Scenarios
Implementation Decisions
Acceptance Criteria
Verification Seam
Test Strategy
Out of Scope
One-way Decisions
```

For browser-facing work, resolve runtime verification preference when it materially affects acceptance evidence.

See `resources/spec-contract.md` and `resources/runtime-verification.md`.

## 5. SLICE

Prefer small, complete, independently reviewable units.

```text
normal behavior change → Vertical Slice / Tracer Bullet
wide mechanical change → Expand → Migrate → Contract
```

The completed Shape + Spec + Slice set is the Codex-authored **Executable Plan**.

See `resources/execution-slicing.md` and `templates/execution-unit.md`.

## 6. SOL HIGH PLAN REVIEW

Default:

```text
Plan Review = enabled
```

If the user explicitly says to skip Sol review / skip plan review / execute directly, skip this step.

Otherwise Codex sends the executable plan through the installed `sol-high-plan-review` Skill, using Chrome DevTools MCP to ChatGPT Web with:

```text
GPT-5.6 Sol
High reasoning
```

Loop:

```text
Codex Plan
→ Sol High Review
→ Codex Adopt / Reject / Modify
→ Revised Plan
```

Maximum Sol review rounds:

```text
3
```

Stop early on `PASS` or when only non-blocking suggestions remain.

If Sol returns `USER_DECISION_REQUIRED`, or round 3 still has blocking disagreement, stop the loop and ask the user. Never start round 4.

See `resources/sol-plan-review.md`.

## 7. PLAN FROZEN

Codex owns the final plan and records:

```text
PLAN FROZEN
```

From this point forward, Sol High exits the task completely.

No Sol High calls during AGY Build, Review, Rework, Verify, Closeout, or Acceptance.

## 8. BASELINE

Before AGY writes:

```bash
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

Record branch, base head and pre-existing changes.

Rule:

```text
current changes - baseline changes = task-introduced changes
```

## 9. BUG DIAGNOSIS

Simple deterministic bug:

```text
RED → root-cause fix → GREEN
```

Complex/uncertain bug:

```text
reproduce
→ minimise
→ falsifiable hypotheses
→ targeted evidence
→ root cause
→ regression proof
```

Do not turn the first plausible code reading into root cause without a symptom-capable feedback loop.

After `PLAN FROZEN`, Sol High is not reopened for bug discussion.

See `resources/bugfix-workflow.md`.

## 10. AGY BUILD

Prefer the thin adapter:

```bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --timeout 30m \
  "<Execution Unit>"
```

Resume bounded rework with the real conversation id when available:

```bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --conversation "$agy_conversation_id" \
  "<Rework Contract>"
```

AGY success or exit 0 only ends the writer turn. It does not prove delivery.

Use tty7 only when real interaction is required.

See `resources/agy-execution.md` and `resources/tty7-supervision.md`.

## 11. THREE-AXIS REVIEW

Codex independently reads repository state and reviews three axes:

```text
A. Spec Fidelity       — did we build the right thing?
B. Engineering Quality — was it built well?
C. Completeness        — what did we forget?
```

Aggregate:

```text
A PASS + B PASS + C PASS → REVIEW PASS
any REWORK               → REWORK_REQUIRED
any unresolved BLOCKED   → BLOCKED
```

Finding severity and convergence live in the same review contract.

Sol High is not part of this stage.

See `resources/review-gates.md` and `templates/review-report.md`.

## 12. REWORK

Every actionable finding uses a stable ID and bounded contract:

```text
Finding ID
Axis / Source
Issue
Evidence
Expected
Required Change
Re-run
Scope Reminder
Forbidden Actions
```

After AGY rework, rerun the full Three-Axis Review before verification.

See `templates/rework-contract.md`.

## 13. CODEX VERIFY

Only after Review PASS, Codex independently runs the relevant seams:

```text
lint / format-check
typecheck
unit
integration
e2e
build/package
schema/contract checks
original bug repro
browser runtime / performance when required
```

Worker self-report cannot replace this step.

Verification failure becomes `V*` and returns to AGY rework, then full Review again, then Verify again.

For browser-facing tasks, Chrome DevTools MCP may be used according to `resources/runtime-verification.md`.

All required verification passing produces `CODE_VERIFIED`.

## 14. CLOSEOUT

After code verification, scan only knowledge surfaces affected by the task.

No documentation diff is required when existing knowledge is already current.

A code defect found during closeout returns to Rework → Review → Verify.

See `resources/closeout-governance.md` and `templates/closeout-contract.md`.

## 15. ACCEPTANCE

Codex may mark `ACCEPTED` only when:

```text
Three-Axis Review PASS
Independent Verification PASS
Required regression proof satisfied
Knowledge Closeout PASS
Baseline preserved
No unauthorized side effect
Final diff explainable
```

## Recovery

If the AGY conversation id is lost, do not guess the latest session. Start a replacement conversation with the frozen plan, current unit, repository state, findings and verification state.

## Final Report

Keep the final report compact:

```text
Task size
Plan review status / rounds
Plan frozen state
What changed
AGY execution status
Three-Axis Review result
Rework findings/cycles
Verification result
Browser runtime result when applicable
Closeout result
Blocked / out-of-scope items
Final repository state
```

## Active Resources

```text
task-sizing
shaping
spec-contract
execution-slicing
sol-plan-review
agy-execution
tty7-supervision
bugfix-workflow
review-gates
completeness-regression
runtime-verification
closeout-governance
```

Keep the workflow serial and small. Add no new orchestration layer when an existing step or resource can express the requirement.
