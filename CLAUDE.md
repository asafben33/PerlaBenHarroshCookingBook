# ספר הבישול של פרלה בן הראש ז"ל

## זהות הפרויקט
- אתר: https://perlabenharrosh-cookingbook.netlify.app/
- GitHub: https://github.com/asafben33/PerlaBenHarroshCookingBook.git
- Branch: main — פרוס אוטומטית ב-Netlify

## מבנה הקבצים
- index.html — HTML ראשי + JS inline (כל הלוגיקה)
- data.js — 1,054 מתכונים (CATS, MENU_STRUCTURE, const R=[...])
- book_data.js — תוכן הספר הביוגרפי (BOOK_HTML, BOOK_HTML_EN)
- pre_en.js — תרגומים לאנגלית (pre-rendered)
- images/ — תמונות מתכונים: images/r-{id}.jpg
- images/ — תמונות ספר: images/WhatsApp_Image_*.jpeg

## כללי עבודה
- כל תמונות מוגשות מתוך תיקיית images/ (לא מ-root)
- נתיב תמונות מתכונים: images/r-{id}.jpg
- נתיב תמונות ספר: images/WhatsApp_Image_*.jpeg
- אסור להשתמש ב: loremflickr.com (403), wikimedia.org (429)
- מותר להשתמש ב: picsum.photos (fallback בלבד)
- שפת ממשק: עברית בלבד, RTL
- אחרי כל שינוי: git add → git commit → git push

## מבנה מתכון (data.js)
id, cat, badge, title, desc, time, serv, diff, img, mem, ingr, steps, tip

## קטגוריות
soups/salads/veg/meat/chick/fish/hol/des/span/iraq/kurd/ashk/yem/pers/buk/tun/isr/turk/nonkosher

## אזהרות
- אל תשנה MENU_STRUCTURE ללא בדיקה
- אחרי git commit תמיד git push כדי להפעיל Netlify deploy
- index.html מכיל 3 </body> — תמיד השתמש ב-rfind() לציין את האחרון