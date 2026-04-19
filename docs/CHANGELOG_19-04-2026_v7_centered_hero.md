# CHANGELOG — תיקון מיקום אלמנטים בדף הראשי + יישום v7.0 + v7.1

**תאריך:** 19/04/2026 (אחרי הצהריים)
**גרסה:** v7.0 + v7.1 (מיושמים יחד)

---

## רקע — מה הצילום הראה

המשתמש שלח צילום מסך של https://asafben33.github.io/PerlaBenHarroshCookingBook/ עם 3 חיצים אדומים (אלמנטים מוצמדים לימין במקום במרכז) וחץ ירוק אחד (כותרת ה-Bio שמוצגת נכון, באמצע).

**הבקשה:** "תסדר את המיקום של האלמנטים המסומנים בהתאמה לעיצוב שדרשתי במוקאפ ולנראות יפה של הדף."

**הפענוח:** ה-Hero (h1, tagline, CTAs) היה מוצמד לימין בגלל `margin-left: auto; margin-right: 0` ו-`text-align: right`. המוקאפ דורש שהוא יהיה במרכז כמו ה-Bio.

---

## השינויים שבוצעו

### 1. Hero — מרכוז (התיקון העיקרי לפי הצילום)

**CSS — שורות ~328-358:**
```diff
- .hero-inner { max-width: 760px; margin-left: auto; margin-right: 0; ... text-align: right; }
+ .hero-inner { max-width: 760px; margin: 0 auto; ... text-align: center; }
- .hero-h1 { ... text-align: right; }
+ .hero-h1 { ... text-align: center; }
- .hero-tagline { ... text-align: right; }
+ .hero-tagline { ... text-align: center; }
+ .hero-orn { ... text-align: center; }
```

**Hero h1 + tagline + CTAs** מופיעים כעת **באמצע הדף** מאותקה אופקית, כמו כותרת ה-Bio.

### 2. v7.0 — Header אחיד (`hdr-brand-v7`)

נוסף בלוק חדש לפני ה-search bar ב-HTML:

```html
<div class="hdr-brand-v7">
  <span class="hdr-brand-title">ספר הבישול של פרלה</span>
  <span class="hdr-brand-count"><span id="hdr-count">1,054</span> מתכונים</span>
</div>
```

**ספירת המתכונים מתעדכנת דינמית** מ-`R.length.toLocaleString()` ב-`initHdrCount()`. במסכים קטנים (≤640px) הספירה מוסתרת.

### 3. v7.0 — Hero CTAs (כפתורי קריאה לפעולה)

נוסף `.hero-cta-row` עם 2 כפתורים:

- **`#hero-cta-browse`** ("עיון במתכונים") — primary, רקע אדום-תבליני (`--c-spice`). לחיצה: סימולציה של לחיצה על ה-nav "הכל" → גילוי הרשת + scroll חלק ל-`#main`.
- **`#hero-cta-book`** ("קרא את הספר") — secondary, מסגרת זהובה. לחיצה: scroll חלק ל-`#book-wrapper`.

### 4. v7.0 — MENU_STRUCTURE שטוח (6 קבוצות עליונות)

ב-`data.js` הוחלף ה-MENU_STRUCTURE הישן (single wrapper "all_master" עם 4 רמות nested) ב-flat 6-group:

```
1. הכל (id:'all', leaf)
2. מרוקו (key:'morocco', 8 sub-items: soups, salads, veg, meat, chick, fish, hol, des)
3. ספרד (id:'span', leaf)
4. עדות ישראל (key:'communities', 9 עדות + Option C placeholder)
5. חגים (id:'hol', leaf)
6. לא כשר (id:'nonkosher', leaf)
```

**Option C** ("חגי העדות (בקרוב)") נשאר כ-`{placeholder:'communityHolidays'}` שמציג toast במקום למלא — אין תיוג חגי עדות עדיין.

### 5. v7.1 — הסתרת רשת מתכונים בטעינה

ב-HTML: `<main id="main" class="main-hidden" role="main" aria-hidden="true">`
ב-CSS: `.main-hidden { display: none !important; }`

