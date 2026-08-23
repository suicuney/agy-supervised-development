# Repository Review Gates — v3.1 Alpha 2

本文件定义 Codex 对 **AGY Primary Worker 产出的真实 repository state** 做独立 Review 的门禁。

AGY stream-json、conversation metadata、Worker summary 只用于诊断；真正交付从 Git state 和 Codex Independent Verification 获取。

> Alpha 2 只完成 Runtime 对齐；Alpha 3 会把这些 Gate 正式重组为 **Spec Fidelity / Engineering Quality / Completeness** 三轴 Review。

---

## Gate 0 — Baseline Integrity

确认：

- 当前 branch / HEAD 已记录；
- 任务前已有未提交改动已识别；
- 没有为了“清理”回滚用户改动；
- AGY 本任务新增改动可与 baseline 区分。

```bash
git status --short
git diff --stat
git diff --check
```

核心：

```text
current changes - baseline changes = task-introduced changes
```

---

## Gate 1 — Scope / Scope Drift

检查：

- 修改属于当前 Spec / Execution Unit；
- 没有无关 refactor/format；
- 没有无关 dependency/config/CI/deploy 变化。

超初始 Scope 的 path：

1. 是当前 change 必然 propagation → 可以纳入 completeness scope；
2. 无充分证据 → REWORK；
3. 只撤销 AGY 本任务引入的越界改动；
4. 不碰 baseline-owned changes。

---

## Gate 2 — Spec / Acceptance Coverage

把 Spec / Execution Unit 的 Acceptance Criteria 对应到：

```text
implementation
observable behavior
API/schema/contract
migration/data
verification seam
tests
UI/caller（若适用）
```

不能用 AGY “已完成”替代覆盖证明。

---

## Gate 3 — Change Propagation & Blast Radius

Review current diff + missing diff。

追踪：

- direct callers；
- indirect callers / re-export / scripts；
- types / enums / validation / serialization；
- schema / migration / existing data；
- sibling flows / jobs；
- error / empty / permission / retry / fallback；
- cache / derived state / stale IDs；
- orphaned old path / dead code；
- tests；
- Knowledge Closeout impact。

必要时：

```bash
rg "<changed-symbol>" .
rg "<old-route|old-field|old-enum|old-config>" .
```

Remainder disposition：

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

---

## Gate 4 — Architecture & Contract

检查：

- 项目分层/模块边界；
- 没绕开已有抽象；
- API contract 与 caller 一致；
- DTO/model/entity 边界；
- schema/migration/persistence；
- config convention；
- 没有 Speculative Generality / 无依据架构扩张。

---

## Gate 5 — Correctness & Edge Cases

按相关性检查：

- null / empty / missing；
- boundary value；
- error path；
- retry / idempotency；
- timezone / locale；
- concurrency / race；
- transaction；
- pagination / ordering；
- authorization；
- partial failure；
- backward compatibility。

---

## Gate 6 — Error Handling & Observability

检查：

- exception 是否被吞；
- status/error code；
- log 是否泄漏敏感数据；
- debug/临时输出；
- 定位上下文；
- retry 是否放大永久错误。

---

## Gate 7 — Verification Seam, Test Layers & Regression Proof

每个任务必须明确：

