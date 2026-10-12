"""Single-player rules simulation. Not live gameplay in either installed game."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from combat_golf.engine import Match
m=Match();m.add_player('solo')
for i in range(10):
    print(json.dumps(m.record_event({'event_id':f'kill-{i}','event':'mwiii_kill','player':'solo','victim':'enemy'})))
print(json.dumps(m.record_event({'event_id':'hole1','event':'golf_hole_completed','player':'solo','hole_id':'course1:1','par':4,'strokes':3})))
print(json.dumps(m.cast('solo','cruise_missile',now=100)))
print(json.dumps(m.cast('solo','juggernaut',now=100)))
print(json.dumps(m.record_event({'event_id':'hazard1','event':'golf_hazard_hit','player':'solo','hazard_id':'bumper'},now=105)))
print(json.dumps(m.state(now=105)))
