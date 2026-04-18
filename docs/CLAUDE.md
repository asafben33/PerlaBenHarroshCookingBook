# ספר הבישול של פרלה בן הראש ז"ל

**גרסה: 6.4 | 19/04/2026**

## זהות הפרויקט
- אתר (Netlify): https://perlabenharrosh-cookingbook.netlify.app/
- אתר (GitHub Pages): https://asafben33.github.io/PerlaBenHarroshCookingBook/
- GitHub: https://github.com/asafben33/PerlaBenHarroshCookingBook.git
- Branch: main — פרוס אוטומטית ב-Netlify וב-GitHub Pages
- User: Asaf Yaakov Ben-Harrosh (אסף יעקב בן-הראש), youngest son (בן הזקונים) of Perla & Pinchas z"l

## מבנה הקבצים
- index.html — HTML ראשי + JS inline (כל הלוגיקה) — v6.4: 388,399 bytes
- data.js — 1,054 מתכונים (CATS, MENU_STRUCTURE, HOLIDAY_TAGS, const R=[...])
- book_data.js — תוכן הספר הביוגרפי (BOOK_HTML, BOOK_HTML_EN)
- pre_en.js — תרגומים לאנגלית (pre-rendered)
- about_redesigned.{html,css,js} — דף "אודות" מעוצב מחדש
- sw.js — Service Worker (network-first למסמכים, cache-first לתמונות)
- manifest.json — PWA manifest (PWA install button ב-v6.3)
- _headers — Netlify HTTP headers (CSP, X-Frame-Options, etc.) — v6.2
- images/recipes_images/ — תמונות מתכונים: r-{id}.jpg
- images/book_images/ — תמונות ספר: WhatsApp_Image_*.jpeg + wedding.jpg
- images/site_images/ — אייקונים, OG image, favicons, cat-*.jpg fallbacks

## מסמכי תיעוד
- HLD_Perla_CookingBook.md — גרסה 6.3 (High-Level Design)
- LLD_Perla_CookingBook.md — גרסה 6.3 (Low-Level Design)
- INTEGRATION_GUIDE.md — גרסה 2.0 (FormSubmit.co, לא Netlify Forms)
- CHANGELOG_19-04-2026_v6.3.md — שינויי סשן 19/04
- CHANGELOG_18-04-2026_v2.md — שינויי 18/04 (v6.0-6.2)
- CHANGELOG_download_images_v5.md — שינויי download_images.py v5.1
- README.md — גרסה 6.3 (סקירה כללית)

## כללי עבודה
- כל התמונות מוגשות מתוך תיקיית images/ (לא מ-root)
- נתיב תמונות מתכונים: images/recipes_images/r-{id}.jpg
- נתיב תמונות ספר: images/book_images/
- נתיב תמונות קטגוריה: images/site_images/cat-{cat}.jpg (20 placeholders ב-v6.2)
- אסור להשתמש ב: loremflickr.com (403), upload.wikimedia.org (429), picsum.photos (CSP block)
- שפת ממשק: עברית בלבד כברירת מחדל, RTL (עם toggle ל-EN)
- אחרי כל שינוי: git add → git commit → git push (PowerShell, פקודות אחת אחת)
- CRLF line endings חובה (index.html משתמש ב-\r\n)

## מבנה מתכון (data.js) — שדות חובה
id, cat, badge, title, desc, time, serv, diff, img, mem, ingr, steps, tip
שדות אופציונליים: src, vid, tags

## קטגוריות (20 ב-CATS, כולל all)
all, soups, salads, veg, meat, chick, fish, hol, des, span,
iraq, kurd, ashk, yem, pers, buk, tun, isr, turk, nonkosher

