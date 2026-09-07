# Rework Contract Template

Codex Three-Axis Review / Independent Verification / Closeout 发现问题后，优先发送给**同一个 Herdr-managed AGY worker**。Herdr 负责 native session continuity；Contract 本身不携带或调用 AGY resume 命令。

```text
Rework Contract

Source
- Execution Unit: <name>
- Herdr Agent: <stable task-local agent name>
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

稳定 ID 让 Review → Rework → Re-review 可以准确追踪，不依赖 session memory。

## 合并规则

多个 finding 只有在同一 root cause 或同一小范围修改可一起解决时才放进同一 Rework Contract。

## Re-review 规则

- 不发送模糊的“继续”“再检查一下”“修一下刚才的问题”。
- Herdr/AGY conversation history 是辅助上下文，不替代 Evidence。
- Herdr `done` / AGY self-report 后仍必须回 Codex Three-Axis Review。
- 即使只修一个 Q finding，也重新确认 Spec Fidelity / Quality / Completeness。
- Verification finding 修复后不能直接回 VERIFYING；先重新 Three-Axis Review。
