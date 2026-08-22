# AGY Supervised Development 3.0 Failure Modes

本文件把“Pi 卡住 / Provider 不可用 / 看起来完成但其实没有 / Tool Guard 阻塞”拆成可诊断状态。

原则：

> **先收集证据，再采取动作；未知状态不猜成成功；runtime failure 不等于 repository progress 无效。**

---

## 1. Pi / Harness entrypoint 不存在

Preflight 发现 Pi 或 `pi-supervisor` 等 Harness entrypoint 不可用：

```text
HARNESS_PREFLIGHT → BLOCKED
```

处理：

- 报告缺失能力；
- 不假装已经进入 supervised implementation；
- 不自动全局安装/升级 Pi 或 Harness，除非用户明确要求。

---

## 2. Harness 版本/协议不兼容

例如：

- Evidence schema 不认识；
- extension API 已变化；
- required SDK/RPC capability 缺失；
- mode/tool guard 未加载。

处理：

- fail closed；
- 报告实际 Pi/Harness version 与缺失 capability；
- 不靠降级到“只发 prompt”绕开 policy。

---

## 3. Repository binding mismatch

迹象：

- Harness cwd 不等于 `repo_root`；
- Pi session resume 到另一个 project；
- branch 与 Task Contract 不一致；
- worker 读取/修改 repo 外路径。

处理：

1. 停止当前 operation；
2. abort（若仍运行）；
3. 检查 Git state；
4. 不回滚来源不明改动；
5. 修正 cwd/session binding；
6. 重新 Preflight。

---

## 4. Provider 缺失

目标 Provider 未安装/未注册：

```text
provider-missing
```

处理：

- BLOCKED；
- 不自动 `pi install`；
- 告诉用户需要自己选择/审查 Provider，或明确授权安装。

---

## 5. OAuth / Auth required

现象：Provider 已存在，但 auth missing/expired/invalid。

处理：

- `PROVIDER_AUTH_BLOCKED`；
- 不读取/展示 token；
- 不模拟登录；
- 用户自己完成 provider login/auth flow。

---

## 6. 第三方 Antigravity Provider 风险不清

如果 Provider README/版本提示 Terms of Service、账号封禁、endpoint 不稳定等风险：

- 明确告诉用户这是第三方非官方集成；
- 不把它说成官方 AGY 路径；
- 用户没有接受风险前不自动启用/安装；
- 已安装时仍保持 credential redaction。

---

## 7. Provider quota / rate limit

例如 429/quota exhausted：

```text
PROVIDER_CAPACITY_BLOCKED
```

处理：

- 保留 Run、session 和 repository progress；
- 允许有限 retry（遵守 retry-after）；
- 不无限重试；
- 不静默换模型/provider。

---

## 8. Provider transient transport error

例如 timeout/5xx/reset：

- 记录 `PROVIDER_TRANSIENT_FAILURE`；
- 确认当前 operation 是否可能已经执行 tool effects；
- 对有 replay 风险的 operation 不无脑重发；
- safe retry 必须有上限。

---

## 9. Provider model removed / tool capability changed

模型 catalog 存在变化或 tool call 不再支持：

```text
PROVIDER_CAPABILITY_FAILURE
```

处理：

- 运行时 discovery；
- 不 hard-code 旧 model ID；
- 需要切模型时由 Codex/用户决定或依 Task Contract fallback policy；
- 记录 transition。

---

## 10. Operation settled，但 Git 没有实现

Pi/model 报告完成，Evidence Bundle 也 `settled`，但：

```bash
git status --short
git diff
```

没有 Task Contract 对应改动。

处理：

- 不接受；
- `REWORK_REQUIRED` 或诊断 repo/session mismatch；
- `OPERATION_SETTLED` 只证明 worker 停止，不证明 delivery。

---

## 11. Stale Operation Result

现象：上一个 operation 的异步 event/evidence 晚到，被错误当成当前 rework 的结果。

处理：

- 所有结果必须关联 `run_id + operation_id`；
- 不接受不匹配的 event；
- state transition 只消费 current operation；
- stale result 可保留诊断，但不能推进状态。

---

## 12. Harness bridge crash

处理顺序：

1. 读取 durable Run Store；
2. 读取 Pi session identity；
3. 检查最新 operation state；
4. 检查 repository；
5. 判断是否有外部 effect settlement uncertainty；
6. 能安全 resume 才 resume；否则创建 recovery operation。

禁止把 crash 自动解释为 operation failure 后从头重做所有修改。

---

## 13. Pi Session 丢失/不可恢复

如果 session file/id 不存在：

- 不猜 session ID；
- 保留当前 repository state；
- 用 Task Contract + baseline + diff + Review evidence 重建 replacement session；
- 新 session identity 写回 Run Store。

如果已经 `CODE_VERIFIED`，replacement session 只继续 Closeout，不重做实现。

---

## 14. Tool Guard 意外允许危险命令

例如模型成功执行：

```text
git push
git reset --hard
deploy
credential export
```

而 Task Contract 未授权。

这是 **Harness defect**，不是普通 worker issue。

处理：

- 立即停止 operation；
- 检查实际 side effect；
- 不隐瞒；
- 标记 Gate External Side Effects FAIL/BLOCKED；
- 修复 Harness policy before trusting further operations。

---

## 15. Tool Guard 误杀正常命令

例如合法 test/build 被错误分类成危险 mutation。

处理：

- Evidence Bundle 记录 blocked tool + reason；
- Codex 判断是 Task Contract 限制还是 classifier bug；
- 修改 policy 时使用更窄规则，不直接切 YOLO；
- 重新发新 operation。

