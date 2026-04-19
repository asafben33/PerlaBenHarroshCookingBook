# CHANGELOG — v8.0: השלמת תחזוקה (i18n + light theme + SEO + print)

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 19/04/2026 — סוף לילה (אחרי v7.9)
**גרסה:** 8.0 (גרסת ניקיון/תחזוקה אחרי כל ה-v7.x)

---

## הבקשה

> תמשיך לעבוד ביסודיות ובמקצועיות על מה שעוד נשאר לבצע במסמכים PLAN_v7_0_HEBREW/ENGLISH

---

## מה בוצע (4 משימות)

### 1. i18n — חיווט מלא של תפריט העדות לאנגלית

**הבעיה:** ה-DICT הכיל 21 מפתחות חדשים מ-v7.6, אבל הם לא היו מחוברים ל-`_NAV_I18N` (המיפוי תווית-עברית→מפתח-i18n שמשמש את `applyLang('en')` כדי לתרגם את ה-DOM). תוצאה: לחיצה על EN לא תרגמה את "מרוקו\\ספרד", "מאכלי חגים" וכל פריטי v7.x החדשים.

**הפתרון:** הרחבת `_NAV_I18N` עם 8 mappings חדשים, והוספת 5 entries חסרים ל-DICT:

```javascript
// _NAV_I18N (index.html ~12055) — additions
'מרוקו\\ספרד':'nav_morocco_span',                    // v7.9
'כל מתכוני מרוקו וספרד':'nav_morocco_span_all',      // v7.9
'ספרד (אנדלוסי)':'nav_span_andalusi',                // v7.9
'מאכלי חגים':'community_holidays_folder',            // v7.4
'מאכלים מסורתיים לעדה':'community_traditional',      // v7.4
'תבשילי ירקות':'nav_veg_dishes',                     // v7.0
'כל מתכוני החגים':'morocco_all_holidays',            // v7.8
'מרוקו':'nav_morocco', 'עדות ישראל':'nav_communities', 'חגים':'nav_holidays'
```

```javascript
// DICT (index.html ~11971) — new entries
nav_morocco_span:     {he:'מרוקו\\ספרד', en:'Morocco / Spain'},
nav_morocco_span_all: {he:'כל מתכוני מרוקו וספרד', en:'All Morocco & Spain Recipes'},
nav_span_andalusi:    {he:'ספרד (אנדלוסי)', en:'Spain (Andalusian)'},
nav_veg_dishes:       {he:'תבשילי ירקות', en:'Vegetable Dishes'},
morocco_all_holidays: {he:'כל מתכוני החגים', en:'All Holiday Recipes'},
```

עכשיו לחיצה על EN בתפריט מתרגמת את **כל** פריטי התפריט, כולל פריטי v7.x החדשים.

### 2. Light theme — Overrides עבור v7.x classes שלא היו

**הבעיה:** v7.0 → v7.9 הוסיפו classes חדשים (`.hdr-brand-v7`, `.hero-cta-primary`, `.pc-comm-hol:hover`, `.pc-empty`) — אבל רק 2 מהם קיבלו `html.light` overrides. בlight theme, brand title הופיע מטושטש ו-pc-comm-hol hover לא בלט.

**הפתרון:** הוספת 7 light theme overrides ב-index.html ~שורה 451:

```css
html.light .hdr-brand-v7 .hdr-brand-title { color: #6e3d0a; }
html.light .hdr-brand-v7 .hdr-brand-count { color: rgba(74,42,20,.65); }
html.light .pc-comm-hol {
  background: rgba(184,66,35,.06);
  border-color: rgba(184,66,35,.30);
}
html.light .pc-comm-hol:hover {
  background: rgba(184,66,35,.12);
  border-color: rgba(184,66,35,.55);
  color: #6e2410;
}
html.light .pc-comm-hol.pc-empty { opacity: .45; }
html.light .hero-cta-primary {
  background: var(--c-spice);
  color: #fff;
}
html.light .hero-cta-primary:hover { background: #922f18; }
```

