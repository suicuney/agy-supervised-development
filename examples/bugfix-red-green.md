# Example — Bugfix RED → GREEN with AGY Supervised Development 3.3

场景：CacheService 在空 key 时仍访问 backend，导致异常；现有 contract 要求空 key 返回 empty result。

## 1. Compact Task Contract

这是一个 Small、确定性 Bug：

```text
Goal
- 修复 empty/null key 导致的 backend access。

Scope
- CacheService 相关实现与测试。

Acceptance Criteria
- null/blank key 返回 empty result。
- 不访问 cache backend。
- 正常 key 行为不变。

Regression Proof
- required: 同一 regression test 必须经历 RED → GREEN。
```

Small 任务保持紧凑。Sol High 默认只在 PLAN FROZEN 前评审计划。

## 2. PLAN FROZEN / BASELINE

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

存在用户已有改动时保存 baseline evidence，不清理工作区。

## 3. Herdr 启动 AGY 并建立 RED Evidence

```bash
scripts/check-herdr.sh

created="$(herdr workspace create \
  --cwd "$repo_root" \
  --label "agy-cache-red-green" \
  --no-focus)"
pane_id="$(printf '%s' "$created" | jq -r '.result.root_pane.pane_id')"
agy_agent="agy-cache-red-green"

herdr agent start "$agy_agent" --kind agy --pane "$pane_id"
```

发送一个 bounded Execution Unit，明确先证明 RED 再改 production code：

```bash
execution_unit='First add a regression test for null/blank keys returning empty without backend access. Prove the unfixed behavior is RED, then fix the root cause and rerun the same test. Preserve normal-key behavior.'

herdr agent prompt "$agy_agent" "$execution_unit" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout 1800000
```

若 blocked，先 read 后判断：

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 120
```

目标 regression test：

```bash
./mvnw -Dtest=CacheServiceTest test
```

必须观察到 unfixed behavior 因目标缺陷而失败，而不是环境原因。

## 4. Root Cause + GREEN

AGY 修复 root cause 后重跑同一测试，形成：

```text
Before fix: FAIL
After fix: PASS
```

Herdr `done` 只表示 Writer lifecycle settled；Codex 仍必须读取 Git。

## 5. Codex Three-Axis Review

```bash
git diff --check
git diff
git status --short
rg "CacheService|cache\.get|cache\.put" src test
```

确认：

```text
Spec Fidelity
- 空 key contract 和正常 key 行为都满足。

Engineering Quality
- 修复的是 root cause，不是吞异常。

Completeness
- sibling method/caller 没有遗漏。

Regression
- 同一 proof 确实经历 RED → GREEN。
```

若发现 finding，向同一 Herdr-managed AGY 发送完整 Rework Contract：

```bash
herdr agent prompt "$agy_agent" "$rework_contract" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout 1800000
```

返工后重新执行完整三轴 Review。

## 6. Codex Independent Verification

Codex 独立重跑：

```bash
./mvnw -Dtest=CacheServiceTest test
```

最终证据至少满足：

```text
Original repro before: RED
Minimal regression: RED
After fix: GREEN
Original repro after: GREEN
Codex re-run: PASS
Completeness Review: PASS
```

只有必要验证全部通过，才能进入 `CODE_VERIFIED`。

## 7. Knowledge Closeout

纯内部 bugfix 且知识面均 current 时，Closeout 可以是零文档 diff。Codex 完成 Closeout 后才可 `ACCEPTED`。
