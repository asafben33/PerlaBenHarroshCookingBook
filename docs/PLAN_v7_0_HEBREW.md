# תוכנית עבודה — ספר הבישול של פרלה בן-הראש ז״ל

**עודכן אחרון:** 19/04/2026 — סוף לילה (אחרי v8.0)
**גרסה נוכחית של האתר:** v8.0 (פרוס מ-v7.5; v7.6-v8.0 ממתינים לפריסה)

---

## סטטוס המחזור הנוכחי — v7.0 הושלם, v7.7-v8.0 בוצעו

מחזור v7.0 הוגדר ב-13/04/2026 ונפרס ב-11 שלבים (v7.0 → v8.0) במהלך 19/04/2026. **כל המשימות הראשוניות בוצעו**, פלוס תוספות שהמשתמש ביקש במהלך העבודה, פלוס משימות תחזוקה אוטומטיות (i18n מלא, light theme, sitemap, print).

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
| **v8.0** | חיווט i18n מלא של תפריט (8 mappings + 5 DICT entries), light theme עברה ל-v7.x classes, sitemap.xml + robots.txt, print rules הורחב | 19/04 |

### תיקונים קריטיים שנעשו במחזור

1. **Web3Forms key** (v7.6) — היה placeholder. הוחזר ל-`'705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'`.
2. **Mimouna בעדות** (v7.4) — הוסרה לחלוטין מ-`COMMUNITY_HOLIDAY_TAGS`. נשארת רק במרוקו.
3. **HOLIDAY_TAGS שגוי** (v7.7) — היה אותם 80 מתכונים בכל 10 החגים. תוקן.
4. **כפילות "חגים" בתפריט** (v7.8) — הקטגוריה העליונה הוסרה.
5. **i18n חלקי** (v8.0) — תפריט העדות ופריטים חדשים לא תורגמו לאנגלית. הורחב `_NAV_I18N`.
6. **CRLF** — תוקן ידנית בכל גרסה.

---

## ארכיטקטורה נוכחית (v8.0)

### תפריט עליון — 4 קבוצות שטוחות (היה 6 ב-v7.0)

```
1. הכל              (1,054)
2. מרוקו\ספרד       (744)  — accordion: 11 sub-items (מרוקו 671 + ספרד 73)
3. עדות ישראל       (270)  — 9 עדות, כל אחת accordion עם 3 פריטים
4. לא כשר           (40)
```

### מבנה "מרוקו\\ספרד" (v7.9)

```
מרוקו\ספרד (744 מתכונים)
├── כל מתכוני מרוקו וספרד (744)
├── מרקים (103) | סלטים (103) | תבשילי ירקות (87)
├── בשר וקציצות (82) | עוף ושבת (66) | דגים (70)
├── חגים ומועדים (תיקיה nested) ← v7.8
│   ├── כל מתכוני החגים (80)
│   ├── שבת (54), ראש השנה (14), יום כיפור (0)
│   ├── פסח (4), מימונה (7), חנוכה (2), פורים (1)
│   └── שבועות (12), סוכות (27), חינה (14)
├── קינוחים ומאפים (80)
└── ספרד (אנדלוסי) (73)
```

### מבנה כל עדה (v7.4 — נשמר)

```
עיראק (accordion)
├── כל המתכונים (30)
├── מאכלים מסורתיים לעדה (3)
└── מאכלי חגים (תיקיה nested)
    └── 9 חגים × IDs מ-COMMUNITY_HOLIDAY_TAGS
```

### i18n מלא — תרגום אוטומטי לאנגלית (v8.0)

הקבוע `_NAV_I18N` מכיל מיפוי תוויות עבריות → מפתחות i18n. הפונקציה `applyLang('en')` סורקת את ה-DOM ומתרגמת **את כל פריטי התפריט**, כולל הפריטים החדשים מ-v7.x:

