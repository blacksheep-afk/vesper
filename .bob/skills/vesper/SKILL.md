---
name: vesper
description: Run a sequential Java checkout review, reproduction and candidate-verification workflow with actual evidence and a human patch decision.
---

# Vesper workflow

Read AGENTS.md, docs/requirements.md and docs/SPRINT-4.md. Use docs/system-design.md for the longer design; do not pretend deferred commands exist.

## Existing R3 demonstration — one starting request

1. Explain that this is a disclosed seeded bug replay using the already corrected Sprint 3 candidate, not an organic discovery. Read demo/requirements.md, Checkout.java and ReproducerR3Test.java. R3 expects 900 cents for a 1000-cent checkout with a 10% discount on the expiry date. If the developer disputes that expectation, resolve it before running a confirmation workflow.
2. Check Python, Java and Maven. If local tools exist, dot-source scripts/use-local-tools.ps1. Run `python -m vesper workflow --timeout 300` from the project root. Do not swap application files manually; the runner owns isolated snapshots.
3. Open the printed report.md and workflow.json. Inspect each attempt's result.json and execution.log. The runner establishes a passing baseline, repeats the original targeted failure, runs the unchanged candidate reproducer and verifies the complete baseline test set. A nonzero command exit is not success: explain the recorded blocker and stop the verification claim.
4. Present the requirement, exact failing input and expected/observed output, both original attempts, candidate result, regression scope, duration and exact diff. Link to the actual report and logs. Explain any unsuccessful or unresolved attempts. No tests executed means no application evidence.
5. The candidate is verified separately from human approval. Ask for a patch decision only if integration is actually requested and not already authorized. Never record approval on the developer's behalf. This demo command does not integrate changes; the accepted demo already contains the historical Sprint 3 fix.
6. Remind the developer to capture this actual Bob task's consumption summary in bob_sessions. Do not invent screenshots, task usage or measured productivity improvements.

## Gate challenge and final demonstration

Read docs/VERIFICATION-20260926.md for the current evidence and docs/SUBMISSION-READINESS.md
for remaining work. Run `python -m experiments.gate_challenge` to exercise 16
deliberate synthetic conditions against the actual gate. This command does not
run Java or an AI agent. Its exit 0 means the expected accept/reject decisions
were observed, not that every fixture is a verified patch. Show one rejected
changed-assertion case alongside the actual Maven replay. Never describe the
fixture counts as an agent error rate. Attribute this repair's engineering and
execution to Codex; a new Bob session must have its own real task summary.

## New investigations

The implemented workflow is specific to the supplied R3 demo. Do not claim it accepts arbitrary findings or generates repairs. For a new requirement, confirm its interpretation, establish a passing baseline, review bounded scope, and prepare a valid reproducer in a separate workspace. A passing test is not reproduced, and setup errors are not bugs. Preserve unsuccessful attempts. Freeze an accepted test during repair, keep the candidate separate, verify actual test identities and fresh regression evidence, and show the exact diff before human-approved integration. Implement further runner support only when requested.


## Interactive workspace

For the supported local demo, read docs/WORKSPACE.md. Launch `python -m vesper workspace` from a Java/Maven-ready terminal. The browser starts actual R3 verification after the developer confirms its expected result. React presents observed progress, logs and evidence; it does not invoke Bob or generate a repair. Keep the optional human decision separate from verification and never enter one on the developer's behalf. Preserve the real Bob session summary for the launch and interpretation task.
