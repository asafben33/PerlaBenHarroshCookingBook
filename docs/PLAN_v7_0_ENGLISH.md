# PLAN — Perla Cookbook v7.x Technical Handoff

**Last updated:** 19/04/2026 — late evening
**Current site version:** v7.6 (deployed v7.5; v7.6 ready to push)

---

## Project identity

Hebrew memorial cookbook (RTL, single-file HTML/CSS/JS) for Perla Ben-Harrosh z"l (1933-2025), Moroccan-born grandmother whose cooking blended Moroccan and Andalusian-Spanish traditions through her marriage to Pinchas (descendant of Rabbi Yosef Karo, expelled from Castile 1492). The site preserves 1,054 family recipes for future generations.

**User:** Asaf Yaakov Ben-Harrosh (אסף יעקב בן-הראש), youngest son of Perla & Pinchas z"l.

**Live URL:** https://perlabenharrosh-cookingbook.netlify.app/ (Netlify, primary)
**Mirror:** https://asafben33.github.io/PerlaBenHarroshCookingBook/ (GitHub Pages)
**Repo:** https://github.com/asafben33/PerlaBenHarroshCookingBook (branch: `main`)

---

## Critical context — must read before touching code

### Multi-session history (why things are the way they are)

The site went through 3 major architectural eras:
- **v1-v5:** Initial recipe database (~600 recipes), basic categories
- **v6.x (Mar-Apr 2026):** Added Web3Forms, PWA, Back-to-Top, expanded to 1,054 recipes with 9 community cuisines
- **v7.x (Apr 2026):** Complete UX/UI redesign per approved mockup. **You are here.**

### v7.0 cycle COMPLETED (19/04/2026)

All 10 plan tasks executed across 7 deployments:

| Version | What | Date |
|---|---|---|
| v7.0 | Unified header (`hdr-brand-v7`), Hero CTAs, flat 6-group MENU_STRUCTURE, Hero centered | 19/04 |
| v7.1 | Recipe grid hidden on load (`main-hidden`), revealed only by nav/search/CTA | 19/04 |
| v7.2 | New `COMMUNITY_HOLIDAY_TAGS` constant, 221 unique community-holiday taggings | 19/04 |
| v7.3 | Flat holidays under each community + search bar centering fix | 19/04 |
| v7.4 | "Holiday folder" + "Traditional folder" per community, mimouna removed from communities | 19/04 |
| v7.5 | Header strip max-width reduced 1440→1100 to align with content | 19/04 |
| v7.6 | 21 i18n keys added to DICT, DOM order fixed (Main after Bio), Web3Forms key restored | 19/04 |

### Critical bugs found & fixed in this cycle

1. **Web3Forms key** was reverted to `'PASTE_YOUR_WEB3FORMS_ACCESS_KEY_HERE'` somewhere in v7.0-v7.5. Fixed in v7.6 to `'705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'` (PUBLIC by design — Web3Forms requires client-side key).
2. **Mimouna in communities** — was tagged for Tunisia (6 recipes). Removed in v7.4. Mimouna is a Moroccan-only tradition; stays only in `HOLIDAY_TAGS` for Morocco (74 recipes).
3. **CRLF normalization** — every Python edit on `index.html` strips CRLF to LF. Must be re-normalized binarily after each edit.

---

## File inventory

### Production files (deploy to GitHub)

| File | Size | Purpose |
|---|---|---|
| `index.html` | 540 KB / 12,946 lines | Single-page app (HTML + inline JS) |
| `data.js` | 1.4 MB | All 1,054 recipes + MENU_STRUCTURE + COMMUNITY_HOLIDAY_TAGS |
| `book_data.js` | smaller | Book chapters (separate from recipes) |
| `pre_en.js` | ~1057 lines | Auto-generated English recipe content (NOT UI strings) |
| `manifest.json` | small | PWA manifest |
| `sw.js` | small | Service worker |
| `_headers` | small | Netlify HTTP headers (CSP, X-Frame-Options) |

### Documentation files

