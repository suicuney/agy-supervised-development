# Astra Code Review Report

```text
CODE REVIEW REPORT

task_id: <task-id>
contract: <contract-id>@<revision>
reviewed_code_state_digest: <digest>

Task delta reviewed
- committed since baseline: yes/no + ref
- staged: yes/no
- unstaged: yes/no
- untracked contents: yes/no
- deletions/renames: yes/no
- relevant binary changes: yes/no/not-applicable
- baseline user changes preserved: yes/no

Code inspection
- contract fidelity: PASS | REWORK | BLOCKED
- correctness by inspection: PASS | REWORK | BLOCKED
- applicable repository rules: PASS | REWORK | BLOCKED
- completeness/propagation: PASS | REWORK | BLOCKED

Findings
- <finding-id / code evidence / required outcome / status>

Important
- tests/builds/quality gates executed by Astra in this phase: NONE

Outcome
- CODE_REVIEW_PASS | CODE_REVIEW_REWORK | BLOCKED
```

A pass is valid only for the recorded code-state digest. Any later production/task-code change makes it stale and requires another Astra code review.
