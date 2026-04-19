# תוכנית עבודה מפורטת — שלב 1: שיפוץ הדף הראשי

**ספר הבישול של פרלה בן-הראש ז״ל**
**גרסה מתוכננת: 7.0**
**תאריך תכנון: 19/04/2026**

---

## מטרות כוללות

ארבעה שינויים מבניים בדף הראשי, בהתאם למוקאפ שאושר:

1. **Header מאוחד** — כל הכפתורים בשורה אחת
2. **Hero מקוצר** — פחות תוכן, כפתורי CTA ברורים
3. **Bio לפני רשת המתכונים** — סדר גלילה נכון
4. **תפריט ניווט משופר** — 5 קבוצות יציבות + "חגי העדה" לכל עדה

כל השינויים ב-commit אחד גדול (לבקשתך).

---

## לפני שמתחילים — ממצא חשוב מאוד

במהלך בדיקת ה-`data.js` גיליתי דבר שחייבים להבהיר לפני תחילת העבודה:

**ה-HOLIDAY_TAGS הקיים מכיל רק מתכונים של "מטעמי אמא ממרוקו"** (המתכונים שמתחילים ב-`h*`, `hn*`, `hle*` וכו׳). המתכונים של 9 העדות האחרות (עיראק, כורדיסטן, אשכנז, תימן, פרס, בוכרה, טוניסיה, טורקיה, ישראלי) **אינם מתויגים לחגים** כרגע.

משמעות הדבר: אם אנחנו רוצים קבוצת "חגי העדה" תחת כל עדה — **צריך להוסיף תיוג חגים ידני למתכונים של כל עדה**. זה לא נעשה אוטומטית.

### 3 אפשרויות להמשך:

**אפשרות A — תיוג ידני מלא (הכי מדויק, הכי ארוך)**
אתה תספק לי רשימה: "במטבח עיראקי, המתכונים X, Y, Z מוגשים בראש השנה; A, B ב-שבועות..." — ואני אתייג את data.js בהתאם. דרוש ממך זמן ומחקר, או ידע מוקדם מהמשפחה.

**אפשרות B — תיוג חלקי לפי ידע כללי (מהיר, לא שלם)**
אני מתייג לפי ידע כללי על המטבחים (למשל "סופגניות ← חנוכה" בכל עדה; "קניידלעך אשכנזי ← פסח"). ה*סיכון*: מתכון שאצל משפחה מסוימת נהוג לחג אחד — אצל משפחה אחרת לחג אחר. אני אציין בכל תיוג איזה מקור השתמשתי.

**אפשרות C — דחייה של "חגי העדה" לשלב מאוחר יותר**
היום נבנה את המבנה (container) של "חגי העדה" בתפריט עם placeholder ריק. בשלב 2 נמלא את המתכונים בקצב שלך. ככה שלב 1 יושלם מהר ותוכל לראות תוצאות.

**ההמלצה שלי:** אפשרות C לשלב 1, ואפשרות A בעתיד. זה משקף את הכנות שלי — אין לי ידע מקורי על מסורות חגים של 9 עדות שונות, ואני לא רוצה לפברק תיוגים.

**תגיד לי איזה אפשרות אתה מעדיף לפני שאמשיך בקוד.**

---

## קבצים שמושפעים

| קובץ | מצב | תיאור שינוי |
|------|------|-------------|
| `index.html` | שינוי משמעותי | Header חדש, Hero חדש, Bio חדש, CSS חדש |
| `data.js` | שינוי ממוקד בלבד | עדכון `MENU_STRUCTURE` + אם אפשרות A/B: תיוג חגים ב-R[] |
| `pre_en.js` | הוספת תרגומים | טקסטים חדשים באנגלית |
| `manifest.json` | ללא שינוי | — |
| `sw.js` | ללא שינוי | — |
| `about_redesigned.*` | ללא שינוי | — |
| `book_data.js` | ללא שינוי | — |
| `download_images.py` | ללא שינוי | — |

---

## שלב 1.1 — מבנה HTML חדש

### לפני (המצב הנוכחי)
```
<header> = חיפוש + הכפתורים (התקן/נושא/שפה)
<nav>    = תפריט קטגוריות (שורה אחת + drawer)
<section hero> = h1 גדול + סיסמה
<section bio>  = תמונת חתונה + ביוגרפיה מלאה (3 פסקאות)
<section book> = כפתור ״קרא את הספר״ + תוכן נגלל
<section about-redesigned> = הסעיף המלא של ״על שביל האהבה״
<main> = רשת המתכונים
```

