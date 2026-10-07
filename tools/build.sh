#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m unittest discover -s tests
python -m pyxel package game game/main.py
python -m pyxel app2html game.pyxapp
mv game.html index.html
