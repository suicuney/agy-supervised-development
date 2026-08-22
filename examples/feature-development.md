# Example — Feature Development with Pi Native Harness (v3.0.1)

场景：给现有 API 增加一个可选 `currency` 过滤条件，并同步必要测试和文档。

---

## 1. Codex 建立 Baseline

```bash
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

记录用户已有改动，不能为了给 Pi 清理工作区而回滚。

```text
INIT → BASELINED
```

---

## 2. Pi Native Preflight

Codex确认：

```bash
command -v pi
pi --version
pi --help
```

并确认：

```text
--mode json available
session resume available
Provider/auth usable
selected model tool-capable
workflow extension status known
repo cwd correct
```

如果已安装并验证 `pi-agent-modes`，本例实现阶段使用：

```text
build
```

否则省略 `--modes`，并明确不声称程序化 mode enforcement。

```text
BASELINED → PI_READY
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
- 不 push/merge/deploy

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

Verification
- targeted tests
- repository lint/typecheck/build as applicable
```

---

## 4. Codex 调 Pi 实现

在 repo root：

```bash
pi --mode json --modes build --name "agy:orders-currency" "<Task Contract>"
```

如果 `pi-agent-modes` 不可用：

```bash
pi --mode json --name "agy:orders-currency" "<Task Contract>"
```

Codex读取 JSON session header，保存真实：

```text
pi_session_id = <Pi returned id>
pi_session_cwd = <Pi returned cwd>
```

必须满足：

```text
pi_session_cwd == repo_root
```

状态：

```text
PI_READY → IMPLEMENTING
```

Pi stream 出现当前 invocation 的 `agent_end` 或进程正常退出，只表示实现 turn 返回。

---

## 5. Codex Diff Review

Codex自己：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

假设实现逻辑正确、未破坏 baseline：

```text
IMPLEMENTING → REVIEWING → COMPLETENESS_REVIEW
```

Pi summary 不是 PASS 依据。

---

## 6. Completeness Review

Codex搜索：

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

如果发现 export script 也使用被改的 shared query contract：

- 不更新会直接坏 → `unfinished`；
- 独立 contract、不受影响 → `not-applicable`。

若是 unfinished，Codex形成 Rework Contract：

```text
Issue
- export script still uses old shared query contract

Evidence
- <search/call evidence>

Expected
- caller follows new optional currency contract

Required change
- update only proven propagation path and tests

Re-run
- <target command>
```

然后 resume 同一真实 Pi session：

```bash
pi --mode json --session <pi-session> --modes build "<Rework Contract>"
```

返工后重新 Review。

最终：

```text
Completeness Sweep: PASS
```

---

## 7. Codex Independent Verification

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

## 8. Knowledge Closeout

因为 public API query contract 变化，升级为 Full Closeout。

Codex先做 Knowledge Impact Scan，然后生成 Closeout Contract：

```text
Goal
- update only authority docs/examples affected by final verified currency contract

Source of Truth
- final diff + verified tests + completeness evidence

Required
- update API/README example
- search stale request examples
- keep rules concise

Forbidden
- unrelated production code changes
- unrelated documentation rewrite
- push/merge/deploy
```

需要修改时继续同一 Pi session：

```bash
pi --mode json --session <pi-session> --modes build "<Closeout Contract>"
```

Pi turn 返回后 Codex 再检查：

```bash
git diff --check
git diff
git status --short
rg "<old-request-shape>" .
```

最后：

```text
CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

最终结果说明：

```text
Pi session identity
Provider/model if observable
Workflow mode if used
Implementation
Completeness evidence
Test layer decisions
Independent verification
Knowledge surfaces
Residual risk
```
