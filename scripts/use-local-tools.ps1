# Dot-source this file: . ./scripts/use-local-tools.ps1
$vesperRoot = Split-Path -Parent $PSScriptRoot
$vesperJdk = Join-Path $vesperRoot '.tools/jdk-17.0.20.1+1'
$vesperMaven = Join-Path $vesperRoot '.tools/apache-maven-3.9.9'
if (!(Test-Path (Join-Path $vesperJdk 'bin/java.exe')) -or !(Test-Path (Join-Path $vesperMaven 'bin/mvn.cmd'))) {
    throw 'Local Java or Maven is missing. See docs/SPRINT-1.md.'
}
$env:JAVA_HOME = $vesperJdk
$env:PATH = "$vesperJdk/bin;$vesperMaven/bin;$env:PATH"
$env:MAVEN_OPTS = "-Dmaven.repo.local=$vesperRoot/.tools/m2"
Write-Host 'Vesper Java and Maven are ready in this terminal.'
