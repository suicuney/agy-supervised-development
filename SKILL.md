---
name: agy-supervised-development
description: Astra plans and reviews code; AGY implements and later executes Astra-defined tests through Herdr.
version: 4.1.0-alpha.1
---

# AGY Supervised Development 4.1

> **Astra plans. AGY builds. Astra reviews code. AGY proves it with Astra-defined tests.**

## Flow

```text
USER
→ ASTRA: PROBLEM + DEVELOPMENT CONTRACT
→ AGY via HERDR: IMPLEMENT ONLY
→ ASTRA: CODE REVIEW ONLY
   ├─ REWORK → AGY FIX → ASTRA CODE REVIEW
   └─ PASS
→ ASTRA: TEST PLAN + ACCEPTANCE METRICS
→ AGY via HERDR: TEST
   ├─ METRICS PASS → COMPLETE
   └─ METRICS FAIL/BLOCKED → AGY FIX or BLOCKED
        └─ any code change → ASTRA CODE REVIEW → refreshed TEST PLAN → AGY TEST
```

## Roles

- **Astra / architect**: locate the problem, freeze `WHAT / BOUNDARY / DONE`, review code, and after code review passes freeze the test plan and acceptance metrics.
- **AGY / worker**: inspect implementation details, write/fix code, and later execute the frozen test plan. Every AGY execution goes through Herdr.
- **Git + evidence**: baseline, task delta, code-review input, and test-result truth.

There is no default Luna/supervisor stage in 4.1.

## Development Contract

Keep it compact:

```yaml
contract_id: <id>
revision: 1
goal: <outcome>
behavior: [<observable result>]
constraints: [<important boundary>]
done: [<final completion condition>]
```

AGY owns ordinary implementation `HOW`. Do not require a file-level implementation plan by default.

## Phase 1 — AGY implementation only

AGY receives the Contract, applicable repository rules, baseline, and working directory.

The implementation order must explicitly say:

```text
IMPLEMENT ONLY.
Do not execute the formal task test plan or project quality gates in this phase.
Do not declare task completion.
```

AGY may inspect code and use non-test tooling needed to understand/edit it. If a command would execute tests or a formal verification gate, defer it to the testing phase unless Astra explicitly classifies it as necessary diagnostic inspection.

## Phase 2 — Astra code review only

After AGY stops writing, Astra reviews the complete task code delta against the Contract and applicable repository rules. This phase reviews code; it does not run tests.

```text
CODE_REVIEW_PASS | CODE_REVIEW_REWORK | BLOCKED
```

On `CODE_REVIEW_REWORK`, send only bounded findings to AGY, then review the resulting code again. Repeat until pass or a real blocker/product decision appears.

Read `resources/code-review.md` only for this phase.

## Phase 3 — Astra test plan

Only after `CODE_REVIEW_PASS`, Astra produces a frozen Test Plan with measurable acceptance criteria. The plan must identify required commands/checks, working directory, expected result/metric, applicability, and any project-required gates.

Astra does not execute the tests. AGY may not weaken or redefine the frozen metrics.

Read `resources/testing.md` for the test-plan and metric contract.

## Phase 4 — AGY testing

AGY executes the frozen Test Plan through Herdr and reports raw results plus normalized metrics. A check that did not execute cannot be PASS.

If all required metrics pass and no required check is blocked/not-run:

```text
TASK COMPLETE
```

Astra does not perform a second test-review pass.

If testing leads AGY to modify production code, the previous `CODE_REVIEW_PASS` and affected test evidence become stale. Return to Astra code review, then refresh/freeze the Test Plan and test again.

## Runtime / baseline / recovery

- Preserve user changes; do not auto-stash, clean, reset, overwrite, push, merge, deploy, or perform irreversible actions without authority.
- Herdr workspace is runtime isolation, not Git isolation.
- Capture baseline before AGY writes and bind code-review/test evidence to the actual code state, including uncommitted content.
- Store Run State under Git-private storage; never store credentials or unrelated chat history.
- Do not guess lost sessions or automatically replay commands with uncertain side effects.

Read `resources/run-state.md` when creating/resuming/recovering a run and `resources/agy-execution.md` when dispatching AGY.

## Progressive disclosure

Load only what the current stage needs:

- `resources/development-contract.md` — Contract + patch authority
- `resources/run-state.md` — baseline, phase state, recovery
- `resources/agy-execution.md` — Herdr worker dispatch
- `resources/code-review.md` — Astra code-only review loop
- `resources/testing.md` — frozen test plan, metrics, completion

Legacy 3.x and 4.0 Luna-supervisor material is not part of the default execution path.
