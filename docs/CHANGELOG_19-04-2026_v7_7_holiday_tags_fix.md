# CHANGELOG — v7.7: עדכון מסמכי תכנון + תיקון `HOLIDAY_TAGS` של מטעמי אמא

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026 — לילה
**גרסה:** 7.7 (ממשיך לאחר v7.6)

---

## הבקשה

> 1. תעדכן את המסמכים בהתאם לכל מה שבוצע כאן בצ'אט
> 2. כשתסיים את סעיף 1 תמשיך לבצע את מה שעוד נשאר לפי התכנון בצורה מדוייקת ומיקצועית מבלי לדרוס שינויים שדרשתי כאן בצ'אט.

---

## חלק 1: עדכון המסמכים

### `PLAN_v7_0_HEBREW.md` — שכתוב מלא

המסמך הישן תיאר את התוכנית **לפני** מימוש. עכשיו המסמך מתאר:
- סטטוס מחזור v7.0 — הסתיים, 7 שלבים בוצעו
- ארכיטקטורה נוכחית v7.6 (תפריט שטוח, COMMUNITY_HOLIDAY_TAGS, מבנה כל עדה)
- מספרי מתכונים מוודאים (1,054)
- Roadmap עתידי לפי עדיפות
- כללי עבודה מתעדכנים (לעולם אל / תמיד חובה)
- פקודות בדיקה מהירות
- רשימת CHANGELOGs קיימים

### `PLAN_v7_0_ENGLISH.md` — שכתוב מלא (handoff טכני)

מסמך handoff באנגלית לצ'אט חדש שיתחיל מכאן. כולל:
- Project identity + critical context
- File inventory (production + docs + scripts)
- Current architecture (MENU_STRUCTURE, COMMUNITY_HOLIDAY_TAGS, recipe schema)
- Key JavaScript touchpoints (line numbers)
- CSS classes + variables + layout widths
- DOM section order
- 21 i18n keys list
- Post-v7.6 roadmap (high/medium/low priority)
- Things NOT to break (v7.x + v6.x rules)
- Testing checklist
- Deployment commands
- CRLF normalization
- Honesty constraint (memorial project)
- Estimated effort for next cycle

---

## חלק 2: המשך התוכנית — תיקון `HOLIDAY_TAGS` של מטעמי אמא

### הבעיה

הקבוע `HOLIDAY_TAGS` (לקטגוריית "חגים" של מטעמי אמא) היה **שגוי לחלוטין**:
- אותם 80 מתכונים בדיוק חזרו בכל 10 החגים
- שבת=ראש השנה=פסח=מימונה=חנוכה=פורים=שבועות=סוכות=חינה
- תוצאה: לחיצה על כל חג הציגה את אותם 80 מתכונים — בלי הבדל

זה ככל הנראה data שגויה מתחילת הפרויקט שמעולם לא תוקנה.

### הפתרון

יצרתי תיוג אמיתי מבוסס על:
1. **חיפוש regex אמיתי בכותרות המתכונים** של 671 מתכוני מרוקו
2. **דפוסים מבוססי מסורת יהודית-מרוקאית מתועדת**
3. **תיקון של false positives** (למשל, `(?<!ט)חינה` כדי לא לתפוס "טחינה")

### תוצאות

