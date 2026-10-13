#!/usr/bin/env python3
"""Render a wine profile page from a page.json file.

Usage: python3 render_page.py page.json out.html [--pdf out.pdf]

Everything (fonts, icons, logo, stylesheet) is read from ../assets and embedded,
so the HTML is one self-contained file. Wine Label-to-Profile Skill,
Corina-Bianca Gonteanu, CC BY-NC 4.0. See ../LICENSE.txt and ../licenses/.
"""
import base64, html, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "assets")
esc = html.escape

def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

RNG = "U+0100-02BA,U+1E00-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF"

def face(fam, w, fn, ext=False):
    ur = f"unicode-range:{RNG};" if ext else ""
    return (f"@font-face{{font-family:'{fam}';font-weight:{w};font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64(os.path.join(A,'fonts',fn))}) format('woff2');{ur}}}\n")

def fonts():
    return (face("Alata", 400, "alata-latin-400-normal.woff2")
            + face("Alata", 400, "alata-latin-ext-400-normal.woff2", True)
            + face("Cormorant Infant", 400, "cormorant-infant-latin-400-normal.woff2")
            + face("Cormorant Infant", 400, "cormorant-infant-latin-ext-400-normal.woff2", True)
            + face("Cormorant Infant", 600, "cormorant-infant-latin-600-normal.woff2")
            + face("Cormorant Infant", 600, "cormorant-infant-latin-ext-600-normal.woff2", True))

def icon(name):
    s = open(os.path.join(A, "icons", name + ".svg")).read()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", s, re.S).group(1).strip()
    inner = re.sub(r"\s+", " ", inner)
    return ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + inner + "</svg>")

ICONS = dict(scores="award", glass="wine", winemaking="grape", serving="bottle-wine",
             producer="warehouse", geography="map-pin", designation="shield-check",
             sources="book-open", pairing="utensils")

def logo():
    s = open(os.path.join(A, "logo.svg")).read()
    s = re.sub(r"<\?xml.*?\?>", "", s)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r'\s(sodipodi|inkscape):[a-z\-]+="[^"]*"', "", s)
    s = re.sub(r'\sxmlns:(sodipodi|inkscape|xlink|svg)="[^"]*"', "", s)
    s = s.replace("fill:#000000", "fill:currentColor")
    s = re.sub(r'\swidth="[^"]*"\s+height="[^"]*"', "", s, count=1)
    s = s.replace("<svg", '<svg class="logo" role="img" aria-label="WineFluent"', 1)
    return re.sub(r"\s+", " ", s)

def img_uri(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}.get(ext, "image/png")
    return f"data:{mime};base64,{b64(path)}"

def photo_uri(path):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        w = 224
        im = im.resize((w, round(im.height * w / im.width)))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        # Graceful fallback: embed raw image without resizing if Pillow is missing
        return img_uri(path)

def label(l):
    l = l.strip()
    return esc(l if l.endswith(":") else l + ":")

def value_html(row):
    v = row.get("value", "")
    if isinstance(v, dict) and "clusters" in v:
        out = ""
        for c in v["clusters"]:
            out += '<div class="cluster"><div class="ch">' + esc(c["heading"]) + "</div><ul>" \
                   + "".join(f"<li>{i}</li>" for i in c["items"]) + "</ul></div>"
        return out
    out = v or ""
    if row.get("limit"):
        out += ' <span class="min">(' + row["limit"] + ")</span>"
    return out

def rows_html(rows, cls="rows", PAIRLABEL=None):
    out = f'<dl class="{cls}">'
    for r in rows:
        if r.get("pairing"):
            out += '<div class="pair"><dt>' + icon("utensils") + label(r["label"]) + "</dt><dd>" + value_html(r) + "</dd></div>"
        else:
            out += "<div><dt>" + label(r["label"]) + "</dt><dd>" + value_html(r) + "</dd></div>"
    return out + "</dl>"

def sec(S, sid, body):
    return (f'<section id="{sid}"><h2>{icon(ICONS[sid])}<span>{esc(S["sections"][sid]["title"])}</span></h2>{body}</section>')

