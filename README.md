# Vesper

**Vesper doesn't ask developers to trust AI. It makes AI back its claims with evidence.**

A developer workflow built around IBM Bob IDE that connects code review, bug reproduction, repair and testing. Previously named ProofLoop.

## Project overview

Developers spend time investigating AI review findings before they know whether the reported bugs are real. A suggested fix creates another question: does it solve the problem without breaking existing behaviour?

Vesper connects each confirmed finding to a requirement, a reproducible failing test and the results after a proposed fix. The developer reviews the evidence and decides whether to accept the change.

The project aims to:

- reduce manual investigation of unsupported findings;
- connect review, debugging and testing in one workflow;
- show actual test results alongside proposed fixes;
- measure investigation time and verified outcomes;
- keep the developer in control of accepting changes.

Our business value is less investigation and rework. We will measure this with a comparable manual task; no productivity improvement has been measured yet.

## Use-case scenario

Suppose a developer wants to check a checkout service against its discount rules:

1. Open the project in Bob and provide its requirements document.
2. Confirm that expired discount codes should be rejected.
3. Ask Vesper to review the relevant module.
4. Bob identifies a suspected problem and writes a test for an expired code.
5. A valid test fails on the original code, reproducing the requirement violation.
6. Bob prepares a fix, then runs the unchanged test and the existing test suite.
7. The developer reviews the patch and evidence before accepting it.

This is an illustrative journey, not a claim that the prototype has already found this bug.

## Core features

These are planned MVP capabilities.

| Stage | Feature | Result |
| --- | --- | --- |
| Read | Understand the requirements and selected code | Expected behaviours for the developer to confirm |
| Review | Identify requirement-linked suspects | A small list of possible bugs |
| Reproduce | Write and run a valid test | Reproduced, not reproduced or unresolved finding |
| Fix | Prepare a candidate patch | A change for review |
| Verify | Run the unchanged reproducer and existing tests | Recorded test and regression results |
| Review evidence | Show the requirement, results and diff | A human decision about the patch |
| Report | Summarize the investigation | Findings, fixes, unresolved work and elapsed time |

## Finding structure

Each finding will contain a small, readable evidence record. The following is an example of the intended report content, not a fixed API contract or a real result.

| Field | Example | Purpose |
| --- | --- | --- |
| Finding | Expired discount accepted | Names the suspected problem |
| Requirement | Expired codes must be rejected | Explains the expected behaviour |
| Code location | Checkout discount validation | Identifies the reviewed code |
| Reproducer | Apply a code past its expiry | Shows how to trigger the behaviour |
| Original result | Test fails: code is accepted | Records the observed requirement violation |
| Candidate result | Same test passes | Shows the effect of the proposed change |
| Regression result | Existing suite passes | Records checks for other breakages |
| Human decision | Pending review | Separates testing from acceptance |

A test failure alone is not enough: the expectation must be valid and the failure must come from the alleged application bug. Compilation and environment failures are recorded separately.

## Current project status

- [x] Select the Vesper name and product direction
- [x] Create the project folder and initial documentation
- [x] Prepare a Bob workflow skill and first build task
- [x] Confirm hackathon registration
- [x] Install Bob IDE and sign in, as confirmed by the developer
- [x] Verify the local Java, Maven and Python toolchain
- [x] Build the standalone demo and establish passing baseline tests
- [x] Reproduce one requirement-linked bug
- [x] Prepare and verify a candidate fix
- [x] Connect the stages with a sequential runner and Bob instructions (live Bob walkthrough pending)
- [x] Generate a report from actual results
- [ ] Measure impact and prepare submission assets

Sprints 1–3 provide the baseline runner, disclosed R3 reproducer and integrated correction. Sprint 4 adds an isolated sequential replay and generated Markdown evidence report. The full Java workflow has been executed successfully; see docs/SPRINT-4.md. A live Bob walkthrough and its actual task-summary screenshot remain pending.

## Task breakdown

### Sprint 1: Working foundation

- Check Java, Maven and Python availability.
- Create a small standalone Java checkout/discount demo.
- Write its requirements and existing tests.
- Add a minimal runner that records actual baseline results.
- Detect failed execution, missing reports, zero tests and skipped-only runs.

**Done when:** the demo and baseline checks run successfully in Bob without a database or app server.

### Sprint 2: Reproduce a bug

- Choose one requirement and confirm its meaning.
- Review the relevant code and record a suspect.
- Write a test that checks the expected behaviour.
- Confirm the failure is caused by the application behaviour.
- Repeat the reproduction and preserve the result.
- Clearly label any deliberately seeded demo defect.

**Done when:** a valid, repeatable test demonstrates one requirement violation on the original code.

### Sprint 3: Fix and verify

- Preserve the accepted reproducer unchanged.
- Prepare a candidate patch separately from the accepted source.
- Run the same reproducer against the candidate.
- Run the existing regression suite and retain actual results.
- Show the diff for developer review.

**Done when:** the unchanged reproducer and existing tests pass, and the developer can inspect the proposed change.

### Sprint 4: Connect the workflow and report

- Connect the stages through the reusable Vesper Bob instruction.
- Keep the workflow sequential and focused on one finding at a time.
- Generate a simple report from execution records.
- Include unsuccessful and unresolved investigations honestly.
- Walk through the entire journey from a single starting request.

