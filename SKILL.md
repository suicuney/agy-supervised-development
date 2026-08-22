---
name: agy-supervised-development
description: Use Codex App as the sole master supervisor and a programmable Pi harness as the sole primary worker runtime. Pi owns execution, tool policy, durable worker state and evidence; the selected provider (default target: Antigravity via a user-installed Pi provider) supplies model intelligence only. Preserve baseline protection, evidence-based rework, completeness/blast-radius review, test-layer decisions, deterministic bugfix RED→GREEN proof, independent Codex verification, and mandatory knowledge closeout before acceptance.
version: 3.0.0
---

# AGY Supervised Development 3.0

当用户明确使用 `$agy-supervised-development`，或明确要求采用 **Codex App 主控 + Pi Harness 执行 + Antigravity/其他 Pi Provider 推理** 的监督式开发时，按本流程工作。

v3.0 不再把 `agy` CLI 或 tty7 作为主链路依赖。名称 `AGY Supervised Development` 为项目连续性保留；运行时语义已经从“监督 AGY CLI”升级为“Codex 监督自定义 Pi Harness”。

核心原则：

> **Codex owns supervision. Pi owns execution. Provider supplies intelligence. Repository owns truth.**

## 角色固定

- **Codex App = Master Supervisor / Architect / Reviewer / QA / Final Decision Maker**：理解需求、建立 Git baseline、生成 Task Contract、调用 Pi Harness、审查真实 repository state、做 Completeness / Blast Radius Review、独立 Verification、Knowledge Closeout Review，并且是唯一可以把任务判定为 `ACCEPTED` 的角色。
- **Pi Harness = Sole Primary Worker Runtime / Writer**：运行模型和工具循环，执行代码修改、测试、返工和受影响知识文件更新；负责 worker session、operation state、tool policy、scope guard、evidence collection 和结构化返回。
- **Provider = Intelligence only**：默认目标可以是用户已安装并登录的 Antigravity Pi Provider；Provider 只负责推理/生成，不拥有任务生命周期、权限边界或最终完成判定。
- **Repository state = Source of Truth**：Pi/Provider 的总结、`done`、operation settled、测试自述都不是完成证明。

运行时与实现协议见：

- `resources/pi-harness.md`：Pi Harness 架构、SDK/RPC、模式、Tool Guard、Evidence Bundle；
- `resources/provider-boundary.md`：Provider/OAuth 边界、Antigravity 接入与可替换性；
- `resources/run-lifecycle.md`：监督状态、operation、rework 和 resume；
- `resources/failure-modes.md`：Harness / Provider / state / tool policy 故障；
- `resources/completeness-regression.md`：Completeness、Blast Radius、测试层和 RED→GREEN；
- `resources/review-gates.md`：最终仓库 Review Gates；
- `resources/closeout-governance.md`：代码稳定后的 Knowledge Closeout。

---

# 不可违反的边界

1. **只有 Codex 可以 `ACCEPTED`。** Pi operation settled 只表示 worker 本轮不再自动继续。
2. **Pi 是唯一主要 Writer。** Codex 默认不与 Pi 并行修改生产代码，避免双 Writer 冲突；只有用户明确要求、Pi 无法继续、或极小监督性修补时例外，并在最终汇报说明。
3. **Provider 不等于 Harness。** 不把 Antigravity/Gemini/Claude 的模型回复当生命周期或权限事实。
4. **不默认依赖 `agy` CLI / tty7。** v3 主链路不做 pane、PTY、capture、Turn Nonce、AGY conversation DB 或 AGY status hook 管理。
5. **Capability Detection > Capability Assumption。** 每次运行确认 Pi、Harness entrypoint、Provider、模型、tool set 与 session 能力；不能靠文档版本猜。
6. **Provider/OAuth 由用户管理。** 不自动安装第三方 Provider、不自动登录、不提取/复制 OAuth token、不把 credential 写入 repository/evidence/log。
7. **第三方 Antigravity Provider 属于非官方集成。** 若其条款、账号风险、兼容性或登录状态不确定，必须显式报告；不得把它包装成 Google 官方支持路径。
8. **Pi Extension policy 不是 OS sandbox。** Tool Guard 能约束当前模型的工具能力，但不能被描述为对恶意本地进程的强安全隔离。
9. **当前 checkout + baseline protection 仍是默认单 Writer 拓扑。** 用户已有未提交改动可能就是任务上下文；不要机械切 worktree。
10. **不 push / merge / release / deploy / production write / irreversible delete**，除非用户明确授权。
11. **Completeness 不是 Scope Expansion。** unfinished 必须补齐，different ticket 留在 Scope 外；one-way decision 进入 `BLOCKED`。
12. **测试绿色不等于策略正确。** 每个开发任务必须明确 Unit / Integration / E2E applicability。
13. **可安全、确定性复现的 bug 默认要求 RED → root-cause fix → GREEN → Codex independent re-run。**
14. **`CODE_VERIFIED != ACCEPTED`。** 实际开发任务还必须完成 Knowledge Impact Scan / Closeout Review。

