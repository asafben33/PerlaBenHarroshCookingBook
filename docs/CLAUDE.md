# ספר הבישול של פרלה בן הראש ז"ל

**גרסה: 6.10 | 19/04/2026**

## זהות הפרויקט
- אתר (Netlify): https://perlabenharrosh-cookingbook.netlify.app/
- אתר (GitHub Pages): https://asafben33.github.io/PerlaBenHarroshCookingBook/
- GitHub: https://github.com/asafben33/PerlaBenHarroshCookingBook.git
- Branch: main — פרוס אוטומטית ב-Netlify וב-GitHub Pages
- User: Asaf Yaakov Ben-Harrosh (אסף יעקב בן-הראש), youngest son (בן הזקונים) of Perla & Pinchas z"l

## מבנה הקבצים
- `index.html` — HTML ראשי + JS inline (כל הלוגיקה) — v6.8: ~343 KB
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

## סקריפטי ניהול (חדש — v6.7)
- `recipe_utils.py` — ספריית עזר: parser של `data.js`, כותב עם גיבוי, לוגר, CLI Hebrew UI + rtl_fix ל-Windows
- `add_recipe.py` — אשף אינטראקטיבי להוספת מתכון (7 שלבים, validation, preview, `--dry-run`)
- `edit_recipe.py` — אשף עריכה/מחיקה של מתכון קיים
- פרטים ב-`README_Recipe_CLI.md`

## מסמכי תיעוד
- `HLD_Perla_CookingBook.md` — High-Level Design (נכתב ב-v6.3, נשאר רלוונטי בעיקרון)
- `LLD_Perla_CookingBook.md` — Low-Level Design (נכתב ב-v6.3)
- `INTEGRATION_GUIDE.md` — מדריך אינטגרציה (FormSubmit.co — הוחלף ל-Web3Forms ב-v6.6)
- `README.md` — סקירה כללית
- `README_Recipe_CLI.md` — מדריך לסקריפטי Python
- `CHANGELOG_19-04-2026_v6_3.md` — עד `v6_8.md` — לוג שינויים לכל סשן

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
| **v6.6 (נוכחי)** | **Web3Forms** — `fetch()` + CORS תקין | ✓ עובד |

### פרטים טכניים (v6.6+)
- Endpoint: `https://api.web3forms.com/submit`
- Access Key ב-JS כקבוע: `WEB3FORMS_KEY` (שורה ~6969)
- **המפתח ציבורי בכוונה** — זה alias לאימייל, לא סוד
- CSP: `connect-src 'self' https://api.web3forms.com;`
- תגובה JSON: `{success: true/false, message: "..."}`
- Fallback: mailto (base64) — עובד תמיד ללא אינטרנט
- הסרו: iframe/hidden-form + FormSubmit CSP entries

## PWA Install Button (v6.10 — תמיד נראה + Custom Modal)
- Button: `#pwa-install-btn` ב-`.hdr-tools`
- CSS: `.hdr-btn-install` עם `@keyframes pwa-pulse`
- **v6.9:** הכפתור **תמיד נראה** (`style="display:none"` הוסר מה-HTML)
- **v6.10:** `alert()` הוחלף ב-**Custom Modal** (`#pwa-modal-ovl` + `#pwa-modal-box`) — מונע את ה-prefix "<origin> says" של הדפדפן. עיצוב תואם לאתר, bilingual (HE/EN), עם OL מובנה לשלבי התקנה ו-note בגוון שונה לטיפים
- JS: IIFE לפני `</body>`, מסתיר רק ב-3 מקרים:
  1. רץ כ-PWA מותקן (standalone mode)
  2. המשתמש דחה דרך `SEEN_KEY` ב-localStorage
  3. האפליקציה הותקנה (`appinstalled` event)
- Click handler זיהוי-דפדפן לפי 5 מסלולים: iOS Safari, Android, Firefox desktop, Safari macOS, Chrome/Edge desktop — כל מסלול עם `{title, steps, note}` מותאם בעברית ובאנגלית
- כל הטקסטים מזכירים את שם האתר "ספר הבישול של פרלה" ולא URL של הדומיין
- Modal מקבל: OK button, click-outside close, Escape key
- i18n: `pwa_label / pwa_title / pwa_aria`

