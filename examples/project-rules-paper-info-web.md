# Example: Adapting to paper-info-web Repository Rules

This is an adaptation example, not a global default.

When supervising a task in `paper-info-web`, first read its applicable `AGENTS.md`. The current repository rules require, among other things:

- Java 21 Spring Boot modular monolith; do not introduce microservices.
- `contracts/openapi.yaml` is the sole authoritative public API contract.
- Public API changes update OpenAPI, generated clients, tests and the traceability matrix.
- React is embedded in the production executable JAR.
- `workers/browser-worker` is excluded from default build, CI and release.
- Applicable quality gates include pnpm lint/typecheck/test/build, Maven test/integration/package, and docker-compose config validation.

## Supervisor packet

Do not copy the whole repository. Pass the frozen Contract plus a reference/summary of these applicable rules and the baseline/Run State.

If a task changes a public API, missing generated client/test/traceability updates are implementation completeness defects, not automatic "scope expansion". Luna keeps them inside normal supervision because the project rules make them necessary for the frozen behavior.

If a task does not touch the Browser Worker, do not add it to default build/release verification just because it exists in the repository.

A focused test may run first for fast feedback, but it does not replace the applicable repository gates required by `AGENTS.md`.
