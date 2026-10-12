# Combat Golf: Killstreak Chaos | Solo Edition

**Single-player only | source prototype v0.2.0-dev | MIT, community remixing permitted**

**NOT PLAYABLE YET.** The solo rules and local-only development bridge have automated tests, but neither game is hooked into the project. This cannot honestly be released on Melty as a one-click mod.

## Planned two-game mashup

The host is **Golf With Your Friends**. **Call of Duty: Modern Warfare III (2023)** is a required companion. A solo player earns points from real MWIII eliminations and golf achievements and spends them on solo golf power-ups. Both installed games will be required; none of their original files are included.

| Scoring event | Points |
|---|---:|
| MWIII elimination | +1 |
| Birdie | +2 |
| Eagle | +3 |
| Hole-in-one | +5 |

| Ability | Cost | Planned golf effect |
|---|---:|---|
| UAV / Tactical Vision | 2 | Aiming guidance for the next shot |
| Cruise Missile / Recovery Blast | 4 | Controlled repositioning impulse on **your own** golf ball |
| Juggernaut / Hazard Armor | 6 | Protect against one course-hazard hit during 30 seconds |

The rules engine handles points, cooldowns, replay protection, one-hit hazard shields and **one player per session**. In-game targeting, physics, aim guidance, MWIII event reading and real golf scoring are **not yet implemented**.

## Test the source without either game

Python 3.10+ required, standard library only.

```bash
python tools/preflight.py --stage core
python tools/generate.py
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/demo.py
```

On Windows PowerShell set `$env:PYTHONPATH = "src"` and run `python -m unittest discover -s tests -v`.

### Solo loopback developer simulation

```bash
# Terminal 1
PYTHONPATH=src python -m combat_golf.server --secret LOCAL_DEV_SECRET
# Terminal 2: only one player accepted
PYTHONPATH=src python -m combat_golf.dev_client --role player --player solo --secret LOCAL_DEV_SECRET
# Terminal 3: synthetic event adapter, NOT actual MWIII
PYTHONPATH=src python -m combat_golf.dev_client --role adapter --secret LOCAL_DEV_SECRET
```

Type `kill solo` four times in the adapter; type `cast cruise_missile` in the player terminal. You'll see a local recovery impulse *command*, not a real moved ball. This is a source test, **not game play**.

## Contents

- `sheets/` authoritative JSON game, scoring, power-up, system and unverified hook specifications
- `tools/generate.py` generated Python and C# rules
- `src/combat_golf/` solo point engine and single-player localhost development bridge
- `tests/` rule and one-player bridge tests
- `golf-plugin/` uncompiled Unity/BepInEx overlay scaffold (no real golf hooks)
- `melty.draft.json` illustrative solo layout, **not** valid/tested Melty packaging
- `docs/RELEASE_GATES.md` remaining prerequisites before public game release

**Mode:** single-player only. No opponent targeting, lobbies, multiplayer synchronization, or friend joining.

**License:** MIT for original Combat Golf code, remixes permitted. Original COD/GWYF content is not distributed. BepInEx is separate and not bundled.

**Actual release status:** game integration and compilation unverified; no gameplay capture, Melty install test, or one-click validation. Do not upload the source pre-release as a working mod.
