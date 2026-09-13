# Astra Code Review Report

```text
CODE REVIEW REPORT

task_id: <task-id>
review_id: <review-id>
contract: <contract-id>@<revision>
reviewed_deliverable_digest: <digest>
baseline_snapshot: <ref>

Reviewed delta
- committed since baseline
- staged / unstaged
- untracked original contents
- delete / rename / mode / binary
- production + tests/fixtures/config/lock/generated artifacts
- required callers/consumers/schema/docs

Findings
- <id / code evidence / required outcome / status>

Astra test/build execution in this phase: NONE
Outcome: CODE_REVIEW_PASS | CODE_REVIEW_REWORK | BLOCKED
```

A PASS is valid only for the recorded Contract content and deliverable digest. Any later deliverable change makes it stale.
