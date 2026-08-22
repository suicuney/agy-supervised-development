# Skill Evals

本目录用于验证 `agy-supervised-development` 自己的监督行为，而不是验证某个业务项目。

v2.1.2 首先采用**场景契约 eval**：给 Supervisor 一个仓库状态/AGY 行为/任务条件，检查它是否得到正确的状态转换、Gate 结论和禁止动作。

场景定义见 `scenarios.json`。

## 为什么需要 Evals

这个 Skill 已经包含：

```text
baseline
tty7 ownership
launch proof
native/fallback observation
workspace binding
review/rework
completeness/blast radius
test layer decision
regression proof
independent verification
knowledge closeout
cleanup
```

仅靠读 Markdown 很容易出现跨文件规则冲突。Evals 的目标是固定最危险的 near-miss：**看起来可以 PASS，但其实必须 REWORK/BLOCK；看起来应该改文档，但其实必须保持零 diff。**

## 场景结果字段

每个 case 至少验证：

- `expected_state`：最终应停在哪个 Supervisor state；
- `must_do`：必须执行/报告的动作；
- `must_not_do`：禁止行为；
- `expected_gate`：关键 Gate 结论；
- `notes`：为什么这个 case 有价值。

## 使用方式

当前仓库不绑定某个特定 eval harness，因此先保持 portable：

1. 将 `scenarios.json` 的一个 case 作为测试上下文交给支持本 Skill 的 Supervisor；
2. 不要求真的执行破坏性动作，可用 fixture repo / mock tty7/AGY transcript；
3. 比较 Supervisor 的计划、Gate 结论、状态转换和最终报告是否满足 assertions；
4. 修改 Skill 规则后优先回归这些 cases。

未来如果引入自动 grader，可以直接读取 JSON，不需要改场景语义。

## 最低回归集

每次修改核心流程，至少覆盖：

```text
dirty baseline
false done
missing tty7 status hook
scope drift
hidden caller / partial propagation
bugfix red-green
wrong test layer
stale docs after API change
internal bugfix with zero doc diff
one-way decision
```

## 通过标准

一个 eval 不是“最终回答看起来合理”就算通过。必须同时满足：

```text
State transition correct
+ Gate verdict correct
+ Evidence source correct
+ Forbidden action not performed
+ Acceptance not reached early
```

特别注意：

- `TURN_COMPLETE` 不能让 case 提前 PASS；
- current diff green 不能跳过 Completeness Review；
- tests green 不能跳过 Test Layer Decision；
- `CODE_VERIFIED` 不能跳过 Knowledge Closeout；
- `user-skipped` E2E 不能被报告成 `not-applicable`；
- 可复现 bug 没有 RED proof 不能被包装成完整 regression proof。