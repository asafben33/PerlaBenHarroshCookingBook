# CHANGELOG — v8.15: שינוי שם תפריט "עדות ישראל" → "מתכונים טעימים מעוד עדות"

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.15

---

## הבקשה

> תשנה את הכיתוב בתפריט מ"עדות ישראל" ל"מתכונים טעימים מעוד עדות"

הטקסט החדש יותר מזמין וברור — הוא מתאר מה המבקר ימצא שם (מתכונים טעימים) ומאיפה (מעוד עדות, רמיזה לכך שיש כבר "מרוקו\\ספרד" הראשי).

---

## השינויים

### 1. `data.js` — `MENU_STRUCTURE` (התווית הראשית בתפריט)

```javascript
// היה
{lbl:'עדות ישראל', key:'communities', items:[ ... ]}

// עכשיו
{lbl:'מתכונים טעימים מעוד עדות', key:'communities', items:[ ... ]}
```

זה הטקסט שמופיע בכפתור התפריט הראשי — כשמשתמש רואה את התפריט, יראה את הטקסט החדש.

### 2. `index.html` — `DICT` (תרגום עברי + אנגלי)

```javascript
// היה
nav_communities: {he:'עדות ישראל', en:'Jewish Communities'}

// עכשיו
nav_communities: {he:'מתכונים טעימים מעוד עדות', en:'Tasty Recipes from Other Communities'}
```

### 3. `index.html` — מפת `_NAV_I18N` (label-to-key mapping)

```javascript
// היה — שורה אחת
'מרוקו':'nav_morocco','עדות ישראל':'nav_communities','חגים':'nav_holidays',

// עכשיו — מבנה מפורש עם תאימות אחורה
'מרוקו':'nav_morocco',
'מתכונים טעימים מעוד עדות':'nav_communities',  /* v8.15 - new label */
'עדות ישראל':'nav_communities',                  /* legacy - kept for back-compat */
'חגים':'nav_holidays',
```

**שמרתי את ה-`עדות ישראל` הישן כ-back-compat key** כי יכול להיות שיש אזורים בקוד שעדיין בודקים את התווית הישנה (למשל URL hashes, bookmarks). זה לא משפיע על UX — רק וודאות שאם משהו קורא את הטקסט הישן, ימצא את ה-translation.

### 4. `data.js` — הערה מעודכנת

ההערה שמתארת את הסקציה `/* 4. עדות ישראל ... */` עודכנה ל-`/* 4. מתכונים טעימים מעוד עדות ... v8.15: renamed from 'עדות ישראל' ... */`.

---

## רוחב התפריט

| תפריט | טקסט | אורך | רוחב משוער |
|---|---|---|---|
| הכל | "הכל" | 3 תווים | ~80px |
| מרוקו\\ספרד | "מרוקו\\ספרד" | 10 תווים | ~190px |
| **מתכונים טעימים מעוד עדות** | 24 תווים | **~360px** |
| לא כשר | "לא כשר" | 6 תווים | ~140px |

**סה"כ:** ~770px. מתאים לחלוטין לרוחב שולחני (מסך 1280px+).

**מובייל:** התפריט משתמש ב-`flex-wrap`, ולכן במסכים צרים הוא יעטוף לשורות מרובות אם יש צורך.

---

## בדיקות שעברו (5/5)

```
✓ index.html JS syntax: OK
✓ data.js JS syntax: OK
✓ index.html CRLF: 13,559 שורות (100%, 0 lone LF)
✓ index.html DICT updated (HE + EN)
✓ index.html i18n map - new label present
✓ index.html i18n map - legacy back-compat present
✓ data.js MENU_STRUCTURE updated
✓ Old 'עדות ישראל' lbl in data.js: REMOVED (still in legacy i18n map)
```

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | DICT עודכן + מפת i18n labels הורחבה |
| `data.js` | ה-`lbl` הראשי של communities עודכן + הערה מעודכנת |

`download_images.py`, `find_videos.py`, `sw.js`, `sitemap.xml`, `robots.txt` — **לא נגעתי**.

---

## פריסה

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\data.js" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_15_menu_rename.md" "." -Force
```
```powershell
git add index.html data.js CHANGELOG_20-04-2026_v8_15_menu_rename.md
```
```powershell
git commit -m "v8.15: rename menu 'עדות ישראל' to 'מתכונים טעימים מעוד עדות' (more inviting label)"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

1. **התפריט הראשי** — לחץ ובדוק שהכפתור השלישי מציג את הטקסט החדש "מתכונים טעימים מעוד עדות"
2. **לחיצה על הכפתור** — אמורה לפתוח את אותו תפריט נפתח עם 9 העדות (עיראק, כורדיסטן, אשכנז, תימן, פרס, בוכרה, טוניס, ישראל, טורקיה)
3. **EN mode** — לחץ EN, הכפתור אמור להציג "Tasty Recipes from Other Communities"
4. **מובייל** — בדוק שהתפריט עדיין נגיש (אם יש flex-wrap זה יעבור לשורות נפרדות)
5. **כפתור "הכל"** — מציג עדיין 1056 מתכונים (כל המספרים נשמרים)
6. **לחיצה על קטגוריה** מתוך התפריט החדש (למשל "עיראק") — צריכה להציג את 30 מתכוני העדה כרגיל

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
