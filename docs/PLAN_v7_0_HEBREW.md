# תוכנית עבודה — ספר הבישול של פרלה בן-הראש ז״ל

**עודכן אחרון:** 19/04/2026 — לילה
**גרסה נוכחית של האתר:** v7.6 (פרוס מ-v7.5; v7.6 ממתין לפריסה)

---

## סטטוס המחזור הנוכחי — v7.0 הסתיים

מחזור v7.0 הוגדר ב-13/04/2026 ונפרס ב-7 שלבים (v7.0 → v7.6) במהלך 19/04/2026. **כל 10 משימות התוכנית בוצעו**, פלוס 6 תוספות שהמשתמש ביקש במהלך העבודה.

### מה הושלם

| שלב | מה בוצע | תאריך |
|---|---|---|
| **v7.0** | Header אחיד (`hdr-brand-v7`), Hero CTAs, MENU_STRUCTURE שטוח 6-קבוצות, Hero ממורכז | 19/04 |
| **v7.1** | רשת מתכונים מוסתרת בטעינה (`main-hidden`), מתגלה רק אחרי לחיצה/חיפוש | 19/04 |
| **v7.2** | `COMMUNITY_HOLIDAY_TAGS` חדש, 221 תיוגים יחודיים של חגי-עדה | 19/04 |
| **v7.3** | מבנה שטוח של חגים תחת כל עדה + תיקון מרכוז ה-search bar | 19/04 |
| **v7.4** | תיקיית "מאכלי חגים" + "מאכלים מסורתיים" לכל עדה, מימונה הוסרה | 19/04 |
| **v7.5** | Header strip מצומצם ל-1100px (היה 1440) — ממורכז כתוכן | 19/04 |
| **v7.6** | 21 i18n keys ל-DICT, סדר DOM מתוקן, Web3Forms key מוחזר | 19/04 |

### תיקונים קריטיים שנעשו במחזור

1. **Web3Forms key** — היה `'PASTE_YOUR_WEB3FORMS_ACCESS_KEY_HERE'` לאורך כל v7.0-v7.5 ולא תוקן עד v7.6. כעת `'705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'`.
2. **Mimouna בעדות** — הוסרה לחלוטין מ-`COMMUNITY_HOLIDAY_TAGS`. נשארת רק ב-`HOLIDAY_TAGS` של מטעמי אמא (חג מרוקאי בלעדי).
3. **CRLF** — בכל עריכת Python ה-CRLF נשבר ל-LF. תוקן ידנית בכל גרסה.

---

## ארכיטקטורה נוכחית (v7.6)

### תפריט עליון — 6 קבוצות שטוחות

```
1. הכל          (1,054)
2. מרוקו         (671)  — accordion: 8 sub-categories
3. ספרד          (73)
4. עדות ישראל    (270)  — 9 עדות, כל אחת accordion עם 3 פריטים
5. חגים          (80)
6. לא כשר        (40)
```

### מבנה כל עדה (v7.4)

```
עיראק (accordion)
├── כל המתכונים (30)              ← {id:'iraq', lbl:'כל המתכונים'}
├── מאכלים מסורתיים לעדה (3)      ← {lbl:'...', ids:['iq7','iq16','iq23']}
└── מאכלי חגים (תיקיה nested)     ← {lbl:'...', items:[...]}
    ├── שבת (9)                    ← {communityHoliday:'iraq', holidayKey:'shabbat'}
    ├── ראש השנה (5)
    ├── יום כיפור (4)
    ├── פסח (6)
    ├── חנוכה (2)
    ├── פורים (3)
    ├── שבועות (3)
    ├── סוכות (4)
    └── חינה (2)
```

**9 חגים פר-עדה** (mimouna הוסרה — מסורת מרוקאית בלעדית). כל עדה זהה מבנית.

### מבנה כל מתכון (DATA SCHEMA)

