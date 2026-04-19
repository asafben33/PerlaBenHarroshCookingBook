# CLAUDE.md — תוספת לעדכון v7.0 → v7.6

**הוסף את הסעיף הזה ל-CLAUDE.md הקיים, מתחת לסעיף האחרון הקיים.
או החלף את כל הסעיפים שמתייחסים ל-v6.x במידע מ-v7.x להלן.**

---

## ארכיטקטורה — v7.0 → v7.6 (אפריל 2026)

### תפריט שטוח עם 6 קבוצות עליונות (v7.0)

`MENU_STRUCTURE` ב-`data.js` שוכתב מחדש מבסיס. במקום wrapper יחיד "all_master" עם 4 רמות nested, עכשיו 6 קבוצות עליונות:

```
1. הכל          (id:'all')        — leaf, 1054 מתכונים
2. מרוקו         (key:'morocco')   — 8 sub: soups/salads/veg/meat/chick/fish/hol/des
3. ספרד          (id:'span')       — leaf, 73 מתכונים
4. עדות ישראל    (key:'communities') — 9 עדות, כל אחת accordion עם 3 פריטים (v7.4)
5. חגים          (id:'hol')        — leaf, 80 מתכונים מרוקאיים
6. לא כשר        (id:'nonkosher')  — leaf, 40 מתכונים
```

### Header brand + Hero CTAs (v7.0)

- `<div class="hdr-brand-v7">` בראש ה-header עם שם הספר + ספירת מתכונים דינמית מ-`R.length`
- `<div class="hero-cta-row">` עם 2 כפתורים: "עיון במתכונים" (אדום) → reveal grid + scroll, "קרא את הספר" (זהוב) → scroll ל-#book-wrapper
- 4 פונקציות גלובליות חדשות: `window.showMainGrid()`, `window.hideMainGrid()`, `window.initHdrCount()`, `window.initHeroCTAs()`

### Grid-on-demand (v7.1)

`<main id="main" class="main-hidden">` כברירת מחדל. רשת המתכונים מוסתרת בטעינה. מתגלה רק אחרי:
- לחיצה על קטגוריה ב-nav (`selectCat`/`selectMulti`/`selectByIds` קוראים ל-`showMainGrid()` כצעד ראשון)
- חיפוש (כש-SEARCH truthy ב-`doSearch`)
- לחיצה על כפתור "עיון במתכונים" ב-Hero

### חגים פר-עדה (v7.2 → v7.4)

קבוע חדש `COMMUNITY_HOLIDAY_TAGS` ב-`data.js` (לפני `MENU_STRUCTURE`):

```javascript
const COMMUNITY_HOLIDAY_TAGS = {
  iraq: { shabbat:[...], rosh:[...], kippur:[...], pesach:[...],
          hanukkah:[...], purim:[...], shavuot:[...], sukkot:[...], henna:[...] },
  kurd: { ... },  ashk: { ... },  yem: { ... },
  pers: { ... },  buk:  { ... },  tun:  { ... },
  turk: { ... },  isr:  { ... }
};
```

**9 חגים** (mimouna הוסר מעדות — הוא מסורת מרוקאית בלעדית, נשאר רק ב-`HOLIDAY_TAGS` של מטעמי אמא). **221 תיוגים יחודיים** מתוך 270 מתכוני עדות (82% כיסוי). 49 מתכונים שלא תויגו לאף חג מופיעים תחת "מאכלים מסורתיים לעדה".

### מבנה כל עדה (v7.4)

```
עיראק (accordion)
├── כל המתכונים (30)              ← {id:'iraq', lbl:'כל המתכונים'}
├── מאכלים מסורתיים לעדה (3)      ← {lbl:'...', ids:['iq7','iq16','iq23']}
└── מאכלי חגים (תיקיה nested)     ← {lbl:'...', items:[...]}
    ├── שבת (9)                    ← {communityHoliday:'iraq', holidayKey:'shabbat', lbl:'שבת'}
    ├── ראש השנה (5)
    ├── יום כיפור (4)
    ├── פסח (6)
    ├── חנוכה (2)
    ├── פורים (3)
    ├── שבועות (3)
    ├── סוכות (4)
    └── חינה (2)
```

חגים עם 0 תיוגים מופיעים אפורים-שקופים (`.pc-empty`) ומציגים toast במקום לחיצה ריקה.

### buildPanel — תמיכה ב-3 רמות nesting

הוספתי 3 branches ב-`buildPanel`:
1. רמה 1 (`item.communityHoliday`) — כפתור ישיר בפאנל
2. רמה 2 (`s.communityHoliday`) — בתוך accordion body של עדה
3. רמה 3 (`ns.communityHoliday`) — בתוך nested accordion ("מאכלי חגים" → 9 חגים)

כל branch יוצר `<button class="pc pc-comm-hol">` עם הטיפול הזהה (toast לריקים, `selectCommunityHoliday()` לפעילים).

### `selectCommunityHoliday(community, holidayKey, label, groupKey)` — JS function חדש

מסנן את הרשת לפי `COMMUNITY_HOLIDAY_TAGS[community][holidayKey]`. אם המערך ריק → מציג toast ולא משנה את המצב. אחרת מגדיר `ACT_IDS = new Set(ids)`, מעדכן `ACT_CAT` ו-`ACT_HOLIDAY`, מעדכן `sec-title` בפורמט `<עדה> — <חג>`.

### עיצוב — מרכוז + כפתורי חגים

