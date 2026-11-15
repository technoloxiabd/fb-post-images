#!/usr/bin/env python3
"""Build a 1080x1080 branded post image from a small JSON spec.

Usage: python3 tools/make_post.py spec.json out.png

spec.json:
{
  "brand": "technoloxia" | "ornateit" | "cicio" | "cfde" | "vq",
  "style": "split" | "dark" | "side" | "accent" | "frame" | "poster",   # six different layouts
  "tag": "Website Tips",                    # short label (<= 22 chars)
  "headline": "line one\n*highlighted words* line two",   # max 2 lines
  "sub": "one short line under the headline",
  "items": [{"title": "...", "text": "..."}, ...],          # 3-5 items, text optional
  "footer_title": "...", "footer_sub": "...",
  "contact": ["+880 1671 43 79 32", "technoloxia.com"]      # 1-2 short lines
}
Each brand also has its own background motif (dots, grid, rings, arcs, stripes),
so the same style looks different from Page to Page.
"""
import sys, os, json, html, re, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANDS = {
 "technoloxia": dict(logo="technoloxia.png", logo_h=104, accent="#45a007", accent2="#7ddb2a", dark="#1c2633", dark2="#2f3d4a", motif="dots"),
 "ornateit":    dict(logo="ornateit-light.png", logo_h=70, accent="#1e8c3a", accent2="#5fd487", dark="#06180d", dark2="#14512b", motif="grid"),
 "cicio":       dict(logo="cicio-light.png", logo_h=112, accent="#05aaea", accent2="#5fd0fb", dark="#1c2633", dark2="#02232d", motif="rings"),
 "cfde":        dict(logo="cfde.png", logo_h=80, accent="#00709f", accent2="#8fd3f0", dark="#003f5c", dark2="#00709f", pop="#e9002e", motif="arcs"),
 "vq":          dict(logo="vq.png", logo_h=70, accent="#e8421a", accent2="#ff9a76", dark="#2f3136", dark2="#4a4d55", motif="stripes"),
}
F = "font-family:'Hind Siliguri','Poppins',sans-serif"

def esc(s): return html.escape(s or "")
def hl(s):
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", esc(s).replace("\n", "<br>"))

def motif(kind, c, seed=0):
    """Decorative background, different for every brand. c = colour."""
    if kind == "dots":
        pts = [(880, 90, 150, .9), (760, 250, 70, .6), (990, 300, 96, .4), (700, 70, 40, .5), (930, 470, 46, .35), (640, 200, 22, .5)]
        return "".join(f'<i style="position:absolute;left:{x+seed*7 % 60}px;top:{y}px;width:{r}px;height:{r}px;border-radius:50%;background:{c};opacity:{o}"></i>' for x, y, r, o in pts)
    if kind == "grid":
        return (f'<i style="position:absolute;inset:0;background-image:linear-gradient({c}22 1px,transparent 1px),linear-gradient(90deg,{c}22 1px,transparent 1px);background-size:54px 54px"></i>'
                f'<i style="position:absolute;right:-220px;top:-240px;width:680px;height:680px;border-radius:50%;background:radial-gradient(circle,{c}aa 0%,{c}00 70%)"></i>')
    if kind == "rings":
        return "".join(f'<i style="position:absolute;right:{-140-i*60}px;top:{-150-i*60}px;width:{420+i*120}px;height:{420+i*120}px;border-radius:50%;border:{22-i*5}px solid {c};opacity:{.55-i*.14}"></i>' for i in range(3))
    if kind == "arcs":
        return (f'<i style="position:absolute;right:-200px;top:-200px;width:560px;height:560px;border-radius:50%;background:{c};opacity:.35"></i>'
                f'<i style="position:absolute;right:120px;top:210px;width:170px;height:170px;border-radius:50%;background:{c};opacity:.22"></i>'
                f'<i style="position:absolute;left:-150px;bottom:-190px;width:420px;height:420px;border-radius:50%;border:44px solid {c};opacity:.22"></i>')
    if kind == "stripes":
        return (f'<i style="position:absolute;right:-160px;top:-60px;width:520px;height:520px;transform:rotate(18deg);background:repeating-linear-gradient(90deg,{c} 0 26px,transparent 26px 64px);opacity:.55"></i>')
    return ""

