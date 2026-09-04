# Example — Feature Development with AGY Supervised Development 3.2

场景：给现有 API 增加一个可选 currency 过滤条件，并同步必要测试和文档。

---

## 1. Codex 建立 Shape / Spec / Slice

这是一个 Medium 任务：

~~~text
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

Verification Seam
- Primary: GET /orders
- Secondary: existing repository query tests when needed
~~~

为本次变更建立一个完整的 Execution Unit：

~~~text
Execution Unit
- Goal: deliver the optional currency filter end to end.
- Scope: orders controller/service/repository query path, related DTO/validation,
  directly affected tests and docs.
- Completeness: inspect callers, serializers, fixtures and sibling query paths.
- Constraints: preserve baseline; no push/merge/deploy.
~~~

默认的 Sol High Plan Review 只审实现前的 Executable Plan：

~~~text
Codex Plan
→ Sol High Review
→ Codex Adopt / Reject / Modify
→ PLAN FROZEN
~~~

开始浏览器工作前检查依赖：

~~~bash
scripts/check-sol-plan-review.sh
~~~

最多进行 3 轮；若用户明确要求跳过方案评审，则直接记录 PLAN FROZEN。PLAN FROZEN 之后不再调用 Sol High。

---

## 2. PLAN FROZEN → BASELINE

在 AGY 写入前记录仓库状态：

~~~bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
~~~

如果工作区已有用户改动，记录 baseline-owned paths；需要时保存原始 patch 指纹：

~~~bash
git diff --binary -- <baseline paths> | shasum -a 256
~~~

不能为了让 AGY 获得干净工作区而回滚这些改动。

---

## 3. Codex 调 AGY 实现

在 repo_root 绑定的 Execution Unit 通过薄适配器交给 AGY：

~~~bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --timeout 30m \
  "Execution Unit: implement the optional currency filter for GET /orders.
   Preserve omitted-currency behavior, existing validation, auth and pagination.
   Update only the proven propagation path, tests and directly affected docs."
~~~

AGY 使用官方 CLI 的 headless stream-json 路径。Codex 至少记录：

~~~text
init.conversation_id → agy_conversation_id
init.cwd
permission_mode
tools
~~~

必须同时验证两层工作目录：

~~~text
init.cwd == repo_root
~~~

以及 AGY 第一个实际命令的输出：

~~~bash
pwd
git -C "$repo_root" rev-parse --show-toplevel
git -C "$repo_root" branch --show-current
~~~

如果命令 cwd 落在 AGY CLI home 或其他目录，停止相对路径写入，先恢复 workspace 绑定。

stream-json 的 result.status = SUCCESS 只表示本轮 Writer turn 返回；它不等于 Review PASS，也不等于交付完成。若工具调用被权限策略阻止，必须记录为 blocked/not-run。

状态：

~~~text
PLAN FROZEN → BASELINE → AGY BUILD
~~~

---

## 4. Codex Three-Axis Review

AGY 返回后，Codex 直接读取 Git：

~~~bash
git status --short
git diff --stat
git diff --check
git diff
~~~

然后分别判断：

~~~text
A. Spec Fidelity
- currency 省略、有效值、无效值是否都符合 contract。

B. Engineering Quality
- controller/service/repository/DTO 的职责和错误处理是否合理。

C. Completeness
- callers、validator、serializer、fixtures、sibling paths 和 docs 是否同步。
~~~

Completeness 搜索示例：

~~~bash
rg "currency" src test docs
rg "findOrders|listOrders" .
~~~

如果发现 export script 仍使用旧的 shared query contract，形成证据驱动的 Rework Contract：

~~~text
Issue
- export script still uses the old shared query contract.

Evidence
- <search/call-chain evidence>

Expected
- proven affected caller follows the new optional currency contract.

Required Change
- update only this propagation path and its tests.

Re-run
- <targeted command>
~~~

优先恢复同一个真实 AGY conversation：

~~~bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --conversation "$agy_conversation_id" \
  --timeout 30m \
  "<Rework Contract>"
~~~

返工后重新执行完整 Three-Axis Review；不能只复查原来的一个 finding。

---

## 5. Codex Independent Verification

只有 Review PASS 后才进入独立验证：

~~~bash
./mvnw -Dtest=OrdersTest test
./mvnw test
~~~

按项目实际情况补充 lint、typecheck、integration、build 或 E2E。全部必要验证通过后：

~~~text
REVIEW PASS → CODEX VERIFY → CODE_VERIFIED
~~~

如果是 browser-facing 变更，浏览器运行时验证由 Codex 负责；它不能替代三轴 Review。

---

## 6. Knowledge Closeout

由于 public API query contract 发生变化，升级为 Full Closeout。

~~~text
Goal
- 让 API、README、示例和现役 Contract 与最终 verified implementation 一致。

Source of Truth
- final diff
- verified tests
- completeness evidence

Required
- update API/README examples if affected
- search stale request examples
- keep rules concise

Forbidden
- unrelated production changes
- speculative documentation rewrite
- push/merge/deploy
~~~

如果确实需要修改知识文件，可以继续同一个 AGY conversation：

~~~bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --conversation "$agy_conversation_id" \
  --timeout 30m \
  "<Closeout Contract>"
~~~

随后 Codex 检查：

~~~bash
git diff --check
git diff
git status --short
rg "<old-request-shape>" .
~~~

最终生命周期：

~~~text
CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
~~~

最终报告至少包含：

~~~text
AGY conversation_id
changed behavior
changed files
Completeness evidence
tests/checks actually run
blocked/not-run checks
Independent Verification
Knowledge surfaces
residual risk
~~~
