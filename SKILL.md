---
name: agy-supervised-development
description: Use Codex as supervisor/reviewer and AGY (Antigravity CLI) as the primary implementer in a dedicated tty7 workspace, with tty7-native pane ownership, AGY capability detection, fallback turn completion markers, evidence-based review, rework loops, and independent acceptance.
version: 2.1.0
---

# AGY 监督开发

当用户明确使用 `$agy-supervised-development`，或明确要求采用“Codex 监督 + tty7 + AGY 执行”开发时，按本流程工作。

核心角色固定为：

- **Codex = Supervisor / Reviewer / QA**：理解需求、建立 Git baseline、创建和管理本次 tty7 worker workspace、委派 AGY、审查真实 repository state、驱动返工、独立验证并最终验收。
- **tty7 = Worker Runtime**：提供持久 PTY、独立 workspace/pane、agent detection、send/capture/wait 等运行时能力；不要在 Skill 内重复造进程管理器。
- **AGY = Implementer / Sole Primary Writer**：主要负责实现生产代码、补测试、执行针对性验证和按证据返工。
- **Repository state = 真相来源**：AGY 的 `done`、总结、测试自述和 turn marker 都不是完成证明。

本 Skill 只定义监督编排主流程。AGY 运行时见 `resources/agy-runtime.md`；tty7 操作协议见 `resources/tty7-supervision.md`；监督状态与 Turn 协议见 `resources/run-lifecycle.md`；故障见 `resources/failure-modes.md`；审查门禁见 `resources/review-gates.md`。

## 不可违反的边界

- 只有 Codex 可以把任务判定为 `ACCEPTED`。AGY 的 `done` 或 `TURN_COMPLETE` 最多表示当前 worker turn 返回。
- 主要生产代码由 AGY 修改。Codex 负责监督、Review、验证和返工；仅在 AGY 无法继续、用户明确要求或极小的监督性修补时例外，并在最终汇报说明。
- 每个监督任务创建独立 tty7 workspace + pane。只操作本次任务保存的稳定 workspace id 和 pane id；已有用户 pane、其他 agent pane 和其他 workspace 一律只读。
- 不缓存 `@N` 作为 worker identity；tab 序号会漂移。优先保存 `tty7 new --json` 返回的 workspace id 和 pane id。
- 不执行 `tty7 server stop`、`tty7 server restart`、`tty7 pane close --orphans`，不清理不是本 Skill 创建的资源。
- 不因为 `tty7 send` 成功就认为命令启动成功；新 pane 第一次 send 后必须做 Launch Proof，防止 shell 启动期吞掉 Enter。
- 不因为 `tty7 procs` 显示空就认为 AGY 已退出；coding agent 存活判断优先看 `tty7 agents` 和实际 pane 画面。
- 不假设 AGY 一定有 tty7 status hook。Preflight 必须判断当前 tty7/AGY 是否能提供 native agent state；没有则使用 Turn Nonce + capture fallback。
- 任何向 AGY 的 `send`、Enter、方向键、Escape、Ctrl-C 等操作之前，都先读取当前 pane：**Read Before Send**。
- 不执行 push、merge、release、deploy、远端历史修改等外部操作，除非用户明确授权。
- 不默认使用全局跳过权限确认的危险模式；权限、账号、联网、破坏性操作和跨范围访问必须可审计。
- 尊重仓库已有改动：先记录 baseline，不得为了“清理”回滚、覆盖或删除用户已有改动。
- 不因为 tty7 pane 的 cwd 正确，就假设 AGY 的内部 workspace/context 一定正确；必须显式绑定或验证。

## 1. 建立任务范围和 Git Baseline

先确定仓库根目录并读取适用规则：

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- 项目开发规范
- OpenAPI / Schema / Contract
- CI / lint / test / build 约定

记录：

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

必要时保存 baseline 的具体 changed paths / diff，以便后续判断 scope drift 时区分用户已有改动和 AGY 本轮新增改动。

本流程默认让唯一 Writer AGY 工作在用户当前 checkout，因为未提交改动可能正是任务上下文。只有多 Writer 并行、高风险隔离实验、或用户明确要求时才改用独立 worktree；不要机械套用 worktree。

