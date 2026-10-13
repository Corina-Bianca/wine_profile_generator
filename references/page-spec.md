# Wine page specification

Wine Label-to-Profile Skill (/wine-page) by Corina-Bianca Gonteanu, CC BY-NC 4.0.
This document defines every section, row, and formatting rule of the generated wine profile page.

## Core rules

- Fixed structure: At a glance panel, Scores and awards, What's in the glass, Grapes and winemaking, Serving, storage and pairing, Producer, Geography, Designation and certifications (if applicable), Sources and limitations.
- Tone: No judgments, marketing puffery, or editorial praise. No taglines or section blurbs under titles. Factual rows and tables only; the winemaking note is the designated place for concise explanatory prose.
- Origin is geographical only (political and regional hierarchy; legal classification belongs in Designation).
- Exact-vintage rule: technical values, critic scores, tasting notes, bottle counts, and bottle photos must belong strictly to the bottle's vintage. Serving temperature, glassware, decanting, storage directions, pairing, occasion, and producer history may come from any vintage.
- Blank rows instead of guesses: applicable rows without verified facts remain empty strings (""). Never write "N/A" or "unknown".
- Display limits: producer's figure leads; designation limit follows in parentheses: (Grand Superior min. 12 months in wooden barrels).
- Never substitute the user's label photograph for the official bottle photo.

## Header & At a glance panel

Top of page contains:
- title: browser tab title and PDF running header, formatted strictly as `<Producer> <Wine> <Vintage>` without suffix or trailing text (matches the worked example and prevents header pollution).
- h1: wine name as printed on the label (or commercial name). If available, link to the producer's official wine page (h1_url).
- subtitle: formatted as `<Classification or style> · <Vintage> · <Place>` (e.g. Egri Bikavér Grand Superior · 2022 · Eger, Hungary).
- date: profile generation date written out in the page's language.
- photo: object {"path": "<path>", "alt": "<text>"} or null. Official bottle photo from producer tech sheet or retailer bottle listing strictly matching the exact vintage and label design. The renderer reads the "alt" key. If no verified bottle photo is downloadable, set to null and document under Sources in the "Not found" item.

Panel rows (strictly 8 rows in fixed order):
1. Producer: Producer name, linked to official website if available.
2. Wine: Full commercial wine name, including its designation or tier (e.g. Nagy-Eged Egri Bikavér Grand Superior).
3. Vintage: Harvest year as printed. Do not infer "NV" from the absence of a year; keep the label's own term if stated (e.g. 2019 · millesimato) or leave blank if undated.
4. Colour: White, Red, Rosé, Orange/Amber. Leave blank if not stated or unverifiable.
5. Origin: Country, region, subregion (geographical hierarchy only; a place-based designation may appear with its place, e.g. "PDO Eger, Hungary").
6. Style: Sweetness category (WSET scale) or legally defined style (e.g. Dry, Medium-dry, Tawny, Ruby); for sparkling wines, the dosage category as printed on the label (e.g. Brut Nature, Extra Brut, Brut).
7. Alcohol: Actual alcohol by volume from label or tech sheet (e.g. 14.0% vol). If missing from front label, use verified producer figure or an exact-vintage retailer/review listing.
8. Bottle size: Volume as stated, formatted as 75 cl (or matching label unit if non-standard).

## Scores and awards

Rows: Scores, Awards.
- Scores: Critic scores strictly and exclusively for the bottle's exact vintage, with the critic named and linked (e.g. 95 points, Falstaff). Cross-vintage critic scores are strictly forbidden. Reviews and tasting notes without numerical ratings are not scores.
- Awards: Awards won by the bottle's vintage. At most one mention of an exceptional award from another vintage may be included, explicitly labelled with that vintage (e.g. Decanter Best in Show (2020 vintage)).

## What's in the glass

Rows: Appearance, Aroma, Flavour, Mouthfeel, Finish, Aftertaste.
- Appearance: Colour depth, core shade, rim variation, and clarity. For sparkling wines, bubbles and bead as observed belong here.
- Aroma & Flavour: Structured as wheel clusters. Heading combines first tier and distinct second tier (e.g. Fruity · Berry). Bullets contain the source's exact descriptor words. Never invent categories; unplaced terms go to Other. Exclude cork taint (TCA).
- Mouthfeel: Acidity, tannin, body, alcohol warmth, and texture on standard scales (e.g. WSET Level 3 scale terms) or source words. Mousse texture (delicate, creamy, aggressive) belongs here for sparkling wines.
- Finish & Aftertaste: Length (short, medium(-), medium, medium(+), long) and persistent sensory notes.

