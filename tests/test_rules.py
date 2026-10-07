import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'game'))
from rules import Run,CARDS

class RulesTests(unittest.TestCase):
    def apply(self,r,index):
        if r.upgrade_pending:r.upgrade('variety')
        r.offer=[index,3,0];r.money=100
        expected=r.preview(index)
        self.assertTrue(r.choose(index))
        self.assertEqual(r.history[-1]['points'],expected)

    def test_shadow_is_consumed_and_bell_is_one_action(self):
        r=Run(5)
        self.apply(r,1)
        self.assertEqual(r.preview(2),42)
        self.apply(r,4)
        self.assertEqual(r.preview(2),63)
        self.apply(r,2)
        self.assertFalse(r.boost)
        self.assertEqual(r.shadow,0)
        self.assertEqual(r.preview(2),24)

    def test_early_finish_and_lock(self):
        r=Run(4)
        for _ in range(4):self.apply(r,5)
        self.assertTrue(r.early)
        self.assertEqual(r.final_bonus+r.contract_bonus,0)
        score=r.score
        self.assertFalse(r.choose(3))
        self.assertEqual(score,r.score)

    def test_completion_and_seeded_runs(self):
        for seed in range(100):
            a,b=Run(seed,'star'),Run(seed,'star')
            self.assertEqual(a.contract,b.contract)
            while not a.finished:
                if a.upgrade_pending:
                    self.assertTrue(a.upgrade('memory'));self.assertTrue(b.upgrade('memory'))
                self.assertEqual(a.offer,b.offer)
                self.assertIn(3,a.offer)
                a.choose(3);b.choose(3)
            self.assertEqual(a.score,b.score)
            self.assertEqual(a.turn,8)
            self.assertGreater(a.final_bonus,0)
            self.assertFalse(a.early)

    def test_unaffordable_no_mutation(self):
        r=Run(3);r.offer=[5,3,1];r.money=0
        old=(r.hp,r.score,r.turn,r.offer[:])
        self.assertFalse(r.choose(5))
        self.assertEqual((r.hp,r.score,r.turn,r.offer),old)
        r.choose(3)
        self.assertEqual(r.money,4)

    def test_upgrade_pauses_execution(self):
        r=Run(4)
        for _ in range(4):self.apply(r,3)
        self.assertTrue(r.upgrade_pending)
        self.assertFalse(r.choose(3))
        self.assertFalse(r.upgrade('wrong'))
        self.assertTrue(r.upgrade('bell'))
        self.apply(r,4)
        self.assertEqual(r.breakdown(5)['mult'],2)

    def test_seal_effects_and_final_turn_zero_hp(self):
        r=Run(1,'star');self.assertEqual(r.damage(5),20)
        r=Run(1,'stairs');r.stairs=2;self.assertEqual(r.preview(0),42)
        r=Run(1,'shadow');self.assertEqual(r.preview(1),18)
        r.turn=7;r.hp=7;r.offer=[3]
        self.assertTrue(r.choose(3));self.assertFalse(r.early)
        self.assertEqual(r.final_bonus,40)

    def test_contract_bonus_is_counted_once(self):
        r=Run(1);r.contract=('test','variety',4,48,'test')
        for i in [0,1,2,3,3,3,3,3]:self.apply(r,i)
        self.assertEqual(r.contract_bonus,48)
        self.assertEqual(r.score,sum(h['points'] for h in r.history)+r.final_bonus+r.contract_bonus)
        score=r.score;self.assertFalse(r.choose(3));self.assertEqual(r.score,score)

if __name__=='__main__':unittest.main()
