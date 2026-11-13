#!/usr/bin/env python3
"""Render an HTML file to a 1080x1080 PNG.  Usage: python3 tools/render.py in.html out.png"""
import sys, os, shutil
from playwright.sync_api import sync_playwright
src, out = os.path.abspath(sys.argv[1]), sys.argv[2]
exe = next((p for p in (shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser")) if p), None)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1080})
    pg.goto("file://" + src)
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    pg.screenshot(path=out)
    b.close()
print(out)
