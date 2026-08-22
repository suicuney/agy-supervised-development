# Knowledge Closeout Governance

本文件定义 AGY 完成实现、Codex 完成 **Diff Review + Completeness Review + Regression/Test Proof + Independent Verification** 之后的知识收尾协议。目标不是“多写文档”，而是确保最终代码事实、项目文档、Agent 规则、外部 Contract 和可解释的工作区状态彼此一致，然后才允许 Supervisor 进入 `ACCEPTED`。

该阶段保持本 Skill 的职责边界：

- AGY 仍是 Sole Primary Writer，负责修改受影响的代码、测试和知识文件；
- Codex 仍是 Supervisor / Reviewer / QA，负责判断影响面、审查修改和最终验收；
- Completeness Review 负责“代码世界有没有漏改”；Closeout 负责“知识世界有没有同步”；
- 不把本 Skill 扩张成通用 Memory、发布或 Workspace 管家；
- repository state 仍是首要真相来源。

## 1. Definition of Done

代码通过测试不再直接等于任务完成。

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

正常状态：

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

`CODE_VERIFIED` 表示代码层已经稳定：当前 diff 正确、blast radius 已解释、测试层选择已满足、可复现 bug 的 regression proof 已成立、Codex 已独立验证。只有此时才根据**最终实现**同步权威知识面；不要把中间态提前写进文档。

## 2. Closeout 与 Completeness 的边界

两者互补但不重复：

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

Completeness 可以在 `CODE_VERIFIED` 前标记 `Knowledge impact = affected`，但知识文件的最终修改优先放在 Closeout，基于 final implementation 执行。

## 3. 每次开发都 Scan，不是每次开发都改文档

所有实际开发任务在进入 `ACCEPTED` 前都执行 Knowledge Impact Scan。

每个相关知识面使用以下状态之一：

- `verified-current`：检查过，现有内容仍准确，无需修改；
- `changed-and-verified`：本次已同步修改，并由最终代码/配置/测试证据验证；
- `pending`：确认存在影响，但当前无法安全裁决或验证；
- `out-of-scope`：存在影响，但超出当前授权或任务边界；
- `not-applicable`：该事实面与本次开发无关或项目不存在该事实面。

不要为了制造“收尾 diff”而修改没有实际变化的 Markdown。

例如纯内部 bug 修复可能得到：

```text
README              verified-current
AGENTS / CLAUDE     verified-current
API Contract        not-applicable
Architecture Docs   not-applicable
Residue             verified-current
```

这是合格的 Closeout，即使没有任何文档文件发生变化。

## 4. Source of Truth 顺序

Closeout 以最终状态裁决，不以开发过程裁决。证据优先级：

1. 当前 branch / final diff；
2. 当前代码、schema、配置和测试；
3. Completeness / blast radius evidence；
4. Codex 已实际验证的 runtime / command result；
5. 项目现役 Contract / generated schema；
6. README / docs / rules；
7. AGY 总结、旧计划、历史说明。

如果旧文档与最终代码冲突，以已验证的当前实现为准；若无法证明哪一边才是预期行为，标 `pending`，不要把猜测写成权威事实。

## 5. 默认检查的知识面

### A. Usage / README

检查用户或开发者实际如何安装、启动、调用、配置和使用变化后的能力。

### B. Agent Rules

检查实际生效的：

- `AGENTS.md`；
- `CLAUDE.md`；
- 项目内其他明确声明的 Agent / development rules。

只同步“下次 Agent 不知道就容易做错”的稳定规则。不要把本轮开发流水账、一次性分析或已完成 TODO 塞进规则文件。

### C. Contract / Schema

若本次涉及 API/route/request/response、database schema、event/message schema、CLI contract、shared interface，必须核对项目已有权威 Contract、示例和 consumer-facing 文档。

### D. Runtime / Configuration

若本次涉及 environment variables、ports、service names、provider/model、feature flags、deploy/run commands、cron/jobs，必须核对已有配置说明、runbook 或示例配置。

### E. Workspace Residue

只读检查本轮是否产生明显一次性残留，例如：

- `PLAN.md` / `TODO.md` / implementation notes；
- 临时 debug script；
- `*_old.*` / `*_backup.*`；
- 中间生成物；
- 已被正式文档吸收的一次性说明。

默认只列为 `deletion-candidate`，不要在 Closeout 中擅自删除。若 Task Contract 或用户已经对特定文件明确授权删除，可按原授权处理。

## 6. Lightweight Closeout 与 Full Closeout

### Lightweight Closeout — 默认每次开发执行

至少：

1. 读取 final diff / changed paths；
2. 读取 Completeness Review 的 `Knowledge impact`；
3. 判断 README、rules、Contract、runtime/config、residue 是否受影响；
4. 对每个相关面给出状态；
5. 需要修改时由 AGY 在同一 worker pane 完成；
6. Codex Review 修改后的 Git state。

### Full Closeout — 影响面较大时自动升级

出现以下任一变化时走完整路径：

- API / public Contract；
- schema / migration / persistence contract；
- CLI 参数或命令；
- environment variable / provider / model / feature flag；
- 用户流程、权限或导航；
- 模块职责、架构边界或重大重构；
- 部署、服务名、端口、后台任务；
- 退役 / 重命名 / 下线路由、字段、配置或服务；
- 跨项目共享协议。

完整路径还要：

