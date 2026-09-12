# Astra Code Review Report

```text
CODE REVIEW REPORT

task_id: <task-id>
review_id: <stable review id>
contract: <contract-id>@<revision>
reviewed_deliverable_digest: <digest>
baseline_snapshot: <ref>

Task delta reviewed
- committed since baseline: yes/no + ref
- staged / unstaged: yes/no
- untracked original contents: yes/no
- deletes / renames / mode / binary: yes/no
- production + test/assertion/fixture/golden/config/lockfile/generated changes: covered
- required caller/consumer/schema/docs propagation: covered
- baseline user changes preserved: yes/no

Code inspection
- Contract scenarios/counterexamples: PASS | REWORK | BLOCKED
- correctness by inspection: PASS | REWORK | BLOCKED
- repository rules: PASS | REWORK | BLOCKED
- completeness/propagation: PASS | REWORK | BLOCKED

Findings
- <id / concrete code evidence / required outcome / status>

Tests/builds/quality gates executed by Astra here: NONE

Outcome
- CODE_REVIEW_PASS | CODE_REVIEW_REWORK | BLOCKED
```

A PASS applies only to the recorded Contract revision + deliverable digest. Any later deliverable change makes it STALE.
