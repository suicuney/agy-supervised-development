---
name: agy-supervised-development
description: Codex-supervised development workflow. Codex owns the executable plan and final acceptance; Herdr is the only AGY runtime; Antigravity CLI implements bounded work; Git and independent verification prove delivery.
version: 3.3.0-alpha.1
---

# AGY Supervised Development 3.3

> **Codex governs. Herdr runs. AGY builds. Git tells the truth.**

Use this workflow when Codex should supervise implementation performed by Antigravity CLI (AGY) through Herdr.

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
→ AGY BUILD                 # Herdr only
→ THREE-AXIS REVIEW
→ CODEX VERIFY
→ CLOSEOUT
→ ACCEPTED
```

If the user explicitly opts out of Sol plan review:

```text
SLICE
→ PLAN FROZEN
→ BASELINE
→ AGY BUILD
```

## Roles

```text
User     = product / one-way decision authority
Codex    = supervisor / plan owner / reviewer / verifier / acceptance authority
Sol High = pre-implementation plan reviewer only
Herdr    = sole AGY runtime / agent control plane
AGY      = primary writer
Git      = repository source of truth
```

Chrome DevTools MCP remains Codex-owned. It may transport Sol High plan review before freeze and provide browser-runtime verification after implementation, but it never owns workflow decisions.

## Non-Negotiable Boundaries

1. Only Codex may mark `ACCEPTED`.
2. Codex remains the authoritative executable-plan owner.
3. Sol High only reviews the plan before `PLAN FROZEN`.
4. Every AGY execution runs through Herdr. Do not invoke `agy` directly from this workflow.
5. Do not add a second terminal runtime, fallback runtime, or runtime-selection layer.
6. Herdr lifecycle state is runtime evidence only: `done` / `idle` / `blocked` are not delivery verdicts.
7. `AGY SUCCESS != REVIEW PASS`.
8. `REVIEW PASS != CODE_VERIFIED`.
9. `CODE_VERIFIED != ACCEPTED`.
10. Repository state is authoritative delivery evidence.
11. AGY does not decide unresolved product or architecture trade-offs.
12. One-way decisions require explicit user authority.
13. Do not push, merge, release, deploy, mutate production, or perform irreversible deletion unless explicitly authorized.
14. Do not use blanket permission bypass as a normal workaround.
15. Preserve user pre-existing changes.

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

Plan Review is enabled by default. If the user explicitly says to skip Sol review / skip plan review / execute directly, skip this step.

Otherwise Codex sends the executable plan through the installed `sol-high-plan-review` Skill, using Chrome DevTools MCP to ChatGPT Web with GPT-5.6 Sol + High reasoning.

Before browser work, run:

```bash
scripts/check-sol-plan-review.sh
```

Loop:

```text
Codex Plan
→ Sol High Review
→ Codex Adopt / Reject / Modify
→ Revised Plan
```

Maximum Sol review rounds: `3`. Stop early on PASS or when only non-blocking suggestions remain. If Sol returns `USER_DECISION_REQUIRED`, or round 3 still has blocking disagreement, stop and ask the user. Never start round 4.

See `resources/sol-plan-review.md`.

## 7. PLAN FROZEN

Codex owns the final plan and records:

```text
PLAN FROZEN
```

From this point forward, Sol High exits the task completely. No Sol High calls during AGY Build, Review, Rework, Verify, Closeout, or Acceptance.

## 8. BASELINE

Before AGY writes:

```bash
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

Record baseline-owned changed paths and a binary patch fingerprint outside the repository when needed:

```bash
git diff --binary -- <baseline paths> | shasum -a 256
```

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

After `PLAN FROZEN`, Sol High is not reopened for bug discussion.

See `resources/bugfix-workflow.md`.

## 10. AGY BUILD — HERDR ONLY

Preflight:

```bash
scripts/check-herdr.sh
```

If Herdr, AGY, the running Herdr server, AGY kind support, or the Antigravity integration is unavailable, stop as `BLOCKED`. Runtime setup is explicit; the task flow never silently installs or rewrites user-level integrations.

Create a task-owned Herdr workspace bound to the repository and use the IDs returned by Herdr:

```bash
created="$(herdr workspace create --cwd "$repo_root" --label "$task_label" --no-focus)"
workspace_id="$(printf '%s' "$created" | jq -r '.result.workspace.workspace_id')"
pane_id="$(printf '%s' "$created" | jq -r '.result.root_pane.pane_id')"
```

Create one stable task-local AGY name matching Herdr's agent naming rules, then start AGY in that exact pane:

```bash
herdr agent start "$agy_agent" --kind agy --pane "$pane_id"
```

Send the current Execution Unit through Herdr:

```bash
herdr agent prompt "$agy_agent" "$execution_unit" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout "$timeout_ms"
```

If the agent becomes blocked, read before interacting:

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 120
```

Codex may send the minimum safe key interaction only when it is within the frozen Execution Unit and existing authority. A one-way decision still returns to the user.

After a settled runtime state, read the worker report and inspect Git independently:

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 160
git status --short
git diff --stat
git diff --check
git diff
```

Herdr `done` / `idle` only means the runtime reached a recognized state. It never skips repository Review or Verification.

Use the same named AGY worker for bounded Rework while the task session remains valid. Herdr's Antigravity integration owns native conversation identity and restore; this workflow does not call `agy --conversation` itself.

See `resources/agy-execution.md` and `resources/failure-modes.md`.

## 11. THREE-AXIS REVIEW

Codex independently reviews repository state on three axes:

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

Send the Rework Contract to the same Herdr-managed AGY worker. After AGY rework, rerun the full Three-Axis Review before verification.

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

Worker self-report cannot replace this step. Verification failure becomes `V*` and returns to AGY rework, then full Review again, then Verify again.

For browser-facing tasks, Chrome DevTools MCP may be used according to `resources/runtime-verification.md`.

All required verification passing produces `CODE_VERIFIED`.

## 14. CLOSEOUT

After code verification, scan only knowledge surfaces affected by the task. No documentation diff is required when existing knowledge is already current.

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

A task-owned Herdr workspace may be closed after acceptance. Never close or mutate a user-owned unrelated workspace.

## Recovery

Herdr owns runtime/session continuity. With the official Antigravity integration installed, Herdr can restore the reported AGY conversation after a Herdr server restart.

If the exact AGY session cannot be restored, do not guess another conversation. Preserve repository state and mark the runtime blocked. A replacement Herdr-managed AGY worker may be started only with the frozen plan, current unit, repository state, findings and verification state explicitly re-supplied.

## Final Report

Keep the final report compact:

```text
Task size
Plan review status / rounds
Plan frozen state
Herdr runtime status
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
failure-modes
bugfix-workflow
review-gates
completeness-regression
runtime-verification
closeout-governance
```

Keep the workflow serial and small. Herdr is infrastructure, not governance. One task uses one primary AGY writer; multi-writer orchestration is out of scope for 3.3.
