# ספר הבישול של פרלה בן הראש ז"ל

**גרסה: 7.1 | 19/04/2026**

## זהות הפרויקט
- אתר (Netlify): https://perlabenharrosh-cookingbook.netlify.app/
- אתר (GitHub Pages): https://asafben33.github.io/PerlaBenHarroshCookingBook/
- GitHub: https://github.com/asafben33/PerlaBenHarroshCookingBook.git
- Branch: main — פרוס אוטומטית ב-Netlify וב-GitHub Pages
- User: Asaf Yaakov Ben-Harrosh (אסף יעקב בן-הראש), youngest son (בן הזקונים) of Perla & Pinchas z"l

## מבנה הקבצים
- `index.html` — HTML ראשי + JS inline (כל הלוגיקה) — v7.1: ~515 KB
- `data.js` — 1,054 מתכונים (CATS, MENU_STRUCTURE, HOLIDAY_TAGS, const R=[...])
- `book_data.js` — תוכן הספר הביוגרפי (BOOK_HTML, BOOK_HTML_EN)
- `pre_en.js` — תרגומים לאנגלית (pre-rendered)
- `about_redesigned.{html,css,js}` — דף "אודות" מעוצב מחדש
- `sw.js` — Service Worker (network-first למסמכים, cache-first לתמונות)
- `manifest.json` — PWA manifest (PWA install button פעיל מ-v6.3)
- `_headers` — Netlify HTTP headers (CSP, X-Frame-Options, etc.) — v6.2
- `images/recipes_images/` — תמונות מתכונים: `r-{id}.jpg`
- `images/book_images/` — תמונות ספר: `WhatsApp_Image_*.jpeg` + `wedding.jpg`
- `images/site_images/` — אייקונים, OG image, favicons, `cat-*.jpg` fallbacks

## סקריפטי ניהול (v6.7)
- `recipe_utils.py` — ספריית עזר: parser של `data.js`, כותב עם גיבוי, לוגר, CLI Hebrew UI + rtl_fix ל-Windows
- `add_recipe.py` — אשף אינטראקטיבי להוספת מתכון (7 שלבים, validation, preview, `--dry-run`)
- `edit_recipe.py` — אשף עריכה/מחיקה של מתכון קיים
- פרטים ב-`README_Recipe_CLI.md`

## מסמכי תיעוד
- `HLD_Perla_CookingBook.md` — High-Level Design (עודכן ל-v7.1)
- `LLD_Perla_CookingBook.md` — Low-Level Design (עודכן ל-v7.1)
- `INTEGRATION_GUIDE.md` — מדריך אינטגרציה (Web3Forms מ-v6.6)
- `README.md` — סקירה כללית (עודכן ל-v7.1)
- `README_Recipe_CLI.md` — מדריך לסקריפטי Python
- `PLAN_v7_0_HEBREW.md` + `PLAN_v7_0_ENGLISH.md` — תוכנית תכנון v7.0 (מוגשמת)
- `CHANGELOG_19-04-2026_v6_3.md` → `v7_1.md` — לוג שינויים לכל סשן

## כללי עבודה
- כל התמונות מוגשות מתוך תיקיית `images/` (לא מ-root)
- נתיב תמונות מתכונים: `images/recipes_images/r-{id}.jpg`
- נתיב תמונות ספר: `images/book_images/`
- נתיב תמונות קטגוריה: `images/site_images/cat-{cat}.jpg` (20 placeholders)
- אסור להשתמש ב: `loremflickr.com` (403), `upload.wikimedia.org` (429), `picsum.photos` (CSP block)
- שפת ממשק: עברית בלבד כברירת מחדל, RTL (עם toggle ל-EN)
- אחרי כל שינוי: `git add` → `git commit` → `git push` (PowerShell, פקודות אחת אחת)
- CRLF line endings חובה (`index.html` משתמש ב-`\r\n`)

