# AGY Supervised Development 3.2

当前开发版本：**3.2.0-alpha.2**

一个简单的监督式开发插件：

```text
Codex 负责想清楚、拆清楚、验清楚
AGY 负责实现
Git 负责提供仓库事实
```

> **Codex shapes and proves. AGY builds. Git tells the truth.**

## 主流程

```text
SIZE
→ SHAPE
→ SPEC
→ SLICE
→ BUILD
→ THREE-AXIS REVIEW
→ VERIFY
→ CLOSEOUT
→ ACCEPTED
```

核心边界：

```text
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
```

只有 Codex 可以最终标记 `ACCEPTED`。

## 安装

```bash
codex plugin marketplace add suicuney/agy-supervised-development --ref codex/agy-supervised-v3.2-pluginized
codex plugin add agy-supervised-development@agy-supervised-development
```

## Runtime

默认实现路径：

```text
Codex
→ Execution Unit
→ scripts/agy-run.sh
→ official AGY CLI
→ Repository
→ Codex Review / Verification
```

`agy-run.sh` 只是薄适配器，不负责 workflow state、review 或 acceptance。

需要交互时才使用 `tty7 + AGY TUI`，例如 login、permissions、manual approval 或 TUI-only 行为。

## Review

Codex 独立执行 Three-Axis Review：

```text
A. Spec Fidelity
B. Engineering Quality
C. Completeness
```

Finding severity 和 `NO_BLOCKING_FINDINGS` 收敛规则统一定义在：

```text
resources/review-gates.md
```

Review PASS 后仍必须执行 Independent Verification。

## Browser Runtime Verification

对于 Web UI、浏览器集成、Chrome Extension、Console / Network 问题等 browser-facing 任务，可选使用 Chrome DevTools MCP。

规则很简单：

```text
Browser applicable?
  ├─ No  → skip
  └─ Yes
       ↓
No effective preference?
       ↓
Ask before Spec freeze:
Enable / Disable / Auto-decide
```

Chrome DevTools MCP 属于 **Codex verification capability**，不是 AGY writer dependency。

它只有两个使用点：

```text
Complex browser bug → DIAGNOSE
Review PASS          → Independent Runtime Verification
```

如果必需的 browser verification 无法执行，且没有等价 verification seam，就不能标记 `CODE_VERIFIED`。

详见：

```text
resources/runtime-verification.md
templates/browser-verification.md
```

## Optional AGY Consult

需要第二意见时可使用只读 Consult：

```bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --mode consult \
  "Review this implementation plan for hidden risks."
```

它只是 advisory evidence，不能替代 Codex Review / Verification。

## 自检

```bash
scripts/test-readiness.sh
```

只检查必要的机器契约：plugin manifest、必要文件、脚本语法和 runtime wrapper 行为。

## Active Structure

```text
skills/agy-supervised-development/SKILL.md
SKILL.md

resources/
├── task-sizing.md
├── shaping.md
├── spec-contract.md
├── execution-slicing.md
├── agy-execution.md
├── agy-consult.md
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

scripts/
├── agy-run.sh
├── validate-structure.sh
├── validate-docs.sh
├── validate-runtime.sh
└── test-readiness.sh
```

## 原则

```text
小步
串行
简单
同一条规则只定义一次
其他地方只引用
```
