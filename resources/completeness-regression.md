# Completeness & Regression Proof — v3.1

本文件定义进入 `CODE_VERIFIED` 前的两个核心门禁：

```text
Change Completeness Sweep
Regression / Test Proof
```

它们回答两个不同问题：

- 当前 diff 里的东西是否正确；
- 是否还有“本来应该改、却没有进入 diff”的传播面。

---

## 1. Completeness Contract

判断边界：

> 如果现在交付，Reviewer 会把剩余项称为 **unfinished**，还是 **a different ticket**？

- `unfinished`：属于当前 Spec / slice，必须补齐或证明不适用；
- `different ticket`：保持 Out of Scope，不借 Completeness 扩需求。

典型 unfinished remainder：

- 函数签名变了，caller 仍用旧签名；
- enum/type 增值，validator/serializer/fixture 没同步；
- schema 增字段，existing rows 需要处理却遗漏；
- 新状态可达，但 error/empty/permission/retry 分支没处理；
- API 变了，consumer/SDK/test fixture 仍按旧 contract；
- bugfix 只修第一个实例，同根因 sibling 仍可达。

---

## 2. Missing Diff Review

对每一个语义变化追踪：

```text
Changed Symbol / Behavior
        ↓
Direct Callers
        ↓
Indirect Callers / Re-exports / Scripts
        ↓
Types / Enums / Validation / Serialization
        ↓
Schema / Migration / Existing Data
        ↓
Sibling Paths / Jobs / Handlers
        ↓
Reachable Error / Empty / Permission / Retry States
        ↓
Caches / IDs / Derived State / Fallbacks
        ↓
Dead / Orphaned Old Path
        ↓
Tests
        ↓
Knowledge Impact Handoff
```

最后一项只判断知识面是否受影响；真正 docs/rules 修改放在 `CODE_VERIFIED` 后的 Closeout。

---

## 3. Blast Radius Evidence

Completeness 需要证据，不接受“应该只有这一处”。

按项目能力使用：

```bash
rg "<changed-symbol>" .
rg "<old-route|old-field|old-enum|old-config>" .
```

必要时继续追：

- import/re-export/barrel；
- interface/implementation；
- producer/consumer；
- controller → service → repository；
- DB schema → ORM/model → serializer；
- event producer → queue/topic → consumer；
- shared SDK/scripts/cron/admin tooling；
- sibling endpoint/platform；
- retry/fallback/cache invalidation。

Review 至少回答：

```text
Changed surface:
Known consumers:
Propagation surfaces checked:
Remainder found:
Remainder disposition:
Knowledge impact:
```

Remainder disposition：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

---

## 4. Completeness 与 Execution Unit Scope

两者方向相反但必须同时成立：

```text
Scope Drift Guard
= 不允许做当前 Spec/slice 之外的东西

Completeness Sweep
= 不允许漏掉当前 change 必然产生的传播面
```

因此：

- 顺手升级依赖通常是 scope drift；
- 新参数导致所有实际 caller 必须补齐是 completeness；
- 顺便重做全站架构是 different ticket；
- existing data 必须变更才能被新代码正确读取通常是 completeness。

若 AGY/Review 发现新的 propagation path：

1. Codex 用调用链/contract evidence 判断是否 unfinished；
2. 是 → 更新 `Rework Contract` 的有效 scope；
3. resume 当前真实 AGY conversation；
4. 否 → 保持 different ticket。

Execution Unit 的初始文件范围不是永久静态 whitelist。

---

## 5. 与 Vertical Slice / Wide Refactor 的关系

### Vertical Slice

每个 slice 的 Completeness 先保证：

> 这个 slice 自己交付的行为是完整的。

多个 slice 完成后，再做一次 Global Completeness，防止跨 slice contract 漏传播。

### Expand → Migrate → Contract

每个 migration batch 可以只完成一部分调用点，但必须符合已批准 migration sequence。

最终 `CONTRACT` 前必须证明：

```text
old form no longer has active callers
migration batches complete
compatibility bridge can safely remove
```

不要把计划内的 later migration batch误判成当前 batch 的 unfinished；同时也不能遗漏不在 migration plan 里的真实 caller。

---

## 6. One-way Door

以下不能为了 completeness 擅自决定：

- destructive/non-additive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- production mutation；
- irreversible deletion。

标：

```text
blocked-decision-needed
```

