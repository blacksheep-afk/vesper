# Petclinic Sprint 3 investigation

Source pinned to 818c4136ea971c21674525f9053de0d9c7ad8cfe. Isolated checkout: ../petclinic-investigation.

## Scope and expected behaviour

Pet editing only. The following expectations are inferred from the application constraints and existing tests; they are not a separate stakeholder-approved specification.

- Names must be nonblank and at most 30 characters (PetValidator and its tests).
- Birth date is required and cannot be in the future (PetValidator, PetController).
- Pet type must be present before persisting an edited pet: H2 schema defines pets.type_id INTEGER NOT NULL. New-pet validation already enforces this and the edit form exposes the same field.

## Candidate hypothesis

PetValidator checks missing type only when pet.isNew(). An existing pet with a cleared type may pass validation. Investigate with a validator regression and an HTTP controller test. Do not claim actual database failure without an integration test.

No defect was seeded. No production code has been changed. This is local investigation by Codex, not Bob session evidence. Prior upstream knowledge/novelty has not been checked, so do not market this as a newly discovered vulnerability.

## Baseline

The teammate's recorded full baseline is 72 passing tests, 2 skipped MySQL tests and no executed Postgres tests without Docker. Local scoped baseline is being run for PetControllerTests, PetValidatorTests and OwnerTests. This scoped run is not a replacement for full regression.
