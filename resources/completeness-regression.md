# Completeness & Regression Proof

本文件定义 v2.1.2 的两个代码交付门禁：**Change Completeness Sweep** 与 **Regression/Test Proof**。它们解决两个不同问题：

- 当前 diff 本身是否正确；
- 是否还有“本来应该改、但没有改”的传播面。

Knowledge Closeout 负责代码稳定后的知识对齐；本文件优先负责进入 `CODE_VERIFIED` 之前的**代码世界完整性**。

## 1. Completeness Contract

一个改动不能因为核心文件已经实现就被视为完整。

判断边界：

> 如果现在交付，Reviewer 会把剩余项称为 **unfinished**，还是 **a different ticket**？

- `unfinished`：属于本任务，必须补齐或明确证明不适用；
- `different ticket`：保持 out-of-scope，不借完整性扩大需求。

Completeness 不是“顺手把附近都重构掉”，而是禁止把**本次改动自己制造的 remainder** 推给未来。

典型 remainder：

- 函数签名变了，但仍有 caller 使用旧签名；
- enum/type 增加了值，但 validator/serializer/fixture 没同步；
- schema 增加字段，但 existing rows 没有需要的 backfill；
- 新状态可达，但 error/empty/permission-denied 分支没处理；
- 新路径落地后旧路径已无意义，却仍有 orphaned dead code；
- API 变了，但内部 consumer / SDK / test fixture 仍按旧 contract 工作；
- 修复只覆盖第一个实例，同类 sibling path 仍保留同一根因。

## 2. Change Completeness Sweep

Codex 在实现 Review 时，不能只读 diff，还要做一次 **Missing Diff Review**。

对每一个有语义变化的 symbol / contract / state，沿以下链路检查：

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

最后一项只判断“是否影响知识面”，真正的 README/docs/rules 修改仍放在 `CODE_VERIFIED` 后的 Knowledge Closeout。

## 3. Blast Radius Evidence

Completeness 需要证据，不接受“应该只有这一处”。

按项目能力使用：

```bash
rg "<changed-symbol>" .
rg "<old-route|old-field|old-enum|old-config>" .
```

必要时继续追：

- import / re-export / barrel；
- interface / implementation；
- producer / consumer；
- controller → service → repository；
- DB schema → ORM/model → serializer；
- event producer → queue/topic → consumer；
- shared SDK / scripts / cron / admin tooling；
- sibling endpoint / sibling platform；
- retry / fallback / cache invalidation。

Review 报告至少能回答：

```text
Changed surface:
Known consumers:
Propagation surfaces checked:
Remainder found:
Remainder disposition:
Knowledge impact:
```

`Remainder disposition` 只能是：

- `fixed-in-run`；
- `not-applicable`；
- `out-of-scope-different-ticket`；
- `blocked-decision-needed`。

不要使用含糊的 `later` / `follow-up maybe` 掩盖本任务的未完成部分。

## 4. Completeness 与 Scope Drift 的关系

两者方向相反但必须同时成立：

```text
Scope Drift Guard
= 不允许做需求之外的东西

Completeness Sweep
= 不允许漏掉需求之内、由本次改动必然产生的传播面
```

因此：

- “顺手升级依赖”通常是 scope drift；
- “函数新增 currency 参数后把所有实际 caller 补齐”是 completeness；
- “顺便做全站 locale 系统”是 different ticket；
- “已有数据必须增加 currency 才能被新代码正确读取”通常是 completeness。

无法判断时，不让 AGY自行扩张；Codex 依据 Task Contract、现有 contract 和可逆性裁决，必要时 `BLOCKED`。

## 5. One-way Door

Codex 可以自行裁决普通、可逆、范围内的实现细节，优先：

- narrower over broader；
- additive over destructive；
- flag-off over flag-on；
- deny over allow（安全边界）；
- project convention over invented pattern。

但以下属于 one-way / high-blast-radius decision，不能为了 completeness 擅自决定：

- destructive / non-additive migration；
- breaking public API contract；
- auth / tenancy boundary relaxation；
- money / billing semantics；
- secrets / credential behavior；
- production mutation；
- irreversible data deletion。

此时把可独立完成的安全部分做完，危险决策标 `blocked-decision-needed`。

## 6. Bugfix Regression Proof：Red → Green

对于**能够确定性自动复现**的 bug，默认要求：

