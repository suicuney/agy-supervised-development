# Legacy — tty7 Supervision (v2.1 only)

> **v3.0.1 主流程不使用本文件。**

AGY Supervised Development 已从：

```text
Codex → tty7 → AGY CLI
```

迁移为：

```text
Codex App
  ↓
Pi Native CLI / JSON Session
  ↓
Pi built-in Coding Harness
  ↓
Pi Provider
```

因此下列 v2.1 机制在 3.0.1 中不再是运行要求：

- tty7 workspace/pane ownership；
- Launch Proof；
- `tty7 send/capture/wait`；
- AGY status hook / capture fallback；
- Read Before Send；
- Turn Nonce；
- AGY conversation DB/resume；
- AGY TUI permission interaction。

3.0.1 同样不再要求 v3.0.0 曾考虑的：

- custom `pi-supervised-harness`；
- `pi-supervisor` CLI；
- custom Run Store；
- `run_id + operation_id`；
- custom Evidence Bundle。

Active runtime contract：

- `pi-interaction.md`：Codex↔Pi Native CLI/JSON/session；
- `run-lifecycle.md`：Codex governance states；
- `provider-boundary.md`：Provider/OAuth；
- `review-gates.md`：Pi session/runtime/extension evidence gates。

本文件仅用于说明 v2.1 → v3 的迁移，不得被 3.0.1 Skill 当成 active runtime contract。

如需旧 tty7 + AGY CLI 工作流，请使用 `codex/agy-supervised-v2.1` 分支。
