---
name: agy-supervised-development
description: Use Codex as supervisor/reviewer and AGY (Antigravity CLI) as the primary implementer in an isolated tty7 pane, with capability detection, workspace binding, evidence-based review, rework loops, and independent acceptance.
version: 2.0.0
---

# AGY 监督开发

当用户明确使用 `$agy-supervised-development`，或明确要求采用“Codex 监督 + AGY 执行”开发时，按本流程工作。

核心角色固定为：

- **Codex = Supervisor / Reviewer / QA**：理解需求、建立基线、选择执行策略、审查真实 diff、独立运行验证、驱动返工、最终验收。
- **AGY = Implementer**：主要负责分析实现细节、修改生产代码、补测试、按返工意见修正。
- **Repository state = 真相来源**：AGY 的 `done`、摘要、自述测试结果都不是完成证明。

本 Skill 只定义监督编排主流程。AGY 参数、版本差异和已知限制见 `resources/agy-runtime.md`；故障分类见 `resources/failure-modes.md`；审查门禁见 `resources/review-gates.md`。

## 不可违反的边界

- 不把 AGY 的 `done`、自述测试结果或摘要当成完成证明。每个重要阶段都必须独立检查实际文件、`git diff`、构建和测试结果。
- 主要生产代码由 AGY 修改。Codex 负责监督、审查、验证和返工，不抢走主要实现工作；仅在 AGY 无法继续、用户明确要求或极小的监督性修补时例外，并必须在最终汇报说明。
- 只操作本次 Skill 创建的 tty7 workspace/pane。已有用户终端、其他 agent pane 和其他 workspace 一律只读，不得发送按键、关闭或复用。
- 不执行 push、merge、release、deploy、修改远端历史等外部操作，除非用户明确授权。
- 不使用“为了省事”而全局跳过权限确认的危险模式作为默认策略。权限、账号、网络、破坏性操作和跨范围访问必须保持可审计。
- 尊重仓库已有改动：先记录基线，不得为了“清理”回滚、覆盖或删除用户已有改动。
- 不因为 tty7 pane 的 CWD 正确，就假设 AGY 的内部 workspace/context 一定正确；必须显式校验或绑定。

## 1. 建立任务范围和 Git 基线

先确定仓库根目录并读取适用的项目规则文件，例如：

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- 项目内开发规范、OpenAPI/Schema/Contract 文件
- CI、lint、test、build 约定

