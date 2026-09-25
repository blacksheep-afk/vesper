# Vesper project instructions

The project is Vesper (formerly ProofLoop). Read README.md and docs/requirements.md first; consult docs/system-design.md for detail.

Build one complete sequential workflow before expanding. Target Java/Maven; use a small Python standard-library runner where practical. Do not introduce a server, database, external model API or parallel agents for the initial milestone.

Separate AI proposals from observed execution evidence. Never fabricate test results, timing, Bobcoin consumption, screenshots or human approvals. A passing test means not reproduced, not a proven false positive. Compile/setup failures are not evidence of an application bug. A failing test needs a valid, requirement-linked expected result.

Freeze an accepted reproducer during repair. Check that the targeted test actually ran and that full regression results are fresh, nonempty and not skipped. Keep candidate changes separate from accepted source; show the exact diff before human approval and integration. Never discard user changes.

Work only with synthetic or properly licensed demo data. Clearly disclose sample/seeded defects. Record actual task-summary screenshots under bob_sessions; never synthesize them.

Implement in small milestones. Report what was verified and what remains unverified. Do not publish, submit the hackathon form, or merge remotely without user instruction.
