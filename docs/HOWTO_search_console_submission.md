# הוראות לסבמיט האתר ל-Google Search Console ולמנועי חיפוש נוספים

**ספר הבישול של פרלה בן-הראש ז״ל**
**מטרה:** הזרזת אינדוקס של 1,054 המתכונים ב-Google ו-Bing.
**זמן צפוי:** 15 דקות סבמיט + 2-4 שבועות עד להופעה בתוצאות חיפוש.

---

## מה כבר הוכן (אוטומטית)

האתר מצויד בכל הנדרש לסבמיט:

- **`sitemap.xml`** — 1,080 URLs (הוכן ב-v8.7)
- **`robots.txt`** — מפנה ל-sitemap משני האתרים (Netlify + GitHub Pages) (עודכן ב-v8.7)
- **Meta tags לאימות** ב-`<head>` של `index.html` — 3 placeholders שצריך להחליף בקודים אמיתיים
- **JSON-LD Schema.org** — 4 schemas: WebSite, Person, CollectionPage, BreadcrumbList
- **`SearchAction` schema** — מאפשר לגוגל להציג sitelinks-search-box

---

## חלק 1 — סבמיט ל-Google Search Console (חובה)

### שלב 1.1 — כניסה והוספת property

1. כנס ל-https://search.google.com/search-console
2. התחבר עם חשבון Google שלך (אסיף.ben...@gmail.com או דומה)
3. לחץ **"Add Property"** (פלוס בצד שמאל למעלה)
4. בחר **"URL prefix"** (לא Domain — Domain דורש גישה ל-DNS שאין לך ב-Netlify)
5. הזן את ה-URL: `https://perlabenharrosh-cookingbook.netlify.app/`
6. לחץ **"Continue"**

### שלב 1.2 — אימות בעלות

מסך האימות יציג מספר שיטות. **בחר "HTML tag"** (זאת השיטה שתואמת למה שכבר הכנו):

1. גוגל יראה לך משהו כזה:
   ```
   <meta name="google-site-verification" content="AbCdEfGhIjKlMnOpQrStUv-1234567890_xyz">
   ```

2. **העתק רק את הערך של `content="..."`** — דהיינו `AbCdEfGhIjKlMnOpQrStUv-1234567890_xyz` (במקרה שלך הקוד יהיה שונה)

3. **פתח את `index.html`** במחשב שלך, חפש את השורה (סביב שורה 17):
   ```html
   <meta name="google-site-verification" content="REPLACE-WITH-GOOGLE-CODE-FROM-SEARCH-CONSOLE">
   ```

4. **החלף** את `REPLACE-WITH-GOOGLE-CODE-FROM-SEARCH-CONSOLE` בקוד שגוגל נתן לך:
   ```html
   <meta name="google-site-verification" content="AbCdEfGhIjKlMnOpQrStUv-1234567890_xyz">
   ```

5. **שמור, ה-commit, ו-push** ל-git:
   ```powershell
   cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
   git add index.html
   git commit -m "Add Google Search Console verification meta tag"
   git push origin main
   ```

6. המתן ~30 שניות ל-Netlify לפרוס

7. חזור ל-Search Console ולחץ **"Verify"** — אמור להופיע ✓ ירוק

### שלב 1.3 — סבמיט הסיטמאפ

לאחר אימות מוצלח:

1. בתפריט הצד השמאלי לחץ **"Sitemaps"** (תחת "Indexing")
2. בשדה "Add a new sitemap" הזן: `sitemap.xml`
3. לחץ **"Submit"**
4. אם הצליח, תראה:
   ```
   Status: Success
   Discovered URLs: ~1080
   ```

זה ייקח לגוגל מספר ימים-שבועות לסרוק את כל ה-URLs. תוכל לראות את ההתקדמות במסך **"Coverage"**.

### שלב 1.4 — בקשה לאינדוקס מהיר של דף הבית

