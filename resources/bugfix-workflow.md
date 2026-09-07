# Bugfix Workflow — Evidence Before Guessing

本文件定义 AGY Supervised Development 3.3 的 Bug 分流与证据要求。

目标不是把每个 Bug 都流程化，而是防止复杂 Bug 进入：

```text
看几眼代码
→ 猜一个原因
→ 改
→ 测试绿
→ 误以为修好
```

核心原则：

> **先建立能抓住这个 Bug 的反馈环，再让实现围绕证据推进。**

## 1. 先判断 Bug 类型

### Simple / Deterministic Bug

满足大部分：症状明确、可安全稳定复现、根因空间小、正确 Verification Seam 已知、一个 Worker context 足够。

```text
REPRODUCE
→ RED
→ ROOT-CAUSE FIX
→ GREEN
→ CODEX RE-RUN
```

### Complex / Uncertain Bug

出现 flaky、性能、跨服务/线程/异步、多个 hypothesis、真实数据依赖或现有测试抓不住症状时：

```text
FEEDBACK LOOP
→ REPRODUCE
→ MINIMISE
→ HYPOTHESES
→ INSTRUMENT
→ ROOT CAUSE
→ REGRESSION
→ FIX
→ VERIFY ORIGINAL REPRO
```

## 2. Build a Tight Feedback Loop

按实际情况优先：

```text
1. failing test at the real seam
2. curl / HTTP script
3. CLI fixture invocation
4. browser automation
5. captured trace replay
6. minimal throwaway harness
7. stress/property/fuzz loop
8. differential old-vs-new loop
9. git bisect runnable check
10. structured HITL reproduction as last resort
```

完成标准：Red-capable、Deterministic（或显著提高复现率）、Fast、Agent-runnable。

## 3. Reproduce and Minimise

先确认反馈环复现的是**同一个 Bug**，再最小化输入、调用方、配置、数据、步骤、并发条件和时间窗口。每次只移除一个变量并重跑。

## 4. Ranked, Falsifiable Hypotheses

复杂 Bug 默认形成 3~5 个有排序 hypothesis：

```text
Hypothesis H1
Cause:
Prediction:
Probe:
What would falsify it:
```

无法提出证伪方式的“感觉”不算强 hypothesis。产品/风险取舍仍返回 Shaping。

## 5. Instrument One Prediction at a Time

Instrumentation 必须服务某个具体 prediction。优先 debugger / profiler / targeted instrumentation，避免到处加日志。临时 instrumentation 在最终 Review 前清理。

性能 Bug 必须有 baseline measurement 和 change 后对比，不能只说“感觉更快”。

## 6. Root Cause Finding

宣布 Root Cause 前应能回答：

```text
Symptom:
Minimal repro:
Root cause:
Why this cause produces the symptom:
Evidence that distinguishes it from rejected hypotheses:
Same cause elsewhere:
```

“改这里以后绿了”本身不够。

## 7. Regression Proof

如果存在正确公共 Verification Seam：

```text
same regression proof
unfixed behavior → RED
root-cause fix
same proof → GREEN
Codex independent re-run → GREEN
```

没有正确 seam 时记录 N/A 原因和替代证据，不为形式制造无法抓真实症状的测试。

## 8. Verify the Original Repro

Minimal regression 绿以后，还必须重新执行最初 feedback loop / 原始未最小化场景。

```text
Original repro before: RED
Minimal repro: RED
Regression proof after: GREEN
Original repro after: GREEN
```

## 9. Cleanup

进入 Review 前确认：

```text
临时 debug logs removed
throwaway harness deleted or clearly isolated
profiling artifacts not accidentally committed
secret/captured auth data redacted
final tests target public behavior where possible
```

来源不明或可能属于用户 baseline 的文件不能擅自删除。

## 10. 与 Three-Axis Review 的关系

```text
Spec Fidelity
- 用户症状/冻结修复目标真的被满足了吗？

Engineering Quality
- root-cause fix 是否健康？
- regression test 是否绑定内部实现？

Completeness
- 同一 root cause 在 sibling/reachable path 是否仍存在？
```

```text
feedback loop 找原因
Three-Axis Review 判断交付
Independent Verification 重新跑证据
```

三者不能互相代替。
