# Supervisor Review Report

```text
REVIEW REPORT

task_id: <task-id>
contract: <contract-id>@<revision>
code_state_digest: <digest>

Contract status
- behavior: PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE
- done criteria: <summary>

Project rules
- applicable AGENTS.md / constraints: <refs>
- required gates: <results>

Task delta reviewed
- committed since baseline: yes/no + ref
- staged: yes/no
- unstaged: yes/no
- untracked contents: yes/no
- deletions/renames: yes/no
- binary changes: yes/no/not-applicable
- baseline user changes preserved: yes/no

Verification
- method/command: <...>
- cwd: <...>
- exit_code: <n|null>
- result: PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE
- log_ref: <...>
- evidence code_state_digest: <...>

Findings
- <id / category / evidence / status>

Worker
- confirmed stopped writing: yes/no
- AGY self-review: <supporting summary only>

Outcome
- PASS | REWORK | ESCALATE | BLOCKED
```

`PASS` is invalid when evidence is stale, project-required gates were skipped without a valid classification, the worker may still write, or any part of the task delta was not reviewed.
