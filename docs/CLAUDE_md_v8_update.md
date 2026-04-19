# CLAUDE.md — תוספת עדכון v7.x → v8.0

**הוסף את הסעיף הזה ל-CLAUDE.md הקיים, מתחת לסעיף האחרון הקיים.**
**קובץ זה ממשיך את `CLAUDE_md_v7_update.md` שנכתב ב-v7.6.**

---

## מחזור v7.7 → v8.0 (אפריל 2026 — סוף החודש)

### v7.7 — תיקון `HOLIDAY_TAGS` של מטעמי אמא

`HOLIDAY_TAGS` הקיים היה **שגוי לחלוטין** — אותם 80 מתכונים בכל 10 החגים. תוצאה: לחיצה על "מימונה" הציגה את אותם מתכונים שהציגה לחיצה על "פסח".

**הפתרון:** תיוג אמיתי מבוסס regex על כותרות 671 מתכוני מרוקו + מסורת יהודית-מרוקאית מתועדת.

```javascript
const HOLIDAY_TAGS = {
  shabbat:  [54 recipes],   // טאג'ין, חמין, סקינה, פסטייה, חלה
  rosh:     [14 recipes],   // דבש, רימון, דלעת מתוק
  kippur:   [],             // אין מתכון מרוקאי-יהודי ספציפי במאגר
  pesach:   [4 recipes],    // חרוסת, מצה
  mimouna:  [7 recipes],    // מופלטה!, פרנה מימונה, ריבות
  hanukkah: [2 recipes],    // ספינג', סופגניות
  purim:    [1 recipe],     // אוזני המן
  shavuot:  [12 recipes],   // גבינות, מאפי גבינה
  sukkot:   [27 recipes],   // ירקות ממולאים
  henna:    [14 recipes]    // מתכוני טקס חתונה
};
```

**121 תיוגים יחודיים / 671 מתכוני מרוקו (18%).**

### v7.8 — הסרת כפילות "חגים" + סידור תחת מרוקו

הקטגוריה "חגים" הייתה כפתור עליון נפרד עם 80 מתכונים, **באותו זמן** שמרוקו כבר כללה sub-category "חגים ומועדים". כפילות מובהקת.

**הפתרון:** הסרת ה-leaf העליון; המרת ה-leaf "חגים ומועדים" תחת מרוקו ל-folder עם 11 פריטים (כל מתכוני החגים + 10 חגים נפרדים, באמצעות `h:` parameter).

```javascript
{lbl:'חגים ומועדים', items:[
  {id:'hol', lbl:'כל מתכוני החגים'},
  {id:'hol', h:'shabbat',  lbl:'שבת'},
  // ... 9 חגים נוספים
]}
```

### v7.9 — איחוד מרוקו + ספרד

המטבח של פרלה משלב מרוקו וספרד אצל פרלה (משפחת קארו, מגורשי ספרד 1492). אין סיבה להפריד בתפריט.

**הפתרון:** איחוד ל-`{lbl:'מרוקו\\ספרד', key:'morocco_span', items:[...]}` עם:
- "כל מתכוני מרוקו וספרד" (744) — `selectMulti(['soups','salads',...,'span'])`
- 7 sub-categories של מרוקו
- "חגים ומועדים" folder
- "ספרד (אנדלוסי)" sub-item

**התפריט הראשי כעת מציג 4 קטגוריות במקום 6.**

### v8.0 — חיווט i18n מלא של תפריט העדות

ה-DICT הכיל 21 keys ב-v7.6 אבל לא היה wired לתפריט. תיקנתי בכך שהרחבתי את `_NAV_I18N` (mapping של תוויות עבריות → מפתחות i18n) עם הוספות חדשות מ-v7.x. כעת `applyLang('en')` מתרגם **גם** את הפריטים החדשים: "מרוקו\\ספרד" → "Morocco / Spain", "מאכלי חגים" → "Holiday Dishes" וכו'.

**מנגנון:** הוספתי 8 mappings חדשים ל-`_NAV_I18N` + 5 entries חדשים ל-DICT (`nav_morocco_span`, `nav_morocco_span_all`, `nav_span_andalusi`, `nav_veg_dishes`, `morocco_all_holidays`). כל פריטי תפריט שמורת חדשים הוסרו מסונכרנים בעת לחיצה על כפתור EN.

---

## ארכיטקטורה סופית (v8.0)

### תפריט עליון — 4 קבוצות שטוחות

| # | תווית | מספר | סוג |
|---|---|---|---|
| 1 | הכל | 1,054 | leaf |
| 2 | מרוקו\\ספרד | 744 | accordion (11 sub-items) |
| 3 | עדות ישראל | 270 | accordion (9 communities × 3 items each) |
| 4 | לא כשר | 40 | leaf |

### קבועי data ב-data.js

| קבוע | תוכן | גרסה |
|---|---|---|
| `R` | מערך 1,054 מתכונים | קיים |
| `CATS` | 20 קטגוריות | קיים |
| `MENU_STRUCTURE` | 4 קבוצות עליונות | v7.9 |
| `HOLIDAY_TAGS` | 10 חגים → 121 IDs יחודיים | v7.7 (תוקן) |
| `COMMUNITY_HOLIDAY_TAGS` | 9 עדות × 9 חגים | v7.4 |

