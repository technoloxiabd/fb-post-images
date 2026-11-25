#!/usr/bin/env python3
"""Build a 1080x1080 branded post image from a small JSON spec.

Usage: python3 tools/make_post.py spec.json out.png

spec.json:
{
  "brand": "technoloxia" | "ornateit" | "cicio" | "cfde" | "vq",
  "style": "split" | "dark" | "side" | "accent" | "frame" | "poster" | "timeline" | "bands" | "duo" | "tiles" | "spot" | "diag" | "bubbles" | "editorial" | "stack" | "invert" | "ticket",
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

    elif style == "timeline":
        gap = {3: 40, 4: 26, 5: 14}.get(n, 26)
        css = f"""body{{background:#fff;color:{D}}}
.st{{position:absolute;left:0;top:0;bottom:0;width:20px;background:linear-gradient(180deg,{A},{D})}}
.w{{position:relative;height:100%;padding:58px 76px 52px 96px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}} .tag{{background:{A};color:#fff}}
h1{{margin-top:38px;font-size:62px;line-height:1.2;font-weight:700}} h1 em{{color:{POP}}}
.sub{{margin-top:10px;font-size:28px;color:#5b6470}}
.its{{position:relative;margin:auto 0;display:flex;flex-direction:column;gap:{gap}px}}
.its:before{{content:"";position:absolute;left:28px;top:30px;bottom:30px;width:4px;background:{A}40;border-radius:4px}}
.it{{position:relative;display:flex;gap:28px;align-items:center}}
.it b{{flex:none;width:60px;height:60px;border-radius:50%;background:{A};color:#fff;font-size:24px;display:flex;align-items:center;justify-content:center;border:5px solid #fff;box-shadow:0 0 0 3px {A}}}
.it:nth-child(even) b{{background:{D};box-shadow:0 0 0 3px {D}}}
.it h3{{font-size:32px;font-weight:700;line-height:1.25}} .it p{{font-size:24px;color:#5b6470;margin-top:2px}}
.foot{{background:{A}1c;border-radius:20px;padding:20px 28px;display:flex;justify-content:space-between;align-items:center;gap:24px}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:20px;font-weight:400;color:#5b6470}}
.web{{text-align:right;font-size:24px;font-weight:700;color:{A};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="mo" style="opacity:.10;left:45%;top:35%">{motif(M, A)}</div><div class="st"></div><div class="w"><div class="top">{logo()}<span class="tag">{tag}</span></div>
<h1>{head}</h1><div class="sub">{sub}</div><div class="its">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>"""

    elif style == "bands":
        css = f"""body{{background:#fff;color:{D};display:flex;flex-direction:column}}
.hd{{position:relative;background:linear-gradient(120deg,{A} 0%,{D} 115%);color:#fff;padding:50px 72px 40px;overflow:hidden}}
.hd>*{{position:relative}} .tag{{background:#fff;color:{A}}}
h1{{margin-top:26px;font-size:60px;line-height:1.22;font-weight:700}} h1 em{{color:{A2}}}
.sub{{margin-top:14px;font-size:28px;opacity:.95}}
.its{{flex:1;display:flex;flex-direction:column}}
.it{{flex:1;display:flex;flex-direction:row-reverse;justify-content:space-between;align-items:center;padding:0 72px;gap:30px}}
.it:nth-child(even){{background:#f0f3f6}}
.it b{{font-size:70px;line-height:1;font-weight:700;color:{A};opacity:.32}}
.it h3{{font-size:32px;font-weight:700;line-height:1.25}} .it p{{font-size:24px;color:#5b6470;margin-top:3px}}
.foot{{background:{D};color:#fff;padding:24px 72px;display:flex;justify-content:space-between;align-items:center;gap:24px}}
.fl{{display:flex;align-items:center;gap:24px}} .cta{{font-size:22px;font-weight:600}} .cta small{{display:block;font-size:18px;font-weight:400;opacity:.8}}
.web{{text-align:right;font-size:23px;font-weight:600;color:{A2};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="hd"><div class="mo" style="opacity:.28">{motif(M, "#ffffff")}</div><span class="tag">{tag}</span><h1>{head}</h1><div class="sub">{sub}</div></div>
<div class="its">{items_html(items)}</div>
<div class="foot"><div class="fl">{logo(pill=True, h=min(int(b["logo_h"]*.7), 54))}<div class="cta">{ft}<small>{fs}</small></div></div><div class="web">{cbr}</div></div>"""

    elif style == "duo":
        gap = {3: 26, 4: 18, 5: 12}.get(n, 18); pad = {3: 30, 4: 22, 5: 14}.get(n, 22)
        css = f"""body{{background:#fff;color:{D}}}
.l{{position:absolute;left:0;top:0;bottom:0;width:480px;padding:58px 40px 52px 60px;display:flex;flex-direction:column}}
.tag{{border:2px solid {A};color:{A};align-self:flex-start;margin-top:54px}}
h1{{margin-top:26px;font-size:52px;line-height:1.24;font-weight:700}} h1 em{{color:{POP}}}
.sub{{margin-top:18px;font-size:26px;color:#5b6470;line-height:1.4}}
.bt{{margin-top:auto}} .cta{{font-size:22px;font-weight:600}} .cta small{{display:block;font-size:19px;font-weight:400;color:#5b6470}}
.web{{margin-top:14px;font-size:24px;font-weight:700;color:{A};line-height:1.45}}
.r{{position:absolute;left:480px;right:0;top:0;bottom:0;background:linear-gradient(160deg,{A} 0%,{D2} 140%);border-radius:70px 0 0 70px;padding:0 54px 0 50px;display:flex;flex-direction:column;justify-content:center;gap:{gap}px;overflow:hidden}}
.it{{position:relative;background:#fff;border-radius:20px;padding:{pad}px 24px;display:flex;gap:20px;align-items:center;box-shadow:0 12px 30px rgba(0,0,0,.18)}}
.it b{{flex:none;width:54px;height:54px;border-radius:16px;background:{D};color:#fff;font-size:22px;display:flex;align-items:center;justify-content:center}}
.it h3{{font-size:29px;font-weight:700;line-height:1.25}} .it p{{font-size:22px;color:#5b6470;margin-top:2px;line-height:1.3}}"""
        body = f"""<div class="l">{logo()}<span class="tag">{tag}</span><h1>{head}</h1><div class="sub">{sub}</div><div class="bt"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>
<div class="r"><div class="mo" style="opacity:.25">{motif(M, "#ffffff")}</div>{items_html(items)}</div>"""

    elif style == "tiles":
        css = f"""body{{background:#f3f5f8;color:{D}}}
.w{{position:relative;height:100%;padding:56px 68px 50px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}} .tag{{background:{D};color:#fff}}
h1{{margin-top:32px;font-size:58px;line-height:1.22;font-weight:700}} h1 em{{color:{POP}}}
.sub{{margin-top:8px;font-size:28px;color:#5b6470}}
.its{{flex:1;margin:28px 0 26px;display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.it{{background:#fff;border-radius:26px;padding:26px 30px;display:flex;flex-direction:column;justify-content:center;box-shadow:0 8px 24px rgba(20,30,45,.07);overflow:hidden;position:relative}}
.it b{{font-size:58px;line-height:1;font-weight:700;color:{A};margin-bottom:12px}}
.it h3{{font-size:31px;font-weight:700;line-height:1.25}} .it p{{font-size:23px;color:#5b6470;margin-top:4px;line-height:1.3}}
.it:nth-child(1){{background:{A};color:#fff}} .it:nth-child(4){{background:{D};color:#fff}}
.it:nth-child(1) b,.it:nth-child(4) b{{color:#fff;opacity:.85}} .it:nth-child(1) p,.it:nth-child(4) p{{color:#fff;opacity:.88}}
.it:nth-child(3):last-child,.it:nth-child(5){{grid-column:1/-1}}
.foot{{display:flex;justify-content:space-between;align-items:center;gap:24px}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:20px;font-weight:400;color:#5b6470}}
.web{{text-align:right;font-size:24px;font-weight:700;color:{A};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="w"><div class="top">{logo()}<span class="tag">{tag}</span></div>
<h1>{head}</h1><div class="sub">{sub}</div><div class="its">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>"""

    elif style == "spot":
        cols = "1fr" if n == 3 else "1fr 1fr"
        css = f"""body{{background:#fff;color:{D}}}
.c{{position:absolute;right:-150px;top:-170px;width:860px;height:860px;border-radius:50%;background:linear-gradient(150deg,{D2} 0%,{D} 100%);overflow:hidden}}
.c2{{position:absolute;right:560px;top:500px;width:120px;height:120px;border-radius:50%;background:{A};opacity:.9}}
.hh{{position:absolute;right:64px;top:120px;width:520px;color:#fff}}
h1{{font-size:54px;line-height:1.24;font-weight:700}} h1 em{{color:{A2}}}
.sub{{margin-top:14px;font-size:26px;color:#dfe6ee;line-height:1.35}}
.lt{{position:absolute;left:64px;top:60px;width:330px}} .tag{{background:{A};color:#fff;margin-top:34px}}
.w{{position:absolute;left:0;right:0;top:668px;bottom:0;padding:0 64px 46px;display:flex;flex-direction:column}}
.its{{display:grid;grid-template-columns:{cols};gap:{18 if n == 3 else 30}px 34px;margin:auto 0}}
.it{{display:flex;gap:16px;align-items:center}}
.it:nth-child(5){{grid-column:1/-1}}
.it b{{flex:none;width:54px;height:54px;border-radius:14px;background:{A};color:#fff;font-size:22px;display:flex;align-items:center;justify-content:center}}
.it h3{{font-size:{34 if n == 3 else 31}px;font-weight:700;line-height:1.25}} .it p{{font-size:22px;color:#5b6470;margin-top:1px;line-height:1.3}}
.foot{{display:flex;justify-content:space-between;align-items:center;gap:24px;border-top:3px solid {A};padding-top:18px}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:19px;font-weight:400;color:#5b6470}}
.web{{text-align:right;font-size:24px;font-weight:700;color:{A};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="c"><div class="mo" style="opacity:.5">{motif(M, A)}</div></div><div class="c2"></div>
<div class="lt"><img src="file://{logo_path}" style="display:block;max-width:290px;max-height:96px"><br><span class="tag">{tag}</span></div>
<div class="hh"><h1>{head}</h1><div class="sub">{sub}</div></div>
<div class="w"><div class="its">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>"""

    elif style == "diag":
        cols = "1fr" if n == 3 else "1fr 1fr"
        css = f"""body{{background:#fff;color:{D}}}
.top{{position:absolute;left:68px;right:68px;top:52px;display:flex;justify-content:space-between;align-items:center}} .tag{{background:{A};color:#fff}}
.bd{{position:absolute;left:-90px;right:-90px;top:238px;height:330px;transform:rotate(-5deg);background:linear-gradient(100deg,{D} 0%,{D2} 100%);overflow:hidden;box-shadow:0 18px 40px rgba(0,0,0,.18)}}
.bi{{position:relative;height:100%;padding:0 170px;display:flex;flex-direction:column;justify-content:center;color:#fff}}
h1{{font-size:60px;line-height:1.2;font-weight:700}} h1 em{{color:{A2}}} .sub{{margin-top:8px;font-size:27px;color:#dfe6ee}}
.ac{{position:absolute;left:-90px;right:-90px;top:556px;height:16px;transform:rotate(-5deg);background:{A}}}
.w{{position:absolute;left:0;right:0;top:640px;bottom:0;padding:0 72px 48px;display:flex;flex-direction:column}}
.its{{margin:auto 0;display:grid;grid-template-columns:{cols};gap:{20 if n == 3 else 26}px 40px}}
.it{{display:flex;gap:18px;align-items:flex-start}}
.it:nth-child(5){{grid-column:1/-1}}
.it b{{flex:none;font-size:40px;line-height:1;font-style:italic;font-weight:700;color:{A};width:60px}}
.it h3{{font-size:{33 if n == 3 else 29}px;font-weight:700;line-height:1.25}} .it p{{font-size:22px;color:#5b6470;margin-top:2px;line-height:1.3}}
.foot{{display:flex;justify-content:space-between;align-items:center;gap:24px}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:19px;font-weight:400;color:#5b6470}}
.web{{text-align:right;font-size:24px;font-weight:700;color:{A};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="top">{logo()}<span class="tag">{tag}</span></div>
<div class="bd"><div class="mo" style="opacity:.6">{motif(M, A)}</div><div class="bi"><h1>{head}</h1><div class="sub">{sub}</div></div></div><div class="ac"></div>
<div class="w"><div class="its">{items_html(items)}</div><div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>"""

    elif style == "bubbles":
        sz = {3: 290, 4: 232, 5: 190}.get(n, 232); fz = {3: 30, 4: 25, 5: 21}.get(n, 25)
        css = f"""body{{background:#f4f7fa;color:{D}}}
.w{{position:relative;height:100%;padding:56px 64px 50px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}} .tag{{background:{D};color:#fff}}
h1{{margin-top:40px;font-size:60px;line-height:1.2;font-weight:700;text-align:center}} h1 em{{color:{POP}}}
.sub{{margin-top:10px;font-size:28px;color:#5b6470;text-align:center}}
.its{{margin:auto 0;display:flex;justify-content:center;align-items:flex-start}}
.it{{width:{sz}px;margin:0 -6px;text-align:center;position:relative}}
.it:nth-child(even){{margin-top:54px}}
.it>div{{}} .it b{{position:absolute;left:50%;top:26px;transform:translateX(-50%);font-size:24px;color:#fff;opacity:.8}}
.it h3{{width:{sz}px;height:{sz}px;border-radius:50%;background:{A};color:#fff;display:flex;align-items:center;justify-content:center;padding:36px 22px 20px;font-size:{fz}px;font-weight:700;line-height:1.25;box-shadow:0 14px 34px rgba(0,0,0,.16);border:8px solid #fff}}
.it:nth-child(even) h3{{background:{D}}}
.it p{{margin-top:14px;padding:0 10px;font-size:{22 if n < 5 else 19}px;color:#5b6470;line-height:1.3}}
.foot{{background:#fff;border-radius:22px;padding:20px 30px;display:flex;justify-content:space-between;align-items:center;gap:24px;box-shadow:0 8px 24px rgba(20,30,45,.07)}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:19px;font-weight:400;color:#5b6470}}
.web{{text-align:right;font-size:24px;font-weight:700;color:{A};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="mo" style="opacity:.10">{motif(M, A)}</div><div class="w"><div class="top">{logo()}<span class="tag">{tag}</span></div>
<h1>{head}</h1><div class="sub">{sub}</div><div class="its">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>"""

    elif style == "editorial":
        pad = {3: 30, 4: 22, 5: 14}.get(n, 22)
        css = f"""body{{background:#fbfaf7;color:{D}}}
.sb{{position:absolute;left:0;top:0;bottom:0;width:116px;background:{D};display:flex;align-items:center;justify-content:center;overflow:hidden}}
.sb span{{writing-mode:vertical-rl;transform:rotate(180deg);font-size:34px;font-weight:700;letter-spacing:6px;text-transform:uppercase;color:{A2};white-space:nowrap}}
.sb i{{position:absolute;left:0;right:0;bottom:0;height:150px;background:{A}}}
.w{{position:absolute;left:116px;right:0;top:0;bottom:0;padding:54px 64px 48px 60px;display:flex;flex-direction:column}}
.lg{{display:flex;justify-content:flex-end}}
.ov{{margin-top:26px;font-size:24px;font-weight:600;letter-spacing:1px;color:{A}}}
h1{{margin-top:10px;font-size:68px;line-height:1.14;font-weight:700}} h1 em{{color:{A}}}
.rl{{margin-top:26px;height:5px;background:{D}}}
.its{{margin:auto 0;display:flex;flex-direction:column}}
.it{{display:flex;gap:26px;align-items:baseline;padding:{pad}px 0;border-bottom:2px solid #ddd9d0}}
.it:last-child{{border-bottom:none}}
.it b{{flex:none;width:64px;font-size:30px;font-weight:600;color:#a8a294}}
.it>div{{flex:1;display:flex;justify-content:space-between;align-items:baseline;gap:24px}}
.it h3{{font-size:32px;font-weight:700;line-height:1.25}} .it p{{font-size:23px;color:#6a6558;text-align:right;line-height:1.3}}
.foot{{border-top:5px solid {D};padding-top:18px;display:flex;justify-content:space-between;align-items:center;gap:24px}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:19px;font-weight:400;color:#6a6558}}
.web{{text-align:right;font-size:24px;font-weight:700;color:{A};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="sb"><i></i><span>{tag}</span></div><div class="w"><div class="lg">{logo()}</div>
<div class="ov">{sub}</div><h1>{head}</h1><div class="rl"></div><div class="its">{items_html(items)}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>"""

    elif style == "stack":
        gap = {3: 30, 4: 20, 5: 12}.get(n, 20); pad = {3: 28, 4: 20, 5: 13}.get(n, 20)
        rot = [-1.8, 1.5, -1.2, 1.9, -1.5]; off = [0, 70, 24, 96, 40]
        cards = "".join(f'<div class="it" style="transform:rotate({rot[i]}deg);margin-left:{off[i]}px"><b>{i+1}</b><div><h3>{esc(it["title"])}</h3>' + (f'<p>{esc(it["text"])}</p>' if it.get("text") else "") + '</div></div>' for i, it in enumerate(items))
        css = f"""body{{background:linear-gradient(165deg,{A}30 0%,{A}0d 100%),#fff;color:{D}}}
.w{{position:relative;height:100%;padding:56px 68px 50px;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}} .tag{{background:{A};color:#fff}}
h1{{margin-top:34px;font-size:58px;line-height:1.2;font-weight:700}} h1 em{{color:{POP}}}
.sub{{margin-top:8px;font-size:28px;color:#4b5563}}
.its{{margin:auto 0;display:flex;flex-direction:column;gap:{gap}px;padding-left:20px}}
.it{{position:relative;width:800px;background:#fff;border-radius:22px;padding:{pad}px 30px {pad}px 62px;box-shadow:0 14px 34px rgba(20,30,45,.14)}}
.it b{{position:absolute;left:-24px;top:50%;margin-top:-34px;width:68px;height:68px;border-radius:50%;background:{D};color:#fff;font-size:28px;display:flex;align-items:center;justify-content:center;border:6px solid #fff}}
.it:nth-child(odd) b{{background:{A}}}
.it h3{{font-size:31px;font-weight:700;line-height:1.25}} .it p{{font-size:23px;color:#5b6470;margin-top:2px}}
.foot{{display:flex;justify-content:space-between;align-items:center;gap:24px}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:19px;font-weight:400;color:#4b5563}}
.web{{text-align:right;font-size:24px;font-weight:700;color:{D};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="mo" style="opacity:.12">{motif(M, A)}</div><div class="w"><div class="top">{logo(pill=True, h=min(int(b["logo_h"]*.82), 68))}<span class="tag">{tag}</span></div>
<h1>{head}</h1><div class="sub">{sub}</div><div class="its">{cards}</div>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div>"""

    elif style == "invert":
        cols = "1fr" if n == 3 else "1fr 1fr"
        css = f"""body{{background:#fff;color:{D}}}
.t{{position:absolute;left:0;right:0;top:0;height:560px;padding:52px 68px 0;display:flex;flex-direction:column}}
.top{{display:flex;justify-content:space-between;align-items:center}} .tag{{background:{A};color:#fff}}
.its{{margin:auto 0;display:grid;grid-template-columns:{cols};gap:{18 if n == 3 else 24}px 36px}}
.it{{display:flex;gap:18px;align-items:center}}
.it:nth-child(5){{grid-column:1/-1}}
.it b{{flex:none;width:54px;height:54px;border-radius:50%;border:4px solid {A};color:{A};font-size:22px;display:flex;align-items:center;justify-content:center}}
.it h3{{font-size:{33 if n == 3 else 28}px;font-weight:700;line-height:1.25}} .it p{{font-size:22px;color:#5b6470;margin-top:1px;line-height:1.3}}
.bt{{position:absolute;left:0;right:0;top:560px;bottom:0;background:linear-gradient(150deg,{D} 0%,{D2} 100%);border-radius:70px 70px 0 0;color:#fff;overflow:hidden}}
.bi{{position:relative;height:100%;padding:50px 68px 44px;display:flex;flex-direction:column}}
.ov{{font-size:25px;font-weight:600;color:{A2};letter-spacing:.5px}}
h1{{margin-top:10px;font-size:72px;line-height:1.16;font-weight:700}} h1 em{{color:{A2}}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:24px;border-top:2px solid rgba(255,255,255,.2);padding-top:18px}}
.cta{{font-size:24px;font-weight:600}} .cta small{{display:block;font-size:19px;font-weight:400;opacity:.8}}
.web{{text-align:right;font-size:24px;font-weight:700;color:{A2};line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="t"><div class="top">{logo()}<span class="tag">{tag}</span></div><div class="its">{items_html(items)}</div></div>
<div class="bt"><div class="mo" style="opacity:.6">{motif(M, A)}</div><div class="bi"><div class="ov">{sub}</div><h1>{head}</h1>
<div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div></div>"""

    elif style == "ticket":
        gap = {3: 26, 4: 16, 5: 9}.get(n, 16)
        css = f"""body{{background:linear-gradient(150deg,{D} 0%,{D2} 100%);color:{D}}}
.tk{{position:absolute;left:62px;right:62px;top:62px;bottom:62px;background:#fff;border-radius:36px;display:flex;flex-direction:column;box-shadow:0 26px 60px rgba(0,0,0,.35)}}
.a{{padding:44px 52px 30px}} .top{{display:flex;justify-content:space-between;align-items:center}} .tag{{background:{A};color:#fff}}
h1{{margin-top:30px;font-size:56px;line-height:1.2;font-weight:700}} h1 em{{color:{POP}}}
.sub{{margin-top:8px;font-size:27px;color:#5b6470}}
.cut{{position:relative;height:0;border-top:5px dashed #c5ccd6;margin:0 34px}}
.cut:before,.cut:after{{content:"";position:absolute;top:-30px;width:56px;height:56px;border-radius:50%;background:{D}}}
.cut:before{{left:-62px}} .cut:after{{right:-62px;background:{D2}}}
.b{{flex:1;padding:26px 52px 36px;display:flex;flex-direction:column}}
.its{{margin:auto 0;display:flex;flex-direction:column;gap:{gap}px}}
.it{{display:flex;gap:22px;align-items:center}}
.it b{{flex:none;width:58px;height:58px;border-radius:14px;background:{A}22;color:{A};font-size:24px;display:flex;align-items:center;justify-content:center}}
.it h3{{font-size:31px;font-weight:700;line-height:1.25}} .it p{{font-size:23px;color:#5b6470;margin-top:1px}}
.foot{{display:flex;justify-content:space-between;align-items:center;gap:24px;background:{A};color:#fff;border-radius:18px;padding:16px 26px}}
.cta{{font-size:23px;font-weight:600}} .cta small{{display:block;font-size:18px;font-weight:400;opacity:.9}}
.web{{text-align:right;font-size:23px;font-weight:700;line-height:1.4;white-space:nowrap}}"""
        body = f"""<div class="mo" style="opacity:.7">{motif(M, A)}</div><div class="tk"><div class="a"><div class="top">{logo()}<span class="tag">{tag}</span></div>
<h1>{head}</h1><div class="sub">{sub}</div></div><div class="cut"></div>
<div class="b"><div class="its">{items_html(items)}</div><div class="foot"><div class="cta">{ft}<small>{fs}</small></div><div class="web">{cbr}</div></div></div></div>"""

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
