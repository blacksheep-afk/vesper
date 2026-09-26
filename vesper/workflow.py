"""Sprint 4/5 workflow runner — full end-to-end demonstration of the Vesper R3 cycle.

Stages (sequential):
  1. baseline     — clean Maven build, all tests must pass
  2. seed         — swap in the seeded (buggy) Checkout.java
  3. reproduce    — run the frozen ReproducerR3Test; must FAIL
  4. regress_bug  — full suite on seeded code; records which tests fail
  5. restore      — reinstate the integrated (fixed) Checkout.java
  6. verify       — run the frozen reproducer on fixed code; must PASS
  7. regress_fix  — full suite on fixed code; all must pass
  8. report       — write a human-readable summary of every stage

Run only trusted local projects. Never modify the frozen reproducer test.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

# Ensure console output handles Unicode on Windows (cp1252 terminals)
if sys.stdout.encoding and sys.stdout.encoding.lower().replace("-", "") != "utf8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import time
from pathlib import Path

# Import web server for real-time UI
from vesper.web_server import VesperWebServer, create_web_ui_files

SEEDED_SOURCE = Path("demo/evidence/seeded/Checkout.java.seeded")
APP_SOURCE    = Path("demo/src/main/java/dev/vesper/Checkout.java")
REPRODUCER    = "dev.vesper.ReproducerR3Test"
RUNS_DIR      = Path(".vesper/runs")


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _mvn(args, project, timeout, label):
    """Run a Maven command; return (exit_code, output_text)."""
    project = Path(project).resolve()
    cmd = [shutil.which("mvn") or "mvn", "-B"] + args
    start = time.time()
    try:
        p = subprocess.run(
            cmd, cwd=project,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, errors="replace",
            timeout=timeout,
        )
        return p.returncode, p.stdout, round(time.time() - start, 3)
    except subprocess.TimeoutExpired as exc:
        return None, f"TIMEOUT after {timeout}s: {exc}", round(time.time() - start, 3)
    except OSError as exc:
        return None, f"OS error: {exc}", round(time.time() - start, 3)


def _parse_surefire(report_dir):
    """Return counts and test-id list from Surefire XML; raises on malformed."""
    import xml.etree.ElementTree as ET
    counts = dict(tests=0, failures=0, errors=0, skipped=0)
    ids = []
    for p in sorted(Path(report_dir).glob("TEST-*.xml")):
        root = ET.parse(p).getroot()
        cases = root.findall("testcase")
        counts["tests"]    += len(cases)
        counts["failures"] += sum(c.find("failure") is not None for c in cases)
        counts["errors"]   += sum(c.find("error")   is not None for c in cases)
        counts["skipped"]  += sum(c.find("skipped") is not None for c in cases)
        ids.extend(c.get("classname", "") + "#" + c.get("name", "") for c in cases)
    return counts, ids


def _stage_header(n, name):
    print(f"\n{'='*60}")
    print(f"  Stage {n}: {name}")
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# Individual stages
# ---------------------------------------------------------------------------

def stage_baseline(run_dir, timeout):
    _stage_header(1, "baseline — fixed source, all tests must pass")
    reports = run_dir / "baseline_reports"
    reports.mkdir(parents=True)
    code, out, dur = _mvn(
        ["-f", "demo/pom.xml", "clean", "test",
         f"-Dvesper.reportsDirectory={reports.resolve()}",
         "-DfailIfNoTests=true"],
        ".", timeout, "baseline",
    )
    counts, ids = _parse_surefire(reports) if code == 0 else ({}, [])
    status = "passed" if (code == 0 and counts.get("tests", 0) > 0
                          and counts.get("failures", 0) == 0
                          and counts.get("errors",   0) == 0
                          and counts.get("skipped",  0) == 0) else "failed"
    print(out[-3000:])
    print(f">> {status}  ({counts})  {dur}s")
    return dict(stage="baseline", status=status, exit_code=code,
                counts=counts, test_ids=ids, duration_seconds=dur)


def stage_seed(run_dir):
    _stage_header(2, "seed — swap in the disclosed seeded (buggy) Checkout.java")
    src = SEEDED_SOURCE.resolve()
    dst = APP_SOURCE.resolve()
    if not src.is_file():
        print(f"ERROR: seeded source not found at {src}")
        return dict(stage="seed", status="error", error=f"missing {src}")
    # Save fixed version
    (run_dir / "Checkout.java.fixed-bak").write_bytes(dst.read_bytes())
    shutil.copy2(src, dst)
    print(f"  Swapped {dst.name} with seeded version from {src}")
    return dict(stage="seed", status="ok", seeded_path=str(src))


def stage_reproduce(run_dir, timeout):
    _stage_header(3, "reproduce — frozen ReproducerR3Test must FAIL on seeded code")
    reports = run_dir / "reproduce_reports"
    reports.mkdir(parents=True)
    code, out, dur = _mvn(
        ["-f", "demo/pom.xml", "clean", "test",
         f"-Dtest={REPRODUCER}",
         f"-Dvesper.reportsDirectory={reports.resolve()}",
         "-DfailIfNoTests=true"],
        ".", timeout, "reproduce",
    )
    counts, ids = _parse_surefire(reports)
    # We WANT a failure here — that is the reproduction
    reproduced = (counts.get("failures", 0) > 0 and code != 0)
    status = "reproduced" if reproduced else "not_reproduced"
    print(out[-3000:])
    print(f">> {status}  ({counts})  {dur}s")
    return dict(stage="reproduce", status=status, exit_code=code,
                counts=counts, test_ids=ids, duration_seconds=dur,
                note="EXPECTED failure on seeded code — confirms defect is present")


def stage_regress_bug(run_dir, timeout):
    _stage_header(4, "regress_bug — full suite on seeded code")
    reports = run_dir / "regress_bug_reports"
    reports.mkdir(parents=True)
    code, out, dur = _mvn(
        ["-f", "demo/pom.xml", "clean", "test",
         f"-Dvesper.reportsDirectory={reports.resolve()}",
         "-DfailIfNoTests=true"],
        ".", timeout, "regress_bug",
    )
    counts, ids = _parse_surefire(reports)
    print(out[-3000:])
    print(f">> exit {code}  ({counts})  {dur}s")
    return dict(stage="regress_bug", exit_code=code,
                counts=counts, test_ids=ids, duration_seconds=dur,
                note="Full regression on seeded code — failures expected from R3 boundary bug")


def stage_restore(run_dir):
    _stage_header(5, "restore — reinstate the integrated fixed Checkout.java")
    bak = run_dir / "Checkout.java.fixed-bak"
    dst = APP_SOURCE.resolve()
    if not bak.is_file():
        print(f"ERROR: backup not found at {bak}")
        return dict(stage="restore", status="error", error=f"missing {bak}")
    shutil.copy2(bak, dst)
    print(f"  Restored fixed Checkout.java from {bak}")
    return dict(stage="restore", status="ok")


def stage_verify(run_dir, timeout):
    _stage_header(6, "verify — frozen ReproducerR3Test must PASS on fixed code")
    reports = run_dir / "verify_reports"
    reports.mkdir(parents=True)
    code, out, dur = _mvn(
        ["-f", "demo/pom.xml", "clean", "test",
         f"-Dtest={REPRODUCER}",
         f"-Dvesper.reportsDirectory={reports.resolve()}",
         "-DfailIfNoTests=true"],
        ".", timeout, "verify",
    )
    counts, ids = _parse_surefire(reports)
    verified = (code == 0 and counts.get("failures", 0) == 0
                and counts.get("errors", 0) == 0)
    status = "verified" if verified else "failed"
    print(out[-3000:])
    print(f">> {status}  ({counts})  {dur}s")
    return dict(stage="verify", status=status, exit_code=code,
                counts=counts, test_ids=ids, duration_seconds=dur)


def stage_regress_fix(run_dir, timeout):
    _stage_header(7, "regress_fix — full suite on fixed code; all must pass")
    reports = run_dir / "regress_fix_reports"
    reports.mkdir(parents=True)
    code, out, dur = _mvn(
        ["-f", "demo/pom.xml", "clean", "test",
         f"-Dvesper.reportsDirectory={reports.resolve()}",
         "-DfailIfNoTests=true"],
        ".", timeout, "regress_fix",
    )
    counts, ids = _parse_surefire(reports)
    all_pass = (code == 0
                and counts.get("tests", 0) > 0
                and counts.get("failures", 0) == 0
                and counts.get("errors",   0) == 0
                and counts.get("skipped",  0) == 0)
    status = "all_passed" if all_pass else "failed"
    print(out[-3000:])
    print(f">> {status}  ({counts})  {dur}s")
    return dict(stage="regress_fix", status=status, exit_code=code,
                counts=counts, test_ids=ids, duration_seconds=dur)


def stage_report(run_dir, stages, workflow_duration):
    _stage_header(8, "report — human-readable summary")
    lines = [
        "# Vesper Workflow Report — Sprint 5 Rehearsal",
        "",
        f"Run directory : {run_dir}",
        f"Total duration: {round(workflow_duration, 1)}s",
        "",
        "## Stage summary",
        "",
        "| Stage | Status | Tests | Failures | Duration |",
        "|-------|--------|-------|----------|----------|",
    ]
    for s in stages:
        c = s.get("counts", {})
        lines.append(
            f"| {s['stage']} | {s.get('status', s.get('exit_code', '—'))} "
            f"| {c.get('tests','—')} | {c.get('failures','—')} "
            f"| {s.get('duration_seconds','—')}s |"
        )

    lines += [
        "",
        "## Finding",
        "",
        "**R3 — expiry-day boundary (seeded defect, disclosed):**",
        "  Seeded: `!today.isBefore(expiry)` → discount skipped on expiry day.",
        "  Fix:    `today.isAfter(expiry)`   → discount applied on expiry day.",
        "",
        "## Verification outcome",
    ]
    verify  = next((s for s in stages if s["stage"] == "verify"),  {})
    regress = next((s for s in stages if s["stage"] == "regress_fix"), {})
    lines.append(f"  Reproducer (fixed code): {verify.get('status','—')}")
    lines.append(f"  Full regression (fixed) : {regress.get('status','—')}")

    report_path = run_dir / "workflow_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nReport written to {report_path}")
    return dict(stage="report", status="written", path=str(report_path))


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def run_workflow(timeout, web_ui=True, web_port=8080):
    run_id = time.strftime("workflow-%Y%m%d-%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    print(f"\nVesper workflow — run ID: {run_id}")
    print(f"Run directory  : {run_dir}")
    print(f"Timeout/stage  : {timeout}s")

    # Initialize web server if requested
    web_server = None
    if web_ui:
        web_ui_dir = Path("vesper/web_ui")
        create_web_ui_files(web_ui_dir)
        web_server = VesperWebServer(port=web_port, web_root=web_ui_dir)
        server_url = web_server.start()
        print(f"Web UI          : {server_url}")

    workflow_start = time.time()
    stages = []

    # Guard: make sure fixed source is in place before seeding
    fixed_line14 = APP_SOURCE.read_text(encoding="utf-8").splitlines()[13]
    if "!today.isBefore" in fixed_line14:
        print("\nWARNING: Checkout.java appears to have the seeded bug already in place.")
        print("Restore the fixed version before running the workflow.")
        if web_server:
            web_server.broadcast_error("Checkout.java has seeded bug already in place")
            web_server.stop()
        return 2

    # Run all stages; if seed fails, do not proceed (can't restore what wasn't saved)
    if web_server:
        web_server.broadcast_stage("baseline", "running")
    
    result = stage_baseline(run_dir, timeout)
    stages.append(result)
    
    if web_server:
        web_server.broadcast_stage("baseline", result["status"], {
            "counts": result.get("counts"),
            "duration_seconds": result.get("duration_seconds")
        })
    
    if result["status"] != "passed":
        print("\nABORTED: baseline must pass before proceeding.")
        _save(run_dir, stages, time.time() - workflow_start)
        if web_server:
            web_server.broadcast_complete("failed", time.time() - workflow_start)
            web_server.stop()
        return 1

    if web_server:
        web_server.broadcast_stage("seed", "running")
    
    result = stage_seed(run_dir)
    stages.append(result)
    
    if web_server:
        web_server.broadcast_stage("seed", result["status"], {
            "note": "Swapped in seeded Checkout.java"
        })
    
    if result["status"] != "ok":
        print("\nABORTED: could not swap in seeded source.")
        _save(run_dir, stages, time.time() - workflow_start)
        if web_server:
            web_server.broadcast_complete("failed", time.time() - workflow_start)
            web_server.stop()
        return 1

    try:
        if web_server:
            web_server.broadcast_stage("reproduce", "running")
        
        stages.append(stage_reproduce(run_dir, timeout))
        
        if web_server:
            reproduce_result = stages[-1]
            web_server.broadcast_stage("reproduce", reproduce_result["status"], {
                "counts": reproduce_result.get("counts"),
                "duration_seconds": reproduce_result.get("duration_seconds"),
                "note": reproduce_result.get("note")
            })
        
        if web_server:
            web_server.broadcast_stage("regress_bug", "running")
        
        stages.append(stage_regress_bug(run_dir, timeout))
        
        if web_server:
            regress_bug_result = stages[-1]
            web_server.broadcast_stage("regress_bug", "failed" if regress_bug_result["exit_code"] != 0 else "passed", {
                "counts": regress_bug_result.get("counts"),
                "duration_seconds": regress_bug_result.get("duration_seconds"),
                "note": regress_bug_result.get("note")
            })
    finally:
        # Always restore the fixed source, even on error
        if web_server:
            web_server.broadcast_stage("restore", "running")
        
        restore_result = stage_restore(run_dir)
        stages.append(restore_result)
        
        if web_server:
            web_server.broadcast_stage("restore", restore_result["status"], {
                "note": "Restored fixed Checkout.java"
            })

    if web_server:
        web_server.broadcast_stage("verify", "running")
    
    stages.append(stage_verify(run_dir, timeout))
    
    if web_server:
        verify_result = stages[-1]
        web_server.broadcast_stage("verify", verify_result["status"], {
            "counts": verify_result.get("counts"),
            "duration_seconds": verify_result.get("duration_seconds")
        })
    
    if web_server:
        web_server.broadcast_stage("regress_fix", "running")
    
    stages.append(stage_regress_fix(run_dir, timeout))
    
    if web_server:
        regress_fix_result = stages[-1]
        web_server.broadcast_stage("regress_fix", regress_fix_result["status"], {
            "counts": regress_fix_result.get("counts"),
            "duration_seconds": regress_fix_result.get("duration_seconds")
        })

    workflow_duration = time.time() - workflow_start
    stages.append(stage_report(run_dir, stages, workflow_duration))
    _save(run_dir, stages, workflow_duration)
    
    # Broadcast diff information
    if web_server:
        original_code = "if (!today.isBefore(expiry)) return subtotalCents;  // SEEDED BUG (Sprint 2): expiry day incorrectly excluded — violates R3 \"inclusive\""
        candidate_code = "if (today.isAfter(expiry)) return subtotalCents;  // R3: expiry is inclusive; discount expires only after the expiry date"
        web_server.broadcast_diff(original_code, candidate_code)

    # Final exit code: 0 only if verify+regress both passed
    verify  = next((s for s in stages if s["stage"] == "verify"),     {})
    regress = next((s for s in stages if s["stage"] == "regress_fix"), {})
    ok = (verify.get("status") == "verified"
          and regress.get("status") == "all_passed")
    
    print(f"\n{'WORKFLOW PASSED [OK]' if ok else 'WORKFLOW FAILED [!!]'}  "
          f"({round(workflow_duration, 1)}s total)")
    
    if web_server:
        web_server.broadcast_complete("ok" if ok else "failed", round(workflow_duration, 1))
        # Keep server running for a bit to allow viewing results
        print(f"\nWeb UI will remain available at {server_url} for 30 seconds...")
        time.sleep(30)
        web_server.stop()
    
    return 0 if ok else 1


def _save(run_dir, stages, duration):
    record = dict(stages=stages, total_duration_seconds=round(duration, 3))
    (run_dir / "result.json").write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["workflow"])
    parser.add_argument("--timeout", type=int, default=120,
                        help="Per-stage Maven timeout in seconds (default: 120)")
    parser.add_argument("--no-web-ui", action="store_true",
                        help="Disable the web UI (default: enabled with auto-open browser)")
    parser.add_argument("--web-port", type=int, default=8080,
                        help="Port for web UI (default: 8080)")
    args = parser.parse_args(argv)
    return run_workflow(args.timeout, web_ui=not args.no_web_ui, web_port=args.web_port)
