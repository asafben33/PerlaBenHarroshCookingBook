# ספר הבישול של משפחת בן הראש

## HLD — High Level Design

**גרסה 6.0 | אפריל 2026**

*לזכרם של פרלה ופנחס בן הראש שזכרונם יהיה לברכה וגאווה לדורי דורות*
*דרך הטעם המעלה זכרונות שחשבנו שכבר שכחנו...*

| פרט | ערך |
|---|---|
| Repository | github.com/asafben33/PerlaBenHarroshCookingBook |
| Netlify | https://perlabenharrosh-cookingbook.netlify.app/ |
| GitHub Pages | https://asafben33.github.io/PerlaBenHarroshCookingBook/ |
| Branch | main |
| Deployment | push ידני (ללא CI/CD) |
| גרסה נוכחית | 6.0 (18/04/2026) |
| גרסה קודמת | 5.0 (אפריל 2026) |

---

## 1. מבוא ומטרת המערכת

ספר הבישול של משפחת בן הראש הוא אתר ווב סטטי המתעד 1,054 מתכונים אותנטיים מהמטבח המרוקאי, הספרדי-יהודי, ומטבחי יהדות המזרח — כולל 40 מתכונים לא כשרים בקטגוריה ייעודית. האתר נבנה כמסמך דיגיטלי חי, המשמר מורשת קולינרית של יהדות קזבלנקה ומרקש, תוך שילוב השפעות ספרדיות ממשפחת קארו — צאצאי מגורשי ספרד 1492 — ומתכונים שנלמדו מהשכנים והחברים שעטפו את המשפחה באהבה בשכונת הקטמון בירושלים.

### 1.1 מטרות עיקריות

- **שימור מורשת קולינרית לדורות הבאים** — מניעת אובדן מתכונים מסורתיים שסבתות העבירו בעל פה.
- **שמירת כשרות** — הפרדה ברורה בין מתכונים כשרים ולא כשרים, עם הצעות לתחליפי פרווה.
- **נגישות** — כל אחד יכול לבשל, גם מי שמעולם לא בישל; כמויות מדויקות, שלבים ברורים, טיפים.
- **ריספונסיביות מלאה** — עובד על טלפון, טאבלט ומחשב בכל גודל מסך.
- **ביצועים** — אפס תלות בשרת חיצוני דינמי, multi-file SPA סטטי.
- **ניווט אינטואיטיבי** — תפריט dropdown רב-רמתי עם 19 קטגוריות.
- **דו-לשוניות** — עברית RTL ואנגלית מלאה עם 3 שכבות תרגום.
- **פרטיות ואבטחה** — CSP מחוזק, הסתרת אימייל של המתחזק, ללא איסוף נתוני משתמשים.

### 1.2 קהל יעד

- בני המשפחה המורחבת (5 דורות) המעוניינים לבשל את מאכלי הסבתא.
- חברים ואורחים שרוצים להכיר את המטבח המרוקאי-ספרדי-ישראלי.
- חוקרי קולינריה יהודית-ספרדית.
- הציבור הרחב המחפש מתכונים אותנטיים.

---

## 2. סקירת הפתרון הטכני

### 2.1 ארכיטקטורת Multi-File SPA

| מאפיין | ערך | תיאור |
|---|---|---|
| `index.html` | 359 KB | SPA — UI, CSS, JS, מילון, כותרות EN, HTML של הספר, מערכת פידבק |
| `data.js` | 1,389 KB | 1,054 מתכונים, CATS, MENU_STRUCTURE, HOLIDAY_TAGS |
| `pre_en.js` | 782 KB | תרגום EN מוכן: 1,054 × 5 שדות, 0 עברית |
| `book_data.js` | ~80 KB | תוכן הספר "על שביל האהבה ממרוקו לירושלים" (HE + EN) |
| `about_redesigned.css` | ~20 KB | עיצוב סקציית "אודות" החדשה |
| `about_redesigned.html` | ~15 KB | HTML של סקציית אודות |
| `about_redesigned.js` | ~5 KB | אינטראקציות של סקציית אודות |
| `sw.js` | 2.3 KB | Service Worker v10 — cache strategy |
| `manifest.json` | 575 B | PWA manifest |
| `download_images.py` | ~152 KB | Unified v5.1 — Clean + Download + Dedup + Alias |
| **סה"כ נתונים** |  |  |
| מתכונים | 1,054 | כולל 40 לא כשרים (`nk_*`) |
| קטגוריות | 19 | כולל `nonkosher` |
| חגים | 10 | HOLIDAY_TAGS — רשימות ID |
| תלויות JS runtime | 0 | Vanilla JS — ללא React/Vue/Node |
| שפה | עברית RTL + אנגלית | `dir="rtl" lang="he"`, מנגנון תרגום 3 שכבות |
| Lazy Loading | `img.loading="lazy"` | `decoding="async"`, `fetchPriority="low"` |

