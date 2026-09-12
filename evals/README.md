# AGY Supervised Development Evals

`scenarios.json` defines semantic regression scenarios for the 4.0 workflow. They are **not** executable proof by themselves.

Current status values:

- `SCENARIOS_DEFINED_NOT_EXECUTED`: scenarios are specified but no semantic runner produced evidence.
- deterministic shell/JSON checks live under `scripts/` and may be reported separately when actually run.
- a real Codex supervisor → Herdr/AGY smoke test is required before reporting `FLOW_VERIFIED`.

The scenarios focus on behavior that static slogan checks cannot prove: honest model handoff, preservation of user changes, complete Git delta review, project-rule gates, evidence invalidation, bounded rework, duplicate-dispatch safety, recovery, and Contract patch authority.

Do not convert the presence of a scenario, a grep assertion, or a mock runtime test into a claim that the real multi-model flow passed.
