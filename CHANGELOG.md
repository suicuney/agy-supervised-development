# Changelog

## [4.1.0-alpha.3] - 2026-09-13

### Validation policy refinement

- Removed Python behavior fixtures, `py_compile`, and Python-based role checking from the default readiness gate.
- Readiness now validates structure, machine-contract fields, active-role dependencies, entrypoint wiring, and workflow logic with Bash/jq.
- Python remains the runtime implementation for snapshot/runner/completion; runtime correctness is proved by real task/smoke evidence rather than Python test execution as a release gate.

### Deterministic identity
- Added one canonical JSON hashing rule and `contract_digest` binding across Run State, Astra review, Test Plan and results/receipts.
- Added stable acceptance-scenario/counterexample IDs and Test Plan coverage mapping.
- Added frozen snapshot policy digest for exact ignored inputs and sensitive-untracked authorization.

### Snapshot safety
- Reworked snapshot capture around immutable new output directories; existing outputs are rejected and existing parent permissions are not changed.
- Added canonical output boundary checks, tracked stable deletion support, exact symlink target/executable/binary identity, recoverable untracked archives, baseline artifact integrity verification and fail-closed submodule handling.
- Separated deliverable content digest from Git/index ownership digest so staging-only changes do not invalidate code review.

### Formal test evidence
- Added `run-frozen-check.sh` / `run_frozen_check.py` to execute frozen argv, timeout, cwd, stdout/stderr, before/after snapshots and per-attempt immutable receipts.
- Added `test-receipt.schema.json`; `test-results.json` is now an index of immutable receipt path/hash rather than worker-authored PASS/metrics.
- Added structured-report metric extraction and re-parsing at completion; no generic natural-language log parser.
- Split business applicability from environment prerequisites and blocked manual observations from mechanical PASS.

### State machine
- Unified phase mutations around state-version, cooperative lock and atomic replace.
- Made COMPLETE terminal; TEST_REWORK requires invalidate side effects; BLOCKED resume returns only to the original phase.
- Added controlled writer/dispatch/review/plan/finding/result binding commands and stable machine reason codes.

## [4.1.0-alpha.2] - 2026-09-13

- Introduced structured Contract/Plan/results, deliverable vs ownership digests, Git-private run state, a first deterministic completion gate and implementation diagnostics.

## [4.1.0-alpha.1] - 2026-09-13

- Replaced the prior Luna-supervisor topology with Astra plan → AGY implement → Astra code review → Astra test plan → AGY test.

## 4.0 and earlier

See Git history. Historical Luna/Sol/3.x flows are not active defaults in 4.1.