### 2.2 שכבות הארכיטקטורה

| שכבה | טכנולוגיה | תיאור |
|---|---|---|
| **Presentation** | HTML5 + CSS3 | HTML semantic, Grid/Flex, RTL, 34 Custom Properties, Frank Ruhl Libre + Heebo fonts |
| **Application** | JavaScript ES6+ | 60+ פונקציות: ניווט, סינון, מדיה, מודאל, חיפוש, תרגום, feedback system |
| **Data** | `data.js` + `pre_en.js` + `book_data.js` | 1,054 מתכונים + CATS + MENU + HOLIDAYS + translations + book content |
| **Storage (client)** | `localStorage` | העדפות: שפה, נושא, מדיה אישית, מועדפים, ביטול סרטונים |
| **Cache** | `sw.js` | Service Worker — network-first HTML, cache-first images |
| **Forms/Feedback** | Netlify Forms | טופס פידבק — אימייל מוסתר ב-Dashboard בלבד |
| **Image Pipeline** | `download_images.py` v5.1 | Clean → Download (200 מקורות) → Dedup → Auto-inline |

### 2.3 עקרונות תכנון

- **Static-first** — ללא שרת אפליקציה; HTML/CSS/JS בלבד + Service Worker.
- **Zero external dependencies at runtime** — כל הקוד nativ לדפדפן.
- **Progressive enhancement** — גם ללא JS, HTML בסיסי נקרא.
- **Defense in depth** — CSP, HTTPS, honeypot, base64 obfuscation למיילים.
- **Accessibility by default** — ARIA מלא, focus management, keyboard navigation, `prefers-reduced-motion`.
- **Mobile-first responsive** — breakpoints: 480px, 768px, 1200px.

---

## 3. מבנה הנתונים

### 3.1 Recipe Object Schema

| שדה | סוג | חובה | תיאור |
|---|---|---|---|
| `id` | string | כן | מזהה ייחודי: `s1`, `sa2`, `nk_fn3`, `nm_001`... |
| `cat` | string | כן | קטגוריה: `soups`, `meat`, `span`, `nonkosher`... |
| `badge` | string | כן | תג תצוגה: `מרוקאי`, `ספרדי`, `חגיגי`, `מטעמי אמא`... |
| `title` | string | כן | שם המתכון בעברית |
| `desc` | string | כן | תיאור קצר |
| `time` | string | כן | זמן הכנה (`30 דקות`) |
| `serv` | string | כן | מנות (`4 מנות`) |
| `diff` | string | כן | קושי: `קל` / `בינוני` / `מתקדם` |
| `img` | string | כן | URL תמונה ברירת מחדל |
| `mem` | string | לא | זיכרון ממרוקו — טקסט רגשי |
| `ingr` | `Array<{q,i}>` | כן | מרכיבים: `q`=כמות, `i`=מרכיב |
| `steps` | `Array<{t,s}>` | כן | שלבים: `t`=זמן (minutes, אופציונלי), `s`=הוראה |
| `tip` | string | לא | טיפ של פרלה |
| `src` | string | לא | קישור למקור |
| `vid` | string | לא | קישור לסרטון YouTube |
| `tags` | `Array<string>` | לא | תגיות חיפוש מהירות |

---