def render(P):
    S = json.load(open(os.path.join(A, "strings.en.json"), encoding="utf-8"))
    for k, v in (P.get("strings") or {}).items():
        if isinstance(v, dict) and isinstance(S.get(k), dict):
            for k2, v2 in v.items():
                if isinstance(v2, dict) and isinstance(S[k].get(k2), dict): S[k][k2].update(v2)
                else: S[k][k2] = v2
        else:
            S[k] = v
    sx = P.get("sections", {})
    date = P["date"]
    title = P["title"]
    notice = P.get("notice") or (S["notice"] if P.get("back_label") else S["notice_no_back"])
    h1 = esc(P["h1"])
    if P.get("h1_url"): h1 = f'<a href="{esc(P["h1_url"], quote=True)}">{h1}</a>'
    head = (f'<header class="top"><p class="quiet">{esc(notice)}</p><h1>{h1}</h1>'
            f'<p class="sub">{esc(P["subtitle"])}</p></header>')
    ph = P.get("photo")
    photo = ""
    if ph and ph.get("path"):
        photo = f'<img class="bottle" src="{photo_uri(ph["path"])}" alt="{esc(ph.get("alt",""), quote=True)}">'
    prow = rows_html(P["panel"], "rows compact")
    if photo:
        panel = f'<div class="panel"><div class="hero">{photo}<div style="flex:1;min-width:0">{prow}</div></div></div>'
    else:
        panel = f'<div class="panel solo"><div class="hero"><div style="flex:1;min-width:0">{prow}</div></div></div>'
    order = ["scores", "glass", "winemaking", "serving", "producer", "geography", "designation", "sources"]
    present = [s for s in order if sx.get(s)]
    nav = f'<nav class="toc" aria-label="{esc(S["toc_label"], quote=True)}">' + "".join(
        f'<a href="#{s}">{icon(ICONS[s])}{esc(S["sections"][s]["nav"])}</a>' for s in present) + "</nav>"
    body = ""
    for s in present:
        d = sx[s]
        if s in ("scores", "glass", "serving", "geography"):
            b = rows_html(d["rows"])
        elif s == "winemaking":
            b = rows_html(d["rows"]) + (f'<p class="gloss">{d["note"]}</p>' if d.get("note") else "")
        elif s == "producer":
            b = f'<p>{d.get("html","")}</p>'
        elif s == "designation":
            b = f'<p>{d["intro"]}</p>' if d.get("intro") else ""
            if d.get("table"):
                th = S["table_head"]; cl = S["cmp_labels"]
                b += ('<table class="cmp"><thead><tr>' + "".join(f"<th>{esc(x)}</th>" for x in th) + "</tr></thead><tbody>")
                for t in d["table"]:
                    b += (f'<tr><th scope="row" data-l="{esc(cl[0],quote=True)}">{t["requirement"]}</th>'
                          f'<td data-l="{esc(cl[1],quote=True)}">{t["meaning"]}</td>'
                          f'<td data-l="{esc(cl[2],quote=True)}">{t["this_wine"]}</td></tr>')
                b += "</tbody></table>"
            if d.get("seals"):
                b += '<dl class="rows" style="margin-top:14px">'
                for sl in d["seals"]:
                    qr = f'<img src="{img_uri(sl["qr"])}" alt="" style="width:84px;height:84px;margin-right:12px;float:left">' if sl.get("qr") else ""
                    b += f'<div><dt>{label(sl["label"])}</dt><dd>{qr}{sl["html"]}</dd></div>'
                b += "</dl>"
        elif s == "sources":
            b = (f'<p class="legend">{d["legend"]}</p>' if d.get("legend") else "") + '<ul class="audit">' + "".join(
                f'<li><b>{esc(i["label"].rstrip(":"))}:</b> {i["html"]}</li>' for i in d["items"]) + "</ul>"
        body += sec(S, s, b)
    foot = (f'<footer class="foot"><div class="brand">{logo()}</div>'
            f'<p>{esc(S["footer_made"])} <a href="https://about.me/corinagonteanu">Corina-Bianca Gonteanu</a> · '
            f'<a href="https://creativecommons.org/licenses/by-nc/4.0/">CC BY-NC 4.0</a> · '
            f'<a href="https://substack.com/@corinabianca">{esc(S["footer_follow"])}</a></p>'
            f'<p class="small">{esc(S["footer_generated"].format(date=date))} {esc(S["footer_logo_note"])}</p></footer>')
    css = fonts() + open(os.path.join(A, "page.css"), encoding="utf-8").read().replace(
        "__RUNNING__", f"{title} · {date}".replace('"', "'"))
    lang = esc(P.get("lang", "en"), quote=True)
    desc = esc(P.get("description") or f"Wine profile of {title}.", quote=True)
    return (f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="author" content="Corina-Bianca Gonteanu">'
            f'<meta name="description" content="{desc}">'
            f'<link rel="license" href="https://creativecommons.org/licenses/by-nc/4.0/">'
            f'<!-- Wine Label-to-Profile Skill by Corina-Bianca Gonteanu, CC BY-NC 4.0. Icons: Lucide (ISC). '
            f'Fonts: Alata and Cormorant Infant (SIL OFL 1.1). Aroma categories: Wine Aroma Wheel by Ann C. Noble, adapted; sparkling: InnoVinum. -->'
            f'<style>{css}</style></head><body><div class="wrap">{head}{panel}{nav}<main>{body}</main>{foot}</div></body></html>')

def make_pdf(html_path, pdf_path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.stderr.write("warning: playwright is not installed; skipping PDF generation.\n")
        return False
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            pg.goto("file://" + os.path.abspath(html_path))
            pg.pdf(path=pdf_path, format="A4", print_background=True, prefer_css_page_size=True)
            b.close()
        return True
    except Exception as e:
        sys.stderr.write(f"warning: PDF generation failed ({e}); skipping PDF.\n")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    P = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    open(out, "w", encoding="utf-8").write(render(P))
    print("wrote", out, os.path.getsize(out) // 1024, "kB")
    if "--pdf" in sys.argv:
        pdf = sys.argv[sys.argv.index("--pdf") + 1]
        if make_pdf(out, pdf):
            print("wrote", pdf)