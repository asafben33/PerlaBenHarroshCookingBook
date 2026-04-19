# ספר הבישול של משפחת בן הראש

**גרסה 8.0 | 19 אפריל 2026**

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
| חגים — מרוקו | **10** (`HOLIDAY_TAGS` תוקן ב-v7.7) |
| חגים — עדות | **9** לכל אחת מ-9 העדות (`COMMUNITY_HOLIDAY_TAGS`, ללא מימונה) |
| תיוגים יחודיים — מרוקו | **121** מתוך 671 מתכוני מרוקו (18%) |
| תיוגים יחודיים — עדות | **221** מתוך 270 מתכוני עדות (82%) |
| מילון תרגום (עברית-אנגלית) | **~2,860** ערכים (155 ב-DICT + ~1,054 מ-pre_en.js + ~1,650 ב-_FOOD_DICT) |
| כותרות אנגליות מתורגמות | **1,054** (367 תוקנו לשמות מקוריים) |
| תרגום מוכן מראש (pre_en.js) | **1,054** מתכונים × 5 שדות |
| ערכי TITLE_QUERIES בסקריפט ההורדה | **810** |
| תלויות חיצוניות | **0** |
| גרסאות במחזור v7.0 → v8.0 | **11** (19/04/2026) |

---

## מבנה הפרויקט

```
PerlaBenHarroshCookingBook/
├── index.html              ← SPA — UI, CSS, JS, מילון, כותרות EN, PWA install btn, v8.0 i18n + light theme
├── data.js                 ← 1,054 מתכונים + CATS + MENU_STRUCTURE (v7.9 — 4 flat groups) + HOLIDAY_TAGS (v7.7) + COMMUNITY_HOLIDAY_TAGS (v7.4)
├── pre_en.js               ← תרגום EN מוכן — desc, mem, tip, steps, ingr
├── book_data.js            ← תוכן הספר הביוגרפי (BOOK_HTML / BOOK_HTML_EN)
├── about_redesigned.html   ← דף "אודות" מעוצב מחדש
├── about_redesigned.css    ← עיצוב דף אודות
├── about_redesigned.js     ← לוגיקת דף אודות
├── sw.js                   ← Service Worker — network-first documents, cache-first images
├── manifest.json           ← PWA manifest (התקנה כאפליקציה)
├── sitemap.xml             ← SEO sitemap (חדש v8.0 — 6 URLs + hreflang)
├── robots.txt              ← מצביע ל-sitemap (חדש v8.0)
├── _headers                ← Netlify HTTP headers — CSP, X-Frame-Options, Permissions-Policy (v6.2)
├── recipe_utils.py         ← ספריית Python לניהול מתכונים (v6.7)
├── add_recipe.py           ← אשף הוספת מתכון (v6.7)
├── edit_recipe.py          ← אשף עריכה/מחיקה של מתכון (v6.7)
├── download_images.py      ← סקריפט הורדת תמונות v5.1 (מאוחד, 810 search terms)
├── audit_recipes.py        ← סקריפט ביקורת אוטומטי לאיכות מתכונים (לא מתקן)
├── images/
│   ├── recipes_images/     ← תמונות מתכונים: r-{id}.jpg
│   ├── book_images/        ← תמונות ספר + wedding.jpg
│   └── site_images/        ← אייקונים, OG image, 7 favicons, 20 cat-*.jpg placeholders
├── HLD_Perla_CookingBook.md       ← High Level Design (יסטוריה — v6.3, רענון מתוכנן)
├── LLD_Perla_CookingBook.md       ← Low Level Design (יסטוריה — v6.3, רענון מתוכנן)
├── INTEGRATION_GUIDE.md           ← מדריך אינטגרציה (Web3Forms)
├── PLAN_v7_0_HEBREW.md            ← תוכנית עבודה (עודכן v8.0 — Roadmap מקוצר)
├── PLAN_v7_0_ENGLISH.md           ← Handoff טכני (עודכן v8.0)
├── CLAUDE_md_v7_update.md         ← תוספת ל-CLAUDE.md עבור v7.0-v7.6
├── CLAUDE_md_v8_update.md         ← תוספת ל-CLAUDE.md עבור v7.7-v8.0
├── CHANGELOG_19-04-2026_v8_0_*.md ← v8.0 — i18n + theme + SEO + print
├── CHANGELOG_19-04-2026_v7_9_*.md ← v7.9 — איחוד מרוקו וספרד
├── CHANGELOG_19-04-2026_v7_8_*.md ← v7.8 — הסרת כפילות חגים
├── CHANGELOG_19-04-2026_v7_7_*.md ← v7.7 — תיקון HOLIDAY_TAGS
├── CHANGELOG_19-04-2026_v7_6_*.md ← v7.6 — i18n + DOM order + Web3Forms
├── CHANGELOG_19-04-2026_v7_5_*.md ← v7.5 — header strip מצומצם
├── CHANGELOG_19-04-2026_v7_4_*.md ← v7.4 — תיקיות חגים + מימונה רק במרוקו
├── CHANGELOG_19-04-2026_v7_3_*.md ← v7.3 — חגים בתוך כל עדה
├── CHANGELOG_19-04-2026_v7_2_*.md ← v7.2 — COMMUNITY_HOLIDAY_TAGS
├── CHANGELOG_19-04-2026_v7_centered_hero.md ← v7.0 + v7.1
├── CHANGELOG_19-04-2026_v6_3..v6_10.md ← שינויי סשני v6.x
├── README_Recipe_CLI.md           ← מדריך סקריפטי Python
├── .gitignore
├── CLAUDE.md                      ← הנחיות למפתחים/AI (יסטוריה — v6.10, יחד עם CLAUDE_md_v7/v8_update)
└── README.md                      ← המסמך הזה (v8.0)
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

## מבנה התפריט (MENU_STRUCTURE) — v8.0 (4 Top-Level Groups)

**החל מ-v7.9:** 4 קבוצות עליונות במקום 6. שינויים מהותיים:
- v7.4 — לכל עדה accordion עם 3 פריטים (כל המתכונים / מאכלים מסורתיים / מאכלי חגים)
- v7.7 — `HOLIDAY_TAGS` של מרוקו תוקן (היו אותם 80 מתכונים בכל 10 חגים, עכשיו 121 תיוגים יחודיים)
- v7.8 — הכפתור העליון "חגים" הוסר (כפול עם "חגים ומועדים" של מרוקו)
- v7.9 — "מרוקו" + "ספרד" אוחדו ל-"מרוקו\\ספרד" (מורשת קארו 1492)
- v8.0 — i18n מלא (תפריט עברי מתורגם לאנגלית בלחיצה אחת)

```
┌──────────┬─────────────────┬──────────────┬──────────┐
│  הכל     │  מרוקו\ספרד     │  עדות ישראל  │  לא כשר  │
│  1,054   │      744        │     270      │    40    │
└──────────┴─────────────────┴──────────────┴──────────┘

