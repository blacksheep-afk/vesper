# Vesper submission statements

Drafts for team review. Confirm current form constraints before submission. Attribution must match retained session evidence.

## Problem and Solution Statement

Developers reviewing AI-proposed fixes need to know what was actually tested. A successful command alone can hide missing tests, skipped tests or a changed assertion. Vesper makes the evidence for a patch decision inspectable: the requirement, original failure, unchanged candidate test, regression scope and exact diff.

The prototype combines an IBM Bob IDE workflow skill with a local Python and Maven runner. For its disclosed checkout demonstration, the runner creates separate baseline, original and candidate snapshots. It requires the expected expiry-boundary failure twice, checks that the same test passes on the candidate, and verifies that the baseline test identities remain present in the regression run. Input hashes and fresh per-attempt reports help detect changed or missing evidence. Developer approval and source integration remain separate from verification.

The saved Java replay records 12 baseline passes, the expected original failure twice, a passing candidate reproducer and 12 regression passes. A synthetic challenge of 16 known cases accepts its valid control and rejects all 15 invalid cases. These are controlled development checks, not measurements of how frequently coding agents make mistakes. The demonstration uses a seeded defect and an existing corrected candidate; it does not claim a newly discovered bug or an automatically authored repair.

Vesper aims to reduce the effort of checking AI proposals. That benefit has not yet been measured against an ordinary agent workflow. A six-task seeded Codex pilot using an experimental supplied-snapshot gate produced correct repairs and appropriate control behavior in both conditions. The gate found no additional error and falsely blocked one correct control; that defect was fixed separately after the trial. This small pilot does not establish an accuracy or productivity advantage. Human judgment about the requirement remains essential.

## IBM Bob Usage Statement

IBM Bob IDE is the intended user-facing environment for Vesper's sequential investigation workflow. The repository provides a reusable Bob skill in .bob/skills/vesper/SKILL.md and operating rules in AGENTS.md. Bob can read the requirement, invoke the local runner, inspect saved reports and explain the patch and remaining uncertainty to the developer.

For the implemented R3 demonstration, Bob invokes python -m vesper workflow --timeout 300. The Python runner creates isolated copies and applies deterministic acceptance checks to Maven results. It records the repeated original failure, unchanged candidate reproducer, regression identities, logs, hashes and diff. Bob interprets those artifacts; the demo command itself does not discover a new bug or generate a new fix.

The project retains Bob session evidence in bob_sessions and describes historical investigation work in its sprint reports. The team must retain actual task-consumption summaries for all relevant participant sessions and confirm final attribution against those records. No new Bob session or Bobcoin usage was measured during this continuation.

Development also used Codex for verification repairs, synthetic challenge work and documentation. These contributions must not be described as entirely Bob-authored. The runner makes mechanical classification decisions, while requirement interpretation and the final patch decision require human judgment. The current implementation supports the supplied checkout replay; broader investigations require separately prepared evidence and further runner support.
