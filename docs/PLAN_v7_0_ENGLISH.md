# PLAN — Perla Cookbook v7.x → v8.0 Technical Handoff

**Last updated:** 19/04/2026 — late evening (after v8.0)
**Current site version:** v8.0 (deployed v7.5; v7.6-v8.0 ready to push)

---

## Project identity

Hebrew memorial cookbook (RTL, single-file HTML/CSS/JS) for Perla Ben-Harrosh z"l (1933-2025), Moroccan-born grandmother whose cooking blended Moroccan and Andalusian-Spanish traditions through her marriage to Pinchas (descendant of Rabbi Yosef Karo, expelled from Castile 1492). The site preserves 1,054 family recipes for future generations.

**User:** Asaf Yaakov Ben-Harrosh (אסף יעקב בן-הראש), youngest son of Perla & Pinchas z"l.

**Live URL:** https://perlabenharrosh-cookingbook.netlify.app/ (Netlify, primary)
**Mirror:** https://asafben33.github.io/PerlaBenHarroshCookingBook/ (GitHub Pages)
**Repo:** https://github.com/asafben33/PerlaBenHarroshCookingBook (branch: `main`)

---

## Critical context — must read before touching code

### Multi-session history

The site went through 3 major architectural eras:
- **v1-v5:** Initial recipe database (~600 recipes), basic categories
- **v6.x (Mar-Apr 2026):** Added Web3Forms, PWA, Back-to-Top, expanded to 1,054 recipes with 9 community cuisines
- **v7.x → v8.0 (Apr 2026):** Complete UX/UI redesign per approved mockup. **You are here at v8.0.**

### Cycle COMPLETED — v7.0 plan + 4 user-requested extensions + maintenance

All deployments executed in 11 stages:

| Version | What | Date |
|---|---|---|
| v7.0 | Unified header, Hero CTAs, flat MENU_STRUCTURE, Hero centered | 19/04 |
| v7.1 | Recipe grid hidden on load, revealed only by nav/search/CTA | 19/04 |
| v7.2 | New COMMUNITY_HOLIDAY_TAGS, 221 unique community-holiday tags | 19/04 |
| v7.3 | Flat holidays under each community + search bar centering fix | 19/04 |
| v7.4 | Holiday folder + Traditional folder per community, mimouna removed | 19/04 |
| v7.5 | Header strip max-width 1440→1100 to align with content | 19/04 |
| v7.6 | 21 i18n keys to DICT, DOM order fixed, Web3Forms key restored | 19/04 |
| v7.7 | HOLIDAY_TAGS Morocco rebuild — 80×10 identical → 121 unique tags | 19/04 |
| v7.8 | Removed duplicate top-level "חגים" — now only under Morocco | 19/04 |
| v7.9 | Merged "מרוקו" + "ספרד" into single folder (Karo heritage 1492) | 19/04 |
| **v8.0** | **i18n wiring complete + light theme overrides + sitemap.xml + print rules** | **19/04** |

### Critical bugs found & fixed

1. **Web3Forms key** (v7.6) reverted to placeholder. Restored to `'705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'` (PUBLIC by design).
2. **Mimouna in communities** (v7.4) — removed from non-Moroccan communities (Tunisia had 6 false tags). Mimouna stays only in `HOLIDAY_TAGS` for Morocco.
3. **HOLIDAY_TAGS broken** (v7.7) — same 80 recipes in EVERY holiday key. Fixed via regex pattern matching.
4. **Duplicate "חגים"** (v7.8) — top button + Morocco sub-category. Top removed.
5. **Morocco/Spain separated** (v7.9) — merged for Karo heritage continuity.
6. **i18n incomplete** (v8.0) — `_NAV_I18N` lacked v7.x label mappings. Extended.
7. **Light theme gaps** (v8.0) — `.hdr-brand-v7`, `.hero-cta-primary`, `.pc-comm-hol:hover` had no light-theme overrides. Added.
8. **CRLF normalization** — every Python edit strips CRLF. Re-normalized binarily.

