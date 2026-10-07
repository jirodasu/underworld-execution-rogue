"""Five automated native Pyxel input/update/draw runs, not manual browser play."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'game'))
import pyxel
import main

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

capture('title-v3.png')
labels=['元気を残す','今の点を優先','影から鏡','星とひと休み','休みすぎる']
rows=[]
for n,label in enumerate(labels):
    app.run=main.Run(410+n)
    app.screen='title'
    app.cooldown=0
    key(pyxel.KEY_RETURN)
    assert app.screen=='play'
    old=(app.run.turn,app.run.hp,app.run.score)
    key(pyxel.KEY_RETURN)
    assert old==(app.run.turn,app.run.hp,app.run.score)
    while not app.run.finished:
        r=app.run
        safe=[i for i in r.offer if r.hp_after(i)>0]
        if n==0:
            idx=max(safe,key=lambda i:r.preview(i)+(4 if i==3 and r.hp<=4 and r.turn<7 else 0))
        elif n==1:
            idx=max(r.offer,key=r.preview)
        elif n==2:
            idx=3 if r.hp<=3 and r.turn<7 else max(safe,key=lambda i:r.preview(i)+(4 if i==0 and not r.shadow else 0))
        elif n==3:
            idx=3 if r.hp<=4 and r.turn<7 else max(safe,key=r.preview)
        else:idx=3
        old=(r.turn,r.hp,r.score)
        key((pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3)[r.offer.index(idx)])
        assert old==(r.turn,r.hp,r.score),'Selection must not execute'
        predicted,expected_hp=r.preview(idx),r.hp_after(idx)
        if n==2 and r.turn==0:capture('play-v3.png')
        if n==2 and r.shadow and 1 in r.offer:
            key((pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3)[r.offer.index(1)])
            capture('combo-v3.png')
            key((pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3)[r.offer.index(idx)])
        key(pyxel.KEY_RETURN)
        assert r.history[-1]['points']==predicted
        assert r.hp==expected_hp
    tick(40)
    if n==2:capture('result-v3.png')
    assert r.score==sum(e['points'] for e in r.history)+r.final_bonus
    rows.append({'run':n+1,'seed':r.seed,'strategy':label,'score':r.score,'turns':r.turn,'early':r.early,'hp':r.hp,'bonus':r.final_bonus,'history':r.history[:]})
    score=r.score;key(pyxel.KEY_1);assert r.score==score
    seed=r.seed;first=main.Run(seed).offer
    key(pyxel.KEY_R)
    assert app.screen=='play' and app.run.seed==seed and app.run.offer==first
key(pyxel.KEY_H);assert app.help
capture('help-v3.png')
key(pyxel.KEY_RETURN);assert not app.help
t=app.run.turn
key(pyxel.KEY_M);assert app.muted
key(pyxel.KEY_V);assert app.reduced_motion
assert app.run.turn==t
(ROOT/'docs/qa/simple-runs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(json.dumps([{k:v for k,v in row.items() if k!='history'} for row in rows],ensure_ascii=False,indent=2))
print('Five native input/update/draw runs passed; preview, selection, replay and help verified.')
