# Development Contract

The Contract is the compact handoff from Astra to Luna and AGY. It freezes outcomes and boundaries, not implementation choreography.

## Default shape

```yaml
contract_id: <stable task contract id>
revision: 1
goal: <desired outcome>
behavior:
  - <observable result>
constraints:
  - <important boundary>
done:
  - <evidence that proves completion>
escalate_if:
  - <contract-level blocker>
```

`contract_id` and `revision` are metadata, not planning ceremony. Only add fields such as `architecture_intent` or `out_of_scope` when they materially change what AGY may do.

## Rules

- Keep it small enough to pass between models cheaply.
- Do not transcribe the repository.
- Do not prescribe ordinary file/class/line-level implementation steps.
- AGY owns normal `HOW` inside the Contract.
- `CONTRACT FROZEN` means `WHAT / BOUNDARY / DONE` are stable for that revision.
- Applicable repository rules (for example `AGENTS.md`) remain binding even when not copied into the Contract; reference them instead of duplicating them.

## Patch

Luna may request a patch but may not make a material one itself. Only the architect or user may issue a material patch.

A patch must:

```text
increment revision
identify actor = architect | user
list changed fields
state reason
state whether prior verification assumptions were invalidated
```

Record the patch in Run State. Continue from current repository state unless the patch explicitly invalidates prior work. Do not ask the user again for a decision they already authorized.
