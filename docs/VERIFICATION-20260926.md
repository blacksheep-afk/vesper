# Verification continuation — 26 September 2026

Starting revision: master `1a6c304963453a86d48559a75d0fd6d7a070411d`.
The repaired snapshot runner and historical Java replay were already committed. The interrupted documentation finalization was not.

## Fresh checks on this machine

- Python standard-library suite: 28 tests passed.
- Current gate challenge: 16/16 conforming; valid control accepted, all 15 invalid cases rejected; zero crashes.
- Accepted demo hashes remained unchanged during the challenge.
- [Portable challenge record](../evidence/experiments/gate-repair-20260926/results.json) includes runner/harness hashes and individual outcomes.

The initial suite run using the system temporary directory failed one mutation-fixture check. Repeating with TEMP and TMP under the writable workspace passed all 28 checks. This environment-dependent first failure is retained here rather than silently omitted.

## Historical Java execution

[Saved Java report](../evidence/verification-20260926/workflow-20260926-141036-d39fa35f/report.md): 12 baseline passes; one expected R3 failure on each of two original attempts; one candidate reproducer pass; 12 regression passes, with no skips. The recorded workflow duration is 81.489 seconds.

These are saved results from the previous machine, not a new Maven run here. Java 17 is installed here, but Maven was not found on PATH. Do not present the historical duration as developer time saved.

## Limits

Synthetic fixtures replace process execution. Passing them demonstrates behavior on these known cases, not an agent mistake rate or protection against a hostile agent that can edit the verifier. The runner supports the supplied R3 replay and existing corrected candidate; it does not generate a new repair or accept arbitrary project pairs. The live Codex comparison has not run. Verification is separate from approval and integration.

## Subsequent live pilot

The [live comparison](LIVE-CODEX-COMPARISON-20260926.md) subsequently ran real Java/Maven checks on six new bounded tasks using an experimental supplied-snapshot gate. Both conditions handled their tasks correctly; no additional gate detection was observed, and the frozen gate falsely blocked one correct control. A post-study fix allows additional passing tests while preserving required baseline identities; all 30 Python checks and the real control rerun pass. This later execution supersedes the pending live-comparison status above. It does not turn the earlier saved R3 replay into a fresh rerun.
