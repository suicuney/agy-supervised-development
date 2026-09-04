# AGY Execution — Herdr Only

AGY Supervised Development 3.3 has one runtime path:

```text
Codex Governance
  ↓ Execution Unit / Rework Contract
Herdr
  ↓
Antigravity CLI (AGY)
  ↓
Repository
  ↓
Git + Codex Review / Verify
```

> **Herdr is infrastructure, not governance.**

Herdr owns agent launch, identity, terminal lifecycle, interaction and native session restore. Codex owns scope, decisions, Review, Verification and Acceptance.

---

## 1. One-time setup

Herdr and AGY must already be installed. Install the official Antigravity integration explicitly once for the user account:

```bash
herdr integration install antigravity-cli
```

The integration writes Antigravity user-level hook configuration, so task execution must never install it silently.

The Antigravity integration reports native conversation identity for restore. Herdr still derives `working` / `idle` / `blocked` / `done` from Antigravity's terminal screen detection.

---

## 2. Per-task preflight

Before AGY BUILD:

```bash
scripts/check-herdr.sh
```

Required:

```text
herdr executable available
agy executable available
Herdr server reachable
Herdr supports --kind agy
antigravity-cli integration installed/current enough to be usable
```

If any requirement fails:

```text
AGY BUILD → BLOCKED
```

Do not silently switch runtimes. Do not invoke AGY directly.

---

## 3. Workspace binding

Create a task-owned workspace directly on the repository root:

```bash
repo_root="$(git rev-parse --show-toplevel)"
created="$(herdr workspace create \
  --cwd "$repo_root" \
  --label "$task_label" \
  --no-focus)"
```

Herdr returns JSON. Use the IDs it returns; never guess topology IDs:

```bash
workspace_id="$(printf '%s' "$created" | jq -r '.result.workspace.workspace_id')"
pane_id="$(printf '%s' "$created" | jq -r '.result.root_pane.pane_id')"
```

Validate both values are non-empty before launch.

This workspace is runtime state, not task truth. Git remains repository truth.

---

## 4. Agent identity and launch

Create one stable task-local agent name that matches:

```text
[a-z][a-z0-9_-]{0,31}
```

Example:

```text
agy-orders-4f2a
```

Use the same name for the task's Build and Rework chain.

Start AGY only through Herdr:

```bash
herdr agent start "$agy_agent" \
  --kind agy \
  --pane "$pane_id"
```

`agent start` requires an existing available shell pane and returns only after Herdr recognizes the expected AGY process as ready for interaction.

---

## 5. Prompt and wait

Send an Execution Unit atomically through the Agent API:

```bash
herdr agent prompt "$agy_agent" "$execution_unit" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout "$timeout_ms"
```

Use milliseconds for Herdr timeouts. Pick a bounded value appropriate to task size; do not encode one global timeout for every repository.

Important semantic boundary:

```text
Herdr settled state
!=
Execution Unit PASS
```

Herdr wait is lifecycle-oriented, not a turn-level delivery proof. Always read current output and Git afterward.

---

## 6. Read before interaction

When state is `blocked`, inspect first:

```bash
herdr agent read "$agy_agent" \
  --source recent-unwrapped \
  --lines 120
```

Then classify:

```text
Within frozen scope + already authorized + reversible
→ minimum safe key interaction may proceed

One-way / product / architecture decision
→ USER_DECISION_REQUIRED

Out of scope / unsafe
→ refuse or keep BLOCKED
```

When a terminal key is genuinely required:

```bash
herdr agent send-keys "$agy_agent" enter
```

Never blindly approve based only on `blocked` status.

---

## 7. Worker report and Git handoff

After `idle` or `done`, collect enough recent output to index the worker's claims:

```bash
herdr agent read "$agy_agent" \
  --source recent-unwrapped \
  --lines 160
```

Worker report should include:

```text
Changed behavior
Changed files
Tests/checks actually run
Tests/checks blocked or not run
Permission/tool failures
Known limitations
Unresolved items
```

Then Codex independently inspects:

```bash
git status --short
git diff --stat
git diff --check
git diff
```

Herdr state and AGY self-report are runtime evidence only.

---

## 8. Rework

After a Review finding, reuse the same live Herdr-managed AGY worker:

```bash
herdr agent prompt "$agy_agent" "$rework_contract" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout "$timeout_ms"
```

Conversation history helps context, but the Rework Contract remains explicit:

```text
Issue
Evidence
Expected
Required Change
Re-run
Scope Reminder
Forbidden Actions
```

After rework, perform the full Three-Axis Review again.

---

## 9. Session restore

With the official `antigravity-cli` integration installed, Antigravity reports its conversation on `PreInvocation`. Herdr can then restore that pane after a Herdr server restart using the native AGY conversation reference.

The workflow itself never executes a direct resume command.

If the exact session reference is missing, invalid, stale, or cannot be restored:

```text
Do not guess another conversation.
```

Preserve current repository evidence. Start a replacement Herdr-managed AGY only when safe, supplying:

```text
frozen Spec / current Execution Unit
repo + branch + baseline summary
current diff
review findings
verification state
```

---

## 10. Workspace ownership and close

The workflow may close only a workspace it created for the current task, and only after the work no longer needs the live AGY session:

```bash
herdr workspace close "$workspace_id"
```

Do not close, rename, reuse as task-owned, or otherwise mutate unrelated user Herdr workspaces.

---

## 11. Runtime / Governance boundary

Herdr answers:

```text
Where is the AGY worker?
What agent/session is in that pane?
Is it working / idle / blocked / done?
What is visible in recent output?
Can the native session be restored?
```

Codex answers:

```text
Is the implementation within scope?
Does it satisfy the Spec?
Is engineering quality acceptable?
Is propagation complete?
Did independent verification pass?
Can the task be accepted?
```

Therefore:

```text
Herdr done
→ CODEX REVIEWING
```

never:

```text
Herdr done
→ ACCEPTED
```
