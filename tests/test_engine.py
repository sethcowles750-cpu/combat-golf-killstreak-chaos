import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from combat_golf.engine import Match, GameRuleError

class SoloRulesTests(unittest.TestCase):
    def setUp(self):
        self.m=Match()
        self.m.add_player('solo')
    def kills(self,n=1):
        for i in range(n):
            self.m.record_event({'event_id':f'kill-{i}', 'event':'mwiii_kill','player':'solo','victim':'enemy'})
    def hole(self,n,hole):
        return self.m.record_event({'event_id':f'h-{hole}', 'event':'golf_hole_completed','player':'solo','hole_id':hole,'strokes':n,'par':4})
    def hazard(self,hazard_id,at):
        return self.m.record_event({'event_id':f'hazard-{hazard_id}','event':'golf_hazard_hit','player':'solo','hazard_id':hazard_id},now=at)
    def test_cannot_add_second_player(self):
        with self.assertRaisesRegex(GameRuleError,'solo session'):self.m.add_player('bravo')
        self.assertEqual(len(self.m.players),1)
    def test_joint_scoring(self):
        self.kills(2)
        self.assertEqual(self.hole(3,'1')['points_awarded'],2)
        self.assertEqual(self.hole(2,'2')['points_awarded'],3)
        self.assertEqual(self.hole(1,'3')['points_awarded'],5)
        self.assertEqual(self.hole(4,'4')['points_awarded'],0)
        self.assertEqual(self.m.players['solo'].points,12)
    def test_recovery_targets_self(self):
        self.kills(4)
        result=self.m.cast('solo','cruise_missile',now=100)
        self.assertEqual(result['target'],'solo')
        self.assertEqual(result['effect'],'impulse')
        self.assertEqual(result['points_remaining'],0)
        with self.assertRaisesRegex(GameRuleError,'own ball'):
            self.m.cast('solo','cruise_missile','bravo',now=115)
    def test_juggernaut_blocks_first_course_hazard(self):
        self.kills(6)
        self.m.cast('solo','juggernaut',now=100)
        self.assertTrue(self.hazard('bumper1',105)['blocked'])
        self.assertFalse(self.hazard('bumper2',106)['blocked'])
    def test_expired_shield_does_not_block(self):
        self.kills(6)
        self.m.cast('solo','juggernaut',now=100)
        self.assertFalse(self.hazard('fan',131)['blocked'])
    def test_cooldown_and_balance(self):
        self.kills(6)
        self.m.cast('solo','uav',now=100)
        with self.assertRaisesRegex(GameRuleError,'cooldown'):self.m.cast('solo','uav',now=104)
        self.m.cast('solo','uav',now=105)
        self.assertEqual(self.m.players['solo'].points,2)
    def test_dedup_and_bad_data(self):
        self.kills(1)
        with self.assertRaisesRegex(GameRuleError,'duplicate'):self.kills(1)
        self.hole(3,'1')
        with self.assertRaisesRegex(GameRuleError,'already scored'):
            self.m.record_event({'event_id':'new','event':'golf_hole_completed','player':'solo','hole_id':'1','strokes':3,'par':4})
        with self.assertRaisesRegex(GameRuleError,'valid'):self.hole(True,'2')
        with self.assertRaisesRegex(GameRuleError,'hazard_id'):
            self.m.record_event({'event_id':'bad','event':'golf_hazard_hit','player':'solo'})

if __name__=='__main__':unittest.main()
