# AGY Supervised Development

一个面向 **Codex + tty7 + Antigravity CLI (`agy`)** 的监督式开发 Skill。

它不是 AGY CLI 百科，也不是通用多 Agent Framework。v2.1 系列只把一条路径做扎实：

```text
User Requirement
      ↓
Codex Supervisor
      ↓
tty7 Worker Runtime
      ↓
AGY Sole Primary Writer
      ↓
Repository Changes
      ↓
Codex Diff Review
      ↓
Change Completeness / Blast Radius Review
   ↙                         ↘
Rework → AGY                PASS
                              ↓
                    Independent Verification
                              ↓
                         CODE_VERIFIED
                              ↓
                    AGY Knowledge Closeout
                              ↓
                    Codex Closeout Review
                       ↙             ↘
                  Rework → AGY     ACCEPTED
```

## 核心原则

- Codex 负责主控、Review、Completeness / Blast Radius、QA、Knowledge Closeout Review 和最终验收。
- AGY 是唯一主要 Writer，负责实现、测试、返工，以及同步受最终实现影响的项目知识文件。
- tty7 只负责持久 PTY、独立 workspace/pane 和可观察运行时，不在 Skill 里重复造进程管理器。
- Repository state 是交付真相；`done` / `TURN_COMPLETE` 只是 Turn 返回证据。
- 每次任务先建立 Git baseline，保护用户已有改动。
- 每个任务创建独立 tty7 workspace + pane，只操作自己创建的稳定 ID。
- AGY 必须显式验证 repo root / branch，不能只相信 pane CWD。
- AGY/tty7 能力按当前安装版本实时检测。
- Review 不只看“改了什么”，还检查“本来应该改但漏掉了什么”。
- Completeness 不等于 Scope Expansion：unfinished 必须收完，different ticket 保持 out-of-scope。
- 每个任务明确 Unit / Integration / E2E 的 applicability。
- 可安全、确定性复现的 bug 默认要求 regression test **RED → fix root cause → GREEN**。
- 代码层全部通过只进入 `CODE_VERIFIED`；实际开发任务还必须完成 Knowledge Impact Scan。
- 每次开发都做 Closeout Scan，但只有真正受影响的知识面才修改文档。
- 默认不 push / merge / deploy，也不借“完整性/收尾”扩大 destructive / one-way 权限。

## v2.1 基础能力

### tty7-native Worker Lifecycle

```bash
tty7 new --json "$repo_root"
```

保存稳定 workspace id + pane id，正常结束只清理本次 workspace。

### Launch Proof

新 pane 第一次 `send --enter` 可能被 shell startup 吞掉。启动 AGY 后立刻 `capture`，确认命令真的执行；必要时只补一次 Enter。

### Native Status / Capture Fallback

```text
native status available
→ tty7 wait --until waiting,done --changed

status hook unavailable
→ tty7 agents + capture + Turn Nonce
```

Skill 不假设固定 tty7 版本一定已经给 Antigravity 增加 hook。

### Supervisor State

v2.1.2 只记录 Codex 能证明的状态：

