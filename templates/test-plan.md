# Frozen Test Plan

The JSON file is authoritative. This Markdown is explanatory only.

Each check freezes: id/type/cwd/required, Contract scenario coverage, business applicability, environment prerequisites, evidence types, max attempts, and either argv + accepted exit codes + timeout + structured reports or a structured observation source.

Metrics use only `eq | ge | le`, a typed threshold, optional unit, and a structured report field. `eq` is type-strict; environment failure is BLOCKED rather than N/A. AGY executes the frozen plan but does not rewrite it.

Formal command execution uses `scripts/run-frozen-check.sh`; completion uses `scripts/validate-run-state.sh complete`. Any deliverable change invalidates prior review/plan/formal evidence.
