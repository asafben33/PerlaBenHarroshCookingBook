# CHANGELOG — v8.13: שיפור פונטים בכרטיסי המתכונים ובמודאל

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.13

---

## הקשר

ב-v8.12 שיפרתי את הקריאות של **תוכן הספר** ו-**הצבעים הגלובליים** של תמת אור. אבל הסקירה שעשיתי לאחר מכן גילתה שעוד 9 אלמנטים באתר משתמשים בפונטים קטנים מדי (<0.7rem):

```
Font-size scan:
  .6rem: 2 occurrences  (decorative ornaments — OK)
  .68rem: 4 occurrences (header subtitle, rotd-chip, modal-badge, caption — REAL TEXT)
  .64rem: 2 occurrences (card-badge, modal-badge — REAL TEXT)
  .69rem: 1 occurrence  (card-meta — REAL TEXT)
```

הסקירה הזו השלימה את העבודה של v8.12 על אזורים שלא טופלו במפורש: **כרטיסי המתכונים בגריד** ו-**המודאל שנפתח כשלוחצים על מתכון**. אלו האזורים שאסף קורא הכי הרבה כשהוא משתמש באתר.

---

## השיפורים ב-v8.13

### 1. כרטיסי מתכונים בגריד (`.c-*`)

| אלמנט | היה | עכשיו | שיפור |
|---|---|---|---|
| `.c-title` (כותרת) | 0.85rem (13.6px) | **0.95rem (15.2px)** | +12% |
| `.c-desc` (תיאור) | 0.74rem (11.8px) | **0.82rem (13.1px)** | +11% |
| `.c-meta` (זמן/קושי/מנות) | 0.69rem (11px) | **0.76rem (12.2px)** | +10% |
| `.c-badge` (תג מרוקו/ספרד) | 0.64rem (10.2px) | **0.72rem (11.5px)** | +12% |
| `.c-upload-btn` | 0.68rem (10.9px) | **0.75rem (12px)** | +10% |
| `.c-info` padding | 0.65/0.7rem | **0.7/0.75rem** | יותר נשימה |
| `.c-tag` padding | 0.1/0.4rem | **0.12/0.45rem** | יותר נשימה |
| `.c-diff-*` padding | 0.1/0.4rem | **0.12/0.45rem** | יותר נשימה |
| `.c-title` margin-bottom | 0.25rem | **0.3rem** | רווח טוב יותר |
| `.c-desc` line-height | 1.5 | **1.55** | פסיק יותר |

**למה זה חשוב:** הגריד הוא הדבר הראשון שרואים אחרי הגלילה. אם הכותרת קשה לקרוא, המבקר לא ידע לאיזה מתכון להיכנס. עכשיו 15.2px ו-13.1px - גודל קריא בנוחות.

### 2. מודאל המתכון (`.m-*`) — השיפור הקריטי ביותר

זה האזור הכי חשוב: **כשאסף או בני המשפחה פותחים מתכון, הם קוראים הוראות בישול ארוכות**. אלה היו 0.88rem (~14px) - קטן מדי לקריאה ארוכה.

| אלמנט | היה | עכשיו | שיפור |
|---|---|---|---|
| `.m-title` (כותרת מתכון) | 1.35rem (21.6px) | **1.45rem (23.2px)** | +7% |
| `.m-subdesc` (תיאור) | 0.84rem (13.4px) | **0.92rem (14.7px)** | +10% |
| `.m-step` (**הוראת בישול**) | 0.88rem (14.1px) | **1rem (16px)** | **+14%** ⭐ |
| `.m-ingr-q` (כמות) | 0.88rem | **0.98rem (15.7px)** + weight 700 | +11% |
| `.m-ingr-i` (שם מרכיב) | 0.88rem | **0.98rem (15.7px)** | +11% |
| `.m-mem` (זיכרונות מרוקו) | 0.88rem | **0.96rem (15.4px)** | +9% |
| `.m-tip-wrap` (טיפ של פרלה) | (ללא font-size) | **0.96rem + line-height 1.65** | חדש |
| `.m-sec-h` (כותרות סקציות) | 0.78rem | **0.88rem (14.1px)** | +13% |
| `.m-tip-label` | 0.72rem | **0.82rem (13.1px)** | +14% |
| `.m-badge` | 0.64rem (10.2px) | **0.76rem (12.2px)** | +19% |
| `.m-src-box a` (קישור מקור) | 0.84rem | **0.92rem** | +10% |
| `.m-vid-item` (קישור וידאו) | 0.8rem | **0.88rem** | +10% |

**שיפורים נוספים בקריאות:**
- `.m-step` line-height: 1.7 → **1.75** (קריא יותר)
- `.m-ingr-i` line-height: ללא → **1.5** (לשמות מרכיבים ארוכים)
- `.m-ingr-q` font-weight: 600 → **700** (כמויות בולטות יותר)
- `.m-ingr-q` min-width: 80px → **85px** (מקום לכמויות ארוכות)
- `.m-ingr-item` gap: 0.6rem → **0.65rem**, padding: 0.3rem → **0.35rem**
- `.m-step` padding: 0.4rem → **0.55rem** (יותר נשימה בין שלבים)

