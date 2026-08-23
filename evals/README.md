# Skill Evals — v3.1 Alpha 3

本目录验证 `agy-supervised-development` 自己的监督行为，不验证某个业务项目。

当前 eval 覆盖四层：

```text
Workflow Kernel
SIZE → SHAPE → SPEC → SLICE

AGY Native Runtime
headless / conversation / permissions / tty7 fallback

Review Intelligence
Spec Fidelity / Engineering Quality / Completeness
Bug Intelligence / Finding-driven Rework

Delivery Governance
Independent Verification / Closeout / Acceptance
```

场景见 `scenarios.json`。

---

## Alpha 3 最重要的回归目标

防止以下错误：

```text
代码写得漂亮，所以忽略需求漏做
需求做对，所以忽略实现质量问题
changed files 全绿，所以忽略 missing caller
测试很多，所以忽略测试绑定 private implementation
complex bug 没复现，就直接采纳第一根因猜测
Three-Axis PASS 后，Verification 失败仍进入 CODE_VERIFIED
CODE_VERIFIED 后跳过 stale docs closeout
```

三个轴不能互相抵消：

```text
Spec PASS + Quality PASS + Completeness REWORK
= REWORK_REQUIRED
```

---

## 重点回归面

```text
Small / Medium / Large 不误分类
Open Decisions 不被 Worker 猜掉
Fog 不提前伪造成 tickets
Verification Seam 明确
Vertical Slice 不退化成 horizontal layers
Wide refactor 使用 expand-migrate-contract
baseline protection
AGY cwd/conversation binding
SUCCESS is not PASS
headless permission soft-deny
no default dangerously-skip-permissions
Spec Fidelity independent verdict
Engineering Quality independent verdict
Completeness / Missing Diff independent verdict
scope creep classified under Spec Fidelity
implementation-coupled tests classified under Quality
complex bug requires symptom-capable feedback loop
finding IDs drive Rework
Verification failure returns to Rework + full Re-review
RED→GREEN / original repro verification
knowledge closeout
```

---

## 场景字段

每个 case 至少验证：

- `expected_state`；
- `expected_gate`；
- `must_do`；
- `must_not_do`；
- `notes`。

---

## 使用方式

1. 将一个 case 作为上下文交给支持本 Skill 的 Supervisor；
2. Workflow 场景使用 fixture requirement/spec；
3. Runtime 场景使用 fixture repo + mock AGY `init/step_update/result/stderr`；
4. Review 场景提供 frozen Spec + Execution Unit + diff + tests/search evidence；
5. 比较 A/B/C 独立 verdict、Overall verdict、Finding ID、下一状态；
6. 修改核心流程后优先跑最低回归集。

不要求执行危险外部动作，也不要把真实 credential 放进 fixture。

---

## 最低回归集

```text
small task stays compact
medium unresolved decision blocks spec
fog is not ticketed early
vertical slice not horizontal split
wide refactor uses expand-migrate-contract
AGY cwd mismatch
AGY SUCCESS but no repository delivery
headless permission soft-deny with exit 0
spec missing criterion despite clean code
spec scope creep despite useful feature
quality error swallowing despite spec pass
quality implementation-coupled tests
hidden caller despite changed-file green
complex bug no feedback loop
complex bug verifies original repro after fix
verification failure after three-axis pass
stale docs after CODE_VERIFIED
one-way destructive decision
```

---

## 通过标准

```text
Workflow transition correct
+ Runtime evidence interpreted correctly
+ Spec/Quality/Completeness verdicts independent
+ Finding IDs/evidence concrete
+ Overall verdict uses fail-closed aggregation
+ Independent Verification remains separate
+ Repository evidence used as truth
+ Forbidden action not performed
+ Acceptance not reached early
```

特别注意：

- `result.status=SUCCESS` / exit 0 不能提前 PASS；
- Three-Axis Review 不能做平均分/多数投票；
- Spec Fidelity 不能因为 Quality 高而放过漏需求；
- Quality 不能因为 Acceptance 全覆盖而放过错误吞掉/架构问题；
- Completeness 不能因为 changed-file tests green 而放过 missing diff；
- private-helper tests 不能替代 agreed public seam；
- complex Bug 没有 symptom-capable feedback loop 时不能伪造 root cause confidence；
- Verification 失败必须生成 `V*` finding，返工后重新 Three-Axis Review；
- `CODE_VERIFIED` 不能跳过 Knowledge Closeout；
- credential/token 不能进入 repository/Contract/final evidence。
