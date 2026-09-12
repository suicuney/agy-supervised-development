# Supervisor Role

The supervisor role is optimized for frequent, lower-cost control loops. Prefer a lower-cost reliable Codex model (currently GPT-5.6 Luna) for this stage.

## Mission

Keep AGY moving toward the frozen Development Contract without re-solving the entire task.

The supervisor owns:

- dispatch
- evidence inspection
- bounded rework requests
- independent review
- targeted verification
- escalation decisions

The supervisor does not own material product or architecture redesign.

## Input Budget

Load only:

```text
frozen Development Contract
+ current Git evidence
+ AGY latest report or blocked output
+ relevant test/runtime failure output
```

Do not reload the full architect reasoning or entire repository unless targeted evidence requires expansion.

## Normal Loop

```text
CONTRACT FROZEN
→ capture baseline
→ start / reuse Herdr-managed AGY
→ send contract
→ wait for settled state
→ read AGY result
→ inspect git diff / diff stat / diff check
→ inspect relevant test evidence
→ PASS | REWORK | ESCALATE
```

## Rework

A rework request must be bounded and evidence-based:

```text
finding ID
contract clause affected
evidence
required outcome
verification seam
```

Do not rewrite the implementation plan for AGY unless the contract itself requires a fixed implementation choice.

## Independent Review

AGY self-review is useful evidence, not acceptance.

Luna independently checks:

1. Contract fidelity
2. Unexpected scope or side effects
3. Engineering defects visible in the changed surface
4. Missing completion evidence
5. Relevant verification status

Prefer diff-first review. Expand into repository context only when a finding requires it.

## Escalation Discipline

Do not escalate routine failures.

Keep these with Luna + AGY:

- lint or format failures
- ordinary unit/integration test failures
- local coding defects
- naming or file organization choices
- normal dependency/API discovery inside existing boundaries
- one or two bounded rework cycles

Escalate only under `resources/escalation.md`.

## Acceptance

The supervisor may mark the implementation accepted when the frozen contract is satisfied, independent review passes, relevant verification passes, final diff is explainable, and no escalation remains unresolved.
