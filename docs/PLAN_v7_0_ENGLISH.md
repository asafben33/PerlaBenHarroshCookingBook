# Perla Cookbook — v7.0 Homepage Redesign Technical Handoff

**This document is written for a future Claude instance that needs to resume this work in a new chat. It contains everything you need to understand the project state, the intended changes, and the constraints.**

---

> ## ✓ STATUS: IMPLEMENTED
>
> **Version deployed: 7.1** (19/04/2026, afternoon)
> **Decision made: Option C** — Community Holidays as empty placeholder container
>
> **What was actually implemented:**
> - ✓ **v7.0** — All 4 structural changes (Header brand, Hero CTAs, section reorder, flat 6-group MENU_STRUCTURE)
> - ✓ **v7.1** — Hotfix following v7.0 deployment: recipe grid hidden on load, shown only on user action (nav/search/CTA)
>
> **Documents created post-implementation:**
> - `CHANGELOG_19-04-2026_v7_0.md` — full detail of v7.0 changes
> - `CHANGELOG_19-04-2026_v7_1.md` — hotfix detail of v7.1
> - `CLAUDE.md`, `README.md`, `HLD`, `LLD`, `INTEGRATION_GUIDE.md` updated to v7.1
>
> **See the "Implementation Summary" section at the end of this document** for what shipped, what differed from the plan, and what comes next (Stage 2: `audit_recipes.py`).
> *This document is preserved as a historical record of the planning process.*

---

## Project identity (for context if you're a new Claude)

- **Name:** Perla Ben-Harrosh Cookbook — `ספר הבישול של פרלה בן-הראש ז״ל`
- **Purpose:** Hebrew-language memorial cookbook for the user's late mother Perla (1933–2025), Moroccan-Jewish immigrant from Casablanca
- **User:** Asaf Yaakov Ben-Harrosh (אסף יעקב בן-הראש), Perla's youngest son
- **Scale:** 1,054 recipes in `data.js` (18,859 lines)
- **Live URLs:**
  - https://perlabenharrosh-cookingbook.netlify.app/ (Netlify)
  - https://asafben33.github.io/PerlaBenHarroshCookingBook/ (GitHub Pages)
- **Repo:** `asafben33/PerlaBenHarroshCookingBook` branch `main`
- **Stack:** Static HTML/JS/CSS, no backend, RTL Hebrew UI with EN toggle
- **Fonts:** Frank Ruhl Libre + Heebo (Google Fonts)
- **Current version:** 6.10 (as of 19/04/2026)
- **Planned version:** 7.0 (homepage redesign — this doc)

---

## Critical context — must read before touching code

### Multi-session history (why things are the way they are)

1. **v6.0-v6.5:** Multiple failed attempts at form backend (Netlify Forms → FormSubmit iframe → FormSubmit+_url) — all 403'd.
2. **v6.6 (SUCCESS):** Migrated to Web3Forms. Access key `705d4207-c4a6-43a2-8fdc-d8e202bc6c9c` is intentionally public (email alias). DO NOT revert.
3. **v6.7:** Modal nav made sticky; hero gallery arrows swapped to RTL.
4. **v6.8:** Hero tagline made bold/white. Base font 17px (16px mobile).
5. **v6.9:** PWA install button made always-visible (previously hidden behind Chrome engagement heuristic). Back-to-Top enhanced.
6. **v6.10:** Replaced native `alert()` in PWA install flow with custom modal (`#pwa-modal-*`) to hide browser's "origin says" prefix.

### User preferences (persistent across sessions)

- Hebrew UI throughout; scripts can have English code with Hebrew comments.
- PowerShell commands one at a time (not chained with `;`).
- Deployment cycle: `git add` → `git commit` → `git push` → auto-deploy ~30 seconds.
- Test in incognito window to avoid cache.
- CRLF line endings required in `index.html`.
- Gershayim U+05F4 (״) for ז״ל (not regular quotes).
- Short response mode requested.
- Do NOT create automated fix scripts unless specifically asked.
- User prefers step-by-step instructions for edits, BUT approved Claude doing v7.0 refactor directly.

### Honesty constraint (extremely important)

