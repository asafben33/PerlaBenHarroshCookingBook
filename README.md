<div dir="rtl">

# ספר הבישול של משפחת בן הראש
### לזכרם של פרלה ופנחס בן הראש שזכרונם יהיה לברכה וגאווה לדורי דורות דרך הטעם המעלה זכרונות שחשבנו שכבר שכחנו...

---

## על הפרויקט

פרלה נולדה בקזבלנקה, גדלה במרקש, ועלתה לישראל עם לב מלא בטעמים ובסיפורים.
נישאה לפנחס, איש ממשפחת קארו — צאצאי **רבי יוסף קארו**, מגורשי קסטיליה 1492.
המטבח שלה שילב שני עולמות: **מרוקו העמוקה** ו**ספרד האנדלוסית**, ומאכלים שלמדה משכנים וחברים שתמיד עטפו אותה באהבה וחום.

עם העלייה לישראל הגיעו לשכונת הקטמון בירושלים. שם, בין שכנות מעיראק, כורדיסטן, אשכנז, תימן, פרס ובוכרה — הפך מטבחה לפסיפס שלם.

> *"ספר הבישול של משפחת בן הראש — דרך הטעם המעלה זכרונות שחשבנו שכבר שכחנו..."*

---

## כתובות האתר

| סביבה | כתובת |
|-------|-------|
| **Netlify (ראשי)** | https://perlabenharrosh-cookingbook.netlify.app/ |
| **GitHub Pages** | https://asafben33.github.io/PerlaBenHarroshCookingBook/ |
| **GitHub Repo** | https://github.com/asafben33/PerlaBenHarroshCookingBook.git |

---

## סטטיסטיקות (v7)

| מאפיין | ערך |
|--------|-----|
| מתכונים | **1,054** (1,014 רגילים + 40 לא כשרים) |
| קטגוריות קולינריות | **20** (כולל nonkosher) |
| ערכי TITLE_QUERIES בסקריפט | **~600** |
| גודל index.html | **178 KB** (לוגיקה בלבד) |
| גודל data.js | **1,400 KB** (נתונים) |
| תלויות חיצוניות | **0** (רק Google Fonts) |
| Service Worker | **כן** — עבודה offline |
| PWA Manifest | **כן** — ניתן להתקנה |
| תמיכה בשפות | **עברית + אנגלית** (UI) |

---

## מבנה הפרויקט

```
PerlaBenHarroshCookingBook/
├── index.html              ← SPA — HTML + CSS + JS (178 KB)
├── data.js                 ← 1,054 מתכונים + קטגוריות + תפריט + חגים (1,400 KB)
├── sw.js                   ← Service Worker — cache offline
├── manifest.json           ← PWA manifest
├── wedding.jpg             ← תמונת חתונה פרלה ופנחס (29 KB)
├── download_images.py      ← סקריפט הורדת תמונות (SHA256 dedup)
├── images/                 ← תמונות מורדות (r-{id}.jpg)
├── logs/                   ← לוגים: download_images_YYYY-MM-DD_HH.MM.log
├── HLD_Perla_CookingBook.docx   ← High Level Design
├── LLD_Perla_CookingBook.docx   ← Low Level Design
└── README.md               ← מסמך זה
```

---

## התקנה והפעלה

### צפייה מקומית
```bash
# שרת מקומי (נדרש ל-Service Worker)
python -m http.server 8000
# פתח http://localhost:8000
```

### הורדת תמונות
```bash
# הורדה מלאה + ניקוי כפילויות
python download_images.py

# בלי proxy (חיבור ביתי)
python download_images.py --no-proxy

# רק dedup (ללא הורדה)
python download_images.py --skip-download

# תצוגה מקדימה
python download_images.py --dry-run
```

### פריסה
```bash
git add index.html data.js sw.js manifest.json wedding.jpg download_images.py
git commit -m "update"
git push
# Netlify מתעדכן אוטומטית
```

---

## פיצ'רים

### חיפוש וסינון
- **חיפוש חופשי** — חיפוש מורפולוגי עברי (מנרמל סופיות, מזהה תחיליות ב/ה/ו/כ/ל/מ/ש)
- **סינון לפי רמת קושי** — קל / בינוני / מתקדם
- **סינון לפי זמן הכנה** — עד 30 דקות / שעה / שעתיים / מעל שעתיים
- **ניווט קטגוריות** — dropdown עם תת-קטגוריות, חגים, ומטבחי שכנות

### מצב חשוך/בהיר
- כפתור ☀/🌙 בפינת ה-header
- 42 כללי CSS מותאמים למצב בהיר
- הבחירה נשמרת ב-localStorage

### תרגום לאנגלית
- כפתור EN/HE בפינת ה-header
- 27 מחרוזות UI מתורגמות (header, hero, כפתורים, modal, footer)
- תוכן המתכונים נשאר בעברית (מורשת אותנטית)

### טיימר בישול
- כפתור "התחל X'" ליד כל שלב עם זמן
- widget צף עם ספירה לאחור (דקות:שניות)
- צליל + הודעה בסיום הטיימר

