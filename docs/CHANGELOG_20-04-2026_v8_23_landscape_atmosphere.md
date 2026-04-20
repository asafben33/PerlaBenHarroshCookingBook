# CHANGELOG — v8.23: כפיית מצב Landscape + שיפורי אווירה

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.23

---

## הבקשה / הדיווח

מהסרטון + console log של v8.22 ראיתי:

✅ **מה עבד:**
- StPageFlip נטענה ורצה
- האנימציה של הדפדוף התרחשה (ראיתי את הדף שמתקפל)
- תוכן הדפים קריא
- פתיחה וסגירה של הדפים (log מראה "Flipped to page: 0, 1, 2... 17")

❌ **מה לא עבד:**
1. **מצב Portrait במקום Landscape** - הספר הציג דף יחיד באמצע המסך במקום שני דפים זה לצד זה
2. **הדף המתקפל הופיע רחוק מהספר** (בפינה השמאלית של המסך) - כי הקונטיינר היה רחב מדי (1200px) והספר עצמו התמקם במרכז
3. **הרקע סביב הספר היה שחור לגמרי** - לא מורגש שהספר יושב על רקע אווירה
4. **אין צל מתחת לספר** - נראה כמו דף על רקע שחור, לא כמו ספר

---

## האבחון

### שגיאה 1: `size: 'stretch'` + `usePortrait: true`
ב-StPageFlip, כש`size: 'stretch'` והרוחב הפנוי גדול, הספרייה מחליטה על בסיס יחס גובה/רוחב האם להציג portrait או landscape. עם `usePortrait: true` היא העדיפה portrait **תמיד** כש-width של הקונטיינר שלנו היה 1200px עם height 780px - היחס נראה לה לא מתאים ל-landscape.

### שגיאה 2: הקונטיינר רחב מדי
1200px רוחב זה יותר ממה שצריך לספר של שני דפים ~500px כל אחד. כשהספר יושב באמצע, השוליים של 100px+ מכל צד יוצרים מקום שבו הדף המתקפל יכול "להישמט" בלי קשר ויזואלי לספר.

### שגיאה 3: חסרה אווירה
הקונטיינר שלנו לא הוגדר עם רקע או צל - הוא היה שקוף. StPageFlip רק מצייר את הדפים, לא ספר שלם.

---

## התיקונים

### תיקון 1: `size: 'fixed'` + `usePortrait` דינמי
```javascript
// v8.22 - היה שגוי
size: 'stretch',      // יצר ליזום את StPageFlip לfallback portrait
usePortrait: true,    // תמיד portrait
// minWidth/maxWidth/minHeight/maxHeight: ...

// v8.23 - נכון
size: 'fixed',                   // גודל קבוע שאנחנו קובעים
usePortrait: !isLandscape,       // landscape רק במסך רחב (>= 900px)
autoSize: false,                 // אל תנסה להתאים אוטומטית
```

### תיקון 2: חישוב dimensions נקי
```javascript
// v8.23
var isLandscape = !isMobile && availableWidth >= 900;

if (isMobile || availableWidth < 900) {
  // Portrait: single page
  w = Math.min(availableWidth - 40, 460);
  h = Math.min(availableHeight - 40, w * 1.35);
} else {
  // Landscape: two pages side by side
  w = Math.floor(Math.min((availableWidth - 40) / 2, 500));
  h = Math.floor(Math.min(availableHeight - 40, w * 1.4));
}
```

### תיקון 3: קונטיינר מתאים לספר
```css
/* v8.22 - היה שגוי */
.book-flip-container {
  width: min(1200px, 95vw);    /* רחב מדי */
  height: min(780px, 78vh);
  /* אין רקע, אין צל */
}

/* v8.23 - נכון */
.book-flip-container {
  width: min(1100px, 94vw);     /* מתאים בדיוק לשני דפים */
  height: min(760px, 75vh);
  box-shadow: 0 40px 80px rgba(0,0,0,.7), 0 20px 40px rgba(0,0,0,.5);
  border-radius: 4px;
}
```

הצל מתחת נותן תחושה של ספר **שיושב באוויר** מעל רקע כהה - כמו מצולם עם flash מעליו.

### תיקון 4: maxShadowOpacity יותר גבוה
```javascript
// v8.22: maxShadowOpacity: 0.55   // צל מינימלי בזמן דפדוף
// v8.23: maxShadowOpacity: 0.7    // צל בולט, מרגיש 3D
```

### תיקון 5: flippingTime מ-1200 ל-1000
StPageFlip תוכנן במקור ל-1000ms - זה ה"תזמון טבעי" של הדפדוף. 1200 היה מעט איטי מדי.

---

## סיכום השינויים

| אלמנט | v8.22 | v8.23 |
|---|---|---|
| Container width | 1200px | **1100px** |
| Container height | 780px | **760px** |
| Container shadow | אין | **`0 40px 80px rgba(0,0,0,.7)`** |
| size mode | stretch | **fixed** |
| usePortrait | תמיד true | **רק אם < 900px** |
| autoSize | לא הוגדר | **false** |
| maxShadowOpacity | 0.55 | **0.7** |
| flippingTime | 1200ms | **1000ms** |

---

## בדיקות (11/11 עברו)

```
JS scripts: 9 total, 0 failed

OK CSS: fixed size (not stretch)
OK JS: forced landscape on desktop
OK JS: landscape check (width >= 900)
OK JS: autoSize disabled
OK JS: more visible shadows (0.7)
OK JS: smooth 1s timing
OK CSS: container sized correctly (1100px)
OK CSS: atmospheric box-shadow
OK Old stretch mode - REMOVED
OK Old always-portrait - REMOVED
OK Old wider container - REMOVED

CRLF: 14,741 שורות
Size: 606,751 bytes
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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_23_landscape_atmosphere.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_23_landscape_atmosphere.md
```
```powershell
git commit -m "v8.23: force landscape mode on desktop + atmospheric shadows + proper container sizing"
```
```powershell
git push origin main
```

**אחרי Hard Refresh** (Ctrl+Shift+R), הספר אמור להיראות:
- **שני דפים פתוחים זה לצד זה** (לא דף יחיד במרכז)
- **צל חזק מתחת** שנותן תחושת ריחוף
- **הדף המתקפל מופיע סמוך לספר** (לא רחוק ממנו)
- **האנימציה חלקה ב-1 שנייה**

---

## בדיקה אחרי הפריסה

### DevTools Console — מה לצפות לראות
```
[BookReader] StPageFlip is available, opening book...
[BookReader] Total pages: 44
[BookReader] Created 46 page elements
[BookReader] Container rect: 1100x760
[BookReader] Computed page size: 500x700 (mode: landscape)   ← חשוב!
[BookReader] PageFlip instance created, loading pages...
[BookReader] Found 46 .book-page elements
[BookReader] All set up — ready to flip!
```

המילה המפתח היא **`(mode: landscape)`**. אם תראה `(mode: portrait)` במסך רחב - עדיין יש בעיה.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
