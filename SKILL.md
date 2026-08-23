---
name: agy-supervised-development
description: A workflow-first supervised development process where Codex shapes requirements, freezes a testable spec, slices work into verifiable execution units, delegates implementation to the official AGY CLI, then independently proves delivery through Three-Axis Review, verification, and knowledge closeout. Use Small/Medium/Large sizing, decision shaping, verification seams, vertical slices or expand-migrate-contract, AGY headless with tty7 fallback, Spec Fidelity / Engineering Quality / Completeness review, evidence-driven bug diagnosis, regression proof, and mandatory closeout.
version: 3.1.0-alpha.3
---

# AGY Supervised Development 3.1 — Workflow First (Alpha 3)

当用户明确使用 `$agy-supervised-development`，或要求采用 **Codex 规划/监督 → AGY 实现 → Codex Review/验收** 的开发流程时，按本流程工作。

> **Codex shapes and proves. AGY builds. Git tells the truth.**
>
> **Codex 想清楚、拆清楚、验清楚；AGY 负责实现；Git 负责作证。**

3.1 的中心不是 Harness，而是一条稳定的软件开发方法。

---

# Alpha 3 已落地的完整主链

```text
INTAKE
→ SIZE
→ SHAPE
→ SPEC
→ SLICE
→ BASELINE
→ WORKER READY
→ DIAGNOSE          # complex bug only
→ AGY BUILD
→ THREE-AXIS REVIEW
   ├─ A Spec Fidelity
   ├─ B Engineering Quality
   └─ C Completeness
→ CODEX INDEPENDENT VERIFY
→ CODE_VERIFIED
→ KNOWLEDGE CLOSEOUT
→ ACCEPTED
```

Runtime：

```text
Execution Unit
→ AGY official CLI headless / stream-json   # default
→ tty7 + AGY TUI                            # interactive fallback only
```

Optional：

```text
Codex → Pi specialist
        research / second opinion / blast-radius analysis
```

Pi 不进入默认 `Codex → Pi → AGY` 主链。

---

# 角色固定

- **User = Product / One-way Decision Authority**：决定真正的产品、架构、风险取舍；不负责替 Agent 查 repository 里能自己查到的事实。
- **Codex App = Master Supervisor / Shaper / Spec Owner / Reviewer / QA / Final Acceptance**：Size、Shape、Spec、Slice、Baseline、委派 AGY、Three-Axis Review、独立 Verification、Closeout，并且是唯一可以判定 `ACCEPTED` 的角色。
- **AGY official CLI = Primary Implementer / Writer**：执行已冻结、已切好的 Execution Unit；不得重新定义产品语义。
- **tty7 = Optional Interactive Runtime**：login、permissions、manual approval、TUI-only flow 等真正需要交互时使用。
- **Pi = Optional Specialist**：仅在 research / second opinion / blast-radius / specialized capability 明显有价值时旁路使用。
- **Git Repository = Source of Truth**：Worker summary、AGY `SUCCESS`、TUI `Done`、测试自述都不能代替 repository evidence。

---

# Active Resources

## Workflow Kernel

- `resources/task-sizing.md` — Small / Medium / Large；
- `resources/shaping.md` — Decision Tree、Frontier、Resolved/Open/Fog/Out-of-Scope；
- `resources/spec-contract.md` — Spec、Acceptance Criteria、Verification Seams；
- `resources/execution-slicing.md` — Vertical Slice / Tracer Bullet、Expand→Migrate→Contract。

## Execution Runtime

- `resources/agy-execution.md` — 官方 AGY CLI headless-first adapter；
- `resources/tty7-supervision.md` — interactive fallback；
- `resources/pi-interaction.md` — optional Pi specialist；
- `resources/run-lifecycle.md` — 3.1 governance lifecycle；
- `resources/failure-modes.md` — runtime/workflow failure modes。

## Review Intelligence

- `resources/review-gates.md` — Three-Axis Review + cross-cutting gates；
- `resources/completeness-regression.md` — Axis C / Regression / Test Proof；
- `resources/bugfix-workflow.md` — Simple vs Complex Bug Intelligence；
- `resources/closeout-governance.md` — Knowledge Closeout。

