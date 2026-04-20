# CHANGELOG — v8.8: רקע מקצועי חדש + עיצוב מחודש של "המתכון של היום"

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.8

---

## הבקשה (מצילום המסך)

> 1. תסיר את הרקע הקיים בתצוגה החשוכה ותתאים רקע לאתר לפי כלי עיצוב מקצועיים בהתאם למהות האתר ואופיו.
> 2. תעצב בצורה יותר יפה את הצגת "מתכון היום הנבחר" ולא כפי שזה נראה בצילום מסך המצורף בשילוב של כלל האלמנטים שבאתר.

הצילום הראה את האתר במצב כהה — רקע "קזבלנקה בלילה" (בנייני העיר עם כיפת מרכזית עם מגן דוד), וכרטיס "מתכון היום" פשוט יחסית עם תמונה משמאל וטקסט מימין.

---

## חלק 1 — רקע מקצועי חדש

### הבעיה ברקע הקודם

הרקע הישן (`.casablanca-bg`) היה SVG מורכב של **18,354 תווים** המתאר את קזבלנקה בלילה — עם בנייני עיר, גגות, כיפה, מגן דוד וכו'. זה היה:

- **כבד מדי** — 18KB של SVG markup רק לרקע
- **מציג נושא ספציפי מדי** — בנייני עיר במקום אופי מטבחי
- **מתחרה עם התוכן** — האלמנטים הוויזואליים של הבנייה מסיחים את העין מהמתכונים
- **לא משקף את מהות האתר** — האתר הוא על אוכל, לא על אדריכלות

### הפתרון — רקע מבוסס Zellige מרוקאי

החלפתי ב-SVG מקצועי של **3,210 תווים** (חיסכון של 82%) המבוסס על מוטיבים אותנטיים:

```
Layer 1: Spice gradient                    (#0d0703 → #1a0c06 → #2a1108 → #0d0703)
Layer 2: Warm radial glow                  (saffron + clay tints, 8% opacity)
Layer 3: Zellige pattern                   (8-point Moroccan star, 120×120 tile)
Layer 4: Paper grain texture               (feTurbulence noise, 4% opacity)
Layer 5: Vignette                          (darker edges to focus center)
```

### למה Zellige?

**זליג'/זליז'** (זה מה שזה נקרא בערבית: زليج) הוא ה**אומנות הקרמית הגיאומטרית המרוקאית הקלאסית** — אותה אריחים צבעוניים שמכסים קירות במסגדים, ארמונות ומבני מגורים בפס, מרקש ושאר ערי מרוקו. זה ה**חתימה הוויזואלית** של מרוקו, ולכן הרבה יותר מתאים מאדריכלות עירונית.

הסטרנים אצלנו — כוכב 8-נקודות מורכב משני ריבועים מסובבים ב-45°, אוקטגון פנימי, ונקודה במרכז — הם הצורה הקלאסית. אבל בעדינות בלבד (opacity 0.18) — שלא מסיח מהתוכן.

### צבעי הרקע

הצבעים מבוססים על **תבלינים מרוקאיים** ולא על שמיים-לילה:

| משתנה | RGB | אסוציאציה |
|---|---|---|
| `#0d0703` | חום-שחור עמוק | קלאי שרוף (clay) |
| `#1a0c06` | חום-קקאו | פלפל אנגלי |
| `#2a1108` | חום-שוקולד | זנגביל מרוקאי |
| `#c4930a` (saffron) | זהב-כתום | זעפרן (מרכיב יקר במטבח) |
| `#b84223` (clay) | אדום-כתום | פפריקה / הריסה |

זה לא **רקע "כהה"**, זה **רקע "תבלינים חשוכים"** — הבדל גדול ב-feel.

### תאימות לתמת אור

ה-CSS החדש כולל פילטר חכם לתמת האור:

```css
html.light .site-bg-svg {
  opacity: 0.35;
  filter: invert(1) hue-rotate(180deg) brightness(1.2);
}
```

המשמעות: באור הזליג'ה מופיע **בהיר וזהוב** במקום כהה — מתאים לרקע parchment שכבר קיים באתר.

---

## חלק 2 — עיצוב מחודש של "המתכון של היום"

### הבעיה בעיצוב הקודם

הכרטיס בצילום המסך נראה **פשוט מדי** — תיבה כהה עם תמונה קטנה (220px) משמאל, טקסט קצר מימין, ותו לא. זה לא **מציג** את המתכון, רק **רושם** אותו.

