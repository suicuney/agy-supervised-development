# Repository Review Gates — v3.0.1

本文件定义 Codex 对 **Pi Native Worker 产出的真实 repository state** 做独立 Review 的维度。

Pi JSON events、session metadata、Provider/model 信息和 Worker summary 只用于诊断；真正交付从 Git state 获取。

---

## Gate 0 — Baseline Integrity

确认：

- 当前 branch / HEAD 已记录；
- 任务前已有未提交改动已识别；
- 没有为了“清理”回滚用户改动；
- Pi 本任务新增改动可与 baseline 区分。

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

- 修改属于 Task Contract；
- 没有无关 refactor/format；
- 没有无关 dependency/config/CI/deploy 变化。

超初始 Scope 的 path：

1. 是需求必然 propagation → 可以纳入 completeness scope；
2. 无充分证据 → REWORK；
3. 只撤销 Pi 本任务引入的越界改动；
4. 不碰 baseline-owned changes。

---

## Gate 2 — Requirement Coverage

把需求逐项对应到：

- implementation；
- API/schema/contract；
- migration/data；
- tests；
- UI/caller（若适用）。

不能用 Pi “已完成”替代覆盖证明。

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
- 没有无依据架构扩张。

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

## Gate 7 — Tests, Test Layers & Regression Proof

每个任务必须明确：

```text
Unit:        required | not-applicable
Integration: required | not-applicable
E2E:         required | not-applicable | user-skipped
```

- pure logic → unit；
- module/DB/serialization/queue/adapter contract → integration；
- UI→API→DB、service→service、CLI→filesystem 等真实边界 → 优先 E2E；
- `user-skipped` 不得改写成 N/A。

### Bugfix RED → GREEN

可安全、确定性自动复现：

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
- fix 后才补一个从没证明能 RED 的测试。

---

## Gate 8 — Pi Session / Turn Evidence Integrity

3.0.1 不要求 custom `run_id/operation_id`。

确认：

- Pi session id/file 来自真实 Pi 输出；
- JSON session header 的 `cwd` 与 `repo_root` 一致；
- resume 使用的是当前任务真实 session，而不是最近一个未知 session；
- `agent_end` / 正常 process exit 只被解释为“Pi turn returned”；
- JSON stream 截断时没有无脑 replay 可能产生写副作用的 turn；
- Provider/model 切换若发生是显式、可解释的；
- Worker summary 与 Git state 冲突时以 Git 为准。

规则：

```text
Pi agent_end != PASS
```

---

## Gate 9 — Independent Verification

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

Pi 报告“我跑过”只能作为线索。

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

默认验收边界：本地 repository 可交付。

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

标 `blocked-decision-needed`，不能借 completeness 自动授权。

---

## Gate 12 — Pi Runtime / Extension / Credential Hygiene

3.0.1 不再 Review 自研 Harness，而 Review **实际 Pi runtime 能力是否被如实使用和报告**。

### Native runtime

- 使用 Pi 原生 session，而非伪造 session identity；
- 不要求不存在的 custom daemon/Run Store；
- JSON/RPC capability 使用前已由当前安装能力确认。

### Workflow extension

如果报告 `read-only enforced`：

- 必须确认可信 extension 已加载；
- 当前 mode 必须是实际 read-only mode（如已验证的 `plan/review`）；
- task-introduced mutation 与 read-only 声明不矛盾。

如果 extension 不存在：

```text
mode_enforcement = unavailable/prompt-only
```

不得包装成程序化 Tool Guard。

监督流程默认不使用 `yolo` 绕过阻塞。

### Provider boundary

- Provider 只作为 intelligence；
- 没自动安装/登录未经用户确认的 Provider；
- 没提取 OAuth token/credential；
- auth/quota/model/transport error 与 code error 分类清楚；
- provider/model failover 不静默。

### Credential hygiene

不得把：

```text
access token
refresh token
Authorization header
client secret
credential file contents
```

写入 Task Contract、项目文件、最终报告或为了“留证”复制到仓库。

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
- env/config/provider/service/deploy/job docs 同步；
- rename/retirement 无 stale current-state reference；
- 没有多个文档争夺同一事实权威；
- 没把开发流水账写进长期规则；
- 未验证行为没写成“已完成/已上线”；
- residue 如实报告且未未经授权删除。

每次开发都 Scan，不是每次都必须修改 Markdown。

---

# Review Verdict

## PASS

```text
PASS
- 当前 Task Contract 阶段满足。
- Baseline 完整，无无依据 scope drift。
- Completeness/blast radius 已检查。
- 相关代码/测试证据成立。
- Pi session/runtime evidence 与 repository 不冲突。
- 可以进入下一阶段。
```

## REWORK

```text
REWORK
- Issue: <问题>
- Evidence: <file/diff/test/call-chain/Pi session evidence>
- Expected: <期望>
- Required change: <Pi 要修改什么>
- Re-run: <命令>
```

## BLOCKED

```text
BLOCKED
- Blocker: <环境/Provider/权限/one-way decision/session/extension capability>
- Evidence: <实际证据>
- Safe state: <repository / governance state>
- Decision needed: <用户决定>
```

最终 `ACCEPTED` 必须同时经过 Completeness、Test/Regression Proof、Codex Independent Verification、Pi Runtime/Extension Hygiene 和 Knowledge Closeout Review。
