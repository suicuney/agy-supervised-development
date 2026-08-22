# Pi Harness Contract

本文件定义 AGY Supervised Development 3.0 的 **Worker Harness**。目标不是重新实现 Pi，而是在 Pi 官方 SDK / RPC / Extension 能力之上建立一层很薄、可审计、可恢复的监督执行层。

核心关系：

```text
Codex App
  │ Task Contract / Rework Contract
  ▼
Pi Supervisor Bridge
  │
  ▼
Pi AgentSession / AgentSessionRuntime
  │
  ├─ Harness Extension
  │   ├─ state
  │   ├─ mode
  │   ├─ scope/tool guards
  │   └─ evidence
  │
  └─ Provider
      └─ Antigravity / other configured model source
```

Pi Harness 不是最终 Supervisor。它是可编程 worker runtime。

---

## 1. 为什么选择 Pi Harness

Pi 已经提供了 v3 所需的底层 primitives：

- `AgentSession`：agent lifecycle、message history、model、compaction、abort、event stream；
- `AgentSessionRuntime`：new/resume/fork/import 和 cwd-bound runtime replacement；
- `SessionManager`：持久 session；
- built-in `read/bash/edit/write/grep/find/ls` tools；
- extension lifecycle hooks；
- `tool_call` blocking / result interception；
- `setActiveTools()`；
- custom tools / commands；
- RPC JSONL；
- SDK embedding。

因此 v3 不应再写自己的 PTY、shell terminal emulator、conversation database 或 provider transport。

---

## 2. 参考实现中吸收的模式

### Pi 官方 plan-mode

吸收：

- plan/read-only 时从 active tool set 中移除 `edit/write`；
- bash 走 read-only allowlist；
- execution 时恢复原 tool set；
- 状态持久化，resume 后仍知道当前模式。

不照搬：

- `[DONE:n]` 文本 marker 不是 v3 的 operation identity；
- v3 用结构化 Run/Operation state。

### Pi 官方 subagent example

吸收：

- 隔离上下文时使用独立 session/process；
- structured output；
- abort propagation；
- token/turn/error evidence。

v3.0 首版不默认启用多 subagent。单 Worker 仍是默认，以减少 writer conflict 和 orchestration complexity。

### `pi-agent-modes`

吸收其 defense-in-depth 模式：

```text
Tool visibility
+ tool_call hook
+ system prompt policy
```

其中 read-only mode 对 unknown custom tools 默认 fail closed 的思想尤其适合 v3。

### `pi-permission-system`

吸收：

- policy 应由 extension code 执行，而不是只靠 prompt；
- allow / ask / deny 必须可审计；
- permission decision 要进入 runtime evidence。

注意：Pi Extension 级权限不是 OS security sandbox。v3 文档必须一直保留这条边界。

### Pi AgentHarness v2 设计

吸收：

- 显式 total operation state；
- accepted operation 有 durable identity；
- 外部 effect 前后记录状态；
- crash/retry 要明确 replay uncertainty；
- 不通过“某些事件有没有出现”反推隐藏 program counter。

v3 不需要复制它全部 lane/transaction 复杂度，但自己的 Run state 必须使用同样的**显式状态优先**原则。

### `@minhduydev/pi-harness`

吸收：

- lifecycle authority 单一；
- evidence 是 durable artifact，而不是模型自述；
- provider/auth 不应由 harness bootstrap 隐式决定；
- irreversible action 保留 human authority；
- package-owned policy 与 project-owned context 分层。

不照搬：

- 大规模多 package suite；
- 多 agent role catalog；
- knowledge database；
- heavyweight bootstrap。

### `pi-maestro-flow`

借鉴其 run-control / supervision / permission / verifier 的边界设计，但 v3.0 **明确不复制 DAG、多 teammate、自主 goal loop、cockpit 和 YOLO 默认模式**。

---

## 3. 推荐实现形态

建议未来创建独立包，例如：

