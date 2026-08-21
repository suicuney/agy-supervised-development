# Example: Review → Rework → Re-review

这个例子专门展示 v2.1 如何避免“AGY 说修好了，Codex 就结束”的假闭环。

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
- 增加 null/blank regression tests。

Re-run
- ./mvnw -Dtest=CacheServiceTest test
```

Review 结论：`REWORK`。

## 2. Read Before Send

```bash
tty7 capture "$PANE" --plain
```

确认 AGY 已经结束上一 turn、当前界面可以接收输入。

如果是 permission/menu/error，先处理那个状态，不能把返工 prompt 直接打进去。

## 3. 新 Rework Turn

生成新 nonce：

```text
D4B821
```

发送上面的 Evidence，并加：

```text
只处理上述 blocking issue，不做无关重构。
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

如果 native status 可用：

```bash
tty7 wait "$PANE" --until waiting,done --changed --timeout 1800
```

如果没有 AGY status hook：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

看到当前 nonce 后：

```text
Supervisor State = TURN_RETURNED
```

注意旧的 `TURN_COMPLETE` 不算。

## 5. Re-review

Codex 不接受 AGY 的“已修复”描述，重新检查：

```bash
git diff --check
git diff
git status --short
```

并自己运行相关 test。

### 情况 A：通过

```text
PASS
→ VERIFYING
```

### 情况 B：同一问题仍存在

再次形成 Evidence，`rework_count=2`，新 nonce，新 Turn。

### 情况 C：修 A 坏 B

记录新问题，同时注意是否开始出现 repair oscillation。

## 6. Soft Limit

如果已经完成三轮：

```text
Review → Rework → Re-review
```

仍有 blocking issue，不直接继续第四轮。

先重新评估：

- Task Contract 是否不清；
- Codex 的根因判断是否错；
- AGY 是否反复修坏别处；
- 是否需要先让 AGY只分析根因；
- 是否是环境/测试问题。

必要时：

```text
BLOCKED
- 当前安全 repository state
- 已发生 3 轮返工
- 仍未解决的问题
- 需要用户决定的下一步
```

这样避免 Supervisor 和 Implementer 无限互相修。