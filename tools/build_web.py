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
  <meta name="game-version" content="0.4.0">
  <title>冥界執行局 — 架空処刑ローグライト</title>
  <style>
    html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #0a1015; color: #e8e4cf; font-family: system-ui, sans-serif; }
    #pyxel-screen { position: fixed !important; inset: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left); width: auto !important; height: auto !important; background: #0a1015 !important; }
    #canvas { image-rendering: pixelated; touch-action: none; }
    #pyxel-prompt { opacity: 0; }
    #portrait, #boot { position: fixed; inset: 0; background: #0a1015; align-items: center; justify-content: center; text-align: center; padding: 16px; box-sizing: border-box; }
    #boot { display: flex; z-index: 100; background: radial-gradient(ellipse at 50% 40%, #263b40 0, #0a1015 70%); }
    .invitation { max-width: 560px; padding: clamp(20px, 4vw, 44px); border: 1px solid #52665f; box-shadow: 0 0 0 8px #0a1015, 0 0 0 9px #32564e; }
    .eyebrow { font-size: 11px; letter-spacing: .24em; color: #cfa15f; margin-bottom: 22px; }
    .seal { width: 42px; height: 42px; border: 1px solid #cfa15f; margin: 0 auto 22px; transform: rotate(45deg); display: grid; place-items: center; }
    .seal span { transform: rotate(-45deg); color: #f3d78e; }
    .small { font-size: 12px; color: #a7b8ad; }
    #failure a { color: #f3d78e; display: inline-block; padding: 12px; }
    #failure [hidden] { display: none !important; }
    #failure input { display: block; box-sizing: border-box; width: min(100%, 650px); margin: 14px auto; padding: 12px; background: #0a1015; color: #e8e4cf; border: 1px solid #52665f; }
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

</head>
<body>
  <div id="boot"><div class="invitation"><div class="eyebrow">UNDERWORLD BUREAU · CASE 008</div><div class="seal" aria-hidden="true"><span>冥</span></div><h1>冥界執行局</h1><p>点を取ると、おばけの元気がへる。<br>休みながら８回選んで、＋20点をめざそう。</p><button id="boot-start" disabled>準備しています…</button><p id="boot-status" role="status">はじめの読み込みには時間がかかります。</p><div class="small">架空のおばけと不思議な刑の、短いスコアアタック。</div></div></div>
  <div id="portrait"><div><h1>冥界執行局</h1><p>スマートフォンを横向きにしてください。<br>おばけの元気を残して、８回選ぼう。</p></div></div>
  <div id="failure" role="alert"><h2>起動できませんでした</h2><p id="failure-message"></p><button id="retry" onclick="location.reload()">もう一度読み込む</button> <button id="copy-link" hidden>リンクをコピー</button><p id="copy-status" role="status"></p><input id="game-link" aria-label="別のブラウザで開くゲームのリンク" readonly hidden><a href="https://github.com/jirodasu/underworld-execution-rogue#readme">遊び方・PC版の起動方法</a><details><summary>くわしいエラー</summary><pre id="failure-detail"></pre></details></div>
  <script>
    const boot = document.getElementById('boot');
    const startButton = document.getElementById('boot-start');
    let ready = false, failed = false;
    const loadingTimeout = setTimeout(() => showFailure('読み込みが60秒以内に終わりませんでした。通信を確認して、もう一度読み込んでください。'), 60000);
    const link = document.getElementById('game-link');
    link.value = location.href.split('#')[0];
    document.getElementById('copy-link').addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(link.value);
        document.getElementById('copy-status').textContent = 'コピーしました。SafariやChromeを開き、アドレス欄にはりつけてください。';
      } catch (_) {
        link.hidden = false;
        link.focus(); link.select();
        document.getElementById('copy-status').textContent = '下のリンクを選んでコピーし、別のブラウザで開いてください。';
      }
    });
    function showFailure(error) {
      if (failed) return;
      failed = true;
      clearTimeout(loadingTimeout);
      boot.style.display = 'none';
      const message = String(error || '不明なエラー');
      const graphicsError = /OpenGL|WebGL/i.test(message);
      document.getElementById('copy-link').hidden = !graphicsError;
      document.getElementById('retry').hidden = graphicsError;
      if (graphicsError) link.hidden = false;
      document.getElementById('failure-message').textContent = graphicsError
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
        clearTimeout(loadingTimeout);
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
    const runtime = document.createElement('script');
    runtime.src = 'https://cdn.jsdelivr.net/gh/kitao/pyxel@2.5.7/wasm/pyxel.js';
    runtime.onerror = () => showFailure('ゲームの実行ファイルを読み込めませんでした。通信を確認してください。');
    runtime.onload = () => {
      if (failed) return;
      if (typeof launchPyxel !== 'function') {
        showFailure('ゲームの実行ファイルを読み込めませんでした。');
      } else {
        launchPyxel({ command: 'play', name: 'game.pyxapp', gamepad: 'disabled', base64: 'PAYLOAD' }).catch(showFailure);
      }
    };
    document.head.appendChild(runtime);
  </script>
</body>
</html>
'''.replace('PAYLOAD',payload)
(root/'index.html').write_text(html)
print('Web build bytes:',len(html.encode()))
