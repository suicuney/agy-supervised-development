# Repository Review Gates

本文件定义 Codex 监督 AGY 时的独立 Review 维度。不是所有任务都机械执行所有项，但所有**相关项**必须有结论。AGY screen 只用于诊断和 Turn observation，真正交付从 Git state 获取。

## Gate 0 — Baseline Integrity

确认：

- 当前 branch / HEAD 已记录；
- 任务开始前已有的未提交改动已识别；
- 没有为了清理工作区误删/回滚用户改动；
- AGY 本任务新增改动可与 baseline 区分。

基础命令：

```bash
git status --short
git diff --stat
git diff --check
```

如果工作区在任务开始时已经 dirty，Review 时重点比较“baseline changed paths”和“当前 changed paths”的差异。

## Gate 1 — Scope / Scope Drift

检查：

- 修改是否属于 Task Contract Scope；
- 是否出现顺手重构；
- 是否有无关格式化；
- 是否新增不必要依赖；
- 是否改动无关配置、CI、部署文件。

强制区分：

```text
current changes
- baseline changes
= task-introduced changes
```

如果 AGY 新增 path 超出 Scope：

1. 判断是否为完成需求必需；
2. 没有充分证据则 REWORK；
3. 只撤销 AGY 本任务产生的越界修改；
4. 再次检查 baseline integrity。

## Gate 2 — Requirement Coverage

把需求拆成可验证条目，逐项对应到：

- 实现代码；
- API / schema / contract；
- 数据迁移；
- 测试；
- UI/调用方（若适用）。

不能用“总体看起来完成了”代替逐项覆盖。

## Gate 3 — Change Propagation & Blast Radius

本 Gate 不只检查“改了什么”，还检查“**本来应该改但漏掉了什么**”。详细协议见 `completeness-regression.md`。

对每个有语义变化的 symbol / contract / state 追踪：

- direct callers；
- indirect callers、re-export/barrel、scripts；
- types / enums / validation / serialization；
- schema / migration / existing data；
- sibling handlers / jobs / flows；
- error / empty / permission / retry / fallback states；
- cache / derived state / stale IDs；
- orphaned old path / dead code；
- tests；
- 后续 Knowledge Closeout 影响面。

必要时：

```bash
rg "<changed-symbol>" .
rg "<old-route|old-field|old-enum|old-config>" .
```

每个发现的 remainder 必须得到一种明确处置：

- `fixed-in-run`；
- `not-applicable`；
- `out-of-scope-different-ticket`；
- `blocked-decision-needed`。

规则：Completeness 不能成为 scope expansion 的借口；判断标准是“现在交付会被 Reviewer 称为 unfinished，还是另一个 ticket”。前者必须收完，后者留在 Scope 外。

## Gate 4 — Architecture & Contract

检查：

- 是否遵守项目分层/模块边界；
- 是否绕开已有抽象重复造实现；
- API contract 是否与调用方同步；
- DTO/model/entity 边界是否混乱；
- DB schema / migration / persistence 是否一致；
- 配置是否遵循已有方式；
- 是否引入架构方向偏离。

Completeness 发现的传播面不能用破坏架构边界的方式补齐。

## Gate 5 — Correctness & Edge Cases

按任务相关性检查：

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

## Gate 6 — Error Handling & Observability

检查：

- 异常是否被吞掉；
- 错误码/HTTP status 是否正确；
- 日志是否泄漏敏感信息；
- 是否出现 debug/临时输出；
- 是否有足够上下文定位问题；
- retry 是否放大永久错误。

## Gate 7 — Tests, Test Layers & Regression Proof

测试必须验证真实需求，而不是只为了绿色。

### Test Layer Decision

每个实际开发任务都要有明确结论：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

- 纯逻辑通常由 unit 覆盖；
- 跨 module / DB / serialization / queue / adapter contract 时考虑 integration；
- UI→API→DB、service→service、CLI→filesystem 等真实跨边界流程优先考虑 E2E；
- 用户明确跳过 E2E 时必须记为 `user-skipped`，不能伪装成 `not-applicable`。

### Bugfix Red → Green

可安全、确定性自动复现的 bug 默认要求：

```text
regression test
→ 在 unfixed behavior 上 RED
→ fix root cause
→ 同一 test GREEN
→ Codex independent re-run
```

记录：

```text
Regression proof: required | not-applicable
Before fix: FAIL evidence
After fix: PASS
Codex re-run: PASS | FAIL
```

`not-applicable` 必须有原因和替代证据，不能只是“没写 regression test”。

同时检查：

- happy path；
- 关键 failure path；
- 重要边界；
- contract / integration；
- 可达的 error/empty/permission state；
- bug root cause 是否在 sibling site 仍存在。

警惕：

