# Example: Bugfix RED → GREEN（v2.1.2）

场景：`CacheService` 在空 key 时仍访问 backend，导致异常；现有 contract 要求空 key 返回 empty result。

## 1. Task Contract

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
- 不把缓存模块顺手重构成新 abstraction。

Test Strategy
- Unit: required
- Integration: not-applicable
- E2E: not-applicable

Regression Proof
- required：该 bug 可确定性、无外部副作用地自动复现。
```

## 2. 先证明 Bug

要求 AGY **先写 regression test，不先改 production code**：

```text
Test
- null key returns empty and never calls backend
- blank key returns empty and never calls backend
```

运行：

```bash
./mvnw -Dtest=CacheServiceTest test
```

必须观察到 unfixed behavior 下测试因为预期缺陷而失败：

```text
Regression proof
- Test: CacheServiceTest#nullKeyReturnsEmptyWithoutBackend
- Before fix: FAIL
- Evidence: backend interaction observed / expected empty result mismatch
```

如果测试一开始就是 GREEN，说明它没有捕获原 bug：修正测试或重新确认复现，不允许把它直接算 regression proof。

## 3. 修 Root Cause

AGY 现在才能修改 production code。

Codex Review 要求说明：

```text
Symptom
- null/blank key causes backend access

Root cause
- public service entry lacks the same empty-key guard used by sibling operation

Same cause elsewhere
- searched sibling cache methods; no other exposed path lacks the guard

Regression boundary
- null + blank + normal key
```

只在 UI/调用方拦住 null，而 backend/service 仍可被其他 caller 触发，不算 root-cause fix。

## 4. GREEN

AGY 运行相同测试：

```bash
./mvnw -Dtest=CacheServiceTest test
```

记录：

```text
After fix: PASS
```

## 5. Completeness Sweep

Codex 搜索同类入口：

```bash
rg "CacheService|cache\.get|cache\.put" src test
```

确认：

- 所有 public caller 是否可能传空 key；
- sibling method 是否已有/缺少同类 guard；
- error/fallback path 是否仍访问 backend；
- 没有新增 dead workaround；
- 测试覆盖 normal behavior，避免 guard 误伤正常 key。

示例：

```text
Completeness Sweep: PASS
Remainders: none
```

## 6. Codex Independent Verification

Codex 自己重跑：

```bash
./mvnw -Dtest=CacheServiceTest test
```

并检查最终 diff：

```bash
git diff --check
git diff
git status --short
```

最终证据：

```text
Unit: required → PASS
Integration: not-applicable
E2E: not-applicable
Regression proof: RED → GREEN
Codex re-run: PASS
Completeness Sweep: PASS
```

只有这些成立才进入 `CODE_VERIFIED`。

## 7. Knowledge Closeout

这是纯内部 bugfix，假设 README / public API / config 都未受影响：

```text
README              verified-current
AGENTS / CLAUDE     verified-current
API Contract        not-applicable
Runtime Config      not-applicable
Residue             verified-current
```

零文档 diff 是正确结果。Gate 13 PASS 后才进入 `ACCEPTED`。