# AGY Supervised Development 3.1 Failure Modes — Alpha 3

本文件覆盖 Workflow-First + 官方 AGY CLI + Three-Axis Review 的常见失败。

原则：

> **先收证据，再动作；Runtime 成功不等于交付成功；Review 三个轴互不抵消；失败不自动清空 repository progress。**

---

## 1. AGY CLI 不存在 / Headless Capability 不足

```bash
command -v agy
agy --version
agy --help
```

缺失当前流程需要的 headless 能力时：

```text
headless_ready = false
```

选择：受控升级、tty7 interactive fallback、或 `BLOCKED`。

不要静默切到第三方 Antigravity OAuth Provider。

---

## 2. AGY cwd mismatch

`init.cwd != repo_root`：

1. 停止把该 run 当当前任务证据；
2. 检查错误 workspace 是否有副作用；
3. 不自动 rollback 来源不明修改；
4. 在正确 repo root 重启；
5. 重新确认 baseline。

---

## 3. Conversation identity 丢失 / 错 resume

- 不猜 conversation id；
- 自动监督有真实 ID 时优先 `--conversation <id>`；
- 不用 `-c` 把未知最近 conversation 冒充当前任务；
- 原 conversation 丢失时，用 Spec + Execution Unit + current diff + findings 重建上下文。

Repository progress 不因为 conversation 丢失而作废。

---

## 4. AGY `SUCCESS` / exit 0，但没有交付

如果：

```text
result.status = SUCCESS
exit = 0
```

但 Git 没有对应 Execution Unit 的实现：

```text
→ REWORK_REQUIRED
```

`SUCCESS` 只证明本轮返回，不证明 Spec 满足。

---

## 5. Headless permission soft-deny

Ask 类命令在 headless 中可能被拒绝，但 run 继续甚至 exit 0。

必须同时检查：

```text
result.status/error
stderr
tool/step error
actual Git state
```

被拒绝的测试：

```text
blocked/not-run
```

不能写 PASS。

---

## 6. 为了解阻塞默认使用 `--dangerously-skip-permissions`

禁止把它当普通 fallback。

优先：

```text
已有安全 allow
→ 最窄 fine-grained allow
→ tty7 one-off human approval
→ BLOCKED
```

不要为一条 test command 全局解除边界。

---

## 7. tty7 重新变成默认 Runtime

正常 headless 可用时，不应恢复：

```text
每轮都 tty7 send/capture/wait
screen parse = completion evidence
```

tty7 只用于真实交互需求。

---

## 8. Pi 重新变成永久父 Agent

禁止无收益地恢复：

```text
Codex → Pi → AGY
```

Pi 仅在 research / second opinion / blast-radius / specialized extension 有明确价值时旁路使用。

---

# Workflow Failures

## 9. Small task 被过度流程化

明确的小修复不要为了形式建立大 Decision Map / Ticket DAG。

允许：

```text
Compact Shape/Spec
→ one Execution Unit
→ AGY
→ Review
```

---

## 10. Complex task 被伪装成 Small

出现：

```text
新 Open Decision
跨模块 contract
复杂 data propagation
one-way door
multi-session uncertainty
```

应升级 Medium/Large，而不是继续塞进一个 Worker turn。

---

## 11. Open Decision 被 Worker 猜掉

真正产品/架构语义未决定时：

```text
→ SHAPING / BLOCKED
```

不要让 AGY 用“实现一个看起来合理的版本”替用户决定。

---

## 12. Fog 被提前伪造成 Ticket

当前问题无法精确陈述，只依赖前置决定时，保留：

```text
Not Yet Specified
```

不要为了计划完整而生成假精度 Execution Units。

---

## 13. Horizontal Slicing

默认不要拆成：

```text
all DB
all API
all UI
all tests
```

能按行为切时使用 Vertical Slice；Wide Refactor 才用 Expand → Migrate → Contract。

---

# Three-Axis Review Failures

## 14. Quality 很高掩盖 Spec 漏做

典型：代码漂亮、测试完善，但 Acceptance Criterion 缺一项。

结论：

```text
Axis A = REWORK
Overall = REWORK_REQUIRED
```

不能用 Quality PASS 抵消 Spec failure。

---

## 15. Spec 全做对掩盖 Engineering Defect

典型：Acceptance 全覆盖，但：

- exception 被吞；
- auth boundary 错；
- transaction/race 不安全；
- speculative abstraction；
- tests 绑定内部实现。

结论：

```text
Axis B = REWORK
Overall = REWORK_REQUIRED
```

---

## 16. Changed-file tests green 掩盖 Missing Diff

当前 diff 全绿，但 hidden caller / consumer / schema / script 仍旧：

```text
Axis C = REWORK
```

不能直接 VERIFYING。

---

## 17. Completeness 被误用成 Scope Expansion

判断：

> 不做这一项，当前 change 会被称为 unfinished 吗？

不会 → `out-of-scope-different-ticket`。

不要借 Axis C 做邻近重构、依赖升级、新产品功能。

---

## 18. Scope Creep 被包装成“有用增强”

Spec 未要求的新行为，即使有测试、看起来有价值，也先产生 `S*` finding。

若是必然传播面，Axis C 会证明；否则移除或回 Shaping。

---

## 19. Three-Axis Review 做平均分 / 多数投票

