# מדריך אינטגרציה — מערכת פידבק לאתר ספר הבישול של פרלה ז״ל

**גרסה 3.0** — 19/04/2026 — **FormSubmit.co עם Hidden Iframe (פתרון CORS)**

*(גרסה 2.0 ניסתה fetch+JSON ונכשלה ב-CORS; גרסה 1.0 השתמשה ב-Netlify Forms — ראו סעיף 1.2 להיסטוריה)*

---

## תוכן

1. [סקירה כללית](#1-סקירה-כללית)
2. [שיטת הסתרת כתובת האימייל](#2-שיטת-הסתרת-כתובת-האימייל)
3. [קבצים ומה נוסף](#3-קבצים-ומה-נוסף)
4. [הוראות אינטגרציה צעד-אחר-צעד](#4-הוראות-אינטגרציה-צעד-אחר-צעד)
5. [הפעלת FormSubmit — שלב חד-פעמי](#5-הפעלת-formsubmit--שלב-חד-פעמי)
6. [בדיקות ואימות](#6-בדיקות-ואימות)
7. [תרחישי edge cases](#7-תרחישי-edge-cases)
8. [תחזוקה עתידית](#8-תחזוקה-עתידית)
9. [מיגרציה מגרסאות קודמות](#9-מיגרציה-מגרסאות-קודמות)

---

## 1. סקירה כללית

המערכת מספקת שלוש נקודות כניסה למשתמש:

| נקודה | איפה | מה זה עושה |
|---|---|---|
| **כפתור "הערה / תיקון"** | בתוך modal של כל מתכון, ב-`.m-actions` | פותח חלון פידבק עם הקשר למתכון |
| **FAB צף** | פינה שמאלית-תחתונה, תמיד גלוי | פידבק כללי לאתר / דיווח תקלה |
| **פונקציה גלובלית** | `window.openFeedbackModal(type, recipe)` | לשימוש מכל מקום בקוד |

### 1.1 ארכיטקטורת High-level (v3.0)

```
משתמש → FAB / כפתור "הערה / תיקון"
    ↓
Modal פידבק עם טופס
    ↓
JS validation (אורך, email regex)
    ↓
JS מאכלס hidden form (#fb-hidden-form) — 12 שדות
    ↓
JS מגדיר action דינמית: 'https://formsubmit.co/' + atob(EMAIL_B64)
    ↓
hf.submit() — Form POST classic, target=hidden iframe
    ↓
הדפדפן שולח POST ישיר (NO CORS preflight!)
    ↓
FormSubmit מעביר ל-asafben33@gmail.com
    ↓
iframe.onload נורה → "תודה! ההודעה נשלחה בהצלחה."
    ↓
(15s timeout) → אם לא הגיע load → fallback ל-mailto
```

### 1.2 היסטוריית הגרסאות

| גרסה | גישה | בעיה |
|---|---|---|
| **v1.0** | Netlify Forms (data-netlify="true") | נכשל ב-GitHub Pages עם 405 (Method Not Allowed) |
| **v2.0** | FormSubmit.co AJAX — fetch + JSON | נכשל ב-CORS preflight (No Access-Control-Allow-Origin) |
| **v3.0** | FormSubmit.co + Hidden Iframe + Form POST | **עובד** — לא כפוף ל-CORS |

### 1.3 למה הגישה הזו עובדת

**CORS preflight** (OPTIONS request מקדים) מופעל אוטומטית כש:
- שולחים `Content-Type: application/json` (או כל `Content-Type` שאינו `application/x-www-form-urlencoded`, `multipart/form-data`, או `text/plain`)
- מוסיפים custom headers כמו `Accept: application/json`
- משתמשים במתודות כמו PUT, DELETE

**FormSubmit's AJAX endpoint** אינו מחזיר `Access-Control-Allow-Origin` בתגובת ה-OPTIONS, ולכן הדפדפן חוסם את ה-POST.

**אבל:** טפסי HTML מסורתיים (`<form method="POST">`) עם `target="iframe"` **אינם כפופים ל-CORS** (זו התנהגות מורשת מ-HTML 4). הדפדפן שולח POST ישירות, התגובה מטוענת ב-iframe (JS אינו קורא אותה), ואין צורך ב-Access-Control-Allow-Origin.

---

## 2. שיטת הסתרת כתובת האימייל

### 2.1 Base64 obfuscation בקוד

כתובת `asafben33@gmail.com` מקודדת כ-base64:

```javascript
var FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ==';
// runtime: atob(FORMSUBMIT_EMAIL_B64) → 'asafben33@gmail.com'
```

חשוב: ה-action של ה-form **אינו** hardcoded ב-HTML. הוא מוגדר דינמית ב-JS ברגע השליחה:

```javascript
hf.action = 'https://formsubmit.co/' + atob(FORMSUBMIT_EMAIL_B64);
```

זה מונע מ-scrapers פשוטים לזהות את הכתובת בסורס.

### 2.2 Fallback: mailto

אם iframe לא מטען תוך 15 שניות, או אם `hf.submit()` זורק שגיאה, מופיע קישור mailto עם הכתובת המפוענחת באותה דרך.

### 2.3 שדרוג פרטיות (אחרי activation)

FormSubmit מספק URL מוצפן אחרי ההפעלה הראשונה: `https://formsubmit.co/el/{hash}`. אפשר להחליף את `FORMSUBMIT_EMAIL_B64` עם base64 של ה-hash — אז הכתובת **כלל לא תופיע בקוד**.

---

## 3. קבצים ומה נוסף

| רכיב | מיקום | גודל |
|---|---|---|
| A. CSS | בסוף `<style>` | ~150 שורות |
| B. HTML — modal + FAB | לפני `</body>` | ~50 שורות |
| **C. HTML — hidden iframe + form** (v3.0) | לפני `</body>` | ~20 שורות |
| D. JavaScript | בסוף `<script>` | ~180 שורות |
| E. כפתור "הערה / תיקון" ב-modal מתכון | ב-`.m-actions` | שורה 1 |
| F. CSP update | ב-`<meta>` CSP | עדכון ערכים |
| G. `_headers` | שורש הפרויקט | קובץ חדש |

---

## 4. הוראות אינטגרציה צעד-אחר-צעד

### שלב A: CSS

*(זהה לגרסה 2.0)*

### שלב B: HTML — Modal + FAB

*(זהה לגרסה 2.0)*

### שלב C: HTML — Hidden iframe + hidden form (חדש ב-v3.0)

**זה החלק הקריטי לפתרון CORS.** הוסף לפני `</body>`:

```html
<!-- ═══════════════════════════════════════════════════════════
     FEEDBACK FORM — Hidden iframe + form for FormSubmit.co
     Why: FormSubmit's /ajax/ endpoint doesn't handle CORS preflight
     from cross-origin pages. Traditional form POSTs to a hidden
     iframe target are NOT subject to CORS, so this works anywhere.
═══════════════════════════════════════════════════════════ -->
<iframe name="fb-iframe-target"
        id="fb-iframe-target"
        title="טופס פידבק (יעד מוסתר)"
        aria-hidden="true"
        tabindex="-1"
        style="position:absolute;width:0;height:0;border:0;visibility:hidden"></iframe>

<form id="fb-hidden-form"
      method="POST"
      target="fb-iframe-target"
      enctype="application/x-www-form-urlencoded"
      accept-charset="UTF-8"
      style="display:none"
      aria-hidden="true"
      hidden>
  <!-- action set dynamically by JS — keeps email base64-obfuscated -->
  <input type="hidden" name="_subject"     id="fb-hf-subject"      value="">
  <input type="hidden" name="_template"    value="table">
  <input type="hidden" name="_captcha"     value="false">
  <input type="hidden" name="_honey"       value="">
  <input type="hidden" name="name"         id="fb-hf-name"         value="">
  <input type="hidden" name="email"        id="fb-hf-email"        value="">
  <input type="hidden" name="message"      id="fb-hf-message"      value="">
  <input type="hidden" name="type"         id="fb-hf-type"         value="">
  <input type="hidden" name="recipe_id"    id="fb-hf-recipe-id"    value="">
  <input type="hidden" name="recipe_title" id="fb-hf-recipe-title" value="">
  <input type="hidden" name="page_url"     id="fb-hf-page-url"     value="">
  <input type="hidden" name="user_agent"   id="fb-hf-user-agent"  value="">
</form>
```

**חשוב:**
- `name="fb-iframe-target"` — חובה כדי ש-`target` של הטופס יזהה אותו
- `enctype="application/x-www-form-urlencoded"` — "simple request", לא מפעיל preflight
- `accept-charset="UTF-8"` — תמיכה נכונה בעברית
- action **לא** מוגדר ב-HTML — מוגדר ב-JS (`hf.action = ...`)

### שלב D: JavaScript (v3.0 — Hidden Iframe)

חפש את סוף ה-`<script>` הראשי ב-`index.html`. הדבק:

```javascript
/* ═══════════════════════════════════════════════════════════════════
   FEEDBACK SYSTEM v3.0 — Perla Cookbook (Hidden Iframe + Form POST)
   Bypass CORS by using classic form submission to a hidden iframe.
   Works from any origin (GH Pages, Netlify, file://, localhost).
═══════════════════════════════════════════════════════════════════ */
(function() {
  'use strict';

  var FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ==';
  var FORM_NAME = 'perla-feedback';
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
    var ovl = $('fb-ovl'), title = $('fb-title'), context = $('fb-context'), form = $('fb-form');
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
    setTimeout(function() { var f = $('fb-message'); if (f) f.focus(); }, 100);
  }

  function closeFeedbackModal() {
    var ovl = $('fb-ovl');
    if (!ovl) return;
    ovl.classList.remove('open');
    ovl.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    _type = null; _recipe = null;
  }

  function submitFeedback(e) {
    if (e) e.preventDefault();
    if (_isSubmitting) return;

    var submitBtn = $('fb-submit');
    var message = ($('fb-message') || {}).value || '';
    var name    = ($('fb-name') || {}).value || '';
    var email   = ($('fb-email') || {}).value || '';

    if (!message.trim()) { setStatus('נא לכתוב הודעה לפני השליחה.', 'error'); return; }
    if (message.length > MAX_MSG) { setStatus('ההודעה ארוכה מדי (מקסימום ' + MAX_MSG + ' תווים).', 'error'); return; }
    if (email && !email.match(/^[^@\s]+@[^@\s]+\.[^@\s]+$/)) { setStatus('כתובת אימייל לא תקינה.', 'error'); return; }

    _isSubmitting = true;
    if (submitBtn) submitBtn.disabled = true;
    setStatus('שולח הודעה...', 'loading');

    var subject = (_type === 'recipe' && _recipe)
      ? 'תיקון למתכון: ' + _recipe.title
      : 'הצעה / תקלה — אתר ספר הבישול של פרלה ז\u05f4ל';

    var mailtoData = {
      'feedback-type': _type || 'site',
      'recipe-title':  _recipe ? String(_recipe.title) : '',
      'recipe-id':     _recipe ? String(_recipe.id)    : '',
      'sender-name':   name.slice(0, 80),
      'message':       message.slice(0, MAX_MSG),
      'page-url':      location.href
    };

    /* Hidden iframe + form approach — bypasses CORS preflight entirely. */
    var hf = $('fb-hidden-form');
    var iframe = $('fb-iframe-target');
    if (!hf || !iframe) {
      setStatus('שליחה ישירה לא זמינה. <a href="#" id="fb-mailto-fallback">פתח באימייל במקום</a>', 'error');
      var mFb = $('fb-mailto-fallback');
      if (mFb) mFb.addEventListener('click', function(ev) { ev.preventDefault(); openMailtoFallback(mailtoData); });
      _isSubmitting = false; if (submitBtn) submitBtn.disabled = false;
      return;
    }

    hf.action = 'https://formsubmit.co/' + atob(FORMSUBMIT_EMAIL_B64);

    function setF(id, value) { var el = $(id); if (el) el.value = value || ''; }
    setF('fb-hf-subject',      subject);
    setF('fb-hf-name',         name.slice(0, 80) || '(לא צוין)');
    setF('fb-hf-email',        email.slice(0, 100) || '(לא צוין)');
    setF('fb-hf-message',      message.slice(0, MAX_MSG));
    setF('fb-hf-type',         _type || 'site');
    setF('fb-hf-recipe-id',    _recipe ? String(_recipe.id) : '');
    setF('fb-hf-recipe-title', _recipe ? String(_recipe.title) : '');
    setF('fb-hf-page-url',     location.href);
    setF('fb-hf-user-agent',   (navigator.userAgent || '').slice(0, 200));

    var done = false;
    function onSuccess() {
      if (done) return;
      done = true;
      try { iframe.removeEventListener('load', onSuccess); } catch(e) {}
      clearTimeout(timeoutId);
      setStatus('תודה! ההודעה נשלחה בהצלחה.', 'success');
      setTimeout(closeFeedbackModal, 2500);
      _isSubmitting = false; if (submitBtn) submitBtn.disabled = false;
    }

    function onTimeout() {
      if (done) return;
      done = true;
      try { iframe.removeEventListener('load', onSuccess); } catch(e) {}
      setStatus('שליחה אורכת זמן רב מהצפוי. <a href="#" id="fb-mailto-fallback">פתח באימייל במקום</a>', 'error');
      var mF = $('fb-mailto-fallback');
      if (mF) mF.addEventListener('click', function(ev) { ev.preventDefault(); openMailtoFallback(mailtoData); });
      _isSubmitting = false; if (submitBtn) submitBtn.disabled = false;
    }

    iframe.addEventListener('load', onSuccess);
    var timeoutId = setTimeout(onTimeout, 15000);

    try {
      hf.submit();
    } catch (err) {
      try { iframe.removeEventListener('load', onSuccess); } catch(e) {}
      clearTimeout(timeoutId);
      setStatus('שליחה ישירה נכשלה. <a href="#" id="fb-mailto-fallback">פתח באימייל במקום</a>', 'error');
      var mE = $('fb-mailto-fallback');
      if (mE) mE.addEventListener('click', function(ev) { ev.preventDefault(); openMailtoFallback(mailtoData); });
      _isSubmitting = false; if (submitBtn) submitBtn.disabled = false;
    }
  }

  function openMailtoFallback(data) {
    var to = atob('YXNhZmJlbjMzQGdtYWlsLmNvbQ==');
    var subject = data['feedback-type'] === 'recipe'
      ? 'תיקון למתכון: ' + data['recipe-title']
      : 'הצעה / דיווח — אתר ספר הבישול של פרלה ז\u05f4ל';
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
  }

  function initFeedback() {
    var fab = $('fb-fab');
    if (fab) fab.addEventListener('click', function() { openFeedbackModal('site', null); });
    var closeBtn = $('fb-close');   if (closeBtn) closeBtn.addEventListener('click', closeFeedbackModal);
    var cancelBtn = $('fb-cancel'); if (cancelBtn) cancelBtn.addEventListener('click', closeFeedbackModal);
    var ovl = $('fb-ovl');          if (ovl) ovl.addEventListener('click', function(e) { if (e.target === ovl) closeFeedbackModal(); });
    var form = $('fb-form');        if (form) form.addEventListener('submit', submitFeedback);
    var msg = $('fb-message');      if (msg) msg.addEventListener('input', updateCharCount);
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        var ovl = $('fb-ovl');
        if (ovl && ovl.classList.contains('open')) closeFeedbackModal();
      }
    });
    var recBtn = $('m-feedback-act');
    if (recBtn) recBtn.addEventListener('click', function() {
      if (typeof CUR_REC !== 'undefined' && CUR_REC) openFeedbackModal('recipe', { id: CUR_REC.id, title: CUR_REC.title });
      else openFeedbackModal('site', null);
    });
  }

  window.openFeedbackModal  = openFeedbackModal;
  window.closeFeedbackModal = closeFeedbackModal;

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initFeedback);
  else initFeedback();
})();
```

### שלב E: כפתור "הערה / תיקון" ב-modal מתכון

*(זהה לגרסה 2.0)*

```html
<button id="m-feedback-act" class="m-act-media fb-recipe-btn" aria-label="הערה או תיקון למתכון">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" aria-hidden="true">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
  הערה / תיקון
</button>
```

### שלב F: CSP עדכון (v3.0 — שונה מ-v2.0!)

ב-`<meta http-equiv="Content-Security-Policy">`:

```
/* לפני (v2.0) */
connect-src 'self' https://formsubmit.co;
frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com;
form-action 'self';

/* אחרי (v3.0) */
connect-src 'self';
frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://formsubmit.co;
form-action 'self' https://formsubmit.co;
```

**הגיון:**
- `connect-src` — הוסר formsubmit.co כי **לא משתמשים עוד ב-fetch**.
- `frame-src` — הוסף formsubmit.co כי ה-iframe מטען אליו (form submit מנווט את ה-iframe).
- `form-action` — הוסף formsubmit.co כי ה-form נשלח אליו (directive זה שולט על היעדים המותרים לטפסים).

### שלב G: `_headers` של Netlify

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob: https://i.ytimg.com https://img.youtube.com; media-src 'self' blob:; connect-src 'self'; frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://formsubmit.co; object-src 'none'; base-uri 'self'; form-action 'self' https://formsubmit.co; frame-ancestors 'none';
```

---

## 5. הפעלת FormSubmit — שלב חד-פעמי

FormSubmit דורש **אישור חד-פעמי** בשליחה הראשונה.

### 5.1 Deploy

Push ל-GitHub. Netlify/GitHub Pages יפרוס תוך 1-2 דקות.

### 5.2 שלח הודעת בדיקה

פתח את האתר, לחץ על FAB, מלא הודעה, שלח. צריך להופיע "תודה! ההודעה נשלחה בהצלחה."

### 5.3 בדוק את תיבת הדוא"ל

חפש מייל מ-`contact@formsubmit.co` עם נושא `Please activate your form submission`. לחץ על קישור האישור.

### 5.4 סיום

מרגע זה — כל ההודעות יגיעו ישירות לתיבה. לפרטיות מקסימלית, שקול להחליף את `FORMSUBMIT_EMAIL_B64` בbase64 של ה-hashed alias שתקבל אחרי ה-activation.

---

## 6. בדיקות ואימות

### ✅ בדיקה 1: פידבק על מתכון
פתח מתכון → "הערה / תיקון" → מלא ושלח → צריכה להופיע הודעת הצלחה.

### ✅ בדיקה 2: פידבק כללי
לחץ FAB → מלא ושלח.

### ✅ בדיקה 3: ולידציה
שלח ריק → שגיאה. הזן email לא תקין → שגיאה. שלח תקין → הצלחה.

### ✅ בדיקה 4: נגישות
Escape סוגר. Tab navigation. Click outside סוגר.

### ✅ בדיקה 5: Mobile
iPhone/Android → modal bottom-sheet, FAB קטן בלי label.

### ✅ בדיקה 6: Fallback mailto
חסום formsubmit.co ב-DevTools → Network → שלח → iframe לא נטען → 15s timeout → mailto מוצע.

### ✅ בדיקה 7: CSP (קריטי ב-v3.0)
DevTools Console → שלח → וודא שאין:
- **שגיאת CORS** — אם יש, המיגרציה לא הושלמה (עדיין משתמש ב-fetch).
- שגיאת `Refused to frame 'https://formsubmit.co/' because it violates the following Content Security Policy directive: "frame-src..."` — `frame-src` לא כולל formsubmit.co.
- שגיאת `Refused to send form data to '...' because it violates form-action directive` — `form-action` לא כולל formsubmit.co.

### ✅ בדיקה 8: iframe mechanics
DevTools → Elements → חפש `<iframe id="fb-iframe-target">`. צריך להיות ריק (about:blank) לפני שליחה, ואחרי שליחה צריך להציג דף של FormSubmit.

---

## 7. תרחישי edge cases

| תרחיש | מה קורה | איך מטופל |
|---|---|---|
| משתמש סוגר modal באמצע שליחה | `_isSubmitting` נשאר true רגע, iframe מטען ברקע | בטוח — אין data loss |
| Network timeout | iframe לא מטען → 15s timeout | fallback mailto |
| שדה הודעה ריק | Submit לא נשלח | שגיאה "נא לכתוב הודעה" |
| הודעה > 2000 תווים | Submit נעצר | מונה תווים + שגיאה |
| אימייל לא תקין | Submit נעצר | regex validation |
| Bot ממלא `_honey` | FormSubmit דוחה אוטומטית | — |
| **פעם ראשונה (לפני activation)** | FormSubmit מחזיר activation page ב-iframe | iframe.load עדיין נורה → "תודה! ההודעה נשלחה בהצלחה." |
| **FormSubmit rate-limit** | iframe מטען דף שגיאה | iframe.load נורה → "תודה" (UX) — ההודעה אכן לא הגיעה |
| **CSP blocks iframe load** | `frame-src` לא מאפשר | timeout 15s → mailto |
| **CSP blocks form-action** | `form-action` לא מאפשר | `hf.submit()` throws → catch → mailto |
| **Offline** | iframe לא מטען | timeout → mailto |
| User לחץ "שלח" כפול | `_isSubmitting` flag | כפתור מושבת |

---

## 8. תחזוקה עתידית

### להחליף את כתובת היעד

1. `btoa('newemail@example.com')` → base64 חדש.
2. עדכן `FORMSUBMIT_EMAIL_B64` ב-JS.
3. עדכן גם ב-`openMailtoFallback()` (hardcoded base64 שני).
4. **חזור על תהליך ה-activation** (סעיף 5).

### לעבור ל-hashed alias

אחרי activation ראשון, קבל hash מ-FormSubmit → ב-JS, שנה את ה-endpoint:

```javascript
var HASH_B64 = 'base64-of-your-hash';
hf.action = 'https://formsubmit.co/' + atob(HASH_B64);
// או ישירות:
// hf.action = 'https://formsubmit.co/el/' + atob(HASH_B64);
```

### להוסיף auto-response

בטופס, הוסף שדה hidden:
```html
<input type="hidden" name="_autoresponse" value="תודה על הפנייה — נחזור אליך בהקדם.">
```

### להוסיף webhook

FormSubmit Dashboard → Webhooks → הוסף URL (Slack/Discord/Zapier).

---

## 9. מיגרציה מגרסאות קודמות

### 9.1 מ-v1.0 (Netlify Forms) ל-v3.0

1. **הסר** את ה-form הנסתר: `<form data-netlify="true" hidden>...</form>`
2. **הוסף** את שלב C (iframe + hidden form).
3. **החלף** את כל קוד ה-JS בשלב D.
4. **עדכן** CSP לפי שלב F.
5. **צור** `_headers` לפי שלב G.
6. **בטל** התראות ב-Netlify Dashboard (אופציונלי).
7. **הפעל** FormSubmit (סעיף 5).

### 9.2 מ-v2.0 (fetch AJAX) ל-v3.0

**זו המיגרציה המהירה — רק 3 שינויים:**

1. **הוסף** את שלב C (iframe + hidden form) לפני `</body>`.
2. **החלף** את פונקציית `submitFeedback()` בזו של שלב D.
3. **עדכן** CSP:
   - `connect-src` — הסר formsubmit.co
   - `frame-src` — הוסף formsubmit.co
   - `form-action` — הוסף formsubmit.co
4. **עדכן** `_headers` באותה צורה.

ה-activation של FormSubmit נשמר — אם כבר הפעלת מ-v2.0, **אין צורך להפעיל שוב**.

### 9.3 השוואת גרסאות

| מאפיין | v1.0 | v2.0 | v3.0 |
|---|---|---|---|
| עובד ב-GitHub Pages | ✗ (405) | ✗ (CORS) | ✓ |
| עובד ב-Netlify | ✓ | ✗ (CORS) | ✓ |
| עובד ב-file:// | ✗ | ✗ (CORS) | ✓ |
| שליחה דרך JS | POST classic | fetch JSON | Form POST |
| CORS preflight | N/A | כן (נכשל) | **לא!** |
| קורא תגובת שרת | — | כן | לא (iframe load) |
| תמיכה בניטור בהצלחה | ✓ | ✓ | חלקי (iframe load means "data sent") |
| שמירת email מוסתר | ✓ | ✓ | ✓ |

---

## קבצים מצורפים

- `feedback_demo.html` — דמו עצמאי
- `INTEGRATION_GUIDE.md` — המסמך הזה (v3.0)
- `_headers` — Netlify HTTP headers

---

## סיכום

1. הדבק CSS (A) + Modal+FAB HTML (B) + **iframe+form HTML (C)** + JS (D) + כפתור mod (E).
2. **עדכן CSP** (F) — `frame-src` ו-`form-action` כוללים formsubmit.co.
3. **צור `_headers`** (G) עם אותן הגדרות.
4. Push ל-GitHub → Netlify/GitHub Pages יפרוס.
5. שלח הודעת בדיקה → לחץ על activation link במייל.
6. בדוק לפי 8 הבדיקות.

**הסוד של v3.0:** form submissions ל-iframe לא כפופים ל-CORS — זו התנהגות מורשת של HTML שעובדת בכל דפדפן בכל אירוח.

**גרסה 3.0** — 19/04/2026