若用户尚未给出具体开发目标，只做环境和连通性验证，不开始编码。

## 2. Preflight：检测 AGY 与 tty7 的真实能力

AGY：

```bash
command -v agy
agy --version 2>/dev/null || true
agy --help
```

tty7：

```bash
tty7 doctor
tty7 agents --json
tty7 pane ls --all --json
```

检查两类能力：

### AGY capabilities

根据 `agy --help` 实际确认：

- workspace/directory 绑定（如 `--add-dir`）
- execution mode（如 `--mode`）
- reasoning effort（如 `--effort`）
- sandbox / permission
- conversation resume
- 其他本任务准备使用的参数

规则：**Capability Detection > Capability Assumption**。

### tty7 AGY status capability

检查 `tty7 doctor` / `tty7 agents --json` 是否表明当前 Antigravity/AGY 有可用状态 hook。

- **若有 native status**：后续可以用 `tty7 wait "$PANE" --until waiting,done --changed ...`。
- **若 AGY 只能被识别、没有 status hook**：这是可支持的正常降级，不要阻塞任务；后续走 capture + Turn Nonce fallback。
- **若 tty7 server 不可达**：停止并告知用户；不要自行启动或重启 server。
- 不自行安装/修改 tty7 或 AGY hooks，除非用户明确要求。

## 3. 创建独立 tty7 Worker Workspace

使用 `tty7 new --json`，不要默认 split 用户当前窗口：

```bash
read -r WS PANE < <(
  tty7 new --json "$repo_root" |
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"], "%%%d" % d["pane"])'
)
```

把 `WS` 和 `PANE` 放入当前监督 Run Context。它们是本任务 tty7 ownership 的唯一依据。

必要时核对：

```bash
tty7 ws tree "$WS"
tty7 pane ls --all --json
```

必须确认新 pane 的 cwd 与 `repo_root` 对应。之后所有 `send` / `capture` / cleanup 都必须显式使用 `$PANE` / `$WS`，避免误操作调用者自己的 pane。

## 4. 启动 AGY，并证明真的启动了

优先使用 AGY 当前版本支持的显式 workspace 绑定。如果 `--add-dir` 可用：

```bash
tty7 send "$PANE" "agy --add-dir '$repo_root'" --enter
```

否则启动普通交互 AGY，并在下一步做严格 workspace verification。

### Launch Proof：新 pane 第一次 send 后强制检查

新 shell 还在跑启动脚本时可能吞掉第一次 Enter。发送启动命令后立刻：

```bash
tty7 capture "$PANE" --plain | tail -5
```

若启动命令仍停在 shell prompt、没有执行，只补一次：

```bash
tty7 send "$PANE" --enter
```

不要重复发送整条 `agy ...`，避免启动两个进程。

之后用：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

确认 `$PANE` 中实际识别到了 AGY / Antigravity 且交互界面已出现。`tty7 procs` 不是 coding-agent 存活证明，不要把 `nothing running` 误判为 AGY 死亡。

如果出现 trust 界面，只有路径准确等于 `repo_root` 且当前选项明确表示信任该目录时才可确认一次。账号、OAuth、联网授权、危险权限等交给用户决定。

## 5. Workspace Binding Verification

AGY 可能维护独立于 shell CWD 的持久化 project/conversation context。因此进入正式任务前，要求 AGY 回报或实际执行：

```text
- 当前 repository root
- 当前 branch
- 一个目标仓库中的已知文件
```

必要时让它执行：

```bash
git rev-parse --show-toplevel
git branch --show-current
```

Codex 自己也核对同样信息。

只有以下条件都满足才进入 `AGY_READY`：

1. tty7 worker pane cwd 指向 `repo_root`；
2. AGY 实际读到当前仓库中的已知内容；
3. AGY repo root 与 Codex `repo_root` 一致；
4. AGY branch 与当前任务目标一致；
5. 没有旧项目/旧任务上下文串入的证据。

如果不一致，停止编码并按 `resources/failure-modes.md` 的 context mismatch 流程处理。

## 6. 根据任务复杂度选择 AGY 策略

