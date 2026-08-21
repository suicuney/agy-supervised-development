# AGY Supervised Development

一个面向 **Codex + Antigravity CLI (`agy`) + tty7** 的监督式开发 Skill。

它不是 AGY CLI 百科，而是一套开发治理流程：

```text
User Requirement
      ↓
Codex Supervisor
      ↓
AGY Implementer (isolated tty7 pane)
      ↓
Repository Changes
      ↓
Codex Independent Review
   ↙                 ↘
Rework → AGY       PASS → Independent Tests
                         ↓
                      Acceptance
```

## 核心原则

- Codex 负责主控、Review、QA 和最终验收。
- AGY 负责主要代码实现和返工。
- 不相信 Agent 自己的 `done`，只相信真实 repository state。
- 每次任务先建立 Git baseline，保护用户已有改动。
- AGY 必须运行在本 Skill 新建的独立 tty7 pane 中。
- 不假设 shell CWD 等于 AGY 内部 workspace；显式校验项目上下文。
- AGY 参数按当前安装版本实时检测，不把某个版本写死。
- 默认不 push / merge / deploy，不使用全局跳过权限的危险策略。

## v2 重点

v2 在原有监督闭环基础上增加：

1. **AGY Capability Detection**：先 `agy --help` / `--version`，再决定使用哪些参数。
2. **Workspace Binding Guard**：防止 AGY 复用旧项目 context 导致串仓库。
3. **Execution Mode Strategy**：按任务选择普通实现、快速编辑或 plan-first。
4. **Task Contract**：标准化 Goal / Scope / Constraints / Acceptance / Verification。
5. **Failure Mode Matrix**：针对启动、权限、串项目、测试失败、越界修改等确定处理方式。
6. **Repository Review Gates**：把 Scope、Architecture、Edge Case、Tests、Diff Hygiene 等审查维度显式化。
7. **Version-aware Runtime Reference**：AGY 工具知识独立维护，避免主 Skill 变成 CLI 手册。

## 文件结构

```text
agy-supervised-development/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── resources/
│   ├── agy-runtime.md
│   ├── failure-modes.md
│   └── review-gates.md
└── examples/
    └── feature-development.md
```

### `SKILL.md`

监督开发主流程。定义角色、基线、AGY preflight、workspace 绑定、Task Contract、Review/返工和最终验收。

### `resources/agy-runtime.md`

只保存监督流程真正需要的 AGY runtime 知识，包括 execution mode、workspace、permission、headless 等。

### `resources/failure-modes.md`

把“AGY 卡住了”拆成可诊断状态，避免盲目重复命令。

### `resources/review-gates.md`

Codex 独立 Review 的检查清单与 PASS / REWORK / BLOCKED 结论格式。

### `examples/feature-development.md`

一个中型功能从 baseline → Task Contract → AGY 实现 → Codex Review → 返工 → 验收的完整示例。

## 设计取向

这个 Skill 刻意不复制完整 AGY flag、快捷键、插件、credits、UI 等百科内容。原因是监督式开发真正需要的是：

```text
知道当前 AGY 能做什么
        ↓
正确约束它在目标仓库实现
        ↓
独立检查它实际做了什么
        ↓
有证据地返工
        ↓
最终验收
```

AGY 升级后优先更新 `resources/agy-runtime.md`，尽量保持 `SKILL.md` 的治理语义稳定。
