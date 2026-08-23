# Closeout Contract Template

仅在 `CODE_VERIFIED` 后使用。优先 resume 当前 AGY conversation；如果 conversation 已不可用，则新开 conversation，但 Source of Truth 必须来自最终 repository state。

```text
Closeout Contract

Source of Truth
- final verified diff
- final code/schema/config/tests
- Codex Completeness evidence
- Codex Independent Verification results

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
- 如果 Closeout 暴露真实代码缺陷，停止知识修补，退回 Codex 的 Review / Completeness / Verification。
- AGY `result.status=SUCCESS` 不等于 Closeout PASS；Codex 仍需重新检查 Git 和 stale references。
