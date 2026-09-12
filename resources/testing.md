# Test Plan and Metrics

Testing begins only after Astra records `CODE_REVIEW_PASS` for the current code-state digest.

## Astra freezes the test plan

Astra reads the final reviewed code, Development Contract, applicable project rules, and code-review findings, then writes a compact plan:

```yaml
test_plan_id: <id>
contract_revision: <n>
reviewed_code_state_digest: <digest>
checks:
  - id: T1
    method: <command or inspection>
    cwd: <working directory>
    required: true
    expected: <measurable pass condition>
metrics:
  - <aggregate acceptance metric>
```

Include all project-required gates applicable to the changed surface. "Cheapest decisive check first" controls ordering only; it does not authorize skipping required gates.

Astra does not execute the tests. Once frozen, AGY may not remove required checks, reduce thresholds, redefine PASS, or relabel failures as not applicable.

## AGY executes

AGY receives the frozen plan and executes it through Herdr. For every check report:

```text
check_id
method/command
cwd
exit_code if available
result = PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE
measured_values
summary
log/evidence reference
code_state_digest
```

A command that did not run cannot be PASS. `NOT_APPLICABLE` requires the reason already implied by the frozen plan or an objective condition; AGY cannot use it to waive a required test.

AGY self-report must preserve actual output/metrics. Do not fabricate token usage, timings, pass counts, coverage, or cost data.

## Completion rule

No second Astra test-review is required. Completion is mechanical against the frozen plan:

```text
all required checks = PASS
AND all frozen acceptance metrics satisfied
AND no required BLOCKED / NOT_RUN
AND tested code_state_digest still equals current deliverable
→ TASK COMPLETE
```

The root host may format the result for the user but must not reinterpret failed metrics as success.

## Test failure

If a test fails because of code behavior, AGY may diagnose and fix it within the existing Contract. The moment production/task code changes:

```text
prior CODE_REVIEW_PASS = STALE
prior affected test evidence = STALE
→ ASTRA CODE REVIEW
→ refreshed/frozen TEST PLAN
→ AGY TEST
```

If failure is purely environmental/auth/dependency and no code change can legitimately solve it, return `BLOCKED`; do not modify the Contract or code merely to make the environment green.

If only test artifacts/logging change without changing the reviewed deliverable, rerun only affected checks and retain still-valid evidence.
