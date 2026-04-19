# CHANGELOG — עדכון תיעוד ל-v7.1

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026
**סוג:** עדכון תיעוד בלבד (pure docs update)
**קוד:** ללא שינוי. רק 5 מסמכי markdown.

---

## רקע

לאחר פריסת v7.0 (שיפוץ דף ראשי) ו-v7.1 (הסתרת רשת בטעינה), התיעוד הטכני של הפרויקט היה עדיין בגרסה 6.3-6.4. המסמכים לא שיקפו:
- את המבנה החדש flat 6-group של MENU_STRUCTURE
- את סידור החלקים החדש (Main לפני Book)
- את כפתורי ה-CTA ב-Hero
- את `hdr-brand-v7` ואת ספירת המתכונים הדינמית
- את `showMainGrid()`/`hideMainGrid()` והתנהגות "רשת על פי דרישה"
- את המעבר ל-Web3Forms (v6.6) — עדיין תיעדו FormSubmit

## 5 מסמכים שעודכנו

### 1. `CLAUDE.md` — שכתוב מלא (197 שורות)

- Header גרסה: 6.10 → 7.1
- סעיף חדש: **"ארכיטקטורת ניווט — MENU_STRUCTURE (v7.0+)"** עם טבלת 6 הקבוצות העליונות והסבר על Option C
- סעיף חדש: **"v7.0 — שיפוץ דף ראשי"** עם 4 השינויים המבניים
- סעיף חדש: **"v7.1 — הסתרת רשת מתכונים בטעינה"**
- סעיף "אזהרות" עודכן — נוספו אזהרות על אל-שחזור מבנה v6.x
- סעיף "שינויים בסשנים" הורחב עם v6.5→v7.1
- סעיף מערכת פידבק עודכן — מפתח Web3Forms נכתב במפורש
- ספירת מתכונים לפי קטגוריה נוספה (671 מרוקו, 270 עדות, וכו')

### 2. `README.md` — עדכונים ממוקדים (361 שורות)

- Header גרסה: 6.4 → 7.1
- **תרשים MENU_STRUCTURE** נכתב מחדש — flat 6-group במקום single wrapper
- **תיקון מספר קריטי:** 744 מרוקו → 671 (זה היה שגוי גם ב-v6.x)
- סעיף **"דף ראשי (v7.0 + v7.1)"** חדש בתחת "חוויית משתמש"
- מערכת פידבק עודכנה מ-FormSubmit+iframe ל-Web3Forms
- CSP: `formsubmit.co` → `api.web3forms.com`
- טבלת "פריסה" ללא שלב activation של FormSubmit
- טבלת "תיעוד טכני" עם PLAN docs ו-CHANGELOG v7.0/v7.1
- רשימת קבצים עם סקריפטי Python + PLAN docs + v7.x changelogs
- טבלת "היסטוריית גרסאות" הורחבה מ-6.4 ל-7.1 (הוספו 8 שורות)

### 3. `HLD_Perla_CookingBook.md` — עדכונים ממוקדים (764 שורות)

- Header גרסה: 6.4 → 7.1
- טבלת meta: 6.4 → 7.1
- **סעיף 4 (ארכיטקטורת ניווט)** נכתב מחדש:
  - טבלה מסכמת של 6 הקבוצות עם סוג/keys/ids/מתכונים/עומק
  - תת-סעיף חדש: "Option C — חגי העדה (v7.0)"
  - **4.1 תרשים ניווט מלא** — flat 6-group חדש
  - **4.2 buildNav() v7.0** — הסבר על הפונקציה המחודשת (14205→8162 chars)
  - **4.3 הסתרת רשת בטעינה (v7.1)** — 4 נקודות כניסה לגילוי
- **סעיף 9 (מערכת פידבק)**: Header שונה ל-"v6.6+ (Web3Forms)" עם הערה בתחילה על המעבר מ-FormSubmit

### 4. `LLD_Perla_CookingBook.md` — עדכונים ממוקדים (1,806 שורות)

- Header גרסה: 6.4 → 7.1
- טבלת meta: 6.4 → 7.1
- **סעיף 4.1 (DOM IDs)** הורחב — נוספו: `hdr-count`, `hero-cta-browse`, `hero-cta-book`, `main` (עם class="main-hidden"), הערות על סדר החלקים החדש
- **סעיף 5.4 (buildNav)** עודכן — תיאור v7.0 עם 42% הפחתה, תוספת `showMainGrid()` לכל select functions
- **סעיף 5.5 (renderItem)** חדש — החליף את 5.5 הישן (buildPanel): 6 branches (כולל placeholder)
- **סעיף 5.6 (showMainGrid/hideMainGrid)** חדש — תיאור הפונקציות הגלובליות של v7.1 ו-5 נקודות הקריאה
- **סעיף 6 (MENU_STRUCTURE)** נכתב מחדש:
  - 6.1 רמה עליונה (טבלת 6 nodes)
  - 6.2 Morocco מפרט מלא
  - 6.3 Communities + Option C placeholder
  - 6.4 Holidays (10 חגים)
  - 6.5 פונקציות select עם v7.1 side effects
  - 6.6 buildNav v7.0 iteration model
- **סעיף 20 חדש** — "שינויים v6.x → v7.1" — 6 תת-סעיפים:
  - 20.1 v7.0 Homepage Redesign (4 שינויים A-D)
  - 20.2 v7.1 הסתרת רשת — CSS/HTML/JS
  - 20.3 שינויים ב-data.js (MENU_STRUCTURE diff)
  - 20.4 שינויים ב-pre_en.js (אין)
  - 20.5 אבטחה / WEB3FORMS_KEY
  - 20.6 טבלת סיכום שינויים בקבצים
- **סעיף 21 (מפת התיעוד)** — טבלה מעודכנת עם PLAN docs ו-v7.x CHANGELOGs

### 5. `INTEGRATION_GUIDE.md` — שכתוב מלא (260 שורות, ירידה מ-604)

- Header גרסה: 3.0 → **4.0** (שינוי major)
- **נכתב מחדש לגמרי** עבור Web3Forms:
  - סעיף 2 (ארכיטקטורה) — `fetch()` + JSON, response format, המפתח הציבורי
  - סעיף 3 (קבצים) — מה השתנה מ-v3.0 (אין יותר hidden form/iframe/base64)
  - סעיף 4 (הגדרה) — אין שלב activation
  - סעיף 5 (בדיקות) — 6 בדיקות חדשות ל-Web3Forms
  - סעיף 6 (edge cases) — טבלה של 10 תרחישים
  - סעיף 7 (תחזוקה) — domain whitelist, auto-response, webhooks
  - סעיף 8 (fallback mailto) — בלי שינוי משמעותי
  - **סעיף 9 (היסטוריה)** — טבלה של 5 גרסאות (v1.0 → v4.0) + הסבר למה FormSubmit נכשל + 3 סיבות למה Web3Forms עובד
  - סעיף 10 (נושא ידוע) — WEB3FORMS_KEY ריק ב-v6.10 שוחזר ב-v7.0
- **הוסר:** כל התיעוד על FormSubmit activation, iframe mechanics, CORS workarounds, base64 obfuscation

## מסמכים **שלא עודכנו** (במכוון)

- **`README_Recipe_CLI.md`** — מדריך לסקריפטי Python (add_recipe.py, edit_recipe.py, recipe_utils.py). לא השתנה מ-v6.7 ואין בו מידע על הדף הראשי.
- **CHANGELOG ישנים (v6.3 עד v6.10)** — היסטוריה נצורה, אין טעם לגעת.
- **PLAN_v7_0_HEBREW.md** + **PLAN_v7_0_ENGLISH.md** — תוכניות היסטוריות (מוגשמות). נשמרים כרקורד של למה וכיצד v7.0 הוחלט.
- **`download_images_usage_guide.md`** + **`CHANGELOG_download_images_v5.md`** — לא מושפעים.

## בדיקות שבוצעו

- ✓ Header "גרסה 7.1" בכל 4 מסמכי הליבה
- ✓ אין הפניות לארכיטקטורה ישנה (single wrapper "all_master")
- ✓ אין הפניות ל-FormSubmit.co (חוץ מסעיפי היסטוריה)
- ✓ תאריך 19/04/2026 בכל המסמכים

## פריסה

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CLAUDE.md" ".\CLAUDE.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\README.md" ".\README.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\HLD_Perla_CookingBook.md" ".\HLD_Perla_CookingBook.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\LLD_Perla_CookingBook.md" ".\LLD_Perla_CookingBook.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\INTEGRATION_GUIDE.md" ".\INTEGRATION_GUIDE.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_docs_v7_1.md" ".\CHANGELOG_19-04-2026_docs_v7_1.md" -Force
```
```powershell
git add CLAUDE.md README.md HLD_Perla_CookingBook.md LLD_Perla_CookingBook.md INTEGRATION_GUIDE.md CHANGELOG_19-04-2026_docs_v7_1.md
```
```powershell
git commit -m "docs: Update all documentation to v7.1 - flat 6-group nav, grid-on-demand, Web3Forms"
```
```powershell
git push origin main
```

**הערה:** עדכון זה **לא משנה את הקוד של האתר** — רק את מסמכי הטקסט. האתר ימשיך לפעול כפי שהוא, והמסמכים יתעדכנו להשקף את המציאות.

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
