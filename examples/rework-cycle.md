# Example — Review → Rework → Re-review with Pi Native Session (v3.0.1)

这个例子展示如何避免“Pi 说修好了，Codex 就结束”，以及为什么普通 Diff Review PASS 后还要进入 Completeness Review。

---

## 初始状态

```text
Supervisor State = REVIEWING
Pi Session = <real session id>
Rework count = 0
```

Codex Review 发现：新增缓存逻辑没有处理 key 为空的场景，测试只覆盖 happy path。

---

## 1. 形成 Evidence-driven Rework Contract

```text
Issue
- CacheService.java:87 在 key 为空时仍访问 cache backend。

Evidence
- 当前 diff 没有 empty/null guard。
- CacheServiceTest 只有正常 key 场景。

Expected
- 空 key 按现有 service contract 返回 empty result，不访问 backend。

Required change
- 按项目现有 validation pattern 修 root cause。
- 若 bug 可确定性复现，先证明 regression test 在 unfixed behavior 上 RED。
- 增加 null/blank regression tests。

Re-run
- ./mvnw -Dtest=CacheServiceTest test

Scope reminder
- 只处理 blocking issue 和被证明为 unfinished 的 propagation path。
```

Review 结论：

```text
REWORK_REQUIRED
```

---

## 2. Resume 同一 Pi Session

Codex不启动第二个并行 Writer，而是 resume 真实 session。

若 `pi-agent-modes` 已验证：

```bash
pi --mode json --session <pi-session> --modes debug "<Rework Contract>"
```

普通结构性返工也可以：

```bash
pi --mode json --session <pi-session> --modes build "<Rework Contract>"
```

没有 mode extension 时：

```bash
pi --mode json --session <pi-session> "<Rework Contract>"
```

此时必须明确 `mode_enforcement = unavailable/prompt-only`，不能虚构 Tool Guard。

Pi session history 可以帮助理解上下文，但 Rework Contract 仍带完整 Issue/Evidence/Expected。

```text
REWORK_REQUIRED → REWORKING
```

---

## 3. Pi Turn 返回

JSON stream 出现当前 invocation 的 `agent_end`，或 Pi 正常退出，只表示：

```text
Pi turn returned
```

不是 `PASS`，也不需要创建 `operation_id` / `OPERATION_SETTLED`。

Codex立即回到：

```text
REWORKING → REVIEWING
```

---

## 4. Re-review

Codex重新读取 repository：

```bash
git diff --check
git diff
git status --short
```

### 情况 A：Diff Review 通过

进入：

```text
REVIEWING → COMPLETENESS_REVIEW
```

继续搜索：

```bash
rg "CacheService|cache\.get|cache\.put" src test
```

确认 sibling method/caller 没有相同 root cause，tests 覆盖 regression boundary。

Completeness PASS 后：

```text
VERIFYING
```

### 情况 B：同一问题仍存在

形成新 Rework Contract：

```text
rework_count = 2
```

继续同一真实 Pi session。

### 情况 C：修 A 坏 B

记录新 evidence，并判断是否出现 repair oscillation。

### 情况 D：当前 fix 正确，但同一 root cause 在 sibling site 仍存在

这是 Completeness REWORK：

```text
COMPLETENESS_REVIEW
→ REWORK_REQUIRED
```

不能因为原 targeted test 已绿继续 Verification。

---

## 5. RED → GREEN

若 bug 可安全、确定性复现：

```text
Before fix: regression test RED
After fix: same test GREEN
Codex re-run: PASS
```

若不适用：

```text
Regression proof: not-applicable
Reason: ...
Alternative evidence: ...
```

“修完以后补了一个 green test”不能包装成完整 RED→GREEN proof。

---

## 6. Extension Policy 的正确表述

如果本轮用了真实 `pi-agent-modes debug/build`，可以记录实际 workflow mode。

如果没有安装 Extension：

```text
mode_enforcement = unavailable/prompt-only
```

不要说：

```text
"Harness blocked all out-of-scope tool calls"
```

除非当前实际 Extension/runtime evidence 能证明这一点。

无论如何，最终 Scope 判断仍由 Codex 基于 Git baseline/diff 做。

---

## 7. Soft Rework Limit

默认最多观察 3 个完整：

```text
Review → Rework → Re-review
```

达到 soft limit 后重新评估：

- Task Contract 是否有歧义；
- Codex root-cause 判断是否错误；
- completeness 边界是否错；
- Provider/model 是否不适合；
- mode extension 是否造成 false positive/限制；
- 是否环境/测试故障；
- 是否触发 one-way decision。

不要静默进入第四、第五轮，也不要切 `yolo` 绕过问题。

必要时：

```text
BLOCKED
- current safe repository state
- real Pi session identity
- rework cycles
- remaining blocking issues
- user decision needed
```
