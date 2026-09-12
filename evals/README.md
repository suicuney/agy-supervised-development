# AGY Supervised Development Evals

`scenarios.json` defines semantic regression scenarios for the 4.1 workflow. They are **not** executable proof by themselves.

Current status:

- `SCENARIOS_DEFINED_NOT_EXECUTED`: scenarios exist but no semantic runner produced evidence.
- deterministic shell/JSON checks live under `scripts/` and may be reported only when actually run.
- a real Astra plan → Herdr/AGY implementation → Astra code review → Astra test plan → Herdr/AGY test run is required before reporting `FLOW_VERIFIED`.

The scenarios focus on phase separation, no formal testing during implementation, code-only Astra review, bounded review/rework, frozen metrics, no second Astra test-review, evidence invalidation after code changes, baseline protection, project rules, Herdr dispatch safety and recovery.

Do not convert the presence of a scenario, grep assertion, schema validation, or mock runtime test into a claim that the real workflow passed.
