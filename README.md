# AGY Supervised Development 3.0

一个以 **Codex App 为唯一主入口和最终 Supervisor、Pi 为可编程 Worker Harness、Provider 为模型推理层** 的监督式开发 Skill。

> **Codex owns supervision. Pi owns execution. Provider supplies intelligence. Repository owns truth.**

名称保留 `AGY Supervised Development` 作为项目连续性；v3.0 主链路已经不再依赖 `agy` CLI 或 tty7。

---

## 架构

```text
User
  ↓
Codex App
Master Supervisor / Reviewer / Final Acceptance
  ↓ Task Contract / Rework Contract
Pi Harness
Worker Runtime / Writer / Tool Policy / State / Evidence
  ↓
Pi Provider
Antigravity (default target) / other configured provider
  ↓
Repository Changes
  ↓
Codex Diff Review
  ↓
Change Completeness / Blast Radius Review
  ↓
Codex Independent Verification
  ↓
CODE_VERIFIED
  ↓
Pi Closeout Operation
  ↓
Codex Closeout Review
  ↓
ACCEPTED
```

### 四个角色

- **Codex App**：需求理解、Task Contract、架构决策、Review、Completeness、独立 QA、最终 Acceptance。
- **Pi Harness**：唯一主要 Writer；管理 session、operation、tools、scope、permissions、evidence、rework、closeout。
- **Provider**：只提供模型 intelligence。默认目标可为用户自己安装/登录的 Antigravity Pi Provider。
- **Git Repository**：最终事实源。模型自述和 operation settled 都不能代替 repository evidence。

---

# 为什么从 2.1.x 升到 3.0

v2.1.x 的监督方法已经成熟，但 Worker Runtime 仍依赖：

```text
Codex
→ tty7
→ AGY CLI
→ AGY Harness
→ Antigravity
```

为了可靠控制这个外部 Harness，Skill 需要维护：

- tty7 workspace/pane；
- Launch Proof；
- capture/wait；
- AGY status hook fallback；
- Turn Nonce；
- AGY workspace/context binding；
- AGY conversation resume。

v3.0 把链路缩成：

```text
Codex App
→ Pi Harness
→ Provider
```

所有 repository tool calls 都在 Pi Harness 内执行，因此 scope、read-only、command guard、evidence 可以直接程序化。

---

# v3.0 保留的 2.1.x 核心资产

没有推翻监督方法论，完整保留并升级：

- Git baseline protection；
- repository state as source of truth；
- Task Contract；
- Scope Drift Guard；
- Evidence-driven Rework；
- Change Completeness / Blast Radius；
- Test Layer Decision；
- deterministic bugfix RED → GREEN；
- Codex Independent Verification；
- `CODE_VERIFIED != ACCEPTED`；
- Knowledge Impact Scan / Closeout；
- one-way-door / external-side-effect boundary；
- Skill 自测 evals。

---

# v3.0 新增：Pi Harness Contract

详细见 `resources/pi-harness.md`。

核心能力：

```text
Pi SDK / RPC
  ↓
Persistent AgentSession
  ↓
Explicit Run + Operation State
  ↓
Mode Policy
  ↓
Tool Visibility
+ tool_call Guard
+ System Policy
  ↓
Scope / Command / Credential Guard
  ↓
Evidence Bundle
```

推荐 Worker modes：

```text
inspect   read-only exploration
implement scoped code changes
rework    evidence-driven fixes
verify    read-only test/build verification
closeout  knowledge-surface updates only
```

### 三层 Tool Guard

参考 Pi 官方 plan-mode 与 `pi-agent-modes` 的成熟模式：

1. read-only mode 直接移除写工具；
2. `tool_call` hook 再做 fail-closed policy；
3. `before_agent_start` 注入当前 mode/scope/contract。

Prompt 不再承担唯一权限职责。

---

# Provider Boundary

详细见 `resources/provider-boundary.md`。

目标：

```text
Pi
 ↓ Google OAuth / Provider auth
Antigravity
```

而不是：

```text
Pi → agy CLI → AGY Harness
```

### 重要边界

- v3 Skill 不绑定具体第三方 Antigravity package；
- 不自动安装 Provider；
- 不自动 OAuth 登录；
- 不读取/复制 token；
- 不把 credential 写进 evidence/repository；
- Provider auth/quota/transport failure 与代码失败分开；
- Provider/model 可以替换，但 Harness 和监督规则不变。

