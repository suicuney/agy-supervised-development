# Code Review Rework Finding

```text
CODE REVIEW FINDING

task_id: <task-id>
round: <n>
contract: <contract-id>@<revision>
finding_id: <stable-id>
category: IMPLEMENTATION_DEFECT | CONTRACT_AMBIGUITY | ENVIRONMENT_BLOCKER

contract_or_rule
- <clause or repository rule>

code_evidence
- <file/symbol/diff evidence>

why_it_matters
- <correctness/completeness/risk>

required_outcome
- <bounded code result>

progress_marker
- <what substantive progress means>
```

Rules:
- Astra authors code-review findings; AGY resolves implementation findings.
- Rework remains `IMPLEMENT_REWORK`; do not execute the formal Test Plan.
- AGY does not rewrite the Contract.
- Two consecutive no-progress rounds on the same finding stop blind rework and require classification/escalation.
- Environment blockers do not become repeated code changes.
- Do not resend an uncertain Herdr prompt.
