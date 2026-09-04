# AGY Supervised Development 3.3

当前开发版本：**3.3.0-alpha.1**

一个串行、单 Writer、Herdr-only 的监督式开发插件：

```text
Codex 负责方案、评审、验证和最终裁决
Sol High 只负责实现前的方案评审
Herdr 负责 AGY 的运行、交互、状态和会话恢复
AGY 负责实现
Git / Tests / Runtime Evidence 负责证明交付
```

> **Codex governs. Herdr runs. AGY builds. Git tells the truth.**

## 主流程

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
→ SOL HIGH PLAN REVIEW
→ PLAN FROZEN
→ BASELINE
→ AGY BUILD          # Herdr only
→ THREE-AXIS REVIEW
→ VERIFY
→ CLOSEOUT
→ ACCEPTED
```

## 3.3 的核心变化

3.3 只有一条 AGY 执行链：

```text
AGY Supervised Development
→ Herdr
→ Antigravity CLI / AGY
→ Repository
→ Git
→ Codex Review / Verify
```

不再维护第二套 AGY Runtime，也不再保留 Runtime selection。Herdr 是基础设施，不是 Supervisor。

```text
Herdr done != REVIEW PASS
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
```

## 安装插件

```bash
codex plugin marketplace add suicuney/agy-supervised-development --ref codex/agy-supervised-v3.3-herdr-runtime
codex plugin add agy-supervised-development@agy-supervised-development
```

## Herdr / Antigravity 一次性准备

3.3 要求 Herdr 和 `agy` 已安装，并要求官方 Antigravity integration 可用。

显式安装 integration：

```bash
herdr integration install antigravity-cli
```

这个命令会修改当前用户的 Antigravity hooks 配置，因此插件任务执行阶段不会偷偷安装或覆盖它。

启动 Herdr（交互使用 `herdr`，服务式环境可使用 `herdr server`），然后检查：

```bash
scripts/check-herdr.sh
```

预检会确认：

```text
herdr executable
agy executable
Herdr server reachable
Herdr supports --kind agy
Antigravity integration present and usable
```

失败就 `BLOCKED`，不会绕开 Herdr 直接启动 AGY。

## AGY Runtime

AGY Build 固定使用 Herdr Agent API：

```text
PLAN FROZEN
→ BASELINE
→ herdr workspace create --cwd <repo_root>
→ capture returned root pane ID
→ herdr agent start <task-agent> --kind agy --pane <pane_id>
→ herdr agent prompt ... --wait
→ blocked 时先 read 再最小交互
→ agent read
→ Git Review
```

Herdr workspace 创建响应中的：

```text
.result.workspace.workspace_id
.result.root_pane.pane_id
```

是本轮 Runtime 身份来源，不从 UI 顺序猜 ID。

Antigravity integration 会在首个 prompt 后报告 native conversation identity；Herdr 可在 server restart 后按该 identity 恢复 AGY session。插件自身不再维护 AGY conversation 恢复命令。

详见 `resources/agy-execution.md`。

## Sol High Plan Review

默认开启：

```text
Codex Executable Plan
→ Chrome DevTools MCP
→ ChatGPT Web
→ GPT-5.6 Sol + High
→ Sol Review
→ Codex Adopt / Reject / Modify
```

最多 3 轮；`PLAN FROZEN` 后 Sol High 立即退出任务。

首次运行前检查独立 Sol Skill：

```bash
scripts/check-sol-plan-review.sh
```

如果缺失，再显式运行：

```bash
scripts/install-sol-plan-review.sh
scripts/check-sol-plan-review.sh
```

## Review / Verification

AGY runtime settled 后，Codex 独立执行：

```text
A. Spec Fidelity
B. Engineering Quality
C. Completeness
```

通过后再独立运行：

```text
lint / typecheck / build
unit / integration / e2e
original repro
browser runtime when applicable
```

对于 browser-facing 任务，Chrome DevTools MCP 仍是 Codex-owned runtime verification adapter。

## 运行前快速清单

```text
1. Sol dependency = COMPLETE（除非用户明确跳过 Sol review）
2. Herdr preflight = HERDR_READY
3. PLAN FROZEN before AGY writes
4. Baseline captured before AGY writes
5. Herdr workspace cwd = repo_root
6. pane ID = Herdr create response, never guessed
7. AGY launched with --kind agy
8. blocked → read before interaction
9. Herdr done/idle = runtime evidence only
10. Git + Codex Review + independent Verify = delivery evidence
```

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
├── failure-modes.md
├── bugfix-workflow.md
├── review-gates.md
├── completeness-regression.md
├── runtime-verification.md
└── closeout-governance.md

scripts/
├── check-herdr.sh
├── check-sol-plan-review.sh
├── install-sol-plan-review.sh
├── test-sol-plan-review.sh
├── validate-structure.sh
├── validate-docs.sh
├── validate-runtime.sh
└── test-readiness.sh
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
一个 AGY Runtime：Herdr
Herdr 管运行，不管结论
Sol 只评方案
Git 是 repository truth
```
