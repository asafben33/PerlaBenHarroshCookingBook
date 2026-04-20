# CHANGELOG — v8.5: צמידת שם המרכיב לכמות (הצמדה לימין)

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026 — חצות+ (אחרי v8.4)
**גרסה:** 8.5 (תיקון CSS אחד שמשפיע על כל המתכונים)

---

## הבקשה

> תצמיד לימין את מה שמסומן באדום בכל כך שיראו בהמשך למלל שמסומן בירוק בכל המתכונים ולא בצורה מדגמית.

לפי הצילום של מתכון "כוטלט (שניצל פרסי ירקות)":
- **ירוק** (צד ימין): כמויות — `3 תפוחי אדמה`, `300 גרם`, `1 ביצה`
- **אדום** (צד שמאל): שמות מרכיבים — `מבושלים ומרוסקים`, `עוף מבושל ומפורק`, `מגורד`

הם היו פזורים לרוחב המודאל — כמויות בימין הרחוק, שמות בשמאל הרחוק, רווח עצום ביניהם. הבקשה: להצמיד את שם המרכיב צמוד לכמות, מימין-לשמאל ברצף טבעי.

---

## הגורם

קובץ `index.html` שורה 861 — מחלקת CSS `.m-ingr-item`:

```css
/* לפני (v8.4) */
.m-ingr-item {
  direction: rtl;
  display: flex;
  justify-content: space-between;  /* ← זה הגורם */
  align-items: baseline;
  padding: .3rem 0;
  border-bottom: 1px solid var(--c-bg3);
}
```

`justify-content: space-between` דוחק את שני הילדים אל הקצוות הרחוקים של ה-flex container. ב-RTL זה מתבטא ב:
- כמות (`.m-ingr-q`) → קצה ימני
- שם מרכיב (`.m-ingr-i`) → קצה שמאלי
- ביניהם רווח גדול ולא רצוי

---

## התיקון

**קובץ:** `index.html` שורות 861-863

```css
/* אחרי (v8.5) */
.m-ingr-item {
  direction: rtl;
  display: flex;
  justify-content: flex-start;       /* ← היה space-between */
  align-items: baseline;
  gap: .6rem;                        /* ← חדש: רווח קבוע בין הכמות לשם */
  padding: .3rem 0;
  border-bottom: 1px solid var(--c-bg3);
}
.m-ingr-q {
  direction: rtl;
  text-align: right;
  font-weight: 600;
  min-width: 80px;
  flex-shrink: 0;                    /* ← חדש: הכמות לא מתכווצת */
  color: var(--c-ink);
  font-size: .88rem;
}
.m-ingr-i {
  direction: rtl;
  text-align: right;
  color: var(--c-ink-m);
  font-size: .88rem;
  flex: 1;                           /* ← חדש: שם המרכיב תופס את שאר הרוחב */
}
```

### למה זה עובד

- `justify-content: flex-start` ב-RTL מציב את שני הילדים בתחילת ה-flex (= צד ימין)
- `gap: .6rem` יוצר מרווח עקבי של ~10px בין הכמות לשם
- `flex-shrink: 0` ב-`.m-ingr-q` מבטיח שהכמות תשאר ב-80px קבועים גם אם השם ארוך
- `flex: 1` ב-`.m-ingr-i` מאפשר לשם לתפוס את שאר הרוחב — מועיל למרכיבים ארוכים שעוברים שורה

### השפעה על ה-DOM

**אין שינוי ב-DOM.** הסדר נשאר כפי שהיה (`q` קודם, אחר כך `i` בקוד JS שורה 8431-8432). רק ה-CSS השתנה. זה אומר:
- ✓ אין שינוי ב-`data.js` (גם לא נדרש)
- ✓ אין השפעה על תרגום אנגלית
- ✓ אין השפעה על הדפסה
- ✓ אין השפעה על light theme

### השפעה על כל המתכונים

מאחר וזה תיקון CSS אחד שמתקבל על-ידי `.m-ingr-item` שמשמש בכל מתכון — **השינוי חל על כל 1,054 המתכונים מיד**, לא בצורה מדגמית.

---

## דוגמה (מתכון `iq8` — כוטלט)

**לפני (פיזור):**
```
3 תפוחי אדמה              מבושלים ומרוסקים
300 גרם                   עוף מבושל ומפורק
1 ביצה                    
1 בצל                     
0.5 כוס                   מגורד
                          פטרוזיליה
1 כפית                    כורכום
```

**אחרי (צמוד לימין):**
```
3 תפוחי אדמה  מבושלים ומרוסקים
300 גרם  עוף מבושל ומפורק
1 ביצה
1 בצל
0.5 כוס  מגורד
פטרוזיליה
1 כפית  כורכום
```

(כעת שם המרכיב צמוד לכמות עם רווח קבוע — לא מתפזר לקצה ההפוך)

---

## בדיקות שעברו

```
✓ index.html JS syntax (node -c): OK
✓ CRLF: 12,993 שורות (100%, 0 lone LF)
✓ data.js syntax: OK (לא נגעתי)
✓ 1,054 מתכונים נשמרים
✓ flex-start applied
✓ gap: .6rem added
✓ flex-shrink: 0 on .m-ingr-q
✓ flex: 1 on .m-ingr-i
✓ space-between removed from m-ingr-item
```

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | 3 שורות CSS שונו (שורות 861-863) |

`data.js` **לא השתנה** מ-v8.4.

---

## פריסה

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" ".\index.html" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_5_ingredient_alignment.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_5_ingredient_alignment.md
```
```powershell
git commit -m "v8.5: align ingredient name next to quantity (RTL right-aligned, was spread to extremes)"
```
```powershell
git push origin main
```

---

## מה לבדוק אחרי הפריסה

1. פתח כל מתכון — שמות המרכיבים אמורים להיות צמודים לכמויות, לא בצד שמאל הרחוק
2. בדוק מתכון עם שם מרכיב ארוך (כמו "תפוחי אדמה מבושלים ומרוסקים") — אמור להמשיך טבעית מהכמות
3. בדוק במובייל ובדסקטופ
4. בדוק במצב light + dark — השינוי לא צריך להשפיע על שום צבע

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