记录基线：

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
```

必要时记录当前 HEAD：

```bash
git rev-parse HEAD
```

目的不是要求工作区必须干净，而是区分：

1. 用户在本任务之前已有的改动；
2. AGY 本次产生的改动；
3. 构建/测试产生的临时或生成文件。

若用户尚未给出具体开发目标，只完成环境和 AGY 连通性验证，不开始编码。

## 2. AGY Preflight：先检测能力，再决定怎么启动

不要把某个 AGY 版本的参数写死为永久事实。每次任务开始都做一次轻量能力检测：

```bash
command -v agy
agy --version 2>/dev/null || true
agy --help
```

同时检查 tty7：

```bash
tty7 doctor
tty7 agents
tty7 pane ls --all
```

根据 `agy --help` 的实际输出确认当前版本是否支持本次计划使用的能力，例如：

- workspace/directory 绑定能力（如 `--add-dir`）
- execution mode（如 `--mode`）
- reasoning effort（如 `--effort`）
- agent 选择（如 `--agent`）
- sandbox / permission 相关参数
- conversation / continue 能力

**规则：Capability Detection > Capability Assumption。**

如果文档记忆与本机 `agy --help` 冲突，以本机实际能力为准，并在最终汇报指出版本差异。

如果 tty7 服务不可达，停止 AGY 编排并告知用户；不要自行启动、重启或接管用户的 tty7 server。

## 3. 创建隔离 pane，并防止 AGY 串错项目

为本任务创建独立 tty7 workspace：

```bash
tty7 new --json "$repo_root"
```

从 JSON 结果取得新 pane 的数字 id，并使用 `%<id>` 作为唯一 pane 地址。

### 3.1 Workspace Binding Guard

AGY 可能维护独立于 shell CWD 的持久化项目/会话状态，因此不能只依赖 `tty7 new "$repo_root"`。

启动 AGY 时，优先采用当前版本实际支持的显式 workspace 绑定方式。若 `agy --help` 显示支持 `--add-dir`，优先：

```bash
tty7 send "%<id>" "agy --add-dir '$repo_root'" --enter
```

如果当前版本不支持 `--add-dir`，则启动交互模式后，要求 AGY 明确回报它正在工作的 repository/root，并通过读取目标仓库文件、`git rev-parse --show-toplevel` 等方式验证。

只有以下条件都满足才算 workspace 绑定成功：

1. tty7 pane 的 cwd 是 `repo_root`；
2. AGY 能实际读取目标仓库中的已知文件；
3. AGY 返回/执行得到的仓库 root 与 `repo_root` 一致；
4. 没有证据表明它沿用了另一个项目的旧上下文。

若发现上下文串项目，不允许继续编码；按 `resources/failure-modes.md` 处理。

### 3.2 启动和连通性验证

```bash
tty7 capture "%<id>" --plain
```

若出现项目 trust 界面，只有当路径准确等于 `repo_root` 且当前选项明确是信任该目录时，才可确认一次。其他权限、账号、联网或破坏性确认都要先停下。

AGY 进入交互提示后，发送一个轻量验证问题，例如要求它返回当前仓库 root、当前分支和一个已知项目文件名，再 capture：

```bash
tty7 capture "%<id>" --plain --scrollback
```

必须看到 AGY 的实际新响应，才认为启动成功。若 status hooks 可用，可用 `tty7 wait ... --changed` 避免把上一轮 stale `done` 当成当前回复；hooks 不可用时以 `capture` / `procs` 为准，不自行安装 hooks。

## 4. 根据任务复杂度选择 AGY 执行策略

不要所有任务都用同一种 AGY 模式。先结合本机能力和任务风险做选择。

### A. 小型、边界清晰的修改

例如：单点 bug、字段调整、小范围测试补充。

目标：减少 AGY 自身逐文件确认，让 Codex 在外层统一 Review。

若当前 AGY 支持自动接受编辑的 execution mode，可考虑使用类似 `accept-edits` 的模式；但仍不得自动放开高风险 shell/外部权限。

### B. 中型功能开发

默认采用：

1. Codex 建立 Task Contract；
2. AGY 理解现状并实现；
3. Codex 阶段性 Review；
4. AGY 返工；
5. Codex 独立验收。

### C. 大型重构、架构改造、跨模块变更

若 AGY 当前版本支持 plan mode，优先：

1. AGY 先产出实施计划；
2. Codex 审查计划是否满足仓库架构和需求；
3. 计划通过后才允许 AGY 实现；
4. 每个阶段都进行 Repository-level Review。

必要时，如果当前版本支持 reasoning effort，可对高复杂度任务选择更高推理级别，但不要仅因为“更强”就默认拉高所有任务成本。

## 5. 用 Task Contract 委派，而不是只丢一句自然语言

每次正式委派给 AGY 的任务，应尽量包含以下结构：

```text
Goal
- 本阶段必须实现什么。

Scope
- 允许修改哪些模块/目录/接口。

Context
- 当前架构、关键调用链、已有实现、基线改动。

Constraints
- 项目规则、兼容性、禁止事项、不能破坏的行为。

Acceptance Criteria
- 可被检查的完成条件。

Verification
- AGY 应运行哪些针对性测试/检查。

Forbidden Actions
- 不 push / merge / deploy；不回滚用户已有改动；不扩大任务范围。

