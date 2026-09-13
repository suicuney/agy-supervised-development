# Astra Code Review

Astra reviews after AGY stops writing. This stage is code/deliverable inspection only; Astra does not run tests or quality gates here.

Review the complete task delta against the Contract and repository rules, including committed/staged/unstaged/untracked content, deletions/renames, binary/mode changes, test/config/lock/generated artifacts, and required callers/consumers/schema/docs.

Outcomes:

```text
CODE_REVIEW_PASS
CODE_REVIEW_REWORK
BLOCKED
```

A finding needs only:

```text
finding id
Contract/rule
concrete code evidence
required outcome
status
```

Put findings in `templates/review-report.md`; there is no separate rework contract. AGY performs bounded rework and stops, then Astra reviews the complete deliverable again.

A PASS is bound to the current Contract digest and deliverable digest. Any later deliverable change—including tests, fixtures, configuration, lockfiles or generated source—makes the PASS stale.
