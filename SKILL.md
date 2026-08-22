---
name: agy-supervised-development
description: Use Codex as supervisor/reviewer and AGY (Antigravity CLI) as the sole primary implementer in a dedicated tty7 workspace, with baseline protection, capability detection, evidence-based review/rework, change-completeness and blast-radius checks, test-layer decisions, bugfix RED→GREEN regression proof, independent verification, and mandatory knowledge closeout before acceptance.
version: 2.1.2
---

# AGY 监督开发

当用户明确使用 `$agy-supervised-development`，或明确要求采用“Codex 监督 + tty7 + AGY 执行”开发时，按本流程工作。

核心角色固定为：

- **Codex = Supervisor / Reviewer / QA**：理解需求、建立 Git baseline、创建和管理本次 tty7 worker workspace、委派 AGY、审查真实 repository state、做 Change Completeness / Blast Radius Review、独立验证、审查 Knowledge Closeout 并最终验收。
- **tty7 = Worker Runtime**：提供持久 PTY、独立 workspace/pane、agent detection、send/capture/wait 等运行时能力；不要在 Skill 内重复造进程管理器。
- **AGY = Implementer / Sole Primary Writer**：负责实现生产代码、补测试、执行针对性验证、按证据返工，并在代码稳定后同步受影响的项目知识面。
- **Repository state = 真相来源**：AGY 的 `done`、总结、测试自述和 turn marker 都不是完成证明。

本 Skill 只定义监督编排主流程。AGY 运行时见 `resources/agy-runtime.md`；tty7 操作协议见 `resources/tty7-supervision.md`；监督状态与 Turn 协议见 `resources/run-lifecycle.md`；故障见 `resources/failure-modes.md`；完整性交付和回归证明见 `resources/completeness-regression.md`；审查门禁见 `resources/review-gates.md`；开发完成后的代码/文档/规则对齐见 `resources/closeout-governance.md`。

## 不可违反的边界

- 只有 Codex 可以把任务判定为 `ACCEPTED`。AGY 的 `done` 或 `TURN_COMPLETE` 最多表示当前 worker turn 返回。
- 当前 diff 正确不等于改动完整；实现 Review PASS 后还必须做 Change Completeness / Blast Radius Review。
- “测试绿色”不等于测试策略正确；每个实际开发任务必须明确 Unit / Integration / E2E 的 applicability。
- 对可安全、确定性自动复现的 bug，默认要求 regression test 在 unfixed behavior 上先 RED，再修根因并 GREEN；无法适用时必须给出原因和替代证据。
- 代码通过 Review / Completeness / test / build 只允许进入 `CODE_VERIFIED`，不能直接 `ACCEPTED`；实际开发任务必须再完成 Knowledge Impact Scan 和 Closeout Review。
- 主要生产代码、测试和受影响知识文件由 AGY 修改。Codex 负责监督、Review、验证和返工；仅在 AGY 无法继续、用户明确要求或极小的监督性修补时例外，并在最终汇报说明。
- 每个监督任务创建独立 tty7 workspace + pane。只操作本次任务保存的稳定 workspace id 和 pane id；已有用户 pane、其他 agent pane 和其他 workspace 一律只读。
- 不缓存 `@N` 作为 worker identity；tab 序号会漂移。优先保存 `tty7 new --json` 返回的 workspace id 和 pane id。
- 不执行 `tty7 server stop`、`tty7 server restart`、`tty7 pane close --orphans`，不清理不是本 Skill 创建的资源。
- 不因为 `tty7 send` 成功就认为命令启动成功；新 pane 第一次 send 后必须做 Launch Proof，防止 shell 启动期吞掉 Enter。
- 不因为 `tty7 procs` 显示空就认为 AGY 已退出；coding agent 存活判断优先看 `tty7 agents` 和实际 pane 画面。
- 不假设 AGY 一定有 tty7 status hook。Preflight 必须判断当前 tty7/AGY 是否能提供 native agent state；没有则使用 Turn Nonce + capture fallback。
- 任何向 AGY 的 `send`、Enter、方向键、Escape、Ctrl-C 等操作之前，都先读取当前 pane：**Read Before Send**。
- 不执行 push、merge、release、deploy、远端历史修改等外部操作，除非用户明确授权。
- Completeness 不能成为 scope expansion 的借口，也不能授权 destructive migration、breaking public API、auth/tenancy relaxation、money/secrets/production/irreversible deletion 等 one-way decision。
- 不默认使用全局跳过权限确认的危险模式；权限、账号、联网、破坏性操作和跨范围访问必须可审计。
- 尊重仓库已有改动：先记录 baseline，不得为了“清理”回滚、覆盖或删除用户已有改动。
- Knowledge Closeout 默认只同步当前项目直接受影响的 README/docs/rules/Contract/config 等知识面，不因为“收尾”自动获得 memory、跨项目写入、发布或破坏性清理权限。
- 不因为 tty7 pane 的 cwd 正确，就假设 AGY 的内部 workspace/context 一定正确；必须显式绑定或验证。