禁止：

```text
Spec PASS
Quality PASS
Completeness REWORK
→ overall PASS  # 错
```

正确：

```text
any REWORK → REWORK_REQUIRED
any unresolved BLOCKED → BLOCKED
```

---

## 20. Finding 模糊，无法驱动 Rework

禁止：

```text
“再检查一下”
“这里似乎有问题”
“看看还有没有漏的”
```

必须：

```text
Finding ID
Axis/Source
Issue
Evidence
Expected
Required Change
Re-run
```

---

## 21. Rework 后只复查原 finding

修一个 Q finding 可能破坏 Spec 或引入新 missing diff。

因此 Rework 后：

```text
→ full Three-Axis Review
```

不是只检查 Q1 消失就直接 VERIFY。

---

# Bug Intelligence Failures

## 22. Complex Bug 没 feedback loop 就开始猜修复

如果 Bug flaky / cross-service / performance / multiple hypotheses，却没有能抓用户症状的反馈环：

```text
→ DIAGNOSING
```

不要把第一 plausible theory 当 root cause。

---

## 23. Feedback Loop 抓到的是错误症状

如果测试复现的是附近异常，不是用户真实问题：

- 不继续 root-cause claim；
- 调整 feedback loop；
- 重新 reproduce/minimise。

Wrong bug → wrong fix。

---

## 24. 单一 hypothesis 锚定

复杂 Bug 默认形成 3~5 ranked/falsifiable hypotheses。

每个至少有：

```text
Prediction
Probe
What falsifies it
```

无法证伪的“感觉”不是强 hypothesis。

---

## 25. Instrumentation 无目标 / 残留

避免“到处加 log 再 grep”。

Instrumentation 要对应某个 hypothesis prediction，并在最终 Review 前清理临时 debug/profiling residue。

---

## 26. Fix 绿了但 Root Cause 说不清

如果只能说明：

```text
“改这里后测试绿了”
```

但无法回答 cause → symptom 链路及排除证据，仍不能把它包装成高置信 root cause。

Axis B 可要求更健康的根因修复。

---

## 27. Regression test 只有 post-fix GREEN

确定性 Bug 如果从未证明同一 proof 在 unfixed behavior 上 RED：

```text
Regression Proof incomplete
```

能安全复现时要求 before/after。

---

## 28. Minimal regression 绿，但原始 repro 没重跑

复杂 Bug：

```text
minimal GREEN != original user symptom proven fixed
```

Independent Verification 还要重跑原始 feedback loop / 原始未最小化场景。

---

# Verification / Closeout Failures

## 29. Three-Axis PASS 后 Verification 失败

产生 `V*` finding：

```text
VERIFYING
→ REWORK_REQUIRED
→ AGY
→ Three-Axis Review again
→ Verify again
```

不能修完测试后直接跳回 VERIFYING。

---

## 30. Worker 自述测试通过替代 Codex Verification

AGY Worker evidence 只是线索。

Codex 必须独立执行相关 Verification Seam/Test Strategy 命令。

---

## 31. Verification Seam 错

如果 Spec 的公共 seam 是 API/CLI/UI 行为，却只验证 private helper：

- Axis A 可能 seam fidelity REWORK；
- Axis B 可能 test quality REWORK；
- 不能因为测试数量多而 PASS。

---

## 32. CODE_VERIFIED 被当成最终完成

`CODE_VERIFIED` 后仍需 Knowledge Impact Scan。

API/schema/config/workflow 等变化若 docs stale：

```text
K* finding → Closeout Rework
```

---

## 33. Closeout 为制造 diff 而改文档

纯内部修复且知识面都 current 时，零文档 diff 是正常 PASS。

不要为了证明“做了 Closeout”修改 README。

---

## 34. Closeout 用文档掩盖代码缺陷

Closeout 发现实现本身错误时：

```text
→ K finding
→ REWORK_REQUIRED
→ Three-Axis Review
→ Verification
→ Closeout again
```

不能只把文档改成符合错误实现。

---

# Safety / Scope Failures

## 35. One-way Door 被 Runtime permission 当成授权

AGY permission engine 允许执行，不代表用户授权：

```text
destructive migration
breaking API
auth relaxation
money/billing
credential semantics
production mutation
irreversible delete
push/merge/release/deploy
```

无明确授权：`BLOCKED / blocked-decision-needed`。

---

## 36. 用户 baseline 被 Worker/Rework 清理

禁止为“恢复干净状态”执行粗暴 reset/rollback。

只处理明确属于当前任务的 task-introduced changes。

---

## 37. Credential 泄漏

如果日志/diagnostics 出现 token、Authorization、secret：

- 不继续复制；
- 不写入 Contract/repo/final report；
- 只记录 auth status；
- 按项目安全流程处理。

---

## 38. 用户取消

停止当前 process/interactive action，然后：

```text
inspect repository partial progress
do not auto rollback
preserve real conversation id if available
CANCELLED or BLOCKED if risk unresolved
```

---

# Failure Handling Summary

所有失败都优先保留：

```text
baseline
approved Spec
Execution Unit
current repository progress
real AGY conversation identity
Three-Axis findings
bug diagnosis evidence
verification evidence
```

不要因为 Runtime/Review 某一步失败就默认从头重写。