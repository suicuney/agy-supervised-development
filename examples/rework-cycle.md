# Example — Review → Rework → Re-review with AGY (v3.2)

这个例子展示如何避免“Worker 说修好了就结束”，以及为什么普通 Diff Review PASS 后仍要完成 Completeness Review。

---

## 初始状态

~~~text
Supervisor State = REVIEWING
AGY Conversation = <real conversation_id>
Rework count = 0
~~~

Codex Review 发现：新增缓存逻辑没有处理 key 为空的场景，测试只覆盖 happy path。

---

## 1. 形成 Evidence-driven Rework Contract

~~~text
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
~~~

Review 结论：

~~~text
REWORK_REQUIRED
~~~

---

## 2. Resume 同一 AGY Conversation

Codex 不启动第二个并行 Writer，而是优先恢复真实 conversation：

~~~bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --conversation "$agy_conversation_id" \
  --timeout 30m \
  "<Rework Contract>"
~~~

Conversation history 只提供上下文；Rework Contract 仍必须包含完整的 Issue、Evidence、Expected、Required Change、Re-run 和 Scope Reminder。

如果真实 conversation_id 丢失，不猜测其他会话；新开会话时重新提供冻结的 Spec、Execution Unit、当前 repository state、diff、finding 和验证状态。

---

## 3. AGY Turn 返回

AGY 的 stream-json 关键事件是：

~~~text
init
step_update *
result
~~~

需要区分：

~~~text
result.status = SUCCESS
- 只表示本次 Writer turn 返回。
- 不等于 Review PASS。
- 不等于 CODE_VERIFIED。
~~~

如果 AGY 在已经执行编辑后因为 CLI、权限或其他运行时错误退出：

1. 先检查 Git 是否已有部分写入；
2. 保存错误和 permission evidence；
3. 不自动 replay 可能产生重复副作用的 Execution Unit；
4. 能安全恢复时继续使用真实 conversation_id；
5. 否则带着当前 repository evidence 新开会话。

---

## 4. Re-review

Codex 重新读取 repository：

~~~bash
git diff --check
git diff
git status --short
~~~

然后按当前三轴重新审查：

~~~text
A. Spec Fidelity
B. Engineering Quality
C. Completeness
~~~

### 情况 A：三轴都通过

继续检查：

~~~bash
rg "CacheService|cache\.get|cache\.put" src test
~~~

确认 sibling method/caller 没有相同 root cause，tests 覆盖 regression boundary，随后进入 Independent Verification。

### 情况 B：同一问题仍存在

形成新的、证据完整的 Rework Contract：

~~~text
rework_count = 2
~~~

继续恢复同一个真实 AGY conversation，并在返工后重新跑完整三轴 Review。

### 情况 C：修 A 坏 B

记录新的 evidence，按新的 S*/Q*/C*/V* finding 处理；不能因为原来的 finding 已解决就直接通过。

### 情况 D：当前 fix 正确，但 sibling site 仍有同一 root cause

这是 Completeness REWORK：

~~~text
COMPLETENESS_REVIEW
→ REWORK_REQUIRED
~~~

不能因为 targeted test 已绿就跳过传播面检查。

---

## 5. RED → GREEN

若 Bug 可安全、确定性复现：

~~~text
Before fix: regression test RED
After fix: same test GREEN
Codex re-run: PASS
Original repro after fix: GREEN
~~~

若不适用：

~~~text
Regression proof: not-applicable
Reason: ...
Alternative evidence: ...
~~~

“修完以后补了一个 green test”不能包装成完整 RED → GREEN proof。

---

## 6. 运行时和恢复边界

~~~text
AGY headless permission denied
→ 记录真实 conversation_id 和 evidence
→ 仅在确实需要人工批准时使用窄范围 tty7 fallback
→ 回到 Git Review
~~~

不要使用全局权限绕过。无论 AGY 还是 tty7 如何结束，最终判断都回到：

~~~text
Git state
→ Three-Axis Review
→ Codex Independent Verification
→ Closeout
~~~

默认观察最多 3 个完整的：

~~~text
Review → Rework → Re-review
~~~

达到 soft limit 后重新评估 Spec、root cause、slice 粒度、权限、环境和测试；不要机械进入第四轮，也不要 push/merge/release/deploy。
