# AGY Supervised Development

一个面向 **Codex + tty7 + Antigravity CLI (`agy`)** 的监督式开发 Skill。

它不是 AGY CLI 百科，也不是通用多 Agent Framework。v2.1 专门把这一条链路做稳：

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
                      ACCEPTED
```

## 核心原则

- Codex 负责主控、Review、QA 和最终验收。
- AGY 是唯一主要 Writer，负责实现和返工。
- tty7 负责持久 PTY、独立 workspace/pane 和可观察运行时，不在 Skill 里重复造进程管理器。
- 不相信 AGY 自己的 `done` / `TURN_COMPLETE`，只相信真实 repository state。
- 每次任务先建立 Git baseline，保护用户已有改动。
- 每个任务创建独立 tty7 workspace + pane，只操作自己创建的稳定 ID。
- 不使用会漂移的 `@N` 作为 worker identity。
- AGY 必须显式验证 repo root / branch，不能只相信 pane CWD。
- AGY/tty7 能力按当前安装版本实时检测。
- 默认不 push / merge / deploy，不默认全局跳过权限。

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

v2.1 记录 Codex 能证明的状态：

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
→ ACCEPTED
```

`TURN_COMPLETE != ACCEPTED`。

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
│   └── review-gates.md
└── examples/
    ├── feature-development.md
    └── rework-cycle.md
```

### `SKILL.md`

Codex → tty7 → AGY 的监督主流程。

### `resources/tty7-supervision.md`

workspace/pane ownership、Launch Proof、native/fallback status、Read Before Send、crash recovery 和 cleanup。

### `resources/run-lifecycle.md`

Supervisor State、Run Context、Turn Nonce、Scope Drift 和 Rework Budget。

### `resources/agy-runtime.md`

监督流程需要的 AGY capability、workspace、execution mode、permission、conversation 等知识。

### `resources/failure-modes.md`

将启动失败、缺少 status hook、swallowed Enter、串项目、API error、worker exit、scope drift 等拆成证据驱动处理流程。

### `resources/review-gates.md`

Codex 独立 Review 与 PASS / REWORK / BLOCKED / final Acceptance 规则。

## v2 → v2.1

v2 解决：

> Codex 应该怎样监督 AGY。

v2.1 进一步解决：

> Codex 怎样利用 tty7 可靠地控制一个可观察、可接管、可返工的 AGY worker，同时在 AGY 没有 tty7 native status hook 时仍然不误判状态。

v2.1 暂不抽象 Grok/Pi/Claude 通用 Adapter，也不做多 Worker orchestration。先把 `Codex → tty7 → AGY` 单 worker 路径做稳定，再考虑后续泛化。