## Templates

- `templates/execution-unit.md`；
- `templates/review-report.md`；
- `templates/rework-contract.md`；
- `templates/closeout-contract.md`。

---

# 不可违反的边界

1. **只有 Codex 可以 `ACCEPTED`。**
2. **Workflow 与 Runtime 解耦。** Shape/Spec/Slice/Review 不因 AGY headless、tty7 或 optional Pi 改变。
3. **AGY 是 Primary Writer，不是 Product Owner。** 未解决产品/架构决策必须回 Shaping。
4. **Facts ≠ Decisions。** 能查的事实由 Codex 查；真实取舍才问用户。
5. **Repository state 是交付真相。** `result.status=SUCCESS != REVIEW PASS`。
6. **Three-Axis Review 不做平均分。** A/B/C 任一 REWORK，整体就是 REWORK。
7. **Review PASS != CODE_VERIFIED。** 必须 Codex Independent Verification。
8. **CODE_VERIFIED != ACCEPTED。** 必须 Knowledge Closeout。
9. **Completeness 不是 Scope Expansion。** unfinished 收完；different ticket 留在 Out of Scope。
10. **One-way Door 不由 Worker 自行决定。** destructive migration、breaking API、auth relaxation、billing/money、credential semantics、production mutation、irreversible delete 等必须显式授权。
11. **每个开发任务明确 Verification Seam + Unit/Integration/E2E applicability。**
12. **Simple deterministic bug 默认 RED → root-cause fix → GREEN → Codex re-run。**
13. **Complex bug 默认先建立 symptom-capable feedback loop，再形成 root cause 结论。**
14. **当前 checkout + baseline protection 是默认单 Writer 拓扑。** 不回滚用户已有改动。
15. **不 push / merge / release / deploy / production write / irreversible delete**，除非用户明确授权。
16. **AGY headless 默认不使用 `--dangerously-skip-permissions`。**
17. **Exit 0 不等于 Tool 真执行。** Headless permission soft-deny 必须识别。
18. **tty7 是 fallback，不是默认 screen-scraping runtime。**
19. **Small 不过度流程化，Large 不伪装成 Small。**

---

# 0. INTAKE — 先读事实

读取项目现役规则与真实状态：

```text
AGENTS.md / CLAUDE.md / README.md
相关 code / schema / API / tests
CI / build / e2e conventions
Git state
```

不要先写一个漂亮计划再去验证代码是不是那样。

---

# 1. SIZE — Small / Medium / Large

依据：

```text
需求清晰度
决策数量
模块/contract 数量
数据/状态传播
测试边界
风险/不可逆性
单个 Worker context 是否足够
```

### Small

```text
Compact Shape/Spec
→ one Execution Unit
→ AGY
→ Three-Axis Review
→ Verify
→ Closeout
```

### Medium

```text
Shape
→ Spec
→ 2~5 左右 verifiable slices（按实际复杂度）
→ AGY slice-by-slice
→ Review/Rework each slice
→ final Verify/Closeout
```

### Large

```text
Destination
→ Decision Map / Fog
→ resolve frontier decisions
→ Spec
→ staged slices / migration sequence
→ AGY sequential execution
```

Size 可随新证据向上升级。

---

# 2. SHAPE — 先把决定想清楚

维护：

```text
Goal / Destination
Resolved Decisions
Open Decisions
Not Yet Specified
Out of Scope
One-way Decisions
```

Frontier 规则：

```text
repository fact → Codex 自己查
external fact   → Codex research
product/architecture trade-off → 用户决定
blocked downstream question    → later frontier
```

进入 Spec 前：

```text
关键 Open Decisions 已解决
剩余 Fog 不阻塞当前 implementation
One-way decisions 已授权或明确 blocked
Out of Scope 明确
```

不要让 AGY 用代码替代未解决需求。

---

# 3. SPEC — 冻结稳定行为契约

至少包含：

