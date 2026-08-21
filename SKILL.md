---
name: agy-supervised-development
description: Use agy in a dedicated tty7 terminal for implementation while Codex independently reviews the working tree, runs verification, and drives rework through acceptance.
---

# agy 监督开发

当用户明确使用 `$agy-supervised-development`，或明确要求采用“Codex 监督 + agy 执行”开发时，按本流程工作。Codex 是主控、代码审查和验收者；agy（Antigravity CLI，命令为 `agy`）是主要编码执行者。

## 不可违反的边界

- 不把 agy 的 `done`、自述测试结果或摘要当成完成证明。每个重要阶段都必须独立检查实际文件、`git diff`、构建和测试结果。
- 主要生产代码由 agy 修改。Codex 负责审查、运行检查、提出精确返工意见，并通过 tty7 继续交给 agy 修正；不要直接承担主要编码工作。
- 只操作本次 skill 创建的 tty7 工作区/面板。已有的用户终端、其他 agent 面板和其他工作区一律只读，不得向其发送按键，也不得关闭。
- 不执行 push、merge、发布或其他超出用户任务的外部操作。除非用户另行明确授权，不改变提交历史。
- 尊重仓库已有改动：先记录基线，不能为了“清理”而回滚、覆盖或删除用户的改动。

## 1. 建立范围和基线

先确定仓库根目录并读取适用的 `AGENTS.md`、`CLAUDE.md` 或项目规则文件，再读取任务需求。记录：

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
```

把基线中的未提交改动与 agy 本次改动区分开。检查 `contracts/openapi.yaml`、测试约定和项目质量门禁；若是本仓库，遵守根目录 `AGENTS.md` 中 Java 21/Spring Boot 模块化单体、React 嵌入式发布、OpenAPI 权威契约及 Browser Worker 不参加默认构建等规则。

若用户尚未给出具体开发目标，只完成 agy 初始化和连通性验证，然后向用户索要明确目标，不开始编码。

## 2. 在右侧终端启动并验证 agy

使用 tty7，而不是在 Codex 自己的 shell 中直接启动 agy。先做只读检查：

```bash
command -v agy
tty7 doctor
tty7 agents
tty7 pane ls --all
```

如果 tty7 服务不可达，停止并告知用户，不要自行启动或重启 tty7 server。为本次任务创建独立工作区：

```bash
tty7 new --json "$repo_root"
```

从 JSON 结果取得新面板的数字 id，并以 `%<id>` 作为 pane 地址（例如 `%12`）。只在这个新 pane 中执行：

```bash
tty7 send "%<id>" 'agy' --enter
tty7 capture "%<id>" --plain
```

如果出现项目 trust 界面，只能在路径正好是 `repo_root` 且当前选项明确为 “Yes, I trust this folder” 时发送一次 Enter；其他权限、账号、网络或破坏性确认都要先停下并向用户说明。

agy 进入交互提示后，发送并读取：

```bash
tty7 send "%<id>" 'hello' --enter
tty7 capture "%<id>" --plain --scrollback
```

必须看到来自 agy 的实际响应，才认为启动成功。若看不到响应，先用 `tty7 capture` 和 `tty7 procs` 判断是启动慢、停在问题上还是进程退出；不要盲目重复发送。若 agent status hooks 可用，发送后用 `tty7 wait ... --changed`，防止读到上一轮 stale 的 `done`；hooks 不可用时以 capture/procs 为准，不要自行安装 hooks。

在启动、等待、遇到确认界面或发生阻塞时，用 commentary 简短告知用户当前状态；不要把中间状态伪装成完成。

## 3. 委派开发并分阶段监督

收到具体目标后，通过新 pane 把原始需求、验收条件、不可违反的仓库规则和“完成后报告修改/测试”要求发给 agy。任务较长时拆成可检查的阶段，例如：理解现状与方案、实现、针对性测试、收尾。

每个重要阶段（包括 agy 第一次说 done 之后）都执行以下闭环：

1. 读取 agy 的实际终端输出，确认它说做了什么。
2. 在 Codex 自己的 shell 独立检查 `git status --short`、`git diff --stat`、`git diff --check`、完整相关 diff、实际文件和测试；必要时用 `rg` 检查调用链、边界条件和重复实现。
3. 对照需求、仓库规则、现有架构和 API 契约审查：实现是否完整，是否引入架构偏离，是否遗漏错误处理/边界条件/权限/时区/持久化/API 生成物/测试，是否误改无关文件。
4. 只有检查通过才进入下一阶段。发现任何问题，就通过同一个 tty7 pane 给 agy 发送带证据的返工意见，要求它修改并重新验证；之后重新执行本闭环。

返工意见应包含文件和行号（如能确定）、实际观察到的行为、违反的需求/规则、期望行为和需要重跑的测试。不要只说“请修复”或接受没有证据的口头保证。

当 agy 请求输入时，先 capture 了解它在问什么，再只提供任务范围内的答案。遇到需要新权限、外部协调或会扩大范围的选择，停止并让用户决定。

## 4. 独立构建、测试和验收

实现稳定后，Codex 自己运行项目规定的质量门禁；不要把 agy 运行过的命令当作独立验证。优先使用仓库明确列出的命令，并遵守其顺序和环境要求。当前仓库的根目录 `AGENTS.md` 列出的门禁为：

```bash
pnpm check:api
pnpm lint
pnpm typecheck
pnpm test
./mvnw -f services/platform-server/pom.xml test
./mvnw -f services/platform-server/pom.xml verify -Pintegration
./mvnw -f services/platform-server/pom.xml package
docker compose --env-file .env.example -f deploy/docker-compose.dev.yml config
```

不要把 `workers/browser-worker` 纳入默认构建、CI 或发布。若某项门禁不适用于本次改动，说明原因并运行所有相关门禁；若失败，保留完整失败证据，通过 tty7 交给 agy 修正，再独立重跑。构建和测试通过后，再复核一次最终 `git diff`，确认没有生成物、临时文件、调试输出或无关改动混入。

验收完成的必要条件是：需求逐项满足、架构和项目规则没有冲突、关键边界已审查、独立门禁通过、最终 diff 可解释。任何一项不满足，都不能结束任务。

## 5. 结束和汇报

任务完成后，只清理本 skill 创建的 pane；若用户要求保留右侧终端供后续跟进则保留，并明确告知 pane 地址。最终用中文汇报：

- agy 完成了什么；
- 修改了哪些核心文件；
- Codex 独立审查发现了什么问题；
- 进行了哪些返工，以及返工后的结果；
- 实际运行的构建/测试及结果；
- 仍存在的风险、未覆盖项或待办；
- 明确说明没有执行 push、merge 或发布。
