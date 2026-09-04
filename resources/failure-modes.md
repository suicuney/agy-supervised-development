# AGY Supervised Development 3.3 Failure Modes

This file covers the active Herdr-only runtime and the Codex governance boundaries around it.

> **Collect evidence first. Herdr state is runtime evidence. Git and Codex verification decide delivery.**

## 1. Herdr or AGY is unavailable

Run:

```bash
scripts/check-herdr.sh
```

If Herdr, AGY, the running Herdr server, AGY kind support, or the Antigravity integration is unavailable:

```text
→ BLOCKED
```

Do not silently start AGY outside Herdr and do not introduce another runtime path.

## 2. Antigravity integration missing or outdated

The integration is an explicit user-level setup step:

```bash
herdr integration install antigravity-cli
```

Task execution reports the missing prerequisite. It does not rewrite user-level hooks automatically.

## 3. Workspace created against the wrong repository

Use:

```text
herdr workspace create --cwd <repo_root>
```

and consume `.result.workspace.workspace_id` plus `.result.root_pane.pane_id` from the returned JSON.

If the workspace cwd or repository facts do not match the intended task, stop before writes and inspect for side effects.

## 4. Wrong or stale pane identity

Never guess pane IDs from UI order or old output. Use the ID returned by Herdr for the task-owned workspace.

If the expected pane no longer exists, do not send input elsewhere. Re-establish task-owned runtime state explicitly.

## 5. Agent name collision

Herdr agent names are unique among live agents. Generate one stable task-local name and reuse it for the Build/Rework chain.

If the name already belongs to another live agent, do not take it over. Choose a different task-local name.

## 6. `agent start` is not ready

If startup times out or returns not-ready/blocked:

1. inspect `herdr agent read` / pane state;
2. confirm the pane was an available shell pane;
3. resolve login or bounded interaction explicitly;
4. do not bypass Herdr by starting AGY separately.

## 7. AGY becomes blocked

Read before interacting:

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 120
```

Then distinguish:

```text
safe + in scope + already authorized → minimum interaction
one-way decision                  → user
out of scope / unsafe             → refuse / BLOCKED
```

A runtime permission prompt is not product authorization.

## 8. Herdr says `done` but Git does not satisfy the plan

`done` only means Herdr recognized a settled lifecycle state.

```text
Herdr done != REVIEW PASS
```

Read Git. If the frozen Execution Unit is not satisfied, create a bounded Rework finding.

## 9. Herdr wait returns for the wrong lifecycle transition

Wait conditions are not a unique turn correlation protocol. A lifecycle change may satisfy the wait without proving that the just-sent Execution Unit is complete.

Therefore always pair wait with:

```text
agent read
+ repository diff
+ Codex Review
```

Do not invent another turn-state machine unless a proven correctness gap requires it.

## 10. Session restore fails

Herdr owns native session restore. If the exact Antigravity session cannot be restored:

```text
Do not guess another conversation.
```

Preserve Git progress. If safe, start a replacement Herdr-managed AGY and explicitly re-supply frozen task context, current diff, findings and verification state.

## 11. Herdr server restarts after partial edits

A runtime restart does not imply no writes occurred.

1. inspect Git;
2. let Herdr restore the exact native session when available;
3. do not replay a possibly side-effecting Execution Unit automatically;
4. return to Review once the worker turn settles.

## 12. Worker reports tests passed but Codex has not verified

AGY self-report is an index only.

```text
worker tests green != CODE_VERIFIED
```

Codex independently runs the Verification Seam/Test Strategy after Three-Axis Review PASS.

## 13. User baseline is modified

Never clean the tree simply to make AGY execution easier. Compare task-introduced changes against the recorded baseline and preserve original user hunks.

## 14. Small task is over-orchestrated

3.3 still defaults to one primary writer and a serial flow. A localized task should remain:

```text
Compact Shape/Spec
→ one Execution Unit
→ one Herdr-managed AGY
→ Review
→ Verify
```

Do not turn Herdr into a multi-agent DAG merely because it can host many agents.

## 15. Open decision is guessed by AGY

Unresolved product/architecture semantics return to Shaping/User authority. Herdr being able to keep AGY running does not expand AGY decision authority.

## 16. Completeness is mistaken for scope expansion

If an omitted change is required for the current behavior to be complete, it is Completeness work. If not, keep it out of scope.

## 17. Verification fails after Review PASS

Create `V*` evidence and return through:

```text
REWORK_REQUIRED
→ same Herdr-managed AGY
→ full Three-Axis Review
→ CODEX VERIFY again
```

Do not patch a test and jump directly back to verification.

## 18. CODE_VERIFIED is treated as final completion

Knowledge Closeout still runs before `ACCEPTED`. A stale public contract, README, config description or runbook remains a closeout defect.

## 19. One-way action is treated as runtime approval

The following remain user-authority boundaries unless already explicitly authorized:

```text
destructive migration
breaking API
auth relaxation
money/billing
credential semantics
production mutation
irreversible delete
push/merge/release/deploy
```

## 20. User cancellation

Stop further runtime input, then inspect repository partial progress. Do not auto-rollback. Preserve Herdr/session identifiers when useful for safe recovery and report the actual state.

## Summary

```text
Herdr failure → preserve repository evidence
AGY runtime settled → Codex Review
Review failure → bounded Rework through same Herdr worker
Verification failure → Rework + full Review + Verify
Session loss → never guess another conversation
User-owned changes → never silently clean
```