```text
Problem
Expected Behavior
User/System Scenarios
Implementation Decisions
Acceptance Criteria
Verification Seams
Test Strategy
Out of Scope
One-way Decisions
```

默认不要把易过期的逐文件施工步骤写进 Spec；它们属于 Execution Unit。

### Verification Seam

先明确：

```text
Primary Seam
Secondary Seam = optional
Existing Prior Art
```

再判断：

```text
Unit
Integration
E2E
Regression Proof
```

---

# 4. SLICE — Worker 可完成的小步

先判断：

```text
normal behavior change → Vertical Slice / Tracer Bullet
wide mechanical change → Expand → Migrate → Contract
```

Vertical Slice 要尽量：

```text
Narrow
Complete
Independently reviewable
Independently verifiable
Fits one fresh Worker context
```

优先：

```text
input/user action
→ business behavior
→ persistence/integration
→ observable output
→ verification
```

避免默认水平拆成“所有 DB / 所有 API / 所有 UI / 最后 tests”。

每个步骤实例化 `templates/execution-unit.md`。

---

# 5. BASELINE — Writer 动手前保护工作区

Codex 记录：

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

---

# 6. WORKER READY — AGY Native Preflight

默认使用官方 AGY CLI。

```bash
command -v agy
agy --version
agy --help
```

至少确认当前安装所需：

```text
-p / --print
--output-format stream-json
--conversation
repo cwd
auth
permission behavior
```

headless 不适用时才走 tty7 interactive fallback；不静默改第三方 Provider。

---

# 7. BUG ROUTING — 只有 Bug 任务执行

先判断：

```text
simple-deterministic
or
complex-uncertain
```

### Simple

```text
REPRODUCE
→ RED
→ ROOT-CAUSE FIX
→ GREEN
```

### Complex

进入 `DIAGNOSING`：

```text
Tight Feedback Loop
→ Reproduce
→ Minimise
→ 3~5 Ranked/Falsifiable Hypotheses
→ Targeted Instrumentation
→ Root Cause Evidence
→ Regression Proof
→ Fix
→ Verify Original Repro
```

核心：**没有能抓住用户症状的反馈环，不把第一个代码猜测写成 root cause。**

详见 `resources/bugfix-workflow.md`。

---

# 8. IMPLEMENT — AGY Headless First

默认：

```bash
cd "$repo_root"
agy -p "<Execution Unit>" \
  --output-format stream-json \
  --print-timeout <appropriate-timeout>
```

保存真实：

```text
conversation_id
cwd
permission/tool evidence
result status
```

要求：

```text
init.cwd == repo_root
```

`SUCCESS` / exit 0 只意味着 AGY 本轮返回：

```text
IMPLEMENTING → REVIEWING
```

### Permission Soft-deny

同时检查：

```text
exit code
result.status/error
stderr
step_update.tool_info.error
Git state
```

被挡的测试只能写：

```text
blocked/not-run
```

默认禁止用 `--dangerously-skip-permissions` 解决普通阻塞。

---

# 9. THREE-AXIS REVIEW — Codex 独立验交付

AGY 返回后固定：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

然后使用 `templates/review-report.md` 独立形成三个 verdict。

## Axis A — Spec Fidelity：做对了吗？

检查：

```text
Acceptance coverage
missing / partial requirement
wrong semantics
scope creep
unauthorized decision
verification seam fidelity
```

Finding ID：`S1`, `S2` ...

## Axis B — Engineering Quality：写得好吗？

检查相关：

```text
architecture/module responsibility
contract/data consistency
correctness/edge cases
error handling/observability
security/side effects
backward compatibility
code smells / speculative generality
test quality / implementation coupling
```

不要浪费 LLM Review 重复 formatter/linter/compiler 已能稳定发现的普通问题。

Finding ID：`Q1`, `Q2` ...

## Axis C — Completeness：漏了吗？

做 Missing Diff Review：