- `.hero-inner { margin: 0 auto; text-align: center }` (v7.0) — Hero ממורכז
- `.hdr-inner { max-width: 1100px; justify-content: space-between }` (v7.5) — header strip מצומצם וממורכז (היה 1440px)
- `.cat-nav-inner { max-width: 1100px; justify-content: center }` (v7.5) — אותו דבר ל-nav
- `.nav-panel-inner { max-width: 1100px }` (v7.5) — אותו דבר לפאנל הנפתח
- `.hdr-search { flex: 0 1 480px; max-width: 480px; margin: 0 auto }` (v7.3) — חיפוש לא נמתח
- `.pc-comm-hol` — כפתור חג של עדה: רקע אדום-אלמוגי `rgba(184,66,35,.10)`, טקסט `#d4603a`
- `.pc-empty` — opacity .5 + cursor: help לחגים ריקים
- `.main-hidden { display: none !important }` (v7.1) — הסתרת רשת בטעינה

### סדר ה-DOM (v7.6)

```
Hero (1675) → Bio (1689) → Main (1707) → Book (1733) → About (1768)
```

`<main>` הוזז מאחרי About לאחרי Bio — המשתמש רואה את רשת המתכונים מיד אחרי ה-Bio במקום אחרי גלילה דרך הספר וה-About.

### i18n — 21 מפתחות חדשים ב-DICT (v7.6)

```javascript
site_name_short, recipes_label, hero_cta_browse, hero_cta_book,
nav_morocco, nav_communities, nav_holidays,
community_all, community_traditional, community_holidays_folder,
holiday_shabbat, holiday_rosh, holiday_kippur, holiday_pesach,
holiday_mimouna, holiday_hanukkah, holiday_purim,
holiday_shavuot, holiday_sukkot, holiday_henna,
toast_no_recipes_holiday
```

הוספתי לאחר `pwa_aria` ולתוך section "Navigation categories" של ה-DICT.

---

## כללים נוספים — v7.x

### הזרקת תיוגים — שקיפות

`COMMUNITY_HOLIDAY_TAGS` הוא **תיוג ראשוני מבוסס מקורות מתועדים** של מטבח יהודי-ספרדי/מזרחי/אשכנזי, לא ידע משפחתי אישי. וריאציות בין משפחות וקהילות הן צפויות. אם אסף או בני המשפחה רואים שילוב לא נכון — לעדכן ידנית במערך הרלוונטי.

### Mimouna — מסורת מרוקאית בלעדית

לעולם לא לשים `mimouna` ב-`COMMUNITY_HOLIDAY_TAGS`. החג קיים רק ב-`HOLIDAY_TAGS` של מטעמי אמא (74 מתכוני מרוקו). ב-v7.4 הסרתי 6 תיוגי מימונה שהיו תחת `tun` בטעות.

### CRLF — אובדן בכל עריכת Python

כל פעם שעורכים את `index.html` עם Python שקורא בטקסט-מצב, ה-CRLF נשבר ל-LF. החובה לסיים כל עריכה עם:
```python
raw = open('index.html', 'rb').read()
text = raw.replace(b'\r', b'').replace(b'\n', b'\r\n')
open('index.html', 'wb').write(text)
```

### WEB3FORMS_KEY — ציבורי בכוונה

`WEB3FORMS_KEY = '705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'` ב-`index.html` ~שורה 12374.

זה מפתח **ציבורי בכוונה** — Web3Forms דורש מפתח client-side. אסור להחליף ב-`PASTE_YOUR_WEB3FORMS_ACCESS_KEY_HERE`. ב-v7.6 גיליתי שהוא הוחלף ב-placeholder באחת העריכות והחזרתי. תמיד לבדוק עם `grep -c "705d4207"` לפני pushing.

### חוקי buildPanel

המבנה תומך ב-3 רמות nesting בלבד. אל תיצור MENU_STRUCTURE עם 4+ רמות. אם צריך עומק רב יותר, להשתמש ב-`{placeholder:'...', lbl:'...'}` כדי להציג toast במקום, או לשטח את המבנה.

---

## אדריכלות מובל v6.10 → v7.6 — מה השתנה

| תחום | v6.10 | v7.6 |
|---|---|---|
| MENU_STRUCTURE | wrapper יחיד 4-רמות nested | flat 6-קבוצות עליונות |
| Recipe grid | תמיד גלוי בטעינה | מוסתר עד nav/search/CTA |
| Header layout | brand בכותרת, search מתוח | brand+search+tools מאוזנים, max-width 1100 |
| Hero | text-align: right | text-align: center, ממורכז במלואו |
| Per-cuisine holidays | לא קיים | 9 עדות × 9 חגים, 221 תיוגים יחודיים |
| Community subtree | flat (30 מתכונים) | accordion עם 3 פריטים (כל/מסורתיים/חגים) |
| DOM section order | Hero→Bio→Book→About→Main | Hero→Bio→Main→Book→About |
| i18n keys | ~130 | ~150 (21 חדשים ב-v7.6) |

---

## פקודות טסטים מהירות

```bash
# Syntax checks
node -c data.js

# Recipe count (must be 1054)
grep -oE "\{id:'[^']+',cat:'\w+'" data.js | wc -l

# Mimouna NOT in communities
grep "mimouna:\['" data.js   # should return ZERO matches in COMMUNITY_HOLIDAY_TAGS

# Web3Forms key intact
grep -c "705d4207-c4a6-43a2-8fdc-d8e202bc6c9c" index.html  # ≥1

# CRLF integrity (Python)
python3 -c "raw=open('index.html','rb').read(); print('CRLF',raw.count(b'\r\n'),'LONE',raw.count(b'\n')-raw.count(b'\r\n'))"
```

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
