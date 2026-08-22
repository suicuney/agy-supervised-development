# Knowledge Closeout Governance

本文件定义 Pi Worker 完成实现、Codex 完成 **Diff Review + Completeness Review + Regression/Test Proof + Independent Verification** 之后的知识收尾协议。

目标不是“多写文档”，而是确保最终代码事实、项目文档、Agent 规则、外部 Contract 和可解释的工作区状态一致，然后才允许 Codex 进入 `ACCEPTED`。

---

## 1. 职责边界

- **Pi Worker**：在 `closeout` operation 中修改受最终实现直接影响的 README/docs/rules/Contract/config 等知识文件；
- **Codex**：决定哪些知识面受影响、审查 Closeout diff、执行 stale-reference search，并最终验收；
- **Provider**：只提供模型推理，不拥有知识权威或 Closeout 生命周期；
- **Repository state**：首要真相来源。

Completeness Review 负责“代码世界有没有漏改”；Closeout 负责“知识世界有没有同步”。

---

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

状态：

```text
REVIEWING
  ↓
COMPLETENESS_REVIEW
  ↓
VERIFYING
  ↓
CODE_VERIFIED
  ↓
CLOSEOUT
  ↓
CLOSEOUT_REVIEW
  ↓
ACCEPTED
```

`CODE_VERIFIED` 表示代码层稳定，不等于最终完成。

---

## 3. Closeout 与 Completeness

```text
Completeness Sweep
- callers / consumers
- types / enums / validation / serialization
- schema / migration / existing data
- sibling flows / jobs
- reachable states / retry / fallback
- dead/orphaned old path
- tests

Knowledge Closeout
- README / usage
- AGENTS / CLAUDE / project rules
- API / schema / CLI / shared Contract docs
- env / config / runtime / deploy docs
- current-state examples
- workspace residue
```

Completeness 可以提前标 `Knowledge impact = affected`，真正的知识文件修改基于 final implementation 在 Closeout 执行。

---

## 4. 每次开发都 Scan，不是每次都改文档

每个相关知识面使用：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

纯内部 bugfix 可能得到：

```text
README              verified-current
AGENTS / CLAUDE     verified-current
API Contract        not-applicable
Architecture Docs   not-applicable
Residue             verified-current
```

这仍是合格 Closeout，即使没有 Markdown diff。

---

## 5. Source of Truth 顺序

1. 当前 branch / final diff；
2. 当前 code/schema/config/tests；
3. Completeness / blast-radius evidence；
4. Codex 已实际验证的 runtime/command result；
5. 项目现役 Contract / generated schema；
6. README/docs/rules；
7. Pi Worker summary / 旧计划 / 历史说明。

旧文档与已验证 final implementation 冲突时，以最终实现为准；若产品预期无法裁决，标 `pending`，不要把猜测写成权威事实。

---

## 6. 默认检查知识面

### A. Usage / README

安装、启动、调用、配置、使用方式是否仍正确。

### B. Agent Rules

检查：

- `AGENTS.md`；
- `CLAUDE.md`；
- 项目其他现役 Agent/development rules。

只同步“下次 Agent 不知道就容易做错”的稳定规则，不写开发流水账和已完成 TODO。

### C. Contract / Schema

API/route/request/response、DB schema、event/message schema、CLI contract、shared interface 改动必须核对权威 Contract、示例和 consumer-facing docs。

### D. Runtime / Configuration

env、ports、service names、provider/model、feature flags、deploy/run commands、cron/jobs 改动必须核对 runbook/示例配置。

### E. Workspace Residue

检查：

- PLAN/TODO/implementation notes；
- 临时 debug script；
- `*_old.*` / `*_backup.*`；
- generated artifacts；
- `.pi/supervised` runtime state 是否按约定 ignored；
- Evidence Bundle 是否含敏感信息。

来源/安全性不明确的文件只列 `deletion-candidate`，不擅自删除。

---

## 7. Lightweight / Full Closeout

### Lightweight — 默认

1. 读取 final diff / changed paths；
2. 读取 Completeness `Knowledge impact`；
3. 判断 README/rules/Contract/runtime/config/residue；
4. 分类每个知识面；
5. 需要修改时由同一 Pi Run 创建 `mode=closeout` operation；
6. Codex Review 新 diff。

### Full — 自动升级

出现任一：

- API/public Contract；
- schema/migration/persistence contract；
- CLI；
- env/provider/model/flag；
- 用户流程/权限/navigation；
- 模块职责/架构边界/重大重构；
- deploy/service/port/background job；
- rename/retirement；
- cross-project shared protocol。

