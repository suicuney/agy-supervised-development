# Three-Axis Review Report Template

本模板用于 AGY 完成一个 Execution Unit 后，由 Codex 独立 Review repository state。

核心规则：

> **三个轴独立判断，最后才汇总。一个轴的优秀不能抵消另一个轴的失败。**

```text
Review Report

Execution Unit
- ID / Name: <...>
- Spec: <source>
- Baseline: <base_head / branch>
- AGY Conversation: <real id | none>
- Review Cycle: <n>

Repository Evidence
- git status --short: <summary>
- git diff --stat: <summary>
- git diff --check: PASS | FAIL
- Runtime anomalies: <none | permission block | partial run | ...>

==================================================
A. SPEC FIDELITY — 做对了吗？
==================================================

Verdict: PASS | REWORK | BLOCKED

Acceptance Coverage
- AC-1: PASS | REWORK | BLOCKED
  Evidence: <observable implementation/test/contract evidence>
- AC-2: ...

Findings
- S1 <severity>: <finding>
  Evidence: <spec clause + code/diff/runtime evidence>
  Expected: <required semantics>

Check explicitly
- missing requirement
- partial implementation
- wrong semantics
- scope creep / speculative feature
- unauthorized product/architecture decision
- verification seam mismatch

==================================================
B. ENGINEERING QUALITY — 写得好吗？
==================================================

Verdict: PASS | REWORK | BLOCKED

Findings
- Q1 <severity>: <finding>
  Evidence: <file/hunk/test/architecture evidence>
  Risk: <why this matters>
  Expected: <quality target>

Check by relevance
- architecture/module responsibility
- contract/data consistency
- error handling/observability
- transaction/concurrency/idempotency/retry
- authorization/security boundary
- backward compatibility
- unnecessary abstraction / speculative generality
- duplication / shotgun surgery / feature envy / data clumps
- test quality and implementation coupling

Do not spend LLM review budget repeating issues already deterministically enforced by formatter/linter/compiler unless they reveal a deeper design problem.

==================================================
C. COMPLETENESS — 漏了吗？
==================================================

Verdict: PASS | REWORK | BLOCKED

Changed Surface
- <symbol / route / schema / behavior>

Blast-Radius Evidence
- <rg/search/call-chain/producer-consumer/schema evidence>

Propagation Surfaces Checked
- direct callers
- indirect callers / re-exports / scripts
- DTO/types/enums/validation/serialization
- schema/migration/existing data
- sibling flows/jobs
- reachable error/empty/permission/retry/fallback
- cache/derived state/stale IDs
- old/orphaned path
- tests
- knowledge impact

Remainders
- C1: <remainder>
  Disposition: fixed-in-run | not-applicable | out-of-scope-different-ticket | blocked-decision-needed

==================================================
OVERALL
==================================================

Spec Fidelity:       PASS | REWORK | BLOCKED
Engineering Quality: PASS | REWORK | BLOCKED
Completeness:        PASS | REWORK | BLOCKED

Overall: PASS | REWORK_REQUIRED | BLOCKED

Blocking Findings
- <S/Q/C ids>

Next Action
- PASS → Codex Independent Verification
- REWORK_REQUIRED → build Rework Contract from concrete finding IDs/evidence
- BLOCKED → preserve repository state and surface the decision/environment blocker
```

## 汇总规则

```text
all three PASS                → REVIEW PASS
any axis REWORK               → REWORK_REQUIRED
any unresolved blocking axis  → BLOCKED
```

不要把三个轴合成一个“整体感觉不错”的分数，也不要用多数投票。

## Context Isolation

如果当前 Codex 环境支持独立子任务/并行 reviewer，可以让三个轴独立读取同一 fixed diff 与各自必要上下文，再由主 Codex 汇总。

如果不支持并行，也必须按 A → B → C 分别形成 verdict 后再汇总，避免 Quality 的正面印象掩盖 Spec/Completeness 缺陷。