## מבנה מתכון (data.js) — שדות חובה
`id, cat, badge, title, desc, time, serv, diff, img, mem, ingr, steps, tip`
שדות אופציונליים: `src, vid, tags`

## קטגוריות (20 ב-CATS, כולל all)
`all, soups, salads, veg, meat, chick, fish, hol, des, span, iraq, kurd, ashk, yem, pers, buk, tun, isr, turk, nonkosher`

### ספירת מתכונים לפי קטגוריה (ל-1,054 סה"כ)
- **מרוקו (671):** soups=103, salads=103, veg=87, meat=82, hol=80, des=80, fish=70, chick=66
- **עדות ישראל (270):** iraq/kurd/ashk/yem/pers/buk/tun/isr/turk = 30 × 9
- **ספרד (73):** span
- **לא כשר (40):** nonkosher (14 פירות ים + 26 בשר+חלב)

## ארכיטקטורת ניווט — MENU_STRUCTURE (v7.0+)

**מבנה שטוח של 6 קבוצות עליונות מקבילות** (הוחלף ב-v7.0 את ה-wrapper הבודד של v6.x):

| `key` | תווית | `ids` (group aggregate) | מתכונים | עומק מקסימלי |
|---|---|---|---|---|
| `all` | הכל | (leaf, `id:'all'`) | 1,054 | 0 |
| `morocco` | מרוקו | 8 cat-IDs | 671 | 2 (מנות עיקריות → בשר/עוף/דגים) |
| `spain` | ספרד | 73 recipe-IDs | 73 | 1 |
| `communities` | עדות ישראל | 9 cat-IDs | 270 | 2 (מטבח ישראלי → 4 תתי) |
| `holidays` | חגים | `['hol']` | 80 | 1 |
| `nonkosher` | לא כשר | 40 recipe-IDs | 40 | 1 |

**עומק קינון מקסימלי בכל התפריט: 2 רמות** (היה 4 ב-v6.x).

**Option C — חגי העדה:** תחת "עדות ישראל" יש placeholder מיוחד:
```javascript
{placeholder:'communityHolidays', lbl:'חגי העדות (בקרוב)',
  emptyMsg:'מתכונים לחגי העדות יתווספו בעתיד...'}
```
לחיצה מציגה `showToast()`. עתיד: תיוג ידני של מתכוני עדות לחגים.

## לוגיקת תמונות ב-index.html
- `getRecipeImg(r)` תמיד מחזירה `images/recipes_images/r-{id}.jpg` (לא `r.img`)
- **v6.5:** `_heroGalleryInit` מנסה וריאנטים `-2`/`-3` רק אם התמונה הראשית נטענת — הפחתה משמעותית של רעש 404 בקונסול
- `r.img` הוסר מ-fallback ב-v6.1 (מונע 1054 CSP violations)
- fallback chain: `CAT_IMG[r.cat] → CAT_IMG._def`
- `_IMG_ALIAS` ממופה על ידי `download_images.py` v5.1 (`--inline-alias`)
- `CAT_IMG` כל הנתיבים מקומיים (`images/site_images/cat-*.jpg`)

## מערכת פידבק — היסטוריה + מצב נוכחי

| גרסה | Backend | סטטוס |
|------|---------|-------|
| v6.0–v6.2 | Netlify Forms | ✗ 405 ב-GitHub Pages |
| v6.3 | FormSubmit.co AJAX + `fetch()` | ✗ CORS preflight fail |
| v6.4 | FormSubmit.co + hidden iframe | ✗ 403 (anti-spam) |
| v6.5 | FormSubmit + שדה `_url` | ✗ עדיין 403 |
| **v6.6+ (נוכחי)** | **Web3Forms** — `fetch()` + CORS תקין | ✓ עובד |

