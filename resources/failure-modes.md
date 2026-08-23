# AGY Supervised Development 3.1 Failure Modes — Alpha 2

本文件覆盖 Workflow-First + 官方 AGY CLI Runtime 的常见失败。

原则：

> **先收证据，再动作；Runtime 成功不等于交付成功；失败不自动清空 repository progress。**

---

## 1. AGY CLI 不存在 / Headless Capability 不足

```bash
command -v agy
agy --version
agy --help
```

缺失当前流程要求的：

```text
-p / --print
--output-format stream-json
--conversation
```

则：

```text
headless_ready = false
```

选择：

- 受控升级；
- tty7 interactive fallback；
- `BLOCKED`。

不要静默切到第三方 Antigravity OAuth Provider。

---

## 2. Auth / Login Required

官方 AGY CLI 未登录或 session/auth 失效：

```text
→ BLOCKED
```

需要交互登录时可以进入 tty7 / terminal TUI。

禁止：

- 抽取 credential/token；
- 复制 auth 数据到 Skill evidence；
- 用第三方 OAuth Provider 偷偷替代官方 CLI。

---

## 3. Wrong Workspace / `init.cwd` Mismatch

如果 stream-json：

```text
init.cwd != repo_root
```

立即：

1. 停止把该 run 当当前任务；
2. 检查错误 workspace 是否有副作用；
3. 不自动回滚来源不明改动；
4. 回正确 repo_root；
5. 重新确认 branch/baseline；
6. 新建或恢复正确 conversation。

---

## 4. Conversation ID 丢失

- 不猜 ID；
- 不把“最近 conversation”自动当当前任务；
- 保留 repository progress；
- 新 conversation 输入 Spec + Execution Unit + current diff + Review evidence。

`-c` 是人工便捷入口，不是自动化精确关联的首选。

---

## 5. Wrong / Stale Conversation Resume

迹象：

- AGY 回答明显属于另一任务；
- conversation 与当前 repository facts 冲突；
- cwd / project context 不一致。

处理：

1. 停止当前 turn；
2. 读取 Git；
3. 不依赖错误 conversation 的总结；
4. 切回真实 `conversation_id`，或重建 context。

Conversation continuity 只是上下文，不是 Source of Truth。

---

## 6. Stream JSON 截断 / 无 `result`

可能是：

```text
process crash
SIGINT
network/backend failure
CLI bug
output corruption
```

处理：

1. 保存已取得的 `conversation_id`；
2. 检查 repository tool effects；
3. 检查 stderr / tool errors；
4. 不无脑 replay 可能产生重复副作用的 Execution Unit；
5. 能安全 resume 时用 `--conversation`；
6. 否则 replacement conversation + current repo evidence。

---

## 7. Terminal Result 非 SUCCESS

可能：

```text
ERROR
CANCELED
INTERRUPTED
INVALID
WAITING
RUNNING
```

不要只按进程退出码分类。

保留：

```text
result.status
result.error
stderr
conversation_id
repository partial progress
```

然后判断：retry / resume / rework / blocked。

---

## 8. `SUCCESS` 但没有 Repository Delivery

AGY 返回：

```text
result.status = SUCCESS
```

但：

```bash
git status --short
git diff
```

没有当前 Execution Unit 的实现。

结论：

```text
REWORK_REQUIRED or BLOCKED
```

禁止：

```text
SUCCESS → ACCEPTED
```

---

## 9. Headless Permission Soft-Deny

这是 Alpha 2 必须防的 near-miss。

Headless 没有人工 prompt；需要 `Ask` 的 command/tool 可能被 soft-deny，本轮仍继续，甚至 exit 0。

必须同时检查：

```text
stderr permission notice
step_update.tool_info.error
actual command evidence
repository state
result.status
```

如果 AGY 说“测试通过”，但实际测试 command 被 permission block：

```text
worker_test_execution = blocked/not-run
```

不能标 PASS。

---

## 10. 为了方便使用 `--dangerously-skip-permissions`

默认禁止把它作为 supervised path。

遇到 command block 时优先：

1. 判断是否属于本任务；
2. 使用项目已有窄 permission rule；
3. 用户授权后增加最小 allow；
4. 需要一次人工判断则 tty7 fallback；
5. 不直接全量 auto-approve。

---

## 11. Permission Rule 过宽

危险例子：

```text
command(*) allow
write_file(*) allow outside intended workspace
always-proceed used globally
```

处理：

- 缩到本项目真实需要的 action/target；
- 不把 permission config 变成绕过 Supervisor 的永久后门；
- One-way action 仍要求用户授权，即使 permission engine 会 allow。

---

## 12. Sandbox 不兼容

`--sandbox` 可能限制某些构建、测试、工具链。

如果 sandbox 导致本应合法的项目命令失败：

- 先确认是 sandbox 限制而非代码失败；
- 不把 sandbox failure 当 regression；
- 选择更窄 permission/环境方案；
- 仍不默认切 `--dangerously-skip-permissions`。

