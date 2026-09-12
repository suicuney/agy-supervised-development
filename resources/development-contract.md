# Development Contract

The Contract is the compact handoff from Astra to Luna and AGY. It freezes outcomes and boundaries, not implementation choreography.

## Default Shape

```yaml
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

Only add fields such as `architecture_intent` or `out_of_scope` when they materially change what AGY may do.

## Rules

- Keep it small enough to pass between models cheaply.
- Do not transcribe the repository.
- Do not prescribe ordinary file/class/line-level implementation steps.
- AGY owns normal `HOW` inside the Contract.
- `CONTRACT FROZEN` means `WHAT / BOUNDARY / DONE` are stable.

## Patch

Luna may request a patch but may not make a material one itself. Astra or the user returns only the changed contract fields plus a short reason. Continue from current repository state unless the patch invalidates prior work.
