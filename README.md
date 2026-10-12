# Combat Golf: Killstreak Chaos

**GitHub-ready source repository | 0.1.0-dev | MIT, remixing permitted**

**STATUS: RULES/RELAY TESTED LOCALLY. THE GAME MOD IS SOURCE-ONLY, UNBUILT AND UNTESTED. NOT READY FOR MELTY PUBLICATION.**

Multiplayer chaos that combines *Golf With Your Friends* with *Call of Duty: Modern Warfare III (2023)*. The intended player experience is: play an actual GWYF round while MWIII runs as a required companion; gain killstreak points from real MWIII eliminations and exceptional golf shots; buy UAV, Cruise Missile or Juggernaut abilities to help yourself or sabotage friends. Melty should eventually install into and launch GWYF as the primary game and also require MWIII, with both games running together. **This behavior is a target design, not a currently working two-game integration.**

## Proposed rules

| Award | Points | Source |
|---|---:|---|
| MWIII elimination | +1 | MWIII (real event source NOT implemented) |
| Birdie | +2 | Golf (real hole callback NOT implemented) |
| Eagle or better, other than hole-in-one | +3 | Golf |
| Hole-in-one | +5 | Golf |

| Ability | Cost | Intended actual in-game effect |
|---|---:|---|
| UAV / Tactical Vision | 2 | Brief aiming guidance overlay |
| Cruise Missile / Ball Strike | 4 | Knock opponent ball with a physics impulse |
| Juggernaut / Armored Ball | 6 | Temporarily shield ball from one Cruise Missile |

Stats, costs, cooldowns and effect properties come from `sheets/*.json`. The Python scoring engine handles deductions, shields, cooldowns, replay protection, and scoring. It **does not** move an actual ball until game hooks are developed.

## Developer quick start (standard-library Python 3.10+)

```bash
python tools/preflight.py --stage core
python tools/generate.py
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/demo.py
```

On Windows PowerShell, replace the `PYTHONPATH=src ...` form with:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

### Local two-peer event relay simulation

```bash
# Terminal 1: choose a secret yourself (never commit or share it)
PYTHONPATH=src python -m combat_golf.server --secret LOCAL_DEV_SECRET
# Terminals 2 and 3: players
PYTHONPATH=src python -m combat_golf.dev_client --role player --player alpha --secret LOCAL_DEV_SECRET
PYTHONPATH=src python -m combat_golf.dev_client --role player --player bravo --secret LOCAL_DEV_SECRET
# Terminal 4: fake event injector for testing ONLY
PYTHONPATH=src python -m combat_golf.dev_client --role adapter --secret LOCAL_DEV_SECRET
```

From the fake injector, type `kill alpha` four times; from alpha, type `cast cruise_missile bravo`. Both players receive the same authoritative effect event. **No real MWIII activity was detected and no ball was moved**. Shared developer secret and local loopback mean this is not online multiplayer.

## Repository map

- `sheets/`: authoritative rule rows, game roles, subsystems and deliberately unverified hook checklist.
- `tools/generate.py`: generates matching Python rules and C# power definitions. Never hand-edit generated outputs.
- `tools/preflight.py`: validates cells, IDs, and references. `--stage release` deliberately fails until all hooks are verified.
- `src/combat_golf/`: tested local rule engine and development TCP relay; uses no third-party dependencies.
- `tests/`: scoring, power-ups, replay protection, shield defense, two-client relay tests.
- `golf-plugin/`: BepInEx/Unity C# **scaffold only**. It may draw a local development HUD if built for a compatible Unity Mono release but has **NO verified golf gameplay hooks**. Do not ship it as a working mod.
- `melty.draft.json`: **illustrative** roles, companion token, together intent, multiplayer placeholders, and blockers; **not a validated Melty recipe**. Deliberately named `.draft` rather than `melty.json` to avoid misleading one-click import.
- `docs/RELEASE_GATES.md`: exact work required before Melty one-click release.
- `docs/PROTOCOL.md`: current protocol and its security/functional limits.

## Build status and safety

- **Tested:** Python scoring engine and local two-player relay simulations.
- **Not tested:** Unity DLL compilation, MWIII kill detection, GWYF golf state, in-game physics/VFX, in-game multiplayer, install automation, Melty API checks, or screenshots.
- **Game files:** not included; do not copy official game models, audio, assets, multiplayer code, or community content into this repository. Both games are required in the planned finished mashup.
- **Melty:** no draft or release has been created on Melty. The game-info/schema checks could not be called in this environment, so do not treat the recipe as validated.
- **GitHub:** this archive can be uploaded to a new GitHub repository. No repo was created or pushed from this environment.

## What needs to happen next

See [release gates](docs/RELEASE_GATES.md). The game files and Melty connector must be accessible from the Windows PC that has both games; then add and verify real game hooks, build the C# mod, test it with two actual clients, and validate its one-click recipe.

## Credits and license

Original prototype source: Combat Golf contributors. Licensed under [MIT](LICENSE); modification and remixing are permitted. No Call of Duty or Golf With Your Friends game assets or trademarks are licensed by this repository. BepInEx is a separate third-party project with its own license and is *not bundled*.
