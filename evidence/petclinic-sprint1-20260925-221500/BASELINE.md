# Petclinic Baseline — Sprint 1

## Outcome

**COMPLETE — BUILD SUCCESS, 72 tests passed, 2 skipped (Docker unavailable)**

---

## Pinned Source Revision

| Field | Value |
|---|---|
| Repository | https://github.com/spring-projects/spring-petclinic |
| Commit SHA | `818c4136ea971c21674525f9053de0d9c7ad8cfe` |
| Branch | `main` |
| Baseline tag | `vesper-baseline-sprint1-20260925` (local tag in petclinic clone) |
| Commit message | docs: Fix formatting in Docker container instructions |
| Commit date | 2026-08-26 11:57:54 +0100 |
| Git status at clone | clean |
| Git status after build | clean — no tracked files changed |
| UTC start time | 2026-09-25T22:17:46Z |

---

## Source and Evidence Paths

| Path | Description |
|---|---|
| `C:\Users\Learner\Documents\spring-petclinic` | Petclinic source checkout (outside Vesper) |
| `C:\Users\Learner\Documents\vesper\evidence\petclinic-sprint1-20260925-221500` | Evidence directory |
| `attempts\attempt-01\build.log` | Complete Maven stdout+stderr (2867 lines) |
| `attempts\attempt-01\result.json` | Exit code, timing, test counts |
| `attempts\attempt-01\surefire-reports\` | 18 Surefire XML report files |
| `attempts\attempt-01\command-metadata.json` | Command and environment record |

---

## Environment

| Tool | Version | Source |
|---|---|---|
| Java | OpenJDK 17.0.14 (Microsoft-10800295) | `.tools/jdk-17.0.14+7` (local, non-system-wide) |
| Maven | 3.9.9 (8e8579a9e76f7d015ee5ec7bfcdc97d260186937) | `.tools/apache-maven-3.9.9` (local) |
| Maven wrapper | included in repo (`mvnw.cmd`) | Petclinic source |
| Git | 2.46.0.windows.1 | System |
| Python | 3.12.6 | System |
| OS | Windows 10 10.0.19045 amd64 | — |
| Shell | PowerShell 5.1 | — |
| Docker | Not installed | — |
| `JAVA_HOME` | `C:\Users\Learner\Documents\vesper\.tools\jdk-17.0.14+7` | Set for build session |
| `MAVEN_OPTS` | `-Dmaven.repo.local="C:\Users\Learner\Documents\vesper\.tools\m2"` | Set for build session |
| Local m2 repo | `C:\Users\Learner\Documents\vesper\.tools\m2` | Populated on first run |

Java and Maven are local distributions, not system-wide installs. Java 17 satisfies the project's `requireJavaVersion` rule. Docker is absent, which affects two test classes (see Skips).

---

## Build Tool and Configuration

- **Wrapper**: `mvnw.cmd` (from Petclinic's own Maven wrapper)
- **Config**: `pom.xml` at repo root — default configuration used, no profiles enabled
- **Spring Boot**: 4.1.0
- **Default database**: H2 in-memory (no external database required)
- **Java version required**: 17+ (enforced by `maven-enforcer-plugin`)

---

## Test Suites Covered

The `verify` lifecycle runs Maven Surefire for all test classes discovered under `src/test/java`.

| Suite | Class | Executed | Skipped | Reason |
|---|---|---|---|---|
| Unit / slice | `ValidatorTests` | 2 | 0 | — |
| Unit / slice | `OwnerControllerTests` | 15 | 0 | — |
| Unit / slice | `OwnerTests` | 2 | 0 | — |
| Unit / slice | `PetControllerTests` | 14 | 0 | — |
| Unit / slice | `PetTypeFormatterTests` | 3 | 0 | — |
| Unit / slice | `PetValidatorTests` | 7 | 0 | — |
| Unit / slice | `VisitControllerTests` | 4 | 0 | — |
| Integration (H2) | `PetClinicIntegrationTests` | 3 | 0 | — |
| Integration (H2) | `PetClinicConcurrencyTests` | 1 | 0 | — |
| Integration (H2) | `ClinicServiceTests` | 12 | 0 | — |
| Integration (H2) | `CrashControllerIntegrationTests` | 2 | 0 | — |
| Integration | `CrashControllerTests` | 1 | 0 | — |
| Integration | `I18nPropertiesSyncTest` | 2 | 0 | — |
| Integration | `WelcomeControllerTests` | 1 | 0 | — |
| Integration | `VetControllerTests` | 2 | 0 | — |
| Unit | `VetTests` | 1 | 0 | — |
| Integration (MySQL container) | `MySqlIntegrationTests` | 0 | **2** | `@Testcontainers(disabledWithoutDocker=true)` — Docker unavailable |
| Integration (Postgres compose) | `PostgresIntegrationTests` | **0** | 0 | `assumeTrue(DockerClientFactory.instance().isDockerAvailable())` aborts `@BeforeAll` — Docker unavailable. No test entries appear in Surefire XML. |

### Checks excluded from scope

The `verify` lifecycle does **not** run:
- `MysqlTestApplication` (has a `main()` method; not a test class)
- Checkstyle / nohttp-checkstyle (runs at `validate` phase — passes without failures in this run)
- Spring Java Format validation (runs at `validate` — passes)
- JaCoCo coverage report (generated but not checked for thresholds)
- Gradle build (separate workflow; not used here)

---

## Command Executed

```
.\\mvnw.cmd -B verify
```

Working directory: `C:\Users\Learner\Documents\spring-petclinic`

Source: documented CI command from `.github/workflows/maven-build.yml` (`./mvnw -B verify`), adapted to `.cmd` extension for Windows.

---

## Results

| Metric | Value |
|---|---|
| Exit code | **0** |
| Outcome | **BUILD SUCCESS** |
| UTC start | 2026-09-25T22:17:46Z |
| UTC end | 2026-09-25T22:20:07Z |
| Elapsed | ~141 seconds (~2 min 21 s) |
| Tests run | **74** |
| Failures | **0** |
| Errors | **0** |
| Skipped | **2** |
| Passed | **72** |

---

## Skips and Exclusions

| Class | Count | Reason | Effect on coverage |
|---|---|---|---|
| `MySqlIntegrationTests` | 2 tests skipped | `@Testcontainers(disabledWithoutDocker=true)` — Docker not available | MySQL integration path not exercised |
| `PostgresIntegrationTests` | 0 tests registered | `assumeTrue(isDockerAvailable())` in `@BeforeAll` — Docker not available | Postgres integration path not exercised |

These are expected and explicitly guarded by the project's own annotations. Installing Docker would exercise those 2–4 additional tests. They are not failures; they are a documented limitation of this environment.

---

## Failures and Errors

None. All 72 executed tests passed.

---

## Limitations

1. **Docker not installed**: `MySqlIntegrationTests` (2 tests) and `PostgresIntegrationTests` (tests) are skipped. The default H2 in-memory path is fully covered. The MySQL and Postgres integration paths require Docker (Testcontainers).
2. **First-run dependency download**: Dependencies were resolved from Maven Central on first run and cached locally. Subsequent runs will be faster and offline-capable within the local m2 cache.
3. **Local toolchain**: Java and Maven are local to the Vesper `.tools/` directory. They must be on PATH or JAVA_HOME must be set before re-running.

---

## Raw Evidence

- [`attempts/attempt-01/build.log`](attempts/attempt-01/build.log) — complete Maven output (2867 lines)
- [`attempts/attempt-01/result.json`](attempts/attempt-01/result.json) — structured result
- [`attempts/attempt-01/command-metadata.json`](attempts/attempt-01/command-metadata.json) — command and environment
- [`attempts/attempt-01/surefire-reports/`](attempts/attempt-01/surefire-reports/) — 18 Surefire XML files
