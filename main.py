#!/usr/bin/env python3
"""Entrypoint: copy the committed entry.png to the harness output dir.

The image is pre-rendered by generate.py (Pillow is not guaranteed in the
harness environment, and the repo may be mounted read-only), so this
script only copies bytes. The target directory comes from
$MAKEFUN_OUTPUT_DIR, default /output.
"""
from pathlib import Path
import os

OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
SRC = Path(__file__).resolve().parent / "entry.png"

OUT_DIR.mkdir(parents=True, exist_ok=True)
target = OUT_DIR / "entry.png"
data = SRC.read_bytes()
target.write_bytes(data)
