# Petclinic Sprint 5 — Evidence Index

Run identifier: `petclinic-sprint5-run-001`  
Assembled: 2026-09-26 (Sprint 5 reporting task)  
Assembled by: Sprint 5 reporting (Bob session — current task)

This index catalogs every artifact that supports the Sprint 5 report. All
evidence is drawn from the Vesper git repository and its commit history.
Nothing has been fabricated, inferred from file timestamps, or substituted
from the checkout-demo sprints.

---

## 1. Source revision

| Field | Value |
|---|---|
| Target repository | https://github.com/spring-projects/spring-petclinic |
| Pinned commit SHA | `818c4136ea971c21674525f9053de0d9c7ad8cfe` |
| Commit message | "docs: Fix formatting in Docker container instructions" |
| Commit date | 2026-08-26 11:57:54 +0100 |
| Pinned by | Vesper Sprint 1, commit `67a5e86` in vesper repo (2026-09-26 00:51 CEST) |
| Git status at clone | clean |

---

## 2. Vesper repository revision

| Field | Value |
|---|---|
| Vesper repository | https://github.com/blacksheep-afk/vesper |
| Sprint 1 evidence commit | `67a5e86c2b11340b8da93099977d08c63969e538` (2026-09-26 00:51 CEST) |
| Sprint 4 evidence commit | `7aa3a03f230de3e8f758f3d9effd17861545d7d0` (2026-09-26 04:26 CEST) |
| Current HEAD (sprint5 branch) | `2b04367` |

---

## 3. Sprint 1 — Baseline

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint1-20260925-221500/` (git `67a5e86`) | ✅ Read from commit |
| Attempt | attempt-01 | — |
| Command | `.\\mvnw.cmd -B verify` | ✅ In `command-metadata.json` |
| Working directory | `C:\Users\Learner\Documents\spring-petclinic` | ✅ In metadata |
| UTC start | 2026-09-25T22:17:46Z | ✅ In BASELINE.md |
| UTC end | 2026-09-25T22:20:07Z | ✅ In BASELINE.md |
| Elapsed | ~141 seconds | ✅ Calculated |
| Exit code | 0 | ✅ In result.json |
| Tests run | 74 | ✅ In result.json |
| Failures | 0 | ✅ |
| Errors | 0 | ✅ |
| Skipped | 2 | ✅ (`MySqlIntegrationTests` — Docker unavailable) |
| Passed | 72 | ✅ |
| Surefire XML files | 18 | ✅ In BASELINE.md |
| Source hash check | clean tree before and after | ✅ In BASELINE.md |
| Claim supported | Passing non-empty baseline established | ✅ |

**Exclusions:** `MySqlIntegrationTests` (2 skips, `@Testcontainers(disabledWithoutDocker=true)`).
`PostgresIntegrationTests` recorded 0 tests — Docker absent, `@BeforeAll` aborted before
tests registered. Docker coverage is explicitly absent.

---

## 4. Sprint 2/3 — Investigation scope (supplied evidence)

| Field | Value | Verified |
|---|---|---|
| Scope selected | Pet record editing — `PetValidator.validate()` | ✅ REPRODUCE.md |
| Feature | Edit-pet form: type field for existing pets | ✅ |
| Suspected problem | `pet.isNew()` guard on type-required check excludes existing pets | ✅ In Sprint 4 README |
| Source location | `PetValidator.java` line 51 (original) | ✅ In candidate.patch |
| Schema reference | `db/h2/schema.sql` — `pets.type_id INTEGER NOT NULL` | ✅ In Sprint 4 README |
| Reproducer class | `VesperPetTypeReproductionTests` | ✅ In result.json files |
| Reproducer SHA-256 | `02a62f3ce7106a85e9d5239ee454b16f360e7fc48d5c6c72a73f607d425b6ddf` | ✅ In verification.json |
| Earlier pasted hash | `F406E70A...` (mismatched — noted as discrepancy in Sprint 4 README) | ⚠️ Discrepancy recorded |
| Developer confirmation of scope | Not separately recorded in the available evidence | ❌ Unverified |

**Note:** The Sprint 4 README (git `7aa3a03`) describes the expectation as
"an application-constraint interpretation, not a separately approved
stakeholder specification." Developer explicit sign-off on the requirement
interpretation is not separately recorded in the available artifacts.

Supplied Sprint 3 evidence location: `evidence/petclinic-sprint4-20260926/supplied-sprint3-evidence/`
(git `7aa3a03`).

---

## 5. Sprint 3/4 — Reproduction attempts

### Attempt 03 — First reproduction (`03-original-reproduction`)

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/runs/03-original-reproduction/` (git `7aa3a03`) | ✅ |
| Source SHA | `818c4136ea971c21674525f9053de0d9c7ad8cfe` | ✅ In result.json |
| Working directory | `…/petclinic-sprint4-work/original` | ✅ In result.json |
| Command | `mvn -B -DfailIfNoTests=true clean test -Dtest=VesperPetTypeReproductionTests -Dspring-javaformat.validate.skip=true` | ✅ |
| started_at (epoch) | 1790388882.554726 | ✅ (~2026-09-25T23:14:42 UTC, unconfirmed) |
| Exit code | 1 | ✅ |
| Duration | 52.511 s | ✅ |
| Tests | 2 / failures 2 / errors 0 / skipped 0 | ✅ |
| Failure 1 | `existingPetMustRejectMissingType` — `expected: <true> but was: <false>` | ✅ |
| Failure 2 | `editMustRejectClearedType` — `Status expected:<200> but was:<302>` | ✅ |
| Input hashes before/after | identical — source unchanged by run | ✅ |