### אחרי (הסדר החדש)
```
<header> = שם + ספירה + חיפוש + כפתורים (שורה אחת מאוחדת)
<nav>    = תפריט קטגוריות (5 קבוצות יציבות + drawer משופר)
<section hero> = כותרת + סיסמה + 2 כפתורי CTA (קצר)
<section bio>  = תמונת חתונה + ביוגרפיה (נשאר כמו שהוא!)
<main> = רשת המתכונים (מיד אחרי ה-Bio)
<section book> = כפתור הספר (ללא שינוי)
<section about-redesigned> = ללא שינוי
```

**שים לב:** ה-Bio נשאר במיקומו הנוכחי. המוקאפ הראה אותו "לפני רשת המתכונים" — וזה בדיוק המיקום הנוכחי שלו. ה-main (הרשת) כבר אחרי ה-bio.

---

## שלב 1.2 — CSS חדש

### שינויים ב-Header
```css
/* חדש: שם + ספירה כרכיב יחד */
.hdr-brand-new {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
  flex-shrink: 0;
}
.hdr-brand-title {
  color: var(--c-gold-l);
  font-family: 'Frank Ruhl Libre', serif;
  font-size: 1rem;
  font-weight: 500;
}
.hdr-brand-count {
  color: rgba(237,224,196,.5);
  font-size: .7rem;
}
```

### שינויים ב-Hero
```css
/* המצב הנוכחי: .hero מגיע עם h1 ענק + padding גדול */
/* אחרי: שמירה על אותו עיצוב עם הוספת שורת CTA */
.hero-cta-row {
  display: flex;
  gap: .6rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 1.2rem;
}
.hero-cta-primary {
  background: var(--c-spice);
  color: #fff;
  border: none;
  border-radius: 100px;
  padding: .7rem 1.6rem;
  font-family: inherit;
  font-size: .95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--t-fast);
}
.hero-cta-primary:hover { background: var(--c-spice-d); }
.hero-cta-secondary {
  background: transparent;
  color: var(--c-gold-l);
  border: 0.5px solid rgba(196,147,10,.35);
  border-radius: 100px;
  padding: .7rem 1.6rem;
  font-family: inherit;
  font-size: .95rem;
  cursor: pointer;
}
```

### שינויים ב-Nav
```css
/* החלפת ה-nav-panel הקיים במבנה משופר */
.nav-drawer {
  background: var(--c-deep);
  border-top: 0.5px solid rgba(196,147,10,.15);
  padding: 1rem 1.2rem 1.2rem;
  display: none;
}
.nav-drawer.open { display: block; animation: drawerSlide .2s ease-out; }
@keyframes drawerSlide { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }

.nav-drawer-header {
  display: flex; align-items: baseline; gap: .6rem;
  margin-bottom: .8rem;
}
.nav-drawer-title {
  color: var(--c-gold-l);
  font-size: .88rem; font-weight: 500;
}
.nav-drawer-meta {
  color: rgba(237,224,196,.4);
  font-size: .72rem;
}

.nav-sub-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: .35rem;
}

/* קבוצת "חגי העדה" — מודגשת בצבע אדום-חום */
.nav-holidays-group {
  background: rgba(184,66,35,.1);
  border: 0.5px solid rgba(184,66,35,.35);
  color: #d4603a;
}
.nav-holidays-group:hover {
  background: rgba(184,66,35,.18);
}
```

---

## שלב 1.3 — שינויים ב-JS

### `buildNav()` — שדרוג מלא

הפונקציה הקיימת (שורה ~2723) תעבור שיפוץ משמעותי. הקוד החדש:

