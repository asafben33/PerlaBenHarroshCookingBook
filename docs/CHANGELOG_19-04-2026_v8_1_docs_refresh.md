# CHANGELOG — v8.1: רענון תיעוד מקיף (README, CLAUDE.md, HLD, LLD)

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026 — לילה (אחרי v8.0)
**גרסה:** 8.1 (תיעוד בלבד — אין שינויי קוד)

---

## הבקשה

> תמשיך לתקן ולשפר לפי התכנון

המשימה הבאה ב-Roadmap הייתה **"עדכון תיעוד טכני"** — הטמעת ה-patches לתוך המסמכים הקיימים שעדיין הכילו תוכן ישן.

---

## הבעיה

לאחר 11 פריסות (v7.0 → v8.0) ב-19/04, המסמכים הבסיסיים נשארו לא מסונכרנים:

| קובץ | הבעיה |
|---|---|
| `README.md` | header v7.1, MENU_STRUCTURE מציג 6 קבוצות (היה ב-v7.0), אין סעיף SEO, אין הזכרה של v7.7-v8.0 |
| `CLAUDE.md` | header v7.1, אזהרות מעודכנות רק ל-v7.1, אין סעיפים על v7.2-v8.0, רישום סשנים מסתיים ב-v7.1 |
| `HLD_Perla_CookingBook.md` | מתאר ארכיטקטורה של v6.4 |
| `LLD_Perla_CookingBook.md` | מתאר עיצוב נמוך-רמה של v7.1 |

---

## מה בוצע

### 1. README.md — שכתוב חלקי + הוספות

**סעיפים שעודכנו:**

- **Header version**: v7.1 → v8.0
- **טבלת סטטיסטיקות**: הוספתי שורות חדשות עם נתוני התיוגים (121 לבד מרוקו, 221 לעדות), 11 גרסאות במחזור
- **מבנה הפרויקט**: רשימת הקבצים מורחבת — sitemap.xml, robots.txt, audit_recipes.py, כל ה-CHANGELOG חדשים, CLAUDE_md_v7/v8_update
- **MENU_STRUCTURE**: עברתי מ-6 קבוצות (v7.0) ל-4 קבוצות (v7.9) עם תיאור מלא של "מרוקו\\ספרד" ועדות
- **דף ראשי**: סעיף הורחב מ-"v7.0 + v7.1" ל-"v7.0 → v8.0" עם 9 bullet points במקום 5
- **SEO** (חדש): סעיף sitemap, robots.txt, hreflang, JSON-LD

### 2. CLAUDE.md — הוספת 9 סעיפים חדשים + עדכון אזהרות

**Header version**: v7.1 → v8.0

**סעיפים חדשים שנוספו אחרי v7.1**:
- v7.2 — COMMUNITY_HOLIDAY_TAGS
- v7.3-v7.4 — מבנה תפריט עדות
- v7.5 — מרכוז Header strip
- v7.6 — i18n keys + DOM order + Web3Forms restore
- v7.7 — תיקון HOLIDAY_TAGS של מרוקו
- v7.8 — הסרת כפילות "חגים" + תיקיית חגים תחת מרוקו
- v7.9 — איחוד מרוקו + ספרד
- v8.0 — i18n wiring + light theme + SEO + print
- ארכיטקטורה נוכחית (v8.0) — טבלאות סיכום

**אזהרות**: רשימה הורחבה מ-9 ל-15 כללי "אל" (כולל v7.4, v7.6, v7.7, v7.8, v7.9, v8.0).

**רישום סשנים**: הוספתי 9 entries חדשות ל-19/04/2026 (v7.2 עד v8.0).

### 3. HLD_Perla_CookingBook.md — נספח v7.0 → v8.0

לא דרסתי את תוכן v6.4 (43KB מתועד היטב). במקום, הוספתי **נספח** בסוף הקובץ עם:

- טבלת השוואה v6.4 vs v8.0 (12 היבטים ארכיטקטוניים)
- קבועי data חדשים (HOLIDAY_TAGS תוקן, COMMUNITY_HOLIDAY_TAGS חדש)
- קבועי i18n חדשים (_NAV_I18N הורחב)
- קבצים חדשים (sitemap, robots, audit, CLAUDE patches)
- רשימת CHANGELOGs (10 קבצים)

End marker עודכן: `סוף HLD v6.4 + נספח v8.0`.

### 4. LLD_Perla_CookingBook.md — נספח טכני מקיף

המסמך הקיים (89KB) מתאר עיצוב של v7.1. הוספתי **נספח טכני מקיף** עם:

