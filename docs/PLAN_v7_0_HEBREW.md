# תוכנית עבודה — ספר הבישול של פרלה בן-הראש ז״ל

**עודכן אחרון:** 19/04/2026 — סוף לילה
**גרסה נוכחית של האתר:** v7.9 (פרוס מ-v7.5; v7.6-v7.9 ממתינים לפריסה)

---

## סטטוס המחזור הנוכחי — v7.0 הושלם, v7.7-v7.9 בוצעו

מחזור v7.0 הוגדר ב-13/04/2026 ונפרס ב-10 שלבים (v7.0 → v7.9) במהלך 19/04/2026. **כל המשימות הראשוניות בוצעו**, פלוס מספר תוספות שהמשתמש ביקש במהלך העבודה.

### היסטוריית גרסאות מלאה

| שלב | מה בוצע | תאריך |
|---|---|---|
| **v7.0** | Header אחיד (`hdr-brand-v7`), Hero CTAs, MENU_STRUCTURE שטוח 6-קבוצות, Hero ממורכז | 19/04 |
| **v7.1** | רשת מתכונים מוסתרת בטעינה (`main-hidden`), מתגלה רק אחרי לחיצה/חיפוש | 19/04 |
| **v7.2** | `COMMUNITY_HOLIDAY_TAGS` חדש, 221 תיוגים יחודיים של חגי-עדה | 19/04 |
| **v7.3** | מבנה שטוח של חגים תחת כל עדה + תיקון מרכוז ה-search bar | 19/04 |
| **v7.4** | תיקיית "מאכלי חגים" + "מאכלים מסורתיים" לכל עדה, מימונה הוסרה מעדות | 19/04 |
| **v7.5** | Header strip מצומצם ל-1100px (היה 1440) — ממורכז כתוכן | 19/04 |
| **v7.6** | 21 i18n keys ל-DICT, סדר DOM מתוקן, Web3Forms key מוחזר | 19/04 |
| **v7.7** | רענון `HOLIDAY_TAGS` של מרוקו — מ-80×10 חזרות זהות ל-121 תיוגים יחודיים | 19/04 |
| **v7.8** | הסרת כפתור "חגים" העליון הכפול, תיקיית חגים תחת מרוקו עם 10 חגים | 19/04 |
| **v7.9** | איחוד "מרוקו" + "ספרד" ל-"מרוקו\\ספרד" (מורשת קארו 1492) | 19/04 |

### תיקונים קריטיים שנעשו במחזור

1. **Web3Forms key** (v7.6) — היה `'PASTE_YOUR_WEB3FORMS_ACCESS_KEY_HERE'` לאורך כל v7.0-v7.5 ולא תוקן עד v7.6. כעת `'705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'`.
2. **Mimouna בעדות** (v7.4) — הוסרה לחלוטין מ-`COMMUNITY_HOLIDAY_TAGS`. נשארת רק ב-`HOLIDAY_TAGS` של מטעמי אמא.
3. **HOLIDAY_TAGS שגוי** (v7.7) — היה אותם 80 מתכונים בכל 10 החגים. תוקן לתיוג אמיתי לפי כותרות וfסורות.
4. **כפילות "חגים" בתפריט** (v7.8) — קטגוריה עליונה "חגים" + sub-category "חגים ומועדים" תחת מרוקו. הקטגוריה העליונה הוסרה.
5. **CRLF** — בכל עריכת Python ה-CRLF נשבר ל-LF. תוקן ידנית בכל גרסה.

---

## ארכיטקטורה נוכחית (v7.9)

### תפריט עליון — 4 קבוצות שטוחות (היה 6 ב-v7.0)

```
1. הכל              (1,054)
2. מרוקו\ספרד       (744)  — accordion: 11 sub-items (מרוקו 671 + ספרד 73)
3. עדות ישראל       (270)  — 9 עדות, כל אחת accordion עם 3 פריטים
4. לא כשר           (40)
```

**שינויים מ-v7.0:**
- v7.8 הסיר את "חגים" כקטגוריה עליונה (עבר להיות תת-קטגוריה במרוקו)
- v7.9 איחד "מרוקו" + "ספרד" לכפתור אחד

### מבנה "מרוקו\\ספרד" (v7.9)

```
מרוקו\ספרד (744 מתכונים)
├── כל מתכוני מרוקו וספרד (744)         ← מציג שני המטבחים יחד
├── מרקים (103)
├── סלטים (103)
├── תבשילי ירקות (87)
├── בשר וקציצות (82)
├── עוף ושבת (66)
├── דגים (70)
├── חגים ומועדים (תיקיה nested) ← v7.8
│   ├── כל מתכוני החגים (80)
│   ├── שבת (54)
│   ├── ראש השנה (14)
│   ├── יום כיפור (0)
│   ├── פסח (4)
│   ├── מימונה (7)                       ← מופלטה!
│   ├── חנוכה (2)
│   ├── פורים (1)
│   ├── שבועות (12)
│   ├── סוכות (27)
│   └── חינה (14)
├── קינוחים ומאפים (80)
└── ספרד (אנדלוסי) (73)                 ← רק מתכוני ספרד
```

