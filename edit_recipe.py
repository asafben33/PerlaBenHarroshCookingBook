"""
מטרת הסקריפט:
אשף אינטראקטיבי לעריכה או מחיקה של מתכון קיים ב-data.js.
הסקריפט מחפש מתכון לפי ID או כותרת חלקית, מציג את הערכים הנוכחיים,
מאפשר לערוך שדה אחר שדה (Enter = ללא שינוי), להוסיף/למחוק מרכיבים ושלבים,
מייצר תצוגה מקדימה, גיבוי, ושומר את השינויים.

Interactive wizard for editing or deleting an existing recipe in data.js.
Usage:
  python edit_recipe.py               # live mode — writes to data.js
  python edit_recipe.py --dry-run     # preview only
  python edit_recipe.py --data ../path/to/data.js
"""

# ============================================================
# edit_recipe.py — interactive recipe edit/delete wizard
# ============================================================

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from recipe_utils import (
    CATEGORIES, CATEGORY_DICT, DIFFICULTIES,
    Logger, ask, ask_yes_no, ask_choice,
    load_data_js, save_data_js,
    find_recipe_bounds, scan_all_recipes, extract_recipe_fields,
    replace_recipe, delete_recipe,
    print_recipe_summary,
    hdr, ok, warn, err, dim,
    configure_rtl_fix,
)

# -----------------------------------------------------------
# Parse CLI arguments
# -----------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(
        description='עריכת/מחיקת מתכון קיים ב-data.js (אשף אינטראקטיבי).'
    )
    p.add_argument('--data', default='data.js',
                   help='Path to data.js (default: ./data.js)')
    p.add_argument('-n', '--dry-run', action='store_true',
                   help='Preview only; write to data.js.dryrun instead of overwriting.')
    p.add_argument('--no-rtl-fix', action='store_true',
                   help='Disable auto Hebrew reversal for BiDi-aware terminals.')
    return p.parse_args()

# -----------------------------------------------------------
# Search & select recipe
# -----------------------------------------------------------
def find_target_recipe(text, log):
    """Search by ID or title substring; return recipe_id of the chosen match."""
    all_recipes = scan_all_recipes(text)
    log.info(f"Scanned {len(all_recipes)} recipes in data.js")

    while True:
        print()
        query = ask('חפש מתכון (ID מדויק או קטע מהכותרת)', required=True)

        # Exact ID match
        exact = [r for r in all_recipes if r['id'] == query]
        if exact:
            return exact[0]['id']

        # Substring title match (case-insensitive — Hebrew too)
        q_norm = query.strip().lower()
        matches = [r for r in all_recipes
                   if q_norm in r['title'].lower() or q_norm in r['id'].lower()]

        if not matches:
            print(err(f'  לא נמצאו תוצאות ל-"{query}".'))
            if not ask_yes_no('לנסות חיפוש אחר?', default='y'):
                return None
            continue

        if len(matches) == 1:
            r = matches[0]
            print(ok(f'  נמצאה תוצאה יחידה: {r["id"]} — {r["title"]}'))
            if ask_yes_no('להמשיך עם מתכון זה?', default='y'):
                return r['id']
            continue

        # Multiple — let user pick
        print(f'\n  {hdr(f"נמצאו {len(matches)} תוצאות:")}')
        limit = min(len(matches), 20)
        for i, r in enumerate(matches[:limit], 1):
            cat_lbl = CATEGORY_DICT.get(r['cat'], r['cat'])
            print(f'    {i:2d}. {r["id"]:<8s} — {r["title"]}  {dim(f"({cat_lbl})")}')
        if len(matches) > limit:
            print(dim(f'    … ועוד {len(matches) - limit} תוצאות.'))

        raw = ask(f'בחר [1-{limit}] או ריק לחיפוש מחודש', allow_empty_for_skip=True)
        if not raw:
            continue
        if raw.isdigit() and 1 <= int(raw) <= limit:
            return matches[int(raw) - 1]['id']
        print(err('  בחירה לא תקינה.'))

# -----------------------------------------------------------
# Editing helpers — for each field, show current value and prompt
# -----------------------------------------------------------
def edit_string_field(label, current, required=False, multiline_hint=False):
    """
    Show current value; Enter keeps it, new text replaces it.
    Special: typing '-' clears an optional field.
    """
    shown = current if len(current) < 80 else current[:80] + '…'
    hint = '  (Enter = ללא שינוי, - = נקה)' if not required else '  (Enter = ללא שינוי)'
    print(f"\n  {hdr(label)}: {dim(shown or '(ריק)')}{dim(hint)}")
    try:
        raw = input('    ערך חדש: ').strip()
    except (KeyboardInterrupt, EOFError):
        print('\n' + warn('בוטל.'))
        sys.exit(1)
    if not raw:
        return current
    if raw == '-' and not required:
        return ''
    return raw

