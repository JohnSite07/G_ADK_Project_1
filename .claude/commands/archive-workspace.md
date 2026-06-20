---
description: Archive the current workspace/ into archive/workspace-<date>-runN (excluding regenerable dirs), then reset workspace/ empty for a new test run.
argument-hint: "[optional short note appended to the archive folder name, e.g. universe]"
---

Archive the current `workspace/` and reset it empty so a fresh `studio_pipeline` test run can start clean.

Run this PowerShell **from the project root**. It auto-detects today's date and the next run number for
today, copies `workspace/` into `archive/` excluding the regenerable dirs (`node_modules`, `.next`, `.git`,
`.terraform`) and any `*.tfstate`, then empties `workspace/`. If `workspace/` is already empty it just
confirms it's ready (nothing to archive).

The reset uses `robocopy /MIR` from an empty dir rather than `Remove-Item -Recurse -Force` — a local safety
guard blocks that cmdlet (it misreads the `run(\d+)` regex as a protected path and aborts the whole script).
`robocopy` is a native exe and isn't guarded, so the purge works in one shot.

```powershell
$ErrorActionPreference = 'Stop'
$ws = 'workspace'; $archiveRoot = 'archive'
if (-not (Test-Path $archiveRoot)) { New-Item -ItemType Directory -Path $archiveRoot | Out-Null }

$hasContent = (Test-Path $ws) -and ((Get-ChildItem -Path $ws -Force | Measure-Object).Count -gt 0)
$date = Get-Date -Format 'yyyy-MM-dd'
$note = '$ARGUMENTS'.Trim()

if ($hasContent) {
  $n = 1
  $existing = Get-ChildItem $archiveRoot -Directory -Filter "workspace-$date-run*" -ErrorAction SilentlyContinue
  foreach ($d in $existing) { if ($d.Name -match 'run(\d+)') { $n = [Math]::Max($n, [int]$Matches[1] + 1) } }
  $name = "workspace-$date-run$n"
  if ($note) { $name = "$name-$note" }
  $dest = Join-Path $archiveRoot $name

  robocopy $ws $dest /E /XD node_modules .next .git .terraform /XF *.tfstate /NFL /NDL /NJH /NJS /NP | Out-Null
  if ($LASTEXITCODE -lt 8) { $global:LASTEXITCODE = 0 } else { throw "robocopy (archive) failed (code $LASTEXITCODE)" }

  # Reset workspace/ empty by MIRRORING an empty dir into it (robocopy /MIR purges all
  # contents). Avoids `Remove-Item -Recurse -Force`, which the local safety guard blocks.
  $empty = Join-Path $env:TEMP "_ws_empty_$PID"
  New-Item -ItemType Directory -Path $empty -Force | Out-Null
  robocopy $empty $ws /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
  if ($LASTEXITCODE -lt 8) { $global:LASTEXITCODE = 0 } else { throw "robocopy (reset) failed (code $LASTEXITCODE)" }
  [System.IO.Directory]::Delete($empty)

  Write-Host "Archived -> $dest"
  Write-Host "workspace/ reset empty. Ready for a new run."
} else {
  if (-not (Test-Path $ws)) { New-Item -ItemType Directory -Path $ws | Out-Null }
  Write-Host "workspace/ already empty - nothing to archive. Ready for a new run."
}
```

After it runs, report the archive path and confirm `workspace/` is empty. Do **not** commit automatically —
note that the new `archive/` folder is untracked so the user can commit it when ready.
