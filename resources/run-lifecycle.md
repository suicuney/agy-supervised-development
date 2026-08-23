# Supervisor Run Lifecycle — v3.1 Alpha 2

本文件定义 **Codex 的治理生命周期**。AGY CLI 自己的内部 agent/tool/subagent 状态不复制成第二套 orchestration state machine。

核心顺序：

```text
INTAKE
→ SIZED
→ SHAPING          # Medium/Large when needed
→ SPEC_READY
→ SLICED
→ WORKER_READY
→ IMPLEMENTING
→ REVIEWING
→ COMPLETENESS_REVIEW
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

异常状态：

```text
REWORK_REQUIRED
BLOCKED
CANCELLED
FAILED
```

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

agy_conversation_id = real | none
agy_cwd
agy_result_status
rework_count

completeness_status
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

Size 不是永久标签。后续发现新的决策、blast radius 或 one-way door 时可以升级。

---

## 3. SHAPING

Small 可走 compact shaping；Medium/Large 正式维护：

```text
Resolved Decisions
Open Decisions
Not Yet Specified
Out of Scope
One-way Decisions
```

只有关键 Open Decisions 已解决、剩余 Fog 不阻塞当前实现时，进入 `SPEC_READY`。

Worker 不负责替用户补齐未解决的产品/架构决策。

---

## 4. SPEC_READY → SLICED

Codex 冻结 Spec：

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

再判断 Change Shape：

```text
Vertical Slice
or
Expand → Migrate → Contract
```

生成 Execution Units。Medium/Large 默认不要一次把完整 Spec 交给 Worker。

---

## 5. Git Baseline

进入写实现前建立 baseline：

```bash
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

规则：

```text
current changes - baseline changes = task-introduced changes
```

不得为了“干净工作区”回滚用户已有改动。

---

## 6. WORKER_READY — AGY Native Preflight

默认 Primary Worker 目标是官方 AGY CLI。

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

如果 headless 能力不可用：

- 可以选择受控 tty7 interactive fallback；
- 或在确有需要时 `BLOCKED`；
- 不静默改成第三方 Antigravity Provider。

详见 `agy-execution.md`。

---

## 7. IMPLEMENTING

Codex 只把**当前 Execution Unit**交给 AGY。

默认：

```bash
cd "$repo_root"
agy -p "<Execution Unit>" --output-format stream-json
```

读取真实 `init.conversation_id` 和 `init.cwd`，要求：

```text
agy_cwd == repo_root
```

本轮 terminal `result` 到达后：

```text
IMPLEMENTING → REVIEWING
```

无论 `result.status` 是否 `SUCCESS`，都不能直接进入 Verification/Acceptance。

如果 run 异常中止，先检查 repository partial effects，再决定 resume / replacement conversation。

---

## 8. REVIEWING

Codex 自己读取：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

当前 Alpha 2 继续复用现有 Review Gates；后续 Alpha 3 会升级为：

```text
Spec Fidelity
Engineering Quality
Completeness
```

本阶段结论：

```text
PASS    → COMPLETENESS_REVIEW
REWORK  → REWORK_REQUIRED
BLOCKED → BLOCKED
```

AGY final response、exit 0、`result.status=SUCCESS` 都不是 Review PASS。

---

## 9. REWORK_REQUIRED → REWORKING

Rework 固定使用：

```text
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

自动化监督场景优先显式 `--conversation`，不要用 `-c` 猜“最近 conversation”。

Rework 结束后回：

```text
REVIEWING
```

默认 soft limit：3 个完整 `Review → Rework → Re-review` 周期。达到后重新评估 Spec、slice 边界、root cause、permissions 和环境，不无限循环。

---

## 10. COMPLETENESS_REVIEW

固定做 Missing Diff Review：

```text
changed behavior
→ callers / consumers
→ types / validators / serializers
→ schema / migration / existing data
→ sibling flows / jobs
→ error / retry / fallback
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

发现 unfinished：

```text
→ REWORK_REQUIRED
```

如果属于当前 slice 的真实传播面，Codex 可以扩充 Rework Contract；这不是 Scope Creep。

---

## 11. VERIFYING

只有 Review + Completeness PASS 才进入。

Codex 根据 Spec 的 Verification Seam 和 Test Strategy 独立运行：

```text
lint / format-check
typecheck
unit
integration
e2e
build/package
schema/contract checks
```

Worker 自己声称测试通过不能替代这一阶段。

特别注意：AGY headless 中某些 `Ask` command 可能被 soft-deny，但 run 仍可能 exit 0。因此 Codex 必须区分：

```text
actually-run-and-pass
blocked/not-run
failed
```

确定性 bug 还要满足 RED → root-cause fix → GREEN → Codex re-run。

通过：

```text
VERIFYING → CODE_VERIFIED
```

失败：

```text
VERIFYING → REWORK_REQUIRED
```

---

## 12. CODE_VERIFIED

至少能说明：

```text
Spec/Requirement Review = PASS
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

需要修改时优先 resume 同一 AGY conversation，发送严格 Closeout Contract；如果 conversation 已丢失，则新建 conversation，但必须以 final verified repository state 为 Source of Truth。

Closeout 不能重开新 Feature/架构范围。

---

## 14. CLOSEOUT_REVIEW → ACCEPTED

Codex 重新检查 Git、stale references、knowledge surfaces。

只有满足：

```text
Spec satisfied
Review PASS
Completeness PASS
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

继续：

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
Review/Completeness findings
verification status
```

Repository progress 不作废，也不默认从头重写。

---

## 16. tty7 Fallback

只有需要 TUI 交互时使用：

```text
login/auth
permissions manager
manual approvals
resume picker
slash/TUI-only commands
headless temporary incompatibility
```

进入 tty7 前保留当前 Spec/Execution Unit/baseline/conversation identity；退出后仍回 Codex Review。

**tty7 不拥有 Workflow state，也不拥有最终 Acceptance。**

---

## 17. Cancel / Interrupt

用户取消或 AGY 被中断：

1. 停止当前 process / interactive action；
2. 检查 repository partial progress；
3. 不自动 rollback；
4. 保存真实 conversation id（若已取得）；
5. 报告当前安全状态；
6. `CANCELLED`，存在风险未决时 `BLOCKED`。

---

## 18. One-way Door

以下始终默认需要用户决定：

- destructive/non-additive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- production mutation；
- irreversible deletion；
- push/merge/release/deploy。

AGY permissions 是防护层，不替代用户授权语义。
