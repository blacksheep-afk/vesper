# Sprint 4 — Connected workflow and evidence report

## Delivered

`python -m vesper workflow` runs the supplied checkout R3 demonstration sequentially:

1. Snapshot the current demo into baseline, original and candidate directories under a unique run folder. Accepted application files are never swapped or edited.
2. Run a clean, nonempty baseline on the corrected current demo and retain all executed test identities.
3. Restore the disclosed seeded source in the original snapshot only. Run the R3 reproducer twice. Require the exact expected assertion failure, test identity, and counts on both attempts.
4. Verify that the candidate differs only in Checkout.java; preserve tests, build configuration and requirements unchanged. Run the identical reproducer against the corrected candidate.
5. Run clean candidate regression and require the same full test set as the baseline, without duplicates, skips, failures or errors.
6. Generate `workflow.json` and `report.md`, including every attempted stage, duration, status, source hashes, exact diff and links to command logs and Surefire results.

The candidate is the existing Sprint 3 corrected source. This is a replay of the disclosed demonstration, not a new AI discovery or a newly generated repair. The extra reproducer overlaps an existing expiry-boundary test; the report counts one defect.

## Run from the Vesper project root

Use Python 3 and Java 17+ with Maven on PATH. If project-local tools are available:

```powershell
. ./scripts/use-local-tools.ps1
python -m unittest discover -s tests -v
python -m vesper workflow --timeout 300
```

The last command prints the report path and exits 0 only for a verified candidate. Exit 1 means the run was blocked or unverified; inspect the report and stage logs. `--project`, `--output`, `--maven` and `--timeout` are configurable. The default timeout is 120 seconds per Maven test invocation; initial dependency downloads may need 300 seconds.

To rebuild a report without running tests:

```powershell
python -m vesper report "evidence/sprint-4/<workflow-run-id>"
```

Baseline-only usage remains `python -m vesper baseline`. The full workflow adds clean builds, targeted identity checks, repeat reproduction, input hashes and per-command timeout/process cleanup; these additions do not change the older baseline-only command's limitations.

## Start in Bob

Paste this request with the Vesper folder open:

> Read .bob/skills/vesper/SKILL.md and docs/SPRINT-4.md. Run Vesper's disclosed R3 demonstration using the existing demo and local tools. Inspect the generated report and actual logs. Explain the requirement, original failure, unchanged test results, full regression, and exact candidate diff. Report unresolved attempts honestly and leave the patch decision to me. Remind me to capture this Bob session's real consumption-summary screenshot.

## Scope and acceptance

The workflow supports the supplied Maven demo's report-directory property and R3 reproducer only. Bob remains responsible for explaining requirements, reviewing code and proposing changes for new investigations. General proposal import, arbitrary repositories, automatic repair generation and approval/integration commands remain deferred.

Python tests use clearly labelled synthetic fixtures to check orchestration failure paths. They are not evidence of Java application behavior. Actual Maven runs must be evaluated separately. Passing tests do not prove complete correctness.

Each workflow report leaves human review pending and performs no integration. Historical Sprint 3 approval is not reused as approval of a new snapshot. No Bobcoin or productivity measurement is fabricated. A teammate's complete Bob walkthrough and real Bob task-summary screenshot still require a Bob session.

## Actual local verification — 25 September 2026

- Python runner checks: 20 passed (10 existing and 10 workflow checks).
- Full workflow: `workflow-20260925-225639-8ad672ce`, status `verified_candidate`.
- Baseline: 12 tests passed; original R3 reproducer failed as expected twice (900 expected, 1000 observed).
- Candidate reproducer: 1 passed; candidate regression: 12 passed, 0 failures/errors/skips, exact baseline identities preserved.
- Recorded workflow duration: 77.156 seconds; this is execution timing, not a productivity comparison.
- [Actual local report](../.vesper/runs/workflow-20260925-225639-8ad672ce/report.md) and adjacent raw evidence are ignored local run artifacts; regenerate them on another checkout.
- Java 17 and Maven 3.9.9 were provisioned under ignored `.tools` without global settings changes. Java source and tests in the accepted demo were unchanged.
- Bob walkthrough and real task-summary screenshot remain pending. Implementation and these checks were performed in Codex.

## Visible Sprint 4 evidence

The manually executed run is preserved in [evidence/sprint-4/workflow-20260925-231048-a534f44c/report.md](../evidence/sprint-4/workflow-20260925-231048-a534f44c/report.md). New workflow runs default to `evidence/sprint-4/`, a visible, Git-trackable folder. Original logs and metadata retain their original execution paths. Build outputs are excluded. This is manual test evidence, not a Bob AI consumption-summary screenshot.
