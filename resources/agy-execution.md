# AGY Execution — Herdr Only

Every AGY implementation, rework and formal test execution goes through Herdr. Herdr runtime state never equals acceptance PASS.

## Implementation / rework

AGY receives the current Contract, applicable repository rules and bounded findings. It chooses ordinary implementation HOW.

During code work, AGY may run only diagnostics already authorized by the Contract or required by repository rules. Record them as `formal_acceptance=false`; they are feedback, not final evidence.

After implementation or rework, AGY stops writing and returns control to Astra code review.

## Formal TEST

After Astra freezes the command Test Plan, AGY executes the listed commands with its existing execution tools. The Skill does not provide a second generic runner.

For every attempt, AGY records the actual:

```text
check_id / attempt_id / attempt_number
argv / cwd
started_at / ended_at
exit_code / timed_out
raw log or artifact path + sha256
deliverable_digest_before / deliverable_digest_after
status = PASS | FAIL | BLOCKED
reason
```

Do not fabricate tool results. Keep every attempt; respect frozen `max_attempts`. Missing browser, credentials or dependencies are BLOCKED and do not authorize removal of a frozen command.

If TEST reveals a deliverable defect, preserve the failed record, stop the writer, invalidate the old review/plan/results, perform one bounded repair, stop again, and return to Astra code review.

## Dispatch safety

- Never resend `SEND_UNKNOWN` automatically.
- Never start a second writer while prior writer status is RUNNING or UNKNOWN.
- `idle/done` is lifecycle only.
- Preserve existing user changes; no automatic stash/reset/clean.
