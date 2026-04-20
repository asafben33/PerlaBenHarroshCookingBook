# CHANGELOG — v8.22: תיקוני קריטיים ל-StPageFlip — ה-layout והאתחול

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.22

---

## הבקשה / הדיווח

> לא נראה לי שמשהו השתנה (אחרי v8.21)

הסרטון הראה ש-v8.21 הועלה, הדפים מציגים עם drop caps ומספרי עמוד ("עמודים 3-4") **אבל אין דפדוף ויזואלי**. StPageFlip לא הצליחה לבצע את האנימציה.

---

## האבחון

הבעיה הייתה **3 קונפליקטים בו-זמנית** ב-CSS וב-JS:

### בעיה 1: קונפליקט dimensions
```css
/* v8.21 - שגוי */
.book3d.is-open {
  width: min(1280px, 96vw);  /* הספר מקבל גודל מסוים */
  height: min(880px, 82vh);
}
.book-flip-container {
  width: 100%;                /* הקונטיינר תופס 100% של ההורה */
  height: min(820px, 78vh);   /* גובה אחר! */
}
```
הקונטיינר ירש width מההורה (% מבוסס) אבל height מ-min(). StPageFlip ניסתה לקרוא את הגדלים ב-`getBoundingClientRect()` וקיבלה ערכים לא יציבים.

### בעיה 2: אתחול לפני שה-DOM התעדכן
```javascript
// v8.21 - שגוי
book.classList.add('is-open');           // משנה את ה-CSS
container.innerHTML = ...;                // ממלא תוכן
setTimeout(initializePageFlip, 600);     // 600ms שרירותי - לא תמיד מספיק
```
ה-`setTimeout(600)` לא מבטיח שהדפדפן סיים את ה-layout pass. StPageFlip ניסתה לקרוא dimensions בזמן שה-CSS עוד לא התייצב.

### בעיה 3: שריד קוד מ-v8.21 בתוך ה-replace
היה שריד של `} catch (err)` block ישן ש-cluttered את ה-flow ויצר עוד `setTimeout(600)` כפול.

---

## התיקונים

### תיקון 1: `.book-flip-container` עם dimensions מפורשים
```css
/* v8.22 - נכון */
.book-flip-container {
  width: min(1200px, 95vw);   /* רוחב יציב, תלוי viewport */
  height: min(780px, 78vh);    /* גובה יציב, תלוי viewport */
  margin: 0 auto;
  display: none;
  position: relative;
  z-index: 5;
  box-sizing: border-box;      /* חשוב ל-StPageFlip */
}
```

### תיקון 2: `.book3d.is-open` עם auto sizing
```css
/* v8.22 - נכון */
.book3d.is-open {
  width: auto;                 /* לא מכריח גודל */
  height: auto;                /* הקונטיינר מקבל קוד */
  transform: rotateX(0deg);
  display: flex;               /* flexbox למרכוז */
  align-items: center;
  justify-content: center;
}
```

### תיקון 3: `requestAnimationFrame` במקום `setTimeout`
```javascript
// v8.22 - נכון
requestAnimationFrame(function() {
  requestAnimationFrame(function() {
    setTimeout(initializePageFlip, 50);
  });
});
```

**למה 2 frames + 50ms?**
- Frame 1: הדפדפן מבצע layout pass עם השינויים החדשים
- Frame 2: הדפדפן מבצע paint
- 50ms: גמלאי ביטחון נוסף

זה מבטיח שכשStPageFlip קוראת `getBoundingClientRect()` היא מקבלת **dimensions אמיתיים שכבר התייצבו**.

### תיקון 4: דימנשנים מבוססי-מדידה
```javascript
// v8.22 - מודד את האמת ולא מנחש
var rect = container.getBoundingClientRect();
var availableWidth = rect.width || (window.innerWidth - 60);
var availableHeight = rect.height || (window.innerHeight * 0.75);

if (isMobile || availableWidth < 800) {
  // Single page
  w = Math.min(availableWidth - 20, 420);
  h = Math.min(availableHeight - 20, w * 1.35);
} else {
  // Two-page spread
  w = Math.min((availableWidth - 40) / 2, 540);
  h = Math.min(availableHeight - 20, w * 1.4);
}
```

יחס 1.35-1.4 בין width:height הוא יחס נייר נכון (A4 הוא 1.41).

