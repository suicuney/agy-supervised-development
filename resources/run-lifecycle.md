# Supervisor Run Lifecycle — v3.1 Alpha 3

本文件定义 **Codex 的治理生命周期**。AGY CLI 的内部 agent/tool/subagent 状态不复制成第二套 orchestration state machine。

核心顺序：

```text
INTAKE
→ SIZED
→ SHAPING              # Medium/Large when needed
→ SPEC_READY
→ SLICED
→ WORKER_READY
→ DIAGNOSING            # complex bug only, optional
→ IMPLEMENTING
→ REVIEWING             # Three-Axis Review
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

异常状态：

```text
REWORK_REQUIRED
REWORKING
BLOCKED
CANCELLED
FAILED
```

Alpha 3 的关键变化：**Completeness 已成为 Three-Axis Review 的 Axis C，不再在 Review PASS 后重复跑一个独立 `COMPLETENESS_REVIEW` 状态。**

---

## 1. Supervisor Context

每个开发任务至少维护：

```text
repo_root
branch
base_head
baseline_changed_paths
baseline_diff_or_fingerprint

task_size = small | medium | large
shape_record
approved_spec
execution_units
current_execution_unit

test_strategy
primary_verification_seam
regression_proof_status
bug_workflow = simple | complex | not-applicable
feedback_loop = command/evidence | none

agy_conversation_id = real | none
agy_cwd
agy_result_status
rework_count

review_cycle
spec_fidelity_status = pending | pass | rework | blocked
engineering_quality_status = pending | pass | rework | blocked
completeness_status = pending | pass | rework | blocked
review_findings
blast_radius_evidence
remainder_dispositions

closeout_level
knowledge_surface_status
```

不要求：

```text
custom run_id
custom operation_id
custom daemon state
custom worker database
```

---

## 2. INTAKE → SIZED

先做 Task Sizing：

```text
Small
Medium
Large
```

详见 `task-sizing.md`。

Size 不是永久标签；新的决策、blast radius 或 one-way door 可以使其升级。

---

## 3. SHAPING

Small 可 compact shaping；Medium/Large 正式维护：

```text
Resolved Decisions
Open Decisions
Not Yet Specified
Out of Scope
One-way Decisions
```

只有关键 Open Decisions 已解决、剩余 Fog 不阻塞当前实现时，进入 `SPEC_READY`。

Worker 不负责替用户补齐未解决的产品/架构决定。

---

## 4. SPEC_READY → SLICED

Codex 冻结：

```text
Problem
Expected Behavior
Scenarios
Implementation Decisions
Acceptance Criteria
Verification Seams
Test Strategy
Out of Scope
```

再选择：

```text
Vertical Slice
or
Expand → Migrate → Contract
```

生成 Execution Units。Medium/Large 默认不要把完整 Spec 一次塞给 Worker。

---

## 5. Git Baseline

Writer 动手前：

```bash
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

保存 baseline，始终按：

```text
current changes - baseline changes = task-introduced changes
```

不得为了制造干净工作区回滚用户已有改动。

---

## 6. WORKER_READY — AGY Native Preflight

默认 Primary Worker 是官方 AGY CLI。

确认：

```bash
command -v agy
agy --version
agy --help
```

至少要求：

```text
-p / --print
--output-format stream-json
--conversation
correct repo cwd
auth usable
```

headless 不可用时可选择受控 tty7 fallback，或 `BLOCKED`；不静默切第三方 Antigravity Provider。

---

## 7. Optional DIAGNOSING — Complex Bug Only

先按 `resources/bugfix-workflow.md` 判断：

```text
Simple deterministic bug
→ compact RED → FIX → GREEN

Complex / uncertain bug
→ DIAGNOSING
```

Complex Bug 的 DIAGNOSING 至少推进：

```text
Tight Feedback Loop
→ Reproduce
→ Minimise
→ Ranked/Falsifiable Hypotheses
→ Targeted Instrumentation
→ Root Cause Evidence
```

没有 red-capable / symptom-capable feedback loop 时，不能把第一个 plausible code reading 包装成 root cause。

需要产品语义决定时返回 SHAPING；需要环境/权限时 BLOCKED；技术诊断得到足够证据后进入 IMPLEMENTING。

---

## 8. IMPLEMENTING

Codex 只把当前 Execution Unit / Bugfix Contract 交给 AGY。

默认：

```bash
cd "$repo_root"
agy -p "<Execution Unit>" --output-format stream-json
```

读取真实：

```text
init.conversation_id
init.cwd
```

要求：

```text
agy_cwd == repo_root
```

terminal `result` 到达后：

```text
IMPLEMENTING → REVIEWING
```

`result.status=SUCCESS`、exit 0、Worker summary 都不能直接进入 VERIFYING。

复杂 Bug 修复还应保存：

```text
original feedback loop before
minimal repro
root cause evidence
regression proof
original feedback loop after
```

---

## 9. REVIEWING — Three-Axis Review

Codex 固定重新读取：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

然后按照 `resources/review-gates.md` 独立做三个轴：

