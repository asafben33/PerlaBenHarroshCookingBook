# ספר הבישול של פרלה בן הראש ז"ל

## זהות הפרויקט
- אתר: https://perlabenharrosh-cookingbook.netlify.app/
- GitHub: https://github.com/asafben33/PerlaBenHarroshCookingBook.git
- Branch: main — פרוס אוטומטית ב-Netlify

## מבנה הקבצים
- index.html — HTML ראשי + JS inline (כל הלוגיקה)
- data.js — 1,054 מתכונים (CATS, MENU_STRUCTURE, HOLIDAY_TAGS, const R=[...])
- book_data.js — תוכן הספר הביוגרפי (BOOK_HTML, BOOK_HTML_EN)
- pre_en.js — תרגומים לאנגלית (pre-rendered)
- about_redesigned.{html,css,js} — דף "אודות" מעוצב מחדש
- sw.js — Service Worker v10 (network-first למסמכים, cache-first לתמונות)
- manifest.json — PWA manifest
- images/recipes_images/ — תמונות מתכונים: r-{id}.jpg
- images/book_images/ — תמונות ספר: WhatsApp_Image_*.jpeg + wedding.jpg
- images/site_images/ — אייקונים, OG image, תמונות קטגוריה fallback

## כללי עבודה
- כל התמונות מוגשות מתוך תיקיית images/ (לא מ-root)
- נתיב תמונות מתכונים: images/recipes_images/r-{id}.jpg
- נתיב תמונות ספר: images/book_images/
- נתיב תמונות קטגוריה: images/site_images/cat-{cat}.jpg
- אסור להשתמש ב: loremflickr.com (403), upload.wikimedia.org (429)
- מותר להשתמש ב: picsum.photos (fallback בלבד — לשדה img ב-data.js, עוקף על ידי _resolveImg ב-index.html)
- שפת ממשק: עברית בלבד, RTL
- אחרי כל שינוי: git add → git commit → git push

## מבנה מתכון (data.js) — שדות חובה
id, cat, badge, title, desc, time, serv, diff, img, mem, ingr, steps, tip
שדות אופציונליים: src, vid, tags

## קטגוריות (20 ב-CATS, כולל all)
all, soups, salads, veg, meat, chick, fish, hol, des, span,
iraq, kurd, ashk, yem, pers, buk, tun, isr, turk, nonkosher

## לוגיקת תמונות ב-index.html
- getRecipeImg(r) תמיד מחזירה images/recipes_images/r-{id}.jpg (לא r.img)
- _getImgFallbacks(r) מספק שרשרת fallback: r-{id}-2.jpg, r-{id}-3.jpg, r.img, CAT_IMG[r.cat], CAT_IMG._def
- _IMG_ALIAS ממופה על ידי cleanup_hardlinks.py (Python — לא PowerShell)
- CAT_IMG כל הנתיבים מקומיים (images/site_images/cat-*.jpg)

## אזהרות
- אל תשנה MENU_STRUCTURE ללא בדיקה
- אחרי git commit תמיד git push כדי להפעיל Netlify deploy
- index.html מכיל `</body>` פעם אחת בלבד בסוף הקובץ (שורה אחרונה). יש 2 `</body>` נוספים בתוך מחרוזות JS (עבור הדפסה ו-popups) — אל תתבלבל בין מחרוזות לבין DOM אמיתי.
- אחרי שינוי ב-data.js: תמיד הרץ `node -c data.js` לוידוא תחביר לפני commit.
