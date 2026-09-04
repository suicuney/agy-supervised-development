# AGY Native Execution Adapter — Headless First

AGY Supervised Development 3.1 把 Runtime 与 Workflow 解耦。`SIZE → SHAPE → SPEC → SLICE` 决定做什么和如何切；本文件只负责把一个已经批准的 **Execution Unit** 可靠交给官方 AGY CLI。

核心原则：

> **Headless first. Interactive only when interaction is genuinely required.**

```text
Codex App
  ↓ Execution Unit
AGY official CLI
  ├─ headless / stream-json   ← default
  └─ tty7 interactive         ← fallback
  ↓
Repository
  ↓
Codex Review
```

---

## 1. 为什么默认 Headless

官方 AGY CLI 已提供足够的程序化边界：

```text
-p / --print
--output-format json | stream-json
--conversation <id>
-c / --continue
--print-timeout
--sandbox
fine-grained permissions
```

因此 3.1 不再默认依赖：

```text
tty7 capture/wait
PTY screen parsing
Turn Nonce
AGY conversation DB reverse engineering
status hook inference
```

这些只在真正需要交互式 TUI 时才回退使用。

---

## 2. Preflight

每次正式实现前做 capability detection，不按旧版本文档猜：

```bash
command -v agy
agy --version
agy --help
```

至少确认：

```text
agy executable available
-p / --print available
--output-format stream-json available
--conversation available
repo cwd known
auth/session usable
```

可选确认：

```text
--sandbox
--model / --effort / --agent
--print-timeout
```

若当前安装不支持所需 headless 能力：

```text
headless_ready = false
```

再决定升级 CLI、使用受控 tty7 fallback，或 `BLOCKED`。不要静默换成第三方 Antigravity Provider。

---

## 3. Workspace Binding

调用前：

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git branch --show-current
git rev-parse HEAD
```

启动：

```bash
agy -p "<Execution Unit>" --output-format stream-json
```

`init` event 中必须检查：

```text
init.cwd == repo_root
```

不一致：立即停止把该 run 当作当前任务执行证据，并检查错误 workspace 是否已有副作用。

AGY conversation history 由当前 working directory 做 workspace scoping；不能用 `-c` 代替显式身份校验。

`init.cwd == repo_root` 只是第一道检查，不足以证明后续工具命令的 cwd。首个 `run_command` 后还要核对命令输出中的：

```bash
pwd
git -C "$repo_root" rev-parse --show-toplevel
git -C "$repo_root" branch --show-current
```

如果 `pwd` 落到 AGY CLI home 或其他目录，停止写入；改用绝对路径或重新绑定 workspace。不要因为 `init` 看起来正确就继续使用相对路径。

---

## 4. 默认单次执行

MVP 默认一轮一个进程：

```bash
agy -p "<Execution Unit>" \
  --output-format stream-json \
  --print-timeout 30m
```

`30m` 只是示例。实际 timeout 根据 task size / repository tests 调整，不在 Skill 中写死唯一值。

为什么优先单次进程：

- 生命周期简单；
- 每轮 Review 后 Codex 可以决定是否继续；
- crash/retry 更容易与 repository state 对齐；
- 不需要维护常驻自定义 daemon。

---

## 5. Stream JSON Contract

Headless `stream-json` 的关键事件：

```text
init
step_update *
result
```

### `init`

至少读取：

```text
conversation_id
cwd
tools
permission_mode
model/agent if observable
```

保存真实：

```text
agy_conversation_id
agy_cwd
```

不要自己生成 conversation id。

### `step_update`

可用于观察：

```text
agent_response
工具调用
tool error
subagent activity
usage
```

不要把每一个 step 再复制成自己的 runtime state machine。

### `result`

终态可见：

```text
SUCCESS
ERROR
CANCELED
INTERRUPTED
INVALID
WAITING
RUNNING
```

关键语义：

```text
result.status == SUCCESS
!=
Execution Unit PASS
```

它只说明 AGY 本轮完成并产生响应；随后必须由 Codex 读取 Git。

同理，`ERROR` 也不自动等于“没有改动”：若 CLI 在已执行编辑后因反馈问卷、TUI 或其他运行时错误退出，先检查 Git 是否已有部分写入，再由 Codex Review 和独立验证判断正确性。不要自动回滚或自动重放可能产生重复副作用的单元。

---

## 6. 不要只看 Exit Code

这是 3.1 的重要 Runtime 规则。

Headless 模式无法弹出人工确认时，某些默认 `Ask` 的 tool action 会被 soft-deny。本轮仍可能继续，甚至最终 exit code 为 0。

因此执行结果判断至少同时看：

```text
process exit code
result.status / result.error
stderr permission notices
step_update.tool_info.error
repository state
```

禁止：

```text
exit 0 → implementation success
```

如果 AGY 想运行测试但 `run_command` 被 soft-deny，必须记录：

```text
worker_test_execution = blocked/not-run
```

不能转述成“测试通过”。

---

## 7. Permission Strategy

官方 AGY CLI 使用 fine-grained permissions。

3.1 默认：

```text
Deny > Ask > Allow
```

只为本项目长期稳定需要的行为配置窄范围规则，例如项目测试/build 命令。

禁止默认使用：

```bash
--dangerously-skip-permissions
```

这个 flag 会自动批准所有 tool calls，包括文件写入和命令执行；它不是 supervised workflow 的正常入口。

如果某 Execution Unit 必须运行命令但 headless policy 会 soft-deny，优先顺序：

1. 判断命令是否真的属于本任务；
2. 使用现有项目 permission policy；
3. 用户明确同意时添加最小 allow rule；
4. 若需要一次性人工判断，转 tty7 interactive fallback；
5. 不直接全局 always-proceed。

若错误明确来自写入权限（例如 `write_file` / `replace_file_content` 被拒绝），不要在 headless 中盲目重复同一 turn。保存真实 `conversation_id` 和错误证据，转到受控 tty7 做一次性人工批准；批准后仍需回到 Git Review。

### Sandbox

`--sandbox` 可作为额外终端限制，但不是所有仓库都适配。只有当前 CLI 和项目验证可用时启用，不把它当 OS 级完整安全边界。

---

## 8. Rework Resume

Codex Review 发现问题后，优先继续**同一个真实 AGY conversation**：

```bash
agy -p "<Rework Contract>" \
  --conversation "$agy_conversation_id" \
  --output-format stream-json \
  --print-timeout 30m
