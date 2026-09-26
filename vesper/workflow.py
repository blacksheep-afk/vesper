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

def run_workflow(timeout):
    run_id = time.strftime("workflow-%Y%m%d-%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    print(f"\nVesper workflow — run ID: {run_id}")
    print(f"Run directory  : {run_dir}")
    print(f"Timeout/stage  : {timeout}s")

    workflow_start = time.time()
    stages = []

    # Guard: make sure fixed source is in place before seeding
    fixed_line14 = APP_SOURCE.read_text(encoding="utf-8").splitlines()[13]
    if "!today.isBefore" in fixed_line14:
        print("\nWARNING: Checkout.java appears to have the seeded bug already in place.")
        print("Restore the fixed version before running the workflow.")
        return 2

    # Run all stages; if seed fails, do not proceed (can't restore what wasn't saved)
    result = stage_baseline(run_dir, timeout)
    stages.append(result)
    if result["status"] != "passed":
        print("\nABORTED: baseline must pass before proceeding.")
        _save(run_dir, stages, time.time() - workflow_start)
        return 1

    result = stage_seed(run_dir)
    stages.append(result)
    if result["status"] != "ok":
        print("\nABORTED: could not swap in seeded source.")
        _save(run_dir, stages, time.time() - workflow_start)
        return 1

    try:
        stages.append(stage_reproduce(run_dir, timeout))
        stages.append(stage_regress_bug(run_dir, timeout))
    finally:
        # Always restore the fixed source, even on error
        restore_result = stage_restore(run_dir)
        stages.append(restore_result)

    stages.append(stage_verify(run_dir, timeout))
    stages.append(stage_regress_fix(run_dir, timeout))

    workflow_duration = time.time() - workflow_start
    stages.append(stage_report(run_dir, stages, workflow_duration))
    _save(run_dir, stages, workflow_duration)

    # Final exit code: 0 only if verify+regress both passed
    verify  = next((s for s in stages if s["stage"] == "verify"),     {})
    regress = next((s for s in stages if s["stage"] == "regress_fix"), {})
    ok = (verify.get("status") == "verified"
          and regress.get("status") == "all_passed")
    print(f"\n{'WORKFLOW PASSED [OK]' if ok else 'WORKFLOW FAILED [!!]'}  "
          f"({round(workflow_duration, 1)}s total)")
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
    args = parser.parse_args(argv)
    return run_workflow(args.timeout)
