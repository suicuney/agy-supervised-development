# AGY Supervised Development

一个面向 **Codex + tty7 + Antigravity CLI (`agy`)** 的监督式开发 Skill。

它不是 AGY CLI 百科，也不是通用多 Agent Framework。v2.1 系列专门把这一条链路做稳；v2.1.1 在代码验收之后补上 Knowledge Closeout，让“代码完成”和“项目知识完成”成为同一个 Definition of Done：

```text
User Requirement
      ↓
Codex Supervisor
      ↓
tty7 Worker Runtime
      ↓
AGY Interactive Implementer
      ↓
Repository Changes
      ↓
Codex Independent Review
   ↙                 ↘
Rework → AGY       PASS → Independent Verification
                         ↓
                    CODE_VERIFIED
                         ↓
                  AGY Knowledge Closeout
                         ↓
                  Codex Closeout Review
                    ↙              ↘
               Rework → AGY      ACCEPTED
```

## 核心原则

- Codex 负责主控、Review、QA、Knowledge Closeout Review 和最终验收。
- AGY 是唯一主要 Writer，负责实现、测试、返工，以及同步受最终实现影响的项目知识文件。
- tty7 负责持久 PTY、独立 workspace/pane 和可观察运行时，不在 Skill 里重复造进程管理器。
- 不相信 AGY 自己的 `done` / `TURN_COMPLETE`，只相信真实 repository state。
- 每次任务先建立 Git baseline，保护用户已有改动。
- 每个任务创建独立 tty7 workspace + pane，只操作自己创建的稳定 ID。
- 不使用会漂移的 `@N` 作为 worker identity。
- AGY 必须显式验证 repo root / branch，不能只相信 pane CWD。
- AGY/tty7 能力按当前安装版本实时检测。
- 代码通过测试只进入 `CODE_VERIFIED`；实际开发任务还必须完成 Knowledge Impact Scan。
- 每次开发都做 Closeout Scan，但只有真正受影响的知识面才修改文档。
- 默认不 push / merge / deploy，不默认全局跳过权限，也不借“收尾”扩大破坏性清理权限。

## v2.1 的关键变化

### 1. tty7-native Worker Lifecycle

统一通过：

```bash
tty7 new --json "$repo_root"
```

保存稳定：

```text
workspace id
pane id
```

正常结束清理本次 workspace，而不是碰用户其他终端。

### 2. Launch Proof

新 pane 第一次 `send --enter` 可能因 shell 启动脚本吞掉 Enter。

v2.1 强制启动 AGY 后立刻 `capture`，确认命令真的离开 shell prompt；必要时只补一次 Enter。

### 3. Native Status / Capture Fallback 双路径

Codex 先通过 `tty7 doctor` / `tty7 agents --json` 判断当前 AGY 是否拥有 tty7 status hook。

```text
native status available
→ tty7 wait --until waiting,done --changed

status hook unavailable
→ tty7 agents + capture + Turn Nonce
```

因此 Skill 不依赖某个固定 tty7 版本是否已经给 Antigravity 增加 hook。

### 4. Supervisor State，而不是伪造 AGY 内部状态

v2.1.1 记录 Codex 能证明的状态：

```text
INIT
→ BASELINED
→ TTY7_ALLOCATED
→ AGY_BOOTING
→ AGY_READY
→ TURN_SENT
→ OBSERVING
→ TURN_RETURNED
→ REVIEWING
→ VERIFYING
→ CODE_VERIFIED
→ CLOSEOUT
→ CLOSEOUT_REVIEW
→ ACCEPTED
```

`TURN_COMPLETE != ACCEPTED`，`CODE_VERIFIED != ACCEPTED`。

### 5. Read Before Send

任何 prompt、Enter、菜单按键、Escape、Ctrl-C 之前重新 capture 当前 pane：

```text
CAPTURE → CLASSIFY → DECIDE → SEND
```

避免把几秒前应答 permission 的按键发进已经变化的 TUI。

### 6. Evidence-driven Rework + Soft Budget

每轮返工必须包含 Issue / Evidence / Expected / Rework / Re-run。

默认 3 个完整 `Review → Rework → Re-review` 周期为 soft limit；达到后必须重新评估根因，不能两个 Agent 无限互修。

### 7. Scope Drift Guard

Review 不只看当前 diff，还要区分：

```text
current changes - baseline changes = task-introduced changes
```

