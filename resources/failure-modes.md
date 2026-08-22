# AGY Supervised Development Failure Modes

本文件用于把“卡住了 / 看起来完成了但其实没有”拆成可诊断状态。原则：**先收集证据，再采取动作；不要盲目重复 send，不要把未知状态猜成成功。**

## 1. AGY binary 不存在

```bash
command -v agy
```

无输出或退出非 0：停止监督开发并报告；不自行安装、升级或修改全局 PATH，除非用户明确要求。

---

## 2. tty7 Server 不可达

```bash
tty7 doctor
```

报告 server unreachable：

- 不自行 `tty7 server start/restart`；
- 不接管其他 pane；
- 向用户报告阻塞点。

---

## 3. AGY 没有 tty7 Status Hook

这不是自动失败。

证据：`tty7 doctor` / `tty7 agents --json` 显示 AGY 可识别，但没有 `working/waiting/done` hook。

处理：

- `tty7_status_mode=capture-fallback`；
- 使用 `tty7 agents + capture + Turn Nonce`；
- 不等待不存在的 native `done`；
- 不自行安装 hook。

---

## 4. Fresh Pane 启动命令没有执行

第一次 `send --enter` 返回成功，但 capture 中完整 `agy ...` 仍停在 shell prompt。

处理：

```bash
tty7 capture "$PANE" --plain | tail -5
tty7 send "$PANE" --enter
```

只补 Enter 一次。不要重发完整 `agy` 命令，避免启动两个进程。

---

## 5. `tty7 procs` 显示 Nothing Running

不要由此推断 AGY died。按顺序检查：

```bash
tty7 agents --json
tty7 pane ls --all --json
tty7 capture "$PANE" --plain
```

只有 pane 真退出或有其他直接证据，才进入 worker-exit 路径。

---

## 6. AGY 启动后没有可确认的新进展

可能是启动中、Enter 被吞、trust/auth/permission、无 native hook、TUI active、API error、pane exit 或读错 pane。

处理：

1. 核对 Run Context `$PANE`；
2. `tty7 agents --json`；
3. capture 足够多 screen；
4. 区分 active / input-required / error / marker / prompt / unknown；
5. `UNKNOWN` 时继续有界观察，不重复发送 Task Contract。

---

## 7. Trust / Auth / Permission 阻塞

- Trust：只有路径准确等于 `repo_root` 才可确认。
- Auth：账号登录、OAuth、订阅/配额默认交给用户。
- Permission：只允许 Task Contract 内、本地、低风险操作；workspace 外访问、外部系统、破坏性命令、发布动作必须停止。
- 所有按键前继续 **Read Before Send**。

---

## 8. Workspace / Context 串项目

迹象：AGY 提到别的项目、root/branch 不一致、找不到当前已知文件、修改 workspace 外路径、恢复了错误 conversation。

处理：

1. 立即停止正式 Turn；
2. capture 留证；
3. 检查 Git state；
4. 不直接删除/回滚未知改动；
5. 只清理本 Run 创建的错误 worker workspace；
6. 新建隔离 worker；
7. 显式绑定目录；
8. 重新 Workspace Verification。

---

## 9. 当前 Turn 没有出现 Nonce

Nonce 是 completion hint，不是唯一真相。

- capture 当前画面；
- 有 native status 时结合 status；
- 明确回到 prompt 且 turn 内容已经返回，可进入 Review，但记录 marker missing；
- 不能可靠判断则保持 `OBSERVING` / `UNKNOWN`；
- 不为拿 marker 盲目再发 prompt。

---

## 10. AGY 声称 Done / TURN_COMPLETE，但 Git 没有对应改动

```bash
git status --short
git diff --stat
git diff
```

处理：

- 不接受完成；
- 告诉 AGY repository state 不满足 Task Contract；
- 要求定位写入位置；
- 检查 workspace/context 串项目；
- `TURN_COMPLETE` 只能让 Turn 返回，不能让实现 Gate PASS。

---

## 11. Scope Drift

例子：顺手重构无关模块、大面积格式化、改无关配置/依赖、删除用户已有文件。

处理：

