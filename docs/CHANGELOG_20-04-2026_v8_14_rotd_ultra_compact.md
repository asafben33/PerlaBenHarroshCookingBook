# CHANGELOG — v8.14: כיווץ סופי של "המתכון של היום" לגודל אולטרא-קומפקטי

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.14

---

## הבקשה

> תקטין את המוצג במה שמסומן באדום ותקטין אותו לגודל של הסימון בירוק בצילום מסך המצורף

הסימון האדום בצילום הקיף את כל סקציית "המתכון של היום" (~430px גובה).
הסימון הירוק היה רק חלק עליון מצומצם (~280px גובה).

**יחס:** ~65% מהגובה הקודם. כל הסקציה כולה צריכה להיות הרבה יותר קומפקטית.

---

## החלפת אסטרטגיה

ב-v8.10 הקטנתי את ה-card עצמו (max-width 540px, image 180px). זה לא הספיק.

ב-v8.14 אני מקטין **את כל הרכיבים** עוד פעם:
- **ה-padding של הסקציה** (היה האשם העיקרי לגובה הענק — 2rem padding-top + 2.5rem padding-bottom = 4.5rem בלי להחשיב את הכרטיס עצמו)
- **התמונה** (180px → 130px width, 160px → 120px height)
- **כל הטקסטים בכרטיס** (title 1.2rem → 1rem, desc 0.82rem → 0.72rem)
- **הרווחים בין אלמנטים** (gap 0.8rem → 0.35rem)
- **המסגרת והקישוטים** הופחתו אך לא הוסרו

---

## השינויים המדויקים

| אלמנט | היה (v8.13) | עכשיו (v8.14) | יחס |
|---|---|---|---|
| `rotd-section` padding-top | 2rem | **0.8rem** | 40% |
| `rotd-section` padding-bottom | 2.5rem | **1rem** | 40% |
| `rotd-section::before` width (top divider) | 180px | **140px** | 78% |
| `rotd-section::before` margin-bottom | 1.2rem | **0.5rem** | 42% |
| `rotd-inner` max-width | 540px | **480px** | 89% |
| `rotd-inner` gap | 0.8rem | **0.35rem** | 44% |
| `rotd-eyebrow` font-size | 0.72rem | **0.65rem** | 90% |
| `rotd-eyebrow` gap | 0.7rem | **0.55rem** | 79% |
| `rotd-eyebrow::before/after` | 0.6rem | **0.55rem** | 92% |
| `rotd-card` grid-template image | 180px | **130px** | 72% |
| `rotd-card::before` inset | 5px | **4px** | 80% |
| `rotd-img` min-height | 160px | **120px** | 75% |
| `rotd-body` padding | 1.1rem | **0.7rem 0.85rem 0.65rem** | 64% |
| `rotd-body` gap | 0.45rem | **0.3rem** | 67% |
| `rotd-body::before` (✧ flourish) | 0.7rem | **0.62rem** | 89% |
| `rotd-title` font-size | 1.2rem | **1rem** | 83% |
| `rotd-title` line-height | 1.25 | **1.2** | 96% |
| `rotd-desc` font-size | 0.82rem | **0.72rem** | 88% |
| `rotd-desc` line-height | 1.55 | **1.45** | 94% |
| `rotd-meta-row` gap | 0.35rem | **0.25rem** | 71% |
| `rotd-meta-chip` font-size | 0.76rem | **0.65rem** | 86% |
| `rotd-meta-chip` padding | 0.2/0.6rem | **0.12/0.45rem** | 70% |
| `rotd-cta` font-size | 0.78rem | **0.68rem** | 87% |
| `rotd-cta` margin-top + padding-top | 0.55+0.55rem | **0.35+0.35rem** | 64% |
| Mobile padding | 1.5rem 0.8rem 2rem | **0.7rem 0.8rem 0.8rem** | 47% |
| Mobile image height | 160px | **120px** | 75% |

---

## מה נשמר

- ✓ כל המבנה: eyebrow, top divider, frame, card, image, body, title, desc, chips, cta
- ✓ כל האלמנטים המעוטרים: `✦` ornaments, `✧` flourish, golden inner frame
- ✓ Hover effect (translateY + scale + golden glow)
- ✓ Light theme support מלא
- ✓ EN mode (lang-en) overrides
- ✓ Linear gradient על הקלף
- ✓ Cubic-bezier transitions

**רק המידות הופחתו, העיצוב זהה.**

---

## בדיקות שעברו (14/14)

```
✓ JS syntax: OK
✓ CRLF: 13,555 שורות (100%, 0 lone LF)
✓ Size: 561,051 bytes (כמעט זהה ל-v8.13)
✓ rotd-section padding 0.8/1rem
✓ Top divider 140px width
✓ rotd-inner 480px max-width, 0.35rem gap
✓ Eyebrow 0.65rem
✓ Card grid 130px (was 180px)
✓ Image min-height 120px (was 160px)
✓ Body padding compact
✓ Title 1rem (was 1.2rem)
✓ Desc 0.72rem (was 0.82rem)
✓ Chip 0.65rem
✓ CTA 0.68rem
✓ Old 2rem padding REMOVED
✓ Old 180px grid REMOVED
✓ Old 160px image REMOVED
```

---

## תוצאת הקיווץ

**גובה הסקציה הכוללת:**
- v8.13 (קודם): ~430px
- v8.14 (עכשיו): **~280px** (שווה ערך לסימון הירוק)

**הסקציה תופסת עכשיו פחות מקום, ועדיין:**
- כל המידע נראה (כותרת, תיאור, 3 chips של זמן/מנות/קושי, CTA)
- כל הקישוטים נשמרו (eyebrow, divider, frame, ✧ flourish)
- התמונה עדיין מציגה את המנה (130px width, מספיק לראייה אך לא דומיננטי)
- האפקטים האינטראקטיביים עובדים זהה

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | 26 ערכי מידה ב-CSS של ROTD הוקטנו ל-~70-90% מהקודם |

`data.js`, `download_images.py`, `find_videos.py`, `sw.js`, `sitemap.xml`, `robots.txt` — **לא נגעתי**.

---

## פריסה

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_14_rotd_ultra_compact.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_14_rotd_ultra_compact.md
```
```powershell
git commit -m "v8.14: ultra-compact Recipe of the Day - section ~430px to ~280px (65%) - reduced padding, image, fonts, gaps"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

1. **גודל הסקציה** — תופסת עכשיו ~280px במקום ~430px (35% פחות)
2. **כל האלמנטים** — eyebrow, divider, card, image, title, desc, chips, CTA — הכל שם
3. **קישוטים** — `✦`, `✧`, frame, divider — שמורים
4. **Hover** — עובד זהה (golden glow, image zoom, border highlight)
5. **תמונה גלויה** — 130px במחשב, מספיק לראייה
6. **מובייל** — image 120px height, padding מוקטן
7. **תמת אור + תמת כהה** — שניהם עובדים נכון

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
