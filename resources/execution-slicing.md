# Execution Slicing — Vertical Slices and Wide Refactors

Spec 解决“做什么”；Slicing 解决“以什么粒度交给 Worker 做”。

3.1 默认不把整个 Medium/Large Spec 一次塞给 Primary Worker，而是先生成可独立验证的 Execution Units。

---

## 1. 默认：Vertical Slice / Tracer Bullet

一个好的 slice 是一条窄但完整的行为路径：

```text
input / user action
→ business behavior
→ persistence/integration
→ observable output
→ verification
```

它不是某一层的横向批处理。

### 好的切法

```text
Slice 1: 用户可以创建采集任务
UI/CLI → API → service → persistence → test

Slice 2: 用户可以查看当天任务
UI → API → query → response → test
```

### 不好的切法

```text
Ticket 1: 建所有表
Ticket 2: 写所有后端 API
Ticket 3: 写所有前端
Ticket 4: 最后补测试
```

后者会制造长时间不可验证的半成品。

---

## 2. Slice 必须满足

```text
Narrow
Complete
Independently reviewable
Independently verifiable when practical
Fits one fresh Worker context
Keeps repository in an understandable state
```

每个 slice 都应该能回答：

> 这一小步完成后，新增了哪个真实可观察能力？

如果答案只是“多了几个 DTO 文件”，通常切得太横向。

---

## 3. Execution Unit

每个 slice 转换为一个 Execution Unit：

```text
Slice Goal
- 这一轮交付的唯一行为。

Spec Source
- 对应的 Spec section / acceptance criteria。

Scope
- 预计影响的模块/contract。
- 明确禁止顺手做的相邻工作。

Context
- 当前 repository state。
- 已完成前序 slices。
- 相关 resolved decisions。

Acceptance
- 本 slice 完成的可观察条件。

Verification Seam
- Primary seam。
- Worker 应运行的 targeted checks。

Completeness Focus
- 这一 slice 需要追踪的 caller/consumer/data/state propagation。

Constraints
- baseline protection。
- one-way doors。
- no push/merge/deploy unless authorized。

Report
- changed paths。
- commands/tests。
- unresolved findings。
```

Execution Unit 是短期施工单；Spec 是长期一点的需求/决定权威。不要混为同一个文档。

---

## 4. Dependency / Frontier

Slices 可以存在依赖关系：

```text
Slice A ─┐
         ├→ Slice C
Slice B ─┘
```

`Frontier` = 当前 blockers 全部完成、现在可以执行的 slices。

默认单 Writer 流程一次只取一个 frontier slice：

```text
Slice
→ Worker
→ Codex Review
→ PASS/REWORK
→ next frontier slice
```

不要因为后面还有 4 个 slice，就跳过当前 slice 的 Review。

---

## 5. Prefer behavior dependencies, not artificial sequencing

不要为了让列表看起来线性，制造假的 blocker。

只有真正满足以下条件才阻塞：

```text
B cannot be implemented or verified correctly until A exists
```

如果两个 slice 独立，但因为默认 single-writer 不能并行，只需要顺序执行，不必伪造业务依赖。

---

## 6. Prefactor

如果当前设计让一个小功能非常难实现，可以先有一个极小的 prefactor slice：

```text
Make the change easy
→ then make the easy change
```

但 prefactor 必须：

- 有明确理由；
- 比目标改动更窄；
- 不借机做通用架构重写；
- 自身保持 behavior unchanged；
- 能独立验证。

---

## 7. Wide Refactor Exception

不是所有变化都适合 vertical slice。

典型 wide refactor：

- rename shared field/column；
- shared type signature change；
- cross-codebase contract migration；
- 一个机械变化会同时影响大量 caller。

如果强行按业务 vertical slice，可能导致每一步都无法保持兼容/green。

此时使用：

# Expand → Migrate → Contract

```text
EXPAND
增加新 form，与旧 form 共存
      ↓
MIGRATE A
迁移一组 caller/consumer
      ↓
MIGRATE B
迁移下一组
      ↓
MIGRATE ...
      ↓
CONTRACT
确认旧 form 无 caller 后删除
```

规则：

- Expand 尽量 additive；
- 每个 migrate batch 按 blast radius 大小切分；
- 中间尽量保持 tests/CI green；
- Contract 被所有 migrate batches 阻塞；
- 删除旧路径前必须有 zero-consumer evidence。

如果某些 migrate batch 无法单独 green，可以显式使用 integration stage，但不能假装每一步独立通过。

---

## 8. Slice Review Boundary

每个 slice 完成后至少做：

```text
Spec Fidelity for this slice
Scope / obvious Quality issues
Local Completeness / Blast Radius
Targeted Verification
```

全部 slices 完成后再做：

```text
Global Spec Review
Global Completeness
Cross-slice integration verification
Knowledge Closeout
```

Local PASS 不等于整个 Feature PASS。

---

## 9. When to Re-slice

执行中出现以下情况时停止硬推当前计划：

- 一个 slice 需要远超预期的上下文；
- slice 无法独立解释/验证；
- 新发现的 decision 会改变多个后续 slices；
- hidden caller 让原 slice scope 明显失真；
- 一个“业务 slice”实际上是 wide refactor；
- worker 连续返工说明 Execution Unit 粒度或 contract 有问题。

处理：

```text
pause execution
→ update evidence
→ return to SHAPING / SPEC / SLICING as appropriate
→ generate new frontier
```

不要把计划当成不可修改的脚本。

---

## 10. Sliced Gate

进入 `SLICED` 前：

```text
Every required behavior is covered by at least one slice
No slice is merely a horizontal layer unless justified
Each slice has observable acceptance
Dependencies/blockers are explicit
Each slice is plausible for one Worker context
Wide refactors use Expand/Migrate/Contract
Out-of-scope work is not hidden in a slice
```

Small task 可以只有一个 implicit slice；Medium/Large 默认需要显式 slicing。