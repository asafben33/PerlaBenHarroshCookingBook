# CHANGELOG — v7.6: השלמת התוכנית v7.0 (משימות 7-10)

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026 — לילה
**גרסה:** 7.6 (סופית של מחזור v7.0)

---

## סקירה

זו הגרסה הסופית של מחזור v7.0. עוסקת ב-4 המשימות שנותרו מהתוכנית `PLAN_v7_0_ENGLISH.md`:

| # | משימה | מצב |
|---|---|---|
| 7 | i18n strings — 21 מפתחות חדשים ב-DICT | ✅ |
| 8 | Testing checklist — 10 בדיקות | ✅ |
| 9 | Documentation update — סעיף חדש ל-CLAUDE.md | ✅ |
| 10 | סדר DOM: Hero → Bio → **Main** → Book → About | ✅ |

---

## משימה 10: שינוי סדר ה-DOM (Main אחרי Bio)

**לפני:**
```
Line 1675: Hero
Line 1689: Bio
Line 1707: Book
Line 1742: About
Line 2124: Main   ← הרשת אחרי כל שאר התכנים
```

**אחרי:**
```
Line 1675: Hero
Line 1689: Bio
Line 1707: Main   ← מועברת לכאן
Line 1733: Book
Line 1768: About
```

הסיבה לפי התוכנית (שורה 313): המשתמש דיווח על "יותר מדי מידע בעמוד הראשי". כעת אחרי Bio קצרה הוא רואה מיד את רשת המתכונים, בלי לגלול דרך הספר וה-About.

הזזתי את כל בלוק `<main>` (24 שורות) ממיקומו הקודם ל-מיקום מיד אחרי `</section>` של Bio.

## משימה 7: i18n — 21 מפתחות חדשים ב-DICT

נוספו לאחר המפתחות הקיימים `pwa_*`:

```javascript
// Header brand + count
site_name_short: {he:'ספר הבישול של פרלה', en:"Perla's Cookbook"},
recipes_label:   {he:'מתכונים', en:'recipes'},

// Hero CTAs
hero_cta_browse: {he:'עיון במתכונים', en:'Browse Recipes'},
hero_cta_book:   {he:'קרא את הספר', en:'Read the Book'},

// Top-level groups (חדשים ל-v7.0)
nav_morocco:     {he:'מרוקו', en:'Morocco'},
nav_communities: {he:'עדות ישראל', en:'Jewish Communities'},
nav_holidays:    {he:'חגים', en:'Holidays'},

// Community sub-folder labels (v7.4)
community_all:             {he:'כל המתכונים', en:'All Recipes'},
community_traditional:     {he:'מאכלים מסורתיים לעדה', en:'Traditional Community Dishes'},
community_holidays_folder: {he:'מאכלי חגים', en:'Holiday Dishes'},

// Holiday names (10)
holiday_shabbat, holiday_rosh, holiday_kippur, holiday_pesach,
holiday_mimouna, holiday_hanukkah, holiday_purim,
holiday_shavuot, holiday_sukkot, holiday_henna,

// Toast for empty community-holiday combos
toast_no_recipes_holiday: {he:'אין עדיין מתכונים מתויגים לחג זה בעדה הזו', 
                           en:'No recipes tagged for this holiday in this community yet'},
```

**הערה חשובה:** הוספתי את המפתחות ל-DICT, אבל **התוויות הנראות לעין עדיין מקודדות בעברית ב-data.js וב-buildPanel.** המפתחות מוכנים לשימוש עתידי כשתחליט לחבר אותם דרך `data-i18n` attributes או דרך `t()` function. כרגע ה-`_LANG === 'en'` מתרגם רק את המחרוזות שכבר משתמשות ב-`t()` — לא את התפריט החדש של v7.x.

זה היה תכנון מודע שלי: לוודא ש-DICT מוכן לעתיד בלי לפצל את עבודת ההזרקה לשני שלבים. תיווך התווית של תפריט העדות לאנגלית מלאה דורש refactor של buildPanel לשימוש ב-`t()` במקום `esc(item.lbl)` — זה התרחבות שעדיף לעשות במחזור נפרד.

## משימה 8: Testing Checklist — 10/10 ✓

