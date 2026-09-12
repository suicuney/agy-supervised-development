# Frozen Test Plan, Results, and Completion

Formal testing begins only after Astra records `CODE_REVIEW_PASS` for the current **deliverable digest**.

## Canonical data

Runtime truth is JSON, not Markdown:

- `schemas/test-plan.schema.json` + `templates/test-plan.json` — frozen Astra Test Plan.
- `schemas/test-results.schema.json` + `templates/test-results.json` — AGY execution attempts.
- `scripts/validate-run-state.sh` — cross-document/phase/completion validator.

`templates/test-plan.md` is a human-facing guide only. Do not manually maintain a second factual plan.

Plan digest is SHA-256 of canonical JSON (`sort_keys`, compact separators, ASCII escaping). AGY may execute a frozen plan but may not change its content/digest, remove required checks, lower thresholds, or redefine applicability.

## Test Plan

The plan binds `task_id`, Contract id/revision, plan id/revision and `reviewed_deliverable_digest`. Each check has a unique id, type (`command` or `observation`), cwd, `required`, frozen applicability, evidence types and `max_attempts`.

Command checks freeze an argv array, acceptable exit codes and timeout. Observation checks freeze explicit steps and require an evidence reference. Free-form `expected` text may explain intent but never substitutes for machine-readable exit-code/metric rules.

Applicability is either:

```json
{"mode":"always"}
```

or a frozen objective equality:

```json
{"mode":"fact_eq","fact":"browser_available","value":true}
```

A conditional result must carry matching applicability evidence. Unknown applicability is BLOCKED. Execution failure cannot be relabeled N/A. A required check whose condition is true cannot be waived.

Metrics use only `eq`, `ge`, or `le`, a source check, measured-value field, threshold, optional unit, and required flag. No `eval`, scripts, or arbitrary expressions are accepted.

A legitimate no-command task uses `checks: []` only with frozen `no_checks_acceptance` pointing to hashed acceptance evidence. Empty-array truthiness can never complete a task by itself.

## Evidence attempts

Every attempt is independent and records check id, attempt id/number, timestamps, actual argv or observation completion, cwd, exit/observation result, `measured_values`, evidence paths + hashes, reason, and deliverable digest before/after.

Evidence files must exist under Run State `evidence_root` and match their recorded SHA-256. Different attempts cannot merge logs or metrics. Attempts for a check are contiguous from 1, bounded by frozen `max_attempts`, and the latest attempt is authoritative; old success cannot hide a later failure.

This detects record inconsistency and accidental/stale evidence. It is not cryptographic proof against a malicious worker with the same filesystem permissions.

## Deliverable versus evidence output

The deliverable digest includes tracked/untracked task content such as production code, test source, assertions, fixtures, goldens/snapshots, configuration, lockfiles and generated source. Changing any of these invalidates prior code review and formal test evidence.

Logs/reports/cache may avoid digest churn only when written to the predeclared Git-private/out-of-worktree `evidence_root`. Do not use broad ignore rules to hide source changes.

Ignored files are outside the default snapshot. If a required check depends on one, list it in Test Plan `input_paths` and include it explicitly when capturing the snapshot. Unsupported submodules or unsafe inputs fail closed rather than silently disappearing from evidence.

## AGY formal testing

AGY executes only the frozen checks through Herdr. Environment/auth/dependency failures remain `BLOCKED`. Retry/flaky behavior is bounded by `max_attempts`; keep every attempt and never retry indefinitely to obtain green.

If testing exposes a code defect, first persist the failure, confirm the current writer stops, then run:

```text
validate-run-state invalidate ...
```

This marks review and plan STALE and enters `TEST_REWORK`. AGY may then perform a complete bounded repair within the Contract and stop. The repaired deliverable returns to Astra code review; a new/fresh plan is required before formal testing resumes.

By default a changed deliverable reruns all applicable required formal checks. This version does not implement dependency-based evidence reuse.

## Entering TEST

The host must call:

```bash
scripts/validate-run-state.sh transition \
  --run-state "$state" --contract "$contract" --test-plan "$plan" \
  --to TEST --expected-state-version "$version"
```

The command re-snapshots the repository and rejects stale Contract/review/plan digest, `SEND_UNKNOWN`, active/unknown writer state, missing plan inputs, and illegal transitions.

## Completion

The host must call the deterministic command, not infer success from AGY prose:

```bash
scripts/validate-run-state.sh complete \
  --run-state "$state" --contract "$contract" \
  --test-plan "$plan" --results "$results" \
  --expected-state-version "$version"
```

It re-reads disk, re-snapshots the current deliverable, validates all JSON Schemas, Contract/review/plan identities, plan digest, complete check enumeration, attempt sequence, actual argv/exit codes or observation evidence, evidence hashes, applicability, metrics, open findings, dispatch/writer state, and before/after/current deliverable digests. Only a successful decision atomically writes `phase=COMPLETE`.

Astra does not perform a second test-review pass. The deterministic validator is the completion gate.
