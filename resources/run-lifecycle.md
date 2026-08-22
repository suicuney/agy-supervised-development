# Supervisor Run Lifecycle — v3.0.1

本文件只定义 **Codex 的治理状态**。Pi 内部 agent loop、tool events、provider streaming 和 session persistence 由 Pi 自己管理；3.0.1 不再复制第二套 Run/Operation runtime state machine。

---

## 1. Supervisor Context

每个开发任务建议保存：

```text
repo_root
branch
base_head
baseline_changed_paths
baseline_diff_or_fingerprint

task_contract
pi_session_id
pi_session_file = optional
pi_session_cwd
provider_id = observable | unknown
model_id = observable | unknown
workflow_extension = detected | absent | unknown
workflow_mode = plan | build | review | debug | none

supervisor_state
rework_count

completeness_status = pending | pass | rework | blocked
blast_radius_evidence
remainder_dispositions

test_strategy:
  unit = required | not-applicable
  integration = required | not-applicable
  e2e = required | not-applicable | user-skipped
regression_proof = required | red-green-pass | not-applicable

closeout_level = lightweight | full
knowledge_surface_status
```

不要求：

```text
custom run_id
custom operation_id
harness_version
custom durable Run Store
```

Pi session identity 使用 Pi 实际返回值，不自己发明。

---

## 2. Supervisor State Machine

```text
INIT
  ↓
BASELINED
  ↓
PI_READY
  ↓
PLANNING              optional
  ↓
IMPLEMENTING
  ↓
REVIEWING
  ├────────→ REWORK_REQUIRED
  │               ↓
  │           REWORKING
  │               ↓
  │           REVIEWING
  ↓
COMPLETENESS_REVIEW
  ├────────→ REWORK_REQUIRED
  ├────────→ BLOCKED
  ↓
VERIFYING
  ├────────→ REWORK_REQUIRED
  ├────────→ BLOCKED
  ↓
CODE_VERIFIED
  ↓
CLOSEOUT
  ↓
CLOSEOUT_REVIEW
  ├────────→ REWORK_REQUIRED
  ├────────→ BLOCKED
  ↓
ACCEPTED
```

任何阶段都可能因用户取消进入 `CANCELLED`，因不可恢复运行错误进入 `FAILED`。

---

## 3. `PI_READY`

`BASELINED → PI_READY` 之前确认：

- Pi executable/CLI capability；
- `--mode json`；
- session persistence/resume；
- repo cwd；
- Provider/model 可用性；
- auth 状态；
- workflow extension/mode 能力是否存在。

缺失必需能力：

```text
→ BLOCKED
```

默认不自动安装 Pi/Provider/Extension，也不自动 OAuth。

---

## 4. PLANNING 是可选治理阶段

复杂任务可先让 Pi 做只读 plan/inspect。

如果可信 `pi-agent-modes` 可用：

```text
PLANNING → --modes plan
```

否则可以使用普通 Pi + read-only Task Contract 做分析，但必须明确：

```text
programmatic read-only enforcement = unavailable
```

对于必须强制只读才安全的场景，缺失可信 policy extension 时应 BLOCK，而不是把 prompt 当 sandbox。

Planning 不是所有小任务必经阶段。

---

## 5. IMPLEMENTING

Codex 发 Task Contract，Pi 作为唯一主要 Writer 执行。

推荐：

```text
Pi JSON mode
+ same repo cwd
+ new real session
+ build workflow mode if trusted extension is available
```

Pi JSON stream 的 `agent_end` / 正常进程退出只说明本次 turn 返回。

不要额外建立：

```text
OPERATION_SETTLED
```

这样的治理状态。turn 返回后直接由 Codex进入 `REVIEWING`。

---

## 6. REVIEWING

Pi turn 返回后，Codex重新读取 repository：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

实现 Review 结论：

```text
PASS    → COMPLETENESS_REVIEW
REWORK  → REWORK_REQUIRED
BLOCKED → BLOCKED
```

Pi final answer、JSON `agent_end`、Provider completion 都不能直接 PASS。

---

## 7. REWORKING

Rework 固定使用：

```text
Issue
Evidence
Expected
Required change
Re-run
Scope reminder
```

优先 resume 同一真实 Pi session：

```text
same pi_session_id
new Pi invocation
```

如果 `pi-agent-modes` 可用：

```text
bug/root-cause rework → debug
general structural rework → build
```

Rework 后回 `REVIEWING`。

默认：

```text
soft_rework_limit = 3
```

计数单位是完整：

