# AGY Supervised Development Failure Modes

本文件用于把“卡住了”拆成可诊断状态。原则：**先收集证据，再采取动作；不要盲目重复 send，不要把未知状态猜成成功。**

## 1. AGY binary 不存在

### 证据

```bash
command -v agy
```

无输出或退出非 0。

### 处理

- 停止监督开发；
- 告知用户本机找不到 `agy`；
- 不自行安装、升级或修改全局 PATH，除非用户明确要求。

---

## 2. tty7 Server 不可达

### 证据

```bash
tty7 doctor
```

报告 server unreachable。

### 处理

- 不自行 `tty7 server start/restart`；
- 不接管其他 pane；
- 向用户报告阻塞点。

---

## 3. AGY 没有 tty7 Status Hook

这不是自动失败。

### 证据

`tty7 doctor` / `tty7 agents --json` 显示 AGY/Antigravity 可被识别，但没有 status hook 或不能报告 `working/waiting/done`。

### 处理

- 标记本 Run `tty7_status_mode=capture-fallback`；
- 不调用依赖 AGY native `done` 的 wait 作为正常完成条件；
- 使用 `tty7 agents + capture + Turn Nonce` 观察；
- 不自行安装 hook。

如果未来当前 tty7 版本已经支持 AGY hook，则按真实检测结果切回 native-status。

---

## 4. Fresh Pane 启动命令没有执行

### 现象

第一次：

```bash
tty7 send "$PANE" "agy ..." --enter
```

返回成功，但 capture 中完整 `agy ...` 仍停在 shell prompt。

### 原因

新 shell 仍执行启动脚本，第一次 Enter 被吞。

### 处理

```bash
tty7 capture "$PANE" --plain | tail -5
tty7 send "$PANE" --enter
```

只补 Enter 一次。不要重新发送完整 `agy` 命令，否则可能启动两个 AGY。

---

## 5. `tty7 procs` 显示 Nothing Running

### 规则

不要由此推断 AGY died。

coding-agent detection/status 与普通 foreground process observation 不是同一通道。

### 检查顺序

```bash
tty7 agents --json
tty7 pane ls --all --json
tty7 capture "$PANE" --plain
```

只有 pane 真退出或有其他直接证据，才进入 worker-exit 路径。

---

## 6. AGY 启动后没有可确认的新进展

### 可能原因

- 仍在启动；
- 第一次 Enter 被吞；
- 停在 trust/auth/permission；
- AGY 没有 native status hook；
- TUI 正在工作但 capture 片段不足；
- API/connection error 后已回 prompt；
- pane 已退出；
- 当前 pane 不是本 Run 所有的 pane。

### 处理

1. 核对 Run Context 的 `$PANE`；
2. `tty7 agents --json`；
3. capture 足够多的当前 screen；
4. 区分 active / input-required / error / marker / prompt / unknown；
5. `UNKNOWN` 时继续有界观察或诊断，不重复发送相同 Task Contract。

---

## 7. Trust / Auth / Permission 阻塞

### Trust

只有路径准确等于当前 `repo_root`，且确认项明确表示信任该目录时，才允许确认一次。

### Auth

账号登录、OAuth、订阅/配额属于用户控制范围，默认暂停。

### Permission

只允许 Task Contract 内、本地、低风险操作继续。workspace 外访问、外部系统、破坏性命令、发布动作必须停止。

### tty7 操作规则

任何 Enter/方向键/确认之前先重新 capture：**Read Before Send**。

---

## 8. Workspace / Context 串项目

这是高优先级故障。

### 迹象

- AGY 提到另一个项目名；
- AGY 返回的 root 与 `repo_root` 不一致；
- branch 不一致；
- AGY 找不到当前仓库已知文件，却描述旧项目；
- AGY 修改 workspace 外路径；
- 恢复了不属于本任务的旧 conversation。

### 处理

1. 立即停止正式 Turn；
2. capture 留证；
3. 检查 Git state，确认是否已有误改；
4. 不直接删除/回滚未知改动；
5. 只清理本 Run 创建的错误 worker workspace；
6. 新建隔离 tty7 workspace；
7. 使用当前 AGY 支持的显式 directory/project 绑定；
8. 重新 Workspace Verification；
9. 确认无误后再继续。

---

## 9. 当前 Turn 没有出现 Nonce

### 可能情况

- AGY 仍在工作；
- AGY 忘了输出 marker；
- turn 因错误中断；
- permission/question 卡住；
- TUI 已返回 prompt，但 marker 被遗漏。

### 处理

Nonce 是 completion hint，不是唯一真相。

- capture 当前画面；
- 有 native status 时结合 status；
- 如果明确回到 prompt 且 turn 内容已经返回，可进入 Review，但记录 marker missing；
- 如果不能可靠判断，保持 `OBSERVING` / `UNKNOWN`；
- 不为了拿 marker 而盲目再发一句 prompt，先判断当前 UI。

---

## 10. AGY 声称 Done / TURN_COMPLETE，但 Git 没有对应改动

### 检查

```bash
git status --short
git diff --stat
git diff
```

### 处理

- 不接受完成；
- 明确告诉 AGY 实际 repository state 不满足 Task Contract；
- 要求定位写入位置；
- 重点检查 workspace/context 串项目；
- 仍按 Git 证据 Review。

---

## 11. Scope Drift

### 例子

- 顺手重构无关模块；
- 大面积格式化；
- 改无关配置/依赖；
- 删除用户已有文件；
- API contract 改了但需求不需要。

