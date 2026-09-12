# Frozen Test Plan — Human View

The canonical runtime plan is JSON validated by `schemas/test-plan.schema.json`; start from `templates/test-plan.json`. This Markdown is only a review/display view and must not become a second manually maintained source of truth.

Astra freezes after current `CODE_REVIEW_PASS`:

```text
task / contract revision
plan id / revision / canonical SHA-256
reviewed deliverable digest
checks:
  id / command-or-observation / cwd / required / applicability
  allowed exit codes or observation steps
  evidence types / timeout / max attempts
metrics:
  source check / measured field / eq|ge|le / threshold / unit
```

Rules:
- Include applicable project-required gates and map them back to Contract behavior/rules, not merely the implementation shape.
- `NOT_APPLICABLE` requires the frozen objective condition and evidence; unknown is BLOCKED.
- Natural-language `expected` explains intent but cannot mechanically pass a check by itself.
- AGY executes but cannot edit plan content/digest or thresholds.
- Any deliverable change makes review/plan/formal evidence stale and returns to Astra review.
