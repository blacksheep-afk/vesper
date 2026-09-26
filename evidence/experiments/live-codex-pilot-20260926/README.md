# Live pilot evidence

Read ../../../docs/LIVE-CODEX-COMPARISON-20260926.md for findings and limitations.

- results.json preserves every completed and quota-interrupted model attempt and gate decision.
- adjudication.json and summary.json separate candidate correctness from gate acceptance.
- PROTOCOL.md, manifest.json and frozen-inputs.json retain the pre-run design, assignments and hashes.
- frozen-pilot-gate.py is the exact experimental gate used during the live trial, including its false-rejection defect.
- post-study-fix.json identifies the old and repaired gate hashes and separate rerun outcome.
- RESUMPTION.md and results-before-resume.json retain quota interruption history.

The full raw bundle is delivered as live-comparison-evidence.zip with the task outputs. It contains original/candidate snapshots, prompts, session events, Maven logs/XML, oracle source, scripts and frozen source. Absolute machine paths in records are historical provenance, not portable command defaults. Reconfigure tool/workspace paths before rerunning the harness. No credentials are required to inspect the saved Java evidence; new live Codex sessions require the operator's own authenticated access.