**Done when:** a teammate can start Vesper in Bob and follow a complete requirement-to-tested-fix journey.

### Sprint 5: Demo and submission

- Rehearse the complete workflow.
- Measure time and outcomes against a comparable manual task.
- Collect real Bob task-summary screenshots.
- Record a narrated video of at most three minutes, including at least 90 seconds of the working solution.
- Prepare slides, a cover image, the public repository and both required statements.

**Done when:** the evidence and submission assets are ready before 27 September 2026 at 17:00 SAST.

## Technologies used

Planned implementation stack:

- IBM Bob IDE: requirement understanding, review, test generation and proposed fixes.
- Java and Maven: standalone demonstration project and test execution.
- JUnit: application tests.
- Python: small local runner for execution records and reporting.
- Markdown or HTML: readable evidence report.
- Git: source history and patch review.

No hosted backend, database or additional model API is required for the initial prototype.

## Project structure

Current files:

```text
vesper/
|-- .bob/skills/vesper/SKILL.md
|-- bob_sessions/README.md
|-- docs/
|   |-- FIRST-BOB-TASK.md
|   |-- event-requirements.md
|   |-- requirements.md
|   `-- system-design.md
|-- .gitignore
|-- AGENTS.md
`-- README.md
```

Planned additions during the sprints:

```text
demo/       Java project, business requirements and application tests
vesper/     Small Python runner and report generation
tests/      Checks for the runner's result classification
evidence/   Selected real test logs and demonstration reports
```

The longer system design describes possible engineering depth. The sprint scope in this document is the hackathon priority; elaborate state machines, hash-based approval tracking and automated integration are deferred.

## Requirements

Before running the implemented prototype, we expect to need:

- IBM Bob IDE signed into the hackathon-provisioned account;
- a compatible JDK, with Java 17 as the proposed demo target;
- Maven;
- Python 3;
- Git for source tracking.

Sprint 1 will confirm the supported versions and document the actual commands. Signing into Bob does not by itself confirm the selected hackathon account or available Bobcoins.

## Installation

The project is not packaged yet. To start development:

1. Open IBM Bob IDE.
2. Select **File > Open Folder**.
3. Open `C:\Users\LEARNER\Documents\mlab\Blacksheep\vesper`.
4. Ask Bob: **Read docs/FIRST-BOB-TASK.md and carry out the task described there.**
5. Review the reported prerequisite checks and build results.

Clone, dependency installation and application commands will be added once they exist and have been verified.

## Available scripts

From the project root, with Python 3 available:

```powershell
python -m unittest discover -s tests -v
python -m vesper baseline
python -m vesper workflow --timeout 300
python -m vesper report ".vesper/runs/<workflow-run-id>"
```

For this machine, first run `. ./scripts/use-local-tools.ps1` in PowerShell. The baseline requires Java and Maven on PATH. You can select Maven with `--maven C:/path/to/mvn.cmd`. Results and logs are saved to a unique folder under `.vesper/runs/`. The command exits with 0 only for a passing baseline; missing tools are recorded as environment errors. See `docs/SPRINT-1.md` for the verification status and this machine's Python command.

## Using Vesper

The intended starting request in Bob is:

> Run Vesper on the checkout module using its requirements document. Show me the expected behaviours to confirm, reproduce supported findings, and prepare tested fixes for my review.

Bob will read, review and propose code changes. The local runner will execute tests and record their results. The developer will clarify requirements and review proposed patches.

The supplied R3 demonstration now runs sequentially with `python -m vesper workflow`. It uses the existing seeded original and corrected candidate; it does not automatically discover bugs or generate fixes. See [Sprint 4](docs/SPRINT-4.md) for the exact Bob starting request and remaining live-session check.

## Testing the workflow

1. Run the existing suite and establish a passing, nonempty baseline.
2. Confirm the meaning of the selected requirement.
3. Run the reproducer on the original code and inspect the actual failure.
4. Repeat it to check that the failure is consistent.
5. Run the unchanged test after the proposed fix.
6. Run the full declared regression suite.
7. Check that the report matches the actual logs and that the expected tests ran.
8. Review the patch before accepting it.

Also check that setup failures, missing results, zero tests and skipped-only runs cannot be reported as successful verification. A passing reproducer means the suspicion was not reproduced; it does not establish that the code has no bug.

## Working as a team

- Use one shared project repository when it is created.
- Assign each sprint a clear owner and review its outcome together.
- Keep application fixtures synthetic and retain attribution for external code.
- Each teammate saves their own relevant Bob task-summary screenshots in `bob_sessions`.
- Demonstrate the complete journey before adding more bugs or parallel reviews.

## Important limitations

- The R3 replay runs locally end to end; general discovery/repair automation and live Bob acceptance remain unfinished.
- The MVP supports one local Java/Maven project and one finding at a time.
- Test evidence is not formal proof or a guarantee of complete correctness.
- Requirement interpretation and proposed patches still need human review.
- Workspaces separate changes but do not sandbox executable project code.
- Multi-language support, automated merging, hosted repository execution and elaborate workflow infrastructure are out of scope for the hackathon.
- No speedup, bug count or success rate should be claimed before it is measured.

## Author

Developed by the Black Sheep team for the IBM Bob 2.0 Hackathon.

## License

A project license has not yet been added. The event requires an original, MIT-compliant submission. Confirm the project license and any third-party notices before publication.
