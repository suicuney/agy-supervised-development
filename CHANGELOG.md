# Changelog

All notable changes to this Skill are documented here.

## [2.0.0] - 2026-08-21

### Added

- Runtime capability detection via `agy --version` / `agy --help` before choosing AGY flags or modes.
- Workspace Binding Guard to prevent AGY persistent context from silently targeting a different repository.
- Task-complexity-based execution strategy for small changes, normal feature work, and plan-first large refactors.
- Structured Task Contract covering Goal, Scope, Context, Constraints, Acceptance Criteria, Verification, Forbidden Actions, and Report.
- `resources/agy-runtime.md` for version-aware AGY runtime knowledge.
- `resources/failure-modes.md` for startup, tty7, trust/auth/permission, workspace mismatch, false-done, scope drift, test failure, timeout, and external-side-effect handling.
- `resources/review-gates.md` for baseline, scope, architecture, correctness, error handling, testing, verification, diff hygiene, and external-side-effect gates.
- `examples/feature-development.md` showing a complete supervised feature workflow.
- README describing the Supervisor → Implementer → Review → Rework → Acceptance architecture.

### Changed

- Clarified Codex as Supervisor / Reviewer / QA and AGY as the primary Implementer.
- Strengthened repository state as the source of truth instead of AGY self-reported completion.
- Changed AGY startup from implicit CWD trust to explicit workspace verification/binding.
- Changed AGY CLI handling from hard-coded assumptions to runtime capability detection.
- Added evidence-based PASS / REWORK / BLOCKED review outcomes.
- Made blanket permission bypass explicitly non-default in supervised development.
- Made final acceptance depend on independent Codex verification and explainable final diff.

### Preserved

- tty7 pane isolation.
- Protection of pre-existing user changes.
- No push / merge / deploy by default.
- Iterative AGY rework driven by Codex review evidence.

## [1.x]

Initial single-file supervised development workflow: Codex supervises and independently validates work implemented by AGY in an isolated tty7 pane.