### i18n ב-index.html

| קבוע | מטרה | גרסה |
|---|---|---|
| `DICT` | מילון UI strings | ~150 keys |
| `_NAV_I18N` | mapping תוויות → keys | v8.0 (הורחב) |
| `t(key)` | פונקציית תרגום | קיים |
| `applyLang(lang)` | החלפת שפה | קיים, מתרגם DOM |

---

## כללים נוספים — v7.7+

### לעולם אל

- **v7.7:** אל תחזיר את `HOLIDAY_TAGS` למבנה הישן (אותם 80 מתכונים בכל חג) — זה היה bug מקורי, לא feature
- **v7.8:** אל תוסיף בחזרה `{id:'hol', lbl:'חגים'}` כקטגוריה עליונה — זה כפול
- **v7.9:** אל תפריד את "מרוקו" ו"ספרד" לכפתורים נפרדים — מאוחדים תרבותית
- **v8.0:** כשמוסיפים תוויות חדשות ל-MENU_STRUCTURE, לעדכן גם את `_NAV_I18N` *וגם* את DICT אחרת התרגום לאנגלית לא יעבוד

### תהליך הוספת label חדש

1. הוסף `{lbl:'תווית חדשה', ...}` ל-MENU_STRUCTURE ב-data.js
2. הוסף ל-DICT ב-index.html: `key_chosen: {he:'תווית חדשה', en:'New Label'}`
3. הוסף ל-`_NAV_I18N`: `'תווית חדשה':'key_chosen'`
4. בדוק ש-`applyLang('en')` מתרגם נכון

---

## אדריכלות מובל v6.10 → v8.0 — מה השתנה (טבלה מעודכנת)

| תחום | v6.10 | v8.0 |
|---|---|---|
| MENU_STRUCTURE | wrapper יחיד 4-רמות nested | flat 4-קבוצות עליונות |
| Recipe grid | תמיד גלוי בטעינה | מוסתר עד nav/search/CTA |
| Header layout | brand בכותרת, search מתוח | brand+search+tools מאוזנים, max-width 1100 |
| Hero | text-align: right | text-align: center, ממורכז במלואו |
| Per-cuisine holidays | לא קיים | 9 עדות × 9 חגים, 221 תיוגים |
| Community subtree | flat | accordion עם 3 פריטים |
| **HOLIDAY_TAGS Morocco** | **80×10 חזרות זהות** | **121 תיוגים יחודיים** |
| **Top-level "חגים"** | **כפתור עליון נפרד** | **הוסר — תחת מרוקו בלבד** |
| **Morocco/Spain** | **2 כפתורים נפרדים** | **כפתור מאוחד "מרוקו\\ספרד"** |
| **i18n nav** | **חלקי** | **מלא — כל הפריטים מתורגמים ל-EN** |
| DOM section order | Hero→Bio→Book→About→Main | Hero→Bio→Main→Book→About |
| i18n keys | ~130 | ~155 (26 חדשים ב-v7.6+v8.0) |

---

## פקודות טסטים מהירות (v8.0)

```bash
# Syntax checks
node -c data.js

# Recipe count (must be 1054)
grep -oE "\{id:'[^']+',cat:'\w+'" data.js | wc -l

# v7.4: Mimouna NOT in communities
python3 -c "
import re
d = open('data.js', encoding='utf-8').read()
m = re.search(r'const COMMUNITY_HOLIDAY_TAGS = \{(.*?)\n\};', d, re.DOTALL)
hits = re.findall(r\"mimouna:\['?\w\", m.group(1))
print('Mimouna in communities:', len(hits), '(must be 0)')
"

# v7.6: Web3Forms key intact
grep -c "705d4207-c4a6-43a2-8fdc-d8e202bc6c9c" index.html  # ≥1

# v7.7: HOLIDAY_TAGS shabbat ≠ pesach
python3 -c "
import re
d = open('data.js', encoding='utf-8').read()
m = re.search(r'const HOLIDAY_TAGS = \{(.*?)\n\};', d, re.DOTALL)
sha = re.search(r\"shabbat:\[(.*?)\]\", m.group(1)).group(1)
pes = re.search(r\"pesach:\[(.*?)\]\", m.group(1)).group(1)
print('SAME (BAD):', sha == pes)
"

# v7.8: No top-level חגים entry
grep -c "^\s*{id:'hol', lbl:'חגים'}" data.js  # must be 0

# v7.9: Morocco/Spain merged
grep -c "morocco_span" data.js  # must be ≥1

# v8.0: i18n wiring complete
grep -c "nav_morocco_span:" index.html  # must be ≥1
grep -c "'מרוקו\\\\ספרד':'nav_morocco_span'" index.html  # must be ≥1

# CRLF integrity (Python)
python3 -c "raw=open('index.html','rb').read(); print('CRLF',raw.count(b'\r\n'),'LONE',raw.count(b'\n')-raw.count(b'\r\n'))"
```

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