AGY 新增的超 Scope path 必须有需求依据，否则返工。

## v2.1.1 — Knowledge Closeout

v2.1.1 不改变 Codex / AGY / tty7 的核心角色，只补齐开发任务最后一段。

### 每次开发都做 Knowledge Impact Scan

默认检查：

```text
README / usage
AGENTS.md / CLAUDE.md / project rules
API / Schema / CLI / shared Contract
config / env / provider / service / deploy / job docs
workspace residue
```

每个相关知识面标记：

```text
verified-current
changed-and-verified
pending
out-of-scope
not-applicable
```

因此纯内部 bug 修复可能完全不产生文档 diff，只要相关知识面已经 `verified-current`。

### Lightweight / Full Closeout

普通内部改动默认 Lightweight Closeout。

以下变化自动升级 Full Closeout：

- API / public Contract；
- schema / migration；
- CLI；
- env / provider / model / feature flag；
- 用户流程、权限、导航；
- 模块职责、重大重构；
- 服务、部署、端口、后台任务；
- rename / retirement；
- 跨项目共享协议。

Full Closeout 会根据 final diff 搜索旧 symbol / route / env / field / service 等 stale reference，再由 AGY 就地更新现有权威知识文件。

### 不把 Closeout 变成第二套框架

默认不纳入：

- Agent memory 写入；
- production deploy / live verification；
- remote branch / PR / release cleanup；
- 跨项目写入；
- 未授权删除用户文件或历史资料。

这些动作只有原 Task Contract 或用户明确授权时才执行。

## 为什么不默认 Worktree

tty7 的通用多 Agent delegation 很适合“一任务一 worktree”。但这个 Skill 的默认拓扑是：

```text
AGY = sole primary writer
Codex = read/review/verify
```

用户当前 checkout 的未提交改动又可能是任务上下文，因此 v2.1 默认继续使用当前 checkout + baseline protection。

只有：

- 多 Writer 并行；
- 高风险隔离实验；
- 用户明确要求；

才优先使用独立 worktree。

## 文件结构

```text
agy-supervised-development/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── resources/
│   ├── agy-runtime.md
│   ├── tty7-supervision.md
│   ├── run-lifecycle.md
│   ├── failure-modes.md
│   ├── review-gates.md
│   └── closeout-governance.md
└── examples/
    ├── feature-development.md
    └── rework-cycle.md
```

### `SKILL.md`

Codex → tty7 → AGY 的监督主流程，包括代码 Verification 后的 Knowledge Closeout。

### `resources/tty7-supervision.md`

workspace/pane ownership、Launch Proof、native/fallback status、Read Before Send、crash recovery 和 cleanup。

### `resources/run-lifecycle.md`

Supervisor State、Run Context、Turn Nonce、Scope Drift、Rework Budget，以及 `CODE_VERIFIED → CLOSEOUT → ACCEPTED` 生命周期。

### `resources/agy-runtime.md`

监督流程需要的 AGY capability、workspace、execution mode、permission、conversation 等知识。

### `resources/failure-modes.md`

将启动失败、缺少 status hook、swallowed Enter、串项目、API error、worker exit、scope drift 等拆成证据驱动处理流程。

### `resources/review-gates.md`

Codex 独立 Review 与 PASS / REWORK / BLOCKED / final Acceptance 规则，包含 Gate 12 Knowledge & Documentation Alignment。

### `resources/closeout-governance.md`

定义每次开发后的 Knowledge Impact Scan、Lightweight / Full Closeout、变更到知识面的路由、AGY Closeout Turn 和 Codex Closeout Review。

## v2 → v2.1 → v2.1.1

v2 解决：

> Codex 应该怎样监督 AGY。

v2.1 进一步解决：

> Codex 怎样利用 tty7 可靠地控制一个可观察、可接管、可返工的 AGY worker，同时在 AGY 没有 tty7 native status hook 时仍然不误判状态。

v2.1.1 再补齐：

> 当代码已经验证完成后，怎样让 AGY 根据最终事实把 README、规则、Contract 和运行说明收尾到同一现役答案，再由 Codex 验收。

v2.1 系列暂不抽象 Grok/Pi/Claude 通用 Adapter，也不做多 Worker orchestration。先把 `Codex → tty7 → AGY` 单 worker 路径和任务终态做稳定，再考虑后续泛化。