# Three-Axis Repository Review — v3.1 Alpha 3

本文件定义 Codex 对 **AGY Primary Worker 产出的真实 repository state** 做独立 Review 的正式模型。

核心问题被拆成三个互不替代的轴：

```text
A. Spec Fidelity        — 做对了吗？
B. Engineering Quality  — 写得好吗？
C. Completeness         — 漏了吗？
```

> **三个轴独立判断，最后才汇总。一个轴的优秀不能抵消另一个轴的失败。**

AGY stream-json、conversation metadata、Worker summary 只用于诊断；交付事实来自 Git、代码、Spec、搜索证据和 Codex Independent Verification。

---

# 0. Review Prerequisites

AGY 一轮返回后，Codex 固定重新读取：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

同时固定当前 Review 的比较边界：

```text
approved Spec
current Execution Unit
base_head / baseline
current task-introduced diff
```

如果 baseline、cwd、conversation 或 diff 身份不可信，先处理 Cross-cutting Gates，不要带着错误输入做三轴 Review。

---

# Axis A — Spec Fidelity：做对了吗？

Spec Fidelity 不评价代码“漂亮不漂亮”，只回答：

> **当前实现是否忠实实现已经冻结的 Spec / Execution Unit？**

## A1. Acceptance Coverage

逐条建立覆盖关系：

```text
Acceptance Criterion
→ observable implementation
→ contract/schema/data behavior
→ agreed Verification Seam
→ relevant test/evidence
```

每项只能：

```text
PASS
REWORK
BLOCKED
```

不能用 AGY 的“已完成”或测试数量代替需求覆盖证据。

## A2. Missing / Partial Requirement

检查：

- requirement 完全遗漏；
- happy path 有了但关键规定行为缺失；
- UI/API/data 只实现一半；
- migration/compatibility 被 Spec 要求但未实现；
- Verification Seam 没有实际可达实现。

## A3. Wrong Semantics

代码“有这个功能”但语义错误，同样 REWORK。

例如：

```text
Spec: duplicate request must be idempotent
Code: catches duplicate error and returns 500
```

不是 Requirement Coverage PASS。

## A4. Scope Creep / Speculative Feature

检查 AGY 是否实现了 Spec 没要求的：

- 新产品行为；
- 新 public API；
- 无依据配置项；
- speculative abstraction；
- unrelated refactor；
- 新 dependency / infrastructure；
- “顺便优化”。

如果它是完成当前需求必然需要的 propagation，交给 Axis C 判断；如果不是，属于 scope drift。

## A5. Unauthorized Decision

AGY 不得通过实现偷偷决定：

```text
产品语义
breaking contract
one-way migration
auth/tenancy relaxation
money/billing behavior
credential semantics
production mutation
irreversible delete
```

未授权 → `BLOCKED` 或 REWORK 回 Shaping，而不是让 Worker 的实现事实替代决定。

## A6. Verification Seam Fidelity

Spec 定义了公共观察边界时，Review 要确认实现和测试能从该 seam 证明真实行为。

例如：

```text
Primary Seam = POST /orders
```

只测试 private helper 不能让 Axis A 自动 PASS。

### Axis A Verdict

```text
全部冻结行为得到证据且无 scope creep → PASS
存在遗漏/部分/错误语义/越界       → REWORK
需要未授权产品/one-way decision    → BLOCKED
```

---

# Axis B — Engineering Quality：写得好吗？

Axis B 假设“要做什么”已经由 Spec 冻结，回答：

> **实现这个正确目标的方式是否健康、可维护、符合项目边界？**

不要把 formatter/linter/compiler 已经能稳定发现的问题重复当成主要 LLM Review 工作；除非这些错误暴露更深的设计缺陷。

## B1. Architecture / Module Responsibility

检查：

- 是否遵守现有分层/模块边界；
- 是否绕开已有 abstraction；
- responsibility 是否放在正确模块；
- 是否制造不必要 middle-man / coupling；
- 是否出现无真实需求支撑的 generalized framework。

## B2. Contract & Data Consistency

检查：

- API/request/response 与 caller/consumer 一致；
- DTO/model/entity/schema 边界；
- serialization/validation；
- persistence/migration；
- existing-data semantics；
- backward compatibility。

注意：漏掉 consumer 属于 Axis C；当前已改 contract 的设计本身不健康属于 Axis B。

## B3. Correctness / Edge Cases

按相关性检查：

```text
null / empty / missing
boundary values
error path
transaction
concurrency / race
retry / idempotency
timezone / locale
pagination / ordering
authorization
partial failure
backward compatibility
```

