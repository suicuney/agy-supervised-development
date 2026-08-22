# Supervisor Run Lifecycle

本文件定义 v2.1.2 的监督状态、Turn 协议、返工预算、Completeness Review 和 Knowledge Closeout 状态。这里描述的是 **Codex Supervisor 能确认的状态**，不是假装知道 AGY 内部每一刻在做什么。

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

completeness_status = pending | pass | rework | blocked
blast_radius_evidence
remainder_dispositions

test_strategy:
  unit = required | not-applicable
  integration = required | not-applicable
  e2e = required | not-applicable | user-skipped
regression_proof = required | red-green-pass | not-applicable

closeout_level = lightweight | full
knowledge_surface_status
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
COMPLETENESS_REVIEW
  ├────────→ REWORK_REQUIRED
  │               ↓
  │            TURN_SENT
  ↓
VERIFYING
  ├────────→ REWORK_REQUIRED
  ↓
CODE_VERIFIED
  ↓
CLOSEOUT
  ↓
CLOSEOUT_REVIEW
  ├────────→ REWORK_REQUIRED
  │               ↓
  │            TURN_SENT
  ↓
ACCEPTED
```

`CANCELLED` 可由用户主动停止产生。

### 为什么不定义 `AGY_WORKING` / `AGY_DONE`

当 tty7 没有 AGY status hook 时，Supervisor 无法可靠知道 AGY 内部状态。Skill 记录的是自己能证明的状态：我已经发送了 Turn、我正在观察、我看到了返回证据、我正在 Review。

如果 native status 可用，它用于提高 observation 精度，不改变 Supervisor 状态语义。

### 为什么增加 `COMPLETENESS_REVIEW`

普通 `REVIEWING` 主要回答：

> 当前 diff 里的实现是否正确？

`COMPLETENESS_REVIEW` 额外回答：

> 是否还有本来应该出现在 diff 中、却被漏掉的 caller / consumer / data / state / test 传播面？

所以：

```text
Diff Review != Missing Diff Review
```

只有两者都 PASS，才进入独立 Verification。

### 为什么保留 `CODE_VERIFIED`

`VERIFYING` 通过说明：

- 代码实现正确；
- completeness / blast radius 已解释；
- Test Layer Decision 已满足；
- 可复现 bug 的 Regression Proof 已成立；
- Codex 已独立运行相关门禁。

但它仍不保证 README、Agent rules、Contract、配置说明等知识面已经同步，因此先进入 `CODE_VERIFIED`，再根据最终实现做 Knowledge Closeout。

## 3. Turn

一个 Run 由多个 Turn 构成，例如：

```text
Turn 1  现状分析 / plan
Turn 2  实现
Turn 3  Review / completeness rework
Turn 4  verification / regression rework
Turn 5  knowledge closeout
Turn 6  closeout rework（若需要）
```

每次正式向 AGY 派一个可结束的动作，就递增 `turn_seq`。

Completeness、Verification Rework、Closeout 都继续使用同一个 worker pane、Read Before Send、native-status/capture-fallback 和 Turn Nonce，不引入第二套 AGY 生命周期。

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
- blast radius 完整；
- 测试层选择正确；
- Regression Proof 成立；
- Task Contract 已满足；
- 文档/规则已经对齐；
- 没有越界修改。

因此：

```text
TURN_COMPLETE != ACCEPTED
```

看到当前 nonce 后，状态只能从 `OBSERVING` 进入 `TURN_RETURNED`，然后必须进入对应的 Review。

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

实现阶段 Review 结论：

- `REWORK` → `REWORK_REQUIRED` → 新 Turn；
- `BLOCKED` → 等用户/环境决策；
- `PASS` → 进入 `COMPLETENESS_REVIEW`，而不是直接 Verification。

## 8. Completeness Review Transition

详细协议见 `completeness-regression.md`。

固定检查：

```text
changed symbol / behavior
→ direct callers
→ indirect callers / scripts / re-exports
→ type / enum / validator / serializer
→ schema / migration / existing data
→ sibling flows / jobs
→ reachable states / retry / fallback / cache
→ orphaned old path
→ tests
```

Completeness Review 结论：

- `PASS` → `VERIFYING`；
- `REWORK` → `REWORK_REQUIRED` → 同一 AGY worker 新 Turn；
- `BLOCKED` → one-way decision / 跨范围依赖需要用户判断。

每个 remainder 必须有明确 disposition：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

Completeness 与 Scope Drift 必须同时成立：不允许漏做，也不允许借完整性做另一个 ticket。

## 9. Test Strategy & Regression Proof

在进入 `VERIFYING` 前，Run Context 应已有明确 Test Layer Decision：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

对于可安全、确定性自动复现的 bug：

```text
regression_proof = required
```

并形成：

```text
unfixed → regression test RED
fix root cause
same test → GREEN
Codex independent re-run
```

无法安全/稳定自动复现时可 `not-applicable`，但必须记录原因和替代证据。

## 10. Independent Verification Transition

只有实现 Review + Completeness Review 都 PASS 才进入：

```text
VERIFYING
```

Codex 根据 Test Layer Decision 独立运行仓库门禁。AGY 的运行结果只是线索。

Verification 失败：

```text
VERIFYING → REWORK_REQUIRED
```

全部通过后：

```text
VERIFYING → CODE_VERIFIED
```

进入 `CODE_VERIFIED` 前必须能够说明：

- Completeness Sweep = PASS；
- blast radius evidence；
- remainder dispositions；
- Test Layer Decision；
- Regression Proof = RED→GREEN 或 not-applicable；
- Codex independent commands + results。

然后必须进入 Knowledge Closeout，不直接进入 `ACCEPTED`。

## 11. Rework Budget

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
- completeness 边界是否判断错误；
- 是否存在架构冲突；
- 是否是环境/依赖失败。

soft limit 可以在明确新证据下继续，但必须显式说明理由；不能静默无限循环。

Closeout rework 也计入该 Run 的返工观察，但应区分代码返工和知识返工；若 Closeout 发现真实实现缺陷，应退回代码 Review / Completeness / Verification，而不是只改文档掩盖代码问题。

## 12. Scope Drift

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

Completeness 发现的“本次改动必然需要传播”的 caller / data / test 可以属于任务 Scope，即使初始文件列表没有逐个枚举；必须能证明它们是 unfinished remainder，而不是 another ticket。

Knowledge Closeout 修改 README/docs/rules 时，如果这些文件是本次最终实现的直接知识面，视为可解释的 closeout scope；仍必须证明关联性，不能借收尾顺手重写无关文档。

## 13. One-way Door

Completeness 不能让 Codex/AGY 擅自跨越不可逆决策。

普通可逆实现细节可按项目约定和更窄/更安全方案自行裁决。

以下默认需要明确授权或用户判断：

- destructive / non-additive migration；
- breaking public API；
- auth / tenancy boundary relaxation；
- money / billing semantics；
- secrets / credentials；
- production mutation；
- irreversible data deletion。

此时尽量完成不依赖该决定的安全部分，把 remainder 标为 `blocked-decision-needed`。

## 14. Knowledge Closeout Transition

`CODE_VERIFIED` 后，Codex 根据 final diff 判断：

```text
closeout_level = lightweight | full
```

详细标准见 `closeout-governance.md`。

固定流程：

```text
CODE_VERIFIED
  ↓
