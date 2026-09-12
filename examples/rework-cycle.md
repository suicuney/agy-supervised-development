# Example: Astra Code Review and Test Rework

Astra reviews the implementation and finds `CR1`: a required consumer update implied by Contract/repository rules is missing. AGY receives only the bounded finding in `IMPLEMENT_REWORK`, completes the repair and stops; any Contract-preauthorized diagnostic remains non-formal evidence.

Astra then reviews the complete current **deliverable digest** again. Two consecutive no-progress rounds stop blind rework and classify the real decision/blocker rather than looping indefinitely.

Only after the final deliverable receives `CODE_REVIEW_PASS` does Astra freeze the structured Test Plan.

If formal TEST later fails because of a code/deliverable defect:

```text
persist failed attempt
→ confirm worker STOPPED
→ validate-run-state invalidate
→ TEST_REWORK / AGY complete bounded repair
→ AGY STOP
→ Astra full code review
→ fresh frozen plan
→ formal test again
```

Environment/auth/dependency failures become BLOCKED rather than code churn. `SEND_UNKNOWN` is investigated and never blindly resent.
