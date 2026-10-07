"""Eight choices, one health bar, one visible shadow-to-mirror combo."""
from dataclasses import dataclass
import random

MAX_HP = 10
TURNS = 8
FINISH_BONUS = 20

@dataclass(frozen=True)
class Sentence:
    name: str
    damage: int
    base: int
    tag: str
    role: str
    lines: tuple
    flavor: str
    color: int

CARDS = (
    Sentence('影の刑', 1, 2, 'shadow', '次の鏡を強くする', ('鏡が強くなる影を１つためる', '影は１つまで。鏡を使うまで残る'), '影が、鏡の出番を待っている。', 12),
    Sentence('鏡の刑', 2, 3, 'mirror', '影があると８点', ('影があれば３点から８点に！', '使うと、ためた影がなくなる'), '鏡の向こうで、影がはじけた。', 12),
    Sentence('星の刑', 3, 7, 'star', '今すぐ大きな点', ('７点もらえる。元気は３へる', '元気が足りないと、ここで終わり'), '大きな星が、法廷に落ちる。', 8),
    Sentence('ひと休み', 0, 1, 'memory', '元気を２もどす', ('元気を２もどす。点は１点', '１回使う。元気は10まで'), 'ひと休みして、次の刑へ。', 11),
)

class Run:
    def __init__(self, seed):
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.hp = MAX_HP
        self.score = 0
        self.turn = 0
        self.shadow = 0
        self.finished = False
        self.early = False
        self.final_bonus = 0
        self.history = []
        self.last = '３枚から１枚選ぼう。'
        self.deal()

    def deal(self):
        self.offer = self.rng.sample([0, 1, 2], 2) + [3]
        self.rng.shuffle(self.offer)

    def damage(self, index):
        return CARDS[index].damage

    def preview(self, index):
        return CARDS[index].base + (5 if index == 1 and self.shadow else 0)

    def hp_after(self, index):
        return min(MAX_HP, self.hp + 2) if index == 3 else max(0, self.hp - self.damage(index))

    def choose(self, index):
        if self.finished or index not in self.offer:
            return False
        before = self.hp
        shadow_before = self.shadow
        points = self.preview(index)
        self.hp = self.hp_after(index)
        self.score += points
        if index == 0:
            self.shadow = 1
        elif index == 1:
            self.shadow = 0
        self.turn += 1
        self.history.append({'name': CARDS[index].name, 'card': index, 'points': points,
                             'hp_before': before, 'hp_after': self.hp,
                             'shadow_before': shadow_before, 'shadow_after': self.shadow})
        self.last = f'{CARDS[index].name}  ＋{points}点'
        if self.hp == 0 or self.turn == TURNS:
            self.finished = True
            self.early = self.hp == 0
            self.final_bonus = 0 if self.early else FINISH_BONUS
            self.score += self.final_bonus
        else:
            self.deal()
        return True
