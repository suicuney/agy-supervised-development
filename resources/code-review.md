# Astra Code Review

Astra reviews after AGY implementation/rework stops. This stage is intentionally **code/deliverable inspection only**: Astra does not execute tests, builds, linters, integration checks, browser checks or project quality gates here.

## Inputs

```text
Development Contract + revision
observable acceptance scenarios + counterexamples
applicable AGENTS.md / repository constraints
baseline snapshot reference
full task delta
current deliverable digest
AGY implementation report (index only)
open review findings
```

Review the actual task delta, not only AGY's summary. Include committed task changes after baseline, staged/unstaged changes, untracked contents, deletions/renames, binary/mode changes, test source/assertions/fixtures/goldens/config/lockfiles/generated source, and required callers/consumers/schema/docs. Separate task changes from baseline user changes.

## Review dimensions

Use one lightweight risk-driven review:

- Contract fidelity and observable scenarios/counterexamples.
- Correctness by inspection: control flow, state/error/lifecycle, concurrency/data/security where applicable.
- Project-rule compliance: architecture/API/schema/generated-client/config/documentation propagation.
- Completeness: implementation-required callers, consumers and generated artifacts are not mislabeled scope expansion.
- Maintainability proportional to risk; do not reject ordinary HOW merely because Astra would code differently.

## Outcomes

```text
CODE_REVIEW_PASS
CODE_REVIEW_REWORK
BLOCKED
```

A finding carries `finding_id`, Contract/rule, concrete code evidence, why it matters and required outcome. AGY performs bounded `IMPLEMENT_REWORK` and stops; Astra reviews the complete resulting deliverable again. Formal tests remain deferred except Contract-preauthorized diagnostics, whose result is never formal acceptance evidence.

If the same finding has two consecutive rounds without substantive progress, stop blind rework and classify the actual blocker/decision.

## Pass binding

Record a stable `review_id`, Contract revision, reviewed deliverable digest, delta reference and resolved findings. `CODE_REVIEW_PASS` is inspection evidence only.

**Any subsequent deliverable change**—including production code, test code/assertions, fixture/golden, configuration, lockfile or generated source—invalidates the pass. Predeclared evidence logs/reports stored outside the deliverable do not.
