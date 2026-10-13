# Wine Label-to-Profile Skill

`/wine-page [overview|details] [lang]` turns a photo of a wine's front label into a finished wine profile: one self-contained HTML page (readable on a phone, printable on A4, PDF if a headless browser is available) with a fixed structure, researched facts and checked links.

By Corina-Bianca Gonteanu · [about.me](https://about.me/corinagonteanu) · [Substack](https://substack.com/@corinabianca) (a courtesy, not a licence term)

## What a page contains

At a glance (producer, wine, vintage, colour, origin, style, alcohol, bottle size) · Scores and awards · What's in the glass (aroma and flavour grouped on the Noble wheel) · Grapes and winemaking · Serving, storage and pairing (ageing potential in bands) · Producer · Geography · Designation and certifications (the registered rules against this wine) · Sources and limitations.

Rules the skill keeps: front label only and no questions; facts only from sources that were opened, per row from the producer first and then reviews of the exact vintage; exact-vintage data only; blank rows instead of guesses; no judgments or marketing words; no "N/A".

## Install

- Claude (custom skill): upload this folder as a ZIP in your Claude settings. Custom skills are private to the account that uploads them; to share, give people the ZIP or this repository.
- Claude Code: place the `wine-page` folder in `~/.claude/skills/` (or a project's `.claude/skills/`).

Then send a front-label photo with `/wine-page`, for example `/wine-page details ro`.

## Requirements

Python 3 with Pillow (bottle photo), OpenCV (reading QR codes) and Playwright with Chromium (PDF, optional). The skill works without Playwright; it then delivers the HTML only.

## Folder

`SKILL.md` (instructions) · `references/` (rules and the aroma, sparkling and fortified models) · `assets/` (stylesheet, fonts, icons, logo, strings) · `scripts/` (`check_page.py`, `render_page.py`) · `examples/` (blank template and a worked example) · `licenses/` and `NOTICE.txt`.

## Licence

CC BY-NC 4.0 (see `LICENSE.txt`). The licence covers the instructions, scripts and page design. It does not cover the WineFluent name and logo, the third-party fonts, icons and aroma categories (see `NOTICE.txt`), or the wine facts and photographs a generated page draws from its sources.

## Open points

- Sparkling aroma wheel (InnoVinum): a few entries were read from a small image (see the notes at the end of the aroma table in `references/sparkling.md`).
- WSET Level 3 wording (scales and readiness statements) is used as scale words only; the WSET document is copyright WSET and is not included. Check WSET's terms before wider distribution.
- Overview and details differ only in depth (see `SKILL.md`); `lang` assumes the whole page is written in the chosen language.
- Producer pages with a vintage selector: the skill looks for the matching entry, but this has not been tested on live pages.