---

## File inventory (v8.0)

### Production files

| File | Size | Purpose |
|---|---|---|
| `index.html` | 542 KB / 12,990 lines | Single-page app (HTML + inline JS + CSS) |
| `data.js` | 1.4 MB | All 1,054 recipes + MENU_STRUCTURE + tags |
| `book_data.js` | smaller | Book chapters |
| `pre_en.js` | ~1057 lines | Auto-generated English recipe content |
| `manifest.json` | small | PWA manifest |
| `sw.js` | small | Service worker |
| `_headers` | small | Netlify CSP + headers |
| **`sitemap.xml`** | 1.5 KB | **NEW v8.0 — SEO sitemap** |
| **`robots.txt`** | 154 B | **NEW v8.0 — points crawlers to sitemap** |

### Documentation files

| File | Status |
|---|---|
| `CLAUDE.md` | ⚠ Pre-v7.x |
| `CLAUDE_md_v7_update.md` | v7.6 patch — section to add |
| `CLAUDE_md_v8_update.md` | **NEW v8.0 — patch for v7.7+v8.0** |
| `HLD_Perla_CookingBook.md` | ⚠ v6.3 architecture |
| `LLD_Perla_CookingBook.md` | ⚠ v6.3 architecture |
| `PLAN_v7_0_HEBREW.md` | UPDATED 19/04 (after v8.0) |
| `PLAN_v7_0_ENGLISH.md` | UPDATED 19/04 (this file) |

---

## Current architecture (v8.0)

### Top-level navigation — 4 flat groups

```javascript
const MENU_STRUCTURE = [
  {id:'all', lbl:'הכל'},                                       // 1,054
  {lbl:'מרוקו\\ספרד', key:'morocco_span', items:[...]},        // 744 (11 sub-items)
  {lbl:'עדות ישראל', key:'communities', items:[...]},          // 270 (9 communities)
  {id:'nonkosher', lbl:'לא כשר'}                               // 40
];
```

### Morocco/Spain accordion (v7.9)

```javascript
{lbl:'מרוקו\\ספרד', key:'morocco_span', items:[
  // Multi-cat selector showing ALL 744 recipes
  {lbl:'כל מתכוני מרוקו וספרד', ids:['soups','salads','veg','meat','chick','fish','hol','des','span']},
  
  // Moroccan sub-categories
  {id:'soups', lbl:'מרקים'}, {id:'salads', lbl:'סלטים'},
  {id:'veg', lbl:'תבשילי ירקות'}, {id:'meat', lbl:'בשר וקציצות'},
  {id:'chick', lbl:'עוף ושבת'}, {id:'fish', lbl:'דגים'},
  
  // Holiday folder (v7.8 — uses HOLIDAY_TAGS via h: param)
  {lbl:'חגים ומועדים', items:[
    {id:'hol', lbl:'כל מתכוני החגים'},                         // all 80
    {id:'hol', h:'shabbat',  lbl:'שבת'},                       // 54
    {id:'hol', h:'rosh',     lbl:'ראש השנה'},                  // 14
    {id:'hol', h:'kippur',   lbl:'יום כיפור'},                 // 0
    {id:'hol', h:'pesach',   lbl:'פסח'},                       // 4
    {id:'hol', h:'mimouna',  lbl:'מימונה'},                    // 7
    {id:'hol', h:'hanukkah', lbl:'חנוכה'},                     // 2
    {id:'hol', h:'purim',    lbl:'פורים'},                     // 1
    {id:'hol', h:'shavuot',  lbl:'שבועות'},                    // 12
    {id:'hol', h:'sukkot',   lbl:'סוכות'},                     // 27
    {id:'hol', h:'henna',    lbl:'חינה'}                       // 14
  ]},
  
  {id:'des', lbl:'קינוחים ומאפים'},   // 80
  {id:'span', lbl:'ספרד (אנדלוסי)'}    // 73
]}
```