### תיקון 5: console logs לדיבוג
הוספתי 8 `console.log` הודעות שיגלו בקלות אם משהו לא עובד:
```javascript
console.log('[BookReader] Waiting for StPageFlip library to load...');
console.log('[BookReader] Library loaded after ' + attempts + ' attempts');
console.log('[BookReader] StPageFlip is available, opening book...');
console.log('[BookReader] Total pages: ' + pages.length);
console.log('[BookReader] Created ' + container.children.length + ' page elements');
console.log('[BookReader] Container rect:', rect.width + 'x' + rect.height);
console.log('[BookReader] Computed page size: ' + w + 'x' + h);
console.log('[BookReader] Found ' + pageElements.length + ' .book-page elements');
console.log('[BookReader] PageFlip initialized successfully:', e.data);
console.log('[BookReader] All set up — ready to flip!');
```

ב-DevTools Console נוכל לראות בדיוק היכן זה נכשל.

### תיקון 6: timeout ל-CDN load גדל ל-8 שניות
```javascript
// v8.21 היה 5 שניות (50 attempts × 100ms)
// v8.22 8 שניות (80 attempts × 100ms)
// יותר זמן לגרסאות mobile עם רשת איטית
```

### תיקון 7: הסרת שריד הקוד הישן
היה blockquote של `} catch (err) { ... }, 600);  // give cover-open animation time` שנשאר מ-v8.21 ויצר tags לא מאוזנים. הוסר.

---

## בדיקות (11/11 עברו)

```
JS scripts: 9 total, 0 failed

OK CSS: container has explicit width
OK CSS: container has explicit height
OK CSS: is-open is auto-size (auto, not min())
OK CSS: is-open uses flex
OK JS: separated init function (initializePageFlip)
OK JS: waits for paint (requestAnimationFrame)
OK JS: measures actual dimensions (getBoundingClientRect)
OK JS: debug logs ([BookReader] prefix)
OK JS: 8s wait for library (attempts > 80)
OK Old setTimeout pattern - REMOVED
OK Old error msg - REMOVED

CRLF: 14,732 שורות (100%)
Size: 606,092 bytes (+3KB מ-v8.21 - debug logs)
```

---

## פריסה

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_22_stpageflip_layout_fix.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_22_stpageflip_layout_fix.md
```
```powershell
git commit -m "v8.22: critical fixes for StPageFlip - container dimensions, requestAnimationFrame init, real dimension measurement, debug logs"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה — איך לאבחן

### צעד 1: Hard refresh
**זה קריטי** - הדפדפן עשוי להחזיק קאש של v8.21.

- **Windows:** `Ctrl + F5` או `Ctrl + Shift + R`
- **Mac:** `Cmd + Shift + R`

### צעד 2: פתח את DevTools (F12)
לחץ על "Console" tab.

### צעד 3: לחץ "📖 מצב ספר" → לחץ על הספר
ב-Console צריכים להופיע 10 שורות שמתחילות ב-`[BookReader]`:

```
[BookReader] StPageFlip is available, opening book...
[BookReader] Total pages: 92
[BookReader] Created 94 page elements
[BookReader] Container rect: 1100x780
[BookReader] Computed page size: 540x756
[BookReader] PageFlip instance created, loading pages...
[BookReader] Found 94 .book-page elements
[BookReader] PageFlip initialized successfully: {page: 0, mode: "landscape"}
[BookReader] All set up — ready to flip!
```

### אם רואים שגיאות אדומות:
- **"Failed to load resource: net::ERR_BLOCKED_BY_CSP"** → CSP לא עודכן (לא העלית את index.html החדש)
- **"St is not defined"** → CDN לא הצליח להגיע (מחכה 8 שניות, אז אומר "שגיאה בטעינת המנוע")
- **"Container rect: 0x0"** → הקונטיינר עוד לא התייצב, צריך לחקור עוד
- **"Cannot read properties of null"** → אחד הelements חסר מה-DOM

### אם הכל בסדר אבל עדיין אין אנימציה:
שלח לי screenshot של ה-Console + אגיד לך מה קורה.

---

## איך לאבחן בעצמך

ה-`console.log` המסיבי הוא **הגנה ולא פאר עיצובי** — הוא נכלל **בכוונה** כי אנחנו לא יודעים מה השתבש בלי לראות בכל שלב מה קרה. ב-v8.23 (אם יהיה) אם הכל עובד נסיר אותם.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
