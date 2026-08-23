# Rework Contract Template

Codex Review / Completeness / Verification 发现问题后，用真实 AGY `conversation_id` resume，并发送完整 Rework Contract。

```text
Rework Contract

Source
- Execution Unit: <name>
- Conversation: <real AGY conversation id>
- Review cycle: <n>

Issue
- <一个明确问题>

Evidence
- <git diff / code / test / search / runtime evidence>

Expected
- <正确行为 / 正确 contract / 正确范围>

Required Change
- <本轮必须修复什么>

Re-run
- <Worker 应重新执行的 targeted checks>

Scope Reminder
- 保持原 Spec / Execution Unit 范围。
- 只允许已被 Completeness 证明为 unfinished 的新增 propagation surface。

Do Not
- 不顺手重构无关代码。
- 不重新解释已冻结的产品决策。
- 不 push / merge / release / deploy。
- 不执行未授权 one-way action。

Report
- fix summary
- changed files
- tests/checks actually run
- blocked/not-run checks
- unresolved items
```

## 规则

- 不发送模糊的“继续”“修一下刚才的问题”。
- 一个 Rework Contract 可以包含多个彼此同根因、同范围的 finding；无关 finding 应分开处理。
- Conversation history 是上下文，不替代 Evidence。
- AGY 本轮 `SUCCESS` 后仍必须回 Codex Review。