### Each community (v7.4 — preserved)

```javascript
{lbl:'עיראק', items:[
  {id:'iraq', lbl:'כל המתכונים'},                              // all 30
  {lbl:'מאכלים מסורתיים לעדה', ids:['iq7','iq16','iq23']},     // non-holiday (3)
  {lbl:'מאכלי חגים', items:[                                    // nested folder
    {communityHoliday:'iraq', holidayKey:'shabbat', lbl:'שבת'},
    // ... 8 more holidays
  ]}
]}
```

### Tag systems

```javascript
// COMMUNITY_HOLIDAY_TAGS (v7.4): community × holiday → recipes
const COMMUNITY_HOLIDAY_TAGS = {
  iraq: { shabbat:[...], rosh:[...], ... },     // 9 holidays per community
  // ... 8 more communities (no mimouna - Moroccan-only)
};

// HOLIDAY_TAGS (v7.7 - REBUILT): Morocco's per-holiday tags
const HOLIDAY_TAGS = {
  shabbat:  [54], rosh:[14], kippur:[],
  pesach:   [4],  mimouna:[7], hanukkah:[2],
  purim:    [1],  shavuot:[12], sukkot:[27], henna:[14]
};
```

### i18n wiring (v8.0)

The `_NAV_I18N` constant maps Hebrew labels → DICT keys. Function `applyLang('en')` walks the DOM and translates. v8.0 added missing v7.x mappings:

```javascript
var _NAV_I18N = {
  // ... existing pre-v7.x entries ...
  
  // v7.x additions (NEW in v8.0)
  'מרוקו':'nav_morocco',
  'עדות ישראל':'nav_communities',
  'חגים':'nav_holidays',
  'מרוקו\\ספרד':'nav_morocco_span',                     // v7.9
  'כל מתכוני מרוקו וספרד':'nav_morocco_span_all',        // v7.9
  'ספרד (אנדלוסי)':'nav_span_andalusi',                  // v7.9
  'מאכלי חגים':'community_holidays_folder',              // v7.4
  'מאכלים מסורתיים לעדה':'community_traditional',        // v7.4
  'תבשילי ירקות':'nav_veg_dishes',                       // v7.0
  'כל מתכוני החגים':'morocco_all_holidays'               // v7.8
};
```

DICT entries added for all of these in v8.0.

### Light theme overrides (v8.0)

Added to `index.html` ~line 451:
```css
html.light .hdr-brand-v7 .hdr-brand-title { color: #6e3d0a; }
html.light .hdr-brand-v7 .hdr-brand-count { color: rgba(74,42,20,.65); }
html.light .pc-comm-hol { background: rgba(184,66,35,.06); border-color: rgba(184,66,35,.30); }
html.light .pc-comm-hol:hover { ... }
html.light .pc-comm-hol.pc-empty { opacity: .45; }
html.light .hero-cta-primary { background: var(--c-spice); color: #fff; }
html.light .hero-cta-primary:hover { background: #922f18; }
```

### Print stylesheet (v8.0 extended)

`@media print` now hides v7.x elements that didn't exist when the original print rules were written:
```css
.hdr-brand-v7, .hero-cta-row, .pc-comm-hol, .pc-empty,
#main, .main-hidden, #book-wrapper, #about-redesigned,
.feedback-fab, #pwa-modal-ovl, #pwa-install-btn { display: none !important; }
```

### Recipe schema (unchanged)

```javascript
{
  id: 'iq1',                  // unique within data.js
  cat: 'iraq',                // one of 20 CATS
  badge: 'מטעמי אמא',         // optional
  title: 'קובה בסלק אדום',
  desc, time, serv, diff,     // standard fields
  img: 'r-iq1.jpg',
  mem: 'memory note',
  ingr: [{q:'1 cup', i:'flour'}, ...],
  steps: [{t:'10 min', s:'do this'}, ...],
  tip, tags, h, src, vid      // optional
}
```

### Key JavaScript touchpoints