1. 从 baseline 扣除用户已有 changed paths；
2. 找出 task-introduced 越界 paths；
3. 判断是否需求必要；
4. 无依据则 `REWORK`；
5. 只撤销 AGY 自己引入的越界修改；
6. 重查 baseline integrity。

禁止 `git reset --hard` 粗暴清理。

---

## 12. Completeness Remainder 被误当成 Follow-up

### 现象

当前 changed files 编译/测试都绿，但：

- 仍有 caller 使用旧函数签名；
- indirect/barrel/script caller 被漏掉；
- enum/type 已变但 validator/serializer 没同步；
- schema 已变但 existing data 必须的 backfill 没处理；
- 新状态可达但 error/empty/permission path 没实现；
- old path 已失去意义却仍 orphaned；
- 同一 root cause 在 sibling site 仍存在。

### 处理

- 进入 `COMPLETENESS_REVIEW`；
- 使用 `rg` / 调用链 / contract evidence；
- 判断是 `unfinished` 还是 `different ticket`；
- unfinished → `REWORK_REQUIRED`；
- different ticket → `out-of-scope-different-ticket`；
- 不能因为 targeted tests green 就进入 `VERIFYING`。

---

## 13. Completeness 被误用成 Scope Expansion

### 现象

AGY/Codex 以“完整”为理由顺便：

- 新增未要求功能；
- 做邻近重构；
- 升级依赖；
- 建全站新架构；
- 处理与本 change 无必然关系的旧债。

### 判断

> 如果不做这一项，现在的 change 会被 Reviewer 称为 unfinished 吗？

- 会 → completeness；
- 不会，只是另一个有价值工作 → different ticket。

无法判断时不要扩大 Scope，必要时 `BLOCKED`。

---

## 14. Test Layer 不匹配

### 例子

- UI→API→DB 的新流程只跑 unit tests；
- schema/serialization 改动只 mock DB；
- 用户明确说 skip E2E，却被记录为 `not-applicable`；
- 项目已有 E2E harness，但关键跨边界 flow 完全没覆盖。

### 处理

明确：

```text
Unit: required | not-applicable
Integration: required | not-applicable
E2E: required | not-applicable | user-skipped
```

相关层未满足则 Gate 7/9 不 PASS。

`user-skipped` 是显式 trade-off，必须在最终报告保留，不能偷换成 N/A。

---

## 15. Regression Test 只在修复后跑过

### 现象

Bug 可确定性自动复现，但 AGY 先改 production code，再补了一个 green test。

### 风险

这个 test 可能在 unfixed code 上本来就会 green，不能证明它能捕获回归。

### 处理

- 若可安全还原/对照 unfixed behavior，要求观察同一 regression test 在 unfixed 状态 RED；
- 确认失败原因就是目标 bug；
- 再证明 root-cause fix 后同一 test GREEN；
- Codex 独立重跑。

没有 RED evidence 时，不报告为完整 RED→GREEN proof。

---

## 16. RED→GREEN 不适用

允许情况：不可控第三方、无法稳定复现 race、纯视觉且无 harness、构建环境本身故障、安全复现会产生不允许的外部副作用。

处理：

```text
Regression proof: not-applicable
Reason: <为什么无法安全/确定性 red>
Alternative evidence: <fixture/static check/manual repro/targeted integration>
```

不能 fabricated RED，也不能因此跳过所有验证。

---

## 17. 修了症状，没有修 Root Cause

例子：

- double submit 只禁用按钮，服务端仍可重复创建；
- catch exception 隐藏 transaction bug；
- caller 加 null guard，但 public service 仍可被其他 caller 触发；
- 只修第一个 endpoint，同类 unscoped query 仍存在。

处理：要求明确：

```text
Symptom
Root cause
Same cause elsewhere
Regression boundary
```

同一根因的可达 sibling sites 属于 Completeness Sweep。

---

## 18. 普通测试失败

分类：

1. 本次真实回归；
2. 测试需要合理更新；
3. 环境/依赖问题；
4. 与本任务无关的既有失败；
5. flaky / 外部服务不可用。

把失败命令、关键错误、相关文件、预期行为作为 Evidence 发给 AGY。修复后 Codex 独立重跑。

