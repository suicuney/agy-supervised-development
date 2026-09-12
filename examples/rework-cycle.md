# Example: Astra Code Review Rework

Astra reviews the implementation and finds `CR1`: a required consumer update implied by the Contract/repository rules is missing.

Round 1 sends only the bounded code-review finding to the same Herdr-managed AGY worker in `IMPLEMENT_REWORK` mode. AGY changes code but does not run the formal Test Plan.

Astra then reviews the complete current code state again. If `CR1` is still materially unresolved after two consecutive rounds without substantive progress, stop blind rework and classify the real cause: product/architecture decision, worker capability limit, or environment/tooling blocker.

Ordinary coding choices stay with AGY. Environment/auth/dependency problems become `BLOCKED`, not repeated coding prompts.

Only after the final code digest receives `CODE_REVIEW_PASS` does Astra freeze a Test Plan and metrics. If later testing causes code changes, this pass becomes stale and the workflow returns here.
