import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from combat_golf.engine import Match, GameRuleError


class CombatGolfRules(unittest.TestCase):
    def setUp(self):
        self.g=Match(); self.g.add_player('alpha'); self.g.add_player('bravo')

    def kill(self, n=1, player='alpha'):
        for i in range(n): self.g.record_event({'event_id':f'k-{player}-{i}', 'event':'mwiii_kill', 'player':player,'victim':'enemy'})

    def hole(self, strokes, par=4, hole='1', player='alpha'):
        return self.g.record_event({'event_id':f'h-{player}-{hole}', 'event':'golf_hole_completed', 'player':player,'hole_id':hole,'strokes':strokes,'par':par})

    def test_joint_scoring(self):
        self.kill(2)
        self.assertEqual(self.hole(3)['points_awarded'], 2)
        self.assertEqual(self.g.players['alpha'].points, 4)
        self.assertEqual(self.hole(2,hole='2')['points_awarded'], 3)
        self.assertEqual(self.hole(1,hole='3')['points_awarded'], 5)
        self.assertEqual(self.hole(4,hole='4')['points_awarded'], 0)
        self.assertEqual(self.g.players['alpha'].points, 12)

    def test_spend_points_and_powerup(self):
        self.kill(4)
        x = self.g.cast('alpha','cruise_missile','bravo',now=100)
        self.assertEqual(x['effect'],'impulse')
        self.assertEqual(x['points_remaining'],0)
        self.assertFalse(x['blocked'])

    def test_juggernaut_consumes_shield(self):
        self.kill(6)
        self.g.cast('alpha','juggernaut',now=100)
        self.kill(4,'bravo')
        r=self.g.cast('bravo','cruise_missile','alpha',now=105)
        self.assertTrue(r['blocked'])
        self.assertFalse(self.g.state(now=105)['players']['alpha']['shielded'])

    def test_cooldown(self):
        self.kill(10)
        self.g.cast('alpha','uav',now=100)
        with self.assertRaisesRegex(GameRuleError,'cooldown'): self.g.cast('alpha','uav',now=104)
        self.g.cast('alpha','uav',now=105)

    def test_event_dedup(self):
        self.kill()
        with self.assertRaisesRegex(GameRuleError,'duplicate'): self.kill()
        self.hole(3)
        with self.assertRaisesRegex(GameRuleError,'already scored'): self.g.record_event({'event_id':'unique','event':'golf_hole_completed','player':'alpha','hole_id':'1','strokes':3,'par':4})

    def test_invalid_inputs(self):
        self.kill(4)
        with self.assertRaisesRegex(GameRuleError,'different'): self.g.cast('alpha','cruise_missile','alpha')
        with self.assertRaisesRegex(GameRuleError,'valid'): self.hole(True)
        with self.assertRaisesRegex(GameRuleError,'not enough'): self.g.cast('bravo','uav')
        self.assertEqual(self.g.players['alpha'].points,4)

if __name__ == '__main__':unittest.main()
