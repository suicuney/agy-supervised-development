# Sol High Plan Review

Use this gate only before implementation.

```text
Codex = Plan Owner
Sol High = Independent Plan Reviewer
ego-browser / ego-lite = Sole Browser Transport
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

Use the installed `sol-high-plan-review` Skill for packet format, verdict parsing, and model-truth expectations. Transport selection and browser operations are governed strictly by `resources/ego-browser-runbook.md`; the paired skill cannot override transport or reintroduce a manual confirmation gate. Interaction and send policies are authoritatively owned by the plugin kernel (`SKILL.md`) and entrypoint.

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
- 语义上忠实于同一份待冻结可执行计划（完整 packet 可额外包含评审元数据、sentinels、验收准则及契约包装）；
- 不用 packet 字符数、文件大小、附件大小代替计划内容；
- 不需要把完整技术 packet 原样倒给用户。

**自动发送策略（无需确认）**：
展示中文计划预览后，**不向用户请求发送确认**。Codex 自动执行数据包安全性检查（确保无凭据或敏感信息）及 ego-browser 预检。各项 Fail-Closed 门禁均通过后，**自动发送且仅发送一次**。
配套的 `sol-high-plan-review` Skill 仅提供数据包结构与裁决语义，无权重新引入人工确认门禁。

后续 `REVISE` 轮次由 Codex 自动 `Adopt / Reject / Modify` 并继续同一会话，**不要求发送确认**。

只有以下情况才打断用户：

```text
数据包包含凭据等敏感内容（Credential findings / Hard Stop）
AUTH_REQUIRED（登录交接）
USER_CONTROLLING（用户正在控制，严禁未经授权接管）
MODEL_MISMATCH（模型非 GPT-5.6 Sol 或推理深度非 High，严禁静默降级）
USER_DECISION_REQUIRED
真正 one-way / product / architecture decision
Send 状态 UNKNOWN（终态，无重试跃迁，严禁自动重发）
其他真实 blocker
```

## Browser Runbook

All browser operations use `ego-browser` / `ego-lite` following `resources/ego-browser-runbook.md`.

The execution flow uses:
1. Isolated task space (`useOrCreateTaskSpace`) reusing `task.id`.
2. Exact tab selection (`openOrReuseTab`, `listTabs`, `switchTab`).
3. Semantic observation with `snapshotText()` before consequential actions.
4. Pre-send verification of visible state:
   ```text
   Model family = GPT-5.6 Sol
   Reasoning     = High
   ```
5. Inspection for pre-send failure states and hard stops:
   - Credential-like packet findings: hard stop, do not submit secrets.
   - Login / auth missing (`AUTH_REQUIRED`): hand off to user with `handOffTaskSpace`.
   - Control conflict (`USER_CONTROLLING`): hard stop, wait for user confirmation before `takeOverTaskSpace`.
   - Model / reasoning mismatch (`MODEL_MISMATCH`): hard stop, do not silently substitute.
6. Single Send with duplicate-send safety (never resend automatically from `UNKNOWN`).
7. Polling and reading in the same conversation.
8. Dedicated task space cleanup with `completeTaskSpace(task.id, { keep: false })`.

## Packet and Send State

Track explicitly:

```text
NOT_SENT → SENT | UNKNOWN
```

- `NOT_SENT → SENT`: 必须有同一会话内的可见证据（证明 packet 已送达且 assistant 开始生成）。
- `NOT_SENT → UNKNOWN`: 若发送前后网络、超时或 UI 状态存在歧义，状态立即转为 `UNKNOWN`。
- `UNKNOWN` 是终态（terminal state），**不存在向重试的跃迁（no retry transition）**。严禁自动重新发送（Duplicate-Send Safety）。
- 若要排查 `UNKNOWN`，在同一会话中调用 `await snapshotText()` 检查是否已送达。若仍未解决，停机并向用户汇报真实状态，绝不自动重发。

After Send, wait for assistant generation to finish, then read the same conversation. A review is complete only when the required sentinel is present and the response contains exactly one of `PASS`, `REVISE`, or `USER_DECISION_REQUIRED`.

## Loop

```text
Codex Plan
→ 第一轮中文计划预览
→ 预检通过后自动发送（不请求确认）
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

If ego-browser / ego-lite, ChatGPT login, GPT-5.6 Sol, or High is unavailable, do not silently substitute another model or transport.

Report the capability failure. The user may fix the capability or explicitly disable plan review for the task.
