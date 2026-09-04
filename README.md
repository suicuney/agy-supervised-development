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

# 首次运行前检查独立的 Sol High plan-review skill
scripts/check-sol-plan-review.sh
# 若返回 MISSING，再显式安装完整私有源并复查
scripts/install-sol-plan-review.sh
scripts/check-sol-plan-review.sh
```

`SKILL.md` 单独存在不代表依赖完整；检查器会核对版本化 manifest 中的全部 references、scripts、tests 和元数据文件。安装器只做全量 checkout，不覆盖已有目录。若返回 `INCOMPLETE`，先保留并报告该目录，确认是失败安装产物后移走，再重新安装；不要自动删除或覆盖。

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

AGY 运行前必须同时确认 `init.cwd` 和首个实际命令的 `pwd`/repository root/branch。Headless 写入被拒绝时，保留真实 conversation id，转 tty7 做一次性批准；CLI 以错误结束也先查 Git，再由 Codex Review 和独立验证判断。

本次运行的最短 fallback 顺序：

```text
headless AGY
→ 检查 init + command cwd
→ 检查 stream result / tool error / Git
→ 必要时 tty7 one-off approval
→ Codex Review / Verify
```

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

## 运行前快速清单

```text
1. Sol dependency = COMPLETE
2. Codex plan packet = safety check passed
3. ChatGPT Web = authenticated in the approved browser session
4. Model = GPT-5.6 Sol; reasoning = High
5. Unrelated user tabs = untouched
6. Send = one action-time confirmation; UNKNOWN = no retry
7. AGY init cwd + command cwd = verified
8. AGY result = runtime evidence only; Git + Codex Review = delivery evidence
```

自动化可以准备 packet、扫描安全性、确认模型和填充草稿；外部 Send 仍保留最后的明确确认。

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
├── sol-plan-review-manifest.json
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
