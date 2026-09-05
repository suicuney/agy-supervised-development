---
name: agy-supervised-development
description: Codex-supervised development workflow. Codex owns the executable plan and final acceptance; Herdr is the only AGY runtime; Antigravity CLI implements bounded work; Git and independent verification prove delivery.
version: 3.3.0-alpha.2
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
→ SOL HIGH PLAN REVIEW      # 中文发送前计划 + 一次确认；max 3 rounds
→ PLAN FROZEN               # 中文最终计划展示；无需再次确认
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

ego-browser / ego-lite remains Codex-owned. It serves as the sole browser transport for Sol High plan review before freeze and optional browser-runtime verification after implementation, but it never owns workflow decisions. Browser operations are governed strictly by `resources/ego-browser-runbook.md`.

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

## 2. SIZE

Classify the task as `Small | Medium | Large`. Small uses compact Shape/Spec and normally one execution unit; Medium/Large use multiple verifiable slices. See `resources/task-sizing.md`.

## 3. SHAPE

Resolve only decisions needed for implementation. Repository facts are inspected by Codex, external facts researched when needed, and real product/architecture trade-offs return to the user. See `resources/shaping.md`.

## 4. SPEC

Freeze intended behavior into a testable contract: problem, expected behavior, scenarios, implementation decisions, acceptance criteria, verification seam, test strategy, out of scope and one-way decisions. See `resources/spec-contract.md` and `resources/runtime-verification.md`.

## 5. SLICE

Prefer small, complete, independently reviewable units. Normal behavior change uses Vertical Slice / Tracer Bullet; wide mechanical change uses Expand → Migrate → Contract. See `resources/execution-slicing.md` and `templates/execution-unit.md`.

## 6. SOL HIGH PLAN REVIEW

Plan Review is enabled by default unless the user explicitly opts out. Codex sends the executable plan through the installed `sol-high-plan-review` Skill using the ego-browser / ego-lite transport (guided by `resources/ego-browser-runbook.md`) to ChatGPT Web with GPT-5.6 Sol + High reasoning.

Before browser work:

```bash
scripts/check-sol-plan-review.sh
```

Before the **first** Send, Codex must show a concise Chinese summary of the plan being reviewed:

```text
【准备发送给 Sol High 的计划】

目标
- <本次任务目标>

计划
1. <关键步骤>
2. <关键步骤>
3. <关键步骤>

重点风险
- <真正重要的风险；没有可省略>
```

The summary must be Chinese, concise, and focused on what Codex plans to do. Do not substitute packet size, character count, filenames, or attachment size for the actual plan content.

Ask the user to confirm the **first Send once**. After that confirmation, later `REVISE` rounds continue automatically in the same verified conversation after Codex applies `Adopt / Reject / Modify`. Do not repeatedly ask for Send confirmation.

Only return to the user during the review loop for `USER_DECISION_REQUIRED`, a real one-way/product/architecture decision, authentication handoff, `UNKNOWN` Send state, or another genuine blocker.

Maximum review rounds: `3`. Stop early on PASS or non-blocking notes. `USER_DECISION_REQUIRED` or blocking round 3 returns to the user. Never start round 4. See `resources/sol-plan-review.md`.

## 7. PLAN FROZEN

When Sol review converges, Codex forms the final authoritative plan and shows a concise Chinese summary before freezing:

```text
【最终执行计划】

Sol High 评审：PASS | 已收敛
评审轮次：<n>

最终计划
1. <最终执行步骤>
2. <最终执行步骤>
3. <最终执行步骤>

评审后的主要调整
- <有则列出；没有则写“无关键调整”>
```

This is visibility output, not another approval gate. Do **not** ask the user to confirm again when no real decision remains.

Then record:

```text
PLAN FROZEN
```

and continue automatically to `BASELINE → AGY BUILD`.

From `PLAN FROZEN` onward, Sol High exits the task completely.

## 8. BASELINE

Before AGY writes:

