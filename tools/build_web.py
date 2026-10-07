from pathlib import Path
import base64
root=Path(__file__).resolve().parents[1]
payload=base64.b64encode((root/'game.pyxapp').read_bytes()).decode()
html='''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#0a1015">
  <meta name="description" content="３枚から１枚。おばけの元気を残して８回選ぶスコアアタック。">
  <title>冥界執行局 — 架空処刑ローグライト</title>
  <style>
    html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #0a1015; color: #e8e4cf; font-family: system-ui, sans-serif; }
    #pyxel-screen { position: fixed !important; inset: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left); width: auto !important; height: auto !important; background: #0a1015 !important; }
    #canvas { image-rendering: pixelated; touch-action: none; }
    #portrait { display: none; position: fixed; inset: 0; z-index: 999; background: #0a1015; align-items: center; justify-content: center; text-align: center; padding: 24px; }
    #portrait h1 { color: #f3d78e; font-size: 24px; font-weight: 600; letter-spacing: .14em; }
    #portrait p { color: #a7b8ad; line-height: 1.9; }
    #failure { display: none; position: fixed; inset: 20%; z-index: 1000; padding: 24px; background: #16232b; border: 1px solid #cfa15f; text-align: center; }
    #failure button { background: #263b40; border: 1px solid #f3d78e; color: #e8e4cf; padding: 12px 24px; cursor: pointer; }
    @media (orientation: portrait) { #portrait { display: flex; } }
  </style>
  <script src="https://cdn.jsdelivr.net/gh/kitao/pyxel@2.5.7/wasm/pyxel.js"></script>
</head>
<body>
  <div id="portrait"><div><h1>冥界執行局</h1><p>スマートフォンを横向きにしてください。<br>おばけの元気を残して、８回選ぼう。</p></div></div>
  <div id="failure" role="alert"><h2>起動できませんでした</h2><p>通信を確認して、もう一度お試しください。</p><button onclick="location.reload()">再読み込み</button></div>
  <script>
    launchPyxel({ command: 'play', name: 'game.pyxapp', gamepad: 'disabled', base64: 'PAYLOAD' }).catch(() => {
      document.getElementById('failure').style.display = 'block';
    });
  </script>
</body>
</html>
'''.replace('PAYLOAD',payload)
(root/'index.html').write_text(html)
print('Web build bytes:',len(html))