| File | Status |
|---|---|
| `CLAUDE.md` | ⚠ Pre-v7.x, references v6.10 |
| `CLAUDE_md_v7_update.md` | NEW (v7.6) — section to add to CLAUDE.md |
| `HLD_Perla_CookingBook.md` | ⚠ References v6.3 architecture |
| `LLD_Perla_CookingBook.md` | ⚠ References v6.3 architecture |
| `README.md` | ⚠ Pre-v7.x |
| `PLAN_v7_0_HEBREW.md` | UPDATED 19/04 |
| `PLAN_v7_0_ENGLISH.md` | UPDATED 19/04 (this file) |

### Scripts (Python utilities, not deployed)

- `add_recipe.py`, `edit_recipe.py`, `recipe_utils.py`
- `download_images.py` — downloads recipe images from web
- `audit_recipes.py` — quantity/quality audit tool

---

## Current architecture (v7.6)

### Top-level navigation — flat 6 groups

```javascript
const MENU_STRUCTURE = [
  {id:'all', lbl:'הכל'},                                       // 1,054
  {lbl:'מרוקו', key:'morocco', items:[...]},                   // 671 (8 sub)
  {id:'span', lbl:'ספרד'},                                     // 73
  {lbl:'עדות ישראל', key:'communities', items:[...]},          // 270 (9 communities)
  {id:'hol', lbl:'חגים'},                                      // 80
  {id:'nonkosher', lbl:'לא כשר'}                               // 40
];
```

### Each community = accordion with 3 items (v7.4)

```javascript
{lbl:'עיראק', items:[
  {id:'iraq', lbl:'כל המתכונים'},                              // all 30
  {lbl:'מאכלים מסורתיים לעדה', ids:['iq7','iq16','iq23']},     // non-holiday (3)
  {lbl:'מאכלי חגים', items:[                                    // nested folder
    {communityHoliday:'iraq', holidayKey:'shabbat', lbl:'שבת'},
    {communityHoliday:'iraq', holidayKey:'rosh', lbl:'ראש השנה'},
    {communityHoliday:'iraq', holidayKey:'kippur', lbl:'יום כיפור'},
    {communityHoliday:'iraq', holidayKey:'pesach', lbl:'פסח'},
    {communityHoliday:'iraq', holidayKey:'hanukkah', lbl:'חנוכה'},
    {communityHoliday:'iraq', holidayKey:'purim', lbl:'פורים'},
    {communityHoliday:'iraq', holidayKey:'shavuot', lbl:'שבועות'},
    {communityHoliday:'iraq', holidayKey:'sukkot', lbl:'סוכות'},
    {communityHoliday:'iraq', holidayKey:'henna', lbl:'חינה'}
  ]}
]}
```

**9 holidays per community** (mimouna removed). Same structure for all 9 communities.

### COMMUNITY_HOLIDAY_TAGS — community × holiday → recipe IDs

```javascript
const COMMUNITY_HOLIDAY_TAGS = {
  iraq: { shabbat:[...], rosh:[...], kippur:[...], pesach:[...],
          hanukkah:[...], purim:[...], shavuot:[...], sukkot:[...], henna:[...] },
  kurd: { ... },  ashk: { ... },  yem:  { ... },
  pers: { ... },  buk:  { ... },  tun:  { ... },
  turk: { ... },  isr:  { ... }
};
```

**Coverage:** 221 unique tags / 270 community recipes (82%). The other 49 are tagged as "Traditional" (non-holiday) per community.

### Recipe schema

```javascript
{
  id: 'iq1',                  // unique within data.js
  cat: 'iraq',                // one of 20 CATS
  badge: 'מטעמי אמא',         // optional
  title: 'קובה בסלק אדום',
  desc: 'short description',
  time: 90,                   // minutes
  serv: 4,                    // servings
  diff: 'בינוני',
  img: 'r-iq1.jpg',           // file in images/recipes_images/
  mem: 'memory note',         // family/cultural connection
  ingr: [{q:'1 cup', i:'flour'}, ...],
  steps: [{t:'10 min', s:'do this'}, ...],
  tip: 'optional final tip',
  tags: [...],                // optional
  h: 'shabbat',               // optional holiday key (legacy from HOLIDAY_TAGS)
  src: 'https://...',         // optional source
  vid: 'https://...'          // optional video URL
}
```