## לוגיקת תמונות ב-index.html
- getRecipeImg(r) תמיד מחזירה images/recipes_images/r-{id}.jpg (לא r.img)
- _getImgFallbacks(r): r-{id}-2.jpg, r-{id}-3.jpg → **הוסרו ב-v6.1** (עדיין ב-_getAllRecipeImages לגלריה)
- _getImgFallbacks(r): r.img → **הוסר ב-v6.1** (מונע 1054 CSP violations)
- fallback chain (v6.3): CAT_IMG[r.cat] → CAT_IMG._def
- _IMG_ALIAS ממופה על ידי download_images.py v5.1 (--inline-alias)
- CAT_IMG כל הנתיבים מקומיים (images/site_images/cat-*.jpg)

## מערכת פידבק (v6.4 — FormSubmit + Hidden Iframe)
- **הוחלף** מ-Netlify Forms (שנכשל ב-GitHub Pages עם 405)
- Endpoint: `https://formsubmit.co/ajax/{email}` (AJAX, JSON)
- Email מוסתר כ-base64: `FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ=='`
- CSP: `connect-src 'self' https://formsubmit.co;`
- _headers: `form-action 'self' https://formsubmit.co;`
- **דורש activation חד-פעמי** — שליחה ראשונה → מייל מ-contact@formsubmit.co → לחיצה על הקישור
- Fallback: mailto (base64) — עובד תמיד ללא אינטרנט

## PWA Install Button (v6.3 — שוחזר)
- Button: `#pwa-install-btn` ב-`.hdr-tools` (ראשון)
- CSS: `.hdr-btn-install` עם `@keyframes pwa-pulse`
- JS: IIFE לפני `</body>`, עם `beforeinstallprompt` + iOS fallback + localStorage dismissal
- i18n: pwa_label / pwa_title / pwa_aria

## אזהרות
- אל תשנה MENU_STRUCTURE ללא בדיקה
- אחרי git commit תמיד git push כדי להפעיל Netlify/GH Pages deploy
- index.html מכיל `</body>` פעם אחת בסוף הקובץ (שורה אחרונה). יש 2 `</body>` נוספים בתוך מחרוזות JS (עבור הדפסה ו-popups) — אל תתבלבל בין מחרוזות לבין DOM אמיתי
- אחרי שינוי ב-data.js: תמיד הרץ `node -c data.js` לוידוא תחביר לפני commit
- Hebrew gershayim U+05F4 (״) — לא `"` רגיל — בכל מקום שכתוב ז"ל או ש"ץ
- `frame-ancestors` **רק ב-`_headers`** ולא ב-meta (הדפדפן מתעלם ממנו ב-meta)

## שינויים אחרונים (v6.4 — סשן 19/04/2026)
- **v6.4: תיקון CORS בפידבק** — מעבר מ-fetch+JSON ל-hidden iframe + form POST
  - שגיאה שהתגלתה ב-GitHub Pages: `No 'Access-Control-Allow-Origin' header is present`
  - פתרון: form submissions ל-iframe אינן כפופות ל-CORS
  - CSP שונה: connect-src מצומצם, frame-src + form-action מורחבים
- v6.3 שינויים (נשארים):
  - UI enlargement סיבוב שני: search flex, --nav-h 60px, .nb 1.1rem, .acc-hdr 1.18rem
  - Hero title: המטבח של משפחת בן הראש (ארוש\\הרוש)
  - Hero tagline: הוסף ז״ל, שכמעט שכחנו
  - About memorial: הוסף הלאה לדורי דורות
  - About h2: המשפחה שעיצבה מטבח שלם שיזכר ויתבשל הלאה לדורי דורות
  - PWA Install button: שוחזר במלואו

## אזהרות חשובות (v6.4)
- **אל תחזיר את הקוד ל-fetch+JSON** — זה יחזיר את שגיאת ה-CORS.
- **hidden iframe + form** היא הפתרון הנכון לטפסי פידבק מאתרים סטטיים (GH Pages, Netlify).
- בעת שינוי CSP: `form-action` הוא ה-directive שחשוב לטפסים, לא `connect-src`.
- `frame-src` חייב לכלול את היעד של ה-iframe (formsubmit.co) — אחרת הדפדפן יחסום את הנווטות של ה-iframe.
