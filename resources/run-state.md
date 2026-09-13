# Run State and Recovery

Run State lives in Git-private storage and is schema v3. It separately binds Contract digest, snapshot policy/digest, baseline manifest, Herdr identity, writer/dispatch state, code review, frozen plan, results index, findings and BLOCKED recovery metadata.

Normal phases:

```text
CONTRACT → IMPLEMENT → CODE_REVIEW → TEST_PLAN → TEST → COMPLETE
                       ↘ IMPLEMENT_REWORK ↗
TEST --invalidate--> TEST_REWORK → CODE_REVIEW
any nonterminal phase → BLOCKED --resume--> original phase only
```

`COMPLETE` is terminal. Reopening requires a new run. Mutation commands use `state_version`, one cooperative lock, atomic replace and parent-directory fsync. `writer=UNKNOWN`, `dispatch=SENT` or `SEND_UNKNOWN` prevents unsafe new execution.

Baseline snapshots are immutable directories. Snapshot verification checks manifest identity and archived untracked blobs. Snapshot-policy changes require re-evaluation; policy expansion is never silently authorized. Old states missing new digest/receipt bindings are `MIGRATION_REQUIRED` and must rebuild current review/plan evidence.

The workflow lock coordinates cooperating workflow CLIs only; it is not OS-level filesystem isolation and does not prove arbitrary writers cannot modify the repository.