| Function/Const | Location (line) | Purpose |
|---|---|---|
| `MENU_STRUCTURE` | data.js:18777 | Top-level menu (4 groups in v7.9+) |
| `COMMUNITY_HOLIDAY_TAGS` | data.js:18746 | Community × holiday → IDs |
| `HOLIDAY_TAGS` | data.js:18764 | Morocco holiday → IDs (REBUILT v7.7) |
| `R` | data.js:1 | Main recipes array (1,054) |
| `selectCommunityHoliday` | index.html:7913 | Filter by community-holiday |
| `selectCat` | index.html:7857 | Filter by category (handles h: param) |
| `selectMulti` | index.html:7866 | Filter by category list |
| `selectByIds` | index.html:7894 | Filter by specific recipe IDs |
| `buildPanel` | index.html:7943 | Renders accordion content |
| `buildNav` | index.html:8093 | Builds top nav buttons |
| `window.showMainGrid` | index.html | Reveals hidden grid (v7.1) |
| `window.initHdrCount` | index.html | Updates header count |
| `window.initHeroCTAs` | index.html | Wires Hero CTA handlers |
| `t(key)` | index.html:12080 | i18n translation |
| `DICT` | index.html:11860+ | UI translation dict (~155 entries) |
| `_NAV_I18N` | index.html:12055 | Hebrew→key mapping (extended v8.0) |
| `applyLang` | index.html:12082 | Switches language, translates DOM |

### CSS layout widths (v7.5)

```css
.hdr-inner       { max-width: 1100px; }
.cat-nav-inner   { max-width: 1100px; }
.nav-panel-inner { max-width: 1100px; }
.hdr-search      { flex: 0 1 480px; max-width: 480px; }
.hero-inner      { max-width: 760px; margin: 0 auto; text-align: center; }
.bio-inner       { max-width: 860px; }
```

### DOM section order (v7.6)

```
Hero (1675) → Bio (1689) → Main (1707) → Book (1733) → About (1768)
```

---

## What remains to do (post-v8.0 roadmap)

### High priority — REQUIRES family/Asaf involvement

1. **`COMMUNITY_HOLIDAY_TAGS` review** — first-pass tagging based on documented Sephardic/Mizrahi/Ashkenazi traditions. Variations exist between families/regions. User (Asaf) should review and update.

2. **`HOLIDAY_TAGS` Morocco refinement** — v7.7 fix is automatic regex-based. May have false negatives. Needs review against original recipe titles.

### Medium priority

3. **Documentation refresh** — Embed `CLAUDE_md_v7_update.md` + `CLAUDE_md_v8_update.md` into `CLAUDE.md`. Update `HLD` and `LLD` from v6.3 to v8.0.

4. **Missing recipe images** — many community recipes (especially Tunisia, Bukhara) lack `r-{id}.jpg` files. Run `download_images.py` to fetch.

5. **Cultural review per community** — verify holiday tags work for families from different regions within same community (e.g., Kurdish from Zakho vs Jerusalem).

### Low priority

6. **Breadcrumbs** — recipe pages lack breadcrumb navigation.
7. **Recipe of the day** — landing page carousel.
8. **OG images per category** — separate social sharing images.
9. **Lazy loading + virtualization** — for recipe grid as it grows.

### Already done — DO NOT redo

- ✅ v7.0: Unified header, Hero CTAs, MENU_STRUCTURE rewrite
- ✅ v7.1: Grid-on-demand
- ✅ v7.2-v7.4: Community holiday system
- ✅ v7.5: Header strip width
- ✅ v7.6: i18n keys + DOM order + Web3Forms key
- ✅ v7.7: HOLIDAY_TAGS Morocco rebuild
- ✅ v7.8: Removed duplicate "חגים"
- ✅ v7.9: Merged Morocco + Spain
- ✅ v8.0: i18n wiring + light theme + sitemap + print rules

---

## Things NOT to break

### v7.x → v8.0 rules (NEW)

