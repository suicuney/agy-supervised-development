# Final Acceptance Record

Use after Luna verification. This is not another workflow phase.

```text
FINAL ACCEPTANCE

task_id: <task-id>
contract: <contract-id>@<revision>
final_code_state_digest: <digest>

changed_behavior
- <summary>

key_files
- <path>

verification
- <check>: PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE

rework_count: <n>
escalations: <none | summary>
contract_patches: <none | revision summary>
worker_stopped: yes/no
baseline_user_changes_preserved: yes/no

final_status: ACCEPTED | NOT_ACCEPTED
```

Only use `ACCEPTED` when the Contract, project rules, full task delta and current evidence all support it. Documentation changes are performed when the Contract or repository rules require them; there is no mandatory legacy closeout ceremony.
