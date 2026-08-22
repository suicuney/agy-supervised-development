# Repository Review Gates

本文件定义 AGY Supervised Development 3.0 中 Codex 对 **Pi Worker 产出的 repository state** 做独立 Review 的维度。

不是所有任务都机械执行所有项，但所有相关项必须有结论。

Pi Evidence Bundle / worker summary 只用于诊断和定位；真正交付从 Git state 获取。

---

## Gate 0 — Baseline Integrity

确认：

- 当前 branch / HEAD 已记录；
- 任务开始前已有未提交改动已识别；
- 没有为了“清理”误删/回滚用户改动；
- 本 Run 新增改动可与 baseline 区分。

```bash
git status --short
git diff --stat
git diff --check
```

核心：

```text
current changes
- baseline changes
= task-introduced changes
```

---

## Gate 1 — Scope / Scope Drift

检查：

- 修改是否属于 Task Contract；
- 是否顺手重构；
- 是否无关格式化；
- 是否新增不必要依赖；
- 是否改无关 config/CI/deploy。

如果 Pi 新增 path 超初始 Scope：

1. 判断是否为需求必然传播面；
2. 有 blast-radius/completeness evidence 可以纳入；
3. 没有充分证据 → REWORK；
4. 只撤销本 Run 引入的越界修改；
5. 不碰 baseline-owned changes。

---

## Gate 2 — Requirement Coverage

把需求拆成可验证条目，逐项对应：

- 实现代码；
- API/schema/contract；
- migration/data；
- tests；
- UI/caller（若适用）。

不能用“Worker 说完成了”替代逐项覆盖。

---

## Gate 3 — Change Propagation & Blast Radius

本 Gate 同时 Review current diff 与 missing diff。详细协议见 `completeness-regression.md`。

每个语义变化追踪：

- direct callers；
- indirect callers / re-export / scripts；
- types / enums / validation / serialization；
- schema / migration / existing data；
- sibling flows / jobs；
- error / empty / permission / retry / fallback；
- cache / derived state / stale IDs；
- orphaned old path / dead code；
- tests；
- Knowledge Closeout 影响面。

必要时：

```bash
rg "<changed-symbol>" .
rg "<old-route|old-field|old-enum|old-config>" .
```

每个 remainder 必须是：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

Completeness 不能成为 scope expansion 借口。

---

## Gate 4 — Architecture & Contract

检查：

- 遵守项目分层/模块边界；
- 没有绕开已有抽象重复实现；
- API contract 与 caller 同步；
- DTO/model/entity 边界清晰；
- DB schema/migration/persistence 一致；
- config 遵循已有模式；
- 没有为完成任务引入无依据的新架构。

---

## Gate 5 — Correctness & Edge Cases

按相关性检查：

- null / empty / missing；
- boundary value；
- error path；
- retry / idempotency；
- timezone / locale；
- concurrency / race；
- transaction boundary；
- pagination / ordering；
- authorization；
- partial failure；
- backward compatibility。

---

## Gate 6 — Error Handling & Observability

检查：

- exception 是否被吞；
- HTTP/status/error code 是否正确；
- log 是否泄漏敏感数据；
- debug/临时输出是否残留；
- 是否有足够定位上下文；
- retry 是否放大永久错误。

---

## Gate 7 — Tests, Test Layers & Regression Proof

每个实际开发任务必须有：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

- 纯逻辑通常 unit；
- module/DB/serialization/queue/adapter contract 考虑 integration；
- UI→API→DB、service→service、CLI→filesystem 等真实边界流程优先 E2E；
- `user-skipped` 不能改写成 `not-applicable`。

### Bugfix RED → GREEN

可安全、确定性自动复现的 bug 默认要求：

```text
regression test
→ unfixed behavior RED
→ fix root cause
→ same test GREEN
→ Codex independent re-run
```

记录：

```text
Regression proof: required | not-applicable
Before fix: FAIL evidence
After fix: PASS
Codex re-run: PASS | FAIL
```

警惕：

- 只改 assertion 迎合实现；
- 删除测试；
- 大面积 skip；
- mock 掉真实 contract；
- fix 后才补一个从没证明能 RED 的测试。

---

## Gate 8 — Operation Evidence Integrity

Pi 的 `agent_settled` / RPC settled / Evidence Bundle 只说明当前 worker operation 返回。

确认：

