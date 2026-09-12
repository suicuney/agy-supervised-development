# Codex Supervisor Handoff

This is the preferred host path for 4.0: Astra remains the root architect; Codex Multi-Agent V2 spawns one independent supervisor; that supervisor drives Herdr-managed AGY and returns the delivery verdict.

## Capability check

Use only capabilities actually exposed by the current Codex host. Multi-Agent V2 currently exposes `spawn_agent`, `send_message`, `followup_task`, and `wait_agent` when collaboration tools are enabled. Do not invent hidden arguments.

Host capability references checked for this design:

- `openai/codex/codex-rs/core/src/tools/handlers/multi_agents_spec.rs` — `spawn_agent`, model override exposure, `send_message`, `followup_task`, `wait_agent`, and spawn output schemas.
- `openai/codex/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs` — `fork_turns` and model/reasoning inputs.

These are implementation references, not permission to assume a particular installed Codex build exposes every field. Inspect the current host tool schema at runtime.

For the supervisor spawn, inspect the exposed `spawn_agent` schema first:

- If `model` is exposed, request `gpt-5.6-luna` (or the user-required model).
- If `model` is not exposed, do not pretend the request was made. Spawn only if same-model supervision is allowed; otherwise report `BLOCKED_MODEL_SELECTION`.
- Use `fork_turns: "none"` when exposed/supported. A full-history fork inherits the parent model and defeats both minimal-context and explicit model override semantics.

Example call shape when those fields are exposed by the host:

```json
{
  "task_name": "agy_supervisor_<task_id>",
  "message": "<compact supervisor packet>",
  "fork_turns": "none",
  "model": "gpt-5.6-luna"
}
```

The compact packet contains only:

```text
Development Contract + revision
repo/worktree path
applicable AGENTS.md rules or exact references
run-state path
baseline reference
allowed authority / hard boundaries
```

Do not forward Astra's full reasoning transcript.

## Identity evidence

Record distinct facts:

```text
requested_model       # what spawn asked for; null if no model field was available
host_model_evidence   # host config/tool/UI/runtime metadata if actually exposed
model_status          # VERIFIED | REQUESTED_UNVERIFIED | UNAVAILABLE | SAME_MODEL
handoff_status        # SPAWNED | NOT_SPAWNED | UNKNOWN
```

A successful `spawn_agent` response proves a supervisor task was created. It does not by itself prove the exact child model when the response omits model metadata. Child self-description is not model proof. Never convert `REQUESTED_UNVERIFIED` into `VERIFIED`.

`UNVERIFIED` is not a substitute for a missing handoff: if no child was actually spawned, use `NOT_SPAWNED`.

## Control ownership

The supervisor owns the live delivery loop after spawn:

```text
read Contract + project rules
→ validate/capture baseline and Run State
→ start/reuse Herdr AGY
→ dispatch round
→ inspect result + Git
→ independently verify
→ PASS | REWORK | ESCALATE | BLOCKED
```

The root orchestrator waits for supervisor messages/final status and presents the final user result. Astra re-enters only for a Contract patch or user/product decision. The supervisor persists Run State and controls the Herdr task resources it created.

## Waiting and duplicate safety

Use bounded `wait_agent` calls so the root remains interruptible. A timeout is not failure and is not permission to respawn the supervisor. First inspect the existing agent status/message path.

For supervisor → AGY dispatch, follow `resources/agy-execution.md`: confirm the worker is not still processing the prior round; associate every prompt with `task_id` + `round`; distinguish `NOT_SENT`, `SENT`, and `SEND_UNKNOWN`; never auto-resend `SEND_UNKNOWN`.

## Supervisor loss / recovery

If the supervisor disappears:

1. Read Run State and current Git state.
2. Verify task id, repo/worktree, Contract revision and baseline still match.
3. Attempt host-supported resume/reuse only when an exact supervisor identity is available.
4. Never guess another session/thread.
5. If exact resume is impossible, start a replacement supervisor only after confirming the old supervisor/worker is stopped or cannot write concurrently.
6. The replacement receives only Contract + current Run State + current repository evidence + unresolved findings/verification state.

Do not replay commands with possible side effects merely because their result is missing.

## Degraded supervision

When model selection is unavailable but the user has not required Luna specifically, an independent supervisor may run on the inherited/same model. Record:

```text
model_status = SAME_MODEL
cost_optimization = NOT_VERIFIED
```

Do not claim lower-cost supervision. If the user explicitly requires Luna, model selection/verification failure is a blocker rather than a silent downgrade.
