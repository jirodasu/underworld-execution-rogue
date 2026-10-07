# title: 冥界執行局
# author: jirodasu
# desc: 架空の刑を組み合わせるスコアアタック試作
# version: 0.1.0
import math
import random
from pathlib import Path
import pyxel
from rules import Run, CARDS

class App:
    def __init__(self):
        pyxel.init(480, 270, title='冥界執行局 v0.1', fps=30)
        pyxel.mouse(True)
        self.font = pyxel.Font(str(Path(__file__).parent / 'assets/japanese.bdf'))
        self.run = Run(random.randint(1, 999999))
        self.screen = 'title'
        self.selected = 0
        self.cooldown = 0
        self.effect = 0
        self.best = 0
        pyxel.sounds[0].set('c2e2g2c3', 't', '4321', 'f', 6)
        pyxel.run(self.update, self.draw)

    def text(self, x, y, s, col=7):
        pyxel.text(x, y, s, col, self.font)

    def center(self, y, s, col=7):
        self.text((480-self.font.text_width(s))//2, y, s, col)

    def hit(self, x, y, w, h):
        return x <= pyxel.mouse_x < x+w and y <= pyxel.mouse_y < y+h

    def restart(self, same=False):
        self.run = Run(self.run.seed if same else random.randint(1, 999999))
        self.screen = 'play'
        self.selected = 0
        self.cooldown = 8

    def update(self):
        self.effect = max(0, self.effect-1)
        self.cooldown = max(0, self.cooldown-1)
        if self.cooldown:
            return
        click = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        enter = pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE)
        if self.screen == 'title':
            if enter or (click and self.hit(140, 211, 200, 34)):
                self.restart(True)
            return
        if self.run.finished:
            if pyxel.btnp(pyxel.KEY_R) or (click and self.hit(58, 222, 170, 30)):
                self.restart(True)
            elif enter or (click and self.hit(250, 222, 170, 30)):
                self.restart()
            return
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.selected = (self.selected-1)%3
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.selected = (self.selected+1)%3
        choice = self.selected if enter else None
        for i, key in enumerate((pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3)):
            if pyxel.btnp(key) or (click and self.hit(10+i*156, 156, 148, 102)):
                choice = i
                self.selected = i
        if choice is not None:
            if self.run.choose(self.run.offer[choice]):
                self.cooldown = 12
                self.effect = 15
                pyxel.play(0, 0)
                if self.run.finished:
                    self.best = max(self.best, self.run.score)

    def room(self):
        pyxel.rect(0, 0, 480, 270, 0)
        for x in range(20, 470, 60):
            pyxel.rect(x, 38, 10, 106, 1)
            pyxel.rect(x-3, 36, 16, 5, 13)
        pyxel.ellib(168, 120, 146, 25, 13)
        pyxel.ellib(181, 125, 120, 14, 2)
        bob = int(math.sin(pyxel.frame_count/12)*2)
        pyxel.circ(240, 82+bob, 13, 13)
        pyxel.tri(228, 90+bob, 252, 90+bob, 257, 118+bob, 13)
        pyxel.rect(232, 80+bob, 4, 3, 10)
        pyxel.rect(244, 80+bob, 4, 3, 10)
        pyxel.line(235, 91+bob, 245, 91+bob, 2)
        for i in range(12):
            a = i*math.tau/12 + pyxel.frame_count/90
            pyxel.pset(240+math.cos(a)*42, 100+math.sin(a)*24, 12 if self.effect else 5)
        if self.effect:
            pyxel.circb(240, 96, 44-self.effect, 10)

    def button(self, x, y, w, label, col=2):
        pyxel.rect(x, y, w, 30, col)
        pyxel.rectb(x, y, w, 30, 10)
        self.text(x+(w-self.font.text_width(label))//2, y+9, label, 7)

    def draw(self):
        self.room()
        r = self.run
        if self.screen == 'title':
            self.center(16, '冥界執行局', 10)
            self.center(35, '架空処刑ローグライト / 試作 v0.1', 6)
            self.center(150, '刑を組み合わせ、苦痛スコアを稼ぐ。')
            self.center(168, '生命力０で早期終了。８手番完遂で加点。', 6)
            self.center(186, '影→鏡で加点 ／ 鐘→次の刑が1.5倍', 10)
            self.button(140, 211, 200, '執行を開始する')
            self.center(253, '架空の亡者と超常的な刑を扱う作品です。', 13)
            return
        if r.finished:
            pyxel.rect(35, 38, 410, 176, 1)
            pyxel.rectb(35, 38, 410, 176, 13)
            self.center(49, '早期消滅：完遂ボーナスなし' if r.early else '最終判決を執行：完遂', 10)
            self.center(73, f'苦痛スコア  {r.score} 点', 7)
            self.center(94, f'刑の得点 {r.score-r.final_bonus} ＋ 完遂 {r.final_bonus}', 6)
            self.center(111, f'手番 {r.turn}/8   残存生命力 {r.hp}   今回の最高 {self.best}', 6)
            for i, (name, points) in enumerate(r.history):
                x = 55 + (i//4)*196
                self.text(x, 135+(i%4)*17, f'{i+1}. {name} +{points}', 7)
            self.button(58, 222, 170, '同じ条件で再挑戦')
            self.button(250, 222, 170, '新しい条件で挑戦')
            return
        pyxel.rect(0, 0, 480, 32, 1)
        self.text(10, 6, f'手番 {r.turn+1}/8', 10)
        self.text(112, 6, f'予算 {r.money}', 7)
        self.text(215, 6, f'苦痛 {r.score} 点', 7)
        self.text(361, 6, f'条件 {r.seed}', 13)
        self.text(10, 39, f'生命力 {r.hp}/100', 7)
        pyxel.rect(10, 55, 120, 6, 1)
        pyxel.rect(10, 55, int(r.hp*1.2), 6, 8 if r.hp < 30 else 11)
        self.text(10, 72, f'影欠け {r.shadow}', 12)
        self.text(10, 89, f'階段累積 {r.stairs}', 6)
        self.text(10, 106, '次の刑 1.5倍' if r.boost else '次の刑 通常倍率', 10 if r.boost else 13)
        self.text(328, 45, '目標：８手番完遂', 10)
        self.text(328, 63, '生命力０で終了', 6)
        self.text(328, 81, '最後に判決ボーナス', 6)
        pyxel.rect(8, 133, 464, 18, 1)
        self.text(14, 136, r.last, 7)
        for i, index in enumerate(r.offer):
            c = CARDS[index]
            x = 10+i*156
            available = r.money >= c.cost
            hover = self.hit(x, 156, 148, 102)
            pyxel.rect(x, 156, 148, 102, 1)
            pyxel.rectb(x, 156, 148, 102, 10 if i == self.selected or hover else 13)
            self.text(x+7, 162, f'{i+1}  {c.name}', 7 if available else 13)
            self.text(x+7, 180, f'予算 {c.cost} / 生命力 -{c.damage}', 6)
            self.text(x+7, 197, f'獲得 ＋{r.preview(index)} 点', 10)
            self.text(x+7, 215, c.lines[0], 7)
            self.text(x+7, 231, c.lines[1], 12)
            self.text(x+7, 246, '早期終了の危険' if c.damage >= r.hp else ('タップで執行' if available else '予算不足'), 8 if c.damage >= r.hp else 13)
        self.center(260, 'タップ / 1・2・3 ／ 左右＋Enter', 13)

if __name__ == '__main__':
    App()
