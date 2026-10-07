"""Deterministic rules. All sentences and suffering values are fictional."""
from dataclasses import dataclass
import random

@dataclass(frozen=True)
class Sentence:
    name: str
    cost: int
    damage: int
    base: int
    tag: str
    role: str
    lines: tuple
    flavor: str
    color: int

CARDS = (
    Sentence('無限階段刑', 2, 9, 16, 'stairs', '累積', ('階段の累積ごとに＋９点', '累積はこの挑戦中ずっと有効'), '出口は、登った数だけ遠ざかる。', 11),
    Sentence('影流し刑', 2, 11, 12, 'shadow', '仕込み', ('影欠けを１つ付与', '鏡審判で影を消費して加点'), '影だけが、先に川を渡った。', 12),
    Sentence('鏡審判刑', 3, 17, 24, 'mirror', '連携', ('影欠け１つにつき＋18点', '執行後に影欠けを全て消費'), '鏡の向こうで、判決が揃う。', 12),
    Sentence('記憶没収刑', 0, 7, 9, 'memory', '補給', ('予算を４回復', '資金を整える低負荷の刑'), '思い出の値札は、白紙だった。', 10),
    Sentence('終わらぬ鐘刑', 2, 12, 18, 'bell', '倍率', ('次の刑の得点が1.5倍', '記憶没収も倍率を消費する'), '最後の一音だけが、来ない。', 9),
    Sentence('星落とし刑', 4, 26, 48, 'star', '高得点', ('大きな得点と大きな消耗', '鐘の直後なら倍率で加点'), '空から、名前のない星が落ちる。', 8),
)

@dataclass(frozen=True)
class Seal:
    name: str
    key: str
    lines: tuple
    color: int

SEALS = (
    Seal('影渡りの印', 'shadow', ('影流しの基礎得点＋６', '影から鏡へつなぐ構成'), 12),
    Seal('巡礼の印', 'stairs', ('階段の累積加点＋４', '繰り返すほど得点が伸びる'), 11),
    Seal('星守りの印', 'star', ('星落としの消耗－６', '高得点の刑を扱いやすく'), 8),
    Seal('残響の印', 'bell', ('鐘の次の刑が２倍', '1.5倍から２倍に強化'), 9),
    Seal('徴収の印', 'memory', ('記憶没収の予算回復＋２', '後半の高額な刑を支える'), 10),
    Seal('記録官の印', 'variety', ('未使用の刑は＋８点', 'まだ使っていない刑を試す'), 6),
)

CONTRACTS = (
    ('鏡の判決', 'mirror', 2, 48, '鏡審判を２回執行'),
    ('終わらぬ巡礼', 'stairs', 3, 48, '無限階段を３回執行'),
    ('多彩な裁き', 'variety', 4, 48, '異なる刑を４種類執行'),
)

class Run:
    def __init__(self, seed, seal='plain'):
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
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
        self.contract_bonus = 0
        self.seals = {seal} if seal != 'plain' else set()
        self.upgrade_pending = False
        self.contract = CONTRACTS[random.Random(self.seed+9000).randrange(len(CONTRACTS))]
        self.counts = {c.tag: 0 for c in CARDS}
        self.history = []
        self.last = '執行する刑を選んでください。'
        self.deal()

    def deal(self):
        self.offer = self.rng.sample([0, 1, 2, 4, 5], 2) + [3]
        self.rng.shuffle(self.offer)

    def damage(self, index):
        c = CARDS[index]
        return c.damage - (6 if c.tag == 'star' and 'star' in self.seals else 0)

    def breakdown(self, index):
        c = CARDS[index]
        base = c.base + (6 if c.tag == 'shadow' and 'shadow' in self.seals else 0)
        combo = 0
        if c.tag == 'stairs':
            combo = self.stairs * (13 if 'stairs' in self.seals else 9)
        elif c.tag == 'mirror':
            combo = self.shadow * 18
        novelty = 8 if 'variety' in self.seals and self.counts[c.tag] == 0 else 0
        mult = (2 if 'bell' in self.seals else 1.5) if self.boost else 1
        points = int((base + combo + novelty) * mult)
        return {'base': base, 'combo': combo, 'novelty': novelty, 'mult': mult, 'points': points}

    def preview(self, index):
        return self.breakdown(index)['points']

    def contract_progress(self):
        _, tag, target, _, _ = self.contract
        progress = sum(v > 0 for v in self.counts.values()) if tag == 'variety' else self.counts[tag]
        return min(progress, target), target

    def upgrade(self, key):
        if not self.upgrade_pending or key not in ('bell', 'memory', 'variety'):
            return False
        self.seals.add(key)
        self.upgrade_pending = False
        return True

    def choose(self, index):
        if self.finished or self.upgrade_pending or index not in self.offer:
            return False
        c = CARDS[index]
        if c.cost > self.money:
            self.last = '予算不足。記憶没収で予算を補給できます。'
            return False
        details = self.breakdown(index)
        before = self.hp
        self.money -= c.cost
        self.hp = max(0, self.hp - self.damage(index))
        self.score += details['points']
        self.boost = c.tag == 'bell'
        if c.tag == 'stairs':
            self.stairs += 1
        elif c.tag == 'shadow':
            self.shadow += 1
        elif c.tag == 'mirror':
            self.shadow = 0
        elif c.tag == 'memory':
            self.money += 6 if 'memory' in self.seals else 4
        self.turn += 1
        self.counts[c.tag] += 1
        self.history.append({'name': c.name, 'card': index, 'points': details['points'], 'hp_before': before, 'hp_after': self.hp, **details})
        self.last = f'{c.name}  ＋{details["points"]}点'
        if self.hp == 0 or self.turn == 8:
            self.finished = True
            self.early = self.hp == 0 and self.turn < 8
            self.final_bonus = 0 if self.early else 40 + self.hp // 2
            progress, target = self.contract_progress()
            self.contract_bonus = self.contract[3] if not self.early and progress == target else 0
            self.score += self.final_bonus + self.contract_bonus
        else:
            self.deal()
            self.upgrade_pending = self.turn == 4
        return True
