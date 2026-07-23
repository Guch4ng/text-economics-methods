param(
    [string]$Lesson = "latest",
    [switch]$All
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LessonsDir = Join-Path $RepoDir "lessons"

function Get-LessonDirectories {
    $dirs = Get-ChildItem $LessonsDir -Directory |
        Where-Object { $_.Name -match "^\d{2}_" } |
        Sort-Object Name

    if ($All) {
        return $dirs
    }

    if ($Lesson -eq "latest") {
        return @($dirs | Select-Object -Last 1)
    }

    $lessonNumber = "{0:D2}" -f [int]$Lesson
    $matched = @($dirs | Where-Object { $_.Name -match "^$lessonNumber`_" })
    if ($matched.Count -eq 0) {
        throw "Cannot find lesson $Lesson under $LessonsDir"
    }
    return $matched
}

function Invoke-CheckedPython {
    param([string]$ScriptPath)
    Write-Host "Running: $ScriptPath"
    & python $ScriptPath
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: python $ScriptPath"
    }
}

$lessonDirs = @(Get-LessonDirectories)
if ($lessonDirs.Count -eq 0) {
    throw "No lesson directories found under $LessonsDir"
}

foreach ($lessonDir in $lessonDirs) {
    Write-Host ""
    Write-Host "== $($lessonDir.Name) =="
    $codeDir = Join-Path $lessonDir.FullName "code"
    $scripts = Get-ChildItem $codeDir -Filter "*.py" -File |
        Where-Object { $_.Name -match "^\d{2}_" } |
        Sort-Object Name
    if ($scripts.Count -eq 0) {
        throw "No numbered Python scripts found under $codeDir"
    }
    foreach ($script in $scripts) {
        Invoke-CheckedPython $script.FullName
    }
}

Write-Host ""
Write-Host "Done."
