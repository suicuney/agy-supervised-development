# Example: 中型功能开发

这个例子展示 `agy-supervised-development` 的推荐闭环，不绑定具体语言或框架。

## 场景

用户要求：

> 给现有服务增加一个“按状态过滤”的查询能力，并补测试，不改变现有默认行为。

## 1. Codex 建立 baseline

```bash
repo_root="$(git rev-parse --show-toplevel)"
git status --short
git diff --stat
git branch --show-current
```

读取项目规则和现有查询实现，确认 API contract、测试命令和相关模块。

## 2. AGY Preflight

```bash
command -v agy
agy --version 2>/dev/null || true
agy --help
tty7 doctor
```

确认当前 AGY 支持哪些 workspace/mode 能力。

## 3. 创建隔离 pane

```bash
tty7 new --json "$repo_root"
```

若支持显式目录绑定，启动时绑定目标仓库；随后要求 AGY 返回实际 repo root 和当前分支，验证没有串项目。

## 4. Task Contract

发送给 AGY 的内容可以类似：

```text
Goal
- 为现有查询接口增加可选 status 过滤。
- 未提供 status 时保持当前行为完全不变。

Scope
- 只修改查询相关 controller/service/repository 和对应测试。

Context
- 现有 API contract 已定义查询接口。
- 当前 repository 已支持其他过滤条件。

Constraints
- 不改变默认排序和分页语义。
- 不新增第三方依赖。
- 不修改无关模块。
- 不 push / merge / deploy。

Acceptance Criteria
- status 缺省：结果与改动前一致。
- status 合法：只返回匹配状态。
- status 非法：遵循项目现有参数错误规范。
- 有覆盖以上行为的测试。

Verification
- 跑查询模块 targeted tests。

Report
- 报告修改文件、实现方式和真实测试结果。
```

## 5. AGY 实现后，Codex 独立 Review

```bash
git status --short
git diff --stat
git diff --check
git diff
```

重点检查：

- 是否真的保持默认行为；
- 是否重复实现已有过滤机制；
- 参数错误行为是否符合项目规范；
- 是否修改了不相关文件；
- 测试是否包含缺省、合法和非法场景。

## 6. 发现问题时返工

例如发现 AGY 在 `status=null` 时仍追加 SQL 条件：

```text
REWORK
- Issue: status 缺省时仍进入新增过滤逻辑，会改变现有默认查询。
- Evidence: <file>:<line> 对 null 进行了错误映射，repository 最终仍拼接 status 条件。
- Expected: 未提供 status 时查询语义必须与改动前一致。
- Required change: 复用现有 optional-filter 模式修正，并补缺省 status regression test。
- Re-run: <targeted test command>
```

AGY 修复后，Codex 再从头检查相关 diff，而不是只看它新改的几行。

## 7. 独立验收

Codex 自己运行项目规定的相关门禁，例如：

```text
lint / typecheck
unit tests
targeted integration tests
build/package
```

最后再复核：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

只有真实 repository state、需求覆盖和独立测试都满足，才能最终 PASS。