### Key JavaScript touchpoints

| Function/Const | Location (line) | Purpose |
|---|---|---|
| `MENU_STRUCTURE` | data.js:18777 | Top-level menu definition |
| `COMMUNITY_HOLIDAY_TAGS` | data.js:18746 | Community × holiday → recipe IDs |
| `HOLIDAY_TAGS` | data.js:18764 | Morocco holiday → recipe IDs (legacy, currently broken) |
| `CATS` | data.js:11 | All 20 category definitions |
| `R` | data.js:1 | Main array of all 1,054 recipes |
| `selectCommunityHoliday(c, h, label, key)` | index.html:7913 | Filter by community-holiday combo |
| `selectCat(catId, hol, key)` | index.html:7857 | Filter by category |
| `selectMulti(ids, label, key)` | index.html:7866 | Filter by category list |
| `selectByIds(ids, label, key)` | index.html:7894 | Filter by specific recipe IDs |
| `buildPanel(node, pi)` | index.html:7943 | Renders accordion content per nav group |
| `buildNav()` | index.html:8093 | Builds top nav buttons |
| `window.showMainGrid()` | index.html | Reveals hidden recipe grid (v7.1) |
| `window.initHdrCount()` | index.html | Updates header recipe count |
| `window.initHeroCTAs()` | index.html | Wires Hero CTA click handlers |
| `t(key)` | index.html | i18n translation function |
| `DICT` | index.html:11860+ | UI translation dictionary (HE/EN) |
| `_LANG` | index.html | Current language ('he' or 'en') |

### CSS key classes (v7.x)

| Class | Purpose |
|---|---|
| `.hdr-brand-v7` | Header brand title + dynamic count (v7.0) |
| `.hero-cta-row`, `.hero-cta-primary`, `.hero-cta-secondary` | Hero CTAs (v7.0) |
| `.main-hidden` | Hides recipe grid until user action (v7.1) |
| `.pc-comm-hol` | Community-holiday chip (red-coral accent) |
| `.pc-empty` | Empty community-holiday combo (semi-transparent + cursor:help) |

### CSS variables (DO NOT modify)

```css
:root {
  --c-spice: #b84223;     /* Used for .pc-comm-hol */
  --c-spice-d: #8c2e14;
  --c-spice-l: #d4603a;   /* Used for .pc-comm-hol text */
  --c-gold: #c4930a;
  --c-gold-l: #e5b020;
  --c-gold-d: #9a7208;
  /* ... */
}
```

### Layout widths (v7.5)

```css
.hdr-inner       { max-width: 1100px; }  /* was 1440 in v6.x */
.cat-nav-inner   { max-width: 1100px; }  /* was 1440 in v6.x */
.nav-panel-inner { max-width: 1100px; }  /* was 1440 in v6.x */
.hdr-search      { flex: 0 1 480px; max-width: 480px; }
.hero-inner      { max-width: 760px; margin: 0 auto; text-align: center; }
.bio-inner       { max-width: 860px; }
```

### DOM section order (v7.6)

```
Hero (1675) → Bio (1689) → Main (1707) → Book (1733) → About (1768)
```

`<main>` was moved from after About to right after Bio so the user reaches the recipe grid immediately after the brief Bio, not after scrolling through the book and the long About section.

### i18n keys added in v7.6 (21 total)

Located in `DICT` constant (~line 11906):
```
site_name_short, recipes_label, hero_cta_browse, hero_cta_book,
nav_morocco, nav_communities, nav_holidays,
community_all, community_traditional, community_holidays_folder,
holiday_shabbat, holiday_rosh, holiday_kippur, holiday_pesach,
holiday_mimouna, holiday_hanukkah, holiday_purim,
holiday_shavuot, holiday_sukkot, holiday_henna,
toast_no_recipes_holiday
```

**WARNING:** These keys are READY but NOT YET WIRED to the visible UI. `buildPanel` still uses `esc(item.lbl)` directly. Full i18n of community menu requires a refactor pass.

---

## What remains to do (post-v7.6 roadmap)

### High priority

1. **Fix `HOLIDAY_TAGS` for Morocco** — current state is BROKEN. Same 80 recipes appear in EVERY holiday key. This is suspicious data from initial generation. Needs proper per-holiday tagging like v7.2 did for communities.