```text
Review → Rework → Re-review
```

达到 soft limit 后重新评估 Task Contract、根因、Provider/model、extension policy、环境和 completeness 边界，不静默无限循环，也不直接切 `yolo`。

---

## 8. COMPLETENESS_REVIEW

固定检查：

```text
changed symbol / behavior
→ direct callers
→ indirect callers / scripts / re-exports
→ types / enums / validators / serializers
→ schema / migration / existing data
→ sibling flows / jobs
→ reachable error / empty / permission / retry / fallback
→ cache / derived state / stale IDs
→ orphaned old path
→ tests
→ knowledge impact
```

Remainder disposition：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

结论：

```text
PASS    → VERIFYING
REWORK  → REWORK_REQUIRED
BLOCKED → BLOCKED
```

Completeness 可以扩大“被证明为 unfinished”的实际文件传播面，但不能扩大到另一个 ticket。

---

## 9. VERIFYING

Codex 根据 Test Layer Decision 独立运行门禁。

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

可安全确定性复现的 bug 还要求：

```text
unfixed → regression test RED
fix root cause
same test → GREEN
Codex independent re-run
```

Verification 失败：

```text
VERIFYING → REWORK_REQUIRED
```

全部相关门禁满足：

```text
VERIFYING → CODE_VERIFIED
```

---

## 10. CODE_VERIFIED

进入前至少能说明：

```text
Diff Review = PASS
Completeness Sweep = PASS
Blast radius evidence
Remainder dispositions
Test Layer Decision
Regression Proof
Codex independent commands/results
```

`CODE_VERIFIED` 不是最终完成，随后必须做 Knowledge Impact Scan。

---

## 11. CLOSEOUT

Codex判断：

```text
closeout_level = lightweight | full
```

所有实际开发任务都 Scan。

如果现有知识已经正确：

```text
verified-current
```

可以零文档 diff。

需要修改时，resume 同一 Pi session。若 `pi-agent-modes` 可用，使用：

```text
build + strict Closeout Contract
```

不发明 `closeout` custom mode。

Pi turn 返回后：

```text
CLOSEOUT → CLOSEOUT_REVIEW
```

Closeout 发现真实代码问题时退回代码 Review/Completeness/Verification，不通过改文档掩盖。

---

## 12. Session Resume

只 resume 真实 Pi session：

```text
Do not guess session id/file.
```

同时验证：

```text
session cwd == repo_root
```

如果 session 丢失：

- 保留 repository state；
- 新建 replacement Pi session；
- 输入原 Task Contract + current diff + Review/Completeness/Test evidence；
- 不自动从头重写代码。

如果已经 `CODE_VERIFIED`，replacement session 只继续 Closeout。

---

## 13. Provider Failure 不清空治理进度

Auth/quota/transport/model failure 不自动重置：

```text
baseline
repository progress
Pi session if still valid
review/completeness/test status
```

有限 safe retry 可以继续；Provider/model failover 不得静默发生。

如果用户授权切换 Provider/model，记录变化后继续当前 repository state。

---

## 14. Scope Drift

每轮 Review：

```text
current changes
- baseline changes
= task-introduced changes
```

超 Scope path：

1. 判断是否是本次改动必然 propagation；
2. 是 → 纳入 completeness scope；
3. 否 → REWORK，只撤销 Pi 本任务产生的越界修改；
4. 不碰 baseline-owned changes。

---

## 15. One-way Door

以下默认需要用户决定：

- destructive/non-additive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- production mutation；
- irreversible deletion；
- push/merge/release/deploy。

可信 policy extension 若能阻断是加分项；无论 extension 是否存在，Codex 都不能把这些行为默认为已授权。

---

## 16. Cancel / Abort

用户停止任务时：

- 停止当前 Pi invocation；
- 若使用 RPC，调用 Pi 原生 abort；
- 检查 repository partial progress；
- 不自动 rollback；
- 状态进入 `CANCELLED` 或风险情况下 `BLOCKED`。

---

## 17. Acceptance

只有 Codex 可以：

```text
CLOSEOUT_REVIEW → ACCEPTED
```

至少满足：

- Task Contract 完成；
- relevant Review Gates PASS；
- Completeness PASS；
- Test Strategy 满足；
- Regression Proof 满足/N/A 合理；
- Codex Independent Verification PASS；
- Knowledge Closeout PASS；
- baseline/user changes 未被破坏；
- Provider/session/extension facts 没有被伪造；
- external side effects 符合授权；
- final diff 可解释。
