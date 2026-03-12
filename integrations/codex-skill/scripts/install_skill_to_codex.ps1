$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetSkillDir = Join-Path $env:USERPROFILE ".codex\skills\zotero-wordflow"

New-Item -ItemType Directory -Force -Path $targetSkillDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $targetSkillDir "scripts") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $targetSkillDir "references") | Out-Null

Copy-Item (Join-Path $projectRoot "..\SKILL.md") (Join-Path $targetSkillDir "SKILL.md") -Force
Copy-Item (Join-Path $projectRoot "..\..\README.md") (Join-Path $targetSkillDir "references\README.md.txt") -Force
Copy-Item (Join-Path $projectRoot "..\..\docs\manifest-schema.md") (Join-Path $targetSkillDir "references\manifest-schema.md") -Force
Copy-Item (Join-Path $projectRoot "build_manifest_from_natural_text.py") (Join-Path $targetSkillDir "scripts\build_manifest_from_natural_text.py") -Force
Copy-Item (Join-Path $projectRoot "run_zotero_wordflow.py") (Join-Path $targetSkillDir "scripts\run_zotero_wordflow.py") -Force

Write-Host "Installed skill to $targetSkillDir"
Write-Host "Make sure 'python -m pip install zotero-wordflow' has been run in the active Python environment."
