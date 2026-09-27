"""Persistent local styling preview of the live dashboard and saved run evidence."""
import argparse
import json
from pathlib import Path
import time

from .web_server import VesperWebServer, create_web_ui_files


def saved_events(folder):
    """Translate a saved workflow record using the same event shape as the runner."""
    folder = Path(folder)
    record = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
    stages = record['stages']
    events = []
    for item in stages:
        event = {key: item[key] for key in ('stage', 'status', 'counts', 'duration_seconds', 'note') if key in item}
        if item['stage'] == 'regress_bug':
            event['status'] = 'failed' if item['exit_code'] != 0 else 'passed'
        if item['stage'] in ('seed', 'restore'):
            event['note'] = ('Swapped in seeded Checkout.java' if item['stage'] == 'seed'
                             else 'Restored fixed Checkout.java')
        events.append(('stage', event))
    fixed = folder / 'Checkout.java.fixed-bak'
    seeded = Path(__file__).resolve().parents[1] / 'demo/evidence/seeded/Checkout.java.seeded'
    if fixed.is_file() and seeded.is_file():
        original = next((line.strip() for line in seeded.read_text(encoding='utf-8').splitlines() if 'isBefore(expiry)' in line), None)
        candidate = next((line.strip() for line in fixed.read_text(encoding='utf-8').splitlines() if 'isAfter(expiry)' in line), None)
        if original and candidate:
            events.append(('diff', {'original': original, 'candidate': candidate}))
    statuses = {item['stage']: item.get('status') for item in stages}
    passed = statuses.get('verify') == 'verified' and statuses.get('regress_fix') == 'all_passed'
    events.append(('complete', {'status': 'ok' if passed else 'failed',
                                'duration': round(record['total_duration_seconds'], 1)}))
    return events


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--run-dir', type=Path, required=True,
                        help='Saved workflow folder containing result.json; no tests are rerun')
    args = parser.parse_args(argv)
    events = saved_events(args.run_dir)
    assets = Path(__file__).resolve().parent / 'web_ui'
    create_web_ui_files(assets)
    server = VesperWebServer(port=args.port, web_root=assets)
    for kind, data in events:
        server.sse_handler.broadcast(kind, data)
    print(f'Saved-run dashboard: {server.start()}', flush=True)
    print(f'Assets: {assets}\nSaved record: {args.run_dir.resolve()}', flush=True)
    print('Preview only: no tests rerun. Edit styles.css and refresh. Ctrl+C stops the server.', flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
    return 0