```text
changed behavior
→ callers / consumers
→ types / validation / serialization
→ schema / migration / existing data
→ sibling flows / jobs
→ error / retry / fallback
→ cache / derived state
→ old/orphaned path
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

Finding ID：`C1`, `C2` ...

## Aggregate

```text
A PASS + B PASS + C PASS → REVIEW PASS
any REWORK               → REWORK_REQUIRED
any unresolved BLOCKED   → BLOCKED
```

**不平均、不多数投票。**

若支持独立 reviewer，可隔离三个轴上下文；不支持时也必须分别形成结论后再汇总。

---

# 10. REWORK — Finding-driven Resume

使用 `templates/rework-contract.md`。

必须引用：

```text
Finding ID
Axis / Source
Issue
Evidence
Expected
Required Change
Re-run
Scope Reminder
Forbidden Actions
```

优先 resume 同一真实 conversation：

```bash
agy -p "<Rework Contract>" \
  --conversation "$agy_conversation_id" \
  --output-format stream-json
```

不要只发“继续”“修一下刚才的问题”。

Rework 后重新完整 Three-Axis Review；修 Q1 也要确认没有破坏 A/C。

默认 3 个完整 `Review → Rework → Re-review` 周期为 soft limit。

---

# 11. CODEX INDEPENDENT VERIFY

**只有 Three-Axis Review 全 PASS 才进入。**

Codex 基于 Verification Seam / Test Strategy 独立执行相关：

```text
lint / format-check
typecheck
unit
integration
e2e
build/package
schema/contract checks
original bug repro / performance measurement when applicable
```

Worker 自己跑过不能替代。

Verification 失败形成 `V*` finding：

```text
VERIFYING
→ REWORK_REQUIRED
→ AGY
→ THREE-AXIS REVIEW AGAIN
→ VERIFY AGAIN
```

不能“修到测试绿”后绕过重新 Review。

全部通过：

```text
CODE_VERIFIED
```

---

# 12. CODE_VERIFIED — 不是最终完成

进入前至少能说明：

```text
Spec Fidelity = PASS
Engineering Quality = PASS
Completeness = PASS
Blast Radius evidence
Verification Seam exercised
Test Strategy satisfied
Regression Proof satisfied/N/A
Codex Independent Verification = PASS
```

然后必须 Knowledge Impact Scan。

---

# 13. KNOWLEDGE CLOSEOUT

检查：

```text
README / usage
AGENTS / CLAUDE / project rules
API / schema / CLI / shared Contract
env / config / service / deploy / jobs
stale renamed/retired references
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

无需修改时允许零文档 diff。

需要修改时发送 `templates/closeout-contract.md`；优先继续同一 AGY conversation，但 final verified repository state 才是 Source of Truth。

Closeout 发现代码缺陷形成 `K*` finding，退回 Rework → Three-Axis Review → Verification，而不是用文档掩盖。

---

# 14. ACCEPTANCE

只有满足：

```text
Three-Axis Review PASS
Independent Verification PASS
Knowledge Closeout PASS
Baseline preserved
No unauthorized one-way/external side effect
Final diff explainable
```

Codex 才能：

```text
ACCEPTED
```

---

# 15. Runtime Recovery

### 已知真实 AGY conversation

```bash
agy -p "..." --conversation <id> --output-format stream-json
```

### Conversation 丢失

不猜 `-c` 最近会话。建立 replacement conversation，并输入：

```text
approved Spec
current Execution Unit
repo/branch/baseline
current diff
Three-Axis findings
verification state
bug diagnosis evidence when applicable
```

Repository progress 不作废。

### tty7

只在 login / permissions / manual approval / TUI-only flow / headless temporary incompatibility 时使用。退出后仍回 Codex Three-Axis Review。

---

# 16. Final Report

最终至少说明：

```text
Task Size
Spec / Execution Units
AGY execution status
Three-Axis Review:
  Spec Fidelity
  Engineering Quality
  Completeness
Findings/Rework cycles
Verification Seam
Independent Verification
Bug proof when applicable
Knowledge Closeout
Blocked/out-of-scope items
Final repository state
```

不要把 Worker 自述包装成证据，也不要因为“模型说完成了”跳过任何 Acceptance 边界。