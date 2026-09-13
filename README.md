# AGY Supervised Development 4.1

当前开发版本：**4.1.0-alpha.3**

这是一个精简的受监督开发 Skill：Astra 负责需求边界、代码审查和正式测试命令；AGY 经 Herdr 负责实现、返工和执行测试；本地判定器只核对计划、执行记录、证据和当前代码状态是否一致。

## 最短流程

```text
Astra：Contract
→ AGY/Herdr：实现并停止
→ Astra：完整代码审查
→ Astra：冻结必要测试命令
→ AGY/Herdr：执行并记录实际结果
→ validate-run-state complete
```

代码审查有问题就返工再审；测试后修改交付内容就使旧审查/测试证据失效并重走审查与测试；环境缺失使用 `BLOCKED`，恢复后回原阶段。

## Formal Test Plan

正式计划只有命令清单。每条检查冻结：

- check id
- cwd + argv
- accepted exit codes
- timeout
- max attempts
- 必要的显式 input paths

所有进入计划的检查都必须通过。不适用的检查在冻结前删除并写入 `notes`；浏览器、凭证、依赖缺失是 BLOCKED，不是自动免测。

AGY 使用已有执行工具运行命令，并把真实 argv/cwd、时间、退出码、证据 path/hash、before/after deliverable digest 写入 `test-results.json`。本仓库不再提供通用测试执行、指标解析或人工观察适配层。

## 数据保护

`snapshot_code_state.py` 保留 baseline、deliverable digest、Git ownership digest、未跟踪原文保护、binary、symlink target 和 executable bit。snapshot policy 精确声明 ignored inputs 与敏感未跟踪授权，并由 TEST-entry/complete 复用。

## 主要入口

```text
SKILL.md
resources/development-contract.md
resources/run-state.md
resources/agy-execution.md
resources/code-review.md
resources/testing.md
schemas/*.json
templates/development-contract.json
templates/snapshot-policy.json
templates/run-state.json
templates/test-plan.json
templates/test-results.json
templates/execution-unit.md
templates/review-report.md
scripts/snapshot-code-state.sh
scripts/validate-run-state.sh
```

## 能力边界

`validate-run-state` 检查 Contract/plan/digest、命令记录、退出码、证据 hash、attempt 顺序、writer/dispatch/findings 和当前 deliverable 是否一致。它不能仅凭日志 hash 证明所有业务行为正确，也不提供对同权限恶意执行者的不可伪造证明。

需要主观人工验收时保持待人工确认，不伪装成自动 PASS。确实无需执行任何检查时可使用带理由和 hash 证据的 `no_checks_acceptance`。

旧的 alpha.3 前期扩展 Run State/Test Plan/Test Results 与当前精简格式不兼容时，应重新建立当前 run 的审查、计划和测试记录，不自动补成 PASS。

`scripts/test-readiness.sh` 只做结构、文档和工作流静态检查，并可选检查 Herdr 环境；它不执行项目测试、构建、行为复现或完整 AGY 流程。`evals/scenarios.json` 只是场景定义，不代表这些场景已经通过。