- **DO NOT** revert `MENU_STRUCTURE` to v6.x nested wrapper style
- **DO NOT** add `mimouna` to `COMMUNITY_HOLIDAY_TAGS` (Moroccan-only)
- **DO NOT** remove `class="main-hidden"` from `<main>` (v7.1)
- **DO NOT** change `WEB3FORMS_KEY` to placeholder — PUBLIC by design
- **DO NOT** change `.hdr-search` to `flex: 1`
- **DO NOT** revert `max-width: 1440` to header strip
- **v7.7**: DO NOT revert `HOLIDAY_TAGS` to identical-arrays state
- **v7.8**: DO NOT add `{id:'hol', lbl:'חגים'}` back as top-level
- **v7.9**: DO NOT separate "מרוקו" and "ספרד" into separate top buttons
- **v8.0**: When adding a NEW menu label, ALWAYS update both `_NAV_I18N` AND `DICT` simultaneously

### v6.x rules (still valid)

- **PWA install button** — `#pwa-install-btn` in `.hdr-tools` — keep intact
- **PWA modal** — `#pwa-modal-ovl` near `#back-top` — do not remove
- **Back-to-Top** — `#back-top` button + handler ~line 3782
- **Feedback FAB + Web3Forms** — CSP `connect-src` includes `https://api.web3forms.com`
- **Theme toggle / Lang toggle** — `#theme-toggle`, `#lang-toggle` — preserve IDs
- **`html.light` class** — all light-theme overrides must work

---

## Testing checklist

```bash
# 1. data.js syntax
node -c data.js

# 2. Main JS syntax
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

# 4. Mimouna ONLY in HOLIDAY_TAGS, NOT COMMUNITY_HOLIDAY_TAGS
python3 -c "
import re
d = open('data.js', encoding='utf-8').read()
m = re.search(r'const COMMUNITY_HOLIDAY_TAGS = \{(.*?)\n\};', d, re.DOTALL)
hits = re.findall(r\"mimouna:\['?\w\", m.group(1))
print('Mimouna in communities:', len(hits), '(must be 0)')
"

# 5. Web3Forms key intact
grep -c "705d4207-c4a6-43a2-8fdc-d8e202bc6c9c" index.html

# 6. CRLF integrity
python3 -c "raw=open('index.html','rb').read(); print('CRLF',raw.count(b'\r\n'),'LONE',raw.count(b'\n')-raw.count(b'\r\n'))"

# 7. DOM section order: Hero → Bio → Main → Book → About
grep -n "<section class=\"hero\"\|<section id=\"bio\"\|<main id=\"main\"\|id=\"book-wrapper\"\|id=\"about-redesigned\"" index.html | head -5

# 8. v7.7: HOLIDAY_TAGS shabbat ≠ pesach
python3 -c "
import re
d = open('data.js', encoding='utf-8').read()
m = re.search(r'const HOLIDAY_TAGS = \{(.*?)\n\};', d, re.DOTALL)
sha = re.search(r\"shabbat:\[(.*?)\]\", m.group(1)).group(1)
pes = re.search(r\"pesach:\[(.*?)\]\", m.group(1)).group(1)
print('SAME (BAD):', sha == pes)
"

# 9. v7.8: No top-level חגים entry
grep -c "^\s*{id:'hol', lbl:'חגים'}" data.js

# 10. v7.9: Morocco/Spain merged
grep -c "morocco_span" data.js

# 11. v8.0: i18n wiring complete
grep -c "nav_morocco_span:" index.html
grep -c "html.light .hdr-brand-v7" index.html

# 12. v8.0: sitemap + robots exist
ls sitemap.xml robots.txt
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
Copy-Item "$env:USERPROFILE\Downloads\sitemap.xml" ".\sitemap.xml" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\robots.txt" ".\robots.txt" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_*.md" ".\" -Force
```
```powershell
git add index.html data.js sitemap.xml robots.txt CHANGELOG_*.md
```
```powershell
git commit -m "v8.0: i18n + light theme + SEO + print"
```
```powershell
git push origin main
```

