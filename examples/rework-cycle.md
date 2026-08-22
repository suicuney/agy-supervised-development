# Example: Review → Rework → Re-review（v2.1.2）

这个例子展示如何避免“AGY 说修好了，Codex 就结束”，以及为什么普通 Diff Review PASS 后还要进入 Completeness Review。

## 初始状态

```text
Supervisor State = REVIEWING
Turn = 2
Rework count = 0
```

Codex Review 发现：新增缓存逻辑没有处理 key 为空的场景，并且测试只覆盖 happy path。

## 1. 形成 Evidence

```text
Issue
- CacheService.java:87 在 key 为空时仍调用 map.get(key)。

Evidence
- 当前 diff 没有 empty/null guard。
- CacheServiceTest 只有正常 key 场景。

Expected
- 空 key 按现有 service contract 返回 empty result，不访问缓存 backend。

Rework
- 按现有参数校验模式增加 guard。
- 如果 bug 可确定性复现，先建立 RED regression proof，再修 production code。
- 增加 null/blank regression tests。

Re-run
- ./mvnw -Dtest=CacheServiceTest test
```

Review 结论：`REWORK`。

## 2. Read Before Send

```bash
tty7 capture "$PANE" --plain
```

确认 AGY 已结束上一 turn、当前界面可接收输入。permission/menu/error 要先处理，不能把返工 prompt 直接打进去。

## 3. 新 Rework Turn

生成新 nonce：

```text
D4B821
```

发送 Evidence，并要求：

```text
只处理上述 blocking issue 和它必然产生的 completeness remainder，不做无关重构。
完成本轮后输出：
TURN_COMPLETE: D4B821
```

更新：

```text
Supervisor State = TURN_SENT → OBSERVING
Turn = 3
Rework count = 1
```

## 4. 观察

Native status：

```bash
tty7 wait "$PANE" --until waiting,done --changed --timeout 1800
```

Fallback：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

看到当前 nonce 后：

```text
Supervisor State = TURN_RETURNED
```

旧 nonce 不算。

## 5. Re-review

Codex 不接受 AGY 的“已修复”描述，重新检查：

```bash
git diff --check
git diff
git status --short
```

### 情况 A：Diff Review 通过

不是直接 `VERIFYING`，而是：

```text
PASS
→ COMPLETENESS_REVIEW
```

Codex 继续搜索：

```bash
rg "CacheService|cache\.get|cache\.put" src test
```

确认 sibling method / caller 没有相同 root cause，tests 覆盖 regression boundary。

Completeness PASS 后才进入：

```text
VERIFYING
```

### 情况 B：同一问题仍存在

再次形成 Evidence，`rework_count=2`，新 nonce，新 Turn。

### 情况 C：修 A 坏 B

记录新问题，同时检查是否开始 repair oscillation。

### 情况 D：当前 fix 正确，但同根因在 sibling site 仍存在

这是 Completeness REWORK：

```text
COMPLETENESS_REVIEW
→ REWORK_REQUIRED
```

不能因为原文件的 targeted test 已绿就继续 Verification。

## 6. Regression Proof

如果该 bug 可安全、确定性自动复现：

```text
Before fix: regression test RED
After fix: same test GREEN
Codex re-run: PASS
```

如果无法安全/稳定复现，明确：

```text
Regression proof: not-applicable
Reason: ...
Alternative evidence: ...
```

不要把“修完后才写的 green test”包装成 RED→GREEN。

## 7. Soft Limit

如果已经完成三轮：

```text
Review → Rework → Re-review
```

仍有 blocking issue，不直接继续第四轮。

重新评估：

- Task Contract 是否不清；
- Codex 根因判断是否错；
- Completeness 边界是否错；
- AGY 是否反复修坏别处；
- 是否环境/测试问题；
- 是否触发 one-way decision。

必要时：

```text
BLOCKED
- 当前安全 repository state
- 已发生 3 轮返工
- 仍未解决的问题
- 需要用户决定的下一步
```

这样避免 Supervisor 和 Implementer 无限互修。