# Example — Feature Development with Pi Harness

场景：给现有 API 增加一个可选 `currency` 过滤条件，并同步必要测试和文档。

---

## 1. Codex 建立 Baseline

```bash
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

记录用户已有改动，不能为了给 Worker 清理工作区而回滚。

状态：

```text
INIT → BASELINED
```

---

## 2. Harness Preflight

Codex 调用 Harness doctor，确认：

```text
repo_root correct
Pi/Harness compatible
persistent session available
Provider installed/auth usable
selected model tool-capable
mode/tool policy loaded
```

状态：

```text
BASELINED → HARNESS_PREFLIGHT → HARNESS_READY
```

---

## 3. Task Contract

```text
Goal
- GET /orders 支持可选 currency query parameter。

Scope
- orders controller/service/repository query path
- related DTO/validation if required
- directly affected tests/docs
- unrelated billing refactor is out-of-scope

Constraints
- currency omitted 时保持现有行为
- invalid currency 按项目现有 validation pattern 返回
- 不改变 auth/pagination semantics

Acceptance Criteria
- valid currency filters results
- omitted currency preserves old behavior
- invalid value follows current contract

Completeness
- search all order query callers
- check DTO/validator/serializer
- check repository query and existing fixtures
- check sibling export/order-search paths only if they consume same changed contract

Test Strategy
- Unit: required
- Integration: required if repository query contract crosses real DB adapter
- E2E: not-applicable if no user-facing cross-process flow is changed

Regression Proof
- not-applicable: feature, not bugfix

Execution Policy
- mode=implement
- no push/merge/deploy
- no unrelated dependency upgrade

Verification
- targeted tests
- repository lint/typecheck/build as applicable
```

---

## 4. Pi Implement Operation

Codex 发 Task Contract 给同一 Pi Harness：

```text
run_id = R-...
operation_id = OP-001
mode = implement
```

Pi Harness：

- `before_agent_start` 注入 contract/mode/scope；
- 只暴露该 mode 允许的 tools；
- `tool_call` 再做 path/command guard；
- Provider 只负责产生 model reasoning/tool calls；
- operation settle 后生成 Evidence Bundle。

状态：

```text
HARNESS_READY
→ OPERATION_SENT
→ EXECUTING
→ OPERATION_SETTLED
```

---

## 5. Evidence Bundle

示例：

```text
run_id: R-123
operation_id: OP-001
mode: implement
provider: antigravity
model: <actual model>
status: settled
changed_paths:
  - src/orders/...
  - test/orders/...
commands:
  - targeted test ... PASS
policy_blocks: none
unresolved: none
```

Codex 不因为这个 bundle 就 PASS。

---

## 6. Codex Diff Review

Codex 自己：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

发现实现逻辑正确，未破坏 baseline，进入：

```text
REVIEWING → COMPLETENESS_REVIEW
```

---

## 7. Completeness Review

Codex 搜索：

```bash
rg "currency" src test docs
rg "findOrders|listOrders" .
```

检查：

```text
controller
→ service
→ repository
→ validator
→ serializer/DTO
→ direct/indirect callers
→ tests
```

如果发现一个 export script 也使用被改动的 shared query contract：

- 若不更新会直接坏 → `unfinished`，必须 rework；
- 若它使用独立 contract、此次变化对它无影响 → `not-applicable`。

假设所有必然传播面已覆盖：

```text
Completeness Sweep: PASS
```

---

## 8. Codex Independent Verification

根据 Test Strategy 独立执行：

```text
unit tests
integration tests if required
lint/typecheck/build
```

全部通过：

```text
VERIFYING → CODE_VERIFIED
```

---

## 9. Knowledge Closeout

因为 public API query contract 变化，升级为 Full Closeout。

Codex 创建：

```text
operation_id = OP-002
mode = closeout
```

Closeout Contract 要求 Pi：

- 更新权威 API/README 示例；
- 搜旧 request 示例；
- 不修改无关文档；
- 不把开发过程写进 rules。

Pi settle 后 Codex 再 Review diff 和 stale references。

状态：

```text
CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

最终结果必须同时说明：

```text
Implementation
Completeness evidence
Test layer decisions
Independent verification
Knowledge surfaces
Harness/provider runtime identity
Residual risk
```