---

## 19. Rework 震荡

默认 3 个完整 `Review → Rework → Re-review` 周期为 soft limit。

达到后重新评估：

- 同一缺陷是否反复出现；
- 是否修 A 坏 B；
- Task Contract 是否不清；
- 根因是否判断错；
- completeness 边界是否错；
- 是否架构/环境故障。

不能静默无限循环。

---

## 20. One-way Door 被 Completeness 触发

Completeness 发现要完整交付似乎需要：

- destructive/non-additive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- secrets/credentials；
- production mutation；
- irreversible deletion。

处理：

- 不自行决定；
- 尽量完成不依赖该决定的安全工作；
- remainder 标 `blocked-decision-needed`；
- 进入 `BLOCKED` 并向用户呈现证据和选项。

---

## 21. AGY API / Connection Error，但 TUI 仍活着

1. capture 错误和当前 prompt；
2. 检查 Git state；
3. TUI 已回可输入状态时 Read Before Send；
4. 同一 pane 基于已有改动继续；
5. 恢复 Turn 使用新 nonce。

不要立即启动第二个 Writer 同时修改同一 checkout。

---

## 22. Worker Pane 真正退出

1. 先 `git status` / `git diff`；
2. Review 已产生的有效工作；
3. 不自动回滚，不自动从头开始；
4. 需要继续才创建 replacement worker；
5. 只有真实、经过验证的 conversation id 才 resume；
6. 否则用 Task Contract + 当前 diff + Review/Completeness Evidence 重建上下文。

如果已经 `CODE_VERIFIED`，replacement worker 只需继续 Closeout，不重做已验证实现。

---

## 23. 长时间 `UNKNOWN`

- 使用合理间隔有界观察；
- 检查 `tty7 agents --json`；
- capture 更完整 screen；
- 看 visible error / prompt / permission；
- 长期无可靠变化则 `BLOCKED` / failure diagnosis，不无限 polling。

---

## 24. 生成物 / 临时文件污染

常见：build output、coverage、log、临时 patch、debug 文件、IDE metadata、意外 lockfile。

区分来源：

- 明确由本轮 AGY 生成、按项目惯例可安全移除 → 可让 AGY 清理；
- 来源/唯一性/用途不明确 → `deletion-candidate`，不直接删；
- baseline 已存在 → 不得当成本轮 residue 回滚或删除。

---

## 25. Closeout 发现文档与代码冲突

例子：README 仍写旧 CLI、API 示例还是旧 schema、rules 指向退役目录、配置说明仍把旧 env 当现役。

处理：

1. Source of Truth = final diff + code/schema/config/tests + Completeness evidence + Codex verification；
2. 实现明确 → `CLOSEOUT REWORK`，由同一 AGY worker 同步知识面；
3. 若冲突证明实现传播没做完整 → 退回 `COMPLETENESS_REVIEW` / `VERIFYING`；
4. 不允许只改文档掩盖错误代码；
5. 修复后重做 stale-reference search 和 Gate 13 Review。

---

## 26. Closeout 无法裁决 / 跨项目影响

- 两份现役文档冲突，代码不足以裁决产品预期；
- 公共 Contract 影响另一仓库，但当前无跨项目写权限；
- 需要 production/live evidence 才能确认“已上线”；
- 需要删除/重命名/外部权限才能统一。

处理：标 `pending` / `out-of-scope`，保留证据，不把无法验证的事实写成完成，不扩大 memory/deploy/跨项目/删除权限。必要时 `CLOSEOUT BLOCKED`。

---

## 27. 外部副作用请求

AGY 若准备 push、merge、deploy、release、删远端资源、写生产数据库、创建云资源，默认停止并交用户决定。

Completeness / Verification / Closeout 都不改变这条边界。

---

## 28. Cleanup 风险

正常仅清理当前 Run 创建的 workspace：

```bash
tty7 ws rm "$WS"
```

禁止：

```text
tty7 pane close --orphans
tty7 server stop
tty7 server restart
关闭其他 workspace/pane
```

知识收尾报告的用户文件、计划文档、backup、历史资料等 `deletion-candidate` 不属于 tty7 cleanup。