---
name: agy-supervised-development
description: Delegate repository implementation to AGY through Herdr while Codex keeps task boundaries, supervision, escalation, and delivery verification.
version: 4.0.0-alpha.1
---

# AGY Supervised Development 4.0

> **Astra frames. Luna supervises. AGY builds. Git tells the truth.**

Use this workflow when Codex should delegate repository implementation to Antigravity CLI (AGY) through Herdr while keeping model cost proportional to decision difficulty.

## Default Flow

```text
USER INTENT
→ ASTRA ARCHITECT
→ DEVELOPMENT CONTRACT
→ CONTRACT FROZEN
→ LUNA SUPERVISOR
→ BASELINE
→ AGY BUILD                 # Herdr only
→ AGY SELF-REVIEW
→ LUNA REVIEW / VERIFY
→ ACCEPTED
```

Escalation is exceptional, not the default path:

```text
LUNA
→ ESCALATE
→ ASTRA
→ CONTRACT PATCH
→ LUNA
→ AGY
```

## Roles

```text
User   = product / one-way decision authority
Astra  = architect / high-value reasoning / contract author
Luna   = supervisor / dispatcher / independent reviewer / verifier
Herdr  = sole AGY runtime / control plane
AGY    = implementation planner / primary writer / self-reviewer
Git    = repository source of truth
```

Model names describe preferred role bindings, not hard-coded product dependencies. If an equivalent model is substituted, preserve the capability split: `architect = strongest reasoning`, `supervisor = lower-cost reliable supervision`.

## Core Boundaries

1. The architect owns `WHAT / WHY / BOUNDARY / DONE`, not detailed implementation choreography.
2. AGY owns normal implementation planning and `HOW` decisions inside the frozen contract.
3. Luna may supervise, inspect evidence, request bounded rework, and verify completion, but must not silently redesign the contract.
4. Escalate to Astra only for architecture conflict, material requirement ambiguity, scope explosion, repeated core failure, or one-way decisions.
5. Every AGY invocation runs through Herdr. Do not add a second AGY runtime or silently invoke `agy` directly.
6. Herdr lifecycle state is runtime evidence only. `done` / `idle` / `blocked` are never delivery verdicts.
7. AGY self-review is required but never substitutes for Luna independent review.
8. Prefer Git diff, targeted repository evidence, AGY reports, and test output over re-reading the entire repository during supervision.
9. Preserve pre-existing user changes and existing repository instructions.
10. Do not push, merge, deploy, mutate production, perform destructive migration, or make irreversible deletion without existing user authority.
11. `CONTRACT FROZEN != implementation complete`.
12. `AGY SUCCESS != REVIEW PASS`.
13. `REVIEW PASS != VERIFIED`.
14. `VERIFIED != ACCEPTED` when unresolved blockers or unauthorized side effects remain.

## Progressive Disclosure Router

Read only the resource needed for the current stage:

- Architect behavior and context budget: `resources/architect.md`
- Development Contract schema and freeze rules: `resources/development-contract.md`
- Luna supervision loop and evidence policy: `resources/supervisor.md`
- Escalation thresholds and Contract Patch semantics: `resources/escalation.md`
- AGY autonomy and Herdr execution: `resources/agy-execution.md`
- Review and verification: `resources/verification.md`
- Legacy high-risk external plan review, only when explicitly justified: `resources/sol-plan-review.md`
- Browser transport when actually needed: `resources/ego-browser-runbook.md`

Do not preload all resources for every task.

## Context Economy

Default to pointer-over-copy:

```text
Astra receives:
- user intent
- only repository facts needed to resolve contract-level decisions
- relevant constraints

Luna receives:
- frozen Development Contract
- current Git evidence
- AGY completion / blocked report
- relevant test or runtime output

AGY receives:
- frozen Development Contract
- repository workspace
- bounded rework findings when needed
```

Avoid copying large source files, repository summaries, or Astra reasoning into the Luna or AGY prompt when those facts can be discovered in the workspace.

## Completion

A normal task finishes only when:

```text
contract satisfied
+ relevant implementation complete
+ AGY self-review complete
+ Luna independent review passes
+ relevant verification passes
+ final diff is explainable
+ no unresolved escalation remains
```

Keep the workflow serial and single-writer. Supervision may be cheap; architectural reasoning should be sparse and valuable.
