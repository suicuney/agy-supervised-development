# Supervisor Run Lifecycle

本文件定义 v3.0 的 Codex Supervisor 状态、Pi Run/Operation 协议、返工预算、Completeness Review、Verification 和 Knowledge Closeout 状态。

这里描述的是 **Codex 能证明的状态**。不要假装知道 Provider 内部 token-by-token 的真实意图，也不要把 Pi 的 `agent_settled` 直接等同于实现完成。

---

## 1. Run Context

每个用户开发任务对应一个监督 Run。

建议保存：

```text
run_id
repo_root
branch
base_head
baseline_status / baseline_diff fingerprint
baseline_changed_paths

task_contract_hash
harness_version
pi_session_id
pi_session_file
provider_id
model_id

supervisor_state
operation_seq
current_operation_id
current_mode
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

稳定 runtime identity 是：

```text
run_id + pi_session_id + operation_id
```

不是 TUI 文本、最后一条模型消息或某个旧 process id。

---

## 2. Supervisor State Machine

```text
INIT
  ↓
BASELINED
  ↓
HARNESS_PREFLIGHT
  ├────────→ BLOCKED
  ↓
HARNESS_READY
  ↓
OPERATION_SENT
  ↓
EXECUTING
  ├────────→ BLOCKED
  ├────────→ FAILED
  ├────────→ CANCELLED
  ↓
OPERATION_SETTLED
  ↓
REVIEWING
  ├────────→ REWORK_REQUIRED
  │               ↓
  │         OPERATION_SENT
  ↓
COMPLETENESS_REVIEW
  ├────────→ REWORK_REQUIRED
  │               ↓
  │         OPERATION_SENT
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
  │               ↓
  │         OPERATION_SENT
  ├────────→ BLOCKED
  ↓