```text
Primary Verification Seam
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

测试应优先通过公共行为边界观察，而不是绑定内部实现。

### Bugfix RED → GREEN

可安全确定性自动复现：

```text
unfixed → regression test RED
fix root cause
same test → GREEN
Codex independent re-run
```

警惕：

- 只改 assertion；
- 删/skip tests；
- mock 掉真实 contract；
- fix 后才补一个从没证明能 RED 的 test；
- test layer 对了但 seam 错了。

---

## Gate 8 — AGY Run / Conversation Evidence Integrity

确认：

- `conversation_id` 来自真实 AGY `init/result`；
- `init.cwd == repo_root`；
- rework 使用当前任务真实 `--conversation <id>`；
- `-c` 没被用于猜一个未知“最近 session”冒充精确身份；
- stream-json 截断时没有无脑 replay 可能有副作用的任务；
- `result.status=SUCCESS` 只被解释为本轮 AGY 返回；
- Worker summary 与 Git 冲突时以 Git 为准。

规则：

```text
AGY result SUCCESS != PASS
```

---

## Gate 9 — Codex Independent Verification

Codex 必须自己执行相关门禁：

```text
lint
format/check
typecheck
unit
integration
e2e（required 时）
build/package
contract/schema check
```

AGY 报告“我跑过”只能作为线索。

尤其要区分：

```text
actually-run-and-pass
blocked/not-run
failed
```

Headless permission soft-deny 不得伪装成测试 PASS。

E2E required 时记录 command、startup/readiness、seed/fixture、account/sandbox、teardown。

---

## Gate 10 — Diff Hygiene

最终检查：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

确认没有：

- debug code；
- temp/build artifacts；
- 意外 lockfile；
- unrelated rename/format；
- sensitive information；
- 超范围 docs/config。

---

## Gate 11 — External Side Effects / One-way Door

未经授权不得：

- push；
- merge；
- release；
- deploy；
- production write；
- remote delete；
- cloud mutation。

以下 decision 同样默认需要用户明确决定：

- destructive/non-additive migration；
- breaking public API；
- auth/tenancy relaxation；
- money/billing semantics；
- credential behavior；
- irreversible data deletion。

AGY permission engine 的 allow 只代表 Runtime 允许，不代表产品/风险层已授权。

---

## Gate 12 — AGY Runtime / Permission / Credential Hygiene

### Native Runtime

确认：

- 使用官方 AGY CLI 主链；
- headless capability 使用前由当前 `agy --help` 验证；
- `stream-json` 按 `init / step_update / result` 解析；
- 不默认 screen scrape；
- 不 reverse-engineer conversation DB 作为主身份来源。

### Permission Integrity

- 默认不使用 `--dangerously-skip-permissions`；
- 需要 allow 时尽量使用窄 fine-grained rule；
- `Ask` 在 headless 中被 soft-deny 时被如实记录；
- exit 0 不被当成所有 tool 都成功；
- tty7 只用于真正需要人工交互的 fallback。

### Credential Hygiene

不得把：

```text
access token
refresh token
Authorization header
client secret
credential store contents
```

写进 Execution Unit、Rework Contract、项目文件或最终报告。

### Pi Boundary

如果使用 Pi，只能作为 optional specialist。不要让 Pi 重新成为默认 `Codex → Pi → AGY` 中间层，也不要用第三方 Antigravity OAuth Provider 偷偷替代官方 AGY CLI 主链。

---

## Gate 13 — Knowledge & Documentation Alignment

代码通过相关 Gate 和 Independent Verification 后执行 Knowledge Closeout。

每个相关知识面标：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

检查：

- README/usage 与 final implementation 一致；
- `AGENTS.md` / `CLAUDE.md` / project rules 准确且不过度膨胀；
- API/schema/CLI/shared Contract 与实现/示例/caller 一致；
- env/config/service/deploy/job docs 同步；
- rename/retirement 无 stale current-state reference；
- 没有多个文档争夺同一事实权威；
- 没把开发流水账写进长期规则；
- residue 如实报告且未未经授权删除。

每次开发都 Scan，不是每次都必须修改 Markdown。

---

# Review Verdict

## PASS

```text
PASS
- 当前 Spec / Execution Unit 满足。
- Baseline 完整，无无依据 scope drift。
- Completeness/blast radius 已检查。
- 相关代码/测试证据成立。
- AGY runtime evidence 与 repository 不冲突。
- 可以进入下一阶段。
```

## REWORK

```text
REWORK
- Issue: <问题>
- Evidence: <file/diff/test/call-chain/runtime evidence>
- Expected: <期望>
- Required change: <AGY 要修改什么>
- Re-run: <命令>
```

## BLOCKED

```text
BLOCKED
- Blocker: <环境/auth/permission/one-way decision/conversation capability>
- Evidence: <实际证据>
- Safe state: <repository / governance state>
- Decision needed: <用户决定>
```

最终 `ACCEPTED` 必须经过 Completeness、Test/Regression Proof、Codex Independent Verification、Runtime/Permission Hygiene 和 Knowledge Closeout Review。
