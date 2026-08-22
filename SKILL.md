---
name: agy-supervised-development
description: Use Codex App as the sole master supervisor and Pi's native coding harness as the sole primary worker runtime. Codex sends structured Task/Rework/Closeout Contracts through Pi's native CLI/JSON session interface; trusted existing Pi extensions may enforce workflow modes and tool policy; the selected provider supplies model intelligence only. Preserve baseline protection, evidence-based rework, completeness/blast-radius review, test-layer decisions, deterministic bugfix RED→GREEN proof, independent Codex verification, and mandatory knowledge closeout before acceptance.
version: 3.0.1
---

# AGY Supervised Development 3.0.1

当用户明确使用 `$agy-supervised-development`，或要求采用 **Codex App 主控 + Pi 原生 Harness 执行 + Antigravity/其他 Pi Provider 推理** 的监督式开发时，按本流程工作。

v3.0.1 的核心收敛是：**不再自研第二套 Pi Harness、Bridge、Run Store 或 `pi-supervisor` CLI。Pi 本身就是 Worker Harness。** Skill 只定义监督策略、Codex→Pi 交互契约和最终 Review/Verification/Closeout。

> **Codex owns supervision. Pi owns execution. Provider supplies intelligence. Repository owns truth.**

## 角色固定

- **Codex App = Master Supervisor / Architect / Reviewer / QA / Final Decision Maker**：理解需求、建立 baseline、生成 Task Contract、调用 Pi、独立 Review Git、做 Completeness / Blast Radius、Verification、Knowledge Closeout Review，并且是唯一可以判定 `ACCEPTED` 的角色。
- **Pi Native Harness = Sole Primary Worker / Writer**：使用 Pi 原生 agent loop、session、tools、extensions 和 provider 完成代码修改、测试、返工和需要的知识文件更新。
- **Existing Pi Extensions = Optional Policy Layer**：优先复用成熟扩展，不在本 Skill 内重造 mode/tool policy。若使用 `pi-agent-modes`，Skill phase 映射到它现有的 `plan/build/review/debug` 等模式；不得把未安装的扩展能力假装成已生效。
- **Provider = Intelligence only**：默认目标可以是用户自己选择、安装并登录的 Antigravity Pi Provider；Provider 不拥有任务生命周期、权限边界或最终验收。
- **Repository state = Source of Truth**：Pi 的 `agent_end`、最终回复、测试自述都不是完成证明。

运行协议见：

- `resources/pi-interaction.md`：Codex↔Pi 原生 CLI/JSON/session 交互；
- `resources/provider-boundary.md`：Provider/OAuth 边界；
- `resources/run-lifecycle.md`：Codex 监督状态、session resume、rework；
- `resources/failure-modes.md`：Pi/session/extension/provider 故障；
- `resources/completeness-regression.md`：Completeness、Blast Radius、测试层、RED→GREEN；
- `resources/review-gates.md`：Repository Review Gates；
- `resources/closeout-governance.md`：Knowledge Closeout。

`resources/pi-harness.md` 仅保留为 v3.0.0 历史设计说明，不是 3.0.1 active runtime contract。

---

# 不可违反的边界

1. **只有 Codex 可以 `ACCEPTED`。** Pi JSON stream 出现 `agent_end` 或进程正常退出，只表示本次 Pi turn 返回。
2. **Pi 是唯一主要 Writer。** Codex 默认不与 Pi 并行修改生产代码；例外必须明确说明。
3. **不自研第二套 Harness。** 不要求 `pi-supervisor`、自定义 daemon、Run Store、`run_id`、`operation_id` 或专有 Evidence Bundle。
4. **Pi session 是 Worker continuity 的主要 runtime identity。** 只使用 Pi 实际返回的 session id/file；不猜 session。
5. **不依赖 `agy` CLI / tty7。** v3 主链路不做 PTY、pane、capture、Turn Nonce、AGY conversation DB/status hook 管理。
6. **Capability Detection > Assumption。** 每次确认当前 Pi、CLI flags、JSON/RPC、Provider、model、extension/mode 能力；不要用旧文档硬猜。
7. **Provider/OAuth 由用户管理。** 不自动安装 Provider、不自动登录、不读取/复制 token、不把 credential 放进 prompt、日志、repo 或 review evidence。
8. **第三方 Antigravity Provider 是非官方集成。** 对兼容性/条款/账号风险保持显式边界。
9. **Mode Extension 不是 OS sandbox。** 即使 `pi-agent-modes` 等扩展能限制 tools，也不能描述成恶意本地进程级隔离。
10. **未检测到可信 mode/tool-policy extension 时，不宣称 read-only/write guard 已被程序化执行。** 此时只能依靠 Task Contract + Codex repository review，必要时 `BLOCKED` 等待用户安装/选择策略扩展。
11. **默认不使用 `yolo`。** 监督开发不得为了绕过阻塞静默切入全放行模式。
12. **当前 checkout + baseline protection 是默认单 Writer 拓扑。** 不机械切 worktree，不回滚用户已有改动。
13. **不 push / merge / release / deploy / production write / irreversible delete**，除非用户明确授权。
14. **Completeness 不是 Scope Expansion。** unfinished 必须收完；different ticket 保持 out-of-scope；one-way decision 进入 `BLOCKED`。
15. **每个开发任务明确 Unit / Integration / E2E applicability。**
16. **可安全、确定性复现的 bug 默认 RED → root-cause fix → GREEN → Codex independent re-run。**
17. **`CODE_VERIFIED != ACCEPTED`。** 之后仍需 Knowledge Impact Scan / Closeout Review。

