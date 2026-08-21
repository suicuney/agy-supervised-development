# tty7 Supervision Protocol

本文件定义 `agy-supervised-development` 使用 tty7 驱动 AGY 时的运行时规则。tty7 是 worker runtime，不是 AGY wrapper：AGY 仍运行在普通 PTY 中，Codex 通过稳定 workspace/pane id 操作它。

## 1. Runtime Ownership

每个监督任务使用：

```bash
tty7 new --json "$repo_root"
```

保存：

```text
WS   = stable workspace id
PANE = stable pane id, e.g. %83
```

只允许对当前 `WS` / `PANE` 写操作。

### 禁止

- 不缓存 `@N` 作为长期 worker identity；tab 序号会随布局变化。
- 不向未由本次 Skill 创建的 pane `send` / `--key`。
- 不关闭其他 pane/tab/workspace。
- 不执行 `tty7 pane close --orphans`。
- 不执行 `tty7 server stop` / `server restart`。

## 2. Preflight

```bash
tty7 doctor
tty7 agents --json
tty7 pane ls --all --json
```

### Server unreachable

直接 `BLOCKED`，告知用户。不要自行启动或重启 server。

### AGY Hook Capability

Antigravity/AGY 可能被 tty7 正确识别，但当前安装的 tty7 未必提供 status hook。

判断原则：

- doctor/agents 明确显示 AGY native status 可用 → `native-status`。
- 识别到 AGY 但 hook unavailable/missing/not supported → `capture-fallback`。
- 不自行安装 hook。

Skill 必须同时支持两条路径，不把某一 tty7 版本的 hook 矩阵写死为永久事实。

## 3. Create Worker Workspace

推荐：

```bash
read -r WS PANE < <(
  tty7 new --json "$repo_root" |
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"], "%%%d" % d["pane"])'
)
```

必要时验证：

```bash
tty7 ws tree "$WS"
tty7 pane ls --all --json
```

不要为了一个正常单 worker 任务修改用户现有窗口布局。`split` 更适合用户明确希望在当前窗口旁边看到 worker 的情况。

## 4. First Send / Launch Proof

新 pane 的 shell 可能仍在执行启动脚本；第一次 `send --enter` 可能把文本写入 prompt，但 Enter 被吞。

因此启动 AGY 后强制：

```bash
tty7 capture "$PANE" --plain | tail -5
```

如果完整启动命令仍停在 shell prompt，只补一次：

```bash
tty7 send "$PANE" --enter
```

不要再次发送完整启动命令。

随后：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

确认目标 pane 真正运行 AGY。

## 5. Agent Detection vs Agent Status

这是 v2.1 的关键区分：

```text
Detected AGY != Status-enabled AGY
```

`tty7 agents` 可以识别 pane 中运行的是 AGY，但只有存在兼容 status hook 时，`working / waiting / done` 才能作为 native status 使用。

不要因为 agent 被识别，就默认：

```bash
tty7 wait "$PANE" --until waiting,done
```

一定可用。

## 6. Native Status Path

仅在 Preflight 已确认 AGY status hook 可用时：

```bash
tty7 wait "$PANE" \
  --until waiting,done \
  --changed \
  --timeout 1800
```

为什么需要 `--changed`：tty7 agent status 是 level，不是 event；上一轮 `done` 可以一直保留到下一轮真正开始。如果 send 后不用 `--changed`，可能立即吃到 stale done。

结果：

- exit `0`：达到 requested state；capture 后处理。
- exit `124`：timeout，只代表“还没观察到目标状态”，进入诊断。
- exit `1`：pane exited，进入 crash recovery。

`waiting` 后必须先 capture，看清问题再回答。

## 7. Capture Fallback Path

当 AGY 无 native status hook：

不要等待不存在的 `done`，也不要把 `no-agent` / `idle` 随意解释为 completion。

使用：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

结合当前 Turn nonce 做有界观察。

推荐 observation 分类：

| Observation | 含义 |
|---|---|
| `AGY_PRESENT` | tty7 仍识别目标 pane 中的 AGY |
| `TUI_ACTIVE` | 画面显示 AGY 仍在执行/流式工作 |
| `INPUT_REQUIRED` | permission/question/menu 等需要输入 |
| `TURN_MARKER_SEEN` | 当前 nonce 的 `TURN_COMPLETE` 已出现 |
| `PROMPT_READY` | AGY 已明显回到可接收下一轮输入状态 |
| `ERROR_VISIBLE` | API/connection/tool 等错误可见 |
| `UNKNOWN` | 无法可靠判断 |

`UNKNOWN` 不能转成成功；继续观察或诊断。

## 8. Read Before Send

所有写入 tty7 worker 的动作之前都必须重新读取当前 pane：

```bash
tty7 capture "$PANE" --plain
```

包括：

- prompt
- Enter
- menu arrow keys
- Escape
- Ctrl-C

固定顺序：

```text
capture → classify → decide → send
```

这比缓存“刚才屏幕是在权限页”可靠。TUI 可能在两次操作之间已经变化。

## 9. `procs` 的正确用途

`tty7 procs` 适合看普通 shell foreground process、进程树和监听端口。

不要用：

```text
tty7 procs says nothing
```

推导：

```text
AGY is dead
```

coding agent pane 的进程观察与 agent detection/status 是不同通道。判断 AGY 存活优先：

1. `tty7 agents --json`
2. pane 是否仍 live
3. `capture --plain`

## 10. Screen is Diagnostic, Git is Deliverable

`tty7 capture` 是 terminal snapshot，不是完整交付记录。长日志可能滚出屏幕，TUI 也会重绘。

因此：

- screen：看权限、错误、进度、Turn marker。
- Git：收代码交付。

Codex Review 使用：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

## 11. Error / Interrupted Turn

如果画面显示 API error、connection closed、turn interrupted，但 AGY TUI 仍存在：

1. capture 足够上下文；
2. 检查 Git state；
3. 等确认回到可输入状态；
4. Read Before Send；
5. 在同一 pane 告诉 AGY 基于现有修改继续。

不要第一时间再启动第二个 AGY 同时写同一 checkout。

## 12. Pane Exit

如果目标 pane 真退出：

1. 先检查 `git status` / `git diff`；
2. 已产生的有效代码不能因为 worker 死亡被忽略；
3. 需要继续时才创建 replacement workspace/pane；
4. 有经过验证的 conversation id 才 resume，否则用 Task Contract + 当前 diff 重建上下文。

## 13. Cleanup

当前 task 使用独立 workspace，因此正常结束优先：

```bash
tty7 ws rm "$WS"
```

如果用户要求保留 worker 给后续人工接管，则不要清理，并明确汇报：

```text
workspace: <id>
pane: %<id>
```

只清理当前 task ownership 内的资源。