# tty7 Interactive Fallback — v3.1

> **3.1 默认 Runtime 是 AGY official CLI headless。tty7 只在确实需要交互式 TUI 时启用。**

主路径：

```text
Codex App
  ↓ Execution Unit / Rework Contract
agy -p ... --output-format stream-json
  ↓
Repository
  ↓
Codex Review
```

Fallback：

```text
Codex App
  ↓
tty7
  ↓
AGY interactive CLI
```

---

## 1. 什么时候应该使用 tty7

适合：

```text
首次/恢复登录
/permissions 管理
需要人工审批 Ask action
/resume picker
TUI-only slash command
长时间 exploratory session 且用户希望实时观察
headless 能力临时不可用/不兼容
```

不适合把每个普通实现任务都重新变成：

```text
send → capture → wait → parse screen
```

正常 Feature/Bugfix/Rework 优先 headless。

---

## 2. 进入 Fallback 前的 Context Envelope

至少保存：

```text
repo_root
branch
base_head
baseline_changed_paths
current Spec
current Execution Unit / Rework Contract
known agy_conversation_id if any
why_interactive_required
```

tty7 pane/workspace 不是任务事实源；Git 和 Contract 才是。

---

## 3. Workspace Binding

启动/接管 AGY interactive 前确认 shell 位于：

```bash
cd "$repo_root"
pwd
git branch --show-current
git status --short
```

不要因为 TUI 标题或历史内容“看起来像正确项目”就跳过验证。

如果当前不在 tty7 pane，使用 `tty7 new --json "$repo_root"` 创建本轮专属 workspace，保存返回的 workspace/pane ID；只操作本轮创建的 pane，完成后关闭它。

### 最小启动与批准序列

新 pane 的第一次 send 之后立即 capture，确认启动命令确实执行；如果仍停在 shell prompt，只补一次 Enter，不要重复整条 `agy` 命令：

```bash
tty7 send "$PANE" "agy --add-dir '$repo_root'" --enter
tty7 capture "$PANE" --plain
tty7 send "$PANE" --key enter
```

后两行只在第一行被启动期吞掉时执行。每次继续发送文字或按键前都先 capture 当前 pane，避免把输入送进旧 prompt、旧错误或别的 agent。

交互式 Edit/Write 出现单文件批准菜单时，只批准已核对的目标文件。按 Enter 应使用：

```bash
tty7 send "$PANE" --key enter
```

不要把无文字的 `--enter` 当成按键；该形式可能被 tty7 拒绝。不要使用 `--dangerously-skip-permissions` 绕过确认。

---

## 4. Conversation Continuity

如果已知真实 AGY conversation id，优先显式恢复：

```bash
agy --conversation <conversation-id>
```

如果是人工挑选历史 conversation，可以使用：

```text
/resume
```

但选定后仍需确认当前 workspace/repository facts。

`-c` / `--continue` 是便利入口，不应在有明确 conversation identity 时替代显式关联。

---

## 5. Permission Interaction

Headless 中无法处理的一次性 `Ask` action，可以在 interactive AGY 中人工批准。

原则：

- 只批准当前 Execution Unit 真正需要的动作；
- 遇到 one-way door 仍回用户决策；
- 不因为已经进入 tty7 就默认批准所有操作；
- 不把 `--dangerously-skip-permissions` 当交互问题的解决方案。

需要长期重复的安全命令，优先维护窄的 AGY fine-grained permission rule，而不是每次人工批准。

---

## 6. tty7 只负责 Transport / Visibility

tty7 可以帮助：

```text
保持一个可观察 terminal
发送输入
查看 TUI
处理人工交互
```

它不负责：

```text
Task Sizing
Shaping
Spec
Execution Slicing
Review verdict
Completeness verdict
Verification verdict
Acceptance
```

这些都属于 Codex governance。

---

## 7. 不再默认要求 v2.1 的重型机制

3.1 不要求每次 headless-compatible task 都维护：

```text
Launch Proof
Turn Nonce
Read Before Send
capture fallback hierarchy
AGY conversation DB reverse engineering
status hook inference
pane output as primary evidence
```

如果某次 tty7 fallback 为避免 stale interaction 确实需要轻量防护，可以局部使用；不要重新把这些升级成整个 3.1 的主状态机。

---

## 8. Fallback 结束后的交接

无论 interactive AGY 最终怎么结束，都必须回到 Codex：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

并进入：

```text
REVIEWING
```

不能因为 TUI 显示“Done”或模型说“完成”直接 PASS。

如果 `tty7 wait` 因 `no-agent` 或缺少 status hook 超时，改用最新 `capture --plain` 和 Git 状态确认，不要把超时当成 worker 失败或成功。若 TUI 在已完成编辑后显示 CLI/反馈问卷错误，也先保留现场并检查 Git；Git 中的改动只证明写入发生，不证明实现正确。

如果 interactive session 中运行了 tests，Codex 仍按 Test Strategy 做独立 Verification。

---

## 9. Abort / Partial State

用户停止或 TUI 异常：

1. 停止当前动作；
2. 检查 Git partial effects；
3. 不自动 rollback；
4. 保存已知 conversation identity；
5. 报告未完成/风险状态。

---

## 10. 与 2.1.x 的关系

2.1.x：

```text
Codex → tty7 → AGY
```

tty7 是主 Runtime，因此需要大量 lifecycle supervision。

3.1：

```text
Codex → AGY headless       # default
          └→ tty7 + AGY    # interactive fallback
```

所以 3.1 **保留 tty7 的实用价值，但不再让 tty7 决定开发流程的复杂度。**
