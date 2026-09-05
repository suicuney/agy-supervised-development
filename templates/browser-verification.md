# Browser Verification Contract

Use only when Browser Runtime Verification is applicable and enabled/auto-selected.

## Decision

```text
Applicability: YES / N/A
Provider: ego-browser / ego-lite (resources/ego-browser-runbook.md)
Mode: enabled / auto
Diagnosis: allowed / disallowed
Final Verification: required / optional
```

## Target

```text
URL / route:
Environment:
Browser/profile assumptions:
```

## Preconditions

- application/services required for the journey are running;
- required test data exists or can be created safely;
- authentication/session requirements are explicit;
- no unauthorized production mutation is required.

## Critical Journey

1. 
2. 
3. 

## Assertions

```text
observable UI behavior:
persisted state after reload when applicable:
console expectations:
network/API expectations:
performance expectation when applicable:
```

## Evidence

Record only evidence needed to support the verdict:

```text
interaction result
console findings
network findings
state/persistence evidence
performance evidence when required
screenshot when meaningful
```

Do not use a screenshot alone as proof of functional correctness.

## Verdict

```text
PASS
REWORK_REQUIRED → create V* finding
BLOCKED / TOOL_UNAVAILABLE
N/A
```

## Re-run

If verification fails, define the exact journey/tests that must be repeated after AGY rework.
