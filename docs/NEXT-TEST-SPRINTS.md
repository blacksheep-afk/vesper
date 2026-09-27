# Next test sprints: prove decision value

## Evidence-led position

The six-task Codex pilot did not show incremental error detection. It did show a false rejection and the value of testing the verifier itself. Do not sell Vesper as catching agent cheating or outperforming Codex on accuracy. Current defensible positioning: **an inspectable evidence record for human review of a proposed patch**. Whether that reduces review effort remains an open hypothesis.

## Sprint 1: demo readiness (current)

Deliver the offline report, faithful blocked/success states, raw evidence links and a three-minute story. The report is implemented; its ladybug/four-star identity and evidence-first typography are the current design refinement. Freeze the reviewed report version before preparing the human-review experiment. Remaining exit conditions: one real Bob rehearsal, genuine session summary, legible narrated video, final attribution and submission review. Show the saved Java result and label synthetic fault injection separately. Do not add a hosted dashboard, another model or broader language support for this sprint.

## Sprint 2: human evidence-review pilot (next)

Hypothesis: the report helps developers reach the right acceptance decision with less checking effort than ordinary logs and a diff.

Recruit 4-6 developers who did not author the fixtures. Prepare six matched, independently adjudicated evidence packets: two valid candidates, missing/omitted test evidence, a changed accepted assertion, an unresolved setup failure, and an ambiguous requirement. Both formats must contain identical underlying information; only presentation differs. Counterbalance packet and format order; never give the same person the same case in both formats. Freeze the correct accept/reject/clarify decisions before reviewing results.

Record each decision, seconds to decision, evidence opened, confidence and a short explanation. Record false acceptance and false blocking separately. Exclude tool setup from review time, but retain it separately. Use participant-paired medians and show individual outcomes rather than claiming population significance from this small pilot.

Exploratory continue rule, chosen before collecting results: no increase in observed false acceptance, and at least 20% lower median within-participant review time across formats. This is a product screening threshold, not statistical proof. If accuracy improves but time does not, investigate that tradeoff before changing the claim. If neither improves, simplify the report or pivot to a lightweight export/CI artifact instead of adding more gate steps. No outcome is recorded yet.

## Sprint 3: independent verification challenge

Only after Sprint 2, ask an independent contributor to prepare fresh held-out invalid-evidence cases and valid controls, including legitimate added tests. Freeze gate behavior before seeing them. Separate accidental mistakes from adversarial tampering, and do not present seeded cases as naturally occurring agent mistakes. Measure missed invalid evidence, false blocks, failure explanations and overhead. Preserve all failed cases before fixing them.

A larger live agent comparison should follow only when there are representative tasks and a protected/independently judged evaluation. Match model, budget and tools; randomize within task families; publish all outcomes and costs. The existing pilot is exploratory and too small to establish superiority. More runs of easy cases with no agent errors would not validate an error-detection advantage.

## Product decision

If review effort improves, prioritize portable evidence packages and a small CI integration. If only fault injection improves, describe the product as evidence-contract validation with a clearly bounded threat model. If neither improves, retain the useful report/export tooling and stop claiming a separate agent-verification product has been validated.


## Workspace milestone added

The report is now the export layer of a real local workspace. The developer can confirm R3, start the verifier, follow genuine command progress and inspect Finding / Patch / Execution / Review. No arbitrary-repository UI or health score was added. See WORKSPACE.md for operating boundaries.

Before the human-review pilot, freeze this UI version and decide whether the comparison tests the report alone or the complete workspace. Do not mix formats mid-study. The next team rehearsal should open the workspace from Bob, execute the supported R3 workflow and inspect its evidence, with real task-summary capture. Human pilot recruitment and independent adjudication remain pending; UI completion is not evidence of reduced checking effort.