[הכל] → leaf (1,054 מתכונים)

[מרוקו\ספרד ▼] — 744 מתכונים (מרוקו 671 + ספרד 73)
├── כל מתכוני מרוקו וספרד (744)  ← multi-cat selector
├── מרקים (103) · סלטים (103) · תבשילי ירקות (87)
├── בשר וקציצות (82) · עוף ושבת (66) · דגים (70)
├── חגים ומועדים ▼ (80)
│   ├── כל מתכוני החגים (80)
│   ├── שבת (54) · ראש השנה (14) · יום כיפור (0)
│   ├── פסח (4) · מימונה (7) · חנוכה (2) · פורים (1)
│   └── שבועות (12) · סוכות (27) · חינה (14)
├── קינוחים ומאפים (80)
└── ספרד (אנדלוסי) (73)

[עדות ישראל ▼] — 9 עדות × 30 מתכונים = 270 (כולן באותו מבנה)
└── עיראק / כורדיסטן / אשכנז / תימן / פרס / בוכרה / טוניסיה / טורקיה / מטבח ישראלי
    ├── כל המתכונים (30)
    ├── מאכלים מסורתיים לעדה (1-8 לכל עדה)
    └── מאכלי חגים ▼ (תיקיה nested)
        └── שבת · ראש השנה · יום כיפור · פסח · חנוכה · פורים
            · שבועות · סוכות · חינה
            (מימונה לא קיימת — מסורת מרוקאית בלעדית)

