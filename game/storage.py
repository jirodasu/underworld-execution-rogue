"""Best score only; failure to save never blocks a run."""
import json
import sys
from pathlib import Path
KEY = 'underworld-bureau-v3'

def load():
    try:
        if sys.platform == 'emscripten':
            import js
            value = js.window.localStorage.getItem(KEY)
        else:
            value = (Path.home()/'.underworld-bureau-v3.json').read_text()
        data = json.loads(str(value))
        return max(0, int(data.get('best', 0)))
    except Exception:
        return 0

def save(best):
    try:
        value = json.dumps({'best': int(best)})
        if sys.platform == 'emscripten':
            import js
            js.window.localStorage.setItem(KEY, value)
        else:
            (Path.home()/'.underworld-bureau-v3.json').write_text(value)
        return True
    except Exception:
        return False
