---
name: agy-supervised-development
description: Astra plans and reviews code; Herdr-managed AGY implements, diagnoses within Contract authority, and executes Astra-frozen tests.
version: 4.1.0-alpha.2
---

# AGY Supervised Development 4.1

> **Astra plans. AGY builds. Astra reviews code. AGY proves it with Astra-defined tests. A deterministic gate completes.**

## Flow

```text
USER
→ ASTRA: PROBLEM + compact CONTRACT + acceptance scenarios + optional diagnostics
→ AGY via HERDR: IMPLEMENT / bounded diagnostics
→ ASTRA: CODE REVIEW ONLY
   ├─ REWORK → AGY bounded fix → ASTRA CODE REVIEW
   └─ PASS
→ ASTRA: freeze machine-readable TEST PLAN + metrics
→ deterministic TEST-entry validation
→ AGY via HERDR: formal TEST
   ├─ code/deliverable change → invalidate → AGY repair → ASTRA CODE REVIEW
   ├─ environment blocker → BLOCKED
   └─ evidence complete
→ deterministic completion validation
→ COMPLETE
```

There is no default Luna supervisor, Sol plan review, or second Astra test-review stage.

## Contract

Astra freezes only `WHAT / BOUNDARY / DONE`, observable acceptance scenarios/counterexamples, and optional **pre-authorized** minimal diagnostics. AGY owns normal implementation `HOW`; do not require a file-level plan.

Diagnostics may include a minimal reproduction, targeted test, typecheck or compile feedback when useful. They are recorded with `formal_acceptance=false` and never satisfy the frozen formal Test Plan. Applicable project rules such as mandatory TDD remain binding.

Read `resources/development-contract.md` when creating/patching the Contract.

## Baseline / identity

Before AGY writes, snapshot the repository with `scripts/snapshot-code-state.sh` into Git-private/external storage. Preserve existing staged/unstaged/untracked user content; do not auto-stash/reset/clean.

Use separate identities:

- `deliverable_digest`: actual deliverable content/type/path/symlink target/executable identity; staging alone does not change it.
- `ownership_digest`: Git HEAD/index/status attribution used by recovery.

Untracked original content is archived locally; symlinks are not followed. Sensitive/unsupported inputs fail closed unless explicitly covered. Herdr workspace is runtime isolation, not code isolation.

Read `resources/run-state.md` for baseline, phase state and recovery.

## AGY / Herdr

Every AGY implementation, rework and formal-test run goes through Herdr. `done/idle` is lifecycle evidence only. Before dispatch confirm the prior worker is not still active; `SEND_UNKNOWN` is investigated and never automatically resent. Do not start a replacement writer until the old writer cannot write concurrently.

Read `resources/agy-execution.md` only when dispatching AGY.

## Astra code review

After AGY stops writing, Astra reviews the full deliverable delta against Contract and applicable repository rules. Astra does **not** execute tests/builds/quality gates here.

Review production code plus test source/assertions/fixtures/goldens, config, lockfiles, generated source, callers/consumers, schema/docs and relevant binary/mode changes. A `CODE_REVIEW_PASS` is bound to `contract_revision + reviewed_deliverable_digest`; any later deliverable change makes it stale.

Read `resources/code-review.md` only for this phase.

## Frozen Test Plan

Only after current code review PASS does Astra freeze JSON conforming to `schemas/test-plan.schema.json`. It defines check type, argv/observation, cwd, required/applicability, allowed exit codes, evidence types, timeout/max attempts and whitelist metrics (`eq/ge/le`). Natural-language expectations cannot replace mechanical criteria.

AGY cannot edit the frozen plan/digest, weaken thresholds, or relabel a failure N/A. Conditional N/A requires frozen objective applicability evidence; unknown is BLOCKED.

Read `resources/testing.md` for plan/result rules.

## Deterministic gates

The host must use `bash scripts/validate-run-state.sh` rather than infer phase/completion from prose.

Before `TEST`, the validator re-reads disk and current Git state and requires current Contract, PASS review/digest, frozen plan/digest, stopped writer and safe dispatch state.

Before `COMPLETE`, it additionally verifies complete/unique check coverage, attempt identity, actual execution/observation evidence, evidence hashes, expected exit codes, frozen applicability, measured metrics, no open findings/blockers, settled dispatch, stopped writer and test before/after/current deliverable digest equality. Only success atomically writes `phase=COMPLETE`.

If a formal test causes a deliverable fix, persist failure, stop worker, invalidate review/plan/results, perform bounded AGY repair, then return to Astra review and a fresh plan. Default: a changed deliverable reruns all applicable required formal checks.

## Recovery

Run State lives under Git-private storage, is versioned, and uses lock + optimistic `state_version` + atomic replace for cooperating local processes. BLOCKED stores reason/source phase/resume action. Recovery revalidates repository/worktree, baseline, Contract, plan and worker; never guess a session or replay unknown side effects.

Older Run State without required v2 evidence must be rebuilt/revalidated for the current phase, never silently promoted to PASS.

## Progressive disclosure

Load only what the current stage needs:

- `resources/development-contract.md`
- `resources/run-state.md`
- `resources/agy-execution.md`
- `resources/code-review.md`
- `resources/testing.md`

Historical 3.x/4.0 role descriptions may remain as clearly marked migration history, but active execution may not depend on removed roles.
