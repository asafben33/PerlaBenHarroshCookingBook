# CHANGELOG — `download_images.py` v6.0.1: Hotfix NameError בלולאה הראשית

**ספר הבישול של פרלה בן-הראש ז״ל**
**תאריך:** 20/04/2026
**גרסה:** 6.0.1 (תיקון מיידי של v6.0)

---

## הבאג

הריצה הראשונה של v6.0 נכשלה אחרי המתכון הראשון (`s1` — מרק חרירה) עם:

```
Traceback (most recent call last):
  File "...\download_images.py", line 3712, in <module>
    main()
  File "...\download_images.py", line 3591, in main
    _score = _score_url_relevance(u_str, r.get('title', ''), q, [])
                                         ^
NameError: name 'r' is not defined. Did you mean: 're'?
```

**גורם:** שתי טעויות בשמות משתנים בקטע ה-relevance scoring שהוספתי ב-v6.0:
- כתבתי `r.get('title', '')` אבל המשתנה בלולאה נקרא `recipe`
- כתבתי `q` אבל המשתנה נקרא `query`

זאת טעות שלי — שמות משתנים שלא תאמו לקוד הקיים בלולאה הראשית של הסקריפט (שורה 3433: `for i, recipe in enumerate(recipes)`).

---

## התיקון

קובץ `download_images.py` שורות 3585-3622:

```python
# לפני (v6.0 — שגוי)
_score = _score_url_relevance(u_str, r.get('title', ''), q, [])
                                     ^^^^^^^^^^^^^^^^^^^  ^
                                     NameError            NameError

lambda u=url, d=img_dest, sc=url_score:
    download_and_save(u, d, recipe=r, source_name=..., relevance_score=sc, query_kw=q)
                            ^                                                       ^
                            NameError                                          NameError
```

```python
# אחרי (v6.0.1 — מתוקן)
_score = _score_url_relevance(u_str, recipe.get('title', ''), query, [])
                                     ^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^
                                     correct loop variables

lambda u=url, d=img_dest, sc=url_score, rec=recipe, qu=query:
    download_and_save(u, d, recipe=rec, source_name=..., relevance_score=sc, query_kw=qu)
                            ^^^^^^^^^^^                                              ^^
                            captured by lambda default args (closure-safe)
```

---

## שינוי טכני נוסף

הוספתי `rec=recipe, qu=query` כ-default parameters ב-lambda — זה closure-safe pattern שמבטיח שגם אם הלולאה הראשית ממשיכה לאיטרציה הבאה לפני שה-lambda מבוצע (דרך `_call_with_timeout`), הערכים יישארו נכונים.

---

## בדיקות שעברו

```
✓ Python syntax: py_compile OK
✓ Import works (MIN_RELEVANCE_SCORE=40, CROSS_SOURCE_BONUS=20)
✓ All v6.0 functions exist
✓ recipe assigned before _score call (✓ via for i, recipe in enumerate())
✓ query  assigned before _score call (✓ via query = build_query(recipe))
✓ rid    assigned before _score call
✓ title  assigned before _score call
✓ No bare 'r' refs in scoring call
✓ No bare 'q' refs in scoring call
✓ Lambda captures rec=recipe, qu=query (closure-safe)
```

---

## מה לא נגעתי בו

כל 7 שכבות הדיוק של v6.0 נשארות כפי שהן:
1. ✓ Relevance Scoring (0-100)
2. ✓ Title Transliterations (48 entries)
3. ✓ Cross-Source Validation (+20 bonus)
4. ✓ Color Histogram Analysis
5. ✓ Composition Check
6. ✓ Negative Phrases (-50)
7. ✓ Provenance Trail (JSON)

רק תיקון ה-NameError. אין שינוי באלגוריתם.

---

## קבצים מצורפים

| קובץ | שינוי |
|---|---|
| `download_images.py` | תיקון 2 שמות משתנים בלולאה הראשית (שורות 3591, 3618-3621) |

---

## פריסה

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\download_images.py" ".\download_images.py" -Force
```
```powershell
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v6_0_1_hotfix.md" "." -Force
```
```powershell
git add download_images.py CHANGELOG_20-04-2026_v6_0_1_hotfix.md
```
```powershell
git commit -m "download_images v6.0.1: hotfix NameError - use 'recipe'/'query' (loop variables) instead of 'r'/'q'"
```
```powershell
git push origin main
```

---

## הריצה החוזרת

הרץ שוב את הפקודה הקודמת:

```powershell
python download_images.py --strict --provenance
```

הפעם זה אמור לרוץ עד הסוף ללא NameError. אם תהיה בעיה אחרת — תעלה את ה-traceback ואני אתקן.

---

## איך זה קרה (שקיפות)

ב-v6.0 כתבתי קוד חדש שעובד עם ה-relevance scoring. ניחשתי שמות משתנים על בסיס ראייה חלקית של הקוד — לא בדקתי בקפדה את הלולאה הראשית. **זה בדיוק סוג הבאג שצריך הרצה אמיתית כדי לתפוס** — `py_compile` עובר כי הסינטקס תקין, אבל ה-NameError מתגלה רק בזמן ריצה.

לפעם הבאה, אהיה זהיר יותר ואבדוק שמות משתנים מ-context אמיתי לפני שאני מוסיף קוד חדש שמתייחס אליהם.

מתנצל על האי-נוחות.

---

**לזכר משפחת בן-הראש — קזבלנקה, מרקש, ירושלים**
