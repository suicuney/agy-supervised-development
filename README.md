# AGY Supervised Development 4.1

当前开发版本：**4.1.0-alpha.1**

> **Astra plans. AGY builds. Astra reviews code. AGY proves it with Astra-defined tests.**

4.1 移除默认 Luna supervisor，把高级模型只放在三个真正需要判断力的位置：问题/方案、代码复核、测试设计。AGY 负责实现和执行测试，所有 AGY 运行继续通过 Herdr。

## 默认流程

```text
USER
→ ASTRA: 定位问题 + Development Contract
→ AGY: 只开发，不做正式测试
→ ASTRA: 只做代码复核
   ├─ REWORK → AGY 修改 → ASTRA 再复核
   └─ CODE_REVIEW_PASS
→ ASTRA: 冻结 Test Plan + Acceptance Metrics
→ AGY: 执行测试
   ├─ 所有必需指标达标 → TASK COMPLETE
   ├─ 环境阻塞 → BLOCKED
   └─ 测试后修改代码 → 回 ASTRA Code Review，再生成测试计划
```

## Development Contract

Contract 继续保持很短：

```yaml
contract_id: task-x
revision: 1
goal: <目标>
behavior: [<可观察结果>]
constraints: [<重要边界>]
done: [<最终完成条件>]
```

普通 `HOW` 由 AGY 决定，不要求默认文件级实施计划。

## AGY 第一阶段：只开发

实现阶段的 worker order 明确写：

```text
IMPLEMENT ONLY.
Do not execute the formal test plan or project quality gates.
Do not declare task completion.
```

AGY 可以读代码、定位实现、修改代码、自查明显问题，但正式测试/质量门禁延后。

## Astra Code Review

AGY 停止写入后，Astra 只审代码，不执行测试。输入包括 Contract、适用 `AGENTS.md`、baseline 和完整 task delta。

复核覆盖：

```text
Contract fidelity
+ code correctness by inspection
+ project-rule compliance
+ caller/consumer/schema/config/docs completeness
+ risk-proportional maintainability
```

结果只有：

```text
CODE_REVIEW_PASS | CODE_REVIEW_REWORK | BLOCKED
```

有 finding 就交给 AGY 修改，再由 Astra 重新看完整代码状态。代码复核通过并不等于测试通过。

## Astra Test Plan

只有当前代码状态获得 `CODE_REVIEW_PASS` 后，Astra 才根据最终实现生成并冻结测试计划：

```yaml
test_plan_id: <id>
contract_revision: <n>
reviewed_code_state_digest: <digest>
checks:
  - id: T1
    method: <command/check>
    cwd: <dir>
    required: true
    expected: <可量化条件>
metrics:
  - <最终验收指标>
```

Astra 不执行测试。AGY 不能自行删除必需检查、降低阈值或重定义 PASS。

## AGY 第二阶段：测试

AGY 通过 Herdr 执行冻结 Test Plan，并记录真实结果：

```text
PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE
```

命令没有实际执行不能标 PASS。

当：

```text
所有 required checks = PASS
+ 所有 frozen metrics 达标
+ 没有 required BLOCKED / NOT_RUN
+ 测试证据仍绑定当前代码状态
```

直接 `TASK COMPLETE`。Astra 不再进行第二次测试复核。

如果测试阶段修改了生产/任务代码，之前的 `CODE_REVIEW_PASS` 与受影响测试证据立即失效，重新进入：

```text
ASTRA CODE REVIEW → ASTRA TEST PLAN → AGY TEST
```

## Baseline / Run State / 恢复

保留 4.0 中有效的安全机制：

- baseline 在 AGY 写入前捕获；
- 完整 delta 包括 committed、staged、unstaged、untracked contents、delete/rename、relevant binary；
- existing user changes 不自动 stash/clean/reset；
- Herdr workspace 不是 Git 隔离；必要时用 task worktree；
- Run State 放在 `git rev-parse --git-path "agy-supervised/runs/<task_id>"`；
- 不猜失联 session，不自动重放副作用未知指令；
- worker 未确认停止前不启动第二个 writer。

Run State 只跟踪 phase、Herdr identity、code-review pass digest、test plan、test results 和恢复信息，不再保存 Luna/model handoff 状态。

## Herdr

AGY 所有实现、返工和测试均通过 Herdr。`Herdr done/idle` 只表示 runtime lifecycle，不等于代码复核成功或测试指标达标。

## 三类就绪状态

```text
STATIC_VALID       结构/文档/schema/规则一致
ENVIRONMENT_READY  Herdr/AGY 本机前置满足
FLOW_VERIFIED      真实 Astra → AGY implement → Astra review → AGY test 获得端到端证据
```

三者不能互相冒充。

## 核心文件

```text
SKILL.md
resources/development-contract.md
resources/run-state.md
resources/agy-execution.md
resources/code-review.md
resources/testing.md
schemas/development-contract.schema.json
schemas/run-state.schema.json
templates/run-state.json
scripts/snapshot-code-state.sh
```

旧 3.x 和 4.0 Luna supervisor 流程不属于默认链路。

## 检查

```bash
scripts/test-readiness.sh
```

真实端到端验证必须单独报告，静态/mock 测试不能冒充真实流程跑通。
