# Completeness & Regression Proof — v3.3 Alpha 1

本文件定义两件不同但互补的证据工作：

```text
Axis C — Completeness / Missing Diff Review
Regression / Test Proof
```

- **Completeness**：还有没有本来应该改、却没有进入 diff 的传播面？
- **Regression Proof**：对于 Bug，验证是否真的能抓住旧缺陷，并证明修复后恢复？

## 1. Completeness Contract

判断边界：

> 如果现在交付，Reviewer 会把剩余项称为 **unfinished**，还是 **a different ticket**？

- `unfinished`：属于当前 Spec / slice，必须补齐或证明不适用；
- `different ticket`：保持 Out of Scope，不借 Completeness 扩需求。

典型 unfinished remainder：

```text
函数签名变了，caller 仍用旧签名
enum/type 增值，validator/serializer/fixture 没同步
schema 增字段，existing rows 需要处理却遗漏
新状态可达，但 error/empty/permission/retry 分支没处理
API 变了，consumer/SDK/test fixture 仍按旧 contract
bugfix 只修第一个实例，同根因 sibling 仍可达
```

## 2. Axis C — Missing Diff Review

从 changed behavior 向外追踪：

```text
Changed Symbol / Behavior
→ Direct / Indirect Callers
→ Types / Validation / Serialization
→ Schema / Migration / Existing Data
→ Producer / Consumer
→ Sibling Paths / Jobs / Handlers
→ Error / Empty / Permission / Retry
→ Caches / IDs / Derived State / Fallbacks
→ Dead / Orphaned Old Path
→ Tests
→ Knowledge Impact Handoff
```

最后一项只判断知识面是否受影响；真正 docs/rules 修改放在 `CODE_VERIFIED` 后的 Closeout。

## 3. Blast Radius Evidence

Completeness 需要证据，不接受“应该只有这一处”。按项目能力使用：

```bash
rg "<changed-symbol>" .
rg "<old-route|old-field|old-enum|old-config>" .
```

必要时继续追 import/re-export、interface/implementation、producer/consumer、controller→service→repository、schema→model→serializer、shared scripts/jobs、retry/fallback/cache invalidation。

Axis C 至少回答：

```text
Changed surface:
Known consumers:
Propagation surfaces checked:
Remainder found:
Remainder disposition:
Knowledge impact:
```

Disposition：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

发现当前任务必须补齐的 remainder，生成 `C*` finding。

## 4. Completeness 与 Execution Unit Scope

```text
Scope Drift Guard
= 不允许做当前 Spec/slice 之外的东西

Completeness Sweep
= 不允许漏掉当前 change 必然产生的传播面
```

若 Review 发现新的 propagation path：

1. Codex 用调用链/contract evidence 判断是否 unfinished；
2. 是 → 形成 `C*` finding，并更新 bounded Rework Contract；
3. 将该 Contract 发给**同一个 Herdr-managed AGY worker**；
4. 否 → 保持 different ticket。

Execution Unit 的初始文件范围不是永久静态 whitelist。

## 5. Wide Refactor

Wide refactor 使用：

```text
EXPAND
→ MIGRATE A
→ MIGRATE B
→ ...
→ CONTRACT
```

最终 CONTRACT 前必须证明：

```text
old form no longer has active callers
migration batches complete
compatibility bridge can safely remove
```

计划中的 later migration batch 不等于当前 batch 的遗漏，但 plan 外真实 active caller 不能漏。

## 6. One-way Door

以下不能为了 Completeness 擅自决定：

```text
destructive/non-additive migration
breaking public API
auth/tenancy relaxation
money/billing semantics
credential behavior
production mutation
irreversible deletion
```

标记：`blocked-decision-needed`。Runtime permission 不改变用户授权要求。

# Regression / Bug Proof

详细复杂 Bug 流程见 `resources/bugfix-workflow.md`。

## 7. Simple Deterministic Bug：RED → GREEN

```text
Reproduce
→ Write/identify regression test at the agreed seam
→ Run against unfixed behavior
→ RED for expected reason
→ Fix Root Cause
→ Run same proof
→ GREEN
→ Codex Independent Re-run
```

记录：