מה היה חסר:
- קווי הפרדה / מסגרת מעוטרת
- היררכיה ויזואלית בין כותרת/תיאור/CTA
- אפקטים אינטראקטיביים (hover state עדין)
- "אופי" המתאים לאופי החגיגי-מסורתי של שאר האתר

### הפתרון — עיצוב "מסגרת חגיגית"

עיצוב חדש שמשלב **כל האלמנטים מהאתר** (כפי שביקשת):

#### 1. Eyebrow עם קישוטים

```
                    ✦ המתכון של היום ✦
```

הקישוטים `✦` מותאמים לאלה שכבר קיימים ב-Hero (`✦ ✦ ✦`) — יוצר אחידות.

#### 2. Decorative top divider

קו זהוב מדורג מעל ה-eyebrow:
```css
background: linear-gradient(to left,
  transparent 0%, rgba(196,147,10,.5) 50%, transparent 100%);
width: 220px;
```

#### 3. Frame עם inner gold line

הכרטיס עצמו מקבל **שתי שכבות מסגרת** — חיצונית עם border קל, ופנימית עם `::before` שמייצר קו זהוב פנימי 6px בתוך הכרטיס. זה ה-effect של **מסגרת קלאסית מעוטרת**, כמו תמונת קודש או דף מספר עתיק.

```css
.rotd-card::before {
  content: '';
  position: absolute;
  inset: 6px;
  border: 1px solid rgba(196,147,10,.18);
  border-radius: calc(var(--r-md) - 4px);
}
```

#### 4. תמונה גדולה יותר + zoom on hover

| מידה | היה | עכשיו |
|---|---|---|
| רוחב תמונה | 220px | **320px** |
| גובה מינימלי | 160px | **220px** |
| Hover effect | אין | **scale(1.05) + 0.6s smooth zoom** |
| Gradient fade | אין | **fade שמאלה לקריאות** |

#### 5. טיפוגרפיה משודרגת

| אלמנט | היה | עכשיו |
|---|---|---|
| כותרת | 1.15rem, weight 700 | **1.55rem, weight 700, Frank Ruhl Libre** |
| תיאור | 0.85rem, 2 שורות | **0.95rem, 3 שורות, line-height 1.65** |
| Chips | 0.72rem padding 0.55rem | **0.76rem padding 0.7rem** |
| CTA | פשוט | **קו עליון מפריד, hover changes color** |

#### 6. Decorative flourish

`✧` קטן בפינה ימנית-עליונה של הגוף — חוזר למוטיב הקישוטים הזהובים שמופיעים לאורך כל האתר.

#### 7. Hover state מקצועי

```css
.rotd-card:hover {
  border-color: rgba(196,147,10,.6);  /* גבול זוהר יותר */
  transform: translateY(-3px);          /* עליה קלה */
  box-shadow:
    0 14px 36px rgba(0,0,0,.5),       /* צל עמוק */
    0 0 32px rgba(196,147,10,.18),    /* זוהר זהוב סביב */
    inset 0 1px 0 rgba(255,255,255,.06); /* highlight עליון */
}
```

זה נותן תחושה של **כרטיס יקר מעוטר שמרים מהדף**.

#### 8. Layered background ב-card

```css
background: linear-gradient(135deg,
  rgba(28,15,8,.85) 0%,
  rgba(45,22,10,.78) 100%);
```

ולא צבע אחיד. זה נותן **עומק** — דומה לחלבון/חרסינה מבריקה.

#### 9. Mobile responsive משופר

**Breakpoint:** הוגדל מ-600px ל-720px — מסכים בינוניים נוטים יותר ל-stack.

**במצב מובייל:**
- תמונה למעלה (220px גובה), טקסט למטה
- Padding מותאם
- כותרת קטנה יותר (1.3rem במקום 1.55rem)
- Gradient fade משתנה כיוון (מלמטה במקום משמאל)

#### 10. תמיכה מלאה ב-EN mode (lang-en)

לפי הסטנדרט של v8.6 — כל ה-overrides עם `!important`:

```css
html.lang-en .rotd-section, .rotd-card, .rotd-body, ...
{ direction: ltr !important; text-align: left !important; }
html.lang-en .rotd-body::before { right: auto; left: 1.6rem; }
html.lang-en .rotd-img-wrap::after {
  background: linear-gradient(to right, ...);  /* fade הופך כיוון */
}
```

