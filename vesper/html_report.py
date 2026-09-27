"""Offline, read-only presentation of a saved evidence run. No model or network."""
from datetime import datetime, timezone
import difflib
from html import escape
import json
from pathlib import Path
from urllib.parse import quote

ASSETS = Path(__file__).with_name('assets')
SOURCE = Path('src/main/java/dev/vesper/Checkout.java')
TEST = 'src/test/java/dev/vesper/ReproducerR3Test.java'


def text(value):
    return escape(str(value), quote=True)


def child(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Evidence path escapes the run directory')
    return path


def load_attempts(root, data):
    return [(name, json.loads(child(root, name + '/result.json').read_text(encoding='utf-8')))
            for name in data.get('attempts', [])]


def split_patch(root, diff):
    paths = [child(root, str(Path(part) / SOURCE)) for part in ('original', 'candidate')]
    if not all(p.is_file() for p in paths):
        return '<p class="empty">Source snapshots are unavailable. Inspect the recorded unified patch below.</p>'
    original, candidate = [p.read_text(encoding='utf-8').splitlines() for p in paths]
    rows = []
    groups = list(difflib.SequenceMatcher(a=original, b=candidate).get_grouped_opcodes(3))
    if not groups:
        return '<p class="empty">No source difference recorded between these snapshots.</p>'
    for group in groups:
        for tag, i1, i2, j1, j2 in group:
            for offset in range(max(i2 - i1, j2 - j1)):
                left = original[i1 + offset] if i1 + offset < i2 else ''
                right = candidate[j1 + offset] if j1 + offset < j2 else ''
                left_number = str(i1 + offset + 1) if i1 + offset < i2 else ''
                right_number = str(j1 + offset + 1) if j1 + offset < j2 else ''
                lc = 'removed' if tag in ('replace', 'delete') and left_number else ''
                rc = 'added' if tag in ('replace', 'insert') and right_number else ''
                rows.append(f'<div class="diff-row"><div class="code-line {lc}"><span class="line-number">{left_number}</span>'
                            f'<span class="change-mark" aria-label="{ "Removed" if lc else "Unchanged" }">{"−" if lc else " "}</span><code>{text(left)}</code></div>'
                            f'<div class="code-line {rc}"><span class="line-number">{right_number}</span>'
                            f'<span class="change-mark" aria-label="{ "Added" if rc else "Unchanged" }">{"+" if rc else " "}</span><code>{text(right)}</code></div></div>')
    return '<div class="split-heading"><span>Original <small>before repair</small></span><span>Candidate <small>proposed repair</small></span></div>' + ''.join(rows)


def render_html(run_dir):
    root = Path(run_dir).resolve()
    data = json.loads((root / 'workflow.json').read_text(encoding='utf-8'))
    attempts = load_attempts(root, data)
    by_name = dict(attempts)
    verified = data.get('status') == 'verified_candidate'
    reproduced = data.get('investigation') == 'reproduced'
    synthetic = data.get('evidence_kind') == 'synthetic_fault_injection'
    badge = 'Verified candidate' if verified else 'Verification blocked'
    color = 'good' if verified else 'warn'
    hero = 'Expiry-day discount' if verified else 'Expiry-day discount: review blocked'
    evidence_label = 'Synthetic challenge · no Java executed' if synthetic else 'Disclosed seeded replay · recorded execution'
    labels = {'01-baseline': ('Establish baseline', 'Existing tests before investigation'),
              '02-original': ('Reproduce the finding', 'Original source · first attempt'),
              '03-original-repeat': ('Repeat the failure', 'Original source · independent attempt'),
              '04-candidate-reproducer': ('Check the candidate', 'Same accepted test · proposed fix'),
              '05-candidate-regression': ('Verify regression scope', 'Complete baseline test identities')}
    stages = []
    for number, name in enumerate(labels, 1):
        title, caption = labels[name]
        item = by_name.get(name)
        if item is None:
            stages.append(f'<article class="stage muted"><div class="stage-number">{number:02}</div><div class="stage-content"><h3>{title}</h3><p>{caption}</p></div><span class="pill neutral">Not run</span></article>')
            continue
        counts = item.get('counts', {})
        expected_failure = name in ('02-original', '03-original-repeat') and reproduced
        passed = item.get('status') == 'passed'
        label = 'Expected failure' if expected_failure else ('Passed' if passed else str(item.get('status', 'Unknown')).replace('_', ' ').capitalize())
        tone = 'good' if passed or expected_failure else 'warn'
        command = ' '.join(str(part) for part in item.get('command', [])) or 'Command not recorded'
        links = quote(name, safe='')
        stages.append(f'''<article class="stage"><div class="stage-number {tone}">{number:02}</div>
<div class="stage-content"><div class="stage-title"><h3>{title}</h3><span class="pill {tone}">{text(label)}</span></div>
<p>{caption}</p><div class="stage-facts"><span><b>{text(counts.get('tests', '—'))}</b> tests</span><span><b>{text(counts.get('failures', '—'))}</b> failures</span><span><b>{text(counts.get('errors', '—'))}</b> errors</span><span><b>{text(counts.get('skipped', '—'))}</b> skipped</span><span class="duration">{text(item.get('duration_seconds', '—'))} s</span></div>
<details class="attempt-detail"><summary>Inspect execution</summary><pre>{text(command)}</pre><div class="detail-links"><a href="{links}/result.json">Execution record ↗</a><a href="{links}/execution.log">Full log ↗</a></div><p>Exit code: {text(item.get('exit_code', 'not recorded'))} · Inputs unchanged: {text(item.get('inputs_unchanged', 'not recorded'))}</p></details></div></article>''')
    baseline = by_name.get('01-baseline', {}).get('counts', {})
    regression = by_name.get('05-candidate-regression', {}).get('counts', {})
    target = by_name.get('04-candidate-reproducer', {}).get('counts', {})
    original_attempts = sum(name in by_name for name in ('02-original', '03-original-repeat'))

    def count_passed(counts):
        if not counts:
            return '—'
        return str(counts.get('tests', 0) - counts.get('failures', 0) - counts.get('errors', 0) - counts.get('skipped', 0))

    metrics = [(f'{original_attempts}/2', 'Original attempts', 'Consistent failure required'),
               (count_passed(target), 'Candidate test passes', 'Accepted reproducer' if verified else 'Reported count; gate may reject'),
               (f'{count_passed(regression)}/{baseline.get("tests", "—")}', 'Regression passes', 'Compared with baseline'),
               (str(data.get('duration_seconds', '—')) + 's', 'Recorded duration', 'Execution time · not time saved')]
    metric_html = ''.join(f'<div class="metric"><div class="metric-number">{text(v)}</div><h2>{text(k)}</h2><p>{text(note)}</p></div>' for v, k, note in metrics)
    hashes = data.get('snapshots', {}).get('candidate', {})
    provenance = [('Test SHA-256', hashes.get(TEST, 'Not recorded')),
                  ('Patch SHA-256', data.get('patch_sha256', 'Not recorded')),
                  ('Runner SHA-256', data.get('runner_sha256', 'Not recorded')),
                  ('Requirement SHA-256', data.get('requirement_sha256', 'Not recorded'))]
    provenance_html = ''.join(f'<div class="hash-row"><dt>{text(k)}</dt><dd><code>{text(v)}</code></dd></div>' for k, v in provenance)
    epoch = data.get('started_at')
    when = datetime.fromtimestamp(epoch, timezone.utc).strftime('%d %b %Y · %H:%M UTC') if epoch is not None else 'Time not recorded'
    observed = '<strong>900¢</strong><span>expected</span><span class="vs">→</span><strong class="failure-text">1,000¢</strong><span>observed on original</span>' if reproduced else '<strong>No confirmed failure</strong><span>Read the recorded blocker before deciding</span>'
    diff = data.get('diff', 'No patch prepared.')
    css = (ASSETS / 'report.css').read_text(encoding='utf-8')
    js = (ASSETS / 'report.js').read_text(encoding='utf-8')
    mark = (ASSETS / 'vesper-mark.svg').read_text(encoding='utf-8')
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><meta name="description" content="Read-only Vesper evidence report with actual execution records and candidate patch.">
<title>{text(badge)} · Vesper evidence</title><style>{css}</style></head>
<body><a class="skip-link" href="#main">Skip to evidence</a>
<aside class="sidebar"><a class="brand" href="#overview" aria-label="Vesper overview">{mark}<span class="brand-word">vesper</span></a><div class="brand-caption">Clarity before acceptance.</div><div class="side-label">This evidence record</div>
<nav aria-label="Report sections"><a href="#overview" class="nav-item active"><span>00</span>Overview</a><a href="#execution" class="nav-item"><span>01</span>Execution trail</a><a href="#patch" class="nav-item"><span>02</span>Candidate patch</a><a href="#provenance" class="nav-item"><span>03</span>Provenance</a></nav>
<div class="sidebar-bottom"><details class="brand-key"><summary>The four stars</summary><p>Requirement<br>Reproduction<br>Verification<br>Human review</p></details>Saved evidence<p>Read-only. Available offline.<br>No live agent is running.</p><span class="side-credit">Black Sheep Team</span></div></aside>
<div class="page"><header class="topbar"><a href="#overview" class="mobile-brand" aria-label="Vesper overview">{mark}<span>vesper</span></a><div class="breadcrumb">Evidence <span>/</span> Checkout <span>/</span> <b>R3</b></div><div class="top-actions"><span class="timestamp">{text(when)}</span><button id="print-report" class="quiet-button" type="button">Print / PDF</button></div></header>
<main id="main"><section id="overview" class="overview"><div class="eyebrow">CHECKOUT <span>/</span> REQUIREMENT R3</div>
<div class="hero"><div><div class="status-line"><span class="pill {color}"><span aria-hidden="true">{'✓' if verified else '!'}</span> {text(badge)}</span><span class="evidence-tag">{text(evidence_label)}</span></div><h1>{hero}</h1><p class="lead">Review the inclusive expiry rule, the recorded test results, and the proposed change to Checkout.java.</p><a class="primary-link" href="#{'patch' if verified else 'execution'}">{'Inspect candidate patch' if verified else 'Inspect verification blocker'} <span aria-hidden="true">↗</span></a></div>
<div class="decision-panel"><div class="side-label">Developer decision</div><h2>{text(str(data.get('approval', 'pending')).replace('_', ' ').capitalize())} review</h2><p>Verification is an input to your decision. It does not approve or apply a patch.</p><div class="decision-footer"><span>Integration</span><b>{text(str(data.get('integration', 'not_performed')).replace('_', ' '))}</b></div></div></div>
<div class="metrics">{metric_html}</div></section>
<section class="requirement-panel"><div><div class="eyebrow">THE EXPECTATION</div><h2>Expiry is inclusive.</h2><p>1,000-cent subtotal · 10% discount · checkout on the expiry date.</p></div><div class="outcome-numbers">{observed}</div></section>
<section id="execution"><div class="section-heading"><div><div class="eyebrow">01 / EXECUTION</div><h2>Execution trail</h2></div><span class="section-note">{len(attempts)} recorded attempts</span></div>
<div class="execution-layout"><div class="timeline">{''.join(stages)}</div><aside class="findings"><h3>{'Recorded conclusion' if verified else 'Why verification stopped'}</h3><p>{text(data.get('explanation', 'No explanation recorded.'))}</p><div class="scope-note"><h4>Tested scope</h4><p>One disclosed seed and an existing fix. The report does not claim a new discovery or complete correctness.</p></div><a href="workflow.json">Read run metadata ↗</a></aside></div></section>
<section id="patch"><div class="section-heading"><div><div class="eyebrow">02 / CANDIDATE</div><h2>Candidate patch</h2></div><div class="view-controls" role="group" aria-label="Patch display"><button type="button" data-view="split" aria-pressed="true">Side by side</button><button type="button" data-view="unified" aria-pressed="false">Unified</button></div></div>
<div class="patch-shell"><div class="file-heading"><code>src/main/java/dev/vesper/Checkout.java</code><span class="file-tag">Proposed patch</span></div><div id="split-view">{split_patch(root, diff)}</div><pre id="unified-view" hidden><code>{text(diff)}</code></pre></div><p class="patch-caption">Line numbers refer to the preserved snapshots. Source text and comments are displayed as recorded.</p></section>
<section id="provenance"><div class="section-heading"><div><div class="eyebrow">03 / TRACEABILITY</div><h2>Source &amp; provenance</h2></div><a class="quiet-button" href="report.md">Markdown version ↗</a></div>
<div class="provenance-panel"><div class="run-label"><span>Run identifier</span><code>{text(root.name)}</code></div><details><summary>Input fingerprints and tool versions</summary><dl>{provenance_html}</dl><h3>Java</h3><pre>{text(data.get('java', {}).get('output', 'Not recorded'))}</pre><h3>Maven</h3><pre>{text(data.get('maven', {}).get('output', 'Not recorded'))}</pre><h3>Python</h3><pre>{text(data.get('python', 'Not recorded'))}</pre></details></div>
<div class="limits"><h3>Limits of this record</h3><p>Requirements still need human judgment. Frozen inputs and separate workspaces are not an operating-system sandbox or authenticated proof. No agent-comparison result, productivity gain, Bob usage or new approval is implied by this report.</p></div></section>
</main><footer><span>vesper <span class="footer-caption">Requirement / Reproduction / Verification / Human review</span></span><span>Read-only · works offline</span></footer></div><script>{js}</script></body></html>'''
    destination = root / 'report.html'
    destination.write_text(html, encoding='utf-8')
    return destination
