# AGY Supervised Development 3.0.1 Failure Modes

本文件把 **Pi 原生 CLI/session、现成 Extension、Provider 和 repository delivery** 的常见失败拆成可诊断状态。

原则：

> **先收证据，再动作；未知状态不猜成功；Pi runtime failure 不等于 repository progress 无效。**

---

## 1. Pi 不存在 / CLI capability 不足

```bash
command -v pi
pi --version
pi --help
```

缺失 `pi`、`--mode json` 或当前流程必需的 session 能力：

```text
→ BLOCKED
```

不自动全局安装/升级，除非用户明确要求。

---

## 2. Workflow Extension 缺失

如果 Task Contract 希望使用 `plan/build/review/debug`，但 `pi-agent-modes` 或等价 extension 没安装：

- 不发送不存在的 `--modes`；
- 不声称 read-only/tool guard 已生效；
- 可继续普通 Pi 时标 `mode_enforcement = unavailable/prompt-only`；
- 若当前安全边界必须程序化 read-only，则 `BLOCKED`，由用户选择可信扩展/隔离方式。

默认不自动安装 extension。

---

## 3. Pi Core `--mode` 与 Extension `--modes` 混淆

错误例子：把 `--mode build` 当成 workflow mode，或把 `--modes json` 当输出协议。

处理：

```text
Pi core:        --mode json | rpc | ...
workflow ext:   --modes plan | build | review | debug | ...
```

调用前以当前 `pi --help` / extension docs/capability 为准。

---

## 4. Session cwd mismatch

JSON session header 返回：

```text
cwd != repo_root
```

处理：

1. 停止使用该 session 作为本任务 Worker；
2. 检查错误 cwd/repo 是否已发生修改；
3. 不自动回滚来源不明改动；
4. 回到正确 repo root 新建/恢复正确 Pi session；
5. 重新验证 branch/baseline。

---

## 5. Session ID 丢失 / 不可恢复

- 不猜 ID；
- 不拿“最近一个 session”冒充当前任务；
- 保留 current repository state；
- 用 Task Contract + baseline + current diff + Review evidence 建 replacement session。

已 `CODE_VERIFIED` 时，只重建 Closeout 上下文。

---

## 6. Wrong / stale session resume

迹象：

- Pi 提到另一个项目；
- session header/cwd 不匹配；
- repository 当前事实与 session 上下文明显冲突。

处理：立即停止本 turn，检查 Git，换回真实当前 session 或重建 session。

Session continuity 是帮助，不是 repository truth。

---

## 7. JSON stream 截断 / 无 `agent_end`

可能是 Pi crash、Provider error、进程被中断或输出损坏。

处理：

1. 检查是否已取得真实 session header；
2. 检查 Git/tool effects；
3. 不对可能有写副作用的 turn 无脑 replay；
4. 能安全 resume 时继续同一 session；
5. 否则 replacement session + current repository evidence。

---

## 8. `agent_end` / 正常 exit，但没有 repository delivery

Pi turn 正常返回，但：

```bash
git status --short
git diff
```

没有 Task Contract 对应实现。

处理：

- 不接受；
- 检查 task understanding / cwd / provider result；
- `REWORK_REQUIRED` 或 `BLOCKED`；
- `agent_end != PASS`。

---

## 9. Provider 缺失

Provider 没注册/没配置：

```text
provider-missing → BLOCKED
```

不自动 `pi install`；由用户选择并审查 Provider。

---

## 10. OAuth / Auth required

Provider 存在，但 credential missing/expired/invalid：

```text
PROVIDER_AUTH_BLOCKED
```

- 不读取/展示 token；
- 不模拟登录；
- 不静默切 Provider；
- 用户自己完成 auth flow。

---

## 11. Antigravity 第三方集成风险

第三方 Pi Antigravity Provider 不是官方 AGY CLI。

如果 README/版本提示 ToS、账号封禁或 endpoint 风险：

- 如实报告；
- 不说成 Google 官方支持；
- 未经用户接受不自动安装/启用；
- credential 始终保持 Provider/Pi-owned。

---

## 12. Provider quota / transport / model failure

分类：

```text
401/auth       → PROVIDER_AUTH_BLOCKED
429/quota      → PROVIDER_CAPACITY_BLOCKED
timeout/5xx    → PROVIDER_TRANSIENT_FAILURE
model removed  → PROVIDER_CAPABILITY_FAILURE
```

保留 repository progress 和 session（若仍有效）。

Transient error 只做有限 safe retry；不无限重试。

Provider/model failover 默认不静默发生；只有用户/Task Contract 允许时切换并记录。

---

## 13. Read-only mode 实际发生写入

如果可信 extension 声称当前是 `plan/review` read-only，但 repository 出现 task-introduced mutation：

这是 policy violation。

检查：

- extension 是否真的加载；
- mode 是否正确；
- custom tool/bash 是否绕开 policy；
- 是否是 baseline/其他进程变化。

在确定 extension policy 正常前不要继续信任其 read-only 声明。

---

