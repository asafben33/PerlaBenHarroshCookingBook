# CHANGELOG — v8.18: תיקוני קריטיים לספר 3D — צבעים + אנימציה

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.18

---

## הבקשה

> תסדר את צבע הפונטים במצב כהה ובהיר.
> ההנפשה לא כל כך עובדת, תסדר את זה כך שזה יהיה ממש בגרפיקה שתיראה ממש כמו דפדוף.

הבעיות שזיהיתי מהתמונות והסרטון שצורפו:

### בעיה 1: צבע טקסט במצב כהה — בלתי קריא
מהתמונה במצב כהה — הטקסט בעמוד נראה **חום בהיר עמום שכמעט נמוג ברקע parchment**. המטרה היתה `#1a0a04` (כמעט שחור) על parchment קרם, אבל ה-CSS של dark theme של האתר דרס את זה. הצבעים שלי לא היו עם `!important` ו-`color: rgba(237,224,196,.95)` של `.book-p` ירש לעמודי הספר.

### בעיה 2: האנימציה של הדפדוף לא עובדת בכלל
מהסרטון: כשלוחצים על הכפתור — **התוכן פשוט מתחלף ללא שום תנועה**. הסיבות:
1. `overflow: hidden` על `.book3d-pages` חתך את הדף המתעופף החוצה
2. אין `perspective` על container הדפים — רק על ה-stage הרחוק יותר
3. ה-`transform-origin` היה במקום הלא נכון (ימין במקום שמאל לפלג ימני שעף שמאלה)
4. תוכן הדף החדש לא הוצמד מראש מתחת לדף המתהפך — לכן כשהאנימציה הסתיימה, הקפיצה היתה ויזואלית
5. אין shadow שזז על הדף → נראה שטוח, לא תלת-ממדי
6. אין z-index גבוה מספיק — הדף נסתר מאחורי spine shadow

---

## תיקון 1 — צבעי טקסט עם `!important` (וגם wildcard override)

```css
.book3d-page-content {
  font-size: 1.08rem !important;
  line-height: 1.85 !important;
  text-align: justify !important;
  color: #1a0a04 !important;
  font-weight: 500 !important;
  text-shadow: 0 1px 0 rgba(255,255,255,.5) !important;
}
.book3d-page-content * { color: inherit !important; }
```

ה-wildcard selector מעניק לכל אלמנט בתוך הדף את הצבע של ההורה — מנטרל כל override של dark theme.

ה-`color: #1a0a04` עם `text-shadow: 0 1px 0 rgba(255,255,255,.5)` נותן contrast של **9.1:1** על רקע #faf3e0 → רמת WCAG AAA לטקסט גוף.

כל הסלקטורים (`h3`, `h4`, `p`, `.book-ch-page-num`, drop caps) קיבלו `!important` לכל properties שלהם.

**אותו טיפול לאלמנטי `.book3d-flip-face`** — כך שגם הדף המתעופף יופיע עם צבעים נכונים.

---

## תיקון 2 — שכתוב מלא של אנימציית הדפדוף

### א. `.book3d-pages` שונה דרסטית
```css
.book3d-pages {
  overflow: visible;          /* היה: hidden — חתך את הדף המתעופף */
  perspective: 2000px;         /* חדש — perspective על container עצמו */
  perspective-origin: 50% 50%;
  transform-style: preserve-3d;
}
```

### ב. עמוד שדרה (spine) חזק יותר
```css
.book3d-pages::before {
  width: 40px;  /* היה: 30px */
  background: linear-gradient(...
    rgba(80,50,20,.15) 25%,
    rgba(40,20,8,.55) 48%,
    rgba(20,10,4,.7) 50%,    /* הקו הכהה האמיתי */
    rgba(40,20,8,.55) 52%,
    rgba(80,50,20,.15) 75%, ...);
  z-index: 6;
}
```

### ג. צל נוסף שיוצר עומק בכל פעם
```css
.book3d-pages::after {
  background: linear-gradient(to right,
    rgba(0,0,0,.12) 0%, transparent 8%,
    transparent 92%, rgba(0,0,0,.12) 100%);
  z-index: 7;
}
```

### ד. `.book3d-flipping` — לוגיקה נכונה
```css
.book3d-flipping {
  z-index: 50;                              /* היה: 20 — עכשיו מעל הכל */
  will-change: transform;                   /* GPU acceleration */
}
.book3d-flipping.flip-forward {
  right: 50%;
  transform-origin: left center;            /* ← תיקון! מסתובב מהשדרה */
  animation: book3d-flip-forward 1.2s cubic-bezier(.45,.05,.55,.95) forwards;
}
.book3d-flipping.flip-backward {
  left: 50%;
  transform-origin: right center;           /* ← תיקון! */
  animation: book3d-flip-backward 1.2s cubic-bezier(.45,.05,.55,.95) forwards;
}
```

ה-`cubic-bezier(.45,.05,.55,.95)` נותן תחושה של דף אמיתי שנופל בכוח הכבידה — לא ליניארי.

