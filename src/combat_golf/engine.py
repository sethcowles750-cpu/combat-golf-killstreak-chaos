"""Deterministic authoritative rules for Combat Golf.

Only trusted game adapters may call record_event. Nothing in this module
reads a real game process, hooks a golf ball or verifies player identity.
"""
from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from .generated_rules import POWERUPS, SCORING


class GameRuleError(ValueError):
    pass


@dataclass
class Player:
    id: str
    points: int = 0
    kills: int = 0
    holes: int = 0
    shields_until: float = 0.0
    last_cast: dict[str, float] = field(default_factory=dict)


class Match:
    def __init__(self):
        self.players: dict[str, Player] = {}
        self.event_ids: set[str] = set()
        self.completed_holes: set[tuple[str, str]] = set()
        self.event_sequence = 0

    def add_player(self, player_id: str) -> dict:
        if not isinstance(player_id, str) or not (1 <= len(player_id) <= 32) or not all(c.isalnum() or c in '_-' for c in player_id):
            raise GameRuleError('player ID must be 1-32 letters, digits, hyphens or underscores')
        if player_id not in self.players:
            self.players[player_id] = Player(id=player_id)
        return self.state()

    def state(self, now: float | None = None) -> dict:
        t = monotonic() if now is None else now
        return {
            'sequence': self.event_sequence,
            'players': {
                k: {'points': p.points, 'kills': p.kills, 'holes': p.holes,
                    'shielded': p.shields_until > t}
                for k, p in sorted(self.players.items())
            },
        }

    def record_event(self, event: dict[str, Any]) -> dict:
        """Trusted adapter supplies unique event_id, event, player and event-specific data."""
        if not isinstance(event, dict):
            raise GameRuleError('event must be an object')
        event_id, kind, player_id = event.get('event_id'), event.get('event'), event.get('player')
        if not isinstance(event_id, str) or not (1 <= len(event_id) <= 128):
            raise GameRuleError('missing/invalid unique event_id')
        if event_id in self.event_ids:
            raise GameRuleError('duplicate event_id')
        if player_id not in self.players:
            raise GameRuleError('unknown player')
        member = self.players[player_id]
        if kind == 'mwiii_kill':
            victim = event.get('victim')
            if victim == player_id:
                raise GameRuleError('self eliminations do not score')
            points = SCORING['mwiii_kill']['points']
            member.kills += 1
            label = 'mwiii_kill'
        elif kind == 'golf_hole_completed':
            strokes, par, hole_id = event.get('strokes'), event.get('par'), event.get('hole_id')
            if (not isinstance(strokes, int) or isinstance(strokes, bool) or strokes < 1 or
                not isinstance(par, int) or isinstance(par, bool) or par < 1 or par > 20 or
                not isinstance(hole_id, str) or not hole_id.strip() or len(hole_id) > 80):
                raise GameRuleError('hole requires valid strokes, par and hole_id')
            key = (player_id, hole_id)
            if key in self.completed_holes:
                raise GameRuleError('hole already scored for this player')
            self.completed_holes.add(key)
            member.holes += 1
            if strokes == 1:
                label = 'hole_in_one'
            elif strokes <= par - 2:
                label = 'eagle'
            elif strokes == par - 1:
                label = 'birdie'
            else:
                label = 'par_or_worse'
            points = SCORING[label]['points'] if label in SCORING else 0
        else:
            raise GameRuleError('unknown event (only mwiii_kill / golf_hole_completed)')
        self.event_ids.add(event_id)
        member.points += points
        self.event_sequence += 1
        return {'type': 'score', 'player': player_id, 'source_event': kind,
                'award': label, 'points_awarded': points, 'new_balance': member.points,
                'sequence': self.event_sequence}

    def cast(self, player_id: str, powerup_id: str, target_id: str | None = None,
             now: float | None = None) -> dict:
        t = monotonic() if now is None else now
        if player_id not in self.players:
            raise GameRuleError('unknown player')
        if powerup_id not in POWERUPS:
            raise GameRuleError('unknown powerup')
        rule = POWERUPS[powerup_id]
        player = self.players[player_id]
        if rule['target'] == 'self':
            if target_id not in (None, player_id):
                raise GameRuleError('powerup only targets self')
            target_id = player_id
        elif target_id not in self.players or target_id == player_id:
            raise GameRuleError('powerup requires a different, registered opponent')
        if player.points < rule['points']:
            raise GameRuleError('not enough streak points')
        previous = player.last_cast.get(powerup_id)
        if previous is not None and (t - previous) < rule['cooldown_seconds']:
            raise GameRuleError('powerup on cooldown')
        player.points -= rule['points']
        player.last_cast[powerup_id] = t
        target = self.players[target_id]
        blocked = powerup_id == 'cruise_missile' and target.shields_until > t
        if blocked:
            target.shields_until = 0.0  # one incoming strike consumes the shield
        elif powerup_id == 'juggernaut':
            target.shields_until = t + rule['duration_seconds']
        self.event_sequence += 1
        return {'type': 'powerup', 'player': player_id, 'target': target_id,
                'powerup': powerup_id, 'effect': rule['effect'],
                'duration_seconds': rule['duration_seconds'], 'strength': rule['strength'],
                'blocked': blocked, 'points_remaining': player.points,
                'sequence': self.event_sequence}
