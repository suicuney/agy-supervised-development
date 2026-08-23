# AGY Supervised Development 3.1 — Workflow First

当前开发版本：**3.1.0-alpha.3**

这是一个以 **Codex App 负责 Shape / Spec / Review / Verification，官方 AGY CLI 负责实现，Git Repository 负责事实证明** 的定制监督式开发 Skill。

> **Codex shapes and proves. AGY builds. Git tells the truth.**

3.1 不再把“选哪个 Harness”当项目中心，而是把一次软件开发稳定拆成：

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
→ BUILD
→ THREE-AXIS REVIEW
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
              Shape / Spec / Slice / Review
                          │
                    Execution Unit
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
         ┌────────────┼────────────┐
         ▼            ▼            ▼
   Spec Fidelity    Quality    Completeness
         └────────────┼────────────┘
                      ▼
             Independent Verify
                      ▼
                 CODE_VERIFIED
                      ▼
                   Closeout
                      ▼
                   ACCEPTED

Optional sidecar:
Codex ─────→ Pi specialist
             research / second opinion / blast-radius analysis
```

---

# 3.1 三个已经落地的阶段

## Alpha 1 — Workflow Kernel

```text
SIZE → SHAPE → SPEC → SLICE
```

核心能力：

- Small / Medium / Large 路由；
- Decision Tree / Frontier；
- Resolved / Open / Fog / Out-of-Scope；
- Spec 与施工单分离；
- Verification Seam；
- Vertical Slice / Tracer Bullet；
- Wide Refactor 使用 Expand → Migrate → Contract。

## Alpha 2 — AGY Execution Adapter

```text
Execution Unit
→ AGY official CLI headless / stream-json
→ repository
```

核心能力：

- 官方 AGY CLI 作为 Primary Writer；
- `conversation_id` 精确 resume；
- `init.cwd == repo_root`；
- `SUCCESS != PASS`；
- headless permission soft-deny 不伪装成测试成功；
- 默认不使用 `--dangerously-skip-permissions`；
- tty7 只做 interactive fallback；
- Pi 降级为 optional specialist。

## Alpha 3 — Review Intelligence

```text
                 AGY Delivery
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   Spec Fidelity    Quality   Completeness
          │           │           │
          └───────────┼───────────┘
                      ▼
             Independent Verify
```

### A. Spec Fidelity — 做对了吗？

检查：

```text
Acceptance coverage
missing / partial requirement
wrong semantics
scope creep
unauthorized decisions
Verification Seam fidelity
```

### B. Engineering Quality — 写得好吗？

检查：

```text
architecture / module responsibility
contract / data consistency
correctness / edge cases
error handling / observability
security / side effects
backward compatibility
code smells / speculative generality
test quality / implementation coupling
```

### C. Completeness — 漏了吗？

做 Missing Diff Review：

```text
changed behavior
→ callers / consumers
→ types / validation / serialization
→ schema / migration / existing data
→ sibling flows / jobs
→ error / retry / fallback
→ cache / derived state
→ old/orphaned path
→ tests
→ knowledge impact
```

汇总不是打平均分：

```text
A PASS + B PASS + C PASS → REVIEW PASS
any REWORK               → REWORK_REQUIRED
any BLOCKED              → BLOCKED
```

---

# Bug Intelligence

## Simple deterministic bug

```text
REPRODUCE
→ RED
→ ROOT-CAUSE FIX
→ GREEN
→ CODEX RE-RUN
```

## Complex / uncertain bug

```text
TIGHT FEEDBACK LOOP
→ REPRODUCE
→ MINIMISE
→ RANKED/FALSIFIABLE HYPOTHESES
→ TARGETED INSTRUMENTATION
→ ROOT CAUSE
→ REGRESSION PROOF
→ FIX
→ VERIFY ORIGINAL REPRO
```

关键原则：

> **复杂 Bug 没有能抓住用户症状的反馈环，就不要把第一个代码猜测包装成根因。**

---

# 为什么 Review 和 Verification 分开

```text
Review
= 对代码、Spec、传播面的工程判断

Verification
= Codex 自己实际运行验证命令取得执行证据
```

所以：

```text
AGY SUCCESS
!= REVIEW PASS

REVIEW PASS
!= CODE_VERIFIED

CODE_VERIFIED
!= ACCEPTED
```

Verification 失败会形成 `V*` finding，返工后重新过 Three-Axis Review，再重新 Verification。

---

# Finding IDs

Review / Rework 使用稳定 Finding ID：

```text
S* = Spec Fidelity
Q* = Engineering Quality
C* = Completeness
V* = Independent Verification
K* = Knowledge Closeout
```

例如：

```text
C1
Axis: Completeness
Issue: export script still calls retired signature
Evidence: rg / call-chain
Expected: all reachable callers migrated
```

AGY 返工必须收到具体 Finding + Evidence，不发送“再检查一下有没有漏改”。

---

# 任务大小与实际使用

## Small

```text
Compact Shape/Spec
→ one Execution Unit
→ AGY
→ Three-Axis Review
→ Verify
→ Closeout
```

适合：明确 bug、字段校验、小范围 contract 修正。

## Medium

```text
Shape
→ Spec
→ 2~5 verifiable slices
→ AGY slice-by-slice
→ Three-Axis Review / Rework
→ Verify
→ Closeout
```

这是默认主力流程。

## Large

```text
Destination
→ Decision Map / Fog
→ resolve frontier
→ Spec
→ staged slices / migration sequence
→ AGY
→ Three-Axis Review
```

只在真正大且不确定的工作中使用，不把普通 Feature 强行变成 Issue DAG。

---

# Active Files

```text
SKILL.md

resources/
├── task-sizing.md
├── shaping.md
├── spec-contract.md
├── execution-slicing.md
├── agy-execution.md
├── bugfix-workflow.md
├── review-gates.md
├── completeness-regression.md
├── run-lifecycle.md
├── failure-modes.md
├── closeout-governance.md
├── tty7-supervision.md
└── pi-interaction.md

templates/
├── execution-unit.md
├── review-report.md
├── rework-contract.md
└── closeout-contract.md

evals/
├── README.md
└── scenarios.json
```

---

# 不做什么

3.1 默认不要求：

```text
custom Pi harness
pi-supervisor daemon
custom Run Store
custom operation protocol
Goal/DAG for every task
GitHub issue for every tiny change
tty7 screen scraping for every AGY turn
third-party Antigravity OAuth provider as main path
```

Runtime 只是执行层；Workflow 才是本 Skill 的长期核心。

---

# Definition of Done

```text
DONE
=
Spec satisfied
+ Engineering Quality PASS
+ Completeness PASS
+ Independent Verification PASS
+ Regression/Bug Proof satisfied when applicable
+ Knowledge aligned
+ Baseline preserved
+ No unauthorized one-way/external side effects
```

只有 Codex 可以最终标记：

```text
ACCEPTED
```
