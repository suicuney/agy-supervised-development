# AGY Supervised Development Evals

`scenarios.json` defines semantic regression scenarios for the 4.1 workflow. They are **not** executable proof by themselves.

Evidence classes stay separate:

- `SCENARIOS_DEFINED_NOT_EXECUTED`: semantic scenarios only.
- `scripts/test-readiness.sh`: structure/document/workflow checks when actually run; it does not execute command-result behavior tests. Document-role fixtures and Herdr mocks are separate scripts and are not run by this entry point.
- `FLOW_VERIFIED`: only a real disposable Codex/Astra → Herdr/AGY implement → Astra code review → frozen plan → Herdr/AGY formal test → deterministic completion run.

The case list in `scenarios.json` is the source of truth for coverage. Formal acceptance uses frozen command checks; runtime conditional exemptions and generic metric/observation evaluation are not part of the current workflow.

Do not convert a scenario definition, grep assertion, schema fixture or mock into a real multi-agent/runtime pass claim.
