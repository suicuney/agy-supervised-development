---
name: agy-supervised-development
description: A workflow-first supervised development process where Codex shapes requirements, freezes a testable spec, slices work into verifiable execution units, delegates implementation to the official AGY CLI, then independently reviews, verifies, and closes out the repository. Use Small/Medium/Large task sizing, decision shaping, verification seams, vertical slices or expand-migrate-contract, AGY headless stream-json with tty7 interactive fallback, baseline protection, completeness/blast-radius review, regression proof, and mandatory knowledge closeout.
version: 3.1.0-alpha.2
---

# AGY Supervised Development 3.1 — Workflow First (Alpha 2)

当用户明确使用 `$agy-supervised-development`，或要求采用 **Codex 规划/监督 → AGY 实现 → Codex Review/验收** 的开发流程时，按本流程工作。

3.1 的核心不是再造 Harness，而是建立一个稳定的软件开发方法：

> **Codex shapes and proves. AGY builds. Git tells the truth.**
>
> **Codex 想清楚、拆清楚、验清楚；AGY 负责实现；Git 负责作证。**

Alpha 2 已完成：

```text
Workflow Kernel
SIZE → SHAPE → SPEC → SLICE

Execution Adapter
Execution Unit → AGY official CLI headless → Repository
                         └→ tty7 interactive fallback
```

当前后半段继续复用成熟的 Review / Completeness / Verification / Closeout；后续 Alpha 3 再把 Review 正式收敛成三轴模型。

---

# 角色固定

- **User = Product / One-way Decision Authority**：决定真正需要产品、架构、风险取舍的问题；不负责替 Agent 查 repository 中能查到的事实。
- **Codex App = Master Supervisor / Shaper / Spec Owner / Reviewer / QA / Final Acceptance**：Size、Shape、Spec、Slice、建立 baseline、委派 AGY、Review、Completeness、独立 Verification、Closeout，并且是唯一可以判定 `ACCEPTED` 的角色。
- **AGY official CLI = Primary Implementer / Writer**：执行已经被冻结并切好的 Execution Unit；不得重新定义产品语义。
- **tty7 = Optional Interactive Runtime**：仅在 login、permissions、人工审批、TUI-only flow 等需要交互时使用。
- **Pi = Optional Specialist**：research / second opinion / blast-radius analysis 等旁路能力；不要求所有任务经过 Pi，也不放在 AGY 前面做永久父 Agent。
- **Git Repository = Source of Truth**：Worker 总结、AGY `SUCCESS`、TUI `Done`、测试自述都不能代替 repository evidence。

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
- `resources/pi-interaction.md` — optional Pi specialist，不是主 Runtime；
- `resources/run-lifecycle.md` — 3.1 governance lifecycle；
- `resources/failure-modes.md` — AGY/runtime/workflow failure modes。

## Delivery Governance

- `resources/completeness-regression.md` — Completeness、Blast Radius、Test Layers、RED→GREEN；
- `resources/review-gates.md` — 当前 Review Gates（Alpha 3 将升级三轴）；
- `resources/closeout-governance.md` — Knowledge Closeout。

## Templates

- `templates/execution-unit.md`；
- `templates/rework-contract.md`；
- `templates/closeout-contract.md`。

---

# 不可违反的边界

1. **只有 Codex 可以 `ACCEPTED`。**
2. **Workflow 与 Runtime 解耦。** Shape/Spec/Slice/Review 不因 AGY headless、tty7 或 optional Pi 改变。
3. **AGY 是 Primary Writer，不是 Product Owner。** 未解决的产品/架构决策必须回 Shaping。
4. **Facts ≠ Decisions。** 能查的事实由 Codex 查；真实取舍才问用户。
5. **Repository state 是交付真相。** `result.status=SUCCESS != PASS`。
6. **当前 checkout + baseline protection 是默认单 Writer 拓扑。** 不回滚用户已有改动。
7. **不 push / merge / release / deploy / production write / irreversible delete**，除非用户明确授权。
8. **One-way Door 不由 Worker 自行决定。** destructive migration、breaking API、auth relaxation、billing/money、credential semantics、production mutation、irreversible delete 等必须显式授权。
9. **Completeness 不是 Scope Expansion。** unfinished 收完；different ticket 留在 Out of Scope。
10. **每个开发任务明确 Verification Seam + Unit/Integration/E2E applicability。**
11. **可安全确定性复现的 bug 默认 RED → root-cause fix → GREEN → Codex re-run。**
12. **AGY headless 默认不使用 `--dangerously-skip-permissions`。**
13. **Exit 0 不等于命令真的执行。** Headless permission soft-deny 必须被识别。
14. **tty7 是 fallback，不是默认 screen-scraping runtime。**
15. **Pi 是 optional specialist，不是 `Codex → Pi → AGY` 固定中间层。**
16. **`CODE_VERIFIED != ACCEPTED`。** 必须做 Knowledge Closeout。
17. **Small 不过度流程化，Large 不伪装成 Small。**