Report
- 完成后报告修改文件、关键设计、实际执行的测试及失败项。
```

Task Contract 的目的不是让提示词变长，而是降低“AGY 自己补全错误假设”的概率。

## 6. 分阶段监督，而不是等最后一次性验收

任务较长时拆成可检查阶段，例如：

1. 理解现状与实施方案；
2. 核心实现；
3. 边界和错误处理；
4. 测试；
5. 收尾。

每个重要阶段，包括 AGY 第一次说 `done` 之后，都执行同一个闭环：

1. capture AGY 的实际终端输出，确认它声称做了什么；
2. Codex 在自己的 shell 独立读取 repository state；
3. 对照 Task Contract 和项目规则 Review；
4. 通过才进入下一阶段；
5. 有问题则把**带证据的返工意见**发回同一个 pane；
6. AGY 修正后重新执行完整 Review 闭环。

最低检查集合：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

必要时再用：

```bash
rg <symbol-or-pattern>
```

检查调用链、重复实现、遗漏分支、错误处理、权限、时区、持久化、API 契约、生成物和测试覆盖。

完整 Review Gate 见 `resources/review-gates.md`。

## 7. 返工意见必须可执行、可验证

不要只发送：

```text
这里有问题，请修复。
```

优先包含：

- 文件路径和行号（若能确定）；
- Codex 实际观察到的行为；
- 它违反的需求 / 项目规则 / contract；
- 期望行为；
- 建议关注的调用链或边界；
- 修正后必须重跑的测试。

示例结构：

```text
Issue
- services/foo/...: 当前 XXX 在 YYY 情况下会返回 ZZZ。

Evidence
- diff 中新增逻辑只处理了 A，没有处理 B；现有测试也未覆盖 B。

Expected
- A/B 两种输入都应遵循同一个 contract。

Rework
- 修正实现并补一个 B 场景测试；完成后重跑 <command>，把真实结果告诉我。
```

Codex 之后仍要自己重跑验证，不能把 AGY 的复测结果直接当成验收结果。

## 8. 独立构建、测试和最终验收

实现稳定后，Codex 自己运行仓库规定的质量门禁；AGY 跑过的命令不算独立验证。

优先级：

1. 仓库 `AGENTS.md` / README / CI 明确规定的命令；
2. 与改动直接相关的 targeted tests；
3. lint / typecheck / unit tests；
4. integration / package / build；
5. 必要的配置校验。

若某项门禁不适用，要说明原因；若失败，保留失败证据并通过 tty7 交给 AGY 修正，然后由 Codex 独立重跑。

最终再做一次：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

确认没有：

- 临时文件；
- debug 输出；
- 无关格式化；
- 意外生成物；
- 用户基线改动被覆盖；
- 超出 Task Contract 的改动。

验收完成的必要条件：

- 需求逐项满足；
- 关键边界已审查；
- 项目架构/契约未被破坏；
- 独立门禁通过或失败项已明确解释；
- 最终 diff 可解释；
- 没有未经授权的外部副作用。

任何关键项不满足，都不能把任务标记为完成。

## 9. 故障和阻塞处理

遇到以下情况，不要盲目重复发送命令：

- AGY 启动失败；
- AGY 没有新输出；
- AGY 停在 trust / auth / permission；
- workspace/context 疑似串项目；
- AGY 进程退出；
- 长任务 timeout；
- AGY 声称完成但 repository 没有对应改动；
- 测试失败；
- AGY 反复修不好同一个问题。

先 capture/procs/真实 Git state 定位，再按 `resources/failure-modes.md` 的分类处理。

## 10. 结束和汇报

任务完成后，只清理本 Skill 创建的 pane。若用户要求保留终端供后续跟进，则保留并明确 pane 地址。

最终中文汇报至少包含：

- AGY 完成了什么；
- 修改了哪些核心文件；
- Codex 独立 Review 发现了什么问题；
- 进行了哪些返工，以及返工结果；
- Codex 实际运行了哪些构建/测试及结果；
- 当前 AGY 版本/能力是否影响了执行策略；
- 仍存在的风险、未覆盖项或待办；
- 明确说明是否执行过 push / merge / deploy（默认应为没有）。

最终汇报要基于真实 repository state 和命令结果，而不是复述 AGY 的总结。
