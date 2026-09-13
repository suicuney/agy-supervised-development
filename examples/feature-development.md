# Example: Small Feature

Astra freezes a compact Contract with observable behavior and optional bounded diagnostics. AGY implements through Herdr and stops. Astra reviews the complete deliverable without running tests.

After `CODE_REVIEW_PASS`, Astra freezes only the commands needed for acceptance. Each command records cwd, argv, accepted exit codes, timeout and retry limit. Checks that are not applicable are simply not included; the plan notes why.

AGY runs the frozen commands through its existing execution tools and records actual argv/cwd, timestamps, exit code, raw evidence hashes and before/after deliverable digests. `validate-run-state complete` checks those records against the frozen plan and current deliverable.

If testing changes any deliverable file, the old review and test evidence become stale and the task returns to Astra review.
