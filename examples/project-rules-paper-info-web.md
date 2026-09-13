# Example: Repository Rules

This is an adaptation example, not a global default. Read the target repository's current `AGENTS.md` before freezing the Contract.

For a repository such as `paper-info-web`, Astra keeps API/schema/generated-client propagation rules in the code review and places applicable project-required pnpm/Maven/docker-compose commands in the frozen Test Plan. Commands that do not apply to the changed surface are omitted before freeze and the plan notes why.

AGY executes the frozen commands through Herdr. Missing browser/auth/dependency is BLOCKED, not an automatic exemption. The completion gate checks command identity, exit codes, evidence hashes and current deliverable binding; it does not reinterpret the target project's business assertions.
