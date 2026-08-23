---
name: agy-supervised-development
description: A workflow-first supervised development process where Codex shapes requirements, freezes a testable spec, slices work into verifiable execution units, delegates implementation to the primary worker (target: official AGY CLI), then independently reviews, verifies, and closes out the repository. Use Small/Medium/Large task sizing, decision shaping, verification seams, vertical slices or expand-migrate-contract, baseline protection, completeness/blast-radius review, regression proof, and mandatory knowledge closeout.
version: 3.1.0-alpha.1
---

# AGY Supervised Development 3.1 — Workflow First (Alpha 1)

当用户明确使用 `$agy-supervised-development`，或要求采用 **Codex 规划/监督 → AGY 实现 → Codex Review/验收** 的定制开发流程时，按本流程工作。

v3.1 的核心变化不是再次替换 Harness，而是把 Skill 从“怎么控制某个 Worker Runtime”升级为“怎么稳定完成一次软件开发”。

> **Codex shapes and proves. AGY builds. Git tells the truth.**
>
> **Codex 想清楚、拆清楚、验清楚；AGY 负责实现；Git 负责作证。**

## 3.1 Alpha 1 范围

当前 alpha 先正式落地前半段 Workflow Kernel：

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
```

后半段继续复用已经成熟的：

```text
Implementation
→ Review / Rework
→ Completeness / Blast Radius
→ Independent Verification
→ Knowledge Closeout
```

后续 alpha 再把 AGY execution adapter 和三轴 Review 独立收敛。**不要把当前分支里的旧 Pi runtime 文档误认为 3.1 最终主链路。**

---

# 角色固定

- **User = Product / One-way Decision Authority**：决定真正需要产品、架构、风险取舍的问题；不负责替 Agent 查 repository 中能自己查到的事实。
- **Codex App = Master Supervisor / Shaper / Spec Owner / Reviewer / QA / Final Acceptance**：理解目标、查事实、推进决策、建立 Spec、切 Execution Units、建立 Git baseline、Review、Completeness、独立 Verification、Knowledge Closeout，并且是唯一可以判定 `ACCEPTED` 的角色。
- **AGY CLI = Target Primary Implementer / Writer**：目标主链使用官方 AGY CLI 执行已经被 Shape/Spec/Slice 清楚的工作。Runtime 适配细节在 3.1 后续阶段收敛；实现者不得重新定义产品语义。
- **Pi = Optional Specialist**：若未来某个 Pi capability 对 research / second opinion / blast-radius analysis 有明显价值，可以旁路使用；不要求所有任务经过 Pi。
- **tty7 = Optional Interactive Runtime**：只属于 Worker 交互/运行方式，不决定 Workflow 语义。
- **Git Repository = Source of Truth**：Worker 总结、模型自述、测试自述都不能代替当前 repository evidence。

---

# Active Workflow Resources

前半段 Workflow Kernel：

- `resources/task-sizing.md`：Small / Medium / Large 路由；
- `resources/shaping.md`：Decision Tree、Frontier、Resolved/Open/Fog/Out-of-Scope；
- `resources/spec-contract.md`：稳定 Spec、Acceptance、Verification Seams；
- `resources/execution-slicing.md`：Vertical Slice / Tracer Bullet、Expand→Migrate→Contract。

当前继续复用的后半段能力：

- `resources/completeness-regression.md`：Completeness、Blast Radius、Test Layers、RED→GREEN；
- `resources/review-gates.md`：现有 Review Gates（后续 alpha 将升级为三轴 Review）；
- `resources/closeout-governance.md`：Knowledge Closeout；
- `resources/run-lifecycle.md`：现有生命周期规则中仍适用的 Review/Rework/Verify/Closeout 语义。

3.0/3.0.1 runtime 相关文件属于迁移历史或临时参考，不应驱动新的 Workflow 设计。

---

# 不可违反的边界

1. **只有 Codex 可以 `ACCEPTED`。** Primary Worker 完成一轮实现，不等于 Review PASS。
2. **Workflow 与 Runtime 解耦。** Shape / Spec / Slice / Review 规则不能因为以后使用 AGY headless、tty7 或其他执行入口而改变。
3. **Primary Worker 不重新做产品决策。** 未解决的关键需求/架构语义必须回到 Shaping，不允许靠 Worker 猜。
4. **Facts ≠ Decisions。** repository / docs / call graph 能查到的事实由 Codex 查；真正的产品/架构取舍才问用户。
5. **当前 checkout + baseline protection 是默认单 Writer 拓扑。** 不机械切 worktree，不回滚用户已有改动。
6. **不 push / merge / release / deploy / production write / irreversible delete**，除非用户明确授权。
7. **Completeness 不是 Scope Expansion。** unfinished 必须补齐；different ticket 留在 Out of Scope。
8. **One-way door 不由 Worker 自行决定。** destructive migration、breaking public API、auth relaxation、billing/money、credential semantics、production mutation、irreversible deletion 等需要显式授权。
9. **每个开发任务必须明确验证边界。** 不只判断 Unit / Integration / E2E，还要记录主要 Verification Seam。
10. **可安全、确定性复现的 bug 默认要求 RED → root-cause fix → GREEN → Codex independent re-run。**
11. **`CODE_VERIFIED != ACCEPTED`。** 代码稳定后仍需 Knowledge Impact Scan / Closeout Review。
12. **不要为了形式把简单任务复杂化。** Small task 允许 compact path。
13. **不要为了速度把复杂任务伪装成 Small。** 出现新的决策/传播面/one-way door 时必须升级流程。

---

# 0. INTAKE：先理解目标，不立即写施工计划

先读取当前上下文和 repository 中已有规则：

```text
AGENTS.md
CLAUDE.md
README / architecture docs
CONTEXT / ADR（若存在）
API / Schema / Contract
CI / lint / test / build / e2e 约定
```

如果任务需要实际开发，建立 Git baseline：

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

保存：

```text
repo_root
branch
base_head
baseline_changed_paths
baseline_diff_or_fingerprint
```

规则：

```text
current changes - baseline changes = task-introduced changes
```

不得为了“干净工作区”回滚用户已有修改。

---

# 1. SIZED：Small / Medium / Large

先执行 `resources/task-sizing.md`。

输出：

```text
Task Size: Small | Medium | Large
Why:
- uncertainty
- blast radius
- one-way doors
- worker context size

