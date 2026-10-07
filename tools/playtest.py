"""Five complete input/update/draw runs using the real native Pyxel renderer.
Input injection is a test harness, not an OS-level or manual play session.
"""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'game'))
import pyxel
import main
from rules import CARDS

pyxel.run=lambda u,d:None
main.storage.load=lambda:0
main.storage.save=lambda best:True
app=main.App()
pressed=set()
pyxel.btnp=lambda key,*args:key in pressed

def tick(n=1):
    for _ in range(n):app.update();app.draw()

def key(k):
    pressed.add(k);tick();pressed.clear();tick(36)

def capture(name):
    app.draw();pyxel.screen.save(str(ROOT/'docs/qa'/name),2)

capture('title-v2.png')
strategies=['安全・判決書','目先の得点','影と鏡','階段累積','鐘と星']
rows=[]
for n,label in enumerate(strategies):
    app.run=main.Run(410+n)
    app.screen='title'
    app.cooldown=0
    key(pyxel.KEY_RETURN)
    key((pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3)[[2,2,0,1,2][n]])
    key(pyxel.KEY_RETURN)
    assert app.screen=='play'
    old=(app.run.turn,app.run.hp,app.run.money)
    key(pyxel.KEY_RETURN)
    assert old==(app.run.turn,app.run.hp,app.run.money),'Unselected execute mutated run'
    path=[]
    while not app.run.finished:
        r=app.run
        if r.upgrade_pending:
            key((pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3)[[1,2,2,2,0][n]])
            key(pyxel.KEY_RETURN)
            assert not r.upgrade_pending
            continue
        legal=[i for i in r.offer if CARDS[i].cost<=r.money]
        if n==0:
            safe=[i for i in legal if r.damage(i)<r.hp or r.turn==7]
            idx=max(safe or legal,key=lambda i:r.preview(i)-r.damage(i)*1.2+(25 if CARDS[i].tag==r.contract[1] else 0))
        elif n==1:idx=max(legal,key=r.preview)
        elif n==2:idx=max(legal,key=lambda i:r.preview(i)+(24 if i==1 and r.turn<5 else 0))
        elif n==3:idx=max(legal,key=lambda i:r.preview(i)+(25 if i==0 else 0))
        else:idx=max(legal,key=lambda i:r.preview(i)+(18 if i==4 and r.turn<6 else 0))
        slot=r.offer.index(idx)
        old=(r.turn,r.hp,r.money,r.score)
        key((pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3)[slot])
        assert old==(r.turn,r.hp,r.money,r.score),'Selection executed immediately'
        predicted=r.preview(idx)
        predicted_hp=max(0,r.hp-r.damage(idx))
        if n==2 and r.turn==0:capture('play-v2.png')
        key(pyxel.KEY_RETURN)
        assert r.history[-1]['points']==predicted
        assert r.hp==predicted_hp
        path.append(r.history[-1])
    tick(40)
    if n==4:capture('result-v2.png')
    rows.append({'run':n+1,'seed':r.seed,'strategy':label,'score':r.score,'turns':r.turn,'early':r.early,'hp':r.hp,'seals':sorted(r.seals),'contract':r.contract[0],'contract_bonus':r.contract_bonus,'history':path})
    score=r.score;key(pyxel.KEY_1)
    assert r.score==score,'Result input modified completed run'
    oldseed=r.seed
    key(pyxel.KEY_R)
    assert app.screen=='seals' and app.run.seed==oldseed
# Optional presentation controls and modal don't consume a turn.
key(pyxel.KEY_1);key(pyxel.KEY_RETURN)
t=app.run.turn
key(pyxel.KEY_H);assert app.help
key(pyxel.KEY_RETURN);assert not app.help
key(pyxel.KEY_M);assert app.muted
key(pyxel.KEY_V);assert app.reduced_motion
assert app.run.turn==t
(ROOT/'docs/qa/improved-runs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(json.dumps([{k:v for k,v in row.items() if k!='history'} for row in rows],ensure_ascii=False,indent=2))
print('Five full input/update/draw runs passed; replay, help, settings, and selection guards passed.')