```javascript
function buildNav() {
  var bar = document.getElementById('cat-inner');
  if (!bar) return;
  bar.innerHTML = '';

  // 5 רמות עליונות קבועות
  var TOP_GROUPS = [
    { key: 'all',     lbl: 'הכל',         ids: 'all' },
    { key: 'morocco', lbl: 'מרוקו',       ids: ['soups','salads','veg','meat','chick','fish','hol','des'] },
    { key: 'spain',   lbl: 'ספרד',        ids: [/* span IDs */] },
    { key: 'communities', lbl: 'עדות ישראל', ids: ['iraq','kurd','ashk','yem','pers','buk','tun','turk','isr'] },
    { key: 'holidays', lbl: 'חגים',       ids: ['hol'] },
    { key: 'nonkosher', lbl: 'לא כשר',    ids: [/* nk IDs */] }
  ];

  TOP_GROUPS.forEach(function(g) {
    var btn = makeTopButton(g);
    bar.appendChild(btn);
  });
}

function makeTopButton(g) {
  var count = catCnt(g.ids);
  var btn = document.createElement('button');
  btn.className = 'nb-top';
  btn.innerHTML = esc(g.lbl) + ' · <span class="nb-cnt">' + count.toLocaleString() + '</span>';
  btn.addEventListener('click', function(e) {
    e.stopPropagation();
    toggleDrawer(g);
  });
  return btn;
}

function toggleDrawer(group) {
  var drawer = document.getElementById('nav-drawer');
  if (!drawer) return;
  if (ACTIVE_DRAWER === group.key) {
    closeDrawer();
    return;
  }
  renderDrawer(group);
  drawer.classList.add('open');
  ACTIVE_DRAWER = group.key;
}

function renderDrawer(group) {
  var inner = document.getElementById('nav-drawer-inner');
  inner.innerHTML = '';

  // כותרת
  var header = document.createElement('div');
  header.className = 'nav-drawer-header';
  header.innerHTML = '<span class="nav-drawer-title">' + esc(group.lbl) + '</span>' +
                     '<span class="nav-drawer-meta">' + catCnt(group.ids) + ' מתכונים</span>';
  inner.appendChild(header);

  // תת-קבוצות
  var sub = document.createElement('div');
  sub.className = 'nav-sub-grid';

  if (group.key === 'communities') {
    // לעדות ישראל — 9 עדות + לכל עדה פנימה יש "חגי העדה"
    renderCommunitiesDrawer(sub, group);
  } else if (group.key === 'holidays') {
    // לחגים — 10 חגים
    renderHolidaysDrawer(sub);
  } else if (group.key === 'morocco') {
    renderMoroccoDrawer(sub);
  }
  // ... וכו׳

  inner.appendChild(sub);
}

function renderCommunitiesDrawer(container, group) {
  var cuisines = [
    { id: 'iraq', lbl: 'עיראק' },
    { id: 'kurd', lbl: 'כורדיסטן' },
    // ... וכו׳
  ];
  cuisines.forEach(function(c) {
    var btn = makeSubButton(c);
    container.appendChild(btn);
  });

  // חזרה אחרי בחירת עדה — renderCuisineDetail משיך ל-level 2
}

function renderCuisineDetail(cuisineId) {
  // רמה 2: תת-קבוצות של עדה מסוימת
  // כולל קבוצה ייחודית של "חגי העדה" בצבע אדום-חום
  var btn = document.createElement('button');
  btn.className = 'nav-sub nav-holidays-group';
  btn.innerHTML = 'חגי העדה ה' + cuisineAdjective(cuisineId);
  btn.addEventListener('click', function() {
    filterByCuisineHolidays(cuisineId);
  });
}
```

**הערה:** זה pseudocode — הקוד האמיתי יהיה מפורט יותר.

### פונקציית `filterByCuisineHolidays`

פונקציה חדשה שמסננת מתכונים לפי עדה **וגם** לפי תיוג חג:

```javascript
function filterByCuisineHolidays(cuisineId) {
  var recipes = R.filter(function(r) {
    if (r.cat !== cuisineId) return false;
    // בדיקה אם למתכון יש tag של חג
    return r.h || (r.tags && r.tags.some(isHolidayTag));
  });
  // הצגה
  renderGridFromRecipes(recipes);
  setSectionTitle('חגי העדה ה' + cuisineAdjective(cuisineId));
}
```

---

## שלב 1.4 — שינויים ב-`data.js`

### שינוי בלבד ב-MENU_STRUCTURE

המבנה החדש (פסוודו-קוד):

```javascript
const MENU_STRUCTURE = [
  { key: 'all', lbl: 'הכל', ids: 'all' },
  { key: 'morocco', lbl: 'מרוקו', items: [ /* תתי-קבוצות של מרוקו */ ] },
  { key: 'spain', lbl: 'ספרד', items: [ /* תתי-קבוצות של ספרד */ ] },
  { key: 'communities', lbl: 'עדות ישראל', items: [
    { key: 'iraq', lbl: 'עיראק', items: [
      { key: 'iraq_all', lbl: 'הכל', cat: 'iraq' },
      { key: 'iraq_soups', lbl: 'מרקים ותבשילים', ... },
      { key: 'iraq_meat', lbl: 'בשר ועוף', ... },
      // ...
      { key: 'iraq_holidays', lbl: 'חגי העדה העיראקית',
        className: 'nav-holidays-group',
        filter: 'holidays' }  // ← הקבוצה החדשה
    ]},
    // ... וכו' לכל 9 העדות
  ]},
  { key: 'holidays', lbl: 'חגים', items: [ /* 10 חגים */ ]},
  { key: 'nonkosher', lbl: 'לא כשר', items: [ ... ]}
];
```

