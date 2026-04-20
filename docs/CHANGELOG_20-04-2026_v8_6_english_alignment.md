# CHANGELOG — v8.6: יישור לשמאל באנגלית, חזרה לימין בעברית

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.6 (תיקון CSS — מצב EN/HE)

---

## הבקשה

> 1. כשאני עובר לתצוגה באנגלית של האתר תצמיד את כל המלל לשמאל.
> 2. כשחוזרים לעברית שיחזור להיות כפי שקיים כרגע כשמוצמד לימין.

---

## הגורם

תשתית `html.lang-en` המקיפה כבר הייתה קיימת ב-CSS (שורות 888-911) וגם ב-JS (`applyLang()` שורה 12196 — מוסיף/מסיר את ה-class). אבל ה-CSS overrides היו עם specificity חלש מדי:

```css
html.lang-en .m-ingr-item { direction: ltr; }   /* בלי !important */
```

מסומן בצילום של אסף — שמות המרכיבים נשארים מודבקים לימין באנגלית, וגם שורת ה-chips של זמן/מנות/קושי. ה-overrides נדרסו על ידי הצהרות `direction: rtl` פנימיות באלמנטים נצרכים.

---

## התיקון

### 1. הוספת `!important` לכל overrides של lang-en

CSS specificity של `html.lang-en .m-ingr-q { direction: ltr }` שווה ל-(0,2,1). אבל הצהרת `.m-ingr-q { direction: rtl }` (0,1,0) קודמת בקובץ, מה שדרש !important כדי להבטיח דריסה מוחלטת.

### 2. הוספת overrides שלא היו קיימים

הוספתי 7 elements שלא היו ברשימה:

| Element | תפקיד |
|---|---|
| `.m-meta` | שורת ה-chips (זמן/מנות/קושי) |
| `.m-actions` | כפתורי פעולה (שמירה למועדפים, הדפסה, שיתוף) |
| `.m-act-media` | כפתור מדיה |
| `.m-body` | גוף המודאל |
| `.m-vid-wrap` | תיבת וידאו |
| `.m-hero-nav` | חיצי ניווט בגלריה |
| `.m-hero-dots` | נקודות גלריה |
| `.m-nav` | רצועת ניווט עליונה במודאל |

### 3. הוספת `justify-content: flex-start !important`

ל-`.m-ingr-item` ו-`.m-meta` — כשה-`direction` משתנה ל-LTR, ברירת המחדל של flex היא להציב את הילדים מ-start. עם !important נכפה זאת.

### קוד מלא

```css
html.lang-en #mbox { direction: ltr !important; }
html.lang-en .m-title,
html.lang-en .m-subdesc,
html.lang-en .m-sec-h,
html.lang-en .m-step,
html.lang-en .m-tip-wrap,
html.lang-en .m-tip-label,
html.lang-en .m-src-box,
html.lang-en .m-vid-item,
html.lang-en .m-mem { direction: ltr !important; text-align: left !important; }

html.lang-en .m-mem {
  border-right: none;
  border-left: 3px solid var(--c-gold-d);
  background: linear-gradient(to right, rgba(196,147,10,.1), rgba(196,147,10,.03));
}

/* v8.6: ingredient row */
html.lang-en .m-ingr-item {
  direction: ltr !important;
  justify-content: flex-start !important;
}
html.lang-en .m-ingr-q,
html.lang-en .m-ingr-i {
  direction: ltr !important;
  text-align: left !important;
}

/* v8.6: meta chips row */
html.lang-en .m-meta {
  direction: ltr !important;
  justify-content: flex-start !important;
}
html.lang-en .m-chip { direction: ltr !important; }

/* v8.6: steps padding flip */
html.lang-en .m-steps {
  padding-right: 0 !important;
  padding-left: 1.3rem !important;
  direction: ltr !important;
}

/* v8.6: video / actions / body / nav coverage */
html.lang-en .m-vid-list { direction: ltr !important; }
html.lang-en .m-vid-wrap { direction: ltr !important; text-align: left !important; }
html.lang-en .m-actions { direction: ltr !important; }
html.lang-en .m-act-media { direction: ltr !important; }
html.lang-en .m-body { direction: ltr !important; }
html.lang-en .m-hero-nav { direction: ltr !important; }
html.lang-en .m-hero-dots { direction: ltr !important; }
html.lang-en .m-nav { direction: ltr !important; }
```

---

## התנהגות מעודכנת

