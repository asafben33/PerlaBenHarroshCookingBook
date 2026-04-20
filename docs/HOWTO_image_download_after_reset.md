# הורדת תמונות מאופס — סדר פקודות מלא

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**תרחיש:** איפוס מלא של תיקיית `images/recipes_images/` → הורדה חדשה מקסימלית

---

## עקרונות התהליך

הסקריפט `download_images.py` v6.0.1 כולל 7 שכבות דיוק, אבל **ריצה אחת לא מספיקה** — אם נריץ רק עם `--strict` (סף 60) חלק מהמתכונים יישארו ללא תמונות בכלל. הגישה הנכונה: **5 ריצות מדורגות** מהקפדני ביותר עד הסלחני ביותר, כש**כל ריצה ממלאת רק את החסר** (כי בלי `--overwrite` הסקריפט מדלג על מתכונים שכבר יש להם תמונה).

זה דומה לרשת דיג עם רשתות צפופות במיוחד תחילה (תופס רק דגים גדולים+מובהקים), ואז רשתות פחות צפופות (תופס דגים בינוניים).

---

## הסדר המומלץ — 5 שלבים

### שלב 1 — בדיקת הסביבה (לפני כל הרצה)

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```

```powershell
# וודא שהתיקייה אכן ריקה (אחרי איפוס)
Get-ChildItem .\images\recipes_images\ -Filter "r-*.jpg" | Measure-Object
```

ציפיה: `Count: 0` (או מספר נמוך מאוד).

```powershell
# וודא שהסקריפט הוא v6.0.1 (אחרי ה-hotfix)
Select-String -Path .\download_images.py -Pattern "recipe.get\('title', ''\)" | Select-Object -First 1
```

ציפיה: שורה אחת תופיע. אם לא — אל תמשיך, צריך לעדכן את הסקריפט קודם.

---

### שלב 2 — סבב 1: ניקוד 75 (מקסימום דיוק)

```powershell
python download_images.py --skip-clean --skip-dedup --min-score 75 --provenance
```

**מה קורה:** רק URLs עם ניקוד ≥ 75 עוברים. זאת אומרת:
- URL בדומיין מאומת + מכיל transliteration של שם המתכון + cross-source verified
- צפי: ~30-50% מהמתכונים יקבלו תמונה (הפופולריים — טאג'ין, קוסקוס, מופלטה, וכו')

**למה דילוג על clean ו-dedup:** התיקייה ריקה — אין מה לנקות. דה-דופ נריץ פעם אחת בסוף.

---

### שלב 3 — סבב 2: ניקוד 60 (--strict)

```powershell
python download_images.py --skip-clean --skip-dedup --strict --provenance
```

**מה קורה:** מתכונים שעדיין אין להם תמונה מקבלים סבב נוסף עם הסף `--strict` הסטנדרטי. הסקריפט **מדלג אוטומטית** על מתכונים שכבר יש להם תמונה (בלי `--overwrite`).

**צפי:** עוד 30-40% מהמתכונים מתמלאים. סה"כ אחרי שלב 3 — ~70% מהמתכונים יש להם תמונה איכותית.

---

### שלב 4 — סבב 3: ניקוד 50 (סלחני יותר)

```powershell
python download_images.py --skip-clean --skip-dedup --min-score 50 --provenance
```

**מה קורה:** מתכונים שעדיין חסרי תמונה — רובם אזוטריים (מתכוני בוכרה ספציפיים, דגי מלוח עתיקים) — מקבלים סבב עם סף בינוני.

**צפי:** עוד 15-20% מתמלאים. סה"כ אחרי שלב 4 — ~90% כיסוי.

---

### שלב 5 — סבב 4: ברירת מחדל 40

```powershell
python download_images.py --skip-clean --skip-dedup --provenance
```

**מה קורה:** ברירת המחדל (סף 40) — רוב המתכונים שנותרו יקבלו תמונה כלשהי.

**צפי:** סה"כ אחרי שלב 5 — ~95-98% מהמתכונים עם תמונה.

---

### שלב 6 — ניקוי חוזר + dedup + alias מאוחד

```powershell
python download_images.py --skip-download --aggressive-clean --inline-alias
```

**מה קורה:**
1. **`--skip-download`** — לא יורד תמונות חדשות, רק מנקה ומאחד
2. **`--aggressive-clean`** — סורק את כל התמונות שירדו ומוחק כל אחת שלא עומדת בקריטריונים מחמירים יותר (גודל מינימלי 5KB, aspect ratio 1.9/0.55)
3. **dedup** — מזהה תמונות זהות (SHA256) ומוחק כפילויות
4. **`--inline-alias`** — מזריק את ה-alias map לתוך index.html (כדי שכפילויות יחליפו זו את זו ללא צורך בקבצים נוספים)

זה השלב שבו תמונות "סבירות אבל לא מצוינות" שעברו את שלב 5 (סף 40) נחתכות.

---

## כל הפקודות יחד (העתק-הדבק)

```powershell
# שלב 1 — בדיקת סביבה
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
Get-ChildItem .\images\recipes_images\ -Filter "r-*.jpg" | Measure-Object

# שלב 2 — סבב 1: ניקוד 75 (מקסימום דיוק)
python download_images.py --skip-clean --skip-dedup --min-score 75 --provenance

