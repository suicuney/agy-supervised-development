# Real Flow Smoke Test

Use only on a disposable temporary Git repository when Codex supervisor spawning, the requested model/authentication, Herdr and AGY are actually available. Never run this smoke in a business repository.

## Task

Create a tiny repository with one source file and one deterministic test. Example behavior: change a pure function from returning `hello` to returning `hello-v4` and update/add the focused test.

## Evidence sequence

1. Root architect freezes a compact Contract and records baseline/Run State.
2. Root actually spawns an independent supervisor using `resources/codex-supervisor-handoff.md`.
3. Record requested model, spawn result, and any host/runtime model evidence. Never infer missing model metadata.
4. Supervisor starts AGY through Herdr, sends a task/round-tagged worker order, and records Herdr IDs actually returned.
5. AGY implements, runs the test and self-reviews.
6. Supervisor independently snapshots the code state, reads the full task delta, reruns the deterministic test, and binds the result to the final digest.
7. Confirm AGY stopped writing before `ACCEPTED`.
8. Close only Herdr resources created by this smoke and delete the disposable repository after evidence is recorded.

## Result

Record results with `templates/experiment-record.md`.

- `FLOW_VERIFIED` requires real child-supervisor + Herdr/AGY + independent verification evidence.
- If model selection/auth is unavailable, record the exact blocker and stop that portion; static/deterministic tests remain separate evidence.
- If usage/token data is unavailable, record `unavailable`; never estimate savings from model names.