---

## שלב 1.5 — תרגומים ב-`pre_en.js`

מילים חדשות שדורשות תרגום:

| עברית | English |
|--------|---------|
| ספר הבישול של פרלה | Perla's Cookbook |
| מתכונים | recipes |
| עיון במתכונים | Browse Recipes |
| קרא את הספר | Read the Book |
| הסיפור של המשפחה | Family Story |
| הכל | All |
| מרוקו | Morocco |
| ספרד | Spain |
| עדות ישראל | Jewish Communities |
| חגים | Holidays |
| לא כשר | Non-Kosher |
| חגי העדה העיראקית | Iraqi Community Holidays |
| חגי העדה הכורדיסטאנית | Kurdish Community Holidays |
| חגי העדה האשכנזית | Ashkenazi Community Holidays |
| חגי העדה התימנית | Yemenite Community Holidays |
| חגי העדה הפרסית | Persian Community Holidays |
| חגי העדה הבוכרית | Bukharian Community Holidays |
| חגי העדה הטוניסאית | Tunisian Community Holidays |
| חגי העדה הטורקית | Turkish Community Holidays |
| חגי העדה הישראלית | Israeli Community Holidays |

---

## שלב 1.6 — בדיקות לאחר שינוי

לפני push, אני אעבור על:

1. **תחביר JS** — `node -c` על data.js ו-pre_en.js
2. **ספירת מתכונים** — ודא שעדיין 1,054 מתכונים לאחר עדכון MENU_STRUCTURE
3. **כל הקטגוריות מופיעות** — ידנית בודק שמכל 5 הקבוצות העליונות ניתן להגיע לכל 20 הקטגוריות
4. **PWA install עובד** — כפתור נראה, modal מופיע
5. **Back-to-Top עובד** — מופיע בגלילה
6. **Feedback button עובד** — modal מופיע
7. **מעבר לאנגלית** — כל הטקסטים החדשים מתורגמים
8. **Bio מופיע לפני רשת המתכונים** — סדר הגלילה נכון
9. **שום מתכון לא "אבד"** — רק לחיצה על "הכל" מראה 1,054

---

## שלב 1.7 — מה יקרה אחרי הפריסה

אחרי ה-commit הגדול, תעשה:
```powershell
git pull
git add index.html data.js pre_en.js CLAUDE.md CHANGELOG_19-04-2026_v7_0.md
git commit -m "v7.0: Homepage redesign — unified header, shorter hero, improved nav with per-cuisine holidays"
git push origin main
```

**Netlify + GH Pages יפרסו תוך 30-60 שניות.**

אני מעריך את הריסק של שבירה **לא אפסי** — יכולים להופיע באגים קטנים:
- צבע לא תואם בנושא בהיר/כהה
- כפתור שלא מגיב ללחיצה
- תרגום חסר
- פריסה לא נכונה במובייל

אם תראה משהו כזה — שלח screenshot ואני אתקן ב-hotfix v7.0.1.

---

## רשימת "לא אגע" (חוזר על עצמו בכוונה)

1. שמות, מרכיבים, ושלבים של **אף מתכון**
2. לינקי תמונות (`img` field ב-recipes)
3. `download_images.py`
4. `book_data.js`
5. `about_redesigned.*`
6. `sw.js` + `manifest.json`
7. לוגיקת Web3Forms
8. לוגיקת PWA install (כבר עובד)
9. לוגיקת Back-to-Top (כבר עובד)

אם תגלה שמשהו מהרשימה הזאת נשבר אחרי הפריסה — זו שגיאה שלי ואני אתקן.

---

## השאלה המכרעת לפני התחלה

בחר אחת מהאפשרויות A/B/C (בתחילת המסמך) עבור "חגי העדה".

אחרי שתבחר — אני מתחיל כתיבת קוד מיידית. אם תבחר C, אני יכול להתחיל תוך דקות. אם תבחר A, נצטרך קודם שיחה נפרדת על התיוג.

---

**לזכר פרלה בן-הראש ז״ל (1933-2025)**