### הדפסה וייצוא PDF
- **הדפסת מתכון בודד** — כפתור 🖨 במודל, תבנית מעוצבת עם תמונה, מרכיבים, שלבים
- **ייצוא PDF של מתכון** — כפתור 📄, פותח הדפסה > "שמור כ-PDF"
- **ספר בישול שלם** — כפתור 📖 בפוטר, מייצר את כל 1,054 המתכונים עם תוכן עניינים
- **@media print** — CSS מלא להדפסה ישירות מהמודל

### ניהול מדיה
- העלאת תמונות מקומיות (localStorage, base64)
- הוספת/מחיקת סרטוני YouTube
- שיתוף מתכון (Web Share API / העתקת קישור)

### PWA ועבודה Offline
- Service Worker (`sw.js`) — cache-first ל-shell, network-first לתמונות
- Manifest (`manifest.json`) — ניתן להתקנה כאפליקציה
- עובד ללא חיבור אינטרנט אחרי טעינה ראשונה

---

## קטגוריות מתכונים

### מרוקאי (577 מתכונים)
מרקים (103) · סלטים (103) · ירקות (87) · בשר (82) · עוף (66) · דגים (70) · חגים (80) · קינוחים (80)

**חגים ומועדים:** שבת · ראש השנה · יום כיפור · פסח · מימונה · חנוכה · פורים · שבועות · סוכות · חינה

### ספרדי-מרוקאי וס"ט (73 מתכונים)
מרקים · בשר · דגים · ירקות · שבת וחגים · רטבים · מאפים · קינוחים

### שכנות הקטמון (270 מתכונים)

| קהילה | מתכונים |
|-------|---------|
| עיראק | 30 |
| כורדיסטן | 30 |
| אשכנז | 30 |
| תימן | 30 |
| פרס | 30 |
| בוכרה | 30 |
| טוניסיה | 30 |
| מטבח ישראלי | 30 |
| יהדות טורקיה | 30 |

### מתכונים לא כשרים (40 מתכונים)
- פירות ים ודגים לא כשרים (9)
- בשר וחלב (31)

---

## ארכיטקטורה

### מבנה קבצים

| קובץ | תפקיד | גודל |
|-------|--------|------|
| `index.html` | HTML + CSS + JS (לוגיקה, UI, אירועים) | 178 KB |
| `data.js` | CATS, R[], HOLIDAY_TAGS, MENU_STRUCTURE | 1,400 KB |
| `sw.js` | Service Worker — cache strategy | 2 KB |
| `manifest.json` | PWA manifest | 0.5 KB |
| `wedding.jpg` | תמונת חתונה (embedded base64 ב-about) | 29 KB |

### Global State (index.html)

| משתנה | ברירת מחדל | תיאור |
|-------|-----------|-------|
| `ACT_CAT` | `'all'` | קטגוריה פעילה |
| `ACT_CATS` | `[]` | קטגוריות multi-select |
| `ACT_IDS` | `null` | `Set<string>` — סינון לפי מזהי מתכון |
| `ACT_HOLIDAY` | `null` | חג פעיל |
| `ACT_DIFF` | `'all'` | סינון רמת קושי |
| `ACT_TIME` | `'all'` | סינון זמן הכנה |
| `SEARCH` | `''` | חיפוש חופשי |
| `_LANG` | `'he'` | שפת ממשק (he/en) |

### שרשרת Fallback תמונות

```
1. localStorage (משתמש העלה תמונה)
2. images/r-{id}.jpg (הורד ע"י download_images.py)
3. r.img (loremflickr — חלקי)
4. CAT_IMG (Wikimedia Commons — לפי קטגוריה)
5. כפתור העלאת תמונה (placeholder)
```

### Data Structures (data.js)

| מבנה | תיאור |
|------|-------|
| `CATS[]` | 20 קטגוריות {id, lbl} |
| `R[]` | 1,054 מתכונים {id, cat, title, desc, time, serv, diff, img, src, vid, mem, ingr[], steps[], tip} |
| `HOLIDAY_TAGS{}` | 10 חגים → מערכי מזהי מתכונים |
| `MENU_STRUCTURE[]` | 5 פריטים עליונים: all, moroccan, span, katamon, nonkosher |

### ניהול מדיה (localStorage)

| מפתח | מבנה | תיאור |
|-------|------|-------|
| `perla_media_{id}` | `{imgs:[base64], vids:[url]}` | תמונות וסרטונים למתכון |
| `perla_vid_del_{id}` | `'1'` | סימון מחיקת סרטון |
| `perla_favs` | `[id1, id2, ...]` | מועדפים |
| `perla_theme` | `'dark'`/`'light'` | ערכת צבעים |
| `perla_lang` | `'he'`/`'en'` | שפת ממשק |

---

## סקריפט הורדת תמונות (download_images.py)

