# ego-browser / ego-lite Runbook

This runbook defines the active browser transport contract for Codex-supervised development.

```text
Codex = Supervisor / Plan Owner / Verifier
ego-browser / ego-lite = Sole Documented Browser Transport
ChatGPT Web = Sol High Plan Review Host
Local Web App / Testbed = Optional Browser Runtime Verification Seam
```

## Transport Precedence & Authority Boundary

1. **Transport Selection & Operation Authority**: This file (`resources/ego-browser-runbook.md`) authoritatively owns browser transport selection, task space lifecycle, tab routing, observation, and browser execution.
2. **Semantic Boundary**: The paired `sol-high-plan-review` skill supplies only review packet structure, verdict sentinels (`PASS`, `REVISE`, `USER_DECISION_REQUIRED`), and model truth expectations. It cannot override, substitute, or dictate browser transport.
3. **Sole Transport**: `ego-browser` / `ego-lite` is the sole documented browser transport for this plugin's Sol High review and optional browser runtime verification. Direct, unmanaged, or legacy browser transports are not supported.

## Execution Model

Codex runs browser operations using heredocs via the Bash tool:

```bash
ego-browser nodejs <<'EOF'
// Node.js script controlling ego-browser task space
const task = await useOrCreateTaskSpace('sol-high-plan-review')
cliLog('task space id: ' + task.id)
...
EOF
```

Do not write script files to disk. Output results to the terminal with `cliLog(...)`.

## 1. Isolated Task Space

Every browser workflow must run inside an isolated task space:

```js
const task = await useOrCreateTaskSpace('sol-high-plan-review')
cliLog('task space id: ' + task.id)
```

- Each task space is an isolated browsing context inheriting the user's existing login state.
- It does not disturb the user's normal browser tabs or windows.
- Capture `task.id` and reuse the numeric ID in subsequent heredoc rounds to prevent name collisions and maintain context continuity.
- Follow-up rounds for the same goal must resume the existing task space.

## 2. Tab Management

Always reuse or open the exact target tab and confirm active tab selection:

```js
await openOrReuseTab('https://chatgpt.com', { wait: true, timeout: 20 })
const tabs = await listTabs()
cliLog('open tabs: ' + tabs.length)
```

If navigating or switching tabs:
- Use `switchTab(targetId)` to ensure the target page is focused.
- Close scratch tabs when they accumulate via `closeTab(targetId)`; do not leave unnecessary tabs open.

## 3. Observation Before Consequential Actions

Before any consequential interaction (fill, click, submit, or state transition), capture fresh semantic structure:

```js
const snapshot = await snapshotText()
cliLog(snapshot)
```

- `snapshotText()` produces a full-page semantic tree with locators (`@N`, `loc=...`).
- Inspect the snapshot to verify page state, locate active input fields, and identify buttons.
- Never act blindly without inspecting the snapshot.

## 4. Pre-Send Verification & Three Pre-Send Failure States

Before submitting any review packet, verify visible model and reasoning depth:

```text
Model family = GPT-5.6 Sol
Reasoning     = High
```

Inspect page state for the three distinct pre-send failure states:

### State A: Login / Authentication Missing (`AUTH_REQUIRED`)
- **Symptom**: Login prompt, authentication wall, or logged-out landing page.
- **Handling**: Call `await handOffTaskSpace(task.id)`, notify the user to complete login in the opened ego-browser window, and wait. Do not attempt credential entry or password automation.

### State B: Control Conflict (`USER_CONTROLLING`)
- **Symptom**: Error indicating user is controlling the task space, or task space is inactive/unassigned.
- **Handling**: Hard stop. Do not retry or attempt automated takeover. The user has deliberately taken control. Ask the user for confirmation and wait. Only call `await takeOverTaskSpace(task.id)` after explicit user instruction to continue.

### State C: Model / Reasoning Mismatch (`MODEL_MISMATCH`)
- **Symptom**: Model selector does not show `GPT-5.6 Sol`, or reasoning level is not `High` (e.g., standard GPT-4o, mini, low/medium reasoning).
- **Handling**: Hard stop. Never silently substitute another model, tier, or reasoning setting. If the required model/reasoning cannot be selected, report the failure to the user.

## 5. Packet Fill & Single-Send Rule (Duplicate-Send Safety)

Fill the review packet and submit:

```js
await fillInput('@<input_ref>', reviewPacket)
await click('@<submit_ref>', { label: 'send plan review packet' })
```

### Duplicate-Send Safety
- Send **exactly once**.
- Track send state:
  ```text
  NOT_SENT → SENT
  NOT_SENT → UNKNOWN
  ```
- If network, timeout, or UI state around Send is ambiguous, mark state as `UNKNOWN`.
- **Never automatically resend from `UNKNOWN`**. Resending risks duplicate submission, corrupted conversation thread, or prompt flooding.
- To resolve `UNKNOWN`, inspect the same conversation using `await snapshotText()` to verify whether the packet was received or generation started.

## 6. Polling & Reading the Same Conversation

After sending, poll and read the assistant response in the **same** conversation tab:

```js
await wait(5)
const status = await snapshotText()
cliLog(status)
```

- Wait for generation to finish (check for completion indicators or disappearance of stop button).
- Read the response from the same conversation thread.
- Parse the verdict sentinel:
  - `PASS`: Plan approved, proceed to freeze.
  - `REVISE`: Revision required, apply Adopt/Reject/Modify and proceed to next round.
  - `USER_DECISION_REQUIRED`: Hard stop, requires user architectural/product decision.

## 7. Control Handoff & Takeover Rules

Only one side (agent or user) holds control of a task space at any time.

- **Handing Off**: When user action is required (login, captcha, or manual confirmation), call:
  ```js
  await handOffTaskSpace(task.id)
  ```
  Provide clear instructions on what the user needs to do in the browser.
- **Regaining Control**: Regain control **only** after explicit user confirmation (e.g. user says "continue" or confirms via prompt). Then in a new heredoc:
  ```js
  await takeOverTaskSpace(task.id)
  ```
  **Never** call `takeOverTaskSpace` autonomously without user confirmation.
- **Unexpected User Takeover**: If an operation fails because the user took control, do not fight for control. Yield immediately and ask the user how to proceed.

## 8. Dedicated Task Space Cleanup

When the entire browser interaction is finished:

```bash
ego-browser nodejs <<'EOF'
await completeTaskSpace(taskId, { keep: false })
EOF
```

- **Dedicated heredoc**: `completeTaskSpace` must run in its own dedicated final heredoc.
- **Prior confirmation**: Only run after a previous heredoc has proven that the review or verification task is completely finished.
- **Keep policy**: Default to `{ keep: false }` to close the task space cleanly. Use `{ keep: true }` only when the user explicitly requests to keep the live page open.

## 9. Browser Runtime Verification Seam

When optional browser runtime verification is enabled for web UI, frontend/backend integration, or browser state:

1. Create a dedicated task space: `const task = await useOrCreateTaskSpace('runtime-verification')`.
2. Open the test target: `await openOrReuseTab(targetUrl, { wait: true })`.
3. Observe semantic structure with `await snapshotText()`.
4. Perform critical journey interactions (`click`, `fillInput`, `typeText`).
5. Verify observable behavior, assertions, and console/network state (`drainEvents()`, `pageInfo()`).
6. Optionally capture visual evidence with `await captureScreenshot()` where meaningful.
7. Clean up the task space with `await completeTaskSpace(task.id, { keep: false })`.