Knowledge Impact Scan
  ↓
CLOSEOUT
  ↓
AGY updates affected knowledge surfaces (only if needed)
  ↓
CLOSEOUT_REVIEW
```

Closeout Review 结论：

- `PASS` → 可以进入最终 Acceptance 判断；
- `REWORK` → 同一 AGY worker 新 Turn 修正；
- `BLOCKED` → 保留当前安全状态并报告 pending/out-of-scope/decision needed。

每次开发都执行 Scan，但允许零文档 diff。`verified-current` 本身就是有效结果。

## 15. Worker Failure Does Not Erase Run Progress

AGY process / pane 失败时，Run 不自动重置为 INIT。

先检查 repository state。已有有效改动可继续 Review 或交给 replacement worker。

只有用户任务本身被取消，或者当前变更无法安全识别/继续，才结束 Run。

如果 worker 在 `CODE_VERIFIED` 之后、Closeout 之前失败，也不要重做已经独立验证通过的实现；replacement worker 应以 final diff + Closeout Contract 重建收尾上下文。

## 16. Session Resume

如果存在经过验证的真实 AGY conversation id，且当前 AGY capability 支持恢复，可用对应 resume 能力。

否则：

```text
Do not guess a session id.
```

replacement worker 使用：

- 原 Task Contract；
- 当前 repository diff；
- 剩余 Review / Completeness evidence；
- Test Strategy / Regression Proof 状态；
- 当前 `CODE_VERIFIED` / Closeout 状态（若已经到该阶段）。

重新建立任务上下文即可。

## 17. Acceptance

只有 Codex 可以进入 `ACCEPTED`，且必须满足：

- Task Contract 覆盖完成；
- Gate 0–12 中所有相关代码项 PASS；
- Change Completeness / Blast Radius PASS；
- Test Layer Decision 已完成；
- 可复现 bug 的 Regression Proof 已完成或有合理 `not-applicable`；
- Codex Independent Verification 完成并进入 `CODE_VERIFIED`；
- Knowledge Impact Scan 已执行；
- Gate 13 Knowledge & Documentation Alignment PASS；
- final diff 可解释；
- baseline 完整；
- remainder / `pending` / `out-of-scope` / deletion candidates 已如实报告；
- 无未经授权外部副作用、one-way decision 或破坏性清理。

AGY 是否说 `done`、测试是否绿色、甚至代码是否已经 `CODE_VERIFIED`，都与最终 Acceptance 不直接等价。最终条件是：**代码正确 + 改动传播完整 + 测试证据成立 + 知识对齐 + 边界可解释**。