# Example: Bounded Rework and Escalation

Luna finds `F1`: the implementation satisfies the main behavior but misses a required consumer update implied by the repository rules.

Round 1 sends only `F1` evidence, required outcome and verification seam to the same Herdr-managed AGY worker. If the repository changes meaningfully toward resolving the finding, Luna re-verifies the affected surface.

If round 1 and round 2 both end with the same root defect and no substantive progress, Run State records the progress counters and Luna escalates:

```text
Contract: <id>@<revision>
Finding: F1
Attempts: round 1 + round 2
Evidence: <minimal decisive facts>
Decision needed: <contract/architecture/supervisor capability question>
```

Ordinary coding choices do not escalate. Authentication/dependency failure is `BLOCKED`, not a coding rework loop.

If a material Contract patch is required, only the architect/user increments the revision and records changed fields/reason. Evidence whose assumptions changed becomes stale before AGY continues.
