# Closeout Contract Template

仅在 `CODE_VERIFIED` 后使用。确实需要 AGY 修改知识文件时，优先发送给当前**同一个 Herdr-managed AGY worker**；Herdr 负责 session continuity。如果 exact session 不可恢复，不猜其他 conversation，而是按 `resources/closeout-governance.md` 的恢复规则处理。

```text
Closeout Contract

Source of Truth
- final verified diff
- final code/schema/config/tests
- Codex Completeness evidence
- Codex Independent Verification results

Runtime Target
- Herdr Agent: <stable task-local AGY name>

Goal
- 让项目知识面与最终实现一致；不是继续扩展功能。

Inspect
- README / usage
- AGENTS.md / CLAUDE.md / project rules
- API / schema / shared contracts
- config / env / CLI / runtime docs
- stale examples / retired symbols
- workspace residue

Required
1. 对每个相关知识面标：verified-current | changed-and-verified | pending | out-of-scope | not-applicable。
2. 只修改受 final implementation 直接影响的知识文件。
3. stale current-state 说明就地更新，不制造第二份权威文档。
4. 不把开发流水账写入长期 README/rules。
5. residue 默认报告 deletion-candidate，除非删除已明确安全授权。

Forbidden
- unrelated production-code redesign
- new feature work
- speculative cleanup
- destructive delete
- credential exposure
- push / merge / release / deploy

Report
- knowledge surfaces checked
- status per surface
- changed files
- stale-reference searches
- pending/out-of-scope/deletion-candidate
```

## 规则

- Closeout 允许零 diff：如果所有相关知识面都已经正确，记录 `verified-current` 即可。
- 如果 Closeout 暴露真实代码缺陷，停止知识修补，退回 Codex 的 Review / Verification。
- Herdr `done` / AGY self-report 不等于 Closeout PASS；Codex 仍需重新检查 Git 和 stale references。
