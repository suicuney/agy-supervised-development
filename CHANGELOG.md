# Changelog

All notable changes to this Skill are documented here.

## [2.1.0] - 2026-08-21

### Added

- tty7-native worker lifecycle based on stable workspace/pane ownership returned by `tty7 new --json`.
- Mandatory Launch Proof after the first send into a fresh tty7 pane to catch swallowed Enter during shell startup.
- Native-status / capture-fallback dual strategy so AGY supervision does not assume a tty7 `working/waiting/done` hook exists.
- Supervisor State Machine describing only states Codex can prove: baseline, worker allocation, turn sent/returned, review, verification, acceptance.
- Turn Nonce protocol (`TURN_COMPLETE:<nonce>`) for stale-output-resistant AGY turn boundaries when native status is unavailable.
- Read Before Send rule for every prompt, Enter, menu key, Escape, and interrupt sent to the AGY pane.
- `resources/tty7-supervision.md` for tty7 ownership, launch, status, observation, crash recovery, and cleanup.
- `resources/run-lifecycle.md` for Run Context, Supervisor State, Turn Nonce, Scope Drift, and Rework Budget.
- Scope Drift Guard based on task-introduced changes relative to the initial Git baseline.
- Three-cycle soft rework budget with mandatory root-cause reassessment before continuing beyond it.
- Worker crash recovery that preserves valid repository progress before replacement/resume decisions.
- tty7 ownership/cleanup checks in repository Review Gates.

### Changed

- Reframed tty7 as the worker runtime instead of treating pane capture as an ad-hoc transport.
- Changed task cleanup from closing only a pane to removing only the dedicated worker workspace when appropriate.
- Changed coding-agent liveness checks to prefer `tty7 agents` + pane evidence; `tty7 procs` is no longer treated as authoritative for AGY liveness.
- Changed AGY completion semantics: native `done` or `TURN_COMPLETE` means only “worker turn returned”; only Codex Independent Verification can reach `ACCEPTED`.
- Changed AGY hook handling from optional wording to an explicit runtime capability branch.
- Kept the current checkout as the default for a single AGY writer, with worktrees reserved for multi-writer or explicit isolation scenarios.
- Extended failure modes for missing AGY hooks, swallowed Enter, marker loss, long `UNKNOWN`, interrupted turns, and worker pane exit.

### Preserved

- Codex as Supervisor / Reviewer / QA.
- AGY as the primary implementation writer.
- Repository state as the source of truth.
- Protection of pre-existing user changes.
- No push / merge / deploy by default.
- Evidence-driven review and rework.

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
