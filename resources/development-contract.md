# Development Contract

The Development Contract is the stable handoff from architect to supervisor and AGY.

It replaces the default requirement for a detailed supervisor-owned executable plan.

## Required Shape

```yaml
goal: <what outcome the user wants>
problem: <current gap or reason for change>
expected_behavior:
  - <observable behavior>
constraints:
  - <important boundary>
architecture_intent:
  - <only decisions that must remain stable>
definition_of_done:
  - <observable completion condition>
agy_authority:
  - inspect relevant repository state
  - choose ordinary implementation details
  - modify in-scope files
  - run relevant tests
  - repair failures caused by this task
  - self-review before completion
supervisor_authority:
  - inspect Git evidence
  - request bounded rework
  - run targeted verification
  - reject incomplete delivery
escalate_if:
  - architecture conflict
  - material requirement ambiguity
  - material scope expansion
  - repeated core failure
  - one-way or destructive decision
out_of_scope:
  - <explicit exclusions when useful>
```

Fields may be omitted when genuinely unnecessary. Do not add boilerplate merely to fill the schema.

## Contract Quality

The contract should be:

- compact enough to pass between models cheaply
- specific enough for independent completion judgment
- free of unnecessary repository transcription
- stable across normal implementation choices

## CONTRACT FROZEN

Freeze the contract once contract-level ambiguity is resolved.

`CONTRACT FROZEN` means:

```text
WHAT / WHY / BOUNDARY / DONE are stable.
```

It does not mean:

```text
all implementation steps are predetermined.
```

AGY may adapt `HOW` as repository evidence is discovered, provided the frozen contract remains satisfied.

## Contract Patch

Only the architect or user may materially patch a frozen contract.

A patch must identify:

```text
reason
changed field(s)
new boundary / behavior
effect on prior work
```

Luna may request an escalation but must not silently perform a material Contract Patch itself.
