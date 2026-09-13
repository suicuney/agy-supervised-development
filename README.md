# AGY Supervised Development 4.1

当前开发版本：**4.1.0-alpha.3**

> Astra 定需求与验收边界，AGY 经 Herdr 实现和执行冻结测试，Astra 只做代码复核，本地确定性 gate 最终决定 COMPLETE。

## 默认流程

```text
Astra：Contract + 验收场景/反例 + 可选诊断权限
→ AGY/Herdr：实现（诊断不是正式验收）
→ Astra：Code Review only
→ Astra：冻结结构化 Test Plan
→ TEST-entry gate
→ AGY/Herdr：run-frozen-check
→ validate-run-state complete
```

没有默认 Luna supervisor、Sol plan review、第二次 Astra 测试复核，也不要求小任务写文件级施工计划。

## alpha.3 可靠性重点

- Contract 使用 canonical `contract_digest`，同 revision 改正文会让 review/plan/results 失效。
- snapshot 输出不可覆盖；不修改已有父目录权限；tracked 删除可表达；未跟踪原文、binary、symlink target、可执行位可恢复/核对。
- `deliverable_digest` 与 Git/index `ownership_digest` 分离，纯 `git add` 不触发无意义代码重审。
- 冻结 snapshot policy，精确控制 ignored 输入与敏感未跟踪授权；runner、TEST-entry、complete 全程复用同一 policy digest。
- Test Plan / receipt / results 全部机器可读；AGY 不再手工定义正式 exit、PASS 或 measured values。
- `run-frozen-check.sh` 实际执行冻结 argv；`validate-run-state.sh` 负责状态与完成判定。
- business applicability 与 environment prerequisite 分开：业务不适用才 N/A，缺浏览器/认证/依赖是 BLOCKED。
- `COMPLETE` 是终态；测试修代码必须 invalidate → TEST_REWORK → Astra 重审 → 新计划 → 重测。

## 核心文件

```text
SKILL.md
resources/development-contract.md
resources/run-state.md
resources/agy-execution.md
resources/code-review.md
resources/testing.md
schemas/development-contract.schema.json
schemas/snapshot-policy.schema.json
schemas/run-state.schema.json
schemas/test-plan.schema.json
schemas/test-receipt.schema.json
schemas/test-results.schema.json
scripts/snapshot-code-state.sh
scripts/run-frozen-check.sh
scripts/validate-run-state.sh
```

## 验证策略

alpha.3 默认 readiness **只检查代码与工作流逻辑的一致性**：文件结构、JSON 可解析性、版本、活跃角色依赖、schema 关键字段和 runtime entrypoint wiring。它不执行 Python fixture、`py_compile` 或 Python 行为回归，也不会把静态逻辑检查冒充真实运行证明。

Python 文件仍是 snapshot / runner / completion 的运行实现。真实正确性由真实任务或一次性临时仓库 smoke 单独证明。

```bash
bash scripts/test-readiness.sh
bash scripts/test-readiness.sh --environment   # 额外检查 Herdr 环境
```

默认输出区分：

```text
STATIC_LOGIC_VALID
ENVIRONMENT_READY
PYTHON_BEHAVIOR_CHECKS
FLOW_VERIFIED
SEMANTIC_EVALS
```

## 迁移

alpha.2 及更早 Run State 缺少 contract/policy/receipt 绑定时不能自动补成 PASS。应从当前仓库状态重建需要的身份关系，重新 Code Review、冻结计划并重新执行正式 checks。