def edit_list_of_pairs(label, current_pairs, key_a_name, key_b_name, log):
    """
    Interactive editor for a list of (a, b) pairs (ingredients or steps).
    Menu: show list / add / edit index / delete index / done.
    """
    pairs = list(current_pairs)

    def _show():
        print(f'\n  {hdr(label)} — {len(pairs)} פריטים:')
        if not pairs:
            print(dim('    (ריק)'))
            return
        for i, (a, b) in enumerate(pairs, 1):
            b_shown = b if len(b) < 70 else b[:70] + '…'
            print(f'    {i:2d}. [{a}]  {b_shown}')

    while True:
        _show()
        print(f'\n  {hdr("פעולות")}: [ה]וסף | [ע]רוך | [מ]חק | [ס]יום')
        try:
            raw = input('    פעולה: ').strip().lower()
        except (KeyboardInterrupt, EOFError):
            print('\n' + warn('בוטל.'))
            sys.exit(1)

        if raw in ('ס', 's', 'done', ''):
            return pairs

        if raw in ('ה', 'a', 'add'):
            a = ask(f'    {key_a_name}', required=True)
            b = ask(f'    {key_b_name}', required=True)
            pairs.append((a, b))
            log.info(f"Added pair to {label}: [{a}] {b[:50]}")
            continue

        if raw in ('ע', 'e', 'edit'):
            if not pairs:
                print(err('  אין פריטים לעריכה.'))
                continue
            idx_s = ask(f'    מספר פריט לעריכה [1-{len(pairs)}]', required=True)
            if not idx_s.isdigit():
                print(err('  מספר לא תקין.'))
                continue
            idx = int(idx_s) - 1
            if not (0 <= idx < len(pairs)):
                print(err('  מחוץ לטווח.'))
                continue
            cur_a, cur_b = pairs[idx]
            print(dim(f'    {key_a_name} נוכחי: {cur_a}'))
            new_a = ask(f'    {key_a_name} חדש (Enter = ללא שינוי)',
                        allow_empty_for_skip=True) or cur_a
            print(dim(f'    {key_b_name} נוכחי: {cur_b}'))
            new_b = ask(f'    {key_b_name} חדש (Enter = ללא שינוי)',
                        allow_empty_for_skip=True) or cur_b
            pairs[idx] = (new_a, new_b)
            log.info(f"Edited pair #{idx+1} in {label}")
            continue

        if raw in ('מ', 'd', 'delete'):
            if not pairs:
                print(err('  אין פריטים למחיקה.'))
                continue
            idx_s = ask(f'    מספר פריט למחיקה [1-{len(pairs)}]', required=True)
            if not idx_s.isdigit():
                print(err('  מספר לא תקין.'))
                continue
            idx = int(idx_s) - 1
            if not (0 <= idx < len(pairs)):
                print(err('  מחוץ לטווח.'))
                continue
            removed = pairs.pop(idx)
            log.info(f"Deleted pair #{idx+1} from {label}: {removed}")
            print(ok(f'  ✓ נמחק.'))
            continue

        print(err('  פעולה לא ברורה. ה=הוסף, ע=ערוך, מ=מחק, ס=סיום.'))

# -----------------------------------------------------------
# Main edit flow
# -----------------------------------------------------------
def edit_recipe_interactive(recipe, log):
    """Walk through each field, allowing edit. Returns updated dict."""
    r = dict(recipe)  # copy

    print()
    print(hdr('════════════════════════════════════════════════════════'))
    print(hdr(' עריכת המתכון — לחץ Enter לכל שדה כדי להשאיר ללא שינוי'))
    print(hdr('════════════════════════════════════════════════════════'))

    # ID is NOT editable — it's the key and changing it would break refs
    print(f"\n  {dim('מזהה (לא ניתן לעריכה):')} {r['id']}")

    # Category
    print(f"\n  {hdr('קטגוריה נוכחית:')} {r['cat']} ({CATEGORY_DICT.get(r['cat'], '?')})")
    if ask_yes_no('לשנות קטגוריה?', default='n'):
        r['cat'] = ask_choice('בחר קטגוריה חדשה:', CATEGORIES)

    # Simple text fields
    r['badge'] = edit_string_field('תג (badge)',    r.get('badge', ''))
    r['title'] = edit_string_field('כותרת',          r.get('title', ''), required=True)
    r['desc']  = edit_string_field('תיאור',          r.get('desc',  ''), required=True)
    r['time']  = edit_string_field('זמן',            r.get('time',  ''), required=True)
    r['serv']  = edit_string_field('מנות',           r.get('serv',  ''), required=True)

    # Difficulty — pick from list
    cur_diff = r.get('diff', '')
    print(f"\n  {hdr('רמת קושי נוכחית:')} {cur_diff or '(ריק)'}")
    if ask_yes_no('לשנות?', default='n'):
        diff_options = [(d, d) for d in DIFFICULTIES]
        r['diff'] = ask_choice('רמת קושי חדשה:', diff_options)

    r['img'] = edit_string_field('תמונה (URL)',      r.get('img',   ''))
    r['src'] = edit_string_field('קישור מקור',       r.get('src',   ''))
    r['vid'] = edit_string_field('קישור וידאו',      r.get('vid',   ''))
    r['mem'] = edit_string_field('זיכרון / סיפור',   r.get('mem',   ''), required=True)

    # Ingredients
    if ask_yes_no(f'\nלערוך מרכיבים? (כעת {len(r.get("ingr", []))} מרכיבים)', default='n'):
        r['ingr'] = edit_list_of_pairs('מרכיבים', r.get('ingr', []),
                                       'כמות', 'פריט', log)

    # Steps
    if ask_yes_no(f'\nלערוך שלבים? (כעת {len(r.get("steps", []))} שלבים)', default='n'):
        r['steps'] = edit_list_of_pairs('שלבי הכנה', r.get('steps', []),
                                        'זמן', 'טקסט השלב', log)

    # Tip
    r['tip'] = edit_string_field('טיפ',               r.get('tip',   ''))

    return r

