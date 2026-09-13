# Frozen Test Commands and Completion

Formal testing starts only after current deliverable content has `CODE_REVIEW_PASS`.

## Frozen plan

Runtime truth is `test-plan.json` validated by `schemas/test-plan.schema.json`. The plan contains only mandatory command checks. Each check freezes:

```text
id
cwd
argv
accepted exit codes
timeout
max attempts
optional exact input paths
```

All checks listed in the plan are required. If a check is not applicable, Astra omits it before freeze and explains the omission in `notes`. AGY cannot remove a frozen command after a failure.

Browser/auth/dependency absence is BLOCKED and never removes a frozen command. Subjective/manual acceptance remains pending human confirmation; it is not represented as a command PASS.

A genuine task with no executable checks may use `no_checks_acceptance` with a reason plus hashed evidence. It cannot bypass a failed test or pending manual confirmation.

## Result record

AGY uses its existing execution tools and writes actual command results to `test-results.json`. Each attempt records command identity, cwd, start/end time, exit code, timeout flag, raw evidence path/hash, before/after deliverable digests, status and reason.

The latest attempt decides the current result. Earlier failures remain recorded. Retry count cannot exceed the frozen `max_attempts`, and evidence paths cannot be reused across attempts.

## Completion gate

`validate-run-state complete` rechecks:

- current Contract digest and frozen snapshot policy digest;
- current Astra review and plan binding;
- current deliverable digest;
- complete plan check coverage by result attempts;
- exact argv/cwd, accepted exit code and timeout status;
- attempt ordering and retry limit;
- evidence file existence and SHA-256;
- stopped writer, settled dispatch and no open findings.

Every frozen command must have latest status PASS. A deliverable change invalidates old review and formal results.

The validator checks consistency of recorded execution facts. A log hash does not prove all business behavior was correct, and the workflow does not claim tamper-proof evidence against a same-permission actor.
