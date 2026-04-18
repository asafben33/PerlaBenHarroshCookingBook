# ספר הבישול של משפחת בן הראש

**גרסה 6.4 | 19 אפריל 2026**

לזכרם של **פרלה ופנחס בן הראש ז״ל** שזכרונם יהיה לברכה וגאווה הלאה לדורי דורות
דרך הטעם המעלה זכרונות שכמעט שכחנו...

פרלה נולדה בקזבלנקה, גדלה במרקש, ועלתה לישראל עם לב מלא בטעמים ובסיפורים.
נישאה לפנחס, איש ממשפחת קארו — צאצאי **רבי יוסף קארו**, מגורשי קסטיליה 1492.
המטבח שלה שילב שני עולמות: **מרוקו העמוקה** ו**ספרד האנדלוסית**, ומאכלים שלמדה משכנים וחברים שתמיד עטפו אותה באהבה וחום.
עם העלייה לישראל הגיעו לשכונת הקטמון בירושלים. שם, בין שכנות מעיראק, כורדיסטן, אשכנז, תימן, פרס ובוכרה — הפך מטבחה לפסיפס שלם.

> *"ספר הבישול של משפחת בן הראש — דרך הטעם המעלה זכרונות שכמעט שכחנו..."*

---

## סטטיסטיקות

| מאפיין | ערך |
|--------|-----|
| מתכונים | **1,054** (כולל 40 לא כשרים) |
| קטגוריות קולינריות | **19** |
| חגים ומועדים | **10** |
| מילון תרגום (עברית-אנגלית) | **2,853** ערכים |
| כותרות אנגליות מתורגמות | **1,054** (367 תוקנו לשמות מקוריים) |
| תרגום מוכן מראש (pre_en.js) | **1,054** מתכונים × 5 שדות |
| ערכי TITLE_QUERIES בסקריפט ההורדה | **810** |
| תלויות חיצוניות | **0** |

---

## מבנה הפרויקט

```
PerlaBenHarroshCookingBook/
├── index.html              ← SPA — UI, CSS, JS, מילון, כותרות EN, PWA install btn (v6.3)
├── data.js                 ← 1,054 מתכונים + CATS + MENU_STRUCTURE + HOLIDAY_TAGS
├── pre_en.js               ← תרגום EN מוכן — desc, mem, tip, steps, ingr
├── book_data.js            ← תוכן הספר הביוגרפי (BOOK_HTML / BOOK_HTML_EN)
├── about_redesigned.html   ← דף "אודות" מעוצב מחדש
├── about_redesigned.css    ← עיצוב דף אודות
├── about_redesigned.js     ← לוגיקת דף אודות
├── sw.js                   ← Service Worker — network-first documents, cache-first images
├── manifest.json           ← PWA manifest (התקנה כאפליקציה)
├── _headers                ← Netlify HTTP headers — CSP, X-Frame-Options, Permissions-Policy (v6.2)
├── download_images.py      ← סקריפט הורדת תמונות v5.1 (מאוחד, 810 search terms)
├── images/
│   ├── recipes_images/     ← תמונות מתכונים: r-{id}.jpg
│   ├── book_images/        ← תמונות ספר + wedding.jpg
│   └── site_images/        ← אייקונים, OG image, 7 favicons, 20 cat-*.jpg placeholders
├── HLD_Perla_CookingBook.md       ← High Level Design v6.3
├── LLD_Perla_CookingBook.md       ← Low Level Design v6.3
├── INTEGRATION_GUIDE.md           ← מדריך אינטגרציה v2.0 (FormSubmit.co)
├── CHANGELOG_19-04-2026_v6.3.md   ← שינויי סשן 19/04
├── CHANGELOG_18-04-2026_v2.md     ← שינויי 18/04
├── CHANGELOG_download_images_v5.md ← שינויי download_images.py v5.1
├── download_images_usage_guide.md ← מדריך הרצת סקריפט הורדה
├── .gitignore
├── CLAUDE.md                      ← הנחיות למפתחים/AI (v6.3)
└── README.md                      ← המסמך הזה
```

---

## התקנה והפעלה

```bash
open index.html        # macOS
start index.html       # Windows
python -m http.server 8000  # עם שרת מקומי
```

---

## הורדת תמונות

```bash
python download_images.py
# לוג נשמר ב: logs/download_images_YYYY-MM-DD_HH.MM.log
```

---

## מבנה התפריט (MENU_STRUCTURE)

כפתור יחיד **"כל המתכונים"** עם dropdown:

