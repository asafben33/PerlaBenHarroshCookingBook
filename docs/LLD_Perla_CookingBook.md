# ספר הבישול של משפחת בן הראש

## LLD — Low Level Design

**גרסה 8.38 | 22 אפריל 2026**

*מפרט טכני מפורט — מבנה הקבצים, CSS, DOM, JS, State, Storage, Security, Service Worker.*

| פרט | ערך |
|---|---|
| Repository | github.com/asafben33/PerlaBenHarroshCookingBook |
| גרסה נוכחית | 8.38 (22/04/2026) |
| `index.html` | ~520 KB, 12,373 שורות |
| `data.js` | ~1,500 KB, 19,073 שורות |
| `pre_en.js` | ~800 KB |
| `book_data.js` | ~228 KB |
| `sw.js` | 3.8 KB (v19) |
| `_headers` | 2.2 KB |

> **מקור סמכות:** `docs/CLAUDE.md`. מסמך זה מציג מפרט טכני מפורט; שינויים שוטפים מתועדים ב-CLAUDE.md + CHANGELOGs.

---

## תוכן עניינים

1. [מבנה קובץ `index.html`](#1-מבנה-קובץ-indexhtml)
2. [CSS Design Tokens](#2-css-design-tokens)
3. [CSS Classes עיקריים](#3-css-classes-עיקריים)
4. [מבנה DOM — IDs עיקריים](#4-מבנה-dom--ids-עיקריים)
5. [פונקציות JavaScript — קטלוג](#5-פונקציות-javascript--קטלוג)
6. [State Variables Global](#6-state-variables-global)
7. [LocalStorage Schema](#7-localstorage-schema)
8. [MENU_STRUCTURE — מפרט מלא](#8-menu_structure--מפרט-מלא)
9. [`buildPanel` — זרימה מלאה](#9-buildpanel--זרימה-מלאה)
10. [תתי-קטגוריות — recipe ID arrays](#10-תתי-קטגוריות--recipe-id-arrays)
11. [מערכת תרגום — מימוש](#11-מערכת-תרגום--מימוש)
12. [מערכת פידבק — Web3Forms](#12-מערכת-פידבק--web3forms)
13. [`download_images.py` v5.1](#13-download_imagespy-v51)
14. [Content Security Policy — מפרט מלא](#14-content-security-policy--מפרט-מלא)
15. [JSON-LD Schema.org](#15-json-ld-schemaorg)
16. [Error Handling & Edge Cases](#16-error-handling--edge-cases)
17. [Service Worker — `sw.js` v19](#17-service-worker--swjs-v19)
18. [Glossary של גרסאות קריטיות](#18-glossary-של-גרסאות-קריטיות)

---

## 1. מבנה קובץ `index.html`

מבנה לוגי (ולא קפדני פר-שורה, כי הקובץ עודכן הרבה):

| קטע | תיאור | שורות משוערות |
|---|---|---|
| `<head>` | meta tags (CSP, OG, Twitter, JSON-LD, icons, manifest, sitemap link) | 1-80 |
| `<style>` inline | CSS מלא — tokens, layout, components, print, dark/light theme, @media queries | 80-~3000 |
| `<body>` | Skip link + Header + Hero + Bio + Main + Book + About | ~3000-3080 |
| Global state | `let ACT_CAT`, `ACT_HOLIDAY`, `ACT_IDS`, ... | ~3083 |
| Helper utilities | `_safeLS`, `debounce`, toast, a11y helpers | ~3100-3500 |
| Recipe rendering | `renderGrid`, `buildCard`, card/modal logic | ~3500-4500 |
| Modal & gallery | `openModal`, `closeModal`, `_heroGalleryInit`, user media | ~4500-6800 |
| Nav/Panel | `buildNav`, `buildPanel`, `selectCat`, `selectMulti`, `selectByIds`, `selectCommunityHoliday`, `showMainGrid`, `hideMainGrid` | ~6800-7600 |
| Search | `doSearch`, index building | ~7600-8000 |
| Personal media | `savePersonalImage`, `deletePersonalImage` (localStorage-based) | ~8000-8100 |
| i18n | `DICT`, `_NAV_I18N`, `t()`, `applyLang()`, `_PRE_EN` wiring | ~8300-11700 |
| Feedback | modal + `submitFeedback` + mailto fallback + `WEB3FORMS_KEY` | ~11780-12050 |
| PWA install | IIFE — `beforeinstallprompt`, custom modal, platform-specific guides | ~12100-12370 |
| Footer + scripts | script tags for data.js, pre_en.js, book_data.js, about_redesigned.js | ~12370-12373 |

### 1.1 עקרונות עריכה

- **UTF-8 + CRLF** — Windows שומר את הקובץ ב-CRLF. אחרי עריכה ב-Python יש לנרמל בינארית (כתוב במפורש `\r\n`).
- **כל הקוד inline** — אין קבצי JS/CSS חיצוניים. בכוונה — מפשט PWA shell caching.
- **`</body>` מופיע פעם אחת** בסוף. קיימים 2 `</body>` **בתוך** מחרוזות JS (הדפסה, popups) — לא להתבלבל.

---

## 2. CSS Design Tokens

מוגדרים ב-`:root` (dark theme) עם overrides ב-`html.light` (light theme). ~34 custom properties. דוגמאות מפתח:

### 2.1 Colors

```css
:root {
  --c-bg:        #130c05;  /* background (dark) */
  --c-paper:     #1a1108;  /* card bg (dark) */
  --c-ink:       #e8d9b8;  /* text primary */
  --c-muted:     #a08b6a;  /* text secondary */
  --c-spice:     #c57a3b;  /* accent warm (primary CTAs) */
  --c-gold:      #e5b020;  /* accent metal (titles, FAB) */
  --c-border:    rgba(197, 122, 59, 0.28);
  --c-overlay:   rgba(0, 0, 0, 0.78);
}
html.light {
  --c-bg:    #fdf8ee;
  --c-paper: #fff;
  --c-ink:   #2a1d10;
  --c-muted: #6e5a3e;
  /* spice/gold stay similar — צבעי מותג */
}
```

### 2.2 Typography

```css
--f-title: 'Frank Ruhl Libre', 'Noto Serif Hebrew', serif;
--f-body:  'Heebo', 'Assistant', sans-serif;
--fs-base: 17px;    /* 16px במובייל */
```

### 2.3 Layout / Spacing

```css
--nav-h:     60px;   /* nav bar height */
--hdr-h:     64px;
--gap-xs: .4rem;  --gap-sm: .7rem;  --gap-md: 1rem;  --gap-lg: 1.5rem;
--radius-sm: 8px;  --radius-md: 14px;  --radius-lg: 22px;
--shadow-sm: 0 2px 6px rgba(0,0,0,.35);
--shadow-md: 0 8px 24px rgba(0,0,0,.45);
```

### 2.4 Breakpoints

`@media (max-width: 480px)` — mobile | `481-768` — large phone | `769-1200` — tablet | `1201+` — desktop.

---

## 3. CSS Classes עיקריים

### 3.1 Header & Nav

| Class | תפקיד |
|---|---|
| `.hdr` | wrapper header |
| `.hdr-inner` | container (max-width 1100px, v7.5) |
| `.hdr-brand-v7` | brand strip (site name + count, v7.0) |
| `.hdr-search` | search input container |
| `.hdr-tools` | toolbar icons (lang, theme, PWA, book toggle) |
| `.cat-nav` | main nav bar |
| `.cat-nav-inner` | nav container (centered) |
| `.nb` | nav button (top-level group) |
| `.nb-cnt` | count badge inside nav button |
| `.nb-arr` | chevron for dropdown |
| `.nav-panel` | dropdown open state |
| `.nav-panel-inner` | dropdown container |
| `.panel-row` | top-level row inside panel (v8.38: קובע את ה-focused-view scope) |

### 3.2 Accordion chips

| Class | תפקיד |
|---|---|
| `.pc` | panel chip (leaf item) |
| `.pc.active` | selected chip |
| `.pc-cnt` | count badge inside chip |
| `.pc-comm-hol` | community-holiday chip (אלמוגי, v7.3) |
| `.pc-empty` | no-recipes chip (אפור + cursor:help) |
| `.acc-hdr` | accordion header (expandable sub-folder) |
| `.acc-hdr.open` | expanded state (v8.37: mutual exclusion) |
| `.acc-body` | accordion content wrapper |
| `.acc-body.open` | expanded body |

**v8.34 shrink:** chips הוקטנו ~30% (padding/fontsize) כדי להכיל folders צפופים כמו "חגים ומועדים".

**v8.38 focused-view:**
```css
:is(.panel-row, .acc-body):has(> .acc-hdr.open) > .acc-hdr:not(.open),
:is(.panel-row, .acc-body):has(> .acc-hdr.open) > .acc-body:not(.open) {
  display: none !important;
}
```

### 3.3 Hero & Main

| Class | תפקיד |
|---|---|
| `.hero` | section (v7.0: ממורכז, max-width 760) |
| `.hero-cta-row` | 2 כפתורי CTA (v7.0) |
| `.hero-cta-primary` | "עיון במתכונים" (רקע `--c-spice`) |
| `.hero-cta-book` | "קרא את הספר" (זהוב שקוף) |
| `.main-hidden` | `display: none !important` — רשת מוסתרת (v7.1) |
| `.grid` | `<main>` recipe grid |
| `.card` | recipe card |
| `.card-img` / `.card-title` / `.card-desc` | תוכן קלף |

### 3.4 Modal (Recipe)

| Class | תפקיד |
|---|---|
| `.m-ovl` | overlay (רקע כהה) |
| `.m-box` | modal container |
| `.m-hero` | hero image + gallery |
| `.m-body` | content wrapper |
| `.m-actions` | action buttons bar |
| `.m-feedback-act` | "הערה / תיקון" (v8.35: צבעי FAB) |

### 3.5 FAB & Feedback

| Class | תפקיד |
|---|---|
| `#fb-fab` | Floating Action Button "הצעות ודיווח" |
| `#fb-ovl` / `#fb-form` | feedback modal |
| `.fb-status` | success/error display |

---

## 4. מבנה DOM — IDs עיקריים

| ID | תפקיד |
|---|---|
| `#skip-link` | skip to main (a11y) |
| `#srch` | search input |
| `#lang-toggle` | HE/EN toggle |
| `#theme-toggle` | dark/light |
| `#pwa-install-btn` | PWA install (v6.9: תמיד נראה) |
| `#book-toggle` | פתיחת/סגירת הספר |
| `#book-wrapper` | תוכן הספר (scroll mode בלבד מ-v8.33) |
| `#nav-panel` | dropdown container |
| `main` | `<main>` grid (`class="main-hidden"` כברירת מחדל, v7.1) |
| `#hdr-count` | ספירת מתכונים בכותרת (1,056) |
| `#hero-cta-browse` / `#hero-cta-book` | 2 כפתורי CTA (v7.0) |
| `#fb-fab`, `#fb-ovl`, `#fb-form` | Feedback FAB + modal |
| `#back-top` | Back-to-top button (v6.9) |
| `#pwa-modal-ovl`, `#pwa-modal-box` | PWA install custom modal (v6.10) |

---

## 5. פונקציות JavaScript — קטלוג

פונקציות עיקריות (לא כולל helpers פנימיים):

### 5.1 Rendering

| פונקציה | מיקום | תפקיד |
|---|---|---|
| `renderGrid()` | ~4500 | מרנדר את רשת המתכונים לפי `ACT_*` state |
| `buildCard(r)` | ~4400 | HTML לקלף מתכון |
| `openModal(id)` | ~4700 | פותח modal מלא של מתכון |
| `closeModal()` | ~5100 | סגירה + reset focus |
| `_heroGalleryInit()` | ~7800 | גלריית תמונות במודאל + user media |

### 5.2 Nav / Panel (v8.38)

| פונקציה | שורה | תפקיד |
|---|---|---|
| `buildNav()` | 7021 | בונה 4 כפתורים עליונים + wiring |
| `buildPanel(node, pi)` | 7203 | רקורסיבי; בונה את תוכן ה-dropdown |
| `panelCnt(item)` | 7059 | walker רקורסיבי — ספירת מתכונים לתת-עץ |
| `_itemHasActive(it)` | 7488 | walker — האם הפריט או צאצא תואם state נוכחי |
| `_closeSiblingAccordions(hdr)` | 7030 | סוגר accordions אחים (v8.37) |
| `selectCat(catId, hol, groupKey)` | 7119 | בחירת קטגוריה בסיסית |
| `selectMulti(ids, label, groupKey)` | 7137 | מספר קטגוריות יחד (`morocco_span`) |
| `selectByIds(recipeIds, label, groupKey)` | 7155 | סינון לפי רשימת IDs (מסורתיים לעדה / non-kosher) |
| `selectCommunityHoliday(community, holidayKey, label, groupKey)` | 7176 | חג × עדה (v7.4) |
| `showMainGrid()` | 6824 | חושף את `<main>` |
| `hideMainGrid()` | 6831 | מסתיר בחזרה |

### 5.3 Search

| פונקציה | תפקיד |
|---|---|
| `doSearch(val)` | סינון לפי טקסט + קריאה ל-`showMainGrid()` |
| `_buildSearchIndex()` | index ראשוני מ-`R` |

### 5.4 Personal media (localStorage)

| פונקציה | תפקיד |
|---|---|
| `savePersonalImage(rid, dataUrl)` | שומר תמונה אישית של משתמש ל-recipe |
| `deletePersonalImage(rid)` | מוחק |
| `loadPersonalMedia(rid)` | קורא |

### 5.5 i18n

| פונקציה | תפקיד |
|---|---|
| `t(key)` | lookup ב-DICT לפי שפה נוכחית |
| `applyLang(lang)` | סורק DOM, מחליף טקסטים לפי `_NAV_I18N` + `data-i18n-key` |

### 5.6 Feedback

| פונקציה | תפקיד |
|---|---|
| `openFeedbackModal(type, recipe)` | פותח modal פידבק |
| `submitFeedback()` | שולח ל-Web3Forms |
| `openMailtoFallback(data)` | mailto fallback |

### 5.7 Theme & Utilities

| פונקציה | תפקיד |
|---|---|
| `toggleTheme()` | dark ⇄ light + `localStorage.perla_theme` |
| `showToast(msg)` | toast ARIA-live |
| `debounce(fn, ms)` | helper |
| `_safeLS(fn)` | try/catch wrapper ל-localStorage |

---

## 6. State Variables Global

(index.html:3083-3095)

| משתנה | ערך התחלתי | תפקיד |
|---|---|---|
| `ACT_CAT` | `'all'` | קטגוריה פעילה |
| `ACT_CATS` | `[]` | multi-cat (למשל `morocco_span`) |
| `ACT_HOLIDAY` | `null` | חג פעיל (למסננים של `HOLIDAY_TAGS`) |
| `ACT_DIFF` | `'all'` | מסנן קושי (קל/בינוני/מתקדם) |
| `ACT_TIME` | `'all'` | מסנן זמן (30/60/120/121 דקות) |
| `SEARCH` | `''` | טקסט חיפוש |
| `SHOW_FAVS` | `false` | מצב "מועדפים בלבד" |
| `ACT_IDS` | `null` | `Set<string>` של IDs (sub-cat ספציפיות) |
| `ACT_NAV_KEY` | `'all_group'` | מסמן איזה nav button "active" |
| `FAV` | `new Set()` | IDs של מועדפים |
| `ING_TAGS` | `new Set()` | מרכיבים שהמשתמש בחר (סינון פעיל) |
| `CUR_REC` | `null` | המתכון הפתוח במודאל |
| `CUR_IDX` | `-1` | אינדקס במודאל (לניווט ←/→) |

---

## 7. LocalStorage Schema

כל המפתחות ב-prefix `perla_*`:

| Key | ערך | עדכון |
|---|---|---|
| `perla_favs` | JSON array של recipe IDs | `FAV` set |
| `perla_media_{rid}` | JSON — user-uploaded images/URLs למתכון | ריבוי תמונות |
| `perla_img_{rid}` | (legacy) single image URL | **נמחק** כשקיים `perla_media_` |
| `perla_vid_del_{rid}` | `'1'` — המשתמש ביטל את הסרטון | boolean הסתרה |
| `perla_lang` | `'he'` / `'en'` | שפת ממשק |
| `perla_theme` | `'dark'` / `'light'` | theme |
| `perla_pwa_dismissed` | `'yes'` | המשתמש סגר את כפתור ה-PWA install |

**`_safeLS(fn)` wrapper** — עוטף `localStorage` ב-try/catch (Safari private mode זורק).

---

## 8. MENU_STRUCTURE — מפרט מלא

ב-`data.js:18884`. מבנה נוכחי (v7.8 + v7.9 + v8.15 + v8.28):

```javascript
const MENU_STRUCTURE = [
  /* 1. הכל — leaf */
  {id:'all', lbl:'הכל'},

  /* 2. מרוקו\ספרד — 744 מתכונים */
  {lbl:'מרוקו\\ספרד', key:'morocco_span', items:[
    {lbl:'כל מתכוני מרוקו וספרד',
     ids:['soups','salads','veg','meat','chick','fish','hol','des','span']},
    {id:'soups',  lbl:'מרקים'},
    {id:'salads', lbl:'סלטים'},
    {id:'veg',    lbl:'תבשילי ירקות'},
    {id:'meat',   lbl:'בשר וקציצות'},
    {id:'chick',  lbl:'עוף ושבת'},
    {id:'fish',   lbl:'דגים'},
    {lbl:'חגים ומועדים', items:[                        // v7.8
      {id:'hol', lbl:'כל מתכוני החגים'},
      {id:'hol', h:'shabbat',  lbl:'שבת'},              // 54
      {id:'hol', h:'rosh',     lbl:'ראש השנה'},         // 14
      {id:'hol', h:'kippur',   lbl:'יום כיפור'},        // 0
      {id:'hol', h:'pesach',   lbl:'פסח'},              // 4
      {id:'hol', h:'mimouna',  lbl:'מימונה'},           // 7 (מרוקו בלבד)
      {id:'hol', h:'hanukkah', lbl:'חנוכה'},            // 2
      {id:'hol', h:'purim',    lbl:'פורים'},            // 1
      {id:'hol', h:'shavuot',  lbl:'שבועות'},           // 12
      {id:'hol', h:'sukkot',   lbl:'סוכות'},            // 27
      {id:'hol', h:'henna',    lbl:'חינה'}              // 14
    ]},
    {id:'des',  lbl:'קינוחים ומאפים'},
    {id:'span', lbl:'ספרד (אנדלוסי)'}
  ]},

  /* 3. מתכונים טעימים מעוד עדות — 270 (v8.15: renamed from "עדות ישראל") */
  {lbl:'מתכונים טעימים מעוד עדות', key:'communities', items:[
    {lbl:'עיראק', items:[
      {id:'iraq', lbl:'כל המתכונים'},
      {lbl:'מאכלים מסורתיים לעדה', ids:[/* IDs */]},
      {lbl:'מאכלי חגים', items:[                        // 9 חגים (ללא מימונה)
        {communityHoliday:'iraq', holidayKey:'shabbat', lbl:'שבת'},
        {communityHoliday:'iraq', holidayKey:'rosh',    lbl:'ראש השנה'},
        // ... 7 more
      ]}
    ]},
    /* כורדיסטן, אשכנז (ללא חינה v8.28), תימן, פרס, בוכרה, טוניסיה, טורקיה,
       מטבח ישראלי (ללא חינה v8.28) — same 3-item pattern */
  ]},

  /* 4. לא כשר — 40 (14 פירות ים + 26 בשר+חלב) */
  {id:'nonkosher', lbl:'לא כשר'}
];
```

### 8.1 סוגי פריטים (entry types) ב-buildPanel

| מפתח | סמנטיקה |
|---|---|
| `{id, lbl}` | leaf של קטגוריה — `selectCat(id)` |
| `{id, h, lbl}` | קטגוריה + חג — `selectCat(id, h)` (שימוש ב-HOLIDAY_TAGS) |
| `{ids, lbl}` | ids של קטגוריות — `selectMulti()` |
| `{ids, lbl}` שבו `ids[0]` נראה כ-recipe ID (למשל `iq7`) | ids של מתכונים — `selectByIds()` |
| `{communityHoliday, holidayKey, lbl}` | עדה × חג — `selectCommunityHoliday()` |
| `{lbl, items:[...]}` | accordion |
| `{lbl, key, items:[...]}` | top-level group with explicit key |

`buildPanel` מזהה את סוג הפריט ע"י בדיקת המפתחות הקיימים.

---

## 9. `buildPanel` — זרימה מלאה

זוהי הפונקציה הקריטית ביותר של התפריט. רקורסיבית עד 3 רמות קינון (קבוצה → עדה → תיקייה → חג).

### 9.1 מבנה רקורסיה

```
node (קבוצה top-level עם items)
├── item (sub-item של הקבוצה)
│   ├── {id, lbl}                  → chip (.pc) → selectCat
│   ├── {ids, lbl}                 → chip (.pc) → selectMulti / selectByIds
│   ├── {communityHoliday, ...}    → chip (.pc-comm-hol) → selectCommunityHoliday
│   └── {lbl, items}               → accordion (.acc-hdr + .acc-body)
│        └── s (sub-item)          ← רקורסיה רמה 2
│             ├── {id|ids|communityHoliday, lbl} → chip
│             └── {lbl, items}     → nested accordion
│                  └── ns (sub-sub) ← רקורסיה רמה 3
```

### 9.2 Auto-expand (v8.36)

לכל `.acc-hdr` שנבנית, הפונקציה קוראת ל-`_itemHasActive(item)`:

```javascript
function _itemHasActive(it) {
  if (!it) return false;
  if (it.id && ACT_CAT === it.id && !ACT_HOLIDAY) return true;
  if (it.h && ACT_HOLIDAY === it.h && ACT_CAT === it.id) return true;
  if (it.communityHoliday && it.holidayKey &&
      ACT_CAT === it.communityHoliday && ACT_HOLIDAY === it.holidayKey) return true;
  if (Array.isArray(it.ids) && ACT_IDS && it.ids.length === ACT_IDS.size &&
      it.ids.every(function(x) { return ACT_IDS.has(x); })) return true;
  var kids = it.items || it.sub;
  return Array.isArray(kids) && kids.some(_itemHasActive);
}
```

אם מחזיר `true` → ה-accordion מתחיל במצב `.open`. **זה מאפשר שפתיחת מודאל של מתכון מפרס, למשל, תבליט את branch "פרס → מאכלי חגים → שבת" פתוח אוטומטית.**

**תיקון v8.36:** לפני ה-fix, הפונקציה הישנה בדקה `item.sub && item.sub.some(...)` — אבל MENU_STRUCTURE משתמש ב-`.items` (לא `.sub`). לכן auto-expand לא עבד כמעט אף פעם.

### 9.3 Sibling mutual exclusion (v8.37)

בכל click על `.acc-hdr`, לפני הפתיחה:

```javascript
function _closeSiblingAccordions(hdr) {
  var parent = hdr.parentElement;
  if (!parent) return;
  Array.prototype.forEach.call(parent.children, function(child) {
    if (child === hdr) return;
    if (child.classList.contains('acc-hdr') && child.classList.contains('open')) {
      child.classList.remove('open');
      child.setAttribute('aria-expanded', 'false');
    }
    if (child.classList.contains('acc-body') && child.classList.contains('open')) {
      var prev = child.previousElementSibling;
      if (prev !== hdr) child.classList.remove('open');
    }
  });
}
```

### 9.4 Focused view (v8.38) — CSS בלבד

לא בקוד JS. CSS מסתיר accordions סגורים כשאחד פתוח באותה רמה:

```css
:is(.panel-row, .acc-body):has(> .acc-hdr.open) > .acc-hdr:not(.open),
:is(.panel-row, .acc-body):has(> .acc-hdr.open) > .acc-body:not(.open) {
  display: none !important;
}
```

דורש Chrome 105+ / Safari 15.4+ / Firefox 121+.

---

## 10. תתי-קטגוריות — recipe ID arrays

### 10.1 "מאכלים מסורתיים לעדה" (v7.4)

לכל עדה — רשימת IDs של מתכונים לא-חגיגיים אופייניים:

| עדה | IDs |
|---|---|
| עיראק | `iq7, iq16, iq23` |
| כורדיסטן | `ku6, ku7, ku8, ku13, ku16` |
| אשכנז | `as13, as15, as16, as21, as23, as26, as29` |
| תימן | `ye11, ye12, ye19, ye23, ye26` |
| פרס | `pe3, pe8, pe12, pe13, pe15, pe20, pe25` |
| ... | ... (ב-`data.js:18884+`) |

### 10.2 לא כשר — 40 IDs

- **14 פירות ים** (`nk_fn*` / `nk_ss*`): שרימפס, קלמרי, סרטן, אוקטופוס, מידיה, חמוצים, ...
- **26 בשר+חלב** (`nk_mm*`): פיצה פפרוני עם גבינה, קרמבו מעורב, ...

---

## 11. מערכת תרגום — מימוש

### 11.1 DICT (index.html:~11900)

~155 מפתחות UI. דוגמה:

```javascript
var DICT = {
  he: {
    site_name_short: 'ספר הבישול',
    recipes_label:   'מתכונים',
    hero_cta_browse: 'עיון במתכונים',
    hero_cta_book:   'קרא את הספר',
    nav_grp_all:     'הכל',
    nav_grp_morocco_span: 'מרוקו\\ספרד',
    nav_grp_communities:  'מתכונים טעימים מעוד עדות',
    nav_grp_nonkosher:    'לא כשר',
    community_holidays_folder: 'מאכלי חגים',
    holiday_shabbat: 'שבת',
    holiday_rosh:    'ראש השנה',
    /* ... 8 more holidays */
  },
  en: { /* parallel EN keys */ }
};
```

### 11.2 `_NAV_I18N` — nav labels mapping

```javascript
var _NAV_I18N = {
  'הכל':                           'nav_grp_all',
  'מרוקו\\ספרד':                   'nav_grp_morocco_span',
  'מתכונים טעימים מעוד עדות':     'nav_grp_communities',
  'לא כשר':                        'nav_grp_nonkosher',
  'מאכלי חגים':                    'community_holidays_folder',
  'שבת':                           'holiday_shabbat',
  /* ... */
};
```

### 11.3 `applyLang(lang)`

1. שומר `localStorage.perla_lang = lang`.
2. סורק `document.querySelectorAll('[data-i18n-key]')` → מחליף `textContent` לפי DICT.
3. סורק `.nb`, `.pc`, `.acc-hdr` → מחפש את ה-label הנוכחי ב-`_NAV_I18N` → מחליף.
4. רינדור מחדש של הרשת (`renderGrid()` משתמש ב-`_PRE_EN` במצב EN).

### 11.4 `_PRE_EN` (pre_en.js)

```javascript
var _PRE_EN = {
  s1:  { d: '...', m: '...', t: '...', st: [...], ig: [...] },
  /* 1,056 entries */
};
```

---

## 12. מערכת פידבק — Web3Forms

### 12.1 Constants

```javascript
// index.html:11795
var WEB3FORMS_KEY  = '705d4207-c4a6-43a2-8fdc-d8e202bc6c9c';
// הערה מפורשת בקוד: המפתח ציבורי בכוונה (email alias)
```

### 12.2 Payload

```javascript
{
  access_key:   WEB3FORMS_KEY,
  subject:      '[Perla Cookbook] ' + subjectLine,
  from_name:    name || '(לא צוין)',
  email:        email || 'noreply@perlabenharrosh.local',
  message:      combinedMessage,      // כולל recipe_id/title אם יש
  page_url:     location.href,
  user_agent:   navigator.userAgent,
  botcheck:     ''                     // honeypot
}
```

### 12.3 זרימה

```
משתמש → FAB / "הערה-תיקון" → openFeedbackModal(type, recipe?)
  → user מזין message (+ name/email אופציונליים)
  → submitFeedback():
     → validate (length, regex email)
     → fetch('https://api.web3forms.com/submit', {method:'POST', body:JSON.stringify(...)})
     → response.json()
     → success: true  → setStatus('תודה! ההודעה נשלחה בהצלחה')
     → success: false → fallback to mailto
     → catch (network/CSP): fallback to mailto
```

### 12.4 CSP relevant

```
connect-src 'self' https://api.web3forms.com https://cdn.jsdelivr.net;
```

### 12.5 Mailto fallback

`openMailtoFallback({subject, body})` — `atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==')` → `mailto:asafben33@gmail.com?subject=...&body=...`. עובד תמיד (גם offline).

---

## 13. `download_images.py` v5.1

### 13.1 Entry points (CLI)

```bash
python download_images.py                    # הרצה רגילה
python download_images.py --reset-images     # מחיקת כל r-*.jpg קודם
python download_images.py --clean-only       # רק שלב 1
python download_images.py --skip-clean       # דלג על שלב 1
python download_images.py --aggressive-clean # סף נמוך יותר של size/aspect
python download_images.py --inline-alias     # אחרי download, עדכן index.html
python download_images.py --dry-run          # הדפסה בלבד
```

### 13.2 שלבי Pipeline

| שלב | פונקציה | תפקיד |
|---|---|---|
| 0 | `auto_detect_proxy()` | משתמש ב-pac.gov.il אם נמצא |
| 0b | `reset_images()` | `--reset-images` — מחיקת כל r-*.jpg |
| 1 | `clean_existing_bad_images()` | EXIF + aspect + size checks |
| 2a | `batch_israeli(titles)` | `"מתכון ל" + title` — 100 IL domains |
| 2b | `batch_international(queries)` | `"recipe " + query` — 100 INTL domains |
| 3 | `dedup_sha256()` | SHA256 hash → `_IMG_ALIAS.js` |
| 3b | `inline_alias_into_index()` | מעדכן `_IMG_ALIAS` ב-index.html |

### 13.3 Tiered Israeli Domains

| Tier | דוגמאות | כמות |
|---|---|---|
| 1 (מאומתים אישית) | ynet, walla, mako, haaretz, foody, hashulchan, mevashlim | ~15 |
| 2 (אומת ע"י web search) | culinartica, pascalpr, fingerfood, pastaeveryday, rotteml | ~30 |
| 3 (סבירים — תאגידים/חדשות) | shufersal, tnuva, osem, strauss-group, maariv | ~30 |
| 4 (best-guess) | jewishcuisine.co.il, moroccan-food.co.il | ~25 |

### 13.4 Filtering

- `_BAD_URL_KW`: ~100 מילות-מפתח דוחות.
- `_is_food_image_by_pixels(img)`: aspect ratio `[0.45, 2.2]` + size `>= 150px`.
- EXIF: דוחה תמונות עם DPI חריג או orientation חריג.

### 13.5 `_IMG_ALIAS` injection

אחרי dedup, ה-script מזהה זוגות (SHA256 זהה) וכותב:

```javascript
var _IMG_ALIAS = { "r-s1-2": "r-s4", /* ... */ };
```

רוכב על הנתיבים: `getRecipeImg(r)` בודק אם `_IMG_ALIAS[fname]` קיים ומשתמש באליאס.

---

## 14. Content Security Policy — מפרט מלא

CSP מוגדרת בשני מקומות — **המקור הסמכותי הוא `_headers`** (HTTP header). ה-meta tag הוא fallback ל-GitHub Pages.

### 14.1 `_headers` CSP (v8.26+)

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
  style-src  'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src   'self' https://fonts.gstatic.com;
  img-src    'self' data: blob: https://i.ytimg.com https://img.youtube.com;
  media-src  'self' blob:;
  connect-src 'self' https://api.web3forms.com https://cdn.jsdelivr.net;
  frame-src  'self' https://www.youtube.com https://www.youtube-nocookie.com;
  object-src 'none';
  base-uri   'self';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
```

### 14.2 ניתוח per-directive

| Directive | מקור | למה |
|---|---|---|
| `default-src 'self'` | — | בסיס הכי מגביל |
| `script-src ... cdn.jsdelivr.net` | Vimeo player, book-related (ב-v8.x לא בשימוש — זמין לעתיד) | עם SRI |
| `script-src 'unsafe-inline'` | כל ה-JS inline | נדרש כי אין קבצי JS חיצוניים |
| `style-src ... fonts.googleapis.com` | Google Fonts CSS | Heebo + Frank Ruhl Libre |
| `font-src fonts.gstatic.com` | קבצי הפונט עצמם | |
| `img-src 'self' data: blob:` | תמונות עצמיות + canvas-generated | |
| `img-src ... i.ytimg.com img.youtube.com` | YouTube thumbnails | |
| `media-src 'self' blob:` | Audio recordings (ל-user media) | |
| `connect-src api.web3forms.com` | POST פידבק | |
| `frame-src youtube-nocookie.com` | embed videos | פרטיות! |
| `object-src 'none'` | חסימה מוחלטת של `<object>` | |
| `base-uri 'self'` | מניעת injection של `<base href="...">` | |
| `form-action 'self'` | חסימת submit ל-origin חיצוני | |
| `frame-ancestors 'none'` | מניעת clickjacking (רק HTTP) | |
| `upgrade-insecure-requests` | ממיר HTTP → HTTPS על pages שלנו | |

### 14.3 `<meta>` CSP

קיים שכפול של חלק גדול ב-`<meta http-equiv="Content-Security-Policy">`. **הערה:** הדפדפן מתעלם מ-`frame-ancestors` ו-`report-uri` ב-meta — לכן אלו **רק** ב-`_headers`.

### 14.4 Additional security headers

| Header | ערך | תפקיד |
|---|---|---|
| `X-Frame-Options` | `DENY` | clickjacking (legacy) |
| `X-Content-Type-Options` | `nosniff` | MIME sniffing |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | privacy |
| `Cross-Origin-Opener-Policy` | `same-origin` | popup isolation |
| `Cross-Origin-Resource-Policy` | `same-site` | resource isolation |
| `X-Permitted-Cross-Domain-Policies` | `none` | Flash legacy |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | HSTS |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), ambient-light-sensor=(), autoplay=(self), fullscreen=(self), interest-cohort=()` | מבטל FLoC + permissions רגישות |

### 14.5 Cache headers

```
/sw.js              → Cache-Control: no-cache, no-store, must-revalidate
/images/*           → Cache-Control: public, max-age=31536000, immutable
(other paths)       → default (Netlify auto)
```

---

## 15. JSON-LD Schema.org

בקובץ index.html בתוך `<head>`:

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "ספר הבישול של משפחת בן הראש",
  "url": "https://perlabenharrosh-cookingbook.netlify.app/",
  "description": "1,056 מתכונים מרוקאיים, ספרדיים ויהודיים אותנטיים",
  "inLanguage": "he-IL",
  "author": { "@type": "Person", "name": "אסף בן הראש" }
}
```

---

## 16. Error Handling & Edge Cases

### 16.1 localStorage failures

`_safeLS(fn)` — try/catch עוטף כל שימוש. Safari במצב private זורק; הקוד מתעלם בשקט.

### 16.2 תמונות חסרות

`_getImgFallbacks(r)` מחזיר רשימה:
1. `images/recipes_images/r-{r.id}.jpg`
2. `CAT_IMG[r.cat]` (cat-*.jpg)
3. `CAT_IMG._def`

`<img onerror="_nextFallback(this)">` מנסה את הבאים.

### 16.3 `_heroGalleryInit` — 404 suppression (v6.5)

גלריית `-2`/`-3` מנסה להוסיף רק אם התמונה **הראשית** נטענת. חסך 2,112 404-ים לכל טעינת דף.

### 16.4 Feedback — CSP/network failures

- `fetch()` catch → mailto fallback.
- 15-second timeout (historical v6.4, לא נדרש ב-Web3Forms אבל נשאר להגנה).

### 16.5 RTL edge cases

- `transform: scaleX(-1)` ניסויים ל-RTL book כשלו (v8.27 → revert). הטקסט הופיע במראה גם אחרי counter-flip.
- StPageFlip v2.0.7 אין לו RTL native — זה אחד הגורמים להסרה ב-v8.33.

### 16.6 CRLF line endings

כל עריכה אוטומטית ב-Python על `index.html` חייבת לנרמל בינארית ל-CRLF. אחרת git diff מראה את כל הקובץ כ-modified.

---

## 17. Service Worker — `sw.js` v19

### 17.1 Cache naming

```javascript
const CACHE_NAME = 'perla-cookbook-v19';
```

**v19** לאחר הסרת 3D book (v8.33). בעת bump של v19 → v20, Activate מנקה את v19 אוטומטית.

### 17.2 SHELL

```javascript
const SHELL = [
  './',
  './index.html',
  './data.js',
  './pre_en.js',
  './manifest.json',
  './images/book_images/wedding.jpg',
  './book_data.js'
];
```

Install — `Promise.all(SHELL.map(cache.add(...).catch(...)))` — resilient-to-404 (ממשיך גם אם קובץ יחיד נכשל).

### 17.3 Strategy per request

```javascript
// התעלמות מ-non-GET (POST)
if (e.request.method !== 'GET') return;

// images: cache-first
if (url.pathname.match(/\.(jpg|jpeg|png|webp|gif)$/i) || url.pathname.includes('/images/')) {
  return caches.match(e.request).then(cached => cached || fetch(e.request).then(cacheResp));
}

// default: network-first
return fetch(e.request).then(resp => { cacheResp(resp); return resp; })
                       .catch(() => caches.match(e.request));
```

### 17.4 `_shouldCache` eligibility

- `request.method === 'GET'`
- `response.type === 'basic'` (same-origin, לא opaque)
- `response.status === 200` (לא 0, 206)

### 17.5 Activation

```javascript
caches.keys().then(keys =>
  Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
).then(() => self.clients.claim());
```

**`clients.claim()` חשוב** — לוקח שליטה מיד בלי לחכות לרענון.

### 17.6 bump discipline

כל שינוי ב-HTML/JS/CSS חייב `CACHE_NAME` bump. Netlify `Cache-Control: no-cache` על `/sw.js` מבטיח שהדפדפן תמיד יבדוק.

---

## 18. Glossary של גרסאות קריטיות

| גרסה | מה קרה | רלוונטי ל- |
|---|---|---|
| v6.1 | הסרת `r.img` מ-fallback (CSP violations) | `_getImgFallbacks` |
| v6.3-v6.5 | מסע FormSubmit → iframe → 403 | feedback history |
| **v6.6** | **מעבר ל-Web3Forms** | `WEB3FORMS_KEY`, CSP `connect-src` |
| v7.0 | flat MENU_STRUCTURE, Hero CTAs, `main-hidden` | `buildNav`, `showMainGrid` |
| v7.2 | **`COMMUNITY_HOLIDAY_TAGS`** (221) | data.js |
| v7.4 | תיקיית "מאכלי חגים" לכל עדה | MENU_STRUCTURE, `selectCommunityHoliday` |
| **v7.7** | **`HOLIDAY_TAGS` תוקן** (80×10→121 unique) | data.js |
| v7.9 | איחוד מרוקו+ספרד | MENU_STRUCTURE |
| v8.0 | i18n wiring מלא, sitemap, robots.txt | `_NAV_I18N`, DICT |
| v8.3 | +2 recipes (1,054→1,056) | R.length, JSON-LD, manifest |
| v8.15 | rename "עדות ישראל" → "מתכונים טעימים מעוד עדות" | DICT, `_NAV_I18N` |
| v8.17-v8.32 | **3D book (StPageFlip)** — נוסף וגלגולים | `#book-flip-container` etc. |
| **v8.26-v8.28** | **חיזוק אבטחה** — HSTS, COOP/CORP, SRI, חינה הוסרה מ-ashk+isr | `_headers`, data.js |
| **v8.33** | **הסרת 3D book** — רק scroll mode | ~1,380 שורות הוסרו |
| v8.34 | chips shrink ~30% | CSS `.pc`, `.acc-hdr` |
| v8.35 | צבעי FAB לכפתור "הערה/תיקון" | CSS `.m-feedback-act` |
| v8.36 | **`_itemHasActive` recursive** — auto-expand של branch פעיל | `buildPanel` |
| v8.37 | **`_closeSiblingAccordions`** — mutual exclusion | `buildPanel` event |
| v8.38 | **Focused-view** CSS `:has()` | CSS שורה הבאה |
| v8.39 | הסרת dead code `placeholder:'communityHolidays'` | `buildPanel`, `panelCnt`, `_itemHasActive` |

---

## 19. Checklist — לפני כל שינוי

1. **שינוי ב-`data.js`**: הרץ `node -c data.js`.
2. **שינוי ב-MENU_STRUCTURE**: ודא שה-`_NAV_I18N` ו-DICT כוללים את הלבלים החדשים (HE + EN).
3. **שינוי ב-`buildPanel`/`buildNav`**: בדוק שכל 5 סוגי ה-entries מטופלים (id, id+h, ids, communityHoliday+holidayKey, items).
4. **שינוי ב-CSS של accordions**: ודא שה-focused-view (v8.38) עדיין עובד.
5. **הוספת פריט עם sub-items**: ודא ש-`_itemHasActive` יזהה אותו אם המשתמש בתוך branch פעיל.
6. **שינוי ב-HTML/JS/CSS**: bump `CACHE_NAME` ב-`sw.js`.
7. **שינוי ב-CSP**: עדכן גם את `_headers` וגם את ה-meta.
8. **הוספת תלות CDN**: הוסף SRI hash + `crossorigin="anonymous"`.
9. **הוספת endpoint חיצוני ל-fetch**: הוסף ל-`connect-src` ב-CSP.
10. **CRLF**: אחרי עריכת Python, נרמל בינארית.

---

## 20. בדיקות before push

```bash
# תחביר
node -c data.js
node -c pre_en.js
# (לא ניתן לבדוק inline JS ישירות; Node לא מריץ HTML)

# ספירות בסיסיות
grep -c "^  {id:" data.js          # צפוי: 1056 (פחות/יותר — תלוי formatting)
grep -c "community_holidays_folder" index.html  # ~5

# SW version bump
grep "const CACHE_NAME" sw.js

# CSP sanity
grep -c "frame-ancestors 'none'" _headers
grep -c "api.web3forms.com" _headers

# verify Hebrew gershayim U+05F4 (״) לא " רגיל
grep "פרלה ופנחס בן הראש ז\"ל" index.html    # should be 0
```

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
*"האוכל שלה — הסיפור שלנו"*

**סוף LLD v8.38**
