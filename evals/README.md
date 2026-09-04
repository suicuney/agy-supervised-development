# Skill Evals — v3.3 Alpha 1

`evals/scenarios.json` 验证 AGY Supervised Development 的核心监督边界与 Herdr-only Runtime，不做排列组合测试。

最低回归面：

```text
Small task stays compact
Real user decision is not guessed
Sol High plan review defaults on
Explicit user opt-out skips Sol review
Sol review never exceeds 3 rounds
PLAN FROZEN means Sol High exits
Every AGY writer runs through Herdr
Herdr preflight failure blocks instead of switching runtimes
Workspace/pane identity comes from Herdr returned JSON
AGY launches with --kind agy
Blocked state is read before interaction
Herdr done/idle is not Review PASS
Native session restore failure never guesses another conversation
Three-Axis verdicts remain independent
Verification failure returns to Rework + full Review
Chrome DevTools MCP remains Codex-owned verification tooling
Closeout remains required before ACCEPTED
Baseline evidence is captured before AGY writes
```

## 原则

```text
一条核心边界一个场景
Deterministic validators 检查机器契约
Semantic evals 检查 Agent 行为
Herdr 管运行，不管结论
```

## 通过标准

```text
workflow transition correct
+ plan ownership remains Codex-owned
+ Sol High exits after PLAN FROZEN
+ Herdr remains the only AGY runtime
+ AGY remains primary writer
+ Review / Verify / Closeout boundaries remain separate
+ forbidden early ACCEPTED never occurs
```
