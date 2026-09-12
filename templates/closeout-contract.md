# Final Completion Record

Use after AGY finishes the frozen Test Plan. This is a record, not another review phase.

```text
FINAL COMPLETION

task_id: <task-id>
contract: <contract-id>@<revision>
final_code_state_digest: <digest>
code_review_result: PASS
code_review_digest: <digest>
test_plan: <id>@<revision>

required_checks
- <check-id>: PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE

acceptance_metrics
- <metric-id>: <measured value> / <required condition> / PASS|FAIL

code_changed_after_review: yes/no
worker_stopped: yes/no
baseline_user_changes_preserved: yes/no

final_status: TASK_COMPLETE | NOT_COMPLETE
```

`TASK_COMPLETE` is mechanical: the current deliverable still matches the code-review/test-plan binding, every required check actually passed, every frozen metric is satisfied, and no required blocker/not-run remains. Astra does not perform another test-review step.
