# Example: 中型功能开发（v2.1.2）

场景：给现有服务增加“按状态过滤”的查询能力并补测试，不改变现有默认行为。

## 1. Codex 建立 Baseline

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

读取项目规则、查询实现、API contract、调用方和测试约定。

## 2. Preflight + Worker

```bash
command -v agy
agy --version 2>/dev/null || true
agy --help

tty7 doctor
tty7 agents --json
tty7 pane ls --all --json
```

创建独立 worker：

```bash
read -r WS PANE < <(
  tty7 new --json "$repo_root" |
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"], "%%%d" % d["pane"])'
)
```

启动 AGY 后做 Launch Proof，并完成 Workspace Verification。之后只操作 `$WS` / `$PANE`。

## 3. Task Contract

```text
Goal
- 为现有查询接口增加可选 status 过滤。
- 未提供 status 时保持当前行为完全不变。

Scope
- 查询相关 controller/service/repository、contract 和对应测试。

Constraints
- 不改变默认排序和分页语义。
- 不新增第三方依赖。
- 不修改无关模块。

Acceptance Criteria
- status 缺省：结果与改动前一致。
- status 合法：只返回匹配状态。
- status 非法：遵循现有参数错误规范。

Completeness
- 检查所有调用该查询能力的入口。
- 检查 request DTO / validator / OpenAPI 或现有 contract。
- 检查 sibling query path 是否共享同一过滤模型。
- 不把“新增更多筛选条件”扩成另一个 ticket。

Test Strategy
- Unit: required
- Integration: required
- E2E: not-applicable（本例没有独立用户跨进程流程，已有 integration 可覆盖 HTTP/contract）

Regression Proof
- not-applicable（这是新功能，不是 bugfix）

Verification
- 查询模块 unit + integration tests。

Run Policy
- AGY 是唯一主要 Writer。
- 不 push / merge / deploy。
- 不回滚 baseline 用户改动。
- 不扩大 Scope。

Completion Protocol
- 本轮结束后输出 TURN_COMPLETE: A7F2E9
```

## 4. 实现 Turn 返回

Native status：

```bash
tty7 wait "$PANE" --until waiting,done --changed --timeout 1800
```

Fallback：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

`TURN_COMPLETE` 只表示 Turn 返回，不等于 PASS。

## 5. Codex Diff Review

```bash
git status --short
git diff --stat
git diff --check
git diff
```

检查：

- status 缺省是否保持默认行为；
- 非法参数是否符合 contract；
- 是否复用项目既有 filtering 模式；
- task-introduced changed paths 是否超 Scope。

## 6. Change Completeness / Blast Radius

Diff Review PASS 后不能直接跑 Verification。

先追踪传播面：

```bash
rg "<query-method|request-dto|status>" .
```

示例检查：

```text
Changed surface
- query request 新增 optional status

Known consumers
- HTTP controller
- internal service caller
- request DTO validator
- OpenAPI/contract

Propagation checked
- default path
- filtered path
- invalid status path
- pagination/order path
- sibling query endpoint

Remainder
- none

Knowledge impact
- API Contract affected
```

如果发现某个 internal caller 构造 DTO 时假设字段集固定，或者 sibling validator 仍拒绝 status，这是 `unfinished`，必须 REWORK。

如果发现“顺便增加 category filter”只是相邻需求，这是 `out-of-scope-different-ticket`，不扩张。

## 7. Evidence-driven Rework

假设发现 `status=null` 仍追加 SQL 条件：

```text
REWORK

Issue
- status 缺省时仍进入新增过滤逻辑，会改变现有默认查询。

Evidence
- <file>:<line> 对 null 进行了错误映射。

Expected
- 未提供 status 时查询语义与改动前一致。

Required change
- 修正 optional-filter 逻辑并补 regression-style coverage。

Re-run
- <targeted test command>
```

AGY 修复后，Codex 重新做 Diff Review + Completeness Review，不只看最后补丁。

## 8. Codex Independent Verification

根据 Test Layer Decision 独立运行：

```text
Unit        required → PASS
Integration required → PASS
E2E         not-applicable
```

以及：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

进入 `CODE_VERIFIED` 前需要有：

```text
Completeness Sweep: PASS
Blast radius evidence: callers + DTO + validator + contract + sibling path
Remainders: none
Regression proof: not-applicable (feature)
Independent verification: PASS
```

此时仍不能 `ACCEPTED`。

## 9. Knowledge Impact Scan

本例新增 API 查询参数，因此执行 Full Closeout。

```text
README / usage       ?
AGENTS / CLAUDE      ?
API Contract         affected
config/runtime       not-applicable
workspace residue    ?
```

搜索现役说明：

```bash
rg "status|<query-route>|<request-model>" README.md docs/ .
```

README 如果不描述 API 参数，可以保持 `verified-current`，不要为了留痕硬改。

## 10. AGY Closeout Turn

向同一 `$PANE` 发新 nonce：

```text
Closeout Goal
- 根据最终实现同步 status 过滤能力相关知识面。

Required
- 对 README / rules / API Contract / runtime docs / residue 做 Knowledge Impact Scan。
- 只修改真正受影响的知识文件。
- Contract / examples 中增加 optional status，并明确缺省行为不变。
- 不把开发过程写进 README / rules。
- 不删除未授权 residue。
```

## 11. Codex Closeout Review

```bash
git status --short
git diff --stat
git diff --check
git diff
rg "status|<query-route>|<request-model>" README.md docs/ .
```

示例结果：

```text
README              verified-current
AGENTS / CLAUDE     verified-current
API Contract        changed-and-verified
API Example         changed-and-verified
Runtime Config      not-applicable
Residue             verified-current
```

只有 Gate 13 PASS 后：

```text
Supervisor State = ACCEPTED
```

## 12. Cleanup

用户没有要求保留 AGY 时：

```bash
tty7 ws rm "$WS"
```

Closeout 发现的 `PLAN.md`、backup、调试脚本等不自动删除；来源或授权不明确时只列 `deletion-candidate`。