Required Path:
- shaping: yes/no
- spec: compact/full
- slicing: yes/no
- decision map: yes/no
```

## Small

适合：目标明确、局部、无关键 open decisions、一个 Worker context 可稳定完成。

```text
INTAKE
→ SIZED(Small)
→ COMPACT SPEC
→ IMPLEMENT
→ REVIEW
→ VERIFY
→ CLOSEOUT
```

## Medium

正常 Feature 默认走：

```text
INTAKE
→ SIZED(Medium)
→ SHAPING
→ SPEC_READY
→ SLICED
→ IMPLEMENT / REVIEW slice-by-slice
→ GLOBAL VERIFY
→ CLOSEOUT
```

## Large

只有复杂度确实需要时：

```text
INTAKE
→ SIZED(Large)
→ DESTINATION
→ DECISION MAP / FOG
→ resolve frontier
→ SPEC_READY
→ SLICED
→ staged IMPLEMENT / REVIEW
→ GLOBAL VERIFY
→ CLOSEOUT
```

Sizing 允许根据新证据升级/降级；不要锁死最初判断。

---

# 2. SHAPING：先解决决定，再写 Spec

Medium/Large 使用 `resources/shaping.md`。

维护：

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

## Frontier 规则

只讨论当前前置条件已解决的问题。

```text
Can Codex look it up?
→ Codex investigates.

Requires product/architecture preference?
→ User decides.