AGY permission engine 是否允许执行，不改变用户授权要求。

---

## 7. Bugfix Regression Proof：RED → GREEN

对于能够确定性、安全复现的 bug，默认要求：

```text
Reproduce
→ Write/identify regression test at the agreed seam
→ Run against unfixed behavior
→ RED for expected reason
→ Fix Root Cause
→ Run same test
→ GREEN
→ Codex Independent Re-run
```

### RED Evidence

```text
Regression proof: required
Verification seam: <public boundary>
Test: <test name/path>
Before fix: FAIL
Failure evidence: <target symptom>
After fix: PASS
Codex re-run: PASS | FAIL
```

AGY 可以提供 before/after worker evidence，但 Codex 必须判断它确实对应目标 bug，并独立重跑最终 test。

---

## 8. 允许 Regression Proof N/A

例如：

- 不可控第三方/生产环境；
- race/timing 无法稳定复现；
- 纯视觉且无自动化 harness；
- 构建环境本身就是修复对象；
- 安全复现会产生未授权外部副作用。

记录：

```text
Regression proof: not-applicable
Reason: ...
Alternative evidence: ...
```

N/A 不是“懒得写测试”。

---

## 9. Fix Root Cause，不只盖症状

Codex Review bugfix 时要求能回答：

```text
Symptom:
Root cause:
Same cause elsewhere:
Regression boundary:
```

同根因存在于 reachable sibling 且不修就仍会产生同类 bug → Completeness remainder。

---

## 10. Verification Seam

Test Layer 之前先明确：

```text
Primary Verification Seam
Secondary Seam = optional
```

测试应优先观察公共行为，不绑定实现细节。

错误例子：

```text
Spec 行为 = POST /orders
实际只测试 private helper
```

即使 helper tests 全绿，也不能证明用户行为。

如果实现过程中发现 seam 本身设计错误，需要回 Codex 修改 Spec 决策，而不是 Worker 私自换验证标准。

---

## 11. Test Layer Decision

每个开发任务显式：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

### Unit

适合纯逻辑、validation、mapping、algorithm。

### Integration

适合：

```text
controller ↔ service
ORM ↔ database
serialization/schema
queue producer/consumer
filesystem/external adapter sandbox
```

### E2E

真实用户/进程边界优先 required：

```text
UI → API → DB
service → service
CLI → filesystem
browser → auth → callback
```

用户明确 skip：

```text
E2E = user-skipped
```

不能伪装为 N/A。

---

## 12. AGY Worker Test Evidence

AGY 的 Worker Report 应区分：

```text
actually-run-and-pass
failed
blocked/not-run
```

特别是在 headless 模式下，Ask permission 的 command 可能 soft-deny，但进程最终 exit 0。

因此：

```text
AGY says "tests pass"
```

只有 tool/runtime evidence 能证明测试命令真实执行时，才能作为 worker evidence；最终仍由 Codex独立重跑。

---

## 13. E2E Run Recipe

E2E required 时记录：

```text
command
app/services startup
readiness condition
seed / fixture
required test account / sandbox
teardown
```

如果仓库没有 E2E harness，不默认为 Small task 引入大型基础设施；由 Spec/Task Size 决定是否建立 minimal harness。

---

## 14. Execution Unit 中的 Test 字段

每个 Execution Unit 至少继承：

```text
Verification Seam
Test Strategy
Regression Proof
Worker Verification
Completeness Watch
```

模板见 `../templates/execution-unit.md`。

---

## 15. Codex Review 顺序

Alpha 2 推荐：

```text
Diff correctness
→ Spec / Acceptance coverage
→ Change Completeness / Blast Radius
→ Architecture / Contract
→ Correctness / Edge Cases
→ Verification Seam / Test Layer / Regression Proof
→ Independent Verification
→ CODE_VERIFIED
```

Alpha 3 会把它重组为三轴，但本文件的 Completeness/Regression 语义继续保留。

---

## 16. Final Evidence

进入 `CODE_VERIFIED` 前，Codex 至少能汇报：

```text
Completeness Sweep: PASS | REWORK | BLOCKED
Blast radius evidence: <search/call-chain/contract>
Remainders: <none | dispositions>
Primary Verification Seam: <...>
Test layers: unit/integration/e2e
Regression proof: RED→GREEN | not-applicable
Independent verification: <commands + result>
```
