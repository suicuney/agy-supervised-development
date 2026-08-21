# AGY Runtime Reference

本文件只保存 `agy-supervised-development` 监督流程真正需要的 AGY 运行时知识。不要把它当完整 CLI 百科；执行时始终以本机 `agy --help` / `agy --version` 为准。

## 1. 核心原则

**Capability Detection > Capability Assumption**

每次任务开始先检查：

```bash
command -v agy
agy --version 2>/dev/null || true
agy --help
```

如果本文件与当前安装版本冲突，以本机输出为准。

## 2. 监督开发最相关的能力

以下能力在较新的 AGY 版本中可能存在，但必须运行时确认：

- `--add-dir <path>`：显式把目录加入当前 workspace/context。
- `--mode <mode>`：选择执行模式，例如 `plan`、`accept-edits`。
- `--effort <level>`：选择推理强度，例如 `low` / `medium` / `high`。
- `--agent <agent>`：指定自定义 agent。
- `--model <model>`：指定模型。
- `--sandbox`：使用受限执行环境。
- `--continue` / `--conversation`：继续已有会话。
- `--print` / `-p`：非交互执行。
- `--output-format`：结构化输出能力。

监督开发默认优先**交互式 tty7 pane**，因为需要观察 trust、permission、任务过程和返工状态；不要仅为了方便就切到 headless。

## 3. Workspace / Project Context

AGY 可能保留持久化的 workspace/project/conversation 状态，因此：

```text
shell CWD == repo_root
```

不等价于：

```text
AGY internal context == repo_root
```

### 推荐策略

1. tty7 pane 自身 cwd 指向 `repo_root`；
2. 若当前版本支持 `--add-dir`，启动时显式绑定；
3. 启动后要求 AGY 回报/执行仓库 root；
4. 让 AGY读取一个目标仓库中的已知文件；
5. 若输出出现其他项目名、旧路径、旧任务上下文，立即停止。

不要把 `--continue` / 恢复旧 conversation 当成默认策略。监督式开发更重视**任务隔离**，除非用户明确要求恢复上下文，或你能验证恢复会话与当前 repo 完全一致。

## 4. Execution Mode Strategy

### `default`

适合：

- 需要 AGY 自身也保留编辑审查/确认；
- 高风险代码区域；
- 监督者希望多一道人工式保护。

缺点：Codex 已经会做外层 Review 时，可能产生重复确认。

### `accept-edits`

适合：

- 小到中型、范围清晰的实现；
- Codex 已建立 Git baseline；
- Codex 会完整 Review 最终 diff。

注意：接受编辑不等于允许所有 shell、网络、权限或破坏性操作。不要把文件编辑策略和全局权限策略混为一谈。

### `plan`

适合：

- 大型重构；
- 跨模块需求；
- 数据模型/API contract 改造；
- 风险高、实现路径不唯一的任务。

推荐流程：

```text
AGY Plan
  ↓
Codex Review Plan
  ↓
AGY Implement
  ↓
Codex Review Code
```

如果当前版本没有 `--mode plan`，可以用 Task Contract 明确要求 AGY “先分析和给方案，不修改文件”，达到等价的监督效果。

## 5. Reasoning Effort

如果当前 AGY 支持 `--effort`：

- `low`：简单查询、非常小的变更；
- `medium`：一般功能开发；
- `high`：复杂架构、跨模块重构、疑难 bug。

不要默认所有任务都开最高 effort。监督式开发追求的是**正确分工和验证**，不是单纯增加推理成本。

## 6. Agent Strategy

如果 AGY 支持 Markdown custom agent / `--agent`，可以额外定义一个专属 implementer，例如：

```yaml
---
name: supervised-implementer
description: Implementation worker controlled by an external supervisor
subagent: false
commandExecutionPolicy: ask
---
```

其行为约束建议包括：

- 只在 Task Contract 范围内实现；
- 不自行 push / merge / deploy；
- 不回滚已有用户改动；
- 不把“测试应该通过”写成“测试已通过”；
- 完成后准确报告修改文件和实际测试命令；
- 接到 Reviewer 返工意见后优先修正证据指出的问题。

是否启用自定义 agent 应由当前环境能力和用户习惯决定，不是 v2 的强制依赖。

## 7. Permission Strategy

不要默认使用全局自动批准权限的危险参数。

监督模式下应区分：

### 通常可自动继续

- 读取 workspace 文件；
- 在 Task Contract 范围内修改文件；
- 本地 lint/test/build；
- 不产生外部副作用的只读检查。

### 应停止或请求用户决定

- 登录/账号授权；
- 访问任务未声明的外部系统；
- 读取 workspace 外敏感目录；
- 删除大量文件；
- reset/rebase/force 等历史修改；
- push/merge/release/deploy；
- 修改全局工具配置；
- 安装未知 plugin/hook/MCP；
- 改变 tty7 server 或其他 agent 会话。

## 8. Headless / Print Mode

`agy -p` 适合脚本化、一次性查询和结构化输出，但不是监督开发默认入口。

如果未来需要使用 headless：

- 先确认首次登录/初始化已完成；
- 明确 timeout；
- 明确权限策略；
- 尽量使用结构化输出；
- 不要因为 headless 卡住就无脑追加“跳过所有权限”；
- 仍要由 Codex 检查真实 repo state。

## 9. 版本更新后的动作

当发现 AGY 版本变化时：

1. 重新检查 `--help`；
2. 检查本 Skill 使用的关键 flag 是否仍存在；
3. 关注 workspace、permission、mode、conversation 行为变化；
4. 必要时更新本文件和 `CHANGELOG.md`；
5. 不因为新增功能就把所有 CLI 细节塞回主 `SKILL.md`。