```javascript
{
  id: 'unique-id',          // unique within data.js
  cat: 'category-id',       // one of 20 (CATS array)
  badge: 'optional badge',  // displayed on card
  title: 'recipe title',
  desc: 'short description',
  time: 90,                 // minutes
  serv: 4,                  // servings
  diff: 'קל'|'בינוני'|'מתקדם',
  img: 'r-id.jpg',
  mem: 'memory note',
  ingr: [{q:'1 cup', i:'flour'}, ...],
  steps: [{t:'10 min', s:'do this'}, ...],
  tip: 'optional final tip',
  tags: ['optional','tags'],
  h: 'optional holiday key',
  src: 'optional source',
  vid: 'optional video URL'
}
```

### מספרי מתכונים (verified)

| מקור | קטגוריות | מתכונים |
|---|---|---|
| מטעמי אמא ממרוקו | 8 (soups/salads/veg/meat/chick/fish/hol/des) | 671 |
| ספרד | 1 (span) | 73 |
| עדות ישראל | 9 (iraq/kurd/ashk/yem/pers/buk/tun/turk/isr) | 270 |
| לא כשר | 1 (nonkosher) | 40 |
| **סה"כ** | **20** | **1,054** |

---

## מה נותר לעשות (Roadmap לאחר v7.6)

### עדיפות גבוהה

1. **רענון `HOLIDAY_TAGS` של מטעמי אמא** — הקבוע הקיים שגוי לחלוטין. אותם 80 מתכונים מופיעים בדיוק בכל 10 החגים (כנראה data שגויה מתחילה). יש לתייג בפועל מתכוני מרוקו לחג ספציפי באותה גישה כמו v7.2.
2. **i18n מלא של תפריט העדות** — DICT מכיל 21 מפתחות חדשים (v7.6) אבל buildPanel עדיין משתמש ב-`esc(item.lbl)` ישיר. לעבור ל-`t(item.i18n_key)` עם fallback ל-`item.lbl`.
3. **רענון תיוגי `COMMUNITY_HOLIDAY_TAGS`** — תיוג ראשוני ב-82% כיסוי, מבוסס מקורות מתועדים. אם אסף או בני המשפחה רואים שילוב לא נכון, לעדכן ידנית.

### עדיפות בינונית

4. **עדכון תיעוד טכני** — `HLD_Perla_CookingBook.md` ו-`LLD_Perla_CookingBook.md` עדיין מתארים v6.3. סעיף `CLAUDE_md_v7_update.md` נכתב ב-v7.6 אבל לא הוטמע ב-CLAUDE.md.
5. **בדיקת תאימות לעדה השנייה** — האם מסורות שתויגו עובדות גם למשפחות מאזורים שונים באותה עדה (כורדי-זכו vs כורדי-ירושלים)?
6. **תמונות חסרות** — הרבה מתכוני עדות (במיוחד טוניסיה, בוכרה) חסרים תמונה. סקריפט `download_images.py` יכול להוריד אוטומטית.

### עדיפות נמוכה

7. **Sitemap.xml** — לא קיים. SEO מתקדם.
8. **Breadcrumbs** — אין breadcrumbs בעמוד מתכון.
9. **Recipe carousel** — "מתכון יומי" שמתחלף.
10. **Dark/Light theme polish** — בדיקת contrast ב-light mode למרכיבים החדשים של v7.x (`.pc-comm-hol`, `.hdr-brand-v7`).

---

## כללי עבודה מתעדכנים (v7.x)

### לעולם אל

- אל תחזיר את MENU_STRUCTURE למבנה nested של v6.x
- אל תוסיף mimouna ל-`COMMUNITY_HOLIDAY_TAGS` (חג מרוקאי בלעדי)
- אל תסיר `class="main-hidden"` מ-`<main>` (תכונת v7.1)
- אל תשנה `WEB3FORMS_KEY` ל-placeholder — זה מפתח ציבורי-בכוונה
- אל תהפוך את ה-`hdr-search` ל-`flex: 1` (יחזור להיות מתוח)
- אל תחזיר `max-width: 1440` לרצועה העליונה

### תמיד חובה

- כל עריכת Python על `index.html` חייבת להסתיים בנירמול CRLF:
  ```python
  raw = open('index.html', 'rb').read()
  text = raw.replace(b'\r', b'').replace(b'\n', b'\r\n')
  open('index.html', 'wb').write(text)
  ```