User has explicitly approved the **staged approach** for v7.0:
- Stage 1 (this): Homepage structural refactor ONLY, no recipe content.
- Stage 2 (future): Build `audit_recipes.py` that flags mechanical issues.
- Stage 3 (future): Fix specific flagged recipes one-by-one.

DO NOT promise to "check every recipe thoroughly" — it's 175-350 hours of real work. User values honesty over false claims of thoroughness. If asked to verify all 1,054 recipes, explain that automated audit is the honest path.

---

## File inventory

| File | Size | Status for v7.0 |
|------|------|-----------------|
| `index.html` | 7,646 lines, ~345KB | **MAJOR changes:** new header, new hero, new nav, new CSS, new JS |
| `data.js` | 18,859 lines | **MINIMAL change:** replace `MENU_STRUCTURE` only. Do NOT touch recipe array `R[]`. |
| `pre_en.js` | ~500 lines | **ADDITIONS only:** new i18n strings for v7.0 UI |
| `book_data.js` | ~70KB | NO CHANGE |
| `about_redesigned.{html,css,js}` | multiple | NO CHANGE |
| `sw.js` | ~2KB | NO CHANGE |
| `manifest.json` | small | NO CHANGE |
| `download_images.py` | 3,248 lines | NO CHANGE |
| `recipe_utils.py`, `add_recipe.py`, `edit_recipe.py` | CLI tools | NO CHANGE |

---

## Current DOM structure (what exists in v6.10)

```
<header class="hdr">                      ← line 1560
  <div class="hdr-inner">
    <div class="hdr-search">...</div>     ← search input
    <div class="hdr-tools">
      <button id="pwa-install-btn">התקן</button>
      <button id="theme-toggle">☀</button>
      <button id="lang-toggle">EN</button>
    </div>
  </div>
</header>

<nav class="cat-nav">                     ← line 1587
  <div class="cat-nav-inner">
    <div id="cat-inner"></div>            ← populated by buildNav()
  </div>
  <div id="nav-panel">                    ← sub-nav drawer
    <div id="nav-panel-inner"></div>
  </div>
</nav>

<section class="hero">                    ← line 1597
  <div class="hero-inner">
    <div class="hero-orn">✦ ✦ ✦</div>
    <h1 class="hero-h1">המטבח של <em>משפחת בן הראש (ארוש\הרוש)</em></h1>
    <p class="hero-tagline">...</p>
  </div>
</section>

<section id="bio" class="bio">            ← line 1607
  <div class="bio-inner">
    <div class="bio-media"> [avatar img] </div>
    <div class="about-body">
      <h2 class="about-h">...</h2>
      <p class="about-memorial">...</p>
      <p class="about-p">...</p>
      <p class="about-p">...</p>
    </div>
  </div>
</section>

<section id="book-wrapper">               ← line 1625
  [book toggle button + collapsible content]
</section>

<section id="about-redesigned">           ← line 1660
  [full redesigned "about" with 10 subsections + gallery]
</section>

<main id="main">                          ← line 2042
  [recipe grid, filter bar, etc.]
</main>

<footer>                                  ← line 2169
```

---

## Key JavaScript touchpoints

### buildNav() — line ~2723
Currently reads `MENU_STRUCTURE` (nested object tree) and renders 2-row category bar + drawer. In v7.0 this gets REPLACED with 5-tier top-level + drawer.

### Internal state variables
- `ACT_CAT` — active category ID (string)
- `ACT_CATS` — array for multi-select
- `ACT_IDS` — Set of specific recipe IDs
- `ACT_HOLIDAY` — active holiday filter
- `ACT_NAV_KEY` — which nav group is expanded
- `R` — the master array of all 1,054 recipes
- `SEARCH` — current search string
- `ACT_DIFF` — difficulty filter ('all', 'easy', 'med', 'hard')

### Key render functions
- `renderGrid()` — redraws recipe card grid based on current filters
- `selectCat(id, hol, groupKey)` — filter by single category
- `selectMulti(ids[], label, groupKey)` — filter by array of cat IDs
- `selectByIds(recipeIds[], label, groupKey)` — filter by specific recipe IDs

### i18n
- Main dictionary: `const DICT = {...}` around line 6540 in `index.html`
- Supplementary: `pre_en.js` has English pre-rendered translations
- Every UI element uses `data-i18n="key"` or `data-i18n-label/title/aria`
- Language toggle: `_LANG` variable, flipped by `#lang-toggle`

