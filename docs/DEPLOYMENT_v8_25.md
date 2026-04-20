# הוראות פריסה — v8.25: כל 151 תמונות הספר

## הקבצים החדשים

| קובץ | גודל | תפקיד |
|---|---|---|
| **`index.html`** | 610,461 bytes | קוד התצוגה + CSS לגלריות |
| **`book_data.js`** | 215,028 bytes | תוכן הספר עם כל 151 התמונות |
| **`CHANGELOG_20-04-2026_v8_25_all_151_images.md`** | תיעוד | מסמך השינויים |
| **`book_images.zip`** | 17.5 MB | כל 151 התמונות |

---

## הוראות פריסה מלאות

### צעד 0 — וודא שהתיקיה `images/book_images/` קיימת בריפו

פתח PowerShell:
```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```
```powershell
# בדוק שיש תיקייה
Test-Path "images\book_images"
```

אם זה מחזיר `False`, צור את התיקייה:
```powershell
New-Item -ItemType Directory -Path "images\book_images" -Force
```

### צעד 1 — חלץ את 151 התמונות לתיקייה הנכונה

הורד את `book_images.zip` מהפלט (קישור ההורדה למעלה).

```powershell
# הוצא את הקבצים מה-zip
Expand-Archive -Path "$env:USERPROFILE\Downloads\book_images.zip" -DestinationPath ".\images\" -Force
```
```powershell
# וודא שכל 151 הקבצים נמצאים שם
(Get-ChildItem "images\book_images\" -File).Count
```

צריך להחזיר `151`.

### צעד 2 — העתק את הקבצים החדשים

```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\book_data.js" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_25_all_151_images.md" "." -Force
```

### צעד 3 — Commit + Push לגיט

```powershell
git add index.html book_data.js CHANGELOG_20-04-2026_v8_25_all_151_images.md images/book_images/
```
```powershell
git status
```

צריך להראות:
- `modified: index.html`
- `modified: book_data.js`
- `new file: CHANGELOG_20-04-2026_v8_25_all_151_images.md`
- `new file: images/book_images/book_g42_*.jpg` (78 קבצים)
- `new file: images/book_images/book_g45_*.jpg` (72 קבצים)
- `new file: images/book_images/wedding.jpg`

```powershell
git commit -m "v8.25: integrate ALL 151 book images - 117 new photos in 11 family album galleries"
```
```powershell
git push origin main
```

> ⚠️ **התמונות יוסיפו ~17MB ל-push.** זה יכול להימשך 1-3 דקות תלוי במהירות ההעלאה.

### צעד 4 — Hard Refresh בדפדפן

**חובה** — אחרת תראה את הקאש הישן.
- **Windows:** `Ctrl + Shift + R`
- **Mac:** `Cmd + Shift + R`

---

## בדיקה אחרי הפריסה

### במצב טקסט (📄 מצב טקסט)
1. גלול לסוף כל פרק
2. צריך לראות **"תמונות מן האלבום המשפחתי"** — כותרת חדשה
3. תחתיה — גלריה של 6-15 תמונות מסודרות 3x3
4. כל תמונה עם כיתוב משלה

### במצב ספר 3D (📖 מצב ספר)
ב-Console (F12) צריך להופיע:
```
[BookReader] Total pages: ~130-145    ← היה 116, עכשיו יותר בגלל גלריות
[BookReader] PageFlip initialized successfully
```

### בדיקת תמונות בדפדפן
פתח את DevTools → Network → Filter "Img":
- צריך לראות 151 בקשות לתמונות `book_g42_*`, `book_g45_*`, `wedding.jpg`
- כולן צריכות להיטען עם status 200 (ירוק)
- אם יש שגיאות 404 — סימן שהתמונות לא הועלו ל-GitHub כראוי

---

## פתרון בעיות

### "Image not found" / 404 על התמונות
- וודא שהתיקייה `images/book_images/` קיימת בריפו ב-GitHub
- בדוק ב-https://github.com/asafben33/PerlaBenHarroshCookingBook/tree/main/images/book_images
- אם חסר — חזור על צעד 1-3

### הספר בקורא 3D נופל / נטען לאט
- אנחנו מציגים עכשיו 130+ עמודים עם 151 תמונות
- בפעם הראשונה זה יכול להיטען 5-10 שניות
- כל התמונות עם `loading='lazy'` — נטענות רק כשמתקרבים אליהן
- אם זה איטי מאוד, אפשר להוריד `WORD_BUDGET` ב-index.html (שורה 14095) מ-95 ל-130, ואז יהיו פחות עמודים

### לא רואה גלריות בכלל
- בדוק ב-Console אם יש שגיאות אדומות
- וודא ש-`book_data.js` הועלה (לא רק `index.html`)
- Hard refresh חוזר (Ctrl+Shift+R פעמיים)

---

## תוצאה צפויה

לפני (v8.24):
- 35 תמונות בלבד מתוך 151
- רק `book_g42_*` משולבות
- 116 עמודים בקורא הספר

אחרי (v8.25):
- **151 תמונות** = 100% מהתיקייה
- **11 גלריות חדשות** (אחת לכל פרק)
- ~130-145 עמודים בקורא הספר
- כל תמונה עם alt text תיאורי בעברית ובאנגלית
- Layout responsive (3 בשורה דסקטופ, 2 טאבלט, 1 מובייל)

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
