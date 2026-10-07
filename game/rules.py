"""Pure, seeded rules for the fictional underworld prototype."""
from dataclasses import dataclass
import random

@dataclass(frozen=True)
class Sentence:
    name: str
    cost: int
    damage: int
    base: int
    tag: str
    lines: tuple

CARDS = (
    Sentence('無限階段刑', 2, 9, 16, 'stairs', ('階段を登るほど遠ざかる', '階段の累積で得点増加')),
    Sentence('影流し刑', 2, 11, 12, 'shadow', ('影だけを異界へ送る', '影欠けを１つ付与')),
    Sentence('鏡審判刑', 3, 17, 24, 'mirror', ('鏡の中から判決が響く', '影欠け１つにつき＋18点')),
    Sentence('記憶没収刑', 0, 7, 9, 'memory', ('思い出を冥界の通貨に', '予算＋４／得点は控えめ')),
    Sentence('終わらぬ鐘刑', 2, 12, 18, 'bell', ('本人にだけ鳴り続ける鐘', '次の刑の得点が1.5倍')),
    Sentence('星落とし刑', 4, 26, 48, 'star', ('罪の星が魂へ降り注ぐ', '高得点だが生命力を消費')),
)

class Run:
    def __init__(self, seed):
        self.seed = seed
        self.rng = random.Random(seed)
        self.hp = 100
        self.money = 14
        self.score = 0
        self.turn = 0
        self.shadow = 0
        self.stairs = 0
        self.boost = False
        self.finished = False
        self.early = False
        self.final_bonus = 0
        self.history = []
        self.last = '刑を選び、８手番で判決を完成させる。'
        self.deal()

    def deal(self):
        # Memory is always offered: no deadlock when the budget is empty.
        self.offer = self.rng.sample([0, 1, 2, 4, 5], 2) + [3]
        self.rng.shuffle(self.offer)

    def preview(self, index):
        c = CARDS[index]
        points = c.base
        if c.tag == 'stairs':
            points += self.stairs * 9
        if c.tag == 'mirror':
            points += self.shadow * 18
        if self.boost:
            points = points * 3 // 2
        return points

    def choose(self, index):
        if self.finished or index not in self.offer:
            return False
        c = CARDS[index]
        if c.cost > self.money:
            self.last = '予算不足。この刑は選べません。'
            return False
        points = self.preview(index)
        self.money -= c.cost
        self.hp = max(0, self.hp - c.damage)
        self.score += points
        self.boost = c.tag == 'bell'
        if c.tag == 'stairs':
            self.stairs += 1
        elif c.tag == 'shadow':
            self.shadow += 1
        elif c.tag == 'memory':
            self.money += 4
        self.turn += 1
        self.history.append((c.name, points))
        self.last = f'{c.name}：＋{points}点'
        if self.hp == 0 or self.turn == 8:
            self.finished = True
            self.early = self.hp == 0 and self.turn < 8
            # The last, supernatural judgement is automatic after eight actions.
            self.final_bonus = 0 if self.early else 40 + self.hp // 2
            self.score += self.final_bonus
        else:
            self.deal()
        return True
