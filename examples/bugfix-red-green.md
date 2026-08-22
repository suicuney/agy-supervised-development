# Example — Bugfix RED → GREEN with Pi Native Harness (v3.0.1)

场景：`CacheService` 在空 key 时仍访问 backend，导致异常；现有 contract 要求空 key 返回 empty result。

---

## 1. Task Contract

Codex先定义：

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
- no push/merge/deploy
```

---

## 2. 启动 Pi Session

如果 `pi-agent-modes` 已安装并验证：

```bash
pi --mode json --modes build --name "agy:cache-null-key" "<Task Contract>"
```

否则：

```bash
pi --mode json --name "agy:cache-null-key" "<Task Contract>"
```

Codex从 session header 保存真实 `pi_session_id` 和 `cwd`，确认 `cwd == repo_root`。

Task Contract 明确要求：**先写 regression test，再改 production code。**

---

## 3. 先建立 RED Evidence

测试目标：

```text
null key returns empty and never calls backend
blank key returns empty and never calls backend
```

Pi运行：

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

如果测试一开始就是 GREEN，说明它没有捕获原 bug，不能算 regression proof。

---

## 4. 修 Root Cause + GREEN

RED 成立后，Pi修改 production code，并说明：

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

然后运行同一测试：

```bash
./mvnw -Dtest=CacheServiceTest test
```

得到：

```text
Before fix: FAIL
After fix: PASS
```

Pi JSON `agent_end` / 正常进程退出只说明本次 turn 返回，不是 `CODE_VERIFIED`。

---

## 5. Codex Diff + Completeness Review

Codex自己：

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

如果发现漏改，Codex形成完整 Rework Contract，并 resume 同一 session：

```bash
pi --mode json --session <pi-session> --modes debug "<Rework Contract>"
```

`debug` 不可用时使用已验证 writable mode 或省略 `--modes`，但不要虚构 enforcement。

---

## 6. Codex Independent Verification

Codex独立重跑：

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

只有这些成立才：

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

不需要为了制造 closeout diff 再调用 Pi 写文档。

Codex完成 Closeout Review 后：

```text
ACCEPTED
```
