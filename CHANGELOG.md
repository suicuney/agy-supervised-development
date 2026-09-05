# Changelog

All notable changes to this Skill are documented here.

## [3.3.0-alpha.2] - 2026-09-05

### Changed

- Before the first Sol High browser Send, Codex now shows a concise **Chinese plan summary** with the task goal, key plan steps, and important risks instead of exposing only packet/file size metadata.
- The user confirms the **first Send once**. Later `REVISE` rounds continue automatically in the same verified Sol conversation after Codex applies `Adopt / Reject / Modify`; repeated per-round Send confirmation was removed.
- After Sol review converges, Codex now shows a concise **Chinese final execution plan** and key review adjustments, then records `PLAN FROZEN` and continues automatically without a second confirmation.
- Added semantic evals and documentation validators for pre-send Chinese plan visibility, single confirmation, automatic revise rounds, and final-plan visibility.
- Updated the paired `sol-high-plan-review` Skill contract so the browser-review layer follows the same interaction model.

## [3.3.0-alpha.1] - 2026-09-04

### Architecture

- Made **Herdr the sole AGY runtime**: `Codex Governance → Herdr → Antigravity CLI / AGY → Repository`.
- Removed the active direct AGY invocation adapter and removed the alternate terminal-runtime branch.
- Kept Herdr strictly below governance: Herdr owns launch, agent identity, interaction, lifecycle state and native session restore; Codex still owns plan, Review, Verification and Acceptance.
- Kept 3.3 single-writer and serial. Multi-agent/multi-worktree orchestration remains out of scope.

### Added

- `scripts/check-herdr.sh` preflight for Herdr, AGY, running Herdr server, `--kind agy` support and the Antigravity integration.
- Herdr-only execution contract in `resources/agy-execution.md` covering task-owned workspace creation, returned pane identity, stable task-local agent names, prompt/wait/read, blocked interaction and session restore.
- Deterministic Herdr runtime contract tests and semantic evals for preflight failure, returned pane identity, blocked read-before-interaction, lifecycle-vs-delivery boundaries and no-guess session recovery.

### Changed

- Bumped plugin, kernel, entrypoint and eval metadata to `3.3.0-alpha.1`.
- Reworked README and examples so every AGY Build/Rework path uses Herdr Agent APIs.
- Reworked failure modes around Herdr runtime evidence and Git/Codex delivery evidence.
- Strengthened structure/docs validation so active documentation cannot reintroduce the removed AGY runtime paths.

### Removed

- `scripts/agy-run.sh` from the active codebase.
- `resources/tty7-supervision.md` from the active codebase.
- Direct-vs-interactive runtime selection and fallback logic from the 3.3 workflow.

## [3.2.0-alpha.3] - 2026-09-04

### Changed

- Added a versioned Sol High dependency manifest, portable completeness checker, full-checkout recovery helper, and fixture coverage for missing, incomplete, invalid, and existing-destination states.
- Documented the proven AGY safeguards: command-level cwd verification after `init.cwd`, evidence-first handling of permission denials and terminal errors, same-conversation recovery, and Git-backed verification.
- Documented the minimal tty7 fallback and current-Chrome Sol High runbook, including login handoff, visible model/High checks, one-send state tracking, and no automatic retry from `UNKNOWN`.
- Expanded evals and deterministic documentation/readiness checks for these boundaries.

## [3.2.0-alpha.1] - 2026-09-02

### Added