```

不要默认使用：

```bash
agy -c
```

作为自动化精确关联方式。

`-c` 适合人工快速继续当前 workspace 最近 conversation；监督流程已经知道真实 `conversation_id` 时，优先显式 `--conversation`。

Rework Contract 必须重新包含：

```text
Issue
Evidence
Expected
Required Change
Re-run
Scope Reminder
Forbidden Actions
```

Conversation history 是辅助上下文，不是 Contract 的替代品。

---

## 9. Conversation 丢失

如果真实 conversation 已不可恢复：

```text
Do not guess another conversation.
```

创建新 AGY conversation，并重新提供：

```text
approved Spec / current Execution Unit
repo/branch/baseline summary
current diff
Codex Review findings
Completeness findings
verification status
```

Repository progress 不因为 conversation 丢失而作废。

不要默认从头重写已经存在的实现。

---

## 10. Continuous Stream Input：Optional

官方 AGY CLI 支持：

```bash
agy --input-format stream-json --output-format stream-json
```

一个进程内连续提交多轮 prompt。

3.1 Alpha 2 **不把它设为默认**。只有以后真实使用证明以下收益明显时再启用：

```text
频繁连续 rework
进程启动成本明显
需要程序即时读 result 后决定下一 prompt
```

原因：常驻 stdin process 会增加 abort/recovery/process ownership 复杂度，而单轮 `--conversation` 已足够覆盖当前监督流程。

---

## 11. tty7 Interactive Fallback

只有真正需要 TUI 交互时使用 tty7，例如：

```text
首次登录 / auth interaction
/permissions 管理
/resume picker
需要人工批准 Ask action
slash commands / TUI-only operation
长时间 exploratory session 且用户希望直接观察
headless capability 临时不可用
```

Fallback 拓扑：

```text
Codex
  ↓
tty7
  ↓
AGY interactive CLI
```

进入 fallback 前记录：

```text
why_interactive_required
repo_root
branch
baseline
current execution unit/rework contract
known conversation id if any
```

退出 fallback 后仍回 Codex Git Review。

**tty7 是 transport/UI fallback，不是新的 Supervisor。**

---

## 12. Worker Report

Execution Unit 要求 AGY 最终报告：

```text
Changed behavior
Changed files
Tests/checks actually run
Tests/checks blocked or not run
Permission/tool failures
Known limitations
Unresolved items
```

这些都是 worker self-report，只作为 Review 索引。

Codex 仍自己执行：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

并根据 Spec/Verification Seam 独立验证。

---

## 13. Failure / Interrupted Run

若：

```text
无 terminal result
status = ERROR/CANCELED/INTERRUPTED/INVALID/WAITING/RUNNING
process crash
stream-json 截断
```

处理顺序：

1. 检查 repository 是否已发生部分写入；
2. 检查真实 conversation id 是否已取得；
3. 保存可见 error/permission evidence；
4. 不自动 replay 可能重复副作用的 Execution Unit；
5. 能安全 resume 时用 `--conversation`；
6. 否则新 conversation + current repository evidence。

---

## 14. Runtime 与 Governance 的分界

AGY Runtime 只回答：

```text
本轮是否启动？
在哪个 cwd？
conversation 是谁？
调用了什么工具？
哪些被阻止？
本轮如何结束？
```

Codex Governance 回答：

```text
需求是否满足？
实现质量是否合格？
有没有漏改？
测试是否正确？
是否可以验收？
```

所以：

```text
AGY result SUCCESS
→ Codex REVIEWING
```

而不是：

```text
AGY result SUCCESS
→ ACCEPTED
```

---

## 15. 3.1 不再默认做的事

```text
Pi Antigravity OAuth Provider
custom Pi harness
pi-supervisor
custom daemon
custom AGY conversation DB
PTY parsing as default
screen scraping as primary evidence
Turn Nonce as primary identity
--dangerously-skip-permissions as normal path
```

只在真实缺口出现时补最薄的一层，不预先重建 Runtime 平台。