---

# 0. INTAKE：理解目标并建立初始事实

读取：

```text
AGENTS.md / CLAUDE.md / README.md
相关 code / schema / API / tests
CI / build / e2e 约定
当前 Git state
```

不要先写计划再查代码。

---

# 1. SIZE：Small / Medium / Large

依据以下信号判断：

```text
需求清晰度
决策数量
模块/contract 数量
数据/状态传播
测试边界
风险/不可逆性
单个 Worker context 能否承载
```

### Small

```text
Compact Spec
→ one Execution Unit
→ AGY
→ Review
→ Verify
→ Closeout
```

### Medium

```text
Shape
→ Spec
→ 2~5 左右可验证 slices（按实际复杂度）
→ AGY slice-by-slice
→ Review/Rework each slice
→ global completeness/verify/closeout
```

### Large

```text
Destination
→ Decision Map / Fog of War
→ resolve frontier decisions
→ Spec
→ staged slices / migration sequence
→ AGY sequential execution
```

Size 可向上升级。

详见 `task-sizing.md`。

---

# 2. SHAPE：先把决定想清楚

维护 Shape Record：

```text
Goal / Destination
Resolved Decisions
Open Decisions
Not Yet Specified
Out of Scope
One-way Decisions
```

### Frontier

只处理前置条件已解决的决策。

```text
repository fact → Codex 自己查
external fact → Codex research
product/architecture trade-off → 用户决定
blocked downstream question → later frontier
```

不要让 AGY 用实现替代未完成的需求决策。

### Shaping Gate

进入 Spec 前要求：

```text
关键 Open Decisions 已解决
剩余 Fog 不阻塞当前 implementation
One-way decisions 已授权或明确 blocked
Out of Scope 明确
```

详见 `shaping.md`。

---

# 3. SPEC：冻结稳定行为契约

Spec 回答：

```text
为什么做？
做成什么样？
哪些决定已经冻结？
如何从公共边界验证？
哪些明确不做？
```

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

默认不要把快速过期的具体文件路径/行号/逐文件施工步骤写进 Spec；这些属于 Execution Unit。

### Verification Seam

必须明确主要公共验证边界：

```text
Primary Seam
Secondary Seam = optional
Existing Prior Art
```

再决定：

```text
Unit
Integration
E2E
Regression Proof
```

详见 `spec-contract.md`。

---

# 4. SLICE：把 Spec 切成 Worker 可完成的小步

先判断 Change Shape：

```text
normal behavior change → Vertical Slice / Tracer Bullet
wide mechanical change → Expand → Migrate → Contract
```

### Vertical Slice

每个 slice 尽量：

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

避免：

```text
先全部 DB
再全部 API
再全部 UI
最后补 tests
```

### Wide Refactor

使用：

```text
EXPAND
→ MIGRATE batches
→ CONTRACT
```

中间尽量保持 repository understandable/green。

每个可执行步骤实例化 `templates/execution-unit.md`。

详见 `execution-slicing.md`。

---

# 5. BASELINE：在 Writer 动手前保护当前工作区

Codex 自己记录：

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

# 6. WORKER READY：官方 AGY CLI Preflight

默认 Primary Worker 使用官方 AGY CLI。

检查：

```bash
command -v agy
agy --version
agy --help
```

至少确认当前安装支持：

```text
-p / --print
--output-format stream-json
--conversation
```

并确认：

```text
auth usable
repo cwd correct
permission mode understood
```

如果 headless 能力缺失/需要人工 TUI：使用 `tty7-supervision.md` 的 fallback；不静默切第三方 Provider。

---

# 7. IMPLEMENT：Headless First

默认：

```bash
cd "$repo_root"
agy -p "<Execution Unit>" \
  --output-format stream-json \
  --print-timeout <appropriate-timeout>
```

从 `init` 保存真实：

```text
conversation_id
cwd
tools
permission_mode
```

必须确认：

```text
init.cwd == repo_root
```

### Runtime completion semantics

stream-json：

```text
init
step_update *
result
```

`result.status=SUCCESS` 只表示 AGY 本轮完成并产生响应：

```text
SUCCESS → REVIEWING
```

不是：

```text
SUCCESS → PASS
```

### Permission soft-deny

