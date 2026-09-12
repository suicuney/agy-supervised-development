# Example: Small Feature in 4.1

Astra freezes a compact Contract with observable behavior/scenario and, only if useful, a bounded diagnostic such as a targeted typecheck. The diagnostic is recorded with `formal_acceptance=false`.

AGY implements through Herdr and stops. Astra reviews the complete deliverable digest (including tests/config/generated artifacts required by repository rules) without executing tests. Findings return as bounded `IMPLEMENT_REWORK` until `CODE_REVIEW_PASS`.

Astra then writes canonical `test-plan.json`. Example command check freezes argv, cwd, applicability, accepted exit codes, timeout/max attempts and required metric threshold.

Before AGY tests, the host calls:

```bash
bash scripts/validate-run-state.sh transition --run-state "$state" --contract "$contract" --test-plan "$plan" --to TEST --expected-state-version "$version"
```

AGY executes the frozen plan through Herdr and stores each attempt separately under the approved evidence root. It cannot edit the plan or lower thresholds.

Final completion is only:

```bash
bash scripts/validate-run-state.sh complete --run-state "$state" --contract "$contract" --test-plan "$plan" --results "$results" --expected-state-version "$version"
```

If a deliverable file changes after review—including test assertions, fixture/golden, config or lockfile—the old review/plan/evidence is stale and cannot complete.