```text
A. Spec Fidelity        — 做对了吗？
B. Engineering Quality  — 写得好吗？
C. Completeness         — 漏了吗？
```

使用 `templates/review-report.md`。

### Axis A

检查：

```text
Acceptance coverage
missing/partial behavior
wrong semantics
scope creep
unauthorized decisions
verification seam fidelity
```

### Axis B

检查：

```text
architecture/module responsibility
contract/data consistency
correctness/edge cases
error handling/observability
security/side effects
code smells
quality of tests
```

### Axis C

固定做 Missing Diff Review：

```text
changed behavior
→ callers / consumers
→ types / validators / serializers
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

### Aggregation

```text
A PASS + B PASS + C PASS → VERIFYING
any REWORK               → REWORK_REQUIRED
any unresolved BLOCKED   → BLOCKED
```

不做平均分/多数投票。

如果环境支持独立 reviewer，可分离三个轴的上下文再由主 Codex 汇总；不支持时也要分轴形成 verdict 后再汇总。

---

## 10. REWORK_REQUIRED → REWORKING

Finding 使用稳定 ID：

```text
S1... = Spec Fidelity
Q1... = Engineering Quality
C1... = Completeness
V1... = Independent Verification finding
K1... = Closeout finding
```

Rework Contract 固定包含：

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

自动监督场景有真实 id 时不用 `-c` 猜最近 conversation。

Rework 完成后：

```text
REWORKING → REVIEWING
```

即使只修了 Q1，也要重新确认 A/B/C，防止修 Quality 时破坏 Spec 或产生新 missing diff。

默认 3 个完整 `Review → Rework → Re-review` 周期为 soft limit；达到后重新评估 Spec、slice、root cause、permissions、environment、conversation quality，而不是无限循环。

---

## 11. VERIFYING — Codex Independent Verification

**只有 Three-Axis Review 全 PASS 才进入。**

Codex 根据 Verification Seam / Test Strategy 独立运行：

```text
lint / format-check
typecheck
unit
integration
e2e
build/package
schema/contract checks
original bug repro / performance benchmark where applicable
```

Worker 自述不能替代。

AGY headless permission soft-deny 必须区分：

```text
actually-run-and-pass
blocked/not-run
failed
```

### Verification Failure

失败产生新的 `V*` finding：

```text
VERIFYING → REWORK_REQUIRED → REWORKING → REVIEWING
```

返工后必须重新 Three-Axis Review，再重新 Verification；不能只修到某个测试绿就跳回 VERIFYING。

### Pass

```text
VERIFYING → CODE_VERIFIED
```

---

## 12. CODE_VERIFIED

至少能说明：

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

它仍不是最终完成。

---

## 13. CLOSEOUT

所有实际开发任务都做 Knowledge Impact Scan。

若无需修改：

```text
verified-current
```

可零文档 diff。

需要修改时，优先 resume 同一 AGY conversation 发送严格 Closeout Contract；conversation 丢失时可新建，但 final verified repository state 是 Source of Truth。

Closeout 不能重开 Feature/架构范围。

---

## 14. CLOSEOUT_REVIEW → ACCEPTED

Codex 检查 Git、stale references、knowledge surfaces。

Closeout 发现代码真实缺陷：

```text
K finding
→ REWORK_REQUIRED
→ REVIEWING
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
```

不能只改文档掩盖代码问题。

只有满足：

```text
Three-Axis Review PASS
Independent Verification PASS
Knowledge Closeout PASS
Baseline preserved
No unauthorized one-way/external side effect
Final diff explainable
```

才能：

```text
ACCEPTED
```

---

## 15. AGY Conversation Recovery

### 已知真实 conversation id

```bash
agy -p "..." --conversation <id> --output-format stream-json
```

### Conversation 丢失

不猜另一个 conversation。新开 AGY session，并输入：

```text
approved Spec
current Execution Unit
repo/branch/baseline
current diff
Three-Axis findings
verification status
bug diagnosis evidence when applicable
```

Repository progress 不作废，也不默认从头重写。

---

## 16. tty7 Fallback

只在真实 TUI 交互需要时使用：

```text
login/auth
permissions manager
manual approvals
resume picker
slash/TUI-only commands
headless temporary incompatibility
```

进入 tty7 前保留 Spec/Execution Unit/baseline/conversation identity；退出后仍回 Codex Three-Axis Review。

`tty7` 不拥有 Workflow state 或 Acceptance。

---

## 17. Cancel / Interrupt

用户取消或 AGY 中断：

1. 停止当前 process / interactive action；
2. 检查 repository partial progress；
3. 不自动 rollback；
4. 保存真实 conversation id（若取得）；
5. 报告当前安全状态；
6. `CANCELLED`，风险未决时 `BLOCKED`。

---

## 18. One-way Door

始终默认需要用户决定：

```text
destructive/non-additive migration
breaking public API
auth/tenancy relaxation
money/billing semantics
credential behavior
production mutation
irreversible deletion
push/merge/release/deploy
```

AGY permissions 是 Runtime 防护层，不替代用户授权语义。