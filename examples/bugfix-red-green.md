# Example: Deterministic Bugfix in 4.0

For a reproducible bug, keep the workflow small.

## Contract

```yaml
contract_id: bug-x
revision: 1
goal: Remove the reported defect without changing unrelated behavior.
behavior:
  - The original reproduction no longer fails.
constraints:
  - Preserve existing compatibility and applicable repository rules.
done:
  - Original reproduction is rerun after the fix.
  - Relevant regression test/check passes.
```

## Execution

The supervisor captures baseline and Run State, then sends AGY a worker order through Herdr containing the reproduction and Contract reference. AGY diagnoses, implements, tests and self-reviews.

## Independent verification

Luna reruns the original reproduction or equivalent decisive check independently and verifies project-required gates for the affected surface. A worker statement such as "fixed/tests pass" is not enough.

If the same finding receives two rework rounds without material progress, escalate rather than endlessly retrying.