---

# 1. 建立任务范围和 Git Baseline

先确定 repository root，并读取项目现役规则：

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- 项目开发规范
- API / Schema / Contract
- CI / lint / test / build / e2e 约定

Codex 自己记录：

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

不得为了“给 Pi 一个干净工作区”而回滚用户已有改动。

---

# 2. Pi Harness Preflight

v3.0 正式开发前必须证明 Harness 可用；不要先发实现任务再补检查。

至少确认：

```text
Pi executable/runtime available
Harness entrypoint available
Harness protocol/version compatible
repo_root binding correct
persistent session capability available
active tool set known
Provider available
auth state usable
selected model tool-capable
```

推荐 Harness 对 Codex 暴露一个稳定入口，例如：

```text
pi-supervisor doctor
pi-supervisor run ...
pi-supervisor resume ...
pi-supervisor status ...
pi-supervisor abort ...
```

名称可以变化，但能力契约必须满足 `resources/pi-harness.md`。

若 Harness 尚未安装/实现：

- 可以完成设计、Task Contract、baseline 和环境诊断；
- 不假装已经进入 supervised implementation；
- 不自动下载或安装第三方包，除非用户明确要求。

## Provider Preflight

默认目标是：

```text
Pi Harness
  ↓
Pi Provider
  ↓
Antigravity / other configured provider
```

确认：

- Provider 已由用户安装并信任；
- OAuth/API credential 已由用户配置；
- 模型能正常产生 tool-capable turn；
- Provider 当前没有明显 quota/auth/transport 错误。

不要求 v3 Skill 知道 Provider 内部 endpoint/token 实现。

---

# 3. 建立 Task Contract

正式委派给 Pi 前，Codex 生成结构化 Task Contract：

```text
Goal
- 本阶段必须实现什么。

Scope
- 允许修改哪些模块/目录/接口。
- 哪些相邻工作明确 out-of-scope。

Context
- 当前架构、调用链、baseline 中已有改动、关键 contract。

Constraints
- 项目规则、兼容性、安全边界、不可破坏行为。

Acceptance Criteria
- Codex 可独立验证的完成条件。

Completeness
- 必须追踪哪些 caller / consumer / data / state propagation。
- 哪些 remainder 明确是 different ticket。

Test Strategy
- Unit: required | not-applicable
- Integration: required | not-applicable
- E2E: required | not-applicable | user-skipped
- E2E required 时记录 command/startup/readiness/seed/account/teardown。

Regression Proof
- bugfix: required | not-applicable
- not-applicable 时说明原因和替代证据。

Execution Policy
- mode: inspect | implement | rework | verify | closeout
- allowed roots / protected paths
- forbidden side effects
- network/package-install policy

Verification
- Worker 应运行哪些针对性检查。
- Codex 最终必须独立重跑哪些检查。

Report
- changed files
- commands/tests
- blast-radius evidence
- unresolved risks
- evidence bundle
```

Task Contract 是 Codex → Pi 的权威输入。Provider 不得自行扩大它。

---

# 4. Codex → Pi：只走 Harness 边界

Codex 不直接控制 Provider，不向 Provider OAuth/backend 发请求。

主路径：

```text
Codex App
  ↓ Task Contract
Pi Harness
  ↓ provider/model
Antigravity or other Provider
  ↓ tool calls
Pi Harness Tool Policy
  ↓
Repository
```

推荐实现使用 Pi SDK 的 `AgentSession` / `AgentSessionRuntime`；若以子进程边界集成，则使用 Pi RPC JSONL。两者都必须保持相同的 Run/Evidence Contract。

