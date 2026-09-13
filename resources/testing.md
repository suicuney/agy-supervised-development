# Frozen Testing and Completion

Only after Astra code-review PASS does Astra freeze the authoritative JSON Test Plan. The plan binds task/Contract digest, snapshot-policy digest, reviewed deliverable digest, check definitions, scenario coverage, business applicability, environment prerequisites, evidence types, max attempts and typed metrics.

Business applicability is separate from environment readiness. Proven business non-applicability may yield `NOT_APPLICABLE`; missing browser/auth/dependency is `BLOCKED` and requires another attempt after recovery.

Command checks run via `run-frozen-check.sh`; observations must use structured machine-readable sources. Natural-language logs alone never prove PASS. Structured report fields are re-parsed during completion and compared with the receipt. `eq` is type-strict (`true != 1`); `ge/le` require finite numeric values. Optional metric failure is reported but does not block COMPLETE.

`validate-run-state complete` re-verifies Contract/policy/plan/results identities, baseline integrity, every historical receipt, latest-attempt semantics, current deliverable digest, required checks, scenario coverage and required metrics. Only that command writes `COMPLETE`. The cooperative lock coordinates workflow CLIs but is not OS-level filesystem isolation.
