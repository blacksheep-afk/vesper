# Vesper MVP requirements

## User and outcome
A developer checks a selected Java module against a short requirements document and receives reproducible evidence and a proposed repair.

## Acceptance criteria
1. Record the selected source revision/snapshot, specification, scope and tool versions. Existing tests must pass before investigation; zero tests and skipped-only runs are blockers.
2. Present up to five expected behaviours linked to specification sections. The developer confirms their interpretation before a bug can be confirmed.
3. Record up to three distinct suspected bugs with location, requirement, input and expected outcome.
4. Distinguish reproduced, not reproduced, needs clarification, invalid test, environment error and flaky outcomes. A repeatable valid failure is required for reproduced.
5. Preserve the accepted test unchanged between original and candidate runs. Reject altered assertions, absent expected tests, stale results and skipped tests used to claim success.
6. A verified candidate must pass that test and the declared regression suite. Preserve command results, logs, test identities, hashes and timings.
7. Show the exact patch and evidence for a human decision. Candidate verification, approval and integration are separate states.
8. Generate a readable report with confirmed findings, unresolved attempts, proposed fixes and measured duration. Never promise complete correctness or zero false positives.

## First build boundary
Start with the runnable demo and baseline check. Then build one complete bug cycle. The runner does not call a Bob API: Bob invokes local tools through its IDE workflow. Workspaces separate edits; they are not OS sandboxes.

## Demo
Use a small synthetic checkout/discount service with a standalone Maven test suite. Write its business specification before investigating behaviour. Label any intentionally seeded defect; do not invent organic findings. No app server or database.

## Out of scope
Multiple languages, automated PRs/merging, hosted arbitrary-repository execution, dashboard accounts, and parallel repair jobs.
