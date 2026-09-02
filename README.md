# AGY Supervised Development 3.2 — Pluginized Runtime

当前开发版本：**3.2.0-alpha.2**

这是一个以 **Codex App 负责 Shape / Spec / Review / Verification，官方 AGY CLI 负责实现，Git Repository 负责事实证明** 的监督式开发插件。

> **Codex shapes and proves. AGY builds. Git tells the truth.**

v3.2 不重写 v3.1 已稳定的 Workflow Kernel，而是在其上增加 **Codex Plugin Packaging、Thin AGY Adapter、Deterministic Validation、Review Convergence、Optional AGY Consult，以及 Browser Runtime Verification Capability Negotiation**。

## 主流程

```text
INTAKE
→ SIZE
→ RUNTIME CAPABILITY DETECTION / NEGOTIATION   # browser-runtime applicable only
→ SHAPE
→ SPEC
→ SLICE
→ BUILD
→ THREE-AXIS REVIEW
→ INDEPENDENT VERIFY
   ├─ Static / Automated
   ├─ Browser Runtime when applicable
   └─ Regression Proof
→ CLOSEOUT
→ ACCEPTED
```

浏览器能力有两个受控入口：

```text
Complex Bug DIAGNOSE
  └─ Chrome DevTools MCP      # optional, when allowed

Independent Verification
  └─ Chrome DevTools MCP      # optional/applicable runtime adapter
```

核心边界不变：

```text
AGY = Primary Writer
Codex = Reviewer / QA / Runtime Verifier / Final Acceptance
Chrome DevTools MCP = Codex-owned optional Runtime Verification Adapter
```

## v3.2 Alpha 2 新增

### 1. Runtime Capability Negotiation

新增 `resources/runtime-verification.md`。

当任务存在 Web / Browser / Chrome Extension 等运行时验收价值时，Codex 在 **Spec freeze 之前** 判断 Browser Runtime 是否适用。

如果适用且没有既有有效偏好，则询问用户：

```text
Enable
Disable
Auto-decide
```

不适用的纯后端 / CLI / SQL / Library 等任务不机械询问 Chrome DevTools MCP。

偏好优先级：

```text
current task override
> project preference
> global/default preference
```

只有用户明确要求“记住这个项目的选择”时，才应写入项目级持久偏好；不要擅自新增配置文件。

### 2. Chrome DevTools MCP as Runtime Verification Adapter

Chrome DevTools MCP 不进入 AGY Writer 路径，而作为 Codex 的可选 Runtime Verification Adapter。

适合检查：

```text
真实页面操作
Console/runtime errors
Network 4xx/5xx / request-response contract
表单、路由、登录态、浏览器存储
frontend ↔ backend interaction
刷新后的持久化状态
Chrome Extension behavior
Performance when performance is part of the Spec
```

截图只是 evidence 的一种，**Screenshot alone != functional proof**。

### 3. Browser Verification Contract

新增：

```text
templates/browser-verification.md
```

用于固定：

```text
Target / Environment
Preconditions
Critical Journey
Assertions
Console expectations
Network expectations
Persistence evidence
Performance applicability
Verdict / Re-run
```

Runtime verification 失败形成普通 `V*` finding：

```text
VERIFYING
→ V* finding
→ REWORK_REQUIRED
→ AGY
→ THREE-AXIS REVIEW AGAIN
→ VERIFY AGAIN
```

不能因为浏览器重新跑绿了就绕过 Three-Axis Review。

### 4. Provider Unavailable / Fallback

Chrome DevTools MCP 不是 AGY 3.2 的硬依赖。

如果本次已经选择 Browser Runtime Verification，但 provider 不可用：

```text
TOOL_UNAVAILABLE
→ 尝试已批准的 equivalent seam（existing E2E / API integration / manual browser evidence 等）
→ 不允许静默降低 required acceptance criterion
```

如果 Spec 明确要求 Browser Runtime，而没有等价证据，则不能发出 `CODE_VERIFIED`。

### 5. Security Boundary

DevTools 连接的浏览器可能暴露：

```text
Cookie / session
request headers
response bodies
页面敏感数据
authenticated runtime state
```

因此默认倾向：

```text
独立测试浏览器 / Profile
避免个人和生产登录态
不把 MCP 能访问解释成允许 production mutation
不在日志和最终报告泄露凭据
```

浏览器运行时能力不覆盖原有 one-way / external side-effect 授权规则。

## v3.2 Alpha 1 基础能力

### Codex Plugin Packaging

仓库可以作为 Codex Plugin marketplace source：

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

根目录 `SKILL.md + resources/ + templates/` 仍是 Workflow Kernel 的权威来源；插件 Skill 作为 v3.2 overlay 入口，不复制整套 Kernel。

### Thin AGY Adapter

`scripts/agy-run.sh` 只统一 repository binding、build/consult mode、timeout、conversation id、add-dir 和 official `stream-json` 输出，不是 custom harness / daemon / run store / acceptance engine。

### Review Convergence

`resources/review-convergence.md` 支持：

```text
BLOCKING
NON_BLOCKING
BACKLOG
```

`NO_BLOCKING_FINDINGS != ACCEPTED`。

### Optional AGY Consult

`resources/agy-consult.md` 提供只读 second opinion；不能替代 Codex Review、Verification 或 Acceptance。

### Deterministic Validation

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

## Active Files

```text
SKILL.md
skills/agy-supervised-development/SKILL.md

.agents/plugins/marketplace.json
.codex-plugin/plugin.json

resources/
├── agy-execution.md
├── agy-consult.md
├── runtime-verification.md          # Alpha 2
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
├── browser-verification.md          # Alpha 2
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
+ Required Browser Runtime seam exercised when applicable
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
