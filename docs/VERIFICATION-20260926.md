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

## Offline report presentation follow-up

Added a static HTML renderer to the current project after commit `191fd98`, preserving the completed live-pilot results. Regenerated the saved R3 report from its existing JSON and snapshots; did not rerun Maven or change its recorded duration. The current Python suite passes **35 tests**, including five presentation checks for escaping, blocked states, synthetic disclosure, path containment and offline dependencies. An initial Windows read without explicit UTF-8 failed; the test now explicitly reads the report as UTF-8 and the complete rerun passed.

A fresh synthetic qualification at `.vesper/experiments/gate-20260926T163944Z-4516f018` returned 16/16 expected decisions, zero false acceptances, false rejections or crashes. These cases overlap the unit checks. Browser validation at 1440-pixel desktop and 390-pixel mobile widths confirmed patch switching, expandable fingerprints, visible scope explanation and no horizontal mobile overflow. See REPORT-DESIGN.md for scope. No remote CI result is claimed.


## Browser-operated local workspace

The user requested a real local verifier with an interactive product journey. Added a loopback-only Python service and React client. The existing R3 gate now emits actual stage-start/stage-finish callbacks; acceptance rules are unchanged. The workspace offers requirement confirmation, real execution, saved run history, Finding/Patch/Execution/Review tabs, and separate patch-bound human decisions. Arbitrary repositories, AI repair generation and automated integration remain unsupported.

All **44 Python checks passed** (35 existing plus nine workspace tests). The React production bundle built successfully with pinned dependencies; npm reported zero vulnerabilities at installation. Browser checks covered initial disabled run, requirement confirmation, starting a real run, actual log output, completed history, patch and review tabs, keyboard tab selection and a 390-pixel mobile layout with no horizontal document overflow. Approval was deliberately left pending. Review writes were tested only in disposable synthetic test fixtures.

Fresh browser-started run: `workflow-20260926-204208-104c2b5b`, duration **103.77 seconds**, outcome `verified_candidate`.

| Attempt | Tests | Failures | Errors | Skips | Seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 12 | 0 | 0 | 0 | 35.416 |
| Original | 1 | 1 | 0 | 0 | 18.166 |
| Original repeat | 1 | 1 | 0 | 0 | 14.207 |
| Candidate reproducer | 1 | 0 | 0 | 0 | 12.078 |
| Candidate regression | 12 | 0 | 0 | 0 | 11.234 |

Both original failures matched the expected R3 assertion. All five attempts recorded unchanged inputs. Accepted demo source stayed unchanged. No human decision file was created for this run and no integration occurred. This is another disclosed replay, not a new accuracy or productivity measurement.

[Preserved report and raw evidence](../evidence/workspace-20260926/workflow-20260926-204208-104c2b5b/report.html) are copied byte-for-byte from the local run except for omitted generated `target/` build directories. Existing historical evidence is retained. The GitHub workflow now includes frontend build consistency checks, but remote CI has not been run by this task.