---

# 1. 建立 Git Baseline

先读项目现役规则与真实仓库状态：

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

保存至少：

```text
repo_root
branch
base_head
baseline_changed_paths
baseline_diff_or_fingerprint
```

规则：

```text
current changes - baseline changes = task-introduced changes
```

不得为了让 Pi 获得“干净环境”而回滚 baseline-owned changes。

---

# 2. Pi Native Preflight

正式委派前确认当前安装能力：

```bash
command -v pi
pi --version
pi --help
```

至少确认：

```text
Pi executable available
--mode json available
session persistence/resume available
repo cwd can be bound correctly
selected Provider registered/configured
auth usable
selected model tool-capable
workflow-mode extension status known
```

如果使用 `pi-agent-modes` 或其他可信等价扩展，还要确认它当前真的加载、版本兼容，并识别真实模式名称。

注意两个不同的 mode 概念：

```text
Pi core:       --mode json | rpc | ...     # 输出/集成模式
pi-agent-modes: --modes plan | build | ... # 工作流权限模式
```

不要混用。

缺失 Pi、Provider、auth 或必需 policy capability 时进入 `BLOCKED`。默认不自动安装/登录。

---

# 3. 建立 Task Contract

Codex 在调用 Pi 前生成结构化 Contract：

```text
Goal
- 本阶段必须完成什么。

Scope
- 允许修改的模块/目录/接口。
- 明确 out-of-scope。

Context
- 架构、调用链、baseline 已有改动、关键 contract。

Constraints
- 项目规则、兼容性、安全边界、不可破坏行为。

Acceptance Criteria
- Codex 能独立验证的完成条件。

Completeness
- 必须追踪的 caller / consumer / data / state propagation。
- 明确 different-ticket remainder。

Test Strategy
- Unit: required | not-applicable
- Integration: required | not-applicable
- E2E: required | not-applicable | user-skipped
- E2E required 时记录 run recipe。

Regression Proof
- bugfix: required | not-applicable
- N/A 时写原因和替代证据。

Execution Policy
- current Skill phase
- allowed scope / protected actions
- network/package-install policy
- no push/merge/deploy unless authorized

Report
- changed files
- commands/tests
- blast-radius findings
- unresolved risks
```

Task Contract 是 Codex→Pi 的权威输入。Provider 不得自行扩大任务边界。

---

# 4. Codex → Pi：默认使用原生 JSON 模式

3.0.1 MVP 默认直接调用 Pi：

```bash
pi --mode json --name "agy:<short-task-name>" "<Task Contract>"
```

若检测到并决定使用 `pi-agent-modes`，实现阶段可映射为：

```bash
pi --mode json --modes build --name "agy:<short-task-name>" "<Task Contract>"
```

若需要显式 provider/model，只使用当前 Pi `--help` 和已发现 catalog 证明存在的 flags/IDs；不要 hard-code 旧 model 名称。

### Session Header

Pi JSON 输出第一条 session header 时，记录真实：

```text
pi_session_id
cwd
session timestamp/version（若返回）
```

必须确认：

```text
cwd == repo_root
```

不匹配则停止，不让错误 session 继续写另一个项目。

### Turn Returned

JSON event stream 出现当前调用的 `agent_end`，或 Pi 进程正常结束，只能说明：

```text
PI TURN RETURNED
```

随后 Codex 必须重新读取 Git；不能直接进入 `CODE_VERIFIED`。

详细见 `resources/pi-interaction.md`。

---

# 5. Skill Phase → Existing Pi Mode Mapping

Skill phase 是监督语义，不要求我们创建同名 Pi extension mode。

推荐在 `pi-agent-modes` 可用时映射：

```text
PLANNING       → plan
IMPLEMENTING   → build
REWORKING      → debug 或 build
SECONDARY_READ → review
CLOSEOUT       → build + 严格 Closeout Contract
```

说明：

- `plan/review` 可以提供程序化 read-only policy；
- `build/debug` 允许实现或返工；
- Closeout 没有必要发明新的 Pi mode，使用 `build`，但 Contract 只授权知识面；
- 不把 `yolo` 作为 supervised fallback。

如果另一个可信扩展提供等价 capability，可以替换；Skill 不绑定某一个包。

---