- מבנה MENU_STRUCTURE החדש (snippets מלאים של מרוקו\\ספרד ועדות)
- HOLIDAY_TAGS structure + COMMUNITY_HOLIDAY_TAGS structure
- 6 פונקציות JS חדשות עם מספרי שורות
- Filter logic החדש ב-renderGrid()
- 3 branches שנוספו ל-buildPanel()
- 10 CSS classes חדשים עם מספרי שורות
- 7 light theme overrides (v8.0)
- Print stylesheet הורחב (v8.0)
- Layout widths המעודכנים (v7.5)
- 21 i18n keys (v7.6) + 5 (v8.0) + 8 _NAV_I18N mappings
- DOM section order
- תהליך הוספת תווית חדשה
- CRLF normalization snippet
- בדיקות before push

End marker עודכן: `סוף LLD v7.1 + נספח v8.0`.

---

## גישת איכות

**לא דרסתי מסמכים קיימים** — כל המסמכים שעודכנו שמרו על תוכן v6.x ו-v7.x הקיים. במסמכים הגדולים (HLD/LLD) הוספתי נספח. במסמכים הקטנים (README, CLAUDE.md) ערכתי str_replace מדויקים על סעיפים מסוימים.

זה חשוב כי:
1. תיעוד היסטורי ערכי — כך אפשר להבין כיצד הפרויקט התפתח
2. מי שיקרא את ה-LLD בעתיד יראה גם את העיצוב המקורי וגם את השינויים
3. אי-דריסה היא reversible — אם משהו השתבש, אפשר להחזיר את הסעיף הנוסף בלי לפגוע

---

## בדיקות שעברו

```
✓ README.md: header version v8.0
✓ README.md: Morocco/Spain merger mentioned
✓ README.md: v7.9 mentioned
✓ README.md: v8.0 mentioned
✓ README.md: SEO section added
✓ README.md: sitemap referenced
✓ CLAUDE.md: header version v8.0
✓ CLAUDE.md: v7.7 section
✓ CLAUDE.md: v7.8 section
✓ CLAUDE.md: v7.9 section
✓ CLAUDE.md: v8.0 section
✓ CLAUDE.md: updated warnings
✓ HLD: v8.0 appendix
✓ HLD: updated end marker
✓ LLD: v8.0 appendix
✓ LLD: CRLF instructions
✓ LLD: JS function references
✓ LLD: updated end marker
```

18/18 ✓

---

## קבצים מצורפים

| קובץ | שינוי | גודל לפני | גודל אחרי |
|---|---|---|---|
| `README.md` | header + MENU_STRUCTURE + statistics + SEO section | 12.8 KB | 22.3 KB |
| `CLAUDE.md` | header + 9 new sections + updated warnings + 9 session log entries | 12.7 KB | 21.2 KB |
| `HLD_Perla_CookingBook.md` | appended v8.0 appendix | 43.2 KB | 46.4 KB |
| `LLD_Perla_CookingBook.md` | appended technical v8.0 appendix | 89.4 KB | 97.3 KB |

---

## פריסה

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\README.md" ".\README.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CLAUDE.md" ".\CLAUDE.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\HLD_Perla_CookingBook.md" ".\HLD_Perla_CookingBook.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\LLD_Perla_CookingBook.md" ".\LLD_Perla_CookingBook.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_v8_1_docs_refresh.md" "." -Force
```
```powershell
git add README.md CLAUDE.md HLD_Perla_CookingBook.md LLD_Perla_CookingBook.md CHANGELOG_19-04-2026_v8_1_docs_refresh.md
```
```powershell
git commit -m "v8.1: documentation refresh — README/CLAUDE/HLD/LLD synced to v8.0"
```
```powershell
git push origin main
```

`index.html` ו-`data.js` **לא השתנו** מ-v8.0 / v7.9 בהתאמה.

---

## מה נשאר ב-Roadmap לאחר v8.1

מהרשימה ב-`PLAN_v7_0_HEBREW.md`:

### דורש מעורבות אסף או המשפחה
1. רענון תיוגי `COMMUNITY_HOLIDAY_TAGS` — בדיקה משפחתית
2. רענון תיוגי `HOLIDAY_TAGS` של מרוקו — בדיקה ידנית
3. תאימות בין-עדתית (כורדי-זכו vs כורדי-ירושלים)

### דורש החלטות UX או הוצאת זמן
4. תמונות חסרות (`download_images.py` — אסף יריץ בעצמו)
5. Breadcrumbs — דורש החלטה איפה ואיך
6. Recipe carousel — מתכון יומי שמתחלף
7. OG images per category
8. Lazy loading + virtualization

### לא דורש מעורבות אסף — אפשר להמשיך
לא נשאר משהו טכני שאני יכול לבצע בלי החלטה משפחתית או החלטת UX.

המחזור v7.0 → v8.1 הסתיים.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
