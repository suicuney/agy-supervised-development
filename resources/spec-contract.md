# Spec Contract — Freeze What Was Decided

Spec 的职责是把已经完成的 Shaping 固化成 **稳定、可验证、可交接的产品/技术契约**。

Spec 不是施工日志，也不是把所有代码细节提前写死。

核心原则：

> **Shaping makes decisions. Spec records decisions. Execution implements decisions. Review checks fidelity.**

---

## 1. Spec 必须回答什么

```text
Problem
Expected Behavior
Important Scenarios
Implementation Decisions
Acceptance Criteria
Verification Seams
Out of Scope
Known Constraints / One-way Decisions
```

对于 Medium/Large 任务，Spec 是 Codex → 后续切片/实现/Review 的稳定输入。

---

## 2. 推荐模板

```markdown
# <Feature / Change> Spec

## Problem
用户/系统当前遇到什么问题，为什么需要改。

## Expected Behavior
完成后用户或外部系统能观察到什么变化。

## Scenarios / Stories
1. Given ... when ... then ...
2. ...

## Implementation Decisions
- 已决定的模块职责/协议/数据语义。
- 已决定的兼容策略。
- 已决定的错误/边界语义。

## Acceptance Criteria
- [ ] 可独立验证的条件 1
- [ ] 可独立验证的条件 2

## Verification Seams
Primary seam:
- <最高层、最稳定的可观察边界>

Secondary seams:
- <仅在必要时>

Prior art:
- <repo 中已有类似测试/验证方式>

## Test Strategy
- Unit: required | not-applicable
- Integration: required | not-applicable
- E2E: required | not-applicable | user-skipped

## Out of Scope
- ...

## Constraints / One-way Decisions
- ...

## Further Notes
- 非阻塞信息。
```

---

## 3. Spec 不应默认包含什么

避免默认写：

```text
具体文件路径
具体行号
完整代码实现
未来很可能变化的 class/function 名称
逐文件施工清单
```

原因：这些内容容易随着实现演进迅速过期，并把 Spec 从“行为和决定的权威”变成“一次性的施工猜测”。

例外：prototype 得出的某个状态机、schema/type shape 本身就是被确认的设计决定，而且 prose 无法更准确表达时，可以保留最小 decision-rich snippet。

---

## 4. Verification Seam

3.1 在原有 Unit / Integration / E2E 之外，显式记录 **从哪里观察正确行为**。

Seam 是稳定公共边界，例如：

```text
HTTP endpoint
public service interface
CLI command
message/event contract
browser user flow
filesystem contract
```

优先级：

```text
Existing seam > invented seam
Higher stable seam > internal seam
Fewer meaningful seams > testing every implementation detail
```

例：

```text
Primary seam: POST /orders
Integration: required
Unit: not-applicable for orchestration behavior
E2E: required for browser checkout flow
```

不要通过 private method / internal mock interaction 证明用户行为。

---

## 5. Acceptance Criteria

Acceptance Criteria 必须是 Codex 可以独立判断的事实。

好：

```text
- 重复提交同一个 idempotency key 时只创建一个订单。
- API 第二次请求返回同一个 order id。
- integration test 在 unfixed behavior 上失败、修复后通过。
```

差：

```text
- 代码写得优雅。
- 尽量复用现有逻辑。
- 修复相关问题。
```

后者是 implementation guidance，不是验收条件。

---

## 6. Implementation Decisions

Spec 可以写：

- 模块职责变化；
- API/Schema/Message contract；
- 数据兼容策略；
- error/retry semantics；
- 权限/边界规则；
- migration strategy；
- 已确认的 architecture decision。

Spec 不需要决定：

- 普通局部 helper 怎么命名；
- 等价的内部代码组织；
- 不影响外部 contract 的小型 refactor；

这些留给 Worker，实现后由 Quality Review 判断。

---

## 7. Compact Spec for Small Tasks

Small task 可以内联：

```text
Problem:
Expected:
Acceptance:
Primary Test Seam:
Out of Scope:
Regression Proof:
```

不为了形式创建单独长文档。

---

## 8. Spec Ready Gate

进入 `SPEC_READY` 前确认：

```text
Critical Shape decisions are reflected
Expected behavior is testable
Acceptance criteria are observable
Primary verification seam is chosen
Test-layer applicability recorded
Out of Scope is explicit
No hidden product/architecture decision is delegated to Worker
```

如果 Spec 写到一半又暴露关键 undecided behavior：

```text
SPEC → SHAPING
```

先解决决定，再继续。

---

## 9. Spec 与 Review 的关系

后续 Spec Review 只问：

```text
Did the implementation faithfully deliver this Spec?
```

因此 Spec 必须保持稳定，不要在实现后为了让代码“看起来符合”而偷偷改写需求。

如果需求真的改变：

1. 显式记录 decision change；
2. 更新 Spec；
3. 重新判断已经完成的 slice 是否需要 rework；
4. 保留变更原因。