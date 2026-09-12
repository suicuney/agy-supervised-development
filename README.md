# AGY Supervised Development 4.0

当前开发版本：**4.0.0-alpha.2**

> **Astra decides. Luna supervises. AGY builds. Git proves.**

4.0 的目标只有一个：**把昂贵推理放在决策点，把便宜模型放在监督循环，把实现细节交给 AGY。**

## Flow

```text
USER
→ ASTRA: CONTRACT
→ LUNA: SUPERVISE
→ AGY: BUILD + TEST + SELF-REVIEW
→ LUNA: VERIFY
→ ACCEPT
```

只有 Contract 本身出问题才回 Astra：

```text
LUNA → ASTRA: PATCH CONTRACT → LUNA → AGY
```

## Development Contract

Astra 默认只产出：

```yaml
goal: <目标>
behavior: [<可观察结果>]
constraints: [<重要边界>]
done: [<完成证据>]
escalate_if: [<契约级 blocker>]
```

不默认写文件级施工步骤，不默认扫描整个仓库。`CONTRACT FROZEN` 冻结结果、边界和完成标准；AGY 自己决定正常 `HOW`。

## Luna

Luna 默认只看：

```text
Contract + Git diff/status + AGY result + relevant test/runtime output
```

普通 bug、lint/test failure、实现选择由 Luna + AGY 解决。只有需求歧义、架构冲突、明显 scope/risk 扩张、重复核心失败、不可逆决策才升级 Astra。

## Runtime / Verification

Herdr 继续是唯一 AGY runtime。Git 是 repository truth。AGY 必须 self-review，但 Luna 仍独立验证。

验证顺序：

```text
Contract → diff → targeted verification → broader inspection only if needed
```

Sol High 旧评审资源暂时保留为 optional guarded capability，不进入默认链路。

## Install

```bash
codex plugin marketplace add suicuney/agy-supervised-development --ref codex/agy-supervised-v4-astra-skill
codex plugin add agy-supervised-development@agy-supervised-development
```

## Core Files

```text
SKILL.md
resources/development-contract.md
resources/supervisor.md
resources/agy-execution.md
resources/verification.md
schemas/development-contract.schema.json
```

需要哪个阶段才读取哪个资源，不预加载整套流程。

## Check

```bash
scripts/test-readiness.sh
```
