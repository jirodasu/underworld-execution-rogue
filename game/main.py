# title: 冥界執行局
# author: jirodasu
# desc: 架空の刑を組み合わせる冥界スコアアタック
# version: 0.2.0
import math
import random
from pathlib import Path
import pyxel
from rules import Run, CARDS, SEALS
import storage

W, H = 640, 360
CARD_RECTS = [(16+i*205, 204, 198, 104) for i in range(3)]
SEAL_RECTS = [(34+i*195, 167, 182, 118) for i in range(3)]
EXECUTE_RECT = (420, 317, 204, 31)
PALETTE = [0x0A1015, 0x16232B, 0x263B40, 0x32564E, 0x52665F, 0x76857A,
           0xA7B8AD, 0xE8E4CF, 0xEA8875, 0xCFA15F, 0xF3D78E, 0x94C99C,
           0x96BFCF, 0x70778D, 0xCBA7BE, 0xD9CAB5]

class App:
    def __init__(self):
        pyxel.init(W, H, title='冥界執行局 v0.2', fps=30)
        pyxel.colors.from_list(PALETTE)
        pyxel.mouse(True)
        base = Path(__file__).parent / 'assets'
        self.font = pyxel.Font(str(base/'japanese.bdf'))
        self.title_font = pyxel.Font(str(base/'title.bdf'))
        self.run = Run(random.randint(1, 999999))
        self.screen = 'title'
        self.selected = 0
        self.armed = False
        self.cooldown = 0
        self.effect = 0
        self.effect_card = 0
        self.display_score = 0
        self.display_hp = 100.0
        self.best = storage.load()
        self.record = False
        self.save_ok = True
        self.muted = False
        self.reduced_motion = False
        self.help = False
        self.tick = 0
        self.sound_setup()
        pyxel.run(self.update, self.draw)

    def sound_setup(self):
        # Short execution cues, no BGM.
        for i, notes in enumerate(('c2e2g2', 'c2g1c2', 'e3g3b3', 'c3e3', 'g2d3g3', 'c1g1c2')):
            pyxel.sounds[i].set(notes, 't' if i!=4 else 's', '321', 'f', 7)
        pyxel.sounds[6].set('c3e3g3c4', 't', '4321', 'f', 7)

    def text(self, x, y, s, col=7):
        pyxel.text(x, y, str(s), col, self.font)

    def fit(self, s, width):
        s = str(s)
        if self.font.text_width(s) <= width:
            return s
        while s and self.font.text_width(s+'…') > width:
            s = s[:-1]
        return s+'…'

    def center(self, y, s, col=7, font=None):
        font = font or self.font
        pyxel.text((W-font.text_width(s))//2, y, s, col, font)

    def hit(self, rect):
        x,y,w,h = rect
        return x <= pyxel.mouse_x < x+w and y <= pyxel.mouse_y < y+h

    def panel(self, x, y, w, h, border=2, fill=1):
        pyxel.rect(x, y, w, h, fill)
        pyxel.rectb(x, y, w, h, border)
        for px,py in ((x,y),(x+w-3,y),(x,y+h-3),(x+w-3,y+h-3)):
            pyxel.rect(px,py,3,3,border)

    def button(self, rect, label, active=True, accent=10):
        x,y,w,h = rect
        hover = self.hit(rect) and active
        self.panel(x,y,w,h,accent if active else 3,2 if hover else 1)
        self.text(x+(w-self.font.text_width(label))//2,y+(h-12)//2,label,7 if active else 5)

    def begin(self, same=True):
        seed = self.run.seed if same else random.randint(1,999999)
        self.run = Run(seed)
        self.screen = 'seals'
        self.selected = 0
        self.armed = False
        self.help = False
        self.cooldown = 8
        self.effect = 0
        self.display_score = 0
        self.display_hp = 100.0

    def execute(self):
        if not self.armed or self.run.finished:
            return False
        index = self.run.offer[self.selected]
        if not self.run.choose(index):
            return False
        self.effect_card = index
        self.effect = 12 if self.reduced_motion else 30
        self.cooldown = 12
        self.armed = False
        self.selected = 0
        if not self.muted:
            pyxel.play(0,index)
        if self.run.finished:
            self.record = self.run.score > self.best
            self.best = max(self.best,self.run.score)
            self.save_ok = storage.save(self.best)
        return True

    def select(self, i):
        self.selected = i
        self.armed = True

    def update(self):
        self.tick += 1
        self.effect = max(0,self.effect-1)
        self.cooldown = max(0,self.cooldown-1)
        self.display_hp += (self.run.hp-self.display_hp)*0.24
        if self.run.score > self.display_score:
            self.display_score += max(1,(self.run.score-self.display_score)//5)
        click = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        enter = pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE)
        if pyxel.btnp(pyxel.KEY_M) or (click and self.hit((477,10,67,24))):
            self.muted = not self.muted
            if self.muted: pyxel.stop()
            return
        if pyxel.btnp(pyxel.KEY_V) or (click and self.hit((551,10,73,24))):
            self.reduced_motion = not self.reduced_motion
            return
        if self.cooldown:
            return
        if self.screen == 'title':
            if enter or (click and self.hit((218,280,204,38))):
                self.begin()
            return
        if pyxel.btnp(pyxel.KEY_H) or (click and self.hit((443,10,26,24))):
            self.help = not self.help
            return
        if self.help:
            if enter or (click and self.hit((235,298,170,32))): self.help=False
            return
        if self.effect and (self.run.finished or self.run.upgrade_pending):
            return
        if self.run.finished:
            if pyxel.btnp(pyxel.KEY_R) or (click and self.hit((110,308,198,36))):
                self.begin(True)
            elif enter or (click and self.hit((331,308,198,36))):
                self.begin(False)
            return
        seals = self.screen=='seals' or self.run.upgrade_pending
        rects = SEAL_RECTS if seals else CARD_RECTS
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.select((self.selected-1)%3)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.select((self.selected+1)%3)
        for i,key in enumerate((pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3)):
            if pyxel.btnp(key) or (click and self.hit(rects[i])):
                self.select(i)
        if seals:
            if self.armed and (enter or (click and self.hit((218,304,204,34)))):
                seal = SEALS[self.selected+(3 if self.run.upgrade_pending else 0)]
                if self.run.upgrade_pending:
                    self.run.upgrade(seal.key)
                else:
                    self.run=Run(self.run.seed,seal.key)
                    self.screen='play'
                self.armed=False
                self.selected=0
                self.cooldown=8
                if not self.muted: pyxel.play(0,6)
        elif enter or (click and self.hit(EXECUTE_RECT)):
            self.execute()

    def header(self):
        pyxel.rect(0,0,W,43,0)
        pyxel.line(16,42,624,42,3)
        self.text(16,11,'冥界執行局',10)
        pyxel.text(16,29,'UNDERWORLD BUREAU / v0.2',5)
        self.button((477,10,67,24),'音 OFF' if self.muted else '音 ON',accent=4)
        self.button((551,10,73,24),'静止 ON' if self.reduced_motion else '静止 OFF',accent=4)
        if self.screen!='title': self.button((443,10,26,24),'?',accent=4)

    def hall(self, x=174, y=49, w=284, h=134):
        pyxel.rect(x,y,w,h,0)
        center=x+w//2
        # Faceted gothic portal, patterned stone, floor lines.
        for side in (-1,1):
            for k in range(4):
                px=center+side*(98-k*10)
                pyxel.line(px,y+28+k*5,px,y+h-15,2 if k%2 else 3)
                pyxel.line(px,y+28+k*5,center,y+7+k*8,2 if k%2 else 3)
            px=center+side*108
            pyxel.rect(px-5,y+65,10,6,9)
            flame=2 if self.reduced_motion else (self.tick//4)%3
            pyxel.tri(px-4,y+65,px+4,y+65,px,y+52-flame,10)
        pyxel.line(x+6,y+h-12,x+w-6,y+h-12,3)
        for k in range(4):
            pyxel.line(x+6+k*32,y+h-12,center+(k-2)*20,y+h,1)
        pyxel.ellib(center-58,y+h-28,116,20,3)
        pyxel.ellib(center-44,y+h-24,88,12,9)
        for i in range(8):
            a=i*math.tau/8+(0 if self.reduced_motion else self.tick/150)
            pyxel.pset(center+math.cos(a)*49,y+h-18+math.sin(a)*7,10)
        self.ghost(center,y+66)
        if self.effect: self.sentence_effect(center,y+66)

    def ghost(self,x,y):
        bob=0 if self.reduced_motion else int(math.sin(self.tick/15)*2)
        y+=bob
        pyxel.circ(x,y-13,13,6)
        pyxel.circ(x-3,y-15,10,7)
        pyxel.rect(x-12,y-11,24,18,6)
        pyxel.tri(x-12,y+2,x+12,y+2,x+21,y+30,6)
        pyxel.tri(x-12,y+2,x+8,y+2,x-16,y+28,7)
        pyxel.tri(x-16,y+26,x-2,y+23,x-10,y+33,6)
        pyxel.tri(x-2,y+26,x+12,y+24,x+5,y+34,6)
        pyxel.rect(x-7,y-15,4,4,0)
        pyxel.rect(x+4,y-15,4,4,0)
        pyxel.pset(x-6,y-14,10)
        pyxel.pset(x+5,y-14,10)
        pyxel.line(x-2,y-5,x+3,y-5,3)
        pyxel.line(x-3,y+5,x-7,y+22,5)
        pyxel.line(x+4,y+6,x+11,y+21,5)

    def sentence_effect(self,x,y):
        c=CARDS[self.effect_card]
        t=30-self.effect
        if self.reduced_motion:
            pyxel.circb(x,y,35,c.color)
            return
        if c.tag=='stairs':
            for i in range(5):
                px=x-60+i*23
                pyxel.line(px,y+43-i*9,px+23,y+43-i*9,c.color)
                pyxel.line(px+23,y+43-i*9,px+23,y+34-i*9,c.color)
        elif c.tag=='shadow':
            for i in range(8):
                pyxel.pset(x-35-i*3-t,y+20+int(math.sin(i+t/3)*8),12)
        elif c.tag=='mirror':
            for side in (-1,1):
                pyxel.rectb(x+side*45-10,y-23,20,42,12)
                pyxel.line(x+side*45-7,y+14,x+side*45+7,y-16,6)
        elif c.tag=='memory':
            for i in range(5):
                pyxel.rectb(x-32+i*15,y-12-t//2+i%2*8,7,9,10)
        elif c.tag=='bell':
            for i in range(3): pyxel.circb(x,y,15+i*13+t//3,9)
        else:
            for i in range(5):
                px=x-45+i*23
                pyxel.line(px-7,y-55+t*2,px,y-40+t*2,8)
                pyxel.pset(px,y-40+t*2,10)

    def icon(self, tag, x, y, color, large=False):
        if tag=='stairs':
            for i in range(4):
                pyxel.rect(x+i*5,y+14-i*4,5,3,color)
        elif tag=='shadow':
            pyxel.circ(x+10,y+9,9,color)
            pyxel.circ(x+15,y+5,8,1)
        elif tag=='mirror':
            pyxel.rectb(x+3,y,15,21,color)
            pyxel.line(x+6,y+16,x+14,y+4,color)
        elif tag=='memory':
            pyxel.rectb(x+2,y+2,18,16,color)
            pyxel.line(x+10,y+3,x+10,y+17,color)
        elif tag=='bell':
            pyxel.circb(x+10,y+8,7,color)
            pyxel.rect(x+2,y+8,16,9,1)
            pyxel.line(x+1,y+16,x+19,y+16,color)
            pyxel.circ(x+10,y+19,2,color)
        elif tag=='star':
            pyxel.tri(x+10,y,x+3,y+19,x+20,y+8,color)
            pyxel.tri(x+1,y+7,x+16,y+20,x+11,y+1,color)
        else:
            pyxel.rectb(x+3,y,15,21,color)
            for k in range(3): pyxel.line(x+6,y+5+k*5,x+15,y+5+k*5,color)

    def title(self):
        self.header()
        self.hall(95,49,450,143)
        self.center(54,'冥界執行局',10,self.title_font)
        pyxel.text(263,88,'THE FINAL VERDICT',5)
        self.center(201,'残酷な判決にも、段取りがある。',7)
        self.center(223,'刑をつなぐ。予算を整える。最後まで執行する。',6)
        self.center(243,'８手番の苦痛スコアアタック',10)
        self.center(260,f'最高記録  {self.best} 点',6)
        self.button((218,280,204,38),'判決書を受け取る')
        self.center(333,'架空の亡者・超常的な刑を扱うフィクションです。',5)

    def seals_screen(self):
        mid=self.run.upgrade_pending
        self.header()
        self.center(65,'追加の印章を選ぶ' if mid else '執行官の印章を選ぶ',10,self.title_font)
        self.center(101,'４手番を通過。後半の構成を強化する。' if mid else '１つの印章で、この挑戦の得意分野が変わる。',6)
        self.center(128,f'判決書：{self.run.contract[4]} ／ 完遂時＋48点',7)
        pyxel.text(190,29,f'CASE / {self.run.seed:06d}',5)
        for i,(x,y,w,h) in enumerate(SEAL_RECTS):
            seal=SEALS[i+(3 if mid else 0)]
            selected=self.armed and self.selected==i
            self.panel(x,y,w,h,seal.color if selected else 3,2 if selected else 1)
            self.icon(seal.key,x+w//2-10,y+14,seal.color)
            self.text(x+12,y+48,seal.name,7)
            self.text(x+12,y+72,seal.lines[0],seal.color)
            self.text(x+12,y+91,seal.lines[1],6)
        self.button((218,304,204,34),'この印章で進む' if self.armed else '印章を１つ選ぶ',self.armed)
        self.center(343,'タップで選択 → 決定 ／ 1・2・3 → Enter',5)

    def play(self):
        self.header()
        r=self.run
        self.text(194,11,f'執行 {min(8,r.turn+1):02d} / 08',7)
        names=[seal.name for seal in SEALS if seal.key in r.seals]
        self.text(174,28,self.fit(' / '.join(names),252),5)
        for i in range(8):
            pyxel.rect(320+i*12,14,7,7,10 if i<r.turn else 2)
        self.panel(16,50,146,131)
        self.text(28,60,'亡者の生命力',6)
        self.text(28,79,f'{r.hp:03d} / 100',8 if r.hp<=26 else 7)
        pyxel.rect(28,99,121,5,2)
        pyxel.rect(28,99,int(max(0,self.display_hp)*1.21),5,8 if r.hp<=26 else 11)
        if self.armed:
            d=r.damage(r.offer[self.selected])
            after=max(0,r.hp-d)
            pyxel.rect(28+after*1.21,99,(r.hp-after)*1.21,5,9)
        self.text(28,117,f'予算  {r.money}',10)
        self.text(28,142,'苦痛スコア',6)
        self.text(28,158,f'{self.display_score:04d} 点',7)
        self.hall()
        self.panel(468,50,156,131)
        self.text(480,60,'判決書',10)
        self.text(480,80,r.contract[0],7)
        progress,target=r.contract_progress()
        self.text(480,99,f'達成 {progress}/{target}  完遂＋48',11 if progress==target else 6)
        pyxel.line(480,119,612,119,3)
        self.text(480,130,f'影欠け {r.shadow} ／ 階段 {r.stairs}',12)
        self.text(480,152,('次の刑 ２倍' if 'bell' in r.seals else '次の刑 1.5倍') if r.boost else '倍率待機なし',10 if r.boost else 5)
        pyxel.rect(16,185,608,15,0)
        if self.effect and r.history:
            self.text(21,186,self.fit(CARDS[self.effect_card].flavor,390),6)
            self.text(452,186,f'＋{r.history[-1]["points"]} 点',10)
        else:
            self.text(21,186,'１  刑を選択',10)
            self.text(204,186,'２  結果を確認',6)
            self.text(419,186,'３  執行する',6)
        for i,index in enumerate(r.offer):
            c=CARDS[index]
            x,y,w,h=CARD_RECTS[i]
            selected=self.armed and self.selected==i
            available=r.money>=c.cost
            danger=r.damage(index)>=r.hp and r.turn<7
            col=c.color if selected else 3
            self.panel(x,y,w,h,col,2 if selected else 1)
            pyxel.rect(x+1,y+1,3,h-2,c.color if available else 4)
            self.icon(c.tag,x+12,y+11,c.color)
            self.text(x+42,y+11,c.name,7 if available else 5)
            self.text(x+42,y+29,f'{i+1} / {c.role}',6)
            self.text(x+12,y+53,f'＋{r.preview(index):03d} 点',10 if available else 5)
            self.text(x+102,y+53,f'消耗 {r.damage(index)}',8 if danger else 6)
            self.text(x+12,y+72,f'予算 {c.cost}',6)
            b=r.breakdown(index)
            hint='予算不足' if not available else ('早期消滅の危険' if danger else ('連携＋'+str(b['combo']) if b['combo'] else c.role))
            self.text(x+74,y+72,self.fit(hint,112),8 if danger else c.color)
            self.text(x+12,y+88,self.fit(c.lines[0],174),6)
        if self.armed:
            idx=r.offer[self.selected]
            b=r.breakdown(idx)
            after=max(0,r.hp-r.damage(idx))
            next_money = r.money-CARDS[idx].cost
            if idx == 3:
                next_money += 6 if 'memory' in r.seals else 4
            self.text(16,312,f'生命力 {r.hp} → {after} ／ 予算 {r.money} → {next_money}',7)
            self.text(16,327,f'({b["base"]}＋{b["combo"]}＋{b["novelty"]}) × {b["mult"]:g} = {b["points"]}点',6)
            self.text(16,342,self.fit(CARDS[idx].lines[1],390),6)
            active=r.money>=CARDS[idx].cost and not self.cooldown
            label='予算不足' if r.money<CARDS[idx].cost else ('消滅を承知で執行' if after==0 and r.turn<7 else 'この刑を執行する')
            self.button(EXECUTE_RECT,label,active,8 if after==0 and r.turn<7 else 10)
        else:
            self.text(16,318,'カードを選ぶと、執行後の状態を確認できます。',6)
            self.text(16,337,'左右 / 1・2・3：選択    Enter：執行',5)
            self.button(EXECUTE_RECT,'刑を選んでください',False)

    def result(self):
        self.header()
        r=self.run
        self.panel(34,53,572,238,9)
        self.text(52,63,'執行記録 / '+str(r.seed),6)
        self.text(419,63,'早期消滅' if r.early else '最終判決・完遂',8 if r.early else 11)
        self.center(89,'苦痛スコア',6)
        self.center(109,f'{r.score:04d} 点',10,self.title_font)
        self.center(142,('新しい最高記録' if self.record else f'最高記録 {self.best} 点'),10 if self.record else 6)
        self.center(161,f'刑 {r.score-r.final_bonus-r.contract_bonus} ＋ 完遂 {r.final_bonus} ＋ 判決書 {r.contract_bonus}',7)
        pyxel.line(52,182,588,182,3)
        for i,entry in enumerate(r.history):
            x=52+(i//4)*278
            y=194+(i%4)*20
            self.text(x,y,f'{i+1:02d}  {entry["name"]}',6)
            self.text(x+174,y,f'＋{entry["points"]}',10)
        self.center(275,'完遂前に生命力が尽きました。' if r.early else f'判決書 {r.contract_progress()[0]}/{r.contract_progress()[1]} ／ 残存生命力 {r.hp}',8 if r.early else 6)
        self.button((110,308,198,36),'同じ条件で再挑戦')
        self.button((331,308,198,36),'新しい判決書へ')
        if not self.save_ok: self.center(347,'記録はこの起動中のみ保持されます。',5)

    def help_screen(self):
        self.panel(72,57,496,279,9)
        self.center(76,'執行官の手引き',10)
        lines=(
            '８手番で最終判決。苦痛スコアを稼ぐ。',
            '途中で生命力０になると、完遂・判決書加点なし。',
            '完遂加点は40＋残存生命力の半分。',
            '影流し→鏡審判：影を消費し、１つにつき＋18点。',
            '無限階段：繰り返すほど累積加点。',
            '鐘：次の刑に倍率。記憶没収でも消費される。',
            '記憶没収：予算を補給。常に選択肢にある。',
            '４手番後に追加の印章を選び、構成を強化。',
            '静止 ON：背景の動きを止め、刑の演出を短縮。',
        )
        for i,s in enumerate(lines): self.text(94,105+i*20,s,7 if i<3 else 6)
        self.button((235,298,170,32),'執行に戻る')

    def draw(self):
        pyxel.cls(0)
        if self.screen=='title': self.title()
        elif self.run.finished and not self.effect: self.result()
        elif self.screen=='seals' or (self.run.upgrade_pending and not self.effect): self.seals_screen()
        else: self.play()
        if self.help: self.help_screen()

if __name__=='__main__':
    App()
