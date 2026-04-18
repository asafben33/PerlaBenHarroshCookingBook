# תיעוד תיקונים — גרסה מתוקנת — 18/04/2026

דוח מעודכן לאחר שחזור העיצוב הירוק והחלה מחדש של תיקוני ה-meta tags.

---

## מה הלך לא כשורה בגרסה הקודמת

בגרסה הקודמת ששלחתי לך, ה-`index.html` שעבדתי עליו היה ישן יותר מה-working tree שלך ב-Git. כשהגשתי לך את הקובץ אחרי "Major cleanup", הוא שדרג קדימה את ה-meta tags אבל לא הכיל את השינויים העיצוביים שקיבלת מאוחר יותר ב-commits `ca80475`, `1422637`, `bdb519c`:
- כותרת "משפחת בן הראש **המורחבת**"
- הסרת ה-pills מתחת לכותרת
- כפתור "קרא את הספר" עם toggle של תוכן הספר

**הגרסה הנוכחית מתקנת את זה:** היא מבוססת על `index.html` הירוק ששלחת לי, ועליה הוחלו מחדש אותם 10 תיקוני meta tags — בלי לגעת בשום שורת עיצוב.

---

## קבצים בחבילה

| קובץ | מקור | שינויים |
|---|---|---|
| `index.html` | הגרסה הירוקה ששלחת | 10 תיקוני meta/CSP/CAT_IMG בלבד — אין שינויי עיצוב |
| `data.js` | `/mnt/project/data.js` + תיקונים | הוספת `tip` ל-50 מתכונים, יישור תוויות קטגוריה, ניקוי הערות ריקות |
| `CLAUDE.md` | שכתוב | תיקון שגיאות, עדכון מבנה תיקיות |
| `README.md` | `/mnt/project/README.md` + תיקונים | סנכרון עם מצב נוכחי |
| `_gitignore` | `/mnt/project/_gitignore` + תיקון | הסרת שורה שגויה (שנה ידנית ל-`.gitignore`) |

---

## index.html — 10 תיקוני meta/security בלבד

**אימות:** השוואה בין הגרסה הירוקה שלך לבין הקובץ שאני מגיש — **רק 11 אזורים** של שינוי, וכל אחד מהם מוגדר מראש ב-meta/security/CAT_IMG:

| שורה | שינוי | מה תוקן |
|---|---|---|
| 15 | CSP הודק | `img-src *` → `img-src 'self' data: blob: https://i.ytimg.com https://img.youtube.com` + הוספת `media-src`, `form-action`, `frame-ancestors`, פתיחת `frame-src` ל-YouTube |
| 21–23 | OG image | Wikimedia 320×240 → `images/site_images/og-image.jpg` 1200×630 |
| 25 | Favicon | אמוג׳י 🍲 → 3 קבצי PNG מקומיים (192, 512, apple-touch-icon) |
| 28 | פונטים | הוספת Heebo לצד Frank Ruhl Libre |
| 917 | JSON-LD image | Wikimedia → `og-image.jpg` |
| 920 | JSON-LD author | "אסף בן ארוש" → "אסף בן הראש" |
| 1955 | הערת CAT_IMG | עדכון תיאור |
| 1957–1975 | CAT_IMG (20 URLs) | כולם מ-Wikimedia → `images/site_images/cat-*.jpg` (כולל `nonkosher` שלא היה) |
| 1979 | הערת `_IMG_ALIAS` | `cleanup_hardlinks.ps1` → `cleanup_hardlinks.py` |
| 2988 | @import print CSS | הוספת Heebo |
| 6572 | @import print CSS (שני) | הוספת Heebo |

**לא תוקן (נשמר בדיוק כפי שהיה בגרסה הירוקה):**
- Hero section (שורות 1248–1295) — כותרת "המורחבת", כפתור "קרא את הספר", וכו'
- About section — הפיצול לגרסה ישנה וחדשה
- Book toggle logic — כל הלוגיקה של פתיחה/סגירה של תוכן הספר
- about_redesigned section (~2500 שורות של עיצוב מלא)
- כל ה-JS של פילטרים, חיפוש, תצוגת מתכונים