## Back-to-Top Button (v6.9 — משופר)
- Button: `#back-top` (position fixed, bottom-left)
- **v6.9:** הוגדל ל-48px (היה 42px), opacity מלא ב-`.on` (היה .8), transform scale + translateY במעבר
- **v6.9:** סף גלילה הופחת מ-450px ל-300px — מופיע מוקדם יותר
- **v6.9:** בדיקה אוטומטית בטעינה (לא רק בגלילה) — חשוב לחזרה דרך back/forward cache
- Mobile override: 44px במסכים ≤480px
- Focus-visible outline לנגישות מקלדת

## UI/UX (v6.7 + v6.8)
### Modal (חלון מתכון)
- **v6.7:** `.m-nav` (כפתורי סגור/קודם/הבא) שונה מ-`absolute` ל-`sticky` — נשאר גלוי בגלילה
- **v6.7:** הוחלפו מיקומי חיצי גלריית תמונות (`.m-hero-nav`) ל-RTL:  
  prev בצד ימין (`‹`), next בצד שמאל (`›`)
- ה-HTML של `.m-nav` הועבר להיות **לפני** `.m-hero` (נדרש ל-sticky עם margin שלילי)
- `pointer-events: none` על המיכל + `auto` על הכפתורים — מאפשר קליקים לעבור דרך האזור הריק

### Typography (v6.8)
- **Hero tagline** (subtitle "לזכרם של...") הוגדל ל-`1.15rem`, **bold**, צבע לבן (`#ffffff`) עם text-shadow
- **Base font:** `html { font-size: 17px; }` — הגדלה של 6% גלובלית (כל `rem` גדל פרופורציונלית)
- **Mobile exception:** `@media (max-width: 480px) { html { font-size: 16px; } }` — מונע overflow במסכים צרים
- **Book paragraphs** (`.book-p`): `font-size: 1.02rem` (הגדלה נקודתית לקריאות של הטקסטים הארוכים מהספר)

## אזהרות
- אל תשנה `MENU_STRUCTURE` ללא בדיקה
- אחרי `git commit` תמיד `git push` כדי להפעיל Netlify/GH Pages deploy
- `index.html` מכיל `</body>` פעם אחת בסוף הקובץ (שורה אחרונה). יש 2 `</body>` נוספים בתוך מחרוזות JS (עבור הדפסה ו-popups) — אל תתבלבל בין מחרוזות לבין DOM אמיתי
- אחרי שינוי ב-`data.js`: תמיד הרץ `node -c data.js` לוידוא תחביר לפני commit
- Hebrew gershayim U+05F4 (״) — לא `"` רגיל — בכל מקום שכתוב `ז"ל` או `ש"ץ`
- `frame-ancestors` **רק ב-`_headers`** ולא ב-meta (הדפדפן מתעלם ממנו ב-meta)
- **אל תחזיר את הקוד ל-fetch+JSON + FormSubmit** — זה יחזיר את שגיאת ה-CORS
- **אל תנסה לשמור את ה-Web3Forms access_key כ-base64** — הוא מיועד להיות ציבורי

## שינויים בסשנים (19/04/2026)
- **v6.10:** PWA install dialog שוחזר מ-native `alert()` ל-Custom Modal — נעלם ה-prefix "asafben33.github.io says". הטקסטים עודכנו ומזכירים "ספר הבישול של פרלה".
- **v6.9:** PWA Install button תמיד נראה (הוסרה הסתרה ברירת מחדל); Back-to-top הוגדל ומשופר (סף 300, בדיקה בטעינה). תיקון תלות ב-Chrome engagement heuristic.
- **v6.8:** Hero tagline הוגדל/הודגש/הולבן. Base font 17px גלובלי (16px במובייל). `.book-p` ל-1.02rem.
- **v6.7:** `.m-nav` sticky, חיצי גלריה ל-RTL (prev→ימין, next→שמאל).
- **v6.6:** הגירה מלאה מ-FormSubmit.co ל-Web3Forms (פתר בעיית 403 לצמיתות).
- **v6.5:** ניסיון תיקון FormSubmit (`_url` field) — לא הספיק. גם הוסיף תיקון רעש 404 בגלריה.
- **v6.4:** FormSubmit iframe (תיקן CORS אבל לא 403).
- **v6.3:** הגדלת UI נוספת, PWA install.

### כלים חדשים (v6.7)
- `add_recipe.py`, `edit_recipe.py`, `recipe_utils.py` — CLI לניהול מתכונים מבלי לערוך JS ידנית
- תמיכת BiDi ל-Windows Terminal דרך `rtl_fix()` (המילים הפוכות לפני הדפסה כי Windows לא מיישם UBA)
