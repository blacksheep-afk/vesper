# Experiment 1: Merged runner gate challenge

Date: 26 September 2026. Tested merged main: `0b882ce815bced03a5dd4a5bac70715c79d3140f`.

**Outcome: the current gate does not qualify for the live Codex comparison.**

The merges include the Petclinic baseline, repair evidence and Sprint 5 report.
All remaining remote branch tips were ancestors of main at inspection. The
workflow implementation and existing tests were unchanged by those merges.

## Observed results

This was synthetic fault injection into the actual workflow, not an agent trial
or a Maven rerun. Only the Maven execution helper was replaced. Tests used
disposable copies, and the accepted demo's file hashes remained unchanged.

| Measure | Observed |
| --- | --- |
| Cases | 16: one valid control and 15 invalid evidence conditions |
| Valid control | Accepted |
| Invalid conditions incorrectly accepted | 12 |
| Invalid conditions correctly rejected | 2 |
| Invalid condition causing an unhandled crash | 1 |

Incorrectly accepted: missing reports, zero tests, skipped reproducer, wrong
reproducer, changed assertion, omitted regression identity, duplicate identities,
original not reproduced, unrelated assertion failure, original setup failure,
unverified repeatability, and inconsistent XML counters.

Correctly rejected: candidate assertion failure and regression failure.
Malformed XML produced an unhandled parse error. That blocks success but does
not produce the controlled, recorded rejection expected by the experiment.

The repeatability fixture fails on the first original attempt and would pass on
a second. The runner requested only one original targeted attempt, then accepted.
This shows lack of repeat verification; no real flaky Java execution is claimed.

## Meaning and limits

The current gate accepts multiple kinds of incomplete or inconsistent evidence.
It cannot presently substantiate a claim that it independently enforces a more
reliable acceptance standard than Codex alone.

This does **not** measure how frequently Codex produces these mistakes, prove
intentional cheating, or establish that Codex alone is sufficient. The cases
were deliberately selected from known failure paths, not sampled from real agent
work. Do not publish their counts as an agent failure rate.

## Validation and provenance

- New experiment bookkeeping checks: 5 passed.
- Existing baseline checks: 10 passed.
- Existing workflow test module: import error (`SOURCE` no longer exported).
  The complete repository suite is therefore still failing; this predates the experiment.
- Workflow file SHA-256: `70bce72debd5adeae25f32e47ef14a0f5218b193b456084da399fde6b175a696`.
- Full local run: `.vesper/experiments/gate-20260926T115732Z-778b6d48/`.
- Compact portable record: [results.json](../evidence/experiments/gate-qualification-20260926/results.json).
- [Executable challenge](../experiments/gate_challenge.py).

The raw local directory contains the exact harness hash, all fixture XML,
per-case source copies, console output and structured records. It is ignored by
Git; regenerate with `python -m experiments.gate_challenge`. Its nonzero exit
signals gate qualification failures, not an unsuccessful Java build.

## Next decision

Recover and test the stronger historical evidence safeguards, restore the existing
workflow test suite, and support separately supplied original/candidate workspaces
before launching live task comparisons. Freeze the resulting gate revision.

The [Codex comparison protocol](EXPERIMENT-1-VERIFICATION-GATE.md) is prepared.
Its primary question is additional detection or reduced human verification work,
not whether Vesper can replay a prewritten fix. No live Codex comparison has run.
