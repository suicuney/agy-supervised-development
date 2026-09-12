# Worker Order Template

This is a bounded AGY round order, not a second plan or Spec.

```text
WORKER ORDER

task_id: <task-id>
round: <n>
contract: <contract-id>@<revision>
working_directory: <path>
run_state: <git-private run-state path>

Applicable repository rules
- <AGENTS.md path / exact rule reference>

Goal for this round
- <implement Contract or resolve one finding>

Current finding (optional)
- id: <finding-id>
- evidence: <current evidence>
- required outcome: <bounded result>

Authority
- inspect relevant repository state
- choose normal implementation HOW
- modify in-scope files
- run applicable tests/checks
- fix failures caused by this work
- self-review

Boundaries
- preserve baseline user changes
- no push/merge/deploy/destructive action unless already authorized
- do not silently change the Development Contract

Report
- task_id / round / contract revision
- changed behavior and files
- checks actually run + exit/result
- BLOCKED / NOT_RUN checks
- self-review and unresolved findings
```

Do not add Shape/Spec/Slice ceremony. If a material Contract decision is required, stop and return the evidence to the supervisor.
