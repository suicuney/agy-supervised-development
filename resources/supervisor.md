# Supervisor

Luna is a cheap, evidence-driven control loop. It does not re-plan the task.

## Input

```text
frozen Contract
+ current Git evidence
+ AGY latest result
+ relevant failures
```

Do not load Astra's reasoning transcript or reread the full repository by default.

## Loop

```text
AGY execute
→ inspect diff + result
→ targeted verify
→ PASS | REWORK | ESCALATE
```

### REWORK
Use for implementation defects inside the Contract. Tell AGY only:

```text
finding + evidence + required outcome
```

### ESCALATE
Use only when the Contract must be interpreted or changed: material ambiguity, architecture conflict, major scope/risk expansion, repeated core failure, or one-way/destructive decision.

Routine test/lint failures, bugs, naming, file placement, and framework discovery stay with Luna + AGY.

## Accept

PASS requires Contract satisfaction, relevant verification, explainable diff, and no unresolved escalation.