## 4. ארכיטקטורת ניווט — MENU_STRUCTURE

התפריט בנוי מכפתור יחיד **"כל המתכונים"** (`key: all_master`) עם dropdown מרובה רמות. כל הקטגוריות מקוננות תחת "מטעמים של אמא ממרוקו":

| קבוצה | סוג | תתי-קטגוריות | מתכונים |
|---|---|---|---|
| **מטעמים של אמא ממרוקו** | accordion + ids | מרקים, סלטים, מנות עיקריות (3), ירקות, חגים (10), קינוחים | 744 |
| ├ מנות עיקריות | nested accordion | בשר (82), עוף (66), דגים (70) | 218 |
| ├ חגים ומועדים | leaf + `sub[]` | 10 חגים | 80 |
| ├ **מורשת ספרד** | accordion + `ids[]` | 8 תתי: מרקים, בשר, דגים, ירקות, שבת, רטבים, לחמים, קינוחים | 73 |
| **מתכונים מהעדות** | accordion + ids | 9 עדות + מטבח ישראלי (4 תתי) | 270 |
| ├ מטבח ישראלי | nested accordion | רחוב (10), עיקריות (9), לחמים (4), קינוחים (7) | 30 |
| **מתכונים לא כשרים** | accordion + `ids[]` | פירות ים (14), בשר וחלב (26) | 40 |
| **סה"כ** |  |  | **1,054** |

### 4.1 תרשים ניווט מלא

```
[כל המתכונים 1054 ▼]
│
├── הכל (1,054)
│
├── מטעמים של אמא ממרוקו ▼
│   ├── הכל במטעמים (744)
│   ├── מרקים (103)
│   ├── סלטים (103)
│   ├── מנות עיקריות ▼
│   │   ├── בשר וקציצות (82)
│   │   ├── עוף ושבת (66)
│   │   └── דגים (70)
│   ├── ירקות ותוספות (87)
│   ├── חגים ומועדים ▼ (80)
│   │   ├── שבת, ראש השנה, יום כיפור
│   │   ├── פסח, מימונה, חנוכה
│   │   └── פורים, שבועות, סוכות, חינה
│   ├── קינוחים ומאפים (80)
│   └── מורשת ספרד ▼ (73)
│       ├── מרקים ומינסטרות (3)
│       ├── בשר וקציצות (8)
│       ├── דגים (3)
│       ├── ירקות ותוספות (28)
│       ├── שבת וחגים (4)
│       ├── רטבים ותבלינים (4)
│       ├── לחמים ומאפים (9)
│       └── קינוחים ומתוקים (13)
│
├── ────────────
├── מתכונים מהעדות ▼ (270)
│   ├── עיראק (30), כורדיסטן (30), אשכנז (30)
│   ├── תימן (30), פרס (30), בוכרה (30)
│   ├── טוניסיה (30), יהדות טורקיה (30)
│   └── מטבח ישראלי ▼ (30)
│       ├── מאכלי רחוב (10)
│       ├── מנות עיקריות (9)
│       ├── לחמים ומאפים (4)
│       └── קינוחים ועוגות (7)
│
├── ────────────
└── מתכונים לא כשרים ▼ (40)
    ├── פירות ים (14)
    └── בשר וחלב (26)
```

---

## 5. מפרט קטגוריות — 19 קטגוריות