| תווית עברית | מפתח i18n | תרגום אנגלי |
|---|---|---|
| מרוקו\\ספרד | nav_morocco_span | Morocco / Spain |
| כל מתכוני מרוקו וספרד | nav_morocco_span_all | All Morocco & Spain Recipes |
| ספרד (אנדלוסי) | nav_span_andalusi | Spain (Andalusian) |
| מאכלי חגים | community_holidays_folder | Holiday Dishes |
| מאכלים מסורתיים לעדה | community_traditional | Traditional Community Dishes |
| כל מתכוני החגים | morocco_all_holidays | All Holiday Recipes |
| שבת/פסח/מימונה/וכו' | holiday_* | Shabbat/Pesach/Mimouna/etc. |

### מבני ה-data השונים (v8.0)

| קבוע | מטרה | תוכן |
|---|---|---|
| `R` | מערך כל המתכונים | 1,054 אובייקטים |
| `CATS` | רשימת קטגוריות | 20 קטגוריות עם labels |
| `MENU_STRUCTURE` | מבנה התפריט הראשי | 4 קבוצות עליונות (v7.9) |
| `HOLIDAY_TAGS` | חגי מרוקו | 10 חגים → 121 IDs יחודיים (v7.7 תיקן) |
| `COMMUNITY_HOLIDAY_TAGS` | חגי 9 העדות | 9×9 → IDs (v7.4) |
| `DICT` | מילון UI | ~155 מפתחות (5 חדשים ב-v8.0) |
| `_NAV_I18N` | מיפוי תווית→מפתח | הורחב ב-v8.0 |

---

## קבצים בפרויקט (מעודכן v8.0)

### Production (מתפרס ל-GitHub/Netlify)

| קובץ | תפקיד | גרסה |
|---|---|---|
| `index.html` | SPA ראשי (HTML+CSS+JS) | v8.0 |
| `data.js` | 1,054 מתכונים + MENU_STRUCTURE + tags | v7.9 |
| `book_data.js` | פרקי הספר | קיים |
| `pre_en.js` | תרגום תוכן מתכונים אוטומטי | קיים |
| `manifest.json` | PWA manifest | קיים |
| `sw.js` | Service worker | קיים |
| `_headers` | Netlify CSP + headers | קיים |
| **`sitemap.xml`** | **SEO sitemap (חדש v8.0)** | **v8.0** |
| **`robots.txt`** | **מציין ל-crawlers את ה-sitemap (חדש v8.0)** | **v8.0** |

### תיעוד

| קובץ | סטטוס |
|---|---|
| `CLAUDE.md` | ⚠ Pre-v7.x |
| `CLAUDE_md_v7_update.md` | תוספת ל-v7.6 |
| `CLAUDE_md_v8_update.md` | **חדש v8.0** — תוספת ל-v7.7+v8.0 |
| `HLD_Perla_CookingBook.md` | ⚠ v6.3 |
| `LLD_Perla_CookingBook.md` | ⚠ v6.3 |
| `PLAN_v7_0_HEBREW.md` | **עודכן 19/04 (v8.0)** |
| `PLAN_v7_0_ENGLISH.md` | **עודכן 19/04 (v8.0)** |

---

## מה נותר לעשות (Roadmap לאחר v8.0)

### עדיפות גבוהה — דורש מעורבות אסף או המשפחה

1. **רענון תיוגי `COMMUNITY_HOLIDAY_TAGS`** — תיוג ראשוני ב-82% כיסוי, מבוסס מקורות מתועדים. אם אסף או בני המשפחה רואים שילוב לא נכון, לעדכן ידנית.

2. **רענון תיוגי `HOLIDAY_TAGS` של מרוקו** — תיקון v7.7 הוא אוטומטי מבוסס regex על כותרות. ייתכן שיש false negatives (מתכון שצריך להיות מתויג ולא תויג). דורש בדיקה משפחתית.

### עדיפות בינונית

3. **עדכון תיעוד טכני** — `HLD_Perla_CookingBook.md` ו-`LLD_Perla_CookingBook.md` עדיין מתארים v6.3. סעיף `CLAUDE_md_v7_update.md` + `CLAUDE_md_v8_update.md` נכתבו אבל לא הוטמעו ב-CLAUDE.md.

