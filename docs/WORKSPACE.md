# Vesper local workspace

An interactive front end for the existing, bounded verifier. The offline report is now an export from a workflow the developer can operate.

## Run it

From the repository root, with Python 3.10+, Java 17+ and Maven available:

```text
python -m vesper workspace
```

Open `http://127.0.0.1:8765`. On the current Windows checkout, dot-source `scripts/use-local-tools.ps1` first to select the installed Java/Maven and existing dependency cache. Other machines can use their normal installations. `--port`, `--maven` and `--timeout` are optional launch settings. The timeout applies to each command, not the entire five-attempt run. Use the printed 127.0.0.1 URL; a different host name is intentionally rejected.

The built React bundle is checked in, so normal usage needs no npm install, Node server or external frontend requests. To edit the frontend, use Node 20+ and:

```text
cd web
npm ci
npm run build
```

Source: `web/src/main.jsx` and `web/src/workspace.css`. The build uses pinned React/ReactDOM and esbuild from `web/package-lock.json`; it outputs the browser assets under `vesper/assets/`. Retain the emitted third-party notices. This is client-side React, not Next.js or a hosted API.

## The supported journey

1. Choose Checkout / discount service. This version deliberately offers only its supported project, not a nonfunctional GitHub URL box.
2. Confirm R3: a 1,000-cent subtotal with a 10% discount on its expiry date must total 900 cents.
3. Run verification. The real Python runner creates separate snapshots and executes Maven. One run is active at a time.
4. Follow five attempts: baseline, original reproduction, original repeat, candidate reproducer, full regression. Logs and stage changes come from actual command execution. No timer advances a fabricated agent trace.
5. Inspect Finding, Patch, Execution and Review. The patch is the supplied existing fix; the workspace does not call a model or generate a new repair.
6. Optionally record a human decision after checking the evidence. Approval is available only for a verified candidate. A separate `review.json` binds the decision to the patch hash. It never edits source, merges, pushes or replaces `workflow.json`. A recorded decision cannot be overwritten; create a new run for a new decision.
7. Open the full offline report, JSON or Markdown. Keep the report with its sibling evidence files so raw links continue to work.

The sidebar includes recent completed local runs and the existing saved Java example. The example is labelled historical and cannot receive a new decision. Live runs are stored in `.vesper/workspace-runs/`, ignored by Git. Restarting the workspace reloads completed history. Browser refresh reconnects to the current in-memory run while the server remains running. Forced process termination does not resume an interrupted job; inspect retained files before rerunning.

## Scope and boundaries

The local service binds only to loopback, validates Host, rejects cross-site requests and requires a same-origin token for execution and review actions. Project/commands are fixed by the supported adapter; request bodies cannot select a path or shell command. Evidence routes resolve inside known run folders. These controls reduce accidental browser-triggered execution; they do not sandbox hostile code or authenticate multiple local OS users. Do not expose this prototype to a network or use it to execute arbitrary repositories.

Java dependencies may require network access on a cold Maven cache. The browser interface itself is local. Missing tools produce a visible setup state. Verification failures remain failures, and expected original assertion failures are distinguished from candidate success only after the recorded gate conclusion.

## Product reference and design

RepoRevive's [public app](https://reporevive-sable.vercel.app/) was inspected on 26 September 2026. It supplies a clear start action, staged activity and tabbed findings/changes. Its footer explicitly labels a canned dataset with no external calls. Its [public repository](https://github.com/icohangar-ops/reporevive) presented submission material and claimed architecture; this review did not establish live arbitrary-repository execution. Vesper borrows the clear interaction sequence, not its branding, scores, code or claims.

Vesper's mark is the four-star ladybug: requirement, reproduction, verification, human review. The warm-paper report identity now extends to the workspace. Counts and timestamps reflect saved results; there is no invented health score or claimed accuracy gain. React is an implementation choice for this stateful workspace, not an event requirement. IBM Bob remains the required hackathon technology and must be shown in a genuine team workflow/session record.

## Verification

The Python suite passes 44 checks, including nine workspace checks for scope validation, single-run concurrency, execution-error handling, path containment, loopback request controls and append-only patch-bound review decisions. Review writes in these tests use disposable synthetic fixtures; they are not human approval of a real patch. See the current verification record for the browser-driven Java run and any remaining limitations.
