# Optional Pi Specialist Path — v3.1

> **本文件不是 3.1 Primary Runtime Contract。**

3.1 主链：

```text
Codex App
  ↓
AGY official CLI
  ↓
Repository
```

Pi 只作为 optional specialist，在它确实带来额外价值时旁路使用，例如：

```text
research
second opinion
blast-radius analysis
architecture exploration
read-only codebase investigation
specialized Pi extension capability
```

---

## 1. 不要把 Pi 放回 AGY 前面

默认不采用：

```text
Codex App
  ↓
Pi + Codex model
  ↓
AGY CLI
```

原因：

- 多一个 LLM decision layer；
- Context 多次压缩；
- token/latency 增加；
- failure ownership 更难判断；
- 与 Codex App 的 Shaping/Review 职责重叠。

如果 Pi 只是负责“启动 AGY、传 prompt、拿结果”，则无需用一个 Agent 做 transport。

---

## 2. 合适的旁路结构

```text
                  Codex App
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      AGY CLI                  Pi
   Primary Writer       Optional Specialist
          │                     │
          └──────────┬──────────┘
                     ▼
                  Codex
              Final judgement
```

Pi 输出必须回到 Codex 作为辅助分析，不能直接改变 Spec/Execution Unit 或 Acceptance。

---

## 3. 适合 Pi 的任务

### Research

只读调查复杂 library/API/code pattern，给 Codex 提供事实。

### Blast Radius Analysis

对某个 symbol/contract 做独立传播面搜索，不写代码。

### Architecture Second Opinion

对已经 Shape 出来的备选方案做独立 critique。

### Specialized Extension

如果某个 Pi extension 提供明显独有能力，例如 code graph / LSP / research workflow，可按需调用。

---

## 4. 不适合 Pi 的任务

默认不要让 Pi：

- 重新解释用户需求；
- 再拆一次 Codex 已冻结的 Spec；
- 作为 AGY 的永久父 Agent；
- 再 Review 一次 AGY 后再让 Codex Review Pi；
- 通过第三方 Antigravity OAuth Provider 代替官方 AGY CLI 主链。

---

## 5. 如果调用 Pi

Pi 的工作最好是 narrow / read-only / independently useful：

```text
Question
Scope
Evidence expected
No-write expectation where applicable
Return to Codex
```

最终事实仍由 repository / primary docs / trusted external sources验证。

---

## 6. 与 3.0.1 的关系

3.0.1 曾把 Pi Native Harness 作为 Primary Worker Runtime。

3.1 改为 Workflow-First 后，这个位置已经被官方 AGY CLI Primary Implementer 取代。

因此 3.0.1 中以下内容都不再是 3.1 主链要求：

```text
Pi session as main worker identity
Pi --mode json as main execution boundary
pi-agent-modes as required workflow layer
Pi Provider as Antigravity transport
Pi resume for all Rework/Closeout
```

它们只有在未来某个 optional Pi specialist workflow 明确需要时才重新启用。
