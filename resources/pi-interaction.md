# Pi Native Interaction Contract

AGY Supervised Development 3.0.1 不再要求自定义 `pi-supervisor`、Bridge、Run Store 或第二套 Harness。**Pi 本身就是 Worker Harness**；本文件只规定 Codex App 如何可靠地调用 Pi、获取真实 session identity、继续返工并解释 JSON/RPC evidence。

---

## 1. 默认拓扑

```text
Codex App
  ↓ Task / Rework / Closeout Contract
Pi CLI
  ↓
Pi Native Coding Harness
  ├─ Session
  ├─ Tools
  ├─ Existing Extensions
  └─ Provider
  ↓
Repository
```

默认集成路径：

```text
Pi JSON mode = MVP
Pi RPC mode  = optional advanced integration
Pi SDK       = reference / future embedding, not a 3.0.1 requirement
```

---

## 2. Preflight

不要靠文档版本猜当前机器能力。

```bash
command -v pi
pi --version
pi --help
```

确认：

```text
pi executable available
--mode json supported
--session supported
provider/model selection capability known
current project cwd known
installed workflow/policy extension status known
```

如果准备依赖 `pi-agent-modes`，还要确认其真实安装与当前 flags/modes；没有安装时不要发送 `--modes`，也不要宣称 read-only enforcement 已生效。

Provider/OAuth 缺失时进入 `BLOCKED`，默认不自动安装或登录。

---

## 3. 初次调用：JSON mode

默认调用：

```bash
cd "$repo_root"
pi --mode json --name "agy:<short-task-name>" "<Task Contract>"
```

若检测到 `pi-agent-modes` 且实现阶段选择 `build`：

```bash
cd "$repo_root"
pi --mode json --modes build --name "agy:<short-task-name>" "<Task Contract>"
```

Provider/model 只有在当前 Pi help/catalog 已证明参数与 ID 可用时才显式传入。

不要在 Skill 中 hard-code 快速变化的模型列表。

---

## 4. Session Header 是 runtime identity

Pi JSON mode 首行应包含 session header，典型字段：

```json
{
  "type": "session",
  "version": 3,
  "id": "<real-session-id>",
  "timestamp": "...",
  "cwd": "/path/to/repo"
}
```

Codex 保存：

```text
pi_session_id
pi_session_cwd
pi_session_file = optional, only if Pi exposes it
```

强制检查：

```text
pi_session_cwd == repo_root
```

不一致：

1. 停止把该输出作为当前任务 session；
2. 检查 repository 是否已发生修改；
3. 不回滚来源不明改动；
4. 在正确 cwd 新建/恢复正确 session。

不要自己生成、猜测或从旧日志拼接 session ID。

---

## 5. JSON Events 怎么解释

Pi JSON stream 可包含：

```text
session
agent_start
turn_start
message_start / message_update / message_end
tool_execution_start / update / end
turn_end
agent_end
```

Skill 不需要把每个 event 再映射成自己的持久状态机。

### `agent_end`

它表示本次 Pi agent invocation 已返回：

```text
agent_end == Pi turn returned
```

它不证明：

```text
Task Contract satisfied
Git diff correct
Completeness complete
Tests appropriate
Knowledge aligned
```

所以 `agent_end` 后固定回到 Codex repository Review。

### Process exit

正常 exit 与 `agent_end` 类似，只是 turn boundary evidence。

异常 exit：先检查 Git，再判断是否需要 resume/recovery；不要默认从头重做。

---

## 6. Skill Phase 与 `pi-agent-modes`

Skill phase 不等于 Pi core `--mode`。

```text
Pi core --mode json
= 输出/集成协议

pi-agent-modes --modes build
= workflow/tool-policy mode
```

推荐映射：

| Skill Phase | Mode | 说明 |
|---|---|---|
| PLANNING | `plan` | read-only exploration / plan |
| IMPLEMENTING | `build` | 实现写入 |
| REWORKING | `debug` | 定向 bug/rework；不合适时用 `build` |
| SECONDARY_READ | `review` | 只读分析，可选 |
| CLOSEOUT | `build` | 由 Closeout Contract 限制写入知识面 |

`ask` 可用于简单只读问答。

监督开发默认不使用 `yolo`。

### Extension 不可用

如果 `pi-agent-modes` 不存在：

- 可以继续使用 Pi Native Harness；
- 省略 `--modes`；
- Task Contract 仍写清 Scope/Forbidden Actions；
- 但必须报告 `mode_enforcement = unavailable/prompt-only`；
- 不把 prompt-only 约束描述成程序化 Tool Guard。

