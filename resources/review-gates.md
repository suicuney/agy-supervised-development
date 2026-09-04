# Three-Axis Review Gates — AGY Supervised Development

Codex owns independent review after AGY implementation. Review is split into three axes and is never averaged into a score.

## Axis A — Spec Fidelity

Question: **Did we build the right thing?**

Check:

```text
Acceptance coverage
missing / partial behavior
wrong semantics
scope creep
unauthorized product or architecture decisions
verification seam fidelity
```

Findings use `S*` IDs.

## Axis B — Engineering Quality

Question: **Was it built well?**

Check the relevant subset:

```text
architecture / module responsibility
contract and data consistency
correctness / edge cases
error handling / observability
security / side effects
backward compatibility
code smells / speculative generality
test quality / implementation coupling
```

Do not spend LLM review effort duplicating deterministic formatter, linter, compiler, or typechecker findings when those tools can prove the issue directly.

Findings use `Q*` IDs.

## Axis C — Completeness

Question: **What did we forget?**

Perform Missing Diff Review from changed behavior outward:

```text
changed behavior
→ callers / consumers
→ types / validation / serialization
→ schema / migration / existing data
→ sibling flows / jobs
→ error / retry / fallback
→ cache / derived state
→ old / orphaned path
→ tests
→ knowledge impact
```

Classify relevant remainder as:

```text
fixed-in-run
not-applicable
out-of-scope-different-ticket
blocked-decision-needed
```

Findings use `C*` IDs.

## Finding Severity and Convergence

After the three axes have independent verdicts, classify findings:

```text
BLOCKING
NON_BLOCKING
BACKLOG
```

- `BLOCKING` — prevents frozen contract, safe delivery, required propagation, verification, or closeout from passing.
- `NON_BLOCKING` — real in-scope improvement that does not invalidate the current contract; fix when cheap, otherwise record it.
- `BACKLOG` — different ticket, speculative hardening, or optional polish; do not keep the current loop open unless scope expands.

Codex may record `NO_BLOCKING_FINDINGS` only when no unresolved blocking finding remains. It is a convergence signal only:

```text
NO_BLOCKING_FINDINGS != REVIEW PASS by itself
NO_BLOCKING_FINDINGS != CODE_VERIFIED
NO_BLOCKING_FINDINGS != ACCEPTED
```

## Aggregate Verdict

```text
A PASS + B PASS + C PASS → REVIEW PASS
any REWORK               → REWORK_REQUIRED
any unresolved BLOCKED   → BLOCKED
```

No averaging and no majority vote.

## Rework Rule

Every actionable finding must contain:

```text
Finding ID
Axis / Source
Issue
Evidence
Expected
Required Change
Re-run
Scope Reminder
Forbidden Actions
```

After AGY rework, rerun the full Three-Axis Review. Fixing one axis can break another.

A normal soft limit is three complete `Review → Rework → Re-review` cycles. At that point reassess the Spec, slice, root cause, permissions, environment, or the Herdr-managed AGY session instead of looping mechanically.

## Cross-Cutting Rules

```text
Herdr done != REVIEW PASS
AGY SUCCESS != REVIEW PASS
REVIEW PASS != CODE_VERIFIED
CODE_VERIFIED != ACCEPTED
Repository state is authoritative evidence
One-way decisions still require explicit user authority
No push / merge / release / deploy / production mutation without authorization
```

Independent Verification remains a separate gate after Review PASS.
