# Dot-source this file from any directory: . ./scripts/use-local-tools.ps1
$vesperRoot = Split-Path -Parent $PSScriptRoot
$vesperJdk = Get-ChildItem -LiteralPath (Join-Path $vesperRoot '.tools') -Directory -Filter 'jdk*' -ErrorAction SilentlyContinue |
    Where-Object { Test-Path (Join-Path $_.FullName 'bin/java.exe') } | Select-Object -First 1
$vesperMaven = Join-Path $vesperRoot '.tools/apache-maven-3.9.9'
if (!$vesperJdk -or !(Test-Path (Join-Path $vesperMaven 'bin/mvn.cmd'))) {
    throw 'Local Java or Maven is missing. Use an installed Java 17+ and Maven, or provision .tools first. See docs/SPRINT-4.md.'
}
$env:JAVA_HOME = $vesperJdk.FullName
$env:PATH = "$($vesperJdk.FullName)/bin;$vesperMaven/bin;$env:PATH"
$env:MAVEN_OPTS = '-Dmaven.repo.local="' + "$vesperRoot/.tools/m2" + '"'
Write-Host 'Vesper Java and Maven are ready in this terminal.'