1. 提取本次变化的旧/新 symbol；
2. 用 `rg` 或项目等价搜索查找非历史 stale reference；
3. 查项目已有文档索引和直接 consumer-facing knowledge；
4. 就地更新现有权威文档，避免创建平行版本；
5. 再搜索一次旧 symbol，确认没有漏掉现役引用；
6. 对无法编辑的跨项目影响标 `out-of-scope` 并报告。

## 7. Change → Knowledge Routing

| 代码/运行变化 | 优先核对 |
|---|---|
| API / route / protocol | API/集成说明、鉴权、示例、consumer contract |
| schema / storage field | 数据模型、migration、读写边界、测试说明 |
| env / provider / model / flag | 示例配置、默认值、运行说明、回退说明 |
| CLI / command | README、usage、examples、automation scripts |
| 用户流程 / 权限 /导航 | README/产品说明、权限说明、UI/调用方文档 |
| 模块边界 /重构 | architecture、rules 中的目录职责、开发约定 |
| service / deploy / port | runbook、启动命令、服务名、smoke/回滚说明 |
| job / scheduler | 调度说明、失败处理、告警/运维入口 |
| rename / retirement | 搜旧 symbol 的现役引用、rules、consumer、examples |

## 8. 单一权威事实

Closeout 修改遵循：

- 同一现役事实尽量只保留一个权威解释；
- 其他位置保留短摘要或指针，不复制完整机制；
- 过期现役说法直接改写，不追加“v1 / v2 / 新版 / 旧版”平行叙事；
- 历史过程属于 git / changelog / incident 文档，不属于主 README 或 Agent rules；
- 已完成 TODO 不继续冒充当前计划；
- 规则文件只保留可复用约束，详细机制放 docs；
- 不把 secret、token、个人信息或敏感完整配置复制进文档。

## 9. AGY Closeout Turn 模板

Codex 在 `CODE_VERIFIED` 后，先执行 Read Before Send，再向同一 `$PANE` 发新的 Turn nonce：

```text
Closeout Goal
- 根据最终 repository state 完成本次开发的知识收尾。

Source of Truth
- final diff、当前代码/schema/config/tests、Completeness evidence 和 Supervisor 已验证结果。

Inspect
- README / docs
- AGENTS.md / CLAUDE.md / project rules
- API / Schema / Contract
- config / env / CLI / runtime docs
- 本轮明显 workspace residue

Required
1. 先做 Knowledge Impact Scan。
2. 每个相关知识面标记 verified-current / changed-and-verified / pending / out-of-scope / not-applicable。
3. 只有受最终实现影响的知识面才修改。
4. 已过期现役描述就地更新，不创建第二份权威答案。
5. 不把开发流水账写入 README / rules。
6. residue 只列 deletion-candidate；没有明确授权不要删除。
7. 不 push / merge / deploy，不扩大任务范围。

Report
- knowledge surface
- status
- evidence
- changed files
- pending / out-of-scope / deletion-candidate
```

Closeout Turn 和实现 Turn 使用同一个 Turn Protocol：native status / capture fallback、Read Before Send、nonce 和 repository Review 都继续适用。

## 10. Codex Closeout Review

AGY 返回后，Codex 不接受“文档已经同步”的口头结论。至少检查：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

按影响面选择：

```bash
rg "<old-symbol|route|env|field|service>" .
```

确认：

- 文档描述与 final implementation 一致；
- 没有把未验证行为写成已完成；
- 没有为形式制造无意义文档 diff；
- rules 没有膨胀成第二份 README；
- Contract / schema / examples 没有互相冲突；
- 退役 symbol 不再出现在非历史现役面；
- residue 被如实报告且没有未经授权删除；
- Closeout 修改没有覆盖 baseline 或制造新 scope drift。

如果 Closeout 发现某个“文档问题”其实证明代码传播没做完整，例如文档列出的 consumer 仍使用旧 contract，应退回 `COMPLETENESS_REVIEW` / `VERIFYING`，而不是只改文档遮住实现缺陷。

## 11. Closeout 结论

### PASS

```text
CLOSEOUT PASS
- 所有相关知识面已分类。
- 受影响知识面与最终代码事实一致。
- pending / out-of-scope / residue 已明确报告。
- 可以进入最终 Acceptance 判断。
```

### REWORK

```text
CLOSEOUT REWORK
- Issue: <文档/规则/contract 与最终实现的具体矛盾>
- Evidence: <代码/diff/search 证据>
- Expected: <应保留的唯一现役事实>
- Required change: <AGY 要同步什么>
- Re-run: <需要重新搜索/验证什么>
```

### BLOCKED

```text
CLOSEOUT BLOCKED
- Blocker: <无法裁决的事实/跨范围依赖/权限>
- Evidence: <双方证据>
- Safe state: <当前代码与知识状态>
- Decision needed: <需要用户决定什么>
```

只有相关代码 Gates PASS、Gate 3 Completeness PASS、Gate 7 Regression/Test Proof 成立、Independent Verification 完成且 Gate 13 Closeout PASS 后，Codex 才能进入 `ACCEPTED`。

## 12. 明确不默认纳入的范围

以下能力不因为 Knowledge Closeout 自动获得权限：

- Agent memory 写入或清理；
- production deploy / live verification；
- remote branch / PR / release cleanup；
- 删除 worktree、用户文件或历史资料；
- 跨项目写入；
- 发布公告、changelog 或 release note（除非项目规则或用户要求）。

如果当前 Task Contract 本来就包含这些动作，继续服从原任务授权和项目规则；Closeout 本身不扩大权限。