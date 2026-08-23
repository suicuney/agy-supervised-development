# AGY Supervised Development 3.1 — Workflow First

当前开发版本：**3.1.0-alpha.2**

这是一个以 **Codex App 负责 Shape / Spec / Review，官方 AGY CLI 负责实现，Git Repository 负责事实证明** 的定制监督式开发 Skill。

> **Codex shapes and proves. AGY builds. Git tells the truth.**

3.1 不再把“选择哪个 Harness”当项目中心，而是把一次软件开发稳定地拆成：

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
→ BUILD
→ REVIEW
→ COMPLETENESS
→ VERIFY
→ CLOSEOUT
→ ACCEPTED
```

---

## 架构

```text
                         User
                          │
                          ▼
                      Codex App
             Shaper / Spec Owner / Reviewer
                          │
                  Spec + Execution Unit
                          │
                          ▼
                  AGY official CLI
                 headless-first writer
                    │           │
                    │           └── tty7 interactive fallback
                    ▼
                  Repository
                    │
                    ▼
                      Codex
       Review / Completeness / Verification
                    │
                    ▼
                  Closeout
                    │
                    ▼
                  ACCEPTED

Optional sidecar:
Codex ─────→ Pi specialist (research / second opinion / blast-radius analysis)
```

### 角色

- **User**：产品和 one-way decisions；
- **Codex App**：Size、Shape、Spec、Slice、Review、QA、最终 Acceptance；
- **AGY official CLI**：Primary Implementer / Writer；
- **tty7**：只有 TUI/人工交互需要时 fallback；
- **Pi**：可选专家，不进入默认 `Codex → AGY` 主链；
- **Git**：最终 Source of Truth。

---

# Alpha 1：Workflow Kernel

## 1. Task Sizing

每个任务先判断：

```text
Small
Medium
Large
```

### Small

```text
Compact Shape/Spec
→ one Execution Unit
→ AGY
→ Review
→ Verify
```

### Medium

```text
Shape
→ Spec
→ Vertical Slices
→ AGY slice-by-slice
→ Review/Rework
→ Global Verify
```

### Large

```text
Destination
→ Decision Map / Fog of War
→ resolve frontier
→ Spec
→ staged execution
```

详见 `resources/task-sizing.md`。

---

## 2. Decision Shaping

在写 Spec 之前，把需求拆成：

```text
Resolved Decisions
Open Decisions
Not Yet Specified
Out of Scope
One-way Decisions
```

关键思想：

- 能查到的事实由 Codex 自己查；
- 真正的取舍才问用户；
- 下游依赖未解决问题时暂时不问；
- 看不清的问题留在 Fog，不制造假的完整计划。

详见 `resources/shaping.md`。

---

## 3. Stable Spec

Spec 记录已经稳定的行为/决策：

```text
Problem
Expected Behavior
Scenarios
Implementation Decisions
Acceptance Criteria
Verification Seams
Test Strategy
Out of Scope
```

Spec 默认不承担逐文件施工计划。

### Verification Seam

除了 Unit / Integration / E2E，还显式决定：

> 从哪个公共边界观察这个功能是否正确？

详见 `resources/spec-contract.md`。

---

## 4. Execution Slicing

正常功能优先：

```text
Vertical Slice / Tracer Bullet
```

每个 slice 走一条窄而完整的行为路径：

```text
input/user action
→ business behavior
→ persistence/integration
→ observable output
→ verification
```

Wide mechanical refactor 使用：

```text
EXPAND
→ MIGRATE batches
→ CONTRACT
```

详见 `resources/execution-slicing.md`。

---

# Alpha 2：AGY Native Execution Adapter

## 1. Headless First

官方 AGY CLI 作为默认 Writer：

```bash
cd "$repo_root"
agy -p "<Execution Unit>" \
  --output-format stream-json \
  --print-timeout <appropriate-timeout>
```

主要原因：

- 有结构化 `init / step_update / result`；
- 有真实 `conversation_id`；
- 支持 `--conversation` resume；
- 可以观察 tool errors / usage；
- 不需要默认 screen scraping；
- 不需要维护自定义 Harness/daemon/session DB。

详见 `resources/agy-execution.md`。

---

## 2. Conversation Identity

从 AGY `init` 保存真实：

```text
conversation_id
cwd
permission_mode
```

必须：

```text
cwd == repo_root
```

Review 后返工：

```bash
agy -p "<Rework Contract>" \
  --conversation <real-conversation-id> \
  --output-format stream-json