Headless 无法弹人工确认时，某些 `Ask` tool/command 可能 soft-deny，而 run 仍继续甚至 exit 0。

所以同时检查：

```text
exit code
result.status/error
stderr
step_update.tool_info.error
actual Git state
```

AGY 没真正执行的测试必须报告 `blocked/not-run`。

### Permissions

默认禁止：

```bash
--dangerously-skip-permissions
```

需要重复运行安全项目命令时，优先使用窄 fine-grained allow rule；一次性人工批准可转 tty7。

详见 `agy-execution.md`。

---

# 8. REVIEW：AGY 返回后 Codex 自己验 diff

固定读取：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

当前 Alpha 2 继续使用 `review-gates.md`。

至少判断：

```text
baseline integrity
Spec / Acceptance coverage
scope drift
architecture / contract
correctness / edge cases
error handling / observability
test quality / seam
external side effects
diff hygiene
```

Alpha 3 将正式拆成：

```text
Spec Fidelity
Engineering Quality
Completeness
```

---

# 9. REWORK：Evidence-Driven Resume

发现 finding 后，使用 `templates/rework-contract.md`。

优先 resume 同一真实 conversation：

```bash
agy -p "<Rework Contract>" \
  --conversation "$agy_conversation_id" \
  --output-format stream-json
```

自动化监督场景有真实 ID 时，优先 `--conversation`，不靠 `-c` 猜最近 session。

Rework 完成后再次回 Codex Review。

默认 3 个完整 Review→Rework→Re-review 周期为 soft limit；达到后重新评估 Spec、slice、root cause、permissions、environment、conversation quality。

---

# 10. COMPLETENESS：找 Missing Diff

普通 Review 回答：

> 已经改的地方对不对？

Completeness 回答：

> 还有没有本来应该改、却没进入 diff 的地方？

追踪：

```text
Changed behavior
→ callers / consumers
→ types / validation / serialization
→ schema / migration / existing data
→ sibling flows / jobs
→ error / empty / permission / retry / fallback
→ cache / derived state
→ orphaned old path
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

unfinished → Rework。

详见 `completeness-regression.md`。

---

# 11. VERIFY：Codex Independent Verification

只有 Review + Completeness PASS 才进入。

基于 Spec 的 Verification Seam / Test Strategy 独立运行：

```text
lint / format-check
typecheck
unit
integration
e2e
build/package
schema/contract
```

Worker 自己跑过不等于 Codex 可以跳过。

确定性 bug：

```text
unfixed RED
→ root-cause fix
→ same test GREEN
→ Codex re-run
```

全部相关项满足：

```text
CODE_VERIFIED
```

---

# 12. CLOSEOUT

`CODE_VERIFIED` 后做 Knowledge Impact Scan。

需要修改时用 `templates/closeout-contract.md`，优先 resume 当前 AGY conversation。

检查：

```text
README / usage
AGENTS / CLAUDE / rules
API / schema / contracts
config / env / CLI / runtime docs
stale examples / retired symbols
workspace residue
```

状态：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

允许零文档 diff。

Closeout 发现真实代码缺陷 → 回 Review/Completeness/Verify，不用文档掩盖。

---

# 13. ACCEPTANCE

只有 Codex 可以：

```text
CLOSEOUT_REVIEW → ACCEPTED
```

至少满足：

```text
Spec satisfied
Relevant Review Gates PASS
Completeness PASS
Verification Seam exercised appropriately
Test Strategy satisfied
Regression Proof satisfied/N/A justified
Codex Independent Verification PASS
Knowledge Closeout PASS
Baseline preserved
No unauthorized side effects
Final diff explainable
```

---

# 14. Small / Medium / Large 快速路径

## Small

```text
INTAKE
→ SIZE=Small
→ compact Shape/Spec
→ one Execution Unit
→ AGY
→ Review
→ Verify
→ Closeout
```

## Medium

```text
INTAKE
→ SIZE=Medium
→ Shape
→ Spec
→ Vertical Slices
→ [AGY → Review/Rework] per slice
→ Global Completeness
→ Verify
→ Closeout
```

## Large

```text
INTAKE
→ SIZE=Large
→ Destination / Decision Map / Fog
→ resolve frontier
→ Spec
→ staged slices or Expand-Migrate-Contract
→ [AGY → Review/Rework] sequentially
→ Global Completeness
→ Verify
→ Closeout
```

---

# 15. Runtime Selection

默认：

```text
AGY headless stream-json
```

只有需要交互时：

```text
tty7 + AGY interactive
```

Pi：

```text
optional specialist only
```

不让 Runtime choice 重新决定 Workflow。
