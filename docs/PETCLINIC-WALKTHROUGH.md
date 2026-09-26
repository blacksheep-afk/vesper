# Petclinic Investigation Walkthrough

A teammate can use this document to repeat the investigation, understand the
evidence, and verify its limitations.

**Status of these instructions:** steps 1–7 are based on verified evidence from
git history. Step 8 (report navigation) is based on the files created in Sprint 5.
No step has been re-executed as part of Sprint 5 reporting; all expected outcomes
are taken from verified records, not from a fresh replay.

---

## Definitions

| Placeholder | Meaning |
|---|---|
| `<PETCLINIC>` | Root of the Petclinic source checkout, e.g. `C:\Users\Learner\Documents\spring-petclinic` |
| `<WORK>` | Isolated work directory for Sprint 4 reproduction runs, e.g. `C:\sprint4-petclinic` |
| `<VESPER>` | Root of the Vesper repository, e.g. `C:\Users\Learner\Documents\vesper` |
| `<JAVA17_HOME>` | Path to a Java 17 JDK |
| `<MAVEN39>` | Path to Apache Maven 3.9.x `bin/` directory |

---

## Prerequisites

| Requirement | Verified version |
|---|---|
| Java 17+ | OpenJDK 17.0.14 (Sprint 1) or Temurin 17.0.20.1 (Sprint 4) |
| Apache Maven 3.9.9 | `8e8579a9e76f7d015ee5ec7bfcdc97d260186937` |
| Git 2.x | System |
| Python 3 | 3.14.6 (Sprint 4) / 3.12.6 (Sprint 1) |
| Network access | Required on first run for ~200 MB Maven dependency download |
| Docker | Not required (MySQL/Postgres tests auto-skip) |

Set environment for the session:
```powershell
$env:JAVA_HOME = "<JAVA17_HOME>"
$env:PATH = "$env:JAVA_HOME\bin;<MAVEN39>;$env:PATH"
$env:MAVEN_OPTS = '-Dmaven.repo.local="<WORK>\m2"'
```

---

## Step 1 — Obtain the exact Petclinic source revision

```powershell
git clone https://github.com/spring-projects/spring-petclinic <PETCLINIC>
git -C <PETCLINIC> checkout 818c4136ea971c21674525f9053de0d9c7ad8cfe
git -C <PETCLINIC> tag vesper-baseline-sprint1
git -C <PETCLINIC> status
```

Expected output of `status`: `nothing to commit, working tree clean`

**Record** the exact SHA before proceeding:
```powershell
git -C <PETCLINIC> rev-parse HEAD
# Expected: 818c4136ea971c21674525f9053de0d9c7ad8cfe
```

---

## Step 2 — Run the baseline (Sprint 1 reproduction)

```powershell
& "<PETCLINIC>\mvnw.cmd" -B verify --file "<PETCLINIC>\pom.xml"
```

Expected output (final lines):
```
Tests run: 74, Failures: 0, Errors: 0, Skipped: 2
BUILD SUCCESS
```

The 2 skipped tests (`MySqlIntegrationTests#findAll` and `#ownerDetails`) require
Docker, which is unavailable. `PostgresIntegrationTests` registers 0 tests for the
same reason. These are expected and do not block the investigation.

**Verify source unchanged:**
```powershell
git -C <PETCLINIC> status
# Expected: nothing to commit, working tree clean
```

**Recorded baseline result:** 74 run / 72 passed / 0 failed / 0 errors / 2 skipped.
Exit code 0. Duration ~141 s. (Source: BASELINE.md in git `67a5e86`.)

---

## Step 3 — Prepare isolated checkouts

Create separate `original` and `candidate` directories. Do not modify the shared
`<PETCLINIC>` checkout.

```powershell
# Create working area
New-Item -ItemType Directory -Force <WORK>

# Clone original
git clone <PETCLINIC> <WORK>\original
git -C <WORK>\original checkout 818c4136ea971c21674525f9053de0d9c7ad8cfe

# Clone candidate
git clone <PETCLINIC> <WORK>\candidate
git -C <WORK>\candidate checkout 818c4136ea971c21674525f9053de0d9c7ad8cfe
```

**Add the reproducer to both checkouts:**

The reproducer file is preserved in the Vesper repository at:
`evidence/petclinic-sprint4-20260926/supplied-sprint3-evidence/VesperPetTypeReproductionTests.java`
(git `7aa3a03`).