### השוואה לפני/אחרי

| היבט | היה (v8.7) | עכשיו (v8.8) |
|---|---|---|
| תמונה | 220px | **320px (+45%)** |
| מסגרת | קו דק יחיד | **שכבה כפולה (חיצונית + זהובה פנימית)** |
| Eyebrow | טקסט בלבד | **`✦ עם קישוטים ✦`** |
| Hover | translate -2px | **translate -3px + zoom + golden glow** |
| CTA | בלי הפרדה | **קו עליון מפריד + hover color change** |
| Gradient ב-card | אין | **linear-gradient 135°** |
| Flourish | אין | **`✧` בפינה** |
| Top divider | אין | **קו זהוב מדורג** |
| Image transition | אין | **600ms cubic-bezier zoom** |
| Image fade | אין | **fade gradient לקריאות** |
| Mobile breakpoint | 600px | **720px** |

---

## בדיקות שעברו (10/10)

```
✓ index.html JS syntax: OK (node -c)
✓ JSON-LD valid (1 block, @graph עם 4 items)
✓ CRLF: 13,418 שורות (100%, 0 lone LF)
✓ Size: 553,567 bytes (היה 567,038 → -13,471 = -2.4% חיסכון)
✓ New site-bg class
✓ Moroccan zellige pattern present
✓ Spice gradient bgGrad defined
✓ ROTD image wrap
✓ ROTD grid 320px (was 220px)
✓ Smooth animation curves (cubic-bezier)
✓ Image zoom on hover (scale 1.05)
✓ Old casablanca-bg class: REMOVED from HTML
```

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | החלפת רקע (-15KB SVG) + עיצוב מחודש של ROTD (~+200 שורות CSS) |

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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_8_background_rotd_redesign.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_8_background_rotd_redesign.md
```
```powershell
git commit -m "v8.8: replace casablanca background with moroccan zellige + spice gradient (15KB lighter), redesign Recipe of the Day with ornate framing + larger image + hover effects"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

1. **רקע** — פתח את האתר. הרקע אמור להיות:
   - **כהה אחיד** עם דפוס זליג'ה זהוב עדין מאוד
   - **גרעין נייר** קל (paper grain)
   - **vignette** סביב הקצוות
   - **ללא בנייני עיר** (קזבלנקה הלילית הוסרה)
2. **תמת אור** — לחץ על `*` (כפתור התמה). הרקע אמור להיהפך לבהיר עם דפוס זהוב יותר בולט.
3. **המתכון של היום** — גלול מתחת ל-Hero. אמור לראות:
   - קו זהוב מדורג למעלה
   - "✦ המתכון של היום ✦" בקישוטים
   - כרטיס עם מסגרת זהובה כפולה
   - תמונה גדולה (320px במחשב, 220px גובה במובייל)
   - כותרת ב-Frank Ruhl Libre בולטת
4. **Hover על הכרטיס** — אמור לראות:
   - הכרטיס עולה 3px
   - גבול זהוב מתהדר
   - תמונה זומ-אין עדינה (scale 1.05)
   - זוהר זהוב סביב הכרטיס
5. **לחץ על הכרטיס** — אמור לפתוח את המתכון
6. **EN mode** — לחץ EN. הכל אמור להיות מודבק לשמאל
7. **HE mode** — לחץ HE. הכל אמור לחזור לימין

---

## למה זה עדיף ממה שהיה

### רקע
**היה:** SVG כבד של בנייני קזבלנקה — מתחרה עם התוכן, "רעש ויזואלי" שגוזל את העין
**עכשיו:** דפוס מרוקאי אותנטי **שמשרת את התוכן** במקום להתחרות בו. גם 82% קל יותר.

### Recipe of the Day
**היה:** כרטיס פשוט שנראה כמו פיצ'ר טכני. לא מזמין לקריאה.
**עכשיו:** **מצגת יקרה ומעוטרת** שמכבדת את המתכון. הכרטיס עכשיו מרגיש כמו דף מתוך ספר עתיק עם מסגרת זהובה — מאוד מתאים לאופי המורשתי של האתר. תמונה גדולה יותר מציגה את המנה כראוי.

האתר עובר מ"רשימה דיגיטלית" ל"**ספר בישול דיגיטלי בעל אופי**".

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