## 1. 建立任务范围和 Git Baseline

先确定仓库根目录并读取适用规则：

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- 项目开发规范
- OpenAPI / Schema / Contract
- CI / lint / test / build / e2e 约定

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
- **若 AGY 只能被识别、没有 status hook**：这是可支持的正常降级，不阻塞任务；后续走 capture + Turn Nonce fallback。
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

### Launch Proof

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

### 小型、边界清晰

如单点 bug、字段调整、小范围测试补充。仍必须做最小 Completeness Sweep 和 Test Layer Decision；如果是可复现 bug，仍适用 RED→GREEN。

### 中型功能

默认：

```text
Task Contract
→ AGY Implement
→ Codex Review
→ Change Completeness Review
→ AGY Rework（如有）
→ Codex Independent Verification
→ CODE_VERIFIED
→ AGY Closeout
→ Codex Accept
```

### 大型重构 / 跨模块改造

若 AGY 支持 plan mode，先让 AGY 在只分析、不改文件的阶段出方案，Codex Review 通过后再进入 Implement。没有 plan mode 时，用 Task Contract 明确模拟同样的观察阶段。

大型改造的 Completeness Sweep 必须重点追踪 caller/consumer、schema/data、sibling flows、old path 和测试；完成代码 Verification 后默认执行 Full Closeout。

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

Completeness
- 本次变化必须追踪哪些 caller / consumer / data / state propagation。
- 哪些相邻需求明确属于 different ticket。

Test Strategy
- Unit: required | not-applicable
- Integration: required | not-applicable
- E2E: required | not-applicable | user-skipped
- E2E required 时记录 command/startup/readiness/seed/account/teardown。

Regression Proof
- bugfix: required | not-applicable
- not-applicable 时说明原因和替代证据。

Verification
- AGY 应运行哪些针对性测试/检查。

Run Policy
- AGY 是唯一主要 Writer。
- 不 push / merge / deploy。
- 不回滚 baseline 中用户已有改动。
- 不扩大 Scope。
- Completeness 只收本次 change 自己造成的 unfinished remainder。
- one-way decision 必须停下。
- 高风险权限必须停下。

Report
- 修改文件、关键实现、真实运行的测试及失败项。
- blast radius / remainder / regression proof 状态。

