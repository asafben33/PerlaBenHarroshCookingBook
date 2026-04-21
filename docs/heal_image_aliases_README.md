# heal_image_aliases.py - מדריך שימוש

**תאריך:** 21-04-2026  
**גרסה:** 1.0  
**פרויקט:** ספר המתכונים של פרלה בן-הראש ז"ל

---

## מה הסקריפט עושה?

הסקריפט מתקן באופן אוטומטי שגיאות 404 על תמונות מתכונים שמופיעות בקונסול הדפדפן.

### הבעיה

הסקריפט `download_images.py` בפרויקט מבצע דדופליקציה (הסרת כפילויות) של תמונות — כאשר מאות מתכונים חולקים תמונה זהה, רק עותק אחד נשמר בדיסק, ו-`_IMG_ALIAS.js` ממפה את שאר המתכונים אליו.

**התוצאה הלא-רצויה:** לעיתים הקובץ-היעד עצמו נמחק בטעות, אבל ה-aliases עדיין מצביעים אליו. התוצאה: שגיאות 404 בקונסול כמו:
```
r-add22-2.jpg:1  Failed to load resource: 404 (Not Found)
```

### הפתרון

הסקריפט:
1. סורק את כל 4,980 ה-aliases
2. מזהה את אלה ש-target שלהם לא קיים בדיסק
3. מחפש תמונה חלופית (הגרסה הבסיסית או וריאציה סמוכה)
4. מתקן את `_IMG_ALIAS.js` ואת `index.html` באופן אוטומטי
5. יוצר גיבויים + דוחות מפורטים

---

## דרישות מקדימות

1. **Python 3.10+** מותקן
2. **Node.js** (אופציונלי — לוולידציה של JS)
3. הסקריפט ממוקם ב-root של הפרויקט: `C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook\heal_image_aliases.py`

---

## שימוש

### שלב 1 — Dry-run (בדיקה ללא שינויים)

הרץ תחילה במצב יבש כדי לראות מה יעשה הסקריפט:

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
python heal_image_aliases.py
```

הסקריפט ייצור:
- **לוג:** `logs/heal_image_aliases_DD-MM-YYYY_HH.MM.log`
- **דוח טכני (JSON):** `reports/alias_healing_report_DD-MM-YYYY_HH.MM.json`
- **דוח ידידותי (Markdown):** `reports/alias_healing_report_DD-MM-YYYY_HH.MM.md`

**לא יבוצעו שינויים בקבצים.**

### שלב 2 — קרא את הדוח

פתח את קובץ ה-MD ובדוק:
- כמה aliases שבורים נמצאו?
- אילו targets חסרים?
- האם ההחלפות המוצעות נראות הגיוניות?

### שלב 3 — Apply (ביצוע בפועל)

אחרי שאתה מרוצה מההמלצות:

```powershell
python heal_image_aliases.py --apply
```

הסקריפט יבקש אישור מפורש (הקלד `yes`). לאחר האישור:
1. יצור גיבוי של `_IMG_ALIAS.js` ו-`index.html` ב-`backups/`
2. יעדכן את שני הקבצים
3. יאמת את ה-JS עם Node.js
4. יוציא דוחות מפורטים

### שלב 4 — Deploy

```powershell
git add _IMG_ALIAS.js index.html
git commit -m "Heal broken image aliases - fix 404 errors on recipe images"
git push origin main
```

ואז **רענן את הדפדפן ב-Ctrl+Shift+R**.

---

## דגלים נוספים

| דגל | תיאור |
|---|---|
| (ללא) | Dry-run - לא משנה כלום (ברירת מחדל) |
| `--apply` | מבצע את התיקון (דורש אישור אינטראקטיבי) |
| `--verbose` | לוגים מפורטים יותר |
| `--check-all` | סורק גם את `data.js` אחר references חסרים (נוסף על aliases) |

דוגמאות:

```powershell
# Dry-run עם verbose
python heal_image_aliases.py --verbose

# Apply + check-all
python heal_image_aliases.py --apply --check-all

# סקירה מקיפה במצב יבש
python heal_image_aliases.py --verbose --check-all
```

---

## מה קורה אם משהו משתבש?

### שחזור מגיבוי

כל ריצה ב-`--apply` יוצרת גיבויים ב-`backups/` עם timestamp:

```
backups/_IMG_ALIAS.js.21-04-2026_09.04.43.bak
backups/index.html.21-04-2026_09.04.43.bak
```

לשחזור:

```powershell
# לבדוק מהו הגיבוי האחרון
Get-ChildItem backups/ | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# לשחזר
Copy-Item backups/_IMG_ALIAS.js.21-04-2026_09.04.43.bak _IMG_ALIAS.js -Force
Copy-Item backups/index.html.21-04-2026_09.04.43.bak index.html -Force
```

### JS לא תקף

הסקריפט מוודא JS validity עם Node.js. אם הוולידציה נכשלת:
1. הסקריפט יתריע
2. השינוי ייכתב, אבל תקבל אזהרה להסתכל בגיבוי
3. שחזר מגיבוי והרץ שוב ב-`--verbose` כדי לראות פרטים

### Node.js לא מותקן

אם אין Node.js, הוולידציה מוחלפת באזהרה אך הסקריפט ממשיך לפעול.

---

## לוגיקת ההחלפה

עבור target שבור (למשל `r-add22-2` חסר):

1. **אסטרטגיה 1** — נסה את הגרסה הבסיסית: `r-add22` (ללא `-2`)
2. **אסטרטגיה 2** — נסה וריאציות סמוכות: `r-add22-3`, `r-add22-4`, `r-add22-5`...
3. **אסטרטגיה 3** — כל קובץ עם אותו prefix
4. **אסטרטגיה 4** — אם אין כלום, הסר את ה-alias כך שהמתכון יפול לתמונת הקטגוריה

---

## אבטחה ואמינות

| הגנה | תיאור |
|---|---|
| Dry-run as default | הסקריפט לא משנה כלום בלי `--apply` מפורש |
| Interactive confirm | גם עם `--apply` נדרש הקלדה של `yes` |
| Backup מלא | כל קובץ המתעדכן מגובה ב-`backups/` |
| Validation JS | Node.js נקרא אחרי כל שינוי |
| UTF-8 תומך בעברית | כל הלוגים והדוחות ב-UTF-8 |
| Logging מלא | כל פעולה מתועדת בקובץ לוג |
| סיכום בסוף | הסקריפט מדווח בדיוק מה בוצע |

---

## תמיכה

אם משהו לא ברור או לא עובד:
1. הרץ שוב עם `--verbose`
2. בדוק את `logs/heal_image_aliases_*.log` - הוא מכיל את כל הפרטים
3. שחזר מגיבוי ופנה לתמיכה

---

## מבנה תיקיות שנוצר אוטומטית

```
PerlaBenHarroshCookingBook/
├── heal_image_aliases.py         (הסקריפט)
├── _IMG_ALIAS.js                  (יעודכן)
├── index.html                     (יעודכן)
├── data.js                        (נקרא)
├── images/
│   └── recipes_images/             (נסרק)
├── logs/                           (נוצר אוטומטית)
│   └── heal_image_aliases_*.log
├── reports/                        (נוצר אוטומטית)
│   ├── alias_healing_report_*.json
│   └── alias_healing_report_*.md
└── backups/                        (נוצר רק במצב --apply)
    ├── _IMG_ALIAS.js.*.bak
    └── index.html.*.bak
```
