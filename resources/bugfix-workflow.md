# Bugfix Workflow — Evidence Before Guessing

本文件定义 AGY Supervised Development 3.1 的 Bug 分流与证据要求。

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

---

## 1. 先判断 Bug 类型

### Simple / Deterministic Bug

满足大部分：

```text
症状明确
可安全稳定复现
根因空间小
正确 Verification Seam 已知
一个 Worker context 足够
```

使用 compact path：

```text
REPRODUCE
→ RED
→ ROOT-CAUSE FIX
→ GREEN
→ CODEX RE-RUN
```

### Complex / Uncertain Bug

出现任一强信号：

```text
偶发 / flaky
性能退化
跨服务/跨线程/异步链路
症状与根因距离远
多个 plausible hypotheses
生产/真实数据依赖
现有测试无法抓住用户症状
```

使用完整 Bug Intelligence：

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

---

## 2. Phase 1 — Build a Tight Feedback Loop

复杂 Bug 在提出根因结论前，优先建立一个可重复执行的 pass/fail signal。

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

完成标准：

```text
Red-capable — 能抓住用户描述的这个症状
Deterministic — 或至少把 flaky 复现率提高到可调试水平
Fast — 尽可能秒级/短周期
Agent-runnable — Worker/Codex 可重复运行
```

没有 feedback loop 时不要把“代码看起来可能是 X”包装成 root cause。

---

## 3. Phase 2 — Reproduce and Minimise

先确认反馈环真的复现的是**同一个 Bug**，而不是附近另一个错误。

然后最小化：

```text
输入
调用方
配置
数据
步骤
并发条件
时间窗口
```

每次只移除一个变量并重跑，直到剩余元素基本都是 load-bearing。

最小复现的价值：

- 缩小 hypothesis space；
- 形成更准确 regression test；
- 降低 AGY 为了“顺便修周边”产生 scope drift 的概率。

---

## 4. Phase 3 — Ranked, Falsifiable Hypotheses

复杂 Bug 默认先形成 3~5 个有排序的 hypothesis，而不是只保留第一个直觉。

每个 hypothesis 使用：

```text
Hypothesis H1
Cause:
Prediction:
Probe:
What would falsify it:
```

要求 Prediction 可证伪，例如：

```text
如果缓存失效顺序是根因，禁用缓存后错误应消失；
如果事务边界是根因，把读取移入同一事务后症状应改变；
```

不能提出验证方式的“感觉”不算强 hypothesis。

真正涉及产品语义/风险取舍的问题仍返回 Shaping；技术假设由 Codex/AGY 用证据验证。

---

## 5. Phase 4 — Instrument One Prediction at a Time

Instrument 必须服务于某个具体 hypothesis。

优先：

```text
debugger / REPL / profiler
→ targeted instrumentation
→ narrow logs/metrics/traces
```

避免：

```text
到处加 log 再 grep
一次改多个变量
把 debug instrumentation 混进最终代码
```

临时 instrumentation 使用明显唯一标记，便于 Closeout 前清理。

性能 Bug：

```text
baseline measurement
→ profile/query plan/timing evidence
→ change
→ compare measurement
```

不要仅凭“感觉更快”。

---

## 6. Phase 5 — Root Cause Finding

宣布 Root Cause 前应能回答：

```text
Symptom:
Minimal repro:
Root cause:
Why this cause produces the symptom:
Evidence that distinguishes it from rejected hypotheses:
Same cause elsewhere:
```

如果只能说“改了这里以后绿了”，还不够证明 root cause。

---

## 7. Phase 6 — Regression Proof

如果存在正确的公共 Verification Seam：

```text
same regression proof
unfixed behavior → RED
root-cause fix
same proof → GREEN
Codex independent re-run → GREEN
```

如果没有正确 seam：

```text
Regression Proof = not-applicable / architecture-gap
Reason = <why existing seam cannot represent the real bug>
Alternative Evidence = <original feedback loop / integration fixture / trace replay>
```

不要为了形式在错误 seam 写一个永远绿、无法抓真实症状的测试。

---

## 8. Phase 7 — Verify the Original Repro

Regression test 绿以后，还必须重新执行最初的 feedback loop / 原始未最小化场景。

因为：

```text
minimal regression green
!=
original user symptom definitely gone
```

最终至少记录：

```text
Original repro before: RED
Minimal repro: RED
Regression proof after: GREEN
Original repro after: GREEN
```

适用时再加性能/flake rate 前后数据。

---

## 9. Cleanup

进入 Review 前确认：

```text
临时 debug logs removed
throwaway harness deleted or clearly isolated
profiling artifacts not accidentally committed
secret/captured auth data redacted
final tests target public behavior where possible
```

来源不明或可能属于用户 baseline 的 debug 文件不能擅自删除。

---

## 10. 与 Three-Axis Review 的关系

Bug 修复完成后仍进入三轴：

```text
Spec Fidelity
- 用户症状/冻结修复目标真的被满足了吗？

Engineering Quality
- root-cause fix 是否健康？是否只是 swallow/error masking？
- regression test 是否绑定内部实现？

Completeness
- 同一 root cause 在 sibling/reachable path 是否仍存在？
```

所以：

```text
feedback loop 找原因
Three-Axis Review 判断交付
Independent Verification 重新跑证据
```

三者不能互相代替。