## 14. 没有 Extension 却把 Prompt 当 Tool Guard

禁止报告：

```text
"read-only enforced"
```

如果实际只是 prompt 写了“不要修改”。

正确写：

```text
mode_enforcement = prompt-only / unavailable
```

Codex 必须依赖最终 Git review 发现越界写入。

---

## 15. 为了绕过阻塞切 `yolo`

监督流程默认禁止把 `yolo` 当 fallback。

遇到 policy block：

- 判断是安全限制、Scope/one-way boundary，还是 extension false positive；
- 修正 Contract/选择更合适已知模式；
- 不静默解除所有保护。

---

## 16. Scope Drift

```text
current changes - baseline changes = task-introduced changes
```

发现无关 refactor/format/dependency/config：

1. 判断是否为必然 propagation；
2. 无依据 → REWORK；
3. 只撤销 Pi 本任务产生的越界改动；
4. 不碰 baseline-owned changes。

禁止 `git reset --hard` 粗暴清理。

---

## 17. Completeness propagation 超初始文件 Scope

初始 Scope 不应成为静态 whitelist。

如果新 caller/schema/test 是不更新就会 unfinished：

- Codex 用 blast-radius evidence 判定；
- 将它纳入当前 Task Contract propagation scope；
- resume 同一 Pi session 返工。

若只是邻近优化，则 different ticket。

---

## 18. Completeness remainder 被误当 follow-up

典型：caller 旧签名、validator/serializer 漏同步、schema existing data 漏处理、sibling 同根因仍可达。

处理：`COMPLETENESS_REVIEW → REWORK_REQUIRED`。

不能因 targeted tests green 进入 Verification。

---

## 19. Completeness 被误用成 Scope Expansion

判断：

> 不做这一项，当前 change 会被 Reviewer 称为 unfinished 吗？

不会 → different ticket。

不要借 completeness 升级依赖、做大重构、解决无关旧债。

---

## 20. Test Layer 不匹配

明确：

```text
Unit: required | not-applicable
Integration: required | not-applicable
E2E: required | not-applicable | user-skipped
```

UI→API→DB 等真实跨边界流程只跑 unit 不够。

用户 skip E2E 必须保留 `user-skipped`。

---

## 21. Regression test 只有 fix 后 GREEN

确定性 bug 如果 test 没证明 unfixed 时 RED：

- 不算完整 RED→GREEN；
- 能安全还原/对照时要求同一 test 在 unfixed behavior 上 RED；
- 确认失败原因是目标 bug；
- fix 后 GREEN；
- Codex 独立重跑。

---

## 22. RED→GREEN 不适用

允许：不可控第三方、unstable race、纯视觉无自动化、安全复现会造成未授权副作用等。

记录：

```text
Regression proof: not-applicable
Reason: ...
Alternative evidence: ...
```

不 fabricated RED，也不跳过全部验证。

---

## 23. 修症状不修 Root Cause

Review 必须能回答：

```text
Symptom
Root cause
Same cause elsewhere
Regression boundary
```

同根因仍存在于 reachable sibling → Completeness remainder。

---

## 24. Rework 震荡

默认 3 个：

```text
Review → Rework → Re-review
```

达到后重新评估：Task Contract、root cause、Provider/model、mode extension、scope/completeness、环境依赖。

不要静默无限循环。

---

## 25. One-way Door

包括：

- destructive migration；
- breaking API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- production mutation；
- irreversible delete；
- push/merge/release/deploy。

无明确授权 → `BLOCKED / blocked-decision-needed`。

Extension 能 block 更好，但最终授权边界由 Codex/用户决定，不依赖模型自觉。

---

## 26. Generated artifact / residue

coverage/log/tmp/build output/debug/lockfile：

- 明确本 turn 生成且按项目惯例可安全删除 → 可清理；
- 来源/用途不明 → `deletion-candidate`；
- baseline 已存在 → 不删除。

---

## 27. Closeout 文档与代码冲突

- final verified implementation 是优先事实；
- 实现明确 → Closeout rework；
- 如果文档冲突揭示代码传播漏改 → 退回 Completeness/Verification；
- 不只改文档遮住错误代码。

---

## 28. Closeout 无法裁决 / 跨项目影响

标：

```text
pending
out-of-scope
```

保留证据，不把无法验证的行为写成 current truth；必要时 BLOCKED 请求用户判断。

---

## 29. Sensitive data 出现在输出

如果 Provider/Pi diagnostics 包含 token、Authorization、secret：

- 不继续复制传播；
- 不 commit；
- 最终报告只记录 auth status，不记录 value；
- 按项目安全流程处理潜在泄漏。

3.0.1 没有自定义 Evidence Store，所以尤其不要为了“留证”把原始敏感 JSONL 复制进仓库。

---

## 30. 用户取消

停止当前 Pi invocation；RPC 模式下调用原生 abort。

随后：

- 检查 repository partial progress；
- 不自动 rollback；
- 报告当前安全状态；
- `CANCELLED` 或风险未决时 `BLOCKED`。