---

## Recipe data structure (for reference only)

```javascript
{
  id: 'h1',                               // unique string ID
  cat: 'hol',                             // category (see CATS list)
  badge: 'מטעמי אמא',                    // optional badge label
  title: 'הכוונון המוזהב של פרלה',       // Hebrew title
  desc: 'תיאור קצר',                     // short description
  time: '45 דקות',                       // prep+cook time
  serv: '6-8 מנות',                      // servings
  diff: 'בינוני',                        // difficulty: 'קל'|'בינוני'|'קשה'
  img: 'images/recipes_images/r-h1.jpg', // local image path
  mem: 'סיפור/זיכרון ממקסיקו',          // memory/story (optional)
  ingr: [{q:'2 כוסות', i:'קמח'}, ...],   // ingredients array
  steps: [{t:'5 דק׳', c:'...'}, ...],    // steps with timer
  tip: 'טיפ טיפטיפוני',                 // optional tip
  tags: ['shabbat'],                     // optional tags array
  h: 'shabbat',                          // single holiday tag (for 'hol' cat)
  src: 'https://...',                    // optional source URL
  vid: 'https://youtube.com/...'         // optional video URL
}
```

### Category IDs (20 total)
`all, soups, salads, veg, meat, chick, fish, hol, des, span, iraq, kurd, ashk, yem, pers, buk, tun, isr, turk, nonkosher`

### Per-cuisine recipe counts
- `iraq, kurd, ashk, yem, pers, buk, tun, turk, isr`: 30 each = 270 total
- Moroccan (`soups, salads, veg, meat, chick, fish, hol, des`): 671 total
- Spanish heritage (`span` IDs): 73 total
- Non-kosher (`nk_*` IDs): 40 total
- **Grand total: 1,054**

---

## v7.0 implementation plan

### Change 1 — Unified header

**Location:** `index.html` line 1560-1582

**Current:** Header has ONLY search on left and tools on right. The site name/count appears elsewhere (in the hero + in the grid header).

**Target:** Add `.hdr-brand` div showing site name + recipe count as first element inside `.hdr-inner`:

```html
<header class="hdr" role="banner">
  <div class="hdr-inner">
    <div class="hdr-brand">
      <span class="hdr-brand-title" data-i18n="site_name">ספר הבישול של פרלה</span>
      <span class="hdr-brand-count"><span id="hdr-count">1,054</span> <span data-i18n="recipes_label">מתכונים</span></span>
    </div>
    <div class="hdr-search">...</div>  <!-- unchanged -->
    <div class="hdr-tools">...</div>   <!-- unchanged -->
  </div>
</header>
```

**CSS additions** (~line 155, near `.hdr-brand`):
```css
.hdr-brand {
  display: flex; flex-direction: column; line-height: 1.15;
  flex-shrink: 0; padding-inline-end: .8rem;
  border-inline-end: 0.5px solid rgba(196,147,10,.15);
}
.hdr-brand-title {
  color: var(--c-gold-l);
  font-family: 'Frank Ruhl Libre', serif;
  font-size: .95rem; font-weight: 500;
}
.hdr-brand-count {
  color: rgba(237,224,196,.5);
  font-size: .7rem;
}
html.light .hdr-brand-title { color: #8a5a20; }
html.light .hdr-brand-count { color: rgba(74,42,20,.55); }
@media (max-width: 640px) {
  .hdr-brand-count { display: none; }  /* hide count on narrow screens */
}
```

### Change 2 — Shorter hero

**Location:** `index.html` line 1597-1603

**Current:** Hero has title + tagline only. Nothing else.

**Target:** Add CTA button row under the tagline:

```html
<section class="hero" aria-labelledby="hero-h1">
  <div class="hero-inner">
    <div class="hero-orn" aria-hidden="true">✦ ✦ ✦</div>
    <h1 class="hero-h1" id="hero-h1">המטבח של <em>משפחת בן הראש (ארוש\הרוש)</em></h1>
    <p class="hero-tagline" data-i18n="hero_tagline">לזכרם של פרלה ופנחס בן הראש ז״ל — טעמים שמעלים זכרונות שכמעט שכחנו...</p>
    <div class="hero-cta-row">
      <button class="hero-cta-primary" data-scroll="#main" data-i18n="cta_browse">עיון במתכונים</button>
      <button class="hero-cta-secondary" data-scroll="#book-wrapper" data-i18n="cta_read_book">קרא את הספר</button>
    </div>
  </div>
</section>
```