```

自动化场景优先显式 `--conversation`，而不是靠 `-c` 猜最近 session。

---

## 3. `SUCCESS` / exit 0 不是交付证明

```text
AGY result.status = SUCCESS
```

只代表本轮 AGY 正常产生了响应。

真正交付仍然要：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

然后由 Codex Review。

### Headless Permission Soft-Deny

AGY headless 下需要 Ask 的 tool/command 可能被 soft-deny，本轮仍可能继续、甚至 exit 0。

所以必须同时检查：

```text
result.status / error
stderr
step_update.tool_info.error
actual command evidence
repository state
```

测试 command 没真正执行时只能写：

```text
blocked / not-run
```

不能包装成 PASS。

---

## 4. Permission Strategy

默认不使用：

```bash
--dangerously-skip-permissions
```

优先：

```text
现有安全 permission rules
→ 最小范围 allow
→ 一次性人工审批
→ tty7 interactive fallback
```

而不是全量 always-proceed。

`--sandbox` 可以作为可选额外防护，但只有项目/CLI 实测兼容时启用。

---

## 5. tty7 的新定位

2.1.x：

```text
Codex → tty7 → AGY
```

3.1：

```text
Codex → AGY headless       # default
          └→ tty7 + AGY    # interactive fallback
```

使用 tty7 的典型场景：

```text
login/auth
/permissions
manual Ask approval
/resume picker
TUI-only command
interactive exploration
headless temporary incompatibility
```

详见 `resources/tty7-supervision.md`。

---

## 6. Pi 的新定位

Pi 不再是 Primary Runtime，也不固定放在 AGY 前面。

适合：

```text
research
second opinion
blast-radius analysis
architecture critique
specialized Pi extension
```

不推荐默认：

```text
Codex → Pi/Codex → AGY
```

避免重复 decision layer、context handoff 和 token/latency。

详见 `resources/pi-interaction.md`。

---

# Execution Contracts

3.1 把“需求权威”和“施工授权”分开。

### Spec

```text
长期一点的 stable decisions / behavior contract
```

### Execution Unit

```text
当前 slice 到底允许 Worker 做什么
```

模板：`templates/execution-unit.md`

### Rework Contract

```text
Issue
Evidence
Expected
Required Change
Re-run
```

模板：`templates/rework-contract.md`

### Closeout Contract

只在 `CODE_VERIFIED` 后更新受影响知识面。

模板：`templates/closeout-contract.md`

---

# Review / Completeness / Verification

Alpha 2 暂时保留 3.0.1 已成熟的后半段治理：

```text
AGY delivery
→ Codex Diff Review
→ Completeness / Blast Radius
→ Codex Independent Verification
→ CODE_VERIFIED
→ Knowledge Closeout
→ ACCEPTED
```

Alpha 3 将把 Review 正式升级为：

```text
              AGY Delivery
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
Spec Fidelity   Quality    Completeness
      └────────────┼────────────┘
                   ▼
              Verification
```

---

# 当前 Active 文件

```text
resources/
├── task-sizing.md
├── shaping.md
├── spec-contract.md
├── execution-slicing.md
├── agy-execution.md
├── run-lifecycle.md
├── failure-modes.md
├── tty7-supervision.md
├── pi-interaction.md
├── completeness-regression.md
├── review-gates.md
└── closeout-governance.md

templates/
├── execution-unit.md
├── rework-contract.md
└── closeout-contract.md
```

旧 `pi-harness.md` / `provider-boundary.md` 属于 3.0.x 架构历史，不再决定 3.1 主链。

---

# 当前演进

```text
v2.1.x
Codex → tty7 → AGY

v3.0 / 3.0.1
探索 Pi Native Harness / Provider 路线

v3.1 Alpha 1
Workflow First：Size → Shape → Spec → Slice

v3.1 Alpha 2
AGY official CLI headless-first
+ tty7 interactive fallback
+ Pi optional specialist
```

下一阶段：**Alpha 3 — Three-Axis Review + Bugfix Workflow**。
