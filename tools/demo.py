"""Deterministic rules demo. This does NOT play either game."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from combat_golf.engine import Match

m=Match()
m.add_player('alice');m.add_player('bob')
for idx in range(7):
    print(json.dumps(m.record_event({'event_id':f'example-kill-{idx}', 'event':'mwiii_kill', 'player':'alice','victim':'enemy'})))
print(json.dumps(m.record_event({'event_id':'golf-a-1','event':'golf_hole_completed','player':'alice','hole_id':'course1:1','par':4,'strokes':3})))
print(json.dumps(m.cast('alice','juggernaut',now=100)))
print(json.dumps(m.record_event({'event_id':'golf-b-1','event':'golf_hole_completed','player':'bob','hole_id':'course1:1','par':4,'strokes':1})))
print(json.dumps(m.cast('bob','cruise_missile','alice',now=105)))
print(json.dumps(m.state(now=105)))