```
[כל המתכונים 1054 ▼]
│
├── הכל (1,054)
│
├── מטעמים של אמא ממרוקו ▼
│   ├── הכל במטעמים (671)
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
│   ├── מורשת ספרד ▼ (73)
│   │   ├── מרקים ומינסטרות (3)
│   │   ├── בשר וקציצות (8)
│   │   ├── דגים (3)
│   │   ├── ירקות ותוספות (28)
│   │   ├── שבת וחגים (4)
│   │   ├── רטבים ותבלינים (4)
│   │   ├── לחמים ומאפים (9)
│   │   └── קינוחים ומתוקים (13)
│   ├── ────────────
│   ├── מתכונים מהעדות ▼ (270)
│   │   ├── עיראק (30), כורדיסטן (30), אשכנז (30)
│   │   ├── תימן (30), פרס (30), בוכרה (30)
│   │   ├── טוניסיה (30), יהדות טורקיה (30)
│   │   └── מטבח ישראלי ▼ (30)
│   │       ├── מאכלי רחוב (10)
│   │       ├── מנות עיקריות (9)
│   │       ├── לחמים ומאפים (4)
│   │       └── קינוחים ועוגות (7)
│   ├── ────────────
│   └── מתכונים לא כשרים ▼ (40)
│       ├── פירות ים (14)
│       └── בשר וחלב (26)
```

---

## קטגוריות (19)

### מטעמים של אמא ממרוקו (744 מתכונים)

| cat | שם בממשק | מתכונים | הערות |
|-----|----------|---------|-------|
| soups | מרקים | 103 | חרירה, מרק עדשים, מרק ירקות |
| salads | סלטים | 103 | מטבוחה, זאלוק, טקטוקה, חומוס |
| meat | בשר וקציצות | 82 | טאג׳ין, קפתה, קציצות |
| chick | עוף ושבת | 66 | טאג׳ין עוף, סנה, פסטייה |
| fish | דגים | 70 | דג בחרמולה, דג ברוטב |
| veg | ירקות ותוספות | 87 | חצילים, במיה, כרוב |
| hol | חגים ומועדים | 80 | 10 חגים, מימונה, חינה |
| des | קינוחים ומאפים | 80 | מקרוד, שבקיה, ספינג׳ |
| span | מורשת ספרד | 73 | 8 תתי-קטגוריות, אלבונדיגס, אדאפינה |

### ספרדי-מרוקאי וס"ט (73 מתכונים, 8 תתי-קטגוריות)

| תת-קטגוריה | מתכונים | דוגמאות |
|------------|---------|---------|
| מרקים ומינסטרות | 3 | גספאצ׳ו, קלדו |
| בשר וקציצות | 8 | אלבונדיגס, קבב ספרדי |
| דגים | 3 | סוקד, טיירה דה פשקה |
| ירקות ותוספות | 28 | טורטייה, פטאטאס ברבאס |
| שבת וחגים | 4 | אדאפינה, קוקידו |
| רטבים ותבלינים | 4 | סופריטו, אייולי |
| לחמים ומאפים | 9 | בורקיטאס, פסטלון |
| קינוחים ומתוקים | 13 | קרמה קטלנה, ביסקוצ׳וס |

### מתכונים מהעדות (270 מתכונים)

| cat | קהילה | מתכונים |
|-----|-------|---------|
| iraq | עיראק | 30 |
| kurd | כורדיסטן | 30 |
| ashk | אשכנז | 30 |
| yem | תימן | 30 |
| pers | פרס | 30 |
| buk | בוכרה | 30 |
| tun | טוניסיה | 30 |
| turk | יהדות טורקיה | 30 |
| isr | מטבח ישראלי | 30 |

**תתי-קטגוריות מטבח ישראלי (30 מתכונים):**
מאכלי רחוב ישראליים (10) — פלאפל, חומוס, שקשוקה, שוורמה, סביח
מנות עיקריות (9) — מג׳דרה, חמין ישראלי, כבד קצוץ
לחמים ומאפים (4) — פיתה, בורקס, ג׳חנון
קינוחים ועוגות (7) — עוגת תפוחים, קרמבו, עוגיות קוקוס

### מתכונים לא כשרים (40 מתכונים)

| תת-קטגוריה | מתכונים | הסבר |
|------------|---------|-------|
| פירות ים | 14 | שרימפס, קלמארי, דגים לא כשרים |
| בשר וחלב | 26 | מתכונים עם שילוב בשר וחלב |

---

## ארכיטקטורה טכנית

### קבצים