# -----------------------------------------------------------
# Main flow
# -----------------------------------------------------------
def main():
    args = parse_args()
    if args.no_rtl_fix:
        configure_rtl_fix(False)
    log = Logger('edit_recipe')

    try:
        log.progress(10, 'קורא את data.js...')
        text = load_data_js(args.data)
        log.info(f"Loaded data.js ({len(text):,} chars) from {args.data}")

        log.progress(20, 'חיפוש מתכון יעד...')
        target_id = find_target_recipe(text, log)
        if not target_id:
            print(warn('לא נבחר מתכון. הסקריפט מסתיים.'))
            return 0
        log.info(f"Target recipe ID: {target_id}")

        log.progress(30, 'שולף את המתכון...')
        bounds = find_recipe_bounds(text, target_id)
        if not bounds:
            log.error(f"Recipe bounds not found for ID: {target_id}")
            return 3
        start, end = bounds
        block_text = text[start:end]
        recipe = extract_recipe_fields(block_text)
        log.info(f"Parsed recipe: {recipe['title']} ({len(recipe['ingr'])} ingr, "
                 f"{len(recipe['steps'])} steps)")

        # Show current state
        print()
        print(hdr('== מצב נוכחי =='))
        print_recipe_summary(recipe)

        # Top-level action menu
        print(f"\n  {hdr('מה ברצונך לעשות?')}")
        action = ask_choice('פעולה:', [
            ('edit',   'עריכת שדות המתכון'),
            ('delete', 'מחיקת המתכון לחלוטין'),
            ('cancel', 'ביטול — יציאה ללא שינוי'),
        ])

        if action == 'cancel':
            print(warn('בוטל.'))
            log.info('User cancelled before editing')
            return 0

        if action == 'delete':
            log.progress(60, 'אישור מחיקה...')
            print()
            print(err(f'⚠  עומד למחוק את המתכון: {recipe["title"]} (ID: {recipe["id"]})'))
            if not ask_yes_no('פעולה זו לא הפיכה. למחוק בכל זאת?', default='n'):
                print(warn('המחיקה בוטלה.'))
                log.info('Delete cancelled')
                return 0
            log.progress(70, 'מוחק מהקובץ...')
            new_text = delete_recipe(text, target_id)
            log.info(f"Deleted recipe {target_id}")

        else:  # edit
            log.progress(40, 'מפעיל אשף עריכה...')
            updated = edit_recipe_interactive(recipe, log)

            log.progress(60, 'תצוגה מקדימה של השינויים...')
            print()
            print(hdr('== המתכון לאחר העריכה =='))
            print_recipe_summary(updated)

            if not ask_yes_no('לשמור את השינויים?', default='y'):
                print(warn('העריכה בוטלה.'))
                log.info('Edit cancelled at save prompt')
                return 0

            log.progress(70, 'מחליף במערך R...')
            new_text = replace_recipe(text, target_id, updated)
            log.info(f"Replaced recipe {target_id}. Size delta: "
                     f"{len(new_text) - len(text):+,} chars")

        log.progress(85, 'מאמת תחביר בסיסי...')
        if new_text.rfind('\n];\n') == -1 and new_text.rfind('\n];') == -1:
            raise RuntimeError("Syntax check failed: `];` array closer missing after edit")

        log.progress(95, 'כותב לקובץ...' + (' (dry-run)' if args.dry_run else ''))
        result_path = save_data_js(new_text, args.data, dry_run=args.dry_run, logger=log)

        log.progress(100, 'הסתיים בהצלחה.')
        print()
        if args.dry_run:
            print(ok(f'✓ DRY-RUN הסתיים. הפלט נכתב אל: {result_path}'))
            print(dim(f'  ההפעלה לא שינתה את {args.data}.'))
        else:
            verb = 'נמחק' if action == 'delete' else 'עודכן'
            print(ok(f'✓ המתכון {verb} בהצלחה ב-{args.data}'))
            print(dim(f'  גיבוי: {result_path}'))
            print()
            print(hdr('הצעדים הבאים:'))
            print('  1. בדוק באתר שהשינוי תקין: פתח index.html בדפדפן.')
            print('  2. אם הכל בסדר:')
            print(dim(f'     git add {args.data}'))
            if action == 'delete':
                print(dim(f'     git commit -m "Delete recipe: {recipe["title"]} ({target_id})"'))
            else:
                print(dim(f'     git commit -m "Edit recipe: {recipe["title"]} ({target_id})"'))
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