```powershell
# Extract from Vesper git history
git -C <VESPER> show 7aa3a03:evidence/petclinic-sprint4-20260926/supplied-sprint3-evidence/VesperPetTypeReproductionTests.java `
  > "<WORK>\VesperPetTypeReproductionTests.java"

# Copy to both checkouts (do not modify the file)
$dest = "src\test\java\org\springframework\samples\petclinic\owner"
Copy-Item "<WORK>\VesperPetTypeReproductionTests.java" "<WORK>\original\$dest\"
Copy-Item "<WORK>\VesperPetTypeReproductionTests.java" "<WORK>\candidate\$dest\"
```

**Verify reproducer SHA-256:**
```powershell
Get-FileHash "<WORK>\VesperPetTypeReproductionTests.java" -Algorithm SHA256
# Expected: 02A62F3CE7106A85E9D5239EE454B16F360E7FC48D5C6C72A73F607D425B6DDF
```

**Apply the candidate patch to `candidate` only:**

Extract the patch:
```powershell
git -C <VESPER> show 7aa3a03:evidence/petclinic-sprint4-20260926/candidate.patch `
  > "<WORK>\candidate.patch"
```

Apply:
```powershell
git -C "<WORK>\candidate" apply "<WORK>\candidate.patch"
git -C "<WORK>\candidate" diff HEAD
```

The diff should show exactly one production line changed in `PetValidator.java`:
```diff
-        if (pet.isNew() && pet.getType() == null) {
+        if (pet.getType() == null) {
```

---

## Step 4 — Run the baseline (no format flag)

Confirm the upstream baseline passes in the original checkout before adding the
reproducer interaction. (The Sprint 1 and Sprint 4 upstream baselines both passed;
this step documents the expected command.)

```powershell
& "<WORK>\original\mvnw.cmd" -B verify
```

Expected: 74 run, 0 failures, 0 errors, 2 skipped. Exit 0.

---

## Step 5 — Run the original reproduction twice

**Attempt 1:**
```powershell
<MAVEN39>\mvn.cmd -B -DfailIfNoTests=true clean test `
  -Dtest=VesperPetTypeReproductionTests `
  -Dspring-javaformat.validate.skip=true `
  --file "<WORK>\original\pom.xml"
```

**Attempt 2:** Run the identical command a second time without any changes.

**Expected output (both attempts):**
```
Tests run: 2, Failures: 2, Errors: 0, Skipped: 0
existingPetMustRejectMissingType ... FAILED
  expected: <true> but was: <false>
editMustRejectClearedType ... FAILED
  Status expected:<200> but was:<302>
BUILD FAILURE
```

Exit code: 1. Duration ~50 s per attempt.

**Verify source unchanged after each run:**
```powershell
git -C "<WORK>\original" status
# Expected: nothing to commit, working tree clean (tracked files)
```

**Recorded result:** Both attempts produced identical failures.
(Source: `03-original-reproduction/result.json` and `04-original-repeat/result.json`
in git `7aa3a03`.)

---

## Step 6 — Run the unchanged reproducer against the candidate

```powershell
<MAVEN39>\mvn.cmd -B -DfailIfNoTests=true clean test `
  -Dtest=VesperPetTypeReproductionTests `
  -Dspring-javaformat.validate.skip=true `
  --file "<WORK>\candidate\pom.xml"
```

**Expected output:**
```
Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

Exit code: 0. Duration ~52 s.

**Recorded result:** Both tests pass on the candidate.
(Source: `05-candidate-reproducer-retry/result.json` in git `7aa3a03`.)

Note: If you encounter exit code 128 (Git ownership check), run:
```powershell
git config --global --add safe.directory "<WORK>\candidate"
```
Then retry. Retain any failed attempt records separately.

---

## Step 7 — Run the full regression suite against the candidate

```powershell
<MAVEN39>\mvn.cmd -B clean verify `
  -Dspring-javaformat.validate.skip=true `
  -DfailIfNoTests=true `
  --file "<WORK>\candidate\pom.xml"
```

**Expected output:**
```
Tests run: 76, Failures: 0, Errors: 0, Skipped: 2
BUILD SUCCESS
```

Exit code: 0. Duration ~97 s.

The 76 tests = 74 original baseline tests + 2 reproducer tests (both now passing).
Skipped 2 = `MySqlIntegrationTests` (Docker unavailable) — same as baseline.

