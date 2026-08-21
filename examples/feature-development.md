# Example: 中型功能开发（v2.1）

场景：给现有服务增加“按状态过滤”的查询能力并补测试，不改变现有默认行为。

## 1. Codex 建立 Baseline

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
git rev-parse HEAD
```

读取项目规则、查询实现、API contract 和测试约定。

## 2. Preflight

```bash
command -v agy
agy --version 2>/dev/null || true
agy --help

tty7 doctor
tty7 agents --json
tty7 pane ls --all --json
```

记录：

```text
agy capabilities = ...
tty7 AGY status mode = native-status | capture-fallback
```

如果 AGY 可识别但没有 status hook，不阻塞，选择 `capture-fallback`。

## 3. 创建 Worker Workspace

```bash
read -r WS PANE < <(
  tty7 new --json "$repo_root" |
  python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"], "%%%d" % d["pane"])'
)
```

从此只操作 `$WS` / `$PANE`。

## 4. 启动 AGY + Launch Proof

假设当前 AGY 支持 `--add-dir`：

```bash
tty7 send "$PANE" "agy --add-dir '$repo_root'" --enter
tty7 capture "$PANE" --plain | tail -5
```

如果命令仍停在 shell prompt，只补一次：

```bash
tty7 send "$PANE" --enter
```

然后：

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

确认 AGY 真正启动。

## 5. Workspace Verification

先 Read Before Send，然后要求 AGY 返回：

```text
- repository root
- branch
- 一个已知项目文件
```

并与 Codex 自己的 `git rev-parse --show-toplevel` / branch 比对。

只有一致才进入正式 Turn。

## 6. Task Contract

```text
Goal
- 为现有查询接口增加可选 status 过滤。
- 未提供 status 时保持当前行为完全不变。

Scope
- 只修改查询相关 controller/service/repository 和对应测试。

Constraints
- 不改变默认排序和分页语义。
- 不新增第三方依赖。
- 不修改无关模块。

Acceptance Criteria
- status 缺省：结果与改动前一致。
- status 合法：只返回匹配状态。
- status 非法：遵循现有参数错误规范。
- 有覆盖以上行为的测试。

Verification
- 跑查询模块 targeted tests。

Run Policy
- AGY 是唯一主要 Writer。
- 不 push / merge / deploy。
- 不回滚 baseline 用户改动。
- 不扩大 Scope。

Completion Protocol
- 本轮结束后输出 TURN_COMPLETE: A7F2E9
```

发送前先 capture 当前 pane。

## 7. 等待本 Turn 返回

### Native status

```bash
tty7 wait "$PANE" --until waiting,done --changed --timeout 1800
```

### Capture fallback

```bash
tty7 agents --json
tty7 capture "$PANE" --plain
```

看到当前 `TURN_COMPLETE: A7F2E9`，或明确看到 AGY 已返回 prompt 后，进入 Review。

`TURN_COMPLETE` 不等于 PASS。

## 8. Codex 独立 Review

```bash
git status --short
git diff --stat
git diff --check
git diff
```

重点：

- status 缺省是否真的保持默认行为；
- 是否复用已有过滤机制；
- 非法参数是否符合 contract；
- tests 是否覆盖缺省/合法/非法；
- task-introduced changed paths 是否超出 Scope。

## 9. Evidence-driven Rework

假设发现 `status=null` 仍追加 SQL 条件。

先 capture，确认 AGY 当前可以接收新输入。生成新 nonce `C291B4`，发送：

```text
REWORK

Issue
- status 缺省时仍进入新增过滤逻辑，会改变现有默认查询。

Evidence
- <file>:<line> 对 null 进行了错误映射，repository 最终仍拼接 status 条件。

Expected
- 未提供 status 时查询语义必须与改动前一致。

Required change
- 复用现有 optional-filter 模式修正，并补缺省 status regression test。

Re-run
- <targeted test command>

Completion Protocol
- 完成本轮后输出 TURN_COMPLETE: C291B4
```

AGY 修复后，Codex 从完整相关 diff 重新 Review，不只看最后几行。

## 10. 独立 Verification

Codex 自己运行相关门禁：

```text
lint / typecheck
unit tests
targeted integration tests
build/package
```

再：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

只有真实 repository state、需求覆盖和独立测试都满足，Supervisor 才进入 `ACCEPTED`。

## 11. Cleanup

如果用户没有要求保留 AGY：

```bash
tty7 ws rm "$WS"
```

如果用户希望继续观察/接管，则保留并汇报稳定 `WS` / `PANE`。