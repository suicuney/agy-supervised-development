# Example: Adapting to paper-info-web Repository Rules

This is an adaptation example, not a global default. Read the repository's current applicable `AGENTS.md` before freezing the Contract.

Representative rules include Java 21 Spring Boot modular monolith boundaries, `contracts/openapi.yaml` as public API authority, synchronized generated clients/tests/traceability for public API changes, React packaged in the executable JAR, Browser Worker excluded from default build/release, and applicable pnpm/Maven/docker-compose gates.

## Contract / diagnostics

Astra records observable API/UI behavior and counterexamples. If fast feedback is useful it may pre-authorize a scoped compile/typecheck or focused reproduction; this diagnostic cannot satisfy formal acceptance.

## Code review

Astra checks the full deliverable propagation by inspection. For a public API change, missing OpenAPI/generated client/test/traceability updates are implementation completeness defects, not automatic scope expansion. Browser Worker is not pulled into default delivery when the repository rules say it is excluded.

## Formal Test Plan

After review PASS, Astra maps the affected surface and project-required gates into structured checks. A focused test may run first for feedback, but it cannot replace applicable required pnpm/Maven/docker-compose gates. Applicability is frozen objectively rather than chosen by AGY after seeing failures.

AGY executes the plan through Herdr; `validate-run-state complete` decides completion from current deliverable and evidence.