[לא כשר ▼] — 40 מתכונים
```

**שינוי מהותי מ-v6.x:** בעבר היה wrapper יחיד "כל המתכונים" עם קינון של עד 4 רמות שהקשה על ניווט. ב-v8.0 — 4 קבוצות שטוחות ומקבילות, drawer אחיד עם עומק מקסימלי של 3 רמות (עדה → מאכלי חגים → חג ספציפי).

---

## קטגוריות (19)

### מטעמים של אמא ממרוקו (671 מתכונים)

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

### דף ראשי (v7.0 → v8.0)
- **Header מאוחד** — שם האתר + ספירת מתכונים בזמן אמת + שורת חיפוש ממורכזת + כפתורי כלים, max-width 1100px (v7.5)
- **Hero ממורכז עם 2 כפתורי CTA** — "עיון במתכונים" (מציג את כל 1,054) ו"קרא את הספר" (פותח את הספר)
- **סדר סקציות (v7.6):** Hero → Bio → Main (רשת) → Book → About
- **רשת מתכונים מוסתרת בטעינה (v7.1):** מופיעה רק אחרי לחיצה על קטגוריה, חיפוש, או CTA
- **ניווט שטוח (v7.9):** 4 קבוצות עליונות (הכל / מרוקו\\ספרד / עדות ישראל / לא כשר), עומק קינון מקסימלי 3 רמות
- **תיוג חגים אמיתי (v7.7):** כל אחד מ-10 חגי מרוקו מציג את המתכונים הנכונים שלו (במקום אותם 80 לכל חג)
- **חגים פר-עדה (v7.4):** כל עדה כוללת תיקיית "מאכלי חגים" עם 9 חגים (ללא מימונה — מסורת מרוקאית בלעדית)
- **i18n מלא (v8.0):** כל פריטי התפריט מתורגמים לאנגלית בלחיצה אחת על EN
- **light theme polish (v8.0):** כל classes חדשים של v7.x מקבלים overrides נכונים בנושא בהיר

### תרגום
- **עברית + אנגלית** — toggle מיידי, 2,853 ערכי מילון + 1,054 תרגומים מוכנים מראש
- תרגום morphological של כותרות, תיאורים, זיכרונות, טיפים, שלבים, מרכיבים

### PWA (Progressive Web App)
- **כפתור "התקן" בולט** בהדר (v6.3 — שוחזר) — pulse animation, מתחבא אחרי התקנה
- **iOS support** — הוראות הוספה למסך הבית אם הדפדפן לא תומך ב-`beforeinstallprompt`
- **Service Worker** — network-first למסמכים, cache-first לתמונות
- **offline mode** — האתר פועל גם בלי אינטרנט (מתוך cache)

### מערכת פידבק (v6.6+ — Web3Forms)
- **כפתור "הערה / תיקון"** בכל modal של מתכון
- **FAB צף** שמאלי-תחתון — "הצעות ודיווח"
- **שיטה: `fetch()` + JSON** → `https://api.web3forms.com/submit`
- **Access key ציבורי בכוונה** — `705d4207-c4a6-43a2-8fdc-d8e202bc6c9c` (alias אימייל, לא סוד)
- **CSP:** `connect-src 'self' https://api.web3forms.com;`
- Timeout + **fallback ל-mailto** אוטומטי אם משהו נכשל
- **היסטוריה:** v6.0-v6.2 Netlify Forms (נכשל ב-GH Pages), v6.3-v6.5 FormSubmit.co (CORS/403), v6.6+ Web3Forms (עובד)

### SEO (v8.0 — חדש)
- **`sitemap.xml`** — 6 URLs כולל primary (Netlify) + mirror (GitHub Pages) + 4 anchor URLs לסקציות עיקריות
- **`robots.txt`** — מצביע ל-sitemap, מאפשר crawling מלא
- **hreflang tags** — תמיכה במולטילינגווליזם he/en
- **JSON-LD schema** (קיים מ-v6.x) — Recipe schema לכל מתכון

### אבטחה
- **CSP מוחזק** (v6.6+) — רק מקורות מאושרים, `connect-src` כולל `api.web3forms.com` בלבד
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