4. **בדיקת תאימות לעדה השנייה** — האם מסורות שתויגו עובדות גם למשפחות מאזורים שונים באותה עדה (כורדי-זכו vs כורדי-ירושלים)?

5. **תמונות חסרות** — הרבה מתכוני עדות (במיוחד טוניסיה, בוכרה) חסרים תמונה. סקריפט `download_images.py` יכול להוריד אוטומטית.

### עדיפות נמוכה

6. **Breadcrumbs** — אין breadcrumbs בעמוד מתכון.
7. **Recipe carousel** — "מתכון יומי" שמתחלף.
8. **OG images per category** — תמונות social sharing נפרדות לכל קטגוריה.
9. **Lazy loading + virtualization** — לרשת המתכונים, לתמיכה בהמשך גידול.

### בוצע — לא להתחיל מחדש

- ~~רענון `HOLIDAY_TAGS` של מטעמי אמא~~ ✅ v7.7
- ~~הסרת כפילות "חגים" בתפריט~~ ✅ v7.8
- ~~איחוד מרוקו וספרד~~ ✅ v7.9
- ~~i18n keys ל-DICT~~ ✅ v7.6 + v8.0 (חיווט מלא)
- ~~Light theme polish~~ ✅ v8.0
- ~~Sitemap.xml + robots.txt~~ ✅ v8.0
- ~~Print stylesheet הורחב~~ ✅ v8.0
- ~~Hero centering~~ ✅ v7.0
- ~~Header strip centering~~ ✅ v7.5
- ~~Grid-on-demand~~ ✅ v7.1
- ~~Holiday folder per community~~ ✅ v7.4
- ~~Mimouna removed from communities~~ ✅ v7.4
- ~~Web3Forms key restored~~ ✅ v7.6

---

## כללי עבודה מתעדכנים (v7.x → v8.0)

### לעולם אל

- אל תחזיר את MENU_STRUCTURE למבנה nested של v6.x
- אל תוסיף mimouna ל-`COMMUNITY_HOLIDAY_TAGS` (חג מרוקאי בלעדי)
- אל תסיר `class="main-hidden"` מ-`<main>` (תכונת v7.1)
- אל תשנה `WEB3FORMS_KEY` ל-placeholder — זה מפתח ציבורי-בכוונה
- אל תהפוך את ה-`hdr-search` ל-`flex: 1`
- אל תחזיר `max-width: 1440` לרצועה העליונה
- **v7.7:** אל תחזיר את `HOLIDAY_TAGS` למבנה הישן
- **v7.8:** אל תוסיף בחזרה `{id:'hol', lbl:'חגים'}` כקטגוריה עליונה
- **v7.9:** אל תפריד את "מרוקו" ו"ספרד" לכפתורים נפרדים
- **v8.0:** כשמוסיפים תווית חדשה ל-MENU_STRUCTURE, תמיד לעדכן גם את `_NAV_I18N` *וגם* את DICT — אחרת התרגום לאנגלית לא יעבוד

### תמיד חובה

- כל עריכת Python על `index.html` חייבת להסתיים בנירמול CRLF
- כל commit חייב לעבור `node -c data.js` ו-`node -c` על ה-JS הראשי ב-index.html
- כל גרסה חדשה צריכה CHANGELOG משלה
- pushing ל-git רק עם הפקודות one-at-a-time

### תהליך הוספת label חדש (v8.0)

1. הוסף `{lbl:'תווית חדשה', ...}` ל-MENU_STRUCTURE ב-data.js
2. הוסף ל-DICT ב-index.html: `key_chosen: {he:'תווית חדשה', en:'New Label'}`
3. הוסף ל-`_NAV_I18N`: `'תווית חדשה':'key_chosen'`
4. בדוק ש-`applyLang('en')` מתרגם נכון

### הוספת חג חדש לעדה

