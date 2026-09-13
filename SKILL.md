---
name: agy-supervised-development
description: Astra defines and reviews; Herdr-managed AGY implements and runs frozen test commands; the local gate checks completion records.
version: 4.1.0-alpha.3
---

# AGY Supervised Development 4.1

> Astra defines the outcome. AGY implements. Astra reviews code. Astra freezes the necessary test commands. AGY executes them. The local gate checks completion consistency.

## Active flow

```text
ASTRA: Contract / boundaries / observable acceptance
→ AGY via HERDR: IMPLEMENT
→ ASTRA: CODE REVIEW
   ├─ finding → AGY REWORK → stop → ASTRA CODE REVIEW
   └─ PASS
→ ASTRA: freeze necessary command Test Plan
→ AGY via HERDR: execute commands and record actual results
→ validate-run-state complete
```

Three exceptions remain:

- **Code defect** — bounded rework, stop writer, review again.
- **Deliverable changes during/after TEST** — prior review and formal evidence become stale; invalidate, repair, review and test again.
- **Environment unavailable** — `BLOCKED`; record reason and resume from the original phase after the blocker is resolved.

There is no default Luna supervisor, Sol plan review, second Astra test review, or file-level implementation ceremony.

## Contract and diagnostics

Astra freezes compact `WHAT / BOUNDARY / DONE` plus observable scenarios/counterexamples. AGY owns ordinary implementation `HOW`.

Astra may pre-authorize a minimal reproduction, targeted test, typecheck or compile feedback during implementation. Diagnostics are recorded as `formal_acceptance=false`; project TDD rules remain binding. Diagnostic success never satisfies the formal Test Plan.

## Code review

Astra reviews the complete deliverable delta after AGY stops writing. It does not execute tests in this phase. The PASS is bound to the current Contract digest and deliverable digest.

Review findings use `templates/review-report.md`; no separate rework contract is required.

## Formal Test Plan

After code review PASS, Astra freezes only the commands actually needed for acceptance. Every listed command is mandatory. An inapplicable check is omitted before freeze and explained in plan notes; AGY cannot remove a frozen command after seeing a failure.

Missing browser, credentials or dependencies is `BLOCKED`; it never removes a frozen command. Subjective/manual acceptance remains pending human confirmation and is not converted into command PASS.

A legitimate task with no executable checks may use the explicit hashed `no_checks_acceptance` exception. It cannot bypass a failed test or pending manual confirmation.

## Results and completion

AGY executes frozen commands through its existing tools under Herdr and records actual argv, cwd, time, exit code, evidence path/hash, attempt identity, and before/after deliverable digests. Retries are bounded; all attempts remain recorded and the latest attempt determines the current result.

The completion gate checks record/plan/current-state consistency. It does **not** prove every business behavior from log hashes and does not protect against a malicious same-permission writer.

## Safety and recovery

- Every AGY execution goes through Herdr; `idle/done` is lifecycle only.
- Preserve staged/unstaged/untracked user content; never auto-stash/reset/clean.
- Preserve baseline, deliverable digest, Git ownership information, binary/symlink/executable/untracked content protection.
- Do not guess lost sessions, resend `SEND_UNKNOWN`, or start a second writer while prior writer identity is uncertain.
- `COMPLETE` is terminal for the run. Start a new run if work must be reopened.
- Old incompatible Run State/Test Plan/Test Results are not auto-migrated to PASS; rebuild the current run evidence.

## Phase resources

Load only what the current phase needs:

- `resources/development-contract.md`
- `resources/run-state.md`
- `resources/agy-execution.md`
- `resources/code-review.md`
- `resources/testing.md`

Runtime JSON is authoritative. Markdown explains the protocol.
