# Legacy — Custom Pi Harness Design (v3.0.0 only)

> **AGY Supervised Development 3.0.1 不再使用本文件作为 active runtime contract。**

v3.0.0 曾考虑在 Pi 之上再开发一层：

```text
Codex App
  ↓
custom pi-supervised-harness / pi-supervisor
  ↓
Pi SDK / RPC
  ↓
Provider
```

并为此设计：

```text
custom run_id
custom operation_id
custom durable Run Store
custom Evidence Bundle
custom mode/tool-policy layer
custom bridge CLI
```

3.0.1 调研和架构收敛后，正式取消这套默认方案。

原因：**Pi 本身已经是 Coding Harness**，原生提供 session、agent loop、tools、JSON/RPC、extensions、Provider abstraction 和 resume。再造一层会形成第二套 runtime state/failure model，增加维护成本。

3.0.1 主链路改为：

```text
Codex App
  ↓ Task Contract
Pi Native CLI / JSON Session
  ↓
Pi built-in Harness
  ├─ native session
  ├─ built-in tools
  ├─ existing trusted extensions
  └─ Provider
```

Active specification 请读取：

- `pi-interaction.md`：Codex↔Pi 原生 CLI/JSON/session；
- `run-lifecycle.md`：简化后的 Codex governance states；
- `provider-boundary.md`：Provider/OAuth；
- `review-gates.md`：Pi session/runtime/extension evidence gates。

## 仍然保留的设计思想

v3.0.0 调研中这些结论仍有效：

- 不把模型自述当 delivery evidence；
- Provider 与 Harness 分离；
- irreversible action 保留 human/Codex authority；
- read-only/tool policy 应优先由可信 extension 程序化执行，而不是只靠 prompt；
- Pi 官方 plan-mode、`pi-agent-modes` 等已有实现应优先复用；
- Pi Extension policy 不是 OS security sandbox；
- 默认单 Writer，不引入大型 DAG/multi-agent orchestration。

## 何时才重新考虑自定义 Harness

只有未来真实使用证明 Pi Native CLI/RPC + existing extensions 无法满足稳定需求，例如：

- Codex App 必须长期持有一个 Pi process；
- 需要强一致的跨进程 transaction/effect journal；
- 需要 Pi 原生 session 无法表达的多 Writer orchestration；
- 需要统一管理多个非 Pi runtime。

即使出现，也优先新增**最薄 adapter**，而不是直接恢复 v3.0.0 的完整自研 Harness 方案。

本文件只作为 v3.0.0 → v3.0.1 的架构决策记录。
