# CHANGELOG — v8.20: דפדוף ריאליסטי איטי עם 9 פריימים תלת-ממדיים

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.20

---

## הבקשה

> תגדיר את הנפשת המעבר בין הדפים איטית יותר כדי שאפשר יהיה לעשות את ההנפשה עם יותר פריימים של דפים שעוברים ואז אולי זה יראה ממש כמו היפוך דף בספר בתלת מימד

הבקשה הזו חכמה מאוד — היא משלבת **שני** עקרונות אנימציה מקצועיים:
1. **הארכת זמן** — נותן יותר זמן למוח לקלוט את התנועה
2. **פריימים נוספים** — תנועה עשירה יותר נראית טבעית יותר

---

## מה השתנה

### לפני (v8.18-v8.19)
```css
animation: book3d-flip-forward 1.2s cubic-bezier(.45,.05,.55,.95) forwards;

@keyframes book3d-flip-forward {
  0%   { transform: rotateY(0deg); }
  100% { transform: rotateY(180deg); }
}
```

**רק 2 פריימים, רק סיבוב על ציר אחד.** התוצאה: הדף "מסתובב" אבל לא נראה כמו דף אמיתי.

### עכשיו (v8.20)
```css
animation: book3d-flip-forward 2.4s cubic-bezier(.55,.05,.45,.95) forwards;

@keyframes book3d-flip-forward {
  0%   { transform: rotateY(0deg) skewY(0deg) translateZ(0px); ... }
  10%  { transform: rotateY(-15deg) skewY(.5deg) translateZ(8px); ... }
  25%  { transform: rotateY(-45deg) skewY(1.5deg) translateZ(20px); ... }
  40%  { transform: rotateY(-75deg) skewY(2deg) translateZ(30px); ... }
  50%  { transform: rotateY(90deg) skewY(0deg) translateZ(35px); ... }
  60%  { transform: rotateY(105deg) skewY(-2deg) translateZ(30px); ... }
  75%  { transform: rotateY(135deg) skewY(-1.5deg) translateZ(20px); ... }
  90%  { transform: rotateY(165deg) skewY(-.5deg) translateZ(8px); ... }
  100% { transform: rotateY(180deg) skewY(0deg) translateZ(0px); ... }
}
```

**9 פריימים, 3 צירי תנועה במקביל, + צל דינמי + בהירות דינמית.**

---

## הטכניקות החדשות

### 1. סיבוב + כיפוף (rotateY + skewY)
**הסוד הגדול.** דף אמיתי לא רק מסתובב — הוא **מתעקל** באוויר. כשהוא בזווית 45° הוא יוצר עקומה קלה (skewY 1.5deg). בשיא (90° אנכי) — חוזר לישר. כשמתחיל ליפול לצד השני — הכיפוף מתהפך (-1.5deg → -2deg).

זה יוצר תחושה אינטואיטיבית של **נייר שמתעקל מכוח הכבידה**.

### 2. הרמה תלת-ממדית (translateZ)
הדף לא נשאר על שולחן הספר. הוא **מתרומם** בזמן התנועה:
- 0%: 0px (שטוח)
- 25%: 20px (מתחיל לעלות)
- 50%: **35px (שיא — מרחף מעל הספר)**
- 75%: 20px (יורד)
- 100%: 0px (שוכב על הצד השני)

זה יוצר את התחושה שהדף **נפרד מהדף שמתחתיו** ועף, במקום פשוט להסתובב על ציר.

### 3. צל דינמי משתנה
ב-CSS box-shadow מקבל ערכים שונים בכל פריים:
- בהתחלה: `0 2px 6px rgba(0,0,0,.2)` — צל קטן
- ב-50% (שיא): `0 22px 40px rgba(0,0,0,.55)` — **צל ענק כהה** (הדף הכי גבוה)
- בסוף: חוזר לקטן

כיוון הצל גם משתנה: בתחילה הצל לצד שמאל (`-16px 18px ...`), באמצע ישר למטה, בסוף לצד ימין (`16px 18px ...`). **הצל "עוקב" אחרי הדף** כמו צל אמיתי תחת תאורה צמודה.

### 4. בהירות דינמית (filter brightness)
האור "תופס" את הדף בזווית הנכונה:
- 0%: brightness(1) — רגיל
- 25%: brightness(1.12) — מתחיל להאיר
- 50%: **brightness(1.2)** — הכי בהיר (הזווית האנכית מקבלת הכי הרבה אור)
- 100%: חזרה ל-1

מדמה את הצורה שבה דף לבן **משקף אור** כשהוא בזווית — אפקט קולנועי.

### 5. שדרה דינמית
ה-`.book3d-pages::before` (קו השדרה האנכי באמצע הספר) **מתרחב** ב-CSS בזמן הדפדוף:
- בדרך כלל: 40px רוחב
- בזמן דפדוף: **80px רוחב, יותר כהה**

מדמה את ההתפצלות הפיזית של ספר עבה כשפותחים אותו או דופקים את הדפים.

### 6. צל "סוויפ" משופר
ה-`.book3d-flip-shadow` (אלמנט נפרד שיושב מעל הדף) עכשיו:
- **9 keyframes** של opacity (0 → .4 → .85 → 1 → 1 → 1 → .85 → .4 → 0)
- `mix-blend-mode: multiply` — הצל מתערבב **כהה אמיתי** עם הטקסט מתחת
- gradient עמוק יותר: `rgba(0,0,0,.65) 0%, rgba(0,0,0,.2) 30%, transparent 60%`