לאחר סבמיט הסיטמאפ:
1. בתפריט הצד לחץ **"URL inspection"** (סמל זכוכית מגדלת למעלה)
2. הזן: `https://perlabenharrosh-cookingbook.netlify.app/`
3. לחץ **Enter**
4. לחץ **"Request indexing"**

זה אומר לגוגל "אל תחכה לסריקה הבאה — סרוק עכשיו".
**מגבלה:** ניתן לעשות זאת רק ל-10-12 URLs ביום.

---

## חלק 2 — סבמיט ל-Bing Webmaster Tools (מומלץ)

Bing מהווה 6-8% מתנועת החיפוש העולמית — שווה את 5 הדקות.

1. כנס ל-https://www.bing.com/webmasters
2. התחבר (אפשר עם חשבון Microsoft או Google)
3. לחץ **"Add a Site"**
4. הזן: `https://perlabenharrosh-cookingbook.netlify.app/`
5. לחץ **"Add"**

### אופציה מהירה — Import מ-Google Search Console

אם כבר אימתת ב-Google:
1. במסך הוספת אתר ב-Bing, לחץ **"Import sites from Search Console"**
2. אשר את ההרשאה
3. Bing יוסיף אוטומטית את האתר עם האימות וה-sitemap

### אופציה ידנית — אימות בנפרד

אם לא משתמש ב-import:
1. Bing יציג meta tag דומה לזה של Google:
   ```
   <meta name="msvalidate.01" content="1234567890ABCDEF1234567890ABCDEF">
   ```
2. החלף את ה-placeholder ב-`index.html` (שורה 18):
   ```html
   <meta name="msvalidate.01" content="1234567890ABCDEF1234567890ABCDEF">
   ```
3. Commit + push, אז `Verify`
4. Submit sitemap: `https://perlabenharrosh-cookingbook.netlify.app/sitemap.xml`

---

## חלק 3 — Yandex (אופציונלי — לא חובה)

Yandex מתאים אם רוצים תנועה דוברי רוסית או חלק מהקהילה הצרפתית-מרוקאית.

1. כנס ל-https://webmaster.yandex.com/
2. הוסף אתר חדש
3. בחר HTML Tag verification
4. החלף את `index.html` שורה 19:
   ```html
   <meta name="yandex-verification" content="THE_CODE_FROM_YANDEX">
   ```

אם לא רלוונטי — אפשר להשאיר את ה-placeholder. הוא לא שובר כלום, פשוט לא מאומת.

---

## חלק 4 — בדיקה שהכל עובד

### בדיקה מיידית (תוך דקות מהפריסה)

```powershell
# בדוק ש-robots.txt מצביע נכון
curl https://perlabenharrosh-cookingbook.netlify.app/robots.txt

# בדוק ש-sitemap נגיש ובפורמט תקין
curl https://perlabenharrosh-cookingbook.netlify.app/sitemap.xml | Select-String "<url>" -Count

# צריך להחזיר: 1080
```

### בדיקה ב-Google Rich Results Test

לאחר הפריסה (5 דקות):
1. כנס ל-https://search.google.com/test/rich-results
2. הזן: `https://perlabenharrosh-cookingbook.netlify.app/`
3. לחץ **"Test URL"**

צפי תוצאה: `Item type: WebSite | Page eligible for rich results`

עם 4 schemas ב-`@graph`, זה אמור להראות:
- ✓ WebSite (שדה חיפוש מוצג בתוצאות הראשיות)
- ✓ BreadcrumbList (פירורי לחם בתוצאות)

### בדיקה ב-Schema Validator

1. כנס ל-https://validator.schema.org/
2. הזן URL או הדבק את ה-`<script type="application/ld+json">` הספציפי
3. ודא שאין שגיאות אדומות

---

## חלק 5 — מה לצפות לקרות

### תוך 24 שעות

- Google רושם את ה-property ב-Search Console
- Bing מאשר את הסיטמאפ

### תוך שבוע

- Coverage report ב-Search Console מציג: `Discovered: 1080 URLs, Indexed: ~50-200`
- האתר מתחיל להופיע בחיפושים על "ספר הבישול של פרלה בן הראש"

