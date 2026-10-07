import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'game'))
from rules import Run, CARDS

class RulesTests(unittest.TestCase):
    def apply(self,r,index):
        r.offer=[index]
        expected=r.preview(index)
        hp=r.hp_after(index)
        self.assertTrue(r.choose(index))
        self.assertEqual(r.history[-1]['points'],expected)
        self.assertEqual(r.hp,hp)

    def test_shadow_caps_at_one_and_mirror_consumes(self):
        r=Run(5)
        self.apply(r,0);self.apply(r,0)
        self.assertEqual(r.shadow,1)
        self.assertEqual(r.preview(1),8)
        self.apply(r,1)
        self.assertEqual(r.shadow,0)
        self.assertEqual(r.preview(1),3)

    def test_shadow_survives_rest(self):
        r=Run(4)
        self.apply(r,0);self.apply(r,3)
        self.assertEqual(r.hp,10)
        self.assertEqual(r.preview(1),8)

    def test_rest_uses_a_turn_and_caps_health(self):
        r=Run(4)
        self.apply(r,3)
        self.assertEqual((r.turn,r.hp,r.score),(1,10,1))
        self.apply(r,2);self.apply(r,3)
        self.assertEqual(r.hp,9)

    def test_zero_health_ends_even_on_final_turn(self):
        for turn in (0,7):
            r=Run(4);r.turn=turn;r.hp=3
            self.apply(r,2)
            self.assertTrue(r.early)
            self.assertEqual(r.final_bonus,0)
            old=(r.score,r.hp,r.turn)
            self.assertFalse(r.choose(2))
            self.assertEqual((r.score,r.hp,r.turn),old)

    def test_completion_bonus_fixed_and_counted_once(self):
        for hp in (1,10):
            r=Run(4);r.hp=hp;r.turn=7
            self.apply(r,3)
            self.assertTrue(r.finished)
            self.assertFalse(r.early)
            self.assertEqual(r.final_bonus,20)
            self.assertEqual(r.score,21)
            self.assertFalse(r.choose(3))
            self.assertEqual(r.score,21)

    def test_replay_and_no_deadlock(self):
        for seed in range(100):
            a,b=Run(seed),Run(seed)
            while not a.finished:
                self.assertEqual(a.offer,b.offer)
                self.assertIn(3,a.offer)
                self.assertEqual(len(set(a.offer)),3)
                a.choose(3);b.choose(3)
            self.assertEqual((a.turn,a.score,b.score),(8,28,28))

    def test_unoffered_card_does_not_mutate(self):
        r=Run(4);r.offer=[0,1,3]
        old=(r.hp,r.score,r.turn,r.shadow,r.offer[:])
        self.assertFalse(r.choose(2))
        self.assertEqual((r.hp,r.score,r.turn,r.shadow,r.offer),old)

if __name__=='__main__':unittest.main()
