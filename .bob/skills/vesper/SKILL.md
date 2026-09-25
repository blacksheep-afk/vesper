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

## New investigations

The implemented workflow is specific to the supplied R3 demo. Do not claim it accepts arbitrary findings or generates repairs. For a new requirement, confirm its interpretation, establish a passing baseline, review bounded scope, and prepare a valid reproducer in a separate workspace. A passing test is not reproduced, and setup errors are not bugs. Preserve unsuccessful attempts. Freeze an accepted test during repair, keep the candidate separate, verify actual test identities and fresh regression evidence, and show the exact diff before human-approved integration. Implement further runner support only when requested.
