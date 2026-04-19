# CHANGELOG — v7.5: מרכוז רצועות header + nav

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026 — לילה
**גרסה:** 7.5

---

## הבקשה

> תמרכז את מה שמסומן באדום בצילום מסך כך שיראה בהתאם לכל שאר התוכן

---

## הניתוח

הצילום הראה שהשורה העליונה (header + nav) **נמתחת לכל רוחב המסך** (מקצה ימין לקצה שמאל), בעוד שכל התוכן למטה (Hero, Bio, About) מרוכז ב-עמודה צרה (760-860px). זה יוצר חוסר הרמוניה: ה-brand מופיע בקצה הקיצוני ימין, ה-tools בקצה הקיצוני שמאל, וקטגוריות הניווט פזורות לאורך כל המסך.

החץ האדום הצביע על האיזון הנדרש: **הרצועה העליונה צריכה להיות באותו רוחב כמו התוכן** — ממורכזת אופקית עם רוחב מקסימום סביר.

---

## התיקון

3 selectors שונו מ-`max-width: 1440px` ל-`max-width: 1100px`:

| selector | תפקיד | רוחב לפני | רוחב אחרי |
|---|---|---|---|
| `.hdr-inner` | container של brand + search + tools | 1440px | **1100px** |
| `.cat-nav-inner` | container של 6 כפתורי הקטגוריה | 1440px | **1100px** |
| `.nav-panel-inner` | container של תפריט המשנה הנפתח | 1440px | **1100px** |

**למה 1100 ולא 760 (כמו Hero)?**
- 760 צר מדי ל-6 כפתורי קטגוריה + brand + search + 3 tools
- 1100 הוא תוצר ביניים שמכיל את הכל בצורה נוחה תוך שמירה על מרכוז יחסי
- במסכים קטנים (`<1100px`) ה-`max-width` לא משפיע — הרצועה תופסת את כל המסך

נוסף גם `justify-content: center` ל-`.cat-nav-inner` כדי לוודא שכפתורי הקטגוריה מרוכזים גם כשהם פחות מ-1100px ברוחב הכולל.

---

## בדיקות שעברו

```
✓ index.html JS syntax (node -c): OK
✓ CRLF: 12,918 שורות (100%, 0 lone LF)
✓ אין יותר max-width: 1440 ב-header/nav
✓ כל 3 ה-selectors שונו ל-1100px
```

---

## קבצים שונו

| קובץ | שינוי |
|---|---|
| `index.html` | 3 שינויי CSS (CSS בלבד, אין שינוי JS) |

`data.js` לא השתנה מ-v7.4 — אם כבר עידכנת אותו, אל תעדכן שוב.

---

## פריסה

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" ".\index.html" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_v7_5_centered_header_strip.md" "." -Force
```
```powershell
git add index.html CHANGELOG_19-04-2026_v7_5_centered_header_strip.md
```
```powershell
git commit -m "v7.5: center header + nav strips at 1100px (was 1440px) to align with content"
```
```powershell
git push origin main
```

---

## אחרי הפריסה (Netlify ~30s)

הרצועה העליונה (header + nav) תופיע כעת **ממורכזת בעמודה אופקית** ברוחב 1100px:
- שם הספר ("ספר הבישול של פרלה" + ספירה) יופיע בצד ימין של הרצועה הממורכזת
- שורת חיפוש במרכז
- כפתורי כלים (התקן/⊙/EN) בצד שמאל של הרצועה
- 6 קטגוריות ניווט פזורות לאורך אותה עמודה

הכל יראה מאוזן ויחיד עם התוכן למטה — ולא יותר נמתחים על קצוות המסך.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
