# Experiment 1: Does verification add value beyond a capable agent?

Chosen agent for the live comparison: **Codex**.

First qualification run: [results and limitations](EXPERIMENT-1-RESULTS.md).

## Question and decision

Does an enforced verification gate reduce incorrect acceptance of agent-generated
patches beyond Codex's normal self-checking, at acceptable additional time and cost?
We must not count a well-prompted coding loop as independent enforcement.

There are two separate measurements. Gate qualification tests whether the current
software enforces its own contract. The live comparison tests whether that
enforcement changes developer outcomes. Passing the first does not prove the second.

## Phase A: Gate qualification (implemented)

Run from the repository root with Python 3:

```console
python -m experiments.gate_challenge
```

Outputs go to a fresh directory under `.vesper/experiments/`. The command exits 1
when any expected decision is missed or the workflow crashes. That is an
experiment result, not a failed Maven build. Each case retains its fixture copy,
XML, workflow output, console record and structured result. The report binds the
tested workflow and harness to their exact SHA-256 hashes and repository revision.

For the restored runner, process execution and version capture are replaced by labeled fixtures. The actual workflow, XML parser, snapshot checks and final exit decision run in isolated copies of the supplied demo. The historical runner comparison replaces its `_mvn` helper.
Neither Java nor Maven runs. Two synthetic test identities stand in for a suite;
do not describe their counts as the actual Java suite's counts. No agent is asked
to cheat, and no intent is inferred from a result.

The 16 known development cases are:

| Input condition | Required decision |
| --- | --- |
| Valid, consistent evidence | Accept |
| Missing targeted reports | Reject |
| Zero targeted cases | Reject |
| Skipped reproducer | Reject |
| Wrong targeted identity | Reject |
| Changed reproducer assertion | Reject |
| Missing baseline regression identity | Reject |
| Duplicate regression identities | Reject |
| Original test already passes | Reject repair claim |
| Unrelated original assertion failure | Reject reproduction claim |
| Original setup failure | Reject repair claim; preserve unresolved state |
| Original would pass on a repeat attempt | Reject repeatability claim |
| XML counters disagree with its cases | Reject |
| Malformed XML | Recorded rejection, not an unhandled crash |
| Candidate assertion still fails | Reject |
| Existing regression breaks | Reject |

Qualification requires all decisions correct, no crashes, and accepted source
unchanged. This deliberately small corpus does not establish general robustness.
The flaky scenario supplies a failing first attempt and would supply a passing
repeat; the report records how many original targeted attempts were requested.

Not covered: determining whether an accepted test expresses the correct business
requirement, hostile modification of the verifier, forged executor output,
arbitrary Maven build behavior, or a real process kill. Frozen inputs and recorded
identities alone are not a security boundary against an agent that can rewrite
the checker or fabricate its trusted inputs.

## Phase B: Codex comparison protocol

A bounded live pilot has now been executed. See [results, deviations and limits](LIVE-CODEX-COMPARISON-20260926.md). The frozen pilot-specific protocol and interruption records are retained with its evidence. The broader study design below remains a plan, not a claim that every element was completed.

Start only after Phase A qualifies a specific gate revision. Freeze the protocol
and acceptance criteria before collecting outcomes. Preserve failed and unresolved
sessions; never replace a poor outcome with an unrecorded retry.

### Experimental unit and conditions

Start with six bounded Java/Maven tasks in three matched pairs, followed by a
larger study only if the workflow is usable. Use three new tasks per condition,
balanced for defect class and difficulty. A pilot this small is descriptive and
cannot establish a reliable population success rate.

- **A, Codex alone:** a fresh session receives the requirements, code and ordinary
  tests. Ask it to fix the issue, verify its work, and report its evidence. Allow
  normal reasoning, terminal use, test authoring and self-correction.
- **B, Codex plus Vesper:** the same capabilities and task brief, with a qualifying
  Vesper gate available. The accepted reproducer and declared regression manifest
  are frozen independently. Codex can correct a rejected patch within the same
  session; include that work and time in the result.

Use the same recorded model, reasoning setting, tools, dependency cache policy,
task time limit and permission policy. Record the actual settings used rather
than assuming the product name identifies a model. Randomize task assignment;
use new sessions so a solution or feedback from one condition is not carried over.
Do not reduce the baseline agent's verification instructions to manufacture value.

### Independent judging

Before coding, a human confirms the expected behavior for each task. Keep the
evaluation oracle and accepted-test manifest outside the editable task workspace.
Use a separate evaluator to run the original/candidate checks, evaluate held-out
boundary cases, compare required test identities, and verify the exact final patch.
Apply this same final evaluation to both conditions. Do not score B using only
Vesper's own success flag. Hide condition labels from the human adjudicator where
practical, and document any unavoidable unblinding.

Include requirement ambiguity as an explicit case; clarification is a valid
outcome. Never label the agent's defensible interpretation a bug using an
undisclosed requirement. Include correct/no-change cases to measure unnecessary
changes. An intentionally tampered evidence bundle is a separate robustness test,
not evidence that Codex naturally produces that behavior.

Protect the evaluator's files and execution records from the coding session.
Merely telling the agent not to edit them provides procedural separation only;
document that limitation if filesystem/process permissions do not enforce it.

### Measurements and decision rules

For every task record:

1. Final agent claim and exact final source/patch hashes.
2. Independently adjudicated outcome: correct, incorrect, needs clarification,
   or unresolved because execution failed.
3. Whether an incorrect patch was accepted, or a correct patch unnecessarily blocked.
4. Time to first claimed completion and final accepted outcome; separately record
   human active minutes, gate execution seconds, correction rounds and setup time.
5. Actual model/tool usage when exposed; leave unavailable cost fields blank.
6. Gate findings and whether Codex had already identified those problems before
   receiving gate feedback. This separates additional detection from duplicated work.

For the pilot, report each task and raw counts. Do not advertise percentages as
population estimates or claim a productivity improvement from runner duration.
Predeclare a time limit, for example 30 minutes per task; timeouts count as
unresolved and their time remains in the record.

Continue toward a larger experiment only if the gate catches an independently
confirmed problem missed before feedback, or reduces measured human checking work
without increased incorrect acceptance. If both conditions solve everything, the
pilot found no demonstrated incremental detection benefit; try harder realistic
tasks without claiming a win. If the gate adds work without benefit, narrow Vesper
to reusable evidence capture or a skill instead of adding more orchestration.

## Execution sheet

Create one row per real session. An empty table is intentionally not a result.

| Task | Condition | Model/settings | Revision | First claim | Final judged outcome | Human minutes | Wall time | Gate time | Corrections | Additional detection | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Immediate order

1. Run qualification on merged main and retain the result.
2. Recover and verify the stronger historical safeguards if qualification fails.
3. Confirm support for independently supplied original/candidate snapshots; the
   hard-coded R3 replay alone cannot support arbitrary Codex task comparisons.
4. Requalify, freeze that gate revision, then execute the Codex pilot above.

No live Codex result, improvement claim, or security guarantee is implied by
creating this protocol or passing its synthetic fixtures.