每个监督 Run 创建或绑定一个明确的 Pi session。必须保存真实 `session_id/session_file`（若 API 暴露），不要猜 session identity。

---

# 5. Pi Harness 模式与 Tool Guard

v3.0 不让“提示词说只读”承担权限职责。Harness 至少用三层防护：

```text
1. Tool visibility
   - read-only 模式移除 edit/write 等写工具

2. tool_call policy hook
   - 对 bash / custom tools / protected path 做 fail-closed 检查

3. system policy injection
   - 每轮明确当前 mode / scope / forbidden actions
```

这是参考 Pi 官方 plan-mode 与成熟 mode extensions 的关键模式。

推荐模式：

### `inspect`

- read-only；
- 用于代码探索、方案确认、blast-radius reconnaissance；
- 禁止 edit/write；bash 只允许只读命令。

### `implement`

- 允许范围内 `edit/write/bash`；
- Scope Guard 生效；
- 默认禁止 external side effects / one-way door。

### `rework`

- 与 implement 类似，但 prompt 只包含明确 Issue/Evidence/Expected/Re-run；
- 禁止顺手扩大 Scope。

### `verify`

- 默认不修改生产代码；
- 运行测试、build、schema/contract checks；
- 若发现实现缺陷，返回 evidence，由 Codex 决定是否进入 rework，而不是偷偷边测边改。

### `closeout`

- 只允许修改受最终实现直接影响的知识面；
- 不重新打开已稳定的架构范围；
- workspace residue 默认只报告 deletion-candidate。

Tool Guard 详细见 `resources/pi-harness.md`。

---

# 6. Run / Operation 状态

v3 用 Pi session + operation identity 替代 tty7 pane + Turn Nonce。

Supervisor 只记录自己能证明的状态：

```text
INIT
→ BASELINED
→ HARNESS_PREFLIGHT
→ HARNESS_READY
→ OPERATION_SENT
→ EXECUTING
→ OPERATION_SETTLED
→ REVIEWING
→ COMPLETENESS_REVIEW
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

任何阶段都可能进入：

```text
BLOCKED
FAILED
CANCELLED
REWORK_REQUIRED
```

关键语义：

```text
OPERATION_SETTLED != PASS
PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
```

Harness 应给每次 worker operation 一个真实 `operation_id` 或等价关联 ID，并在 Evidence Bundle 中回传，防止 stale result 被错配。

详细状态转移见 `resources/run-lifecycle.md`。

---

# 7. Evidence Bundle：Pi 的输出不是一段“我完成了”

每次 operation 返回至少包含：

```text
run_id
operation_id
pi_session_id/session_file (if available)
harness_version
provider_id
model_id
mode
status = settled | blocked | failed | aborted
changed_paths
git_diff_stat
git_diff_check
commands_executed
tests_executed
tool_policy_blocks
scope_findings
blast_radius_findings
unresolved_items
worker_summary
```

敏感数据禁止进入 Evidence Bundle：

- OAuth access/refresh token；
- Authorization header；
- secret/env value；
- credential file content。

Codex 必须重新从 repository state 获取真相；Evidence Bundle 是可审计线索，不是验收替代品。

---

# 8. Codex Diff Review

operation settled 后，Codex 自己检查：

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
- tests/test strategy；
- external side effects；
- diff hygiene。

Pi 报告“测试都通过”不能代替 Codex Review。

---

# 9. Change Completeness / Blast Radius Review

普通 Diff Review 回答：

> 当前 diff 里的改动对不对？

Completeness Review 额外回答：

> 是否还有应该在本次 diff 里出现，却被漏掉的 caller / consumer / data / state / test？

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
→ orphaned old path
→ tests
→ knowledge impact
```

每个 remainder 必须标：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

发现 unfinished remainder：

```text
COMPLETENESS_REVIEW → REWORK_REQUIRED
```

由 Codex 生成 Evidence-driven Rework Contract，再调用**同一 Pi Run/session**继续。

---

# 10. Evidence-driven Rework

返工必须包含：

```text
Issue
Evidence
Expected
Required change
Re-run
```

不要简单发送“再检查一下”“继续修”。

默认 `soft_rework_limit = 3` 个完整：

```text
Review → Rework → Re-review
```

达到 soft limit 后重新判断 Task Contract、根因、模型能力、Harness policy、环境和 provider 是否有系统性问题；不能静默无限循环。