ב-JS גלובליים: `window.showMainGrid()` / `window.hideMainGrid()`.

הרשת מתגלה כאשר:
- לחיצה על קטגוריה ב-nav (`selectCat`, `selectMulti`, `selectByIds`) → קוראים ל-`showMainGrid()`
- חיפוש (`doSearch` כש-`SEARCH` truthy) → קוראים ל-`showMainGrid()`
- לחיצה על "עיון במתכונים" ב-Hero → סימולציה של לחיצת nav

---

## מה בוצע ב-JS — סיכום

| Function/Object | מה עושה |
|---|---|
| `window.showMainGrid()` | מסיר `.main-hidden` מ-`#main`, מסיר `aria-hidden` |
| `window.hideMainGrid()` | מוסיף `.main-hidden` ל-`#main` |
| `window.initHdrCount()` | מעדכן `#hdr-count` עם `R.length.toLocaleString()` |
| `window.initHeroCTAs()` | מקשר handlers ל-`#hero-cta-browse` + `#hero-cta-book` |
| `selectCat` / `selectMulti` / `selectByIds` | קוראים ל-`showMainGrid()` כצעד ראשון |
| `doSearch` | קורא ל-`showMainGrid()` כש-SEARCH truthy |
| `buildPanel` | branch חדש ל-`item.placeholder` שמציג toast |
| `DOMContentLoaded` | קורא ל-`initHdrCount()` ו-`initHeroCTAs()` |

---

## בדיקות שעברו

```
✓ Main JS syntax (node -c): OK
✓ data.js syntax (node -c): OK
✓ CRLF: 12,759 lines, 0 lone LF
✓ Header brand element present
✓ Hero CTA row present
✓ v7.1 main-hidden class on <main>
✓ All 4 init/helper functions present
✓ Placeholder branch in buildPanel
✓ Hero h1 + hero-inner centered
```

---

## קבצים שונו

| קובץ | שינויים |
|---|---|
| `index.html` | CSS hero (מרכוז) + brand + CTA + main-hidden, HTML header brand + hero CTAs + main class, JS helpers + selectCat/Multi/ByIds + doSearch + buildPanel placeholder + DOMContentLoaded init |
| `data.js` | MENU_STRUCTURE שכתוב מלא — flat 6-group + Option C placeholder |

**לא שונו:** `pre_en.js`, `book_data.js`, `about_redesigned.*`, `sw.js`, `manifest.json`, סקריפטי Python.

---

## ספירה — הערה על הצילום

הצילום הראה "1,056 מתכונים" אבל ה-`data.js` ב-`/mnt/project/` (גרסה 6.10) מכיל **1,054 מתכונים מדויק**. ההפרש (2 מתכונים) קיים בגרסה הפרוסה ב-GitHub Pages אך לא ב-project knowledge. כשתעלה את `data.js` החדש, הספירה תהיה 1,054 (אלא אם הוספת 2 מתכונים מאוחר יותר ולא נשמרו לפרויקט). אם רוצה לשמור על 1,056, תעדכן את ה-data.js לפני העלאה.

---

## פריסה

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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_v7_centered_hero.md" ".\CHANGELOG_19-04-2026_v7_centered_hero.md" -Force
```
```powershell
git add index.html data.js CHANGELOG_19-04-2026_v7_centered_hero.md
```
```powershell
git commit -m "v7: center hero per mockup + flat 6-group nav + grid-on-demand"
```
```powershell
git push origin main
```

לאחר הפריסה (Netlify ~30s):
- ה-Hero יופיע **במרכז** הדף, כמו הכותרת של ה-Bio בצילום
- ב-header תופיע ספירת המתכונים מימין
- מתחת ל-Hero יופיעו 2 כפתורי CTA במרכז
- רשת המתכונים תוסתר בהתחלה ותתגלה רק אחרי לחיצה/חיפוש
- תפריט הניווט יציג 6 קבוצות שטוחות במקום ה-wrapper הישן

---

**לזכר פרלה ופנחס בן הראש ז״ל**
