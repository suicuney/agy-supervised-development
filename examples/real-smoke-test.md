# Real Flow Smoke Test

Use only on a disposable temporary Git repository when Astra/Codex, Herdr and AGY are actually available. Never run this smoke in a business repository.

## Task

Create a tiny repository with one source file and one deterministic test. Example: change a pure function from returning `hello` to `hello-v41`.

## Evidence sequence

1. Astra freezes a compact Contract and records baseline/Run State.
2. AGY starts through Herdr in `IMPLEMENT` mode and changes the source without running the formal test.
3. Astra inspects the complete code delta only. If needed, send a bounded finding to AGY and repeat until `CODE_REVIEW_PASS`.
4. Record the reviewed code-state digest.
5. Astra freezes a Test Plan containing the deterministic test and measurable PASS condition.
6. AGY switches to `TEST` mode and executes the frozen check through Herdr.
7. Confirm the reported test result/metric is tied to the same reviewed code digest.
8. If test-stage code changes are required, verify the workflow returns to Astra code review before final testing.
9. If all required metrics pass, record `TASK COMPLETE`; no second Astra test-review is performed.
10. Close only Herdr resources created by this smoke and delete the disposable repository after evidence is recorded.

## Result

Record results with `templates/experiment-record.md`.

`FLOW_VERIFIED` requires real evidence for all four stages: Astra plan, AGY implementation, Astra code review/test-plan creation, and AGY test execution. Static/deterministic script checks are separate evidence.
