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

    $legacySkill = @'
---
name: zotero-word-citation-automation
description: Compatibility alias for zotero-wordflow. Use this skill when an older thread still refers to the previous skill name but the workflow should remain the same.
version: 0.1.2
---

# Zotero Word Citation Automation

This is a compatibility alias for the canonical `zotero-wordflow` skill.

Use the same workflow:

1. Prefer `python -m zotero_wordflow from-text ...`
2. If debugging manifest content is necessary, run:
   - `scripts/build_manifest_from_natural_text.py`
3. Then run:
   - `scripts/run_zotero_wordflow.py`
4. Return the generated `.docx` path and remind the user to run `Refresh` and `Add/Edit Bibliography` inside Word.

## Robustness notes

- UTF-8 BOM input files should be accepted automatically.
- Grouped citations should be emitted as one Zotero field; avoid hand-editing manifests into multiple one-item fields inside the same bracket group.
- Simple narrative citations such as `Smith (2020)` are supported.
'@
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
