# Example: Small Feature in 4.1

User requests a reversible feature with clear behavior.

## 1. Astra contract

Astra reads the applicable repository rules and freezes a compact Contract. No file-by-file plan is required.

## 2. AGY implementation

AGY runs through Herdr in `IMPLEMENT` mode, chooses ordinary implementation details, changes the required code, self-reviews, and does **not** run the formal test plan or acceptance gates.

## 3. Astra code review

Astra inspects the complete task delta against the Contract and project rules. It does not execute tests.

If there is a code defect:

```text
CODE_REVIEW_REWORK → AGY IMPLEMENT_REWORK → ASTRA CODE REVIEW
```

When the current code digest receives `CODE_REVIEW_PASS`, continue.

## 4. Astra test plan

Astra freezes the required commands/checks and measurable metrics for the reviewed implementation, including applicable repository-required gates.

## 5. AGY test

AGY runs the frozen plan through Herdr and reports actual results. If all required checks and metrics pass on the same code digest, the task completes without another Astra test-review pass.

If AGY changes production code while fixing a failure, return to Astra code review before testing can become final.
