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

v2.1 强制区分：

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

## Gate 3 — Architecture & Contract

检查：

- 是否遵守项目分层/模块边界；
- 是否绕开已有抽象重复造实现；
- API contract 是否与调用方同步；
- DTO/model/entity 边界是否混乱；
- DB schema / migration / persistence 是否一致；
- 配置是否遵循已有方式；
- 是否引入架构方向偏离。

必要时：

```bash
rg "<symbol>" .
```

追踪调用链和同类实现。

## Gate 4 — Correctness & Edge Cases

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

## Gate 5 — Error Handling & Observability

检查：

- 异常是否被吞掉；
- 错误码/HTTP status 是否正确；
- 日志是否泄漏敏感信息；
- 是否出现 debug/临时输出；
- 是否有足够上下文定位问题；
- retry 是否放大永久错误。

## Gate 6 — Tests

测试必须验证真实需求，而不是只为了绿色：

- happy path；
- 关键 failure path；
- bug regression case；
- 重要边界；
- contract / integration（若相关）。

警惕：

- 只改 assertion 迎合错误实现；
- 删除测试；
- 大面积 skip；
- mock 掉真正需要验证的逻辑。

## Gate 7 — Turn Evidence Integrity

`TURN_COMPLETE:<nonce>` 或 tty7 native `done` 只说明当前 worker turn 返回。

Review 必须确认：

- 当前看到的是本轮 nonce，不是旧 scrollback；
- native status wait 若使用，发送后带了 `--changed`，避免 stale level；
- marker missing 时没有被无证据猜成成功；
- worker screen 与 Git state 没有明显矛盾。

此 Gate 不决定代码正确性，只保证 Supervisor 没有读错轮次。

## Gate 8 — Independent Verification

Codex 必须自己执行相关命令。优先使用仓库约定：

```text
lint
format/check
typecheck
unit test
integration test
build/package
contract/schema check
```

AGY 报告“我跑过了”只能作为线索，不能代替独立验证。

## Gate 9 — Diff Hygiene

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

## Gate 10 — External Side Effects

默认验收边界是“本地 repository 可交付”。确认没有未经授权：

- push；
- merge；
- release；
- deploy；
- production write；
- remote delete；
- cloud resource mutation。

## Gate 11 — tty7 Ownership / Cleanup

确认：

- 本次只写入 Run Context 保存的 worker pane；
- 未操作其他 agent/user pane；
- 未执行 server stop/restart 或全局 orphan cleanup；
- 若任务完成且用户未要求保留，清理的是本次创建的 workspace；
- 若保留 worker，最终汇报提供稳定 workspace/pane id。

## Review 结论模板

每轮 Review 至少得出一种明确结论：

### PASS

```text
PASS
- 当前 Task Contract 阶段满足。
- Baseline 完整，未发现无依据的 scope drift。
- 相关代码/测试证据成立。
- 可以进入下一阶段或独立 Verification。
```

### REWORK

```text
REWORK
- Issue: <具体问题>
- Evidence: <文件/diff/测试证据>
- Expected: <期望行为>
- Required change: <需要 AGY 做什么>
- Re-run: <修复后 AGY 应跑什么>
```

### BLOCKED

```text
BLOCKED
- Blocker: <环境/权限/外部依赖/需求缺失>
- Evidence: <实际证据>
- Safe state: <当前 repository / worker 状态>
- Decision needed: <需要用户决定什么>
```

只有 PASS 才进入下一重要阶段。最终 `ACCEPTED` 还必须经过 Codex Independent Verification。