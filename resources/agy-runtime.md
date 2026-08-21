# AGY Runtime Reference

本文件只保存 `agy-supervised-development` 监督流程真正需要的 AGY 运行时知识。不要把它当完整 CLI 百科；执行时始终以本机 `agy --help` / `agy --version` 为准。

## 1. 核心原则

**Capability Detection > Capability Assumption**

每次任务开始：

```bash
command -v agy
agy --version 2>/dev/null || true
agy --help
```

如果本文件与当前安装版本冲突，以本机输出为准。

## 2. 监督开发最相关的能力

以下能力在较新的 AGY 版本中可能存在，但必须运行时确认：

- `--add-dir <path>`：显式把目录加入 workspace/context。
- `--mode <mode>`：选择执行模式，例如 `plan`、`accept-edits`。
- `--effort <level>`：推理强度，例如 `low` / `medium` / `high`。
- `--agent <agent>`：指定自定义 agent。
- `--model <model>`：指定模型。
- `--sandbox`：受限执行环境。
- `--continue` / `--conversation <id>`：继续已有会话。
- `--print` / `-p`：非交互执行。
- `--output-format`：结构化输出能力。

监督开发默认使用**交互式 tty7 worker pane**，因为需要可见 TUI、follow-up、permission 处理、错误恢复和人工接管。Headless 不是默认 worker 入口。

## 3. tty7 对 AGY 的能力要单独检测

AGY CLI capability 与 tty7 AGY integration 是两回事。

当前任务开始时同时执行：

```bash
tty7 doctor
tty7 agents --json
```

可能出现：

1. AGY 被识别，并且有 native status hook；
2. AGY 被识别，但没有 `working/waiting/done` status channel；
3. tty7 无法识别目标 pane 中的 AGY。

v2.1 必须支持第 2 种情况：使用 `capture + Turn Nonce` fallback。不要因为 AGY 没有 tty7 hook 就自动停止任务，也不要自行安装 hook。

## 4. Workspace / Project Context

AGY 可能保留持久化 workspace/project/conversation 状态，因此：

```text
shell CWD == repo_root
```

不等价于：

```text
AGY internal context == repo_root
```

### 推荐策略

1. tty7 worker pane cwd 指向 `repo_root`；
2. 若当前版本支持 `--add-dir`，启动时显式绑定；
3. 启动后要求 AGY 返回/执行 repository root + branch；
4. 让 AGY 读取目标仓库已知文件；
5. Codex 自己核对同样信息；
6. 出现旧项目名、旧路径、错误 branch 等证据立即停止正式编码。

不要把 `--continue` / 恢复旧 conversation 当默认策略。监督开发优先任务隔离。

## 5. Execution Mode Strategy

### `default`

适合：

- 高风险代码区域；
- 希望 AGY 自己也保留较多编辑确认；
- Codex 外层 Review 之外还需要一层交互保护。

### `accept-edits`

适合：

- 小到中型、范围清晰；
- Codex 已建立 baseline；
- Codex 会完整 Review 最终 diff。

接受文件编辑不等于允许所有 shell、网络、权限或外部副作用。

### `plan`

适合：

- 大型重构；
- 跨模块需求；
- 数据模型/API contract 改造；
- 风险高、实现路径不唯一。

推荐：

```text
AGY Plan
  ↓
Codex Review Plan
  ↓
AGY Implement
  ↓
Codex Review Code
```

若当前版本没有 plan mode，用 Task Contract 明确“先只分析、不修改文件”。

## 6. Reasoning Effort

若当前版本支持 `--effort`：

- `low`：简单查询、非常小变更；
- `medium`：一般功能；
- `high`：复杂架构、跨模块重构、疑难 bug。

不要默认全部 high。监督开发的可靠性主要来自分工和验证，而不是无限增加推理成本。

## 7. Permission Strategy

不要默认使用全局自动批准权限的危险参数。

### 通常可在 Task Contract 内继续

- 读取 workspace 文件；
- 修改 Scope 内代码；
- 本地 lint/test/build；
- 无外部副作用的只读检查。

### 应停止或请求用户

- 登录/OAuth；
- 任务未声明的外部系统；
- workspace 外敏感目录；
- 大量删除；
- reset/rebase/force；
- push/merge/release/deploy；
- 全局工具配置；
- 安装未知 plugin/hook/MCP；
- 改 tty7 server 或其他 agent 会话。

## 8. Interactive vs Headless

`agy -p` 适合脚本、一次性查询和结构化输出，但在 tty7 worker 中默认使用 interactive AGY：

- 用户能看到真实过程；
- Codex 可 capture 当前 TUI；
- permission/question 可处理；
- turn 中断后可在同一 session follow-up；
- worker 可被人工接管。

不要为了“结构化输出更好解析”而把默认监督 worker 改成一次性 `-p`；那会牺牲 tty7 作为可观察持久 PTY 的主要价值。

## 9. Conversation Resume

较新的 AGY 可能支持：

```bash
agy --conversation <id>
```

是否存在和语义以本机 `agy --help` 为准。

### v2.1 规则

- 只有掌握真实、经过验证的 conversation id 才 resume；
- 不从 pane id、workspace id 或其他编号猜 conversation id；
- tty7 能否自动保存/恢复 AGY session 取决于当前 tty7 integration 是否能取得 AGY session id；不能作为 v2.1 正常成功路径的强依赖；
- 没有可靠 id 时，replacement worker 使用 Task Contract + 当前 Git diff + Review Evidence 重建上下文。

## 10. Custom Agent Strategy

如果 AGY 当前版本支持 Markdown custom agent / `--agent`，可额外定义 implementer，但它不是 v2.1 强制依赖。

建议行为：

- 只在 Task Contract Scope 内实现；
- AGY 是唯一主要 Writer；
- 不 push / merge / deploy；
- 不回滚 baseline 用户改动；
- 不把“应该通过”写成“已经通过”；
- 完成后准确报告修改文件和真实测试命令；
- 遵守 `TURN_COMPLETE:<nonce>` 协议；
- 收到证据返工后优先处理 blocking issue，不顺手扩 scope。

## 11. 版本更新后的动作

AGY 或 tty7 版本变化时：

1. 重新检查 `agy --help`；
2. 重新检查 `tty7 doctor` / AGY hook capability；
3. 检查 workspace、permission、mode、conversation 行为；
4. 如果 tty7 新增 AGY native status hook，优先启用 native-status，但保留 fallback 作为兼容路径；
5. 必要时更新本文件和 `CHANGELOG.md`；
6. 不把完整 CLI 百科塞回主 `SKILL.md`。