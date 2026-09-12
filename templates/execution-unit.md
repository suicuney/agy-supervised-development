# AGY Implementation / Rework Order

```text
AGY WORKER ORDER

task_id: <task-id>
round: <n>
mode: IMPLEMENT | IMPLEMENT_REWORK | TEST_REWORK
contract: <contract-id>@<revision>
working_directory: <path>
run_state: <git-private path>

Applicable repository rules
- <AGENTS.md / exact constraints>

Goal / findings
- <implement Contract or complete bounded repair>

Authority
- inspect relevant repository state
- choose ordinary implementation HOW
- modify in-scope deliverable files required by Contract/project rules
- execute only Contract-preauthorized diagnostics during code work
- self-review the resulting deliverable

Diagnostics
- <kind/scope from frozen Contract, or none>
- record purpose/result with formal_acceptance=false

Formal testing boundary
- do not execute the frozen formal Test Plan while implementing/reworking
- diagnostic green is not completion evidence
- after bounded repair, STOP and return to Astra code review

Safety
- preserve baseline user changes
- no push/merge/deploy/destructive action unless authorized
- do not change Contract scope or frozen test thresholds
- if prior dispatch is SEND_UNKNOWN or worker is busy, investigate rather than resend/start another writer

Report
- changed behavior/files
- diagnostics actually run and purpose
- implementation decisions / risks / unresolved items
- worker stopped: yes/no
```
