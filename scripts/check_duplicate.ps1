# Usage: .\check_duplicate.ps1 -ProjectRoot "C:\path\to\MAXBOT"
# Prints ProcessId to stdout if a python.exe is already running this bot; else prints nothing.
# Exit 0 always (batch reads stdout).

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot
)

$root = $ProjectRoot.TrimEnd('\')
if ([string]::IsNullOrWhiteSpace($root)) { return }

$procs = Get-CimInstance -ClassName Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue
foreach ($p in $procs) {
    $cmd = $p.CommandLine
    if (-not $cmd) { continue }
    if ($cmd.IndexOf($root, [StringComparison]::OrdinalIgnoreCase) -lt 0) { continue }
    if ($cmd -notmatch 'main\.py') { continue }
    Write-Output $p.ProcessId
    return
}
