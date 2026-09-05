# AGY Supervised Development 3.3

当前开发版本：**3.3.0-alpha.2**

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

## 计划评审时你会看到什么

发送给网页版 GPT 前，只展示一份简洁中文计划：

```text
【准备发送给 Sol High 的计划】

目标
- 这次要完成什么

计划
1. 关键步骤
2. 关键步骤
3. 关键步骤

重点风险
- 真正需要注意的风险
```

这时只确认**一次**是否发送。

第一轮已经确认后，如果 Sol High 返回 `REVISE`，Codex 会自行 `Adopt / Reject / Modify` 并继续下一轮，不会每轮重新要求确认。只有真正需要用户决定的产品/架构/one-way 问题才会打断。

评审收敛后，再展示一份中文最终计划：

```text
【最终执行计划】

Sol High 评审：PASS / 已收敛
评审轮次：2

最终计划
1. ...
2. ...
3. ...

评审后的主要调整
- ...
```

这里只展示，不再次确认。随后自动：

```text
PLAN FROZEN
→ BASELINE
→ AGY BUILD
```

不会再用 packet 字符数、文件大小或附件大小代替真正的计划内容。

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

3.3 要求 Herdr、`agy` 和 `jq` 已安装，并要求官方 Antigravity integration 可用。Herdr 当前正式支持 `agent start --kind agy`。

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
jq executable
Herdr server reachable
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
→ 中文简版计划
→ 用户确认一次
→ Chrome DevTools MCP
→ ChatGPT Web
→ GPT-5.6 Sol + High
→ Sol Review
→ Codex Adopt / Reject / Modify
→ 中文最终计划
→ PLAN FROZEN
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
2. 首轮 Sol Send 前 = 中文简版计划 + 一次确认
3. 后续 REVISE = 自动继续，不重复确认
4. Sol 收敛后 = 中文最终计划，只展示不确认
5. Herdr preflight = HERDR_READY
6. PLAN FROZEN before AGY writes
7. Baseline captured before AGY writes
8. Herdr workspace cwd = repo_root
9. pane ID = Herdr create response, never guessed
10. AGY launched with --kind agy
11. blocked → read before interaction
12. Herdr done/idle = runtime evidence only
13. Git + Codex Review + independent Verify = delivery evidence
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
Sol 首轮发送只确认一次
最终计划必须中文可见
Herdr 管运行，不管结论
Sol 只评方案
Git 是 repository truth
```