### במצב **EN** (אחרי לחיצה על כפתור EN):

```
+---------------------------------+
| [hero image]                    |
|                                 |
| [Mimouna]                       |  ← תווית בשמאל
| Mofletta — Moroccan Mimouna...  |  ← כותרת בשמאל
| The latke the Moroccan...       |  ← תיאור בשמאל
|                                 |
| Mom: night of the Mimouna...    |  ← זיכרון בשמאל (border בשמאל)
|                                 |
| [80 minutes] [20 servings]      |  ← chips מודבקים בשמאל
| [Advanced]                      |
|                                 |
| INGREDIENTS                     |  ← כותרת בשמאל
|                                 |
| 1 kg  flour white bread         |  ← מודבק בשמאל מימין-לשמאל
| 1 spoon  yeast dried            |
|                                 |
| INSTRUCTIONS                    |  ← כותרת בשמאל
|                                 |
| 1. mix flour, yeast, sugar...   |  ← מודבק בשמאל
+---------------------------------+
```

### במצב **HE** (חזרה לעברית):

```
+---------------------------------+
| [hero image]                    |
|                                 |
|                       [מימונה]  ← תווית בימין
|     מופלטה — לטקה מרוקאית...    |  ← כותרת בימין
|     הלטקה המרוקאית האייקונית..  |  ← תיאור בימין
|                                 |
|     אמא: לילה של המימונה...    |  ← זיכרון בימין (border בימין)
|                                 |
|       [80 דקות] [20 יח׳]        |  ← chips מודבקים בימין
|       [מתקדם]                   |
|                                 |
|                       מרכיבים   |  ← כותרת בימין
|                                 |
|        קמח לחם לבן  1 ק״ג       |  ← מודבק בימין
|        שמרים יבשים  1 כפית      |
|                                 |
|                       הכנה      |  ← כותרת בימין
|                                 |
|     ערבב קמח, שמרים, סוכר... .1 |  ← מודבק בימין
+---------------------------------+
```

---

## מה לא נדרש לתקן

- **JS שכבר עובד** — הפונקציה `applyLang()` כבר מוסיפה/מסירה את ה-class:
  ```javascript
  if (lang === 'en') {
    html.classList.add('lang-en');
    html.setAttribute('dir', 'ltr');
  } else {
    html.classList.remove('lang-en');
    html.setAttribute('dir', 'rtl');
  }
  ```
- **תרגום תוכן** — תרגומי המתכונים ל-EN כבר קיימים ב-`pre_en.js`
- **דריסה אוטומטית** — כשחוזרים ל-HE, הסיר את ה-class → ה-overrides לא חלים → חוזר RTL טבעי

זאת אומרת שהתיקון הוא **CSS בלבד**, ללא נגיעה ב-JS, וללא נגיעה ב-data.

---

## בדיקות שעברו

```
✓ index.html JS syntax (node -c): OK
✓ CRLF: 13,080 שורות (100%, 0 lone LF)
✓ data.js: לא נגעתי
✓ html.lang-en .m-meta override (chips)
✓ html.lang-en .m-actions override
✓ html.lang-en .m-body override
✓ html.lang-en .m-vid-wrap override
✓ html.lang-en .m-nav override
✓ html.lang-en .m-hero-nav override
✓ justify-content: flex-start !important
✓ JS class toggling exists (applyLang)
✓ v8.6 markers in CSS comments
```

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | רחיבה ושיפור של בלוק `html.lang-en` (~25 שורות CSS) |

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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_6_english_alignment.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_6_english_alignment.md
```
```powershell
git commit -m "v8.6: strengthen English mode (lang-en) LTR overrides - all modal content aligns left in EN, returns to right in HE"
```
```powershell
git push origin main
```

---

## מה לבדוק אחרי הפריסה

1. פתח כל מתכון
2. לחץ על כפתור **EN** (פינה ימנית-עליונה של ההדר)
3. ודא שכל המודאל מודבק לשמאל:
   - כותרת המתכון
   - תיאור
   - זיכרון של פרלה (עם border בשמאל)
   - chips של זמן/מנות/קושי
   - כותרת INGREDIENTS
   - שמות מרכיבים (`1 kg flour white bread`)
   - כותרת INSTRUCTIONS
   - שלבי הכנה ממוספרים מימין
4. לחץ על כפתור **HE** — הכל אמור לחזור להיות מודבק לימין
5. בדוק במובייל ובדסקטופ

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
