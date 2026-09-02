# Review Convergence — v3.2

Three-Axis Review remains authoritative. This file adds a convergence classification so repeated review cycles do not turn optional polish into endless rework.

## Finding classes

### BLOCKING
A concrete S*/Q*/C*/V*/K* finding that prevents the current task from satisfying its frozen contract, safe engineering delivery, required propagation, verification, or closeout.

Examples: missing acceptance criterion, correctness/security defect, reachable caller left unmigrated, required verification failure, stale contract that makes current usage wrong.

### NON_BLOCKING
A real issue worth fixing when cheap and in-scope, but it does not invalidate the frozen task contract or required delivery proof.

Examples: small maintainability improvement with no correctness impact, clearer naming, low-risk local cleanup.

### BACKLOG
Useful future work that is a different ticket, speculative hardening, optional polish, or scope expansion.

## Convergence signal

After A/B/C verdicts are independently formed, Codex may emit:

```text
NO_BLOCKING_FINDINGS
```

only when there are no unresolved BLOCKING findings.

This signal means only that review has converged enough to proceed to the next required governance gate. It does **not** mean:

```text
APPROVED
CODE_VERIFIED
CLOSEOUT PASS
ACCEPTED
```

Independent Verification and Knowledge Closeout remain mandatory.

## Rework policy

- BLOCKING → must rework or become explicitly BLOCKED on a required decision.
- NON_BLOCKING → fix when low-cost and directly in scope; otherwise record without preventing convergence.
- BACKLOG → do not keep the current execution loop open unless the user explicitly expands scope.

Do not downgrade a requirement, security problem, data-loss risk, compatibility break, or verification failure merely to achieve convergence.