הצבעים נבחרו לפי הפלטה הקיימת של light theme (חום-כהה על רקע בז').

### 3. SEO — sitemap.xml + robots.txt חדשים

**הבעיה:** האתר לא הציע sitemap ל-search engines. גם robots.txt לא כיוון אותם ל-sitemap.

**הפתרון:** 2 קבצים חדשים בשורש הפרויקט:

**`sitemap.xml`** (1.5 KB) — מכיל:
- URL ראשי של Netlify + GitHub Pages mirror
- 4 anchor URLs לסקציות עיקריות (#main, #bio, #book-wrapper, #about-redesigned)
- hreflang tags (he/en) ל-multilingual SEO
- priority + changefreq

**`robots.txt`** (158 B):
```
User-agent: *
Allow: /
Sitemap: https://perlabenharrosh-cookingbook.netlify.app/sitemap.xml
```

### 4. Print stylesheet — הרחבה ל-v7.x elements

**הבעיה:** כללי `@media print` הקיימים (משורה 1129) הסתירו אלמנטים מ-v6.x אבל לא מ-v7.x. תוצאה: הדפסה הציגה את brand-v7, hero-cta-row, ועוד אלמנטים שאינם נדרשים בהדפסה של מתכון.

**הפתרון:** הרחבת רשימת ה-selectors בכלל `display: none !important`:

```css
@media print {
  /* existing v6.x rules */
  .hdr, .cat-nav, .nav-panel, #back-top, ...,
  /* v8.0: hide v7.x menu elements + main grid container */
  .hdr-brand-v7, .hero-cta-row, .pc-comm-hol, .pc-empty,
  #main, .main-hidden, #book-wrapper, #about-redesigned,
  .feedback-fab, #pwa-modal-ovl, #pwa-install-btn { display: none !important; }
}
```

---

## בדיקות שעברו

```
✓ Main JS syntax (node -c): OK
✓ data.js syntax: OK (לא נגעתי)
✓ CRLF: 12,990 שורות (100%, 0 lone LF)
✓ 1,054 מתכונים נשמרים
✓ Web3Forms key intact
✓ DICT entry for merged Morocco/Spain
✓ _NAV_I18N mapping complete
✓ Light theme brand override
✓ Light theme hero CTA
✓ Print rules cover v7.x classes
✓ sitemap.xml: 6 URL entries
✓ robots.txt: 158 chars
```

---

## קבצים מצורפים

| קובץ | שינוי | חדש? |
|---|---|---|
| `index.html` | _NAV_I18N + DICT extended, light theme overrides, print rules | עודכן |
| `sitemap.xml` | SEO sitemap עם 6 URLs | **חדש** |
| `robots.txt` | מפנה crawlers ל-sitemap | **חדש** |
| `CLAUDE_md_v8_update.md` | תוספת ל-CLAUDE.md המקורי | **חדש** |
| `PLAN_v7_0_HEBREW.md` | עודכן ל-v8.0 (Roadmap מקוצר) | עודכן |
| `PLAN_v7_0_ENGLISH.md` | עודכן ל-v8.0 (Roadmap מקוצר) | עודכן |

`data.js` **לא השתנה** מ-v7.9.

---

## פריסה

```powershell
cd C:\path\to\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\index.html" ".\index.html" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\sitemap.xml" ".\sitemap.xml" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\robots.txt" ".\robots.txt" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\PLAN_v7_0_HEBREW.md" ".\PLAN_v7_0_HEBREW.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\PLAN_v7_0_ENGLISH.md" ".\PLAN_v7_0_ENGLISH.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CLAUDE_md_v8_update.md" ".\CLAUDE_md_v8_update.md" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_19-04-2026_v8_0_i18n_theme_seo.md" "." -Force
```
```powershell
git add index.html sitemap.xml robots.txt PLAN_v7_0_HEBREW.md PLAN_v7_0_ENGLISH.md CLAUDE_md_v8_update.md CHANGELOG_19-04-2026_v8_0_i18n_theme_seo.md
```
```powershell
git commit -m "v8.0: full i18n wiring + light theme overrides + SEO sitemap + print rules"
```
```powershell
git push origin main
```

---

## מה נשאר ב-Roadmap לאחר v8.0

מ-PLAN_v7_0_HEBREW.md:

### עדיפות גבוהה — דורש מעורבות אסף או המשפחה
1. רענון תיוגי `COMMUNITY_HOLIDAY_TAGS` — בדיקה משפחתית
2. רענון תיוגי `HOLIDAY_TAGS` של מרוקו — בדיקה ידנית

### עדיפות בינונית
3. עדכון תיעוד טכני (CLAUDE.md הטמעה, HLD/LLD רענון)
4. תמונות חסרות (download_images.py)

### עדיפות נמוכה
5. Breadcrumbs
6. Recipe carousel
7. OG images per category
8. Lazy loading + virtualization

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
