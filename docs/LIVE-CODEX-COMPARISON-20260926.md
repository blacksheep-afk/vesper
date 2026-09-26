# Live Codex versus Vesper pilot - 26 September 2026

## Result

The frozen live pilot showed no additional error detection from Vesper. All six first responses were correct under the independent checks and confirmed expectations. Codex alone completed two repairs and correctly left a sound implementation unchanged. Codex with the experimental gate completed two correct repairs and correctly requested clarification on an unspecified rule, but the gate falsely rejected that last response because it added passing tests. This pilot therefore exposed added friction from the gate, not an accuracy advantage.

| Task | Condition | Judged outcome | Agent seconds | Gate seconds | Completed feedback responses |
| --- | --- | --- | ---: | ---: | ---: |
| expiry_b | Codex alone | Correct repair | 206.7 | 0.0 | 0 |
| expiry_a | Codex + experimental Vesper gate | Correct repair | 206.2 | 66.6 | 0 |
| arithmetic_b | Codex alone | Correct repair | 198.7 | 0.0 | 0 |
| arithmetic_a | Codex + experimental Vesper gate | Correct repair | 194.9 | 66.5 | 0 |
| control_correct | Codex alone | Correctly left production unchanged | 365.4 | 0.0 | 0 |
| control_ambiguous | Codex + experimental Vesper gate | Correct clarification; falsely blocked by gate | 210.7 | 74.3 | 1 |

## What actually ran

Six tasks completed in fresh, sequential authenticated Codex CLI sessions using gpt-6-astra; the quota-interrupted task resumed its original session. The recorded reasoning field was unspecified; the same default configuration was retained. CLI 0.155.0-alpha.16.4, Java 17.0.12 and Maven 3.9.9. All sessions used workspace-write with automatic approval review and a shared, prewarmed workspace Maven cache.

The user confirmed expiry, rounding, overflow and control expectations before execution. Assignment was randomized within task families and frozen before model outcomes. The baseline received normal verification instructions and could add tests. The B condition received ordinary capabilities plus external gate feedback after first completion, with correction turns available on rejection.

The new experimental supplied-snapshot adapter reuses Vesper execution and classification. Before the live sessions it accepted four known correct repairs and two unchanged controls, rejected an unfixed candidate, and rejected a changed existing test. This qualification is separate from the live results and from the earlier 16-case synthetic challenge.

Both conditions were judged by a separate evaluator using trusted original build/tests and candidate production code. Held-out checks used BigInteger for 481 deterministic boundary/random combinations plus invalid-input checks. The evaluator detected all four original defects and accepted the correct controls and known correct repair before the pilot. Gate success alone did not determine scoring.

## Gate false rejection

The final control passed all nine tests and left production unchanged. Its gate used exact equality against the three baseline identities, even though the protocol explicitly allowed added tests. The repair path already allowed additions. The frozen control path rejected this correct candidate three times. One feedback response completed: Codex reran passing tests and correctly requested concrete failure evidence rather than changing valid code. A second feedback attempt was blocked by the account usage limit before a response. These interruptions and rechecks are retained; the frozen trial ended with the correct control still blocked.

## Post-study fix, separate from trial outcomes

After freezing and preserving the trial source and results, the control check was changed to require all original identities while allowing additional passing tests. A new regression test failed on the frozen implementation and passed after the fix; a companion test still blocks a missing required identity. The full Python suite passed 30 tests. A real Java rerun on the same unchanged control candidate then returned accepted_no_change. This repair does not erase the pilot false rejection or demonstrate incremental detection benefit. Old and fixed gate hashes are in post-study-fix.json; frozen-source retains the exact gate used in the trial.

## Observed self-correction

On the correct-code control, Codex alone identified an incorrect expectation in a test it had just authored: 199 minus floor(199 times 67 / 100) is 66. The arithmetic oracle and implementation agreed. It corrected its new assertion rather than altering correct production code. This was an intermediate testing mistake resolved before completion, not an incorrect final acceptance or evidence of cheating. A frozen accepted test still needs a correct requirement interpretation.

## Interpretation and limits

Agent seconds include model/tool work and environment troubleshooting until the final response; gate seconds are the added Vesper execution after that response. Common independent judging time and all qualification/setup work are excluded from those columns. These are not active developer minutes, and the arithmetic tasks and controls are not equivalent timing workloads. No productivity improvement can be inferred.

The tasks are small, seeded checkout examples. There were only two repairs and one control per condition. Correctness means the tested contract passed, not complete correctness. The coordinating agent prepared and adjudicated the tasks with user-confirmed expectations; there was no blinded human evaluator. Evaluator files were outside coding workspaces but readable on the host, so this was procedural separation rather than a hostile-agent security test.

Six initial CLI launches failed before model sessions because of incompatible flags. Later, an account usage limit interrupted the B expiry task after tests passed and blocked four tasks at startup. After the user requested continuation and usage became available, the same B session resumed; only the four zero-work sessions were restarted with their unchanged prompts. All attempts and original results are retained. Quota resumption is not counted as gate correction. Windows dependency-cache access errors and escalated reruns are retained.

No monetary cost or human active-time estimate is fabricated. Raw CLI usage counters are retained in archived results and session logs. Their resumed-session aggregation and missing interrupted-turn counters are not interpreted as billed totals or monetary costs. No remote push, merge or hackathon submission was performed.

## Evidence

- live-comparison-results.json: compact judged outcomes and timing.
- live-comparison-evidence.zip: frozen protocol, assignments, hashes, task inputs, first-completion snapshots, raw session events, Maven logs/XML, gate decisions, independent judgments and setup failures.
- Repository docs/LIVE-CODEX-COMPARISON-20260926.md and evidence/experiments/live-codex-pilot-20260926 retain the report and compact records.

Fresh noninteractive execution follows the installed CLI and [official Codex documentation](https://learn.chatgpt.com/docs/non-interactive-mode).
