# IMAGE_MAPPING_v8_25 — תיעוד מלא של מיפוי 151 תמונות הספר

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20-04-2026
**גרסה:** v8.25 — Full Image Integration

---

## מטרת המסמך

מסמך זה מתעד את **המיפוי המלא** של כל 151 תמונות הספר לפרקים, מיקומים ותיאורים. המסמך הוא **המקור המסכמך** (single source of truth) — אם book_data.js נשבר, או אם רוצים לשנות את החלוקה בעתיד, ניתן להריץ את `rebuild_book_images.py` ולשחזר את הכל.

---

## הקבצים במערכת

| קובץ | תפקיד | פורמט |
|---|---|---|
| **`IMAGE_MAPPING_v8_25.json`** | המקור המסכמך — מיפוי של כל 151 התמונות | JSON, machine-readable |
| **`IMAGE_MAPPING_v8_25.csv`** | אותו מיפוי בפורמט גיליון אלקטרוני | CSV, Excel-friendly |
| **`rebuild_book_images.py`** | סקריפט Python לשחזור book_data.js מהמיפוי | Python 3.8+ |
| **`IMAGE_MAPPING_README.md`** | המסמך הזה — תיעוד אנושי | Markdown |
| `book_data.js` | תוצר סופי — מכיל את כל התמונות משולבות | JavaScript |
| `book_images.zip` | 151 קבצי התמונה עצמם | ZIP |

---

## מבנה המיפוי

### קטגוריזציה לפי סוג תמונה

| סדרה | טווח | מספר תמונות | מקור |
|---|---|---|---|
| `book_g42_*` | 016-095 | 78 | תמונות הקבוצה הראשונה — כנראה מהדפסה ראשונה של הספר |
| `book_g45_*` | 000-073 | 72 | תמונות הקבוצה השנייה — תוספות מאוחרות יותר או הדפסה שנייה |
| `wedding.jpg` | — | 1 | דיוקן חתונת פרלה ופנחס ז"ל |
| **סה״כ** | | **151** | |

### חלוקה לפי פרקים

| פרק | שם בעברית | תמונות inline | תמונות בגלריה | סה״כ |
|---|---|---|---|---|
| `prologue` | פרולוג | 0 | 8 | **8** |
| `ch1` | פרק א': שורשים באדמת מרוקו | 5 | 9 | **14** |
| `ch2` | פרק ב': מעגל השנה | 0 | 8 | **8** |
| `ch3` | פרק ג': מרוקו של ילדותי | 3 | 16 | **19** |
| `ch4` | פרק ד': כמיהה ציונית | 4 | 11 | **15** |
| `ch5` | פרק ה': אל הדרור | 4 | 15 | **19** |
| `ch6` | פרק ו': ימים ראשונים | 2 | 10 | **12** |
| `ch7` | פרק ז': סיפורה של פרלה | 5 | 10 | **15** |
| `ch8` | פרק ח': בית ומשפחה | 3 | 12 | **15** |
| `ch9` | פרק ט': במדים | 4 | 10 | **14** |
| `ch10` | פרק י': המבט לעבר | 4 | 8 | **12** |
| **סה״כ** | | **34** | **117** | **151** |

### סוגי placement

- **`inline`** — התמונה משובצת בתוך תת-פרק (`book-sub-block`), ליד הטקסט הרלוונטי. אלו הן 34 התמונות שהיו ב-book_data.js לפני v8.25.
- **`gallery`** — התמונה בגלריה בסוף הפרק (`book-gallery-section`). אלו הן 117 התמונות החדשות שנוספו ב-v8.25.

---

## מבנה ה-JSON

```json
{
  "meta": {
    "version": "8.25",
    "date": "2026-04-20",
    "project": "Perla Ben-Harrosh Cookbook",
    "total_images": 151,
    "image_sets": { "g42": "...", "g45": "...", "wedding": "..." },
    "chapters": { "prologue": "פרולוג", ... }
  },
  "mapping": [
    {
      "filename": "book_g42_016.jpg",
      "chapter_id": "ch1",
      "chapter_name_he": "פרק א': שורשים באדמת מרוקו",
      "image_number": 16,
      "image_set": "g42",
      "placement": "inline",
      "alt_he": "תמונה היסטורית מטנג'יר",
      "alt_en": "Historical photo from Tangier",
      "added_in": "pre-v8.25"
    },
    ...151 entries...
  ],
  "distribution_summary": {
    "prologue": { "name_he": "...", "inline_count": 0, "gallery_count": 8, ... },
    ...
  }
}
```

