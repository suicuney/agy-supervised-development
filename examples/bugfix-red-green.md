# Example: Deterministic Bugfix in 4.1

Astra Contract records the reported observable failure, success scenario, counterexample, and may pre-authorize the **minimal original reproduction** as a diagnostic.

AGY may run that reproduction during IMPLEMENT only to understand/confirm the defect; its result is recorded with `formal_acceptance=false`. AGY implements the root-cause fix and stops without running the frozen formal acceptance plan.

Astra code review inspects the complete repaired deliverable and repository propagation obligations. After `CODE_REVIEW_PASS`, Astra freezes the formal plan, typically including the original reproduction and regression/project gates as required checks.

AGY runs those checks through Herdr with separate attempts/evidence. The deterministic completion gate verifies the current deliverable, exact frozen commands/exit codes/metrics and evidence hashes.

If formal testing exposes another code defect, save the failure first, stop the worker, run `validate-run-state invalidate`, perform one bounded AGY repair, then return to Astra review and a fresh plan. Diagnostic RED/GREEN or AGY prose alone never completes the task.
