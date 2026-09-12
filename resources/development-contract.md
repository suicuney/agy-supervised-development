# Development Contract

The Contract is Astra's compact handoff to AGY. It freezes outcomes and boundaries, not implementation choreography or the later formal Test Plan.

The machine-readable runtime source is a JSON document validated by `schemas/development-contract.schema.json`; `templates/development-contract.json` is the starter shape.

## Default shape

```json
{
  "contract_id": "task-x",
  "revision": 1,
  "goal": "desired outcome",
  "behavior": ["observable result"],
  "acceptance_scenarios": ["observable acceptance scenario"],
  "counterexamples": ["important behavior that must not occur"],
  "constraints": ["important boundary"],
  "diagnostics": [],
  "done": ["final completion condition"],
  "escalate_if": []
}
```

`contract_id` and `revision` are metadata, not planning ceremony. Keep scenarios behavioral; do not pre-write a file-by-file implementation or the final command-level test plan.

## Implementation diagnostics

Astra may pre-authorize a minimal diagnostic when it materially shortens feedback:

```json
{"kind":"minimal_reproduction","scope":"reproduce the reported parser error only"}
```

Allowed kinds are `minimal_reproduction`, `targeted_test`, `typecheck`, `compile_feedback`, and `other`. Diagnostics are optional, bounded to their declared scope, recorded in Run State with `formal_acceptance=false`, and can never satisfy final completion. Project rules such as mandatory TDD remain binding; record the rule interaction rather than silently overriding it.

## Rules

- Keep the Contract small enough to pass between Astra and AGY cheaply.
- Do not transcribe the repository.
- Do not prescribe ordinary file/class/line-level implementation steps.
- AGY owns normal `HOW` inside the Contract.
- Applicable repository rules such as `AGENTS.md` remain binding; reference them instead of duplicating them.
- Formal test commands, applicability and thresholds are frozen only after current code receives Astra `CODE_REVIEW_PASS`.

## Patch

AGY may surface the need for a patch but may not make a material Contract change itself. Only Astra acting as architect, or the user, may issue a material patch.

A patch must increment `revision`, identify `actor = architect | user`, list changed fields and reason, and state which review/test evidence became stale. Record it in Run State. Do not ask the user again for a decision they already authorized.
