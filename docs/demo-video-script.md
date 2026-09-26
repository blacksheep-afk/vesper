# Vesper demo recording script

Target three minutes, including at least 90 seconds of working-solution footage, following the stored event guide. Confirm final requirements before submission. Record real UI and output; do not invent interactions.

| Time | Screen and narration |
| --- | --- |
| 0:00–0:20 | Problem: a green command does not establish that the required test ran. Vesper makes patch evidence reviewable. |
| 0:20–0:45 | Show the gate challenge report: one valid case accepted, 15 invalid cases rejected. Label prominently: synthetic fault injection, not agent failure statistics. |
| 0:45–1:05 | In Bob IDE, ask Bob to run the supplied R3 replay and inspect the report. Explain that this is a seeded defect with an existing corrected candidate. |
| 1:05–1:30 | Show R3 and both original execution records: expiry day is inclusive; expected 900, observed 1000. |
| 1:30–1:50 | Show the report's exact diff and snapshot hashes. The accepted test remains unchanged. |
| 1:50–2:20 | Show candidate reproducer and regression records: use the actual counts from the recorded run. Point out pending approval and no integration. |
| 2:20–2:45 | Explain limits: supplied demo only, correct requirements still matter, no measured time savings, live Codex comparison pending. |
| 2:45–3:00 | Team and repository credit; identify actual Bob usage and other tooling honestly. |

Run `python -m experiments.gate_challenge` and `python -m vesper workflow --timeout 300` before recording. A full replay can take longer than its screen segment: label cuts/time compression. If showing historical output, label it historical. Do not narrate a new test or fix being written unless the recorded session actually does that.

Review legibility, audio, total length and working-solution duration. Capture the real Bob consumption summary separately in bob_sessions. A video and screenshots have not been created by this script.