2. **Wire i18n keys to UI** — `buildPanel` should call `t(item.i18nKey || item.lbl)` instead of `esc(item.lbl)`. Add `i18nKey:'community_traditional'` etc. to MENU_STRUCTURE items.

3. **`COMMUNITY_HOLIDAY_TAGS` review with family** — first-pass tagging based on documented Sephardic/Mizrahi/Ashkenazi traditions. Variations exist between families/regions. User (Asaf) should review and update.

### Medium priority

4. **Documentation refresh** — Embed `CLAUDE_md_v7_update.md` into `CLAUDE.md`. Update `HLD_Perla_CookingBook.md` and `LLD_Perla_CookingBook.md` from v6.3 to v7.x.

5. **Missing recipe images** — many community recipes (especially Tunisia, Bukhara) lack `r-{id}.jpg` files. Run `download_images.py` to fetch.

6. **Light theme polish** — verify `html.light` overrides work for new v7.x classes (`.hdr-brand-v7`, `.pc-comm-hol`, `.hero-cta-row`).

### Low priority

7. **Sitemap.xml** — not generated. SEO opportunity.
8. **Breadcrumbs** — recipe pages lack breadcrumb navigation.
9. **Recipe of the day** — landing page carousel.
10. **Print stylesheet** — currently hides too much; recipe-only print view would help.

---

## Things NOT to break

### v7.x rules (NEW)

- **DO NOT** revert `MENU_STRUCTURE` to v6.x nested wrapper style
- **DO NOT** add `mimouna` to `COMMUNITY_HOLIDAY_TAGS` (Moroccan-only tradition)
- **DO NOT** remove `class="main-hidden"` from `<main>` (v7.1 feature)
- **DO NOT** change `WEB3FORMS_KEY` to placeholder — it's PUBLIC by design
- **DO NOT** change `.hdr-search` to `flex: 1` (will stretch full-width again)
- **DO NOT** revert `max-width: 1440` to header strip (broke alignment with content)

### v6.x rules (still valid)

- **PWA install button** — `#pwa-install-btn` in `.hdr-tools` — keep intact
- **PWA modal** — `#pwa-modal-ovl` near `#back-top` — do not remove
- **Back-to-Top** — `#back-top` button + handler at ~line 3782
- **Feedback FAB + Web3Forms** — CSP `connect-src` includes `https://api.web3forms.com`
- **Theme toggle / Lang toggle** — `#theme-toggle`, `#lang-toggle` — preserve IDs
- **`html.light` class** — all light-theme overrides must continue to work

---

## Testing checklist

```bash
# 1. data.js syntax
node -c data.js  # must be OK

# 2. index.html main JS syntax
python3 -c "
import re, subprocess
html = open('index.html', encoding='utf-8').read()
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
biggest = max(scripts, key=len)
open('/tmp/app.js','w',encoding='utf-8').write(biggest)
r = subprocess.run(['node','-c','/tmp/app.js'],capture_output=True,text=True)
print('Main JS:', 'OK' if r.returncode == 0 else 'FAIL')
"

# 3. Recipe count == 1054
grep -oE "\{id:'[^']+',cat:'\w+'" data.js | wc -l

# 4. Mimouna ONLY in HOLIDAY_TAGS (Morocco), NOT in COMMUNITY_HOLIDAY_TAGS
grep -A 1 "COMMUNITY_HOLIDAY_TAGS" data.js | grep "mimouna:\['" | wc -l   # must be 0

# 5. Web3Forms key intact
grep -c "705d4207-c4a6-43a2-8fdc-d8e202bc6c9c" index.html  # must be ≥1

# 6. CRLF integrity
python3 -c "raw=open('index.html','rb').read(); print('CRLF',raw.count(b'\r\n'),'LONE',raw.count(b'\n')-raw.count(b'\r\n'))"
# Must be: CRLF ≥12000, LONE 0

# 7. DOM section order: Hero → Bio → Main → Book → About
grep -n "<section class=\"hero\"\|<section id=\"bio\"\|<main id=\"main\"\|id=\"book-wrapper\"\|id=\"about-redesigned\"" index.html | head -10

# 8. PWA + Back-to-Top + Theme/Lang toggles intact
grep -c "pwa-install-btn\|back-top\|theme-toggle\|lang-toggle" index.html  # all ≥1
```

