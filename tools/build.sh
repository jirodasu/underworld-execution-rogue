#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python tools/build_fonts.py
python -m unittest discover -s tests
python -m pyxel package game game/main.py
python tools/build_web.py
