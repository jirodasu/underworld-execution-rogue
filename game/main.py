# title: 冥界執行局
# author: jirodasu
# desc: 架空の刑を組み合わせる冥界スコアアタック
# version: 0.4.0
import math
import random
from pathlib import Path
import pyxel
from rules import Run, CARDS, MAX_HP, TURNS, FINISH_BONUS
import storage

W, H = 640, 360
CARD_RECTS = [(16+i*205, 204, 198, 104) for i in range(3)]
EXECUTE_RECT = (420, 317, 204, 31)
PALETTE = [0x0A1015, 0x16232B, 0x263B40, 0x32564E, 0x52665F, 0x76857A,
           0xA7B8AD, 0xE8E4CF, 0xEA8875, 0xCFA15F, 0xF3D78E, 0x94C99C,
           0x96BFCF, 0x70778D, 0xCBA7BE, 0xD9CAB5]

class App:
    def __init__(self):
        pyxel.init(W, H, title='冥界執行局 v0.4.0', fps=30)
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
        self.best = storage.load()
        self.record = False
        self.save_ok = True
        self.muted = False
        self.reduced_motion = False
        self.help = False
        self.tick = 0
        self.previous = None
        self.sound_setup()
        pyxel.run(self.update, self.draw)

    def sound_setup(self):
        # Short execution cues, no BGM.
        for i, notes in enumerate(('c2g1c2', 'e3g3b3', 'c1g1c2', 'c3e3')):
            pyxel.sounds[i].set(notes, 't', '321', 'f', 7)

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
        if self.run.finished:
            self.previous = (self.run.seed, self.run.score)
        seed = self.run.seed if same else random.randint(1,999999)
        self.run = Run(seed)
        self.screen = 'play'
        self.selected = 0
        self.armed = False
        self.help = False
        self.cooldown = 8
        self.effect = 0
        self.display_score = 0

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
        if self.effect and self.run.finished:
            return
        if self.run.finished:
            if pyxel.btnp(pyxel.KEY_R) or (click and self.hit((110,308,198,36))):
                self.begin(True)
            elif enter or (click and self.hit((331,308,198,36))):
                self.begin(False)
            return
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.select((self.selected-1)%3)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.select((self.selected+1)%3)
        for i,key in enumerate((pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3)):
            if pyxel.btnp(key) or (click and self.hit(CARD_RECTS[i])):
                self.select(i)
        if enter or (click and self.hit(EXECUTE_RECT)):
            self.execute()

    def header(self):
        pyxel.rect(0,0,W,43,0)
        pyxel.line(16,42,624,42,3)
        self.text(16,11,'冥界執行局',10)
        pyxel.text(16,29,'UNDERWORLD BUREAU / v0.4.0',5)
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
        if self.run.hp<=3:
            pyxel.line(x-3,y-4,x+3,y-4,8)
            pyxel.pset(x-3,y-3,8)
            pyxel.pset(x+3,y-3,8)
        else:
            pyxel.line(x-2,y-5,x+3,y-5,3)
        if self.run.shadow:
            pyxel.circ(x+29,y+6,5,12)
            pyxel.circ(x+32,y+3,5,0)
        pyxel.line(x-3,y+5,x-7,y+22,5)
        pyxel.line(x+4,y+6,x+11,y+21,5)

    def sentence_effect(self,x,y):
        c=CARDS[self.effect_card]
        t=30-self.effect
        if self.reduced_motion:
            pyxel.circb(x,y,35,c.color)
            return
        if c.tag=='shadow':
            for i in range(8):
                pyxel.pset(x-35-i*3-t,y+20+int(math.sin(i+t/3)*8),12)
        elif c.tag=='mirror':
            for side in (-1,1):
                pyxel.rectb(x+side*45-10,y-23,20,42,12)
                pyxel.line(x+side*45-7,y+14,x+side*45+7,y-16,6)
        elif c.tag=='memory':
            for i in range(5):
                pyxel.rectb(x-32+i*15,y-12-t//2+i%2*8,7,9,10)
        else:
            for i in range(5):
                px=x-45+i*23
                pyxel.line(px-7,y-55+t*2,px,y-40+t*2,8)
                pyxel.pset(px,y-40+t*2,10)

    def icon(self, tag, x, y, color, large=False):
        if tag=='shadow':
            pyxel.circ(x+10,y+9,9,color)
            pyxel.circ(x+15,y+5,8,1)
        elif tag=='mirror':
            pyxel.rectb(x+3,y,15,21,color)
            pyxel.line(x+6,y+16,x+14,y+4,color)
        elif tag=='memory':
            pyxel.rectb(x+2,y+2,18,16,color)
            pyxel.line(x+10,y+3,x+10,y+17,color)
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
        self.center(201,'点を取ると、おばけの元気がへる。',7)
        self.center(223,'３枚から１枚。休みながら８回選ぼう。',6)
        self.center(243,'８回できたら＋20点！ 高い点をめざそう。',10)
        self.center(260,f'最高記録  {self.best} 点',6)
        self.button((218,280,204,38),'はじめる')
        self.center(333,'架空のおばけに、不思議な刑を使うゲームです。',5)

    def hearts(self, x, y, hp, after=None):
        for i in range(MAX_HP):
            col=11 if i<hp else 2
            if after is not None and min(hp,after)<=i<max(hp,after):
                col=10 if after>hp else 8
            px=x+i*12
            pyxel.rect(px,y,9,9,col)
            if i<hp:
                pyxel.rect(px+2,y+2,5,5,0)

    def play(self):
        self.header()
        r=self.run
        self.text(194,11,f'あと {TURNS-r.turn} 回',10)
        self.text(194,28,'元気を残して８回で ＋20点',6)
        for i in range(TURNS):
            pyxel.rect(320+i*12,14,7,7,10 if i<r.turn else 2)
        self.panel(16,50,146,131)
        self.text(28,60,'おばけの元気',6)
        self.text(28,80,f'{r.hp} / 10',8 if r.hp<=3 else 7)
        after=r.hp_after(r.offer[self.selected]) if self.armed else None
        self.hearts(28,102,r.hp,after)
        self.text(28,126,'いまの点',6)
        self.text(28,148,f'{r.score} 点',10)
        self.hall()
        self.panel(468,50,156,131)
        self.text(480,60,'影で鏡が強くなる',10)
        self.icon('shadow',480,84,12 if r.shadow else 3)
        self.text(507,87,'影あり：１つ' if r.shadow else '影なし：０',12 if r.shadow else 6)
        self.text(480,111,'鏡 ３点 → ８点' if r.shadow else '鏡は今３点',7)
        self.text(480,133,'鏡で影を使う' if r.shadow else '影の刑でためる',6)
        self.text(480,155,'影は１つまで',5)
        if self.armed:
            self.text(21,186,'１  カードを選ぶ',6)
            self.text(226,186,'２  結果を見て',10)
            self.text(440,186,'３  決める',10)
        elif r.history:
            entry=r.history[-1]
            note=('影を使った！' if entry['card']==1 and entry['shadow_before'] else
                  '影は１つのまま' if entry['card']==0 and entry['shadow_before'] else
                  '影をためた！' if entry['card']==0 else
                  '元気がもどった' if entry['hp_after']>entry['hp_before'] else '次はどれ？')
            self.text(21,186,f'前の１回：＋{entry["points"]}点  元気 {entry["hp_before"]} → {entry["hp_after"]}  ／ {note}',10)
        else:
            self.text(21,186,'まず１枚選ぼう。点と元気を見くらべよう。',10)
        for i,index in enumerate(r.offer):
            c=CARDS[index]
            x,y,w,h=CARD_RECTS[i]
            selected=self.armed and self.selected==i
            danger=r.hp_after(index)==0
            self.panel(x,y,w,h,c.color if selected else 4 if self.hit(CARD_RECTS[i]) else 3,2 if selected else 1)
            if selected:
                pyxel.line(x+8,y+h-4,x+w-8,y+h-4,c.color)
            pyxel.rect(x+1,y+1,3,h-2,c.color)
            self.icon(c.tag,x+12,y+11,c.color)
            self.text(x+42,y+11,c.name,7)
            self.text(x+42,y+29,c.role,6)
            self.text(x+12,y+51,f'＋{r.preview(index)} 点',10)
            delta=r.hp_after(index)-r.hp
            self.text(x+87,y+51,f'元気 {abs(delta)}'+('回復' if delta>=0 else '使う'),11 if delta>0 else 8 if delta<0 else 6)
            hint='元気０で終わり！' if danger else ('元気はいっぱい！' if index==3 and r.hp==MAX_HP else ('影はもうある' if index==0 and r.shadow else c.lines[0]))
            self.text(x+12,y+72,self.fit(hint,174),8 if danger else c.color)
            self.text(x+12,y+89,f'使ったあと：元気 {r.hp_after(index)}',6)
        if self.armed:
            idx=r.offer[self.selected]
            after=r.hp_after(idx)
            danger=after==0
            self.text(16,312,f'これを使うと ＋{r.preview(idx)}点 ／ 元気 {r.hp} → {after}',7)
            if danger:
                hint='ここで終わる。８回ボーナスはもらえない。'
            elif r.turn==TURNS-1:
                hint='これで８回！ さらに＋20点もらえる。'
            elif idx==3:
                hint='今は回復しない。休んでも１回使う。' if r.hp==MAX_HP else f'元気を{after-r.hp}もどす。休んでも１回使う。'
            elif idx==0:
                hint='影はもうある。鏡を待とう。' if r.shadow else '使うと影がたまる。次の鏡は８点！'
            elif idx==1:
                hint='影を使って８点！ 使った影はなくなる。' if r.shadow else '影を先に使えば、鏡が８点になる。'
            else:
                hint='今７点とる？ 元気を残しておく？'
            self.text(16,334,self.fit(hint,396),8 if danger else 6)
            self.button(EXECUTE_RECT,'終わっても使う' if danger else 'これを使う',not self.cooldown,8 if danger else 10)
        else:
            self.text(16,318,'点を取る？ 元気をもどす？ １枚選ぼう。',7)
            self.text(16,338,'休むのも１回。元気０になると終わり。',5)
            self.button(EXECUTE_RECT,'１枚選ぼう',False)

    def result(self):
        self.header()
        r=self.run
        self.panel(34,53,572,238,9)
        self.text(52,63,f'{r.turn} / ８回',6)
        pyxel.text(52,80,f'CASE {r.seed:06d}',5)
        self.text(419,63,'元気がなくなった' if r.early else '８回できた！',8 if r.early else 11)
        self.center(89,'今回の点',6)
        self.center(109,f'{r.score} 点',10,self.title_font)
        self.center(142,('新しい最高記録！' if self.record else f'最高記録 {self.best} 点'),10 if self.record else 6)
        self.center(161,f'カード {r.score-r.final_bonus}点 ＋ ８回ボーナス {r.final_bonus}点',7)
        pyxel.line(52,182,588,182,3)
        for i,entry in enumerate(r.history):
            x=52+(i//4)*278
            y=194+(i%4)*20
            self.text(x,y,f'{i+1}  {entry["name"]}',6)
            self.text(x+126,y,f'＋{entry["points"]}点  元気{entry["hp_after"]}',10)
        combos=sum(e['card']==1 and e['shadow_before'] for e in r.history)
        if self.previous and self.previous[0]==r.seed:
            delta=r.score-self.previous[1]
            insight=f'前の同じカードより {delta:+d}点。影を使った鏡 {combos}回。'
        else:
            insight='ひと休みで元気を残して、８回をめざそう。' if r.early else f'影を使った鏡 {combos}回。同じカードで別の順番を試そう。'
        self.center(275,insight,8 if r.early else 6)
        self.button((110,308,198,36),'同じカードで再挑戦')
        self.button((331,308,198,36),'新しいカードで遊ぶ')
        if not self.save_ok: self.center(347,'記録はこの起動中だけ残ります。',5)

    def help_screen(self):
        self.panel(72,57,496,279,9)
        self.center(76,'あそびかた',10)
        lines=(
            '１  ３枚から１枚選んで「これを使う」。',
            '２  おばけの元気を残して、８回選ぶ。',
            '３  高い点をめざす。８回できたら＋20点！',
            '星：７点。元気は３へる。',
            '影：２点。元気は１へる。影を１つためる。',
            '鏡：３点。元気は２へる。影があれば８点！',
            '鏡を使うと影はなくなる。影は１つまで。',
            'ひと休み：１点。元気を２もどす。１回使う。',
            '元気０で終わり。元気は10まで。',
        )
        for i,s in enumerate(lines): self.text(94,105+i*20,s,7 if i<3 else 6)
        self.button((235,298,170,32),'もどる')

    def draw(self):
        pyxel.cls(0)
        if self.screen=='title': self.title()
        elif self.run.finished and not self.effect: self.result()
        else: self.play()
        if self.help: self.help_screen()

if __name__=='__main__':
    App()
