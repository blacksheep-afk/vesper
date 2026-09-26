# Vesper — hackathon submission statements

Both statements are written to satisfy the lablab.ai submission form requirements:
- Each statement: 500–4000 characters (form constraint).
- Total word count per statement: at most 500 words (event guide constraint).
- Content: original, honest, based on implemented and verified work only.

---

## Statement 1: Problem and Solution Statement

(Target: 500–4000 characters, at most 500 words)

---

**Problem**

AI code review tools surface suspected bugs, but they do not show whether the bugs are real. A developer who receives a list of findings faces an investigation problem: read the source code, understand the requirement, write a test, run it, and decide whether the failure comes from the application or from a faulty assumption in the test. That investigation can take as long as fixing the bug itself. When the AI also proposes a fix, the developer faces a second question: does this change solve the problem without breaking other behaviour? Without evidence, the answer requires another manual pass.

The result is that AI assistance creates work before it saves work. Developers spend time verifying findings and validating fixes that are supposed to have been verified already.

**Solution**

Vesper connects IBM Bob IDE to a local test runner in one sequential workflow. The developer makes a single starting request. Bob reads the requirements document and the selected source module, presents up to five expected behaviours, and waits for the developer to confirm the interpretation. This confirmation step prevents findings based on misread requirements.

Once a requirement is confirmed, Bob writes a targeted reproducer test and runs it through the local Maven test runner. If the test fails with a valid assertion failure on the application logic, the finding is marked as reproduced. The test is then frozen — it cannot be modified during the repair phase.

Bob prepares a candidate fix as a separate patch and shows the developer the exact diff before applying anything. The unchanged reproducer and the full existing regression suite are run against the candidate. All results — test identities, counts, exit codes, timestamps — are saved in a unique run directory. Nothing is summarised from memory; the evidence comes from the actual Surefire XML reports.

The developer reviews the recorded diff and test results and decides whether to accept the change. Candidate verification, developer approval, and source integration are kept as separate states.

For the hackathon demonstration, Vesper runs on a small synthetic Java checkout service with a disclosed seeded defect in the discount-expiry boundary condition. All findings are labelled as seeded demo bugs. The workflow completes the full requirement-to-tested-fix cycle in one Bob task, leaving a verifiable evidence trail: passing baseline, failing reproducer on the buggy code, single-line diff, passing reproducer on the fixed code, 12/12 regression pass.

Vesper does not claim to find all bugs or to eliminate the need for human judgment. It reduces the manual investigation burden by making the evidence concrete and reviewable before the developer decides.

---

## Statement 2: IBM Bob Usage Statement

(Target: 500–4000 characters, at most 500 words)

---

**How IBM Bob IDE is used in Vesper**

IBM Bob IDE is the core of the Vesper workflow, not a peripheral tool. Every stage that involves reading, reasoning, writing, or proposing a change is performed by Bob. The local Python runner and the Maven test executor provide only execution infrastructure; they do not make decisions.

**Reading and scoping.** Bob reads the requirements document and the selected Java source file at the start of each task. It extracts expected behaviours and presents them to the developer in plain language. This reading step replaces the developer's initial manual review of both documents.

**Requirement confirmation.** Bob presents up to five expected behaviours and waits for the developer's interpretation decision before proceeding. This explicit confirmation step is implemented in the Vesper Bob skill (`/.bob/skills/vesper/SKILL.md`) and enforced through the task conversation. Bob does not proceed to investigation without developer input.

**Reproducer authorship.** Bob writes the JUnit reproducer test. The test includes the input, the expected value derived from the confirmed requirement interpretation, and a descriptive assertion message linking back to the requirement identifier. The developer reviews the test before it is run.

**Candidate patch authorship.** Bob prepares the candidate fix as a separate file and presents the exact unified diff to the developer. No change is applied to the accepted source until the developer approves it in the conversation.

**Evidence coordination.** Bob invokes the local runner commands (`python -m vesper baseline`, `python -m vesper workflow`) through the IDE terminal. It reads and interprets the result JSON and Surefire XML reports, then presents the per-test results, counts, and classification to the developer. The raw files are preserved in `.vesper/runs/` for independent inspection.

**Task evidence.** Each relevant Bob task ends with the developer capturing the task consumption summary screenshot from the Bob IDE Tasks panel. These screenshots are stored in `bob_sessions/` in the repository. The Bobcoin figures are read from the actual screenshot; they are not estimated.

**Skill and agent instruction.** The project includes a Bob skill file (`.bob/skills/vesper/SKILL.md`) that encodes the Vesper workflow as a reusable Bob instruction. The `AGENTS.md` file in the project root provides the agent operating rules, including the prohibition on fabricated results, synthesised screenshots, and self-recorded approvals.

Bob 2.0's extended context and instruction-following capability make the sequential, evidence-separated workflow practical in a single task session. The workflow was developed and tested using the hackathon-provisioned Bob account. Sprint task-summary screenshots are retained in `bob_sessions/` as required by the event guide.