Depends on an unresolved decision?
→ Keep it for a later frontier.
```

## Fog / Not Yet Specified

知道以后可能有问题，但现在还不能准确提出问题时，不要提前造 ticket。

```text
unclear future area
→ Not Yet Specified
→ earlier decision resolves
→ precise question emerges
→ Open Decision / Slice
```

## Shaping Exit

只有关键行为已经足够明确、Worker 不需要自行发明产品/架构语义时，才进入：

```text
SPEC_READY candidate
```

---

# 3. SPEC：把已经决定的内容固化

使用 `resources/spec-contract.md`。

Medium/Large Spec 默认包含：

```text
Problem
Expected Behavior
Scenarios / Stories
Implementation Decisions
Acceptance Criteria
Verification Seams
Test Strategy
Out of Scope
Constraints / One-way Decisions
```

## Verification Seam

除了：

```text
Unit
Integration
E2E
```

还必须回答：

> **从哪个稳定公共边界观察正确行为？**

例如：

```text
Primary Seam: POST /orders
Integration: required
E2E: required for browser checkout
```

优先：

```text
Existing seam > invented seam
Higher stable seam > internal seam
Fewer meaningful seams > implementation-coupled tests everywhere
```

## Spec 不写成施工清单

默认避免把以下内容作为 Spec 权威：

```text
具体文件路径
具体行号
完整实现代码
逐文件 TODO
```

Spec 固化行为和决定；短期施工细节放 Execution Unit。

## SPEC_READY Gate

```text
Critical decisions resolved
Expected behavior testable
Acceptance criteria observable
Primary verification seam chosen
Test layers recorded
Out of Scope explicit
No hidden product/architecture decision delegated to Worker
```

写 Spec 时发现关键 undecided behavior → 回 `SHAPING`。

---

# 4. SLICED：把 Spec 变成 Worker 能稳定完成的小步

Medium/Large 使用 `resources/execution-slicing.md`。

## 默认：Vertical Slice / Tracer Bullet

每个 slice 是窄但完整的行为路径：

```text
input / user action
→ business behavior
→ persistence / integration
→ observable output
→ verification
```

不要默认水平切：

```text
all DB
→ all API
→ all UI
→ tests at the end
```

每个 slice 应：

```text
Narrow
Complete
Reviewable
Verifiable when practical
Fit one fresh Worker context
```

## Execution Unit

每个 slice 生成短期施工单：

```text
Slice Goal
Spec Source
Scope
Context
Acceptance
Verification Seam
Completeness Focus
Constraints
Report
```

Spec 是稳定需求/决定权威；Execution Unit 是当前 Worker 的施工单。

## Wide Refactor 例外

共享字段/type/signature 等大 blast-radius 机械迁移，不强行 vertical slice：

```text
EXPAND
→ MIGRATE A
→ MIGRATE B
→ MIGRATE ...
→ CONTRACT
```

Contract 删除旧 form 前必须有 zero-consumer evidence。

## SLICED Gate

```text
Every required behavior covered
Slices are vertical unless justified
Each slice has observable acceptance
Dependencies explicit
Each slice fits one Worker context
Wide refactors use expand/migrate/contract
Out-of-scope work not hidden inside slices
```

Small task 可以只有一个 implicit Execution Unit。

---

# 5. IMPLEMENT：Worker 只实现当前 Execution Unit

当前 alpha 的重点不是 Runtime adapter；这里先固定 Workflow 语义：

```text
Codex owns Spec + Execution Unit
→ Primary Worker implements exactly this unit
→ repository changes
→ Codex reviews repository truth
```

目标 Primary Worker 是官方 AGY CLI。后续 alpha 会把 AGY headless / tty7 fallback 统一成薄 Execution Adapter；**不要因为运行入口不同而重新定义 Spec/Slice。**

Worker 的报告至少应包含：

```text
changed paths
commands/tests run
known unresolved findings
any discovered scope/completeness concern
```

Worker 发现关键 undecided behavior：停止扩大实现，返回 evidence，让 Codex 回到 SHAPING / SPEC。

Worker 发现新传播 path：先报告；Codex 判断它是 unfinished remainder 还是 different ticket。

---

# 6. Slice Review / Rework

每个 slice 完成后，Codex 不直接进入下一个 slice。

至少检查：

```text
Spec fidelity for this slice
scope drift
architecture/correctness obvious issues
local completeness / blast radius
targeted verification
baseline integrity
```

需要返工时生成 evidence-driven Rework Contract：

```text
Issue
Evidence
Expected
Required change
Re-run
```

默认 3 个完整 `Review → Rework → Re-review` 为 soft limit；达到后重新判断：

- Spec 是否有歧义；
- slice 是否过大/过横向；
- root cause 是否错；
- Worker runtime/model 是否不适合；
- 是否应回到 SHAPING / SPEC / SLICING。

不要无限返工一个错误的 Execution Unit。

---

# 7. Global Completeness / Blast Radius

所有 slices 局部 PASS 后，仍需全局检查 `resources/completeness-regression.md`。

固定追踪：

```text
Changed behavior
→ direct callers
→ indirect callers / re-exports / scripts
→ types / enums / validation / serialization
→ schema / migration / existing data
→ sibling flows / jobs
→ error / retry / fallback
→ cache / derived state
→ dead / orphaned old path
→ tests
→ knowledge impact
```

Remainder：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

unfinished → Rework；different ticket → 保持 Out of Scope。

---

# 8. Test Strategy / Regression Proof

每个任务显式记录：

```text
Primary Verification Seam
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

