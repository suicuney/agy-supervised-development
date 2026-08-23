# Rework Contract Template

Codex Three-Axis Review / Independent Verification / Closeout 发现问题后，用真实 AGY `conversation_id` resume，并发送完整、证据驱动的 Rework Contract。

```text
Rework Contract

Source
- Execution Unit: <name>
- Conversation: <real AGY conversation id>
- Review cycle: <n>

Finding
- ID: <S1 | Q1 | C1 | V1 | K1>
- Axis / Source: <Spec Fidelity | Engineering Quality | Completeness | Verification | Closeout>
- Severity: <blocking | major | normal>

Issue
- <一个明确、可修复的问题>

Evidence
- <Spec clause / git diff / code / test / search / call-chain / runtime evidence>

Expected
- <正确行为 / 正确 contract / 正确质量边界 / 完整传播面>

Required Change
- <本轮必须修复什么>

Re-run
- <Worker 应重新执行的 targeted checks/search/repro>

Scope Reminder
- 保持原 Spec / Execution Unit 范围。
- 只允许已被 Completeness 证明为 unfinished 的新增 propagation surface。

Do Not
- 不顺手重构无关代码。
- 不重新解释已冻结的产品决策。
- 不通过删/skip 测试换 GREEN。
- 不 push / merge / release / deploy。
- 不执行未授权 one-way action。

Report
- addressed finding IDs
- fix summary
- changed files
- tests/checks actually run
- blocked/not-run checks
- unresolved items
```

## Finding ID 规则

```text
S* = Spec Fidelity
Q* = Engineering Quality
C* = Completeness
V* = Codex Independent Verification
K* = Knowledge Closeout
```

稳定 ID 让 Review → Rework → Re-review 可以准确追踪，不依赖“刚才那个问题”这种 session memory。

## 合并规则

一个 Rework Contract 可以包含多个 finding，但仅当它们：

```text
同一 root cause
或
同一小范围修改可以一起解决
```

否则分开，避免一个大返工包同时改产品语义、架构和无关 caller。

## Re-review 规则

- 不发送模糊的“继续”“再检查一下”“修一下刚才的问题”。
- Conversation history 是上下文，不替代 Evidence。
- AGY 本轮 `SUCCESS` 后仍必须回 Codex Three-Axis Review。
- 即使只修一个 Q finding，也重新确认 Spec Fidelity / Quality / Completeness，防止返工引入新问题。
- Verification finding 修复后不能直接回 VERIFYING；先重新 Three-Axis Review。