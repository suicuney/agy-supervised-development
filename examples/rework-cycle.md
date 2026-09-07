# Example — Review → Rework → Re-review with AGY Supervised Development 3.3

这个例子展示为什么 Worker/Runtime 说完成后仍必须回到 Git、Review 和 Verification。

## 初始状态

```text
Supervisor State = REVIEWING
Herdr Agent = <stable task-local AGY name>
Rework count = 0
```

Codex Review 发现：新增缓存逻辑没有处理 key 为空的场景，测试只覆盖 happy path。

## 1. Evidence-driven Rework Contract

```text
Issue
- CacheService.java:87 在 key 为空时仍访问 cache backend。

Evidence
- 当前 diff 没有 empty/null guard。
- CacheServiceTest 只有正常 key 场景。

Expected
- 空 key 按现有 service contract 返回 empty result，不访问 backend。

Required Change
- 按项目现有 validation pattern 修 root cause。
- 增加 null/blank regression tests。
- 如果问题可确定性复现，保留 RED → GREEN 证据。

Re-run
- ./mvnw -Dtest=CacheServiceTest test

Scope Reminder
- 只处理 blocking issue 和被证明为 unfinished 的 propagation path。
```

结论：`REWORK_REQUIRED`。

## 2. 继续同一个 Herdr-managed AGY

不启动第二个并行 Writer：

```bash
herdr agent prompt "$agy_agent" "$rework_contract" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout 1800000
```

如果 AGY blocked：

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 120
```

先读清楚请求，再按已有权限边界处理。

Herdr/Antigravity integration 负责 native session identity 和 server restart 后的 exact-session restore。若 exact session 不可恢复，不猜别的 conversation；保留 Git progress，并在安全时用新的 Herdr-managed AGY 显式重灌 frozen context。

## 3. AGY Runtime settled

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 160
```

需要区分：

```text
Herdr done / idle
- 表示 runtime settled。
- 不等于 Review PASS。
- 不等于 CODE_VERIFIED。
```

Runtime 报错或 server restart 后，也先检查 Git 是否已有部分写入，不自动 replay 可能产生重复副作用的 Execution Unit。

## 4. Re-review

Codex 重新读取 repository：

```bash
git diff --check
git diff
git status --short
```

重新按完整三轴审查：

```text
A. Spec Fidelity
B. Engineering Quality
C. Completeness
```

### 三轴都通过

进入 Independent Verification。

### 同一问题仍存在

形成新的证据完整 Rework Contract，继续同一个 Herdr AGY worker，然后再次完整 Review。

### 修 A 坏 B

记录新的 S*/Q*/C*/V* finding，不能因为旧 finding 消失就直接通过。

### sibling site 仍有同一 root cause

这是 Completeness REWORK，不能因 targeted test 已绿就跳过。

## 5. RED → GREEN

若 Bug 可安全、确定性复现：

```text
Before fix: regression test RED
After fix: same test GREEN
Codex re-run: PASS
Original repro after fix: GREEN
```

修完以后才补的 green test 不能包装成完整 RED → GREEN proof。

## 6. 最终边界

无论 Herdr/AGY 如何结束，最终判断都回到：

```text
Git state
→ Three-Axis Review
→ Codex Independent Verification
→ Closeout
→ ACCEPTED
```

Herdr 管运行，不管结论。