| `cat` | שם (HE) | שם (EN) | מתכונים | קבוצה |
|---|---|---|---|---|
| `soups` | מרקים | Soups | 103 | מטעמי אמא |
| `salads` | סלטים | Salads | 103 | מטעמי אמא |
| `veg` | ירקות ותוספות | Vegetables & Sides | 87 | מטעמי אמא |
| `meat` | בשר וקציצות | Meat & Meatballs | 82 | מטעמי אמא |
| `chick` | עוף ושבת | Poultry & Shabbat | 66 | מטעמי אמא |
| `fish` | דגים | Fish | 70 | מטעמי אמא |
| `hol` | חגים ומועדים | Holidays | 80 | מטעמי אמא |
| `des` | קינוחים ומאפים | Desserts & Pastries | 80 | מטעמי אמא |
| `span` | מורשת ספרד | Sephardic Heritage | 73 | מטעמי אמא |
| `iraq` | עיראק | Iraqi | 30 | עדות |
| `kurd` | כורדיסטן | Kurdish | 30 | עדות |
| `ashk` | אשכנז | Ashkenazi | 30 | עדות |
| `yem` | תימן | Yemenite | 30 | עדות |
| `pers` | פרס | Persian | 30 | עדות |
| `buk` | בוכרה | Bukharan | 30 | עדות |
| `tun` | טוניסיה | Tunisian | 30 | עדות |
| `turk` | יהדות טורקיה | Turkish | 30 | עדות |
| `isr` | מטבח ישראלי | Israeli | 30 | עדות |
| `nonkosher` | לא כשרים | Non-Kosher | 40 | לא כשרים |

> **עדכון v6.0:** תוויות הקטגוריות יושרו — `hol` "חגים וחינה" → "חגים ומועדים"; `des` "מימונה וקינוחים" → "קינוחים ומאפים".

---

## 6. חגים ומועדים — HOLIDAY_TAGS

מתכון יכול להופיע במספר חגים בו-זמנית. `HOLIDAY_TAGS` הם מפה של `{holiday_id: [recipe_ids]}`:

| `id` | שם (HE) | שם (EN) | מתכונים |
|---|---|---|---|
| `shabbat` | שבת | Shabbat | 80 |
| `rosh` | ראש השנה | Rosh Hashanah | 80 |
| `kippur` | יום כיפור | Yom Kippur | 80 |
| `pesach` | פסח | Passover | 80 |
| `mimouna` | מימונה | Mimouna | 80 |
| `hanukkah` | חנוכה | Hanukkah | 80 |
| `purim` | פורים | Purim | 80 |
| `shavuot` | שבועות | Shavuot | 80 |
| `sukkot` | סוכות | Sukkot | 80 |
| `henna` | חינה | Henna | 80 |

---

## 7. מנגנון תרגום לאנגלית — 3 שכבות

### שכבה 1: `_TITLE_EN`
1,054 כותרות אנגליות. 367 תוקנו לשמות מאכלים מקוריים: Zaalouk, Matbucha, Taktouka, Mofletta, Albondigas, Gazpacho, Sfenj, Kubbeh, Shakshuka, Falafel, Jachnun, Malawach, Sabich.

### שכבה 2: `_PRE_EN` (pre_en.js)
1,054 מתכונים × 5 שדות: `d` (desc), `m` (mem), `t` (tip), `st` (steps), `ig` (ingr). אפס תווי עברית. נבנה אוטומטית מ-`_FOOD_DICT`.

### שכבה 3: `_FOOD_DICT`
2,853 ערכי מילון עברית-אנגלית עם מנוע morphological matching:
- **קידומות** (prefixes): `ב/ו/ל/מ/כ/ה`
- **סיומות** (suffixes): `ים/ות/ה/ן/ת`
- **final forms**: `נ→ן`, `מ→ם`, `צ→ץ`
- **שורשים** (root stems) לזיהוי צורות מוטות

---

## 8. מערכת תמונות — v5.1

### 8.1 צינור Download Pipeline

מופעל ע"י `download_images.py` (v5.1 — Unified Pipeline) המאחד 3 סקריפטים היסטוריים:

```
שלב 0:  Proxy Auto-Detection            (תמיד — בטעינת המודול)
שלב 0b: Reset Images     (אופציונלי)    — מחיקת כל r-*.jpg
שלב 1:  Clean Bad Images                 — EXIF + aspect ratio + size
שלב 2:  Download (100 IL + 100 INTL)    — Hebrew-first, English fallback
שלב 3:  Dedup SHA256 + _IMG_ALIAS.js    — מחיקת כפילויות + alias map
שלב 3b: Inline Alias     (אופציונלי)    — החדרה ל-index.html
```

### 8.2 פילטר מחוזק (v5.1)