```bash
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

Record baseline-owned paths and, when needed:

```bash
git diff --binary -- <baseline paths> | shasum -a 256
```

## 9. BUG DIAGNOSIS

Simple deterministic bug: `RED → root-cause fix → GREEN`.

Complex bug: `reproduce → minimise → falsifiable hypotheses → targeted evidence → root cause → regression proof`.

See `resources/bugfix-workflow.md`.

## 10. AGY BUILD — HERDR ONLY

Preflight:

```bash
scripts/check-herdr.sh
```

Required prerequisites are Herdr, AGY, `jq`, a reachable Herdr server, and a usable Antigravity integration. If unavailable, stop as `BLOCKED`; never switch runtimes or silently install user-level integration hooks.

Create a task-owned workspace on `repo_root` and consume the IDs returned by Herdr:

```bash
created="$(herdr workspace create --cwd "$repo_root" --label "$task_label" --no-focus)"
workspace_id="$(printf '%s' "$created" | jq -r '.result.workspace.workspace_id')"
pane_id="$(printf '%s' "$created" | jq -r '.result.root_pane.pane_id')"
```

Start one stable task-local AGY worker:

```bash
herdr agent start "$agy_agent" --kind agy --pane "$pane_id"
```

Send the current Execution Unit:

```bash
herdr agent prompt "$agy_agent" "$execution_unit" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout "$timeout_ms"
```

If blocked, read before interacting:

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 120
```

Only minimum safe interaction within frozen scope and existing authority may proceed. One-way decisions return to the user.

After a settled state:

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 160
git status --short
git diff --stat
git diff --check
git diff
```

Herdr state is runtime evidence only. Use the same Herdr-managed AGY worker for bounded Rework while the exact session remains valid. Herdr's Antigravity integration owns native conversation identity and restore; this workflow never directly resumes AGY.

See `resources/agy-execution.md` and `resources/failure-modes.md`.

## 11. THREE-AXIS REVIEW

Codex independently reviews:

```text
A. Spec Fidelity
B. Engineering Quality
C. Completeness
```

All PASS → REVIEW PASS; any REWORK → REWORK_REQUIRED; unresolved BLOCKED → BLOCKED. See `resources/review-gates.md` and `templates/review-report.md`.

## 12. REWORK

Every actionable finding uses a stable ID and bounded Rework Contract. Send it to the same Herdr-managed AGY worker. After rework, rerun the full Three-Axis Review. See `templates/rework-contract.md`.

## 13. CODEX VERIFY

Only after Review PASS, Codex independently runs relevant lint/format/typecheck/unit/integration/e2e/build/schema/repro/browser seams. Worker self-report cannot replace this step. Verification failures become `V*`, return to Rework, then full Review and Verify again.

## 14. CLOSEOUT

After code verification, scan only knowledge surfaces affected by the task. When AGY edits are needed, they also run through the same Herdr-managed worker. A code defect found during Closeout returns to Rework → Review → Verify. See `resources/closeout-governance.md` and `templates/closeout-contract.md`.

## 15. ACCEPTANCE

Codex may mark `ACCEPTED` only when Three-Axis Review, Independent Verification, required regression proof, Knowledge Closeout, baseline preservation and final diff explainability all pass with no unauthorized side effect.

A task-owned Herdr workspace may be closed after acceptance; never close unrelated user workspaces.

## Recovery

Herdr owns runtime/session continuity. With the official Antigravity integration installed, Herdr can restore the reported AGY conversation after a server restart.

If the exact AGY session cannot be restored, do not guess another conversation. Preserve repository state and mark runtime blocked. A replacement Herdr-managed AGY may start only with frozen plan, current unit, repository state, findings and verification state explicitly re-supplied.

## Final Report

Keep it compact: task size, plan review/rounds, plan frozen, Herdr runtime status, changed behavior/files, AGY status, Three-Axis Review, Rework cycles, Verification, browser runtime when applicable, Closeout, blocked/out-of-scope items and final repository state.

## Active Resources

```text
task-sizing
shaping
spec-contract
execution-slicing
sol-plan-review
ego-browser-runbook
agy-execution
failure-modes
bugfix-workflow
review-gates
completeness-regression
runtime-verification
closeout-governance
```

Keep the workflow serial and small. Herdr is infrastructure, not governance. One task uses one primary AGY writer; multi-writer orchestration is out of scope for 3.3.