### מבנה כל עדה (v7.4 — נשמר)

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
| ספרד (אנדלוסי) | 1 (span) | 73 |
| **סה"כ מרוקו\\ספרד** | **9** | **744** |
| עדות ישראל | 9 (iraq/kurd/ashk/yem/pers/buk/tun/turk/isr) | 270 |
| לא כשר | 1 (nonkosher) | 40 |
| **סה"כ** | **20** | **1,054** |

### מבני ה-data השונים (v7.9)

| קבוע | מטרה | תוכן |
|---|---|---|
| `R` | מערך כל המתכונים | 1,054 אובייקטים |
| `CATS` | רשימת קטגוריות | 20 קטגוריות עם labels |
| `MENU_STRUCTURE` | מבנה התפריט הראשי | 4 קבוצות עליונות (v7.9) |
| `HOLIDAY_TAGS` | חגי מרוקו | 10 חגים → IDs (v7.7 תיקן) |
| `COMMUNITY_HOLIDAY_TAGS` | חגי 9 העדות | עדה × חג → IDs (v7.4) |
| `DICT` | מילון UI | ~150 מפתחות (21 חדשים ב-v7.6) |

---

## מה נותר לעשות (Roadmap לאחר v7.9)

### עדיפות גבוהה

1. **i18n מלא של תפריט העדות** — DICT מכיל 21 מפתחות חדשים (v7.6) אבל buildPanel עדיין משתמש ב-`esc(item.lbl)` ישיר. לעבור ל-`t(item.i18nKey || item.lbl)` עם fallback. זה מאפשר תרגום מלא לאנגלית של כל פריטי התפריט.

2. **רענון תיוגי `COMMUNITY_HOLIDAY_TAGS`** — תיוג ראשוני ב-82% כיסוי, מבוסס מקורות מתועדים. אם אסף או בני המשפחה רואים שילוב לא נכון, לעדכן ידנית.

3. **רענון תיוגי `HOLIDAY_TAGS` של מרוקו** — תיקון v7.7 הוא אוטומטי מבוסס regex על כותרות. ייתכן שיש false negatives (מתכון שצריך להיות מתויג ולא תויג). דורש בדיקה.

### עדיפות בינונית

4. **עדכון תיעוד טכני** — `HLD_Perla_CookingBook.md` ו-`LLD_Perla_CookingBook.md` עדיין מתארים v6.3. סעיף `CLAUDE_md_v7_update.md` נכתב ב-v7.6 אבל לא הוטמע ב-CLAUDE.md.

5. **בדיקת תאימות לעדה השנייה** — האם מסורות שתויגו עובדות גם למשפחות מאזורים שונים באותה עדה (כורדי-זכו vs כורדי-ירושלים)?

6. **תמונות חסרות** — הרבה מתכוני עדות (במיוחד טוניסיה, בוכרה) חסרים תמונה. סקריפט `download_images.py` יכול להוריד אוטומטית.

### עדיפות נמוכה

7. **Sitemap.xml** — לא קיים. SEO מתקדם.
8. **Breadcrumbs** — אין breadcrumbs בעמוד מתכון.
9. **Recipe carousel** — "מתכון יומי" שמתחלף.
10. **Dark/Light theme polish** — בדיקת contrast ב-light mode למרכיבים החדשים של v7.x (`.pc-comm-hol`, `.hdr-brand-v7`).

### בוצע — לא להתחיל מחדש

- ~~רענון `HOLIDAY_TAGS` של מטעמי אמא~~ ✅ v7.7
- ~~הסרת כפילות "חגים" בתפריט~~ ✅ v7.8
- ~~איחוד מרוקו וספרד~~ ✅ v7.9
- ~~i18n keys ל-DICT~~ ✅ v7.6 (החיבור לתפריט עדיין נדרש)
- ~~Hero centering~~ ✅ v7.0
- ~~Header strip centering~~ ✅ v7.5
- ~~Grid-on-demand~~ ✅ v7.1
- ~~Holiday folder per community~~ ✅ v7.4
- ~~Mimouna removed from communities~~ ✅ v7.4
- ~~Web3Forms key restored~~ ✅ v7.6

---

## כללי עבודה מתעדכנים (v7.x)

### לעולם אל