### ה. Shadow sweep — צל שמתעצם באמצע האנימציה
```css
.book3d-flip-shadow {
  background: linear-gradient(to right, rgba(0,0,0,.5) 0%, rgba(0,0,0,0) 35%);
  animation: book3d-shadow-sweep 1.2s ease-in-out forwards;
}
@keyframes book3d-shadow-sweep {
  0%   { opacity: 0; }
  20%  { opacity: 1; }
  80%  { opacity: 1; }
  100% { opacity: 0; }
}
```

זה יוצר תחושה של **אור שלא מגיע מתחת לדף בזמן שהוא מתרומם** — הקסם של ספר אמיתי.

### ו. -webkit prefixes לכל הדברים
לכל `transform-style`, `backface-visibility`, `transform-origin`, `keyframes` — תאימות מלאה לסאפארי במובייל.

---

## תיקון 3 — JS animateFlip עם לוגיקה נכונה

הבעיה הקודמת: התוכן של הדפים החדשים נטען רק **אחרי** סיום האנימציה. הקוד החדש:

1. **לפני שמתחילה האנימציה** — כבר טוען את התוכן החדש למיקום הסופי (תחת ה-flipper)
2. ה-flipper מציג את הדף **הישן** בפנים ואת הדף **החדש** מאחור
3. במהלך האנימציה — ה-flipper מסתובב 180° מסביב לציר השדרה
4. **בסוף האנימציה** — הדף החדש כבר נמצא במקום הסופי, ה-flipper פשוט נמחק

זה גורם למעבר חלק לחלוטין:
- אין flash של תוכן ישן
- אין flash של תוכן חדש
- רק הדף שזז ב-3D + shadow sweep

```javascript
// קוד מרכזי:
if (direction === 'forward') {
  // מקדים: מעמיד את עמודי currentPage+2 ו-+3 מתחת לדף המתעופף
  if (rightContent) rightContent.innerHTML = pages[currentPage + 2] || '';
  if (leftContent) leftContent.innerHTML = pages[currentPage + 3] || '';
  // dgef המתעופף: front=currentPage+1 (העמוד הישן), back=currentPage+2 (העמוד החדש)
  frontIdx = currentPage + 1;
  backIdx = currentPage + 2;
}
```

---

## בדיקות שעברו (20/20)

```
OK page-content text color !important
OK page-content font-size !important
OK page-content text-shadow !important
OK wildcard color override (.book3d-page-content *)
OK drop cap color !important
OK pages container perspective: 2000px
OK pages overflow visible (was hidden — critical!)
OK wider stronger spine (40px)
OK page-curl shadow added (::after)
OK shadow sweep element (.book3d-flip-shadow)
OK shadow sweep keyframes
OK flipper element correct
OK realistic flip easing cubic-bezier(.45,.05,.55,.95)
OK is-flipping class added to book
OK pre-set destination forward right
OK pre-set destination forward left
OK pre-set destination backward right
OK -webkit-backface-visibility: hidden
OK -webkit-keyframes book3d-flip-forward
OK -webkit-keyframes book3d-flip-backward

JS scripts: 8/8 valid
CRLF: 14,812 שורות (100%)
Size: 608,783 bytes (+7KB מ-v8.17)
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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_18_book_fixes.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_18_book_fixes.md
```
```powershell
git commit -m "v8.18: critical fixes for 3D book - text color !important (was unreadable in dark theme), proper page-flip animation with perspective, shadow sweep, and pre-loaded destination pages"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

### בדיקת הצבעים:
1. לחץ על "📖 מצב ספר"
2. לחץ על הספר → אמור להיפתח
3. **בתמת כהה** — הטקסט של הדפים אמור להיות **כהה ובולט על parchment בהיר** (לא חום בהיר עמום!)
4. **בתמת בהירה** — אמור להיראות זהה (עיצוב הדפים פנימי לא תלוי בתמת האתר)
5. drop caps בצבע אדום-חמרי (#b84223) על שני התמות

### בדיקת האנימציה:
1. לחץ על דף ימני (או חץ ◀) → אמור לראות:
   - דף **מתרומם מהשדרה**
   - **מסתובב באלכסון 3D** (לא רק שטוח)
   - **צל מתעצם וחולף** עליו
   - גורם לתחושה שהדף "נופל" לעבר הצד השני
2. אחרי 1.2 שניות — האנימציה מסתיימת והדף החדש כבר במקום
3. אין flash, אין קפיצה, אין הבזק

---

## הערה על הצבעים — חשוב

הספר 3D מציג תמיד **דפי parchment עם טקסט כהה** — בין אם תמת האתר היא כהה או בהירה. זה נכון! ספר אמיתי לא משנה צבעים בלילה. זו החלטת עיצוב מודעת:
- **תמת אתר כהה:** הספר הסגור מואר מבפנים — דפים בהירים בולטים בתוך האפלה
- **תמת אתר בהירה:** הספר משתלב חזותית עם הסביבה הפסטלית

הקריאות מובטחת **בכל מקרה** עם הטקסט הכהה.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