- **100 דומיינים ישראלים** מדורגים לפי 4 tiers ביטחון (Tier 1 מאומתים, Tier 4 best-guess)
- **100 דומיינים בינלאומיים** כמעט כולם מאומתים
- **`_BAD_URL_KW`** — ~100 מילות מפתח דוחות (אנשים, נוף, אירועים, טכנולוגיה)
- **`_is_food_image_by_pixels`** — בדיקת aspect ratio קיצוני (`>2.2` פנורמה, `<0.45` portrait)
- **Prefix עקבי**: כל 10 מקורות עבריים → `"מתכון ל" + title`; כל 13 מקורות אנגליים → `"recipe " + query`

### 8.3 Tiered Israeli Domains

| Tier | תיאור | דוגמאות | כמות |
|---|---|---|---|
| Tier 1 | מאומתים אישית | ynet, walla, mako, haaretz, foody, hashulchan, mevashlim | ~15 |
| Tier 2 | אומת ע"י web search | culinartica, pascalpr, fingerfood, pastaeveryday, rotteml, dvarimbealma, pormeleg.kitchen | ~30 |
| Tier 3 | סבירים (תאגידים/חדשות) | shufersal, tnuva, osem, strauss-group, maariv, nrg, inn, srugim | ~30 |
| Tier 4 | best-guess | jewishcuisine.co.il, moroccan-food.co.il, sephardi-recipes.co.il | ~25 |

### 8.4 שם קבצים

