# מדריך אינטגרציה — מערכת פידבק לאתר ספר הבישול של פרלה ז״ל

**גרסה 4.0** — 19/04/2026 — **Web3Forms** (החלוף ל-FormSubmit מ-v6.6)

*(גרסאות 1.0-3.0 היו מבוססות FormSubmit.co/Netlify Forms ונכשלו בסופו של דבר — ראו סעיף 9 להיסטוריה)*

---

## תוכן

1. [סקירה כללית](#1-סקירה-כללית)
2. [ארכיטקטורה](#2-ארכיטקטורה)
3. [קבצים ומה השתנה](#3-קבצים-ומה-השתנה)
4. [הגדרה חד-פעמית](#4-הגדרה-חד-פעמית)
5. [בדיקות ואימות](#5-בדיקות-ואימות)
6. [תרחישי edge cases](#6-תרחישי-edge-cases)
7. [תחזוקה עתידית](#7-תחזוקה-עתידית)
8. [Fallback — mailto](#8-fallback--mailto)
9. [היסטוריית הגרסאות](#9-היסטוריית-הגרסאות)

---

## 1. סקירה כללית

המערכת מספקת שלוש נקודות כניסה למשתמש:

| נקודה | איפה | מה זה עושה |
|---|---|---|
| **כפתור "הערה / תיקון"** | בתוך modal של כל מתכון, ב-`.m-actions` | פותח חלון פידבק עם הקשר למתכון |
| **FAB צף** | פינה שמאלית-תחתונה, תמיד גלוי | פידבק כללי לאתר / דיווח תקלה |
| **פונקציה גלובלית** | `window.openFeedbackModal(type, recipe)` | לשימוש מכל מקום בקוד |

### 1.1 למה Web3Forms

אחרי 3 ניסיונות כושלים (ראה סעיף 9), Web3Forms נבחר כי הוא:
- **תומך ב-CORS לחלוטין** — `fetch()` + JSON עובד משני המקורות (Netlify + GitHub Pages)
- **תגובה JSON סטנדרטית** — `{success: true, message: "..."}` — קל לטפל ב-JS
- **ללא שלב activation** — אחרי הגדרת המפתח, עובד מייד
- **חינמי** ב-250 הודעות/חודש (מספיק בגדול לפרויקט)
- **ללא CAPTCHA** — זיהוי spam אוטומטי

### 1.2 ארכיטקטורה High-level (v4.0)

```
משתמש → FAB / כפתור "הערה / תיקון"
    ↓
Modal פידבק עם טופס
    ↓
JS validation (אורך מינימלי 5 תווים, email regex)
    ↓
fetch('https://api.web3forms.com/submit', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
  body: JSON.stringify({access_key: WEB3FORMS_KEY, subject, email, message, ...})
})
    ↓
Web3Forms מעביר ל-asafben33@gmail.com
    ↓
תגובה: {success: true, message: "Email sent successfully!"}
    ↓
"תודה! ההודעה נשלחה בהצלחה."
    ↓
(אם fetch נכשל או timeout 15s) → fallback ל-mailto
```

---

## 2. ארכיטקטורה

### 2.1 Endpoint

```
POST https://api.web3forms.com/submit
Content-Type: application/json
Accept: application/json
```

### 2.2 Request body schema

```json
{
  "access_key": "705d4207-c4a6-43a2-8fdc-d8e202bc6c9c",
  "subject": "פידבק אתר - תיקון מתכון: מרק חרירה",
  "from_name": "אתר פרלה",
  "email": "user@example.com",
  "message": "...תוכן ההודעה...",
  "feedback-type": "recipe",
  "recipe-id": "s1",
  "recipe-title": "מרק חרירה",
  "page-url": "https://perlabenharrosh-cookingbook.netlify.app/#s1",
  "user-agent": "Mozilla/5.0 ...",
  "redirect": "false"
}
```

### 2.3 Response

**Success:**
```json
{"success": true, "message": "Email sent successfully!"}
```

**Error:**
```json
{"success": false, "message": "Invalid access key"}
```

### 2.4 המפתח (`WEB3FORMS_KEY`)

```javascript
// index.html שורה ~12043
var WEB3FORMS_KEY = '705d4207-c4a6-43a2-8fdc-d8e202bc6c9c';
```

**חשוב:** המפתח **ציבורי בכוונה**. Web3Forms מיישם:
- Rate limiting (250 הודעות/חודש)
- Spam filtering
- Domain whitelist (אופציונלי)

אין צורך לקודד ב-base64 או לאפלל. אם מישהו משתמש במפתח — Web3Forms יחסום אם זה spam, אחרת זה רק מוסיף הודעה לרשימה.

---

## 3. קבצים ומה השתנה

| קובץ | שורות עיקריות | מה קורה |
|---|---|---|
| `index.html` | ~11900-12300 | CSS + HTML + JS של מערכת הפידבק |
| `index.html` שורה 12043 | `var WEB3FORMS_KEY = '705d...';` | המפתח הציבורי |
| `index.html` שורה ~12150 | `submitFeedback()` | פונקציית `fetch()` ראשית |
| `index.html` שורה ~12200 | `openMailtoFallback()` | fallback אם כל השאר נכשל |
| `_headers` (Netlify) | `connect-src` directive | `'self' https://api.web3forms.com;` |
| `index.html` `<meta CSP>` | `connect-src` | כנ"ל |

### 3.1 CSP — מה חובה

```
connect-src 'self' https://api.web3forms.com;
```

**לא צריך** (בניגוד לגרסאות ישנות):
- ~~`frame-src https://formsubmit.co`~~ — אין iframe יותר
- ~~`form-action https://formsubmit.co`~~ — `fetch()` לא `<form action>`
- ~~`frame-src https://www.google.com`~~ — אין reCAPTCHA

### 3.2 ללא hidden form / iframe

הגישה החדשה **לא משתמשת** ב:
- `<form data-netlify="true">` (Netlify Forms — v1.0)
- `<iframe target=hidden>` + `<form hidden>` (FormSubmit v3.0)
- Base64 obfuscation של כתובת המייל

רק `fetch()` + JSON נקיים. הקוד **פשוט יותר ב-60%** מהגרסה של v3.0.

---

## 4. הגדרה חד-פעמית

### 4.1 אם המפתח כבר מוגדר

אין צורך בדבר. הטופס עובד אוטומטית.

### 4.2 אם רוצים להחליף מפתח (למשל מעבר לחשבון אחר)

1. צור חשבון חדש ב-[web3forms.com](https://web3forms.com)
2. העתק את ה-Access Key החדש
3. ב-`index.html` שורה 12043, עדכן:
   ```javascript
   var WEB3FORMS_KEY = 'YOUR_NEW_KEY_HERE';
   ```
4. Commit + push — המפתח עובד מייד

**אין שלב activation** (בניגוד ל-FormSubmit).

### 4.3 אם רוצים לשנות כתובת יעד

ההודעות מגיעות למייל של החשבון ב-Web3Forms. כדי לשנות יעד:
1. היכנס לחשבון web3forms.com
2. הגדרות → שנה email
3. המפתח נשאר זהה, ההודעות יגיעו לכתובת החדשה

---

## 5. בדיקות ואימות

### ✅ בדיקה 1: טופס מופיע
- לחץ על FAB צף (פינה שמאלית-תחתונה) → modal נפתח
- לחץ על כפתור "הערה / תיקון" בתוך modal של מתכון → modal נפתח עם שדות ה-recipe ממולאים

### ✅ בדיקה 2: validation
- לחץ Submit עם הודעה ריקה → שגיאה "נא לכתוב הודעה"
- הכנס email לא תקין → שגיאה "כתובת אימייל לא תקינה"
- הכנס הודעה קצרה מ-5 תווים → שגיאה "הודעה קצרה מדי"

### ✅ בדיקה 3: שליחה מוצלחת
- מלא טופס תקין → Submit
- צפה ב-"תודה! ההודעה נשלחה בהצלחה."
- בדוק שהגיע מייל ל-asafben33@gmail.com תוך דקה

### ✅ בדיקה 4: CSP
DevTools Console → שלח → ודא שאין:
- שגיאת `Refused to connect to 'https://api.web3forms.com/submit'` → CSP לא כולל את הדומיין

### ✅ בדיקה 5: Network
DevTools → Network → Filter: Fetch/XHR
- Submit → אמור להופיע POST ל-`api.web3forms.com/submit`
- Status: 200 OK
- Response: `{"success": true, ...}`

### ✅ בדיקה 6: Fallback mailto
ב-DevTools → Network → Offline → Submit → אמור לפתוח mailto:

---

## 6. תרחישי edge cases

| תרחיש | מה קורה | איך מטופל |
|---|---|---|
| משתמש סוגר modal באמצע שליחה | `_isSubmitting` נשאר true רגע, fetch ממשיך ברקע | בטוח — אין data loss |
| Network timeout (אין אינטרנט) | fetch throws → catch → timeout 15s | fallback mailto |
| Web3Forms rate limit (250+/חודש) | תגובה: `{success: false, message: "Rate limit..."}` | הודעת שגיאה למשתמש + הצעה ל-mailto |
| Web3Forms spam filter חוסם | תגובה: `{success: false, message: "..."}` | הודעת שגיאה + mailto |
| שדה הודעה ריק | Submit לא נשלח | שגיאה client-side "נא לכתוב הודעה" |
| הודעה > 2000 תווים | Submit נעצר | מונה תווים + שגיאה |
| אימייל לא תקין | Submit נעצר | regex validation |
| Bot ממלא `botcheck` | Web3Forms דוחה אוטומטית | — |
| CSP חוסם connect | fetch throws | timeout → mailto |
| המפתח שגוי/placeholder | תגובה: `{success: false}` | הודעת שגיאה + mailto |

---

## 7. תחזוקה עתידית

### להוסיף שדות לטופס

ב-`submitFeedback()` (שורה ~12150), הוסף ל-payload:

```javascript
var payload = {
  access_key: WEB3FORMS_KEY,
  subject: '...',
  // ...
  new_field: value  // ← הוסף כאן
};
```

### להוסיף domain whitelist

ב-Web3Forms dashboard → הגדרות → Allowed Domains:
```
perlabenharrosh-cookingbook.netlify.app
asafben33.github.io
```

Web3Forms יחסום הגשות מדומיינים אחרים (מונע שימוש לא מורשה).

### להוסיף auto-response למשתמש

ב-payload הוסף:
```javascript
autoresponse: 'תודה על הפנייה — נחזור אליך בהקדם.'
```

Web3Forms ישלח אוטומטית מייל חזרה למשלח.

### להוסיף webhook

ב-Web3Forms dashboard → Webhooks → הוסף URL (Slack/Discord/Zapier).

---

## 8. Fallback — mailto

אם `fetch()` נכשל או לא הגיעה תגובה תוך 15 שניות, המערכת פותחת אוטומטית mailto:

```javascript
var subject = data['feedback-type'] === 'recipe'
  ? 'תיקון למתכון: ' + data['recipe-title']
  : 'הצעה / דיווח — אתר ספר הבישול של פרלה ז"ל';

var body = [
  'סוג: ' + (data['feedback-type'] === 'recipe' ? 'תיקון מתכון' : 'הצעה / תקלה'),
  data['recipe-title'] ? 'מתכון: ' + data['recipe-title'] : '',
  data['recipe-id']    ? 'מזהה: '  + data['recipe-id']    : '',
  'שם: ' + (data['sender-name'] || '(לא צוין)'),
  '', 'תוכן ההודעה:', data['message'] || '',
  '', '---', 'דף: ' + data['page-url']
].filter(Boolean).join('\n');

window.location.href = 'mailto:' + to +
  '?subject=' + encodeURIComponent(subject) +
  '&body='    + encodeURIComponent(body);
```

כתובת היעד נקבעת דינמית: `atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==')` = `asafben33@gmail.com`.

**למה עדיין Base64:** zה לא משחק תפקיד ב-Web3Forms (המפתח הוא הזהות), אבל במסלול ה-fallback של mailto הכתובת גלויה ב-HTML. base64 מונע web scraping פשוט של bots.

---

## 9. היסטוריית הגרסאות

| גרסה | תאריך | גישה | סטטוס |
|---|---|---|---|
| v1.0 | לפני 18/04 | Netlify Forms (`data-netlify="true"`) | נכשל ב-GitHub Pages עם 405 |
| v2.0 | 19/04 (v6.3) | FormSubmit.co AJAX (`fetch`+JSON) | נכשל ב-CORS preflight |
| v3.0 | 19/04 (v6.4) | FormSubmit.co + hidden iframe + form POST | נכשל ב-403 (anti-spam) |
| v3.1 | 19/04 (v6.5) | FormSubmit + שדה `_url` | עדיין 403 |
| **v4.0** | **19/04 (v6.6+)** | **Web3Forms — `fetch()` + JSON + CORS תקין** | **עובד** |

### 9.1 למה FormSubmit נכשל לבסוף

FormSubmit משקיע בגישה של "מינימום הגדרה" ומטיל את החברות שלו על anti-spam אוטומטי. בפועל:
- ה-AJAX endpoint שלו לא החזיר `Access-Control-Allow-Origin` → v2.0 לא עובד
- ה-iframe approach עבד טכנית, אבל anti-spam החזיר 403 לתבניות שדות של הטופס שלנו
- הוספת שדה `_url` לא עזרה — המנגנון שלהם היה אגרסיבי מדי

### 9.2 מה מיוחד ב-Web3Forms

- **CORS נתמך לחלוטין** — headers כוללים `Access-Control-Allow-Origin: *`
- **Spam filter חכם** (לא אגרסיבי) — מבוסס על honeypot (`botcheck` field)
- **Response JSON סטנדרטי** — קל לטפל
- **ללא activation** — הגדרה = עובד

### 9.3 מיגרציה מ-v3.0 ל-v4.0 (v6.6, 19/04/2026)

1. **הסר** את ה-hidden form `#fb-hidden-form` וה-iframe `#fb-iframe-target` מה-HTML
2. **הסר** את הפעולה הדינמית על `hf.action`
3. **הוסף** `var WEB3FORMS_KEY = '705d...';` בתחילת הקובץ
4. **החלף** את `submitFeedback()` בגרסה שמשתמשת ב-`fetch()` → `api.web3forms.com/submit`
5. **עדכן** CSP — הסר formsubmit.co, הוסף api.web3forms.com ל-`connect-src`
6. **מחק** את קבצי הריפו הישנים של FormSubmit (אין צורך)

---

## 10. נושא ידוע — WEB3FORMS_KEY היה ריק ב-v6.10

בעת פריסת v6.10 ב-19/04/2026, המפתח היה placeholder:
```javascript
var WEB3FORMS_KEY = 'PASTE_YOUR_WEB3FORMS_ACCESS_KEY_HERE';
```

טופס המשוב **לא עבד** במשך כמה שעות עד שהמפתח שוחזר ב-v7.0. לא ברור איך ההחלפה קרתה (יתכן סשן Claude קודם שהחליף מפתח ב-placeholder בטעות). **מ-v7.0 המפתח חזר למצבו התקין.**

**מניעה לעתיד:** אם עורכים את `index.html` אוטומטית, ודאו שהמפתח לא מוחלף ב-placeholder.

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