# 6. Resume / Rework

Codex Review 后需要返工，优先 resume **同一个真实 Pi session**：

```bash
pi --mode json --session <real-session-id-or-path> --modes debug "<Rework Contract>"
```

若没有 `pi-agent-modes` 或 `debug` 不适用，使用当前可用、已验证的写模式或省略 `--modes`，但不得虚构 enforcement。

Rework Contract 固定包含：

```text
Issue
Evidence
Expected
Required change
Re-run
```

Pi session history 只是上下文帮助，不能只发“修一下刚才的问题”。

默认 3 个完整 `Review → Rework → Re-review` 周期为 soft limit；达到后重新评估根因、Task Contract、模型、extension policy 和环境，不静默无限循环。

---

# 7. Codex Diff Review

Pi turn 返回后，Codex 自己执行：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

Review 至少判断：

- baseline integrity；
- requirement coverage；
- scope drift；
- architecture/contract；
- correctness/edge cases；
- error handling/observability；
- test strategy；
- external side effects；
- diff hygiene。

Pi 的最终总结只是线索。

---

# 8. Completeness / Blast Radius

普通 Diff Review 回答“改了的地方对不对”；Completeness Review 还要回答“该改但没改的地方有没有”。

固定追踪：

```text
Changed symbol / behavior
→ direct callers
→ indirect callers / scripts / re-exports
→ types / enums / validation / serialization
→ schema / migration / existing data
→ sibling flows / jobs
→ error / empty / permission / retry / fallback
→ cache / derived state / stale IDs
→ dead / orphaned old path
→ tests
→ knowledge impact
```

Remainder 只能是：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

发现 unfinished remainder → `REWORK_REQUIRED`，resume 同一 Pi session。

---

# 9. Test Strategy / Regression Proof

每个任务显式记录：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

可安全、确定性复现的 bug：

```text
same regression test
unfixed → RED
fix root cause
fixed → GREEN
Codex independent re-run
```

只有 Diff Review + Completeness PASS 才进入 Codex Independent Verification。

---

# 10. Codex Independent Verification

Codex 根据仓库约定和 Test Strategy 独立运行相关：

```text
lint / format-check
typecheck
unit
integration
e2e（required 时）
build/package
schema/contract check
```

全部相关项通过后进入：

```text
CODE_VERIFIED
```

Pi 自己跑过同样命令不能代替这一阶段。

---

# 11. Knowledge Closeout

`CODE_VERIFIED` 后执行 Knowledge Impact Scan：

```text
README / usage
AGENTS / CLAUDE / project rules
API / schema / CLI / shared Contract
env / config / provider / service / deploy / job docs
workspace residue
```

每个相关面标：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

如果无需修改，零文档 diff 可以直接进入 Closeout Review。

需要修改时，resume 同一 Pi session；如果 `pi-agent-modes` 可用，使用 `build` + 严格 Closeout Contract：

```bash
pi --mode json --session <session> --modes build "<Closeout Contract>"
```

Closeout 只授权受 final implementation 直接影响的知识面，不能借收尾重新打开生产代码范围。

---

# 12. Supervisor State

3.0.1 只维护 Codex 真正需要的治理状态，不复制 Pi 内部 agent loop：

```text
INIT
→ BASELINED
→ PI_READY
→ PLANNING          (optional)
→ IMPLEMENTING
→ REVIEWING
→ COMPLETENESS_REVIEW
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

异常/循环：

```text
REWORK_REQUIRED
BLOCKED
FAILED
CANCELLED
```

Pi 的 `agent_start/turn_start/tool_execution_*/turn_end/agent_end` 是 runtime evidence，不建立第二套持久 Supervisor 状态机。

关键：

```text
agent_end != PASS
PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
```

---

# 13. Pi RPC：可选增强，不是 MVP 依赖

当以后确实需要长驻 Pi、实时 `steer/follow_up/abort/get_state` 时，可以使用：

```bash
pi --mode rpc
```

3.0.1 不因为这些能力存在就自研 daemon/bridge。JSON CLI 足以作为默认 Codex→Pi 边界；RPC 仅在需求出现时升级。

---

# 14. 最终 Acceptance

只有 Codex 可以进入 `ACCEPTED`，且至少满足：

- Task Contract 全部覆盖；
- baseline/user changes 未受破坏；
- relevant Review Gates PASS；
- Completeness / Blast Radius PASS；
- Test Layer Decision 完整；
- Regression Proof 满足或合理 N/A；
- Codex Independent Verification PASS；
- Knowledge Closeout PASS；
- Provider/session/extension 事实没有被伪造；
- 未发生未经授权 external side effect；
- final diff 可解释。

最终报告至少包含：

```text
Result
Pi session identity
Provider/model（可观察时）
Extension/workflow mode（若使用）
Changed files
Completeness evidence
Test layer decisions
Regression proof
Independent verification
Knowledge closeout
Residual risk / pending / user-skipped
```