### תוך 2-4 שבועות

- 600-900 מ-1,054 URLs יהיו indexed
- חיפושים על "מתכון לטאג'ין" / "חרירה ביתית" / "מופלטה" יתחילו להחזיר את האתר
- חיפושים בעברית **לא דרך הדומיין** יוצגו (זה הקסם)

### תוך 2-3 חודשים

- Click-through rate צפוי: 100-500 ביקורים שבועיים מ-Google
- **Featured snippets** — אם המתכון נכתב טוב, גוגל יבחר אותו לתשובת התוכלית
- **Recipe rich cards** — אם נוסיף בעתיד `Recipe` schema לכל מתכון בנפרד

---

## חלק 6 — פעולות אופציונליות מתקדמות

### 6.1 — הוספת Recipe schema לכל מתכון בנפרד (עתידי)

כרגע יש לנו `CollectionPage` schema אחד שמתאר את האתר כולו. כדי לקבל **Recipe rich cards** (כרטיסים יפים בתוצאות חיפוש עם תמונה, זמן הכנה, כוכבים), צריך לייצר `Recipe` schema לכל אחד מ-1,054 המתכונים בנפרד.

זה דורש סקריפט נוסף שיגנרט את ה-JSON-LD מ-data.js. אם תרצה — נוכל לעשות זאת בעדכון הבא.

### 6.2 — Google Analytics

כדי לראות מי באמת מבקר ומה הוא קורא:
1. https://analytics.google.com → Create property
2. קבל GA4 Measurement ID (G-XXXXXXXXXX)
3. הוסף לפני `</head>` ב-`index.html`:
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX', { 'anonymize_ip': true });
   </script>
   ```

### 6.3 — Open Graph image מותאם

כרגע יש `og:image` המצביע על `images/site_images/og-image.jpg`. אם הקובץ הזה לא קיים, החלפת דפים בפייסבוק/וואטסאפ תראה placeholder גנרי.

צריך לוודא שיש שם תמונה 1200×630 בקובץ הזה. אם אין — להעלות אותה (תמונה איכותית של מאפים מרוקאיים, למשל).

---

## חלק 7 — אפשרות לעקוף לחלוטין את התהליך הידני

אם אינך רוצה להתעסק כרגע עם Search Console:
1. **השאר את ה-placeholders כפי שהם** ב-index.html — הם לא שוברים כלום
2. **אל תאמת בעלות** — Google בכל זאת יסרוק את האתר (פשוט יותר לאט)
3. **לאחר 4-6 שבועות** האתר יופיע בתוצאות חיפוש organic באופן טבעי

ההפסד היחיד: לא תהיה לך גישה ל-Coverage report (לא תראה מה נסרק ומה לא).

מבחינת תזמון אינדוקס — Google יסרוק לפי הסיטמאפ בכל מקרה (כי הוא מצוין ב-robots.txt). הסבמיט ל-Search Console רק מאיץ את התהליך ב-1-2 שבועות.

---

## סיכום — הפעולות שאתה צריך לעשות

### חובה (10 דקות)
1. פרוס את index.html + robots.txt העדכניים (פקודות git שמופיעות בסוף)
2. כנס ל-https://search.google.com/search-console
3. הוסף property → אמת → סבמיט sitemap

### אופציונלי (5 דקות נוספות)
4. עשה את אותו דבר ב-https://www.bing.com/webmasters
5. בדוק את האתר ב-https://search.google.com/test/rich-results

### לעתיד (אם תרצה)
6. הוסף Google Analytics
7. הוסף Recipe schema לכל מתכון בנפרד (סקריפט עתידי)

---

## פריסה (קבצים שעודכנו)

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\robots.txt" "." -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\HOWTO_search_console_submission.md" "." -Force
```
```powershell
git add index.html robots.txt HOWTO_search_console_submission.md
```
```powershell
git commit -m "v8.7+SEO: search engine verification meta tags + comprehensive JSON-LD + improved robots.txt"
```
```powershell
git push origin main
```

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
