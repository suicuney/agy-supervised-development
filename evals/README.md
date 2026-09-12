# AGY Supervised Development Evals

`scenarios.json` defines semantic regression scenarios for the 4.1 workflow. They are **not** executable proof by themselves.

Evidence classes stay separate:

- `SCENARIOS_DEFINED_NOT_EXECUTED`: semantic scenarios only.
- `scripts/test-snapshot-behavior.py`, `scripts/run-completion-behavior-test.py`, document-role fixtures and Herdr mocks: deterministic/static/mock evidence when actually run.
- `FLOW_VERIFIED`: only a real disposable Codex/Astra → Herdr/AGY implement → Astra code review → frozen plan → Herdr/AGY formal test → deterministic completion run.

Current scenarios cover diagnostic-vs-formal evidence, recoverable baselines, special paths/symlinks/binary/mode changes, deliverable vs Git ownership identity, fail-closed capture, structured plan/results, objective applicability, attempt isolation, stale evidence, mechanical completion rejection paths, blocked/recovery/dispatch safety, and migration-note versus active-role detection.

Do not convert a scenario definition, grep assertion, schema fixture or mock into a real multi-agent/runtime pass claim.
