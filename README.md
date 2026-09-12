# AGY Supervised Development 4.0

当前开发版本：**4.0.0-alpha.4**

> **Astra decides. Luna supervises. AGY builds. Git proves. Routing proves itself.**

4.0 把昂贵推理留给契约级决策，把高频监督交给独立 supervisor，把实现细节交给 AGY；同时补齐真实交接、运行状态、恢复、基线和证据绑定。

## 默认流程

```text
USER
→ ASTRA: CONTRACT
→ LUNA: SUPERVISE
→ AGY via HERDR: BUILD + TEST + SELF-REVIEW
→ LUNA: VERIFY
→ ACCEPT
```

只有 Contract 本身需要改变才回 Astra：

```text
LUNA → ASTRA: CONTRACT PATCH → LUNA → AGY
```

## Development Contract

Contract 保持短小，只冻结目标、可观察行为、边界和完成标准：

```yaml
contract_id: task-x
revision: 1
goal: <目标>
behavior: [<可观察结果>]
constraints: [<重要边界>]
done: [<完成证据>]
escalate_if: [<契约级 blocker>]
```

普通 `HOW` 由 AGY 自己决定，不默认生成文件级施工计划。

## Codex supervisor 交接

当前首选宿主是 Codex Multi-Agent V2。真正交接使用宿主实际暴露的 `spawn_agent` 能力；当 `model` 和 `fork_turns` 字段可用时，supervisor 使用 fresh minimal-context spawn，例如 `fork_turns: "none"` 并请求 `gpt-5.6-luna`。

分别记录：

```text
requested_model
host_model_evidence
model_status
handoff_status
```

未实际 spawn 不能宣称 Luna 已启动；只请求了 Luna、但宿主没有返回可核实模型元数据时，只能记录 `REQUESTED_UNVERIFIED`。若用户硬性要求 Luna 且宿主不能选择/证明该模型，则真实 BLOCKED，不静默降级。同模型 supervisor 只能标记 `SAME_MODEL`，成本优化未验证。

详见 `resources/codex-supervisor-handoff.md`。

## Run State / 恢复

运行状态不塞进 Contract。每个任务把状态放在 Git 私有目录：

```bash
git rev-parse --git-path "agy-supervised/runs/<task_id>/run-state.json"
```

它记录 baseline、supervisor/Herdr identity、round/finding、dispatch 状态、code-state digest、verification results 和 Contract patch。不会进入业务提交。

恢复时先核对仓库、工作目录、Contract revision 和当前 Git 状态；不猜会话、不自动重放副作用未知的命令，只有确认旧 worker 不会并行写入后才启动替代 worker。

## Baseline / 工作区

Herdr workspace 只是终端运行环境，不是代码隔离。

- 干净 checkout、没有并行 writer：可以直接执行。
- 已有用户修改、并行 writer 或明确隔离需求：优先任务 worktree。
- 任务依赖未提交修改时，不能从 HEAD 开一个干净 worktree 然后遗漏前置内容。
- 不自动 stash / clean / reset / 覆盖用户修改。

`scripts/snapshot-code-state.sh` 捕获 HEAD、staged、unstaged、untracked 内容哈希并生成 code-state digest，用于基线、恢复和验证证据绑定。

## Herdr / AGY

AGY 只通过 Herdr 执行。`scripts/check-herdr.sh` 只证明 **Environment Ready**：Herdr/AGY/jq 存在、Herdr schema/status 可解析、Antigravity integration 明确为 current。它不证明 AGY 已登录、worker 能跑、模型交接成功或完整流程已验证。

每轮派发带 `task_id + round`。worker 忙时不重复派单；timeout 或发送结果不确定时先 read/investigate，不自动重发。

## Luna 验收

最小上下文：

```text
Contract
+ applicable AGENTS.md / repository rules
+ baseline / Run State
+ AGY result
+ Git evidence
+ relevant verification evidence
```

```text
AGY execute → inspect → verify → PASS | REWORK | ESCALATE | BLOCKED
```

同一 finding 连续两轮无实质进展默认升级。环境/认证/依赖阻塞不会无限返工，也不会用修改业务 Contract 的方式绕过。

## 完整变化审查

最终审查必须覆盖：

```text
committed task changes
+ staged changes
+ unstaged changes
+ untracked file contents
+ deletions / renames
+ relevant binary changes
```

并区分 baseline 已有用户内容和本任务新增内容。

## 验证证据

每个关键结果记录 Contract revision、方法/命令、cwd、exit code、结果、日志引用和 code-state digest。结果只允许：

```text
PASS | FAIL | BLOCKED | NOT_RUN | NOT_APPLICABLE
```

命令没执行不能 PASS。代码变化后，只使受影响证据失效并重跑必要验证。最终 ACCEPT 前 worker 必须停止写入，证据必须对应实际交付状态。

“先跑最便宜的决定性检查”只是顺序，不允许跳过适用的项目质量门禁。

## paper-info-web 规则适配示例

该仓库自己的 `AGENTS.md` 要求 Java 21 Spring Boot 模块化单体、OpenAPI 为公共 API 唯一权威、公共 API 变化同步 generated clients/tests/traceability matrix、React 随 JAR 交付、Browser Worker 不进入默认构建发布，并定义了 pnpm/Maven/docker compose 质量门禁。4.0 的 supervisor 应引用并执行适用规则，而不是把这些规则硬编码成所有仓库默认值。

## 三类状态

```text
STATIC_VALID       文档/路径/schema/版本/活跃规则一致
ENVIRONMENT_READY  本机工具/服务/集成预检满足条件
FLOW_VERIFIED      真实 supervisor → Herdr/AGY → review/verify 获得端到端证据
```

三者不可互相替代。语义 eval 场景若没有执行器，只能标为待执行，不宣称通过。

## 核心文件

```text
SKILL.md
resources/development-contract.md
resources/codex-supervisor-handoff.md
resources/run-state.md
resources/supervisor.md
resources/agy-execution.md
resources/verification.md
schemas/development-contract.schema.json
schemas/run-state.schema.json
scripts/snapshot-code-state.sh
```

旧 3.3 Sol/browser/Shape/Spec/Slice/Three-Axis 流程不属于默认链路；需要保留的历史说明位于 `legacy/`。

## 检查

```bash
scripts/test-readiness.sh
```

输出会区分静态有效、环境就绪和真实流程是否已验证，不会把 mock/static 测试表述成真实多模型流程已跑通。
