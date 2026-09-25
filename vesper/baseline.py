"""Sprint 1 baseline runner. Run only trusted local projects."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET


def classify(report_dir, exit_code):
    counts = dict(tests=0, failures=0, errors=0, skipped=0)
    identities = []
    reports = sorted(Path(report_dir).glob("TEST-*.xml"))
    try:
        for report in reports:
            root = ET.parse(report).getroot()
            if root.tag != "testsuite":
                raise ValueError("Expected Surefire testsuite")
            cases = root.findall("testcase")
            observed = dict(tests=len(cases), failures=sum(c.find("failure") is not None for c in cases),
                            errors=sum(c.find("error") is not None for c in cases),
                            skipped=sum(c.find("skipped") is not None for c in cases))
            for key, value in observed.items():
                if int(root.get(key, "0")) != value:
                    raise ValueError("Report counts disagree with test cases")
                counts[key] += value
            identities.extend(c.get("classname", "") + "#" + c.get("name", "") for c in cases)
    except (ET.ParseError, ValueError, OSError):
        return dict(status="invalid_report", counts=counts, test_ids=identities)
    if exit_code != 0: status = "execution_failed"
    elif not reports: status = "missing_reports"
    elif not counts["tests"]: status = "zero_tests"
    elif counts["failures"] or counts["errors"]: status = "tests_failed"
    elif counts["skipped"]: status = "skipped_tests"
    else: status = "passed"
    return dict(status=status, counts=counts, test_ids=identities)


def capture(command, cwd):
    try:
        p = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", timeout=30)
        return dict(exit_code=p.returncode, output=p.stdout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return dict(exit_code=None, output=str(exc))


def run(project, output, maven):
    project = Path(project).resolve()
    if not (project / "pom.xml").is_file():
        raise ValueError("Project must contain pom.xml")
    attempt = Path(output).resolve() / (time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8])
    attempt.mkdir(parents=True, exist_ok=False)
    reports = attempt / "reports"
    reports.mkdir()
    # A unique report directory prevents reuse of old target/surefire-reports output.
    command = [maven, "-B", "test", "-Dvesper.reportsDirectory=" + str(reports), "-DfailIfNoTests=true"]
    record = dict(project=str(project), command=command, started_at=time.time(), python=sys.version,
                  java=capture(["java", "-version"], project), maven=capture([maven, "-version"], project))
    try:
        with (attempt / "execution.log").open("w", encoding="utf-8") as log:
            p = subprocess.run(command, cwd=project, stdout=log, stderr=subprocess.STDOUT)
        record.update(classify(reports, p.returncode))
        record["exit_code"] = p.returncode
    except OSError as exc:
        record.update(status="environment_error", exit_code=None, error=str(exc))
    except KeyboardInterrupt:
        record.update(status="interrupted", exit_code=None)
    record["duration_seconds"] = round(time.time() - record["started_at"], 3)
    (attempt / "result.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(record["status"] + ": " + str(attempt / "result.json"))
    return 0 if record["status"] == "passed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["baseline"])
    parser.add_argument("--project", default="demo")
    parser.add_argument("--output", default=".vesper/runs")
    parser.add_argument("--maven", default=shutil.which("mvn") or "mvn")
    args = parser.parse_args()
    try:
        return run(args.project, args.output, args.maven)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
