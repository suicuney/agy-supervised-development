# Skill Evals — v3.3 Alpha 2

`evals/scenarios.json` 验证 AGY Supervised Development 的核心监督边界、中文计划可见性与 Herdr-only Runtime，不做排列组合测试。

最低回归面：

```text
Small task stays compact
Real user decision is not guessed
Sol High plan review defaults on
First Sol Send shows a concise Chinese plan
First Sol Send asks for confirmation once
Later REVISE rounds do not repeat confirmation
Final reviewed plan is shown in Chinese without a second confirmation
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
ego-browser / ego-lite remains Codex-owned verification tooling and sole browser transport
Transport precedence belongs to resources/ego-browser-runbook.md
Duplicate-send safety prevents automatic resend from UNKNOWN
Three pre-send failure states (auth, control conflict, model mismatch) trigger explicit handling
Closeout remains required before ACCEPTED
Baseline evidence is captured before AGY writes
```

## 原则

```text
一条核心边界一个场景
Deterministic validators 检查机器契约
Semantic evals 检查 Agent 行为
用户只在第一轮 Sol Send 前确认一次
最终计划必须中文可见
Herdr 管运行，不管结论
```

## 通过标准

```text
workflow transition correct
+ plan ownership remains Codex-owned
+ first Sol Send is informed and confirmed once
+ later Sol rounds do not repeatedly interrupt the user
+ final reviewed plan is visible before PLAN FROZEN
+ Sol High exits after PLAN FROZEN
+ Herdr remains the only AGY runtime
+ AGY remains primary writer
+ Review / Verify / Closeout boundaries remain separate
+ forbidden early ACCEPTED never occurs
```