```javascript
iraq: {
  pesach: ['iq5','iq8','iq14','iq19','iq20','iq24', 'iq30'],  // הוספתי iq30
}
```

### הוספת חג חדש למרוקו

```javascript
const HOLIDAY_TAGS = {
  pesach: ['fin12','hle2','holf4','hn24', 'me5'],  // הוספתי me5
};
```

### הוספת עדה חדשה

מורכב יותר. דורש:
1. הוספת ID ל-`CATS`
2. הוספת 30 מתכונים עם `cat:'newid'`
3. הוספת בלוק ל-`COMMUNITY_HOLIDAY_TAGS` עם 9 חגים
4. הוספת בלוק ל-MENU_STRUCTURE.communities עם 3 פריטים
5. הוספת `nav_<newid>` ל-DICT + `'<עברית>':'nav_<newid>'` ל-`_NAV_I18N`
6. עדכון מספר הכולל בכל מקום שמופיע "270" → "300"

---

## פקודות בדיקה מהירות (v8.0)

```bash
# Recipe count (must be 1054)
grep -oE "\{id:'[^']+',cat:'\w+'" data.js | wc -l

# Mimouna NOT in communities
grep "mimouna:\['" data.js   # 0 in COMMUNITY_HOLIDAY_TAGS section

# Web3Forms key intact
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
grep -c "^\s*{id:'hol', lbl:'חגים'}" data.js   # 0

# v7.9: Morocco/Spain merged
grep -c "morocco_span" data.js   # ≥1

# v8.0: i18n wiring complete
grep -c "nav_morocco_span:" index.html   # ≥1
grep -c "html.light .hdr-brand-v7" index.html   # ≥1

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
Copy-Item "$env:USERPROFILE\Downloads\sitemap.xml" ".\sitemap.xml" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\robots.txt" ".\robots.txt" -Force
```
```powershell
git add index.html data.js sitemap.xml robots.txt CHANGELOG_*.md
```
```powershell
git commit -m "v8.0: full i18n wiring + light theme + sitemap + print"
```
```powershell
git push origin main
```

Netlify deploys automatically ~30s אחרי push.

---

## CHANGELOGs קיימים (v7.x → v8.0 — 10 קבצים)

- `CHANGELOG_19-04-2026_v7_centered_hero.md` — v7.0 + v7.1
- `CHANGELOG_19-04-2026_v7_2_community_holidays.md` — v7.2
- `CHANGELOG_19-04-2026_v7_3_holidays_in_community.md` — v7.3
- `CHANGELOG_19-04-2026_v7_4_holiday_folder.md` — v7.4
- `CHANGELOG_19-04-2026_v7_5_centered_header_strip.md` — v7.5
- `CHANGELOG_19-04-2026_v7_6_final.md` — v7.6
- `CHANGELOG_19-04-2026_v7_7_holiday_tags_fix.md` — v7.7
- `CHANGELOG_19-04-2026_v7_8_remove_duplicate_holidays.md` — v7.8
- `CHANGELOG_19-04-2026_v7_9_morocco_spain_merge.md` — v7.9
- `CHANGELOG_19-04-2026_v8_0_i18n_theme_seo.md` — **v8.0 (חדש)**

---

## אם צ'אט חדש מתחיל מכאן

1. קרא את **`PLAN_v7_0_ENGLISH.md`** — handoff טכני מלא באנגלית
2. קרא את **`CLAUDE_md_v7_update.md`** + **`CLAUDE_md_v8_update.md`** — עדכוני התיעוד הארכיטקטוני
3. בדוק את `userMemories` בהקשר — מכיל את העדכונים האחרונים
4. עבד נגד התיקיה הזאת בלבד: `https://github.com/asafben33/PerlaBenHarroshCookingBook.git`
5. כל שינוי מתפרס ב: `https://perlabenharrosh-cookingbook.netlify.app/` (Netlify)
6. גם קיים: `https://asafben33.github.io/PerlaBenHarroshCookingBook/` (GitHub Pages, mirror)

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