```
1. node -c data.js                              ✓ OK
2. JS braces balance (sum diff = 0)             ✓ OK (Main JS node -c)
3. Recipe count = 1054                          ✓
4. 6 top-nav groups present                     ✓ all/morocco/span/communities/hol/nonkosher
5. PWA install button intact                    ✓
6. Back-to-Top intact                           ✓
7. Lang + Theme toggles intact                  ✓
8. Web3Forms key intact (705d4207...)           ✓ — *תוקן ב-v7.6!*
9. DOM order Hero→Bio→Main→Book→About           ✓
10. CRLF integrity                              ✓ 12,946 / 0 lone

+ Mimouna only in Morocco (not communities)     ✓
+ COMMUNITY_HOLIDAY_TAGS structure              ✓
+ All 21 v7.6 i18n keys present                ✓
```

### ⚠ תיקון קריטי שגיליתי תוך הבדיקות

ה-`WEB3FORMS_KEY` היה `'PASTE_YOUR_WEB3FORMS_ACCESS_KEY_HERE'` — שאריות מהקובץ המקורי שלא תוקנו במחזור v7.x. החזרתי ל-`'705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'`, המפתח הציבורי-בכוונה לפי `<recent_updates>` ב-userMemories.

**זה היה כשל ביצוע שלי** — הייתי צריך לבדוק את זה כבר ב-v7.0 לפי התוכנית "Things NOT to break" (שורה 544 בתוכנית). מתנצל על הפספוס.

## משימה 9: עדכון תיעוד

יצרתי קובץ `CLAUDE_md_v7_update.md` שמכיל סעיף שלם לעדכון ל-`CLAUDE.md` הקיים. הוא כולל:

1. סקירה ארכיטקטונית של v7.0 → v7.6
2. הסברים מפורטים של MENU_STRUCTURE השטוח, COMMUNITY_HOLIDAY_TAGS, buildPanel branches
3. כללים חדשים: שקיפות תיוגים, mimouna רק במרוקו, CRLF, Web3Forms key
4. טבלת השוואה v6.10 vs v7.6
5. פקודות טסטים מהירות

**שימוש:** הוסף את כל הסעיף ל-CLAUDE.md בסוף, או החלף את הסעיפים שמתייחסים ל-v6.x.

לגבי HLD ו-LLD — הם עדיין נכונים בעיקרון (תיאור הארכיטקטורה של data.js single-page app + Netlify deployment). אם תרצה רענון מלא לתעוד טכני, זו עבודה למחזור הבא.

---

## בדיקות סופיות

```
✓ index.html: 540 KB / 12,946 שורות CRLF (100%, 0 lone LF)
✓ data.js: 1.4 MB / 1,054 מתכונים (כולל COMMUNITY_HOLIDAY_TAGS)
✓ Main JS syntax (node -c): OK
✓ data.js syntax (node -c): OK
✓ All 10 plan checklist items pass
✓ All 21 v7.6 i18n keys present
✓ Web3Forms key restored
```

---

## קבצים מצורפים

| קובץ | תיאור |
|---|---|
| `index.html` | + 21 i18n keys, + reorder main, + restore Web3Forms key |
| `data.js` | (לא שונה מ-v7.4 — שמור את הגרסה הקיימת) |
| `CLAUDE_md_v7_update.md` | סעיף חדש לתיעוד הפרויקט |

---

## פריסה

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" ".\index.html" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_v7_6_final.md" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CLAUDE_md_v7_update.md" ".\CLAUDE_md_v7_update.md" -Force
```
```powershell
git add index.html CHANGELOG_19-04-2026_v7_6_final.md CLAUDE_md_v7_update.md
```
```powershell
git commit -m "v7.6: i18n keys + DOM reorder + restore Web3Forms key + docs (final v7.0)"
```
```powershell
git push origin main
```

`data.js` לא השתנה מ-v7.4 — אם הוא כבר deployed, אל תעדכן שוב.

---

## ✓ מחזור v7.0 הושלם

10/10 משימות מהתוכנית בוצעו:

1. ✅ Unified header (`hdr-brand-v7`) — v7.0
2. ✅ Hero CTAs (browse / book) — v7.0
3. ✅ Bio placement verified — v7.0
4. ✅ Navigation redesign (flat 6-group) — v7.0
5. ✅ MENU_STRUCTURE rewrite — v7.0
6. ✅ Per-cuisine holidays — v7.2 → v7.4
7. ✅ i18n strings (21 keys) — v7.6
8. ✅ Testing checklist (10/10) — v7.6
9. ✅ Documentation update — v7.6
10. ✅ DOM order (Main after Bio) — v7.6

**+ תוספות שלא היו בתוכנית:**
- Hero centering — v7.0
- Header strip centering @ 1100px — v7.5
- Grid-on-demand — v7.1
- Holiday folder + Traditional folder per community — v7.4
- Mimouna removed from communities — v7.4
- Web3Forms key restored (critical bug fix) — v7.6

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
