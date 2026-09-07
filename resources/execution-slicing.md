# Execution Slicing — Vertical Slices and Wide Refactors

Spec 解决“做什么”；Slicing 解决“以什么粒度交给 Worker 做”。

3.3 默认不把整个 Medium/Large Spec 一次塞给 Primary Worker，而是先生成可独立验证的 Execution Units。

## 1. 默认：Vertical Slice / Tracer Bullet

一个好的 slice 是一条窄但完整的行为路径：

```text
input / user action
→ business behavior
→ persistence/integration
→ observable output
→ verification
```

不要默认拆成“所有 DB / 所有 API / 所有 UI / 最后补测试”的横向批处理。

## 2. Slice 必须满足

```text
Narrow
Complete
Independently reviewable
Independently verifiable when practical
Fits one fresh Worker context
Keeps repository in an understandable state
```

每个 slice 都应该能回答：这一小步完成后，新增了哪个真实可观察能力？

## 3. Execution Unit

每个 slice 转换为一个 Execution Unit：

```text
Slice Goal
Spec Source
Scope / Out of Scope
Context
Acceptance
Verification Seam
Completeness Focus
Constraints
Report
```

Execution Unit 是短期施工单；Spec 是行为/决定权威。

## 4. Dependency / Frontier

`Frontier` = blockers 已满足、当前可执行的 slices。

默认单 Writer：

```text
Slice
→ Herdr-managed AGY
→ Codex Review
→ PASS/REWORK
→ next frontier slice
```

不要因为后面还有其他 slice 就跳过当前 Review。

## 5. Prefer real dependencies

只有 `B cannot be implemented or verified correctly until A exists` 才是真 blocker。两个独立 slice 因 single-writer 顺序执行，不需要伪造业务依赖。

## 6. Prefactor

必要时允许一个极小、behavior unchanged 的 prefactor：

```text
Make the change easy
→ then make the easy change
```

不得借机做通用架构重写。

## 7. Wide Refactor Exception

rename shared field、shared type signature、cross-codebase contract migration 等 wide refactor 使用：

```text
EXPAND
→ MIGRATE A
→ MIGRATE B
→ ...
→ CONTRACT
```

规则：Expand 尽量 additive；每个 migrate batch 有明确 blast radius；Contract 前要有 zero-consumer evidence。

## 8. Slice Review Boundary

每个 slice 完成后至少做：

```text
Spec Fidelity for this slice
Scope / obvious Quality issues
Local Completeness / Blast Radius
Targeted Verification
```

全部 slices 完成后再做 Global Spec Review、Global Completeness、cross-slice integration verification、Knowledge Closeout。

## 9. When to Re-slice

如果 slice 需要远超预期上下文、无法独立解释/验证、新 decision 改变后续 slices、hidden caller 让 scope 失真、或连续返工说明粒度有问题：

```text
pause execution
→ update evidence
→ return to SHAPING / SPEC / SLICING
→ generate new frontier
```

不要把计划当不可修改的脚本。

## 10. Sliced Gate

```text
Every required behavior is covered by at least one slice
No slice is merely a horizontal layer unless justified
Each slice has observable acceptance
Dependencies/blockers are explicit
Each slice is plausible for one Worker context
Wide refactors use Expand/Migrate/Contract
Out-of-scope work is not hidden in a slice
```

Small task可以只有一个 implicit slice；Medium/Large 默认显式 slicing。