**JS handler:**
```javascript
document.querySelectorAll('[data-scroll]').forEach(function(btn) {
  btn.addEventListener('click', function() {
    var target = document.querySelector(this.getAttribute('data-scroll'));
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});
```

**CSS:**
```css
.hero-cta-row {
  display: flex; gap: .6rem; justify-content: center;
  flex-wrap: wrap; margin-top: 1.4rem;
}
.hero-cta-primary, .hero-cta-secondary {
  border-radius: 100px; padding: .75rem 1.8rem;
  font-family: inherit; font-size: 1rem; font-weight: 500;
  cursor: pointer; transition: all var(--t-fast);
}
.hero-cta-primary {
  background: var(--c-spice); color: #fff; border: none;
}
.hero-cta-primary:hover { background: var(--c-spice-d); transform: translateY(-1px); }
.hero-cta-secondary {
  background: transparent; color: var(--c-gold-l);
  border: 0.5px solid rgba(196,147,10,.45);
}
.hero-cta-secondary:hover { border-color: var(--c-gold); color: var(--c-gold); }
html.light .hero-cta-secondary { color: #7a3a18; border-color: rgba(184,66,35,.35); }
```

### Change 3 — Bio placement (verify only)

**Finding:** Bio section (#bio, line 1607-1622) is already positioned between Hero and Main. The mockup confirmed this is correct.

**Action:** NO CHANGE needed unless user requests bio content edits (they didn't). Just verify the order remains: `hero → bio → book-wrapper → about-redesigned → main`.

Wait — `main` is currently at line 2042, AFTER `about-redesigned`. The user asked for bio BEFORE the recipe grid. Currently the order is:
1. Hero
2. Bio
3. Book-wrapper
4. About-redesigned (huge 10-section story)
5. Main (recipe grid)

This means the user reaches the recipe grid AFTER scrolling through the book and the about. This is likely what the user calls "too much info on the main page".

**Proposed change:** Move `<main>` to be RIGHT AFTER `<section id="bio">`, so the order becomes:
1. Hero
2. Bio
3. **Main (recipe grid)** ← moved here
4. Book-wrapper (moved down)
5. About-redesigned (moved down)

This matches the mockup's section order exactly.

### Change 4 — Navigation redesign (biggest change)

**Location:** `index.html` line 1587-1594 (HTML) + line ~2723 `buildNav()` (JS) + `data.js` `MENU_STRUCTURE` (data)

**Current nav flow:**
1. User sees row of "chip" buttons for top-level groups
2. Click one → `nav-panel` slides down with sub-chips
3. Click a sub-chip → sometimes reveals deeper sub-chips
4. The tree is 4 levels deep in some paths (e.g., All → Mother's recipes → Main courses → Meat)
5. User complaint: "buttons sometimes disappear", "not organized logically"

**New nav design (from approved mockup):**

**Top row (always visible):** 6 stable buttons:
- הכל (1,054) — all recipes
- מרוקו (671) — morocco group
- ספרד (73) — spain group
- עדות ישראל (270) — communities group
- חגים (80) — holidays group
- לא כשר (40) — non-kosher group

**Drawer (opens beneath row, not overlay):** When user clicks a top button, the drawer shows:
- Grid of sub-category pills with count per pill
- For "עדות ישראל": 9 cuisine pills (Iraq/Kurd/Ashk/Yem/Pers/Buk/Tun/Turk/Isr). Clicking one drills into that cuisine's sub-categories.
- For a specific cuisine (e.g., Iraq): shows sub-groups (soups, meat, rice, desserts) PLUS a distinct red-coral colored "חגי העדה העיראקית" (Iraqi Community Holidays) button.

**Max hierarchy depth:** 2 levels. Never deeper.

### Change 5 — MENU_STRUCTURE rewrite in data.js

**Current structure:** Single top-level "כל המתכונים" wrapping everything inside. Deeply nested.

**New structure:** 6 parallel top-level groups, each with its own items[]:

```javascript
const MENU_STRUCTURE = [
  {
    key: 'all', lbl: 'הכל', id: 'all'
  },
  {
    key: 'morocco', lbl: 'מרוקו',
    ids: ['soups','salads','veg','meat','chick','fish','hol','des'],
    items: [
      { id: 'all_morocco', lbl: 'הכל', ids: ['soups','salads','veg','meat','chick','fish','hol','des'] },
      { id: 'soups',  lbl: 'מרקים' },
      { id: 'salads', lbl: 'סלטים' },
      { ids: ['meat','chick','fish'], lbl: 'מנות עיקריות' },
      { id: 'veg',  lbl: 'ירקות ותוספות' },
      { id: 'hol',  lbl: 'חגים ומועדים', openHolidays: true },
      { id: 'des',  lbl: 'קינוחים ומאפים' }
    ]
  },
  {
    key: 'spain', lbl: 'ספרד',
    ids: [/* ALL spanish recipe IDs */],
    items: [
      /* 8 sub-groups from current MENU_STRUCTURE */
    ]
  },
  {
    key: 'communities', lbl: 'עדות ישראל',
    ids: ['iraq','kurd','ashk','yem','pers','buk','tun','turk','isr'],
    items: [
      { id: 'iraq', lbl: 'עיראק', hasHolidays: true },
      { id: 'kurd', lbl: 'כורדיסטן', hasHolidays: true },
      { id: 'ashk', lbl: 'אשכנז', hasHolidays: true },
      { id: 'yem', lbl: 'תימן', hasHolidays: true },
      { id: 'pers', lbl: 'פרס', hasHolidays: true },
      { id: 'buk', lbl: 'בוכרה', hasHolidays: true },
      { id: 'tun', lbl: 'טוניסיה', hasHolidays: true },
      { id: 'turk', lbl: 'יהדות טורקיה', hasHolidays: true },
      { id: 'isr', lbl: 'מטבח ישראלי', hasHolidays: true,
        items: [/* existing israeli sub-groups */] }
    ]
  },
  {
    key: 'holidays', lbl: 'חגים',
    ids: ['hol'],
    items: [
      { id: 'hol', h: null, lbl: 'כל החגים' },
      { id: 'hol', h: 'shabbat', lbl: 'שבת' },
      { id: 'hol', h: 'rosh', lbl: 'ראש השנה' },
      { id: 'hol', h: 'kippur', lbl: 'יום כיפור' },
      { id: 'hol', h: 'pesach', lbl: 'פסח' },
      { id: 'hol', h: 'mimouna', lbl: 'מימונה' },
      { id: 'hol', h: 'hanukkah', lbl: 'חנוכה' },
      { id: 'hol', h: 'purim', lbl: 'פורים' },
      { id: 'hol', h: 'shavuot', lbl: 'שבועות' },
      { id: 'hol', h: 'sukkot', lbl: 'סוכות' },
      { id: 'hol', h: 'henna', lbl: 'חינה' }
    ]
  },
  {
    key: 'nonkosher', lbl: 'לא כשר',
    ids: [/* all nk_* IDs */],
    items: [
      { ids: [/* seafood nk_f* */], lbl: 'פירות ים' },
      { ids: [/* meat+dairy nk_* */], lbl: 'בשר וחלב' }
    ]
  }
];
```

### Change 6 — "Per-cuisine holidays" semantics

**User requirement:** Each ethnic group should show "holidays of that community" — the Jewish holidays are shared, but the dishes per holiday differ per community.

**Discovery during planning:**

I checked `HOLIDAY_TAGS` in data.js. It ONLY contains recipes from the Moroccan core (`h*`, `hn*`, `hle*`, `hv*`, `hw*`, `hx*`, `holf*`, `holfx*` IDs). The 270 ethnic community recipes (Iraq through Israeli) have NO holiday tags.

**This means:** The user's requested "Iraqi Community Holidays" group cannot be populated automatically because the data doesn't exist yet. Three paths forward (user to choose):

- **A. Manual full tagging:** User provides a list like "In Iraqi cuisine, recipes X, Y, Z are served on Rosh Hashanah; A, B on Shavuot..." — Claude tags data.js accordingly.
- **B. Partial AI tagging:** Claude tags based on general Jewish cuisine knowledge (e.g., "sufganiyot → Hanukkah" across all communities). Risk: cultural inaccuracy. Claude would note source.
- **C. Defer to stage 2:** Ship v7.0 with empty "Cuisine Holidays" groups that show "No recipes tagged yet — coming soon". Add tags in a future iteration.

**Claude's recommendation to user:** C for v7.0, then A later. (Honesty: Claude does not have authoritative knowledge of 9 distinct community holiday traditions.)

**User must choose before implementation begins.**

---

## i18n strings to add (to `pre_en.js` and `DICT` in `index.html`)

```javascript
// Site identity
site_name: { he: 'ספר הבישול של פרלה', en: "Perla's Cookbook" },
recipes_label: { he: 'מתכונים', en: 'recipes' },

// CTAs
cta_browse: { he: 'עיון במתכונים', en: 'Browse Recipes' },
cta_read_book: { he: 'קרא את הספר', en: 'Read the Book' },
cta_family_story: { he: 'הסיפור של המשפחה', en: 'Family Story' },

// Top-level nav groups
nav_all: { he: 'הכל', en: 'All' },
nav_morocco: { he: 'מרוקו', en: 'Morocco' },
nav_spain: { he: 'ספרד', en: 'Spain' },
nav_communities: { he: 'עדות ישראל', en: 'Jewish Communities' },
nav_holidays: { he: 'חגים', en: 'Holidays' },
nav_nonkosher: { he: 'לא כשר', en: 'Non-Kosher' },

// Per-cuisine holiday groups
hol_iraq:  { he: 'חגי העדה העיראקית',     en: 'Iraqi Holidays' },
hol_kurd:  { he: 'חגי העדה הכורדיסטאנית',  en: 'Kurdish Holidays' },
hol_ashk:  { he: 'חגי העדה האשכנזית',      en: 'Ashkenazi Holidays' },
hol_yem:   { he: 'חגי העדה התימנית',       en: 'Yemenite Holidays' },
hol_pers:  { he: 'חגי העדה הפרסית',        en: 'Persian Holidays' },
hol_buk:   { he: 'חגי העדה הבוכרית',       en: 'Bukharian Holidays' },
hol_tun:   { he: 'חגי העדה הטוניסאית',     en: 'Tunisian Holidays' },
hol_turk:  { he: 'חגי העדה הטורקית',       en: 'Turkish Holidays' },
hol_isr:   { he: 'חגי העדה הישראלית',      en: 'Israeli Holidays' }
```

---

## Design tokens (preserve across all CSS work)

```css
:root {
  /* Dark theme (default) */
  --c-bg:        #fdf8ee;
  --c-bg2:       #f5ecd7;
  --c-bg3:       #ede0c4;
  --c-deep:      #130c05;
  --c-dark:      #2a1508;
  --c-mid:       #4e2010;
  --c-wood:      #7a3a18;
  --c-gold:      #c4930a;
  --c-gold-l:    #e5b020;
  --c-gold-d:    #9a7208;
  --c-spice:     #b84223;
  --c-spice-d:   #8c2e14;
  --c-spice-l:   #d4603a;
  --c-herb:      #3d6e3a;
  --c-ink:       #1c1008;
  --c-ink-m:     #4a2a14;
  --c-ink-l:     #8a6040;
  --c-bdr:       rgba(196,147,10,.18);
  --c-bdr2:      rgba(196,147,10,.08);
  /* Shadows */
  --sh-xs: 0 1px 3px  rgba(20,8,2,.08);
  --sh-sm: 0 2px 8px  rgba(20,8,2,.10);
  --sh-md: 0 6px 24px rgba(20,8,2,.15);
  --sh-lg: 0 16px 48px rgba(20,8,2,.22);
  --sh-xl: 0 32px 80px rgba(20,8,2,.30);
  /* Radii */
  --r-sm: 6px; --r-md: 12px; --r-lg: 18px; --r-xl: 24px;
  /* Transitions */
  --ease: cubic-bezier(.4,0,.2,1);
  --t-fast: .15s; --t-med: .25s;
  /* Layout */
  --hdr-h: 56px; --nav-h: 60px;
  /* Base font */
}

/* v6.8: +6% readability */
html { font-size: 17px; }
@media (max-width: 480px) { html { font-size: 16px; } }
```

Do NOT change these variables. Do NOT introduce new color variables unless absolutely needed.

---

## Things NOT to break

### PWA install button (v6.10)
- Button: `#pwa-install-btn` in `.hdr-tools` — keep intact in new header
- Modal: `#pwa-modal-ovl` near `#back-top` — do NOT remove
- JS: IIFE at ~line 7340 — do NOT modify

### Back-to-Top (v6.9)
- Button: `#back-top` — keep at current location
- CSS: `#back-top { ... }` at line 796 — keep intact
- JS: handler at ~line 3782 — keep intact

### Feedback form (v6.6 Web3Forms)
- CSP: `connect-src 'self' https://api.web3forms.com;` — do NOT change
- JS constant `WEB3FORMS_KEY = '705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'` — PUBLIC BY DESIGN, do NOT obfuscate
- Feedback FAB button: preserve position + styling

### Theme toggle + lang toggle
- `#theme-toggle`, `#lang-toggle` — preserve IDs and handler bindings
- `html.light` class — all light-theme overrides must continue to work

---

## Testing checklist (before pushing v7.0)

1. Run `node -c data.js` — syntax valid
2. Run `python3 -c "import re; content = open('index.html').read(); scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL); assert sum(s.count('{') - s.count('}') for s in scripts) == 0, 'JS braces unbalanced'"`
3. Verify recipe count: `grep -c "{id:" data.js` should still equal 1054 (or whatever was before)
4. Manually verify each of 5 top-nav groups leads to valid recipes
5. Verify PWA install button appears (after reload, not in standalone mode)
6. Verify Back-to-Top appears after scrolling 300px
7. Verify language toggle still switches correctly
8. Verify theme toggle still switches between dark/light
9. Verify feedback FAB still opens form modal
10. Verify the bio section is positioned AFTER hero but BEFORE the recipe grid

---

## Deployment commands (PowerShell, one at a time)

```powershell
git add index.html data.js pre_en.js CLAUDE.md CHANGELOG_19-04-2026_v7_0.md
git commit -m "v7.0: Homepage redesign - unified header, shorter hero, bio moved before grid, improved nav with per-cuisine holidays"
git push origin main
```

---

## Expected side effects (not bugs, just things to know)

1. Users who have the site bookmarked will see a different homepage. Recipes still accessible — just via new nav.
2. Any user with cached CSS/JS may see broken layout until hard-refresh. Service Worker may need version bump in `sw.js` (check if needed — currently `VERSION_TAG` or similar).
3. The previous `MENU_STRUCTURE` had "כל המתכונים" as the top-level wrapper. Removing that changes the URL hash behavior if users bookmarked specific categories. Consider URL migration (optional).
4. `#bio` section's position in the DOM is changing relative to `#main`. Anchor links to `#bio` from elsewhere in the codebase (e.g., footer, about-redesigned) should still work — verify.

---

## Estimated effort

- HTML changes: 30 minutes
- CSS additions: 45 minutes
- JS rewrite (buildNav + helpers): 2 hours
- data.js MENU_STRUCTURE rewrite: 45 minutes
- pre_en.js additions: 15 minutes
- Testing: 45 minutes
- Debugging post-push: 30 minutes (estimated)

**Total: ~4.5 hours of focused work.**

---

## If you're a new Claude picking this up

1. Read this entire doc first. Do NOT skim.
2. Read `PLAN_v7_0_HEBREW.md` as well — it has user-facing context.
3. Verify with user which holiday-tagging option (A/B/C) they chose — this determines scope.
4. Begin with HTML + CSS (lowest risk).
5. Then JS (highest risk — backup `index.html` first).
6. Then data.js MENU_STRUCTURE.
7. Then pre_en.js.
8. Test locally via `file:///` or simple `python3 -m http.server` before asking user to push.

---

## File outputs for this session (19/04/2026)

- `PLAN_v7_0_HEBREW.md` — this doc's Hebrew counterpart
- `PLAN_v7_0_ENGLISH.md` — THIS DOCUMENT
- `CLAUDE.md` — project context (will be updated post-v7.0)
- `CHANGELOG_19-04-2026_v7_0.md` — will be created when v7.0 ships

---

## ═══ Implementation Summary (19/04/2026, evening — post factum) ═══

### Decision made

**Option C** — Community Holidays as empty container (placeholder). Recommended in the plan, user approved, implemented in v7.0.

### What shipped in v7.0

| Planned | Actually implemented | Notes |
|---|---|---|
| Unified header | ✓ `.hdr-brand-v7` added before search bar | Site name + dynamic recipe count |
| Shorter hero with CTAs | ✓ "Browse Recipes" + "Read the Book" | CSS: `.hero-cta-primary`, `.hero-cta-secondary` |
| Bio before recipe grid | ✓ `<main>` moved after `</section>` of bio | New order: Hero → Bio → Main → Book → About |
| Flat 6-group MENU_STRUCTURE | ✓ 6 parallel top-level groups, 2-level max depth | Includes "חגי העדות (בקרוב)" placeholder |
| Incidental fix: WEB3FORMS_KEY | ✓ Restored from placeholder to actual key | Not in original plan — discovered during work and patched |

### What was added in v7.1 (not in the original plan)

After v7.0 deployment, the user screenshotted the homepage and noted that the recipe grid appeared immediately below the Bio — making the page too long and distracting from the book and about sections.

**The request (translated from Hebrew):** "Don't show the recipes on the main page in wide layout — only if I choose from the menu or search for a recipe"

**The solution implemented (v7.1):**
- `<main class="main-hidden">` by default
- `.main-hidden { display: none !important; }` in CSS
- Global functions `showMainGrid()` / `hideMainGrid()`
- Grid reveals when: nav click / search / hero "Browse Recipes" CTA

This was a significant UX change not in the original v7.0 plan but complementary to it.

### Corrected count — incidental fix

The original plan stated:
- **Morocco: 744 recipes** ← wrong

Actually:
- **Morocco: 671 recipes** (soups=103, salads=103, veg=87, meat=82, chick=66, fish=70, hol=80, des=80)

The old HLD and README.md also contained the wrong number 744. The correct number 671 was corrected in all documents as part of post-implementation documentation update.

### Files actually modified

| File | v7.0 | v7.1 | Total |
|---|---|---|---|
| `index.html` | +50 KB (CSS+HTML+JS+i18n+reorder) | +1 KB (CSS+JS+HTML attr) | Significant |
| `data.js` | MENU_STRUCTURE rewrite (+313 bytes) | Unchanged | Minimal |
| `pre_en.js` | Unchanged | Unchanged | — |
| `book_data.js`, `about_redesigned.*`, `sw.js`, `manifest.json`, `download_images.py` | Unchanged | Unchanged | — |

**Recipes:** 1,054 → 1,054 (100% preserved — no content was touched).

### Documents created post-implementation

- `CHANGELOG_19-04-2026_v7_0.md` — full detail of v7.0
- `CHANGELOG_19-04-2026_v7_1.md` — full detail of v7.1 hotfix
- `CHANGELOG_19-04-2026_docs_v7_1.md` — docs update audit trail
- Updates to `CLAUDE.md`, `README.md`, `HLD_Perla_CookingBook.md`, `LLD_Perla_CookingBook.md`, `INTEGRATION_GUIDE.md`

### Notes for future developers / Claude instances

**Do not revert v7.1:** Hiding the grid on load is an explicit user requirement. If future change is wanted, user will request it explicitly.

**Do not restore old MENU_STRUCTURE:** v6.x used single wrapper nested structure, v7.0 uses flat 6-group. This is a significant UX improvement.

**Option C remains open:** Community holiday recipes were NOT tagged. Future (Stage 2) options:
- Ask the user for authentic family/community holiday tagging (Option A from original plan)
- Or leave the placeholder permanently as a reminder that this work is pending

### Stage 2 (future — not done in this session)

Build `audit_recipes.py` — a Python script that scans the 1,054 recipes and flags mechanical issues (missing ingredients, steps too short, missing prep time, etc.). This is the honest path to improve recipe content — not "check every recipe manually" which would be 175-350 hours of actual work.

### Honesty constraint retained

The user values honesty over false claims of thoroughness. Every future session should remember: **Automated audit is the honest path to improving 1,054 recipes, not claimed manual review.**

---

**In memory of Perla Ben-Harrosh z"l (1933-2025)**
