# Execution Unit Template

用于把一个已批准的 Spec slice 交给 **Herdr-managed AGY Primary Worker**。

```text
Execution Unit

Identity
- Unit: <name / sequence>
- Source Spec: <spec reference>
- Change Shape: vertical-slice | expand | migrate | contract
- Work Type: feature | bugfix | refactor | migration | other

Goal
- 本轮必须交付的一个可验证行为。

User / System Observable Outcome
- 完成后，外部可观察到什么新增或变化行为。

Scope
- 允许修改的模块 / contract / data / tests。
- 已证明属于本 slice 的 propagation surface。

Out of Scope
- 本轮明确不处理的相邻工作。

Resolved Decisions
- 从 Shaping / Spec 继承的关键已决事项。
- Worker 不得重新定义这些语义。

Constraints
- compatibility / architecture / security / data rules
- baseline-owned changes must be preserved
- no push / merge / release / deploy unless explicitly authorized
- no destructive / one-way action without explicit authorization

Acceptance Criteria
1. <observable criterion>
2. <observable criterion>

Verification Seam
- Primary: <public boundary>
- Secondary: <optional>

Test Strategy
- Unit: required | not-applicable
- Integration: required | not-applicable
- E2E: required | not-applicable | user-skipped
- Regression Proof: required | not-applicable

Bug Evidence — only when Work Type = bugfix
- Bug Class: simple-deterministic | complex-uncertain
- User Symptom: <exact observable failure>
- Feedback Loop: <command/script/repro | not-yet-established>
- Before-fix Evidence: <RED / measurement / repro rate>
- Root Cause Evidence: <known | to-be-diagnosed>
- Original Repro Must Be Re-run After Fix: yes | not-applicable

Worker Verification
- <targeted command/check expected during implementation>
- If the worker is blocked before a command actually runs, report blocked/not-run; never report it as passed.

Completeness Watch
- <caller / consumer / schema / state / job / fallback / same-root-cause sibling surfaces that must be checked>

Forbidden Actions
- unrelated refactor
- speculative dependency/config changes
- credential inspection/export
- destructive migration/deletion
- production mutation
- push/merge/release/deploy unless explicitly authorized

Report
- changed behavior
- changed files
- tests/checks actually run
- blocked/not-run checks
- permission/tool failures
- blast-radius findings
- unresolved items
- bugfix only: root cause + before/after feedback-loop evidence
```

## 规则

- 一份 Execution Unit 尽量适配一个 Worker context。
- Medium/Large 任务默认一次只交付一个 slice。
- Spec 是需求权威；Execution Unit 是这一轮施工授权。
- AGY 必须由 Herdr 启动和交互；Execution Unit 不定义第二套 Runtime。
- Worker 发现新的产品/架构决策时应停下来报告，不自行猜测。
- Worker 发现新传播面时可以调查并报告；是否扩大当前 slice 由 Codex 根据 Axis C Completeness 判断。
- Complex Bug 在 root cause 未建立前，不应把猜测直接转换成大范围代码修改；按 `resources/bugfix-workflow.md` 建立反馈环和诊断证据。
