---
name: agy-supervised-development
description: Codex-supervised development workflow. Codex shapes, specifies, reviews and verifies; AGY implements bounded execution units; Git and applicable runtime evidence prove delivery before closeout and acceptance.
version: 3.2.0-alpha.2
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
→ BASELINE
→ AGY BUILD
→ THREE-AXIS REVIEW
→ CODEX VERIFY
→ CLOSEOUT
→ ACCEPTED
```

Optional hooks:

```text
Complex bug → DIAGNOSE
Browser-facing task → optional Chrome DevTools MCP
Need second opinion → read-only AGY Consult
Interactive AGY need → tty7 fallback
```

## Roles

```text
User  = product / one-way decision authority
Codex = supervisor / spec owner / reviewer / verifier / acceptance authority
AGY   = primary writer
Git   = repository source of truth
```

Chrome DevTools MCP, when enabled, is a **Codex-owned verification adapter**. It is never an AGY writer dependency.

## Non-Negotiable Boundaries

1. Only Codex may mark `ACCEPTED`.
2. `AGY SUCCESS != REVIEW PASS`.
3. `REVIEW PASS != CODE_VERIFIED`.
4. `CODE_VERIFIED != ACCEPTED`.
5. Repository state is authoritative delivery evidence.
6. AGY does not decide unresolved product or architecture trade-offs.
7. One-way decisions require explicit user authority.
8. Do not push, merge, release, deploy, mutate production, or perform irreversible deletion unless explicitly authorized.
9. Do not use `--dangerously-skip-permissions` as a normal workaround.
10. Preserve user pre-existing changes; do not manufacture a clean worktree by rolling them back.

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

Classify the task as:

```text
Small
Medium
Large
```

Use complexity of decisions, contracts, propagation, verification, risk and worker context. Size may increase when new evidence appears.

Small tasks use a compact Shape/Spec and normally one execution unit. Medium/Large tasks use multiple verifiable slices.

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

Freeze a testable contract before implementation:

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

For browser-facing work, resolve runtime verification before Spec freeze when it materially affects acceptance evidence. If applicable and no effective preference exists, ask:

```text
Enable
Disable
Auto-decide
```

See `resources/spec-contract.md` and `resources/runtime-verification.md`.

## 5. SLICE

Prefer small, complete, independently reviewable units.

```text
normal behavior change → Vertical Slice / Tracer Bullet
wide mechanical change → Expand → Migrate → Contract
```

A good slice follows observable behavior end-to-end rather than separating all DB, API, UI and tests into unrelated horizontal phases.

See `resources/execution-slicing.md` and `templates/execution-unit.md`.

## 6. BASELINE

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

## 7. BUG DIAGNOSIS

For simple deterministic bugs:

```text
RED → root-cause fix → GREEN
```

For complex/uncertain bugs:

```text
reproduce
→ minimise
→ falsifiable hypotheses
→ targeted evidence
→ root cause
→ regression proof
```

Do not turn the first plausible code reading into root cause without a symptom-capable feedback loop.

For browser-observable bugs, Chrome DevTools MCP may provide Console / Network / runtime evidence when enabled.

See `resources/bugfix-workflow.md`.

## 8. AGY BUILD

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

## 9. THREE-AXIS REVIEW

Codex independently reads the resulting repository state:

```bash
git status --short
git diff --stat
git diff --check
git diff
```

Review three axes separately:

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

Finding severity and convergence live in the same review contract; do not create a second review state machine.

See `resources/review-gates.md` and `templates/review-report.md`.

## 10. REWORK

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

## 11. CODEX VERIFY

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

For browser-facing tasks, Chrome DevTools MCP may be used only according to `resources/runtime-verification.md`.

All required verification passing produces:

```text
CODE_VERIFIED
```

## 12. CLOSEOUT

After code verification, scan only the knowledge surfaces affected by the task:

```text
README / usage
project rules
API / schema / CLI / shared contracts
env / config / service / deploy / jobs
stale renamed or retired references
workspace residue
```

No documentation diff is required when existing knowledge is already current.

A code defect found during closeout returns to Rework → Review → Verify.

See `resources/closeout-governance.md` and `templates/closeout-contract.md`.

## 13. ACCEPTANCE

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

If the AGY conversation id is lost, do not guess the latest session. Start a replacement conversation with the approved Spec, current unit, repository state, findings and verification state. Repository progress remains valid evidence.

## Final Report

Keep the final report compact:

```text
Task size
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
agy-execution
agy-consult
tty7-supervision
bugfix-workflow
review-gates
completeness-regression
runtime-verification
closeout-governance
```

Keep the workflow serial and small. Add no new orchestration layer when an existing step or resource can express the requirement.
