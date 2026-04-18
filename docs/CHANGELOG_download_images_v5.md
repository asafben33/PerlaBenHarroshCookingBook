# download_images.py v5.0 — סקריפט מאוחד

תיעוד מיזוג של שלושת הסקריפטים לסקריפט יחיד — 18/04/2026.

---

## מה הבעיה שנפתרת

1. **תמונות לא רלוונטיות ירדו** (נופים, אנשים, טכנולוגיה, אירועים) — הפילטר לא זיהה תמונות של אנשים כיוון שלא היו בו מילות מפתח כמו `headshot`, `businesswoman`, `ceremony` וכו'.
2. **כפילויות לא קיבלו לינק ב-`_IMG_ALIAS.js`** — הסקריפט `cleanup_hardlinks.py` רץ בנפרד והמשתמש לא תמיד העתיק ידנית את תוכן `_IMG_ALIAS.js` ל-`index.html`.
3. **שלושה סקריפטים נפרדים** (`download_images.py`, `clean_bad_images.py`, `cleanup_hardlinks.py`) — בלבול בתפעול, כפילות קוד, אי-עקביות.

---

## מה התקבל

קובץ יחיד `download_images.py` (v5.0) עם זרימת שלושה שלבים:

### שלב 1 — Clean Existing Bad Images (חדש)
לפני שמתחילים להוריד — סורק את `images/recipes_images/` ומוחק קבצים חשודים:
- קבצים קטנים מדי (<3KB — הורדה נכשלה)
- EXIF/metadata של GoPro/DJI/satellite/landscape
- aspect ratio קיצוני (`>2.2` פנורמה, `<0.45` portrait של אדם)
- טביעות אצבע של picsum placeholders (אם יוגדרו)

במצב `--aggressive-clean`, הסף נעשה קפדני יותר (min-size 5KB, ratio 1.9/0.55).

### שלב 2 — Download (משופר)
אותה לוגיקת חיפוש מקצה-לקצה של הגרסה הקודמת (Hebrew-first ב-42 אתרים ישראלים, ואז אנגלית ב-40 אתרים בינלאומיים) — **אבל עם פילטר URL מחוזק**:

**נוספו ~40 מילות מפתח חדשות** לרשימת `_BAD_URL_KW`:
- אנשים: `man`, `woman`, `boy`, `girl`, `kid`, `headshot`, `mugshot`, `profile-photo`, `smile`, `pose`, `posing`, `portrait-photography`, `businesswoman`, `businessman`, `entrepreneur`, `engineer`, `doctor`, `nurse`, `actor`, `actress`, `celebrity`, `influencer`, `blogger`, `youtuber`
- אירועים: `birthday-party`, `graduation`, `ceremony`, `concert`, `speech`, `award`, `trophy`, `prize`, `congress`, `conference`, `meeting`, `presentation`, `interview`, `podium`, `stage`, `family-portrait`
- עיצוב/אבסטרקט: `illustration`, `vector`, `logo`, `banner`, `poster`, `flyer`, `brochure`
- טבע נוסף: `waterfall`, `canyon`, `valley`, `island`, `shore`, `coast`, `cliff`, `volcano`
- תיירות: `hotel`, `resort`, `touristic`, `tourism`, `travel-destination`, `vacation`
- ספורט: `swimming`, `surfing`
- חיות: `butterfly`, `insect`, `snake`

**פילטר פיקסלים מחוזק** (`_is_food_image_by_pixels`):
- בדיקת aspect ratio באמצעות JPEG SOF marker
- דוחה פנורמות (ratio>2.2) ו-portraits גבוהים (ratio<0.45)
- מרחיב את רשימת ה-EXIF markers

### שלב 3 — Dedup + Alias Auto-inline (משופר)
אותה לוגיקת SHA256 dedup של הגרסה הקודמת, **בתוספת**:
- דגל `--inline-alias` שמחדיר אוטומטית את תוכן `_IMG_ALIAS.js` ישירות לתוך `var _IMG_ALIAS = {...};` ב-`index.html` — **אין צורך עוד להעתיק ידנית**.