```text
pi-supervised-harness/
├── package.json
├── src/
│   ├── cli.ts
│   ├── runtime.ts
│   ├── extension.ts
│   ├── state/
│   │   ├── run-store.ts
│   │   ├── types.ts
│   │   └── transitions.ts
│   ├── policy/
│   │   ├── modes.ts
│   │   ├── tool-guard.ts
│   │   ├── path-guard.ts
│   │   └── command-guard.ts
│   ├── evidence/
│   │   ├── collector.ts
│   │   └── bundle.ts
│   └── bridge/
│       └── codex-cli.ts
└── tests/
```

Pi package manifest 可以只暴露 extension；Codex App 使用的 `pi-supervisor` companion CLI 负责 SDK/RPC integration。

---

## 4. SDK 还是 RPC

### 推荐主实现：SDK

当 bridge 使用 Node.js/TypeScript 时，优先：

```text
createAgentSessionRuntime()
AgentSessionRuntime
AgentSession
```

理由：

- 少一个子进程协议层；
- 能直接订阅 session events；
- 能精确控制 session manager / cwd / tools / extensions；
- 更容易把 operation state 与 Pi event 对齐；
- 更容易做单元测试。

### 兼容入口：RPC

同时保留：

```bash
pi --mode rpc
```

用于：

- 非 Node 调用者；
- CLI smoke tests；
- 对比 Pi 原生行为；
- 将来其他 UI/IDE 集成。

RPC 已有：

```text
prompt
steer
follow_up
abort
new_session
get_state
```

Codex Skill 不应该依赖 TUI 屏幕文本解析。

---

## 5. Run / Session / Operation

三个 identity 不混用。

### Run

一个用户开发任务。

```text
run_id
repo_root
branch
base_head
task_contract_hash
created_at
```

### Pi Session

一个可持久 resume 的 Pi conversation/runtime context。

```text
pi_session_id
pi_session_file
```

### Operation

一次明确可结束的 Worker 动作，例如 inspect / implement / rework / verify / closeout。

```text
operation_id
operation_seq
mode
status
started_at
settled_at
```

规则：

```text
one Run → one primary Pi session
one Run → many sequential operations
```

v3.0 默认同一 Run 不启动第二个并行 Writer session。

---

## 6. Durable Run Store

建议将 Harness 自己的监督元数据与 Pi 原生 session 分开。

例如：

```text
<repo>/.pi/supervised/
  runs/
    <run-id>/
      run.json
      contract.json
      operations.jsonl
      evidence/
        op-001.json
        op-002.json
```

如果这些属于 runtime-only state，应加入项目 `.gitignore` 的明确 managed 区域；不要把 OAuth/auth.json 放进项目。

`run.json` 只保存非敏感引用：

```json
{
  "runId": "...",
  "repoRoot": "...",
  "branch": "...",
  "baseHead": "...",
  "piSessionId": "...",
  "piSessionFile": "...",
  "harnessVersion": "3.0.x",
  "provider": "antigravity",
  "model": "...",
  "state": "HARNESS_READY",
  "reworkCount": 0
}
```

禁止保存 token / Authorization header / credential payload。

---

## 7. Operation State

推荐显式状态：

```text
CREATED
→ DISPATCHED
→ RUNNING
→ SETTLING
→ SETTLED
```

异常：

```text
BLOCKED
FAILED
ABORTED
RECOVERY_REQUIRED
```

`SETTLED` 只说明 Pi 不再继续本 operation；不说明实现正确。

不要通过“最后一条 assistant message 看起来像结束了”来定义状态。

事件层优先使用 Pi 的 agent/session events；如果 SDK/RPC 进程崩溃，Run Store 保留最后 durable state，并进入 recovery，而不是把 operation 猜成 success。

---

## 8. Mode Policy

建议定义：

```ts
type WorkerMode =
  | "inspect"
  | "implement"
  | "rework"
  | "verify"
  | "closeout";
```

### inspect

工具：

```text
read
grep
find
ls
bash(read-only)
```

禁止：

```text
edit
write
mutation custom tools
```

### implement

工具：

```text
read/grep/find/ls
edit/write
bash(policy guarded)
```

必须：Scope Guard + external-side-effect guard。

### rework