完整路径额外：

1. 提取旧/新 symbol；
2. `rg` 或等价搜索非历史 stale reference；
3. 查权威文档索引和 consumer-facing knowledge；
4. 就地更新权威文档，不创建平行版本；
5. 再搜索旧 symbol；
6. 无法编辑的跨项目影响标 `out-of-scope`。

---

## 8. Change → Knowledge Routing

| 变化 | 优先核对 |
|---|---|
| API / route / protocol | API/集成说明、鉴权、示例、consumer contract |
| schema / storage field | 数据模型、migration、读写边界、测试说明 |
| env / provider / model / flag | 示例配置、默认值、运行和回退说明 |
| CLI / command | README、usage、examples、automation scripts |
| 用户流程 / 权限 / navigation | 产品说明、权限说明、UI/caller docs |
| 模块边界 / 重构 | architecture、rules 中目录职责、开发约定 |
| service / deploy / port | runbook、启动命令、服务名、smoke/rollback |
| job / scheduler | 调度、失败处理、告警/运维入口 |
| rename / retirement | 旧 symbol 现役引用、rules、consumer、examples |

---

## 9. 单一权威事实

- 同一现役事实尽量只保留一个权威解释；
- 其他位置只留摘要/指针；
- 过期现役说法直接更新，不追加“v1/v2/新版/旧版”平行叙事；
- 历史过程放 git/changelog/incident；
- 已完成 TODO 不冒充当前计划；
- rules 保持可复用、短而明确；
- 不复制 secret/token/credential 完整配置。

---

## 10. Closeout Contract

Codex 在 `CODE_VERIFIED` 后发给同一 Pi Run：

```text
Mode
- closeout

Closeout Goal
- 根据 final repository state 完成知识收尾。

Source of Truth
- final diff、code/schema/config/tests、Completeness evidence、Codex verified results。

Inspect
- README/docs
- AGENTS.md / CLAUDE.md / project rules
- API / Schema / Contract
- config/env/CLI/runtime docs
- workspace residue / runtime evidence hygiene

Required
1. Knowledge Impact Scan。
2. 每个相关面标 verified-current / changed-and-verified / pending / out-of-scope / not-applicable。
3. 只修改受 final implementation 影响的知识面。
4. stale current-state 描述就地更新，不创建第二权威答案。
5. 不把开发流水账写入 README/rules。
6. residue 默认只报告 deletion-candidate。
7. 不 push/merge/deploy，不扩大任务范围。

Report
- knowledge surface
- status
- evidence
- changed files
- pending/out-of-scope/deletion-candidate
```

Harness `closeout` mode 应限制写入知识面，不能无约束重开 production code 修改。

如果 Closeout 发现生产实现真的有缺陷，operation 应返回 evidence，让 Codex 退回代码 rework。

---

## 11. Codex Closeout Review

Pi operation settled 后 Codex 自己：

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
- retired symbol 不再残留于现役面；
- residue 如实报告且无未经授权删除；
- runtime state/credential 没意外进入 Git；
- Closeout 修改没破坏 baseline 或 Scope Guard。

---

## 12. Closeout 结论

### PASS

```text
CLOSEOUT PASS
- 所有相关知识面已分类。
- 受影响知识面与最终代码一致。
- pending/out-of-scope/residue 已报告。
- 可以进入最终 Acceptance 判断。
```

### REWORK

```text
CLOSEOUT REWORK
- Issue: <具体矛盾>
- Evidence: <code/diff/search>
- Expected: <唯一现役事实>
- Required change: <Pi Worker 应同步什么>
- Re-run: <重新搜索/验证什么>
```

### BLOCKED

```text
CLOSEOUT BLOCKED
- Blocker: <无法裁决事实/跨范围依赖/权限>
- Evidence: <证据>
- Safe state: <当前 code/knowledge 状态>
- Decision needed: <用户决定>
```

只有相关 Review Gates、Completeness、Regression/Test Proof、Independent Verification、Harness Policy 和 Knowledge Closeout 都 PASS，Codex 才能 `ACCEPTED`。

---

## 13. 不默认纳入

Closeout 不自动获得：

- Agent memory 写入/清理；
- production deploy/live verification；
- remote branch/PR/release cleanup；
- 删除用户文件/历史资料；
- cross-project write；
- release announcement/changelog（除非 Task Contract/项目规则要求）。
