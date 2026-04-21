"""
מטרת הסקריפט:
אשף אינטראקטיבי להוספת מתכון חדש ל-data.js של אתר ספר הבישול של פרלה ז"ל.
הסקריפט מבקש ממך את כל שדות המתכון שלב-אחר-שלב, מייצר תצוגה מקדימה,
מבצע וולידציה (מזהה ייחודי, קטגוריה חוקית, כותרת לא כפולה), יוצר גיבוי,
ומזריק את המתכון החדש לקובץ.

Interactive wizard for adding a new recipe to data.js.
Usage:
  python add_recipe.py               # live mode — writes to data.js
  python add_recipe.py --dry-run     # preview only, writes to data.js.dryrun
  python add_recipe.py --data ../path/to/data.js
"""

# ============================================================
# add_recipe.py — interactive recipe-addition wizard
# ============================================================

import argparse
import sys
from pathlib import Path

# Ensure local imports work even when run from a different directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from recipe_utils import (
    CATEGORIES, CATEGORY_DICT, DIFFICULTIES,
    Logger, ask, ask_yes_no, ask_choice,
    load_data_js, save_data_js,
    inject_recipe, suggest_next_id, id_exists, title_exists,
    print_recipe_summary,
    hdr, ok, warn, err, dim,
    configure_rtl_fix,
    DEFAULT_DATA_JS,
)

# -----------------------------------------------------------
# Parse CLI arguments
# -----------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(
        description='הוספת מתכון חדש ל-data.js (אשף אינטראקטיבי).'
    )
    p.add_argument('--data', default=str(DEFAULT_DATA_JS),
                   help='Path to data.js (default: PROJECT_ROOT/data.js)')
    p.add_argument('-n', '--dry-run', action='store_true',
                   help='Preview only; write to data.js.dryrun instead of overwriting.')
    p.add_argument('--no-rtl-fix', action='store_true',
                   help='Disable auto Hebrew reversal for BiDi-aware terminals.')
    return p.parse_args()

# -----------------------------------------------------------
# Wizard — collect recipe fields
# -----------------------------------------------------------
def collect_recipe(text, log):
    """Drive the interactive wizard. Returns a recipe dict ready for format_recipe()."""

    print()
    print(hdr('════════════════════════════════════════════════════════'))
    print(hdr(' הוספת מתכון חדש — ספר הבישול של פרלה בן-הראש ז״ל'))
    print(hdr('════════════════════════════════════════════════════════'))
    print()

    # --- Category ---
    log.step('Step 1/7: category selection')
    cat = ask_choice('בחר קטגוריה:', CATEGORIES)

    # --- ID ---
    log.step('Step 2/7: ID selection')
    suggested = suggest_next_id(text, cat)
    print()
    while True:
        rid = ask(f'מזהה ייחודי (ID)', default=suggested, required=True,
                  validator=lambda s: bool(s) and ' ' not in s and "'" not in s)
        if id_exists(text, rid):
            print(err(f"  מזהה '{rid}' כבר קיים — יש לבחור מזהה אחר."))
            continue
        break

    # --- Basic fields ---
    log.step('Step 3/7: basic metadata')
    print()
    print(hdr('[פרטי מתכון בסיסיים]'))

    while True:
        title = ask('כותרת המתכון', required=True)
        if title_exists(text, title):
            if not ask_yes_no(f"כותרת '{title}' כבר קיימת. להמשיך בכל זאת?", default='n'):
                continue
        break

    badge = ask('תג (badge — אופציונלי, לדוגמה "סמלי" או "מטעמי אמא")',
                allow_empty_for_skip=True)
    desc  = ask('תיאור קצר (1–2 משפטים)', required=True)
    time_ = ask('זמן הכנה כולל (למשל "45 דקות")', required=True)
    serv  = ask('מספר מנות (למשל "6 מנות" או "4–6 מנות")', required=True)

    diff_options = [(d, d) for d in DIFFICULTIES]
    diff = ask_choice('רמת קושי:', diff_options, default_idx=1)

    img = ask('קישור לתמונה (URL מלא, או ריק לברירת מחדל של picsum)',
              allow_empty_for_skip=True)
    if not img:
        # Default placeholder — user can replace via download_images.py later
        img = f'https://picsum.photos/seed/{rid}/600/400'

    src = ask('קישור למקור (URL, אופציונלי)', allow_empty_for_skip=True)
    vid = ask('קישור לוידאו (YouTube URL, אופציונלי)', allow_empty_for_skip=True)

    # --- Memory (mem) ---
    log.step('Step 4/7: memory / cultural note')
    print()
    print(hdr('[זיכרון ממרוקו / הקשר תרבותי]'))
    print(dim('  (תיאור אישי שמחבר את המתכון לאמא, משפחה, או מקום במרוקו — חובה לכל מתכון באתר.)'))
    mem = ask('זיכרון / סיפור קצר', required=True)

    # --- Ingredients ---
    log.step('Step 5/7: ingredients')
    print()
    print(hdr('[מרכיבים]'))
    print(dim('  הזן מרכיב אחר מרכיב. כדי לסיים, השאר את הכמות ריקה ולחץ Enter.'))
    ingr = []
    while True:
        idx = len(ingr) + 1
        print(f"\n  {hdr(f'מרכיב {idx}')}:")
        q = ask('    כמות (למשל "2 כוסות" או "500 גרם", ריק לסיום)',
                allow_empty_for_skip=True)
        if not q:
            if not ingr:
                print(err('  חובה לפחות מרכיב אחד.'))
                continue
            break
        i = ask('    פריט (למשל "קמח לבן" או "בצל גדול, קצוץ דק")', required=True)
        ingr.append((q, i))
        print(ok(f'    ✓ נוסף: {q} — {i}'))

    log.info(f"Collected {len(ingr)} ingredients")

    # --- Steps ---
    log.step('Step 6/7: preparation steps')
    print()
    print(hdr('[שלבי הכנה]'))
    print(dim('  הזן שלב אחר שלב. כל שלב כולל זמן (למשל "5 דק׳") וטקסט הוראה.'))
    steps = []
    while True:
        idx = len(steps) + 1
        print(f"\n  {hdr(f'שלב {idx}')}:")
        t = ask('    זמן (למשל "5 דק׳" או "סיום", ריק לסיום רשימה)',
                allow_empty_for_skip=True)
        if not t:
            if not steps:
                print(err('  חובה לפחות שלב אחד.'))
                continue
            break
        s = ask('    הוראות השלב (משפט או שניים מלאים)', required=True)
        steps.append((t, s))
        print(ok(f'    ✓ נוסף שלב {idx}'))

    log.info(f"Collected {len(steps)} steps")

    # --- Tip ---
    log.step('Step 7/7: final tip')
    print()
    print(hdr('[טיפ סופי]'))
    print(dim('  עצה של אמא, הערה תרבותית, או טריק שיווצר את ההבדל במנה. אופציונלי.'))
    tip = ask('טיפ אחרון (אופציונלי)', allow_empty_for_skip=True)

    # --- Assemble ---
    recipe = {
        'id':    rid,
        'cat':   cat,
        'badge': badge,
        'title': title,
        'desc':  desc,
        'time':  time_,
        'serv':  serv,
        'diff':  diff,
        'img':   img,
        'src':   src,
        'vid':   vid,
        'mem':   mem,
        'ingr':  ingr,
        'steps': steps,
        'tip':   tip,
    }
    return recipe

