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
  <meta name="game-version" content="0.3.1">
  <title>冥界執行局 — 架空処刑ローグライト</title>
  <style>
    html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #0a1015; color: #e8e4cf; font-family: system-ui, sans-serif; }
    #pyxel-screen { position: fixed !important; inset: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left); width: auto !important; height: auto !important; background: #0a1015 !important; }
    #canvas { image-rendering: pixelated; touch-action: none; }
    #pyxel-prompt { opacity: 0; }
    #portrait, #boot { position: fixed; inset: 0; background: #0a1015; align-items: center; justify-content: center; text-align: center; padding: 16px; box-sizing: border-box; }
    #boot { display: flex; z-index: 100; }
    #portrait { display: none; z-index: 999; }
    h1 { color: #f3d78e; font-size: clamp(20px, 4vw, 30px); font-weight: 600; letter-spacing: .14em; margin: 0 0 12px; }
    p { color: #a7b8ad; line-height: 1.7; margin: 8px 0 16px; }
    button { background: #263b40; border: 1px solid #f3d78e; color: #e8e4cf; padding: 12px 24px; font: inherit; cursor: pointer; min-height: 48px; }
    button:disabled { opacity: .5; cursor: wait; }
    button:focus-visible { outline: 3px solid #e8e4cf; outline-offset: 4px; }
    #boot-start { min-width: 204px; }
    #failure { display: none; position: fixed; inset: 12px; z-index: 1000; padding: 16px; background: #16232b; border: 1px solid #cfa15f; text-align: center; overflow: auto; }
    #failure h2 { font-size: 20px; margin: 8px 0; }
    #failure details { margin: 16px auto 0; max-width: 650px; text-align: left; font-size: 12px; }
    #failure pre { white-space: pre-wrap; overflow-wrap: anywhere; }
    @media (orientation: portrait) { #portrait { display: flex; } }
  </style>
  <script src="https://cdn.jsdelivr.net/gh/kitao/pyxel@2.5.7/wasm/pyxel.js"></script>
</head>
<body>
  <div id="boot"><div><h1>冥界執行局</h1><p>３枚から１枚。おばけの元気を残して８回。<br>高い点をめざそう！</p><button id="boot-start" disabled>準備しています…</button><p id="boot-status" role="status">はじめの読み込みには時間がかかります。</p></div></div>
  <div id="portrait"><div><h1>冥界執行局</h1><p>スマートフォンを横向きにしてください。<br>おばけの元気を残して、８回選ぼう。</p></div></div>
  <div id="failure" role="alert"><h2>起動できませんでした</h2><p id="failure-message"></p><button onclick="location.reload()">もう一度ためす</button><details><summary>くわしいエラー</summary><pre id="failure-detail"></pre></details></div>
  <script>
    const boot = document.getElementById('boot');
    const startButton = document.getElementById('boot-start');
    let ready = false, failed = false;
    function showFailure(error) {
      if (failed) return;
      failed = true;
      boot.style.display = 'none';
      const message = String(error || '不明なエラー');
      document.getElementById('failure-message').textContent = /OpenGL|WebGL/i.test(message)
        ? 'このブラウザではゲームの画面を表示できませんでした。別のブラウザ、またはパソコンでお試しください。'
        : 'ゲームを起動できませんでした。もう一度ためしても動かない場合は、下のエラーを確認してください。';
      document.getElementById('failure-detail').textContent = message;
      document.getElementById('failure').style.display = 'block';
      const raw = document.getElementById('pyxel-error-overlay');
      if (raw) raw.hidden = true;
    }
    const observer = new MutationObserver(() => {
      if (failed) return;
      const raw = document.getElementById('pyxel-error-overlay');
      if (raw && raw.textContent.trim()) {
        showFailure(raw.textContent);
        return;
      }
      const prompt = document.getElementById('pyxel-prompt');
      if (prompt && !ready) {
        ready = true;
        startButton.disabled = false;
        startButton.textContent = 'はじめる';
        document.getElementById('boot-status').textContent = '準備できました。ボタンを押してください。';
      } else if (!prompt && ready && boot.isConnected) {
        boot.remove();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
    // The engine waits for a real body click/touch. The Japanese button bubbles
    // that gesture; do not start before its own prompt is present.
    startButton.addEventListener('keydown', event => {
      if (!startButton.disabled && (event.key === 'Enter' || event.key === ' ')) {
        event.preventDefault();
        startButton.click();
      }
    });
    if (typeof launchPyxel !== 'function') {
      showFailure('ゲームの実行ファイルを読み込めませんでした。');
    } else {
      launchPyxel({ command: 'play', name: 'game.pyxapp', gamepad: 'disabled', base64: 'PAYLOAD' }).catch(showFailure);
    }
  </script>
</body>
</html>
'''.replace('PAYLOAD',payload)
(root/'index.html').write_text(html)
print('Web build bytes:',len(html.encode()))
