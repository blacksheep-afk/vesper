# Sprint 1: implementation and verification

Status: implementation verified locally. Bob review/run and session evidence remain pending. The earlier blocker history below is retained for transparency.

## Delivered

- `demo/requirements.md`: five explicit checkout rules using synthetic data.
- `demo/pom.xml`: Java 17-compatible standalone Maven/JUnit project.
- `demo/src/main/java/dev/vesper/Checkout.java`: integer-cent discount calculations, expiry handling, input validation and overflow-safe arithmetic.
- `demo/src/test/java/dev/vesper/CheckoutTest.java`: 11 JUnit test methods covering boundaries and invalid inputs. Not yet executed.
- `vesper/baseline.py`: runs Maven, saves combined logs, versions, test identities/counts, exit status and elapsed time in a unique attempt directory.
- `tests/test_baseline.py`: 10 passing Python checks for success, failed execution, failures in XML, missing/malformed/inconsistent reports, zero tests, skips, stale reports outside the fresh directory and absent executables.

## Actual verification on 25 September 2026

Runner tests: 10 passed outside the Codex filesystem sandbox. Initial sandbox attempts failed because temporary-directory access was denied, not because test assertions failed.

Actual demo baseline: environment_error; Maven is unavailable. Evidence: `.vesper/runs/20260925-201609-37898138/result.json`.

Java/Maven not found on PATH. Python's normal command points at a Windows Store alias; verification used Codex's bundled Python executable below. Maven's official 3.9.9 zip downloaded to `.tools/maven.zip`. The JDK download failed because C: ran out of space; the partial JDK zip was removed. About 159 MiB was free afterward. No global installation/settings changes were made.

## Resume

Free at least 1 GB on C: for the JDK, Maven and downloaded test dependencies, or choose another drive for the toolchain. Do not delete project/user data automatically. Then provision Java 17+ and Maven, confirm their versions and run the demo baseline. Network access is needed for the first Maven dependency resolution.

In this machine's PowerShell terminal, the existing Python runtime can run the checks:

```powershell
& 'C:/Users/Learner/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -m unittest discover -s tests -v
& 'C:/Users/Learner/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -m vesper baseline
```

Run from the Vesper root. On another machine use its installed Python 3 instead of that machine-specific path.

## Scope and limitations

This is a trusted-local-demo baseline checker, not the reproduction or repair workflow. It uses a fresh Surefire report directory for each run and rejects any skipped tests. It has no build timeout/process-tree management yet, does not sandbox build code, and does not yet compare expected test identities against a prior run. Those limits must not be presented as implemented protections. No intentionally seeded defect was added.

Implementation and current verification were done in Codex. Bob has not run or reviewed these files yet. Ask Bob to review and run the existing Sprint 1 implementation after the toolchain is ready, and save the real task-summary screenshot. Do not claim these are Bob-generated files or invent session evidence.

Sources for local tools: https://learn.microsoft.com/en-us/java/openjdk/download and https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/.


## Toolchain recovery

Space was freed by the user. Microsoft OpenJDK 17.0.20.1 and Apache Maven 3.9.9 are now extracted under `.tools/`. These are local tools, not global installs. Their dependencies are also cached locally. In a new PowerShell terminal at the project root, run:

```powershell
. ./scripts/use-local-tools.ps1
```

Then use the Python commands above. On other machines, install a compatible JDK/Maven or supply the same local distributions; ignored `.tools` files are not part of the submission repository.


## Final verified result

- Java suite: 11 tests, 0 failures, 0 errors, 0 skipped.
- Python runner checks: 10 passed.
- Baseline: passed, recorded in `.vesper/runs/20260925-202732-2f6b642b/result.json` with logs and fresh XML reports beside it.
- Corrected the demo POM to explicitly honor the `vesper.reportsDirectory` property. The first Maven build passed but the runner correctly rejected missing reports; that failed attempt is retained.
- The runner currently expects this demo POM report configuration; arbitrary Maven project support is not implemented.

Next in Bob: read these notes, review the implementation against demo/requirements.md, dot-source scripts/use-local-tools.ps1, run the baseline and runner tests with a working Python 3, and capture your actual task summary. Do not rebuild the existing foundation.