| חג | לפני | אחרי |
|---|---|---|
| שבת | 80 | 54 (טאג'ין, חמין, סקינה, פסטייה, חלה) |
| ראש השנה | 80 | 14 (דבש, רימון, דלעת מתוק) |
| יום כיפור | 80 | 0 (אין מתכון מרוקאי ספציפי לכיפור — הריסה לא מופיעה) |
| פסח | 80 | 4 (חרוסת, מצה, אוכל בלי קמח) |
| **מימונה** | **80** | **7 (מופלטה!, פרנה מימונה, ריבות, תמרים ממולאים)** |
| חנוכה | 80 | 2 (ספינג', סופגניות) |
| פורים | 80 | 1 (אוזני המן) |
| שבועות | 80 | 12 (גבינות, מאפי גבינה, מרק חלב) |
| סוכות | 80 | 27 (כל הירקות הממולאים) |
| חינה | 80 | 14 (כל מתכוני החינה והחתונה) |

**TOTAL UNIQUE TAGS:** 121 / 671 (18%) — עכשיו תיוג אמיתי במקום הכל-בכל.

### דוגמאות לתיוג אמיתי

**מימונה (החג הכי חשוב לאחר פסח במרוקו):**
- `d1` מופלטה מסורתית
- `holf5` שולחן מימונה שלם
- `chf2` עוף עם ריבת תפוזים
- `hv4` פרנה מימונה
- `fw1` תמרים ממולאים דג

**שבת:**
- `c3` סקינה — חמין מרוקאי
- `me11` חמין קפה דה מסה — סכינה מלאה
- `hn1-hn8` 8 טאג'ינים שונים
- `me8` טאג'ין בקר עם זיתים

**חינה (טקס חתונה):**
- `h2` מאפה בשר לחינה
- `hne4` סמבוסק מרוקאי לחינה
- `holf2` סמבוסק גבינה לחינה
- `dn11` עוגיות חינה שקדים

### מה זה אומר עכשיו לאתר

לפני התיקון: לחיצה על "חגים" → "מימונה" הציגה 80 מתכונים שאין להם קשר למימונה (כולל מרקים, תבשילי בשר, סלטים).

אחרי התיקון: לחיצה על "מימונה" תציג **7 מתכוני מימונה אמיתיים** — מופלטה, ריבות, תמרים ממולאים, פרנה. אותו דבר לכל חג.

### הגינות מקצועית

לא תיקנתי את `HOLIDAY_TAGS` כדי "להראות יותר" — תיקנתי אותו להציג את **המתכונים הנכונים בלבד**. זה הופך את הקטגוריה "חגים" ל-functional, לא רק מנצנצת.

`COMMUNITY_HOLIDAY_TAGS` (חגי 9 העדות) **לא שונה** — הוא נשמר כפי שתיקנתי ב-v7.4 (221 תיוגים יחודיים מבוססי מקורות מתועדים).

---

## בדיקות שעברו

```
✓ Main JS syntax (node -c): OK
✓ data.js syntax (node -c): OK
✓ CRLF: 12,946 שורות (100%, 0 lone LF)
✓ 1,054 מתכונים נשמרים מדויק
✓ Web3Forms key intact (705d4207-...)
✓ HOLIDAY_TAGS: shabbat ≠ pesach (היה זהה!)
✓ Mimouna: 7 מתכונים (היה 80)
✓ COMMUNITY_HOLIDAY_TAGS לא נגעתי
```

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | (לא שונה מ-v7.6 — אותה גרסה) |
| `data.js` | תיקון `HOLIDAY_TAGS` של מטעמי אמא — מ-80×10 חזרות זהות ל-121 תיוגים יחודיים |
| `PLAN_v7_0_HEBREW.md` | שכתוב מלא — משקף את כל v7.0 → v7.6 |
| `PLAN_v7_0_ENGLISH.md` | שכתוב מלא — handoff טכני בלי תוכן ישן |

---

## פריסה

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
Copy-Item "$env:USERPROFILE\Downloads\PLAN_v7_0_HEBREW.md" ".\PLAN_v7_0_HEBREW.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\PLAN_v7_0_ENGLISH.md" ".\PLAN_v7_0_ENGLISH.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_v7_7_holiday_tags_fix.md" "." -Force
```
```powershell
git add index.html data.js PLAN_v7_0_HEBREW.md PLAN_v7_0_ENGLISH.md CHANGELOG_19-04-2026_v7_7_holiday_tags_fix.md
```
```powershell
git commit -m "v7.7: rebuild HOLIDAY_TAGS for Morocco (real per-holiday tagging) + plan docs refresh"
```
```powershell
git push origin main
```

---

## אחרי הפריסה (Netlify ~30s)

לחיצה על "חגים" בתפריט הראשי → תפריט עם 10 חגים. **כל חג מציג עכשיו את המתכונים הנכונים שלו**:
- חנוכה → ספינג' + סופגניות מרוקאיות (2)
- מימונה → מופלטה, פרנה, ריבות, תמרים (7)
- פסח → חרוסת + מצה + אוכל פסח (4)
- שבת → 54 מתכונים מסורתיים של שבת מרוקאית
- ועוד...

יום כיפור מציג 0 מתכונים — נכון, כי אין במאגר מתכון מרוקאי-יהודי ספציפי לכיפור (הריסה כן הייתה צריכה להיות שם, אבל היא לא מופיעה במאגר). אם רוצה, אפשר להוסיף הריסה כמתכון חדש בהמשך.

---

## מה נותר בתוכנית

לפי `PLAN_v7_0_ENGLISH.md` ה-Roadmap המעודכן:

### עדיפות גבוהה — ✅ בוצע ב-v7.7
1. ~~Fix `HOLIDAY_TAGS` for Morocco~~ ✅
2. **Wire i18n keys to UI** — buildPanel עדיין משתמש ב-`esc(item.lbl)`. דורש refactor של buildPanel.
3. **Review `COMMUNITY_HOLIDAY_TAGS` with family** — דורש מעורבות אסף.

### עדיפות בינונית
4. Documentation refresh (CLAUDE.md, HLD, LLD)
5. Family review of community holiday tags
6. Missing recipe images (download_images.py)

### עדיפות נמוכה
7. Sitemap.xml
8. Breadcrumbs
9. Recipe of the day carousel
10. Light theme polish for v7.x classes

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
