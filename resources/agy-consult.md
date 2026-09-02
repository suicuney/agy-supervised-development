# AGY Consult — v3.2 Optional Read-only Sidecar

AGY Consult is an optional second-opinion path. It is not part of the default writer/reviewer authority chain.

## Good uses

- challenge an implementation plan;
- investigate a difficult code path;
- request blast-radius ideas before Codex verifies them locally;
- compare plausible root-cause hypotheses;
- ask for a second engineering opinion.

## Invocation

Prefer the thin adapter:

```bash
scripts/agy-run.sh --repo "$repo_root" --mode consult "<bounded question>"
```

The adapter prepends a read-only instruction and keeps official AGY CLI as the runtime boundary.

## Contract

Consult prompts should identify the repository slice, current goal, exact question, and requested output. Do not pass secrets, credentials, private keys, tokens, or unrelated private data.

AGY Consult must not be treated as an independent reviewer authority. Its result is advisory evidence only:

```text
AGY Consult finding
→ Codex checks repository/local facts
→ Codex decides whether it matters
```

It cannot produce Three-Axis PASS, Verification PASS, Closeout PASS, or ACCEPTED.

If AGY changes files during a consult despite the read-only contract, stop using the run as clean consultation evidence and inspect the repository diff before any further action. Do not revert unrelated pre-existing user changes.