## B4. Error Handling / Observability

检查：

- exception 是否被吞；
- 错误是否被错误转换成成功/空结果；
- status/error code 是否合理；
- log 是否泄漏 secret；
- retry 是否放大永久错误；
- 定位问题所需上下文是否存在；
- debug instrumentation 是否残留。

## B5. Security / Side-effect Quality

Runtime permission allow 不等于实现安全。

检查：

- authz boundary；
- tenant/data isolation；
- unsafe command/path handling；
- sensitive data；
- unintended external side effects；
- destructive behavior 是否有合理 guard。

## B6. Code Smell Baseline

将以下作为**启发式**，不是机械 hard violation；项目明确规范优先：

```text
Mysterious Name
Duplicated Code
Feature Envy
Data Clumps
Primitive Obsession
Repeated Switches
Shotgun Surgery
Divergent Change
Speculative Generality
Message Chains
Middle Man
Refused Bequest
```

每个 smell finding 必须说明真实维护/理解风险，不能为了“显得 Review 很深”硬挑风格。

## B7. Test Quality

测试是否：

- 从 agreed/public seam 观察行为；
- 不过度 mock 内部 collaborator；
- 不验证 private implementation；
- expected value 有独立来源；
- 能对关键错误语义敏感；
- 没有通过删/skip assertion 换 GREEN；
- test layer 与真实边界匹配。

一个测试很多但 implementation-coupled 的实现，Axis B 仍可 REWORK。

### Axis B Verdict

```text
实现质量足以安全进入 verification → PASS
存在实质工程缺陷                → REWORK
需要外部环境/风险决策才能裁决     → BLOCKED
```

---

# Axis C — Completeness：漏了吗？

Axis A/B 主要检查当前 diff；Axis C 强制做 **Missing Diff Review**：

> **还有没有本来应该因为当前 change 一起改变，却没有进入 diff 的地方？**

详细规则见 `resources/completeness-regression.md`。

## C1. Changed Surface

对每一个有语义变化的：

```text
symbol
route
schema
state
contract
behavior
```

建立传播检查。

## C2. Propagation Sweep

固定按相关性检查：

```text
Changed behavior
→ direct callers
→ indirect callers / re-exports / scripts
→ DTO / types / enums / validation / serialization
→ schema / migration / existing data
→ producer / consumer
→ sibling flows / jobs
→ reachable error / empty / permission / retry / fallback
→ cache / derived state / stale IDs
→ old/orphaned path
→ tests
→ knowledge impact handoff
```

使用 repository evidence，例如：

```bash
rg "<changed-symbol>" .
rg "<old-route|old-field|old-enum|old-config>" .
```

## C3. Unfinished vs Different Ticket

判断标准：

> 不做这一项，当前 change 会被 Reviewer 称为 unfinished 吗？

是：当前任务必须处理。

否：保持 `out-of-scope-different-ticket`。

## C4. Remainder Disposition

所有发现的 remainder 只能归类：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

不允许模糊的：

```text
later
follow-up maybe
probably fine
```

## C5. Wide Refactor Completeness

Expand → Migrate → Contract 时尤其检查：

```text
old form 是否仍有 active caller
所有 migration batch 是否完成
compat bridge 是否仍被需要
contract removal 是否安全
```

### Axis C Verdict

```text
没有 unfinished remainder             → PASS
存在当前任务必须补齐的 missing diff     → REWORK
完成需要未授权 one-way decision         → BLOCKED
```

---

# Three-Axis Aggregation

使用 `templates/review-report.md`。

```text
Spec Fidelity:       PASS | REWORK | BLOCKED
Engineering Quality: PASS | REWORK | BLOCKED
Completeness:        PASS | REWORK | BLOCKED
```

汇总规则：

```text
all PASS       → REVIEW PASS → VERIFYING
any REWORK     → REWORK_REQUIRED
any BLOCKED    → BLOCKED（除非 blocker 独立且可安全先修其他 findings）
```

**不做平均分，不做多数投票。**

### Context Isolation

如果环境支持独立 reviewer/subtask：

```text
Spec Reviewer         → 只做 Axis A
Quality Reviewer      → 只做 Axis B
Completeness Reviewer → 只做 Axis C
Master Codex          → 汇总
```

如果不支持，也要按 A/B/C 分别形成 verdict 后再汇总。

---

# Evidence-Driven Rework

每个 finding 使用稳定 ID：

```text
S1, S2 ... = Spec Fidelity
Q1, Q2 ... = Engineering Quality
C1, C2 ... = Completeness
```

Rework Contract 必须引用：

