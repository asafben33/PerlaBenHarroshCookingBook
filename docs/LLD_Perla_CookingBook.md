# ספר הבישול של משפחת בן הראש

## LLD — Low Level Design

**גרסה 6.4 | 19 אפריל 2026**

*מפרט טכני מלא ומפורט — כל שכבות הקוד, כל פונקציה, כל קומפוננטה*

| פרט | ערך |
|---|---|
| Repository | github.com/asafben33/PerlaBenHarroshCookingBook |
| גרסה נוכחית | 6.4 (19/04/2026) |
| גרסה קודמת | 6.3 (19/04/2026) — נכשלה ב-CORS, הוחלפה |
| גרסת `index.html` | ~375 KB |
| גרסת `download_images.py` | 5.1 (152 KB) |

---

## תוכן עניינים

1. [מבנה קובץ `index.html`](#1-מבנה-קובץ-indexhtml)
2. [CSS Design Tokens — Custom Properties](#2-css-design-tokens--custom-properties)
3. [CSS Classes — רכיבים עיקריים](#3-css-classes--רכיבים-עיקריים)
4. [מבנה DOM — כל ה-IDs](#4-מבנה-dom--כל-ה-ids)
5. [פונקציות JavaScript — מפרט מלא](#5-פונקציות-javascript--מפרט-מלא)
6. [MENU_STRUCTURE — מפרט מלא](#6-menu_structure--מפרט-מלא)
7. [תתי-קטגוריות מורשת ספרד — recipe ID arrays](#7-תתי-קטגוריות-מורשת-ספרד--recipe-id-arrays)
8. [תתי-קטגוריות מטבח ישראלי](#8-תתי-קטגוריות-מטבח-ישראלי)
9. [מתכונים לא כשרים — 40 IDs](#9-מתכונים-לא-כשרים--40-ids)
10. [State Variables Global](#10-state-variables-global)
11. [LocalStorage Schema](#11-localstorage-schema)
12. [מערכת תרגום — פרטי יישום](#12-מערכת-תרגום--פרטי-יישום)
13. [מערכת פידבק — v6.0 (חדש)](#13-מערכת-פידבק--v60-חדש)
14. [`download_images.py` v5.1 — מפרט מלא](#14-download_imagespy-v51--מפרט-מלא)
15. [Content Security Policy — מפרט מלא](#15-content-security-policy--מפרט-מלא)
16. [JSON-LD Schema.org](#16-json-ld-schemaorg)
17. [Error Handling & Edge Cases](#17-error-handling--edge-cases)
18. [שינויים v5.0 → v6.0](#18-שינויים-v50--v60)
19. [שינויים v6.0 → v6.3 — סשן 19/04](#19-שינויים-v60--v63--סשן-1904)

---

## 1. מבנה קובץ `index.html`

הקובץ `index.html` הוא SPA בנפח 359 KB (עודכן מ-303 KB ב-v5.0) המכיל את כל ה-UI כולל מערכת הפידבק החדשה:

| חלק | גודל קירוב | תיאור מפורט |
|---|---|---|
| `<head>` | 2.5 KB | meta charset, viewport, og:title/description/image (1200×630), JSON-LD Schema.org WebSite, CSP מוחזק, manifest, 3 icons (192/512/apple), fonts (Frank Ruhl Libre + Heebo) |
| `<style>` CSS | ~75 KB | 34 CSS Custom Properties, reset, layout, 140+ CSS classes (כולל feedback) |
| HTML structure | ~22 KB | header, hero, about, cat-nav, grid#grid, modal#ovl, #toast, #back-top, #fb-ovl, #fb-fab, hidden Netlify form |
| `var _IMG_ALIAS` | < 1 KB | מפת כפילויות תמונות — מאוכלס ע"י `download_images.py --inline-alias` |
| `var _FOOD_DICT` | ~35 KB | 2,853 ערכי תרגום עברית-אנגלית + morphological engine |
| `var _TITLE_EN` | ~25 KB | 1,054 כותרות מתכונים באנגלית (367 תוקנו) |
| `var _NAV_I18N` | ~3 KB | מיפוי שמות קטגוריות → מפתחות I18N |
| `var I18N` | ~5 KB | כל תרגומי UI: כפתורים, תוויות, הודעות |
| `var CAT_IMG` | ~2 KB | 20 URLs של תמונות fallback לקטגוריות (עודכן ללוקאל מ-Wikimedia) |
| JS functions | ~52 KB | filtered, renderGrid, buildNav, openM, closeM, search, share, translate, feedback system |
| Hidden Netlify form | ~1 KB | `<form name="perla-feedback" data-netlify="true" hidden>` |

---

## 2. CSS Design Tokens — Custom Properties

### 2.1 פלטת צבעים

| משתנה | ערך | שימוש |
|---|---|---|
| `--c-bg` | `#fdf8ee` | רקע כלל-הדף — קרמי בהיר |
| `--c-bg2` | `#f5ecd7` | רקע קומפוננטות — קרמי |
| `--c-bg3` | `#ede0c4` | רקע סקציות, separators |
| `--c-deep` | `#130c05` | header, overlay background |
| `--c-dark` | `#2a1508` | hero, nav header background |
| `--c-mid` | `#4e2010` | nav hover, borders כהים |
| `--c-wood` | `#7a3a18` | accent — חום עץ |
| `--c-gold` | `#c4930a` | צבע accent ראשי — זעפרן |
| `--c-gold-l` | `#e5b020` | hover states, hero titles |
| `--c-gold-d` | `#9a7208` | borders, labels, secondary |
| `--c-spice` | `#b84223` | badge background — פפריקה, feedback primary |
| `--c-spice-d` | `#8c2e14` | badge hover, feedback button hover |
| `--c-spice-l` | `#d4603a` | badge light |
| `--c-herb` | `#3d6e3a` | success, positive — ירוק עשב |
| `--c-ink` | `#1c1008` | primary text |
| `--c-ink-m` | `#4a2a14` | secondary text |
| `--c-ink-l` | `#8a6040` | tertiary text |
| `--c-bdr` | `rgba(196,147,10,.18)` | גבולות עיקריים — זהב שקוף |
| `--c-bdr2` | `rgba(196,147,10,.08)` | גבולות עדינים |

### 2.2 צלליות וערכים

| משתנה | ערך | שימוש |
|---|---|---|
| `--sh-xs` | `0 1px 3px rgba(20,8,2,.08)` | cards |
| `--sh-sm` | `0 2px 8px rgba(20,8,2,.10)` | card hover |
| `--sh-md` | `0 6px 24px rgba(20,8,2,.15)` | nav panel, dropdowns, FAB |
| `--sh-lg` | `0 16px 48px rgba(20,8,2,.22)` | modal, overlay |
| `--sh-xl` | `0 32px 80px rgba(20,8,2,.30)` | feedback modal |
| `--hdr-h` | `56px` | גובה header |
| `--nav-h` | `44px` | גובה nav bar |
| `--r-sm` | `6px` | border-radius small |
| `--r-md` | `12px` | border-radius medium |
| `--r-lg` | `18px` | border-radius large |
| `--r-xl` | `24px` | border-radius extra-large (feedback modal) |
| `--ease` | `cubic-bezier(.4,0,.2,1)` | Material Design easing |
| `--t-fast` | `.15s` | transition fast |
| `--t-med` | `.25s` | transition medium |

---

## 3. CSS Classes — רכיבים עיקריים

### 3.1 Header (עודכן ב-v6.3)

| class | תכונות |
|---|---|
| `.hdr` | `position:sticky; top:0; z-index:600; height:var(--hdr-h); background:var(--c-deep)` |
| `.hdr-inner` | `max-width:1440px; margin:auto; display:flex; align-items:center; gap:1rem; RTL` |
| `.hdr-search` | **v6.3:** `flex:1; max-width:640px; min-width:220px; gap:.6rem; padding:.65rem 1.3rem` (היה `width:320px` קבוע) |
| `#srch` | **v6.3:** `width:100%; min-width:0; font-size:1.05rem; direction:rtl` (היה `width:180px`/`320px`) |
| `.hdr-btn` | `background:none; border:none; color:gold; cursor:pointer; font-size:1.1rem` |
| `.hdr-btn-install` (v6.3) | **חדש — PWA install button:** `display:flex; padding:.45rem .9rem; bg:rgba(196,147,10,.2); border:1px solid gold .45; radius:100px; color:var(--c-gold-l); font:.88rem/700; animation:pwa-pulse 3s infinite` |
| `.hdr-btn-install:hover` | `bg:.32; transform:translateY(-1px); animation:none` |
| `@keyframes pwa-pulse` | `0%/100%: box-shadow 0 0 0 0 rgba(196,147,10,.35); 50%: 0 0 0 6px rgba(196,147,10,.04)` |
| `html.light .hdr-btn-install` | `bg:rgba(196,147,10,.15); color:#8a5a20` |
| `@media (prefers-reduced-motion)` | `.hdr-btn-install { animation: none }` |
| `.hdr-tools` | `display:flex; gap:.3rem; align-items:center; flex-shrink:0` |

### 3.2 Navigation (עודכן משמעותית ב-v6.2/v6.3)

| class | תכונות |
|---|---|
| `.cat-nav` | `position:sticky; top:var(--hdr-h); z-index:500; height:var(--nav-h)` — **v6.3: `--nav-h: 60px`** (היה 44px → 54px → 60px) |
| `.nb` | **v6.3:** `font:1.1rem/700; padding:0 1.5rem; color rgba(245,236,215,.72); border-bottom:3px solid transparent` (היה `.82rem/normal`, padding `0 1rem`, border 2px) |
| `.nb.active` | `color:var(--c-gold-l); border-bottom-color:var(--c-gold)` |
| `.nb-cnt` | **v6.3:** `font-size:.9rem; font-weight:700; background:rgba(196,147,10,.25); padding:.26rem .7rem; color:var(--c-gold-l)` (היה `.65rem/500`, padding `.1rem .4rem`) |
| `.nb-arr` | **v6.3:** `font-size:.88rem; opacity:.75` (היה `.6rem/.6`) |
| `.nav-panel` | `position:absolute; top:calc(hdr+nav); z-index:490` |
| `.nav-panel-inner` | **v6.3:** `padding:1.4rem 1.8rem 1.6rem; display:flex; flex-direction:column; gap:.8rem` (היה `.8rem 1.5rem 1rem` ללא flex) |
| `.pc` | **v6.3:** `display:inline-flex; padding:.72rem 1.5rem; gap:.55rem; font:1.08rem/600; color rgba(245,236,215,.8); border-radius:100px` (היה `.3rem .85rem, .78rem`) |
| `.pc:hover` | `background:rgba(196,147,10,.18); color:var(--c-gold-l)` |
| `.pc.active` | `background:rgba(196,147,10,.25); border-color:rgba(196,147,10,.6)` |
| `.pc-cnt` | **v6.3:** `font-size:.92rem; opacity:.75; font-weight:600` (היה `.66rem/500/.5`) |
| `.acc-hdr` | **v6.3:** `padding:.8rem 1.7rem; gap:.6rem; font:1.18rem/700; color:var(--c-gold-l); border:1px solid rgba(196,147,10,.35)` — **בולטות ביותר** (היה `.78rem/normal`) |
| `.acc-body` | **v6.3:** `display:none → flex when .open; flex-wrap; gap:.7rem; padding:1rem 1.3rem; border-radius:var(--r-md); margin-top:.55rem` |
| `.acc-sep` | `width:100%; height:1px; background rgba gold .12` |

### 3.3 Grid & Card

| class | תכונות |
|---|---|
| `.grid` | `display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:1rem` |
| `.card` | `background:#fff; border-radius:var(--r-md); shadow xs; hover: translateY(-2px)` |
| `.c-img` | `height:148px; overflow:hidden; object-fit:cover` |
| `.c-img.no-img` | `linear-gradient background + dashed circle indicator` |
| `.c-media-bar` | `position:absolute; bottom:0; opacity:0; transition: opacity; gradient overlay` |
| `.card:hover .c-media-bar` | `opacity:1` |
| `.c-upload-btn` | `background:transparent; border:1.5px dashed gold .5; radius sm; padding .2rem .5rem` |
| `.c-info` | `direction:rtl; text-align:right; padding:.65rem .7rem` |
| `.c-badge` | `direction:rtl; background:var(--c-spice); color:#fff; radius:100px` |
| `.c-title` | `direction:rtl; line-clamp:2; font-weight:700` |
| `.c-desc` | `direction:rtl; line-clamp:2; color:var(--c-ink-m)` |
| `.c-meta` | `display:flex; gap:.4rem; flex-wrap:wrap` |
| `.c-tag` | `background:var(--c-bg2); border:1px solid var(--c-bdr2); radius:100px` |
| `.c-diff-קל` | `background:#e8f5e9; color:#2e7d32` |
| `.c-diff-בינוני` | `background:#fff3e0; color:#e65100` |
| `.c-diff-מתקדם` | `background:#fce4ec; color:#c62828` |
| `.c-fav` | `position:absolute; top:.4rem; right:.4rem; font-size:1.1rem` |

### 3.4 Modal (Recipe)

| class | תכונות |
|---|---|
| `#ovl` | `position:fixed; inset:0; z-index:800; backdrop-filter:blur(4px); background:rgba(1,5,15,.72)` |
| `#mbox` | `direction:rtl; max-width:680px; max-height:90vh; overflow-y:auto` |
| `#m-progress` | `position:absolute; top:0; height:3px; gradient gold→spice; scaleX transform` |
| `.m-hero` | `height:240px; background:linear-gradient(135deg, dark, mid); overflow:hidden` |
| `.m-hero-nav` | `position:absolute top:50%; bg rgba(0,0,0,.45); width:32px; radius:50%` |
| `.m-hero-dots` | `position:absolute bottom:.5rem; left:50% translateX(-50%)` |
| `.m-hero-dot` | `width:8px; background rgba(255,255,255,.5); dot.active = #fff` |
| `.m-hero-media` | `position:absolute top:.5rem; display:flex; gap:.35rem` |
| `.m-hero-change` / `.m-hero-del` | `bg rgba(0,0,0,.5); border gold .3; radius:100px` |
| `.m-nav` | `display:flex; justify-content:space-between; position:absolute; top:.5rem; right:.5rem` |
| `.m-close` / `.m-prev` / `.m-next` | `bg rgba(0,0,0,.5); width:32px; height:32px; radius:100px; color:#fff` |
| `.m-body` | `direction:rtl; padding:1.2rem 1.4rem 1.4rem` |
| `.m-badge` | `direction:rtl; background:var(--c-spice); color:#fff; radius:100px; margin-bottom:.4rem` |
| `.m-title` | `color:var(--c-ink); font-size:1.35rem; font-weight:900` |
| `.m-subdesc` | `color:var(--c-ink-m); font-size:.84rem; margin-top:.25rem` |
| `.m-meta` | `display:flex; flex-wrap:wrap; gap:.45rem` |
| `.m-chip` | `font-size:.72rem; bg var(--c-bg2); border var(--c-bdr)` |
| `.m-mem` | `direction:rtl; border-right:3px solid gold; bg gold .1` |
| `.m-ingr-item` | `display:grid; grid-template-columns:auto 1fr; gap:.5rem` |
| `.m-step` | `padding-right:1.5rem; position:relative; border-right:2px solid gold` |
| `.m-tip-wrap` | `background gold .08; border gold; radius:r-md; padding:1rem` |
| `.m-src-box` | `margin-top:1rem; padding:.5rem 1rem; bg var(--c-bg2)` |
| `.m-vid-wrap` | `margin-top:1rem; display:flex; flex-direction:column; gap:.5rem` |
| `.m-vid-add` | `background gold .1; border dashed gold .4; radius:r-md; padding:.42rem 1.1rem` |
| `.m-actions` | `direction:rtl; display:flex; flex-wrap:wrap; gap:.4rem; padding-top:.6rem; border-top:1px solid bg3` |
| `.m-act-media` | `display:flex; align-items:center; gap:.35rem; bg gold .12; border gold .3; radius:100px` |
| `.m-act-media.del` | `border-color:rgba(220,50,50,.35); color:#f99` |

### 3.5 Feedback System (v6.0 — חדש)

| class | תכונות |
|---|---|
| `.fb-ovl` | `position:fixed; inset:0; z-index:950; background:rgba(1,5,15,.75); backdrop-filter:blur(4px)` |
| `.fb-ovl.open` | `display:flex; align-items:center; justify-content:center` |
| `.fb-box` | `direction:rtl; background:var(--c-bg); border-radius:var(--r-xl); max-width:520px; max-height:92vh; overflow-y:auto; box-shadow:var(--sh-xl); animation:fb-enter .28s cubic-bezier(.22,.61,.36,1)` |
| `@keyframes fb-enter` | `from {opacity:0; transform:translateY(12px) scale(.98)} to {opacity:1; transform:translateY(0) scale(1)}` |
| `.fb-head` | `display:flex; justify-content:space-between; padding:1rem 1.4rem; background:linear-gradient(135deg, dark, mid); color:gold-l; position:sticky; top:0; z-index:2` |
| `.fb-title` | `font-family:'Frank Ruhl Libre'; font-size:1.15rem; font-weight:700; color:gold-l` |
| `.fb-close` | `background:rgba(0,0,0,.4); border:1px solid rgba(255,255,255,.2); border-radius:100px; width:32px; height:32px; color:#fff` |
| `.fb-body` | `direction:rtl; text-align:right; padding:1.2rem 1.4rem 1.4rem` |
| `.fb-context` | `background:rgba(196,147,10,.1); border-right:3px solid var(--c-gold); border-radius:var(--r-sm); padding:.6rem .9rem` |
| `.fb-context strong` | `color:var(--c-spice); font-weight:700` |
| `.fb-form` | `direction:rtl` |
| `.fb-field` | `display:block; direction:rtl; margin-bottom:1rem` |
| `.fb-label` | `direction:rtl; display:block; font-size:.84rem; font-weight:600; color:var(--c-ink-m); margin-bottom:.35rem` |
| `.fb-req` | `color:var(--c-spice); font-weight:700` |
| `.fb-form input, textarea` | `width:100%; background:var(--c-bg2); border:1.5px solid var(--c-bdr); border-radius:var(--r-md); padding:.6rem .85rem; font-family:'Heebo'; font-size:.92rem; transition:all var(--t-fast)` |
| `.fb-form :focus` | `outline:none; border-color:var(--c-gold); box-shadow:0 0 0 3px rgba(196,147,10,.15)` |
| `.fb-hint` | `display:block; text-align:left; font-size:.72rem; color:var(--c-ink-l); margin-top:.3rem` |
| `.fb-status` | `direction:rtl; display:none; font-size:.88rem; font-weight:600; padding:0 .9rem; border-radius:var(--r-sm)` |
| `.fb-status.show` | `display:flex; padding:.6rem .9rem; margin-bottom:.9rem; align-items:center; gap:.5rem` |
| `.fb-status.success` | `background:rgba(61,110,58,.12); color:var(--c-herb); border:1px solid rgba(61,110,58,.3)` |
| `.fb-status.error` | `background:rgba(184,66,35,.12); color:var(--c-spice-d); border:1px solid rgba(184,66,35,.3)` |
| `.fb-status.loading` | `background:rgba(196,147,10,.12); color:var(--c-gold-d); border:1px solid rgba(196,147,10,.3)` |
| `.fb-status a` | `color:inherit; text-decoration:underline; font-weight:700` |
| `.fb-actions` | `display:flex; gap:.6rem; justify-content:flex-start; margin-top:1rem; padding-top:1rem; border-top:1px solid var(--c-bg3)` |
| `.fb-btn` | `font-family:'Heebo'; font-size:.9rem; font-weight:700; padding:.58rem 1.5rem; border-radius:100px; cursor:pointer; border:1.5px solid transparent; transition:all var(--t-med)` |
| `.fb-btn:disabled` | `opacity:.6; cursor:wait` |
| `.fb-btn-1` | `background:var(--c-spice); color:#fff` |
| `.fb-btn-1:hover:not(:disabled)` | `background:var(--c-spice-d); transform:translateY(-1px); box-shadow:var(--sh-sm)` |
| `.fb-btn-2` | `background:transparent; color:var(--c-ink-m); border-color:var(--c-bdr)` |
| `.fb-btn-2:hover` | `background:var(--c-bg2)` |
| `.fb-fab` | `position:fixed; z-index:450; bottom:1.5rem; left:1.5rem; display:flex; align-items:center; gap:.55rem; padding:.72rem 1.1rem; background:var(--c-spice); color:#fff; border:2px solid var(--c-gold); border-radius:100px; font-family:'Heebo'; font-size:.88rem; font-weight:700; box-shadow:var(--sh-md); transition:all var(--t-med) cubic-bezier(.4,0,.2,1)` |
| `.fb-fab:hover` | `background:var(--c-spice-d); transform:translateY(-2px); box-shadow:var(--sh-lg)` |
| `.fb-fab svg` | `width:18px; height:18px; flex-shrink:0` |
| `.fb-fab-lbl` | `display:inline-block` |
| `.m-act-media.fb-recipe-btn` | `background:rgba(184,66,35,.12); border-color:rgba(184,66,35,.35); color:var(--c-spice-d)` |
| `.m-act-media.fb-recipe-btn:hover` | `background:rgba(184,66,35,.25); color:var(--c-spice)` |
| `@media (max-width:480px) .fb-box` | `max-height:95vh; border-radius:var(--r-lg) var(--r-lg) 0 0; align-items:flex-end` |
| `@media (max-width:480px) .fb-fab-lbl` | `display:none` |
| `@media (max-width:480px) .fb-fab` | `padding:.85rem` |
| `@media (prefers-reduced-motion:reduce) .fb-box` | `animation:none` |
| `@media print .fb-ovl, .fb-fab, .fb-recipe-btn` | `display:none !important` |

### 3.6 Utility & Feedback (existing)

| class | תכונות |
|---|---|
| `.ing-search` | `padding:.5rem 1.5rem; border-bottom:1px solid gold .1; display:flex; flex-wrap:wrap` |
| `.ing-tag` | `background gold .15; border gold .35; radius:100px; padding:.2rem .6rem` |
| `.timer-box` | `position:fixed; bottom:5rem; right:1.5rem; z-index:700; background:var(--c-dark); padding:.8rem 1.2rem` |
| `#toast` | `position:fixed; bottom:5rem; left:50%; transform:translateX(-50%); z-index:900` |
| `#back-top` | `position:fixed; bottom:1.5rem; left:1.5rem; width:42px; height:42px; background:var(--c-gold)` |

---

## 4. מבנה DOM — כל ה-IDs

### 4.1 IDs עיקריים

| ID | Element | תיאור |
|---|---|---|
| `srch` | `<input>` | חיפוש — `type=search`, `autocomplete=off` |
| `srch-clr` | `<button>` | ניקוי חיפוש — `hidden` default |
| `theme-toggle` | `<button>` | `☀`/`🌙` — dark/light theme |
| `lang-toggle` | `<button>` | `EN` — toggle language |
| `cat-inner` | `<div>` | container לכפתורי `.nb` — innerHTML ע"י `buildNav()` |
| `nav-panel` | `<div>` | panel dropdown — `position:absolute` |
| `nav-panel-inner` | `<div>` | scroll container של panel |
| `pill-cnt` | `<span>` | מונה מתכונים — מעודכן ע"י `renderGrid()` |
| `about-toggle` | `<button>` | expand/collapse אודות |
| `about` | `<section>` | סקציית אודות — `aria-hidden` |
| `book-content` | `<div>` | placeholder שמוחלף ע"י `BOOK_HTML` |
| `grid` | `<div>` | recipe grid — `aria-busy` toggle |
| `sec-title` | `<h2>` | כותרת סקציה נוכחית |
| `sec-cnt` | `<span>` | `N מתכונים` |
| `back-top` | `<button>` | scroll to top |
| `toast` | `<div>` | זעיר — הודעות toast |
| `time-filter` | `<select>` | סינון לפי זמן |

### 4.2 Recipe Modal IDs

| ID | Element | תיאור |
|---|---|---|
| `ovl` | `<div>` | modal overlay — `aria-hidden` |
| `mbox` | `<div>` | modal box |
| `m-progress` | `<div>` | progress bar — `scaleX` |
| `m-hero` | `<div>` | hero image area |
| `m-hero-change` | `<button>` | החלפת תמונה |
| `m-hero-del` | `<button>` | מחיקת תמונה |
| `m-close` | `<button>` | סגירת מודאל |
| `m-prev` / `m-next` | `<button>` | ניווט מתכונים |
| `m-badge` | `<span>` | badge |
| `m-title` | `<h2>` | שם מתכון |
| `m-subdesc` | `<p>` | תיאור קצר |
| `m-mem` / `m-mem-txt` | `<div>` | זיכרון מהבית |
| `m-meta` | `<div>` | chips: זמן, מנות, קושי |
| `m-ingr` | `<div>` | רשימת מרכיבים |
| `m-steps` | `<ol>` | שלבי הכנה |
| `m-tip-wrap` / `m-tip-txt` | `<div>` | טיפ |
| `m-src-box` / `m-src-link` | `<div>` | קישור למקור |
| `m-vid-wrap` / `m-vid-list` / `m-vid-add` | `<div>`/`<button>` | סקציית וידאו |
| `m-print` | `<button>` | הדפסה |
| `m-pdf` | `<button>` | ייצוא PDF |
| `m-share` | `<button>` | שיתוף |
| `m-upload-act` | `<button>` | העלאת תמונה |
| `m-img-del-act` | `<button>` | מחיקת תמונה |
| **`m-feedback-act`** | **`<button>`** | **חדש v6.0 — פידבק על מתכון (class `fb-recipe-btn`)** |

### 4.3 Feedback System IDs (v6.0 — חדש)

| ID | Element | תיאור |
|---|---|---|
| `fb-ovl` | `<div>` | מודל פידבק overlay — `role="dialog" aria-modal="true"` |
| `fb-box` | `<div>` | מודל פידבק container — `role="document"` |
| `fb-title` | `<h2>` | כותרת דינמית: "הערה / תיקון על מתכון" או "הצעה לשיפור או דיווח על תקלה" |
| `fb-close` | `<button>` | סגירה — `aria-label="סגור"` |
| `fb-context` | `<p>` | הקשר דינמי — מוסתר כשזה פידבק אתר, מציג "לגבי המתכון: <strong>X</strong>" |
| `fb-form` | `<form>` | הטופס — `novalidate` (ולידציה ב-JS) |
| `fb-name` | `<input type="text">` | שם (אופציונלי) — `maxlength="80"`, `autocomplete="name"` |
| `fb-email` | `<input type="email">` | אימייל (אופציונלי) — `maxlength="100"`, `autocomplete="email"` |
| `fb-message` | `<textarea>` | הודעה (חובה) — `maxlength="2000"`, `rows="5"`, `required` |
| `fb-count` | `<span>` | מונה תווים חי — `0 / 2000` |
| `fb-status` | `<div>` | הודעת סטטוס — `role="status" aria-live="polite"` |
| `fb-cancel` | `<button>` | ביטול — `fb-btn fb-btn-2` |
| `fb-submit` | `<button type="submit">` | שליחה — `fb-btn fb-btn-1` |
| `fb-fab` | `<button>` | Floating Action Button — `aria-label="הצעות לשיפור או דיווח תקלה"` |
| `fb-mailto-fallback` | `<a>` | קישור dynamic שנוצר בזמן שגיאה — פותח mailto |

### 4.4 Hidden Form + Iframe (v6.4 — מבנה חדש)

**הסיבה:** ב-v6.3 ניסינו לשלוח `fetch()` עם JSON ל-FormSubmit AJAX, אבל הוא נחסם ב-CORS preflight (`No 'Access-Control-Allow-Origin' header is present`). ב-v6.4 חזרנו ל-form classic — לא כפוף ל-CORS — עם iframe כיעד.

**HTML שנוסף לפני `</body>`:**

| ID | Element | תיאור |
|---|---|---|
| `fb-iframe-target` | `<iframe>` | יעד מוסתר ל-form. `name="fb-iframe-target"` (חובה ל-target). `position:absolute;width:0;height:0;border:0;visibility:hidden`. `aria-hidden="true"`, `tabindex="-1"`. |
| `fb-hidden-form` | `<form>` | hidden form. `method="POST"`, `target="fb-iframe-target"`, `enctype="application/x-www-form-urlencoded"`, `accept-charset="UTF-8"`. `action` מוגדר דינמית ב-JS (כדי לשמור email מוסתר ב-base64). |
| `fb-hf-subject` | `<input type="hidden" name="_subject">` | נושא המייל — מוגדר דינמית |
| (קבוע) | `<input type="hidden" name="_template" value="table">` | פורמט מייל בטבלה |
| (קבוע) | `<input type="hidden" name="_captcha" value="false">` | captcha כבוי |
| (קבוע) | `<input type="hidden" name="_honey" value="">` | honeypot |
| `fb-hf-name` | `<input name="name">` | שם השולח |
| `fb-hf-email` | `<input name="email">` | אימייל השולח |
| `fb-hf-message` | `<input name="message">` | תוכן ההודעה |
| `fb-hf-type` | `<input name="type">` | "recipe" / "site" |
| `fb-hf-recipe-id` | `<input name="recipe_id">` | (אם recipe) |
| `fb-hf-recipe-title` | `<input name="recipe_title">` | (אם recipe) |
| `fb-hf-page-url` | `<input name="page_url">` | location.href |
| `fb-hf-user-agent` | `<input name="user_agent">` | navigator.userAgent slice 200 |

### 4.5 PWA Install Button IDs (v6.3 — שוחזר)

| ID | Element | תיאור |
|---|---|---|
| `pwa-install-btn` | `<button>` | כפתור ההתקנה ב-`.hdr-tools`, hidden by default; מוצג דרך JS כשהדפדפן תומך או ב-iOS |

---

## 5. פונקציות JavaScript — מפרט מלא

### 5.1 פונקציות עזר (Helpers)

| פונקציה | חתימה | תיאור |
|---|---|---|
| `_hn` | `(s:string):string` | HTML entity normalization — ניקוד → צורה בסיסית |
| `_initHsfx` | `():void` | אתחול suffixes לחיפוש מורפולוגי עברי |
| `hebrewMorphSearch` | `(text, term):boolean` | חיפוש עם קידומות `ב/ו/ל/מ`, סיומות `ים/ות/ה`, שורשים |
| `esc` | `(str):string` | HTML escape — `&<>"'` → entities (XSS prevention) |
| `setText` | `(id, val):void` | `getElementById(id).textContent = val` — null safe |
| `setHTML` | `(id, html):void` | `innerHTML = html` — trusted HTML only |
| `show` / `hide` | `(id):void` | `element.hidden = false/true` |
| `showToast` | `(msg, dur?):void` | הודעת toast זמנית — fade-in→stay→fade-out |
| `translateHe` | `(text):string` | תרגום runtime: `_PRE_EN` → `_FOOD_DICT` → morphological |
| `applyLang` | `(lang):void` | החלפת שפה `he`/`en` — מעדכן כל UI + מתכונים |

### 5.2 `filtered()` — מנוע הסינון

`filtered()` מחזיר `R.filter()` לפי 8 ממדים בסדר עדיפות:

| Priority | תנאי | פעולה |
|---|---|---|
| 1 | `ACT_IDS` קיים (Set) | `ACT_IDS.has(r.id)` — תת-קטגוריות span/isr/nonkosher |
| 2 | `ACT_CATS.length > 0` | `ACT_CATS.indexOf(r.cat) >= 0` — multi-select |
| 3 | `ACT_CAT === "all"` | `true` |
| 4 | `ACT_CAT === "hol" && ACT_HOLIDAY` | `HOLIDAY_TAGS[h].indexOf(r.id) >= 0` |
| 5 | default | `r.cat === ACT_CAT` |
| — | `ACT_DIFF !== "all" && r.diff !== ACT_DIFF` | reject |
| — | `ACT_TIME !== "all"` | parse מ-`r.time`, compare to limit |
| — | `SHOW_FAVS && !FAV.has(r.id)` | reject |
| — | `ING_TAGS.size` | כל tag חייב להיות ב-ingr text |
| — | `SEARCH` | `hebrewMorphSearch(allFields, SEARCH)` — multi-word AND |

### 5.3 `renderGrid()`

מרנדר כרטיסי מתכון ל-grid:

1. `list = filtered()` → count to `#sec-cnt`.
2. `grid.innerHTML = ""` → `DocumentFragment` for performance.
3. For each recipe: `createElement .card` with `role=button`, `tabindex=0`, `data-rid`.
4. `.c-img` with `loading=lazy`, `decoding=async`, `fetchPriority=low`.
5. `.c-info`: badge, title, desc, meta (time/diff/fav).
6. Click/Enter/Space → `openM(r.id)`.
7. `grid.appendChild(fragment)`.

### 5.4 `buildNav()`

בונה את תפריט הניווט מ-`MENU_STRUCTURE`. פונקציות nested:

| פונקציה | תיאור |
|---|---|
| `catCnt(id)` | ספירת מתכונים — `null`/`string`/`array` safe |
| `isActiveLeaf(catId, hol, ids)` | בודק אם פריט פעיל |
| `makeChip(lbl, c, onClick, active)` | יוצר כפתור `.pc` עם count |
| `selectCat(catId, hol, key)` | `ACT_CAT`, reset `ACT_IDS`/`ACT_CATS`/`SEARCH` |
| `selectMulti(ids, lbl, key)` | `ACT_CATS`, reset `ACT_IDS` |
| `selectByIds(rids, lbl, key)` | `ACT_IDS = new Set(rids)` |
| `buildPanel(node, pi)` | בונה panel: 4 branches (accordion, multi-cat, recipe-IDs, simple) |

### 5.5 `buildPanel(node, pi)` — 4 branches

| Branch | תנאי | פעולה |
|---|---|---|
| 1 | `item.items || item.sub` | Accordion group: `hdr + body`, expand/collapse |
| 2 | `item.ids && !item.items` | Multi-cat leaf: `isRecipeIds ? selectByIds : selectMulti` |
| 3 | `item.sep` | separator div |
| 4 | default (simple chip) | `selectCat(item.id)` |

### 5.6 `openM(id)`

1. `R.find(x => x.id === id)` → `CUR_REC`.
2. `filtered().findIndex` → `CUR_IDX`.
3. `refreshModalMedia(r)` → hero + gallery + video.
4. Badge, title, subdesc, memory, meta chips.
5. Ingredients: `forEach` → `.m-ingr-item` with `q`+`i` (+ `_PRE_EN` for English).
6. Steps: `forEach` → `<li>.m-step` with timing.
7. Tip, source box, nav buttons prev/next.
8. `ovl.classList.add("open")`, `body overflow:hidden`.
9. `_heroGalleryInit(r)` → async image validation + swipe.

### 5.7 פונקציות נוספות

| פונקציה | תיאור |
|---|---|
| `closeM()` | `ovl.remove("open")`; body `overflow:normal`; `CUR_REC=null` |
| `ovlClose(e)` | סגירה בלחיצה מחוץ ל-`.mbox` |
| `navRecipe(dir)` | `CUR_IDX += dir`; `openM(filtered()[newIdx].id)` |
| `doSearch(val)` | `SEARCH = val`; `updateTitle()`; `renderGrid()` |
| `clearSearch()` | `SEARCH=""`; `renderGrid()` |
| `catLbl(id)` | `CATS.find(c=>c.id===id)?.lbl` |
| `holName(h)` | `HOL_NAMES` map → Hebrew name |
| `updateTitle()` | `document.title = category/search label` |
| `printRecipe()` | `window.print()` — `@media print` CSS |
| `exportPDF()` | same as printRecipe + toast hint |
| `exportFullCookbook()` | פותח חלון חדש עם כל המתכונים ב-HTML מותאם PDF |
| `shareRecipe()` | `navigator.share({title, text, url})` |
| `observeLazy()` | `IntersectionObserver` → `img.src = dataset.src` |
| `getRecipeImg(r)` | `media.imgs[0]` \|\| `"images/recipes_images/r-"+r.id+".jpg"` |
| `getMedia(id)` | `localStorage perla_media_{id}` → `{imgs, vids}` |
| `saveMedia(id, data)` | `localStorage.setItem('perla_media_'+id, JSON.stringify(data))` |
| `addImg(id)` | `file input` → `base64` → `localStorage` |
| `deleteImg(id, idx)` | remove from `localStorage` array |
| `addVideo(id)` | `prompt URL` → `localStorage`, max 5 |
| `deleteVideo(id, idx)` | remove from `vids[]` |
| `refreshModalMedia(r)` | updates hero image, gallery, video list |
| `refreshCardImg(recipeId)` | מחדש תמונה בכרטיס |
| `_getImgFallbacks(r)` | fallback chain: custom media → `r-{id}.jpg` → category image |
| `_heroGalleryInit(r)` | async validate images → gallery with ‹/› nav + dots + swipe |
| `_heroGalleryGo(idx)` | עובר לתמונה `idx` בגלריה |
| `_heroGalleryUpdateNav()` | מעדכן כפתורי prev/next + dots |
| `toggleAbout()` | `about aria-hidden` toggle + arrow rotate |
| `toggleTheme()` | מחליף light/dark + localStorage |
| `toggleLang()` | מחליף he/en + `location.reload()` |
| `_resolveImg(name)` | `_IMG_ALIAS` fallback → `images/{name}.jpg` |
| `parseMinutes(timeStr)` | `"30 דקות"` → `30` |
| `startTimer(mins, label)` | timer countdown + audio on complete |
| `stopTimer()` | clear interval + hide box |
| `openPanel(key, btn, builder)` | פתיחת dropdown panel עם callback builder |
| `closePanel()` | סגירת dropdown |

### 5.8 Feedback System Functions (v6.3 — מעודכן ל-FormSubmit.co)

כל הפונקציות נמצאות ב-**IIFE** (Immediately Invoked Function Expression) בסוף ה-`<script>`:

```javascript
(function() {
  'use strict';
  // ... feedback system code ...
})();
```

| פונקציה | חתימה | תיאור |
|---|---|---|
| `$(id)` | `(id:string):Element\|null` | wrapper ל-`document.getElementById` |
| `escapeHtml(s)` | `(s:string):string` | מחליף `<>&"'` ב-entities |
| `encodeFormData(data)` | `(data:object):string` | *לא בשימוש ב-v6.3* — נשאר לצורך תאימות |
| `setStatus(msg, kind)` | `(msg:string\|null, kind?:'success'\|'error'\|'loading'):void` | מעדכן `#fb-status` |
| `updateCharCount()` | `():void` | `$('fb-count').textContent = $('fb-message').value.length` |
| `openFeedbackModal(type, recipe)` | `(type:'recipe'\|'site', recipe?:{id,title}):void` | פותח modal, מגדיר כותרת והקשר |
| `closeFeedbackModal()` | `():void` | סוגר modal, מאפס state |
| `submitFeedback(e)` | `(e:Event):Promise<void>` | **v6.3: POST JSON ל-FormSubmit.co AJAX** — ראו 5.9 |
| `openMailtoFallback(data)` | `(data:object):void` | `window.location = mailto:...` עם נתוני הטופס |
| `initFeedback()` | `():void` | רושם event listeners |

**Constants (v6.3):**

```javascript
// Base64-obfuscated email — prevents simple scrapers
var FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ==';  // = asafben33@gmail.com
var FORM_NAME = 'perla-feedback';  // kept for backward compat
var MAX_MSG   = 2000;              // Max message length
```

**State variables (במסגרת IIFE):**

```javascript
var _type = null;            // 'recipe' | 'site' | null
var _recipe = null;          // { id, title } | null
var _isSubmitting = false;   // prevents double-submit
```

**Global exposure:**

```javascript
window.openFeedbackModal  = openFeedbackModal;
window.closeFeedbackModal = closeFeedbackModal;
```

### 5.9 `submitFeedback(e)` — זרימה מפורטת (v6.4 — Hidden iframe)

```
1. e.preventDefault()  →  אם כבר submitting → return
2. איסוף 3 שדות: message, name, email
3. ולידציה:
   - message ריק → setStatus('נא לכתוב הודעה...', 'error')
   - message > 2000 → setStatus('ההודעה ארוכה מדי...', 'error')
   - email != '' && !regex.test(email) → setStatus('כתובת אימייל לא תקינה', 'error')
4. _isSubmitting = true; submitBtn.disabled = true; setStatus('שולח...', 'loading')
5. בניית subject string (Hebrew gershayim) — תלוי type
6. בניית mailtoData עם מפתחות ישנים (feedback-type, sender-name וכו') לתאימות עם openMailtoFallback()
7. בדיקה ש-#fb-hidden-form ו-#fb-iframe-target קיימים. אם לא → fallback ל-mailto מיד.
8. הגדרת action דינמית: hf.action = 'https://formsubmit.co/' + atob(FORMSUBMIT_EMAIL_B64)
   (שומר email מוסתר ב-base64 בקוד מקור — לא מופיע ב-HTML)
9. אכלוס שדות hidden form דרך setF(id, value):
   - fb-hf-subject, fb-hf-name, fb-hf-email, fb-hf-message
   - fb-hf-type, fb-hf-recipe-id, fb-hf-recipe-title
   - fb-hf-page-url, fb-hf-user-agent
10. רישום iframe.addEventListener('load', onSuccess) — מאזין לטעינת ה-iframe
11. setTimeout(onTimeout, 15000) — fallback אם ה-iframe לא נטען תוך 15 שניות
12. hf.submit() — שליחת form classic (NOT fetch — bypasses CORS)
12a. iframe.onload נורה → onSuccess():
     - clearTimeout(timeoutId), iframe.removeEventListener
     - setStatus('תודה! ההודעה נשלחה בהצלחה.', 'success')
     - setTimeout(closeFeedbackModal, 2500)
     - _isSubmitting = false, submitBtn.disabled = false
12b. timeout 15s פוקע → onTimeout():
     - iframe.removeEventListener
     - setStatus('שליחה אורכת זמן רב מהצפוי. <a>פתח באימייל במקום</a>', 'error')
     - רישום click handler ב-#fb-mailto-fallback → openMailtoFallback(mailtoData)
12c. hf.submit() throws (rare) → catch:
     - clearTimeout, removeEventListener
     - setStatus('שליחה ישירה נכשלה. <a>פתח באימייל במקום</a>', 'error')
```

#### למה לא fetch + JSON (לקח v6.3 → v6.4)

ב-v6.3 ניסינו `fetch(endpoint, { method:'POST', headers:{'Content-Type':'application/json',...}, body: JSON.stringify(payload) })`. שגיאה:

```
Access to fetch at 'https://formsubmit.co/ajax/asafben33@gmail.com'
from origin 'https://asafben33.github.io' has been blocked by CORS policy:
Response to preflight request doesn't pass access control check:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**ניתוח:** Content-Type: application/json הופך את הבקשה ל-"non-simple", הדפדפן שולח OPTIONS preflight. FormSubmit אינו עונה עם Access-Control-Allow-Origin ב-OPTIONS → דפדפן חוסם את ה-POST.

**פתרון:** Form submissions עם `target="iframe"` הם **legacy HTML behavior** שאינו כפוף ל-CORS preflight. הדפדפן שולח POST ישירות, התגובה מטוענת ב-iframe (לא נקראת על ידי JS), אין צורך ב-Access-Control-Allow-Origin.

### 5.10 `openMailtoFallback(data)` — Base64 obfuscation (לא השתנה)

```javascript
// Base64 of 'asafben33@gmail.com'
var to = atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==');

var subject = data['feedback-type'] === 'recipe'
  ? 'תיקון למתכון: ' + data['recipe-title']
  : 'הצעה / דיווח — אתר ספר הבישול של פרלה ז"ל';

var body = [
  'סוג: ' + (data['feedback-type'] === 'recipe' ? 'תיקון מתכון' : 'הצעה / תקלה'),
  data['recipe-title'] ? 'מתכון: ' + data['recipe-title'] : '',
  data['recipe-id']    ? 'מזהה: '  + data['recipe-id']    : '',
  'שם: ' + (data['sender-name'] || '(לא צוין)'),
  '',
  'תוכן ההודעה:',
  data['message'] || '',
  '',
  '---',
  'דף: ' + data['page-url']
].filter(Boolean).join('\n');

window.location.href = 'mailto:' + to +
  '?subject=' + encodeURIComponent(subject) +
  '&body='    + encodeURIComponent(body);
```

**הערה:** `mailtoData` במ-`submitFeedback` משתמש במפתחות הישנים (`feedback-type`, `recipe-title`, `sender-name` וכו') כדי לשמור על תאימות עם הפונקציה הזו.

### 5.11 Event Listeners

| Element | Event | Handler |
|---|---|---|
| `#fb-fab` | `click` | `openFeedbackModal('site', null)` |
| `#fb-close` | `click` | `closeFeedbackModal` |
| `#fb-cancel` | `click` | `closeFeedbackModal` |
| `#fb-ovl` | `click` | if `e.target === ovl` → `closeFeedbackModal` (click outside) |
| `#fb-form` | `submit` | `submitFeedback` |
| `#fb-message` | `input` | `updateCharCount` |
| `document` | `keydown` (Escape) | if `#fb-ovl.open` → `closeFeedbackModal` |
| `#m-feedback-act` | `click` | if `CUR_REC` → `openFeedbackModal('recipe', {id, title})` |

### 5.12 PWA Install Button JS (v6.3 — שוחזר)

IIFE נפרד שמנהל את כפתור ההתקנה. נמצא לפני `</body>`.

```javascript
(function(){
  'use strict';
  var _prompt = null;
  var SEEN_KEY = 'perla_pwa_dismissed';  // localStorage flag

  function _btn(){ return document.getElementById('pwa-install-btn'); }
  function _show(){ var b = _btn(); if (b) b.style.display = 'flex'; }
  function _hide(){ var b = _btn(); if (b) b.style.display = 'none'; }

  /* Hide if already installed (standalone mode) */
  if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) return;
  if (window.navigator.standalone === true) return;  // iOS Safari

  /* Chrome/Edge/Firefox/Samsung: standard install flow */
  window.addEventListener('beforeinstallprompt', function(e){
    e.preventDefault();
    _prompt = e;
    if (localStorage.getItem(SEEN_KEY) !== 'yes') _show();
  });

  window.addEventListener('appinstalled', function(){
    _hide();
    _prompt = null;
    try { localStorage.setItem(SEEN_KEY, 'yes'); } catch(e){}
  });

  /* Click handler — trigger native prompt or iOS instructions */
  document.addEventListener('click', function(e){
    var b = e.target && e.target.closest && e.target.closest('#pwa-install-btn');
    if (!b) return;
    e.preventDefault();

    if (_prompt) {
      _prompt.prompt();
      _prompt.userChoice.then(function(r){
        if (r.outcome === 'accepted') {
          _hide();
          try { localStorage.setItem(SEEN_KEY, 'yes'); } catch(e){}
        }
        _prompt = null;
      });
    } else {
      /* iOS / unsupported — show manual instructions */
      var isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
      var lang = (document.documentElement.lang || navigator.language || 'he').slice(0,2);
      var isHe = lang === 'he';
      var msg;
      if (isIOS) {
        msg = isHe
          ? 'להתקנה ב-iPhone/iPad:\n1. לחצו על כפתור "שיתוף"\n2. בחרו "הוסף למסך הבית"\n3. לחצו "הוסף"'
          : 'To install: Tap Share → "Add to Home Screen" → "Add"';
      } else {
        msg = isHe
          ? 'להתקנה: פתחו את תפריט הדפדפן (שלוש נקודות) ובחרו "הוסף למסך הבית" או "התקן אפליקציה"'
          : 'To install: Browser menu (three dots) → "Install app" or "Add to Home Screen"';
      }
      alert(msg);
    }
  });

  /* iOS doesn't fire beforeinstallprompt — show button after load */
  if (/iphone|ipad|ipod/i.test(navigator.userAgent) && !window.navigator.standalone) {
    window.addEventListener('load', function(){
      if (localStorage.getItem(SEEN_KEY) === 'yes') return;
      setTimeout(_show, 1500);
    });
  }
})();
```

**Event Listeners ב-PWA IIFE:**

| Event | Source | Handler |
|---|---|---|
| `beforeinstallprompt` | `window` | שומר event ומציג כפתור |
| `appinstalled` | `window` | מסתיר כפתור, מעדכן localStorage |
| `click` | `document` (delegated) | קורא `_prompt.prompt()` או מציג `alert()` לפי OS |
| `load` | `window` (iOS only) | מציג כפתור אחרי 1.5s |

---

## 6. MENU_STRUCTURE — מפרט מלא

`key: all_master` — כפתור יחיד "כל המתכונים" עם כל הקטגוריות כ-items:

| item | סוג | action |
|---|---|---|
| `{id:"all", lbl:"הכל"}` | leaf | `selectCat("all")` |
| `{lbl:"מטעמים של אמא"}` | accordion + `ids[8 cats]` | expand → 7 items + ספרד + עדות + נ"כ |
| ├ `{id:"soups"}` | leaf | `selectCat("soups")` |
| ├ `{id:"salads"}` | leaf | `selectCat("salads")` |
| ├ `{lbl:"מנות עיקריות"}` | accordion + `ids[3]` | בשר, עוף, דגים |
| ├ `{id:"veg"}` | leaf | `selectCat("veg")` |
| ├ `{id:"hol", sub:[10]}` | leaf + `sub[]` | `selectCat("hol", h)` per holiday |
| ├ `{id:"des"}` | leaf | `selectCat("des")` |
| ├ `{lbl:"מורשת ספרד"}` | accordion + `ids[73]` | 8 sub-cats by recipe IDs |
| ├ `{sep:true}` | separator | ──────── |
| ├ `{lbl:"מתכונים מהעדות"}` | accordion + `ids[9 cats]` | 9 עדות + ישראלי (4 subs) |
| ├ `{sep:true}` | separator | ──────── |
| └ `{lbl:"לא כשרים"}` | accordion + `ids[40]` | פירות ים (14) + בשר+חלב (26) |

---

## 7. תתי-קטגוריות מורשת ספרד — recipe ID arrays

| תת-קטגוריה | מתכונים | IDs דוגמה |
|---|---|---|
| מרקים ומינסטרות | 3 | `sp3`, `spf2`, `spe3` |
| בשר וקציצות | 8 | `sp2`, `sp4`, `sp6`, `spne3`, `spf3`, `ex41`, `fin18`, `spx3` |
| דגים | 3 | `spn4`, `spv3`, `spx2` |
| ירקות ותוספות | 28 | `sp1`, `sp5`, `sp7`, `sp8`, `spne1`... |
| שבת וחגים | 4 | `spn1`, `spe1`, `spv1`, `spx1` |
| רטבים ותבלינים | 4 | `sau1`, `sau2`, `sau3`, `sau4` |
| לחמים ומאפים | 9 | `spn2`, `spf1`, `spf5`, `add29`... |
| קינוחים ומתוקים | 13 | `sp9`, `spn3`, `spn5`, `ex42`... |

---

## 8. תתי-קטגוריות מטבח ישראלי

| תת-קטגוריה | מתכונים | IDs |
|---|---|---|
| מאכלי רחוב | 10 | `is1`, `is2`, `is3`, `is5`, `is7`, `is8`, `is12`, `is13`, `is21`, `is23` |
| מנות עיקריות | 9 | `is4`, `is9`, `is10`, `is14`, `is15`, `is16`, `is18`, `is26`, `is28` |
| לחמים ומאפים | 4 | `is6`, `is19`, `is22`, `is24` |
| קינוחים ועוגות | 7 | `is11`, `is17`, `is20`, `is25`, `is27`, `is29`, `is30` |

---

## 9. מתכונים לא כשרים — 40 IDs

**פירות ים (14):**
`nk_fn3`, `nk_fn4`, `nk_fe3`, `nk_fe5`, `nk_add34`, `nk_ex19`, `nk_hv3`, `nk_spv2`, `nk_fe10`, `nk_ku25`, `nk_tr8`, `nk_bu2`, `nk_bu4`, `nk_spx3`

**בשר וחלב (26):**
`nk_c5`, `nk_h2`, `nk_sp2`, `nk_sp4`, `nk_hn15`, `nk_hn16`, `nk_rn7`, `nk_cne4`, `nk_se9`, `nk_chf3`, `nk_chf4`, `nk_add43`, `nk_add44`, `nk_ex26`, `nk_ex31`, `nk_fin13`, `nk_cw3`, `nk_chfx2`, `nk_holfx4`, `nk_me9`, `nk_hn18`, `nk_ku3`, `nk_ku30`, `nk_ye19`, `nk_tr26`, `nk_sn23`

---

## 10. State Variables Global

| משתנה | סוג | תיאור |
|---|---|---|
| `R` | `Array` | כל המתכונים — `[...recipes from data.js]` |
| `CUR_REC` | `object\|null` | המתכון הפתוח כעת ב-modal |
| `CUR_IDX` | `number` | אינדקס ב-`filtered()` של המתכון הפתוח |
| `ACT_CAT` | `string` | קטגוריה פעילה (`"all"` ברירת מחדל) |
| `ACT_CATS` | `Array<string>` | multi-category selection (`[]` ברירת מחדל) |
| `ACT_IDS` | `Set<string>\|null` | recipe IDs filter (עבור sub-category filters) |
| `ACT_HOLIDAY` | `string\|null` | `shabbat`, `pesach`... |
| `ACT_DIFF` | `string` | `"all"`, `"קל"`, `"בינוני"`, `"מתקדם"` |
| `ACT_TIME` | `string` | `"all"`, `"30"`, `"60"`, `"90"`, `"120"`, `"121"` (121+) |
| `ACT_NAV_KEY` | `string` | מפתח nav פעיל — להדגשה |
| `SHOW_FAVS` | `boolean` | הצג רק מועדפים |
| `ING_TAGS` | `Set<string>` | תגי מרכיבים מסוננים |
| `FAV` | `Set<string>` | מועדפים של משתמש (`localStorage perla_favs`) |
| `SEARCH` | `string` | מחרוזת חיפוש נוכחית |
| `_LANG` | `string` | `"he"` / `"en"` |
| `_srchTimer` | `number` | debounce timer for search |
| `_heroGallery` | `object` | `{imgs, validated, idx}` של modal gallery |
| `_timerInterval` | `number\|null` | interval של timer המרכזי |
| `_timerRemaining` | `number` | שניות שנותרו בטיימר |
| `_timerLabel` | `string` | תווית של הטיימר |

### 10.1 State Variables של מערכת הפידבק (IIFE-scoped)

| משתנה | סוג | תיאור |
|---|---|---|
| `_type` | `'recipe'\|'site'\|null` | סוג הפידבק הנוכחי |
| `_recipe` | `{id,title}\|null` | מתכון שפידבק התייחס אליו |
| `_isSubmitting` | `boolean` | true כל עוד fetch בתהליך — מונע double-submit |

---

## 11. LocalStorage Schema

| מפתח | סוג ערך | תיאור |
|---|---|---|
| `perla_lang` | `"he"\|"en"` | שפה שנשמרה |
| `perla_theme` | `"light"\|"dark"` | נושא |
| `perla_favs` | JSON array of strings | `["id1","id2",...]` recipe IDs |
| `perla_media_{id}` | JSON `{imgs,vids}` | מדיה מותאמת למתכון: `{imgs:[...base64], vids:[...urls]}` |
| `perla_vid_del_{id}` | `"1"\|null` | ביטול הצגת וידאו דיפולטי |

**מגבלות:**
- `imgs[]`: מקסימום 3 תמונות למתכון (base64)
- `vids[]`: מקסימום 5 URLs למתכון

---

## 12. מערכת תרגום — פרטי יישום

### 12.1 `_PRE_EN` Schema

```javascript
_PRE_EN = {
  "s1": {
    d:  "English description",       // desc
    m:  "English memory",            // mem
    t:  "English tip",               // tip
    st: [                            // steps
      { t: "Boil pasta", s: "..." },
      { t: "Make sauce", s: "..." }
    ],
    ig: [                            // ingredients
      { q: "500g", i: "pasta" },
      { q: "3 cloves", i: "garlic" }
    ]
  },
  // ... 1,054 entries
}
```

### 12.2 `_FOOD_DICT` — דוגמאות

```javascript
_FOOD_DICT = {
  "בצל":        "onion",
  "בצלים":      "onions",
  "שום":        "garlic",
  "פלפל אדום":  "red pepper",
  // ... 2,853 entries
}
```

### 12.3 `translateHe(text)` — סדר עדיפות

1. חיפוש ישיר ב-`_PRE_EN[currentRecipe.id].{field}` אם ב-context של מתכון.
2. חיפוש ב-`_FOOD_DICT` (exact match).
3. `hebrewMorphSearch` — קידומות ב/ו/ל/מ + סיומות ים/ות/ה → נסה לאתר שורש.
4. אם כל הנ"ל נכשל: החזר את המחרוזת המקורית (עברית).

---

## 13. מערכת פידבק — v6.0 (חדש)

### 13.1 Flow Diagram

```
┌──────────────────────────────────────────────────────┐
│  משתמש לוחץ FAB או כפתור "הערה / תיקון"            │
└────────────────────────┬─────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│  openFeedbackModal(type, recipe)                     │
│  - _type = type                                      │
│  - _recipe = recipe                                  │
│  - Reset form                                        │
│  - Set title + context                               │
│  - ovl.classList.add('open')                         │
│  - focus #fb-message                                 │
└────────────────────────┬─────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│  משתמש ממלא שם, email, הודעה → לוחץ "שליחה"         │
└────────────────────────┬─────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│  submitFeedback(e)                                   │
│  1. Validate message (required, <=2000)              │
│  2. Validate email regex (if provided)               │
│  3. _isSubmitting=true, disable button               │
│  4. Build payload (10 fields)                        │
│  5. fetch('/', POST, application/x-www-form-urlencoded)│
└────────────────────────┬─────────────────────────────┘
                  ┌──────┴─────┐
                  ↓            ↓
      ┌─────────────┐    ┌──────────────┐
      │ response.ok │    │    error     │
      └──────┬──────┘    └──────┬───────┘
             ↓                  ↓
    ┌─────────────────┐  ┌──────────────────┐
    │ setStatus('תודה',│  │ setStatus('שליחה │
    │  'success')     │  │  נכשלה', 'error')│
    │ setTimeout(close,│  │ + Show mailto    │
    │  2500)          │  │   fallback link  │
    └─────────────────┘  └──────────────────┘
```

### 13.2 `payload` — 10 שדות

```javascript
var payload = {
  'form-name':     'perla-feedback',
  'bot-field':     '',                     // honeypot - empty = human
  'feedback-type': _type || 'site',        // 'recipe' | 'site'
  'recipe-id':     _recipe ? String(_recipe.id) : '',
  'recipe-title':  _recipe ? String(_recipe.title) : '',
  'sender-name':   name.slice(0, 80),
  'sender-email':  email.slice(0, 100),
  'message':       message.slice(0, MAX_MSG),
  'page-url':      location.href,
  'user-agent':    (navigator.userAgent || '').slice(0, 200)
};
```

### 13.3 Validation Rules

| שדה | חוק | הודעת שגיאה |
|---|---|---|
| `message` | `trim().length > 0` | "נא לכתוב הודעה לפני השליחה." |
| `message` | `length <= 2000` | "ההודעה ארוכה מדי (מקסימום 2000 תווים)." |
| `email` | `== '' \|\| /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test()` | "כתובת אימייל לא תקינה." |
| `bot-field` | חייב להיות ריק (honeypot) | (Netlify דוחה אוטומטית) |

### 13.4 Netlify Dashboard Setup — חד-פעמי

1. Netlify → site → Forms.
2. Verify `perla-feedback` detected.
3. Settings & Usage → Form notifications → Add notification → Email → `asafben33@gmail.com`.
4. (optional) Enable Netlify reCAPTCHA if spam starts arriving.

### 13.5 Base64 Obfuscation

```javascript
// הכתובת המוסתרת:
// 'asafben33@gmail.com'
// כשמחוץ לפונקציה:
atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==')  // = 'asafben33@gmail.com'

// הקוד השלם:
var to = atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==');
// ^ לא חשוף ב-grep על pattern של כתובות מייל
```

---

## 14. `download_images.py` v5.1 — מפרט מלא

### 14.1 ארכיטקטורת שלבים

```
Stage 0:  detect_proxy()                    (on import)
Stage 0b: reset_all_recipe_images()         (optional, --reset-images)
Stage 1:  clean_existing_bad_images()       (unless --skip-clean)
Stage 2:  download_all()                    (unless --skip-download)
Stage 3:  run_dedup()                       (unless --skip-dedup)
Stage 3b: inline_alias_into_index()         (optional, --inline-alias)
```

### 14.2 חתימות פונקציות עיקריות

```python
def clean_existing_bad_images(dry_run: bool = False, aggressive: bool = False) -> dict:
    """
    Scans images/recipes_images/*.jpg and deletes bad ones:
    - Too small (<MIN_SIZE bytes)
    - Has EXIF bad markers (7 markers: gopro, dji, parrot, phantom, satellite, google earth, landscape)
    - Extreme aspect ratio (>RATIO_HIGH or <RATIO_LOW via JPEG SOF parse)
    - Known bad SHA256 hashes

    Returns: {scanned, deleted, freed_bytes, reasons}
    """

def reset_all_recipe_images(dry_run: bool = False) -> dict:
    """
    Full reset — deletes ALL r-*.jpg files (replaces clean_bad_images.py --all).
    Returns: {scanned, deleted, freed_bytes}
    """

def run_dedup(dry_run: bool = False) -> None:
    """
    SHA256 grouping → identifies duplicates → deletes copies → builds alias map.
    Writes to images/_IMG_ALIAS.js (replaces cleanup_hardlinks.py).
    """

def inline_alias_into_index(alias_file: Path, index_file: Path,
                            dry_run: bool = False) -> bool:
    """
    Reads _IMG_ALIAS.js, updates the `var _IMG_ALIAS = {...};` block in index.html.
    Returns True if updated, False otherwise.
    """

def source_il_group_batch(idx: int, recipe_title: str, query_en: str) -> List[str]:
    """
    Builds search URL for Israeli domain batch #idx (0-19).
    Uses "מתכון ל" + recipe_title as query.
    Returns: list of up to DOMAINS_PER_GROUP (5) search URLs.
    """

def source_intl_group_batch(idx: int, query_en: str) -> List[str]:
    """
    Builds search URL for International domain batch #idx (0-19).
    Uses "recipe " + query_en as query.
    Returns: list of up to DOMAINS_PER_GROUP (5) search URLs.
    """

def _is_food_image_by_pixels(data: bytes) -> Tuple[bool, str]:
    """
    Rejects images with:
    - JPEG SOF aspect ratio > RATIO_HIGH (2.2 default, 1.9 aggressive)
    - JPEG SOF aspect ratio < RATIO_LOW (0.45 default, 0.55 aggressive)
    Returns: (is_food, reason)
    """

def main() -> int:
    """argparse → dispatcher → run stages in order."""
```

### 14.3 קבועים ו-Thresholds

```python
# Default (non-aggressive)
MIN_SIZE   = 3000     # bytes — file smaller than this is considered failed download
RATIO_HIGH = 2.2      # landscape panorama threshold
RATIO_LOW  = 0.45     # tall portrait threshold

# Aggressive mode (--aggressive-clean)
MIN_SIZE   = 5000
RATIO_HIGH = 1.9
RATIO_LOW  = 0.55

DOMAINS_PER_GROUP = 5           # number of domains per batch
NUM_IL_GROUPS     = 20          # 100 IL domains / 5 = 20 batches
NUM_INTL_GROUPS   = 20          # 100 INTL domains / 5 = 20 batches
```

### 14.4 EXIF Bad Markers

```python
_BAD_MARKERS = [
    (b'gopro',        "GoPro camera (action/landscape)"),
    (b'dji',          "DJI drone"),
    (b'parrot',       "Parrot drone"),
    (b'phantom',      "drone (Phantom)"),
    (b'satellite',    "satellite imagery"),
    (b'google earth', "Google Earth capture"),
    (b'landscape',    "landscape metadata"),
]
```

### 14.5 `_BAD_URL_KW` — מילות מפתח דוחות (100+)

```python
# אנשים (People)
'headshot', 'portrait', 'profile', 'man', 'woman', 'male', 'female',
'person', 'people', 'businessman', 'businesswoman', 'ceo', 'executive',
'model', 'actor', 'actress', 'celebrity', 'politician',

# אירועים (Events)
'wedding', 'ceremony', 'conference', 'event', 'meeting', 'presentation',
'funeral', 'graduation', 'birthday',

# נוף (Landscape)
'landscape', 'skyline', 'mountain', 'ocean', 'beach', 'desert',
'forest', 'sky', 'sunset', 'sunrise', 'aerial', 'drone',
'satellite', 'hotel', 'resort', 'building', 'architecture',

# טכנולוגיה/אחרים (Technology/Other)
'illustration', 'vector', 'logo', 'icon', 'clipart', 'cartoon',
'abstract', 'geometric', 'pattern', 'texture', 'wallpaper',
'keyboard', 'laptop', 'phone', 'computer',
# ... ~100 total
```

### 14.6 CLI Flags

```
--dry-run           # preview only — no delete/write
--reset-images      # Stage 0b — delete ALL r-*.jpg
--clean-only        # only Stage 1 — overrides skip flags
--skip-clean        # skip Stage 1
--aggressive-clean  # use stricter thresholds
--skip-download     # skip Stage 2
--skip-dedup        # skip Stage 3
--overwrite         # re-download existing files
--inline-alias      # Stage 3b — update index.html
--no-proxy          # ignore proxy detection
--proxy URL         # manual proxy override
--detect-only       # only detect proxy + save config
--test-proxy        # actively test each proxy candidate
```

### 14.7 Hebrew / English Query Prefixes

**כל 10 המקורות הישראלים מקבלים prefix עקבי:**
```python
he_search = "מתכון ל" + recipe_title
# דוגמה: "מתכון ל חרירה"
```

**כל 13 המקורות הבינלאומיים מקבלים prefix עקבי:**
```python
en_search = "recipe " + query_en
# דוגמה: "recipe harira"
```

### 14.8 שרשרת Fallback ל-`_getImgFallbacks(r)`

```
1. media.imgs[0]                              # custom user upload
2. "images/recipes_images/r-" + r.id + ".jpg" # standard file
3. _IMG_ALIAS[r.id] → alternate filename      # dedup alias
4. CAT_IMG[r.cat] || CAT_IMG.default          # category fallback
5. (hide image, show .no-img placeholder)
```

---

## 15. Content Security Policy — מפרט מלא

### 15.1 Policy String ב-`<meta>` (v6.3)

```
default-src 'self';
script-src 'self' 'unsafe-inline';
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com;
img-src 'self' data: blob: https://i.ytimg.com https://img.youtube.com;
media-src 'self' blob:;
connect-src 'self';  /* v6.4: removed formsubmit (no fetch anymore) */
frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://formsubmit.co;  /* v6.4: added formsubmit (iframe target) */
object-src 'none';
base-uri 'self';
form-action 'self' https://formsubmit.co;  /* v6.4: added formsubmit (form target) */
```

**שינויים v6.0 → v6.3:**

| Directive | v6.0 | v6.3 | סיבה |
|---|---|---|---|
| `connect-src` | `'self'` | `'self' https://formsubmit.co` | נדרש לשליחת פידבק דרך AJAX |
| `frame-ancestors` | `'none'` (ב-meta) | **הוסר מה-meta** | הדפדפן מתעלם מ-`frame-ancestors` ב-`<meta>`; מוגדר רק ב-`_headers` |

**הסבר על `frame-ancestors`:**

הכותרת `frame-ancestors` **חייבת** להגיע כ-HTTP response header — הדפדפן מתעלם ממנה אם היא מופיעה ב-`<meta>`. לכן ב-v6.2 הוסרה מ-meta ונוספה רק ל-`_headers` של Netlify. הדבר גם מונע warning בקונסול.

### 15.2 Netlify `_headers` (v6.3)

קובץ בשורש הפרויקט המגדיר HTTP headers:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob: https://i.ytimg.com https://img.youtube.com; media-src 'self' blob:; connect-src 'self' https://formsubmit.co; frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com; object-src 'none'; base-uri 'self'; form-action 'self' https://formsubmit.co; frame-ancestors 'none';
```

**הבדלים בין meta ל-headers:**

- `connect-src` — זהה בשניהם: `'self' https://formsubmit.co`.
- `form-action` — ב-headers: `'self' https://formsubmit.co` (מאפשר שליחה של `<form>` עם action ל-formsubmit). במטה: רק `'self'` (כי JS fetch לא עובר דרך CSP `form-action`).
- `frame-ancestors 'none'` — **רק ב-headers**.
- `X-Frame-Options: DENY` — backup ל-`frame-ancestors`, רק ב-headers.

### 15.3 מה חוסמת ה-CSP

| ניסיון | נחסם? | סיבה |
|---|---|---|
| Inline `<script>` | ❌ | CSP מרשה `'unsafe-inline'` |
| Inline `<style>` | ❌ | CSP מרשה `'unsafe-inline'` |
| Google Fonts CSS | ❌ | מורשה `https://fonts.googleapis.com` |
| YouTube thumbnails | ❌ | מורשה `https://i.ytimg.com` |
| YouTube embeds | ❌ | מורשה `https://www.youtube.com` |
| FormSubmit AJAX | ❌ | מורשה `connect-src https://formsubmit.co` (v6.3) |
| picsum.photos images | ✓ חסום | v6.1 הסיר `r.img` מ-fallback, אין יותר ניסיונות |
| ממילא eval() | ✓ חסום | אין `'unsafe-eval'` |
| Third-party iframes | ✓ חסום | רק YouTube מורשה |
| Frame the site externally | ✓ חסום | `frame-ancestors 'none'` ב-headers |


## 16. JSON-LD Schema.org

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "ספר הבישול של משפחת בן הראש",
  "url": "https://perlabenharrosh-cookingbook.netlify.app/",
  "description": "1,054 מתכונים מרוקאיים, ספרדיים ויהודיים אותנטיים",
  "image": "https://perlabenharrosh-cookingbook.netlify.app/images/site_images/og-image.jpg",
  "inLanguage": "he-IL",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://perlabenharrosh-cookingbook.netlify.app/?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  },
  "author": {
    "@type": "Person",
    "name": "אסף בן הראש"
  },
  "dedication": "לזכר פרלה ופנחס בן הראש ז\"ל"
}
```

**תיקון v6.0:** שם המחבר `"אסף בן ארוש"` → `"אסף בן הראש"`; נתיב `image` עודכן ל-`og-image.jpg` המקומי.

---

## 17. Error Handling & Edge Cases

### 17.1 Network/Fetch Errors

| תרחיש | טיפול |
|---|---|
| Network unreachable (feedback form) | `catch()` → setStatus('error') + mailto fallback link |
| Netlify deploy not updated | fetch returns 404 → fallback path |
| CSP blocks fetch | Browser error → catch → fallback |
| CORS preflight fail | fetch fails → fallback path |

### 17.2 Image Loading

| תרחיש | טיפול |
|---|---|
| Image file not found (r-{id}.jpg) | `onerror` → try next fallback in chain |
| All fallbacks exhausted | `imgDiv.classList.add('no-img')` + upload button |
| Base64 image from localStorage corrupted | try/catch around JSON.parse → graceful empty |
| Service Worker cache miss | network fetch → if fail → placeholder |

### 17.3 LocalStorage

| תרחיש | טיפול |
|---|---|
| `localStorage` disabled (private browsing) | try/catch around every `getItem`/`setItem` |
| Quota exceeded (too many images) | `saveMedia` wrapped in try/catch → `showToast('אחסון מלא')` |
| Invalid JSON in stored value | `JSON.parse` wrapped in try/catch → default empty object |

### 17.4 Modal Edge Cases

| תרחיש | טיפול |
|---|---|
| Opening modal while already open | `openM(id)` overwrites — no double stack |
| Clicking outside modal box | `ovlClose(e)` — `if (e.target === e.currentTarget) closeM()` |
| Pressing Escape while in filter dropdown | `keydown` listener on document — closes topmost open element |
| Tab navigation at modal boundary | Focus trap — cycles back to first focusable |
| Opening modal from URL hash | `setTimeout(() => openM(id), 300)` — wait for DOM ready |

### 17.5 Feedback System (v6.3 — FormSubmit.co)

| תרחיש | טיפול |
|---|---|
| User submits without message | Early return + error status (not submitted) |
| Invalid email format | Regex check + error status |
| Double-click submit | `_isSubmitting = true` flag + disable button |
| Message > 2000 chars | Character counter shows 2000/2000 + error on submit |
| User closes modal mid-submit | Fetch continues in background (safe — no data loss) |
| Bot fills `_honey` field | FormSubmit auto-rejects on server side |
| **First-ever submission** | FormSubmit returns `success:false` + activation email → UX shows "תודה! ההודעה נקלטה בהצלחה" |
| **FormSubmit rate-limit exceeded** | Returns 4xx → `.catch()` → fallback to mailto |
| **CSP blocks fetch** (misconfiguration) | fetch throws → `.catch()` → fallback to mailto |
| **Offline** | fetch throws `TypeError: Failed to fetch` → fallback to mailto |
| **FormSubmit service outage** | fetch returns 5xx → `.catch()` → fallback to mailto |

### 17.6 Search

| תרחיש | טיפול |
|---|---|
| Empty search | `filtered()` returns full list (no SEARCH filter applied) |
| Single character | Filter out words < 2 chars in multi-word search |
| Special regex chars in search | `hebrewMorphSearch` uses `indexOf`, not regex |
| Right-to-left reversal issue | `SEARCH.trim().toLowerCase()` — unicode-aware split |

### 17.7 `download_images.py`

| תרחיש | טיפול |
|---|---|
| Network error on single domain | `try/except` → log + continue to next source |
| All 49 sources fail for a recipe | log warning, move on — existing image kept |
| Corrupted JPEG returned | `_is_food_image_by_pixels` rejects non-JPEG |
| Duplicate SHA256 across many files | `run_dedup` keeps first, aliases others |
| `index.html` alias pattern not found | `inline_alias_into_index` returns `False` + warning |
| Proxy unavailable | `--no-proxy` fallback / `--detect-only` to debug |

---

## 18. שינויים v5.0 → v6.0

### 18.1 Security & Metadata

| שינוי | לפני | אחרי |
|---|---|---|
| CSP `img-src` | `*` | `'self' data: blob: https://i.ytimg.com https://img.youtube.com` |
| CSP `form-action` | לא הוגדר | `'self'` |
| CSP `frame-ancestors` | לא הוגדר | `'none'` |
| CSP `media-src` | לא הוגדר | `'self' blob:` |
| CSP `frame-src` | `'none'` | `'self' https://www.youtube.com ...` |
| OG image | Wikimedia 320×240 | `images/site_images/og-image.jpg` 1200×630 |
| Favicon | emoji `🍲` SVG | 3× PNG (192/512/apple-touch) |
| Fonts | Frank Ruhl Libre בלבד | Frank Ruhl Libre + Heebo (כולל ב-print @import) |
| JSON-LD author | `"אסף בן ארוש"` | `"אסף בן הראש"` |
| JSON-LD image | Wikimedia | `og-image.jpg` מקומי |
| CAT_IMG source | 20 Wikimedia URLs | 20 `images/site_images/cat-*.jpg` מקומיים |
| Comment in `script` | `cleanup_hardlinks.ps1` | `download_images.py` (merged) |

### 18.2 Data.js Changes

- **50 מתכונים** קיבלו `tip` field מותאם אישית.
- תוויות קטגוריות:
  - `hol`: `"חגים וחינה"` → `"חגים ומועדים"`
  - `des`: `"מימונה וקינוחים"` → `"קינוחים ומאפים"`
- תוויות תתי-קטגוריות ב"מורשת ספרד" + "מטבח ישראלי" יושרו ל-README.

### 18.3 CSS Classes הוספו (v6.0)

**מערכת פידבק — 28 classes חדשים:**

- `.fb-ovl`, `.fb-ovl.open`, `@keyframes fb-enter`
- `.fb-box`, `.fb-head`, `.fb-title`, `.fb-close`
- `.fb-body`, `.fb-context`
- `.fb-form`, `.fb-field`, `.fb-label`, `.fb-req`, `.fb-hint`
- `.fb-status`, `.fb-status.show`, `.fb-status.success`, `.fb-status.error`, `.fb-status.loading`
- `.fb-actions`, `.fb-btn`, `.fb-btn-1`, `.fb-btn-2`, `.fb-btn:disabled`
- `.fb-fab`, `.fb-fab:hover`, `.fb-fab svg`, `.fb-fab-lbl`
- `.m-act-media.fb-recipe-btn`

### 18.4 DOM IDs הוספו

**מערכת פידבק — 15 IDs חדשים:**

`fb-ovl`, `fb-box`, `fb-title`, `fb-close`, `fb-context`, `fb-form`, `fb-name`, `fb-email`, `fb-message`, `fb-count`, `fb-status`, `fb-cancel`, `fb-submit`, `fb-fab`, `fb-mailto-fallback`, `m-feedback-act`

### 18.5 JavaScript Functions הוספו

**IIFE חדש בסוף ה-`<script>`:**

- `$(id)`, `escapeHtml(s)`, `encodeFormData(data)`, `setStatus(msg, kind)`, `updateCharCount()`
- `openFeedbackModal(type, recipe)`, `closeFeedbackModal()`
- `submitFeedback(e)`, `openMailtoFallback(data)`
- `initFeedback()`

**Constants:** `FORM_NAME = 'perla-feedback'`, `MAX_MSG = 2000`

### 18.6 Python Pipeline — `download_images.py` v5.1

**Unified from 3 scripts:**

| קודם (v5.0 — 3 קבצים) | עכשיו (v5.1 — קובץ יחיד) |
|---|---|
| `clean_bad_images.py` (175 lines) | `clean_existing_bad_images()` function |
| `clean_bad_images.py --all` | `--reset-images` flag + `reset_all_recipe_images()` |
| `cleanup_hardlinks.py` (107 lines) | `run_dedup()` function |
| Manual copy-paste of `_IMG_ALIAS.js` | `--inline-alias` flag + `inline_alias_into_index()` |
| `download_images.py` (monolithic) | `download_images.py` v5.1 (Unified Pipeline) |

**תוספות ב-v5.1:**

- 6 דגלי CLI חדשים: `--reset-images`, `--clean-only`, `--skip-clean`, `--aggressive-clean`, `--inline-alias`, ו-`--dry-run` משופר.
- הרחבת דומיינים: 40 IL + 40 INTL → 100 IL + 100 INTL (tiered).
- רפקטור פונקציות: 15 duplicated functions → 2 `batch` functions + עטיפות תאימות.
- עקביות prefix: כל 10 HE sources → `"מתכון ל"`; כל 13 EN sources → `"recipe "`.
- חיזוק `_BAD_URL_KW` ב-~40 keywords.
- `_is_food_image_by_pixels` עם aspect ratio check משופר.

### 18.7 HTML Additions

**בסוף `<body>` נוסף:**

1. Hidden Netlify form (`<form name="perla-feedback">`).
2. Feedback modal overlay (`<div id="fb-ovl">`).
3. Floating Action Button (`<button id="fb-fab">`).

**ב-`.m-actions` במודל המתכון נוסף:**

```html
<button id="m-feedback-act" class="m-act-media fb-recipe-btn">
  <svg>...</svg>
  הערה / תיקון
</button>
```

---

## 19. שינויים v6.0 → v6.3 — סשן 19/04

### 19.1 UI Enlargement — 2 סיבובים

**סיבוב ראשון (v6.2):**
| רכיב | לפני | אחרי |
|---|---|---|
| `.hdr-search width` | `320px` | `320px` (ללא שינוי) |
| `#srch width` | `180px` | `320px` |
| `#srch font-size` | `.85rem` | `.95rem` |
| `--nav-h` | `44px` | `54px` |
| `.nb font-size` | `.82rem` | `1rem` |
| `.nb font-weight` | normal | `700` |
| `.nb padding` | `0 1rem` | `0 1.3rem` |
| `.pc font-size` | `.78rem` | `1rem` |
| `.acc-hdr font-size` | `.78rem` | `1.18rem` |
| `.acc-hdr color` | `rgba(245,236,215,.7)` | `var(--c-gold-l)` |

**סיבוב שני (v6.3):**
| רכיב | לפני | אחרי |
|---|---|---|
| `.hdr-search` | `width: 320px` קבוע | `flex:1; max-width:640px; min-width:220px` **(גמיש!)** |
| `.hdr-search padding` | `.5rem 1.1rem` | `.65rem 1.3rem` |
| `#srch width` | `320px` | `100%` |
| `#srch font-size` | `.95rem` | `1.05rem` |
| `--nav-h` | `54px` | `60px` |
| `.nb font-size` | `1rem` | `1.1rem` |
| `.nb font-weight` | `600` | `700` |
| `.nb padding` | `0 1.3rem` | `0 1.5rem` |
| `.nb-cnt font-size` | `.78rem` | `.9rem` |
| `.nb-cnt font-weight` | `600` | `700` |
| `.nb-arr font-size` | `.75rem` | `.88rem` |
| `.pc font-size` | `1rem` | `1.08rem` |
| `.pc padding` | `.55rem 1.3rem` | `.72rem 1.5rem` |
| `.acc-hdr font-size` | `1rem` | `1.18rem` |
| `.acc-hdr padding` | `.55rem 1.3rem` | `.8rem 1.7rem` |
| `.acc-hdr border-alpha` | `.28` | `.35` |
| `.pc-cnt font-size` | `.82rem` | `.92rem` |
| `.pc-cnt font-weight` | `500` | `600` |
| `.acc-body gap` | `.55rem` | `.7rem` |
| `.acc-body padding` | `.8rem 1rem` | `1rem 1.3rem` |
| `.nav-panel-inner padding` | `1.1rem 1.5rem 1.3rem` | `1.4rem 1.8rem 1.6rem` |
| `.nav-panel-inner layout` | (no flex) | `display:flex; flex-direction:column; gap:.8rem` |

### 19.2 Feedback System — Migration ל-FormSubmit.co

**הסיבה:** Netlify Forms אינו עובד מ-GitHub Pages (POST מחזיר 405). ראו HLD 14.7 לפרטים מלאים.

**Code changes מפורטים:**

1. **HTML removed** (859 bytes):
   - `<form name="perla-feedback" data-netlify="true" hidden>` + 9 hidden inputs
   - Removed `form-name`, `bot-field`, `feedback-type`, `recipe-id`, `recipe-title`, `sender-name`, `sender-email`, `message`, `page-url`, `user-agent`
   - Replaced with comment: `<!-- Feedback uses FormSubmit.co AJAX -->`

2. **JavaScript constant added:**
   ```javascript
   var FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ==';
   ```
   (base64 obfuscation of asafben33@gmail.com)

3. **`submitFeedback()` rewritten** — ראו מפורט ב-5.9.

4. **`<meta>` CSP updated:**
   ```
   connect-src 'self';
   ```
   → 
   ```
   connect-src 'self' https://formsubmit.co;
   ```

5. **`_headers` updated:**
   - `connect-src 'self' https://formsubmit.co;`
   - `form-action 'self' https://formsubmit.co;`

**One-time activation:**

FormSubmit דורש אישור חד-פעמי בשליחה הראשונה. על בעל האתר ללחוץ על קישור ה-activation שמגיע ב-email לאחר ה-submission הראשון.

### 19.3 Content Updates

**Hero title (HTML line 1461, i18n line 6461):**

- לפני: `המטבח של משפחת בן הראש המורחבת`
- אחרי: `המטבח של משפחת בן הראש (ארוש\הרוש)` (תעתיקים אלטרנטיביים של שם המשפחה)

**Hero tagline (HTML line 1464, i18n line 6465):**

- לפני: `לזכרם של פרלה ופנחס בן הראש — טעמים שמעלים זכרונות שחשבנו שכבר שכחנו...`
- אחרי: `לזכרם של פרלה ופנחס בן הראש ז״ל — טעמים שמעלים זכרונות שכמעט שכחנו...`
- הוסף ז״ל (Hebrew gershayim U+05F4 — לא `"` רגיל)
- פושט "שחשבנו שכבר שכחנו" → "שכמעט שכחנו"
- English: `In memory of Perla & Pinchas Ben-Harrosh z"l — flavors that awaken memories we almost forgot...`

**About memorial paragraph** (HTML line 1480, i18n line 6474, JSON-LD line 1123):

- לפני: `...שזכרונם יהיה לברכה וגאווה לדורי דורות דרך הטעם המעלה זכרונות שחשבנו שכבר שכחנו...`
- אחרי: `...שזכרונם יהיה לברכה וגאווה הלאה לדורי דורות דרך הטעם המעלה זכרונות שכמעט שכחנו...`
- הוסף "הלאה" לפני "לדורי דורות" — מדגיש המשכיות בין-דורית
- English: `...a source of pride onward for generations to come, through flavors that awaken memories we almost forgot...`

**About heading H2** (HTML line 1477, i18n line 6470):

- לפני: `פרלה ופנחס בן הראש ז״ל — המשפחה שיצבה מטבח`
- אחרי: `פרלה ופנחס בן הראש ז״ל — המשפחה שעיצבה מטבח שלם שיזכר ויתבשל הלאה לדורי דורות`
- תיקון שורש `שיצבה` → `שעיצבה` (שורש ע+צ+ב)
- הרחבה הודגשת ערך המשכיות
- English: `The family that shaped an entire kitchen, to be remembered and cooked onward for generations to come`

### 19.4 PWA Install Button Restored

הכפתור היה קיים בסשנים קודמים, אבד, ושוחזר בסשן זה.

**Complete restoration:**

1. **HTML** — inserted as first element in `.hdr-tools`:
   ```html
   <button id="pwa-install-btn" class="hdr-btn hdr-btn-install"
           aria-label="התקן אפליקציה" title="התקן אפליקציה"
           data-i18n-label="pwa_label" data-i18n-aria="pwa_aria"
           data-i18n-title="pwa_title" style="display:none">
     <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
          stroke-linejoin="round" aria-hidden="true">
       <polyline points="8 17 12 21 16 17"/>
       <line x1="12" y1="3" x2="12" y2="21"/>
     </svg>
     <span class="pwa-label" data-i18n="pwa_label">התקן</span>
   </button>
   ```

2. **CSS** — ראו טבלת 3.1 לעיל.

3. **JavaScript** — ראו 5.12 לעיל.

4. **i18n keys** (3 חדשים):
   ```javascript
   pwa_label:  {he:'התקן',           en:'Install'},
   pwa_title:  {he:'התקן אפליקציה',   en:'Install app'},
   pwa_aria:   {he:'התקן אפליקציה',   en:'Install app'},
   ```

### 19.5 JSON-LD SEO Description Updated

JSON-LD `description` (line ~1123) עודכן כדי להתאים לטקסט של pvm`about_memorial` החדש:

- לפני: `1,054 מתכונים... שזכרונם יהיה לברכה וגאווה לדורי דורות דרך הטעם המעלה...`
- אחרי: `1,054 מתכונים... שזכרונם יהיה לברכה וגאווה הלאה לדורי דורות דרך הטעם המעלה...`

### 19.6 File Size Changes

| קובץ | v6.0 | v6.2 | v6.3 | שינוי |
|---|---|---|---|---|
| `index.html` | 359,000 | 377,689 | ~384,572 | +25,572 |
| `_headers` | — | 1,231 | 1,231 | +1,231 |
| `cat_images/*` (20 files) | — | 335 KB | 335 KB | +335 KB |

## 20. מפת התיעוד

| מסמך | גרסה | תיאור |
|---|---|---|
| `README.md` | 6.3 | סקירה כללית, התקנה, מבנה תפריט |
| `CLAUDE.md` | 6.3 | הנחיות למפתחים/AI agents |
| `HLD_Perla_CookingBook.md` | 6.3 | High Level Design |
| `LLD_Perla_CookingBook.md` | **6.3** | **המסמך הנוכחי — Low Level Design** |
| `INTEGRATION_GUIDE.md` | 2.0 | מדריך אינטגרציה של מערכת הפידבק (FormSubmit) |
| `CHANGELOG_19-04-2026_v6.3.md` | — | שינויי הסשן הנוכחי (UI + FormSubmit + PWA) |
| `CHANGELOG_18-04-2026_v2.md` | — | שינויי אבטחה ו-meta של 18/04 |
| `CHANGELOG_download_images_v5.md` | — | שינויי v5.1 של `download_images.py` |
| `download_images_usage_guide.md` | — | מדריך הרצת סקריפט v5.1 |

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
*"האוכל שלה — הסיפור שלנו"*

**סוף LLD v6.4**
