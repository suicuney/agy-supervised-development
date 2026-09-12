# AGY Supervised Development 4.1

当前开发版本：**4.1.0-alpha.2**

> **Astra 定义和审代码；AGY 开发和执行测试；确定性程序核对完成条件。**

## 默认流程

```text
ASTRA: 问题定位 + 小 Contract + 验收场景 + 可选诊断权限
→ AGY / HERDR: 实现 + 已授权局部诊断
→ ASTRA: 完整交付增量 Code Review（不跑测试）
   ├─ REWORK → AGY 完整修复后停止 → ASTRA 再审
   └─ PASS
→ ASTRA: 冻结结构化 Test Plan / applicability / thresholds / digest
→ deterministic TEST-entry gate
→ AGY / HERDR: 正式测试 + 独立 attempt 证据
   ├─ 交付内容变化 → invalidate → AGY 修复 → ASTRA 再审 → 新计划 → 重测
   ├─ 环境问题 → BLOCKED
   └─ 证据齐全
→ deterministic completion gate
→ COMPLETE
```

没有默认 Luna supervisor、Sol plan review 或第二次 Astra 测试复核。

## Contract 与诊断

Contract 继续只冻结 `WHAT / BOUNDARY / DONE`，并增加可观察 `acceptance_scenarios`、关键反例和可选 `diagnostics`。普通 HOW 仍由 AGY 决定。

实现阶段允许 Astra 在 Contract 中预授权最小复现、定向单测、typecheck/compile feedback 等低成本反馈。它们必须记录 `formal_acceptance=false`，绝不能直接满足最终验收；项目已有 TDD/质量规则仍优先适用。

机器来源：`schemas/development-contract.schema.json` + `templates/development-contract.json`。

## Baseline 与两种身份

`scripts/snapshot-code-state.sh` 现在使用 Python helper fail-closed 采集：

- 从仓库根目录统一采集，子目录调用结果一致；
- 输出只能在 Git 私有目录或工作树外，临时目录完成后原子发布；
- 保存 HEAD/baseline、NUL status、committed/index/worktree binary diff；
- 未跟踪普通文件原文以本地受限 content-addressed blob 保存；
- 路径使用 base64 编码并稳定排序，支持空格/换行/Unicode；
- symlink 只记录目标文本，不跟随仓库外目标，悬空链接变化会失效；
- 二进制、可执行位、删除/重命名/mode 变化可被发现；
- 疑似凭据、特殊文件、submodule 等无法安全覆盖时 fail closed；忽略但影响验收的输入需要精确显式纳入。

身份拆分：

```text
deliverable_digest = 实际交付内容身份\ownership_digest   = Git HEAD/index/status 归属身份
```

单纯 `git add` 不改变 deliverable digest，但会改变 ownership 状态，供恢复核对。

## Astra Code Review

AGY 停止写入后，Astra 只审交付内容，不执行 tests/build/lint/E2E。完整增量包括 production code、测试源码/断言/fixture/golden、配置、lockfile、生成源码、调用方/消费者/schema/docs、未跟踪内容和必要的 binary/mode 变化。

`CODE_REVIEW_PASS` 绑定 Contract revision + `reviewed_deliverable_digest`。任何交付内容变化都会使它 STALE；证据日志只有放在预声明 Git-private/out-of-worktree evidence root 才不会污染交付摘要。

## Structured Test Plan / Results

唯一运行时事实是 JSON：

- `schemas/test-plan.schema.json` / `templates/test-plan.json`
- `schemas/test-results.schema.json` / `templates/test-results.json`

Plan 冻结每个 check 的类型、argv/观察步骤、cwd、required、客观 applicability、允许 exit code、证据类型、timeout/max attempts；指标只支持 `eq/ge/le`。自然语言 expected 只能解释，不能单独机械判 PASS。

每个 attempt 独立记录实际执行、开始结束、exit/观察、measured_values、日志引用+SHA256、执行前后 deliverable digest。不能拼接不同 attempt；最新 attempt 决定该 check，不能拿早先偶然 PASS 掩盖后续 FAIL。

N/A 只能来自冻结的客观 applicability。条件未知是 BLOCKED；失败不能改成 N/A。合法无检查任务也必须有冻结且带 hash 的 `no_checks_acceptance`，空数组不能自动完成。

## Deterministic Run State Gate

Run State v2 记录 baseline、Herdr/writer、review、frozen plan、findings、BLOCKED 恢复信息和 `state_version`。写入使用本地 file lock + optimistic version + fsync/atomic replace，避免合作进程丢失更新，但不冒充 OS sandbox。

进入 TEST：

```bash
bash scripts/validate-run-state.sh transition \
  --run-state <state> --contract <contract> --test-plan <plan> \
  --to TEST --expected-state-version <n>
```

完成：

```bash
bash scripts/validate-run-state.sh complete \
  --run-state <state> --contract <contract> \
  --test-plan <plan> --results <results> \
  --expected-state-version <n>
```

完成判定重新读取磁盘和当前 Git 状态，核对当前 Contract、review/plan digest、全部 check/attempt、真实 argv/exit 或观察证据、日志存在/hash、applicability、metrics、open finding/blocker、dispatch/writer 状态以及 test before/after/current deliverable digest。只有成功才原子写 `COMPLETE`。

测试发现代码缺陷时先保存失败证据、确认 worker 停止，再 `invalidate` 进入 `TEST_REWORK`；AGY 完整修复后停止并回 Astra code review。默认交付摘要变化后重跑所有 applicable required 正式检查，本版不做复杂证据复用。

## Recovery / dispatch

所有 AGY 仍经 Herdr。`done/idle` 不等于通过。busy worker 不重复派单；`SEND_UNKNOWN` 先调查、不能自动重发；旧 writer 可能存活时不能启动第二 writer。BLOCKED 保存原因、来源 phase、恢复动作和关联身份；恢复重新核对仓库/worktree、baseline、Contract、plan 和 worker。

旧 Run State 缺少 v2 必需证据时必须重建/重核当前阶段，不能默默补成 PASS。

## 验证层级

```text
STATIC_VALID       schema / docs / deterministic & mock behavior checks
ENVIRONMENT_READY  目标机 Herdr/AGY 前置条件
FLOW_VERIFIED      一次性临时仓库真实 Astra→AGY→Review→Plan→Test→Completion 证据
```

三者不可互相冒充。

验证依赖：

```bash
python3 -m pip install -r requirements-validation.txt
bash scripts/test-readiness.sh
# 目标机环境检查：
bash scripts/test-readiness.sh --environment
```

历史说明可以提到已移除的 Luna/4.0 流程；活跃执行文档不能依赖它们。
