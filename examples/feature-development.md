# Example: Small Feature in 4.0

User asks for a reversible repository feature with clear behavior.

## Contract

Astra reads only the project rules and repository facts needed to settle behavior:

```yaml
contract_id: feature-x
revision: 1
goal: Add the requested observable behavior.
behavior:
  - Existing behavior remains compatible.
  - New behavior is reachable through the repository's normal public seam.
constraints:
  - Follow applicable AGENTS.md rules.
done:
  - Relevant focused tests pass.
  - Applicable repository-required gates pass or are correctly classified.
```

No file-by-file plan is required.

## Handoff

The root uses the real Codex supervisor spawn path. If Luna is requested but runtime model metadata is unavailable, record `REQUESTED_UNVERIFIED`; do not claim verified Luna identity.

The supervisor receives Contract + project rules + Run State/baseline reference, then independently starts AGY through Herdr.

## Build and verify

AGY decides normal implementation details, runs relevant checks, fixes its own defects and self-reviews. Luna then reviews the complete task delta (including untracked content), runs/collects independent applicable verification, and accepts only when evidence is bound to the final code-state digest.

If code changes after a passing check, only affected evidence is invalidated and rerun.
