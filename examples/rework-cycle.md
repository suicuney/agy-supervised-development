# Example — Review → Rework → Re-review with Pi Harness

这个例子展示如何避免“Pi Worker 说修好了，Codex 就结束”，以及为什么普通 Diff Review PASS 后还要进入 Completeness Review。

---

## 初始状态

```text
Supervisor State = REVIEWING
Run = R-123
Pi Session = S-456
Last Operation = OP-002
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
```

Review 结论：

```text
REWORK_REQUIRED
```

---

## 2. Resume 同一 Pi Run / Session

Codex 不启动第二个并行 Writer，而是：

```text
run_id = R-123
pi_session_id = S-456
operation_id = OP-003
mode = rework
```

Pi session history 可以帮助理解上下文，但 Rework Contract 仍带完整 Issue/Evidence/Expected，不依赖“记得上一轮”。

状态：

```text
REWORK_REQUIRED
→ OPERATION_SENT
→ EXECUTING
```

---

## 3. Harness Policy 继续生效

`rework` mode 仍必须：

- 只暴露当前允许工具；
- `tool_call` 再检查 path/command；
- 禁止 push/merge/deploy；
- 阻止与 blocking issue 无关的重构；
- 将被 block 的 tool call 写入 Evidence Bundle。

不能因为进入返工就临时切成全权限模式。

---

## 4. Operation Settled

Pi operation settle 后返回：

```text
run_id: R-123
operation_id: OP-003
status: settled
changed_paths: ...
tests: ...
policy_blocks: ...
worker_summary: ...
```

Codex 只把它当当前 operation 已返回：

```text
EXECUTING → OPERATION_SETTLED
```

不是 `PASS`。

---

## 5. Re-review

Codex 重新读取 repository：

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

Completeness PASS 后才：

```text
VERIFYING
```

### 情况 B：同一问题仍存在

形成新的 Evidence Contract：

```text
operation_id = OP-004
rework_count = 2
```

继续同一 Run/session。

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

## 6. RED → GREEN

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

## 7. Soft Rework Limit

默认最多观察 3 个完整：

```text
Review → Rework operation → Re-review
```

达到 soft limit 后重新评估：

- Task Contract 是否有歧义；
- Codex root-cause 判断是否错误；
- completeness 边界是否错；
- Provider/model 是否不适合；
- Harness Tool Guard 是否误杀正确实现；
- 是否环境/测试故障；
- 是否触发 one-way decision。

不要静默进入第四、第五轮，也不要直接切 YOLO。

必要时：

```text
BLOCKED
- 当前安全 repository state
- 已发生的 rework cycles
- remaining blocking issues
- provider/harness evidence
- user decision needed
```
