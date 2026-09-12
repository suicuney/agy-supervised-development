# AGY Implementation Order

```text
AGY IMPLEMENTATION ORDER

task_id: <task-id>
round: <n>
mode: IMPLEMENT | IMPLEMENT_REWORK
contract: <contract-id>@<revision>
working_directory: <path>
run_state: <git-private path>

Applicable repository rules
- <AGENTS.md / exact constraints>

Goal
- <implement Contract or resolve bounded code-review findings>

Findings (optional)
- <finding-id>: <required code outcome>

Authority
- inspect relevant repository state
- choose ordinary implementation HOW
- modify in-scope code/config/docs required by the Contract
- self-review the resulting code/diff

Testing boundary
- IMPLEMENT ONLY
- do not execute the formal Test Plan
- do not run project acceptance/quality gates as completion evidence
- do not declare the task complete
- if a test-like command is required for diagnosis, report the need instead of silently converting this phase into TEST

Safety
- preserve baseline user changes
- no push/merge/deploy/destructive action unless already authorized
- do not silently change the Contract

Report
- task_id / round / contract revision
- changed behavior/files
- implementation decisions
- known risks/unresolved items
- formal_tests_run: none | <explicit diagnostic exception>
```