- אל תחזיר את MENU_STRUCTURE למבנה nested של v6.x
- אל תוסיף mimouna ל-`COMMUNITY_HOLIDAY_TAGS` (חג מרוקאי בלעדי)
- אל תסיר `class="main-hidden"` מ-`<main>` (תכונת v7.1)
- אל תשנה `WEB3FORMS_KEY` ל-placeholder — זה מפתח ציבורי-בכוונה
- אל תהפוך את ה-`hdr-search` ל-`flex: 1` (יחזור להיות מתוח)
- אל תחזיר `max-width: 1440` לרצועה העליונה
- **חדש (v7.7):** אל תחזיר את `HOLIDAY_TAGS` למבנה הישן (אותם 80 מתכונים בכל חג) — זה היה bug מקורי
- **חדש (v7.8):** אל תוסיף בחזרה `{id:'hol', lbl:'חגים'}` כקטגוריה עליונה — זה כפול
- **חדש (v7.9):** אל תפריד את "מרוקו" ו"ספרד" לכפתורים נפרדים — הם מאוחדים תרבותית (משפחת קארו)

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

### הוספת חג חדש למרוקו (v7.7+)

ב-`data.js`, מצא `const HOLIDAY_TAGS = {`. דוגמה — להוסיף `me5` לפסח:

```javascript
const HOLIDAY_TAGS = {
  // ...
  pesach: ['fin12','hle2','holf4','hn24', 'me5'],
  // ...
};
```

### הוספת עדה חדשה

מורכב יותר. דורש:
1. הוספת ID חדש ל-`CATS` ב-data.js
2. הוספת 30 מתכונים חדשים עם `cat:'newid'`
3. הוספת בלוק חדש ל-`COMMUNITY_HOLIDAY_TAGS` עם 9 חגים
4. הוספת בלוק חדש ל-MENU_STRUCTURE.communities עם 3 פריטים (כל המתכונים / מסורתיים / חגים)
5. הוספת `nav_<newid>` ל-DICT ולתרגום אוטומטי
6. עדכון מספר הכולל בכל מקום שמופיע "270" → "300"

---

## פקודות בדיקה מהירות (v7.9)

```bash
# Recipe count (must be 1054)
grep -oE "\{id:'[^']+',cat:'\w+'" data.js | wc -l

# Mimouna NOT in communities
grep "mimouna:\['" data.js   # must return 0 in COMMUNITY_HOLIDAY_TAGS section

# Web3Forms key intact
grep -c "705d4207-c4a6-43a2-8fdc-d8e202bc6c9c" index.html  # must be ≥1

# v7.7: HOLIDAY_TAGS shabbat ≠ pesach (must be different)
python3 -c "
import re
d = open('data.js', encoding='utf-8').read()
m = re.search(r'const HOLIDAY_TAGS = \{(.*?)\n\};', d, re.DOTALL)
sha = re.search(r\"shabbat:\[(.*?)\]\", m.group(1)).group(1)
pes = re.search(r\"pesach:\[(.*?)\]\", m.group(1)).group(1)
print('SAME (BAD):', sha == pes)  # must be False
"

# v7.8: No top-level חגים entry
grep -c "^\s*{id:'hol', lbl:'חגים'}" data.js   # must be 0

# v7.9: Morocco/Spain merged
grep -c "morocco_span\|מרוקו\\\\ספרד" data.js   # must be ≥2

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

## CHANGELOGs קיימים (v7.x — 9 קבצים)

- `CHANGELOG_19-04-2026_v7_centered_hero.md` — v7.0 + v7.1 (Hero ממורכז + grid-on-demand)
- `CHANGELOG_19-04-2026_v7_2_community_holidays.md` — v7.2 (COMMUNITY_HOLIDAY_TAGS)
- `CHANGELOG_19-04-2026_v7_3_holidays_in_community.md` — v7.3 (חגים בתוך כל עדה)
- `CHANGELOG_19-04-2026_v7_4_holiday_folder.md` — v7.4 (תיקיות + מימונה רק במרוקו)
- `CHANGELOG_19-04-2026_v7_5_centered_header_strip.md` — v7.5 (header strip מצומצם)
- `CHANGELOG_19-04-2026_v7_6_final.md` — v7.6 (i18n + DOM order + Web3Forms fix)
- `CHANGELOG_19-04-2026_v7_7_holiday_tags_fix.md` — v7.7 (HOLIDAY_TAGS תיקון)
- `CHANGELOG_19-04-2026_v7_8_remove_duplicate_holidays.md` — v7.8 (הסרת כפילות חגים)
- `CHANGELOG_19-04-2026_v7_9_morocco_spain_merge.md` — v7.9 (איחוד מרוקו וספרד)

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
