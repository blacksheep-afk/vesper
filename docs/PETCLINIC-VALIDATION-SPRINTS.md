# Vesper: Second Validation Sprint Plan

## Project overview

Use Spring Petclinic to validate Vesper on an existing application, separately from the original checkout demo.

**Goal:** demonstrate the complete workflow on one feature and one supported bug: understand the requirement, investigate, reproduce, propose a repair, verify it and present the evidence for human review.

Target repository: https://github.com/spring-projects/spring-petclinic

Status: planned. Petclinic has not yet been downloaded, built or tested in this validation round. No bug has been identified.

## Working setup

- Use a separate Petclinic working folder so the team can continue developing Vesper independently.
- Record the exact source revision and preserve it before making changes.
- Begin with the default application configuration and inspect its actual tool requirements.
- Use synthetic data and preserve third-party attribution and license notices.
- Keep the original failing version and candidate fix separate.

## Sprint 1: Establish the baseline

- Obtain the project and record its exact revision.
- Read its setup instructions and verify the required tools.
- Run the existing tests using the default configuration where supported.
- Record the commands, tool versions, exit codes and test results.
- Identify any setup failures before beginning bug investigation.

**Done when:** the relevant existing tests pass, their scope is recorded and the results are saved. A failed or empty baseline is a blocker, not evidence of a newly discovered bug.

## Sprint 2: Define the investigation

- Start by assessing pet-record editing as the candidate feature.
- Read the relevant documentation, code and existing tests.
- Write a short checklist of expected behaviours with source references.
- Distinguish documented requirements from assumptions.
- Confirm the interpretation with the developer before classifying a defect.
- Select a different narrow feature if inspection shows pet editing is unsuitable.

**Done when:** the selected scope and expected behaviour are clear and supported by sources.

## Sprint 3: Investigate and reproduce

- Ask Bob to review the selected feature against the checklist.
- Investigate at most three suspected problems.
- Reuse an existing test when it already reproduces a suspect.
- Otherwise write a focused test for the expected behaviour.
- Distinguish application failures from invalid tests and environment errors.
- Save each attempt's command, exit code, logs and test reports separately.
- Repeat any valid reproduction twice and report the observed consistency without claiming that flakiness is impossible.

**Done when:** one valid requirement-linked failure is reproduced twice, or the investigation ends with an honest no-finding result.

**Time limit:** spend at most 45 minutes on open-ended discovery. If no supported bug emerges, consider a documented historical defect on a known affected revision. Establish that revision's baseline separately and label the exercise historical reproduction. Do not present a known issue as a new discovery.

## Sprint 4: Repair and verify

- Preserve the failing source version and its reproduction evidence.
- Prepare a separate candidate containing the smallest justified fix.
- Keep the accepted reproducer and existing tests unchanged.
- Run the reproducer against the candidate.
- Run the declared regression suite and record exactly what it covers.
- Verify that expected tests actually executed and results are fresh.
- Show the exact diff and evidence to the developer.
- Keep approval distinct from a passing test result; do not integrate without the developer's decision.

**Done when:** the unchanged reproducer and declared regression suite pass, with the patch ready for human review. Any excluded checks or remaining failures must be visible.

## Sprint 5: Report and demonstrate

- Generate a readable Vesper report from actual results.
- Include the requirement, suspected problem, reproducer, original failure, proposed fix and candidate results.
- Identify the source revision and link to raw evidence.
- Capture real Bob task-summary screenshots from each participant involved.
- Prepare a short walkthrough another teammate can follow.
- Report measured time, including retries, and avoid unsupported productivity claims.

**Done when:** a teammate can repeat the investigation and understand the evidence and its limitations.

## Time budget

Aim for roughly three hours overall. This is a planning target, not a measured completion time. Keep open-ended discovery to 45 minutes and reduce scope if setup consumes the available time.

## Evidence rules

- Preserve the starting source revision before edits.
- Count distinct bugs, not failing test cases.
- Save raw logs and test reports for every attempt.
- A passing test means the suspicion was not reproduced; it does not prove the absence of a bug.
- A failing test requires a valid expected result before it supports a bug claim.
- Do not fabricate results, approvals, timings or Bob screenshots.
- Record whether the outcome is a new finding, a historical reproduction or no bug reproduced.
- Keep third-party source and attribution separate from Vesper's original code.

## Current checklist

- [x] Select Spring Petclinic as the proposed second validation target
- [x] Prepare the sprint plan
- [x] Obtain and pin a source revision — `818c4136ea971c21674525f9053de0d9c7ad8cfe` (commit `67a5e86`)
- [x] Pass the baseline tests — 72/74 passed, 2 skipped (Docker), exit 0 (commit `67a5e86`)
- [x] Confirm the investigation scope and expected behaviour — pet editing, type-required check; interpretation recorded; **explicit developer sign-off not separately documented**
- [x] Reproduce a supported defect — `VesperPetTypeReproductionTests` failed twice on original (commit `7aa3a03`)
- [x] Verify a candidate repair — reproducer 2/2 pass, regression 76/0/0/2 pass (commit `7aa3a03`)
- [x] Complete human review — approved 2026-09-26T02:26:32 UTC (`approval.json`, commit `7aa3a03`)
- [x] Save the report and Bob session evidence — report and walkthrough created (Sprint 5); screenshots confirmed for all three participants (Neelo Nkhuna, Sam, Nyakalo Kgwale)

## First milestone

Petclinic builds and its baseline tests pass. Choose the exact investigation after inspecting the version that runs successfully.
