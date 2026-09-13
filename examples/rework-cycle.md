# Example: Rework

If Astra finds a code defect, it records a bounded finding in the normal review report. AGY receives that finding in `IMPLEMENT_REWORK`, fixes it and stops. No separate rework contract is required.

If formal TEST later exposes a deliverable defect:

```text
save failed attempt
→ stop worker
→ validate-run-state invalidate
→ TEST_REWORK / AGY repair
→ stop worker
→ Astra code review
→ fresh frozen command plan
→ test again
```

Environment/auth/dependency failures use BLOCKED instead of code churn. `SEND_UNKNOWN` is investigated, never blindly resent.