Netlify auto-deploys ~30s after push.

---

## CRLF normalization (CRITICAL)

```python
raw = open('index.html', 'rb').read()
text = raw.replace(b'\r', b'').replace(b'\n', b'\r\n')
open('index.html', 'wb').write(text)
```

---

## CHANGELOGs from v7.x → v8.0 cycle (10 files)

- `CHANGELOG_19-04-2026_v7_centered_hero.md` — v7.0+v7.1
- `CHANGELOG_19-04-2026_v7_2_community_holidays.md` — v7.2
- `CHANGELOG_19-04-2026_v7_3_holidays_in_community.md` — v7.3
- `CHANGELOG_19-04-2026_v7_4_holiday_folder.md` — v7.4
- `CHANGELOG_19-04-2026_v7_5_centered_header_strip.md` — v7.5
- `CHANGELOG_19-04-2026_v7_6_final.md` — v7.6
- `CHANGELOG_19-04-2026_v7_7_holiday_tags_fix.md` — v7.7
- `CHANGELOG_19-04-2026_v7_8_remove_duplicate_holidays.md` — v7.8
- `CHANGELOG_19-04-2026_v7_9_morocco_spain_merge.md` — v7.9
- `CHANGELOG_19-04-2026_v8_0_i18n_theme_seo.md` — **v8.0 (NEW)**

---

## If you're a new Claude picking this up

1. Read `userMemories` block in your context
2. Read this file (PLAN_v7_0_ENGLISH.md) end-to-end
3. Read `CLAUDE_md_v7_update.md` + `CLAUDE_md_v8_update.md`
4. Check live site: https://perlabenharrosh-cookingbook.netlify.app/
5. Understand: **v7.0 cycle COMPLETE through v8.0** — focus on post-v8.0 roadmap
6. **Always validate** before pushing: `node -c data.js` + JS syntax + CRLF
7. **Always create CHANGELOG** for any version
8. **PowerShell commands ONE AT A TIME** — user runs them manually

---

## User preferences

From `<userPreferences>`:
- All responses in Hebrew
- Hebrew RTL alignment
- No emojis
- Short response mode
- Don't create automated fix scripts unless explicitly requested
- Step-by-step instructions; user maintains control
- Document every change with version tracking
- Balance quality and speed

---

## Honesty constraint

**Memorial project.** Asaf trusted Claude with preserving authentic family recipes. When making cultural decisions:
- DO use documented sources for Sephardic/Mizrahi/Ashkenazi traditions
- DON'T fabricate "Perla used to..." statements
- DO mark uncertain tagging as "first-pass, family review welcome"
- DON'T present cultural variations as universal truths
- IF unsure, ASK rather than invent

---

## Cultural context — Morocco/Spain merger reasoning (v7.9)

The merger isn't arbitrary. It reflects family heritage:

- **Pinchas Ben-Harrosh** descended from the Karo family
- **Rabbi Yosef Karo** (1488-1575): Author of *Shulchan Aruch*
- The Karo family was **expelled from Castile, Spain in 1492** (Alhambra Decree)
- They settled in Morocco eventually
- **Perla** was born in Casablanca, grew up in Marrakech
- Her cooking absorbed BOTH Moroccan technique AND Spanish-Andalusian flavors learned from her mother-in-law

So "מרוקו\\ספרד" isn't a UI shortcut — it's the actual family kitchen story. Documented in `<about_p1>` text in DICT (~line 11921).

---

## Estimated effort for next cycle

- HOLIDAY_TAGS Morocco refinement (manual review): 1-2 hours
- COMMUNITY_HOLIDAY_TAGS family review: depends on Asaf
- Documentation refresh: 1 hour
- Image gap-fill via download_images.py: 30 min (mostly automated)

---

**For the memory of the Ben-Harrosh family — Casablanca, Marrakech, Jerusalem**
