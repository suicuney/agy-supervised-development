# Changelog

All notable changes to this Skill are documented here.

## [4.0.0-alpha.4] - 2026-09-12

### Architecture

- Kept the compact 4.0 role split: Astra owns `WHAT / BOUNDARY / DONE`, Luna supervises with evidence, AGY owns ordinary implementation `HOW`, and every AGY writer runs through Herdr.
- Replaced the remaining principle-only handoff with an executable Codex Multi-Agent V2 adapter. The workflow uses the host's real `spawn_agent` capability when exposed, prefers `fork_turns: "none"` for a minimal-context supervisor, and separates requested model, host/runtime model evidence, and handoff status.
- Added honest degraded behavior: a missing child is `NOT_SPAWNED`; an unverified requested model is `REQUESTED_UNVERIFIED`; same-model supervision is explicit and does not imply cost savings.
- Removed default 3.3 Sol/browser review, Shape/Spec/Slice, mandatory Three-Axis Review, and closeout ceremony from the active execution path. Historical 3.x details remain available in Git history and are summarized under `legacy/`.

### Execution and recovery

- Added Git-private per-task Run State under `git rev-parse --git-path "agy-supervised/runs/<task_id>/run-state.json"`.
- Added versioned Contract patches restricted to architect/user authority.
- Added supervisor/Herdr identity, round/finding, dispatch state, baseline evidence references, code-state digest, verification results, and recovery rules without expanding the user-facing Contract.
- Added duplicate-dispatch protection (`NOT_SENT | SENT | SEND_UNKNOWN | SETTLED`), bounded waits, read-first timeout/uncertainty handling, and no automatic resend from uncertain delivery.
- Added recovery rules that never guess another session or replay side-effect-unknown commands and only start a replacement worker after parallel-write risk is excluded.

### Baseline and verification

- Clarified that Herdr workspace is runtime/terminal state, not Git code isolation.
- Added direct-checkout vs task-worktree guidance while preserving dirty user baselines and forbidding automatic stash/reset/clean.
- Added `scripts/snapshot-code-state.sh` to capture HEAD/branch/status, committed delta from an optional baseline, staged/unstaged binary diffs, untracked content hashes, and a digest covering the actual uncommitted code state.
- Expanded independent review to cover committed task changes, staged changes, unstaged changes, untracked file contents, deletions/renames, and relevant binary changes while separating baseline user changes from task results.
- Bound material verification evidence to Contract revision, working directory, method/command, exit code, result, log reference, and code-state digest.
- Standardized verification states as `PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE`; a command that did not run cannot be reported as PASS.
- Added evidence invalidation when relevant code changes after verification and required the worker to stop writing before final acceptance.

### Repository rules and supervision

- Required applicable `AGENTS.md` and explicit repository constraints to enter supervisor context without copying the whole repository.
- Clarified that focused/cheap checks define verification order but cannot replace repository-required quality gates.
- Preserved completeness checks for required callers, consumers, contracts/schemas, generated artifacts, configuration, persistence, tests, and documentation without reviving a separate Three-Axis ritual.
- Added bounded rework: two consecutive no-progress rounds on the same finding default to escalation; environment/auth/dependency blockers do not enter infinite coding loops.

### Preflight and tests

- Made `scripts/check-herdr.sh` fail closed against Herdr's structured `status server --json`: explicit running state, numeric protocol and `compatible=true` are required; Antigravity integration must explicitly report `current` with a version.
- Made Herdr preflight output `HERDR_ENVIRONMENT_READY` only; it does not imply AGY authentication, task execution, model handoff, or end-to-end workflow verification.
- Added deterministic runtime/workflow checks for malformed/unknown Herdr state, null IDs, preservation of dirty baselines, staged/untracked digest changes, and honest Run State defaults.
- Replaced 3.3 semantic eval scenarios with 4.0 cases covering handoff honesty, baseline protection, full-delta review, required project gates, evidence invalidation, bounded rework, duplicate dispatch safety, recovery, incomplete acceptance, and Contract patch authority.
- Semantic scenarios are explicitly `SCENARIOS_DEFINED_NOT_EXECUTED` until a real semantic runner produces evidence.
- `scripts/test-readiness.sh` now reports separate meanings: `STATIC_VALID`, optional target-host `ENVIRONMENT_READY`, and `FLOW_VERIFIED=NOT_RUN` until a real Codex supervisor → Herdr/AGY smoke test succeeds.

### Added

- `resources/codex-supervisor-handoff.md`
- `resources/run-state.md`
- `schemas/run-state.schema.json`
- `templates/run-state.json`
- `templates/experiment-record.md`
- `scripts/snapshot-code-state.sh`
- `scripts/validate-workflow.sh`
- `legacy/README.md`

### Notes

- This 4.0 boundary intentionally compacts the changelog. Detailed 3.x history remains available from repository history before this version.

## [4.0.0-alpha.3] - 2026-09-12

- Added observable routing semantics: runtime evidence is required for role/model handoff claims; an unavailable exact model is reported honestly rather than fabricated.

## [4.0.0-alpha.2] - 2026-09-12

- Simplified the 4.0 kernel around a compact Development Contract, low-cost evidence supervision, AGY implementation autonomy, progressive disclosure, and exceptional architect escalation.

## [4.0.0-alpha.1] - 2026-09-12

- Introduced the 4.0 model-tiered direction: strong-model Contract decisions, cheaper routine supervision, AGY-owned implementation planning, Herdr-only execution, and Git-backed verification.

## Historical 3.x and earlier

See Git history before `4.0.0-alpha.4` for the complete 3.3, 3.2, 3.0, 2.x, and earlier changelog entries.
