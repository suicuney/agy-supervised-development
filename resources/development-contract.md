# Development Contract

The Contract is Astra's compact statement of `WHAT / BOUNDARY / DONE`. Runtime truth is the JSON document validated by `schemas/development-contract.schema.json`.

Keep it small:

```json
{
  "contract_id": "task-x",
  "revision": 1,
  "goal": "desired outcome",
  "behavior": ["observable result"],
  "acceptance_scenarios": ["observable acceptance scenario"],
  "counterexamples": ["behavior that must not occur"],
  "constraints": [],
  "diagnostics": [],
  "done": ["final completion condition"],
  "escalate_if": []
}
```

AGY owns ordinary implementation HOW. Do not turn the Contract into a file/class/line plan.

Diagnostics are optional and bounded. A diagnostic entry identifies `kind`, `scope`, and always has `formal_acceptance=false`. Project rules such as required TDD remain binding; diagnostics do not replace the later formal Test Plan.

The runtime binds the Contract by id, revision, and canonical content digest. If the content changes, increment the revision and re-establish downstream review/plan/test evidence. Same revision with different Contract content is rejected.
