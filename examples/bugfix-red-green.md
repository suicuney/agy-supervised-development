# Example — Bugfix RED → GREEN with Pi Harness

场景：`CacheService` 在空 key 时仍访问 backend，导致异常；现有 contract 要求空 key 返回 empty result。

---

## 1. Task Contract

Codex 先定义：

```text
Goal
- 修复 empty/null key 导致的 backend access。

Scope
- CacheService 相关实现与测试。

Acceptance Criteria
- null/blank key 返回 empty result。
- 不访问 cache backend。
- 正常 key 行为不变。

Completeness
- 搜索同类 cache entry points / sibling methods 是否共享同一缺陷。
- 不顺手重构整个缓存模块。

Test Strategy
- Unit: required
- Integration: not-applicable
- E2E: not-applicable

Regression Proof
- required：该 bug 可确定性、无外部副作用自动复现。

Execution Policy
- mode=implement
- no push/merge/deploy
```

---

## 2. Pi Worker 先建立 RED evidence

Codex 发 `implement` operation，但 Contract 明确要求：**先写 regression test，再改 production code**。

```text
run_id = R-...
operation_id = OP-001
mode = implement
```

测试目标：

```text
null key returns empty and never calls backend
blank key returns empty and never calls backend
```

运行：

```bash
./mvnw -Dtest=CacheServiceTest test
```

必须观察到 unfixed behavior 因目标缺陷而失败：

```text
Regression proof
- Test: CacheServiceTest#nullKeyReturnsEmptyWithoutBackend
- Before fix: FAIL
- Evidence: backend interaction observed / expected empty result mismatch
```

如果测试一开始就是 GREEN，说明测试没有捕获原 bug，不能算 regression proof。

---

## 3. Pi Worker 修 Root Cause

RED 成立后，Worker 修改 production code，并在 Evidence Bundle 中说明：

```text
Symptom
- null/blank key causes backend access

Root cause
- public service entry lacks the empty-key guard used by sibling operation

Same cause elsewhere
- searched sibling cache methods; no other exposed path lacks the guard

Regression boundary
- null + blank + normal key
```

只在 caller/UI 层拦 null，而 service 仍可被其他入口触发，不算 root-cause fix。

---

## 4. GREEN

Pi Worker 运行同一测试：

```bash
./mvnw -Dtest=CacheServiceTest test
```

Evidence：

```text
Before fix: FAIL
After fix: PASS
```

operation settle 后，状态只能到：

```text
OPERATION_SETTLED
```

不能直接 `CODE_VERIFIED`。

---

## 5. Codex Diff + Completeness Review

Codex 自己检查：

```bash
git diff --check
git diff
git status --short
rg "CacheService|cache\.get|cache\.put" src test
```

确认：

- 所有 public caller 是否可能传空 key；
- sibling method 是否缺少同类 guard；
- error/fallback path 是否仍访问 backend；
- 没有新增 dead workaround；
- 正常 key 行为仍有测试。

示例：

```text
Completeness Sweep: PASS
Remainders: none
```

---

## 6. Codex Independent Verification

Codex 自己重跑：

```bash
./mvnw -Dtest=CacheServiceTest test
```

最终代码证据：

```text
Unit: required → PASS
Integration: not-applicable
E2E: not-applicable
Regression proof: RED → GREEN
Codex re-run: PASS
Completeness Sweep: PASS
```

只有这些成立才进入：

```text
VERIFYING → CODE_VERIFIED
```

---

## 7. Knowledge Closeout

这是纯内部 bugfix，假设 README/public API/config 均未受影响：

```text
README              verified-current
AGENTS / CLAUDE     verified-current
API Contract        not-applicable
Runtime Config      not-applicable
Residue             verified-current
```

不需要为了制造 closeout diff 再启动写文档 operation。

Codex 完成 Closeout Review 后才：

```text
ACCEPTED
```
