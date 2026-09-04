# Example — Feature Development with AGY Supervised Development 3.3

场景：给现有 API 增加一个可选 currency 过滤条件，并同步必要测试和文档。

## 1. Codex 建立 Shape / Spec / Slice

这是一个 Medium 任务：

```text
Goal
- GET /orders 支持可选 currency query parameter。

Resolved Decisions
- currency 省略时保持现有行为。
- invalid currency 沿用项目已有 validation contract。
- auth 与 pagination semantics 不变。

Out of Scope
- unrelated billing refactor。
- 未被 Completeness 证明受影响的相邻功能。

Acceptance Criteria
- valid currency filters results。
- omitted currency preserves old behavior。
- invalid value follows the current contract。

Test Strategy
- Unit: required
- Integration: required if the repository query crosses a real DB adapter
- E2E: not-applicable if no browser-facing cross-process flow changes
```

默认 Sol High Plan Review 只审实现前的 Executable Plan：

```text
Codex Plan
→ Sol High Review
→ Codex Adopt / Reject / Modify
→ PLAN FROZEN
```

最多 3 轮；用户明确跳过时直接进入 PLAN FROZEN。冻结后不再调用 Sol High。

## 2. BASELINE

AGY 写入前记录：

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

如果已有用户改动，记录 baseline-owned paths；需要时保存原始 patch 指纹：

```bash
git diff --binary -- <baseline paths> | shasum -a 256
```

## 3. 通过 Herdr 启动唯一 AGY Writer

先做 runtime preflight：

```bash
scripts/check-herdr.sh
```

创建本任务专属 workspace，并只使用 Herdr 返回的 ID：

```bash
created="$(herdr workspace create \
  --cwd "$repo_root" \
  --label "agy-orders-currency" \
  --no-focus)"

workspace_id="$(printf '%s' "$created" | jq -r '.result.workspace.workspace_id')"
pane_id="$(printf '%s' "$created" | jq -r '.result.root_pane.pane_id')"
agy_agent="agy-orders-currency"
```

启动 AGY：

```bash
herdr agent start "$agy_agent" --kind agy --pane "$pane_id"
```

发送 Execution Unit：

```bash
execution_unit='Implement the optional currency filter for GET /orders. Preserve omitted-currency behavior, existing validation, auth and pagination. Update only the proven propagation path, tests and directly affected docs.'

herdr agent prompt "$agy_agent" "$execution_unit" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout 1800000
```

如果 `blocked`，先：

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 120
```

再决定是否做最小交互；one-way decision 仍回用户。

AGY settled 后读取 worker report：

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 160
```

`done` / `idle` 只表示 Runtime settled，不表示实现通过。

## 4. Codex Three-Axis Review

Codex 直接读取 Git：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

分别判断：

```text
A. Spec Fidelity
- currency 省略、有效值、无效值是否符合 contract。

B. Engineering Quality
- controller/service/repository/DTO 的职责和错误处理是否合理。

C. Completeness
- callers、validator、serializer、fixtures、sibling paths 和 docs 是否同步。
```

若发现漏改，形成 Evidence-driven Rework Contract，并发给同一个 Herdr AGY worker：

```bash
herdr agent prompt "$agy_agent" "$rework_contract" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout 1800000
```

返工后重新执行完整 Three-Axis Review。

## 5. Codex Independent Verification

只有 Review PASS 后才进入独立验证：

```bash
./mvnw -Dtest=OrdersTest test
./mvnw test
```

按项目实际情况补充 lint、typecheck、integration、build 或 E2E。全部必要验证通过后：

```text
REVIEW PASS → CODEX VERIFY → CODE_VERIFIED
```

## 6. Knowledge Closeout

由于 public API query contract 发生变化，扫描 README/API examples 等知识面。若需要 AGY 修改知识文件，继续向同一个 Herdr worker 发送 bounded Closeout Contract，然后 Codex 再次检查 Git。

最终：

```text
CODE_VERIFIED
→ CLOSEOUT
→ ACCEPTED
```

任务接受后，只有本流程自己创建的 workspace 才可以关闭：

```bash
herdr workspace close "$workspace_id"
```