## Grapes and winemaking

Rows: Grapes, Shares, Harvest, Fermentation, Maturation, Disgorgement, Barrel size, Alcohol, Residual sugar, Total acidity, Bottles.
- Pruning rules:
  - Delete Shares on single-variety wines.
  - Delete Disgorgement unless wine_type is sparkling.
  - Delete Barrel size when no barrel is used (e.g. tank, concrete, amphora).
- Maturation & Metrics: Report producer figure first; registered designation limit in parentheses if applicable.
- Winemaking note: Optional block beneath the table. In overview mode, it holds one short explanation of the designation and tier terms. In details mode, it is the designated place for concise explanatory prose explaining specific production techniques (e.g. skin contact, qvevri, whole-cluster pressing, batônnage).

## Serving, storage and pairing

Rows: Serving temperature, Glass, Decanting, Ageing potential, Storage, Pairing, Occasion.
- Serving temperature: Recommended serving range in °C (e.g. 16–18°C).
- Glass: Specific glassware recommendation (e.g. Bordeaux glass, Burgundy glass, flute, universal).
- Decanting: Recommended aeration time before pouring.
- Ageing potential: Banded per the reference file for the wine type (references/ageing-potential.md, references/sparkling.md, or references/fortified.md). Preserves source wording after a colon and includes optional WSET readiness statement.
- Storage: Two lines when sources provide them: closed bottle (temperature, position, light) and after opening (shelf life and conditions).
- Pairing: Must have "pairing": true in the JSON row. Specific culinary pairings. Producer recommendations lead, followed by specialized reviewer recommendations.
- Occasion: Stated only when the producer or a professional review specifies one; otherwise leave blank.

## Producer

- html: Concise factual overview. Wrap the producer name in `<span class="pname">…</span>` (styled by page.css). Include founding year, locality without street address, estate vineyard area, annual bottle production, and type or size of the estate. Do not list owner names, and do not include philosophical marketing claims.

## Geography

Rows: Country, Region, Zone, Site, Climate.
- Geographical, topographical, and climatic facts strictly for the vineyard origin (elevation, aspect, soil profile, macroclimate).

## Designation and certifications

Omit this entire section if the wine carries no registered geographical indication, PDO/PGI, or official certification.
- intro: Explains what the designation is, its classification tier, and governing registry authority. State the original-language legal term in HTML italics (e.g. <i>oltalom alatt álló eredetmegjelölés</i>), using the specification's own wording.
- table: 3-column verification matrix against official specification:
  - requirement: Legal rule from the product specification. Do not show a limit without a unit of expression (for example, volatile acidity must specify meq/l or g/l as stated in the product specification).
  - meaning: What the rule establishes.
  - this_wine: The wine's own verified factual value (e.g. 14.5% vol, 14 months).
- seals: Array of seal objects present on the packaging:
  - Each item must be an object: {"label": "<name>", "html": "<description>", "qr": "<path-or-null>"}.
  - qr: local file path to the extracted image of the QR code, or null. Never put a URL here (it will crash the renderer); put the decoded destination URL as a clickable link inside html.

## Sources and limitations

- legend: "Unattributed statements come from the producer or producer-submitted listings; reviews and press are named." Translated on non-English pages.
- items: Ordered list of consulted source objects (each with label and html):
  - Item 0: Must be labelled Match, detailing how the bottle and vintage were identified and overall confidence.
  - Subsequent items: Producer technical sheets, national wine register filings (fallback to eAmbrosia), retailer spec sheets, and exact-vintage critic reviews. Every link must be an opened, verified http:// or https:// URL.
  - Terms explained: The linked reference source used for the term and designation explanations (e.g. Wines of Hungary).
  - Not found: The final item in the list. Details verified limitations and any missing data points or assets that could not be verified (e.g. bottle photograph, exact residual sugar, bottle count). Do not narrate missing back-label declarations.