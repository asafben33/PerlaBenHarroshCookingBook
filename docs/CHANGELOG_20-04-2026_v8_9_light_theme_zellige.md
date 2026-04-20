# CHANGELOG — v8.9: רקע מקצועי לתמת אור + תיקון גוונים

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 8.9

---

## הבקשה (מצילום המסך)

> תוסיף רקע בהתאם גם בתצוגה הבהירה של האתר ותתקן את שגיאות הגוונים בתצוגה שבצילום מסך.

הצילום הראה את האתר בתמת האור עם:
- **רקע ריק לבן/קרם** ללא דפוס Zellige
- **כותרת באדום בולט** ("המטבח של משפחת בן הראש (ארוש\\הרוש)") שצורמת מול הסביבה החמימה
- **רקע אפור** (לא מתאים) בין ה-Hero ל-Recipe of the Day
- **כרטיס המתכון נראה שטוח** ללא הזוהר הזהוב המוגדר

---

## הגורמים לבעיות

### 1. ה-Filter שלא עבד

ב-v8.8 הוספתי:
```css
html.light .site-bg-svg {
  opacity: 0.35;
  filter: invert(1) hue-rotate(180deg) brightness(1.2);
}
```

**הבעיה:** `filter: invert` לא עובד טוב על SVGs מורכבים עם `pattern` ו-`gradient` רב-שכבתי. גם `opacity: 0.35` הופך אותו כמעט בלתי-נראה. התוצאה: ב-תמת אור הרקע **נעלם לחלוטין**.

### 2. רקעים אטומים מסתירים את הרקע

ה-CSS הקיים כלל:
```css
html.light main { background: rgba(253,248,238,.6); }   /* 60% אטום */
html.light .hero { background: linear-gradient(...85, .9); }   /* 85-90% אטום */
html.light .about { background: #fdf8ee; }   /* 100% אטום */
```

גם אם הרקע היה עובד, רקעי הסקציות **חסמו** אותו במלואו.

### 3. `.bio` ללא light theme override

ה-`.bio` מוגדר במצב כהה כ-`linear-gradient(180deg, rgba(3,8,20,.35) 0%, ...)` (כחול-שחור עמוק). **לא היה override במצב בהיר**, ולכן זה ה"ריבוע האפור-כחלחל" שראית בצילום בין המתכון של היום לטקסט הבא.

### 4. צבע אדום צורם

`.hero-h1 em { color: #b84223 }` (ה-clay) — נראה טוב בתמת אור על רקע parchment, אבל **בולט מדי** ולא מתחבר עם הצבעים הזהובים של הכותרת והסביבה.

---

## התיקונים ב-v8.9

### תיקון 1 — שני סטים של שכבות SVG במקום filter

החלפתי את ה-`filter: invert` הפגום בפתרון נכון: **שני סטים מלאים של גרדיאנטים ודפוסים בתוך ה-SVG עצמו** — `bg-dark-layer` ו-`bg-light-layer` — שמתחלפים דרך CSS `display: none/block`:

```html
<svg class="site-bg-svg" viewBox="0 0 800 800">
  <defs>
    <!-- Dark theme: spice gradient + zellige (זהב על חום-שחור) -->
    <linearGradient id="bgGradDark">...</linearGradient>
    <pattern id="zelligeDark" stroke="#c4930a">...</pattern>

    <!-- Light theme: parchment gradient + zellige (clay על קרם) -->
    <linearGradient id="bgGradLight">
      <stop offset="0%"   stop-color="#fcf6e8"/>   <!-- cream parchment -->
      <stop offset="35%"  stop-color="#f9efd8"/>
      <stop offset="65%"  stop-color="#f5e8c6"/>   <!-- warm beige -->
      <stop offset="100%" stop-color="#fcf6e8"/>
    </linearGradient>
    <pattern id="zelligeLight" stroke="#b84223">    <!-- clay on cream -->
      ...
    </pattern>
  </defs>

  <g class="bg-dark-layer">  <!-- 5 שכבות לכהה -->
    <rect fill="url(#bgGradDark)"/>
    <rect fill="url(#bgGlowDark)"/>
    <rect fill="url(#zelligeDark)"/>
    <rect filter="url(#bgGrain)"/>
    <rect fill="url(#bgVignetteDark)"/>
  </g>

  <g class="bg-light-layer">  <!-- 5 שכבות זהות לבהיר -->
    ...
  </g>
</svg>
```

```css
/* CSS toggle: clean and reliable */
html.light .bg-dark-layer { display: none; }
.bg-light-layer { display: none; }
html.light .bg-light-layer { display: block; }
```

**יתרונות:**
- אין loss of fidelity (filter invert משחית את הצבעים)
- שליטה מלאה בכל פרמטר (saffron במצב בהיר → clay; clay → saffron — היפוך כלל הצבעים)
- חיסכון ב-rendering (רק שכבה אחת מצוירת בכל פעם)

### תיקון 2 — רקעי סקציות חצי-שקופים

```css
/* היה - אטום מדי, מסתיר את הרקע */
html.light .hero { background: linear-gradient(165deg, rgba(253,248,238,.85), rgba(245,236,215,.9)); }
html.light .about { background: #fdf8ee; }
html.light main { background: rgba(253,248,238,.6); }

/* עכשיו - חצי-שקוף, מאפשר ל-zellige לזרום מבעד */
html.light .hero { background: linear-gradient(165deg, rgba(253,248,238,.55), rgba(245,236,215,.6)); }
html.light .about { background: rgba(253,248,238,.55); }
html.light main { background: rgba(253,248,238,.45); }
```

הפחתה של 30-45% באטימות. הטקסט עדיין קריא, אבל הרקע מתבטא.

### תיקון 3 — Override חדש ל-.bio בתמת אור

