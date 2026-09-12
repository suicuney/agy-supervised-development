# Review and Verification

AGY performs self-review; Luna performs independent review and verification.

## Evidence Order

Prefer the cheapest decisive evidence first:

```text
Development Contract
→ git status / diff --stat / diff --check
→ changed diff
→ AGY completion report
→ targeted tests / runtime evidence
→ broader repository inspection only if needed
```

This is evidence-driven review, not a mandatory full-repository reread.

## Review Questions

1. Does the implementation satisfy every material `expected_behavior` and `definition_of_done` item?
2. Does the diff remain inside contract boundaries?
3. Are there unauthorized or unexplained changes?
4. Are important error paths or persistence / compatibility conditions covered when applicable?
5. Is AGY's self-review supported by repository evidence?

## Verification

Run the narrowest relevant verification seam first:

- original repro for bugs
- focused unit / integration tests
- lint / typecheck for changed code
- build when compilation or packaging is relevant
- browser/runtime verification only for affected runtime behavior

Broaden verification when risk or failures justify it. Do not run every available test merely because it exists.

## Outcomes

```text
PASS      → contract satisfied and evidence sufficient
REWORK    → bounded implementation defect; send finding to AGY
ESCALATE  → contract-level issue; follow escalation policy
BLOCKED   → required dependency/auth/environment unavailable
```

After rework, re-check the affected contract clause and any regression surface materially touched by the fix.

## Final Acceptance Evidence

A compact final report should include:

```text
contract status
changed behavior / key files
AGY self-review status
Luna review status
verification performed + result
rework count
escalations / contract patches, if any
final repository state
```
