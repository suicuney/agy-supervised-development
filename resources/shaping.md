# Shaping — Resolve Decisions Before Planning Execution

Shaping 的目标不是写开发计划，而是把 **该由人/架构层决定的问题先决定清楚**，避免 Worker 在实现时偷偷补全需求。

核心原则：

> **Facts are discovered by Codex. Decisions are made explicitly. Unclear future work stays fog until it becomes a precise question.**

---

## 1. Design Tree

把需求看成一棵 Decision Tree：

```text
Destination / Goal
├─ Decision A
│  ├─ Decision C
│  └─ Decision D
└─ Decision B
   └─ Decision E
```

一个问题只有在它依赖的前置决定已经解决后，才进入当前 `frontier`。

不要提前回答依赖未决问题的下游问题。

---

## 2. Frontier

`Frontier` = 当前已经具备全部前置条件、现在就能可靠讨论/决定的问题。

Codex 每轮：

1. 列出当前 frontier；
2. 先自行查清能从 repository / docs / tools 得到的事实；
3. 只把真正需要产品/架构取舍的决定交给用户；
4. 决定完成后重新计算 frontier。

原则：

```text
Can Codex look it up? → Codex investigates.
Requires product/architecture preference? → User decides.
Depends on unresolved decision? → Later frontier.
```

---

## 3. Shape Record

Medium/Large 任务维护一份轻量 Shape Record：

```text
Goal / Destination

Resolved Decisions
- ...

Open Decisions
- ...

Not Yet Specified
- ...

Out of Scope
- ...

One-way Decisions
- ...
```

### Resolved Decisions

已经明确、后续 Spec 可以依赖的决定。

### Open Decisions

问题已经能精确描述，但还没有答案。

### Not Yet Specified

知道这个区域之后可能需要处理，但现在还不能准确提出问题。

这是 **Fog of Work**，不是 TODO 列表。

例如：

```text
Not Yet Specified
- 维度删除后的历史数据治理可能需要单独策略；具体问题取决于删除语义决定。
```

### Out of Scope

已经明确不属于当前 destination 的工作。

Out of Scope 不会随着 frontier 自动“毕业”为本任务；只有用户重新定义 destination 才能回来。

### One-way Decisions

高代价、难回退、会影响外部兼容/权限/数据的决定：

- destructive migration；
- breaking public API；
- auth/tenancy relaxation；
- billing/money semantics；
- irreversible deletion；
- production mutation。

这些不能被 Worker 默认决定。

---

## 4. Facts vs Decisions

不要把事实问题扔给用户：

错误：

> “这个接口现在有哪些 caller？”

Codex 应先搜索代码。

正确的用户问题是：

> “当前有三个 caller。为了兼容旧 consumer，我们可以双轨保留旧接口，或者一次性 breaking change。你希望哪个方向？”

Shaping 的价值就是把：

```text
unknown fact
```

变成：

```text
known evidence + explicit decision
```

---

## 5. Repository Grounding

Shaping 不能只靠聊天。

需要时检查：

```text
existing architecture
current API/schema/contracts
callers/consumers
existing tests and seams
project rules / ADR / CONTEXT
baseline repository state
```

如果用户描述与当前代码冲突，必须显式指出并要求裁决，而不是默默选一边。

---

## 6. Prototype as a Decision Tool

当问题是：

- “这个 UI 到底应该长什么样？”
- “这个状态模型实际跑起来是否合理？”
- “两种交互哪个更顺？”

允许先做 throwaway prototype 来提高讨论清晰度。

Prototype 只回答具体决策问题，不是提前偷偷实现生产功能。

确认的决定进入 Resolved Decisions / Spec；prototype 本身不自动成为 production contract。

---

## 7. Shaping Exit Gate

只有满足以下条件才进入 `SPEC_READY`：

```text
Goal is explicit
Critical behavior decisions resolved
Known one-way doors resolved or explicitly blocked
Open Decisions = none that would force Worker to invent product/architecture semantics
Not Yet Specified does not block the next implementation boundary
Out of Scope explicit enough to prevent scope creep
```

可以保留 implementation-time reversible choices，例如局部函数命名、等价小实现细节；这些不需要把 Shaping 无限拖长。

---

## 8. Small Task Shortcut

Small task 如果：

- 目标明确；
- 没有真正 open decisions；
- 当前代码已提供足够 context；

可以把 Shape Record 压缩成：

```text
Decision status: clear
Out of scope: ...
One-way doors: none
```

直接进入 Compact Spec。

---

## 9. Anti-patterns

### AI 自动补全 40% 的模糊需求

看起来计划完整，实际上只是把隐含假设变成代码。

### 一开始就拆 tickets

如果关键行为还没决定，ticket 只是在给猜测编号。

### 把所有未来可能问题都变成 ticket

还说不清的问题应该留在 `Not Yet Specified`，不要制造假的精确度。

### Endless grilling

Shaping 只解决会影响当前 delivery 的决定。可逆、局部实现细节交给 Worker + Review，不需要用户逐个拍板。