### פרטים טכניים (v6.6+)
- Endpoint: `https://api.web3forms.com/submit`
- Access Key ב-JS כקבוע: `WEB3FORMS_KEY = '705d4207-c4a6-43a2-8fdc-d8e202bc6c9c'` (שורה ~12043)
- **המפתח ציבורי בכוונה** — זה alias לאימייל, לא סוד
- CSP: `connect-src 'self' https://api.web3forms.com;`
- תגובה JSON: `{success: true/false, message: "..."}`
- Fallback: mailto (base64) — עובד תמיד ללא אינטרנט
- **שים לב:** ב-v7.0 המפתח שוחזר (היה `PASTE_YOUR_...` ב-v6.10)

## PWA Install Button (v6.10 — תמיד נראה + Custom Modal)
- Button: `#pwa-install-btn` ב-`.hdr-tools`
- CSS: `.hdr-btn-install` עם `@keyframes pwa-pulse`
- **v6.9:** הכפתור **תמיד נראה** (`style="display:none"` הוסר מה-HTML)
- **v6.10:** `alert()` הוחלף ב-**Custom Modal** (`#pwa-modal-ovl` + `#pwa-modal-box`) — מונע את ה-prefix "<origin> says" של הדפדפן. עיצוב תואם לאתר, bilingual (HE/EN), עם OL מובנה לשלבי התקנה ו-note בגוון שונה לטיפים
- JS: IIFE לפני `</body>`, מסתיר רק ב-3 מקרים: PWA standalone, SEEN_KEY, `appinstalled`
- Click handler זיהוי-דפדפן לפי 5 מסלולים: iOS Safari, Android, Firefox desktop, Safari macOS, Chrome/Edge desktop
- i18n: `pwa_label / pwa_title / pwa_aria`

## Back-to-Top Button (v6.9)
- Button: `#back-top` (position fixed, bottom-left)
- 48px, opacity מלא ב-`.on`, transform scale + translateY במעבר
- סף גלילה 300px
- בדיקה אוטומטית בטעינה (לא רק בגלילה)
- Mobile override: 44px במסכים ≤480px

## v7.0 — שיפוץ דף ראשי (19/04/2026)

### 4 שינויים מבניים בדף הראשי

**1. Header מאוחד (`.hdr-brand-v7`)** — מוסיף שם אתר + ספירת מתכונים לפני שורת החיפוש:
```html
<div class="hdr-brand-v7">
  <span class="hdr-brand-title">ספר הבישול של פרלה</span>
  <span class="hdr-brand-count"><span id="hdr-count">1,054</span> מתכונים</span>
</div>
```
Responsive: במובייל (≤640px) ה-count מוסתר.

**2. Hero מקוצר עם CTA (`.hero-cta-row`)** — 2 כפתורים אחרי ה-tagline:
- **עיון במתכונים** (`#hero-cta-browse`) — ראשי, רקע `--c-spice`. b-v7.1 מפעיל "הכל" ומציג רשת
- **קרא את הספר** (`#hero-cta-book`) — משני, זהוב שקוף. גלילה + הפעלת `#book-toggle`

**3. סדר חדש של חלקים בדף הראשי:**
```
Header → Hero → Bio → Main (רשת מתכונים) → Book-wrapper → About-redesigned
```
(לפני: Bio → Book → About → Main. הרשת עלתה למעלה, אחרי ה-Bio.)

**4. תפריט ניווט שטוח — 6 קבוצות עליונות** — ראה סעיף "ארכיטקטורת ניווט" למעלה.

### פרטים טכניים
- `buildNav()` נכתב מחדש: מ-14,205 ל-8,162 chars (42% פחות קוד)
- סגירת drawer: נשארה על בסיס `#nav-panel` הקיים + `openPanel()`/`closePanel()`
- MENU_STRUCTURE ב-`data.js` הוחלף מ-nested wrapper ל-flat 6-group
- נוספו 11 מפתחות i18n חדשים: `site_name_short`, `recipes_label`, `hero_cta_browse`, `hero_cta_book`, `nav_grp_all` … `nav_grp_nonkosher`, `community_holidays_lbl`, `community_holidays_msg`
- `pre_en.js` לא שונה (כל הטקסטים החדשים ב-`I18N` מובנה ב-`index.html`)