זה יוצר **גל של חושך** שעובר על פני הדף בזמן הדפדוף.

### 7. Easing משופר
- **לפני:** `cubic-bezier(.45,.05,.55,.95)` (S-curve פשוטה)
- **עכשיו:** `cubic-bezier(.55,.05,.45,.95)` (יותר נחרצת בהתחלה והאצה באמצע)

יחד עם 9 הפריימים, זה יוצר תחושה של **כוח כבידה** — הדף מתחיל לאט, מאיץ באמצע, מתמתן בסוף.

---

## התזמון החדש — JS

```javascript
if (book) {
  book.classList.add('is-flipping');
  // v8.20: מוסיף class ספציפי לכיוון
  book.classList.add(direction === 'forward' ? 'flipping-forward' : 'flipping-backward');
}

setTimeout(function() {
  if (flipper && flipper.parentNode) flipper.parentNode.removeChild(flipper);
  if (book) {
    book.classList.remove('is-flipping');
    book.classList.remove('flipping-forward');
    book.classList.remove('flipping-backward');
  }
  if (callback) callback();
}, 2400);  // היה: 1200
```

ה-classes החדשים `flipping-forward`/`flipping-backward` מאפשרים ל-CSS להגיב גם במקומות אחרים (כמו השדרה), לא רק ב-flipper עצמו.

---

## בדיקות (30/30 עברו)

```
JS scripts: 8 total, 0 failed

OK 2.4s forward duration
OK 2.4s backward duration
OK realistic easing curve cubic-bezier(.55,.05,.45,.95)
OK 10% keyframe with skew+translate (-15deg, .5deg, 8px)
OK 25% keyframe (-45deg, 1.5deg, 20px)
OK 40% keyframe (-75deg, 2deg, 30px)
OK 50% apex (90deg vertical, 35px lift)
OK 60% keyframe (curl reverses to -2deg)
OK 75% keyframe (135deg, -1.5deg)
OK 90% keyframe (165deg, -.5deg)
OK 100% final flat (180deg, 0deg, 0px)
OK brightness peak at apex (1.2)
OK shadow apex (0 22px 40px rgba(0,0,0,.55))
OK 2.4s shadow sweep matched
OK shadow blend mode multiply
OK direction-specific flipping-forward class
OK direction-specific flipping-backward class
OK spine widens during flip (40px → 80px)
OK darker spine during flip
OK JS timeout matched to 2400ms
OK JS adds direction class
OK JS cleans up forward class
OK JS cleans up backward class
OK webkit prefix forward keyframes
OK webkit prefix backward keyframes
OK webkit prefix shadow keyframes
OK Old 1.2s forward - REMOVED
OK Old 1.2s shadow - REMOVED
OK Old 1200ms timeout - REMOVED
OK Old easing - REMOVED

CRLF: 14,961 שורות (100%)
Size: 615,483 bytes (+6.7KB מ-v8.19)
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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_20_realistic_flip.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_20_realistic_flip.md
```
```powershell
git commit -m "v8.20: realistic slow page-flip animation - 9 keyframes (2.4s) with rotateY + skewY + translateZ + dynamic shadow + brightness filter + widening spine"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

1. לחץ על "📖 מצב ספר" ופתח את הספר
2. לחץ על דף או על חץ ניווט
3. **תראה:**
   - הדף **מתחיל לעלות** מהשדרה (לא רק מסתובב)
   - **מתעקל** באוויר (כמו נייר אמיתי שמתכופף)
   - **מתרומם 35px מעל הספר** באמצע התנועה
   - **צל ענק כהה** מצטבר תחתיו
   - **בהירות מתעצמת** ב-50% (כמו אור שתופס את הדף)
   - **השדרה מתרחבת ומחשיכה** — מגיב לתנועה
   - **נופל לצד השני** עם כיפוף הפוך
   - **נוחת בעדינות** במקום החדש
4. כל זה ב-**2.4 שניות** — איטי מספיק לראות הכל, מהיר מספיק לא לעצבן

---

## למה זה עובד טוב יותר?

### העיקרון של אנימציה מקצועית
חוסר טבעיות באנימציה לא מגיע מ"מהירות" אלא מ-**חוסר משחק בין צירים מרובים**. תנועה אמיתית של אובייקט פיזי כוללת:
1. תנועה לאורך ציר ראשי (rotation)
2. שינויי צורה כתוצאה מהכוח (deformation)
3. תנועה לאורך צירים אחרים (translation)
4. שינויי תאורה (lighting)
5. תגובה של הסביבה (shadow)

ב-v8.18 היה רק (1). ב-v8.20 יש את כולם.

### הקסם של 9 פריימים
ה-CSS engine עושה interpolation בין פריימים. כשיש רק 2 פריימים, הוא מבצע אנימציה ליניארית — נראה רובוטי. כשיש 9 פריימים עם **erratic skew values**, האנימציה מקבלת **rhythm** טבעי שמדמה כוח כבידה ואינרציה.

זה הקסם של אנימציות Pixar/Disney: **לא הכמות של הזמן, אלא הצפיפות של ה-keyframes**.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
