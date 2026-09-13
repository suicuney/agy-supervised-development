# AGY Implementation / Rework Order

```text
AGY WORKER ORDER

task_id: <task-id>
round: <n>
mode: IMPLEMENT | IMPLEMENT_REWORK | TEST_REWORK
contract: <contract-id>@<revision>
working_directory: <path>

Goal / findings
- <implement Contract or resolve bounded finding>

Authority
- inspect relevant repository state
- choose ordinary implementation HOW
- modify in-scope deliverable files
- run only Contract-authorized diagnostics during code work

Boundaries
- diagnostics use formal_acceptance=false and never replace formal testing
- formal Test Plan commands run only in TEST
- after implementation/rework, STOP and return to Astra review
- preserve existing user changes
- no push/merge/deploy/destructive action unless authorized
- do not resend SEND_UNKNOWN or start a second writer while prior writer may still run

Report
- changed behavior/files
- diagnostics actually run, if any
- decisions / risks / unresolved items
- worker stopped: yes/no
```