```text
Finding ID
Axis
Issue
Evidence
Expected
Required Change
Re-run
```

可以合并同根因、同范围 findings；不要把无关问题塞成一个模糊返工包。

AGY Rework `SUCCESS` 后仍回 Three-Axis Review，不直接 Verify。

---

# Cross-cutting Gate 0 — Baseline Integrity

确认：

- branch / HEAD 已记录；
- baseline-owned changes 已识别；
- task-introduced changes 可区分；
- 没有为清理 Worker 结果回滚用户已有修改。

```text
current changes - baseline changes = task-introduced changes
```

失败时先修复 review input；不允许 `git reset --hard` 粗暴解决。

---

# Cross-cutting Gate 8 — AGY Run / Conversation Integrity

确认：

- conversation_id 来自真实 AGY output；
- `init.cwd == repo_root`；
- rework 使用当前任务真实 `--conversation <id>`；
- `-c` 不用于猜未知最近 conversation；
- stream 截断时没有无脑 replay 副作用任务；
- `result.status=SUCCESS` 只表示 turn 返回；
- Worker summary 与 Git 冲突时以 Git 为准。

```text
AGY SUCCESS != REVIEW PASS
```

---

# Cross-cutting Gate 9 — Codex Independent Verification

**只有 Three-Axis Review 全 PASS 后进入。**

Codex 自己按 Spec Verification Seam / Test Strategy 执行相关：

```text
lint / format-check
typecheck
unit
integration
e2e
build/package
contract/schema check
original bug repro / performance measurement when applicable
```

区分：

```text
actually-run-and-pass
blocked/not-run
failed
```

AGY 自述测试通过不能代替本 Gate。

Verification 失败：

```text
VERIFYING → REWORK_REQUIRED
```

它不会 retroactively 把 Three-Axis Review 写成 PASS 的错误；失败证据进入新的 finding/rework，再完整 Re-review。

---

# Cross-cutting Gate 10 — Diff Hygiene

最终检查：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

确认没有：

- debug code；
- temp/build/profiling artifacts；
- 意外 lockfile；
- unrelated rename/format；
- sensitive information；
- 超范围 docs/config。

---

# Cross-cutting Gate 11 — External Side Effects / One-way Door

未经明确授权不得：

```text
push
merge
release
deploy
production write
remote/cloud delete
irreversible data mutation
```

以下语义同样需要用户决定：

```text
destructive migration
breaking public API
auth/tenancy relaxation
money/billing
credential behavior
irreversible deletion
```

Runtime permission allow 不等于用户授权。

---

# Cross-cutting Gate 12 — AGY Runtime / Permission / Credential Hygiene

确认：

- 官方 AGY CLI 是 Primary Worker 主链；
- headless capability 来自当前 `agy --help`；
- 默认不使用 `--dangerously-skip-permissions`；
- Ask soft-deny 被如实记录；
- exit 0 不被解释成所有 tool 成功；
- tty7 只用于真实交互 fallback；
- Pi 若使用只作为 optional specialist；
- credential/token 不进入 Contract/repo/final evidence。

---

# Cross-cutting Gate 13 — Knowledge Alignment

`CODE_VERIFIED` 后执行 Knowledge Closeout，而不是在三轴 Review 过程中为了“顺手”修改长期文档。

检查：

```text
README / usage
AGENTS / CLAUDE / project rules
API / schema / CLI / shared Contract
env / config / service / deploy / jobs
rename/retirement stale references
workspace residue
```

每个相关面：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

`CODE_VERIFIED != ACCEPTED`。

---

# Review Verdict Examples

## PASS

```text
THREE-AXIS REVIEW PASS
- Spec Fidelity: PASS
- Engineering Quality: PASS
- Completeness: PASS
- Cross-cutting review gates: PASS
- Next: Codex Independent Verification
```

## REWORK

```text
REWORK_REQUIRED
- Finding: C1
- Axis: Completeness
- Issue: export script still uses retired signature
- Evidence: <search/call-chain>
- Expected: all reachable callers migrated
- Required Change: migrate caller + appropriate regression coverage
- Re-run: <targeted commands/search>
```

## BLOCKED

```text
BLOCKED
- Finding: S2
- Axis: Spec Fidelity / authorization
- Blocker: completing behavior requires a breaking public contract not approved by user
- Evidence: <spec/code/consumer evidence>
- Safe state: <repository state>
- Decision needed: <explicit choice>
```

最终 `ACCEPTED` 必须经过 Three-Axis Review、Codex Independent Verification、Runtime/Permission Hygiene 和 Knowledge Closeout。