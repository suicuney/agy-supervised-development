# Development Contract

Astra freezes compact `WHAT / BOUNDARY / DONE`, plus stable acceptance-scenario/counterexample IDs and optional diagnostic permissions. AGY owns ordinary HOW.

The authoritative Contract is JSON validated by `schemas/development-contract.schema.json`. Its canonical SHA-256 digest is computed from sorted-key compact JSON. Field order does not change the digest; any content change does. A content change must increment `revision`; same revision + new digest is rejected and downstream review/plan/results are stale.

Diagnostics are optional and always `formal_acceptance=false`. They may include minimal reproduction, targeted tests, typecheck or compile feedback when preauthorized. They never satisfy final frozen checks.

Only architect/user may materially patch the Contract. Old alpha.2 states that lack `contract_digest` require migration/re-review, never silent backfill to PASS.
