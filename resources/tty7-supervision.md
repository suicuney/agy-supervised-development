# Legacy — tty7 Supervision (v2.1 only)

> **v3.0 主流程不使用本文件。**

AGY Supervised Development 3.0 已将 Worker Runtime 从：

```text
Codex → tty7 → AGY CLI
```

迁移为：

```text
Codex App → Pi Harness → Pi Provider
```

因此下列 v2.1 机制在 v3.0 中不再是运行要求：

- tty7 workspace/pane ownership；
- Launch Proof；
- `tty7 send/capture/wait`；
- AGY status hook / capture fallback；
- Read Before Send；
- Turn Nonce；
- AGY TUI permission interaction。

v3.0 的等价职责已经迁移到：

- `pi-harness.md`：Pi session/operation、mode、Tool Guard、Evidence Bundle；
- `run-lifecycle.md`：Run/Session/Operation 状态机；
- `provider-boundary.md`：Provider/OAuth 边界；
- `review-gates.md`：Harness Policy & Credential Hygiene Gate。

本文件仅保留为 v2.1 → v3.0 的历史迁移提示，**不得被 v3 Skill 当成 active runtime contract**。

如需使用旧的 tty7 + AGY CLI 工作流，请切回 `codex/agy-supervised-v2.1` 分支。
