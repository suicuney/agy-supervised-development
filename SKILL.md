---
name: agy-supervised-development
description: Contract-first supervised coding with Astra for decisions, Luna for evidence-driven supervision, and AGY through Herdr for implementation.
version: 4.0.0-alpha.4
---

# AGY Supervised Development 4.0

> **Astra decides. Luna supervises. AGY builds. Git proves. Routing proves itself.**

## Flow

```text
USER
→ ASTRA: CONTRACT
→ LUNA: SUPERVISE
→ AGY: BUILD + TEST + SELF-REVIEW   # Herdr only
→ LUNA: VERIFY
→ ACCEPT
```

Exception only:

```text
LUNA → ASTRA: CONTRACT PATCH → LUNA → AGY
```

## Contract

Astra freezes only `WHAT / BOUNDARY / DONE`:

```yaml
goal: <outcome>
behavior: [<observable result>]
constraints: [<important boundary>]
done: [<completion evidence>]
escalate_if: [<contract-level blocker>]
```

AGY owns normal implementation `HOW`. Do not require file-level plans by default.

## Runtime

- Every AGY execution goes through Herdr.
- Herdr lifecycle state is runtime evidence, never acceptance.
- AGY self-review is evidence, never independent acceptance.
- Load project `AGENTS.md` and explicitly referenced constraints before implementation and verification.
- Preserve existing user changes. Do not auto-stash, clean, reset, overwrite, push, merge, deploy, or perform irreversible operations without authority.

## Supervisor handoff

For Codex Multi-Agent V2, use the host's real `spawn_agent` capability when exposed. Prefer a fresh minimal-context supervisor (`fork_turns: "none"`) so the supervisor does not inherit Astra's full reasoning history and explicit model selection remains possible when the host exposes it.

Requested model, host-confirmed/runtime-reported model, and handoff status are separate facts. A prose claim is not evidence. If an independent supervisor was not actually spawned, do not claim a Luna handoff. If a supervisor exists but the exact model cannot be verified, record the model as unverified; use same-model supervision only when the user did not require Luna specifically.

Read `resources/codex-supervisor-handoff.md` only for the handoff stage.

## Run state and recovery

Keep the Development Contract small. Store execution state separately under the repository's Git-private path returned by:

```bash
git rev-parse --git-path "agy-supervised/runs/<task_id>/run-state.json"
```

Run State records baseline, supervisor evidence, Herdr identities, rounds, findings, verification evidence, and recovery status. It must not contain credentials or unrelated conversation history.

Read `resources/run-state.md` only when creating, resuming, or recovering a task.

## Baseline and isolation

Before AGY writes, capture branch/HEAD plus committed, staged, unstaged, untracked and deletion/rename state.

- Clean checkout + no concurrent writer: direct execution is allowed.
- Existing user changes, concurrent writers, or explicit isolation need: prefer a task worktree.
- If the task depends on uncommitted user changes, preserve/copy those prerequisites deliberately; never create a clean HEAD worktree and silently omit them.
- Herdr workspace is terminal/runtime isolation, not code isolation.

## Supervision

Luna receives the minimum useful context:

```text
Contract
+ applicable repository rules
+ baseline/run-state reference
+ AGY result
+ Git evidence
+ relevant test/runtime evidence
```

Loop:

```text
AGY execute → inspect → verify → PASS | REWORK | ESCALATE | BLOCKED
```

Two consecutive rounds without substantive progress on the same finding default to escalation. Environment/auth/dependency blockers do not enter infinite rework and do not justify silently changing the Contract.

## Verification

Use the cheapest decisive check first, but always run project-required gates that apply to the changed surface. Results are `PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE`; a command that did not execute cannot be PASS.

Bind each material verification result to the Contract revision and the actual code state, including uncommitted changes. If code changes invalidate evidence, rerun the affected verification before acceptance.

Final review covers committed task changes, staged changes, unstaged changes, untracked file contents, deletions/renames, and relevant binary changes. Separate task-introduced changes from baseline user changes.

## Progressive disclosure

Load only what the current stage needs:

- `resources/development-contract.md` — Contract + patch rules
- `resources/codex-supervisor-handoff.md` — real Codex supervisor handoff
- `resources/run-state.md` — state, recovery, worktree/baseline rules
- `resources/supervisor.md` — rework/escalation/wait boundaries
- `resources/agy-execution.md` — Herdr execution
- `resources/verification.md` — evidence and acceptance

Legacy 3.3 material is not part of the default execution path.
