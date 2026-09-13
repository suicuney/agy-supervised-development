# Example: Bugfix

Astra records the reported failure, desired behavior and a key counterexample. It may authorize the minimal reproduction as a diagnostic with `formal_acceptance=false`.

AGY reproduces only as authorized, fixes the defect and stops. Astra reviews the full repaired deliverable. After review passes, Astra freezes the necessary regression/project test commands.

AGY executes those commands through Herdr and records the actual tool results. A diagnostic RED/GREEN result is never reused as formal acceptance.

If a formal test finds another code defect: preserve the failed result, stop the writer, invalidate review/test evidence, perform one bounded repair, then return to Astra review and a fresh Test Plan.