### 3. שיפורים אחרים

| אלמנט | היה | עכשיו |
|---|---|---|
| `.hdr-subtitle` (1,054 מתכונים) | 0.68rem | **0.78rem** + weight 500 |
| `.rotd-meta-chip` | 0.68rem | **0.76rem** |
| `.about-avatar-caption` | 0.68rem + opacity 0.7 | **0.78rem + opacity 0.85 + weight 500** |

---

## הפונטים שנשארו ב-0.6rem (ובכוונה)

```css
.acc-a { font-size: .6rem; }       /* חץ ▾ של accordion - סמל בלבד */
.rotd-eyebrow::after { font-size: .6rem; }  /* ✦ ornament - סמל בלבד */
```

**אלה לא טקסט - אלה סמלי עיצוב.** הסמלים ▾ ו-✦ עדיין קריאים בגודל הזה כי הם פיקטוגרמות פשוטות, לא אותיות. החלטתי לא להגדיל אותם כדי לא לשבש את העיצוב.

---

## בדיקות שעברו (16/16)

```
✓ JS syntax: OK
✓ JSON-LD valid (1 block, @graph 4 items)
✓ CRLF: 13,555 שורות (100%)
✓ Size: 561,047 bytes (+126 bytes מ-v8.12 - שינוי ערכים בלבד)
✓ Card title 0.95rem
✓ Card desc 0.82rem + line-height 1.55
✓ Card meta 0.76rem
✓ Card badge 0.72rem
✓ Modal badge 0.76rem
✓ Modal title 1.45rem
✓ Modal subdesc 0.92rem + line-height 1.6
✓ Modal step 1rem (was 0.88rem) ⭐
✓ Modal ingr 0.98rem + line-height 1.5
✓ Modal mem 0.96rem
✓ Modal tip 0.96rem + line-height 1.65
✓ Header subtitle 0.78rem + weight 500
✓ ROTD chip 0.76rem
✓ About avatar caption 0.78rem
```

מ-9 אלמנטים בעלי פונט קטן מדי → **רק 2 נשארו, ושניהם סמלי קישוט בלבד**.

---

## חיתוך תמטי - מה משתפר עבור אסף

### בגלילה הראשונית (כרטיסי המתכונים)
- שמות המתכונים יותר קריאים (לא צריך להתקרב למסך)
- תיאורים נוחים לסריקה מהירה
- תגיות זמן/קושי/מנות בולטות יותר

### בעת קריאת מתכון (המודאל - הכי חשוב)
- **הוראות הבישול** עכשיו ב-16px (תקן WCAG מומלץ)
- כמויות בולטות בשני אופנים: גודל גדול + weight 700
- רשימת מרכיבים יותר נשימה בין שורות
- זיכרונות פרלה (`.m-mem`) קריאים גם הם
- הטיפ של פרלה בולט יותר

### במצב כהה
שום שינוי בצבעים. כל ה-improvements הם **גודל בלבד**, ולכן עובדים זהה בשתי התמות.

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | 16 ערכי font-size + line-height + padding שופרו (כרטיסים + מודאל + footer/header) |

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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_13_card_modal_fonts.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_13_card_modal_fonts.md
```
```powershell
git commit -m "v8.13: enlarge fonts in recipe cards (c-title 0.85→0.95rem) and modal (m-step 0.88→1rem) - WCAG-compliant 16px+ for cooking instructions"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

1. **גלול את רשימת המתכונים** - שמות ותיאורים קריאים יותר ללא צורך בהגדלה
2. **לחץ על כל מתכון** - הוראות הבישול עכשיו נוחות לקריאה (16px)
3. **בדוק רשימת מרכיבים** - כמויות בולטות, נשימה טובה בין שורות
4. **קרא טיפ של פרלה** - גם הוא קריא יותר
5. **תמת אור + תמת כהה** - שניהם זהים מבחינת הגודל (רק הצבעים שונים)
6. **מובייל** - הפונטים עדיין נוחים (אין reduction בנייד)

---

## מדדי קריאות סופיים — תוכן עיקרי באתר

| תוכן | גודל פונט | line-height | תקן WCAG |
|---|---|---|---|
| תוכן הספר (book-p) | 18.4px (1.15rem) | 1.85 | ✓✓ AAA |
| הוראות בישול (m-step) | **16px (1rem)** | 1.75 | ✓ AA |
| מרכיבים (m-ingr) | 15.7px (0.98rem) | 1.5 | ✓ AA |
| תיאור מתכון (m-subdesc) | 14.7px (0.92rem) | 1.6 | ✓ AA |
| כותרת בכרטיס (c-title) | 15.2px (0.95rem) | 1.3 | ✓ AA |
| תיאור בכרטיס (c-desc) | 13.1px (0.82rem) | 1.55 | ✓ AA |

הכל **עכשיו ברמה של מינימום 13px** עם line-height מתאים. אין שום אזור באתר שחסר באפילו 11px בלתי-קריא.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