不要所有任务都使用同一模式。

### 小型、边界清晰

如单点 bug、字段调整、小范围测试补充。若当前 AGY 支持类似 `accept-edits` 的文件编辑模式，可用于减少 AGY 自身重复的 edit review；但不等于放开危险 shell、网络或外部权限。

### 中型功能

默认：Task Contract → AGY Implement → Codex Review → AGY Rework → Codex Verify。

### 大型重构 / 跨模块改造

若 AGY 支持 plan mode，先让 AGY 在只分析、不改文件的阶段出方案，Codex Review 通过后再进入 Implement。没有 plan mode 时，用 Task Contract 明确模拟同样的观察阶段。

## 7. Task Contract + Run Policy

正式委派尽量包含：

```text
Goal
- 本阶段必须实现什么。

Scope
- 允许修改哪些模块/目录/接口。

Context
- 当前架构、关键调用链、baseline 中已有改动。

Constraints
- 项目规则、兼容性、不能破坏的行为。

Acceptance Criteria
- 可由 Codex 检查的完成条件。

Verification
- AGY 应运行哪些针对性测试/检查。

Run Policy
- AGY 是唯一主要 Writer。
- 不 push / merge / deploy。
- 不回滚 baseline 中用户已有改动。
- 不扩大 Scope。
- 高风险权限必须停下。

Report
- 修改文件、关键实现、真实运行的测试及失败项。

Completion Protocol
- 当前 turn 完成并停止继续操作后，在最终回复末尾输出指定 TURN_COMPLETE nonce。
```

Task Contract 降低 AGY 自己补全错误假设的概率；Run Policy 明确它在 tty7 worker 中的行为边界。

## 8. Turn Protocol：每轮都有唯一 Nonce

一个监督任务由多个 worker turn 组成，例如：分析、实现、Review 返工、测试返工。

每次发送正式 Turn 前：

1. `tty7 capture "$PANE" --plain`，确认当前画面可安全接收输入；
2. 生成新的短 nonce，例如 `A7F2E9`；
3. 将本轮指令和 nonce 一起发送；
4. 要求 AGY 最终单独输出：

```text
TURN_COMPLETE: A7F2E9
```

**TURN_COMPLETE 不是验收证明。** 它只表示 AGY 声称当前 Supervisor Turn 已返回，下一步必须进入 Codex Review。

完整 Run/Turn 状态见 `resources/run-lifecycle.md`。

## 9. 等待与观察：Native Status 优先，Fallback 可用

### A. tty7 对 AGY 提供 native status 时

发送 Turn 后：

```bash
tty7 wait "$PANE" --until waiting,done --changed --timeout 1800
```

`--changed` 是必须的，因为 tty7 agent state 是 level，不是 event；上一轮 `done` 可能仍站着。

- `waiting`：先 capture 看它需要什么，再按权限边界决定回答或交给用户。
- `done`：capture 最新输出并进入 Review。
- `124`：timeout 不是失败证明，进入诊断。
- `1`：pane 已退出，进入 worker failure 诊断。

### B. AGY 没有 tty7 status hook 时（当前必须支持的 fallback）

不要等待不存在的 `done`。使用有界观察：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

将当前画面分类为 observation：

- `AGY_PRESENT`
- `TUI_ACTIVE`
- `INPUT_REQUIRED`
- `TURN_MARKER_SEEN`
- `ERROR_VISIBLE`
- `PROMPT_READY`
- `UNKNOWN`

看到当前 nonce 的 `TURN_COMPLETE`，或从画面明确判断该 turn 已返回后，进入 Review。

`UNKNOWN` 是合法状态：继续观察，不要猜成成功，不要盲目 Enter，不要重复发送同一 Task Contract。

## 10. Read Before Send

任何对 worker pane 的写操作之前必须重新 capture 当前画面，包括：

- 新 prompt
- Enter
- permission/menu 按键
- Escape
- Ctrl-C

固定顺序：

```text
CAPTURE
  ↓
CLASSIFY
  ↓
DECIDE
  ↓
SEND
```

这条规则防止根据几秒前的界面状态把按键发送到已经变化的 TUI。

