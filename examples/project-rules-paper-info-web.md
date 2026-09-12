# Example: Adapting to paper-info-web Repository Rules

This is an adaptation example, not a global default.

When working in `paper-info-web`, first read its applicable `AGENTS.md`. Current rules include:

- Java 21 Spring Boot modular monolith; do not introduce microservices.
- `contracts/openapi.yaml` is the sole authoritative public API contract.
- Public API changes update OpenAPI, generated clients, tests and the traceability matrix.
- React is embedded in the production executable JAR.
- `workers/browser-worker` is excluded from default build, CI and release.
- Applicable quality gates include pnpm lint/typecheck/test/build, Maven test/integration/package, and docker-compose config validation.

## How 4.1 applies them

Astra puts the relevant architecture/API boundaries into the Development Contract without copying the whole repository.

During **code review**, Astra checks code-level completeness against these rules. For example, if a public API changed, missing OpenAPI/generated-client/traceability changes are implementation defects, not automatic scope expansion.

After `CODE_REVIEW_PASS`, Astra includes the applicable repository-required quality gates in the frozen Test Plan. A focused check may be ordered first for fast feedback, but it does not replace required gates.

AGY then executes those frozen checks. If the task does not touch Browser Worker, it remains excluded from default build/release exactly as the repository rule says.
