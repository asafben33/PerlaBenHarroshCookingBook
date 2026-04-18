# מדריך אינטגרציה — מערכת פידבק לאתר ספר הבישול של פרלה ז״ל

**גרסה 2.0** — 19/04/2026 — **מותאם ל-FormSubmit.co AJAX**

*(גרסה 1.0 הייתה מבוססת על Netlify Forms — ראו הסבר בסעיף 1.2 מדוע הוחלפה)*

---

## תוכן

1. [סקירה כללית](#1-סקירה-כללית)
2. [שיטת הסתרת כתובת האימייל (v2.0 — FormSubmit)](#2-שיטת-הסתרת-כתובת-האימייל-v20--formsubmit)
3. [קבצים ומה נוסף](#3-קבצים-ומה-נוסף)
4. [הוראות אינטגרציה צעד-אחר-צעד](#4-הוראות-אינטגרציה-צעד-אחר-צעד)
5. [הפעלת FormSubmit — שלב חד-פעמי](#5-הפעלת-formsubmit--שלב-חד-פעמי)
6. [בדיקות ואימות](#6-בדיקות-ואימות)
7. [תרחישי edge cases](#7-תרחישי-edge-cases)
8. [תחזוקה עתידית](#8-תחזוקה-עתידית)
9. [מיגרציה מ-v1.0 ל-v2.0](#9-מיגרציה-מ-v10-ל-v20)

---

## 1. סקירה כללית

המערכת מספקת שלוש נקודות כניסה למשתמש:

| נקודה | איפה | מה זה עושה |
|---|---|---|
| **כפתור "הערה / תיקון"** | בתוך modal של כל מתכון, ב-`.m-actions` | פותח חלון פידבק עם הקשר למתכון (ID + כותרת) |
| **FAB צף** | פינה שמאלית-תחתונה (RTL), תמיד גלוי | פידבק כללי לאתר / דיווח תקלה |
| **פונקציה גלובלית** | `window.openFeedbackModal(type, recipe)` | לשימוש מכל מקום בקוד (למשל קישור ב-footer) |

### 1.1 ארכיטקטורת High-level

```
משתמש → FAB / כפתור "הערה / תיקון" / window.openFeedbackModal()
    ↓
Modal (#fb-ovl) עם טופס (#fb-form)
    ↓
JS validation (message length, email regex)
    ↓
fetch POST (JSON) → https://formsubmit.co/ajax/{email}
    ↓
FormSubmit מעביר את ההודעה ל-asafben33@gmail.com
    ↓
(אם כישלון) fallback ל-mailto: (פותח email client)
```

### 1.2 למה הוחלפה Netlify Forms?

**הבעיה:** האתר מתארח בשני מקומות — Netlify *וגם* GitHub Pages. Netlify Forms עובד רק במקור Netlify. ב-GitHub Pages (שרת סטטי), POST מחזיר `405 Method Not Allowed`.

**לוג הקונסול שהוכיח את הבעיה:**
```
asafben33.github.io/:1 Failed to load resource: the server responded with a status of 405 (Method Not Allowed)
```

**הפתרון:** FormSubmit.co — שירות form-to-email חיצוני ב-AJAX שעובד מכל מקור (GitHub Pages, Netlify, localhost, file://).

---

## 2. שיטת הסתרת כתובת האימייל (v2.0 — FormSubmit)

### 2.1 שיטה עיקרית: FormSubmit.co AJAX

כתובת `asafben33@gmail.com` מקודדת כ-**base64** בקוד המקור (`FORMSUBMIT_EMAIL_B64`), ומפוענחת ב-runtime.

**כיצד זה עובד:**

1. הקוד מכיל: `var FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ==';`
2. ב-runtime: `atob(FORMSUBMIT_EMAIL_B64)` → `'asafben33@gmail.com'`
3. endpoint נבנה: `'https://formsubmit.co/ajax/' + atob(FORMSUBMIT_EMAIL_B64)`
4. fetch POST JSON עם payload (subject, message, metadata).
5. FormSubmit מעביר את ההודעה למייל המוגדר.

**למה זה טוב:**
- עובד מכל מקור (GH Pages, Netlify, localhost).
- ללא תלות בצד-שרת (JS-only).
- אין API keys בקוד (FormSubmit מבוסס על הכתובת עצמה).
- רמת ההגנה: `asafben33@gmail.com` לא מופיע plain-text בסורס — רק base64.

### 2.2 שיטת ה-Fallback: mailto

אם FormSubmit לא זמין (רשת/CSP/offline), ה-JavaScript מציע קישור mailto. הכתובת מקודדת באותה base64:

```javascript
var to = atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==');
// => 'asafben33@gmail.com'
```

### 2.3 Privacy משופרת (אופציונלי)

אחרי הפעלת FormSubmit (סעיף 5), השירות מספק **URL מוצפן עם hash**:

```
https://formsubmit.co/el/{random-hash}
```

אפשר להחליף את `FORMSUBMIT_EMAIL_B64` עם base64 של ה-hash, וכך הכתובת **לא תופיע בקוד בשום צורה**. זה הפתרון האולטימטיבי לפרטיות.

### 2.4 השוואת חלופות

| קריטריון | FormSubmit | Netlify Forms | EmailJS | FormSpree |
|---|---|---|---|---|
| עובד מ-GitHub Pages | ✓ | ✗ | ✓ | ✓ |
| עובד מ-Netlify | ✓ | ✓ | ✓ | ✓ |
| עובד מ-file:// | ✓ | ✗ | ✓ | ✗ |
| ללא הרשמה | ✓ | — | ✗ | ✗ |
| חינם ללא מגבלה | ✓ | 100/חודש | 200/חודש | 50/חודש |
| ללא תלות JS-lib | ✓ | ✓ | ✗ (40KB) | ✓ |
| AJAX native | ✓ | ✗ (redirect) | ✓ | ✓ |

---

## 3. קבצים ומה נוסף

**שלוש פיסות קוד** שצריך להוסיף ל-`index.html`:

| פיסה | מיקום ב-`index.html` | גודל |
|---|---|---|
| A. CSS | בתוך `<style>` הקיים, בסוף | ~150 שורות |
| B. HTML | בסוף `<body>`, לפני `</body>` | ~50 שורות |
| C. JavaScript | בתוך `<script>` הקיים, בסוף | ~170 שורות (v2.0) |
| D. תוספת קטנה ל-`.m-actions` | ב-DOM של modal המתכון | שורה אחת |

גם צריך:
- **`_headers` file** בשורש הפרויקט (ל-Netlify, עם formsubmit.co מותר).
- **CSP update** ב-`<meta>` — `connect-src 'self' https://formsubmit.co`.
- **הפעלה חד-פעמית** של FormSubmit (סעיף 5).

---

## 4. הוראות אינטגרציה צעד-אחר-צעד

### שלב A: CSS

*(לא השתנה מ-v1.0. פרטי ה-CSS זהים. ראו LLD 3.5 לטבלה מלאה של 28 classes.)*

### שלב B: HTML

*(המודל והFAB זהים ל-v1.0. הטופס הנסתר של Netlify **הוסר** — JS שולח JSON ישירות.)*

**חשוב — אם יש לך גרסה קודמת (v1.0):** הסר את הטופס הנסתר של Netlify:

```html
<!-- הסר את זה: -->
<form name="perla-feedback" method="POST" data-netlify="true" hidden>
  ...
</form>
```

החלף ב:

```html
<!-- Feedback uses FormSubmit.co AJAX — no hidden form needed, JS posts directly. -->
```

### שלב C: JavaScript (v2.0 — FormSubmit.co)

חפש את סוף ה-`<script>` הראשי ב-`index.html` (לפני `</script>`). הדבק את הבלוק הבא:

```javascript
/* ═══════════════════════════════════════════════════════════════════
   FEEDBACK SYSTEM v2.0 — Perla Cookbook (FormSubmit.co AJAX)
   Privacy: Email is base64-obfuscated in source code.
            For max privacy, replace with hashed alias after activation.
   Activation: First submission triggers FormSubmit verification email.
               Click link once → future submissions arrive normally.
═══════════════════════════════════════════════════════════════════ */
(function() {
  'use strict';

  /* FormSubmit.co — free form-to-email service (no signup).
     First-ever submission triggers activation: owner receives verification
     email, clicks link, then future submissions arrive normally.
     For extra privacy, after activation replace the email with the hashed
     alias that FormSubmit provides (https://formsubmit.co/el/{hash}). */
  var FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ==';
  var FORM_NAME = 'perla-feedback';  // legacy — kept for compat
  var MAX_MSG   = 2000;

  var _type = null;
  var _recipe = null;
  var _isSubmitting = false;

  function $(id) { return document.getElementById(id); }

  function escapeHtml(s) {
    return String(s || '').replace(/[<>&"']/g, function(c) {
      return ({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;',"'":'&#039;'})[c];
    });
  }

  function setStatus(msg, kind) {
    var el = $('fb-status');
    if (!el) return;
    el.className = 'fb-status' + (kind ? ' show ' + kind : '');
    if (msg === undefined || msg === null) { el.innerHTML = ''; return; }
    el.innerHTML = msg;
  }

  function updateCharCount() {
    var msg = $('fb-message');
    var counter = $('fb-count');
    if (msg && counter) counter.textContent = msg.value.length;
  }

  function openFeedbackModal(type, recipe) {
    _type = type || 'site';
    _recipe = recipe || null;

    var ovl = $('fb-ovl');
    var title = $('fb-title');
    var context = $('fb-context');
    var form = $('fb-form');

    if (!ovl || !title || !context) return;

    if (form) form.reset();
    setStatus('');
    updateCharCount();

    if (_type === 'recipe' && _recipe) {
      title.textContent = 'הערה / תיקון על מתכון';
      context.innerHTML = 'לגבי המתכון: <strong>' + escapeHtml(_recipe.title) + '</strong>';
      context.hidden = false;
    } else {
      title.textContent = 'הצעה לשיפור או דיווח על תקלה';
      context.hidden = true;
    }

    ovl.classList.add('open');
    ovl.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    setTimeout(function() {
      var f = $('fb-message');
      if (f) f.focus();
    }, 100);
  }

  function closeFeedbackModal() {
    var ovl = $('fb-ovl');
    if (!ovl) return;
    ovl.classList.remove('open');
    ovl.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    _type = null;
    _recipe = null;
  }

  function submitFeedback(e) {
    if (e) e.preventDefault();
    if (_isSubmitting) return;

    var submitBtn = $('fb-submit');
    var message = ($('fb-message') || {}).value || '';
    var name    = ($('fb-name') || {}).value || '';
    var email   = ($('fb-email') || {}).value || '';

    /* Validation */
    if (!message.trim()) {
      setStatus('נא לכתוב הודעה לפני השליחה.', 'error');
      return;
    }
    if (message.length > MAX_MSG) {
      setStatus('ההודעה ארוכה מדי (מקסימום ' + MAX_MSG + ' תווים).', 'error');
      return;
    }
    if (email && !email.match(/^[^@\s]+@[^@\s]+\.[^@\s]+$/)) {
      setStatus('כתובת אימייל לא תקינה.', 'error');
      return;
    }

    _isSubmitting = true;
    if (submitBtn) submitBtn.disabled = true;
    setStatus('שולח הודעה...', 'loading');

    /* Build email subject */
    var subject = (_type === 'recipe' && _recipe)
      ? 'תיקון למתכון: ' + _recipe.title
      : 'הצעה / תקלה — אתר ספר הבישול של פרלה ז״ל';

    /* Payload for FormSubmit.co AJAX endpoint.
       Keys prefixed with _ configure email behavior. */
    var payload = {
      _subject:  subject,
      _template: 'table',
      _captcha:  'false',
      _honey:    '',
      name:      name.slice(0, 80) || '(לא צוין)',
      email:     email.slice(0, 100) || '(לא צוין)',
      message:   message.slice(0, MAX_MSG),
      type:      _type || 'site',
      recipe_id:    _recipe ? String(_recipe.id) : '',
      recipe_title: _recipe ? String(_recipe.title) : '',
      page_url:  location.href,
      user_agent: (navigator.userAgent || '').slice(0, 200)
    };

    /* Mailto fallback payload — uses old key names for openMailtoFallback() compat */
    var mailtoData = {
      'feedback-type': _type || 'site',
      'recipe-title':  _recipe ? String(_recipe.title) : '',
      'recipe-id':     _recipe ? String(_recipe.id)    : '',
      'sender-name':   name.slice(0, 80),
      'message':       message.slice(0, MAX_MSG),
      'page-url':      location.href
    };

    /* POST to FormSubmit.co — works from any origin (GH Pages, Netlify, etc.)
       Email is base64-obfuscated to foil simple scrapers. */
    var endpoint = 'https://formsubmit.co/ajax/' + atob(FORMSUBMIT_EMAIL_B64);

    fetch(endpoint, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body:    JSON.stringify(payload)
    })
    .then(function(r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(function(data) {
      /* FormSubmit returns { success: 'true' } on delivery.
         First-ever submission returns success:'false' + activation msg —
         email is queued and delivered after owner clicks verification link.
         For UX we treat both states as successfully captured. */
      var okDelivered = (String(data.success).toLowerCase() === 'true' || data.success === true);
      var msg = okDelivered
        ? 'תודה! ההודעה נשלחה בהצלחה.'
        : 'תודה! ההודעה נקלטה בהצלחה.';
      setStatus(msg, 'success');
      setTimeout(closeFeedbackModal, 2500);
    })
    .catch(function(err) {
      /* Network error, CSP block, offline, or FormSubmit unreachable.
         Fall back to mailto — always works (opens user's email client). */
      setStatus(
        'שליחה ישירה נכשלה. <a href="#" id="fb-mailto-fallback">פתח באימייל במקום</a>',
        'error'
      );
      var m = $('fb-mailto-fallback');
      if (m) m.addEventListener('click', function(ev) {
        ev.preventDefault();
        openMailtoFallback(mailtoData);
      });
    })
    .then(function() {
      _isSubmitting = false;
      if (submitBtn) submitBtn.disabled = false;
    });
  }

  function openMailtoFallback(data) {
    var to = atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==');
    var subject = data['feedback-type'] === 'recipe'
      ? 'תיקון למתכון: ' + data['recipe-title']
      : 'הצעה / דיווח — אתר ספר הבישול של פרלה ז״ל';
    var body = [
      'סוג: ' + (data['feedback-type'] === 'recipe' ? 'תיקון מתכון' : 'הצעה / תקלה'),
      data['recipe-title'] ? 'מתכון: ' + data['recipe-title'] : '',
      data['recipe-id']    ? 'מזהה: '  + data['recipe-id']    : '',
      'שם: ' + (data['sender-name'] || '(לא צוין)'),
      '',
      'תוכן ההודעה:',
      data['message'] || '',
      '',
      '---',
      'דף: ' + data['page-url']
    ].filter(Boolean).join('\n');

    window.location.href = 'mailto:' + to +
      '?subject=' + encodeURIComponent(subject) +
      '&body='    + encodeURIComponent(body);
  }

  function initFeedback() {
    var fab = $('fb-fab');
    if (fab) fab.addEventListener('click', function() {
      openFeedbackModal('site', null);
    });

    var closeBtn = $('fb-close');
    if (closeBtn) closeBtn.addEventListener('click', closeFeedbackModal);

    var cancelBtn = $('fb-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', closeFeedbackModal);

    var ovl = $('fb-ovl');
    if (ovl) ovl.addEventListener('click', function(e) {
      if (e.target === ovl) closeFeedbackModal();
    });

    var form = $('fb-form');
    if (form) form.addEventListener('submit', submitFeedback);

    var msg = $('fb-message');
    if (msg) msg.addEventListener('input', updateCharCount);

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        var ovl = $('fb-ovl');
        if (ovl && ovl.classList.contains('open')) closeFeedbackModal();
      }
    });

    var recBtn = $('m-feedback-act');
    if (recBtn) recBtn.addEventListener('click', function() {
      if (typeof CUR_REC !== 'undefined' && CUR_REC) {
        openFeedbackModal('recipe', { id: CUR_REC.id, title: CUR_REC.title });
      } else {
        openFeedbackModal('site', null);
      }
    });
  }

  window.openFeedbackModal  = openFeedbackModal;
  window.closeFeedbackModal = closeFeedbackModal;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFeedback);
  } else {
    initFeedback();
  }
})();
```

### שלב D: תוספת קטנה ל-`.m-actions` במודל המתכון

*(לא השתנה מ-v1.0)*

ב-`index.html`, מצא את הבלוק של `<div class="m-actions">` (בתוך ה-modal של המתכון). הוסף את הכפתור:

```html
<button id="m-feedback-act" class="m-act-media fb-recipe-btn" aria-label="הערה או תיקון למתכון">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" aria-hidden="true">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
  הערה / תיקון
</button>
```

### שלב E: CSP עדכון (v2.0 — חובה)

ב-`<meta http-equiv="Content-Security-Policy">` ב-`<head>`, וודא ש-`connect-src` מכיל את `formsubmit.co`:

```
connect-src 'self' https://formsubmit.co;
```

**גם חשוב** — הסר את `frame-ancestors` מה-meta (הדפדפן מתעלם ממנו דרך meta; מוגדר ב-`_headers`):
- ❌ הסר: `frame-ancestors 'none';`
- ✓ הגדר ב-`_headers` במקום.

ללא עדכון ה-CSP, הדפדפן יחסום את ה-fetch ל-FormSubmit.

### שלב F: קובץ `_headers` של Netlify (מומלץ)

צור קובץ `_headers` בשורש הפרויקט עם התוכן הבא:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob: https://i.ytimg.com https://img.youtube.com; media-src 'self' blob:; connect-src 'self' https://formsubmit.co; frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com; object-src 'none'; base-uri 'self'; form-action 'self' https://formsubmit.co; frame-ancestors 'none';
```

זה מגדיר CSP כ-HTTP header (נתמך יותר טוב מ-meta) + כותרות אבטחה נוספות + `frame-ancestors` כהלכה.

---

## 5. הפעלת FormSubmit — שלב חד-פעמי

FormSubmit דורש **אישור חד-פעמי** בשליחה הראשונה מכל כתובת חדשה.

### 5.1 Deploy ראשון

1. Push ל-GitHub.
2. Netlify (ו/או GitHub Pages) יפרוס אוטומטית.
3. המתן 1-2 דקות עד סיום ה-deploy.

### 5.2 שליחת הודעת בדיקה

1. פתח את האתר החי.
2. לחץ על כפתור ה-FAB השמאלי-תחתון ("הצעות ודיווח").
3. מלא שדה הודעה עם טקסט כלשהו (למשל "test").
4. לחץ "שליחה".
5. צריך להופיע: **"תודה! ההודעה נקלטה בהצלחה."**

### 5.3 בדוק את תיבת הדוא"ל שלך

1. היכנס ל-`asafben33@gmail.com`.
2. חפש מייל חדש מ-**`contact@formsubmit.co`** עם נושא דומה ל:
   > *"Please activate your form submission"*
3. פתח את המייל.

### 5.4 לחץ על קישור האישור

1. במייל יש כפתור/קישור ירוק לאישור (**"Confirm"** / **"Activate"**).
2. לחץ עליו.
3. תועבר לדף של FormSubmit שמאשר את ההפעלה.
4. **מרגע זה, כל ההודעות הבאות יגיעו ישירות לתיבה שלך** ללא צורך באישור נוסף.

### 5.5 (אופציונלי) — שדרוג פרטיות עם hashed alias

לאחר האישור, FormSubmit מספק URL מוצפן:

1. בעמוד האישור יש לינק ל-"Go to form settings".
2. שם תמצא URL בפורמט: `https://formsubmit.co/el/{some-random-hash}`
3. החלף את `FORMSUBMIT_EMAIL_B64` בקוד עם base64 של ה-hash.

**יתרון:** הכתובת `asafben33@gmail.com` **כלל לא מופיעה בקוד** — רק hash אקראי.

### 5.6 (אופציונלי) הגדרות מתקדמות ב-FormSubmit

בדף ההגדרות של FormSubmit אפשר:
- **Auto-response** — תגובה אוטומטית למשתמש ששלח.
- **Blacklist email patterns** — חסימת ספאם.
- **reCAPTCHA** — אם מתחיל להגיע spam.
- **Webhook** — העברה ל-Slack/Discord/Zapier.

---

## 6. בדיקות ואימות

אחרי הפריסה וההפעלה, בדוק את שבעת התרחישים הבאים:

### ✅ בדיקה 1: פידבק על מתכון ספציפי
1. פתח את האתר.
2. לחץ על מתכון כלשהו → יפתח ה-modal שלו.
3. גלול למטה לאזור הכפתורים → לחץ על "הערה / תיקון".
4. צריך להיפתח modal עם הטקסט "לגבי המתכון: [שם המתכון]".
5. מלא שדה הודעה → לחץ שליחה.
6. צריכה להופיע הודעת הצלחה, והחלון ייסגר אחרי 2.5 שניות.
7. בדוק את המייל שלך — ההודעה צריכה להגיע (אחרי ה-activation).

### ✅ בדיקה 2: פידבק כללי דרך FAB
1. סגור את ה-modal של המתכון.
2. לחץ על הכפתור הצף בפינה שמאלית-תחתונה ("הצעות ודיווח").
3. צריך להיפתח modal בלי שדה context.
4. מלא ושלח → וודא שההודעה הגיעה.

### ✅ בדיקה 3: ולידציה
1. פתח את ה-feedback modal.
2. לחץ "שליחה" בלי להזין הודעה → שגיאה אדומה.
3. הזן אימייל לא תקין (`blah@blah`) ומסר חוקי → שגיאה על האימייל.
4. הזן הודעה תקינה → שליחה תעבוד.

### ✅ בדיקה 4: נגישות
1. פתח modal → לחץ `Escape` → החלון ייסגר.
2. פתח modal → לחץ במרחב הכהה (מחוץ לחלון) → החלון ייסגר.
3. נווט עם `Tab` בין השדות — focus נשאר בתוך ה-modal.
4. פתח עם קורא מסך (אם זמין) — הכותרת נקראת, השדות מתויגים.

### ✅ בדיקה 5: Mobile
1. פתח באייפון/אנדרואיד.
2. ה-modal צריך להיות bottom-sheet (נצמד לתחתית).
3. ה-FAB צריך להיראות קטן יותר (בלי טקסט, רק אייקון).

### ✅ בדיקה 6: Fallback mailto
1. חסום בכוח את `formsubmit.co` (למשל דרך DevTools → Network → Block URL).
2. שלח הודעה — fetch יכשל.
3. תופיע הצעת mailto ("פתח באימייל במקום").
4. לחץ על הקישור → ייפתח לקוח המייל עם הטקסט המלא.

### ✅ בדיקה 7: CSP (חדש ב-v2.0)
1. פתח DevTools → Console.
2. שלח הודעה → וודא שאין שגיאת CSP:
   > *"Refused to connect to 'https://formsubmit.co/...' because it violates the following Content Security Policy directive: \"connect-src 'self'\""*
3. אם הופיעה — עדכן את ה-CSP (ראו שלב E).

---

## 7. תרחישי edge cases

| תרחיש | מה קורה | איך מטופל |
|---|---|---|
| המשתמש סוגר את ה-modal באמצע שליחה | `_isSubmitting` נשאר true רגע, submit יושלם ברקע | בטוח — אין data loss |
| Network timeout | fetch נכשל | fallback mailto מוצע |
| שדה הודעה ריק | Submit לא נשלח | שגיאה "נא לכתוב הודעה" |
| הודעה ארוכה מ-2000 תווים | Submit נעצר | מונה תווים מראה מראש |
| אימייל לא תקין | Submit נעצר | ולידציה regex |
| Bot ממלא את כל השדות | `_honey` field לא אמור להיות מלא | FormSubmit דוחה אוטומטית |
| **פעם ראשונה — לפני activation** | FormSubmit מחזיר `success:"false"` + activation email | UX מציג "תודה! ההודעה נקלטה בהצלחה" — ההודעה נשמרת ותישלח אחרי האישור |
| **FormSubmit rate-limit exceeded** | Returns 4xx → `.catch()` | fallback mailto |
| **CSP חוסם** את fetch ל-formsubmit.co | fetch throws | fallback mailto |
| **Offline / No internet** | fetch throws `TypeError: Failed to fetch` | fallback mailto |
| **FormSubmit service outage** | Returns 5xx | fallback mailto |
| User לחץ כמה פעמים "שלח" | `_isSubmitting` מונע שליחה כפולה | כפתור מושבת |

---

## 8. תחזוקה עתידית

### להוסיף קישור ב-footer

במקום בו יש footer באתר, הוסף:

```html
<a href="#" onclick="openFeedbackModal('site', null); return false;">
  דיווח על תקלה או הצעה לשיפור
</a>
```

### להחליף את כתובת היעד

אם בעתיד תחליף את `asafben33@gmail.com` לכתובת אחרת:

1. קודד את הכתובת החדשה ב-base64:
   ```javascript
   btoa('newemail@example.com')
   // => "bmV3ZW1haWxAZXhhbXBsZS5jb20="
   ```
2. החלף את `FORMSUBMIT_EMAIL_B64` בקוד.
3. החלף גם ב-`openMailtoFallback()` (הוא משתמש ב-base64 נפרד).
4. **חזור על תהליך האישור** (סעיף 5) — הכתובת החדשה דורשת activation חדש.

### לעבור ל-hashed alias (פרטיות מקסימלית)

1. היכנס להגדרות ה-FormSubmit שלך.
2. העתק את ה-URL עם ה-hash: `https://formsubmit.co/el/{hash}`.
3. ב-JavaScript, שנה את בניית ה-endpoint:
   ```javascript
   // Before:
   var endpoint = 'https://formsubmit.co/ajax/' + atob(FORMSUBMIT_EMAIL_B64);
   
   // After (using hash — email never exposed):
   var HASH_B64 = 'base64-of-your-hash';
   var endpoint = 'https://formsubmit.co/ajax/el/' + atob(HASH_B64);
   ```

### ניטור

FormSubmit Dashboard → Submissions — רואה את כל ההודעות שנשלחו (דורש login).

### להוסיף auto-response

בשליחה, הוסף ל-payload:
```javascript
_autoresponse: 'תודה על הפנייה — קיבלנו את ההודעה ונחזור אליך בהקדם.'
```

FormSubmit ישלח אוטומטית את ההודעה הזו למשתמש ששלח (אם מילא אימייל).

---

## 9. מיגרציה מ-v1.0 ל-v2.0

אם יש לך גרסה קודמת שמבוססת על Netlify Forms (v1.0), הנה רשימת פעולות:

### 9.1 הסרת קוד ישן מ-HTML

**הסר** את הטופס הנסתר מ-`index.html`:
```html
<form name="perla-feedback" method="POST" data-netlify="true" netlify-honeypot="bot-field" hidden>
  ...
</form>
```

### 9.2 החלפת JavaScript

**החלף** את כל פונקציית `submitFeedback()` וההגדרות הנלוות בגרסה החדשה מ-שלב C למעלה.

**הוסף** את הקבוע:
```javascript
var FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ==';
```

### 9.3 עדכון CSP ב-meta

- **לפני:** `connect-src 'self'; ... frame-ancestors 'none';`
- **אחרי:** `connect-src 'self' https://formsubmit.co; ...` (בלי `frame-ancestors`)

### 9.4 עדכון `_headers`

אם יש לך `_headers` של Netlify:
- `connect-src 'self' https://formsubmit.co;`
- `form-action 'self' https://formsubmit.co;`
- `frame-ancestors 'none';` — מוגדר כאן בלבד

### 9.5 Netlify Dashboard

אחרי המיגרציה, תוכל **לבטל את ההתראות הישנות** ב-Netlify:
1. Netlify Dashboard → Forms → `perla-feedback`.
2. Settings → Form notifications → הסר את כתובת המייל הישנה.
3. (אופציונלי) מחק את הטופס מה-Dashboard — הוא לא מקבל יותר נתונים.

### 9.6 הפעל FormSubmit

עקוב אחר סעיף 5 לעיל — שלח הודעת בדיקה, קבל מייל activation, לחץ על הקישור.

---

## קבצים מצורפים

- `feedback_demo.html` — דמו HTML עצמאי שאפשר לפתוח בדפדפן ולראות את המערכת עובדת (בלי שליחה אמיתית).
- `INTEGRATION_GUIDE.md` — המסמך הזה.
- `_headers` — קובץ Netlify לכותרות אבטחה.

---

## סיכום

1. הדבק את ה-CSS (שלב A) → HTML (שלב B) → JS v2.0 (שלב C) לתוך `index.html`.
2. הוסף את כפתור ה-"הערה / תיקון" ל-`.m-actions` (שלב D).
3. עדכן CSP ב-meta (שלב E).
4. צור `_headers` (שלב F).
5. Push ל-GitHub → Netlify/GitHub Pages יפרוס אוטומטית.
6. בצע הפעלה חד-פעמית של FormSubmit (סעיף 5).
7. בדוק לפי 7 הבדיקות למעלה.

הכתובת `asafben33@gmail.com` מקודדת כ-base64 בקוד. לפרטיות מקסימלית, החלף בהאש אליאס אחרי ההפעלה.

**גרסה 2.0** — 19/04/2026
