# Petclinic Sprint 4 — Candidate repair and verification

Status: **candidate verified with explicit exclusions; approved by the developer; not integrated into Petclinic**.

## Scope and behavior

Source: https://github.com/spring-projects/spring-petclinic at `818c4136ea971c21674525f9053de0d9c7ad8cfe`.

One supported defect: an existing pet with no type passes PetValidator. A POST with an empty type then returns a success redirect instead of displaying the form's type error. The candidate removes `pet.isNew()` from the type-required guard, so both new and existing pets require a type.

The expectation follows H2 schema `pets.type_id INTEGER NOT NULL`, existing create validation, and the shared edit form. It is an application-constraint interpretation, not a separately approved stakeholder specification. The select template has no explicit blank option; the controller test submits an empty-type POST directly. The repository is mocked: these tests do not demonstrate a database failure or real browser interaction. Upstream novelty has not been researched.

## Exact production patch

```diff
-        if (pet.isNew() && pet.getType() == null) {
+        if (pet.getType() == null) {
```

[Apply-ready patch](candidate.patch) · [Original validator](original/PetValidator.java) · [Candidate validator](candidate/PetValidator.java).

Only this production line changes. Existing tests, build files and dependencies are unchanged; the supplied reproducer is added identically to both isolated checkouts. Nothing has been integrated into an accepted Petclinic checkout or pushed to upstream Petclinic. The developer approved publication of the patch and evidence on a separate Vesper branch.

## Fresh execution evidence

| Attempt | Exit | Tests | Failures | Errors | Skips | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01-upstream-baseline | 0 | 74 | 0 | 0 | 2 | 218.94 | [log](runs/01-upstream-baseline/execution.log), [record](runs/01-upstream-baseline/result.json) |
| 02-original-format-check | 1 | 0 | 0 | 0 | 0 | 11.437 | [log](runs/02-original-format-check/execution.log), [record](runs/02-original-format-check/result.json) |
| 03-original-reproduction | 1 | 2 | 2 | 0 | 0 | 52.511 | [log](runs/03-original-reproduction/execution.log), [record](runs/03-original-reproduction/result.json) |
| 04-original-repeat | 1 | 2 | 2 | 0 | 0 | 49.185 | [log](runs/04-original-repeat/execution.log), [record](runs/04-original-repeat/result.json) |
| 05-candidate-reproducer | 128 | 0 | 0 | 0 | 0 | None | [log](runs/05-candidate-reproducer/execution.log), [record](runs/05-candidate-reproducer/result.json) |
| 05-candidate-reproducer-retry | 0 | 2 | 0 | 0 | 0 | 52.118 | [log](runs/05-candidate-reproducer-retry/execution.log), [record](runs/05-candidate-reproducer-retry/result.json) |
| 06-candidate-regression | 0 | 76 | 0 | 0 | 2 | 97.139 | [log](runs/06-candidate-regression/execution.log), [record](runs/06-candidate-regression/result.json) |

The original reproducer failed twice with the same two assertions: the validator should report a type error, and the controller should return HTTP 200 with a type field error instead of HTTP 302. Both unchanged tests pass on the candidate. Every baseline test identity and its pass/skip status is preserved in the candidate regression, with exactly two additional passing reproducer tests. Source hashes before and after each run confirm no build-time source edits. Test file hashes match across original and candidate.

## Exclusions and input discrepancy

The supplied test fails upstream formatting validation. This failed setup attempt is retained as `02-original-format-check`; it is not bug evidence. Subsequent original and candidate runs use `-Dspring-javaformat.validate.skip=true` to keep the supplied test byte-for-byte unchanged. This disables the formatting gate, not tests. Consequently the candidate is not claimed to pass an unmodified default `verify` command with this test file.

The first candidate setup attempt also stopped at Git's checkout-ownership check before Maven ran. Its record is retained with no elapsed-time claim. The retry scopes Git's safe.directory setting to the exact agent-created checkout for that process only, without changing global configuration. It is a setup interruption, not an application failure.

The upstream baseline runs the default clean verify build with no formatting override. Docker is unavailable: the following test identities are skipped in both baseline and candidate:

- `org.springframework.samples.petclinic.MySqlIntegrationTests#findAll`
- `org.springframework.samples.petclinic.MySqlIntegrationTests#ownerDetails`

Suites with no executed cases: `org.springframework.samples.petclinic.PostgresIntegrationTests`. Database-container coverage is not claimed.

Supplied reproducer SHA-256: `02a62f3ce7106a85e9d5239ee454b16f360e7fc48d5c6c72a73f607d425b6ddf`.

The earlier pasted report cited `F406E70A9C6493F47EB5889BA6F13E1004A0E7081383855F9F3D21D9CF12C721`, which does not match this ZIP file. This run verifies the exact file delivered in the ZIP, not the unprovided bytes behind that earlier hash. The original uploaded test and evidence are retained under [supplied-sprint3-evidence](supplied-sprint3-evidence/); no assertions or formatting were changed. The ZIP's evidence is the earlier Codex investigation and does not include the separate `bob-verification` directories described in the pasted message.

## Reproduction and review

Clone the pinned source twice into `original` and `candidate`. Use Java 17 and Maven 3.9.9. Run the default baseline before adding the reproducer. Copy the supplied Java test to `src/test/java/org/springframework/samples/petclinic/owner/` in both copies. Apply `candidate.patch` only in the candidate.

For each isolated checkout, run a clean targeted test using `mvn -B clean test -Dtest=VesperPetTypeReproductionTests -Dspring-javaformat.validate.skip=true -DfailIfNoTests=true`; repeat on the original. For the candidate's full regression run `mvn -B clean verify -Dspring-javaformat.validate.skip=true -DfailIfNoTests=true`. Expect two original assertion failures, two candidate passes, and the regression totals above. Each run's JSON records the exact command and environment actually used. Bundled Python scripts show the local capture and identity/hash checks; they expect sibling original/candidate checkouts and a local tools directory.

The developer approved this candidate and publication of its patch and evidence on a separate Vesper branch. [Approval record](approval.json) binds that decision to the exact patch hash. Petclinic integration and subsequent verification remain separate future actions. Historical run metadata retains its approval-pending state at execution time. Implementation and fresh verification here were performed in Codex; no new Bob screenshot or Bobcoin usage is claimed.

Petclinic source retains its Apache 2.0 notices; see [upstream license](UPSTREAM-LICENSE.txt).
