# ספר הבישול של משפחת בן הראש

## HLD — High Level Design

**גרסה 8.38 | 22 אפריל 2026**

*לזכרם של פרלה ופנחס בן הראש ז״ל שזכרונם יהיה לברכה וגאווה הלאה לדורי דורות*
*דרך הטעם המעלה זכרונות שכמעט שכחנו...*

| פרט | ערך |
|---|---|
| Repository | github.com/asafben33/PerlaBenHarroshCookingBook |
| Netlify | https://perlabenharrosh-cookingbook.netlify.app/ |
| GitHub Pages | https://asafben33.github.io/PerlaBenHarroshCookingBook/ |
| Branch | `main` (deploy אוטומטי בשני היעדים) |
| גרסה נוכחית | 8.38 (22/04/2026) |
| היסטוריה | CLAUDE.md + docs/CHANGELOG_*.md |
| בעלים | Asaf Yaakov Ben-Harrosh — בן הזקונים של פרלה ופנחס ז״ל |

> **מקור סמכות לשינויים נוכחיים:** `docs/CLAUDE.md`. מסמך זה מציג תמונה ארכיטקטונית רחבה; לפרטי גרסאות וריצ'נג'לוג ראה CHANGELOGs.

---

## תוכן עניינים

1. [מטרת המערכת וקהל היעד](#1-מטרת-המערכת-וקהל-היעד)
2. [סקירת הפתרון הטכני](#2-סקירת-הפתרון-הטכני)
3. [מודל הנתונים](#3-מודל-הנתונים)
4. [ארכיטקטורת ניווט](#4-ארכיטקטורת-ניווט)
5. [קטגוריות מתכונים](#5-קטגוריות-מתכונים)
6. [חגים — HOLIDAY_TAGS + COMMUNITY_HOLIDAY_TAGS](#6-חגים--holiday_tags--community_holiday_tags)
7. [בינלאומיות — 3 שכבות תרגום](#7-בינלאומיות--3-שכבות-תרגום)
8. [מערכת תמונות — download_images.py v5.1](#8-מערכת-תמונות--download_imagespy-v51)
9. [מערכת פידבק — Web3Forms](#9-מערכת-פידבק--web3forms)
10. [אבטחה — CSP, HSTS, COOP/CORP, SRI](#10-אבטחה--csp-hsts-coopcorp-sri)
11. [פריסה ו-GitHub](#11-פריסה-ו-github)
12. [Responsive & Accessibility & SEO](#12-responsive--accessibility--seo)
13. [PWA ו-Service Worker](#13-pwa-ו-service-worker)
14. [אבולוציה — ציון דרך עיקרי](#14-אבולוציה--ציון-דרך-עיקרי)
15. [מפת התיעוד](#15-מפת-התיעוד)

---

## 1. מטרת המערכת וקהל היעד

ספר הבישול של משפחת בן הראש הוא אתר אינטרנט סטטי המתעד **1,056 מתכונים אותנטיים** מהמטבח המרוקאי-ספרדי-יהודי-מזרחי, כולל 40 מתכונים לא כשרים. האתר נבנה כמסמך דיגיטלי חי שמנציח את מורשת יהדות קזבלנקה ומרקש של פרלה ופנחס בן הראש ז״ל, משלב השפעות ספרדיות ממשפחת קארו (מגורשי ספרד 1492), ומתכונים שנלמדו מהשכנים בקטמון בירושלים.

### 1.1 מטרות עיקריות

- **שימור מורשת** — מניעת אובדן מתכונים שהועברו בעל-פה בין דורות.
- **שמירת כשרות** — הפרדה ברורה בין כשר ללא-כשר, עם הצעות לתחליפי פרווה.
- **נגישות קולינרית** — כמויות מדויקות, שלבים ברורים, טיפים; כל אחד יכול לבשל.
- **ריספונסיביות מלאה** — טלפון, טאבלט, דסקטופ.
- **ביצועים** — static-first, ללא שרת דינמי; Service Worker לחוויה offline.
- **דו-לשוניות** — עברית (RTL, ברירת מחדל) + אנגלית מלאה עם 3 שכבות תרגום.
- **פרטיות ואבטחה** — CSP מחוזק, HSTS preload, COOP/CORP, SRI, ללא tracking.

### 1.2 קהל יעד

- בני המשפחה המורחבת (5 דורות).
- חברים ואורחים שמכירים את מורשת פרלה.
- חוקרי קולינריה יהודית-ספרדית.
- הציבור הרחב המחפש מתכונים אותנטיים.

---

## 2. סקירת הפתרון הטכני

### 2.1 ארכיטקטורה — Multi-File Static SPA

| קובץ | גודל | תוכן |
|---|---|---|
| `index.html` | ~520 KB | HTML + CSS + JS inline; כל הלוגיקה (ניווט, חיפוש, מודאל, פידבק, i18n, PWA, book reader בגלילה) |
| `data.js` | ~1,500 KB | `R` (1,056 מתכונים), `CATS`, `MENU_STRUCTURE`, `HOLIDAY_TAGS`, `COMMUNITY_HOLIDAY_TAGS` |
| `pre_en.js` | ~800 KB | `_PRE_EN` — תרגום EN מוכן: 1,056 × 5 שדות (desc, mem, tip, steps, ingr) |
| `book_data.js` | ~228 KB | `BOOK_HTML` / `BOOK_HTML_EN` — תוכן הספר "על שביל האהבה ממרוקו לירושלים" |
| `about_redesigned.{html,css,js}` | ~40 KB | סקציית "אודות" בעיצוב נפרד |
| `sw.js` | 3.8 KB | Service Worker v19 — network-first להקוד, cache-first לתמונות |
| `manifest.json` | 1.2 KB | PWA manifest (dir=rtl, standalone, icons 192/512/180) |
| `_headers` | 2.2 KB | Netlify security headers (CSP, HSTS, COOP/CORP, cache rules) |
| `sitemap.xml` | 1.5 KB | 6 URLs + hreflang he/en |
| `robots.txt` | ~0.2 KB | מפנה crawlers ל-sitemap |
| `download_images.py` | ~152 KB | Unified image pipeline v5.1 |

**תלויות runtime חיצוניות:** **אפס** חבילות npm. Vanilla JS/HTML/CSS בלבד. פונטים מ-Google Fonts ו-MathJax-style polyfills בצד הלקוח בלבד.

### 2.2 שכבות הארכיטקטורה

| שכבה | טכנולוגיה | תפקיד |
|---|---|---|
| **Presentation** | HTML5 + CSS3 | Semantic HTML, Grid/Flex, RTL, design tokens (34 custom properties), Frank Ruhl Libre + Heebo |
| **Application** | Vanilla JS (ES6+) | 60+ פונקציות — ניווט, סינון, מודאל, חיפוש, תרגום, feedback, PWA install |
| **Data** | `data.js` + `pre_en.js` + `book_data.js` | 1,056 מתכונים + CATS + MENU_STRUCTURE + HOLIDAY_TAGS + COMMUNITY_HOLIDAY_TAGS + תרגומים + תוכן ספר |
| **Client Storage** | `localStorage` | העדפות: שפה, theme, מועדפים, ביטול videos, PWA seen flag |
| **Cache** | Service Worker (`sw.js`) | Network-first לקוד; cache-first לתמונות; shell + `images/book_images/wedding.jpg` נטענים מראש |
| **Forms/Feedback** | Web3Forms + mailto fallback | `https://api.web3forms.com/submit` — הקוד של Web3Forms הוא ציבורי בכוונה |
| **Image Pipeline** | `download_images.py` v5.1 | Clean + Download (200 מקורות) + Dedup + Auto-inline alias map |

### 2.3 עקרונות תכנון

- **Static-first** — אין שרת אפליקציה. HTML/CSS/JS + Service Worker בלבד.
- **Zero external runtime dependencies** — הכל native לדפדפן.
- **Progressive enhancement** — גם ללא JS, HTML בסיסי נקרא.
- **Defense in depth** — CSP מחוזק (frame-ancestors, upgrade-insecure-requests), HSTS preload, COOP/CORP, SRI על CDN scripts, base64 obfuscation של email, honeypot בטפסים.
- **Accessibility by default** — ARIA מלא, focus management, keyboard navigation, `prefers-reduced-motion`.
- **Mobile-first responsive** — breakpoints: 480px, 768px, 1200px.

---

## 3. מודל הנתונים

### 3.1 Recipe Object Schema (`data.js::R[i]`)

| שדה | סוג | חובה | תיאור |
|---|---|---|---|
| `id` | string | כן | מזהה ייחודי: `s1`, `sa2`, `nk_fn3`, `iq7`, `pe12`, `nm_001`... |
| `cat` | string | כן | קטגוריה: `soups`, `meat`, `span`, `isr`, `nonkosher`, ... |
| `badge` | string | כן | תג תצוגה: `מרוקאי`, `ספרדי`, `חגיגי`, `מטעמי אמא`, ... |
| `title` | string | כן | שם המתכון בעברית |
| `desc` | string | כן | תיאור קצר |
| `time` | string | כן | זמן הכנה (`30 דקות`) |
| `serv` | string | כן | מנות (`4 מנות`) |
| `diff` | string | כן | קושי: `קל` / `בינוני` / `מתקדם` |
| `img` | string | כן | URL תמונה (שימור היסטורי — לא בשימוש ב-fallback, ראה 8.4) |
| `mem` | string | לא | זיכרון ממרוקו — טקסט רגשי |
| `ingr` | `Array<{q,i}>` | כן | מרכיבים: `q`=כמות, `i`=מרכיב |
| `steps` | `Array<{t,s}>` | כן | שלבים: `t`=דקות (אופציונלי), `s`=הוראה |
| `tip` | string | לא | טיפ של פרלה |
| `src` | string | לא | קישור מקור |
| `vid` | string | לא | YouTube video id |
| `tags` | `Array<string>` | לא | תגיות חיפוש |

### 3.2 ספירות נתונים (v8.38)

| קבוצה | סה"כ | פירוט |
|---|---|---|
| **מתכונים** | **1,056** | +2 מ-v8.3; 1,056 כותרות EN + 1,056×5 שדות EN |
| **קטגוריות (`CATS`)** | 20 | כולל `all` ו-`nonkosher` |
| **עדות (`iraq..isr`)** | 9 | 30 מתכונים כל עדה = 270 |
| **מרוקו core (8 cats)** | 671 | soups 103, salads 103, veg 87, meat 82, chick 66, fish 70, hol 80, des 80 |
| **ספרד (`span`)** | 73 | אוחד עם מרוקו ב-`morocco_span` ב-v7.9 |
| **לא כשר (`nonkosher`)** | 40 | 14 פירות ים + 26 בשר+חלב |
| **תיוגי חג — מרוקו (`HOLIDAY_TAGS`)** | 121 | על 671 מתכוני מרוקו = 18% (תוקן ב-v7.7) |
| **תיוגי חג — עדות (`COMMUNITY_HOLIDAY_TAGS`)** | 221 | 9 עדות × עד 9 חגים (ללא מימונה) |

---

## 4. ארכיטקטורת ניווט

התפריט בנוי מ-**4 קבוצות עליונות שטוחות** (`MENU_STRUCTURE` ב-`data.js`). זה פלט של מסע ארוך: v6.x (wrapper יחיד עמוק 4 רמות) → v7.0 (6 קבוצות שטוחות) → v7.8 (הסרת `hol` הכפול) → v7.9 (איחוד מרוקו+ספרד).

### 4.1 טבלה מסכמת

| # | `key` / `id` | תווית | סוג | מתכונים | עומק מירבי |
|---|---|---|---|---|---|
| 1 | `all` | הכל | leaf | 1,056 | 0 |
| 2 | `morocco_span` | מרוקו\ספרד | accordion (11 sub-items) | 744 | 2 (חגים) |
| 3 | `communities` | מתכונים טעימים מעוד עדות | accordion (9 עדות × 3 items) | 270 | 3 (עדה→חגים→חג) |
| 4 | `nonkosher` | לא כשר | leaf | 40 | 0 |

> **שים לב:** ה-label "מתכונים טעימים מעוד עדות" (ולא "עדות ישראל") נבחר ב-v8.15 ליצירת טון מזמין יותר. ב-data.js זה הכותרת הרשמית.

### 4.2 תרשים הניווט (v8.38)

```
[הכל] (1,056) — leaf

[מרוקו\ספרד ▼] — 744
├── כל מתכוני מרוקו וספרד
├── מרקים (103)
├── סלטים (103)
├── תבשילי ירקות (87)
├── בשר וקציצות (82)
├── עוף ושבת (66)
├── דגים (70)
├── חגים ומועדים ▼ (80, 121 תיוגים)       ← v7.8 (unified with morocco)
│   ├── כל מתכוני החגים
│   ├── שבת (54), ראש השנה (14), יום כיפור (0)
│   ├── פסח (4), מימונה (7), חנוכה (2), פורים (1)
│   └── שבועות (12), סוכות (27), חינה (14)
├── קינוחים ומאפים (80)
└── ספרד (אנדלוסי) (73)                    ← span sub-only (v7.9)

[מתכונים טעימים מעוד עדות ▼] — 270
├── עיראק ▼ (30)
│   ├── כל המתכונים
│   ├── מאכלים מסורתיים לעדה (IDs specific)
│   └── מאכלי חגים ▼ (9 חגים — v7.4)       ← communityHoliday + holidayKey
├── כורדיסטן ▼ (30) — same 3-item pattern
├── אשכנז ▼ (30, ללא חינה)                ← v8.28
├── תימן ▼ (30)
├── פרס ▼ (30)
├── בוכרה ▼ (30)
├── טוניסיה ▼ (30)
├── יהדות טורקיה ▼ (30)
└── מטבח ישראלי ▼ (30, ללא חינה)          ← v8.28

[לא כשר ▼] — 40 — leaf with ids (14 פירות ים + 26 בשר+חלב)
```

**מימונה** מופיעה רק תחת מרוקו (מסורת מרוקאית בלעדית). **חינה** הוסרה מאשכנז ומטבח ישראלי ב-v8.28 (לא מסורת קדם-חתונה בעדות האלה).

### 4.3 רינדור ואינטראקציה

- `buildNav()` (index.html:7021) — בונה את ה-4 כפתורים העליונים.
- `buildPanel(node, pi)` (index.html:7203) — רקורסיבי; בונה accordion + chips בתוך ה-dropdown.
- `panelCnt(item)` — walker רקורסיבי לספירת מתכונים של תת-עץ (עובר על `item.items` + `item.sub`).
- `_itemHasActive(it)` — walker רקורסיבי שבודק אם ה-state הנוכחי (`ACT_CAT`/`ACT_HOLIDAY`/`ACT_IDS`) תואם לפריט או לצאצא (למטרת auto-expand ב-v8.36).
- `_closeSiblingAccordions(hdr)` — סוגר accordions אחים ברמה אחת, mutual exclusion (v8.37).
- **Focused-view** — CSS `:has()` מסתיר לחלוטין accordions סגורים כשאחד פתוח (v8.38):
  ```css
  :is(.panel-row, .acc-body):has(> .acc-hdr.open) > .acc-hdr:not(.open),
  :is(.panel-row, .acc-body):has(> .acc-hdr.open) > .acc-body:not(.open) {
    display: none !important;
  }
  ```
  דורש Chrome 105+ / Safari 15.4+ / Firefox 121+.

### 4.4 הסתרת רשת בטעינה (v7.1)

האלמנט `<main>` מתחיל עם `class="main-hidden"` (`display:none !important`). הרשת נגלה רק ב-4 נקודות כניסה:

1. `selectCat()` / `selectMulti()` / `selectByIds()` / `selectCommunityHoliday()` — כולן קוראות ל-`showMainGrid()`.
2. `doSearch()` — אם יש טקסט חיפוש.
3. CTA ב-Hero "עיון במתכונים" — מדמה קליק על "הכל".
4. רענון → חוזר למוסתר.

---

## 5. קטגוריות מתכונים

20 קטגוריות ב-`CATS` (כולל `all`):

| `cat` | HE | EN | מתכונים | קבוצה |
|---|---|---|---|---|
| `all` | הכל | All | 1,056 | (שקוף) |
| `soups` | מרקים | Soups | 103 | מרוקו |
| `salads` | סלטים | Salads | 103 | מרוקו |
| `veg` | ירקות ותוספות | Vegetables & Sides | 87 | מרוקו |
| `meat` | בשר וקציצות | Meat & Meatballs | 82 | מרוקו |
| `chick` | עוף ושבת | Poultry & Shabbat | 66 | מרוקו |
| `fish` | דגים | Fish | 70 | מרוקו |
| `hol` | חגים ומועדים | Holidays | 80 | מרוקו |
| `des` | קינוחים ומאפים | Desserts & Pastries | 80 | מרוקו |
| `span` | מורשת ספרד | Sephardic Heritage | 73 | ספרד |
| `iraq` | עיראק | Iraqi | 30 | עדות |
| `kurd` | כורדיסטן | Kurdish | 30 | עדות |
| `ashk` | אשכנז | Ashkenazi | 30 | עדות |
| `yem` | תימן | Yemenite | 30 | עדות |
| `pers` | פרס | Persian | 30 | עדות |
| `buk` | בוכרה | Bukharan | 30 | עדות |
| `tun` | טוניסיה | Tunisian | 30 | עדות |
| `turk` | יהדות טורקיה | Turkish | 30 | עדות |
| `isr` | מטבח ישראלי | Israeli | 30 | עדות |
| `nonkosher` | לא כשרים | Non-Kosher | 40 | לא כשר |

---

## 6. חגים — HOLIDAY_TAGS + COMMUNITY_HOLIDAY_TAGS

### 6.1 HOLIDAY_TAGS — מרוקו בלבד (תוקן ב-v7.7)

**הבעיה ההיסטורית:** עד v7.6 כל 10 החגים הכילו את אותם 80 המתכונים של `cat='hol'` — כי ה-regex המקורי היה זהה לכל החגים. ב-v7.7 בוצע תיוג אמיתי מבוסס:
1. Regex על כותרות 671 מתכוני מרוקו.
2. מסורת יהודית-מרוקאית מתועדת (מקורות: Claudia Roden, Simy Cohen).

| `id` | שם | Recipes |
|---|---|---|
| `shabbat` | שבת | 54 |
| `rosh` | ראש השנה | 14 |
| `kippur` | יום כיפור | 0 |
| `pesach` | פסח | 4 |
| `mimouna` | מימונה | 7 |
| `hanukkah` | חנוכה | 2 |
| `purim` | פורים | 1 |
| `shavuot` | שבועות | 12 |
| `sukkot` | סוכות | 27 |
| `henna` | חינה | 14 |

**סה"כ:** 121 תיוגים יחודיים (18% מ-671). מתכון יכול להופיע במספר חגים.

### 6.2 COMMUNITY_HOLIDAY_TAGS — 9 עדות × 9 חגים (v7.2)

קבוע שממפה **עדה × חג ← מתכונים**:

```javascript
const COMMUNITY_HOLIDAY_TAGS = {
  iraq: { shabbat:[...], rosh:[...], kippur:[...], pesach:[...],
          hanukkah:[...], purim:[...], shavuot:[...], sukkot:[...], henna:[...] },
  kurd: { /* ... 9 holidays ... */ },
  ashk: { /* 8 — ללא חינה (v8.28) */ },
  yem:  { /* 9 */ },
  pers: { /* 9 */ },
  buk:  { /* 9 */ },
  tun:  { /* 9 */ },
  turk: { /* 9 */ },
  isr:  { /* 8 — ללא חינה (v8.28) */ }
};
```

**221 תיוגים יחודיים** מתוך 270 מתכוני עדות (82% כיסוי). מבוסס על מקורות מתועדים. **מימונה לא כלולה** — מסורת מרוקאית בלעדית, תחת `HOLIDAY_TAGS` בלבד.

### 6.3 סינון בזמן ריצה

- `selectCat(catId, h?, groupKey?)` — אם `h` סופק, מסנן לפי `HOLIDAY_TAGS[h]`.
- `selectCommunityHoliday(community, holidayKey, label, groupKey)` — מסנן לפי `COMMUNITY_HOLIDAY_TAGS[community][holidayKey]`.

---

## 7. בינלאומיות — 3 שכבות תרגום

עברית היא שפת ברירת המחדל (RTL). מתג בכותרת (`🌐`) מחליף לאנגלית.

### שכבה 1 — `_TITLE_EN`

1,056 כותרות מתכונים באנגלית. 367 תוקנו לשמות מאכלים מקוריים (Zaalouk, Matbucha, Taktouka, Mofletta, Albondigas, Gazpacho, Sfenj, Kubbeh, Shakshuka, Falafel, Jachnun, Malawach, Sabich).

### שכבה 2 — `_PRE_EN` (pre_en.js)

1,056 מתכונים × 5 שדות: `d` (desc), `m` (mem), `t` (tip), `st` (steps), `ig` (ingr). אפס תווי עברית. נבנה אוטומטית מ-`_FOOD_DICT`.

### שכבה 3 — `_FOOD_DICT`

2,853 ערכי מילון עברית-אנגלית עם מנוע morphological matching:
- **קידומות**: `ב/ו/ל/מ/כ/ה`
- **סיומות**: `ים/ות/ה/ן/ת`
- **Final forms**: `נ→ן`, `מ→ם`, `צ→ץ`
- **שורשים** לזיהוי צורות מוטות

### 7.1 `_NAV_I18N` — תפריט

מיפוי תווית עברית → DICT key. הורחב משמעותית ב-v7.6-v8.0 כדי שכל פריט תפריט של v7.x יתורגם.

### 7.2 DICT ו-`t(key)` / `applyLang(lang)`

DICT מכיל ~155 keys ל-UI labels. `applyLang('en')` סורק את ה-DOM ומחליף טקסטים לפי `_NAV_I18N` + לפי `data-i18n-key` attributes.

---

## 8. מערכת תמונות — `download_images.py` v5.1

### 8.1 Pipeline

```
שלב 0:  Proxy Auto-Detection         (תמיד — בטעינת המודול)
שלב 0b: Reset Images (אופציונלי)    — מחיקת כל r-*.jpg
שלב 1:  Clean Bad Images             — EXIF + aspect ratio + size
שלב 2:  Download (100 IL + 100 INTL) — Hebrew-first, English fallback
שלב 3:  Dedup SHA256 + _IMG_ALIAS.js — מחיקת כפילויות + alias map
שלב 3b: Inline Alias (אופציונלי)    — החדרה ל-index.html
```

### 8.2 מקורות

- **100 דומיינים ישראלים** מדורגים ל-4 tiers (Tier 1 מאומתים → Tier 4 best-guess).
- **100 דומיינים בינלאומיים** כמעט כולם מאומתים.
- `_BAD_URL_KW` — ~100 מילות מפתח דוחות (אנשים, נוף, אירועים, טכנולוגיה).
- `_is_food_image_by_pixels` — דוחה aspect ratio קיצוני (`>2.2` פנורמה, `<0.45` portrait).
- **Prefix עקבי:** `"מתכון ל" + title` לעברית, `"recipe " + query` לאנגלית.

### 8.3 שם קבצים

- `images/recipes_images/r-{id}.jpg` — ראשי.
- `images/recipes_images/r-{id}-2.jpg`, `-3.jpg`, ... — עד 10 תמונות למתכון.
- `images/book_images/*.jpeg` — תמונות מהספר (+ `wedding.jpg`).
- `images/site_images/cat-{cat}.jpg` — fallback לקטגוריה (20 placeholders).
- `images/site_images/og-image.jpg` (1200×630), favicons, apple-touch-icon.
- `images/_IMG_ALIAS.js` — מפת כפילויות SHA256 (auto-generated).

### 8.4 Fallback chain ב-runtime

```
getRecipeImg(r) → images/recipes_images/r-{r.id}.jpg
               → CAT_IMG[r.cat]           (e.g. cat-soups.jpg)
               → CAT_IMG._def             (default placeholder)
```

**`r.img` מוסר מה-fallback ב-v6.1** — 1,056 מתכונים הצביעו ל-`picsum.photos` שנחסם ע"י CSP הצר. כל הנתיבים כעת מקומיים.

---

## 9. מערכת פידבק — Web3Forms

### 9.1 רציונל

מטרה: לאפשר דיווח תיקונים ושיפורים במתכונים **תוך הסתרת כתובת המתחזק** ומבלי לדרוש שרת אפליקציה.

### 9.2 היסטוריית המסע

| גרסה | Backend | בעיה | פתרון |
|---|---|---|---|
| v6.0-v6.2 | Netlify Forms | ✗ 405 ב-GitHub Pages | מעבר ל-FormSubmit AJAX |
| v6.3 | FormSubmit AJAX (`fetch`+JSON) | ✗ CORS preflight fail | hidden iframe |
| v6.4 | FormSubmit + hidden iframe | ✗ 403 anti-spam | ניסיון שדה `_url` |
| v6.5 | FormSubmit + `_url` | ✗ 403 עדיין | החלפת ספק |
| **v6.6+ (נוכחי)** | **Web3Forms** — `fetch()` + CORS תקין | ✓ עובד | — |

### 9.3 מימוש נוכחי (v6.6+)

```javascript
// index.html:11795
var WEB3FORMS_KEY = '705d4207-c4a6-43a2-8fdc-d8e202bc6c9c';
// נשלח ב-JSON ל-https://api.web3forms.com/submit
fetch('https://api.web3forms.com/submit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
  body: JSON.stringify({ access_key: WEB3FORMS_KEY, ...data })
});
```

**המפתח ציבורי בכוונה** — זה alias לאימייל, לא סוד. Web3Forms מזוהה ב-CSP תחת `connect-src`.

### 9.4 נקודות כניסה למשתמש

| נקודה | מיקום | סוג הודעה |
|---|---|---|
| כפתור "הערה / תיקון" | בתוך `.m-actions` בכל מודאל מתכון | `type: "recipe"` + recipe_id + recipe_title |
| FAB צף (#fb-fab) | "הצעות ודיווח", פינה שמאלית-תחתונה (RTL), תמיד גלוי | `type: "site"` |
| פונקציה גלובלית | `window.openFeedbackModal(type, recipe)` | גמיש |

> **v8.35** — כפתור "הערה / תיקון" במודאל קיבל את צבעוניות ה-FAB (זהב/תבלינים) לאחידות ויזואלית.

### 9.5 Fallback

אם `fetch()` נכשל (רשת, CSP, offline, Web3Forms down):
- תצוגת "שליחה ישירה נכשלה. [פתח באימייל במקום]".
- לחיצה → `openMailtoFallback()` → `mailto:` עם subject+body מוכנים + base64-decoded email.

---

## 10. אבטחה — CSP, HSTS, COOP/CORP, SRI

חיזוק אבטחה מקיף בוצע ב-v8.26-v8.28. התצורה הנוכחית ב-`_headers`:

### 10.1 `_headers` (Netlify)

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Resource-Policy: same-site
  X-Permitted-Cross-Domain-Policies: none
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=(),
                       usb=(), magnetometer=(), gyroscope=(), accelerometer=(),
                       ambient-light-sensor=(), autoplay=(self), fullscreen=(self),
                       interest-cohort=()
  Content-Security-Policy: default-src 'self';
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

/sw.js
  Cache-Control: no-cache, no-store, must-revalidate

/images/*
  Cache-Control: public, max-age=31536000, immutable
```

### 10.2 הערות מפתח

- **`frame-ancestors: 'none'`** — רק ב-`_headers`, לא ב-meta (הדפדפן מתעלם ממנו דרך meta). שכבת חיזוק נוספת על `X-Frame-Options: DENY`.
- **HSTS preload** — כל הדומיין מכריח HTTPS ל-12 חודשים (כולל subdomains).
- **COOP (`same-origin`)** — מבודד את Browsing Context מ-popups מאתרים אחרים.
- **CORP (`same-site`)** — מונע טעינה cross-origin של נכסים שלנו.
- **`upgrade-insecure-requests`** — מבטיח שכל משאב נטען ב-HTTPS גם אם ההפניה ב-HTTP.
- **YouTube nocookie** — embeds משתמשים ב-`youtube-nocookie.com` לפרטיות.

### 10.3 SRI על CDN scripts

כל `<script>` שמטעין קוד מ-`cdn.jsdelivr.net` מכיל `integrity="sha384-..."` + `crossorigin="anonymous"`. שינוי בקובץ המקור → הדפדפן דוחה.

### 10.4 פרטיות

- **אימייל מוסתר** — base64 ב-JS (`atob(...)`) + Web3Forms key ציבורי (alias).
- **אין tracking** — ללא Google Analytics, ללא Meta pixel, ללא cookies פרסומיים.
- **Honeypot** — שדה `_url` / `botcheck` בטופס; הודעות מבוטים נדחות שקט.
- **PWA** — `display: standalone`, ללא הרשאות רגישות.

---

## 11. פריסה ו-GitHub

### 11.1 זרימת Deployment

```
מפתח:  git add → git commit → git push origin main
           ↓
GitHub: main מתעדכן
           ↓
Netlify: webhook → build & deploy (Netlify)
GitHub Pages: action → deploy ל-asafben33.github.io
           ↓
משתמשים: CDN serves latest
```

### 11.2 מיקומים

| מאפיין | ערך |
|---|---|
| Repository | `github.com/asafben33/PerlaBenHarroshCookingBook` |
| Netlify (ראשי) | `https://perlabenharrosh-cookingbook.netlify.app/` |
| GitHub Pages (mirror) | `https://asafben33.github.io/PerlaBenHarroshCookingBook/` |
| Branch | `main` |
| Deployment | push אוטומטי (ללא CI/CD חיצוני) |

### 11.3 פעולות הפעלה חד-פעמיות

- **Web3Forms:** כבר הופעל — הודעות מגיעות ישירות.
- **Sitemap:** `sitemap.xml` קיים אם יהיה רצון להגיש למנועי חיפוש בעתיד (לא בפוקוס הנוכחי).

---

## 12. Responsive & Accessibility & SEO

### 12.1 Responsive

| Breakpoint | שינויים |
|---|---|
| Desktop > 1200px | Grid 4 עמודות, dropdown מלא, modal side-by-side |
| Tablet 768-1200px | Grid 3 עמודות, nav condensed |
| Mobile 480-768px | Grid 2 עמודות |
| Mobile < 480px | Grid עמודה 1, modal מלא-מסך, feedback כ-bottom sheet, FAB ללא label |

### 12.2 Accessibility

- `dir="rtl" lang="he"` בשורש.
- ARIA מלא — `role`, `aria-label`, `aria-expanded`, `aria-haspopup`, `aria-modal`, `aria-live`.
- Keyboard: Tab, Enter, Escape, Arrow keys — ניווט מלא + focus trap במודאלים.
- `prefers-reduced-motion` — אנימציות מבוטלות.
- Font scaling — base `17px` (16px במובייל), kerning מותאם ל-RTL.

### 12.3 SEO

- Open Graph: `og:title`, `og:description`, `og:image` (1200×630).
- Twitter Card: `summary_large_image`.
- JSON-LD (Schema.org): `WebSite` + `description` + author = "אסף בן הראש".
- `sitemap.xml` (6 URLs, hreflang he/en) + `robots.txt`.
- Lazy loading: `loading="lazy"`, `decoding="async"`, `fetchPriority="low"`.

---

## 13. PWA ו-Service Worker

### 13.1 PWA

- `manifest.json`: `display: standalone`, `dir: rtl`, `theme_color: #130c05`, `background_color: #fdf8ee`.
- Icons: 192, 512, apple-touch-icon 180.
- Install button `#pwa-install-btn` (v6.9+: תמיד נראה; v6.10: Custom Modal במקום `alert()`).
- 5 מסלולי התקנה: iOS Safari, Android, Firefox desktop, Safari macOS, Chrome/Edge desktop.

### 13.2 Service Worker (`sw.js` v19)

```javascript
const CACHE_NAME = 'perla-cookbook-v19';
const SHELL = ['./', './index.html', './data.js', './pre_en.js',
               './manifest.json', './images/book_images/wedding.jpg', './book_data.js'];
```

**Strategy:**
- **GET images** (regex: `\.(jpg|jpeg|png|webp|gif)$` או `/images/`): **cache-first** + network fallback.
- **GET other** (HTML, JS, CSS, fonts): **network-first** + cache fallback.
- **POST**: passthrough — אף פעם לא נשמר ב-cache.
- Install: caches shell resilient-to-404 (ניסיון אישי לכל קובץ).
- Activate: ניקוי כל ה-caches הישנים + `clients.claim()`.
- Eligibility check (`_shouldCache`): GET בלבד, type=basic, status=200.

---

## 14. אבולוציה — ציון דרך עיקרי

תקציר; פרטים מלאים ב-`docs/CLAUDE.md`.

| גרסה | תאריך | מה נוסף/השתנה |
|---|---|---|
| v5.0 | אפריל 2026 | בסיס — `index.html` + `data.js` |
| v6.0-v6.3 | 18-19/04 | Netlify → FormSubmit, PWA, חיזוק UI |
| v6.4-v6.6 | 19/04 | CORS fix (iframe), Web3Forms migration |
| v6.7-v6.10 | 19/04 | PWA custom modal, Python CLI scripts, UI scaling |
| **v7.0-v7.1** | 19/04 | **שיפוץ דף ראשי** — flat 6-group MENU, Hero CTAs, Main אחרי Bio, main-hidden |
| v7.2-v7.4 | 19/04 | **COMMUNITY_HOLIDAY_TAGS (221 תיוגים), תיקיית חגים לכל עדה** |
| v7.7-v7.9 | 19/04 | **HOLIDAY_TAGS תוקן** (80×10→121 יחודיים), איחוד מרוקו+ספרד |
| **v8.0** | 19/04 | i18n wiring מלא, light theme overrides, sitemap, robots.txt |
| v8.1-v8.4 | 19-20/04 | +2 מתכונים (1,054→1,056), audit נקי |
| v8.5-v8.16 | 20/04 | טיפוגרפיה, ROTD קומפקטי, book reader (v1) |
| v8.17-v8.32 | 20-21/04 | **קורא ספר 3D (StPageFlip)** — על כל גלגוליו |
| **v8.26-v8.28** | 21/04 | **חיזוק אבטחה מקיף** — HSTS, COOP/CORP, SRI, path anchoring; חינה הוסרה מאשכנז+isr |
| **v8.33** | 22/04 | **הסרת קורא ספר 3D** — נשאר רק מצב גלילה (-1,380 שורות) |
| v8.34-v8.38 | 22/04 | **שיפוצי UX תפריט** — chips קטנים, auto-expand, sibling close, focused-view |
| v8.39 | 22/04 | הסרת dead code (`placeholder:'communityHolidays'`) |

---

## 15. מפת התיעוד

| מסמך | תפקיד | גרסה |
|---|---|---|
| `CLAUDE.md` | **מקור סמכות** לשינויים — Hebrew brief לפיתוח בעזרת AI | 8.38 |
| `HLD_Perla_CookingBook.md` | המסמך הנוכחי — ארכיטקטורה רחבה | 8.38 |
| `LLD_Perla_CookingBook.md` | Low Level Design — פונקציות, CSS, DOM, CSP מפורט | 8.38 |
| `INTEGRATION_GUIDE.md` | מדריך אינטגרציה (Web3Forms) | 6.6 |
| `README.md` | סקירה כללית + התקנה | 7.x |
| `README_Recipe_CLI.md` | מדריך לסקריפטי Python (add/edit_recipe, recipe_utils) | 6.7 |
| `PLAN_v7_0_HEBREW.md` + `PLAN_v7_0_ENGLISH.md` | תוכנית v7.0 (מוגשמת) | 7.0 |
| `CHANGELOG_*.md` | שינויים פר-גרסה (v6.3 → v8.x, ~30 קבצים) | per-version |

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
*"האוכל שלה — הסיפור שלנו"*

**סוף HLD v8.38**
