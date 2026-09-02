# Skill Evals — v3.2 Alpha 3

`evals/scenarios.json` 只验证 AGY Supervised Development 的核心监督边界，不做排列组合测试。

最低回归面：

```text
Small task stays compact
Real user decision is not guessed
Sol High plan review defaults on
Explicit user opt-out skips Sol review
Sol review never exceeds 3 rounds
PLAN FROZEN means Sol High exits
AGY SUCCESS is not Review PASS
Three-Axis verdicts remain independent
Verification failure returns to Rework + full Review
Chrome DevTools MCP remains Codex-owned verification tooling
Required unavailable verification cannot become CODE_VERIFIED
Closeout remains required before ACCEPTED
```

## 原则

```text
一条核心边界一个场景
不为 UI/模型/状态排列组合复制测试
Deterministic validators 检查机器契约
Semantic evals 检查 Agent 行为
```

## 通过标准

```text
workflow transition correct
+ plan ownership remains Codex-owned
+ Sol High exits after PLAN FROZEN
+ AGY remains primary writer
+ Review / Verify / Closeout boundaries remain separate
+ forbidden early ACCEPTED never occurs
```
