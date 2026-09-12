# Workflow Experiment Record

```text
experiment_id: <id>
date: <date>
host: <Codex host/version if available>
strong_model_participations: <count>
supervisor_requested_model: <model|null>
supervisor_runtime_model_evidence: <value|unavailable>
usage_tokens: <actual value|unavailable>
usage_cost: <actual value|unavailable>
elapsed: <measured duration|unavailable>
rework_count: <n>
escalation_count: <n>
acceptance_failures: <n>
missed_findings: <n|unknown>
flow_status: FLOW_VERIFIED | PARTIAL | BLOCKED | NOT_RUN
notes: <evidence refs and blockers>
```

Do not infer cost savings from role names. If the host does not expose usage, record `unavailable`.
