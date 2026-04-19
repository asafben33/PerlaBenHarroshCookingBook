# CHANGELOG — שלב 2: `audit_recipes.py` (סקריפט ביקורת אוטומטי)

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026
**גרסה:** 1.0 (v1 של סקריפט הביקורת)
**סטטוס שלבים:** שלב 1 (v7.0+v7.1) ✓ יושם · שלב 2 (הסקריפט) ✓ יושם · שלב 3 (תיקון מתכונים ספציפיים) ⊘ לא התחיל

---

## סקירה

שלב 2 לפי `PLAN_v7_0_*.md`: יצירת סקריפט Python שסורק אוטומטית את כל 1,054 המתכונים ב-`data.js` ומסמן בעיות מכניות לטריאז' ידני. **הסקריפט אינו מתקן אוטומטית** — בהתאם להעדפה שלך (#16 ב-`userPreferences`: "Do not create automated fix scripts... unless specifically requested").

הסקריפט הוא *audit* לא *fix*. הוא מייצר 3 דוחות נגישים (JSON/CSV/Markdown) שמאפשרים לך לקבל החלטות מושכלות על מה לתקן ובאיזה סדר.

## מה יש בסקריפט

### 16 בדיקות אוטומטיות בשלוש רמות חומרה

**🔴 HIGH (שובר ממשק):**
1. שדות חובה חסרים (title, desc, time, serv, diff, ingr, steps)
2. קטגוריה לא ידועה
3. מזהי מתכון כפולים

**🟡 MEDIUM (בעיות תוכן):**
4. ערך קושי לא תקני (לא אחד מ: קל, בינוני, קשה)
5. מעט מדי מרכיבים (ברירת מחדל < 3)
6. מעט מדי שלבים (ברירת מחדל < 2)
7. שלבים קצרים מאוד (ברירת מחדל < 20 תווים)
8. כמויות ריקות או מעורפלות ("חופן" בלי גודל, "כמות")
9. טקסט עברי חסר (recipe שחסרה בו עברית לחלוטין)
10. Placeholder text (TODO, FIXME, [לעדכן], ?????)

**🟢 LOW (זוטות):**
11. תיאור קצר מדי (< 30 תווים)
12. הערת זיכרון חסרה או קצרה
13. טיפ חסר
14. זמן לא מפוענח או חריג (< 5 דקות או > 12 שעות)
15. מספר מנות חריג
16. שם קובץ תמונה לא תואם לקונבנציה (אופציונלי — כבוי כברירת מחדל)

### 3 פורמטי פלט

- **JSON** (`audit_report_DD-MM-YYYY_HH.MM.json`) — machine-readable, כולל סטטיסטיקות + פירוט בעיות
- **CSV** (`audit_report_DD-MM-YYYY_HH.MM.csv`) — UTF-8 BOM לפתיחה ב-Excel, מיון ופילטור לפי עמודה
- **Markdown** (`audit_report_DD-MM-YYYY_HH.MM.md`) — סיכום לקריאה אנושית עם טבלאות

### CLI flags

```
--data PATH             # נתיב ל-data.js (ברירת מחדל: ./data.js)
--dry-run               # סריקה ללא כתיבת קבצי דוח
--out-dir DIR           # תיקיית פלט (ברירת מחדל: ./audit_reports/)
--only-category CAT     # סרוק קטגוריה יחידה
--severity high|medium|low|all   # פילטר חומרה
--min-ingr N            # סף מרכיבים (ברירת מחדל: 3)
--min-steps N           # סף שלבים (ברירת מחדל: 2)
--min-step-len N        # סף אורך שלב בתווים (ברירת מחדל: 20)
--min-desc-len N        # סף אורך תיאור (ברירת מחדל: 30)
--min-mem-len N         # סף אורך זיכרון (ברירת מחדל: 20)
--skip-tip-check        # דלג על בדיקת שדה tip
--include-image-check   # הפעל בדיקת שמות תמונות (off כברירת מחדל — אין ערך רב)
--no-rtl-fix            # בטל RTL fix לטרמינלים מודרניים
```

## תוצאות הרצה ראשונה (19/04/2026 19:38)

```
סה"כ מתכונים:           1054
מתכונים עם בעיות:       485 (46.0%)
סה"כ בעיות סומנו:       688

🔴 HIGH   (חובה לתקן):     0
🟡 MEDIUM (תוכן):         671
🟢 LOW    (זוטות):         17
```

### פירוט הבעיות לפי קוד

| קוד | חומרה | מופעים | הסבר |
|---|---|---|---|
| `short_step` | 🟡 | 593 | שלב קצר מ-20 תווים |
| `bad_difficulty` | 🟡 | 73 | "מתקדם" במקום קל/בינוני/קשה |
| `unparseable_serv` | 🟢 | 9 | `serv` לא מכיל מספר |
| `suspicious_time` | 🟢 | 8 | זמן ארוך מ-12 שעות (כולם תקינים — ייבוש/החמצה) |
| `vague_quantity` | 🟡 | 3 | כמות ללא יחידה |
| `few_steps` | 🟡 | 2 | פחות מ-2 שלבים |