**אימותים טכניים:**
- Wikimedia refs remaining: 0
- Emoji 🍲 remaining: 0
- "המורחבת" occurrences: 2 (כותרת + i18n)
- "קרא את הספר" occurrences: 2 (כפתור + i18n)
- Heebo refs: 3 (link tag + 2 @import print)
- CRLF line endings: נשמרו
- File size: 360,334 → 359,472 bytes (ירידה של 862 bytes — חיסכון ב-URLs מקומיים)

---

## data.js, CLAUDE.md, README.md, _gitignore

**לא השתנו** מהגרסה שהגשתי לך קודם — הם עצמאיים מ-index.html ותקינים.

הצעתי המוקדמת לגביהם בעינה:
- 50 מתכונים קיבלו `tip` מותאם אישית
- תוויות קטגוריות hol/des יושרו
- שמות תתי-קטגוריות ב"מורשת ספרד" ו"מטבח ישראלי" יושרו ל-README
- הסרת 5 שורות הערה ריקות
- CLAUDE.md ו-README.md סונכרנו עם מבנה התיקיות בפועל
- `_gitignore` תוקן (שורת `proxy_config.txt` נמחקה)

---

## פעולות ידניות נדרשות

### 1. Git commands

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```

שנה את `_gitignore` ל-`.gitignore`:

```powershell
Move-Item _gitignore .gitignore -Force
```

הוסף את כל הקבצים:

```powershell
git add .gitignore CLAUDE.md README.md index.html data.js
```

Commit:

```powershell
git commit -m "Meta/CSP/CAT_IMG hardening + tips for all 1054 recipes + docs sync"
```

Push:

```powershell
git push origin main
```

### 2. העלאת 24 תמונות (לא קריטי)

אם עוד אין ב-`images/site_images/`, צור והעלה:
- `og-image.jpg` (1200×630) — נראה בשיתוף ב-WhatsApp/FB
- `favicon-192.png`, `favicon-512.png`, `apple-touch-icon.png` — אייקוני האתר
- 20 תמונות קטגוריה: `cat-soups.jpg`, `cat-salads.jpg`, `cat-veg.jpg`, `cat-meat.jpg`, `cat-chick.jpg`, `cat-fish.jpg`, `cat-hol.jpg`, `cat-des.jpg`, `cat-span.jpg`, `cat-iraq.jpg`, `cat-kurd.jpg`, `cat-ashk.jpg`, `cat-yem.jpg`, `cat-pers.jpg`, `cat-buk.jpg`, `cat-tun.jpg`, `cat-turk.jpg`, `cat-isr.jpg`, `cat-nonkosher.jpg`, `cat-default.jpg`

אם חסרות — הקוד לא יקרוס, רק ייפול ל-fallback ריק כשתמונת מתכון ספציפית לא זמינה.

### 3. אימות בדפדפן אחרי deploy

1. רענן cache: `Ctrl+Shift+R`
2. פתח https://perlabenharrosh-cookingbook.netlify.app/
3. ודא שרואה:
   - כותרת: "המטבח של משפחת בן הראש **המורחבת**"
   - בלי pills מתחת לכותרת
   - כפתור "קרא את הספר: על שביל האהבה ממרוקו לירושלים"
   - תוכן הספר **מוסתר** עד לחיצה על הכפתור

---

## לקח מהאירוע הזה (בשבילי לעתיד)

- **לוודא state ראשון**: לפני שמתחילים לערוך index.html, להרים בדיקה של תאריכי commit / גרסאות.
- **diff לפני הגשה**: להציג למשתמש את הקבצים שהשתנו לפני הגשה מלאה.
- **לא להניח שהקבצים שקיבלתי מ-`/mnt/project` הם ה-source of truth**: ה-working tree של המשתמש עשוי להיות מקדים יותר.

שוב מצטער על הטעות. הקבצים המעודכנים זמינים להורדה למעלה.
