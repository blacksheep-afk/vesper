---
name: vesper
description: Review a selected Java module against requirements, reproduce suspected defects with tests, and prepare evidence-backed repairs for human review.
---

# Vesper workflow

Read AGENTS.md and docs/requirements.md. Use docs/system-design.md for the evidence contract. If the runner does not exist yet, implement only the milestone requested by the developer; do not pretend its commands exist.

1. Establish a passing nonempty baseline and record source/specification identity.
2. Draft expected behaviours and obtain the developer's interpretation decision.
3. Review the selected scope and propose bounded, requirement-linked suspects.
4. Write and validate a reproducer. Preserve failed attempts and classify setup errors separately. A passing test is not reproduced. Repeat valid original failure to identify flakiness.
5. Freeze the accepted test; prepare a separate candidate patch. Run the unchanged reproducer and full regression suite, checking actual executed test identities and fresh output.
6. Generate a report from actual runner records. Show the candidate diff and wait for the developer's decision before integrating it.

Keep reasoning/proposals separate from execution evidence. Never record approval on the developer's behalf. Capture real Bob task-summary screenshots after relevant tasks.
