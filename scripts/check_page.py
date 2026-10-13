#!/usr/bin/env python3
"""Check a page.json against the skill's fixed rules before rendering.

Usage: python3 check_page.py page.json
Exit code 0 = no errors (warnings may remain), 1 = errors.
Wine Label-to-Profile Skill, Corina-Bianca Gonteanu, CC BY-NC 4.0.
"""
import json, re, sys
from html.parser import HTMLParser

FIRST = {"Fruity": ["Citrus", "Berry", "Tree fruit", "Tropical fruit", "Fruit (dried/cooked)", "Other"],
 "Floral": [], "Spicy": [], "Herbaceous": ["Fresh", "Dried"], "Vegetable": ["Fresh", "Canned/cooked"],
 "Nutty": [], "Caramel": [], "Woody": ["Resinous", "Phenolic", "Burned"], "Earthy": ["Moldy"],
 "Chemical": ["Petroleum", "Sulfur", "Pungent"], "Oxidized": [], "Microbiological": ["Yeasty", "Lactic", "Other"], "Other": []}
SPARK = {"Fruity": ["Citrus", "Berry", "Tree fruit", "Melon", "Tropical fruit", "Cooked fruit", "Artificial fruit"],
 "Floral": [], "Spicy": [], "Herbaceous": ["Fresh", "Dried"], "Vegetable": ["Fresh", "Canned/cooked"],
 "Nutty": ["Fresh", "Toasted"], "Caramelized": ["Caramel", "Burned"], "Creamy": [], "Yeasty": ["Fresh yeast"],
 "Woody": ["Resinous"], "Earthy": [], "Microbial": ["Lactic"], "Oxidized": [],
 "Chemical": ["Alcohol", "Pungent", "Papery", "Soapy", "Petroleum", "Sulfur"], "Other": []}
SECTIONS = ["scores", "glass", "winemaking", "serving", "producer", "geography", "designation", "sources"]
REQUIRED = ["scores", "glass", "winemaking", "serving", "producer", "geography", "sources"]
errors, warns = [], []
def err(m): errors.append(m)
def warn(m): warns.append(m)

class Bal(HTMLParser):
    VOID = {"br", "img", "hr", "wbr"}
    def __init__(s): super().__init__(); s.st = []; s.bad = False; s.links = []
    def handle_starttag(s, t, a):
        if t not in s.VOID: s.st.append(t)
        if t == "a":
            h = dict(a).get("href", "")
            s.links.append(h)
    def handle_endtag(s, t):
        if t in s.VOID: return
        if s.st and s.st[-1] == t: s.st.pop()
        else: s.bad = True

def frag(path, text):
    if not isinstance(text, str): return
    p = Bal(); p.feed(text)
    if p.bad or p.st: err(f"{path}: unbalanced HTML")
    for h in p.links:
        h_clean = h.strip()
        if not re.match(r"^https?://", h_clean, re.I):
            err(f"{path}: link is not http(s): {h!r}")
    if re.search(r"\b(N/A|n/a|N/a)\b", text): err(f"{path}: 'N/A' text is not allowed (leave the value blank)")
    if re.search(r"\bvegetative\b", text, re.I): err(f"{path}: 'vegetative' is not used (Herbaceous / Vegetable)")

def walk_rows(path, rows):
    for i, r in enumerate(rows):
        lab = r.get("label", "")
        if not str(lab).strip(): err(f"{path}[{i}]: empty label")
        v = r.get("value", "")
        if isinstance(v, dict): continue
        frag(f"{path}[{i}] {lab}", v); frag(f"{path}[{i}] {lab} (limit)", r.get("limit", ""))