| קובץ | גודל | תיאור מפורט |
|-------|------|------------|
| index.html | ~341 KB | SPA — CSS, HTML, _FOOD_DICT (2,853), _TITLE_EN (1,054), CAT_IMG, I18N, JS functions |
| data.js | ~1.4 MB | R[] (1,054 recipes), CATS (20), MENU_STRUCTURE, HOLIDAY_TAGS (10) |
| pre_en.js | ~782 KB | _PRE_EN — 1,054 recipes × 5 fields (d,m,t,st,ig), 0 Hebrew chars |
| sw.js | ~2.7 KB | Service Worker v10 — network-first documents, cache-first images |
| download_images.py | ~104 KB | 810 TITLE_QUERIES, INGR_FALLBACK, CAT_QUERY, 5 image sources |
| cleanup_hardlinks.py | ~3.3 KB | SHA256 scan → dedup → _IMG_ALIAS.js |

### Global State

| משתנה | ברירת מחדל | תיאור |
|-------|-----------|-------|
| `ACT_CAT` | `'all'` | קטגוריה פעילה |
| `ACT_CATS` | `[]` | קטגוריות multi-select |
| `ACT_IDS` | `null` | `Set<string>` — סינון תת-קטגוריה |
| `ACT_HOLIDAY` | `null` | חג פעיל |
| `ACT_DIFF` | `'all'` | רמת קושי |
| `SHOW_FAVS` | `false` | מועדפים בלבד |
| `ING_TAGS` | `Set()` | תגיות מרכיבים |
| `SEARCH` | `''` | חיפוש מורפולוגי עברי |
| `_LANG` | `'he'` | שפה נוכחית (he/en) |

### מנגנון תרגום (אנגלית) — 3 שכבות

1. **_TITLE_EN** — 1,054 כותרות מתורגמות, 367 תוקנו לשמות מקוריים (Zaalouk, Matbucha, Albondigas...)
2. **_PRE_EN** (pre_en.js) — 1,054 מתכונים × 5 שדות (desc, mem, tip, steps, ingr) — 0 תווי עברית
3. **_FOOD_DICT** — 2,853 ערכי מילון עם morphological matching (prefixes ב/ו/ל/מ, suffixes ים/ות/ה)

### ניהול מדיה (localStorage)
- `perla_media_{id}` → `{imgs:[...base64], vids:[...urls]}` — עד 3 תמונות + 5 סרטונים
- `perla_vid_del_{id}` → ביטול סרטון נתוני
- `perla_favs` → מועדפים

### מבנה תיקיית images/
- `images/recipes_images/` — תמונות מתכונים בפורמט `r-{id}.jpg` (מורדות אוטומטית על ידי `download_images.py`)
- `images/book_images/` — תמונות הספר הביוגרפי (WhatsApp) + `wedding.jpg`
- `images/site_images/` — אייקונים (favicon-192, favicon-512, apple-touch-icon), OG image, ותמונות fallback לקטגוריות (`cat-{cat}.jpg`)

---

## פיצ'רים עיקריים

### חוויית משתמש
- **חיפוש מורפולוגי עברי** — מזהה צורות הטיה (בצל, לבצל, מבצל, בצלים)
- **סינון רב-ממדי** — קטגוריה × רמת קושי × חג × תגיות מרכיבים × מועדפים
- **תוצאות חיות** — מתעדכנות בזמן הקלדה
- **דף "אודות"** מעוצב עם ביוגרפיה של פרלה ופנחס ז״ל

### תרגום
- **עברית + אנגלית** — toggle מיידי, 2,853 ערכי מילון + 1,054 תרגומים מוכנים מראש
- תרגום morphological של כותרות, תיאורים, זיכרונות, טיפים, שלבים, מרכיבים

### PWA (Progressive Web App)
- **כפתור "התקן" בולט** בהדר (v6.3 — שוחזר) — pulse animation, מתחבא אחרי התקנה
- **iOS support** — הוראות הוספה למסך הבית אם הדפדפן לא תומך ב-`beforeinstallprompt`
- **Service Worker** — network-first למסמכים, cache-first לתמונות
- **offline mode** — האתר פועל גם בלי אינטרנט (מתוך cache)

### מערכת פידבק (v6.4 — FormSubmit + Hidden Iframe)
- **כפתור "הערה / תיקון"** בכל modal של מתכון
- **FAB צף** שמאלי-תחתון — "הצעות ודיווח"
- **שיטה: Hidden iframe + form POST** — לא fetch (פותר CORS preflight block מ-GitHub Pages)
- Form submissions ל-iframe **אינן כפופות ל-CORS** (התנהגות HTML מורשת) — עובד מכל מקור
- Timeout 15s + **fallback ל-mailto** אוטומטי אם משהו נכשל
- **Base64 obfuscation** של כתובת המייל — action נקבעת דינמית ב-JS