## v7.1 — הסתרת רשת מתכונים בטעינה (19/04/2026)

**UX fix לבקשת המשתמש:** הדף הראשי הציג מייד את כל 1,054 המתכונים מתחת ל-Bio. זה הסיח את הדעת מהמידע המכונן (ספר, אודות). ב-v7.1:

- **ברירת מחדל:** `<main class="main-hidden">` — הרשת לא נראית
- **CSS:** `.main-hidden { display: none !important; }`
- **פונקציות גלובליות חדשות:** `showMainGrid()`, `hideMainGrid()`
- **מתי הרשת מתגלה:**
  - לחיצה על כל כפתור בתפריט הניווט (כל `selectCat`/`selectMulti`/`selectByIds` קוראים `showMainGrid()`)
  - חיפוש במילה (`doSearch`)
  - לחיצה על "עיון במתכונים" ב-Hero (מדמה קליק על "הכל")
- **מתי הרשת נסגרת:** רק ברענון דף (לא סוגרים אוטומטית לאחר שהתגלתה)

## אזהרות (מעודכן ל-v7.1)
- אל תשנה `MENU_STRUCTURE` ללא בדיקה: הוא 6-group flat structure, לא nested wrapper
- אל תחזיר את סדר החלקים ל-v6.x (Bio→Book→About→Main) — המשתמש ביקש Main אחרי Bio
- אל תסיר את `class="main-hidden"` מה-HTML של `<main>` — זה השינוי המרכזי של v7.1
- אחרי `git commit` תמיד `git push` כדי להפעיל Netlify/GH Pages deploy
- `index.html` מכיל `</body>` פעם אחת בסוף הקובץ. יש 2 `</body>` נוספים בתוך מחרוזות JS (הדפסה/popups) — אל תתבלבל
- אחרי שינוי ב-`data.js`: תמיד הרץ `node -c data.js` לוידוא תחביר לפני commit
- Hebrew gershayim U+05F4 (״) — לא `"` רגיל — בכל מקום שכתוב `ז"ל`
- `frame-ancestors` **רק ב-`_headers`** ולא ב-meta
- **אל תחזיר את הקוד ל-fetch+JSON + FormSubmit** — זה יחזיר את שגיאת ה-CORS
- **אל תנסה לשמור את ה-Web3Forms access_key כ-base64** — הוא מיועד להיות ציבורי

## שינויים בסשנים

### 19/04/2026
- **v7.1:** הרשת מוסתרת בטעינה, מופיעה רק אחרי פעולת משתמש (נווט/חיפוש/CTA). `showMainGrid()`/`hideMainGrid()` גלובליות. שינוי ב-`index.html` בלבד.
- **v7.0:** שיפוץ דף ראשי — Header מאוחד, Hero עם CTAs, Main לפני Book, MENU_STRUCTURE flat 6-group עם placeholder "חגי העדות" (Option C). WEB3FORMS_KEY שוחזר אגב הסשן. שינויים ב-`index.html` + `data.js`.
- **v6.10:** PWA install dialog שוחזר מ-native `alert()` ל-Custom Modal.
- **v6.9:** PWA Install button תמיד נראה; Back-to-top הוגדל ומשופר.
- **v6.8:** Hero tagline הוגדל/הודגש/הולבן. Base font 17px גלובלי (16px במובייל).
- **v6.7:** `.m-nav` sticky, חיצי גלריה ל-RTL. סקריפטי Python (add/edit_recipe.py, recipe_utils.py).
- **v6.6:** הגירה מלאה מ-FormSubmit.co ל-Web3Forms.
- **v6.5:** תיקון רעש 404 בגלריה.
- **v6.4:** FormSubmit iframe.
- **v6.3:** הגדלת UI, PWA install.