---

## 16. Read-only mode 出现写入

`inspect` / `verify` 模式发现 task-introduced file mutation：

这是 policy violation。

检查：

- active tools 是否错误包含 edit/write；
- `tool_call` hook 是否未加载；
- bash allowlist 是否允许了 mutation；
- custom tool 是否绕开 policy。

修复 Harness 后重新运行；不能把“模型自己写了”当可接受行为。

---

## 17. Scope Drift

例：Worker 顺手重构/格式化无关模块、改无关依赖/配置。

处理：

```text
current changes - baseline changes = task-introduced changes
```

1. 找出越界 path；
2. 判断是否为需求必然传播；
3. 无依据 → REWORK；
4. 只撤销本 Run 引入的越界修改；
5. 不碰 baseline-owned changes。

禁止 `git reset --hard` 粗暴清理。

---

## 18. Path Guard 阻塞合法 Completeness propagation

例如初始 Scope 只列 service 文件，但修改签名后必须更新 caller/test。

处理：

- 不把 Path Guard 设计成静态 file whitelist；
- 记录新 path + propagation evidence；
- Codex 判断为 unfinished remainder 后扩大当前 Task Contract 的有效 scope；
- 新 operation 再修改。

---

## 19. Completeness remainder 被误当 follow-up

典型：

- caller 仍用旧签名；
- type/enum 变了但 validator/serializer 没同步；
- schema 变了但 existing data 未处理；
- sibling path 仍有同一 root cause；
- old path 已 orphaned。

处理：

- `COMPLETENESS_REVIEW`；
- 用搜索/调用链/contract evidence；
- unfinished → REWORK；
- different ticket → out-of-scope；
- 不因 targeted tests green 进入 VERIFYING。

---

## 20. Completeness 被误用成 Scope Expansion

如果 Worker/Codex 以完整性为理由：

- 新增未要求功能；
- 大范围重构；
- 升级依赖；
- 做全新架构；
- 解决无关旧债；

问：

> 不做这一项，当前 change 会被 Reviewer 称为 unfinished 吗？

不会 → different ticket。

---

## 21. Test Layer 不匹配

例：

- UI→API→DB 只跑 unit；
- schema/serialization 只 mock；
- 用户 skip E2E 却被写成 N/A。

处理：

```text
Unit: required | not-applicable
Integration: required | not-applicable
E2E: required | not-applicable | user-skipped
```

相关层不满足，不进入 `CODE_VERIFIED`。

---

## 22. Regression test 只在 fix 后绿

可确定性复现的 bug，如果 Worker 先修代码后补 green test：

- 不能算 RED→GREEN；
- 若可安全建立 unfixed 对照，要求同一 test 在 unfixed behavior 上 RED；
- 确认失败原因就是目标 bug；
- fix 后同一 test GREEN；
- Codex 独立重跑。

---

## 23. RED→GREEN 不适用

允许：不可控第三方、无法稳定 race、纯视觉无 harness、安全复现会有未授权副作用等。

记录：

```text
Regression proof: not-applicable
Reason: ...
Alternative evidence: ...
```

不能 fabricated RED，也不能跳过所有验证。

---

## 24. 修症状不修 Root Cause

要求 Review 明确：

```text
Symptom
Root cause
Same cause elsewhere
Regression boundary
```

同一根因仍存在于 reachable sibling site → Completeness remainder。

---

## 25. Rework 震荡

默认 3 个完整：

```text
Review → Rework → Re-review
```

达到后重新评估：

- Task Contract；
- root cause；
- Provider/model suitability；
- Harness tool policy；
- scope/completeness boundary；
- environment/dependency failure。

不要静默无限循环或直接切 YOLO。

---

## 26. One-way Door 被 Worker 尝试

包括：

- destructive migration；
- breaking API；
- auth relaxation；
- money/billing；
- credential changes；
- production mutation；
- irreversible deletion；
- push/merge/release/deploy。

Harness 应 block，并返回：

```text
blocked-decision-needed
```

若 Harness 没 block，视为 Harness defect。

---

## 27. Generated artifact / residue

常见：coverage、log、tmp patch、build output、debug file、lockfile。

区分：

- 本 Run 明确生成且按项目惯例可安全删除 → 可让 Pi cleanup；
- 来源/唯一性不明 → `deletion-candidate`；
- baseline 已存在 → 不删。

---

## 28. Closeout 文档与代码冲突

处理：

1. Source of Truth = final diff/code/schema/config/tests + Completeness evidence + Codex verification；
2. 实现明确 → closeout rework；
3. 如果冲突证明实现漏传播 → 退回 Completeness/Verification；
4. 不允许只改文档遮住错误代码。

---

## 29. Closeout 无法裁决 / 跨项目影响

例如另一仓库 consumer 受影响、需要 live evidence、两份权威文档冲突。

处理：

- `pending` / `out-of-scope`；
- 保留证据；
- 不把无法验证的事实写成 current truth；
- 必要时 BLOCKED 请求用户判断。

---

## 30. Sensitive data 进入 Evidence

如果 Evidence/log 包含 token、Authorization、secret value：

- 立即停止继续传播该日志；
- 不 commit；
- 修复 redaction；
- 按项目安全流程处理潜在泄漏；
- 以后只记录 credential status，不记录 value。

---

## 31. 用户取消

调用 Harness abort；然后：

- 等待/确认 abort；
- 检查 repository；
- 报告 partial progress；
- 不自动 rollback；
- 不把 CANCELLED 报成 FAILED 或 ACCEPTED。