### 处理

1. 从 baseline 中扣除用户已有 changed paths；
2. 找出 AGY 本任务新增的越界 paths；
3. 判断是否为需求必要；
4. 无依据则 `REWORK`；
5. 要求 AGY 只撤销它自己引入的越界改动；
6. Codex 再检查 baseline integrity。

禁止用 `git reset --hard` 粗暴清理。

---

## 12. 测试失败

分类：

1. 本次真实回归；
2. 测试需要合理更新；
3. 环境/依赖问题；
4. 与本任务无关的既有失败；
5. flaky / 外部服务不可用。

把失败命令、关键错误、相关文件、预期行为作为 Evidence 发给 AGY。修复后 Codex 独立重跑。

---

## 13. Rework 震荡

默认 3 个完整 `Review → Rework → Re-review` 周期为 soft limit。

达到后必须重新评估：

- 同一缺陷是否反复出现；
- 是否修 A 坏 B；
- Task Contract 是否不清；
- 根因是否判断错；
- 是否架构冲突；
- 是否环境故障。

不要静默无限循环。必要时 `BLOCKED` 并向用户报告当前安全状态。

---

## 14. AGY API / Connection Error，但 TUI 仍活着

### 处理

1. capture 错误和当前 prompt；
2. 检查 Git state；
3. 如果 TUI 已回到可输入状态，Read Before Send；
4. 在同一 pane 告诉 AGY：上一 turn 中断，请基于已有改动继续；
5. 为恢复 Turn 使用新 nonce。

不要立即启动第二个 Writer 同时修改同一 checkout。

---

## 15. Worker Pane 真正退出

### 处理

1. 先 `git status` / `git diff`；
2. Review 已产生的有效工作；
3. 不自动回滚，不自动从头开始；
4. 需要继续时才创建 replacement tty7 workspace/pane；
5. 有真实、经过验证的 AGY conversation id 才尝试 `--conversation`；
6. 没有就用 Task Contract + 当前 diff + Review Evidence 重建上下文。

Worker failure 不等于 Run progress 丢失。

若已经 `CODE_VERIFIED`，replacement worker 应优先使用 final diff + Closeout Contract 继续知识收尾，不无证据重做已验证实现。

---

## 16. 长时间 `UNKNOWN`

AGY 无 hook 的 fallback 模式可能出现 screen 难以判断。

### 处理

- 使用合理间隔做有界观察；
- 检查 `tty7 agents --json` 是否仍识别 AGY；
- capture 更完整 screen，而不是只 tail 极少几行；
- 看是否有 visible error / prompt / permission；
- 若长期无可靠变化，进入 `BLOCKED` 或 failure diagnosis，而不是无限 polling。

---

## 17. 生成物 / 临时文件污染

常见：build output、coverage、log、临时 patch、debug 文件、IDE metadata、意外 lockfile。

先确认是否是项目应提交产物，并区分来源：

- **能明确证明由本轮 AGY 生成，且按项目惯例属于可安全移除的临时/构建残留**：可要求 AGY 清理，再 Review Git state；
- **来源、唯一性或用途不明确**：不要因“收尾”直接删除，列为 `deletion-candidate` 并报告；
- **baseline 已存在**：不得当成本轮 residue 回滚或删除。

---

## 18. Closeout 发现文档与代码冲突

### 例子

- README 仍写旧 CLI 参数；
- API 文档与最终 response schema 不一致；
- `AGENTS.md` 指向已经退役的目录；
- 配置说明仍把旧环境变量标为现役；
- 示例与测试证明的默认行为相反。

### 处理

1. 先确定 Source of Truth：final diff、当前代码/schema/config/tests 和 Codex 已验证结果；
2. 如果最终实现明确，形成 `CLOSEOUT REWORK` Evidence，让同一 AGY worker 就地同步现役知识面；
3. 如果冲突暴露的是实际代码缺陷，退回实现 Review / Verification；
4. 不允许只改文档去掩盖错误代码，也不允许为了迎合旧文档改坏已验证实现；
5. 修复后重新做 stale-reference search 和 Gate 12 Review。

---

## 19. Closeout 无法裁决 / 跨项目影响

### 情况

- 两个现役文档互相冲突，当前代码不足以判断产品预期；
- 公共 Contract 改动影响另一个仓库，但当前任务没有跨项目写权限；
- 需要 production/live evidence 才能确认“已上线”；
- 需要删除、重命名或外部权限才能完成知识统一。

### 处理

- 标记对应知识面 `pending` 或 `out-of-scope`；
- 保留双方证据和当前安全状态；
- 不把无法验证的结论写成“已完成”；
- 不因为 Closeout 自动扩大 memory、deploy、跨项目或删除权限；
- 必要时进入 `CLOSEOUT BLOCKED` 并明确 `Decision needed`。

---

## 20. 外部副作用请求

AGY 若准备：

- push；
- merge；
- deploy；
- release；
- 删除远端资源；
- 写生产数据库；
- 创建云资源；

默认停止并交由用户决定。监督开发默认止于本地 repository 可验收状态。

Knowledge Closeout 不改变这条边界；“为了验证文档”也不能擅自 deploy 或改远端资源。

---

## 21. Cleanup 风险

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

Knowledge Closeout 报告的用户文件、计划文档、backup、历史资料等 `deletion-candidate` 不属于 tty7 cleanup。

如果 `ws rm` 因状态异常需要进一步处理，先检查 ownership 和 pane 内容，不要扩大清理范围。