### מקורות תמונה (סדר עדיפות)
1. **Hebrew** — Wikimedia Commons בחיפוש עברי
2. **TheMealDB** — API חינמי לתמונות אוכל
3. **Wikimedia** — Wikimedia Commons בחיפוש אנגלי
4. **Openverse** — תמונות CC חופשיות
5. **Wikipedia** — תמונות מתוך ערכי ויקיפדיה
6. **DuckDuckGo** — scraping תמונות כמוצא אחרון
7. **Loremflickr** — placeholder אחרון

### Dedup (ניקוי כפילויות)
- **בזמן הורדה:** SHA256 hash index — אם תמונה זהה כבר קיימת, נוצר Hard Link
- **שלב 2 (post-download):** סריקת כל images/ לפי SHA256, איחוד כפילויות
- **מונה hard-links:** מוצג בפלט ההתקדמות

### הגנות מפני תקיעה
| שכבה | מנגנון | timeout |
|------|--------|---------|
| Socket global | `socket.setdefaulttimeout(5)` | 5s |
| Per-request | `timeout=(3, 8)` | connect 3s, read 8s |
| Per-source | `_call_with_timeout(fn, 10)` daemon thread | 10s |
| Per-recipe | recipe total > 45s → skip | 45s |
| Emergency | Ctrl+C → `os._exit(0)` | מיידי |

### פלט
```
  >> [  25/1054]   2% [f1] "moroccan spicy fish"
     OK via wikimedia (0.6s)
  === 2% (25/1054) ok=25 fail=0 links=3 | ETA 51min | hebrew=3 wikimedia=20 ===
```

---

## אבטחה

| אמצעי | פירוט |
|-------|-------|
| CSP | `script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-src 'none'; object-src 'none'` |
| XSS | פונקציות `esc()`, `setText()` — אין innerHTML עם קלט משתמש |
| Referrer | `no-referrer` |
| Content-Type | `nosniff` |
| External links | `noopener noreferrer` |

---

## נגישות (WCAG 2.1)

- 32 `aria-label` attributes
- 27 `role` attributes
- Skip link לתוכן ראשי
- Focus trap במודל
- `prefers-reduced-motion` — כיבוי אנימציות
- ניגודיות צבעים: זהב על כהה (יחס > 4.5:1)
- מקלדת: Escape סוגר מודל, חצים לניווט, Tab ממוקד

---

## היסטוריית גרסאות

| גרסה | תאריך | שינויים |
|-------|--------|---------|
| v1 | — | אתר ראשוני עם 1,045 מתכונים inline |
| v2 | — | תיקוני באגים: back-top, CSP, Schema URL, recipe count |
| v3 | — | סנכרון data.js, 1,054 מתכונים, nonkosher category |
| v4 | — | תמונת חתונה, פירוק מתכונים ארוזים, תיקון כפילויות |
| v5 | — | פיצול index.html + data.js, מחיקת קוד מת (G/IMG/KW), nonkosher בתפריט |
| v6 | — | Service Worker, חיפוש מתקדם (זמן), הדפסה/PDF, Lighthouse fixes |
| v7 | אפריל 2026 | ספר בישול שלם PDF, מצב בהיר/חשוך, טיימר בישול, תרגום אנגלית, isr+turk בשכנות הקטמון, SHA256 dedup |

---

## תיקוני באגים שבוצעו

| # | באג | תיקון |
|---|-----|-------|
| 1 | כפתור "חזרה למעלה" לא מופיע | CSS class `visible`→`on`, הסרת `hidden` attribute |
| 2 | `getRecipeImg()` מתעלם מ-`r.img` | נוסף לשרשרת fallback |
| 3 | onerror בכרטיסים מנסה loremflickr שוב | הוחלף ב-fallback chain |
| 4 | מספר מתכונים שגוי (1,045 במקום 1,054) | תוקן בכל המקומות |
| 5 | Schema.org URL מפנה ל-github.io | תוקן ל-netlify |
| 6 | CSP `connect-src 'none'` | שונה ל-`'self'` |
| 7 | Print CSS `.back-top` (class) | תוקן ל-`#back-top` (id) |
| 8 | `HOLIDAY_TAGS` הוכרז פעמיים | כפילות הוסרה |
| 9 | `MENU_STRUCTURE` הוכרז פעמיים | כפילות הוסרה |
| 10 | 3 מתכונים עם מרכיבים ארוזים | פורקו ל-11-13 מרכיבים |
| 11 | 40 מתכוני nk_ חסרים ב-data.js | נוספו עם קטגוריית nonkosher |
| 12 | 9 מתכונים חדשים חסרים ב-index.html | סונכרנו מ-data.js |
| 13 | Dedup לפי גודל קובץ (לא מדויק) | הוחלף ל-SHA256 hash |
| 14 | download_images.py נתקע | Thread timeouts + per-recipe 45s limit |
| 15 | isr/turk כלשוניות נפרדות | הועברו לשכנות הקטמון |

---

*לזכר משפחת בן הראש — קזבלנקה · מרקש · ירושלים*
*"האוכל שלה — הסיפור שלנו"*

</div>
