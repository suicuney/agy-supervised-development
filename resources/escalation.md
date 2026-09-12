# Escalation Policy

Escalation is an exception path from Luna back to the architect role.

## Escalate When

### 1. Architecture conflict
Repository facts show that a frozen architecture intent cannot be satisfied safely or coherently.

### 2. Material requirement ambiguity
Two or more plausible behaviors would materially change the user-visible or externally observable outcome.

### 3. Scope explosion
The discovered implementation surface is materially larger or riskier than the frozen contract implied.

### 4. Repeated core failure
Two bounded rework cycles fail on the same core issue and additional local iteration is unlikely to resolve the underlying decision.

### 5. One-way decision
The next step requires destructive migration, irreversible deletion, production mutation, breaking public API, security boundary change, or another decision requiring stronger authority.

## Do Not Escalate For

- lint / format problems
- ordinary test failures
- local implementation bugs
- naming decisions
- file placement
- normal framework/API discovery
- implementation preferences that remain inside the frozen contract

## Escalation Packet

Keep the packet compact:

```yaml
contract_ref: <current frozen contract>
trigger: <one escalation category>
evidence:
  - <minimal decisive facts>
question: <decision architect must resolve>
work_already_done:
  - <brief relevant state>
```

Do not resend full repository context or Luna's entire history.

## Resolution

The architect returns one of:

```text
NO_PATCH       # existing contract still stands; supervisor continues
CONTRACT_PATCH # frozen contract materially changes
USER_DECISION_REQUIRED
BLOCKED
```

For `CONTRACT_PATCH`, record the changed fields and return control to Luna. AGY then continues from current repository state unless the patch explicitly invalidates prior work.