## 11. Codex Review：从 Git 收交付，不从 Screen 收交付

AGY screen 用于：

- 观察它在做什么；
- 判断权限/问题/错误；
- 收到 Turn marker；
- 诊断中断。

真正交付必须从 repository state 获取：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

必要时：

```bash
rg <symbol-or-pattern>
```

检查 Task Contract、调用链、架构、边界、错误处理、API/Schema、测试和生成物。完整 Gate 见 `resources/review-gates.md`。

### Scope Drift Guard

将当前变更与 baseline 对比，识别 AGY 本轮新增 changed paths。若超出 Task Contract Scope：

1. 判断是否为满足需求所必需；
2. 没有充分依据则 `REWORK`；
3. 只要求 AGY 撤销它自己本轮引入的越界改动；
4. 不误伤 baseline 中用户已有改动。

## 12. Evidence-driven Rework + Rework Budget

Review 不通过时，通过同一 `$PANE` 发送精确返工：

```text
Issue
- <文件/位置/行为>

Evidence
- <diff / test / 调用链证据>

Expected
- <应该是什么>

Rework
- <AGY 要做的具体改动>

Re-run
- <AGY 本轮应重跑的针对性验证>
```

发送前仍然执行 Read Before Send，并生成新 Turn nonce。

默认 **3 个完整 Review → Rework → Re-review 周期为 soft limit**。达到 soft limit 时必须重新评估是否存在需求不清、根因判断错误、架构冲突、环境问题或修复震荡；不能静默无限返工。必要时进入 `BLOCKED` 并报告用户。

## 13. Codex Independent Verification

实现 Review 稳定后，Codex 自己运行仓库要求的质量门禁。AGY 运行过的命令不算独立验证。

优先：

1. 仓库明确规定的命令；
2. targeted tests；
3. lint / typecheck / unit tests；
4. integration / build / package；
5. contract/schema/config 校验。

失败则保留真实失败证据，重新进入 Evidence-driven Rework；修复后由 Codex 再独立重跑。

最终再检查：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

确认没有临时文件、debug、无关格式化、生成物、baseline 覆盖和越界修改。

只有需求、架构、边界、独立门禁、最终 diff 和外部副作用边界全部满足，Supervisor State 才能进入 `ACCEPTED`。

## 14. Worker Error / Crash Recovery

遇到 API error、连接中断、turn 被切断时：

1. 先 capture 当前画面；
2. 检查 repository state；
3. 若 AGY TUI 仍活着且已经回到可输入状态，优先在同一 pane 内要求基于已有修改继续；
4. 不因为状态显示异常就立即创建第二个 AGY 同时写同一 checkout。

若 pane 真正退出：

1. 先 Review 当前 Git state，保留已经产生的有效工作；
2. 不自动假设全部重来；
3. 只有确实需要继续时才创建 replacement worker；
4. 若掌握经过验证的 AGY conversation id，可按当前版本支持的 `--conversation` 恢复；否则不猜 session id，使用 Task Contract + 当前 diff 重新建立上下文。

具体分类见 `resources/failure-modes.md`。

## 15. tty7 Cleanup

正常完成后，优先清理本 Skill 创建的整个 worker workspace：

```bash
tty7 ws rm "$WS"
```

不要操作其他 workspace/pane，不使用全局 orphan cleanup。

如果用户明确希望保留 AGY 终端继续查看/接管，则保留，并在最终汇报中给出稳定的 workspace id 和 pane id。

## 16. 最终汇报

最终中文汇报至少包含：

- AGY 完成了什么；
- 修改了哪些核心文件；
- Codex Review 发现了什么问题；
- 发生了多少轮返工，以及结果；
- Codex 独立运行了哪些构建/测试及结果；
- 本次 tty7 使用 native status 还是 AGY fallback observation；
- 当前 AGY/tty7 capability 是否影响了执行策略；
- 是否保留或清理了本次 workspace/pane；
- 仍存在的风险、未覆盖项或待办；
- 明确说明是否执行过 push / merge / deploy（默认没有）。

最终结论必须基于真实 repository state 和命令结果，而不是复述 AGY 的总结。