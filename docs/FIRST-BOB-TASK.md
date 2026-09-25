# Current handoff

Sprint 1 code has now been created in Codex. Read `docs/SPRINT-1.md` first. Review the existing implementation instead of rebuilding it. Resolve the documented toolchain blocker, run the real demo tests and baseline checker, and report actual results. Save a real Bob task-summary screenshot after your review/run.

The original build brief below is retained as context, not a request to overwrite the implementation.

# First task in Bob

Paste the following into Bob while this project folder is open:

---
We are building Vesper for the IBM Bob hackathon. Read AGENTS.md, README.md, docs/requirements.md and docs/system-design.md.

Implement only milestone 1: a runnable Java/Maven demo and a trustworthy baseline check. First inspect installed Java, Maven and Python, and report any missing prerequisites. Use Java 17 compatibility where available; do not install tools or change global settings without explaining what is needed.

Create a small standalone checkout/discount demo under demo/ with a clear requirements.md and a nonempty JUnit test suite. No database or app server. Use synthetic data; do not introduce an undisclosed intentional bug in this baseline milestone.

Implement a minimal local Python baseline command that runs the demo tests, records the command, tool versions, exit status and fresh test results, and refuses to call zero-test, skipped-only, missing-report or failed executions successful. Document the actual command you implement. Add meaningful checks for those failure classifications.

Run the demo tests and baseline checks. Stop after showing the files created, actual results, any blockers and the next proposed milestone. Do not implement the entire design, parallel agents, a hosted UI or automatic fixes yet. Do not claim later workflow stages are complete.

Remind me to save this task's real consumption-summary screenshot in bob_sessions.
---