Completion Protocol
- 当前 turn 完成并停止继续操作后，在最终回复末尾输出指定 TURN_COMPLETE nonce。
```

简单任务可以把 Completeness/Test/Regression 字段写得很短，但三个判断不能被默默省略。

初始 Task Contract 不要求 AGY 预先猜所有文档改动；Knowledge Closeout 在最终代码稳定后按 final diff 决定真实知识影响面。

## 8. Turn Protocol：每轮都有唯一 Nonce

一个监督任务由多个 worker turn 组成，例如：分析、实现、Review/Completeness 返工、测试返工、Knowledge Closeout。

每次发送正式 Turn 前：

1. `tty7 capture "$PANE" --plain`，确认当前画面可安全接收输入；
2. 生成新的短 nonce，例如 `A7F2E9`；
3. 将本轮指令和 nonce 一起发送；
4. 要求 AGY 最终单独输出：

```text
TURN_COMPLETE: A7F2E9
```

**TURN_COMPLETE 不是验收证明。** 它只表示 AGY 声称当前 Supervisor Turn 已返回，下一步必须进入 Codex 对应阶段的 Review。

完整 Run/Turn 状态见 `resources/run-lifecycle.md`。

## 9. 等待与观察：Native Status 优先，Fallback 可用

### A. tty7 对 AGY 提供 native status 时

发送 Turn 后：

```bash
tty7 wait "$PANE" --until waiting,done --changed --timeout 1800
```

`--changed` 是必须的，因为 tty7 agent state 是 level，不是 event；上一轮 `done` 可能仍站着。

- `waiting`：先 capture 看它需要什么，再按权限边界决定回答或交给用户。
- `done`：capture 最新输出并进入对应 Review。
- `124`：timeout 不是失败证明，进入诊断。
- `1`：pane 已退出，进入 worker failure 诊断。

### B. AGY 没有 tty7 status hook 时

不要等待不存在的 `done`。使用有界观察：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

将当前画面分类为：

- `AGY_PRESENT`
- `TUI_ACTIVE`
- `INPUT_REQUIRED`
- `TURN_MARKER_SEEN`
- `ERROR_VISIBLE`
- `PROMPT_READY`
- `UNKNOWN`

看到当前 nonce 的 `TURN_COMPLETE`，或从画面明确判断该 turn 已返回后，进入对应 Review。

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

## 11. Codex Review：Review Diff + Review Missing Diff

AGY screen 用于观察、权限判断、Turn marker 和诊断；真正交付必须从 repository state 获取：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

### 11.1 Diff Review

检查 Task Contract、架构、边界、错误处理、API/Schema、测试和生成物。完整 Gate 见 `resources/review-gates.md`。

### 11.2 Scope Drift Guard

将当前变更与 baseline 对比，识别 AGY 本轮新增 changed paths。若超出 Task Contract Scope：

1. 判断是否为满足需求所必需；
2. 没有充分依据则 `REWORK`；
3. 只要求 AGY 撤销它自己本轮引入的越界改动；
4. 不误伤 baseline 中用户已有改动。

### 11.3 Change Completeness / Blast Radius

实现 diff 本身 PASS 后，再检查“missing diff”。详细协议见 `resources/completeness-regression.md`。

对每个语义变化追踪：

```text
Changed Symbol / Behavior
→ Direct Callers
→ Indirect Callers / Re-exports / Scripts
→ Types / Enums / Validation / Serialization
→ Schema / Migration / Existing Data
→ Sibling Paths / Jobs / Flows
→ Error / Empty / Permission / Retry / Fallback
→ Cache / Derived State / Stale IDs
→ Dead / Orphaned Old Path
→ Tests
→ Knowledge Impact Handoff
```

必要时：

```bash
rg "<changed-symbol>" .
rg "<old-route|old-field|old-enum|old-config>" .
```

每个 remainder 只能处置为：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

判断标准：如果现在交付，Reviewer 会叫它 `unfinished` 还是 `different ticket`？unfinished 必须补齐；different ticket 不扩大 Scope。

Completeness Review 不通过时进入 Evidence-driven Rework，不能因为当前 changed files 的测试已绿就继续。

## 12. Evidence-driven Rework + Rework Budget

Review / Completeness / Verification 不通过时，通过同一 `$PANE` 发送精确返工：

```text
Issue
- <文件/位置/行为/漏改传播面>

Evidence
- <diff / test / 调用链 / rg / contract 证据>

Expected
- <应该是什么>

Rework
- <AGY 要做的具体改动>