如果当前任务必须有强 read-only tool enforcement 才安全，则 `BLOCKED`，让用户选择可信扩展或其他隔离方式。

---

## 7. Resume 同一 Session

Review 发现问题后优先：

```bash
cd "$repo_root"
pi --mode json --session <real-session-id-or-path> --modes debug "<Rework Contract>"
```

若不使用 mode extension：

```bash
pi --mode json --session <real-session-id-or-path> "<Rework Contract>"
```

Rework Contract 必须完整：

```text
Issue
Evidence
Expected
Required change
Re-run
Scope reminder
Forbidden actions
```

不要只依赖 session history 发：

```text
"继续"
"修一下刚才的"
```

这样即使 Pi 做了 compaction，上下文仍可由 repository + evidence 重建。

---

## 8. Session 丢失时如何恢复

如果真实 session ID/file 已不可用：

```text
Do not guess.
```

创建 replacement session，并把以下内容重新提供：

- Task Contract；
- repo root / branch；
- baseline 摘要；
- current diff；
- Review / Completeness findings；
- Test Strategy / Regression Proof status；
- 已到达的 governance phase。

Repository progress 不因为 session 丢失而作废。

如果已经 `CODE_VERIFIED`，replacement session 只需要处理 Closeout，不重新实现代码。

---

## 9. Closeout 交互

需要修改知识文件时，优先 resume 同一 session：

```bash
pi --mode json --session <session> --modes build "<Closeout Contract>"
```

Closeout Contract 明确：

```text
Source of Truth = final verified implementation
Allowed = directly affected knowledge surfaces
Forbidden = unrelated production-code redesign, push/merge/deploy, destructive cleanup
Residue = report deletion-candidate unless already authorized
```

Pi turn 返回后，Codex重新检查 Git 和 stale references。

---

## 10. Runtime Evidence：保持轻量

3.0.1 不建立自定义 Evidence Bundle schema。

Codex 至少保留本轮可观察事实：

```text
pi_session_id
cwd
invoked Skill phase
workflow mode if used
provider/model if observable
Pi exit/agent_end status
commands/tests claimed by Pi
errors/policy blocks visible in JSON events
worker final summary
```

但这些都是辅助证据。

交付事实仍由 Codex直接获取：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

以及 Codex 独立运行的 tests/build/checks。

---

## 11. Provider / Model 变化

如果当前 session/下一 turn 需要换 Provider/model：

- 用户明确要求，或 Task Contract 明确允许 fallback，才执行；
- 不静默切换；
- 记录 requested vs actual（若可观察）；
- 保留当前 repository progress；
- auth/quota/model-unavailable 与代码失败分开报告。

Credential 只由 Pi/Provider store 管理。

不得把以下内容复制进 Task Contract / logs / final evidence：

```text
access token
refresh token
Authorization header
client secret
credential file contents
```

---

## 12. RPC 何时值得启用

默认 JSON CLI 已够用。

只有明确需要以下能力时考虑：

```bash
pi --mode rpc
```

典型需求：

- 一个长期存活的 Pi process；
- 实时 `steer`；
- `follow_up` queue；
- `abort`；
- `get_state`；
- 自定义 UI/IDE embedding。

RPC 是 Pi 原生能力，不意味着要新建自定义 Harness 项目。

如果未来 Codex App 的调用方式确实需要常驻 runtime，再升级到 RPC；3.0.1 不提前承担这个维护成本。

---

## 13. SDK 的定位

Pi SDK 是很好的参考/扩展点，但 3.0.1 不要求：

```text
custom Node app
createAgentSessionRuntime()
custom bridge daemon
```

只有未来出现 Pi CLI/RPC 无法满足的稳定需求，再考虑 SDK embedding。

---

## 14. Failure / Abort

### JSON 输出中断

- 检查已有 session header 是否真实；
- 检查 repository 是否已经有 tool effects；
- 不因为 JSON 不完整自动 replay 写操作；
- 能安全 resume 时继续同一 session；否则 replacement session + current diff。

### 用户取消

若是当前前台 Pi process，停止当前 invocation；若使用 RPC，调用原生 abort。

随后：

```text
inspect repository
report partial progress
do not auto rollback
CANCELLED/BLOCKED
```

---

## 15. 不做的事

3.0.1 明确不默认实现：

```text
pi-supervised-harness repo
pi-supervisor CLI
durable custom Run Store
custom operation_id
custom event protocol
custom Provider transport
custom PTY
custom session database
```

只有真实使用中出现 Pi 原生能力无法解决的问题，才新增最薄的一层适配，而不是预先重建 Harness。
