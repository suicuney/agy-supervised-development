# Knowledge Closeout Governance — v3.3

本文件定义 AGY 完成实现、Codex 完成 **Three-Axis Review + Independent Verification** 之后的知识收尾协议。

目标不是“多写文档”，而是确保最终代码事实、项目文档、Agent 规则、外部 Contract 和工作区状态一致，然后才允许 Codex 进入 `ACCEPTED`。

## 1. 职责边界

```text
Codex = 决定知识影响面、生成 Closeout Contract、审查 diff、最终验收
Herdr = 唯一 AGY runtime；只负责运行/交互/session continuity
AGY   = 仅在确实需要修改知识文件时执行 bounded Closeout Contract
Git   = repository truth
```

Completeness Review 负责“代码世界有没有漏改”；Closeout 负责“知识世界有没有同步”。

Herdr 不拥有 Closeout verdict。

## 2. Definition of Done

```text
TASK DONE
=
Implementation Verified
+ Change Propagation Complete
+ Test Strategy Verified
+ Regression Proof Verified / N/A
+ Independent Verification
+ Knowledge Aligned
+ Rules Aligned
+ No Unexplained Residue
```

```text
REVIEW PASS
→ CODEX VERIFY
→ CODE_VERIFIED
→ CLOSEOUT
→ ACCEPTED
```

`CODE_VERIFIED` 表示代码层稳定，不等于最终完成。

## 3. 每次开发都 Scan，不是每次都改文档

每个相关知识面使用：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

纯内部 bugfix 可以没有文档 diff，只要受影响知识面已核对为 current。

## 4. Source of Truth 顺序

1. 当前 branch / final diff；
2. 当前 code/schema/config/tests；
3. Completeness / blast-radius evidence；
4. Codex 已实际验证的 command/runtime result；
5. 项目现役 Contract / generated schema；
6. README/docs/rules；
7. AGY Worker summary / 旧计划 / 历史说明。

旧文档与已验证 implementation 冲突时，以最终实现为准；若产品预期无法裁决，标 `pending`，不要把猜测写成事实。

## 5. 默认检查知识面

```text
README / Usage
AGENTS.md / CLAUDE.md / project rules
API / schema / event / shared contracts
env / flags / runtime config / runbook
architecture responsibilities when affected
workspace residue / debug artifacts / credential leaks
```

来源或安全性不明确的残留只列 `deletion-candidate`，不擅自删除。

## 6. Lightweight / Full Closeout

### Lightweight — 默认

1. 读取 final diff / changed paths；
2. 读取 Completeness 的 knowledge impact；
3. 分类相关知识面；
4. 只有确实 stale 时才要求 AGY 修改；
5. Codex Review 新 diff。

### Full — 以下情况自动升级

```text
public API / protocol
schema / migration / persistence contract
CLI
env / flag / runtime behavior
用户流程 / 权限
模块职责 / 架构边界
service / deploy / port / background job
rename / retirement
cross-project shared protocol
```

Full Closeout 需要搜索旧 symbol/contract，更新唯一权威文档，再搜索一次 stale references。

## 7. Closeout Contract

模板见：

```text
../templates/closeout-contract.md
```

如果需要 AGY 修改知识文件，**必须继续走当前 Herdr-managed AGY worker**：

```bash
herdr agent prompt "$agy_agent" "$closeout_contract" \
  --wait \
  --until idle \
  --until done \
  --until blocked \
  --timeout "$timeout_ms"
```

如果 `blocked`，先：

```bash
herdr agent read "$agy_agent" --source recent-unwrapped --lines 120
```

再按既有授权边界做最小交互。

Closeout Contract 必须限制：

```text
Allowed = directly affected knowledge surfaces
Forbidden = unrelated production redesign / new feature / destructive cleanup / push / merge / deploy
```

## 8. Session continuity

Herdr 的 Antigravity integration 负责 native AGY session identity 和 restore。Closeout 不直接调用 AGY resume 命令。

如果 exact session 无法恢复：

```text
Do not guess another conversation.
```

保留 final verified repository facts。确实需要继续写文档时，只能启动新的 **Herdr-managed AGY**，并显式重新提供 Closeout Contract、final diff、verified behavior 和 scope。

## 9. Closeout Runtime Evidence

```text
Herdr done / idle
AGY self-report
```

只表示 runtime settled，不等于 Closeout PASS。

Codex 必须自己检查：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

必要时：

```bash
rg "<old-symbol|route|env|field|service>" .
```

确认：

- docs 与 final implementation 一致；
- 未验证行为没写成已完成；
- 没为形式制造无意义 Markdown diff；
- rules 没膨胀成第二 README；
- Contract/schema/examples 没冲突；
- retired symbol 不残留于现役面；
- residue 如实报告且无未经授权删除；
- runtime output/credential 没意外进入 Git；
- Closeout 修改没破坏 baseline 或 Scope。

## 10. Closeout 发现代码缺陷

如果知识审查揭示真实代码问题：

```text
CLOSEOUT
→ REWORK_REQUIRED
→ same Herdr-managed AGY
→ THREE-AXIS REVIEW
→ CODEX VERIFY
→ CLOSEOUT again
```

不能只改文档掩盖错误实现。

## 11. Verdict

### PASS

```text
CLOSEOUT PASS
- 所有相关知识面已分类
- 受影响知识面与 verified implementation 一致
- pending/out-of-scope/residue 已报告
```

### REWORK

```text
Issue
Evidence
Expected
Required Change
Re-run
```

### BLOCKED

```text
Blocker
Evidence
Safe state
Decision needed
```

只有 Review、Independent Verification、Knowledge Closeout 和安全边界全部满足，Codex 才能 `ACCEPTED`。

## 12. 不默认纳入

Closeout 不自动获得：

- Agent memory 写入/清理；
- production deploy/live verification；
- remote branch/PR/release cleanup；
- 删除用户文件/历史资料；
- cross-project write；
- release announcement/changelog（除非 Spec/项目规则要求）。