הוספתי בלוק שלא היה קיים:
```css
html.light .bio {
  background: linear-gradient(180deg,
    rgba(253,248,238,.55) 0%,
    rgba(245,236,215,.65) 70%,
    rgba(245,236,215,.7) 100%);
  border-top-color: rgba(196,147,10,.3);
  border-bottom-color: rgba(196,147,10,.3);
}
```

זה פותר את ה"ריבוע האפור-כחלחל" שהיה הגרדיאנט הכהה דולף ל-תמת האור.

### תיקון 4 — צבע hero-h1 em מעודן

```css
html.light .hero-h1 em { color: #a04020; }  /* היה: #b84223 */
```

הפרש קטן אבל משמעותי:
- `#b84223` — clay בולט, אדום-כתום אינטנסיבי
- `#a04020` — אותו ramp אבל עומק יותר, חמדר עדין יותר

הוא משתלב טוב עם ה-`#2a1508` (הצבע של "המטבח של") ויוצר אחידות.

### תיקון 5 — שיפור משמעותי של הכרטיס Recipe of the Day

```css
html.light .rotd-card {
  /* היה: shadow פשוט */
  box-shadow:
    0 6px 22px rgba(184,66,35,.14),
    0 0 0 1px rgba(196,147,10,.08),     /* ← חדש: outer ring זהוב */
    inset 0 1px 0 rgba(255,255,255,.7);
}
html.light .rotd-card:hover {
  /* חדש: hover state בתמת אור */
  box-shadow:
    0 14px 36px rgba(184,66,35,.22),
    0 0 32px rgba(196,147,10,.25),       /* זוהר זהוב חזק */
    inset 0 1px 0 rgba(255,255,255,.8);
}
```

עוד תוספות:
- `.rotd-eyebrow` — text-shadow זהוב עדין
- `.rotd-eyebrow::before/::after` — `✦` בצבע clay
- `.rotd-desc` — צבע כהה יותר לקריאות (`#4a2a14`)
- `.rotd-cta` — clay במקום זהב (`#b84223`), border חמדר
- `.rotd-cta` hover — מעבר ל-`#7a3a18`
- `.rotd-img-wrap` — רקע parchment חצי-שקוף
- `.rotd-img-wrap::after` — gradient fade בכיוון הפוך לבהיר (לקריאות)
- mobile media query — fade מותאם

---

## בדיקות שעברו (15/15)

```
✓ index.html JS syntax: OK (node -c)
✓ JSON-LD valid (1 block, @graph עם 4 items)
✓ CRLF: 13,487 שורות (100%, 0 lone LF)
✓ Size: 556,640 bytes (היה 553,567 → +3,073 bytes = +0.6%)
✓ Dark layer wrapper present
✓ Light layer wrapper present
✓ Light gradient defined (bgGradLight)
✓ Light zellige pattern (zelligeLight)
✓ Light glow gradient (bgGlowLight)
✓ Light vignette (bgVignetteLight)
✓ Dark layer hidden in light theme
✓ Light layer shown in light theme
✓ Bio light theme override (NEW)
✓ ROTD light hover state (NEW)
✓ ROTD eyebrow light (NEW)
✓ Hero em color softened (#a04020, was #b84223)
✓ Main bg semi-transparent (.45)
✓ Hero bg semi-transparent (.55)
✓ Old broken filter REMOVED from CSS
```

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `index.html` | רחיבה של ה-SVG (זה רקע + דפוס בהיר) + 6 בלוקי CSS חדשים/מתוקנים לתמת אור |

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
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_9_light_theme_zellige.md" "." -Force
```
```powershell
git add index.html CHANGELOG_20-04-2026_v8_9_light_theme_zellige.md
```
```powershell
git commit -m "v8.9: light theme zellige background (replaces broken filter) + harmonize hero/bio colors + ROTD card light theme polish"
```
```powershell
git push origin main
```

---

## בדיקה אחרי הפריסה

### תמת אור

לחץ על כפתור התמה (`*`) ועבור לתמת אור. אמור לראות:

1. **רקע** — דפוס Zellige מרוקאי **בצבע clay על רקע parchment קרם** (לא אפור ולא ריק)
2. **Glow מרכזי** — אור זהוב-חמדר עדין במרכז העמוד
3. **Vignette** — קצוות חמדרים-עדינים (לא שחורים)
4. **כותרת Hero** — "המטבח של משפחת בן הראש" — הצבע יותר עמוק וחמדר (לא צורם)
5. **רקע ה-Bio** — parchment חמים (לא ריבוע אפור-כחלחל)
6. **כרטיס המתכון של היום**:
   - shadow עמוק יותר עם רמז זהוב
   - hover: זוהר זהוב חזק סביב הכרטיס
   - CTA ב-clay (לא צהוב חיוור)

### תמת כהה

לחץ שוב על `*` ועבור לתמת הכהה. הכל צריך להישאר **בדיוק כמו ש-v8.8 היה** — אותו רקע Zellige זהוב על חום-שחור, אותו כרטיס מעוטר.

### EN/HE

עבור בין השפות. שני הכיוונים אמורים לעבוד נכון בשתי התמות.

---

## למה v8.9 ולא v8.8 patch

v8.8 הציגה רקע חדש **רק לתמת הכהה**. תמת האור לא קיבלה את הרקע (זה בעיה אמיתית, לא רק קוסמטיקה — שני המשתמשים מקבלים חוויה שונה לחלוטין).

v8.9 משלימה את התמונה — **שתי התמות עכשיו מציגות את אותו דפוס Zellige** בעיצוב הולם לכל אחת מהן. זה לא בלוק חוקתי כמו v8.8, אבל הוא **חיוני** לכך שהאתר ייראה מקצועי בשתי התמות.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