# שלב 3 — סבב 2: ניקוד 60 (strict)
python download_images.py --skip-clean --skip-dedup --strict --provenance

# שלב 4 — סבב 3: ניקוד 50
python download_images.py --skip-clean --skip-dedup --min-score 50 --provenance

# שלב 5 — סבב 4: ברירת מחדל 40
python download_images.py --skip-clean --skip-dedup --provenance

# שלב 6 — ניקוי חוזר אגרסיבי + dedup + alias
python download_images.py --skip-download --aggressive-clean --inline-alias
```

**זמן צפוי:** 4-6 שעות סה"כ (תלוי במהירות הרשת ובזמן תגובה של מקורות).

**ניתן להריץ כל סבב בנפרד** — אם אתה רוצה לבדוק אחרי כל שלב לפני שאתה ממשיך לבא.

---

## בדיקה בין שלבים (אופציונלי)

לראות כמה מתכונים יש להם תמונה כרגע:

```powershell
$total = 1054
$withImage = (Get-ChildItem .\images\recipes_images\r-*.jpg | Where-Object { $_.Name -match '^r-[a-z0-9]+\.jpg$' }).Count
"כיסוי: $withImage / $total ($([Math]::Round(($withImage / $total) * 100, 1))%)"
```

לראות mismatches — מתכונים שאין להם תמונה:

```powershell
# קרא את כל ה-IDs מ-data.js, השווה לקבצים בתיקייה
$dataIds = Select-String -Path .\data.js -Pattern "id:'([^']+)'" -AllMatches | 
    ForEach-Object { $_.Matches.Groups[1].Value } | Sort-Object -Unique
$existingIds = Get-ChildItem .\images\recipes_images\r-*.jpg | 
    ForEach-Object { ($_.BaseName -replace '^r-', '') -replace '-\d+$', '' } | Sort-Object -Unique
$missing = $dataIds | Where-Object { $_ -notin $existingIds }
"מתכונים ללא תמונה: $($missing.Count)"
$missing | Select-Object -First 20
```

---

## בדיקת איכות אחרי הסיום (provenance)

הסקריפט שומר ב-`logs/images_provenance.json` רישום של כל תמונה שירדה עם הניקוד שלה. בדוק את התמונות עם הניקוד הנמוך ביותר — אלה החשודות ביותר:

```powershell
python -c "
import json
log = json.load(open('logs/images_provenance.json', encoding='utf-8'))
sorted_items = sorted(log.items(), key=lambda x: x[1]['relevance_score'])
print('20 התמונות עם הניקוד הנמוך ביותר:')
for rid, entry in sorted_items[:20]:
    print(f'{rid:8s} | score={entry[\"relevance_score\"]:3d} | {entry[\"url\"][:80]}')
"
```

אם אתה רואה שתמונה ספציפית לא מתאימה — מחק אותה ידנית:

```powershell
Remove-Item .\images\recipes_images\r-<ID>.jpg
```

ואחר כך הרץ ריצה ספציפית רק לאותו מתכון... למרבה הצער הסקריפט לא תומך ב-filter חד-פעמי לפי ID, אז במקרה של תיקון אחד-אחד עדיף להשתמש ב-`edit_recipe.py` (הסקריפט הנפרד שאסף יצר).

---

## מה לעשות אם משהו נכשל

### חוסר חיבור לאינטרנט
```powershell
python download_images.py --detect-only
```
יציג את ה-proxy שהסקריפט מצא. אם זה לא נכון — תן ידני:
```powershell
python download_images.py --proxy "http://proxy.gov.il:8080" --skip-clean --skip-dedup --min-score 60
```

### NameError או שגיאת ריצה
תעלה את ה-traceback ואני אתקן את הסקריפט. אבל אם זה אחרי v6.0.1 — לא אמור לקרות.

### זמן ריצה ארוך מדי
אם ריצה מסוימת לוקחת שעות ולא מתקדמת — `Ctrl+C` לעצירה, ואז:
```powershell
python download_images.py --skip-download --skip-clean    # רק dedup על מה שכבר ירד
```

---

## מה זה אומר ב-provenance log אחרי הסיום

לכל מתכון שיש לו תמונה, יהיה רישום כזה ב-`logs/images_provenance.json`:

```json
{
  "iq8": {
    "url": "https://www.themealdb.com/images/media/meals/...",
    "relevance_score": 95,
    "source": "score:95",
    "reason": "saved as r-iq8.jpg (passed pixel + relevance checks)",
    "ts": "2026-04-20T04:15:33"
  }
}
```

`relevance_score` הוא הניקוד הסופי שכלל את כל 7 השכבות + cross-source bonus. ככל שהוא גבוה יותר — כך יותר סביר שהתמונה באמת תואמת את המתכון.

---

## סיכום

```
איפוס מלא  →  ריצה 1 (סף 75)  →  ריצה 2 (סף 60)  →  ריצה 3 (סף 50)
              →  ריצה 4 (סף 40)  →  ניקוי אגרסיבי + dedup + alias
```

**הריצה הזו היא חד-פעמית.** לאחר הסיום, השמירה האקטיבית של התמונות היא דרך `download_images.py --skip-clean --skip-dedup` בריצה רגילה (פעם בחודש לרענון), או דרך תיקונים נקודתיים עם `edit_recipe.py`.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
