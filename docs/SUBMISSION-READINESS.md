# Submission readiness

## Demonstrable now

- Repeated seeded original failure and unchanged candidate test in separate snapshots.
- Exact test identities, input hashes, patch and per-attempt logs.
- Known invalid-evidence challenge: 15 rejections and one valid acceptance.
- Historical Petclinic investigation, with scope and exclusions in its existing reports.

Start with [verification and limits](VERIFICATION-20260926.md). Use [submission statements](submission-statements.md), [video script](demo-video-script.md) and [slides outline](slides-outline.md).

## Team actions still required

- Record a real Bob IDE task invoking the runner and interpreting its report; capture every participant's relevant task-consumption summary in bob_sessions.
- Confirm attribution against actual task records. Codex contributed verifier, experiment and documentation work; do not attribute all implementation to Bob.
- Record and inspect the narrated video and slide presentation. The stored event guide calls for a maximum three-minute MP4 with at least 90 seconds of working-solution footage; recheck current form requirements before submission.
- Confirm public repository contents, licensing, participant screenshots, application-link requirements and final form fields.
- Review and merge the continuation changes through the team's normal process. No remote merge or submission has been performed.

## Claims to avoid

No measured productivity gain, no real-agent cheating rate, no general security guarantee, and no claim that the replay authored its existing fix. A passing frozen test still depends on a correct requirement. Candidate verified does not mean approved or integrated.

## Live pilot and next experiment

The [six-task Codex pilot](LIVE-CODEX-COMPARISON-20260926.md) is complete. Both conditions produced correct tested repairs and appropriate control behavior. Vesper detected no extra error and falsely blocked one correct control because it added passing tests. That caused one completed feedback response; another attempt hit a usage limit. The gate bug was fixed and tested after the trial, without replacing the original result. Do not claim an accuracy or productivity advantage from this result.

The experimental supplied-snapshot adapter is limited to these declared tasks. Next, use independently prepared, representative tasks and a blinded reviewer where practical. Measure additional detection, false blocking and human checking effort; retain negative results. The existing full product does not yet offer a general arbitrary-repository verification interface.