```text
Reproduce
  ↓
Write Regression Test
  ↓
Run against unfixed behavior
  ↓
RED for the expected reason
  ↓
Fix Root Cause
  ↓
Run same test
  ↓
GREEN
  ↓
Codex Independent Re-run
```

目的不是形式化 TDD，而是证明：

> 新测试真的能够捕获这次缺陷，而不是修完以后补了一个本来就会绿的 assertion。

### Red Proof 必须记录

```text
Regression proof: required
Test: <test name/path>
Before fix: FAIL
Failure evidence: <关键错误/断言>
After fix: PASS
Codex re-run: PASS | FAIL
```

### 允许 `not-applicable`

以下情况可以不强制 red-before-green，但必须说明为什么：

- 缺陷依赖不可控第三方或生产环境；
- race / timing 问题无法稳定重现；
- 纯视觉/人工体验问题且项目没有相应自动化能力；
- 修复对象是构建/环境本身，无法在同一 harness 建立 unfixed 对照；
- 安全复现会造成不允许的外部副作用。

此时记录：

```text
Regression proof: not-applicable
Reason: ...
Alternative evidence: targeted verification / fixture / static check / manual repro ...
```

`not-applicable` 不是“懒得写测试”。只要可安全、确定性自动复现，就应优先 Red → Green。

## 7. Fix Root Cause，不只盖症状

Codex Review bugfix 时要求 AGY 回答：

```text
Symptom:
Root cause:
Same cause elsewhere:
Regression boundary:
```

发现同类 pattern 时搜索 sibling sites。若同一根因存在多处，而只修一处会让同类 bug 继续可达，这属于 completeness remainder。

不要用仅 UI 禁用按钮去掩盖服务端重复写入、仅 catch 异常去掩盖错误 transaction boundary 等症状级修复。

## 8. Test Layer Decision

每个实际开发任务在 Task Contract / Review 时对测试层做显式判断：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

不能把“跑过测试”当作测试策略。

### Unit

适合：

- 纯逻辑；
- validation；
- mapping；
- algorithm；
- isolated service behavior。

### Integration

当真实 contract 跨越模块/基础设施边界时考虑：

- controller ↔ service；
- ORM ↔ database；
- serialization / schema；
- queue producer/consumer；
- filesystem / external adapter sandbox。

### E2E

当功能存在真实用户或进程边界流程时优先 required，例如：

```text
UI → API → DB
service → service
CLI → filesystem
browser → auth → callback
```

如果只是纯 library/helper，且 lower layers 已完整覆盖，可以明确 `not-applicable`。

若用户明确要求跳过 E2E，记录 `user-skipped`，不能伪装成 `not-applicable`。

## 9. E2E Run Recipe

当 E2E required 时，Verification 应知道真实运行配方：

```text
command
app/services startup
readiness condition
seed / fixture
required test account / sandbox
teardown
```

如果仓库没有 E2E harness，不默认为了一个小任务擅自引入大型基础设施；将是否建立 minimal harness 作为 Task Contract / decision boundary。

## 10. Task Contract 增量字段

v2.1.2 推荐在原 Task Contract 中增加：

```text
Completeness
- 必须追踪哪些 caller / consumer / data / state propagation。
- 哪些 remainder 明确属于 different ticket。

Test Strategy
- Unit: required | not-applicable
- Integration: required | not-applicable
- E2E: required | not-applicable | user-skipped
- Run recipe / environment constraints（若适用）

Regression Proof
- bugfix: required | not-applicable
- 若 not-applicable，原因和替代证据。
```

对于简单任务可以很短，但三个判断不能被默默省略。

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

如果 Completeness Sweep 找到 missing caller / partial propagation，结论是 `REWORK`，不能靠“当前 changed files 的测试都绿了”继续推进。

## 12. Final Evidence

进入 `CODE_VERIFIED` 前，Codex 至少能够汇报：

```text
Completeness Sweep: PASS | REWORK | BLOCKED
Blast radius evidence: <搜索/调用链/contract>
Remainders: <none | dispositions>
Test layers: unit / integration / e2e
Regression proof: RED→GREEN | not-applicable
Independent verification: <commands + result>
```

只有代码正确、传播完整、测试层选择合理、可复现 bug 的回归证据成立，才允许进入 `CODE_VERIFIED`，然后再执行 Knowledge Closeout。