工具同 implement，但 system policy 强制只处理 Supervisor findings，不主动新增 scope。

### verify

默认：

```text
read/grep/find/ls
bash(test/build/read-only git)
```

禁用 `edit/write`。发现失败后返回 evidence，让 Codex 决定下一次 rework。

### closeout

允许 `edit/write`，但 Path Guard 将写入限制在 Task Contract/Codex Closeout Contract 指定知识面与确有必要的 adjacent authority files。

---

## 9. Defense-in-depth Tool Guard

不要只有一层。

### Layer A — Tool visibility

在 read-only mode：

```text
setActiveTools(...without edit/write...)
```

或创建 session 时只传 read-only tool allowlist。

### Layer B — `tool_call` hook

无论模型是否 somehow 获得某 tool，都再次校验：

```text
mode
repo_root
protected paths
allowed scope
command class
one-way side effects
```

不符合：

```text
{ block: true, reason: ... }
```

### Layer C — System policy

`before_agent_start` 注入：

```text
current operation id
current mode
Task Contract
scope
protected actions
required report
```

Prompt 是指导，不是唯一 enforcement。

---

## 10. Path Guard

最小规则：

```text
outside repo_root → DENY
known secret/credential files → DENY by default
baseline-owned unrelated paths → DENY mutation unless Task Contract requires
Task Contract scope → ALLOW
new propagation path → REQUIRE scope justification / evidence
```

不要把 Scope 写死成“只有最初列出的文件”。Completeness 可能合法扩展到直接 caller/test/schema，但必须可解释。

推荐 decision：

```text
ALLOW
DENY
BLOCKED_NEEDS_SUPERVISOR
```

`BLOCKED_NEEDS_SUPERVISOR` 让 operation 安全结束，把 path + reason 交回 Codex，而不是 live popup 让 worker 自己决定。

---

## 11. Bash / Command Guard

只读 mode 使用 fail-closed allowlist。

可允许：

```text
pwd
ls/tree/find/fd
cat/head/tail
rg/grep
git status
git diff
git log
git show
git branch --show-current
package/test query commands that do not mutate
```

implement/rework 允许项目范围内构建测试命令，但默认阻止：

```text
git push
git merge
git reset --hard
git clean -fd*
release/publish
deploy/production mutation
sudo/system mutation
credential inspection/export
irreversible delete
```

`rm` 不能只按字符串一刀切：项目生成物清理可能合理，但必须证明目标是本 operation 明确创建、位于 repo 内、且不属于 baseline。不能证明则 BLOCK。

Package install / network command 默认由 Task Contract 决定；不要无提示安装依赖。

---

## 12. Evidence Collector

Pi Harness 应自动收集机器可验证证据。

### Operation metadata

```text
run_id
operation_id
mode
provider/model
start/end
stop reason
```

### Repository

```text
git status --short
git diff --stat
git diff --check
changed paths
```

不要求把完整巨大 diff 永久复制进 evidence；Codex 会直接读取 repository。

### Tool evidence

记录：

```text
tool name
sanitized target/command class
result status
duration
blocked reason
```

不要把敏感 stdout 原样写入长期日志。

### Verification

记录：

```text
command
duration
exit code
sanitized key output
layer = unit | integration | e2e | build | lint | schema
```

### Model report

保留 worker summary，但标成：

```text
model_report = untrusted/self-reported
```

---

## 13. Evidence Bundle Schema

建议：

```json
{
  "schemaVersion": 1,
  "runId": "...",
  "operationId": "...",
  "session": { "id": "...", "file": "..." },
  "harness": { "version": "..." },
  "provider": { "id": "antigravity", "model": "..." },
  "mode": "implement",
  "status": "settled",
  "repository": {
    "changedPaths": [],
    "diffStat": "...",
    "diffCheck": "pass"
  },
  "commands": [],
  "tests": [],
  "policyBlocks": [],
  "scopeFindings": [],
  "unresolved": [],
  "workerSummary": "..."
}
```

所有字段都应能 JSON serialization，方便 Codex App / scripts 消费。

---

## 14. Provider 与 Model

