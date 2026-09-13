# Astra Code Review

Astra reviews the complete current deliverable after AGY stops writing. This phase is code-only: no formal test execution.

Inputs: current Contract + `contract_digest`, project rules, baseline/snapshot policy, complete task delta and current `deliverable_digest`. Review includes implementation, tests/fixtures/goldens/config/lockfiles/generated sources and necessary propagation.

A PASS is recorded only through `validate-run-state review-pass`, binding Contract revision+digest and current deliverable digest. Any later deliverable change makes the review stale. Review findings return to Herdr-managed AGY in `IMPLEMENT_REWORK`.