第三方 Antigravity Provider 属于非官方集成，不同项目对 Google Terms/账号风险提示不同；启用前应审查当前 Provider source/README/risk note。

---

# Supervisor State

v3.0 记录 Codex 能证明的状态：

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

关键语义：

```text
OPERATION_SETTLED != PASS
PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
```

`run_id + pi_session_id + operation_id` 代替 v2.1 的 pane/nonce 轮次识别。

---

# Evidence Bundle

Pi 每个 operation 返回结构化证据，而不是一段“我完成了”：

```text
run_id
operation_id
pi_session_id
harness_version
provider/model
mode
status
changed_paths
git_diff_stat
git_diff_check
commands/tests
tool_policy_blocks
scope_findings
blast_radius_findings
unresolved_items
worker_summary
```

Codex 仍必须自己重新读取 Git state。

---

# Change Completeness / Blast Radius

每个语义变化追踪：

```text
Changed Symbol / Behavior
→ Direct Callers
→ Indirect Callers / Re-exports / Scripts
→ Types / Enums / Validation / Serialization
→ Schema / Migration / Existing Data
→ Sibling Flows / Jobs
→ Error / Empty / Permission / Retry / Fallback
→ Cache / Derived State / Stale IDs
→ Dead / Orphaned Old Path
→ Tests
→ Knowledge Impact
```

判断：

> 现在交付时，剩余项是 **unfinished** 还是 **a different ticket**？

unfinished 必须本 Run 完成；different ticket 不借 completeness 扩 Scope。

---

# Test Strategy / RED → GREEN

每个任务显式判断：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

可安全、确定性复现的 bug 默认要求：

```text
Regression Test
→ unfixed behavior RED
→ Fix Root Cause
→ same test GREEN
→ Codex Independent Re-run
```

---

# Knowledge Closeout

每个开发任务在 `CODE_VERIFIED` 后都做 Knowledge Impact Scan，但不是每次都改 Markdown。

状态：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

API/schema/CLI/env/config/provider/model/架构/部署/job/rename/cross-project contract 等变化自动升级 Full Closeout。

需要修改时由同一 Pi Run 使用 `closeout` mode，只更新受 final implementation 直接影响的知识面，然后 Codex 独立 Review。

---

# 参考的 Pi Harness 思路

v3 设计重点参考：

- Pi 官方 `AgentSession` / `AgentSessionRuntime` / SDK；
- Pi RPC headless JSONL；
- Pi 官方 `plan-mode` extension；
- Pi 官方 `subagent` example；
- `pi-agent-modes` 的 defense-in-depth mode policy；
- `pi-permission-system` 的 extension-layer permission 思路；
- Pi `AgentHarness v2` 的显式持久 operation state；
- `@minhduydev/pi-harness` 的 durable evidence / human authority / provider separation；
- `pi-maestro-flow` 的 run-control / verifier 思路。

但 v3.0 明确**不**照搬大型 orchestration：

- 不默认 parallel workers；
- 不做 DAG scheduler；
- 不做 autonomous goal loops；
- 不做大型 knowledge DB；
- 不替代 Codex App UI；
- 不把 Pi 变成最终 Supervisor；
- 不默认 YOLO。

---

# 文件结构

```text
agy-supervised-development/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── resources/
│   ├── pi-harness.md
│   ├── provider-boundary.md
│   ├── run-lifecycle.md
│   ├── failure-modes.md
│   ├── completeness-regression.md
│   ├── review-gates.md
│   └── closeout-governance.md
├── examples/
│   ├── feature-development.md
│   ├── bugfix-red-green.md
│   └── rework-cycle.md
└── evals/
    ├── README.md
    └── scenarios.json
```

---

# 版本演进

```text
v2
→ Codex 怎样监督 AGY

v2.1
→ Codex 怎样通过 tty7 可靠控制 AGY CLI worker

v2.1.1
→ Knowledge Closeout

v2.1.2
→ Completeness / Blast Radius / Test Layers / RED→GREEN / Evals

v3.0
→ 保留监督方法论，把 Worker Harness 收敛到 Pi；Codex App 继续作为唯一主入口，Provider 退回纯 intelligence 层
```

v3.0 的目标不是造一个新的 Orca/Maestro，而是让这条链路足够短、足够可靠：

> **Codex 决策，Pi 执行，Provider 思考，Git 作证。**
