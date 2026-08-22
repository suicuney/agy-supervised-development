# AGY Supervised Development 3.0.1

一个以 **Codex App 为唯一主入口和最终 Supervisor、Pi 原生 Coding Harness 为唯一主要 Worker、Provider 为模型推理层** 的监督式开发 Skill。

> **Codex owns supervision. Pi owns execution. Provider supplies intelligence. Repository owns truth.**

名称继续保留 `AGY Supervised Development` 作为项目连续性；v3 主链路不再依赖 `agy` CLI 或 tty7。

---

## 3.0.1 架构

```text
User
  ↓
Codex App
Master Supervisor / Reviewer / Final Acceptance
  ↓ Task Contract / Rework Contract / Closeout Contract
Pi Native CLI / JSON Session
  ↓
Pi built-in Coding Harness
  ├─ native session persistence
  ├─ read / edit / write / bash / search tools
  ├─ existing trusted extensions (optional)
  └─ configured Provider
       ↓
  Antigravity / other Provider
  ↓
Repository Changes
  ↓
Codex Diff Review
  ↓
Completeness / Blast Radius Review
  ↓
Codex Independent Verification
  ↓
CODE_VERIFIED
  ↓
Knowledge Closeout
  ↓
ACCEPTED
```

### 核心收敛

3.0.0 曾考虑再开发：

```text
pi-supervised-harness
pi-supervisor CLI
custom Run Store
run_id + operation_id
custom Evidence Bundle
```

3.0.1 正式取消这些默认设计。

原因很简单：**Pi 本身已经是 Harness**，已有 session、agent loop、tools、JSON/RPC、extensions 和 Provider abstraction。我们只需要把成熟能力组合起来，不重复造轮子。

---

# 三层职责

### Codex App

负责：

- Requirement / Task Contract；
- Git baseline；
- Architecture decisions；
- Review / Rework direction；
- Completeness / Blast Radius；
- Test Layer Decision；
- Independent Verification；
- Knowledge Closeout Review；
- Final `ACCEPTED`。

### Pi Native Harness

负责：

- agent loop；
- persistent session；
- provider/model invocation；
- read/edit/write/bash/search tools；
- 实现、测试、返工、必要知识文件更新。

### Existing Extensions / Provider

- Mode/tool-policy 尽量复用成熟 Pi Extension；
- 默认参考 `pi-agent-modes` 的 `plan/build/review/debug`；
- Provider 只提供 intelligence；Antigravity 是目标 Provider 之一，不写死到 Skill 生命周期。

---

# Codex → Pi：直接走原生 JSON

默认 MVP 不需要 Adapter daemon。

新任务：

```bash
pi --mode json --name "agy:<task-name>" "<Task Contract>"
```

如果当前已安装、已验证 `pi-agent-modes`：

```bash
pi --mode json --modes build --name "agy:<task-name>" "<Task Contract>"
```

Pi JSON stream 的第一条 session header 提供真实 session identity 和 cwd。Codex 保存：

```text
pi_session_id
cwd
```

并验证：

```text
cwd == repo_root
```

返工继续同一 session：

```bash
pi --mode json --session <session> --modes debug "<Rework Contract>"
```

Closeout：

```bash
pi --mode json --session <session> --modes build "<Closeout Contract>"
```

详细见 `resources/pi-interaction.md`。

---

# 为什么不用自研 Harness

Pi 已经负责：

```text
Agent Loop
Session persistence
Compaction
Model / Provider
Tool execution
JSON events
RPC
Extensions
Abort / continue / resume
```

如果再开发一层：

```text
Codex
→ custom harness
→ Pi harness
```

反而又形成第二套 runtime state、第二套 failure model、第二套维护成本。

3.0.1 的原则是：

> **监督逻辑留在 Skill，执行逻辑留给 Pi，策略能力优先复用 Extension。**

---

# Existing Extension 策略

3.0.1 不把某个第三方 Extension 变成永久硬依赖，但默认优先参考成熟实现。

当前推荐映射：

| Skill Phase | `pi-agent-modes` | 写权限 |
|---|---|---|
| PLANNING | `plan` | read-only |
| IMPLEMENTING | `build` | writable |
| REWORKING | `debug` / `build` | writable |
| SECONDARY REVIEW | `review` | read-only |
| CLOSEOUT | `build` + Closeout Contract | writable, contract-limited |

注意：

