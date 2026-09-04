# Example — Bugfix RED → GREEN with AGY (v3.2)

场景：CacheService 在空 key 时仍访问 backend，导致异常；现有 contract 要求空 key 返回 empty result。

---

## 1. Compact Task Contract

这是一个 Small、确定性 Bug：

~~~text
Goal
- 修复 empty/null key 导致的 backend access。

Scope
- CacheService 相关实现与测试。

Acceptance Criteria
- null/blank key 返回 empty result。
- 不访问 cache backend。
- 正常 key 行为不变。

Completeness
- 搜索同类 cache entry points / sibling methods 是否共享同一缺陷。
- 不顺手重构整个缓存模块。

Test Strategy
- Unit: required
- Integration: not-applicable
- E2E: not-applicable

Regression Proof
- required：该 bug 可确定性、无外部副作用自动复现。

Execution Policy
- preserve baseline
- no push/merge/deploy
~~~

Small 任务可以保持 Shape/Spec 紧凑。Sol High 默认只评审 PLAN FROZEN 之前的计划；用户可以显式要求跳过该评审。

---

## 2. PLAN FROZEN / BASELINE

记录实现前的仓库事实：

~~~bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
~~~

如果存在用户已有改动，保存 baseline-owned paths 和原始 diff 指纹。不要清理或回滚这些改动。

---

## 3. AGY 建立 RED Evidence

把一个 bounded Execution Unit 交给 AGY，并明确先写 regression test，再改 production code：

~~~bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --timeout 30m \
  "Execution Unit: first add a regression test for null/blank keys returning
   empty without backend access, prove the unfixed behavior is RED, then fix
   the root cause and rerun the same test. Preserve normal-key behavior."
~~~

收到 stream-json 的 init 后保存真实 conversation_id，并验证：

~~~text
init.cwd == repo_root
~~~

首个实际命令还必须输出：

~~~bash
pwd
git -C "$repo_root" rev-parse --show-toplevel
git -C "$repo_root" branch --show-current
~~~

如果命令 cwd 不正确，停止相对路径写入。若写入或测试动作被 headless 权限阻止，记录 blocked/not-run；只有需要一次性人工批准时才使用窄范围 tty7 fallback，不使用全局权限绕过。

Regression test：

~~~bash
./mvnw -Dtest=CacheServiceTest test
~~~

必须观察到 unfixed behavior 因目标缺陷而失败：

~~~text
Regression proof
- Test: CacheServiceTest#nullKeyReturnsEmptyWithoutBackend
- Before fix: FAIL
- Evidence: backend interaction observed / expected empty result mismatch
~~~

如果测试一开始就是 GREEN，说明它没有捕获原始 Bug，不能算 regression proof。

---

## 4. Root Cause + GREEN

RED 成立后，AGY 修复 root cause，并说明：

~~~text
Symptom
- null/blank key causes backend access

Root cause
- public service entry lacks the empty-key guard used by the sibling operation

Same cause elsewhere
- searched sibling cache methods; no other exposed path lacks the guard

Regression boundary
- null + blank + normal key
~~~

然后运行同一测试：

~~~bash
./mvnw -Dtest=CacheServiceTest test
~~~

得到：

~~~text
Before fix: FAIL
After fix: PASS
~~~

result.status = SUCCESS 只说明 AGY Writer turn 返回；Codex 仍必须读取 Git 并独立 Review/Verify。

---

## 5. Codex Three-Axis Review

Codex 自己检查：

~~~bash
git diff --check
git diff
git status --short
rg "CacheService|cache\.get|cache\.put" src test
~~~

确认：

~~~text
Spec Fidelity
- 空 key contract 和正常 key 行为都满足。

Engineering Quality
- 修复的是 root cause，而不是吞异常或隐藏 backend failure。

Completeness
- public caller、sibling method、error/fallback path 没有遗漏。

Regression
- 同一测试确实经历了 RED → GREEN。
~~~

如发现漏改，形成带有 Issue/Evidence/Expected/Required Change/Re-run 的 Rework Contract，并用真实 agy_conversation_id 恢复：

~~~bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --conversation "$agy_conversation_id" \
  --timeout 30m \
  "<Rework Contract>"
~~~

返工后重新执行完整三轴 Review。

---

## 6. Codex Independent Verification

Codex 独立重跑：

~~~bash
./mvnw -Dtest=CacheServiceTest test
~~~

同时重新执行原始反馈环，确认：

~~~text
Original repro before: RED
Minimal regression: RED
After fix: GREEN
Original repro after: GREEN
Codex re-run: PASS
Completeness Review: PASS
~~~

只有必要验证全部通过，才能进入：

~~~text
VERIFYING → CODE_VERIFIED
~~~

---

## 7. Knowledge Closeout

这是纯内部 bugfix，假设 README、public API、config 均未受影响：

~~~text
README              verified-current
Agent rules         verified-current
API Contract        not-applicable
Runtime Config      not-applicable
Residue             verified-current
~~~

Closeout 可以是零文档 diff；不为了制造变更而改 README。Codex 完成 Closeout Review 后，才可以：

~~~text
ACCEPTED
~~~