### Deploy מ-PowerShell

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
git add .
```
```powershell
git commit -m "description"
```
```powershell
git push origin main
```

Netlify + GitHub Pages יפרוסו אוטומטית תוך 30-60 שניות.

---

## תיעוד טכני

| מסמך | גרסה | תיאור |
|------|-------|-------|
| `HLD_Perla_CookingBook.md` | 7.1 | High Level Design — ארכיטקטורה, תפריט (v7.0 flat 6-group), קטגוריות, חגים, תרגום, responsive, feedback, PWA |
| `LLD_Perla_CookingBook.md` | 7.1 | Low Level Design — CSS tokens, DOM IDs, 48+ פונקציות, filtered(), buildNav() v7.0, openM(), submitFeedback(), PWA IIFE |
| `INTEGRATION_GUIDE.md` | — | מדריך אינטגרציה של מערכת הפידבק (Web3Forms) |
| `PLAN_v7_0_HEBREW.md` | — | תוכנית v7.0 בעברית (מוגשמת) |
| `PLAN_v7_0_ENGLISH.md` | — | Handoff טכני ל-v7.0 (מוגשם) |
| `CHANGELOG_19-04-2026_v7_1.md` | — | v7.1 — הסתרת רשת מתכונים בטעינה (UX fix) |
| `CHANGELOG_19-04-2026_v7_0.md` | — | v7.0 — שיפוץ דף ראשי (flat 6-group nav, CTAs, reorder) |
| `CHANGELOG_19-04-2026_v6_3..v6_10.md` | — | שינויי סשנים v6.3-v6.10 |
| `CHANGELOG_download_images_v5.md` | — | שינויי download_images.py v5.1 |
| `download_images_usage_guide.md` | — | מדריך הרצת download_images.py v5.1 |
| `README_Recipe_CLI.md` | — | מדריך לסקריפטי Python — add_recipe.py, edit_recipe.py, recipe_utils.py |
| `CLAUDE.md` | 7.1 | הנחיות למפתחים/AI agents לעבודה על הפרויקט |

---

## היסטוריית גרסאות

| גרסה | תאריך | עיקרי השינויים |
|---|---|---|
| 5.0 | אפריל 2026 | בסיס — 1,054 מתכונים, 19 קטגוריות, תרגום מלא, PWA |
| 6.0 | 18/04/2026 | CSP מוחזק, favicons PNG, OG image, feedback system (Netlify Forms) |
| 6.1 | 18/04/2026 | הסרת r.img/-2/-3 מ-fallback (מונע 3,162 שגיאות/טעינה) |
| 6.2 | 18/04/2026 | 20 cat-*.jpg placeholders, `_headers` file, UI enlarge סיבוב 1 |
| 6.3 | 19/04/2026 | UI enlarge סיבוב 2, FormSubmit AJAX migration, PWA install button, content updates |
| 6.4 | 19/04/2026 | CORS fix — FormSubmit iframe approach |
| 6.5 | 19/04/2026 | FormSubmit `_url` field fallback + 404 gallery noise fix |
| 6.6 | 19/04/2026 | **הגירה מלאה מ-FormSubmit.co ל-Web3Forms** (פתר 403 לצמיתות) |
| 6.7 | 19/04/2026 | `.m-nav` sticky, חיצי גלריה ל-RTL, סקריפטי Python CLI (add/edit_recipe, recipe_utils) |
| 6.8 | 19/04/2026 | Hero tagline bold/white, base font 17px גלובלי, book_paragraph 1.02rem |
| 6.9 | 19/04/2026 | PWA install button תמיד נראה; Back-to-top משופר (48px, סף 300, בדיקה בטעינה) |
| 6.10 | 19/04/2026 | PWA install dialog ל-Custom Modal (הוסר ה-prefix "<origin> says") |
| **7.0** | **19/04/2026** | **שיפוץ דף ראשי — Header מאוחד, Hero עם CTAs, Main לפני Book, flat 6-group nav + Option C placeholder לחגי עדות. WEB3FORMS_KEY שוחזר.** |
| **7.1** | **19/04/2026** | **רשת מתכונים מוסתרת בטעינה — מופיעה רק אחרי פעולת משתמש (ניווט/חיפוש/CTA)** |

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
*"האוכל שלה — הסיפור שלנו"*