def items_html(items, cls="it"):
    return "".join(f'<div class="{cls}"><b>{i+1:02d}</b><div><h3>{esc(it["title"])}</h3>' + (f'<p>{esc(it["text"])}</p>' if it.get("text") else "") + '</div></div>' for i, it in enumerate(items))

def build(spec):
    b = BRANDS[spec["brand"]]; style = spec.get("style", "split")
    A, A2, D, D2 = b["accent"], b["accent2"], b["dark"], b["dark2"]; POP = b.get("pop", A)
    logo_path = os.path.join(ROOT, "logos", b["logo"])
    def logo(h=None, pill=False):
        img = f'<img src="file://{logo_path}" style="height:{h or b["logo_h"]}px;display:block">'
        return f'<div style="background:#fff;border-radius:18px;padding:14px 24px;display:inline-block">{img}</div>' if pill else img
    items = spec.get("items", [])[:5]; n = max(1, len(items))
    tag, head, sub = esc(spec.get("tag", "")), hl(spec["headline"]), esc(spec.get("sub", ""))
    ft, fs = esc(spec.get("footer_title", "")), esc(spec.get("footer_sub", ""))
    contact = spec.get("contact", [])[:2]; cbr = "<br>".join(esc(c) for c in contact)
    base = f'''*{{margin:0;padding:0;box-sizing:border-box}} i{{display:block}}
body{{width:1080px;height:1080px;overflow:hidden;position:relative;font-family:'Poppins','Hind Siliguri',sans-serif}}
h1,h3,p,.sub{{{F}}} h1 em{{font-style:normal}} .mo{{position:absolute;inset:0;overflow:hidden}}
.tag{{font-size:23px;font-weight:600;padding:10px 26px;border-radius:40px;white-space:nowrap;display:inline-block}}'''
    M = b["motif"]

    if style == "dark":
        gap = {3: 22, 4: 14, 5: 10}.get(n, 14); pad = {3: 26, 4: 14, 5: 9}.get(n, 14)
        css = f'''body{{background:linear-gradient(155deg,{D} 0%,{D2} 100%);color:#fff}}
.w{{position:relative;height:100%;padding:64px 72px 56px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}} .tag{{border:2px solid {A2};color:{A2};background:{D}}}
h1{{margin-top:36px;font-size:64px;line-height:1.2;font-weight:700}} h1 em{{color:{A2}}}
.sub{{margin-top:10px;font-size:29px;color:#d5dde6}}
.its{{margin-top:28px;display:flex;flex-direction:column;gap:{gap}px}}
.it{{display:flex;align-items:center;gap:22px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:{pad}px 24px}}
.it b{{flex:none;width:54px;height:54px;border-radius:14px;background:{A2};color:{D};font-size:24px;display:flex;align-items:center;justify-content:center}}
.it h3{{font-size:31px;font-weight:600;line-height:1.25}} .it p{{font-size:23px;color:#c5d0db;margin-top:2px}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:center;border-top:2px solid rgba(255,255,255,.18);padding-top:22px;gap:30px}}
.cta{{font-size:25px;font-weight:600}} .cta small{{display:block;font-size:20px;font-weight:400;color:#c5d0db}}
.web{{text-align:right;font-size:24px;font-weight:600;color:{A2};line-height:1.45;white-space:nowrap}}'''
        body = f'''<div class="mo">{motif(M, A)}</div><div class="w"><div class="top">{logo(pill=True, h=min(int(b["logo_h"]*.82), 68))}<span class="tag">{tag}</span></div>
<h1>{head}</h1><div class="sub">{sub}</div><div class="its">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>'''

    elif style == "side":
        gap = {3: 44, 4: 30, 5: 20}.get(n, 30)
        css = f'''body{{background:#fff;color:{D}}}
.l{{position:absolute;left:0;top:0;bottom:0;width:430px;background:linear-gradient(180deg,{D} 0%,{D2} 100%);color:#fff;padding:60px 44px 52px;display:flex;flex-direction:column;overflow:hidden}}
.l>*{{position:relative}} .tag{{background:{A2};color:{D};align-self:flex-start}}
h1{{margin-top:54px;font-size:50px;line-height:1.24;font-weight:700}} h1 em{{color:{A2}}}
.sub{{margin-top:20px;font-size:26px;color:#d5dde6;line-height:1.4}}
.web{{margin-top:auto;font-size:24px;font-weight:600;line-height:1.5;color:{A2}}}
.r{{position:absolute;left:430px;right:0;top:0;bottom:0;padding:52px 60px 0 56px;display:flex;flex-direction:column}}
.lg{{display:flex;justify-content:flex-end}}
.its{{flex:1;display:flex;flex-direction:column;justify-content:center;gap:{gap}px}}
.it{{display:flex;gap:24px;align-items:flex-start}}
.it b{{flex:none;font-size:54px;line-height:1;font-weight:700;color:{A};width:78px}}
.it h3{{font-size:32px;font-weight:700;line-height:1.25}} .it p{{font-size:24px;color:#5b6470;margin-top:4px;line-height:1.35}}
.bar{{margin:0 -60px 0 -56px;background:{A};color:#fff;padding:24px 56px;font-size:25px;font-weight:600}} .bar small{{display:block;font-size:20px;font-weight:400;opacity:.9}}'''
        body = f'''<div class="l"><div class="mo" style="opacity:.5">{motif(M, A2)}</div><span class="tag">{tag}</span><h1>{head}</h1><div class="sub">{sub}</div><div class="web">{cbr}</div></div>
<div class="r"><div class="lg">{logo()}</div><div class="its">{items_html(items)}</div><div class="bar">{ft}<small>{fs}</small></div></div>'''

    elif style == "accent":
        gap = {3: 30, 4: 22, 5: 14}.get(n, 22)
        css = f'''body{{background:linear-gradient(140deg,{A} 0%,{D2} 130%);color:#fff}}
.w{{position:relative;height:100%;padding:58px 64px 50px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}} .tag{{background:{D};color:#fff}}
h1{{margin-top:38px;font-size:62px;line-height:1.28;font-weight:700}} h1 em{{background:{D};padding:0 14px;border-radius:12px;box-decoration-break:clone;-webkit-box-decoration-break:clone}}
.sub{{margin-top:12px;font-size:28px;opacity:.95}}
.card{{margin-top:30px;flex:1;background:#fff;color:{D};border-radius:30px;padding:34px 40px;display:flex;flex-direction:column;justify-content:center;gap:{gap}px;box-shadow:0 20px 50px rgba(0,0,0,.22)}}
.it{{display:flex;gap:20px;align-items:center}}
.it b{{flex:none;width:50px;height:50px;border-radius:50%;background:{A};color:#fff;font-size:0;display:flex;align-items:center;justify-content:center}}
.it b:after{{content:"✓";font-size:28px}}
.it h3{{font-size:31px;font-weight:700;line-height:1.25}} .it p{{font-size:23px;color:#5b6470;margin-top:2px}}
.foot{{margin-top:26px;display:flex;justify-content:space-between;align-items:center;gap:30px}}
.cta{{font-size:25px;font-weight:600}} .cta small{{display:block;font-size:20px;font-weight:400;opacity:.9}}
.web{{text-align:right;font-size:24px;font-weight:700;line-height:1.45;white-space:nowrap}}'''
        body = f'''<div class="mo" style="opacity:.35">{motif(M, "#ffffff")}</div><div class="w"><div class="top">{logo(pill=True, h=min(int(b["logo_h"]*.82), 68))}<span class="tag">{tag}</span></div>
<h1>{head}</h1><div class="sub">{sub}</div><div class="card">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>'''

    elif style == "frame":
        cols = "1fr" if n == 3 else "1fr 1fr"
        css = f'''body{{background:#fff;color:{D}}}
.fr{{position:absolute;inset:26px;border:6px solid {A};border-radius:34px}}
.cn{{position:absolute;left:26px;top:26px;background:{A};color:#fff;border-radius:28px 0 28px 0;padding:16px 34px;font-size:23px;font-weight:600}}
.cn2{{position:absolute;right:26px;bottom:26px;width:150px;height:150px;background:{A};border-radius:120px 0 28px 0;opacity:.14}}
.w{{position:relative;height:100%;padding:112px 84px 70px;display:flex;flex-direction:column;align-items:center;text-align:center}}
h1{{margin-top:40px;font-size:60px;line-height:1.22;font-weight:700}} h1 em{{color:{POP}}}
.sub{{margin-top:12px;font-size:28px;color:#5b6470}}
.ln{{width:120px;height:6px;border-radius:6px;background:{A};margin-top:24px}}
.its{{margin-top:34px;width:100%;display:grid;grid-template-columns:{cols};gap:18px;text-align:left}}
.it{{display:flex;gap:18px;align-items:center;background:#f3f6f9;border-radius:18px;padding:{26 if n == 3 else 26}px 22px}}
.it:nth-child(5){{grid-column:1/-1}}
.it b{{flex:none;width:52px;height:52px;border-radius:14px;background:{A};color:#fff;font-size:22px;display:flex;align-items:center;justify-content:center}}
.it:nth-child(even) b{{background:{D}}}
.it h3{{font-size:{32 if n == 3 else 28}px;font-weight:700;line-height:1.25}} .it p{{font-size:22px;color:#5b6470;margin-top:2px;line-height:1.3}}
.foot{{margin-top:auto;width:100%;background:{D};color:#fff;border-radius:20px;padding:20px 30px;display:flex;justify-content:space-between;align-items:center;text-align:left;gap:24px}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:19px;font-weight:400;opacity:.8}}
.web{{text-align:right;font-size:23px;font-weight:600;color:{A2};line-height:1.4;white-space:nowrap}}'''
        body = f'''<div class="fr"></div><div class="cn">{tag}</div><div class="cn2"></div><div class="w">{logo()}
<h1>{head}</h1><div class="sub">{sub}</div><div class="ln"></div><div class="its">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>'''

    elif style == "poster":
        cols = "repeat(3,1fr)" if n == 3 else "1fr 1fr"
        css = f'''body{{background:#fff;color:{D}}}
.hero{{position:absolute;left:0;right:0;top:0;height:560px;background:linear-gradient(135deg,{D} 0%,{D2} 100%);color:#fff;clip-path:polygon(0 0,100% 0,100% 84%,0 100%);overflow:hidden}}
.hi{{position:relative;padding:60px 72px}} .tag{{background:{POP};color:#fff}}
h1{{margin-top:40px;font-size:74px;line-height:1.18;font-weight:700}} h1 em{{color:{A2}}}
.sub{{margin-top:14px;font-size:30px;color:#dfe6ee}}
.w{{position:absolute;left:0;right:0;top:560px;bottom:0;padding:22px 72px 50px;display:flex;flex-direction:column}}
.its{{margin:auto 0;display:grid;grid-template-columns:{cols};gap:{26 if n == 3 else 30}px {30 if n == 3 else 40}px}}
.it{{{"display:block" if n == 3 else "display:flex;gap:18px;align-items:flex-start"};border-top:5px solid {A};padding-top:14px}}
.it:nth-child(5){{grid-column:1/-1}}
.it b{{flex:none;font-size:{46 if n == 3 else 42}px;line-height:1;color:{A};font-weight:700;display:block;{"margin-bottom:10px" if n == 3 else "width:64px"}}}
.it h3{{font-size:{30 if n == 3 else 31}px;font-weight:700;line-height:1.28}} .it p{{font-size:23px;color:#5b6470;margin-top:4px;line-height:1.3}}
.foot{{display:flex;justify-content:space-between;align-items:center;gap:24px}}
.cta{{font-size:22px;font-weight:600;margin-top:8px}} .web{{text-align:right;font-size:24px;font-weight:700;color:{A};line-height:1.4;white-space:nowrap}}'''
        body = f'''<div class="hero"><div class="mo">{motif(M, A)}</div><div class="hi"><span class="tag">{tag}</span><h1>{head}</h1><div class="sub">{sub}</div></div></div>
<div class="w"><div class="its">{items_html(items)}</div>
<div class="foot"><div>{logo(h=int(b["logo_h"]*.8))}<div class="cta">{ft}</div></div><div class="web">{cbr}</div></div></div>'''

    else:  # split
        cards = (n == 4 and all(it.get("text") for it in items))
        pad = {3: 34, 4: 16, 5: 9}.get(n, 16); fsz = {3: 34, 4: 32, 5: 28}.get(n, 32)
        css = f'''body{{background:#f7f8fa;color:{D}}}
.head{{position:absolute;top:0;left:0;right:0;height:150px;background:#fff;display:flex;justify-content:space-between;align-items:center;padding:0 76px;border-bottom:6px solid {A}}}
.tag{{background:{POP};color:#fff}}
.band{{position:absolute;top:150px;left:0;right:0;height:330px;background:linear-gradient(135deg,{D} 0%,{D2} 100%);overflow:hidden}}
.w{{position:relative;padding:150px 76px 56px;height:100%;display:flex;flex-direction:column}}
.hero{{flex:none;height:330px;display:flex;flex-direction:column;justify-content:center;padding-right:230px;color:#fff}}
h1{{font-size:62px;line-height:1.22;font-weight:700}} h1 em{{color:{A2}}} .sub{{margin-top:10px;font-size:29px;color:#dfe6ee}}
.its{{margin-top:{36 if cards else 30}px;{"display:grid;grid-template-columns:1fr 1fr;gap:24px" if cards else "display:flex;flex-direction:column;gap:13px"}}}
.it{{background:#fff;display:flex;gap:20px;{"align-items:flex-start;border-radius:20px;padding:26px 28px;min-height:160px;border-bottom:5px solid "+A if cards else "align-items:center;border-radius:16px;padding:"+str(pad)+"px 24px;border-left:6px solid "+A};box-shadow:0 8px 26px rgba(20,30,45,.09)}}
.it b{{flex:none;width:54px;height:54px;border-radius:50%;background:{A};color:#fff;font-size:22px;display:flex;align-items:center;justify-content:center}}
.it:nth-child(even) b{{background:{D}}}
.it h3{{font-size:{30 if cards else fsz}px;font-weight:700;line-height:1.25}} .it p{{font-size:23px;color:#5b6470;margin-top:5px;line-height:1.35}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:30px;border-top:2px solid #dfe3e8;padding-top:22px}}
.cta{{font-size:25px;font-weight:600}} .cta small{{display:block;font-size:20px;font-weight:400;color:#5b6470}}
.web{{text-align:right;font-size:24px;font-weight:600;color:{A};line-height:1.45;white-space:nowrap}}'''
        body = f'''<div class="band"><div class="mo" style="left:40%">{motif(M, A2)}</div></div><div class="head">{logo()}<span class="tag">{tag}</span></div>
<div class="w"><div class="hero"><h1>{head}</h1><div class="sub">{sub}</div></div><div class="its">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>'''

    return f'<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{ROOT}/fonts/fonts.css"><style>{base}\n{css}</style></head><body>{body}</body></html>'

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(build(spec)); tmp = f.name
    subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "render.py"), tmp, sys.argv[2]])