Re-run
- <AGY 本轮应重跑的针对性验证>
```

发送前仍然执行 Read Before Send，并生成新 Turn nonce。

默认 **3 个完整 Review → Rework → Re-review 周期为 soft limit**。达到 soft limit 时必须重新评估需求、根因、completeness 边界、架构和环境，不能静默无限返工。

## 13. Test Strategy、Regression Proof 与 Codex Independent Verification

实现 Review + Completeness Review 稳定后，Codex 才进入 `VERIFYING`。

### 13.1 Test Layer Decision

必须有明确结论：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

- 纯逻辑通常 unit；
- 跨 module / DB / serialization / queue / adapter contract 时考虑 integration；
- UI→API→DB、service→service、CLI→filesystem 等真实跨边界 flow 优先 E2E；
- 用户明确跳过 E2E 必须记录 `user-skipped`，不能伪装成 N/A。

### 13.2 Bugfix Regression Proof

对于可安全、确定性自动复现的 bug：

```text
write regression test
→ unfixed behavior 上 RED
→ fix root cause
→ same test GREEN
→ Codex independent re-run
```

Codex 需要看到：

```text
Regression proof: required
Test: ...
Before fix: FAIL + evidence
After fix: PASS
Codex re-run: PASS | FAIL
```

无法安全/稳定自动复现时允许：

```text
Regression proof: not-applicable
Reason: ...
Alternative evidence: ...
```

### 13.3 Independent Verification

Codex 自己运行相关门禁。AGY 运行过的命令不算独立验证。

优先：

1. 仓库明确规定的命令；
2. targeted tests；
3. lint / typecheck；
4. required unit tests；
5. required integration tests；
6. required e2e tests；
7. build / package；
8. contract/schema/config 校验。

E2E required 时记录 run recipe：command、app/services startup、readiness、seed/fixture、test account/sandbox、teardown。

如果仓库没有 E2E harness，不为小任务擅自引入大型测试基础设施；按照 Task Contract / 用户决策处理。

失败则保留真实失败证据，重新进入 Evidence-driven Rework；修复后由 Codex 再独立重跑。

最终再检查：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

进入 `CODE_VERIFIED` 前，Codex 必须能够说明：

```text
Completeness Sweep: PASS
Blast radius evidence: ...
Remainders: none | dispositions
Test layers: unit / integration / e2e
Regression proof: RED→GREEN | not-applicable
Independent verification: commands + results
```

只有这些成立，Supervisor State 才进入 `CODE_VERIFIED`。下一步固定执行 Knowledge Closeout。

## 14. AGY Knowledge Closeout

每次实际开发完成后都执行 Knowledge Impact Scan。详细协议见 `resources/closeout-governance.md`。

### 14.1 先判断影响，不机械改文档

对以下知识面按项目实际存在情况判断：

- README / usage；
- `AGENTS.md` / `CLAUDE.md` / project rules；
- API / Schema / CLI / shared Contract；
- env / config / provider / service / deploy / job 说明；
- 本轮明显 workspace residue。

每个相关面标记：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

允许全部是 `verified-current` / `not-applicable`，此时不产生文档 diff。**每次开发都 Scan，不是每次开发都改 README。**

### 14.2 Lightweight / Full Closeout

普通内部实现变化默认 Lightweight Closeout。

出现 API、schema、CLI、env/config、用户流程、模块边界、部署、后台任务、重命名/退役或跨项目协议变化时升级 Full Closeout，并搜索旧 symbol / route / env / field / service 的非历史引用。

### 14.3 委派同一个 AGY Worker

进入 `CODE_VERIFIED` 后，先 Read Before Send，再向同一 `$PANE` 发新的 Closeout Turn nonce：

```text
Closeout Goal
- 根据最终 repository state 完成本次开发的知识收尾。

Source of Truth
- final diff、当前代码/schema/config/tests、Supervisor 已验证结果。

Required
- 先做 Knowledge Impact Scan。
- 只修改受最终实现影响的知识面。
- 过期现役描述就地更新，不创建第二份权威答案。
- 不把开发过程流水账写进 README / rules。
- 未验证事实标 pending，不写成完成。
- residue 只列 deletion-candidate；没有明确授权不要删除。
- 不 push / merge / deploy，不扩大范围。