- כל commit חייב לעבור `node -c data.js` ו-`node -c` על ה-JS הראשי ב-index.html
- כל גרסה חדשה צריכה CHANGELOG משלה
- pushing ל-git רק עם הפקודות one-at-a-time

### הוספת חג חדש לעדה

ב-`data.js`, מצא `const COMMUNITY_HOLIDAY_TAGS = {`. דוגמה — להוסיף מתכון `iq30` לפסח עיראקי:

```javascript
iraq: {
  // ...
  pesach: ['iq5','iq8','iq14','iq19','iq20','iq24', 'iq30'],
  // ...
},
```

שמור, push, ותוך 30 שניות זה חי.

### הוספת עדה חדשה

מורכב יותר. דורש:
1. הוספת ID חדש ל-`CATS` ב-data.js
2. הוספת 30 מתכונים חדשים עם `cat:'newid'`
3. הוספת בלוק חדש ל-`COMMUNITY_HOLIDAY_TAGS` עם 9 חגים
4. הוספת בלוק חדש ל-MENU_STRUCTURE.communities עם 3 פריטים (כל המתכונים / מסורתיים / חגים)
5. הוספת `nav_<newid>` ל-DICT ולתרגום אוטומטי
6. עדכון מספר הכולל בכל מקום שמופיע "270" → "300"

---

## פקודות בדיקה מהירות

```bash
# Recipe count (must be 1054)
grep -oE "\{id:'[^']+',cat:'\w+'" data.js | wc -l

# Mimouna NOT in communities
grep "mimouna:\['" data.js   # must return 0 in COMMUNITY_HOLIDAY_TAGS section

# Web3Forms key intact
grep -c "705d4207-c4a6-43a2-8fdc-d8e202bc6c9c" index.html  # must be ≥1

# CRLF integrity
python3 -c "raw=open('index.html','rb').read(); print('CRLF',raw.count(b'\r\n'),'LONE',raw.count(b'\n')-raw.count(b'\r\n'))"

# Syntax
node -c data.js
```

---

## פריסה (PowerShell, אחת אחרי השנייה)

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" ".\index.html" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\data.js" ".\data.js" -Force
```
```powershell
git add index.html data.js CHANGELOG_*.md
```
```powershell
git commit -m "v7.x: <description>"
```
```powershell
git push origin main
```

Netlify deploys automatically ~30s אחרי push.

---

## CHANGELOGs קיימים (v7.x)

- `CHANGELOG_19-04-2026_v7_centered_hero.md` — v7.0 + v7.1 (Hero ממורכז + grid-on-demand)
- `CHANGELOG_19-04-2026_v7_2_community_holidays.md` — v7.2 (COMMUNITY_HOLIDAY_TAGS)
- `CHANGELOG_19-04-2026_v7_3_holidays_in_community.md` — v7.3 (חגים בתוך כל עדה)
- `CHANGELOG_19-04-2026_v7_4_holiday_folder.md` — v7.4 (תיקיות + מימונה רק במרוקו)
- `CHANGELOG_19-04-2026_v7_5_centered_header_strip.md` — v7.5 (header strip מצומצם)
- `CHANGELOG_19-04-2026_v7_6_final.md` — v7.6 (i18n + DOM order + Web3Forms fix)

---

## אם צ'אט חדש מתחיל מכאן

1. קרא את **`PLAN_v7_0_ENGLISH.md`** — handoff טכני מלא באנגלית
2. קרא את **`CLAUDE_md_v7_update.md`** — עדכון התיעוד הארכיטקטוני
3. בדוק את `userMemories` בהקשר — מכיל את העדכונים האחרונים
4. עבד נגד התיקיה הזאת בלבד: `https://github.com/asafben33/PerlaBenHarroshCookingBook.git`
5. כל שינוי מתפרס ב: `https://perlabenharrosh-cookingbook.netlify.app/` (Netlify)
6. גם קיים: `https://asafben33.github.io/PerlaBenHarroshCookingBook/` (GitHub Pages, mirror)

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