- 只改 assertion 迎合错误实现；
- 删除测试；
- 大面积 skip；
- mock 掉真正需要验证的逻辑；
- 修复后才补一个从未证明会失败的“回归测试”。

## Gate 8 — Turn Evidence Integrity

`TURN_COMPLETE:<nonce>` 或 tty7 native `done` 只说明当前 worker turn 返回。

Review 必须确认：

- 当前看到的是本轮 nonce，不是旧 scrollback；
- native status wait 若使用，发送后带了 `--changed`，避免 stale level；
- marker missing 时没有被无证据猜成成功；
- worker screen 与 Git state 没有明显矛盾。

此 Gate 不决定代码正确性，只保证 Supervisor 没有读错轮次。

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

AGY 报告“我跑过了”只能作为线索，不能代替独立验证。

如果 E2E required，应记录 command、startup/readiness、seed/fixture、test account/sandbox 和 teardown；仓库没有 E2E harness 时，不擅自为小任务引入大型基础设施，按 Task Contract 决策。

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
- 无关重命名；
- 大面积格式化；
- 敏感信息；
- 超范围文档/配置变化。

## Gate 11 — External Side Effects / One-way Door

默认验收边界是“本地 repository 可交付”。确认没有未经授权：

- push；
- merge；
- release；
- deploy；
- production write；
- remote delete；
- cloud resource mutation。

Completeness 也不能授权 Supervisor/AGY 擅自做 one-way decision。以下默认需要明确授权/用户判断：

- destructive / non-additive migration；
- breaking public API；
- auth / tenancy boundary relaxation；
- money / billing semantics；
- secrets / credentials；
- irreversible data deletion。

## Gate 12 — tty7 Ownership / Cleanup

确认：

- 本次只写入 Run Context 保存的 worker pane；
- 未操作其他 agent/user pane；
- 未执行 server stop/restart 或全局 orphan cleanup；
- 若任务完成且用户未要求保留，清理的是本次创建的 workspace；
- 若保留 worker，最终汇报提供稳定 workspace/pane id。

## Gate 13 — Knowledge & Documentation Alignment

代码通过 Gate 0–12 的相关项和 Independent Verification 后必须执行 Knowledge Closeout。详细协议见 `closeout-governance.md`。

先做 Knowledge Impact Scan；每个相关事实面必须标成：

- `verified-current`；
- `changed-and-verified`；
- `pending`；
- `out-of-scope`；
- `not-applicable`。

检查：

- README / usage 是否仍与最终实现一致；
- `AGENTS.md` / `CLAUDE.md` / 项目 rules 是否仍准确、精简、可执行；
- API / schema / CLI / shared Contract 是否与实现、示例和调用方一致；
- env / config / provider / service / deploy / job 说明是否同步；
- 重命名或退役 symbol 是否仍残留在非历史现役文档中；
- 是否出现多个文档同时声称自己是同一事实的权威来源；
- 是否把一次性开发流水账、已完成 TODO 或中间态写入长期规则；
- 未验证行为是否被误写成“已完成 / 已上线 / 当前默认”；
- 明显 workspace residue 是否已报告为 `deletion-candidate`，且没有未经授权删除；
- Closeout 修改是否仍符合 baseline integrity 和 Scope Drift Guard。

原则：**每次开发都必须执行 Closeout Scan，但不是每次开发都必须修改文档。** 若所有相关知识面都已是现役状态，`verified-current` 即可 PASS。

对于 API、schema、CLI、环境变量、模块边界、部署、用户流程、退役/改名或跨项目协议等高影响变化，必须升级为 Full Closeout，并通过搜索旧 symbol / route / env / field / service 等方式检查 stale reference。

## Review 结论模板

每轮 Review 至少得出一种明确结论：

### PASS

```text
PASS
- 当前 Task Contract 阶段满足。
- Baseline 完整，未发现无依据的 scope drift。
- Completeness / blast radius 相关项已检查。
- 相关代码/测试证据成立。
- 可以进入下一阶段或独立 Verification。
```

### REWORK

```text
REWORK
- Issue: <具体问题>
- Evidence: <文件/diff/测试/调用链证据>
- Expected: <期望行为>
- Required change: <需要 AGY 做什么>
- Re-run: <修复后 AGY 应跑什么>
```

### BLOCKED

```text
BLOCKED
- Blocker: <环境/权限/外部依赖/one-way decision/需求缺失>
- Evidence: <实际证据>
- Safe state: <当前 repository / worker 状态>
- Decision needed: <需要用户决定什么>
```

只有相关代码 Gate PASS 才进入下一重要阶段。最终 `ACCEPTED` 必须同时经过 Change Completeness、Test/Regression Proof、Codex Independent Verification 和 Gate 13 Knowledge Closeout Review。