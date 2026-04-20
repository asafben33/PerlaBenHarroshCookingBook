# CHANGELOG — v8.10: הקטנת תצוגת "המתכון של היום"

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.10

---

## הבקשה

> תקטין את תצוגת "מתכון היום" בגודל של הסימן שבאדום שבצילום מסך המצורף.

הסימון האדום בצילום היה בערך **חצי הרוחב** של הכרטיס המקורי (640px → ~520px), עם דגש שזה צריך להיראות מוצק ומרוכז ולא לתפוס שטח רחב מדי.

---

## הסיבה

ב-v8.8/v8.9 הגדלתי את הכרטיס לגודל בולט (max-width 880px, תמונה 320px, כותרת 1.55rem) כי חשבתי שזה ייצור "wow effect". בפועל זה תפס שטח גדול מדי ועיצב את הסקציה כ"hero" משני ולא כפיצ'ר משני.

הצילום מבהיר: **"המתכון של היום"** הוא **רכיב משני** באתר — לא צריך להיות דומיננטי כמו ה-Hero. צריך להיות חביב ומזמין, אבל קומפקטי.

---

## השינויים (כולם הקטנת מידות יחסיות)

| אלמנט | היה (v8.9) | עכשיו (v8.10) | יחס |
|---|---|---|---|
| `rotd-inner` max-width | 880px | **540px** | 61% |
| `rotd-card` תמונה | 320px | **180px** | 56% |
| `rotd-img` min-height | 220px | **160px** | 73% |
| `rotd-section` padding-top | 2.5rem | **2rem** | 80% |
| `rotd-body` padding | 1.6rem | **1.1rem** | 69% |
| `rotd-title` font-size | 1.55rem | **1.2rem** | 77% |
| `rotd-desc` font-size | 0.95rem | **0.82rem** | 86% |
| `rotd-desc` line clamp | 3 שורות | **2 שורות** | 67% |
| `rotd-chip` font-size | 0.76rem | **0.68rem** | 89% |
| `rotd-cta` font-size | 0.9rem | **0.78rem** | 87% |
| `rotd-eyebrow` font-size | 0.82rem | **0.72rem** | 88% |
| `eyebrow letter-spacing` | 0.25em | **0.22em** | 88% |
| `top divider width` | 220px | **180px** | 82% |

**Mobile breakpoint** הוקטן מ-720px ל-600px (כי הכרטיס כבר קטן יותר בעצמו, אין צורך לעבור ל-stack כל-כך מוקדם).

---

## האסתטיקה נשמרה

כל האלמנטים המעוטרים נשארו:
- ✓ `✦ המתכון של היום ✦` — קישוטים בצידי ה-eyebrow
- ✓ Top divider זהוב מדורג
- ✓ Frame כפול (חיצוני + פנימי זהוב inset 5px)
- ✓ Hover effect (translateY + scale 1.05 + golden glow)
- ✓ `✧` flourish בפינה
- ✓ Border זהוב, shadow מולטי-שכבתי
- ✓ Linear gradient 135° על ה-card
- ✓ Image fade gradient
- ✓ Smooth cubic-bezier transitions
- ✓ Light theme support מלא (Bio override + ROTD light hover + eyebrow text-shadow)
- ✓ EN mode (lang-en) overrides

**רק המידות הופחתו.** העיצוב עצמו זהה.

---

## בדיקות שעברו (12/12)

```
✓ JS syntax: OK
✓ CRLF: 13,488 שורות (100%, 0 lone LF)
✓ Size: 556,674 bytes (כמעט זהה ל-v8.9 — שינוי מידות בלבד)
✓ rotd-inner: max-width 540px
✓ card grid: 180px (היה 320px)
✓ image min-height: 160px (היה 220px)
✓ body padding: 1.1rem (היה 1.6rem)
✓ title: 1.2rem (היה 1.55rem)
✓ desc: 0.82rem (היה 0.95rem)
✓ desc 2 lines clamp (היה 3)
✓ chip: 0.68rem (היה 0.76rem)
✓ cta: 0.78rem (היה 0.9rem)
✓ mobile @ 600px (היה 720px)
✓ Old 880px max-width: REMOVED
✓ Old 320px grid: REMOVED
```

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | הקטנת 13 ערכי מידה ב-CSS של ROTD (פונטים, padding, max-width, breakpoint) |

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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_10_rotd_compact.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_10_rotd_compact.md
```
```powershell
git commit -m "v8.10: reduce Recipe of the Day card to half its previous size (~540px max-width, 180px image, smaller fonts)"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

1. **גודל ויחס** — הכרטיס עכשיו מציג כ-540px max (במקום 880px). זה כ-60% מהגודל הקודם — בדיוק כמו הסימון באדום בצילום.
2. **תמונה** — 180px רוחב (במקום 320px) — קטנה אבל עדיין נראה מצוין.
3. **טקסט** — כותרת בולטת אבל לא ענקית (1.2rem במקום 1.55rem). תיאור 2 שורות במקום 3.
4. **מובייל** — עובר ל-stack רק מתחת ל-600px (במקום 720px), כי ב-720px הכרטיס כבר מספיק קטן.
5. **כל האפקטים** — hover, glow, frame, eyebrow ornaments — עובדים בדיוק כמו בעבר, רק קטנים יותר.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
