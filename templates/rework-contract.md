# Rework Finding Template

Use one bounded finding per repair request when practical.

```text
REWORK FINDING

task_id: <task-id>
round: <n>
contract: <contract-id>@<revision>
finding_id: <stable-id>
category: IMPLEMENTATION_DEFECT | CONTRACT_AMBIGUITY | ENVIRONMENT_BLOCKER | SUPERVISOR_LIMIT

evidence
- <what proves the problem>

required_outcome
- <observable result needed>

verification_seam
- <focused check that can prove the repair>

progress_marker
- <what would count as substantive progress this round>
```

Rules:

- implementation defects stay with Luna + AGY;
- Luna does not rewrite the Contract;
- environment blockers do not become repeated coding rework;
- two consecutive no-progress rounds on the same finding default to escalation;
- do not resend an uncertain prior worker prompt.
