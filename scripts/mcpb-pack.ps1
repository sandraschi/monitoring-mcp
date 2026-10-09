#Requires -Version 5.1
<#
.SYNOPSIS
Fleet pack shim: delegate to the canonical fleet pack script.
The canonical implementation lives in mcp-central-docs so fixes reach the
whole fleet at once; this file must stay a thin shim (never vendor the logic).
#>
param([string]$RepoRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$FleetPack = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'mcp-central-docs\scripts\fleet-mcpb-pack.ps1'
if (-not (Test-Path $FleetPack)) { throw "Fleet pack script not found: $FleetPack" }
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $FleetPack -RepoRoot $RepoRoot
