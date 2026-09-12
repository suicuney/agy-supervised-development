# Example: Deterministic Bugfix in 4.1

For a reproducible bug, keep the workflow small.

## Contract

```yaml
contract_id: bug-x
revision: 1
goal: Remove the reported defect without changing unrelated behavior.
behavior:
  - The original reproduction no longer fails.
constraints:
  - Preserve compatibility and applicable repository rules.
done:
  - The frozen regression checks and required metrics pass.
```

## Implement

AGY runs through Herdr in `IMPLEMENT` mode. It may inspect the known reproduction as input evidence, diagnose and fix the code, but it does not execute the formal regression/test plan yet.

## Code review

Astra inspects the complete code delta and root-cause handling without running tests. Findings return to AGY as bounded implementation rework until `CODE_REVIEW_PASS`.

## Test plan and execution

Astra then freezes the original reproduction/regression check plus applicable repository gates as measurable test criteria. AGY executes them through Herdr and reports actual results.

If all required metrics pass on the reviewed code digest, complete. If AGY changes code after a failed test, return to Astra code review before testing becomes final.