### השדות בכל רשומה
| שדה | סוג | משמעות |
|---|---|---|
| `filename` | string | שם הקובץ במלואו (כולל סיומת `.jpg`) |
| `chapter_id` | string | מזהה הפרק (`prologue`, `ch1`...`ch10`) |
| `chapter_name_he` | string | שם הפרק בעברית (לקריאות) |
| `image_number` | int | מספר התמונה בסדרה (016, 017, וכו') |
| `image_set` | string | סוג: `g42` / `g45` / `wedding` |
| `placement` | string | `inline` (בתוך תת-פרק) / `gallery` (בסוף פרק) |
| `alt_he` | string | טקסט תיאור בעברית (לנגישות) |
| `alt_en` | string | טקסט תיאור באנגלית (לתרגום EN) |
| `added_in` | string | מתי נוספה לספר (`pre-v8.25` / `v8.25`) |

---

## איך להשתמש — תרחישים שכיחים

### תרחיש 1: book_data.js נשבר ורוצים לשחזר
```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
# גיבוי הקובץ הנוכחי
Copy-Item book_data.js book_data.js.bak
# הרצת הסקריפט (יכתוב book_data.js.new)
python rebuild_book_images.py --input book_data.js.bak --output book_data.js
# בדיקה - צריך לראות "HE: 151 תמונות"
```

### תרחיש 2: רוצים לעדכן alt text של תמונה
```powershell
# פתח את IMAGE_MAPPING_v8_25.json בעורך טקסט
# מצא את התמונה (לדוגמה book_g42_021.jpg)
# שנה את "alt_he" ו/או "alt_en"
# שמור והרץ:
python rebuild_book_images.py
# יווצר book_data.js.new עם השינויים
```

### תרחיש 3: רוצים להעביר תמונה לפרק אחר
```powershell
# פתח IMAGE_MAPPING_v8_25.json
# שנה את "chapter_id" ו-"chapter_name_he" של התמונה
# שמור והרץ:
python rebuild_book_images.py
```

### תרחיש 4: הוספת תמונה חדשה (v8.26+)
```powershell
# 1. הוסף את הקובץ ל-images/book_images/
# 2. פתח IMAGE_MAPPING_v8_25.json
# 3. הוסף רשומה חדשה למערך "mapping"
# 4. עדכן "total_images" במטא
# 5. הרץ rebuild_book_images.py
# 6. שנה את הגרסה של הקובץ ל-v8_26
```

### תרחיש 5: בדיקה ידנית של חלוקה (CSV)
פתח `IMAGE_MAPPING_v8_25.csv` ב-Excel.
ניתן לסנן/למיין לפי כל עמודה — שימושי לבדיקה.

---

## הסבר טכני: איך הסקריפט עובד

```
rebuild_book_images.py
    │
    ├── שלב 1: קריאת IMAGE_MAPPING_v8_25.json
    │     └── טעינת מיפוי 151 תמונות
    │
    ├── שלב 2: קריאת book_data.js (קלט)
    │     └── חילוץ BOOK_HTML (HE) + BOOK_HTML_EN (EN)
    │
    ├── שלב 3: עיבוד כל פרק
    │     ├── 3.1 - איסוף תמונות 'gallery' לכל פרק
    │     ├── 3.2 - יצירת HTML של section book-gallery-section
    │     ├── 3.3 - הזרקת ה-section לפני סגירת ה-</div> של הפרק
    │     └── ולידציה: ספירת תמונות לאחר הזרקה
    │
    └── שלב 4: כתיבת book_data.js.new
          └── ולידציה סופית: חייב להיות 151 תמונות ב-HE
```

### מבנה ה-HTML שנוצר

```html
<section class="book-sub-block book-gallery-section">
  <h4 class="book-sub">תמונות מן האלבום המשפחתי</h4>
  <figure class="book-inline-photo">
    <img src="images/book_images/book_g42_020.jpg" 
         alt="סצנה מן הרחוב היהודי במרוקו" 
         loading="lazy">
    <figcaption>סצנה מן הרחוב היהודי במרוקו</figcaption>
  </figure>
  <figure class="book-inline-photo">
    ...עוד תמונות...
  </figure>
</section>
```

ה-CSS המתאים ב-index.html יוצר תצוגת grid:
- **דסקטופ:** 3 תמונות בשורה (`width: calc(33% - 8px)`)
- **טאבלט:** 2 תמונות בשורה
- **מובייל:** 1 תמונה בשורה
- **קורא 3D:** 2 תמונות בשורה (תמונות קטנות יותר — 90px max-height)

---

## גרסה מינימלית של JSON (לדוגמה)

```json
{
  "meta": {
    "version": "8.25",
    "total_images": 151
  },
  "mapping": [
    {
      "filename": "wedding.jpg",
      "chapter_id": "prologue",
      "image_set": "wedding",
      "placement": "gallery",
      "alt_he": "פרלה ופנחס בן-הראש ביום חתונתם",
      "alt_en": "Perla and Pinchas Ben-Harrosh on their wedding day"
    }
  ]
}
```

הסקריפט יודע לעבוד גם עם רשומות חלקיות — רק `filename`, `chapter_id`, `placement`, `alt_he`, `alt_en` הם **חובה**. שאר השדות הם metadata עזר.

---

## שדרוגים עתידיים

### לדיוק 100% — מיפוי לפי הספר הסרוק
המיפוי הנוכחי הוא **דטרמיניסטי לפי מספרי תמונה** (בערך עוקב אחרי מספרי העמודים בספר המקורי). אם תרצה לעדכן למיפוי **המדויק** לפי הספר הסרוק:

1. עבור על הספר הסרוק (WhatsApp images)
2. לכל תמונה — רשום:
   - באיזה פרק היא מופיעה?
   - תחת איזה תת-כותרת?
   - מה הטקסט שלפניה ומה אחריה?
3. עדכן את ה-JSON עם:
   ```json
   {
     "filename": "book_g42_038.jpg",
     "chapter_id": "ch3",
     "placement": "inline",
     "inline_after_subtitle": "ילדות במרוקו",  // ← שדה חדש
     "alt_he": "הילדים בשכונה היהודית"
   }
   ```
4. עדכן את `rebuild_book_images.py` כדי לתמוך ב-`inline_after_subtitle`
5. הרץ ובדוק

### אם תוסיף תמונות חדשות
- שמור על קונבנציית השמות (`book_g42_*` או `book_g45_*` או `*.jpg`)
- הוסף ל-`IMAGE_MAPPING_v8_25.json`
- הרץ `rebuild_book_images.py`
- שנה את הגרסה של הקובץ JSON

---

## שאלות נפוצות

**ש: מה ההבדל בין `inline` ל-`gallery`?**
ת: `inline` = תמונה במיקום ספציפי בתוך הטקסט (אחרי subtitle מסוים). `gallery` = תמונה בקבוצה בסוף הפרק.

**ש: למה יש 117 תמונות ב-`gallery` ורק 34 ב-`inline`?**
ת: 34 תמונות `inline` היו במיקום מדויק בקוד הקיים מלפני v8.25. את ה-117 החדשות הוספתי כ-`gallery` כי **אין לי מיפוי מדויק לטקסט**. אם תספק מיפוי מדויק לכל אחת מהן, אפשר להעביר אותן ל-`inline`.

**ש: אני רוצה לערוך את המיפוי בידנית — מה קל יותר?**
ת: ה-CSV ב-Excel יותר קל לעיון ועריכה מהירה. אבל אחרי שתערוך, **תצטרך להמיר אותו חזרה ל-JSON** לפני הרצת הסקריפט. אפשר להוסיף סקריפט המרה עתידי.

**ש: איך אני יודע שהמיפוי תקין?**
ת: הרץ `python rebuild_book_images.py --dry-run`. אם הוא מסיים בלי שגיאות ומציג "HE: 151 תמונות, EN: 151 תמונות" — הכל תקין.

**ש: מה קורה אם הוספתי תמונה ל-images/ אבל שכחתי לעדכן את ה-JSON?**
ת: התמונה לא תופיע בספר. הסקריפט לא סורק את התיקייה — הוא משתמש רק ב-JSON.

---

## תיעוד גרסאות

| גרסה | תאריך | שינוי |
|---|---|---|
| v8.25 | 20-04-2026 | יצירה ראשונית עם 151 תמונות (34 inline + 117 gallery) |

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