---

# 11. Test Layer Decision 与 RED→GREEN

每个开发任务显式记录：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

跨真实边界的流程优先考虑 Integration/E2E；不能因为 Pi worker 只跑了 unit tests 就宣布验证完成。

对于可安全、确定性自动复现的 bug：

```text
Regression test
→ unfixed behavior RED
→ fix root cause
→ same test GREEN
→ Codex independent re-run
```

若不可适用，记录明确原因和 alternative evidence。

详细规则见 `resources/completeness-regression.md`。

---

# 12. Codex Independent Verification

实现 Review + Completeness Review PASS 后，Codex 自己进入：

```text
VERIFYING
```

根据项目和 Test Strategy 独立运行相关门禁：

```text
lint
format/check
typecheck
unit
integration
e2e
build/package
contract/schema checks
```

Pi worker 的命令结果可帮助选择验证范围，但不能替代独立执行。

全部相关项通过才能：

```text
VERIFYING → CODE_VERIFIED
```

---

# 13. Knowledge Closeout

`CODE_VERIFIED` 后必须做 Knowledge Impact Scan。

根据 final diff + completeness evidence 判断：

```text
closeout_level = lightweight | full
```

知识面状态：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

需要修改时，Codex 调用同一 Pi Run 的 `closeout` operation，让 Pi 只同步受最终实现直接影响的 README/docs/rules/Contract/config 等知识面。

Codex 再做 `CLOSEOUT_REVIEW`。纯内部变化允许零文档 diff，只要相关知识面已经 `verified-current`。

---

# 14. One-way Door / 用户决策

以下默认不允许 Harness 自己决定：

- destructive / non-additive migration；
- breaking public API；
- auth / tenancy relaxation；
- money / billing semantics；
- secrets / credential behavior；
- production mutation；
- irreversible data deletion；
- push / merge / release / deploy。

Harness 遇到这类调用应 fail closed，记录 `blocked-decision-needed`，停止本 operation，并把证据交回 Codex；Codex 再向用户请求决定。

---

# 15. Provider 故障不应污染 Harness 语义

Provider auth/quota/transport/model error：

- 记录 provider failure，不包装成代码失败；
- 保留已经产生的 repository progress；
- 不自动切模型/provider 后继续修改，除非 Task Contract 或用户已允许；
- 如果切换 Provider，Evidence Bundle 必须记录 provider/model transition；
- recovery 后继续同一 Run，但新 operation 必须有新 ID。

Provider 细节见 `resources/provider-boundary.md`。

---

# 16. Final Acceptance

只有 Codex 可以进入 `ACCEPTED`，且至少满足：

- Task Contract coverage PASS；
- baseline integrity PASS；
- Scope / Scope Drift PASS；
- Diff Review PASS；
- Completeness / Blast Radius PASS；
- Test Layer Decision 完整；
- Regression Proof 成立或合理 N/A；
- Codex Independent Verification PASS；
- Knowledge Closeout PASS；
- 没有未解释的 task-introduced residue；
- 没有未经授权的 external side effect / one-way decision；
- final repository state 可解释。

最终报告建议包含：

```text
Outcome: ACCEPTED | BLOCKED | PARTIAL

Implementation
- changed surfaces
- key behavior

Completeness
- blast-radius evidence
- remainder dispositions

Tests
- unit/integration/e2e decisions
- RED→GREEN evidence if applicable

Independent Verification
- commands + results

Closeout
- knowledge surfaces + statuses

Runtime
- Pi harness version
- provider/model used
- run/session identity (non-secret)

Residual Risk
- pending / user-skipped / out-of-scope / blocked decisions
```

---

# 17. v3.0 明确不做的事

首版保持轻量，暂不把 Harness 做成 Orca/Maestro 类通用平台：

- 不默认多 Worker 并行；
- 不引入 DAG scheduler；
- 不引入 autonomous goal loop；
- 不引入长期项目 memory/knowledge database；
- 不把 Codex App 替换成 Pi TUI；
- 不让 Pi 成为最终 Reviewer/Acceptance authority；
- 不硬绑定单一 Provider；
- 不复刻 tty7/AGY CLI lifecycle。

v3.0 的目标只有一个：

> **保留 v2.1.x 已成熟的监督正确性，把 Worker Harness 收敛到 Pi，并让 Codex App 继续成为唯一主入口。**