---

## 13. tty7 Fallback 被误用成默认 Runtime

tty7 只在需要 TUI/人工批准时使用。

如果所有正常任务又回到：

```text
send → capture → wait → parse screen
```

说明 Runtime 设计退化回 2.1.x。

优先恢复 headless；tty7 保持 fallback。

---

## 14. tty7 Interactive Context 串项目

进入 fallback 前必须记录：

```text
repo_root
branch
baseline
Execution Unit/Rework Contract
known conversation id
```

退出后必须重新检查 Git。

不要因为 TUI 看起来在正确项目就跳过 repository binding。

---

## 15. Worker 重新做产品决策

如果 AGY 遇到未解决的产品/架构问题并自行选择：

```text
→ REWORK_REQUIRED or SHAPING
```

Worker 应报告 ambiguity，而不是把猜测固化进代码。

---

## 16. Slice 过大

迹象：

- 一轮修改大量无明显共同行为边界的文件；
- 多个独立用户能力混在一个 Execution Unit；
- Review 很难回答“这一小步交付了什么”。

处理：回 `SLICED`，重新拆 Vertical Slices。

---

## 17. Horizontal Slicing

典型：

```text
all DB
then all API
then all UI
then tests
```

如果中间状态长时间不可独立验证，重新按 tracer-bullet vertical slice 拆。

Wide mechanical refactor 才使用 Expand → Migrate → Contract 例外。

---

## 18. Scope Drift

```text
current changes - baseline changes = task-introduced changes
```

发现无关 refactor/format/dependency/config：

1. 判断是否是当前 slice 必然 propagation；
2. 是 → Completeness scope；
3. 否 → Rework；
4. 只撤销 Worker 本任务越界修改；
5. 不碰 baseline-owned changes。

禁止 `git reset --hard` 粗暴清理。

---

## 19. Completeness Remainder 被误当 Follow-up

例如：

```text
caller 旧签名
validator/serializer 漏同步
existing data 漏迁移
同根因 sibling 仍可达
```

这些若会让当前 change unfinished：

```text
COMPLETENESS_REVIEW → REWORK_REQUIRED
```

不能因为当前 slice targeted test 绿就推给未来。

---

## 20. Completeness 被误用成 Scope Expansion

判断：

> 不做这一项，当前 change 会被 Reviewer 称为 unfinished 吗？

不会 → different ticket / Out of Scope。

---

## 21. Verification Seam 不正确

如果测试只验证内部实现而没有覆盖 Spec 的公共行为边界：

```text
→ REWORK_REQUIRED
```

例如用户行为是 HTTP contract，却只测 private helper。

Test Layer green 不能弥补错误 seam。

---

## 22. Test Layer 不匹配

显式：

```text
Unit
Integration
E2E
```

真实跨边界行为只跑 unit 通常不足。

用户 skip E2E 必须记录 `user-skipped`，不能改写成 N/A。

---

## 23. Regression Test 只有 Fix 后 GREEN

确定性 bug 默认要求：

```text
unfixed → RED
root-cause fix
same test → GREEN
Codex re-run
```

若无法安全复现，记录 N/A 原因和替代证据。

---

## 24. Rework 震荡

默认 soft limit：3 个完整 `Review → Rework → Re-review` 周期。

达到后重新评估：

```text
Spec 是否错误
slice 是否过大
root cause 是否不清楚
permission 是否阻止必要验证
环境是否有问题
conversation 是否污染
```

不要无限 resume 同一 conversation。

---

## 25. One-way Door

包括：

- destructive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- production mutation；
- irreversible delete；
- push/merge/release/deploy。

无明确授权：

```text
BLOCKED / blocked-decision-needed
```

AGY permission allow 不等于产品授权。

---

## 26. Generated Artifact / Residue

coverage/log/tmp/build/debug artifacts：

- 明确本 run 生成、按项目惯例可安全删除 → 可清；
- 来源不明 → `deletion-candidate`；
- baseline 已存在 → 不删。

---

## 27. Closeout 文档与代码冲突

- final verified implementation 是优先事实；
- 文档 stale → Closeout Rework；
- 冲突揭示实现漏传播 → 退回 Review/Completeness/Verification；
- 不只改文档掩盖代码问题。

---

## 28. Sensitive Data 出现在 Runtime Output

如果 stderr/tool output 包含 secret/token/Authorization：

- 不继续复制；
- 不 commit；
- 最终报告只记录状态，不记录值；
- 按项目安全流程处理潜在泄漏。

不要为了“留证”把原始 stream-json 整份提交到 repo。

---

## 29. 用户取消

停止当前 AGY process / interactive action。

随后：

- 检查 repository partial progress；
- 不自动 rollback；
- 保存真实 conversation id（若有）；
- 报告当前状态；
- `CANCELLED` 或风险未决时 `BLOCKED`。
