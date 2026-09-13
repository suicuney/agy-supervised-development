# Changelog

## Unreleased — 4.1 simplification

- Reduced the formal Test Plan to mandatory command checks plus the existing explicit no-check exception.
- Removed the generic runner/receipt layer, generic metrics, structured report parsing, automatic applicability/N/A branches, observation checks, and scenario-coverage IDs from the active runtime contract.
- Test Results now directly record AGY's actual command attempts: argv/cwd/time/exit/timeout/evidence hashes and before/after deliverable digests.
- Simplified Run State by removing runtime-unused diagnostic/patch history arrays while retaining Contract content binding, baseline protection, writer/dispatch safety, BLOCKED recovery, and atomic state writes.
- Consolidated rework findings into the code review report and retired redundant test-plan Markdown, experiment, closeout, and rework templates from the active workflow.
- Kept snapshot policy, recoverable untracked baselines, binary/symlink/executable identity, and deliverable-vs-ownership digests.


## [4.1.0-alpha.3] - 2026-09-13

### Validation policy refinement

- Removed Python behavior fixtures, `py_compile`, and Python-based role checking from the default readiness gate.
- Readiness now validates structure, machine-contract fields, active-role dependencies, entrypoint wiring, and workflow logic with Bash/jq.
- Python remains the runtime implementation for snapshot/runner/completion; runtime correctness is proved by real task execution/smoke evidence rather than Python test execution as a release gate.

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
- Added JSON structured-report metric extraction and re-parsing at completion; no generic natural-language log parser.
- Split business applicability from environment prerequisites and blocked manual observations from mechanical PASS.

### State machine
- Unified phase mutations under state-version + cooperative lock + atomic replace.
- Made COMPLETE terminal; TEST_REWORK requires invalidate side effects; BLOCKED resume returns only to original phase.
- Added controlled writer/dispatch/review/plan/finding/result binding commands and stable machine reason codes.
- Completion re-verifies baseline, identity objects, all attempt receipts and current repository state before writing COMPLETE.

### Tests
- Added real temporary-repository regression coverage for dirty baselines, tracked deletion, symlink/binary/mode/path identity, immutable snapshots, Contract mutation, runner receipts, N/A/environment separation, metrics, attempts, state transitions and optimistic concurrency.
- Retained Herdr mock readiness checks and active-role migration positive/negative tests.

## [4.1.0-alpha.2] - 2026-09-13

- Introduced structured Contract/Plan/results, deliverable vs ownership digests, Git-private run state, a first deterministic completion gate and implementation diagnostics. alpha.3 closes the evidence/identity/state gaps found in the alpha.2 re-review.

## [4.1.0-alpha.1] - 2026-09-13

- Replaced the prior Luna-supervisor topology with Astra plan → AGY implement → Astra code review → Astra test plan → AGY test.

## 4.0 and earlier

See Git history. Historical Luna/Sol/3.x flows are not active defaults in 4.1.