```text
pi --mode json
```

里的 `--mode` 是 Pi core 输出模式；而：

```text
pi --modes build
```

是 `pi-agent-modes` 的 workflow mode。两者不是一回事。

如果没有可信 mode extension，Skill **不能宣称 read-only/tool guard 已程序化生效**。此时仍可运行 Pi，但权限保证下降，必须显式记录并依赖 Codex baseline/scope/repository Review。

监督模式不默认使用 `yolo`。

---

# Supervisor State 也被简化

3.0.0 的 runtime-oriented states：

```text
HARNESS_PREFLIGHT
HARNESS_READY
OPERATION_SENT
EXECUTING
OPERATION_SETTLED
```

不再作为 Codex 的正式持久治理状态。

3.0.1：

```text
INIT
→ BASELINED
→ PI_READY
→ PLANNING          optional
→ IMPLEMENTING
→ REVIEWING
→ COMPLETENESS_REVIEW
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

异常：

```text
REWORK_REQUIRED
BLOCKED
FAILED
CANCELLED
```

Pi 内部 `agent_start / tool_execution_* / agent_end` 由 Pi 自己管理。

关键语义仍然不变：

```text
Pi agent_end != PASS
PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
```

---

# 2.1.x 的核心资产全部保留

3.0.1 只删除 runtime 重复建设，没有削弱监督标准：

- Git baseline protection；
- repository state as source of truth；
- Task Contract；
- Scope Drift Guard；
- Evidence-driven Rework；
- Change Completeness / Blast Radius；
- explicit Unit / Integration / E2E；
- deterministic bugfix RED → GREEN；
- Codex Independent Verification；
- `CODE_VERIFIED != ACCEPTED`；
- Knowledge Impact Scan / Closeout；
- one-way-door / external-side-effect boundary；
- Skill behavior evals。

---

# Provider Boundary

目标仍然允许：

```text
Pi
 ↓ Google OAuth through a user-selected Provider
Antigravity
```

但：

- Skill 不绑定具体 Antigravity package；
- 不自动 `pi install`；
- 不自动 OAuth；
- 不读取 access/refresh token；
- 不把 credential 放进 prompt/log/repo；
- Provider auth/quota/transport failure 与代码失败分开；
- Provider/model failover 不静默发生。

第三方 Antigravity Provider 是非官方集成，启用前应审查当前实现的 source/README/license/risk note。

详细见 `resources/provider-boundary.md`。

---

# Completeness / Test / Closeout

这些规则不因 Runtime 简化而改变。

### Completeness

```text
Changed Symbol / Behavior
→ Direct Callers
→ Indirect Callers / Re-exports / Scripts
→ Types / Enums / Validation / Serialization
→ Schema / Migration / Existing Data
→ Sibling Flows / Jobs
→ Error / Empty / Permission / Retry / Fallback
→ Cache / Derived State / Stale IDs
→ Dead / Orphaned Old Path
→ Tests
→ Knowledge Impact
```

### Test Strategy

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

### Bugfix

```text
Regression Test
→ unfixed behavior RED
→ Fix Root Cause
→ same test GREEN
→ Codex Independent Re-run
```

### Closeout

每次开发都 Scan，但不是每次都修改文档：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

---

# 文件结构

```text
agy-supervised-development/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── resources/
│   ├── pi-interaction.md          # 3.0.1 active runtime interaction
│   ├── provider-boundary.md
│   ├── run-lifecycle.md
│   ├── failure-modes.md
│   ├── completeness-regression.md
│   ├── review-gates.md
│   ├── closeout-governance.md
│   ├── pi-harness.md              # legacy 3.0.0 design note
│   └── tty7-supervision.md        # legacy 2.1 note
├── examples/
└── evals/
```

---

# 版本演进

```text
v2
→ Codex 怎样监督 AGY

v2.1
→ Codex 怎样通过 tty7 可靠控制 AGY CLI

v2.1.1
→ Knowledge Closeout

v2.1.2
→ Completeness / Blast Radius / Test Layers / RED→GREEN / Evals

v3.0
→ 从 AGY CLI 切到 Pi Harness + Provider

v3.0.1
→ 取消自研 Harness/Bridge/Run Store；直接使用 Pi Native CLI/JSON/Session + Existing Extensions + Provider
```

最终形态：

> **Codex 决策，Pi 执行，Extension 约束，Provider 思考，Git 作证。**