Harness 接收 provider/model 配置，但**不自己拥有账号**。

Provider layer 细节见 `provider-boundary.md`。

重要：

- 不在 runtime state 中复制 credential；
- provider/model transition 记录到 evidence；
- auth/quota error 是 runtime blocker，不是假代码 failure；
- 不静默从 Antigravity 切到别的 Provider 后继续写代码。

---

## 15. Resume / Recovery

### 正常 resume

使用真实 Pi `session_id/session_file`。

Codex 给新 operation：

```text
original Task Contract
current repository state
latest Review findings
latest completeness/test state
```

Pi session context 是加速项，不是唯一真相来源。

### Bridge crash

1. 读取 Run Store；
2. 检查 operation durable state；
3. 检查 current repository state；
4. 查询 Pi session 是否仍存在；
5. 对无法证明已经 settlement 的 external effect 标 `recovery uncertainty`；
6. 不无脑 replay 写操作。

### Provider failure

保留 session + repository progress，创建新 operation 继续，不清空 Run。

---

## 16. Codex Bridge CLI Contract

建议最小 CLI：

```bash
pi-supervisor doctor --repo <path>
pi-supervisor run --repo <path> --contract <json-file>
pi-supervisor resume --run <run-id> --contract <json-file>
pi-supervisor status --run <run-id> --json
pi-supervisor abort --run <run-id>
```

stdout 在 `--json` 时只输出 machine-readable result；诊断写 stderr。

### `doctor`

输出：

```text
Pi version/capabilities
Harness version
repo binding
Provider/model availability
auth usable yes/no (never token)
tools/modes loaded
session storage writable
```

### `run/resume`

返回：

```text
run_id
operation_id
status
evidence_path / inline evidence
pi_session identity
```

Codex App 通过 shell/tool 调用即可，不需要用户切到 Pi TUI。

---

## 17. Extension Responsibilities

Extension 应负责：

- mode state；
- tool visibility；
- `tool_call` guard；
- `before_agent_start` policy injection；
- tool result sanitization/evidence hooks；
- session state entry / operation metadata；
- optional diagnostic commands。

Extension 不应负责：

- Google OAuth UI 本身；
- provider private endpoints；
- git final acceptance；
- Codex review decisions；
- cross-project orchestration；
- deployment/release automation。

---

## 18. Testing Harness 本身

至少需要：

### Unit

- state transitions；
- path policy；
- command classification；
- evidence redaction；
- mode tool selection；
- contract validation。

### Integration

- in-memory Pi session + fake model/tool sequence；
- persistent session resume；
- blocked tool call；
- provider error mapping；
- abort propagation；
- dirty baseline preservation。

### E2E

在临时 Git repo：

```text
Codex-like contract
→ Pi worker changes file
→ evidence emitted
→ process restart
→ resume/rework
→ tests
→ final diff remains baseline-safe
```

Provider E2E 应与 Harness deterministic E2E 分开，避免 OAuth/quota/flakiness 让核心 harness 测试不稳定。

---

## 19. v3.0 首版不要做

- parallel writer；
- DAG；
- autonomous long-running goal；
- model voting；
- long-term memory DB；
- browser cockpit；
- full permission language；
- universal provider abstraction beyond Pi's own provider model；
- self-modifying harness；
- automatic Provider installation/login。

如果将来证明单 Worker 是瓶颈，再以新版本增加，而不是把 3.0 首版做成另一个 Orca/Maestro。

---

## 20. Definition of Ready

Pi Harness 可以被本 Skill 视为 READY，至少满足：

```text
[ ] Codex 可 headless 调用
[ ] repo/cwd 绑定明确
[ ] persistent session 可恢复
[ ] operation identity 可关联
[ ] inspect mode 真正 read-only
[ ] implement/rework 有 scope + command guard
[ ] one-way side effects fail closed
[ ] provider/auth 不由 harness 隐式接管
[ ] evidence bundle 可 JSON 消费
[ ] abort/recovery 有明确定义
[ ] credentials 不进入 evidence/repository
[ ] deterministic harness tests 通过
```
