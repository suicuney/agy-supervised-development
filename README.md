# AGY Supervised Development 3.2 — Pluginized Runtime

当前开发版本：**3.2.0-alpha.1**

这是一个以 **Codex App 负责 Shape / Spec / Review / Verification，官方 AGY CLI 负责实现，Git Repository 负责事实证明** 的监督式开发插件。

> **Codex shapes and proves. AGY builds. Git tells the truth.**

v3.2 不重写 v3.1 已稳定的 Workflow Kernel，而是在其上增加 **Codex Plugin Packaging、Thin AGY Adapter、Deterministic Validation、Review Convergence 和 Optional AGY Consult**。

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

运行边界：

```text
Codex
  ↓ Execution Unit
scripts/agy-run.sh            # thin adapter only
  ↓
official AGY CLI / stream-json
  ↓
Repository
  ↓
Codex Three-Axis Review
  ↓
Independent Verification
  ↓
Knowledge Closeout
  ↓
ACCEPTED
```

`tty7 + AGY TUI` 仍只在 login、permissions、manual approval、resume picker 或 TUI-only 行为真正需要交互时作为 fallback。

## v3.2 Alpha 1 新增

### 1. Codex Plugin Packaging

仓库现在可以作为 Codex Plugin marketplace source：

```bash
codex plugin marketplace add suicuney/agy-supervised-development --ref codex/agy-supervised-v3.2-pluginized
codex plugin add agy-supervised-development@agy-supervised-development
```

插件入口：

```text
.agents/plugins/marketplace.json
.codex-plugin/plugin.json
skills/agy-supervised-development/SKILL.md
```

根目录 `SKILL.md + resources/ + templates/` 仍是现有 Workflow Kernel 的单一权威来源；插件 Skill 是 v3.2 入口，不复制整套 Kernel，避免双真相源。

### 2. Thin AGY Adapter

新增：

```text
scripts/agy-run.sh
```

它只统一：

- repository binding；
- build / consult mode；
- timeout；
- conversation id；
- add-dir；
- official `stream-json` 输出。

示例：

```bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --timeout 30m \
  "<Execution Unit>"
```

返工：

```bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --conversation "$agy_conversation_id" \
  "<Rework Contract>"
```

Wrapper **不是** custom harness、daemon、Run Store、session DB 或 acceptance engine。AGY 官方 CLI 仍是 Runtime integration boundary。

### 3. Review Convergence

新增 `resources/review-convergence.md`。

Three-Axis Review 仍独立形成：

```text
A Spec Fidelity
B Engineering Quality
C Completeness
```

随后可把 finding 分类为：

```text
BLOCKING
NON_BLOCKING
BACKLOG
```

当没有 unresolved BLOCKING finding 时，Codex 可以记录：

```text
NO_BLOCKING_FINDINGS
```

但必须牢记：

```text
NO_BLOCKING_FINDINGS != ACCEPTED
REVIEW PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
```

Independent Verification 与 Knowledge Closeout 仍不可跳过。

### 4. Optional AGY Consult

新增 `resources/agy-consult.md`，用于只读第二意见：

```bash
scripts/agy-run.sh \
  --repo "$repo_root" \
  --mode consult \
  "Review this implementation plan for hidden risks."
```

适合：

- plan challenge；
- difficult code-path analysis；
- blast-radius second opinion；
- root-cause hypothesis comparison。

AGY Consult 只产生 advisory evidence，不能替代 Codex Three-Axis Review、Verification、Closeout 或 Acceptance。

### 5. Deterministic Validation

新增：

```text
scripts/validate-structure.sh
scripts/validate-docs.sh
scripts/validate-runtime.sh
scripts/test-readiness.sh
```

本地完整自检：

```bash
scripts/test-readiness.sh
```

覆盖：

```text
plugin manifest / marketplace JSON
required files
script executable bits
bash syntax
plugin metadata/version
README contract
plugin-skill routing
agy-run argument behavior
consult read-only prefix
conversation/add-dir forwarding
```

这和 `evals/` 的职责不同：

```text
Deterministic Validators = 文件、manifest、wrapper、docs contract 的确定性检查
Semantic Evals            = Workflow、Review、状态迁移、Agent 行为的语义回归
```

两者共同组成 v3.2 的自验证层。

## v3.1 Kernel 保持不变的核心边界

- 只有 Codex 可以 `ACCEPTED`；
- Workflow 与 Runtime 解耦；
- AGY 是 Primary Writer，不是 Product Owner；
- Repository state 是交付真相；
- `AGY SUCCESS != REVIEW PASS`；
- Three-Axis Review 不做平均分；
- Verification 独立于 Review；
- CODE_VERIFIED 后仍必须 Knowledge Closeout；
- tty7 是 interactive fallback；
- 默认不使用 `--dangerously-skip-permissions`；
- 不 push / merge / release / deploy / production write，除非用户明确授权。

## Active Files

```text
SKILL.md                         # v3.1 workflow kernel, canonical workflow source
skills/agy-supervised-development/SKILL.md  # v3.2 plugin entrypoint

.agents/plugins/marketplace.json
.codex-plugin/plugin.json

resources/
├── agy-execution.md
├── agy-consult.md
├── review-convergence.md
├── task-sizing.md
├── shaping.md
├── spec-contract.md
├── execution-slicing.md
├── review-gates.md
├── completeness-regression.md
├── bugfix-workflow.md
├── closeout-governance.md
├── run-lifecycle.md
├── failure-modes.md
├── tty7-supervision.md
└── pi-interaction.md

scripts/
├── agy-run.sh
├── validate-structure.sh
├── validate-docs.sh
├── validate-runtime.sh
└── test-readiness.sh

templates/
├── execution-unit.md
├── review-report.md
├── rework-contract.md
└── closeout-contract.md

evals/
├── README.md
└── scenarios.json
```

## Definition of Done

```text
DONE
=
Spec satisfied
+ Engineering Quality PASS
+ Completeness PASS
+ NO unresolved blocking findings
+ Independent Verification PASS
+ Regression/Bug Proof satisfied when applicable
+ Knowledge aligned
+ Deterministic readiness checks satisfied when applicable
+ Baseline preserved
+ No unauthorized one-way/external side effects
```

最终仍只有 Codex 可以标记：

```text
ACCEPTED
```
