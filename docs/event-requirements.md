# Vesper: verified event requirements

Checked 25 September 2026 in the signed-in browser. These are source facts and planning constraints, not instructions authorizing account changes or submissions.

## Sources

- Event: https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon
- Official guide: https://lablab-ibm-bob-2-hackathon-guide.s3.us.cloud-object-storage.appdomain.cloud/index.html
- Signed-in submission form: https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/black-sheep/submission

## Access and timing

Signed-in event page shows Approved, Team Dashboard for black-sheep, and Submit Project. Submission form is accessible. No fields were filled and nothing was submitted.

Kickoff: 25 September 2026, 17:00 SAST. Submission deadline: 27 September 2026, 17:00 SAST (11:00 ET).

## Required build and evidence

- Working prototype improving a specific developer workflow on a real or sample project, with measurable impact.
- IBM Bob IDE must be a core component. Bob Shell and watsonx are optional. Other frameworks/technologies are permitted subject to their usage policies.
- Use the hackathon-provisioned Bob account. 40 Bobcoins are allocated; no additional hackathon Bobcoins after exhaustion.
- Each participant must retain all relevant Bob IDE task session consumption summary screenshots in the final repository's bob_sessions folder. PNG is preferred. Include team, task number and short description in filenames.
- Guide account-name examples differ: invitation ibm-hackathon-xxxx; settings ibm-coding-challenge-xxx or ibm-coding-challenge-uat, region us-east. Verify the actual provisioned account rather than guessing from these examples.
- Guide calls for upgrading IDE 1.0.3 to latest 2.0.x and 2.0.0 to 2.0.2 or later; those older versions stop working September 30.
- No client data, personal information, social-media data, or unauthorized confidential assets. Public sources must permit commercial use; retain source list.

## Submission package

- Title, short description, long Problem & Solution Statement, IBM Bob Usage Statement, category and technology tags.
- Both statements: at most 500 words each.
- Public repository including Bob-assisted files and task summary screenshots from every team member.
- Demo application platform, application URL, cover image, video demonstration, slide presentation are listed on the event page.
- MP4 demonstration: at most 3 minutes, at least 90 seconds showing the working solution, narration, clear Bob usage.
- Event page states submissions must be original and MIT-compliant.

Live form step 1 adds character constraints: title 5–50 characters; short description 50–255 characters; each long statement 500–4000 characters. Meet both the word limit and character limits. Three steps total; later form steps were not inspected because step 1 is empty.

## Judging

Application of Technology (complete, thought-out, clear use of Bob), Presentation, Business Value (practical impact on a high-priority issue), Originality (unique approach using Bob). No weights observed.

## Consequences for Vesper

The accepted one-repo, requirements-to-reproducer-to-fix design fits the challenge. Keep Bob IDE visibly central; retain evidence as tasks finish. A sample project is explicitly allowed: identify seeded bugs honestly and separate them from organic findings. Measure time and valid reproductions; never call every passing test a false positive or every failing generated test a proven bug. Build one working loop before parallel expansion. Reserve time for a narrated 3-minute demo, slides and both statements. A hosted service is not yet established as mandatory: application URL is listed, but later form validation remains unchecked.

Next operational dependency: confirm IBM invitation, IDE installation, hackathon account selection, and Bobcoin allocation. LabLab login alone does not verify IBM Bob access.

