# Astra Code Review

Astra reviews code after AGY implementation/rework stops. This stage is intentionally code-only: do not execute tests, builds, linters, integration checks, browser checks, or project quality gates here.

## Inputs

```text
Development Contract + revision
applicable AGENTS.md / repository constraints
baseline reference
full task delta
current code-state digest
AGY implementation report (index only)
open code-review findings
```

Review the actual task delta, not only AGY's summary. Include committed task changes after baseline, staged changes, unstaged changes, untracked file contents, deletions/renames, and relevant binary changes. Separate task changes from baseline user changes.

## Review dimensions

Use one lightweight review, not a multi-stage ceremony:

- **Contract fidelity** — code implements required behavior and stays inside boundaries.
- **Correctness by inspection** — control flow, state handling, error paths, concurrency/data consistency, lifecycle, security-sensitive logic where applicable.
- **Project-rule compliance** — architecture/API/schema/generated-client/config/documentation obligations that are apparent from code/rules.
- **Completeness** — required callers, consumers, schema/config/docs/generated artifacts are not missing merely because they were outside the initially edited file.
- **Maintainability proportional to risk** — obvious duplication, dead paths, unsafe shortcuts, or needless complexity that materially affect delivery.

Do not reject ordinary implementation choices merely because Astra would have implemented them differently.

## Outcomes

```text
CODE_REVIEW_PASS
CODE_REVIEW_REWORK
BLOCKED
```

A rework finding contains only:

```text
finding_id
contract_or_rule
code_evidence
why_it_matters
required_outcome
```

Send bounded findings to AGY. AGY fixes code only; formal tests are still deferred. After AGY stops writing, Astra reviews the full resulting code state again.

If the same finding has two consecutive rework rounds without substantive code progress, stop and classify the real reason: unresolved product/architecture decision, worker capability problem, or environment/tooling blocker. Do not loop forever.

## Pass evidence

Record:

```text
contract_revision
reviewed_code_state_digest
reviewed_delta_reference
findings_resolved
result = CODE_REVIEW_PASS
```

`CODE_REVIEW_PASS` proves only that Astra's code inspection passed. It is not test evidence and does not mean the task is complete.

Any subsequent production-code change invalidates this pass and requires a new Astra code review before final completion.
