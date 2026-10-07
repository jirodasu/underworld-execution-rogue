# 冥界執行局 — Underworld Execution Rogue

Pyxel製の架空処刑ローグライト試作 v0.1。
冥界の執行官として、提示された刑を組み合わせ、苦痛スコアを競います。

## ブラウザで遊ぶ

[試作を起動する](https://kitao.github.io/pyxel/web/launcher/?play=jirodasu/underworld-execution-rogue/main/game)

起動画面を押すとゲームが始まります。横画面を推奨。
タップ／マウスで刑カードを選択。PCでは1・2・3、左右＋Enterも使用できます。

## ルール

- 8手番。生命力100、予算14から開始。
- 生命力が0になると終了。8手番未満なら完遂ボーナスなし。
- 8手番完遂で最終判決。40＋残存生命力÷2点を加算。
- 影流し→鏡審判で追加得点。鐘→次の刑の得点1.5倍。
- 無限階段は繰り返すほど加点。記憶没収は予算を補充。
- 提示はランダムですが、予算0でも選べる刑が必ずあります。
- 結果画面で同じ条件の再挑戦、新しい条件での挑戦を選択。
- オンラインランキングと永続成長は未実装。最高点は起動中のみ保持。

## Windowsで開発

```powershell
py -m pip install -r requirements.txt
py game/main.py
py -m unittest discover -s tests
py -m pyxel package game game/main.py
py -m pyxel app2html game.pyxapp
```

`game.html` を `index.html` に変更すれば、同じブラウザ版を更新できます。
GitHub Pagesを利用する場合：Settings → Pages → Deploy from a branch → main / root。
Steam販売用の実行ファイル・ストア・審査対応は今後の工程です。

## ファイル

- `game/main.py`：日本語UI・描画・入力
- `game/rules.py`：乱数シード付きのゲームルール
- `game/assets/`：日本語ビットマップフォントとライセンス
- `tests/`：得点、進行、再現性の検証
- `game.pyxapp`：配布用Pyxelアプリ
- `index.html`：ブラウザ配布版
- `docs/DESIGN.md`：試作仕様と合格条件

刑・亡者・苦痛値はフィクションです。
フォントはM+ bitmap fonts由来。ライセンスは `game/assets/FONT_LICENSE.txt`。