```text
INIT
→ BASELINED
→ TTY7_ALLOCATED
→ AGY_BOOTING
→ AGY_READY
→ TURN_SENT
→ OBSERVING
→ TURN_RETURNED
→ REVIEWING
→ COMPLETENESS_REVIEW
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

`TURN_COMPLETE != ACCEPTED`，`CODE_VERIFIED != ACCEPTED`。

### Read Before Send

任何 prompt、Enter、菜单按键、Escape、Ctrl-C 之前重新 capture 当前 pane：

```text
CAPTURE → CLASSIFY → DECIDE → SEND
```

### Evidence-driven Rework

每轮返工包含：

```text
Issue
Evidence
Expected
Rework
Re-run
```

默认 3 个完整 `Review → Rework → Re-review` 周期为 soft limit。

### Scope Drift Guard

```text
current changes - baseline changes = task-introduced changes
```

AGY 新增的超 Scope path 必须有需求依据，否则返工。

## v2.1.1 — Knowledge Closeout

v2.1.1 补齐“代码完成后项目知识是否仍然正确”。

每次开发做 Knowledge Impact Scan：

```text
README / usage
AGENTS.md / CLAUDE.md / project rules
API / Schema / CLI / shared Contract
config / env / provider / service / deploy / job docs
workspace residue
```

状态：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

普通内部变化默认 Lightweight Closeout；API/schema/CLI/env/用户流程/架构/部署/job/rename/cross-project contract 等自动升级 Full Closeout。

纯内部 bugfix 可以零文档 diff，只要相关知识面已经 `verified-current`。

## v2.1.2 — Completeness & Regression Proof

v2.1.2 补的是 `CODE_VERIFIED` 之前的代码交付完整性。

### 1. Change Completeness Sweep

对于每一个语义变化，不只检查 changed files，还追踪：

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

核心判断：

> 现在交付时，Reviewer 会称剩余项为 **unfinished**，还是 **a different ticket**？

unfinished 必须本次完成；different ticket 不借 completeness 扩张 Scope。

### 2. Blast Radius 成为正式 Gate

`resources/review-gates.md` 现在把 Change Propagation & Blast Radius 作为 Gate 3。

Review 从：

```text
Review current diff
```

升级为：

```text
Review current diff
+
Review missing diff
```

### 3. Test Layer Decision

每个任务明确：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

`user-skipped` 不能被包装成 `not-applicable`。

跨边界真实流程如 UI→API→DB、service→service、CLI→filesystem 优先考虑 E2E；纯 helper/library 可明确 N/A。

### 4. Bugfix RED → GREEN

可安全、确定性复现的 bug 默认要求：

```text
Regression Test
→ unfixed behavior 上 RED
→ Fix Root Cause
→ same test GREEN
→ Codex Independent Re-run
```

无法安全/稳定复现时可以 `not-applicable`，但要记录原因和替代证据。

### 5. One-way Door

Completeness 不能自动授权：

- destructive / non-additive migration；
- breaking public API；
- auth / tenancy relaxation；
- money / billing semantics；
- secrets / credentials；
- production mutation；
- irreversible data deletion。

这类 remainder 标 `blocked-decision-needed`，由用户决定。

### 6. Skill 自测 Evals

新增 `evals/` 固定高风险场景：

```text
dirty baseline
false done
missing status hook
scope drift
hidden caller / partial propagation
bugfix red-green
wrong test layer
stale docs
zero-doc-diff closeout
one-way decision
```

目标不是测试业务代码，而是测试 Supervisor 有没有提前 ACCEPT、漏 Gate、误删用户改动或把显式 trade-off 偷偷改写。

## 为什么不默认 Worktree / Multi-Agent Wave

这个 Skill 的默认拓扑仍然是：

```text
AGY = sole primary writer
Codex = supervisor / read / review / verify
tty7 = runtime
```

用户当前 checkout 的未提交改动可能是任务上下文，所以默认继续使用 current checkout + baseline protection。

只有多 Writer 并行、高风险隔离实验或用户明确要求时才优先 worktree。

alamops 风格的多 Agent wave/file partitioning 很有价值，但不在 v2.1.2 引入，避免把单 AGY Supervisor 变成另一套通用 orchestrator。

## 文件结构

```text
agy-supervised-development/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── resources/
│   ├── agy-runtime.md
│   ├── tty7-supervision.md
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

### `resources/completeness-regression.md`

定义 Completeness Contract、Blast Radius Evidence、Scope/Completeness 边界、RED→GREEN、Test Layer Decision 和 one-way door。

### `resources/review-gates.md`

Gate 3 = Change Propagation & Blast Radius；Gate 7 = Tests/Test Layers/Regression Proof；Gate 13 = Knowledge & Documentation Alignment。

### `evals/`

定义 Supervisor 行为回归场景，让 Skill 自己也具备可重复的验收契约。

## 版本演进

```text
v2
→ Codex 怎样监督 AGY

v2.1
→ Codex 怎样通过 tty7 可靠控制一个可观察/可返工 AGY worker

v2.1.1
→ 代码验证后怎样把项目知识收尾到同一现役答案

v2.1.2
→ 怎样证明改动传播完整、测试层选择正确、bugfix 真有回归证据，并开始测试 Skill 自己
```

v2.1 系列暂不抽象 Grok/Pi/Claude 通用 Adapter，也不做多 Worker orchestration。先把 `Codex → tty7 → AGY` 单 worker 的**正确性、完整性、可验证性和终态一致性**做稳。