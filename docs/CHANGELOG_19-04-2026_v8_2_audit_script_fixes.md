# CHANGELOG — v8.2: תיקון סקריפט הביקורת (לא תיקון מתכונים)

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026 — לילה (אחרי v8.1)
**גרסה:** 8.2 (רק סקריפטים — אין שינויי קוד באתר)

---

## הבקשה

> תמשיך בבקשה

---

## הגילוי המרכזי

הרצתי את `audit_recipes.py` על ה-data.js הנוכחי (אחרי v8.1). הסקריפט דיווח על **485 מתכונים עם בעיות (46% מ-1054)**. בדיקה מעמיקה גילתה שמרבית "הבעיות" הן באגים ב-**סקריפט הביקורת עצמו**, לא בנתונים של פרלה.

זה ממצא משמעותי: לפני שטחיתי לתקן 73 מתכונים, גיליתי שהסקריפט פשוט שגוי. **לא מצאתי שום בעיה קריטית בנתוני המתכונים** — שיהיה ברור.

---

## 3 באגים בסקריפט שתוקנו

### 1. `bad_difficulty` — recipe_utils.py שורה 194

הסקריפט הגדיר:
```python
DIFFICULTIES = ['קל', 'בינוני', 'קשה']
```

אבל **ה-data.js וה-PLAN_v7_0_HEBREW.md מגדירים `'מתקדם'`**, לא `'קשה'`. בדיקה:

```python
import re
diffs = re.findall(r"diff:'([^']+)'", open('data.js').read())
from collections import Counter
print(Counter(diffs).most_common())
# [('קל', 698), ('בינוני', 283), ('מתקדם', 73)]
```

**`'קשה'` לא מופיע אפילו פעם אחת.** הסטנדרט הוא `'מתקדם'`.

**תיקון:** שיניתי את הקבוע ב-`recipe_utils.py`:
```python
DIFFICULTIES = ['קל', 'בינוני', 'מתקדם']  # v8.2: was 'קשה' but data.js uses 'מתקדם' across all 1054 recipes
```

**תוצאה:** 73 בעיות `bad_difficulty` נעלמו (תיקון של 100%).

### 2. `unparseable_serv` — audit_recipes.py שורות 175-191

הסקריפט ניסה לפענח רק מספרים מתוך שדה `serv`. אבל מתכוני חמוצים, ממרחים, ריבות, כבישות לא משתמשים במנות אינדיבידואליות — הם נמדדים ב-**מיכל**: "צנצנת גדולה", "כלי קטן", "כד גדול".

דוגמאות מה-data:
- `ye5` זחוק (ממרח תבלינים תימני) → `serv: 'כלי קטן'`
- `tn2` חריסה ביתית טוניסאית → `serv: 'צנצנת גדולה'`
- `iq16` חמוצים בגדדיים → `serv: 'צנצנת גדולה'`
- `as16` גאלחד (כרוב כבוש) → `serv: 'צנצנת גדולה'`

אלה תיאורים תקינים לחלוטין — לא באגים.

**תיקון:** הוספתי whitelist של תיאורי מיכל לגיטימיים:
```python
container_descriptors = (
    'צנצנת', 'כלי', 'קופסה', 'בקבוק', 'כד',     # containers
    'מנה אחת', 'יחיד', 'קערה',                    # single-portion descriptors
    'מנה שמירה', 'גרניש', 'תבלין',               # preservation/garnish/seasoning batches
)
```

הוספתי sentinel value (`-1`) ש-`check_serv_reasonable` יודע לדלג עליו ב-range check.

**תוצאה:** 9 בעיות `unparseable_serv` נעלמו (תיקון של 100%).

### 3. `suspicious_time` — audit_recipes.py שורה 65

הסקריפט הגדיר `MAX_REASONABLE_TIME = 720` (12 שעות) — אבל מתכוני שריה/מליחה/החמצה אותנטיים דורשים זמני המתנה ארוכים יותר:

```
fn2  | דג מלוח מרוקאי — מישייה | 1440 דקות (30 דקות + 24 שעות)
ve7  | בצלים קטנים כבושים    | 2880 דקות (20 דקות + 48 שעות)
ye12 | שמר (שמרי יין תימני)  | 1440 דקות (15 דקות + 24 שעות)
fe14 | דג מלוח מרוקאי — שמורא | 2880 דקות (48 שעות + 10 דקות הכנה)
```

24-48 שעות לדג מלוח, ירקות כבושים, יין — אלו זמני preparation לגיטימיים בכל מטבח של מסורת מרוקאית/ספרדית/תימנית.

**תיקון:** העלאתי את הסף מ-720 ל-4320 דקות (72 שעות):
```python
# v8.2: raised from 720 (12hr) to 4320 (72hr) to accommodate legitimate
# brining/curing/fermentation times in Moroccan/Spanish/Yemeni traditional
# recipes (salted fish, pickled vegetables, wine yeast, etc.)
MAX_REASONABLE_TIME = 4320  # More than 72 hours is suspect
```

