## Inspect installed games before compiling Combat Golf Solo

This read-only Windows PowerShell script gathers installation paths, executable names, and Unity engine markers. It never copies game assets, changes files, or contacts a game service.

From the repository folder on the Windows machine with both games, run:

```powershell
powershell.exe -NoProfile -File .\tools\windows_install_probe.ps1
```

For a non-Steam installation supply `-GolfPath` and `-MwiiiPath` with the actual folders. A generic Steam entry named Call of Duty does not prove that Modern Warfare III is installed, and the script does not guess.

The output file is `combat-golf-install-report.json` in the current folder. Review it before sharing because local paths may reveal a Windows username.

**This is not a build or a playable Melty release.** Required work still includes verified MWIII elimination events, in-game Golf With Your Friends scoring/ball/hazard hooks, compiling and installing the actual plugin, a valid Melty installed-mode recipe, one-click testing, and genuine gameplay media. Do not mark those steps complete without evidence.