def main(f):
    P = json.load(open(f, encoding="utf-8"))
    for k in ("date", "title", "h1", "subtitle", "panel", "sections"):
        if not P.get(k): err(f"missing or empty: {k}")
    wt = P.get("wine_type", "still")
    raw_lang = P.get("lang")
    lang = (raw_lang or "en").lower()
    is_en = lang.startswith("en")
    
    if wt not in ("still", "sparkling", "fortified"): err("wine_type must be still, sparkling or fortified")
    S = P.get("sections", {})
    for s in REQUIRED:
        if s not in S: err(f"missing section: {s}")
    for s in S:
        if s not in SECTIONS: err(f"unknown section: {s}")
    
    panel = P.get("panel", [])
    if len(panel) != 8:
        err(f"panel must contain exactly 8 rows, got {len(panel)}")
    if is_en:
        labels = [r.get("label", "").rstrip(":") for r in panel]
        want = ["Producer", "Wine", "Vintage", "Colour", "Origin", "Style", "Alcohol", "Bottle size"]
        if labels != want: err(f"panel rows must be exactly {want} in this order, got {labels}")
    walk_rows("panel", panel)

    for s in ("scores", "glass", "winemaking", "serving", "geography"):
        if s in S: walk_rows(s, S[s].get("rows", []))
    
    heads = FIRST if wt in ("still", "fortified") else SPARK
    for r in S.get("glass", {}).get("rows", []):
        v = r.get("value")
        if isinstance(v, dict):
            seen = []
            for c in v.get("clusters", []):
                h = c.get("heading", "")
                if not h:
                    err(f"glass {r.get('label')}: cluster missing heading")
                    continue
                if is_en:
                    a, _, b = h.partition(" · ")
                    if a not in heads or (b and b not in heads[a]): err(f"glass {r['label']}: heading {h!r} is not on the {wt} wheel")
                if not c.get("items"): err(f"glass {r.get('label')}: heading {h!r} has no entries")
                a, _, _ = h.partition(" · ")
                seen.append(a)
            if is_en:
                order = list(heads)
                idx = [order.index(a) for a in seen if a in order]
                if idx != sorted(idx): warn(f"glass {r['label']}: headings are not in the fixed display order")
                
    ap = [r for r in S.get("serving", {}).get("rows", []) if r.get("label", "").rstrip(":") in ("Ageing potential", "Potențial de învechire")]
    if not ap and "serving" in S:
        ap_candidates = S.get("serving", {}).get("rows", [])
        if len(ap_candidates) >= 4:
            ap = [ap_candidates[3]]
    if wt in ("sparkling", "fortified") and ap and ap[0].get("value") and not re.search(r"\((from|counted from|de la) ", ap[0]["value"], re.I):
        warn("Ageing potential: sparkling and fortified values name the starting point in brackets, e.g. (from disgorgement)")

    pr = [r for r in S.get("serving", {}).get("rows", []) if r.get("pairing")]
    if len(pr) != 1: err("serving needs exactly one Pairing row with pairing:true")
    if "producer" in S: frag("producer", S["producer"].get("html", ""))
    if "winemaking" in S: frag("winemaking note", S["winemaking"].get("note", ""))
    d = S.get("designation")
    if d:
        frag("designation intro", d.get("intro", ""))
        for i, t in enumerate(d.get("table", [])):
            for k in ("requirement", "meaning", "this_wine"): frag(f"designation table[{i}].{k}", t.get(k, ""))
    src = S.get("sources", {})
    items = src.get("items", [])
    if not items:
        err("sources must contain items")
    elif is_en and items[0].get("label", "").rstrip(":") != "Match":
        err("sources must start with a Match item")
    for i, it in enumerate(items):
        frag(f"sources[{i}]", it.get("html", ""))
        if re.search(r"\b(not used|was not used|were not used)\b", it.get("html", ""), re.I): err(f"sources[{i}]: do not list what was not used")
    if not any("href" in it.get("html", "") for it in items): warn("sources has no links")
    if P.get("photo") and not (P["photo"] or {}).get("path"): err("photo needs a path")
    for w in warns: print("warning:", w)
    for e in errors: print("ERROR:", e)
    print(f"{len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))