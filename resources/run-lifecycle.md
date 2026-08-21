# Supervisor Run Lifecycle

本文件定义 v2.1 的监督状态、Turn 协议和返工预算。这里描述的是 **Codex Supervisor 能确认的状态**，不是假装知道 AGY 内部每一刻在做什么。

## 1. Run Context

每个用户开发任务对应一个监督 Run。Run Context 保持轻量，不额外建立持久化 registry；tty7 已经负责真正的 workspace/pane 生命周期。

建议维护：

```text
repo_root
branch
base_head
baseline_status / baseline_diff

tty7_workspace_id
tty7_pane_id

tty7_status_mode = native-status | capture-fallback
agy_version
agy_capabilities

supervisor_state
turn_seq
current_nonce
rework_count
```

其中稳定 identity 是 `tty7_workspace_id + tty7_pane_id`，不是 tab ordinal。

## 2. Supervisor State Machine

```text
INIT
  ↓
BASELINED
  ↓
TTY7_ALLOCATED
  ↓
AGY_BOOTING
  ↓
AGY_READY
  ↓
TURN_SENT
  ↓
OBSERVING
  ├────────→ BLOCKED
  ├────────→ FAILED
  ↓
TURN_RETURNED
  ↓
REVIEWING
  ├────────→ REWORK_REQUIRED
  │               ↓
  │            TURN_SENT
  ↓
VERIFYING
  ├────────→ REWORK_REQUIRED
  ↓
ACCEPTED
```

`CANCELLED` 可由用户主动停止产生。

### 为什么不定义 `AGY_WORKING` / `AGY_DONE`

当 tty7 没有 AGY status hook 时，Supervisor 无法可靠知道 AGY 内部状态。v2.1 记录的是自己能证明的状态：我已经发送了 Turn、我正在观察、我看到了返回证据、我正在 Review。

如果未来 native status 可用，它用于提高 observation 精度，不改变 Supervisor 状态语义。

## 3. Turn

一个 Run 由多个 Turn 构成，例如：

```text
Turn 1  现状分析 / plan
Turn 2  实现
Turn 3  Review rework
Turn 4  verification rework
```

每次正式向 AGY 派一个可结束的动作，就递增 `turn_seq`。

## 4. Turn Nonce

每轮生成唯一短 nonce，例如：

```text
A7F2E9
```

将当前 Turn 指令末尾加：

```text
完成本轮要求并停止继续操作后，请在最终回复末尾单独输出：
TURN_COMPLETE: A7F2E9
```

### Nonce 的用途

- 区分当前 turn 和 scrollback 中旧 turn；
- 在 AGY 没有 tty7 status hook 时提供 completion hint；
- 降低 stale output 被误判的概率。

### Nonce 不证明什么

它不证明：

- 代码正确；
- 测试通过；
- Task Contract 已满足；
- 没有越界修改。

因此：

```text
TURN_COMPLETE != ACCEPTED
```

看到当前 nonce 后，状态只能从 `OBSERVING` 进入 `TURN_RETURNED`，然后必须 `REVIEWING`。

## 5. Read Before Send Boundary

Supervisor 不能从自己的上一轮记忆推断当前 TUI 仍在相同画面。

任何输入前：

```text
capture current pane
→ classify current UI
→ check task boundary
→ send
```

尤其是 permission、menu、trust、Ctrl-C 这类有副作用的输入。

## 6. Native Status and Fallback

### `native-status`

仅在 Preflight 证明当前 AGY 能向 tty7 报告 status 时使用：

```bash
tty7 wait "$PANE" --until waiting,done --changed --timeout 1800
```

native status 只帮助确定“何时轮到 Supervisor 再行动”。`done` 仍不等于 Acceptance。

### `capture-fallback`

没有 AGY hook 时，Supervisor 使用：

```text
tty7 agents + capture + current nonce + UI evidence
```

观察结果可以是 active/input/error/marker/prompt/unknown。

不要自己发明高频无限 polling loop。用合理间隔做有界观察，并在长时间无可靠变化时进入 failure diagnosis。

## 7. Review Transition

只有出现足够证据表明当前 Turn 已返回，才进入：

```text
TURN_RETURNED → REVIEWING
```

随后从 Git 收结果：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

Review 结论：

- `PASS` → 进入下一阶段或 `VERIFYING`
- `REWORK` → `REWORK_REQUIRED` → 新 Turn
- `BLOCKED` → 等用户/环境决策

## 8. Rework Budget

默认：

```text
soft_rework_limit = 3
```

计数单位是完整：

```text
Review → Rework → Re-review
```

不是消息数量。

达到 3 次时，Supervisor 必须重新评估：

- 是否是同一缺陷反复出现；
- AGY 是否修 A 坏 B，形成震荡；
- Task Contract 是否不清；
- Codex 根因判断是否错；
- 是否存在架构冲突；
- 是否是环境/依赖失败。

soft limit 可以在明确新证据下继续，但必须显式说明理由；不能静默无限循环。

## 9. Scope Drift

每次 Review 将当前 changed paths 与 baseline + Task Contract Scope 对比。

```text
current changes
- baseline changes
= task-introduced changes
```

若 task-introduced path 超 Scope：

1. 检查是否为需求必需；
2. 若不是，`REWORK_REQUIRED`；
3. 要求 AGY 只撤销自己产生的越界改动；
4. 重新检查 baseline integrity。

## 10. Worker Failure Does Not Erase Run Progress

AGY process / pane 失败时，Run 不自动重置为 INIT。

先检查 repository state。已有有效改动可继续 Review 或交给 replacement worker。

只有用户任务本身被取消，或者当前变更无法安全识别/继续，才结束 Run。

## 11. Session Resume

如果存在经过验证的真实 AGY conversation id，且当前 AGY capability 支持恢复，可用对应 resume 能力。

否则：

```text
Do not guess a session id.
```

replacement worker 使用：

- 原 Task Contract
- 当前 repository diff
- 剩余 Review evidence

重新建立任务上下文即可。

## 12. Acceptance

只有 Codex 可以进入 `ACCEPTED`，且必须满足：

- Task Contract 覆盖完成；
- Review Gates 相关项 PASS；
- 独立 Verification 完成；
- final diff 可解释；
- baseline 完整；
- 无未经授权外部副作用。

AGY 是否说 `done` 与最终 Acceptance 没有直接等价关系。