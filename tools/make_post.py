#!/usr/bin/env python3
"""Build a 1080x1080 branded post image from a small JSON spec.

Usage: python3 tools/make_post.py spec.json out.png

spec.json:
{
  "brand": "technoloxia" | "ornateit" | "cicio" | "cfde" | "vq",
  "tag": "Website Tips",                    # short label, top right (<= 22 chars)
  "headline": "আপনার Website কি *ধীরে লোড* হয়?",  # *...* = highlighted words; "\n" = line break (max 2 lines, ~22 chars each)
  "sub": "দ্রুত করার সহজ ৪টি উপায়",          # one short line under the headline
  "layout": "cards" | "list",               # cards = 2x2 grid (4 items), list = rows (3-5 items)
  "items": [{"title": "ছবি Compress করুন", "text": "WebP format সবচেয়ে ভালো"}, ...],  # text optional; keep titles <= 24 chars
  "footer_title": "Web Design • WordPress • Hosting",
  "footer_sub": "Reliable & cost-effective IT solutions",
  "contact": ["+880 1671 43 79 32", "technoloxia.com"]   # 1-2 short lines
}
"""
import sys, os, json, html, re, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANDS = {
 "technoloxia": dict(logo="technoloxia.png", logo_h=104, accent="#45a007", accent2="#6fd11f", dark="#1c2633", dark2="#2a363f"),
 "ornateit":    dict(logo="ornateit-light.png", logo_h=72, accent="#1e8c3a", accent2="#5fd487", dark="#06180d", dark2="#14512b"),
 "cicio":       dict(logo="cicio-light.png", logo_h=118, accent="#05aaea", accent2="#4cc8f7", dark="#1c2633", dark2="#02232d"),
 "cfde":        dict(logo="cfde.png", logo_h=84, accent="#00709f", accent2="#6ec1e4", dark="#004e6f", dark2="#00709f", pop="#e9002e"),
 "vq":          dict(logo="vq.png", logo_h=74, accent="#e8421a", accent2="#ff7a52", dark="#2f3136", dark2="#4a4d55"),
}
def esc(s): return html.escape(s or "")
def hl(s):
    s = esc(s).replace("\n", "<br>")
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
def build(spec):
    b = BRANDS[spec["brand"]]
    logo = os.path.join(ROOT, "logos", b["logo"])
    logo_html = f'<img src="file://{logo}" style="height:{b["logo_h"]}px">' if os.path.exists(logo) else f'<div class="tlogo">{esc(spec.get("brand_name", spec["brand"]))}</div>'
    items = spec.get("items", [])
    layout = spec.get("layout", "cards" if len(items) == 4 else "list")
    if layout == "cards":
        body = '<div class="grid">' + "".join(
            f'<div class="card"><div class="num">{i+1}</div><div><h3>{esc(it["title"])}</h3>' + (f'<p>{esc(it["text"])}</p>' if it.get("text") else "") + '</div></div>'
            for i, it in enumerate(items[:4])) + '</div>'
    else:
        n = max(1, min(len(items), 5)); fs = {1: 36, 2: 36, 3: 34, 4: 32, 5: 28}[n]
        pad = {1: 40, 2: 40, 3: 34, 4: 16, 5: 9}[n]
        body = f'<div class="list" style="font-size:{fs}px">' + "".join(
            f'<div class="row" style="padding-top:{pad}px;padding-bottom:{pad}px"><div class="num">{i+1}</div><div><h3>{esc(it["title"])}</h3>' + (f'<p>{esc(it["text"])}</p>' if it.get("text") else "") + '</div></div>'
            for i, it in enumerate(items[:5])) + '</div>'
    contact = "<br>".join(esc(c) for c in spec.get("contact", [])[:2])
    pop = b.get("pop", b["accent"])
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="file://{ROOT}/fonts/fonts.css"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;font-family:'Poppins','Hind Siliguri',sans-serif;background:#f7f8fa;color:{b["dark"]};overflow:hidden;position:relative}}
.head{{position:absolute;top:0;left:0;right:0;height:150px;background:#fff;display:flex;justify-content:space-between;align-items:center;padding:0 76px;border-bottom:6px solid {b["accent"]}}}
.tlogo{{font-weight:700;font-size:40px;color:{b["dark"]}}}
.tag{{font-size:23px;font-weight:600;background:{pop};color:#fff;padding:10px 26px;border-radius:40px;white-space:nowrap}}
.band{{position:absolute;top:150px;left:0;right:0;height:330px;background:linear-gradient(135deg,{b["dark"]} 0%,{b["dark2"]} 100%);overflow:hidden}}
.dot{{position:absolute;border-radius:50%;background:{b["accent2"]}}}
.wrap{{position:relative;padding:150px 76px 56px;height:100%;display:flex;flex-direction:column}}
.hero{{flex:none;height:330px;display:flex;flex-direction:column;justify-content:center;padding-right:230px}}
h1{{color:#fff;font-family:'Hind Siliguri','Poppins';font-weight:700;font-size:62px;line-height:1.22}}
h1 em{{font-style:normal;color:{b["accent2"]}}}
.sub{{margin-top:10px;color:#dfe6ee;font-family:'Hind Siliguri','Poppins';font-size:29px}}
.grid{{margin-top:36px;display:grid;grid-template-columns:1fr 1fr;gap:24px}}
.card{{background:#fff;border-radius:20px;padding:26px 28px;box-shadow:0 10px 30px rgba(20,30,45,.10);display:flex;gap:20px;align-items:flex-start;min-height:160px;border-bottom:5px solid {b["accent"]}}}
.row .num{{width:52px;height:52px;font-size:25px}}
.num{{flex:none;width:58px;height:58px;border-radius:50%;background:{b["accent"]};color:#fff;font-family:'Poppins';font-weight:700;font-size:28px;display:flex;align-items:center;justify-content:center}}
.card:nth-child(even) .num,.row:nth-child(even) .num{{background:{b["dark"]}}}
h3{{font-family:'Hind Siliguri','Poppins';font-size:1em;font-weight:700;line-height:1.25}}
.card h3{{font-size:30px}}
.card p,.row p{{margin-top:5px;font-family:'Hind Siliguri','Poppins';font-size:23px;font-weight:400;color:#5b6470;line-height:1.35}}
.list{{margin-top:30px;display:flex;flex-direction:column;gap:13px}}
.row{{background:#fff;border-radius:16px;padding:16px 24px;box-shadow:0 8px 24px rgba(20,30,45,.08);display:flex;gap:20px;align-items:center;border-left:6px solid {b["accent"]}}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:30px;border-top:2px solid #dfe3e8;padding-top:22px}}
.cta{{font-size:25px;font-weight:600;font-family:'Poppins','Hind Siliguri'}}
.cta small{{display:block;font-size:20px;font-weight:400;color:#5b6470;margin-top:2px}}
.web{{text-align:right;font-size:24px;font-weight:600;color:{b["accent"]};line-height:1.45;white-space:nowrap}}
</style></head><body>
<div class="band"><div class="dot" style="width:150px;height:150px;right:60px;top:36px;opacity:.9"></div><div class="dot" style="width:70px;height:70px;right:232px;top:150px;opacity:.6"></div><div class="dot" style="width:44px;height:44px;right:200px;top:56px;opacity:.45"></div><div class="dot" style="width:90px;height:90px;right:36px;top:215px;opacity:.4"></div></div>
<div class="head">{logo_html}<div class="tag">{esc(spec.get("tag",""))}</div></div>
<div class="wrap"><div class="hero"><h1>{hl(spec["headline"])}</h1><div class="sub">{esc(spec.get("sub",""))}</div></div>
{body}
<div class="foot"><div class="cta">{esc(spec.get("footer_title",""))}<small>{esc(spec.get("footer_sub",""))}</small></div><div class="web">{contact}</div></div>
</div></body></html>'''
if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(build(spec)); tmp = f.name
    subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "render.py"), tmp, sys.argv[2]])
