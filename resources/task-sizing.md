# Task Sizing — Small / Medium / Large

AGY Supervised Development 3.3 不要求所有任务走同样重的流程。第一步是 **Size the work before planning the work**：先判断任务需要多重的决策、规格和拆分，再决定流程深度。

目标不是估算工时，而是判断 **不确定性、传播面、可逆性和 Agent 上下文负担**。

## 1. 三种规模

### Small

典型特征：目标和正确行为清楚、改动局部、无重要架构/产品决策、无高风险 one-way door、一个实现上下文可以完成并验证。

```text
INTAKE
→ SIZED(Small)
→ COMPACT SPEC / TASK CONTRACT
→ IMPLEMENT
→ REVIEW
→ VERIFY
→ CLOSEOUT
```

Small 不强制单独 Shape 文档、多个 Slice 或 Decision Map。

### Medium

典型特征：目标基本明确但有少量边界需要确认、涉及多个模块/层、可拆成 2–5 个独立可验证 vertical slices、需要显式 Spec/Acceptance/Test Seam。

```text
INTAKE
→ SIZED(Medium)
→ SHAPING
→ SPEC_READY
→ SLICED
→ slice-by-slice IMPLEMENT / REVIEW
→ GLOBAL VERIFY
→ CLOSEOUT
```

Medium 是 3.3 的默认主流程。

### Large

典型特征：目标大、多个相互依赖决策、超过单个 Agent session 稳定承载范围、跨项目/重大迁移/大型重构、存在明显 fog 或高代价 one-way doors。

```text
INTAKE
→ SIZED(Large)
→ DESTINATION
→ DECISION MAP / FOG
→ resolve decisions
→ SPEC_READY
→ SLICED
→ staged IMPLEMENT / REVIEW
→ GLOBAL VERIFY
→ CLOSEOUT
```

Large 才使用 Wayfinding/Decision Map；不要强加给普通任务。

## 2. 判断维度

Codex 至少评估：

```text
Goal clarity
Decision uncertainty
Blast radius
Cross-boundary count
One-way-door risk
Test complexity
Expected worker context size
Independent verifiability
```

| 维度 | Small | Medium | Large |
|---|---|---|---|
| Goal clarity | 高 | 中高 | 中低 |
| Open decisions | 0–1 个局部问题 | 少量 | 多个且相互依赖 |
| Blast radius | 局部 | 多模块/多层 | 跨系统/大范围 |
| Worker context | 单次轻松完成 | 需要切片 | 多 session / 多阶段 |
| One-way door | 无 | 少量可隔离 | 明显 |
| Spec | compact | required | required + decision map |
| Slicing | usually no | required | required / staged |

## 3. Size 不是锁死的

执行中发现新的关键 decision、预期外 blast radius、destructive migration/breaking contract、slice 无法独立验证、上下文显著膨胀时，可以升级 Small→Medium→Large。降级也允许，但必须有证据。

## 4. Sizing 输出

```text
Task Size: Small | Medium | Large
Why:
- uncertainty:
- blast radius:
- one-way doors:
- context size:

Required Path:
- shaping: yes/no
- spec: compact/full
- slicing: yes/no
- decision map: yes/no
```

保持短而可解释。

## 5. Anti-patterns

- 所有任务都跑完整流程 → 形式摩擦；
- 所有任务都当 Small → 隐含假设、partial implementation；
- 用文件数量判断规模 → 不能代表风险；
- 用“预计几小时”判断规模 → 错把治理复杂度当工时。

3.3 的 size 是**决策与执行结构**，不是人类工时估算。
