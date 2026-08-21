# Repository Review Gates

本文件定义 Codex 在监督 AGY 时的独立 Review 维度。不是所有任务都要机械执行所有项，但所有**相关项**都必须有结论。

## Gate 0 — Baseline Integrity

确认：

- 当前分支和 HEAD 已记录；
- 任务开始前已有的未提交改动已识别；
- 没有为了清理工作区而误删/回滚用户改动；
- AGY 改动可以与 baseline 区分。

基础命令：

```bash
git status --short
git diff --stat
git diff --check
```

## Gate 1 — Scope

检查：

- 修改是否都属于 Task Contract；
- 是否出现“顺手重构”；
- 是否有无关格式化；
- 是否新增不必要依赖；
- 是否改动了不应改的配置、CI、部署文件。

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
- 配置项是否遵循项目已有方式；
- 是否引入架构方向偏离。

必要时使用：

```bash
rg "<symbol>" .
```

追踪调用链和同类实现。

## Gate 4 — Correctness & Edge Cases

重点检查：

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

根据任务类型选择相关项，不要求无意义地全部展开。

## Gate 5 — Error Handling & Observability

检查：

- 异常是否被吞掉；
- 错误码/HTTP status 是否正确；
- 日志是否泄漏敏感信息；
- 是否出现 `print` / debug log；
- 是否有足够上下文用于定位问题；
- retry 是否会把永久错误放大。

## Gate 6 — Tests

检查测试是否验证真正需求，而不是只为了绿色：

- happy path；
- 关键 failure path；
- 本次 bug 的 regression case；
- 重要边界；
- contract / integration（若相关）。

警惕：

- 只改 assertion 迎合错误实现；
- 删除测试；
- 大面积 skip；
- mock 掉真正需要验证的逻辑。

## Gate 7 — Independent Verification

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

## Gate 8 — Diff Hygiene

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

## Gate 9 — External Side Effects

默认验收边界是“本地 repository 可交付”。确认没有未经授权：

- push；
- merge；
- release；
- deploy；
- production write；
- remote delete；
- cloud resource mutation。

## Review 结论模板

每轮 Review 至少得出一种明确结论：

### PASS

```text
PASS
- Task Contract 当前阶段满足。
- 未发现越界改动。
- 相关测试/检查通过。
- 可以进入下一阶段。
```

### REWORK

```text
REWORK
- Issue: <具体问题>
- Evidence: <文件/diff/测试证据>
- Expected: <期望行为>
- Required change: <需要 AGY 做什么>
- Re-run: <修复后要求 AGY 跑什么>
```

### BLOCKED

```text
BLOCKED
- Blocker: <环境/权限/外部依赖/需求缺失>
- Evidence: <实际证据>
- Safe state: <当前仓库状态>
- Decision needed: <需要用户决定什么>
```

只有 PASS 才进入下一重要阶段。