### ממצאים חשובים

**✓ אפס HIGH**: כל 1,054 המתכונים בעלי שדות חובה מלאים, קטגוריות תקינות, ואין מזהים כפולים. **הקובץ נקי ברמת המבנה.**

**⚠ 73 ערכי "מתקדם" במקום "קשה"**: בעיה שיטתית — כנראה שמתישהו הוחלף ה-label ב-CSS/HTML מ-"קשה" ל-"מתקדם", אבל נשאר ב-data.js המקורי כ-"מתקדם". זה מתאים לתיקון אוטומטי (אבל לא דרך הסקריפט — אם רוצה, אעדיף על אפשרות עתידית).

**⚠ 593 שלבים קצרים מ-20 תווים**: לא בהכרח בעיה — שלבים כמו "מגררים כרוב דק." (15 תווים) הם תקינים. הסף הוא heuristic. אתה יכול לפתוח את ה-CSV למיין לפי `code=short_step`, ולהחליט איזה מתכונים באמת צריכים הרחבה.

**✓ 8 "זמן ארוך"**: אלה false positives — מתכונים של המלחת דגים, כבישה, תימון. הסקריפט סימן מדריך אבל זה בסדר.

## קבצים חדשים

| קובץ | גודל | תוכן |
|---|---|---|
| `audit_recipes.py` | ~23 KB / ~830 שורות | הסקריפט עצמו |
| `audit_reports/` | תיקייה חדשה | ג'נרטד — מכיל את הדוחות |
| `logs/audit_recipes_DD-MM-YYYY_HH.MM.log` | משתנה | לוג ריצה |

## קבצים קיימים שהשקפיעו

- `recipe_utils.py` — משותף לכל סקריפטי ה-CLI. הסקריפט משתמש ב-`scan_all_recipes`, `extract_recipe_fields`, `find_recipe_bounds`, `Logger`, `load_data_js`, `CATEGORIES`, `CATEGORY_DICT`, `DIFFICULTIES`, `configure_rtl_fix` וכו׳.

## קבצים שלא השתנו

- `index.html`, `data.js`, `pre_en.js`, `book_data.js`, `about_redesigned.*`, `sw.js`, `manifest.json`, `download_images.py`, `add_recipe.py`, `edit_recipe.py`

## שימוש מומלץ

### הרצה ראשונה (סריקה מלאה)

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
python audit_recipes.py
```

בסוף הריצה:
- דוחות ב-`audit_reports/`
- לוג ב-`logs/audit_recipes_DD-MM-YYYY_HH.MM.log`

### פתיחת ה-CSV ב-Excel

1. פתח את `audit_reports/audit_report_*.csv`
2. סדר לפי עמודת `code` כדי לראות את הבעיות מקובצות
3. פלטר לפי `severity = medium` לראות את ה-73 "מתקדם"

### סריקה של קטגוריה אחת

```powershell
python audit_recipes.py --only-category soups
```

### דוח רק על בעיות חמורות

```powershell
python audit_recipes.py --severity medium
```

## פריסה

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\audit_recipes.py" ".\audit_recipes.py" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_audit_v1.md" ".\CHANGELOG_19-04-2026_audit_v1.md" -Force
```
```powershell
git add audit_recipes.py CHANGELOG_19-04-2026_audit_v1.md
```
```powershell
git commit -m "stage2: Add audit_recipes.py v1.0 - automated recipe quality audit"
```
```powershell
git push origin main
```

**הערה:** הדוחות ב-`audit_reports/` לא נכלוים ב-commit (הם תוצר). אפשר להוסיף `audit_reports/` ו-`logs/` ל-`.gitignore` אם רוצה.

---

## שלב 3 (הבא — לא בוצע)

לפי ה-PLAN: "Fix specific flagged recipes one-by-one using existing `edit_recipe.py`".

הרעיון:
1. אתה פותח את ה-CSV
2. בוחר מתכון עם בעיה שמעניינת אותך
3. מריץ `python edit_recipe.py --id <ID>`
4. מתקן ידנית עם ידע שלך על המתכון (או עם עזרה מ-Claude בסשן נפרד)

**למה לא אוטומטי:** תיקון תוכן של מתכון (למשל הרחבת שלב קצר ל-40 תווים) דורש ידע ממשי על הבישול — לא משהו שמודל AI יכול לעשות בבטחה בלי לפברק. התיקון ייעשה ידנית או בעזרת מחקר אמיתי.

### המלצה לסדר עבודה על 688 הבעיות

1. **הכי פריפויה** (15 דקות): 73 `bad_difficulty`. שמתקדם → קשה. זה אפשר אוטומטית אם תבקש ממני (sed/python 1-liner).
2. **חצי יום** (חודשיים ברקע): פתיחת ה-CSV, מיון לפי קטגוריה, עבור על 593 `short_step`, החלט אילו באמת קצרים מדי.
3. **מפוזר** (לא דחוף): 17 ה-LOW.

---

**לזכר פרלה בן-הראש ז״ל (1933-2025)**
