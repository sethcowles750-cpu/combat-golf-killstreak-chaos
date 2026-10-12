<#
Combat Golf Solo read-only Windows installation probe.
No game files are copied or modified. No network requests.
#>
[CmdletBinding()]
param([string]$GolfPath = "", [string]$MwiiiPath = "", [string]$OutputPath = ".\combat-golf-install-report.json")
$ErrorActionPreference = "Stop"
function Inspect-Game([string]$Name, [string]$Folder) {
    if (-not $Folder -or -not (Test-Path -LiteralPath $Folder -PathType Container)) {
        return [ordered]@{ name=$Name; found=$false; path=$Folder }
    }
    $resolved = (Resolve-Path -LiteralPath $Folder).Path
    $dataDirs = @(Get-ChildItem -LiteralPath $resolved -Directory -Filter "*_Data" -ErrorAction SilentlyContinue)
    $assemblies = @()
    foreach ($dir in $dataDirs) {
        $assembly = Join-Path $dir.FullName "Managed\Assembly-CSharp.dll"
        if (Test-Path -LiteralPath $assembly -PathType Leaf) { $assemblies += $assembly }
    }
    return [ordered]@{
        name=$Name
        found=$true
        path=$resolved
        executables=@(Get-ChildItem -LiteralPath $resolved -Filter "*.exe" -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
        unity_data_folders=@($dataDirs | Select-Object -ExpandProperty Name)
        game_assemblies=$assemblies
        unity_player_present=(Test-Path -LiteralPath (Join-Path $resolved "UnityPlayer.dll"))
        il2cpp_gameassembly_present=(Test-Path -LiteralPath (Join-Path $resolved "GameAssembly.dll"))
        bepinex_core_present=(Test-Path -LiteralPath (Join-Path $resolved "BepInEx\core"))
    }
}
$libraryPaths = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$roots = @([Environment]::GetFolderPath("ProgramFilesX86"), [Environment]::GetFolderPath("ProgramFiles"))
foreach ($root in $roots) {
    if ($root) {
        $path = Join-Path $root "Steam\steamapps"
        if (Test-Path -LiteralPath $path -PathType Container) { [void]$libraryPaths.Add($path) }
    }
}
foreach ($drive in @(Get-PSDrive -PSProvider FileSystem)) {
    foreach ($segment in @("SteamLibrary\steamapps", "Steam\steamapps", "Games\SteamLibrary\steamapps")) {
        $path = Join-Path $drive.Root $segment
        if (Test-Path -LiteralPath $path -PathType Container) { [void]$libraryPaths.Add($path) }
    }
}
foreach ($lib in @($libraryPaths)) {
    $vdf = Join-Path $lib "libraryfolders.vdf"
    if (Test-Path -LiteralPath $vdf -PathType Leaf) {
        $vdfText = Get-Content -LiteralPath $vdf -Raw
        foreach ($m in [regex]::Matches($vdfText, '"path"\s+"([^"]+)"')) {
            $steamRoot = $m.Groups[1].Value.Replace("\\", "\")
            $apps = Join-Path $steamRoot "steamapps"
            if (Test-Path -LiteralPath $apps -PathType Container) { [void]$libraryPaths.Add($apps) }
        }
    }
}
$matches = @()
foreach ($lib in $libraryPaths) {
    foreach ($manifest in @(Get-ChildItem -LiteralPath $lib -Filter "appmanifest_*.acf" -File -ErrorAction SilentlyContinue)) {
        $raw = Get-Content -LiteralPath $manifest.FullName -Raw
        $name = [regex]::Match($raw, '"name"\s+"([^"]+)"').Groups[1].Value
        $installDir = [regex]::Match($raw, '"installdir"\s+"([^"]+)"').Groups[1].Value
        if ($name -notmatch '(?i)golf with your friends|call of duty|modern warfare' -or -not $installDir) { continue }
        $folder = Join-Path (Join-Path $lib "common") $installDir
        $matches += [ordered]@{ steam_name=$name; manifest=$manifest.Name; folder=$folder; exists=(Test-Path -LiteralPath $folder -PathType Container) }
    }
}
$golfCandidates = @($matches | Where-Object { $_.steam_name -match '(?i)golf with your friends' -and $_.exists })
if (-not $GolfPath -and $golfCandidates.Count -eq 1) { $GolfPath = $golfCandidates[0].folder }
# Generic Call of Duty manifests do not establish MWIII installation.
$report = [ordered]@{
    tool="Combat Golf Solo install probe"
    generated_utc=[DateTime]::UtcNow.ToString("o")
    scope="installation paths and engine indicators only; no game data copied"
    golf=(Inspect-Game "Golf With Your Friends" $GolfPath)
    mwiii=(Inspect-Game "Modern Warfare III (2023)" $MwiiiPath)
    steam_candidates=$matches
    mwiii_requires_manual_confirmation=(-not [bool]$MwiiiPath)
}
$dest = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputPath)
[IO.File]::WriteAllText($dest, ($report | ConvertTo-Json -Depth 10), (New-Object Text.UTF8Encoding($false)))
Write-Output "Saved read-only inspection report: $dest"
if (-not $report.golf.found) { Write-Warning "Golf With Your Friends not confirmed. Supply -GolfPath if necessary." }
if (-not $report.mwiii.found) { Write-Warning "MWIII not confirmed. Supply -MwiiiPath after identifying the actual installed game." }
