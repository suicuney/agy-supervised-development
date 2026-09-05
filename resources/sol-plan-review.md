# Sol High Plan Review

Use this gate only before implementation.

```text
Codex = Plan Owner
Sol High = Independent Plan Reviewer
Chrome DevTools MCP / approved Chrome session = Browser Transport
User = Product / One-way Decision Authority
```

## Default

Plan review is enabled by default.

If the user explicitly says to skip Sol review / skip plan review / execute directly, skip this gate and freeze the Codex plan without opening ChatGPT Web.

## Dependency Preflight

Run this before opening ChatGPT Web:

```bash
scripts/check-sol-plan-review.sh
```

The check uses the versioned `resources/sol-plan-review-manifest.json` and returns:

```text
0  COMPLETE
10 MISSING
11 INCOMPLETE
12 INVALID_MANIFEST
```

`SKILL.md` alone is not enough. If the result is `MISSING`, install the private source with the explicit helper and check again:

```bash
scripts/install-sol-plan-review.sh
scripts/check-sol-plan-review.sh
```

Do not treat an incomplete install as available and do not copy the private skill into this repository.

## Input

Codex first completes the executable plan from the current Shape / Spec / Slice work.

The review packet should contain only the needed truth:

```text
User Requirement
Repository Facts
Resolved Decisions
Executable Plan
Acceptance Criteria
Execution Slices
Verification Strategy
Risks / One-way Decisions
Codex Local Judgment
```

Use the installed `sol-high-plan-review` Skill for packet and browser details.

## 用户可见计划

在**第一轮发送给网页版 GPT 之前**，先用中文输出一份简洁计划，让用户知道这次准备评审什么。

默认格式保持简单：

```text
【准备发送给 Sol High 的计划】

目标
- <这次要完成什么>

计划
1. <关键步骤>
2. <关键步骤>
3. <关键步骤>

重点风险
- <真正重要的风险；没有可省略>
```

要求：

- 中文；
- 言简意赅；
- 重点说明“这次准备怎么做”；
- 不用 packet 字符数、文件大小、附件大小代替计划内容；
- 不需要把完整技术 packet 原样倒给用户。

展示后只询问一次：是否发送给 GPT-5.6 Sol High 评审。

用户确认第一轮发送后，后续 `REVISE` 轮次由 Codex 自动 `Adopt / Reject / Modify` 并继续同一会话，**不反复要求发送确认**。

只有以下情况才重新打断用户：

```text
USER_DECISION_REQUIRED
真正 one-way / product / architecture decision
登录交接
Send 状态 UNKNOWN
其他真实 blocker
```

## Browser Runbook

Use the approved Chrome browser surface and keep the semantic contract in the installed `sol-high-plan-review` Skill.

Before Send, verify visible state:

```text
Model family = GPT-5.6 Sol
Reasoning     = High
```

Do not silently switch to another browser, model, reasoning level, or transport.

## Packet and Send State

Track only:

```text
NOT_SENT → SENT
NOT_SENT → UNKNOWN
```

If the result around Send is ambiguous, keep `UNKNOWN` terminal until the same conversation visibly proves whether it was sent. Never resend automatically.

After Send, wait for assistant generation to finish, then read the same conversation. A review is complete only when the required sentinel is present and the response contains exactly one of `PASS`, `REVISE`, or `USER_DECISION_REQUIRED`.

## Loop

```text
Codex Plan
→ 第一轮中文计划预览
→ 用户确认一次
→ Sol High Review
→ Codex Adopt / Reject / Modify
→ 必要时自动下一轮
```

Maximum Sol review rounds: `3`.

Stop early when the plan has converged. Non-blocking suggestions and backlog ideas do not keep the loop open.

If round 3 still has unresolved blocking disagreement, stop and ask the user. Never start round 4.

## 最终计划展示

当 Sol Review 已经 `PASS` 或只剩 non-blocking suggestions 时，Codex 形成最终权威执行计划，并用中文输出给用户看。

默认格式：

```text
【最终执行计划】

Sol High 评审：PASS | 已收敛
评审轮次：<n>

最终计划
1. <最终执行步骤>
2. <最终执行步骤>
3. <最终执行步骤>

评审后的主要调整
- <有关键调整则列出；没有则写“无关键调整”>
```

这一步只是让用户看见最终要执行什么，**不再要求确认**。

输出后直接：

```text
PLAN FROZEN
→ BASELINE
→ AGY BUILD
```

如果 Sol 返回 `USER_DECISION_REQUIRED`，则不能冻结，必须先让用户决定。

## Freeze Boundary

When Codex records `PLAN FROZEN`, Sol High exits the task.

Do not use Sol High during AGY Build, Three-Axis Review, Rework, Independent Verification, Browser Runtime Verification, Closeout, or Acceptance.

After freeze, implementation and runtime evidence—not another model opinion—drive delivery decisions.

## Failure

If Chrome DevTools MCP, ChatGPT login, GPT-5.6 Sol, or High is unavailable, do not silently substitute another model or transport.

Report the capability failure. The user may fix the capability or explicitly disable plan review for the task.
