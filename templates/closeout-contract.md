# Final Completion Record

This record is emitted/formatted **after** `bash scripts/validate-run-state.sh complete` succeeds. It is not another review phase and must not be authored to override a rejected validator decision.

```text
FINAL COMPLETION

task_id: <task-id>
contract: <contract-id>@<revision>
review_id: <review-id>
reviewed_deliverable_digest: <digest>
test_plan: <id>@<revision>
test_plan_digest: <sha256>
final_deliverable_digest: <digest>

required_checks
- <check-id>: latest attempt / applicability / result / evidence refs

acceptance_metrics
- <metric-id>: measured value / frozen condition / PASS|FAIL

writer_stopped: yes/no
dispatch_settled: yes/no
open_findings: <none|ids>
baseline_user_changes_preserved: yes/no

validator_decision: COMPLETE | REJECTED
```

Only a successful deterministic decision may persist `phase=COMPLETE`. Astra performs no second test review.