### Attempt 04 — Repeat reproduction (`04-original-repeat`)

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/runs/04-original-repeat/` (git `7aa3a03`) | ✅ |
| Source SHA | `818c4136ea971c21674525f9053de0d9c7ad8cfe` | ✅ |
| Exit code | 1 | ✅ |
| Duration | 49.185 s | ✅ |
| Tests | 2 / failures 2 / errors 0 / skipped 0 | ✅ |
| Failures | same two test IDs and messages | ✅ |
| Input hashes before/after | identical | ✅ |

**Conclusion:** Failure is consistent across two independent runs. Both runs used
`-Dspring-javaformat.validate.skip=true` because the supplied test file fails the
upstream formatting gate. This flag disables formatting validation only; assertions
and test content are byte-for-byte unchanged. This is a documented setup constraint,
not a test weakening.

---

## 6. Sprint 4 — Candidate repair and verification

### Attempt 02 — Format-check failure (setup attempt)

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/runs/02-original-format-check/` | ✅ |
| Exit code | 1 | ✅ |
| Tests | 0 | ✅ |
| Classification | Setup/formatting failure — not bug evidence | ✅ In Sprint 4 README |

### Attempt 05 — First candidate setup failure (`05-candidate-reproducer`)

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/runs/05-candidate-reproducer/` | ✅ |
| Exit code | 128 | ✅ In result.json |
| Duration | None | ✅ |
| Classification | Git checkout-ownership check stopped execution before Maven ran | ✅ In Sprint 4 README |
| Retained | Yes — setup interruption, not application failure | ✅ |

### Attempt 05-retry — Candidate reproducer (`05-candidate-reproducer-retry`)

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/runs/05-candidate-reproducer-retry/` | ✅ |
| Source SHA | `818c4136ea971c21674525f9053de0d9c7ad8cfe` | ✅ |
| Exit code | 0 | ✅ |
| Duration | 52.118 s | ✅ |
| Tests | 2 / failures 0 / errors 0 / skipped 0 | ✅ |
| Both reproducer tests | passed | ✅ |
| Candidate PetValidator hash | `edb622720044bc85a4cbe3ab098dcca3db71c8a5f394e09efb9955f2a55d991d` | ✅ (differs from original `1cee4c2a…`) |
| Reproducer test hash | `02a62f3ce710…` (unchanged vs original run) | ✅ |

