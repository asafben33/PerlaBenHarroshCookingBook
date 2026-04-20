# CHANGELOG — v8.16: עיצוב מחדש של הספר — מושך, רחב, ועם אופי

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.16

---

## הבקשה

> תגדיל את הפונטים בספר ותפרוס אותו יותר לרוחב המסך כך שלא יהיה צר מידי באמצע.
> מה דעתך להדגיש את הפונט בספר כדי שיהיה ברור יותר? או אם יש לך עצה יותר טובה כי הפונט וסידור התצוגה קצת משעמם ולא מושך את העין לקריאת הספר המעניין הזה.

הבקשה מורכבת משלושה חלקים:
1. **פונטים גדולים יותר**
2. **פריסה רחבה יותר**
3. **עיצוב מושך יותר** — לא רק קריא, אלא מזמין לקריאה

הצעתי: לא רק להגדיל ולהדגיש (זה היה הופך את זה רק לכבד יותר). במקום, **לעצב את זה כמו ספר אמיתי** — כל אלמנט ויזואלי מוסיף אופי וזיווג למה שכבר קיים.

---

## הבעיות הקודמות (v8.12)

| בעיה | למה זה משעמם |
|---|---|
| `max-width: 720px` | עמודה צרה באמצע מסך רחב — מבזבז שטח, יוצר תחושה של "עוד אחד הרבה דפים" |
| `font-size: 1.15rem` | קריא אך לא מושך |
| `text-align: justify` ללא `text-indent` | בלוקים שטוחים — אין סימן ויזואלי לתחילת פסקה |
| כותרות פרק `text-align: right` קטנות | לא בולטות — נראה כמו עוד פסקה |
| אין דקור בין פרקים | זרימה אחידה משעממת |
| אין `drop cap` | שום סימן ויזואלי שמושך את העין לתחילת פרק |
| שום background-per-chapter | הכל זורם רצוף, אין הבחנה בין פרק לפרק |

---

## הפתרון — 11 שיפורים מקצועיים

### 1. רוחב גדול יותר — 720px → **980px**
36% יותר רוחב לתוכן. השורות יותר ארוכות, אבל עדיין בטווח קריאה נוח (75-95 תווים).

### 2. פונט גוף גדול יותר — 1.15rem → **1.25rem (20px)**
9% גידול. נוח לקריאה ארוכה לבני 60+.

### 3. **Drop Cap** — האות הראשונה של פסקה ראשונה בכל פרק
זוהי האותה הקלאסית של ספרים מודפסים — האות הראשונה גדולה במיוחד (4×) וזהובה. זו ה"חתימה" של ספרים אמיתיים.

```css
.book-p:first-of-type::first-letter,
.book-chapter > .book-sub + .book-p::first-letter {
  font-size: 4em;
  font-weight: 900;
  color: var(--c-gold);
  float: right;
  line-height: .85;
  margin: .1em .15em 0 0;
  text-shadow: 0 2px 8px rgba(196,147,10,.35);
}
```

זה בנוי גם אחרי כל `<h3>` (sub-heading) — כך שכל פתיחה של חלק חדש מקבל drop cap.

### 4. **Text-indent** — כניסה לשורה הראשונה של כל פסקה
זה הסטנדרט הטיפוגרפי לפרוזה. הפסקה הראשונה בפרק לא נכנסת (יש לה drop cap), אבל כל פסקה אחרי קוד עם `text-indent: 1.5em`.

### 5. **כותרות פרק מרכזיות + מודגשות**
- `font-size`: 1.4rem → **1.85rem** (+32%)
- `text-align`: right → **center**
- `font-weight`: 700 → **800**
- `text-shadow`: זוהר זהוב עדין

### 6. **דקור עליון בכל פרק** — `✦  ✦  ✦`
שלושה כוכבים זהובים מרוחקים, ממורכזים. סימן ויזואלי שמכריז: "פרק חדש מתחיל!".

### 7. **דקור תחתון בכל פרק** — `※`
סמל המקובל לסוף סעיף בספרים יפניים-מודרניים. אלגנטי וצנוע.

### 8. **רקע parchment לכל פרק**
כל פרק יושב על "דף" עם:
- Linear gradient רך (עמום במצב כהה, parchment במצב בהיר)
- מסגרת זהובה דקיקה
- shadow עמוק שיוצר רושם של נפח (כמו דף מדי-קצת מורם מהמשטח)
- corner radius נדיב (12px)

```css
.book-chapter {
  background: linear-gradient(180deg,
    rgba(28,15,8,.35) 0%,
    rgba(28,15,8,.25) 100%);
  border: 1px solid rgba(196,147,10,.18);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,.25),
              inset 0 1px 0 rgba(255,255,255,.04);
  padding: 2.5rem 2rem 2rem;
}
```

### 9. **קו מפריד מתחת ל-page indicator**
"— עמוד 5 —" עכשיו מקבל קו דקורטיבי קצר מתחתיו (gradient עדין). מוקד את העין על תחילת הפרק.

### 10. **Sub-headings יותר אלגנטיים**
- `font-size`: 1.1rem → **1.25rem**
- מסגרת תחתונה: `dotted` במקום solid (יותר רך)
- צבע מחוזק

### 11. **Photo frame מעוטרת**
תמונות עכשיו מקבלות **אפקט מסגרת זהב כפולה** (כמו תמונה אנטיקוויטית במוזיאון):
```css
box-shadow: 0 6px 24px rgba(0,0,0,.4),
            0 0 0 1px rgba(196,147,10,.4),    /* קו זהב פנימי */
            0 0 0 6px var(--c-deep, #1a0c06), /* רווח שחור */
            0 0 0 7px rgba(196,147,10,.5);    /* קו זהב חיצוני */
```

