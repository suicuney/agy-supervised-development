# Knowledge Closeout Governance — v3.1

本文件定义 AGY 完成实现、Codex 完成 **Review + Completeness + Regression/Test Proof + Independent Verification** 之后的知识收尾协议。

目标不是“多写文档”，而是确保最终代码事实、项目文档、Agent 规则、外部 Contract 和工作区状态一致，然后才允许 Codex 进入 `ACCEPTED`。

---

## 1. 职责边界

- **AGY Primary Worker**：只有确实需要修改知识文件时，执行严格 Closeout Contract；
- **Codex**：决定哪些知识面受影响、生成 Closeout Contract、审查 Closeout diff、执行 stale-reference search，并最终验收；
- **Repository state**：首要真相来源；
- **tty7**：仅在 closeout 需要真实 TUI/人工批准时 fallback；
- **Pi**：不参与默认 Closeout 主链。

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
→ COMPLETENESS_REVIEW
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

`CODE_VERIFIED` 表示代码层稳定，不等于最终完成。

---

## 3. 每次开发都 Scan，不是每次都改文档

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

## 4. Source of Truth 顺序

1. 当前 branch / final diff；
2. 当前 code/schema/config/tests；
3. Completeness / blast-radius evidence；
4. Codex 已实际验证的 command/runtime result；
5. 项目现役 Contract / generated schema；
6. README/docs/rules；
7. AGY Worker summary / 旧计划 / 历史说明。

旧文档与已验证 final implementation 冲突时，以最终实现为准；若产品预期无法裁决，标 `pending`，不要把猜测写成权威事实。

---

## 5. 默认检查知识面

### Usage / README

安装、启动、调用、配置、使用方式是否仍正确。

### Agent Rules

检查：

```text
AGENTS.md
CLAUDE.md
project development rules
```

只同步“下次 Agent 不知道就容易做错”的稳定规则，不写开发流水账。

### Contract / Schema

API/route/request/response、DB schema、event/message schema、CLI contract、shared interface 改动必须核对权威 Contract、示例和 consumer-facing docs。

### Runtime / Configuration

env、ports、service names、flags、deploy/run commands、jobs 改动必须核对 runbook/示例配置。

### Workspace Residue

检查：

- PLAN/TODO/implementation notes；
- 临时 debug script；
- `*_old.*` / `*_backup.*`；
- generated artifacts；
- 意外提交的 AGY runtime output / stream-json dump；
- credential/token 是否误入日志、prompt dump 或 diff。

来源/安全性不明确的文件只列 `deletion-candidate`，不擅自删除。

---

## 6. Lightweight / Full Closeout

### Lightweight — 默认

1. 读取 final diff / changed paths；
2. 读取 Completeness `Knowledge impact`；
3. 判断 README/rules/Contract/runtime/config/residue；
4. 分类每个知识面；
5. 只有确实需要修改时才调用 AGY；
6. Codex Review 新 diff。

### Full — 自动升级

出现任一：

- API/public Contract；
- schema/migration/persistence contract；
- CLI；
- env/flag/runtime；
- 用户流程/权限/navigation；
- 模块职责/架构边界/重大重构；
- deploy/service/port/background job；
- rename/retirement；
- cross-project shared protocol。

Full Closeout 额外：

1. 提取旧/新 symbol；
2. 搜索非历史 stale reference；
3. 查权威文档索引和 consumer-facing knowledge；
4. 就地更新权威文档，不创建平行版本；
5. 再搜索旧 symbol；
6. 无法编辑的跨项目影响标 `out-of-scope`。

---

## 7. Change → Knowledge Routing

| 变化 | 优先核对 |
|---|---|
| API / route / protocol | API/集成说明、鉴权、示例、consumer contract |
| schema / storage field | 数据模型、migration、读写边界、测试说明 |
| env / flag | 示例配置、默认值、运行和回退说明 |
| CLI / command | README、usage、examples、automation scripts |
| 用户流程 / 权限 / navigation | 产品说明、权限说明、UI/caller docs |
| 模块边界 / 重构 | architecture、rules 中目录职责、开发约定 |
| service / deploy / port | runbook、启动命令、服务名、smoke/rollback |
| job / scheduler | 调度、失败处理、告警/运维入口 |
| rename / retirement | 旧 symbol 现役引用、rules、consumer、examples |

---

## 8. 单一权威事实

- 同一现役事实尽量只保留一个权威解释；
- 其他位置只留摘要/指针；
- 过期现役说法直接更新，不追加“新版/旧版”平行叙事；
- 历史过程放 git/changelog/incident；
- 已完成 TODO 不冒充当前计划；
- rules 保持可复用、短而明确；
- 不复制 secret/token/credential 完整配置。

---

## 9. Closeout Contract

模板见：

```text
../templates/closeout-contract.md
```

需要修改时优先 resume 当前真实 AGY conversation：

```bash
agy -p "<Closeout Contract>" \
  --conversation <real-conversation-id> \
  --output-format stream-json
```

如果 conversation 丢失，可以新开 AGY conversation，但必须重新提供 final verified repository facts；不要重跑实现。

Closeout Contract 必须限制：

```text
Allowed = directly affected knowledge surfaces
Forbidden = unrelated production redesign / new feature / destructive cleanup / push / merge / deploy
```

---

## 10. Closeout Runtime Evidence

AGY：

```text
result.status=SUCCESS
```

只表示本轮 closeout runtime 返回，不等于 Closeout PASS。

Codex 自己：

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

---

## 11. Closeout 发现代码缺陷

如果文档审查揭示真实代码问题：

```text
CLOSEOUT
→ REWORK_REQUIRED
→ REVIEWING / COMPLETENESS_REVIEW / VERIFYING
```

不能只改文档掩盖错误实现。

---

## 12. Closeout Verdict

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
- Required change: <AGY 应同步什么>
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

只有相关 Review Gates、Completeness、Regression/Test Proof、Independent Verification、Runtime/Permission Hygiene 和 Knowledge Closeout 都 PASS，Codex 才能 `ACCEPTED`。

---

## 13. 不默认纳入

Closeout 不自动获得：

- Agent memory 写入/清理；
- production deploy/live verification；
- remote branch/PR/release cleanup；
- 删除用户文件/历史资料；
- cross-project write；
- release announcement/changelog（除非 Spec/项目规则要求）。