### Attempt 06 — Full regression (`06-candidate-regression`)

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/runs/06-candidate-regression/` | ✅ |
| Exit code | 0 | ✅ In result.json |
| Duration | 97.139 s | ✅ |
| Tests | 76 / failures 0 / errors 0 / skipped 2 | ✅ |
| Baseline identities preserved | Yes | ✅ In verification.json |
| Baseline counts | 74/0/0/2 (Sprint 1) → candidate 76/0/0/2 | ✅ |
| Extra 2 tests | Reproducer tests added | ✅ |

### Upstream baseline re-run for Sprint 4 (`01-upstream-baseline`)

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/runs/01-upstream-baseline/` | ✅ |
| Exit code | 0 | ✅ |
| Duration | 218.94 s | ✅ |
| Tests | 74 / failures 0 / errors 0 / skipped 2 | ✅ |

---

## 7. Candidate patch

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/candidate.patch` (git `7aa3a03`) | ✅ |
| Patch SHA-256 | `eaec842b2196923566d8857025533ffbc8ff395327012dba92ae4f320fe0a1f8` | ✅ In approval.json |
| Change | `if (pet.isNew() && pet.getType() == null)` → `if (pet.getType() == null)` | ✅ |
| Files changed | 1 production file — `PetValidator.java` | ✅ |
| Original snapshot | `evidence/petclinic-sprint4-20260926/original/PetValidator.java` | ✅ |
| Candidate snapshot | `evidence/petclinic-sprint4-20260926/candidate/PetValidator.java` | ✅ |

---

## 8. Human approval record

| Field | Value | Verified |
|---|---|---|
| Artifact path | `evidence/petclinic-sprint4-20260926/approval.json` (git `7aa3a03`) | ✅ |
| Decision | **approved** | ✅ |
| Recorded at UTC | 2026-09-26T02:26:32.113238+00:00 | ✅ |
| Source | "Explicit user approval in this task" | ✅ |
| User instruction | "I approve the fix. Commit and push the Sprint 4 patch and evidence to Vesper." | ✅ |
| Scope | Approval of candidate fix and publication — not an upstream Petclinic merge | ✅ |
| Integration performed | No | ✅ |

---

## 9. Bob session screenshots

| File | Participant | Bobcoins | Content verified |
|---|---|---|---|
| `black_sheep_Neelo_Nkhuna_sprint2_summary.png` | Neelo Nkhuna | 3.20 | ✅ Real Bob task summary — Task Id `44fc493d…`, workspace `vesper-1` |
| `black_sheep_sam_sprint3_investigation_summary.png` | Sam | 2.61 | ✅ Real Bob task summary — Task Id `fb2c9c38…`, workspace `vesper` |
| `bob_sessions_black_sheep_nyakalo_kgwale_task04_sprint4_summary.png` | Nyakalo Kgwale | 3.20 | ✅ Real Bob task summary — Task Id `6b14d3d9…`, workspace `vesper`, "Test sprint 4 if is working" |

**Screenshot assessment:** All three participants have supplied genuine Bob task-summary
screenshots showing a real Task Id, workspace, and Bobcoin consumption. The sprint plan
requires "real Bob task-summary screenshots from each participant involved" — satisfied.

---

## 10. Remaining limitations

| Item | Status |
|---|---|
| Sprint 2 developer sign-off on requirement interpretation | Not separately recorded; acknowledged limitation |
| Upstream novelty research | Not performed |
| Petclinic source checkout on current machine | Outside workspace: `C:\Users\Learner\Documents\spring-petclinic` |

---

## 11. Integrity check summary

| Check | Result |
|---|---|
| Baseline passed with nonzero tests | ✅ 72/74 passed |
| Failure is application failure (not setup/compile) | ✅ Test logic failure after successful build |
| Valid expected result present | ✅ Schema + `PetValidator.validate()` logic |
| Two independent reproduction attempts consistent | ✅ Attempts 03 and 04 both exit 1, same two failures |
| Candidate uses unchanged reproducer (same SHA) | ✅ `02a62f3c…` matches across original and candidate |
| Existing tests not weakened or removed | ✅ All 74 baseline identities preserved |
| Candidate regression results fresh and nonempty | ✅ 76 tests, exit 0 |
| Human approval separately recorded | ✅ `approval.json` (explicit user instruction) |
| Upstream Petclinic not modified | ✅ Integration explicitly not performed |
| Format flag affects formatting only | ✅ `-Dspring-javaformat.validate.skip=true` confirmed |
| Source hashes stable across each run | ✅ `inputs_unchanged: true` in every result.json |
