# AGY Supervised Development 3.1 — Workflow First

> 当前分支：`3.1.0-alpha.1`。本批次先落地 **Workflow Kernel**，后续再收敛 AGY Runtime 和三轴 Review。

这是一套面向个人日常软件开发的监督式流程：

> **Codex shapes and proves. AGY builds. Git tells the truth.**
>
> **Codex 想清楚、拆清楚、验清楚；AGY 负责实现；Git 负责作证。**

3.1 不再把 Skill 的核心定义成“怎么控制某个 Harness”，而是定义一次开发应该如何从模糊需求走到可证明的交付。

---

## 核心流程

```text
User
 ↓
Codex App
 ↓
SIZE
Small / Medium / Large
 ↓
SHAPE
Resolved / Open / Fog / Out-of-Scope
 ↓
SPEC
Behavior / Decisions / Acceptance / Test Seams
 ↓
SLICE
Vertical Slices or Expand→Migrate→Contract
 ↓
Primary Worker
Target: Official AGY CLI
 ↓
Repository
 ↓
Codex Review / Rework
 ↓
Completeness / Blast Radius
 ↓
Independent Verification
 ↓
Knowledge Closeout
 ↓
ACCEPTED
```

Workflow 与 Runtime 解耦：以后 AGY 使用 headless、tty7 交互 fallback，或者某个 specialist 工具，都不应该改变 Size / Shape / Spec / Slice / Review 的方法。

---

# 第一批：Workflow Kernel

## 1. Task Sizing

见 `resources/task-sizing.md`。

不是所有任务都跑同样重的流程：

### Small

```text
Compact Spec
→ Implement
→ Review
→ Verify
```

适合明确局部 bug、小接口、小校验。

### Medium

```text
Shape
→ Spec
→ 2–5 Vertical Slices
→ Implement / Review per slice
→ Global Verify
```

这是正常 Feature 的默认路径。

### Large

```text
Destination
→ Decision Map / Fog
→ Resolve Decisions
→ Spec
→ Slice
→ staged implementation
```

只有真正跨系统、大迁移、大重构、决策高度不确定时才使用重流程。

---

## 2. Shaping

见 `resources/shaping.md`。

Codex 不急着生成施工计划，而是先区分：

```text
Resolved Decisions
Open Decisions
Not Yet Specified
Out of Scope
One-way Decisions
```

采用 `frontier` 思路：只处理前置决定已经解决的问题。

能从代码/文档查到的事实由 Codex 自己调查；真正需要产品/架构取舍的决定才交给用户。

关键规则：

> **看不清的问题先留在 Fog，不要提前制造假的 Ticket 精度。**

---

## 3. Spec Contract

见 `resources/spec-contract.md`。

Spec 固化已经做出的决定：

```text
Problem
Expected Behavior
Scenarios
Implementation Decisions
Acceptance Criteria
Verification Seams
Test Strategy
Out of Scope
Constraints / One-way Decisions
```

Spec 默认不写成逐文件施工单，也不依赖容易过期的行号/内部实现细节。

### Verification Seam

3.1 在原来的 Unit / Integration / E2E 之外，新增一个重要概念：

> **从哪个稳定公共边界观察这个行为？**

例如：

```text
Primary Seam: POST /orders
Integration: required
E2E: required for checkout flow
```

优先复用已有的高层稳定 seam，避免测试绑定内部实现。

---

## 4. Execution Slicing

见 `resources/execution-slicing.md`。

Medium/Large Spec 不默认一次交给 Worker。

### Vertical Slice / Tracer Bullet

```text
input
→ behavior
→ persistence/integration
→ observable output
→ verification
```

每个 slice 应该窄、完整、可 Review、尽量可独立验证，并适合一个 fresh Worker context。

不要默认这样水平切：

```text
先所有 DB
→ 再所有 API
→ 再所有 UI
→ 最后补测试
```

### Wide Refactor

共享字段、类型、签名等 blast radius 很大的机械迁移使用：

```text
EXPAND
→ MIGRATE A
→ MIGRATE B
→ ...
→ CONTRACT
```

旧 form 删除前要求 zero-consumer evidence。

---

# 角色

| 角色 | 3.1 职责 |
|---|---|
| User | 产品/架构/one-way 决策 |
| Codex App | Shape、Spec、Slice、Review、Verification、Final Acceptance |
| AGY CLI | Target Primary Implementer / Writer |
| Pi | Optional Specialist，不要求进入主链 |
| tty7 | Optional Interactive Runtime / fallback |
| Git | Source of Truth |

---

# 3.1 保留的成熟资产

3.1 不推翻前几版已经成熟的后半段治理：

- Git baseline protection；
- repository state as source of truth；
- Evidence-driven Rework；
- Change Completeness / Blast Radius；
- unfinished vs different-ticket boundary；
- Unit / Integration / E2E applicability；
- deterministic bugfix RED → root-cause fix → GREEN；
- Codex Independent Verification；
- `CODE_VERIFIED != ACCEPTED`；
- Knowledge Closeout；
- one-way-door / no push-merge-release-deploy by default。

---

# 当前 active files

```text
agy-supervised-development/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── resources/
│   ├── task-sizing.md            # 3.1 new
│   ├── shaping.md                # 3.1 new
│   ├── spec-contract.md          # 3.1 new
│   ├── execution-slicing.md      # 3.1 new
│   ├── completeness-regression.md
│   ├── review-gates.md           # Phase 2 将升级三轴 Review
│   ├── closeout-governance.md
│   └── run-lifecycle.md
├── examples/
└── evals/
```

旧 `pi-interaction.md` / `provider-boundary.md` / `pi-harness.md` 目前保留用于历史迁移与后续整理，**不是 3.1 Workflow Kernel 的核心依赖**。

---

# 下一批计划

Alpha 2：

```text
AGY Execution Adapter
- Official AGY CLI as Primary Worker
- headless-first
- tty7 interactive fallback
- runtime 与 Workflow 解耦
```

Alpha 3：

```text
Three-Axis Review
- Spec Fidelity
- Engineering Quality
- Completeness / Blast Radius

+ dedicated complex-bug workflow
+ examples
+ evals
+ legacy runtime cleanup
```

3.1 的长期目标不是做另一个 Orca/Maestro，而是形成稳定、轻量、适合个人长期使用的软件开发方法。