```text
Regression proof: required
Verification seam: <public boundary>
Test: <test name/path>
Before fix: FAIL
Failure evidence: <target symptom>
After fix: PASS
Codex re-run: PASS | FAIL
```

AGY 可以提供 before/after worker evidence，但 Codex 必须确认它对应目标 Bug，并独立重跑最终 proof。

## 8. Complex Bug：Feedback Loop Before Guessing

```text
Tight Feedback Loop
→ Reproduce
→ Minimise
→ Ranked/Falsifiable Hypotheses
→ Targeted Instrumentation
→ Root Cause Evidence
→ Regression Proof
→ Fix
→ Verify Original Repro
```

没有 symptom-capable feedback loop 时，不应直接把第一种代码猜测当 root cause。

## 9. Regression Proof N/A

允许的典型情况：

- 不可控第三方/生产环境；
- race/timing 暂时无法稳定自动复现；
- 纯视觉且无自动化 harness；
- 构建环境本身就是修复对象；
- 安全复现会产生未授权外部副作用；
- 当前结构没有能代表真实 Bug 的正确 seam。

记录：

```text
Regression proof: not-applicable
Reason: ...
Alternative evidence: ...
Architecture gap: <if applicable>
```

N/A 不能成为跳过真实 symptom 验证的借口。

## 10. Root Cause

Bug Review 至少能回答：

```text
Symptom:
Minimal repro:
Root cause:
Why this cause produces the symptom:
Rejected alternatives / distinguishing evidence:
Same cause elsewhere:
Regression boundary:
```

同根因存在于 reachable sibling 且不修仍会产生当前缺陷 → Axis C remainder。

## 11. Verification Seam

Test Layer 之前先明确：

```text
Primary Verification Seam
Secondary Seam = optional
```

测试优先观察公共行为，不绑定实现细节。若实现过程中发现 seam 本身设计错误，应回 Codex 修改 Spec，而不是 Worker 私自换验证标准。

## 12. Test Layer Decision

每个开发任务显式：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

用户明确 skip E2E 时记录 `user-skipped`，不能伪装 N/A。

## 13. Test Quality vs Test Execution

```text
Axis B / Test Quality
= 测试是不是验证正确的行为边界？

Independent Verification
= 这些命令是不是真的由 Codex 运行并通过？
```

例如：测试设计正确，但 AGY 在 Herdr 中被 `blocked`、测试命令没有真正执行 → Worker evidence = `blocked/not-run`，不能写 PASS。

## 14. AGY Worker Test Evidence

Worker Report 必须区分：

```text
actually-run-and-pass
failed
blocked/not-run
```

AGY 自述 `tests pass` 只有在可见 runtime output 证明命令真实执行时，才能算 worker evidence；最终仍由 Codex 独立重跑。

Herdr `done` / `idle` 不证明测试执行，也不证明测试结果。

## 15. E2E Run Recipe

E2E required 时记录：

```text
command
app/services startup
readiness condition
seed / fixture
required test account / sandbox
teardown
```

仓库没有 E2E harness 时，不默认为 Small task 引入大型基础设施；由 Spec/Task Size 决定 minimal harness 或替代证据。

## 16. Execution Unit 字段

每个 Execution Unit 至少继承：

```text
Verification Seam
Test Strategy
Regression Proof
Worker Verification
Completeness Watch
```

模板见 `../templates/execution-unit.md`。

## 17. Review 顺序

```text
Three-Axis Review
├─ A Spec Fidelity
├─ B Engineering Quality
└─ C Completeness
       ↓ all PASS
Codex Independent Verification
       ↓
CODE_VERIFIED
```

Regression Proof 设计质量在 Axis B 判断；同根因传播在 Axis C 判断；最终重跑属于 Independent Verification。

## 18. Final Evidence

进入 `CODE_VERIFIED` 前至少能汇报：

```text
Spec Fidelity: PASS
Engineering Quality: PASS
Completeness: PASS
Blast radius evidence: <search/call-chain/contract>
Remainders: <none | dispositions>
Primary Verification Seam: <...>
Test layers: unit/integration/e2e
Regression proof: RED→GREEN | complex-loop proof | not-applicable
Original bug repro after fix: PASS | N/A
Independent verification: <commands + result>
```