- `images/recipes_images/r-{id}.jpg` — תמונה ראשית של מתכון
- `images/recipes_images/r-{id}-2.jpg`, `r-{id}-3.jpg`... — עד 10 תמונות למתכון
- `images/book_images/book_g42_*.jpg` — תמונות מהספר
- `images/site_images/cat-{cat}.jpg` — תמונת fallback לקטגוריה
- `images/site_images/og-image.jpg` — Open Graph (1200×630)
- `images/site_images/favicon-{192|512}.png` + `apple-touch-icon.png`
- `images/_IMG_ALIAS.js` — מפת כפילויות SHA256 (יוצר ע"י v5.1)

---

## 9. מערכת פידבק — v6.0 (חדש)

### 9.1 רציונל

מטרה: לאפשר למשתמשים לדווח על תיקונים במתכונים, להציע שיפורים, או לדווח על תקלות — **תוך הסתרת כתובת האימייל של המתחזק** ומבלי לדרוש שרת אפליקציה.

### 9.2 ארכיטקטורה

```
משתמש → FAB או כפתור "הערה/תיקון" במודל מתכון
    ↓
Modal פידבק עם טופס
    ↓
POST /  (application/x-www-form-urlencoded)
    ↓
Netlify detects form at build time (<form data-netlify="true">)
    ↓
Netlify stores submission + triggers email notification
    ↓
אימייל נשלח מ-no-reply@netlify.com אל asafben33@gmail.com
    (הכתובת מוגדרת רק ב-Netlify Dashboard — NEVER in source code)
```

### 9.3 נקודות כניסה למשתמש

| נקודה | מיקום | סוג הודעה |
|---|---|---|
| כפתור "הערה / תיקון" | בתוך `.m-actions` בכל modal מתכון | `feedback-type: "recipe"` + recipe-id + recipe-title |
| FAB צף | פינה שמאלית-תחתונה (RTL), תמיד גלוי | `feedback-type: "site"` |
| פונקציה גלובלית | `window.openFeedbackModal(type, recipe)` | גמיש (למשל קישור footer) |

### 9.4 שיטות הסתרת האימייל

1. **Netlify Forms (שיטה עיקרית)** — הכתובת מוגדרת ב-Netlify Dashboard, אף פעם לא בקוד המקור.
2. **Base64 fallback** — אם Netlify לא זמין (למשל ריצה מקומית), קישור `mailto:` עם `atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==')`.
3. **Honeypot field** — `<input name="bot-field">` נסתר דוחה בוטים.
4. **reCAPTCHA** — אופציונלי ב-Netlify Dashboard אם מתחיל להגיע spam.

### 9.5 שדות הטופס

| שדה | חובה | אורך מקסימלי |
|---|---|---|
| `sender-name` | לא | 80 תווים |
| `sender-email` | לא | 100 תווים (regex validation) |
| `message` | **כן** | 2000 תווים |
| `feedback-type` | hidden | `"recipe"` או `"site"` |
| `recipe-id` | hidden (אם recipe) | — |
| `recipe-title` | hidden (אם recipe) | — |
| `page-url` | hidden (auto) | — |
| `user-agent` | hidden (auto, 200 תווים) | — |
| `bot-field` | honeypot | צריך להישאר ריק |

---

## 10. אבטחה — CSP & Headers (v6.0 — מוחזק)

### 10.1 Content Security Policy

```
default-src 'self';
script-src 'self' 'unsafe-inline';
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com;
img-src 'self' data: blob: https://i.ytimg.com https://img.youtube.com;
media-src 'self' blob:;
connect-src 'self';
frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com;
object-src 'none';
base-uri 'self';
form-action 'self';
frame-ancestors 'none';
```

שינויים מגרסה 5.0:
- **`img-src`**: `*` → ספציפי (`'self'`, `data:`, `blob:`, YouTube thumbnails)
- **נוסף**: `media-src`, `form-action`, `frame-ancestors`
- **`frame-src`**: `'none'` → `'self'` + YouTube embeds

### 10.2 Meta Headers נוספים

```html
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta name="referrer" content="no-referrer">
```

---

## 11. פריסה ו-GitHub

### 11.1 זרימת Deployment

```
מפתח:  git add → git commit → git push origin main
           ↓
GitHub: קובץ index.html מתעדכן ב-repo
           ↓
Netlify: webhook triggers build
           ↓
Netlify: scans <form data-netlify="true"> — registers form
           ↓
Netlify: publishes to perlabenharrosh-cookingbook.netlify.app
           ↓
משתמשים: CDN serves latest version
```

### 11.2 מיקומים

| מאפיין | ערך |
|---|---|
| Repository | `github.com/asafben33/PerlaBenHarroshCookingBook` |
| Netlify | `https://perlabenharrosh-cookingbook.netlify.app/` |
| GitHub Pages | `https://asafben33.github.io/PerlaBenHarroshCookingBook/` |
| Branch | `main` |
| Deployment | push ידני (ללא CI/CD) |
| Logs | `logs/download_images_YYYY-MM-DD_HH.MM.log` |

### 11.3 הגדרת Netlify Forms (חד-פעמי)

1. Netlify Dashboard → אתר → `Forms`.
2. לוודא שטופס `perla-feedback` מופיע (מזוהה אוטומטית בזמן build).
3. `Settings & Usage` → `Form notifications` → `Add notification` → `Email`.
4. הזן `asafben33@gmail.com` ושמור.

---

## 12. Responsive Design

| Breakpoint | שינויים |
|---|---|
| Desktop `> 1200px` | Grid 4 עמודות, dropdown מלא, modal side-by-side |
| Tablet `768–1200px` | Grid 3 עמודות, nav condensed |
| Mobile `480–768px` | Grid 2 עמודות |
| Mobile `< 480px` | Grid 1 עמודה, modal full screen, feedback modal כ-bottom sheet, FAB ללא label |

---

## 13. נגישות ו-SEO

| מאפיין | פרטים |
|---|---|
| כיוון שפה | `dir="rtl" lang="he"` |
| Open Graph | `og:title`, `og:description`, `og:image` (1200×630) |
| JSON-LD | Schema.org `WebSite`, author: "אסף בן הראש" |
| ARIA | `role`, `aria-label`, `aria-expanded`, `aria-haspopup`, `aria-modal`, `aria-live` |
| Keyboard | Tab, Enter, Escape, Arrow keys — ניווט מלא + focus trap במודאלים |
| Lazy loading | `img.loading="lazy"`, `decoding="async"`, `fetchPriority="low"` |
| PWA | `manifest.json`, Service Worker (`sw.js` v10) |
| `prefers-reduced-motion` | אנימציות מבוטלות |

---

## 14. סיכום שינויים מגרסה 5.0 → 6.0

### 14.1 אבטחה ו-Metadata (אפריל 2026)

- CSP מוחזק (`img-src` מצומצם, הוספת `form-action`, `frame-ancestors`, `media-src`).
- Favicon: אמוג'י `🍲` → 3 קבצי PNG מקומיים (192, 512, apple-touch-icon).
- פונטים: נוסף Heebo לצד Frank Ruhl Libre (הן ב-`<link>` והן ב-`@import` בתוך קוד ההדפסה).
- OG image: Wikimedia → `images/site_images/og-image.jpg` (1200×630).
- JSON-LD: תיקון שם מחבר ("אסף בן ארוש" → "אסף בן הראש") + תיקון נתיב image.

### 14.2 Data & Content

- 50 מתכונים קיבלו `tip` מותאם אישית (עברית, מזכיר את המשפחה/מרוקו).
- תוויות קטגוריות יושרו: `hol` → "חגים ומועדים"; `des` → "קינוחים ומאפים".
- שמות תתי-קטגוריות ב"מורשת ספרד" ו"מטבח ישראלי" יושרו ל-README.

### 14.3 Image Pipeline — `download_images.py` v5.1

- **מיזוג 3 סקריפטים לאחד**: `clean_bad_images.py` + `cleanup_hardlinks.py` + `download_images.py` → `download_images.py` v5.1.
- **שלב 1 חדש**: `clean_existing_bad_images()` — מוחק תמונות חשודות לפני הורדה.
- **שלב 3b חדש**: `inline_alias_into_index()` — עדכון אוטומטי של `_IMG_ALIAS` ב-`index.html`.
- **הרחבה ל-100+100 דומיינים** (לעומת 40+40).
- **רפקטור**: 15 פונקציות כפולות → 2 פונקציות `batch` גנריות + לולאה דינמית.
- **חיזוק פילטרים**:
  - הרחבת `_BAD_URL_KW` ב-~40 מילות מפתח (אנשים, אירועים, אילוסטרציות, נוף נוסף).
  - `_is_food_image_by_pixels` כולל כעת aspect ratio check.
- **עקביות prefix**: כל 10 מקורות עבריים → `"מתכון ל"`; כל 13 מקורות אנגליים → `"recipe "`.
- **שורת לוג משופרת**: מציגה את ה-query האמיתי ששולח (`"מתכון ל" + title`).
- **6 דגלי CLI חדשים**: `--reset-images`, `--clean-only`, `--skip-clean`, `--aggressive-clean`, `--inline-alias`, `--dry-run`.

### 14.4 Feedback System (חדש)

- Modal פידבק עם 3 נקודות כניסה (recipe button, FAB, פונקציה גלובלית).
- Netlify Forms — כתובת `asafben33@gmail.com` מוסתרת ב-Dashboard בלבד.
- Fallback `mailto:` עם base64 obfuscation.
- WCAG 2.1 compliant — focus trap, ARIA, keyboard nav, `prefers-reduced-motion`.
- UI מתבסס על design tokens קיימים (`--c-spice`, `--c-gold`, `--c-ink` וכו').

---

## 15. מפת התיעוד

| מסמך | גרסה | תיאור |
|---|---|---|
| `README.md` | 6.0 | סקירה כללית, התקנה, מבנה תפריט, קבצי נתונים |
| `CLAUDE.md` | 6.0 | הנחיות למפתחים/AI agents לעבודה על הפרויקט |
| `HLD_Perla_CookingBook.md` | **6.0** | המסמך הנוכחי — High Level Design |
| `LLD_Perla_CookingBook.md` | **6.0** | Low Level Design — פונקציות, CSS, DOM |
| `INTEGRATION_GUIDE.md` | 1.0 | מדריך אינטגרציה של מערכת הפידבק |
| `CHANGELOG_18-04-2026_v2.md` | — | שינויי אבטחה ו-meta של 18/04 |
| `CHANGELOG_download_images_v5.md` | — | שינויי v5.1 של `download_images.py` |

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
*"האוכל שלה — הסיפור שלנו"*

**סוף HLD v6.0**