### אבטחה
- **CSP מוחזק** (v6.3) — רק מקורות מאושרים, `connect-src` כולל formsubmit.co בלבד
- **`_headers`** של Netlify — X-Frame-Options, frame-ancestors, Permissions-Policy
- **אין תלויות חיצוניות** — 100% self-contained

### נגישות (WCAG 2.1)
- **RTL + עברית**, `dir="rtl" lang="he"`
- **ARIA roles** — `role`, `aria-label`, `aria-expanded`, `aria-modal`
- **Keyboard navigation** — Tab, Enter, Escape, Arrow keys, focus trap
- **`prefers-reduced-motion`** — אנימציות מבוטלות (pulse, transitions)

### מדיה אישית
- **תמונות אישיות** למתכונים (עד 3 לכל מתכון, localStorage)
- **סרטונים** (YouTube iframes) — עד 5 למתכון
- **מועדפים** — רשימה אישית ב-localStorage

---

## פריסה

| שרת | כתובת |
|-----|-------|
| Netlify | https://perlabenharrosh-cookingbook.netlify.app/ |
| GitHub Pages | https://asafben33.github.io/PerlaBenHarroshCookingBook/ |
| Repository | github.com/asafben33/PerlaBenHarroshCookingBook |
| Branch | main |
| Build | ללא CI/CD — push ידני |
| Logs | logs/download_images_YYYY-MM-DD_HH.MM.log |

### דרישה חד-פעמית (FormSubmit activation)

לאחר הפריסה הראשונה, שלח הודעה דרך FAB. FormSubmit ישלח לך מייל verification — לחץ על הקישור. מאותו רגע כל ההודעות יגיעו רגיל.

### Deploy מ-PowerShell

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
git add .
git commit -m "description"
git push origin main
```

Netlify + GitHub Pages יפרוסו אוטומטית תוך 1-2 דקות.

---

## תיעוד טכני

| מסמך | גרסה | תיאור |
|------|-------|-------|
| `HLD_Perla_CookingBook.md` | 6.4 | High Level Design — ארכיטקטורה, תפריט, קטגוריות, חגים, תרגום, responsive, feedback, PWA |
| `LLD_Perla_CookingBook.md` | 6.4 | Low Level Design — CSS tokens, DOM IDs, 48+ פונקציות, filtered(), buildNav(), openM(), submitFeedback(), PWA IIFE |
| `INTEGRATION_GUIDE.md` | 3.0 | מדריך אינטגרציה של מערכת הפידבק (FormSubmit + Hidden Iframe) |
| `CHANGELOG_19-04-2026_v6.4.md` | — | תיקון CORS — מעבר ל-hidden iframe approach |
| `CHANGELOG_19-04-2026_v6.3.md` | — | שינויי 19/04 חלק א׳ — UI enlargement, FormSubmit AJAX (נכשל), PWA restore, content |
| `CHANGELOG_18-04-2026_v2.md` | — | שינויי 18/04 — meta/security fixes, 50 tips, 20 cat-*.jpg placeholders, 7 favicons |
| `CHANGELOG_download_images_v5.md` | — | שינויי download_images.py v5.1 — unified, 6 CLI flags, 100+100 domains |
| `download_images_usage_guide.md` | — | מדריך הרצת download_images.py v5.1 |
| `CLAUDE.md` | 6.4 | הנחיות למפתחים/AI agents לעבודה על הפרויקט |

---

## היסטוריית גרסאות

| גרסה | תאריך | עיקרי השינויים |
|---|---|---|
| 5.0 | אפריל 2026 | בסיס — 1,054 מתכונים, 19 קטגוריות, תרגום מלא, PWA |
| 6.0 | 18/04/2026 | CSP מוחזק, favicons PNG, OG image, feedback system (Netlify Forms) |
| 6.1 | 18/04/2026 | הסרת r.img/-2/-3 מ-fallback (מונע 3,162 שגיאות/טעינה) |
| 6.2 | 18/04/2026 | 20 cat-*.jpg placeholders, `_headers` file, UI enlarge סיבוב 1 |
| 6.3 | 19/04/2026 | UI enlarge סיבוב 2, FormSubmit AJAX migration, PWA install button, content updates |
| **6.4** | **19/04/2026** | **CORS fix — מעבר מ-fetch+JSON ל-hidden iframe + form POST** |

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
*"האוכל שלה — הסיפור שלנו"*