- Evidence 的 `run_id` 是当前 Run；
- `operation_id` 与当前 operation 一致；
- stale event 没有推进状态；
- status 是 settled/blocked/failed/aborted 中的明确值；
- Provider/model transition 已记录；
- worker summary 与 Git state 明显冲突时以 Git 为准；
- Evidence 没有 token/Authorization/secret。

规则：

```text
OPERATION_SETTLED != PASS
```

---

## Gate 9 — Independent Verification

Codex 必须自己执行相关命令。优先使用仓库约定，并服从 Gate 7 的 Test Layer Decision：

```text
lint
format/check
typecheck
unit test
integration test
e2e test（required 时）
build/package
contract/schema check
```

Pi 报告“我跑过了”只能作为线索。

E2E required 时记录 command、startup/readiness、seed/fixture、account/sandbox 和 teardown。

---

## Gate 10 — Diff Hygiene

最终检查：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

确认没有：

- debug code；
- 临时文件；
- build artifact；
- 意外 lockfile；
- 无关 rename；
- 大面积格式化；
- sensitive information；
- 超范围文档/config 修改。

---

## Gate 11 — External Side Effects / One-way Door

默认验收边界是“本地 repository 可交付”。确认没有未经授权：

- push；
- merge；
- release；
- deploy；
- production write；
- remote delete；
- cloud resource mutation。

Completeness 也不能授权 Codex/Pi 擅自做：

- destructive/non-additive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- irreversible data deletion。

需要时标 `blocked-decision-needed`。

---

## Gate 12 — Harness Policy & Credential Hygiene

v3 新增正式 Harness Gate。

确认：

### Mode policy

- `inspect/verify` 没有写工具或 mutation escape；
- `implement/rework` 写入受到 repo/scope guard；
- `closeout` 没有借收尾重开生产代码范围。

### Tool policy

- blocked tool call 有明确 reason；
- dangerous command 没有绕过 hook；
- custom tool 没有绕开 read-only mode；
- Harness 没有为了成功临时进入 YOLO/全放行。

### Provider boundary

- Provider 只作为模型来源；
- 未自动安装/登录未经用户确认的 Provider；
- 没有提取 OAuth token/credential；
- Provider error 与代码 error 分类清楚。

### Evidence hygiene

- Run Store / Evidence Bundle 不含 access token、refresh token、Authorization header、secret value；
- runtime-only state 没有意外进入 git diff；
- session identity 只记录非敏感 ID/path reference。

如果 Harness policy 本身失效，应先 BLOCK/修复 Harness，不继续相信后续 worker operation。

---

## Gate 13 — Knowledge & Documentation Alignment

代码通过 Gate 0–12 的相关项和 Independent Verification 后执行 Knowledge Closeout。详见 `closeout-governance.md`。

每个相关知识面标：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

检查：

- README/usage 与最终实现一致；
- `AGENTS.md` / `CLAUDE.md` / project rules 准确、精简；
- API/schema/CLI/shared Contract 与实现/示例/caller 一致；
- env/config/provider/service/deploy/job docs 同步；
- rename/retirement 没在现役文档留下 stale reference；
- 没有多个文档声称同一事实都是权威来源；
- 没把一次性开发流水账写入长期规则；
- 未验证行为没被写成“已完成/已上线”；
- residue 已如实报告且无未经授权删除。

原则：每次开发都 Scan，不是每次开发都必须改 Markdown。

---

# Review 结论模板

## PASS

```text
PASS
- 当前 Task Contract 阶段满足。
- Baseline 完整，无无依据 scope drift。
- Completeness/blast radius 已检查。
- 相关代码/测试证据成立。
- Harness operation/evidence identity 正确。
- 可以进入下一阶段。
```

## REWORK

```text
REWORK
- Issue: <具体问题>
- Evidence: <文件/diff/测试/调用链/operation evidence>
- Expected: <期望行为>
- Required change: <Pi Worker 要修改什么>
- Re-run: <修复后应跑什么>
```

## BLOCKED

```text
BLOCKED
- Blocker: <环境/Provider/权限/one-way decision/需求缺失/Harness defect>
- Evidence: <实际证据>
- Safe state: <当前 repository/run 状态>
- Decision needed: <需要用户决定什么>
```

只有相关 Gates PASS 才进入下一重要阶段。最终 `ACCEPTED` 必须同时经过 Completeness、Test/Regression Proof、Codex Independent Verification、Harness Policy Gate 和 Knowledge Closeout Review。