ACCEPTED
```

`FAILED` 指当前 operation/runtime 失败；不自动代表整个 Run 的 repository progress 无效。

---

## 3. 为什么用 `OPERATION_SETTLED`

Pi 有完整 agent loop；模型可能多轮 tool call，甚至经历 compaction/retry/follow-up。

所以 Supervisor 不记录：

```text
MODEL_WORKING
MODEL_DONE
```

而记录自己能证明的边界：

```text
OPERATION_SENT
EXECUTING
OPERATION_SETTLED
```

Harness 使用 Pi SDK events 或 RPC event stream 判断 operation 不再自动继续。

关键：

```text
OPERATION_SETTLED != REVIEW PASS
```

模型最终说“完成”不是 Git evidence。

---

## 4. Operation

一个 Run 由多个顺序 operation 构成：

```text
op-001 inspect / optional plan
op-002 implement
op-003 rework
op-004 verify-worker-side
op-005 closeout
op-006 closeout-rework
```

v3.0 默认：

```text
one Run
→ one primary Pi session
→ one active writer operation at a time
```

不默认并行启动第二个 Pi Writer。

每个 operation 必须有真实 ID：

```text
operation_id
operation_seq
mode
status
```

避免 stale output/event 被错配到新一轮。

---

## 5. Harness Preflight Transition

```text
BASELINED → HARNESS_PREFLIGHT
```

确认：

- Pi runtime/SDK/RPC capability；
- Harness version/protocol；
- repo/cwd binding；
- session storage；
- mode/tool policy；
- Provider installed/configured；
- auth usable；
- model available + tool-capable。

全部满足：

```text
HARNESS_PREFLIGHT → HARNESS_READY
```

否则：

```text
HARNESS_PREFLIGHT → BLOCKED
```

不要为了越过 Preflight 自动安装 Provider 或自动完成 OAuth。

---

## 6. Dispatch Transition

Codex 准备好 Task/Rework/Closeout Contract 后：

```text
HARNESS_READY / REWORK_REQUIRED / CLOSEOUT
→ OPERATION_SENT
```

Harness 返回已接受的 `operation_id` 后进入：

```text
OPERATION_SENT → EXECUTING
```

如果请求在接受前就被拒绝，例如 contract schema 错误、repo mismatch、Provider 不可用：

```text
→ BLOCKED or FAILED
```

不要生成假的 operation completion。

---

## 7. Settlement

Harness 应通过 Pi session/runtime event 判断当前 operation settle，并生成 Evidence Bundle。

```text
EXECUTING → OPERATION_SETTLED
```

Settlement 至少说明：

- 当前 operation 不再自动生成/调用工具；
- 结果关联当前 operation ID；
- status 是 settled / blocked / failed / aborted；
- evidence 已落地或结构化返回。

它不证明：

- Task Contract 满足；
- 代码正确；
- Scope 完整；
- tests strategy 合理；
- Closeout 完成。

---

## 8. Review Transition

只要 operation 产生 repository 相关结果，Codex 必须重新读取 repository：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

然后：

```text
OPERATION_SETTLED → REVIEWING
```

实现阶段结论：

- `REWORK` → `REWORK_REQUIRED`；
- `BLOCKED` → `BLOCKED`；
- `PASS` → `COMPLETENESS_REVIEW`。

不能因为 Evidence Bundle 自报 `status=settled` 直接进入 Verification。

---

## 9. Completeness Transition

详细协议见 `completeness-regression.md`。

固定检查：

```text
changed symbol / behavior
→ direct callers
→ indirect callers / scripts / re-exports
→ type / enum / validator / serializer
→ schema / migration / existing data
→ sibling flows / jobs
→ reachable states / retry / fallback / cache
→ orphaned old path
→ tests
→ knowledge impact
```

结论：

- `PASS` → `VERIFYING`；
- `REWORK` → `REWORK_REQUIRED`；
- `BLOCKED` → one-way decision / unresolved external boundary。

每个 remainder disposition：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

---

## 10. Rework Operation

Codex 必须生成结构化 rework contract：

```text
Issue
Evidence
Expected
Required change
Re-run
```

优先 resume 同一个 Pi session：

```text
REWORK_REQUIRED
→ same run_id
→ same pi_session_id
→ new operation_id
→ mode=rework
```

Pi session history 只是上下文帮助；rework 仍必须带关键 evidence，不能只写“修一下刚才的问题”。

---

## 11. Test Strategy & Regression Proof

进入 `VERIFYING` 前必须有：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

可安全、确定性复现的 bug：

```text
regression_proof = required
```

证据链：

```text
unfixed → regression test RED
fix root cause
same test → GREEN
Codex independent re-run
```

Pi 可以产生 RED/GREEN evidence，但最终 Codex 仍独立检查关键命令和 repository state。

---

## 12. Independent Verification Transition

只有 Diff Review + Completeness PASS 才进入：

```text
VERIFYING
```

Codex 根据 Test Strategy 独立执行相关门禁。

失败：

```text
VERIFYING → REWORK_REQUIRED
```

全部相关门禁通过：

```text
VERIFYING → CODE_VERIFIED
```

进入 `CODE_VERIFIED` 前能够说明：

```text
Completeness Sweep = PASS
Blast radius evidence
Remainder dispositions
Test Layer Decision
Regression Proof
Codex independent commands/results
```

---

## 13. Rework Budget

默认：

```text
soft_rework_limit = 3
```

计数单位：

```text
Review → Rework operation → Re-review
```

达到 soft limit，Codex 重新评估：

- 同一问题是否反复；
- Task Contract 是否有歧义；
- root cause 是否判断错误；
- Provider/model 是否不适合；
- Harness mode/tool guard 是否阻碍正确实现；
- completeness 边界是否错；
- 环境/依赖是否有系统故障。

有新证据可继续，但必须显式说明，不无限循环。

---

## 14. Scope Drift

每次 Review：

```text
current changes
- baseline changes
= task-introduced changes
```

若 task-introduced path 超 Scope：

1. 判断是否为当前需求必然传播面；
2. 若不是 → REWORK；
3. 只让 Pi 撤销它本 Run 引入的越界改动；
4. 不碰 baseline-owned changes。

Completeness 可以合法发现初始 Scope 没列出的 caller/schema/test，但必须证明这是 unfinished remainder。

---

## 15. One-way Door

普通可逆实现细节可按项目约定、安全更窄方案处理。

以下默认需要用户明确决定：

- destructive/non-additive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- production mutation；
- irreversible deletion；
- push/merge/release/deploy。

Harness 遇到这类 tool intent 应 fail closed，产生：

```text
blocked-decision-needed
```

Codex 把证据和选项呈现给用户。

---

## 16. Knowledge Closeout Transition

`CODE_VERIFIED` 后：

```text
Knowledge Impact Scan
→ closeout_level = lightweight | full
→ CLOSEOUT
```

需要修改知识文件时，Codex 创建新的：

```text
mode=closeout
operation_id=<new>
```

同一个 Pi Run/session 执行。

然后：

```text
OPERATION_SETTLED
→ CLOSEOUT_REVIEW
```

结论：

- PASS → 最终 Acceptance 判断；
- REWORK → closeout rework operation；
- BLOCKED → 保留 pending/out-of-scope evidence。

Closeout 发现真实代码缺陷时，退回 `REVIEWING / COMPLETENESS_REVIEW / VERIFYING`，不能只改文档掩盖实现问题。

---

## 17. Runtime / Provider Failure 不清空 Run

### Harness bridge crash

先：

- 读取 durable Run Store；
- 检查 Pi session；
- 检查 repository；
- 检查最新 operation state。

不能证明某个 repeat-sensitive effect 是否完成时，标 `recovery uncertainty`，不要无脑 replay。

### Provider failure

Provider auth/quota/transport failure不自动重置：

```text
run_id
pi_session
repository progress
baseline
review state
```

恢复后创建新 operation；如果换 Provider/model，必须显式记录。

---

## 18. Session Resume

只使用真实 Pi session identity。

```text
Do not guess session id/file.
```

如果 session 不可恢复，replacement session 使用：

- 原 Task Contract；
- current repository diff；
- baseline；
- Review/Completeness evidence；
- Test Strategy/Regression state；
- Closeout state（若适用）。

Repository + contracts 可以重建 worker context。

---

## 19. Cancel / Abort

用户要求停止，或 Codex 判断当前 operation 有风险：

```text
Harness abort
→ wait for abort settlement
→ inspect repository
→ record partial progress
→ CANCELLED or BLOCKED
```

Abort 不等于 rollback。不要自动 `git reset --hard`。

---

## 20. Acceptance

只有 Codex 可以：

```text
CLOSEOUT_REVIEW → ACCEPTED
```

至少满足：

- Task Contract 完成；
- relevant Review Gates PASS；
- Completeness PASS；
- Test Strategy 完整；
- Regression Proof 满足；
- Codex Independent Verification PASS；
- Knowledge Closeout PASS；
- baseline/user changes 未受破坏；
- external side effects 符合授权；
- final diff 可解释。
