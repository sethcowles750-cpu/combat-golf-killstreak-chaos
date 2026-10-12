"""Preflight sheet rows/columns. Release stage intentionally fails until verified.

Usage: python tools/preflight.py --stage core|release
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    'powerups.json': ['id','name','points','target','effect','duration_seconds','strength','source_game','cooldown_seconds','description'],
    'scoring.json': ['id','event','source_game','condition','points'],
    'systems.json': ['id','sheet','component','verified'],
    'hooks.json': ['id','game','event','implementation','verified'],
    'games.json': ['id','name','melty_slug','role','install_verified','engine','in_game_hook_verified'],
}


def check(stage='core'):
    problems = []
    rows = {}
    for filename, columns in REQUIRED.items():
        path = ROOT / 'sheets' / filename
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            problems.append(f'{filename}: {exc}')
            continue
        if not isinstance(data, list) or not data:
            problems.append(f'{filename}: expected nonempty list')
            continue
        rows[filename] = data
        seen = set()
        for i, row in enumerate(data, 1):
            for col in columns:
                if col not in row or row[col] is None or row[col] == '':
                    problems.append(f'{filename} row {i} missing {col}')
            key = row.get('id')
            if key in seen:
                problems.append(f'{filename} duplicate id {key}')
            seen.add(key)
    if len(rows) != len(REQUIRED):
        return problems
    games = {r['id'] for r in rows['games.json']}
    events = {r['event'] for r in rows['scoring.json']}
    effects = {'guidance_overlay', 'impulse', 'shield'}
    targets = {'self'}
    for r in rows['scoring.json']:
        if r['source_game'] not in games: problems.append(f"score {r['id']}: unknown game")
        if not isinstance(r['points'], int) or r['points'] <= 0: problems.append(f"score {r['id']}: invalid points")
    for r in rows['powerups.json']:
        if r['source_game'] not in games: problems.append(f"power {r['id']}: unknown source game")
        if r['target'] not in targets or r['effect'] not in effects: problems.append(f"power {r['id']}: invalid effect/target")
        if not isinstance(r['points'], int) or r['points'] <= 0: problems.append(f"power {r['id']}: invalid cost")
        if r['duration_seconds'] < 0 or r['strength'] <= 0 or r['cooldown_seconds'] < 0: problems.append(f"power {r['id']}: invalid numeric property")
    for r in rows['systems.json']:
        if r['sheet'] not in REQUIRED: problems.append(f"system {r['id']}: missing sheet reference")
        component = r['component']
        component_path = ROOT / ('src/combat_golf/' + component.removeprefix('combat_golf.').replace('.', '/') + '.py' if component.startswith('combat_golf.') else component)
        if not component_path.exists():
            problems.append(f"system {r['id']}: missing component {r['component']}")
    for r in rows['hooks.json']:
        if r['game'] != 'both' and r['game'] not in games: problems.append(f"hook {r['id']}: unknown game")
        if r['event'] in ('mwiii_kill','golf_hole_completed') and r['event'] not in events:
            problems.append(f"hook {r['id']}: unresolved scoring event")
    primary = [r for r in rows['games.json'] if r['role'] == 'primary']
    if len(primary) != 1: problems.append('games: need exactly one primary')
    if stage == 'release':
        for r in rows['hooks.json']:
            if r['verified'] is not True: problems.append(f"BLOCKED release hook {r['id']}: unverified")
        for r in rows['games.json']:
            if r['install_verified'] is not True or r['in_game_hook_verified'] is not True:
                problems.append(f"BLOCKED release game {r['id']}: installation/game hook unverified")
        for r in rows['systems.json']:
            if str(r['verified']).startswith('pending'): problems.append(f"BLOCKED release system {r['id']}: pending test")
    return problems


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--stage', choices=('core','release'), default='core')
    a = p.parse_args()
    issues = check(a.stage)
    if issues:
        print('\n'.join('FAIL ' + item for item in issues))
        sys.exit(1)
    print(f'PASS: {a.stage} sheet cells and cross references checked')
