# CHANGELOG — גרסה 6.3 — 19/04/2026

**ספר הבישול של משפחת בן הראש ז״ל — סיכום שינויי סשן 19 אפריל 2026**

---

## סקירה כללית

| מאפיין | ערך |
|---|---|
| נקודת התחלה | v6.2 (18/04/2026) |
| נקודת סיום | v6.3 (19/04/2026) |
| גודל `index.html` לפני | 377,689 bytes |
| גודל `index.html` אחרי | 384,572 bytes |
| שינוי נטו | +6,883 bytes |
| מספר שינויים | 7 גושים עיקריים |
| בדיקות אימות | 41/41 עברו |

---

## תוכן

1. [UI Enlargement — סיבוב שני](#1-ui-enlargement--סיבוב-שני)
2. [עדכוני תוכן — Hero Title](#2-עדכוני-תוכן--hero-title)
3. [עדכוני תוכן — Hero Tagline](#3-עדכוני-תוכן--hero-tagline)
4. [עדכוני תוכן — About Memorial](#4-עדכוני-תוכן--about-memorial)
5. [עדכוני תוכן — About H2](#5-עדכוני-תוכן--about-h2)
6. [מיגרציית פידבק — Netlify Forms → FormSubmit.co](#6-מיגרציית-פידבק--netlify-forms--formsubmitco)
7. [שחזור כפתור PWA Install](#7-שחזור-כפתור-pwa-install)
8. [קבצים שהתעדכנו](#8-קבצים-שהתעדכנו)
9. [פעולות נדרשות מהמשתמש](#9-פעולות-נדרשות-מהמשתמש)
10. [כל המסמכים שהתעדכנו](#10-כל-המסמכים-שהתעדכנו)

---

## 1. UI Enlargement — סיבוב שני

הגדלות עקביות לכל רכיבי הניווט כדי ליצור hierarchy ברור ונוחות קריאה וקליק.

### 1.1 Search bar (גמיש במקום קבוע)

| רכיב | לפני (v6.2) | אחרי (v6.3) |
|---|---|---|
| `.hdr-search width` | `320px` (קבוע) | `flex: 1; max-width: 640px; min-width: 220px` (**גמיש!**) |
| `.hdr-search padding` | `.5rem 1.1rem` | `.65rem 1.3rem` |
| `.hdr-search gap` | `.5rem` | `.6rem` |
| `#srch width` | `320px` | `100%; min-width: 0` |
| `#srch font-size` | `.95rem` | `1.05rem` |

**תוצאה:** שורת החיפוש ממלאת את כל השטח הפנוי (עד 640px) ומרגישה "נכון" בכל רזולוציה.

### 1.2 תפריט ראשי (Main Nav)

| רכיב | לפני | אחרי |
|---|---|---|
| `--nav-h` | `54px` | `60px` |
| `.nb font-size` | `1rem` | `1.1rem` |
| `.nb font-weight` | `600` | `700` |
| `.nb padding` | `0 1.3rem` | `0 1.5rem` |
| `.nb gap` | `.4rem` | `.5rem` |
| `.nb color` | `rgba(245,236,215,.65)` | `rgba(245,236,215,.72)` |
| `.nb border-bottom` | `2px solid transparent` | `3px solid transparent` |
| `.nb-cnt font-size` | `.78rem` | `.9rem` |
| `.nb-cnt font-weight` | `600` | `700` |
| `.nb-cnt padding` | `.22rem .6rem` | `.26rem .7rem` |
| `.nb-cnt background` | `rgba(196,147,10,.22)` | `rgba(196,147,10,.25)` |
| `.nb-arr font-size` | `.75rem` | `.88rem` |
| `.nb-arr opacity` | `.7` | `.75` |

### 1.3 צ'יפים בתת-תפריט (Panel Chips)

| רכיב | לפני | אחרי |
|---|---|---|
| `.pc font-size` | `1rem` | `1.08rem` |
| `.pc padding` | `.55rem 1.3rem` | `.72rem 1.5rem` |
| `.pc gap` | `.5rem` | `.55rem` |
| `.pc color` | `rgba(245,236,215,.75)` | `rgba(245,236,215,.8)` |
| `.pc-cnt font-size` | `.82rem` | `.92rem` |
| `.pc-cnt font-weight` | `500` | `600` |
| `.pc-cnt opacity` | `.7` | `.75` |

### 1.4 כותרות קטגוריה (Accordion Headers) — הבולטות ביותר

| רכיב | לפני | אחרי |
|---|---|---|
| `.acc-hdr font-size` | `1rem` | `1.18rem` |
| `.acc-hdr padding` | `.55rem 1.3rem` | `.8rem 1.7rem` |
| `.acc-hdr gap` | `.5rem` | `.6rem` |
| `.acc-hdr border-alpha` | `.28` | `.35` |

### 1.5 Panel containers

| רכיב | לפני | אחרי |
|---|---|---|
| `.acc-body gap` | `.55rem` | `.7rem` |
| `.acc-body padding` | `.8rem 1rem` | `1rem 1.3rem` |
| `.acc-body margin-top` | `.4rem` | `.55rem` |
| `.nav-panel-inner padding` | `1.1rem 1.5rem 1.3rem` | `1.4rem 1.8rem 1.6rem` |
| `.nav-panel-inner layout` | *(no flex)* | `display:flex; flex-direction:column; gap:.8rem` |

---

## 2. עדכוני תוכן — Hero Title

### 2.1 היסטוריית שינויים בסשן
- **התחלה (v6.2):** `המטבח של משפחת בן הראש המורחבת`
- **שינוי ראשון:** `המטבח של משפחת בן הראש (ארוש\הרוש) ועוד...` (עם `.hero-h1-more` בלבן)
- **שינוי סופי (v6.3):** `המטבח של משפחת בן הראש (ארוש\הרוש)` (הסרת "ועוד...")

### 2.2 מיקומי עדכון
- **HTML** (line 1461): `<h1 class="hero-h1">`
- **i18n** (line 6461): `hero_title_em` — HE + EN
- **applyLang** (line 6617): `innerHTML` builder — פוושט בהסרת `hero_title_more`

### 2.3 שינויים במסגרת הניסוי
הוסרו לחלוטין אחרי הניסוי:
- CSS selector: `.hero-h1-more { color: #ffffff }` ו-`html.light .hero-h1-more { color: #2a1508 }`
- i18n key: `hero_title_more`
- HTML span: `<span class="hero-h1-more">ועוד...</span>`

### 2.4 תרגום לאנגלית
- לפני: `The Kitchen of the Extended Ben-Harrosh Family`
- אחרי: `The Kitchen of the Ben-Harrosh / Ben-Arrush Family`

---

## 3. עדכוני תוכן — Hero Tagline

### 3.1 השינוי
- **לפני:** `לזכרם של פרלה ופנחס בן הראש — טעמים שמעלים זכרונות שחשבנו שכבר שכחנו...`
- **אחרי:** `לזכרם של פרלה ופנחס בן הראש ז״ל — טעמים שמעלים זכרונות שכמעט שכחנו...`

### 3.2 מה השתנה
1. **הוסף ז״ל** — שימוש ב-Hebrew gershayim U+05F4 (״) במקום `"` רגיל, לעקביות עם 13 מופעים קיימים באתר.
2. **פושט "שחשבנו שכבר שכחנו" → "שכמעט שכחנו"** — הטקסט החדש קולח יותר, פחות דרמטי, ומעביר בדיוק אותו רגש.

### 3.3 מיקומי עדכון
- **HTML** (line 1464): `<p class="hero-tagline">`
- **i18n** (line 6465): `hero_tagline` — HE + EN

### 3.4 תרגום לאנגלית
- לפני: `In memory of Perla & Pinchas Ben-Harrosh — flavors that awaken memories we thought were lost...`
- אחרי: `In memory of Perla & Pinchas Ben-Harrosh z"l — flavors that awaken memories we almost forgot...`

---

## 4. עדכוני תוכן — About Memorial

### 4.1 השינוי
- **לפני:** `...שזכרונם יהיה לברכה וגאווה לדורי דורות דרך הטעם המעלה זכרונות שחשבנו שכבר שכחנו...`
- **אחרי:** `...שזכרונם יהיה לברכה וגאווה הלאה לדורי דורות דרך הטעם המעלה זכרונות שכמעט שכחנו...`

### 4.2 מה השתנה
1. **הוסף "הלאה" לפני "לדורי דורות"** — מדגיש את ערך ההמשכיות הבין-דורית.
2. **"שחשבנו שכבר שכחנו" → "שכמעט שכחנו"** — עקביות עם ה-tagline.

### 4.3 מיקומי עדכון (3 מקומות!)
- **HTML** (line 1480): `<p class="about-memorial">`
- **i18n** (line 6474): `about_memorial` — HE + EN
- **JSON-LD** (line 1123): `"description"` field — לSEO של גוגל ושיתופים ברשתות

### 4.4 תרגום לאנגלית
- לפני: `...a source of pride for generations, through flavors that awaken memories we thought were lost...`
- אחרי: `...a source of pride onward for generations to come, through flavors that awaken memories we almost forgot...`

---

## 5. עדכוני תוכן — About H2

### 5.1 השינוי
- **לפני:** `פרלה ופנחס בן הראש ז״ל — המשפחה שיצבה מטבח`
- **אחרי:** `פרלה ופנחס בן הראש ז״ל — המשפחה שעיצבה מטבח שלם שיזכר ויתבשל הלאה לדורי דורות`

### 5.2 מה השתנה
1. **תיקון שורש** — `שיצבה` → `שעיצבה` (שורש ע+צ+ב, "לעצב").
2. **הרחבה משמעותית** — "מטבח" → "מטבח שלם שיזכר ויתבשל הלאה לדורי דורות", מדגיש את ערך ההמשכיות.

### 5.3 מיקומי עדכון
- **HTML** (line 1477): `<h2 class="about-h">`
- **i18n** (line 6470): `about_h` — HE + EN

### 5.4 תרגום לאנגלית
- לפני: `Perla & Pinchas Ben-Harrosh z"l — The family that shaped a kitchen`
- אחרי: `Perla & Pinchas Ben-Harrosh z"l — The family that shaped an entire kitchen, to be remembered and cooked onward for generations to come`

---

## 6. מיגרציית פידבק — Netlify Forms → FormSubmit.co

### 6.1 הבעיה שהתגלתה

האתר מתארח ב-**שני מקומות** (Netlify + GitHub Pages). Netlify Forms עובד רק במקור Netlify שלו. ב-GitHub Pages (שרת סטטי), POST מחזיר `405 Method Not Allowed`.

**לוג הקונסול:**
```
asafben33.github.io/:1 Failed to load resource: the server responded with a status of 405 (Method Not Allowed)
```

### 6.2 הפתרון: FormSubmit.co

שירות form-to-email חיצוני ב-AJAX שעובד מכל מקור.

### 6.3 שינויים קודיים

| שינוי | תיאור |
|---|---|
| **הסרה** | טופס נסתר `<form name="perla-feedback" data-netlify="true" hidden>` עם 9 שדות (~859 bytes) |
| **הוספה** | `var FORMSUBMIT_EMAIL_B64 = 'YXNhZmJlbjMzQGdtYWlsLmNvbQ==';` (בסיס 64 של asafben33@gmail.com) |
| **שכתוב** | `submitFeedback()` — מ-POST form-urlencoded ל-`/` → POST JSON ל-`https://formsubmit.co/ajax/{email}` |
| **`<meta>` CSP** | `connect-src 'self';` → `connect-src 'self' https://formsubmit.co;` |
| **`<meta>` CSP** | הסרת `frame-ancestors 'none';` (הדפדפן מתעלם ממנו ב-meta) |
| **`_headers`** | `connect-src 'self' https://formsubmit.co;` |
| **`_headers`** | `form-action 'self' https://formsubmit.co;` |
| **`_headers`** | `frame-ancestors 'none';` (רק כאן, לא ב-meta) |

### 6.4 payload של FormSubmit

```javascript
{
  _subject:  'תיקון למתכון: X' | 'הצעה / תקלה...',
  _template: 'table',          // פורמט מייל בטבלה
  _captcha:  'false',          // AJAX — captcha disabled
  _honey:    '',                // honeypot (JSON property)
  name, email, message,
  type, recipe_id, recipe_title,
  page_url, user_agent
}
```

### 6.5 זרימת Activation חד-פעמית

1. שליחה ראשונה → FormSubmit מחזיר `success: "false"` + activation message.
2. FormSubmit שולח מייל activation ל-asafben33@gmail.com מ-`contact@formsubmit.co`.
3. המשתמש לוחץ על קישור האישור.
4. מאותו רגע — כל ההודעות הבאות מגיעות רגיל.
5. ה-UX מטפל בזה באלגנטיות: "תודה! ההודעה נקלטה בהצלחה."

### 6.6 Fallback ללא שינוי

אם fetch נכשל (רשת/CSP/offline/FormSubmit down) — `openMailtoFallback(mailtoData)` פותח email client עם subject + body מוכנים.

---

## 7. שחזור כפתור PWA Install

הכפתור היה קיים בסשנים קודמים, נמחק ברגע כלשהו, ושוחזר במלואו.

### 7.1 HTML (כרכיב ראשון ב-`.hdr-tools`)

```html
<button id="pwa-install-btn" class="hdr-btn hdr-btn-install"
        aria-label="התקן אפליקציה" title="התקן אפליקציה"
        data-i18n-label="pwa_label" data-i18n-aria="pwa_aria"
        data-i18n-title="pwa_title" style="display:none">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
       stroke-linejoin="round" aria-hidden="true">
    <polyline points="8 17 12 21 16 17"/>
    <line x1="12" y1="3" x2="12" y2="21"/>
  </svg>
  <span class="pwa-label" data-i18n="pwa_label">התקן</span>
</button>
```

### 7.2 CSS (כולל @keyframes pwa-pulse)

```css
.hdr-btn-install {
  display: flex; align-items: center; gap: .4rem;
  padding: .45rem .9rem;
  background: rgba(196,147,10,.2);
  border: 1px solid rgba(196,147,10,.45);
  border-radius: 100px;
  color: var(--c-gold-l);
  font-family: inherit; font-size: .88rem; font-weight: 700;
  cursor: pointer;
  transition: background var(--t-fast), border-color var(--t-fast), transform var(--t-fast);
  animation: pwa-pulse 3s ease-in-out infinite;
}
.hdr-btn-install:hover {
  background: rgba(196,147,10,.32);
  border-color: rgba(196,147,10,.6);
  transform: translateY(-1px);
  animation: none;
}
.hdr-btn-install:active { transform: translateY(0); }
.hdr-btn-install svg { flex-shrink: 0; display: block; }
.pwa-label { font-family: inherit; white-space: nowrap; }
@keyframes pwa-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(196,147,10,.35); }
  50%      { box-shadow: 0 0 0 6px rgba(196,147,10,.04); }
}
html.light .hdr-btn-install {
  background: rgba(196,147,10,.15);
  border-color: rgba(196,147,10,.45);
  color: #8a5a20;
}
html.light .hdr-btn-install:hover { background: rgba(196,147,10,.25); }
@media (prefers-reduced-motion: reduce) {
  .hdr-btn-install { animation: none; }
}
```

### 7.3 JavaScript (IIFE לפני </body>)

לוגיקה מלאה כולל:
- `beforeinstallprompt` listener — שומר event + מציג כפתור
- `appinstalled` listener — מסתיר כפתור + localStorage
- Click handler — `prompt.prompt()` או `alert()` ל-iOS
- Standalone detection — מסתיר אם כבר מותקן
- iOS fallback — מציג כפתור אחרי 1.5s (כי iOS לא יורה beforeinstallprompt)
- localStorage `'perla_pwa_dismissed'` — זוכר אם המשתמש דחה

### 7.4 i18n (3 מפתחות חדשים)

```javascript
pwa_label:  {he:'התקן',           en:'Install'},
pwa_title:  {he:'התקן אפליקציה',   en:'Install app'},
pwa_aria:   {he:'התקן אפליקציה',   en:'Install app'},
```

### 7.5 מתי הכפתור יופיע?

| דפדפן / מצב | התנהגות |
|---|---|
| Chrome / Edge / Brave (Win/Mac/Android) | יופיע אחרי PWA criteria (manifest + sw + https) |
| Firefox | דומה ל-Chrome |
| Safari (macOS) | לא תומך — לא יופיע |
| Safari (iOS/iPadOS) | **יופיע תמיד** אחרי 1.5s, עם הוראות ידניות |
| אחרי התקנה | **לא יופיע** (standalone detection) |
| אחרי שמשתמש דחה | **לא יופיע** (localStorage) |

---

## 8. קבצים שהתעדכנו

| קובץ | לפני | אחרי | שינוי |
|---|---|---|---|
| `index.html` | 377,689 bytes | 384,572 bytes | +6,883 |
| `HLD_Perla_CookingBook.md` | 18,970 chars | 28,315 chars | +9,345 |
| `LLD_Perla_CookingBook.md` | 53,709 chars | 67,355 chars | +13,646 |
| `INTEGRATION_GUIDE.md` | 28,765 bytes (v1.0) | ~23,000 bytes (v2.0) | overwrite |
| `CLAUDE.md` | 2,917 bytes | ~5,600 bytes | +2,700 |
| `README.md` | 11,601 bytes | ~16,500 bytes | +4,900 |
| `CHANGELOG_19-04-2026_v6.3.md` | — | חדש | — |

---

## 9. פעולות נדרשות מהמשתמש

### 9.1 Git commit + push

בצע ב-PowerShell אחד-אחד:

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```

```powershell
Copy-Item index.html index.html.backup_before_v63_session
```

החלף את `index.html` בגרסה מ-`/mnt/user-data/outputs/`.

```powershell
git add index.html _headers HLD_Perla_CookingBook.md LLD_Perla_CookingBook.md INTEGRATION_GUIDE.md CLAUDE.md README.md CHANGELOG_19-04-2026_v6.3.md
```

```powershell
git commit -m "v6.3: UI enlarge + FormSubmit migration + PWA button + content updates + docs"
```

```powershell
git push origin main
```

### 9.2 הפעלת FormSubmit (חד-פעמי!)

1. פתח את האתר החי אחרי ה-deploy.
2. לחץ על FAB שמאלי-תחתון ("הצעות ודיווח").
3. מלא הודעת בדיקה → לחץ "שליחה".
4. צריך להופיע "תודה! ההודעה נקלטה בהצלחה."
5. היכנס ל-`asafben33@gmail.com` → חפש מייל מ-`contact@formsubmit.co`.
6. לחץ על קישור האישור במייל.
7. מאותו רגע כל ההודעות מגיעות רגיל.

### 9.3 בדיקות נוספות (אופציונלי)

- **PWA Install** — פתח ב-Chrome, בדוק שכפתור "התקן" מופיע (עם pulse animation).
- **Console** — בדוק שאין שגיאות CSP.
- **Mobile** — בדוק ב-iPhone שהכפתור "התקן" מופיע אחרי 1.5 שניות.

---

## 10. כל המסמכים שהתעדכנו

### 10.1 HLD_Perla_CookingBook.md → v6.3

**סעיפים חדשים/מעודכנים:**
- Header: גרסה 6.0 → 6.3, dedication text updated
- Section 9 (Feedback): שכתוב מלא ל-FormSubmit.co עם 9 תת-סעיפים
- Section 10 (CSP): עדכון + new 10.2 `_headers` + 10.4 email obfuscation
- Section 11.3: "Netlify Forms setup" → "FormSubmit activation"
- Section 14: הוסף 14.5 (stability fixes v6.1/v6.2), 14.6 (UI enlarge), 14.7 (FormSubmit), 14.8 (content), 14.9 (PWA)
- Section 15: doc map version bump

### 10.2 LLD_Perla_CookingBook.md → v6.3

**סעיפים מעודכנים:**
- Header + TOC
- Section 3.1 Header: .hdr-search flex, #srch width 100%, new .hdr-btn-install + @keyframes
- Section 3.2 Navigation: all v6.3 sizes (--nav-h 60px, .nb 1.1rem/700, .acc-hdr 1.18rem)
- Section 4.4 (Netlify form): סומן כ"הוסר ב-v6.3"; new 4.5 PWA IDs
- Section 5.8-5.11: שכתוב מלא ל-FormSubmit + new 5.12 PWA JS
- Section 15 CSP: 15.1 meta / 15.2 _headers / 15.3 blocking table
- Section 17.5 Error handling: FormSubmit scenarios
- **Section 19 NEW**: שינויי v6.0 → v6.3 (UI enlarge 2 rounds table, FormSubmit migration, Content updates, PWA restored, JSON-LD SEO, File sizes)
- Section 20 NEW: doc map

### 10.3 INTEGRATION_GUIDE.md → v2.0

**שכתוב מלא מ-Netlify Forms ל-FormSubmit.co:**
- כל הסעיפים עודכנו
- שלב C (JavaScript) שוכתב מחדש עם קוד FormSubmit מלא
- שלבים חדשים: E (CSP update) + F (_headers)
- סעיף 5 שוכתב ל-FormSubmit activation flow
- **סעיף 9 חדש** — מיגרציה מ-v1.0 ל-v2.0 (6 תת-סעיפים)

### 10.4 CLAUDE.md → v6.3

**עודכן:**
- גרסה ותאריך
- רשימת קבצים
- רשימת מסמכי תיעוד
- סעיף מערכת פידבק — FormSubmit instead of Netlify Forms
- סעיף PWA Install Button
- אזהרות
- שינויים אחרונים

### 10.5 README.md → v6.3

**עודכן:**
- Top dedication: ז״ל + "שכמעט שכחנו" + "הלאה לדורי דורות"
- Blockquote: אותה שפה מעודכנת
- Project structure: הוסף _headers, INTEGRATION_GUIDE v2.0, כל ה-CHANGELOGs
- **NEW: Features section** עם 6 תת-חלקים (UX, תרגום, PWA, פידבק, אבטחה, נגישות, מדיה)
- Deployment: הוספת "דרישה חד-פעמית (FormSubmit activation)"
- Documentation section: כל המסמכים בגרסה 6.3
- **NEW: Version history table** (5.0 → 6.3)

### 10.6 CHANGELOG_19-04-2026_v6.3.md (חדש)

המסמך הזה — סיכום מלא של כל השינויים בסשן.

---

## סיכום כללי

הסשן הזה השלים את **v6.3** עם דגש על:

1. **נוחות קריאה** — UI enlargement סיבוב שני (search גמיש, nav 60px, acc-hdr 1.18rem).
2. **שירות פידבק עובד** — מיגרציה ל-FormSubmit.co פותרת את ה-405 ב-GitHub Pages.
3. **PWA מלא** — כפתור התקנה בולט משוחזר, עם pulse animation + iOS fallback.
4. **תוכן משופר** — 4 עדכוני טקסט עם ניסוחים מעודכנים (ז״ל, "שכמעט שכחנו", "הלאה לדורי דורות", "המשפחה שעיצבה מטבח שלם").

**פעולה חד-פעמית נדרשת:** הפעלת FormSubmit אחרי ה-deploy (סעיף 9.2).

---

**גרסה 6.3** — 19 אפריל 2026
*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
*"האוכל שלה — הסיפור שלנו"*
