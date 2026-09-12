---
name: agy-supervised-development
description: Delegate coding to AGY through Herdr. Use a strong model to freeze task intent, a cheaper model to supervise evidence, and escalate only when the contract must change.
version: 4.0.0-alpha.3
---

# AGY Supervised Development 4.0

> **Astra decides. Luna supervises. AGY builds. Git proves. Routing proves itself.**

## Flow

```text
USER
→ ASTRA: CONTRACT
→ LUNA: SUPERVISE
→ AGY: BUILD + TEST + SELF-REVIEW
→ LUNA: VERIFY
→ ACCEPT
```

Exception only:

```text
LUNA → ASTRA: PATCH CONTRACT → LUNA → AGY
```

## Roles

- **Astra / architect**: decide `WHAT / BOUNDARY / DONE`; use the strongest suitable reasoning model.
- **Luna / supervisor**: dispatch, inspect evidence, request bounded rework, verify; use a cheaper reliable model.
- **AGY / worker**: inspect the repo, decide normal `HOW`, implement, test, fix, self-review.
- **Herdr**: sole AGY runtime.
- **Git**: repository truth.

Model names are preferred bindings, not hard dependencies.

## Contract

Astra outputs one compact Development Contract:

```yaml
goal: <outcome>
behavior: [<observable result>]
constraints: [<important boundary>]
done: [<completion evidence>]
escalate_if: [<contract-level blocker>]
```

Add architecture intent or exclusions only when they materially constrain implementation. Do not write routine file-by-file implementation steps.

After `CONTRACT FROZEN`, Astra exits the normal path.

## Observable Handoff

A role/model handoff is valid only when the runtime exposes evidence for it. Do not trust prose such as "now using Luna" as proof.

Surface compact control events when the host supports them:

```text
CONTRACT_FROZEN
SUPERVISOR_STARTED  role=supervisor model=<runtime-reported-model>
AGY_STARTED         session=<runtime-reported-session>
REWORK              finding=<id>
ESCALATED           role=architect
VERIFY_PASS
ACCEPTED
```

Use runtime-provided model/session metadata when available. If the host cannot prove a requested model binding, report the role as active but the exact model as `UNVERIFIED`; never fabricate model identity.

## Supervision

Luna starts from the frozen Contract, not Astra's reasoning transcript. Prefer:

```text
Contract
+ git diff / status
+ AGY report
+ relevant test/runtime output
```

Luna may ask AGY to fix implementation defects. Luna must not silently change the Contract.

Escalate only when the Contract itself is no longer sufficient: material requirement ambiguity, architecture conflict, major scope/risk expansion, repeated core failure, or a one-way/destructive decision.

## Execution

Every AGY run goes through Herdr. AGY may inspect relevant files, choose implementation details, modify in-scope code, run relevant tests, fix failures caused by its work, and self-review.

`Herdr done != delivery accepted`.

Read `resources/agy-execution.md` only when executing AGY.

## Verification

Luna verifies the cheapest decisive evidence first:

```text
Contract → diff → targeted tests/runtime evidence → broader inspection only if needed
```

Accept only when the Contract is satisfied, relevant verification passes, the final diff is explainable, and no unresolved escalation remains.

## Progressive Disclosure

Load supporting docs only when needed:

- `resources/development-contract.md` — Contract details / patch semantics
- `resources/supervisor.md` — Luna loop / rework / escalation
- `resources/agy-execution.md` — Herdr runtime
- `resources/verification.md` — evidence / verification
- `resources/sol-plan-review.md` — optional guarded legacy review
- `resources/ego-browser-runbook.md` — only for browser work

Do not preload the whole workflow or repository.
