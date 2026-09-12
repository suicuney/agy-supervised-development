# AGY Supervised Development 4.0

当前开发版本：**4.0.0-alpha.1**

这是一次监督架构重构：把高成本推理集中在任务开头，把高频监督交给更低成本模型，把具体实现自主权交给 AGY。

> **Astra frames. Luna supervises. AGY builds. Git tells the truth.**

## 主流程

```text
USER INTENT
→ ASTRA ARCHITECT
→ DEVELOPMENT CONTRACT
→ CONTRACT FROZEN
→ LUNA SUPERVISOR
→ BASELINE
→ AGY BUILD            # Herdr only
→ AGY SELF-REVIEW
→ LUNA REVIEW / VERIFY
→ ACCEPTED
```

异常才升级：

```text
LUNA
→ ESCALATE
→ ASTRA
→ CONTRACT PATCH
→ LUNA
→ AGY
```

## 为什么改成 4.0

3.3 默认链路要求 Codex 先 `SIZE → SHAPE → SPEC → SLICE → Sol High Review → PLAN FROZEN`，随后 Codex 还持续承担监督、Review 和 Verify。这样高阶模型会重复读取仓库并长期驻留在高频控制循环里。

4.0 改成三层职责：

```text
Astra = 高价值分析 / 架构判断 / Development Contract
Luna  = 低成本长期监督 / Review / Verify / Rework dispatch
AGY   = 仓库探索 / 实现计划 / 编码 / 测试 / Self Review
```

核心边界：

```text
Astra owns WHAT / WHY / BOUNDARY / DONE
AGY owns normal HOW
Luna checks whether AGY reached DONE without crossing BOUNDARY
```

## Development Contract

Astra 默认不再生成长篇施工步骤，而是生成一个紧凑任务契约：

```yaml
goal: <目标>
problem: <当前问题>
expected_behavior:
  - <可观察行为>
constraints:
  - <边界>
architecture_intent:
  - <真正需要冻结的架构决定>
definition_of_done:
  - <完成标准>
agy_authority:
  - inspect repository
  - choose ordinary implementation details
  - modify in-scope files
  - run relevant tests
  - fix failures caused by this task
  - self-review
supervisor_authority:
  - inspect Git evidence
  - request bounded rework
  - run targeted verification
escalate_if:
  - architecture conflict
  - material requirement ambiguity
  - material scope expansion
  - repeated core failure
  - one-way decision
```

`CONTRACT FROZEN` 冻结的是需求、边界和完成标准，不是逐行实现计划。

## Token 策略

默认遵循：

```text
Pointer > Copy
Evidence > Full Repo Re-read
Escalation > Strong-model always-on
Definition of Done > Detailed itinerary
```

Astra 只读取解决契约级问题所需的仓库事实。Luna 默认只接收冻结 Contract、Git evidence、AGY 最新报告和相关测试输出。AGY 自己在仓库中发现普通实现细节。

## Luna Supervisor

Luna 可以：

- 启动 / 复用 Herdr 管理的 AGY worker
- 检查 `git status / diff --stat / diff --check / diff`
- 阅读 AGY completion / blocked report
- 运行针对性验证
- 基于证据要求 bounded rework
- 在 Contract 无法继续成立时升级 Astra

Luna 不可以悄悄修改冻结 Contract 或重新设计产品/架构。

## Astra Escalation

只有以下情况默认升级：

1. architecture conflict
2. material requirement ambiguity
3. scope explosion
4. 同一核心问题两轮 bounded rework 仍失败
5. destructive / irreversible / breaking / security 等 one-way decision

普通 lint、test failure、小 bug、命名、文件组织、框架 API 查找都由 Luna + AGY 解决。

## AGY Runtime

Herdr 继续作为唯一 AGY runtime，这部分继承 3.3 的成熟边界：

```text
CONTRACT FROZEN
→ scripts/check-herdr.sh
→ herdr workspace create --cwd <repo_root>
→ use returned .result.root_pane.pane_id
→ herdr agent start <task-agent> --kind agy --pane <pane_id>
→ herdr agent prompt ... --wait
→ blocked: agent read before interaction
→ repository evidence
```

`Herdr done != REVIEW PASS`，runtime 状态只证明运行状态，不证明交付质量。

详见 `resources/agy-execution.md`。

## Review / Verification

AGY 先 Self Review，Luna 再独立 Review：

```text
Development Contract
→ Git status / diff stat / diff check
→ changed diff
→ AGY completion report
→ targeted tests / runtime evidence
→ broader inspection only when justified
```

目标是 **evidence-driven review**，不是每轮重新理解整个仓库。

## Sol High Plan Review

3.3 的 Sol High Plan Review 资源暂时保留，但 **不再属于默认主流程**。它现在是 guarded / legacy escalation capability，只在任务风险或用户明确要求时使用。

## 安装当前分支

```bash
codex plugin marketplace add suicuney/agy-supervised-development --ref codex/agy-supervised-v4-astra-skill
codex plugin add agy-supervised-development@agy-supervised-development
```

## Active Structure

```text
SKILL.md
skills/agy-supervised-development/SKILL.md

resources/
├── architect.md
├── development-contract.md
├── supervisor.md
├── escalation.md
├── verification.md
├── agy-execution.md
├── failure-modes.md
├── sol-plan-review.md          # optional guarded capability
├── ego-browser-runbook.md      # only when browser work is needed
└── ... legacy 3.3 resources retained during migration
```

## 4.0 Alpha 原则

```text
高阶模型只做高价值推理
低阶模型承担高频监督
AGY 获得正常实现自主权
监督基于 Contract + Evidence
强模型升级是异常路径
Herdr 保持唯一 AGY Runtime
Git 保持 repository truth
一个任务仍然只有一个 primary writer
```

## 自检

```bash
scripts/test-readiness.sh
```
