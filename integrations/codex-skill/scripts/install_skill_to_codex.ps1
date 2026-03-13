$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $projectRoot "..\..\..")).Path
$skillsRoot = Join-Path $env:USERPROFILE ".codex\skills"
$canonicalSkillDir = Join-Path $skillsRoot "zotero-wordflow"
$legacySkillDir = Join-Path $skillsRoot "zotero-word-citation-automation"

function Initialize-SkillLayout {
    param([string]$TargetSkillDir)

    New-Item -ItemType Directory -Force -Path $TargetSkillDir | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $TargetSkillDir "scripts") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $TargetSkillDir "references") | Out-Null
}

function Copy-SharedSkillFiles {
    param([string]$TargetSkillDir)

    Copy-Item (Join-Path $repoRoot "README.md") (Join-Path $TargetSkillDir "references\README.md.txt") -Force
    Copy-Item (Join-Path $repoRoot "docs\manifest-schema.md") (Join-Path $TargetSkillDir "references\manifest-schema.md") -Force
    Copy-Item (Join-Path $projectRoot "build_manifest_from_natural_text.py") (Join-Path $TargetSkillDir "scripts\build_manifest_from_natural_text.py") -Force
    Copy-Item (Join-Path $projectRoot "run_zotero_wordflow.py") (Join-Path $TargetSkillDir "scripts\run_zotero_wordflow.py") -Force
}

function Write-LegacyAliasSkill {
    param([string]$TargetSkillDir)

    $canonicalSkillPath = Join-Path $projectRoot "..\SKILL.md"
    $canonicalSkill = Get-Content $canonicalSkillPath -Raw
    $legacySkill = $canonicalSkill `
        -replace '(?m)^name:\s+zotero-wordflow$', 'name: zotero-word-citation-automation' `
        -replace '(?m)^description:\s+.*$', 'description: Compatibility alias for zotero-wordflow. Use this skill when an older thread still refers to the previous skill name but the workflow should remain the same.' `
        -replace '(?m)^# zotero-wordflow$', "# Zotero Word Citation Automation`r`n`r`nThis is a compatibility alias for the canonical ``zotero-wordflow`` skill."
    Set-Content -Path (Join-Path $TargetSkillDir "SKILL.md") -Value $legacySkill -Encoding UTF8
}

Initialize-SkillLayout -TargetSkillDir $canonicalSkillDir
Copy-Item (Join-Path $projectRoot "..\SKILL.md") (Join-Path $canonicalSkillDir "SKILL.md") -Force
Copy-SharedSkillFiles -TargetSkillDir $canonicalSkillDir

Initialize-SkillLayout -TargetSkillDir $legacySkillDir
Write-LegacyAliasSkill -TargetSkillDir $legacySkillDir
Copy-SharedSkillFiles -TargetSkillDir $legacySkillDir

Write-Host "Installed canonical skill to $canonicalSkillDir"
Write-Host "Installed compatibility alias to $legacySkillDir"
Write-Host "Make sure 'python -m pip install zotero-wordflow' has been run in the active Python environment."