### 12. **Hover על פסקאות**
פסקה שעומדים מעליה מקבלת רקע זהוב עדין מאוד. לא טריוויאלי — זה עוזר לעקוב בקריאה ארוכה.

---

## בדיקות (17/17 עברו)

```
OK JS syntax: OK
OK JSON-LD valid (1 block, @graph 4 items)
OK CRLF: 13,790 שורות (100%)
OK Size: 565,935 bytes (+5KB מ-v8.15)
OK book-section wider 980px (was 720px)
OK book-p larger 1.25rem (was 1.15rem)
OK first-line indent 1.5em (book convention)
OK drop cap font-size 4em on first paragraph
OK chapter title 1.85rem (was 1.4rem)
OK decorative top ornament ✦ ✦ ✦
OK end-of-chapter symbol ※
OK parchment chapter background gradient
OK better Hebrew justification (text-justify: inter-word)
OK paragraph hover highlight
OK main title bigger 2.2rem
OK subtitle bigger 1.05rem italic
OK chapter title centered (was right)
OK mobile breakpoint 720px (was 600px)
OK Old 720px - REMOVED
OK Old 1.15rem - REMOVED
OK Old ch-title 1.4rem - REMOVED
```

---

## מה הקוראים יחוו

### **לפני (v8.15)**
פותחים את הספר → רואים עמודה צרה באמצע המסך → הטקסט שטוח אחיד → קוראים מספר שורות → "אוקיי..." → סוגרים.

### **אחרי (v8.16)**
פותחים את הספר → רואים **כותרת ענקית זהובה ממורכזת** → "✦ ✦ ✦" קישוט → **אות ראשונה גדולה זהובה** מושכת את העין מיד → הטקסט זורם בפסקאות עם indent → כל פרק יושב על "דף" עם מסגרת → "※" בסוף → המוח רוצה לדעת מה ההמשך → ממשיכים לפרק הבא.

זה ההבדל בין **טקסט להציג** ל-**ספר לקרוא**.

---

## תאימות מובייל

ה-mobile breakpoint עבר מ-600px ל-**720px** (כי הפונט החדש 1.25rem דורש יותר רוחב למניעת רוחב שורה צר).

במובייל:
- `book-p`: 1.25rem → **1.12rem** (יותר קומפקטי)
- `text-indent`: 1.5em → **1.2em**
- Drop cap: 4em → **3.2em** (עדיין מרשים אבל לא יוצא מהמסך)
- Chapter padding: 2.5rem → **1.8rem**

---

## תאימות תמת אור

כל הצבעים מוגדרים גם בתמת בהיר:

| אלמנט | dark | light |
|---|---|---|
| Drop cap | `var(--c-gold)` `#c4930a` | `#b84223` (clay במקום gold) |
| Chapter background | dark gradient | parchment cream gradient |
| Photo frame | dark deep + gold | parchment cream + clay-gold |
| Title text-shadow | golden glow | white-paper highlight |

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | בלוק `book reader` שופץ במלואו (~140 שורות CSS חדשות מתוך 60 קודמות) |

`data.js`, `download_images.py`, `find_videos.py`, `sw.js`, `sitemap.xml`, `robots.txt` — **לא נגעתי**.

---

## פריסה

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_16_book_reader_redesign.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_16_book_reader_redesign.md
```
```powershell
git commit -m "v8.16: book reader complete redesign - 980px wide, 1.25rem font, drop caps, ornate chapter headers, parchment chapter cards, ✦/※ ornaments"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

1. **לחץ על "קרא את הספר"** ובדוק:
   - הספר מתפרס על **כל הרוחב הזמין** (עד 980px)
   - הכותרת הראשית **בולטת ענקית** (2.2rem זהוב עם זוהר)
   - הסאב-טייטל **ב-italic מתחתיה**

2. **כל פרק:**
   - יושב על **"דף"** עם רקע מודגש קלות, מסגרת זהובה ו-shadow
   - מתחיל ב-**`✦  ✦  ✦`** (3 כוכבים מרוחקים)
   - הכותרת **ממורכזת בענק** (1.85rem)
   - **"— עמוד 5 —"** עם קו דקורטיבי תחתיו
   - **האות הראשונה של הפסקה הראשונה — ענקית וזהובה** (drop cap)
   - **"※"** בסוף הפרק

3. **הפסקאות:**
   - גדולות יותר (1.25rem ≈ 20px)
   - יש **indent (1.5em)** בתחילת כל פסקה (לא הראשונה)
   - **hover עדין** — מסיט את העין

4. **תמת אור:**
   - Drop caps ב-clay (`#b84223`) במקום זהוב
   - Chapter cards על רקע parchment cream
   - הכל קריא וחם

5. **תמונות:**
   - אם יש תמונות בספר, הן מקבלות **מסגרת זהב כפולה** מעוטרת

6. **מובייל:** הכל מוקטן באלגנטיות אבל עדיין מרשים

---

## מספרי קריאות סופיים

| מטריקה | v8.15 | v8.16 | יחס |
|---|---|---|---|
| רוחב מקסימלי | 720px | **980px** | +36% |
| גודל פונט | 18.4px | **20px** | +9% |
| גודל כותרת פרק | 22.4px | **29.6px** | +32% |
| גודל כותרת ראשית | 27.2px | **35.2px** | +29% |
| Drop cap | אין | **80px** | חדש |
| Indent בפסקאות | אין | **1.5em** | חדש |
| מסגרת לכל פרק | אין | **קיימת** | חדש |
| ornaments | אין | **2 (✦/※)** | חדש |

---

**הספר עכשיו לא רק קריא — הוא מזמין לקריאה.**

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
