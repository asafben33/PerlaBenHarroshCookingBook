# מדריך הרצה של `download_images.py` v5.1

## טבלת דגלים מלאה

| דגל | תיאור קצר |
|---|---|
| (ללא דגלים) | מחזור מלא: ניקוי חשודים → הורדה → dedup |
| `--reset-images` | מחיקה של **כל** תמונות המתכונים (איתחול מלא) |
| `--clean-only` | רק שלב 1 — סריקה ומחיקה של תמונות חשודות |
| `--skip-clean` | דלג על שלב הניקוי |
| `--aggressive-clean` | ניקוי קפדני יותר (min-size 5KB, ratio 1.9/0.55) |
| `--skip-download` | דלג על ההורדה |
| `--skip-dedup` | דלג על הסרת כפילויות |
| `--dry-run` | **תצוגה מקדימה בלבד** — לא מוחק, לא כותב |
| `--overwrite` | הורד מחדש גם תמונות שכבר קיימות |
| `--inline-alias` | החדר אוטומטית את `_IMG_ALIAS.js` ל-`index.html` |
| `--no-proxy` | התעלם מ-proxy — חיבור ישיר |
| `--proxy URL` | הגדר proxy ידנית (למשל `http://proxy.gov.il:8080`) |
| `--detect-only` | רק גלה proxy ושמור ל-`proxy_config.txt` |
| `--test-proxy` | בודק כל מועמד proxy באקטיביות (איטי יותר) |

---

## תרחישי הפעלה — סדר מומלץ

### 1. הפעלה מומלצת רגילה

```bash
python download_images.py
```

מרצה את כל 3 השלבים: ניקוי תמונות חשודות → הורדת חדשות → הסרת כפילויות.

### 2. הפעלה מלאה כולל עדכון index.html אוטומטי

```bash
python download_images.py --inline-alias
```

כמו לעיל, ובסוף גם מחדיר את ה-alias map ישירות ל-`index.html` (חוסך copy-paste).

### 3. אתחול מלא — התחלה מאפס

```bash
python download_images.py --reset-images --inline-alias
```

מוחק את **כל** תמונות המתכונים ומוריד הכל מחדש. שימושי אם הספרייה מלאה זבל.

### 4. רק לבדוק מה יקרה (ללא שינויים)

```bash
python download_images.py --dry-run
```

מציג רשימה של מה יימחק ומה יורד, בלי לבצע כלום.

### 5. רק ניקוי חשודים (להתחיל מנקה)

```bash
python download_images.py --clean-only
```

או עם תצוגה מקדימה:

```bash
python download_images.py --clean-only --dry-run
```

או עם פילטר קפדני יותר:

```bash
python download_images.py --clean-only --aggressive-clean
```

### 6. רק להוריד (דלג על ניקוי)

```bash
python download_images.py --skip-clean
```

### 7. רק להסיר כפילויות (ללא הורדה)

```bash
python download_images.py --skip-clean --skip-download
```

### 8. רק לעדכן `index.html` מה-alias הקיים

```bash
python download_images.py --skip-clean --skip-download --skip-dedup --inline-alias
```

### 9. להוריד מחדש גם תמונות שקיימות

```bash
python download_images.py --overwrite
```

שימושי אם החלטת להחליף תמונות ישנות בחדשות.

---

## תרחישי Proxy (ברשת gov.il)

### לגלות proxy אוטומטית ולשמור

```bash
python download_images.py --detect-only
```

הסקריפט יגלה את ה-proxy מה-Registry/PAC ויישמור ל-`proxy_config.txt`. לא מוריד תמונות.

### לבדוק באופן אקטיבי כל proxy מועמד

```bash
python download_images.py --test-proxy
```

איטי יותר אבל מוצא את ה-proxy הראשון שאכן עובד.

### להגדיר proxy ידנית

```bash
python download_images.py --proxy http://proxy.gov.il:8080
```

### להתעלם מ-proxy לחלוטין

```bash
python download_images.py --no-proxy
```

שימושי אם אתה מריץ מהבית או מ-hotspot.

---

## שילובים מומלצים

**פעם ראשונה, אחרי שההורדה הקודמת הביאה תמונות לא רלוונטיות:**

```bash
python download_images.py --aggressive-clean --inline-alias
```

**לחזור למצב נקי ולהתחיל מאפס:**

```bash
python download_images.py --reset-images --inline-alias
```

**לבדוק מה קורה בלי לקלקל כלום:**

```bash
python download_images.py --dry-run --aggressive-clean
```

**להוסיף תמונות חדשות בלי להרוס קיימות:**

```bash
python download_images.py --skip-clean --inline-alias
```

**רק לרענן את ה-alias ב-`index.html`:**

```bash
python download_images.py --skip-clean --skip-download --inline-alias
```