---

## Deployment commands (PowerShell, ONE AT A TIME)

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" ".\index.html" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\data.js" ".\data.js" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_*.md" ".\" -Force
```
```powershell
git add index.html data.js CHANGELOG_*.md
```
```powershell
git commit -m "v7.x: <description>"
```
```powershell
git push origin main
```

Netlify auto-deploys ~30s after push. Verify at https://perlabenharrosh-cookingbook.netlify.app/

---

## CRLF normalization (CRITICAL)

Every Python edit of `index.html` strips CRLF. Always end edits with:

```python
raw = open('index.html', 'rb').read()
text = raw.replace(b'\r', b'').replace(b'\n', b'\r\n')
open('index.html', 'wb').write(text)
```

Verify after:
```bash
python3 -c "raw=open('index.html','rb').read(); print('CRLF',raw.count(b'\r\n'),'LONE',raw.count(b'\n')-raw.count(b'\r\n'))"
```

---

## CHANGELOGs from v7.x cycle

Located in repo root + outputs:
- `CHANGELOG_19-04-2026_v7_centered_hero.md` — v7.0+v7.1
- `CHANGELOG_19-04-2026_v7_2_community_holidays.md` — v7.2
- `CHANGELOG_19-04-2026_v7_3_holidays_in_community.md` — v7.3
- `CHANGELOG_19-04-2026_v7_4_holiday_folder.md` — v7.4
- `CHANGELOG_19-04-2026_v7_5_centered_header_strip.md` — v7.5
- `CHANGELOG_19-04-2026_v7_6_final.md` — v7.6

Earlier v6.x changelogs preserved unchanged.

---

## If you're a new Claude picking this up

1. **First**, read `userMemories` block in your context — contains latest project state
2. **Second**, read this file (PLAN_v7_0_ENGLISH.md) end-to-end
3. **Third**, read `CLAUDE_md_v7_update.md` for architectural details
4. **Fourth**, check `https://perlabenharrosh-cookingbook.netlify.app/` to see current production
5. Understand that **v7.0 is COMPLETE** — don't redo work. Focus on the post-v7.6 roadmap above.
6. **Always validate** before pushing: `node -c data.js` + main JS syntax + CRLF
7. **Always create CHANGELOG** for any version
8. **PowerShell commands one at a time** — user runs them manually, not as script

---

## User preferences (persistent)

From `<userPreferences>`:
- All responses in Hebrew
- Hebrew RTL alignment in all outputs (PDFs, DOCXs, etc.)
- No emojis
- Short response mode for efficiency
- Don't create automated fix scripts unless explicitly requested
- Provide step-by-step instructions; user prefers full control
- Document every change with version tracking
- Balance quality and speed
- Acknowledge AI training cutoff (Oct 2023; current date passed Apr 2026)

---

## Honesty constraint (extremely important)

**This is a memorial project for the user's deceased mother.** Asaf trusted Claude with preserving authentic family recipes. When making cultural/traditional decisions (especially around holiday tagging):

- DO use documented sources (academic/cookbook references for Sephardic/Mizrahi/Ashkenazi traditions)
- DON'T fabricate "Perla used to..." statements that aren't in original recipe `mem` fields
- DO mark uncertain tagging as "first-pass, family review welcome"
- DON'T present cultural variations as universal truths
- IF unsure about a detail, ASK rather than invent

The user explicitly chose mimouna restriction (Moroccan-only) — they understand cultural specificity matters. Honor that.

---

## Estimated effort for next cycle

- Fix `HOLIDAY_TAGS` for Morocco (proper tagging like v7.2): ~3-4 hours
- Wire i18n keys to UI (refactor buildPanel): ~2 hours
- Documentation refresh (CLAUDE.md, HLD, LLD): ~1 hour
- Image gap-fill via download_images.py: ~30 minutes (mostly automated)

---

**For the memory of the Ben-Harrosh family — Casablanca, Marrakech, Jerusalem**