---

## דגלי CLI חדשים

| דגל | פעולה |
|---|---|
| `--clean-only` | רץ רק שלב 1 (ניקוי), דולג על הורדה ו-dedup |
| `--skip-clean` | דולג על שלב 1 (לא מוחק קבצים קיימים) |
| `--aggressive-clean` | שלב 1 עם פילטרים קפדניים יותר |
| `--inline-alias` | אחרי dedup — מחדיר את ה-alias map ישירות ל-`index.html` |

דגלים קיימים שנשמרו: `--skip-download`, `--skip-dedup`, `--dry-run`, `--overwrite`, `--no-proxy`, `--proxy URL`, `--detect-only`, `--test-proxy`.

---

## תרחישי שימוש מומלצים

**תרחיש 1 — מחזור מלא, פעם ראשונה:**
```
python download_images.py --aggressive-clean --inline-alias
```
ינקה תמונות חשודות קיימות, יוריד חדשות, ינקה כפילויות, ויעדכן את index.html.

**תרחיש 2 — לבדוק מה יימחק לפני שמוחקים:**
```
python download_images.py --clean-only --dry-run --aggressive-clean
```
יציג רשימה מלאה של מה שיימחק, ללא מחיקה בפועל.

**תרחיש 3 — רק להוריד חדשות (נניח שכבר ניקיתי):**
```
python download_images.py --skip-clean --inline-alias
```

**תרחיש 4 — לאחר פעולה ידנית, רק לעדכן _IMG_ALIAS ב-index.html:**
```
python download_images.py --skip-clean --skip-download --inline-alias
```

**תרחיש 5 — חזרה לזרימה הישנה (רק הורדה + dedup, ללא ניקוי):**
```
python download_images.py --skip-clean
```

---

## מה לא השתנה (הובטח ששום דבר לא יאבד)

- **0 פונקציות מקוריות** נמחקו (אומת: 57 → 59, 2 פונקציות חדשות, אף אחת לא אבדה)
- כל 42 מקורות ה-Hebrew search — שמורים
- כל 40 מקורות ה-English search — שמורים
- כל לוגיקת ה-Proxy Auto-Detection — שמורה
- `parse_recipes`, `build_query`, `find_youtube_video`, `source_hebrew_first`, `_bing_image_search`, `_ddg_image_search`, `source_mealdb`, `source_wikimedia_single`, `source_openverse`, `source_unsplash_search` — כל אחת מהן זהה
- BiDi console fix עבור PowerShell — שמור
- Live progress bar — שמור
- Ctrl+C immediate-exit handler — שמור

---

## מה לעשות עם הסקריפטים הישנים

אחרי שאתה מתקין את v5.0, אפשר:

**אפשרות A — למחוק את שני הסקריפטים המיותרים מ-Git:**
```powershell
git rm clean_bad_images.py cleanup_hardlinks.py
```
ואז לעדכן את `.gitignore` ו-README.

**אפשרות B — להשאיר אותם כ-fallback** למקרה שתרצה להריץ משימה ממוקדת.

אני ממליץ על אפשרות A — הם מיותרים כי כל היכולת שלהם נמצאת ב-v5.0.

---

## אימות טכני

```
✓ python3 -m py_compile download_images.py — תקין
✓ 57 פונקציות מקוריות נשמרו (אפס איבוד)
✓ 2 פונקציות חדשות: clean_existing_bad_images, inline_alias_into_index
✓ כל דגלי ה-CLI הישנים עובדים כמקודם
✓ 4 דגלי CLI חדשים זמינים
✓ כ-40 מילות מפתח חדשות בפילטר _BAD_URL_KW
✓ פילטר aspect-ratio מוטמע ב-_is_food_image_by_pixels
✓ docstring מעודכן לגרסה 5.0
```