- Codex Plugin packaging metadata: `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and `skills/agy-supervised-development/SKILL.md` as the pluginized entrypoint routing to the canonical root kernel.
- Thin AGY Adapter `scripts/agy-run.sh` standardizing repository binding, execution modes (`build` / `consult`), timeout, conversation resumption, and stream-json output without introducing custom harnesses or daemons.
- Review Convergence contract (`resources/review-convergence.md`) defining `BLOCKING` / `NON_BLOCKING` / `BACKLOG` triage and the `NO_BLOCKING_FINDINGS` checkpoint.
- Optional read-only AGY Consult workflow (`resources/agy-consult.md`) for advisory second opinions.
- Deterministic verification scripts: `scripts/validate-structure.sh`, `scripts/validate-docs.sh`, `scripts/validate-runtime.sh`, and full entrypoint `scripts/test-readiness.sh`.

### Preserved

- Canonical Workflow Kernel (`SKILL.md`, `resources/`, `templates/`) as the single source of truth for supervised development.
- Codex ownership of shaping, specification, Three-Axis Review, independent verification, knowledge closeout, and final acceptance.
- Core acceptance boundaries: `NO_BLOCKING_FINDINGS != ACCEPTED`, `REVIEW PASS != CODE_VERIFIED`, `CODE_VERIFIED != ACCEPTED`.
- AGY as the primary writer; `tty7` as the interactive fallback.

## [3.0.1] - 2026-08-22

### Architecture

- Simplified v3 from **custom Pi harness orchestration** to **Pi Native Harness composition**.
- Removed the default recommendation to create a separate `pi-supervised-harness` repository.
- Removed the default `pi-supervisor` companion CLI/daemon, custom Run Store, custom `run_id + operation_id`, and custom Evidence Bundle protocol.
- Made **Pi native CLI + JSON session** the default Codex → Pi integration boundary.
- Kept Pi RPC as an optional future enhancement for long-lived `steer/follow_up/abort/get_state`, not an MVP dependency.
- Kept Pi SDK as a reference/future embedding option rather than requiring a custom Node bridge.

### Added

- `resources/pi-interaction.md` as the active v3.0.1 runtime interaction contract.
- Native JSON session-header verification: save the real Pi session identity and require `session cwd == repo_root`.
- Explicit distinction between Pi core `--mode json|rpc` and workflow-extension `--modes plan|build|review|debug`.
- Recommended reuse of existing trusted workflow extensions such as `pi-agent-modes` instead of reimplementing mode/tool policy.
- Honest capability rule: if no trusted mode extension is loaded, report `mode_enforcement=unavailable/prompt-only` rather than pretending a Tool Guard exists.
- Pi Native session resume for Review → Rework and Knowledge Closeout.
- New evals for session cwd mismatch, wrong/stale session resume, missing extension false-enforcement, and read-only extension/runtime contradiction.

### Changed

- Skill version bumped to `3.0.1`.
- Main runtime changed from `Codex App → custom Pi Harness/Bridge → Pi` to **`Codex App → Pi Native CLI/JSON Session → Pi built-in Harness → Provider`**.
- Simplified Codex governance state to `BASELINED → PI_READY → optional PLANNING → IMPLEMENTING → REVIEWING → COMPLETENESS_REVIEW → VERIFYING → CODE_VERIFIED → CLOSEOUT → ACCEPTED`.
- Removed `HARNESS_PREFLIGHT / HARNESS_READY / OPERATION_SENT / EXECUTING / OPERATION_SETTLED` from the formal Codex governance state machine.
- Replaced custom operation settlement semantics with Pi-native turn boundary semantics: **`agent_end != PASS`**.
- Changed Rework to resume the same real Pi session using a full Evidence-driven Rework Contract.
- Changed Closeout to reuse an existing writable workflow mode such as `build` plus a strict Closeout Contract; no custom `closeout` mode is required.
- Changed Gate 8 to **Pi Session / Turn Evidence Integrity**.
- Changed Gate 12 to **Pi Runtime / Extension / Credential Hygiene**.
- Updated Failure Modes, Completeness, Provider Boundary, examples, and evals to remove assumptions about a custom Harness/Run Store/operation protocol.

### Preserved

- Codex App as the sole master Supervisor / Reviewer / Final Acceptance authority.
- Pi as the sole primary Writer/Worker in the default topology.
- Provider as intelligence-only and replaceable.
- Git baseline protection and repository state as source of truth.
- Evidence-driven Review → Rework → Re-review.
- Change Completeness / Blast Radius and unfinished-vs-different-ticket boundary.
- Explicit Unit / Integration / E2E Test Layer Decision.
- Deterministic bugfix RED → root-cause fix → GREEN → Codex independent re-run.
- Independent Codex Verification before `CODE_VERIFIED`.
- Mandatory Knowledge Impact Scan / Closeout before `ACCEPTED`.
- One-way-door / external-side-effect boundaries and no push/merge/release/deploy by default.
- Single-writer default and no automatic `yolo` fallback.

### Legacy

- `resources/pi-harness.md` is now an explicit **v3.0.0 legacy design note**, not an active runtime contract.
- `resources/tty7-supervision.md` remains an explicit **v2.1 legacy migration note**.

## [3.0.0] - 2026-08-22

### Architecture

- Kept **Codex App** as the sole master Supervisor / Reviewer / Final Acceptance authority.
- Replaced the v2.1 `Codex → tty7 → AGY CLI` worker path with **`Codex App → Pi Harness → Pi Provider`**.
- Defined **Pi Harness** as the sole primary Writer / Worker Runtime responsible for session, operation state, tool policy, scope guard and evidence.
- Defined **Provider** as intelligence-only. The default target can be an Antigravity Pi provider chosen and authenticated by the user, but the Skill no longer binds worker lifecycle to AGY CLI.
- Kept **repository state** as the final source of truth.

### Added

- `resources/pi-harness.md` defining the v3 worker harness contract, SDK/RPC integration, Run/Session/Operation identities, durable state, worker modes, defense-in-depth Tool Guard, Evidence Bundle, recovery and harness testing.
- `resources/provider-boundary.md` defining Provider/OAuth ownership, Antigravity third-party integration risk, credential redaction, provider health/failure classification and provider replaceability.
- Explicit Worker modes: `inspect`, `implement`, `rework`, `verify`, `closeout`.
- Three-layer Tool Guard: tool visibility + `tool_call` policy + per-operation system policy injection.
- Structured Evidence Bundle with run/operation/session identity, provider/model, repository evidence, tests, policy blocks, scope findings and unresolved items.
- New Gate 12 — Harness Policy & Credential Hygiene.
- v3 failure modes for provider auth, stale operation correlation, read-only blocking, provider failover and credential redaction.

### Changed

- Replaced tty7 workspace/pane + Turn Nonce identity with **`run_id + pi_session_id + operation_id`**.
- Replaced AGY turn states with `HARNESS_PREFLIGHT → HARNESS_READY → OPERATION_SENT → EXECUTING → OPERATION_SETTLED`.
- Changed worker completion semantics to `OPERATION_SETTLED != PASS`; Codex must still independently inspect Git.
- Moved runtime enforcement from prompt-heavy instructions into a programmable Pi Harness contract.
- Changed Provider auth handling so the user/Provider owns install/login/credentials; the Harness records only sanitized availability/health status.
- Updated Review, Completeness, RED→GREEN, Independent Verification and Knowledge Closeout to operate on Pi Worker output.
- Updated examples and Skill evals to the Pi Harness architecture.

### Removed from v3 mainline

- `agy` CLI capability detection and runtime requirement.
- tty7 workspace/pane lifecycle as a mandatory worker runtime.
- Launch Proof, `tty7 send/capture/wait`, AGY status hook fallback, Read Before Send and Turn Nonce.
- AGY conversation database/session resume requirements.
- AGY CLI-specific runtime documentation (`resources/agy-runtime.md`).

`resources/tty7-supervision.md` remains only as an explicit **legacy v2.1 migration note** and is not an active v3 runtime contract.

### Preserved

- Git baseline protection and respect for user-owned uncommitted changes.
- Task Contract and Scope Drift Guard.
- Repository state as the source of truth.
- Evidence-driven Review → Rework → Re-review.
- Change Completeness / Blast Radius Review and unfinished-vs-different-ticket boundary.
- Explicit Unit / Integration / E2E Test Layer Decision.
- Deterministic bugfix RED → root-cause fix → GREEN → Codex independent re-run.
- Independent Codex Verification before `CODE_VERIFIED`.
- Mandatory Knowledge Impact Scan / Closeout before `ACCEPTED`.
- One-way-door and external-side-effect boundaries.
- No push / merge / release / deploy by default.
- Single-writer default; v3.0 intentionally does not become a general multi-agent DAG orchestrator.

## [2.1.2] - 2026-08-22

### Added

- Change Completeness Contract distinguishing `unfinished` remainder from `different ticket` so completeness does not become scope expansion.
- Explicit `COMPLETENESS_REVIEW` Supervisor state between normal code Review and Independent Verification.
- `resources/completeness-regression.md` covering blast-radius evidence, RED→GREEN bugfix proof, Test Layer Decision, and one-way-door boundaries.
- Gate 3 — Change Propagation & Blast Radius, requiring review of both current diff and missing diff.
- Gate 7 — Tests, Test Layers & Regression Proof with explicit Unit / Integration / E2E applicability.
- Deterministic bugfix regression protocol: unfixed behavior RED → root-cause fix → same test GREEN → Codex independent re-run.
- `examples/bugfix-red-green.md` showing a complete supervised regression-proof flow.
- `evals/README.md` and `evals/scenarios.json` for behavioral regression tests of the Skill itself.

### Changed

- Upgraded Task Contract with `Completeness`, `Test Strategy`, and `Regression Proof` fields.
- Changed Review ordering to `Diff Review → Completeness Review → Verification → CODE_VERIFIED`.
- Changed `CODE_VERIFIED` requirements so tests being green is insufficient without blast-radius evidence and explicit test-layer decisions.
- Renumbered Review Gates after inserting the completeness gate: Knowledge & Documentation Alignment is Gate 13.
- Clarified that `user-skipped` E2E is a deliberate trade-off and must not be reported as `not-applicable`.
- Clarified that a post-fix-only green regression test is not equivalent to observed RED→GREEN proof.
- Extended Knowledge Closeout to consume final Completeness/Blast Radius evidence and send implementation defects back to code Review instead of hiding them with documentation edits.

### Preserved

- Codex as Supervisor / Reviewer / QA and sole final Acceptance authority.
- AGY as the sole primary writer in the v2.1 line.
- tty7 as the worker runtime in the v2.1 line.
- Current checkout + Git baseline protection.
- Knowledge Closeout after `CODE_VERIFIED`.
- No push / merge / deploy or destructive external actions by default.

## [2.1.1] - 2026-08-21

### Added

- Mandatory Knowledge Impact Scan after Codex Independent Verification and before final `ACCEPTED`.
- `CODE_VERIFIED → CLOSEOUT → CLOSEOUT_REVIEW → ACCEPTED` Supervisor lifecycle.
- `resources/closeout-governance.md` defining Lightweight / Full Closeout and knowledge-surface statuses.
- Knowledge surface statuses: `verified-current`, `changed-and-verified`, `pending`, `out-of-scope`, `not-applicable`.

### Changed

- Successful code review/tests/builds enter `CODE_VERIFIED` instead of immediately reaching `ACCEPTED`.
- Extended writer responsibility to affected README/docs/rules/Contract/config surfaces after implementation stabilizes.
- Kept Codex as the only actor allowed to decide final Acceptance.

## [2.1.0] - 2026-08-21

### Added

- tty7-native worker lifecycle with stable workspace/pane ownership.
- Launch Proof, native-status / capture-fallback, Turn Nonce, Read Before Send, Scope Drift Guard, Rework Budget and worker crash recovery.

### Preserved

- Codex as Supervisor / Reviewer / QA.
- AGY as primary implementation writer.
- Repository state as source of truth.
- Protection of pre-existing user changes.
- No push / merge / deploy by default.

## [2.0.0] - 2026-08-21

### Added

- Runtime capability detection, Workspace Binding Guard, Task Contract, failure modes and repository Review Gates.

### Changed

- Clarified Codex as Supervisor / Reviewer / QA and AGY as primary Implementer.
- Strengthened repository state as source of truth.
- Made blanket permission bypass explicitly non-default.

## [1.x]

Initial single-file supervised development workflow: Codex supervises and independently validates work implemented by AGY in an isolated tty7 pane.
