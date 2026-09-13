---
name: agy-supervised-development
description: Astra defines/reviews, AGY implements/tests through Herdr, and a local gate checks completion consistency.
version: 4.1.0-alpha.3
---

# AGY Supervised Development

Read `../../SKILL.md`; it is the canonical active workflow.

```text
Astra Contract → AGY implement → Astra code review → Astra frozen command plan → AGY test → completion gate
```

Keep the Contract compact, preserve user changes, use Herdr for every AGY run, and return to Astra review whenever the deliverable changes after review PASS.
