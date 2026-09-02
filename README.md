# AGY Supervised Development 3.2

当前开发版本：**3.2.0-alpha.3**

一个串行、简单的监督式开发插件：

```text
Codex 负责方案、评审、验证和最终裁决
Sol High 只负责实现前的方案评审
AGY 负责实现
Git / Tests / Runtime Evidence 负责证明交付
```

> **Codex shapes and proves. AGY builds. Git tells the truth.**

## 主流程

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
→ SOL HIGH PLAN REVIEW
→ PLAN FROZEN
→ BUILD
→ THREE-AXIS REVIEW
→ VERIFY
→ CLOSEOUT
→ ACCEPTED
```

如果用户明确要求跳过 Sol 方案评审：

```text
SLICE
→ PLAN FROZEN
→ BUILD
```

## Sol High Plan Review

默认开启。

```text
Codex Executable Plan
→ Chrome DevTools MCP
→ ChatGPT Web
→ GPT-5.6 Sol + High
→ Sol Review
→ Codex Adopt / Reject / Modify
```

最多 **3 轮 Sol Review**，但可以提前结束：

```text
PASS                     → PLAN FROZEN
only non-blocking notes  → PLAN FROZEN
USER_DECISION_REQUIRED   → ask user
round 3 still blocking   → ask user, never round 4
```

Codex 永远是 Plan Owner。Sol High 不直接拥有最终方案。

一旦进入：

```text
PLAN FROZEN
```

Sol High 立即退出本次任务，后续 AGY Build / Review / Rework / Verify / Closeout 均不再调用 Sol High。

详见 `resources/sol-plan-review.md` 和独立仓库 `suicuney/sol-consult-skill` 中的 `sol-high-plan-review` Skill。

## 安装

```bash
codex plugin marketplace add suicuney/agy-supervised-development --ref codex/agy-supervised-v3.2-pluginized
codex plugin add agy-supervised-development@agy-supervised-development
```

## AGY Runtime

```text
PLAN FROZEN
→ Codex Execution Unit
→ scripts/agy-run.sh
→ official AGY CLI
→ Repository
```

`agy-run.sh` 只是薄实现适配器，不再包含 consult mode，也不负责 workflow state、review 或 acceptance。

需要真实交互时才使用 tty7。

## Review

AGY 完成后，Codex 独立执行：

```text
A. Spec Fidelity
B. Engineering Quality
C. Completeness
```

```text
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
```

Sol High 不参与这里的 Review。

## Verification / Chrome DevTools MCP

实现后，Codex 根据 Verification Seam 独立验证：

```text
lint / typecheck / build
unit / integration / e2e
original repro
browser runtime when applicable
```

对于 browser-facing 任务，Chrome DevTools MCP 可作为 Codex-owned runtime verification adapter。

因此同一个 MCP 有两个严格分开的使用阶段：

```text
Before PLAN FROZEN:
Chrome DevTools MCP → ChatGPT Web → Sol High Plan Review

After AGY Review PASS:
Chrome DevTools MCP → target Web system → Runtime Verification
```

不新增 MCP manager 或第二套 orchestration。

## Active Structure

```text
skills/agy-supervised-development/SKILL.md
SKILL.md

resources/
├── task-sizing.md
├── shaping.md
├── spec-contract.md
├── execution-slicing.md
├── sol-plan-review.md
├── agy-execution.md
├── tty7-supervision.md
├── bugfix-workflow.md
├── review-gates.md
├── completeness-regression.md
├── runtime-verification.md
└── closeout-governance.md

templates/
├── execution-unit.md
├── review-report.md
├── rework-contract.md
├── browser-verification.md
└── closeout-contract.md
```

## 自检

```bash
scripts/test-readiness.sh
```

## 原则

```text
串行
小步
简单
一个 Writer
一个 Plan Owner
Sol 只评方案
方案冻结后 Evidence > 额外模型意见
同一条规则只定义一次
```