**Recorded result:** 76/0/0/2 on candidate.
(Source: `06-candidate-regression/result.json` in git `7aa3a03`.)

---

## Step 8 — Open the report, logs, diff, and evidence

All evidence lives in the Vesper git history. Use `git show <commit>:<path>` or
check out commit `7aa3a03` into a separate directory.

| What to open | Command / path |
|---|---|
| Sprint 5 report | `docs/PETCLINIC-SPRINT-5-REPORT.md` |
| Evidence index | `evidence/petclinic/sprint-5/run-001/EVIDENCE-INDEX.md` |
| Timing record | `evidence/petclinic/sprint-5/run-001/TIMING.md` |
| Sprint 4 full README | `git show 7aa3a03:evidence/petclinic-sprint4-20260926/README.md` |
| Candidate patch | `git show 7aa3a03:evidence/petclinic-sprint4-20260926/candidate.patch` |
| Approval record | `git show 7aa3a03:evidence/petclinic-sprint4-20260926/approval.json` |
| Verification summary | `git show 7aa3a03:evidence/petclinic-sprint4-20260926/runs/verification.json` |
| Repro attempt 1 result | `git show 7aa3a03:evidence/petclinic-sprint4-20260926/runs/03-original-reproduction/result.json` |
| Repro attempt 2 result | `git show 7aa3a03:evidence/petclinic-sprint4-20260926/runs/04-original-repeat/result.json` |
| Candidate reproducer result | `git show 7aa3a03:evidence/petclinic-sprint4-20260926/runs/05-candidate-reproducer-retry/result.json` |
| Candidate regression result | `git show 7aa3a03:evidence/petclinic-sprint4-20260926/runs/06-candidate-regression/result.json` |
| Sprint 1 baseline log | `git show 67a5e86:evidence/petclinic-sprint1-20260925-221500/attempts/attempt-01/build.log` |
| Bob session screenshots | `bob_sessions/petclinic_sprint_sessions/` |

---

## Step 9 — Review limitations and human decision

**Known limitations:**

1. Docker not installed: MySQL and Postgres integration tests are skipped in every run.
2. The reproducer uses `-Dspring-javaformat.validate.skip=true`. The candidate is
   not claimed to pass the unmodified default `verify` command with this test file.
3. The expectation is an application-constraint interpretation. No separate approved
   stakeholder specification exists.
4. Developer sign-off on the investigation scope interpretation is not separately
   recorded in the available artifacts.
5. Upstream novelty not researched.
6. The fix has not been integrated into upstream Petclinic.

**Human decision:**

The developer approved the candidate fix and its publication to a separate Vesper
branch on 2026-09-26T02:26:32 UTC. The approval record is at
`evidence/petclinic-sprint4-20260926/approval.json` (git `7aa3a03`).

Approval is distinct from integration. No integration into Petclinic or any other
repository has been performed.

**Outstanding screenshot gap:**

The `bob_sessions/petclinic_sprint_sessions/` folder contains two screenshots.
One (`black_sheep_Neelo_Nkhuna_sprint2_summary.png`) documents a checkout-demo
R3 reproduction task, not Petclinic work. The second
(`black_sheep_sam_sprint3_investigation_summarry.png`) shows a pasted-text task;
its Petclinic relevance is unconfirmed. A third screenshot
(`black_sheep_suprise_task01_petclinic_baseline.png`) exists in git `67a5e86` but
was not inspected as an image in this task.

Action required: confirm which screenshots document genuine Petclinic Bob sessions
and supply any missing ones before marking this sprint complete.

---

## Presentation sequence

```
Requirement
  H2 schema: pets.type_id INTEGER NOT NULL
  Create path: PetValidator checks type for new pets
  Edit path: PetValidator skips type check for existing pets
        ↓
Original observation
  POST edit-pet with blank type: HTTP 302 (success redirect)
  Expected: HTTP 200 with form field error
        ↓
Proposed fix
  Remove pet.isNew() guard from type-required check
  One line change in PetValidator.java
        ↓
Verification
  Reproducer: 2/2 pass on candidate (unchanged test bytes)
  Full regression: 76/0/0/2 on candidate (all baseline identities preserved)
        ↓
Human review
  Developer approved — 2026-09-26T02:26:32 UTC
  Integration deferred — approval covers Vesper branch publication only
```