**תוצאה:** 8 בעיות `suspicious_time` נעלמו (תיקון של 100%).

---

## תוצאות מצרפיות

| מדד | לפני v8.2 | אחרי v8.2 | שינוי |
|---|---|---|---|
| מתכונים עם בעיות | 485 (46%) | **418 (40%)** | -13.8% |
| HIGH severity | 0 | 0 | — |
| MEDIUM severity | 671 | 598 | -73 (תיקון bad_difficulty) |
| **LOW severity** | **17** | **0** | **-100%** |
| bad_difficulty | 73 | 0 | -100% |
| unparseable_serv | 9 | 0 | -100% |
| suspicious_time | 8 | 0 | -100% |
| short_step | 593 | 593 | — (לא נוגעים) |
| vague_quantity | 3 | 3 | — (לא נוגעים) |
| few_steps | 2 | 2 | — (לא נוגעים) |

**90 בעיות מזויפות הוסרו.**

---

## למה לא נגעתי במתכונים עצמם

**3 קטגוריות בעיות שאסור לי לגעת בהן בלי הוראת אסף:**

1. **`short_step` (593):** שלב פחות מ-20 תווים. אבל זה התיאור של פרלה. למשל "מערבבים היטב" (16 תווים) — תיאור תקני בעברית. הסף השרירותי של 20 תווים לא תואם לסגנון כתיבה תמציתי במתכוני סבתא.

2. **`vague_quantity` (3):** כמויות עמומות כמו "טיפה" או "חופן". זה הזיכרון של אמא — אם פרלה כתבה "חופן" זה כי היא בישלה בעין, וזה חלק מהאופי של המתכון.

3. **`few_steps` (2):** מתכונים עם 1-2 שלבים. ייתכן שיש מתכונים פשוטים שלא דורשים יותר.

**עיקרון:** סקריפט אוטומטי לא יחליף את שיקול הדעת המשפחתי. כל אחת מ-598 הבעיות הנותרות תלויה בהחלטת אסף — האם זה "תיקון נדרש" או "כך אמא בישלה".

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `recipe_utils.py` | שורה 194: `DIFFICULTIES` תוקן מ-`'קשה'` ל-`'מתקדם'` |
| `audit_recipes.py` | (1) `_serv_to_number` הורחב עם container whitelist, (2) `check_serv_reasonable` מדלג על sentinel -1, (3) `MAX_REASONABLE_TIME` עלה מ-720 ל-4320 |
| `audit_report_v8_2.md` | דו"ח חדש (Markdown) — 1054 מתכונים, 418 עם בעיות |
| `audit_report_v8_2.json` | דו"ח חדש (JSON) — לעיבוד אוטומטי |
| `audit_report_v8_2.csv` | דו"ח חדש (CSV) — לטריאז' בגיליון אלקטרוני |

`data.js`, `index.html` — **לא נגעתי. לא תיקנתי שום מתכון.**

---

## פריסה

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\recipe_utils.py" ".\recipe_utils.py" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\audit_recipes.py" ".\audit_recipes.py" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_v8_2_audit_script_fixes.md" "." -Force
```
```powershell
git add recipe_utils.py audit_recipes.py CHANGELOG_19-04-2026_v8_2_audit_script_fixes.md
```
```powershell
git commit -m "v8.2: audit script fixes — DIFFICULTIES match data, container serv whitelist, raised time threshold for brining"
```
```powershell
git push origin main
```

`audit_report_v8_2.*` הם דו"חות אופציונליים — אסף יכול להעלות אותם או לא, לפי שיקול דעתו (סף הריצה הבאה יווצר אותם מחדש).

---

## איך לקרוא את הדו"ח החדש

הדו"ח כעת מציג רק **בעיות תוכן אמיתיות** — לא false positives של הסקריפט עצמו. אם אסף ירצה לטפל ב-598 short_steps, הוא יכול לפתוח את `audit_report_v8_2.csv` ב-Excel ולעבור עליהם אחד-אחד עם `edit_recipe.py`.

**אבל זה לא חובה.** מתכון "מערבבים היטב" הוא תקין לחלוטין — זה רק **שיקול דעת** של אסף אם להרחיב או לא.

---

## מה נשאר ב-Roadmap לאחר v8.2

זהה ל-v8.1 — אין שינוי. כל מה שנותר דורש **מעורבות אנושית**:

1. רענון תיוגי `COMMUNITY_HOLIDAY_TAGS` (משפחה)
2. רענון תיוגי `HOLIDAY_TAGS` של מרוקו (משפחה)
3. החלטה האם לעבור על 598 short_steps (אסף)
4. תמונות חסרות (`download_images.py` — אסף מריץ)
5. Breadcrumbs / carousel / OG images / lazy loading (החלטות UX)

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
