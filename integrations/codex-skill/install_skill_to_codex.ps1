$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$delegate = Join-Path $scriptDir 'scripts\install_skill_to_codex.ps1'
& powershell -ExecutionPolicy Bypass -File $delegate
