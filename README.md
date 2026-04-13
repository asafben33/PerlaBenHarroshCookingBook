# ספר הבישול של משפחת בן הראש

לזכרם של **פרלה ופנחס בן הראש** שזכרונם יהיה לברכה וגאווה לדורי דורות
דרך הטעם המעלה זכרונות שחשבנו שכבר שכחנו...

פרלה נולדה בקזבלנקה, גדלה במרקש, ונפטרה במאי 2025 בגיל 92.
נישאה לפנחס, איש ממשפחת קארו — צאצאי **רבי יוסף קארו**, מגורשי קסטיליה 1492.
המטבח שלה שילב שני עולמות: **מרוקו העמוקה** ו**ספרד האנדלוסית**, ומאכלים שלמדה משכנים וחברים בשכונת הקטמון בירושלים.

---

## סטטיסטיקות

| מאפיין | ערך |
|--------|-----|
| מתכונים | **1,054** (כולל 40 לא כשרים) |
| קטגוריות | **19** |
| חגים ומועדים | **10** |
| מילון תרגום | **2,853** ערכים |
| כותרות אנגליות | **1,054** |
| תלויות חיצוניות | **0** |

---

## מבנה הפרויקט

```
PerlaBenHarroshCookingBook/
├── index.html              ← SPA (271 KB) — UI, CSS, JS
├── data.js                 ← 1,054 מתכונים + MENU_STRUCTURE + HOLIDAY_TAGS
├── pre_en.js               ← תרגום EN מוכן (771 KB) — desc, mem, tip, steps, ingr
├── sw.js                   ← Service Worker v9
├── manifest.json           ← PWA manifest
├── download_images.py      ← סקריפט תמונות (810 search terms)
├── cleanup_hardlinks.py    ← ניקוי כפילויות תמונות
├── images/                 ← תמונות (r-{id}.jpg)
├── wedding.jpg             ← תמונת החתונה
├── .gitignore
└── README.md
```

---

## מבנה התפריט

```
[כל המתכונים 1054]
├── הכל (1,054)
├── מטעמים של אמא ממרוקו (744)
│   ├── מרקים (103)
│   ├── סלטים (103)
│   ├── מנות עיקריות: בשר (82), עוף (66), דגים (70)
│   ├── ירקות ותוספות (87)
│   ├── חגים ומועדים (80) — 10 חגים
│   ├── קינוחים ומאפים (80)
│   └── מורשת ספרד (73) — 8 תתי-קטגוריות
├── מתכונים מהעדות (270) — 9 עדות + ישראלי (4 תתי)
└── מתכונים לא כשרים (40) — פירות ים (14), בשר וחלב (26)
```

---

## קבצים טכניים

| קובץ | גודל | תפקיד |
|-------|------|-------|
| index.html | 271 KB | SPA, CSS, JS, _TITLE_EN, _FOOD_DICT, CAT_IMG |
| data.js | 978 KB | R[], CATS, MENU_STRUCTURE, HOLIDAY_TAGS |
| pre_en.js | 771 KB | _PRE_EN — 1,054 x 5 שדות (0 עברית) |
| sw.js | 2.3 KB | Cache: data.js, pre_en.js, manifest.json |
| download_images.py | 104 KB | 810 TITLE_QUERIES, 5 מקורות תמונות |
| cleanup_hardlinks.py | 3.3 KB | SHA256 dedup, _IMG_ALIAS.js generator |

---

## פריסה

| שרת | כתובת |
|-----|-------|
| Netlify | https://perlabenharrosh-cookingbook.netlify.app/ |
| GitHub Pages | https://asafben33.github.io/PerlaBenHarroshCookingBook/ |
| Repository | github.com/asafben33/PerlaBenHarroshCookingBook |

---

*לזכר משפחת בן הראש — קזבלנקה, מרקש, ירושלים*