# -----------------------------------------------------------
# Preview & confirmation
# -----------------------------------------------------------
def show_preview(recipe):
    print()
    print(hdr('════════════════════════════════════════════════════════'))
    print(hdr(' תצוגה מקדימה של המתכון החדש'))
    print(hdr('════════════════════════════════════════════════════════'))
    print_recipe_summary(recipe)
    print()

# -----------------------------------------------------------
# Main flow
# -----------------------------------------------------------
def main():
    args = parse_args()
    if args.no_rtl_fix:
        configure_rtl_fix(False)
    log = Logger('add_recipe')

    try:
        log.progress(10, 'קורא את data.js...')
        text = load_data_js(args.data)
        log.info(f"Loaded data.js ({len(text):,} chars) from {args.data}")

        log.progress(20, 'אשף איסוף נתונים...')
        recipe = collect_recipe(text, log)

        log.progress(60, 'מציג תצוגה מקדימה...')
        show_preview(recipe)

        if not ask_yes_no('להוסיף את המתכון ל-data.js?', default='y'):
            print(warn('הוספה בוטלה על ידי המשתמש.'))
            log.info('User aborted before write')
            return 0

        log.progress(70, 'מזריק למערך R...')
        new_text = inject_recipe(text, recipe)
        log.info(f"Injected recipe. New file size: {len(new_text):,} chars "
                 f"(+{len(new_text) - len(text):,})")

        log.progress(80, 'מאמת תחביר בסיסי...')
        # Sanity check: array close marker still exists exactly once near end
        if new_text.rfind('\n];\n') == -1 and new_text.rfind('\n];') == -1:
            raise RuntimeError("Syntax check failed: `];` array closer missing after injection")

        log.progress(90, 'כותב לקובץ...' + (' (dry-run)' if args.dry_run else ''))
        result_path = save_data_js(new_text, args.data, dry_run=args.dry_run, logger=log)

        log.progress(100, 'הסתיים בהצלחה.')
        print()
        if args.dry_run:
            print(ok(f'✓ DRY-RUN הסתיים. הפלט נכתב אל: {result_path}'))
            print(dim(f'  ההפעלה לא שינתה את {args.data}. עיין בקובץ ה-dryrun ואם הכל בסדר,'
                      f' הרץ שוב בלי --dry-run.'))
        else:
            print(ok(f'✓ המתכון נוסף בהצלחה ל-{args.data}'))
            print(dim(f'  גיבוי: {result_path}'))
            print()
            print(hdr('הצעדים הבאים:'))
            print('  1. בדוק באתר שהמתכון מופיע: פתח index.html בדפדפן.')
            print('  2. אם הכל תקין:')
            print(dim(f'     git add {args.data}'))
            print(dim(f'     git commit -m "Add recipe: {recipe["title"]}"'))
            print(dim(f'     git push origin main'))
        print()
        print(dim(f'  לוג מלא: {log.path}'))

    except FileNotFoundError as e:
        log.error(str(e))
        return 2
    except ValueError as e:
        log.error(f"Data error: {e}")
        return 3
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        import traceback
        log.error(traceback.format_exc())
        return 1
    finally:
        log.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())
