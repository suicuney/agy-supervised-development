# Frozen Test Plan

```yaml
test_plan_id: <task-id>-tests-r1
plan_revision: 1
contract_revision: <n>
reviewed_code_state_digest: <digest>
checks:
  - id: T1
    method: <command or inspection method>
    cwd: <working directory>
    required: true
    expected: <measurable pass condition>
metrics:
  - id: M1
    condition: <aggregate measurable condition>
```

Rules:
- Created by Astra only after `CODE_REVIEW_PASS`.
- Includes applicable repository-required quality gates.
- AGY executes but may not remove required checks, lower thresholds, or redefine PASS.
- `NOT_APPLICABLE` for a required check requires an objective condition already compatible with the frozen plan.
- Any later production/task-code change makes this plan stale; return to Astra code review, then refresh/freeze a new plan revision.
