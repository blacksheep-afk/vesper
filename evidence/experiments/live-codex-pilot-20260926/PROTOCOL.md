# Frozen live pilot protocol

User confirmed expected behavior in the parent task before execution on 2026-09-26. Six sequential fresh Codex CLI sessions, three per condition; A ordinary verification, B ordinary verification plus external Vesper gate feedback. Assignments randomized within families using the recorded seed. No baseline verification is weakened. Maximum 10 minutes initial session; up to two B correction turns, within 30 minutes total task time. Preserve failures and timeouts.

Both receive identical tool paths, dependency cache policy, public requirements and ordinary tests. B is informed that gate feedback follows completion; the first answer is retained. A and B both receive an independent final held-out evaluation, implemented using BigInteger arithmetic and deterministic boundary/random cases. Correct/no-change and ambiguity controls are separate qualitative controls, not matched defect-repair timing measurements.

The supplied-snapshot gate is an experimental extension using Vesper's existing execution and XML classifier; it is qualified against known correct, incorrect and mutated inputs before sessions. Its gate source, task originals, requirements, oracle and assignments are hashed before sessions. B can receive its first rejected gate result and correct its patch. A does not receive extra evaluator feedback. Additional detection requires an incorrect first completion independently demonstrated and corrected after feedback.

No claim of independent human blinding: the coordinating agent prepared and judges the tasks, with human-confirmed requirements. Evaluator files are outside task workspaces, but readable on this host: procedural separation, not an adversarial security boundary. Task solutions are deliberately small and seeded; no population success-rate or productivity estimate. Active human minutes and monetary cost are unavailable; record actual token usage and elapsed machine time. Interpret ambiguity via final answer and require unchanged production code. Both control tasks already meet specified single-discount requirements.

Fresh sessions use the installed Codex CLI's default model and reasoning configuration, held constant; record actual model/settings from session metadata. No parallel agents. No remote publishing or source integration. Preflight connectivity calls are not scored tasks.

## Operational details

Codex preflight identifies model gpt-6-astra; retain the default reasoning settings and record actual metadata for each session. Codex CLI 0.155.0-alpha.16.4, Oracle Java 17.0.12, checksum-verified Apache Maven 3.9.9, Python bundled with Codex. Same warmed workspace Maven cache for both conditions. Sequential order alternates A/B within the two repair families, then A/B controls. All original ordinary tests must pass during qualification. Existing test files and build inputs are frozen by the B gate; added tests are permitted. The final judge runs trusted original tests plus held-out tests against only candidate production files.

The two arithmetic tasks have different failure mechanisms (overflow versus premature truncation), and the controls require different decisions. Report individual outcomes; do not interpret their times as a controlled productivity estimate. This pilot measures obvious seeded defects and workflow feasibility, not representative repository work.

Launch correction before any model session: CLI rejected redundant --sandbox with --approve-for-me. Six command-line validation failures (exit 2, no thread id or model usage) are retained in launch-errors. Removed redundant --sandbox; --approve-for-me selects workspace-write. Task assignments, source inputs and oracle are unchanged. These are setup failures, not model outcomes.
