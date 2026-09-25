# Reproduce the Petclinic Baseline

These steps reproduce the Sprint 1 baseline against the exact pinned revision.

## Prerequisites

- Windows (PowerShell) or Linux/macOS (adjust `mvnw.cmd` → `./mvnw`)
- Git 2.x
- Java 17+ (or provision locally as below)
- Maven 3.9.x (or use the repo's wrapper with a compatible JAVA_HOME)
- Network access on first run (Maven Central dependency download, ~200MB)
- No Docker required (MySQL/Postgres tests are automatically skipped)

## Step 1 — Clone Petclinic outside the Vesper workspace

```powershell
git clone https://github.com/spring-projects/spring-petclinic C:\Users\Learner\Documents\spring-petclinic
```

## Step 2 — Pin the exact revision

```powershell
git -C C:\Users\Learner\Documents\spring-petclinic checkout 818c4136ea971c21674525f9053de0d9c7ad8cfe
git -C C:\Users\Learner\Documents\spring-petclinic tag vesper-baseline-sprint1-repro HEAD
```

Expected SHA: `818c4136ea971c21674525f9053de0d9c7ad8cfe`

## Step 3 — Verify Git status (must be clean)

```powershell
git -C C:\Users\Learner\Documents\spring-petclinic status
```

Expected: `nothing to commit, working tree clean`

## Step 4 — Provision Java 17 (if not already installed)

If Java 17+ is not on PATH, provision locally (same as Vesper Sprint 1):

```powershell
# From the Vesper project root
New-Item -ItemType Directory -Force -Path .tools
Invoke-WebRequest -Uri "https://aka.ms/download-jdk/microsoft-jdk-17.0.14-windows-x64.zip" -OutFile ".tools\jdk17.zip" -UseBasicParsing
Expand-Archive ".tools\jdk17.zip" -DestinationPath ".tools" -Force
Invoke-WebRequest -Uri "https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/apache-maven-3.9.9-bin.zip" -OutFile ".tools\maven.zip" -UseBasicParsing
Expand-Archive ".tools\maven.zip" -DestinationPath ".tools" -Force

$env:JAVA_HOME = (Get-ChildItem ".tools" -Directory | Where-Object {$_.Name -match "^jdk"} | Select-Object -First 1).FullName
$env:PATH = "$env:JAVA_HOME\bin;C:\Users\Learner\Documents\vesper\.tools\apache-maven-3.9.9\bin;$env:PATH"
$env:MAVEN_OPTS = '-Dmaven.repo.local="C:\Users\Learner\Documents\vesper\.tools\m2"'
```

## Step 5 — Verify tool versions

```powershell
java -version   # Expected: openjdk 17.0.14 (or any 17+)
mvn -version    # Expected: Apache Maven 3.9.9 (or wrapper version)
git --version
```

## Step 6 — Run the baseline

```powershell
# Record UTC start time
[System.DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")

# Run the documented CI command
& "C:\Users\Learner\Documents\spring-petclinic\mvnw.cmd" -B verify `
    --file "C:\Users\Learner\Documents\spring-petclinic\pom.xml" `
    2>&1 | Tee-Object -FilePath "build-repro.log"

Write-Host "Exit code: $LASTEXITCODE"
[System.DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
```

## Step 7 — Inspect results

Look for:

```
[INFO] Tests run: 74, Failures: 0, Errors: 0, Skipped: 2
[INFO] BUILD SUCCESS
```

The 2 skipped tests (`MySqlIntegrationTests`) are expected — they require Docker.  
`PostgresIntegrationTests` records 0 tests (Docker absent, `@BeforeAll` aborts before tests register).

## Step 8 — Verify Surefire reports

```powershell
Get-ChildItem "C:\Users\Learner\Documents\spring-petclinic\target\surefire-reports" -Filter "*.xml" | Measure-Object
```

Expected: 18 XML report files.

## Step 9 — Confirm source is unchanged

```powershell
git -C C:\Users\Learner\Documents\spring-petclinic status
git -C C:\Users\Learner\Documents\spring-petclinic diff HEAD
```

Both must show a clean tree with no diff.

---

## Expected totals

| Metric | Expected |
|---|---|
| Exit code | 0 |
| Tests run | 74 |
| Failures | 0 |
| Errors | 0 |
| Skipped | 2 |
| Passed | 72 |
| Report files | 18 XML |

---

## Notes

- `mvnw.cmd` is the Maven wrapper bundled in the Petclinic repo. It downloads the correct Maven version automatically if the `.mvn/wrapper` configuration requires it. Our run used an external Maven 3.9.9 pointed at via PATH.
- On Linux/macOS replace `mvnw.cmd` with `./mvnw` and adjust paths.
- On a first run, Maven downloads ~200MB of dependencies. Subsequent runs use the local cache.
- Docker is not required. Installing Docker will additionally exercise 2 MySQL tests and 2 Postgres tests.
