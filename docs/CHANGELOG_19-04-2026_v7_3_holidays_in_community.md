# CHANGELOG — v7.3: שני תיקונים מהצילום

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026 — לילה
**גרסה:** 7.3

---

## הצילום הראה שני בעיות

### בעיה 1 (חיצים אדומים על העדות + placeholder ימני)

ב-v7.2 בניתי MENU_STRUCTURE כך:
```
עיראק (accordion)
└── חגי העדה (accordion פנימי) ← רמה 3
    └── שבת, ראש השנה, פסח, ...
```

הקוד הקיים ב-`buildPanel` תומך ב-3 רמות nesting אבל **לא בודק את `s.communityHoliday` או `ds.communityHoliday`** ברמות הפנימיות. תוצאה: 9 העדות הופיעו כ-chips שטוחים בלי שום אופציה לפתוח חגים, וה-placeholder הישן ("חגי העדות (בקרוב)") עדיין הופיע מימין.

### בעיה 2 (חיצים אדומים על ה-header)

שורת החיפוש (`.hdr-search`) הייתה עם `flex: 1` שמתח אותה לכל הרוחב הזמין, ודחק את הכלים (התקן/⊙/EN) לקצה השמאלי הפינתי. החיצים הירוקים בצילום הצביעו על מרכז המסך — המשתמש רצה layout מאוזן סימטרית.

---

## התיקונים

### תיקון 1 — מבנה שטוח (data.js)

הסרתי את ה-wrapper "חגי העדה" — עכשיו כל **עדה היא accordion אחד שתוכנו: "כל המתכונים" + 10 חגים, כולם באותה רמה**:

```javascript
// v7.3 — 2 levels בלבד, החגים ישירות בתוך accordion של העדה
{lbl:'עיראק', items:[
  {id:'iraq', lbl:'כל המתכונים'},
  {communityHoliday:'iraq', holidayKey:'shabbat', lbl:'שבת'},
  {communityHoliday:'iraq', holidayKey:'rosh', lbl:'ראש השנה'},
  {communityHoliday:'iraq', holidayKey:'kippur', lbl:'יום כיפור'},
  // ... 7 עוד חגים
]}
```

גם הסרתי את ה-Option C placeholder (`{placeholder:'communityHolidays', lbl:'חגי העדות (בקרוב)'}`) — v7.2/v7.3 הופכים אותו למיותר.

### תיקון 2 — branch ב-buildPanel (index.html)

הוספתי טיפול ב-`s.communityHoliday` בתוך הלולאה הפנימית של ה-accordion body (רמה 2):

```javascript
subItems.forEach(function(s) {
  // ...
  if (s.communityHoliday && s.holidayKey) {
    // יוצר כפתור pc pc-comm-hol עם המספר תיוגים
    // אם 0 תיוגים — מוסיף .pc-empty (אפור-שקוף + toast)
    // אחרת — קורא ל-selectCommunityHoliday(comm, hkey, label, groupKey)
  }
});
```

זה גורם לקליק על "עדות ישראל" → תפריט נפתח עם 9 accordion (אחד לכל עדה) → לחיצה על עדה פותחת את הגוף שלה → רואים "כל המתכונים" + 10 כפתורי חגים אדומים-אלמוגיים.

### תיקון 3 — מרכוז ה-header (index.html)

```css
.hdr-inner {
  /* ... */
  justify-content: space-between;  /* brand → שמאל קצה, tools → ימין קצה */
}
.hdr-search {
  flex: 0 1 480px;     /* היה: flex: 1 (מתיחה לכל הרוחב) */
  max-width: 480px;    /* היה: 640px */
  margin: 0 auto;      /* דוחף לאמצע בין brand ל-tools */
}
```

תוצאה לפי המוקאפ: שם הספר מימין → **שורת חיפוש ממורכזת** (480px max) → כפתורי כלים משמאל. הכל סימטרי ומאוזן.

---

## בדיקות שעברו

```
✓ index.html JS syntax (node -c): OK
✓ data.js syntax (node -c): OK
✓ CRLF: 12,881 שורות, 0 lone LF
✓ 1,054 מתכונים נשמרים
✓ Header search limited to 480px
✓ Header uses justify-content: space-between
✓ Communities use flat v7.3 structure (no nested wrapper)
✓ Old Option C placeholder removed
✓ buildPanel branch for s.communityHoliday added
```

---

## קבצים שונו

| קובץ | שינוי |
|---|---|
| `index.html` | + branch `s.communityHoliday` ב-`buildPanel` (רמה 2). + CSS: `.hdr-inner { justify-content: space-between }`, `.hdr-search { flex: 0 1 480px; max-width: 480px; margin: 0 auto }` |
| `data.js` | MENU_STRUCTURE communities שטוח: 9 accordions, כל אחד עם 11 leaf items (1 "כל המתכונים" + 10 חגים) במקום 3 רמות. Option C placeholder הוסר. |

`COMMUNITY_HOLIDAY_TAGS` נשאר זהה — אותם 221 תיוגים יחודיים מ-v7.2.

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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_v7_3_holidays_in_community.md" "." -Force
```
```powershell
git add index.html data.js CHANGELOG_19-04-2026_v7_3_holidays_in_community.md
```
```powershell
git commit -m "v7.3: holidays directly under each community + center header"
```
```powershell
git push origin main
```

---

## אחרי הפריסה (Netlify ~30s)

1. **Header**: שם הספר מימין → שורת חיפוש ממורכזת (לא מתיחה) → התקן/⊙/EN משמאל
2. **תפריט "עדות ישראל"**: לחיצה פותחת רשימת 9 העדות
3. **לחיצה על עדה (למשל "עיראק")**: נפתח accordion עם:
   - "כל המתכונים" (זהוב, רגיל)
   - 10 כפתורי חגים אדומים-אלמוגיים: שבת(9), ראש השנה(5), יום כיפור(4), פסח(6), מימונה (אפור), חנוכה(2), פורים(3), שבועות(3), סוכות(4), חינה(2)
4. **לחיצה על חג**: רשת המתכונים מסוננת לאותם המתכונים המסורתיים בלבד

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
