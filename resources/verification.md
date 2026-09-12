# Verification

AGY self-reviews. Luna independently verifies delivery.

## Evidence Order

```text
Contract
→ git status / diff --stat / diff --check / changed diff
→ targeted tests or runtime evidence
→ broader inspection only when a concrete risk requires it
```

AGY's report is supporting evidence, not proof by itself.

## Outcomes

- `PASS`: Contract satisfied and evidence sufficient.
- `REWORK`: implementation defect inside Contract.
- `ESCALATE`: Contract-level decision required.
- `BLOCKED`: required environment/auth/dependency unavailable.

Run the narrowest meaningful verification first. Broaden only when risk or failure justifies it.

Final report: changed behavior, key diff, verification result, rework/escalation if any, final repository state.