Report
- surface / status / evidence / changed files / pending / out-of-scope / deletion-candidate
```

AGY 完成 Closeout Turn 后，Codex 从 Git state Review，不接受 AGY 自述作为证据。

### 14.4 Gate 13 — Knowledge & Documentation Alignment

Codex 至少确认：

- 受影响文档与最终代码事实一致；
- Agent rules 没有过期，也没有膨胀成第二份 README；
- API/schema/config/examples 没有互相冲突；
- 退役 symbol 没有继续残留在现役知识面；
- 没有为形式制造无意义文档 diff；
- pending / out-of-scope / deletion candidates 已明确；
- 没有未经授权删除或跨项目写入；
- Closeout 修改仍满足 baseline integrity 和 Scope Drift Guard。

Closeout 不通过时继续 Evidence-driven Rework。若 Closeout 暴露的是实际代码/传播缺陷，退回 Review / Completeness / Verification，不允许只改文档掩盖代码问题。

只有代码 Gates PASS、Completeness PASS、Regression/Test Proof 成立、Independent Verification 完成、Knowledge Closeout PASS，Supervisor State 才能进入 `ACCEPTED`。

## 15. Worker Error / Crash Recovery

遇到 API error、连接中断、turn 被切断时：

1. 先 capture 当前画面；
2. 检查 repository state；
3. 若 AGY TUI 仍活着且已经回到可输入状态，优先在同一 pane 内要求基于已有修改继续；
4. 不因为状态显示异常就立即创建第二个 AGY 同时写同一 checkout。

若 pane 真正退出：

1. 先 Review 当前 Git state，保留已经产生的有效工作；
2. 不自动假设全部重来；
3. 只有确实需要继续时才创建 replacement worker；
4. 若掌握经过验证的 AGY conversation id，可按当前版本支持的 `--conversation` 恢复；否则不猜 session id，使用 Task Contract + 当前 diff + Review/Completeness evidence 重建上下文。

如果代码已经进入 `CODE_VERIFIED` 才发生 worker failure，replacement worker 只需基于 final diff + Closeout Contract 重建知识收尾上下文，不要无证据重复修改已验证代码。

具体分类见 `resources/failure-modes.md`。

## 16. tty7 Cleanup

正常完成并且 Closeout Review PASS 后，优先清理本 Skill 创建的整个 worker workspace：

```bash
tty7 ws rm "$WS"
```

不要操作其他 workspace/pane，不使用全局 orphan cleanup。

Knowledge Closeout 中发现的用户文件、计划文档、备份或其他 residue 不属于 tty7 workspace cleanup；除非已有明确授权，否则只报告 deletion candidates，不擅自删除。

如果用户明确希望保留 AGY 终端继续查看/接管，则保留，并在最终汇报中给出稳定的 workspace id 和 pane id。

## 17. 最终汇报

最终中文汇报至少包含：

- AGY 完成了什么；
- 修改了哪些核心代码文件；
- Codex Review 发现了什么问题；
- Change Completeness / Blast Radius 检查了哪些传播面，是否存在 remainder；
- remainder 的 disposition；
- 发生了多少轮返工，以及结果；
- Test Layer Decision：Unit / Integration / E2E；
- bugfix 的 Regression Proof：RED→GREEN 或 not-applicable + 原因；
- Codex 独立运行了哪些构建/测试及结果；
- Knowledge Closeout 使用 Lightweight 还是 Full；
- 哪些知识面是 `changed-and-verified` / `verified-current`；
- 是否存在 `pending` / `out-of-scope` / deletion candidates；
- 本次 tty7 使用 native status 还是 AGY fallback observation；
- 当前 AGY/tty7 capability 是否影响了执行策略；
- 是否保留或清理了本次 workspace/pane；
- 仍存在的风险、未覆盖项或待办；
- 明确说明是否执行过 push / merge / deploy（默认没有）。

最终结论必须基于真实 repository state、Completeness / Blast Radius Evidence、Regression/Test Proof、Independent Verification 和 Closeout Review，而不是复述 AGY 的总结。