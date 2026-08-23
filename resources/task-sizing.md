# Task Sizing — Small / Medium / Large

AGY Supervised Development 3.1 不要求所有任务走同样重的流程。第一步是 **Size the work before planning the work**：先判断任务需要多重的决策、规格和拆分，再决定流程深度。

目标不是估算工时，而是判断 **不确定性、传播面、可逆性和 Agent 上下文负担**。

---

## 1. 三种规模

### Small

典型特征：

- 目标和正确行为已经清楚；
- 改动局部，blast radius 可快速穷举；
- 没有重要架构/产品决策；
- 没有高风险 one-way door；
- 一个实现上下文可以完成并验证。

典型例子：

- 明确根因的 NPE / validation bug；
- 小范围字段校验；
- 单个接口的局部行为修正；
- 小型配置或映射修正。

默认流程：

```text
INTAKE
→ SIZED(Small)
→ COMPACT SPEC / TASK CONTRACT
→ IMPLEMENT
→ REVIEW
→ VERIFY
→ CLOSEOUT
```

Small **不强制**单独 Shape 文档、多个 Slice 或 Decision Map。

---

### Medium

典型特征：

- 目标基本明确，但存在若干需要确认的行为/边界；
- 涉及多个模块或层；
- 可以拆成 2–5 个独立可验证的 vertical slices；
- 需要显式 Spec、Acceptance Criteria 和 Test Seams；
- 一个大任务直接交给 Worker 容易产生遗漏或上下文膨胀。

典型例子：

- 新增正常业务功能；
- 新模块的一部分能力；
- UI → API → DB 的完整流程；
- 有几个 caller/consumer 的协议调整。

默认流程：

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

Medium 是 3.1 的默认主流程。

---

### Large

典型特征：

- 目标很大，路径还不清楚；
- 存在多个相互依赖的设计决策；
- 超过一个 Agent session 能稳定承载的范围；
- 跨项目、跨协议、重大迁移或大型重构；
- 有明显的“现在知道以后还有问题，但目前还无法精确定义”的区域；
- 存在高代价、难回退或需要用户决策的 one-way doors。

典型例子：

- 新系统/大模块；
- 跨仓库协议升级；
- 数据模型大迁移；
- 大型架构重构；
- 多阶段平台能力建设。

默认流程：

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

Large 才使用 Wayfinding/Decision Map 思想；不要把它强加给普通任务。

---

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

可以使用以下判断：

| 维度 | Small | Medium | Large |
|---|---|---|---|
| Goal clarity | 高 | 中高 | 中低 |
| Open decisions | 0–1 个局部问题 | 少量 | 多个且相互依赖 |
| Blast radius | 局部 | 多模块/多层 | 跨系统/大范围 |
| Worker context | 单次轻松完成 | 需要切片 | 多 session / 多阶段 |
| One-way door | 无 | 少量可隔离 | 明显 |
| Spec | compact | required | required + decision map |
| Slicing | usually no | required | required / staged |

---

## 3. Size 不是锁死的

Sizing 是路由决策，不是承诺。

执行中发现：

- 新的关键 open decision；
- 预期外的大 blast radius；
- destructive migration / breaking contract；
- 一个 slice 实际无法独立验证；
- 上下文明显超过单次 Worker 稳定承载；

则允许升级：

```text
Small → Medium
Medium → Large
```

降级也允许，但必须有证据说明复杂度已消失。

不要为了保持最初标签而硬撑错误流程。

---

## 4. Sizing 输出

Codex 在进入下一阶段前记录：

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

这份记录应短而可解释。

---

## 5. Anti-patterns

### 所有任务都跑完整流程

结果：流程摩擦大、用户厌烦、Agent 花时间写形式化材料而不是解决问题。

### 所有任务都当 Small

结果：大任务直接塞给 Worker，出现上下文膨胀、隐含假设、partial implementation 和难 Review diff。

### 用文件数量判断规模

文件多不一定 Large；机械 rename 可能是 wide refactor。文件少也可能高风险，例如 auth/billing/生产迁移。

### 用“预计几小时”判断规模

3.1 的 size 是 **决策与执行结构**，不是人类工时估算。