可安全、确定性复现的 bug：

```text
repro / regression test
→ unfixed RED
→ root-cause fix
→ same test GREEN
→ Codex independent re-run
```

复杂 bug 后续 alpha 会增加专门 diagnosis branch；当前继续沿用现有 RED→GREEN / Completeness 规则。

---

# 9. Codex Independent Verification

只有相关 slice Review + Global Completeness PASS 后，Codex 独立执行适用检查：

```text
lint / format-check
typecheck
unit
integration
e2e（required 时）
build/package
schema/contract checks
```

Worker 自报 green 不能替代这一阶段。

全部相关门禁通过：

```text
CODE_VERIFIED
```

---

# 10. Knowledge Closeout

`CODE_VERIFIED` 后执行 `resources/closeout-governance.md`。

扫描：

```text
README / usage
AGENTS / CLAUDE / project rules
API / schema / CLI / shared Contract
env / config / service / deploy / jobs
workspace residue
```

相关知识面标：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

不要求每个任务都制造 Markdown diff。

Closeout 发现真实实现遗漏 → 退回代码 Review / Completeness / Verification，不用文档掩盖代码问题。

---

# 11. Acceptance

只有 Codex 可以：

```text
CLOSEOUT_REVIEW → ACCEPTED
```

至少满足：

```text
Task was sized appropriately
Required shaping completed
Spec fidelity PASS
All required slices complete
No unexplained scope drift
Completeness / Blast Radius PASS
Test strategy + Verification Seam satisfied
Regression proof satisfied / justified N/A
Codex independent verification PASS
Knowledge Closeout PASS
Baseline/user changes preserved
No unauthorized one-way/external side effects
Final diff explainable
```

---

# 3.1 Workflow State

目标状态机：

```text
INTAKE
→ SIZED
→ SHAPING          # Medium/Large; Small may shortcut
→ SPEC_READY
→ SLICED           # Small may have one implicit slice
→ IMPLEMENTING
→ REVIEWING
→ COMPLETENESS_REVIEW
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

可能回退：

```text
IMPLEMENTING / REVIEWING
→ SHAPING          # hidden decision discovered
→ SPEC_READY       # spec changed
→ SLICED           # execution units need re-cut
```

异常：

```text
BLOCKED
REWORK_REQUIRED
CANCELLED
FAILED
```

核心语义：

```text
Worker done != Review PASS
Slice PASS != Feature PASS
Tests green != Completeness PASS
CODE_VERIFIED != ACCEPTED
```

---

# 当前版本演进

```text
v2.1.x
Codex Supervisor → tty7 → AGY CLI
重点：可靠控制外部 Worker + Review/Closeout

v3.0 / 3.0.1
探索 Pi Native Harness / Provider 分离
重点：Runtime simplification

v3.1
Workflow First
重点：Size → Shape → Spec → Slice → Build → Prove
Runtime 变成可替换执行细节
```

3.1 的长期目标不是再造一个 Agent 平台，而是形成一套稳定的个人软件开发方法：

> **先把问题想清楚，再把任务切小；让 Worker 专心实现，让 Codex 专心证明。**
