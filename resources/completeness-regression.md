# Completeness & Regression Proof — v3.0.1

本文件定义两个代码交付门禁：**Change Completeness Sweep** 与 **Regression/Test Proof**。

它们解决两个不同问题：

- 当前 diff 本身是否正确；
- 是否还有“本来应该改、但没有改”的传播面。

Knowledge Closeout 负责代码稳定后的知识对齐；本文件负责进入 `CODE_VERIFIED` 之前的代码世界完整性。

---

## 1. Completeness Contract

一个改动不能因为核心文件已经实现就被视为完整。

判断边界：

> 如果现在交付，Reviewer 会把剩余项称为 **unfinished**，还是 **a different ticket**？

- `unfinished`：属于本任务，必须补齐或证明不适用；
- `different ticket`：保持 out-of-scope，不借完整性扩大需求。

Completeness 不是顺手重构附近代码，而是禁止把**本次改动自己制造的 remainder** 推给未来。

典型 remainder：

- 函数签名变了，caller 仍使用旧签名；
- enum/type 增加值，validator/serializer/fixture 没同步；
- schema 增字段，existing rows 需要 backfill 却未处理；
- 新状态可达，但 error/empty/permission-denied 分支没处理；
- 新路径落地后旧路径失去意义，却仍 orphaned；
- API 变了，consumer/SDK/test fixture 仍按旧 contract；
- bugfix 只覆盖第一个实例，同一 root cause 在 sibling path 仍可达。

---

## 2. Change Completeness Sweep

Codex 不能只读 diff，还要做 **Missing Diff Review**。

对每一个有语义变化的 symbol / contract / state：

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

最后一项只判断“是否影响知识面”；真正 README/docs/rules 修改优先放在 `CODE_VERIFIED` 后的 Closeout。

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

`Remainder disposition` 只能是：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

---

## 4. Completeness 与 Scope Guard

两者方向相反但必须同时成立：

```text
Scope Drift Guard
= 不允许做需求之外的东西

Completeness Sweep
= 不允许漏掉需求之内、由本次改动必然产生的传播面
```

因此：

- 顺手升级依赖通常是 scope drift；
- 新参数导致所有实际 caller 必须补齐是 completeness；
- 顺便设计全站新架构是 different ticket；
- existing data 必须变更才能被新代码正确读取通常是 completeness。

3.0.1 不要求自研静态 Path Guard。若 Pi/Review 发现新的 propagation path：

1. Codex 用调用链/contract evidence 判断它是不是 unfinished；
2. 如果是，更新 Rework Contract 的有效 scope；
3. resume 同一真实 Pi session 继续修改；
4. 如果只是邻近优化，则保持 different ticket。

如果当前安装的可信 Extension 提供 path/tool policy，可以作为附加防护，但 Skill 不假装它一定存在。

---

## 5. One-way Door

普通、可逆、范围内实现细节优先：

- narrower over broader；
- additive over destructive；
- flag-off over flag-on；
- deny over allow；
- project convention over invented pattern。

以下不能为了 completeness 擅自决定：

- destructive/non-additive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- production mutation；
- irreversible deletion。

可信 Extension 若能程序化 block 是加分项；无论 Extension 是否存在，Codex 都必须把未授权 one-way remainder 标：

```text
blocked-decision-needed
```

并请求用户决策。

---

## 6. Bugfix Regression Proof：RED → GREEN

对于能够确定性自动复现的 bug，默认要求：

```text
Reproduce
  ↓
Write Regression Test
  ↓
Run against unfixed behavior
  ↓
RED for expected reason
  ↓
Fix Root Cause
  ↓
Run same test
  ↓
GREEN
  ↓
Codex Independent Re-run
```

目的不是形式化 TDD，而是证明新测试真的能捕获这次缺陷。

### RED evidence

```text
Regression proof: required
Test: <test name/path>
Before fix: FAIL
Failure evidence: <关键错误/断言>
After fix: PASS
Codex re-run: PASS | FAIL
```

Pi Worker 可以生成 before/after evidence，但 Codex 必须判断证据确实对应目标 bug，并独立重跑最终 test。

### 允许 `not-applicable`

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
Alternative evidence: targeted verification / fixture / static check / manual repro ...
```

`not-applicable` 不是“懒得写测试”。

---

## 7. Fix Root Cause，不只盖症状

Codex Review bugfix 时要求证据能回答：

```text
Symptom:
Root cause:
Same cause elsewhere:
Regression boundary:
```

发现同类 pattern 时搜索 sibling sites。若同一根因存在多处，只修一处会让同类 bug 继续可达，则属于 completeness remainder。

---

## 8. Test Layer Decision

每个开发任务显式判断：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

### Unit

适合：纯逻辑、validation、mapping、algorithm、isolated service behavior。

### Integration

适合真实 contract 跨模块/基础设施：

- controller ↔ service；
- ORM ↔ database；
- serialization/schema；
- queue producer/consumer；
- filesystem/external adapter sandbox。

### E2E

真实用户/进程边界优先 required：

```text
UI → API → DB
service → service
CLI → filesystem
browser → auth → callback
```

纯 library/helper 可明确 N/A。

用户明确 skip E2E：

```text
E2E = user-skipped
```

不能伪装为 N/A。

---

## 9. E2E Run Recipe

E2E required 时，Verification 应记录：

```text
command
app/services startup
readiness condition
seed / fixture
required test account / sandbox
teardown
```

如果仓库没有 E2E harness，不默认为小任务引入大型基础设施；由 Task Contract 决定是否建立 minimal harness。

---

## 10. Task Contract 字段

Task Contract 应包含：

```text
Completeness
- 必须追踪哪些 caller/consumer/data/state propagation。
- 哪些 remainder 明确属于 different ticket。

Test Strategy
- Unit: required | not-applicable
- Integration: required | not-applicable
- E2E: required | not-applicable | user-skipped
- Run recipe/environment constraints（若适用）

Regression Proof
- bugfix: required | not-applicable
- 若 not-applicable，原因与替代证据。
```

简单任务可以很短，但三个判断不能默默省略。

---

## 11. Codex Review 顺序

推荐：

```text
Diff correctness
  ↓
Requirement coverage
  ↓
Change Completeness / Blast Radius
  ↓
Architecture / Contract
  ↓
Correctness / Edge Cases
  ↓
Test Layer / Regression Proof
  ↓
Independent Verification
  ↓
CODE_VERIFIED
```

如果 Completeness 找到 missing caller / partial propagation，结论是 REWORK；不能靠“当前 changed files 测试都绿”继续推进。

---

## 12. Final Evidence

进入 `CODE_VERIFIED` 前，Codex 至少能够汇报：

```text
Completeness Sweep: PASS | REWORK | BLOCKED
Blast radius evidence: <搜索/调用链/contract>
Remainders: <none | dispositions>
Test layers: unit/integration/e2e
Regression proof: RED→GREEN | not-applicable
Independent verification: <commands + result>
```

只有代码正确、传播完整、测试层选择合理、可复现 bug 回归证据成立，才允许进入 `CODE_VERIFIED`，然后执行 Knowledge Closeout。
