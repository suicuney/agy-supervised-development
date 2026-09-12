# Workflow Experiment Record

```text
experiment_id: <id>
date: <date>
host: <Codex host/version if available>
strong_model_participations: <count>
astra_plan_turns: <count|unavailable>
astra_code_review_turns: <count|unavailable>
astra_test_plan_turns: <count|unavailable>
agy_implementation_rounds: <count>
agy_test_rounds: <count>
usage_tokens: <actual value|unavailable>
usage_cost: <actual value|unavailable>
elapsed: <measured duration|unavailable>
code_review_rework_count: <n>
test_failure_count: <n>
acceptance_failures: <n>
missed_findings: <n|unknown>
flow_status: FLOW_VERIFIED | PARTIAL | BLOCKED | NOT_RUN
notes: <evidence refs and blockers>
```

Use only actual host/runtime usage and measured values. If unavailable, record `unavailable`; do not infer cost savings from the workflow shape.
