import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'game'))
from rules import Run, CARDS

class RulesTests(unittest.TestCase):
    def apply(self, r, index):
        r.offer = [index, 3, 0]
        r.money = 100
        self.assertTrue(r.choose(index))

    def test_shadow_mirror_and_bell(self):
        r = Run(5)
        self.apply(r, 1)
        self.assertEqual(r.preview(2), 42)
        self.apply(r, 4)
        self.assertEqual(r.preview(2), 63)
        self.apply(r, 2)
        self.assertFalse(r.boost)

    def test_early_finish_and_lock(self):
        r = Run(4)
        for _ in range(4):
            self.apply(r, 5)
        self.assertTrue(r.early)
        self.assertEqual(r.final_bonus, 0)
        score = r.score
        self.assertFalse(r.choose(3))
        self.assertEqual(score, r.score)

    def test_completion_and_seeded_runs(self):
        for seed in range(100):
            a, b = Run(seed), Run(seed)
            while not a.finished:
                self.assertEqual(a.offer, b.offer)
                self.assertIn(3, a.offer)
                a.choose(3)
                b.choose(3)
            self.assertEqual(a.score, b.score)
            self.assertEqual(a.turn, 8)
            self.assertGreater(a.final_bonus, 0)

    def test_unaffordable_and_preview_matches(self):
        r = Run(3)
        r.offer = [5, 3, 1]
        r.money = 0
        self.assertFalse(r.choose(5))
        self.assertEqual(r.turn, 0)
        expected = r.preview(3)
        r.choose(3)
        self.assertEqual(r.history[-1][1], expected)

if __name__ == '__main__':
    unittest.main()
