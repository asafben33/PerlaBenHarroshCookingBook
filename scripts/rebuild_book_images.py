#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
rebuild_book_images.py — שחזור התמונות בספר מקובץ המיפוי
============================================================================
מטרת הסקריפט:
    סקריפט זה מאפשר לשחזר את כל מיקומי התמונות בקובץ book_data.js
    מתוך IMAGE_MAPPING_v8_25.json. השימוש המרכזי הוא במצבים שבהם:
    1. book_data.js נשבר או נמחק
    2. רוצים לעדכן את alt text או את החלוקה
    3. רוצים להוסיף תמונות חדשות (שדרוג ל-v8.26+)
    4. צריך לחזור גרסה אחורה אחרי טעות

תיאור הסקריפט (Hebrew Purpose Explanation):
    סקריפט זה משחזר את שילוב התמונות בספר ההזיכרון של פרלה ופנחס בן-הראש ז"ל.
    הוא קורא את הקובץ IMAGE_MAPPING_v8_25.json שמכיל את המיפוי המלא של 151 תמונות,
    ומחיל אותן על קובץ book_data.js הקיים — ב-HE וב-EN במקביל.
    
    הקובץ JSON מתוחזק בנפרד כך שאפשר לערוך אותו ידנית
    (לדוגמה: לשנות פרק של תמונה, לעדכן alt text) ואז להריץ את הסקריפט שוב.

שימוש:
    python rebuild_book_images.py [--dry-run] [--mapping FILE] [--input FILE] [--output FILE]
    
    --dry-run         : בדוק את המיפוי בלי לכתוב לקובץ
    --mapping FILE    : קובץ JSON של המיפוי (ברירת מחדל: IMAGE_MAPPING_v8_25.json)
    --input FILE      : book_data.js מקורי (ברירת מחדל: book_data.js)
    --output FILE     : קובץ פלט (ברירת מחדל: book_data.js.new)

דרישות:
    - Python 3.8+
    - הקובץ IMAGE_MAPPING_v8_25.json (באותה תיקייה)
    - הקובץ book_data.js (גרסה ראשונית - לפני שילוב גלריות)

הסבר טכני:
    - 'inline' תמונות מועתקות לפי המיקום הקיים שלהן (בתוך section עם h4 sub-title)
    - 'gallery' תמונות נוספות בסוף כל פרק כ-section חדש מסוג book-gallery-section
    - הסקריפט מטפל גם ב-HE BOOK_HTML וגם ב-EN BOOK_HTML_EN
    - לוג מודפס בעברית עם אחוזי התקדמות (10%, 20%, ... 100%)

מחבר: Claude (Anthropic) עבור Asaf Yaakov Ben-Harrosh
תאריך: 20-04-2026
גרסה: 1.0
============================================================================
"""

import json
import re
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# ─── Absolute path anchoring ─────────────────────────────────────────────
PROJECT_ROOT    = Path(__file__).resolve().parent.parent
DEFAULT_LOG_DIR = PROJECT_ROOT / 'logs'

# ─── הגדרות לוג בעברית עם חותמת זמן בפורמט DD-MM-YYYY_HH.MM ─────────────
LOG_PREFIX_FORMAT = "%d-%m-%Y_%H.%M"
PROGRESS_MILESTONES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# ─── ברירות מחדל ─────────────────────────────────────────────────────────
DEFAULT_MAPPING = str(PROJECT_ROOT / "docs" / "IMAGE_MAPPING_v8_25.json")
DEFAULT_INPUT = str(PROJECT_ROOT / "book_data.js")
DEFAULT_OUTPUT = str(PROJECT_ROOT / "book_data.js.new")

# ─── הגדרות פרקים ────────────────────────────────────────────────────────
CHAPTER_ORDER = ['prologue', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10']

# ─── טקסטים בעברית/אנגלית ────────────────────────────────────────────────
GALLERY_TITLE_HE = "תמונות מן האלבום המשפחתי"
GALLERY_TITLE_HE_PROLOGUE = "אלבום משפחתי"
GALLERY_TITLE_EN = "Photos from the family album"
GALLERY_TITLE_EN_PROLOGUE = "Family album"


def log(msg):
    """Print a log message with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def setup_log_file():
    """Create log file with DD-MM-YYYY_HH.MM format."""
    DEFAULT_LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime(LOG_PREFIX_FORMAT)
    log_path = DEFAULT_LOG_DIR / f"rebuild_book_images_{timestamp}.log"
    return str(log_path)


def report_progress(current, total, milestone_set):
    """Report progress at 10% milestones."""
    pct = int(current / total * 100)
    milestone = (pct // 10) * 10
    if milestone in PROGRESS_MILESTONES and milestone not in milestone_set:
        milestone_set.add(milestone)
        log(f"--- התקדמות {milestone:3d}% ---  ({current}/{total})")


def make_gallery_html(images_with_alts, gallery_title):
    """
    Create the escaped HTML string for a gallery section.
    Format matches book_data.js conventions: \\" for quotes, \\n for newlines.
    """
    parts = [
        f'<section class=\\"book-sub-block book-gallery-section\\">\\n'
        f'<h4 class=\\"book-sub\\">{gallery_title}</h4>\\n'
    ]
    for fname, alt in images_with_alts:
        parts.append(
            f'<figure class=\\"book-inline-photo\\">'
            f'<img src=\\"images/book_images/{fname}\\" '
            f'alt=\\"{alt}\\" loading=\\"lazy\\">'
            f'<figcaption>{alt}</figcaption></figure>\\n'
        )
    parts.append('</section>\\n')
    return ''.join(parts)


def inject_gallery(html_str, chapter_id, gallery_html):
    """
    Find the chapter in the HTML string and inject the gallery HTML
    just before the chapter's closing </div>.
    
    Strategy:
        1. Find chapter opening: <div class=\"book-chapter\" id=\"book-{chapter_id}\">
        2. Find next chapter opening (or end of book-section)
        3. Within this range, find the LAST </div> (which closes the chapter)
        4. Insert gallery just before that </div>
    """
    chapter_start_pat = rf'<div class=\\"book-chapter\\" id=\\"book-{chapter_id}\\"'
    start_match = re.search(chapter_start_pat, html_str)
    if not start_match:
        log(f"  אזהרה: פרק {chapter_id} לא נמצא")
        return html_str

    chapter_start = start_match.start()
    next_chapter_pat = r'<div class=\\"book-chapter\\" id=\\"book-'
    after_start = html_str[chapter_start + len(start_match.group(0)):]
    next_match = re.search(next_chapter_pat, after_start)

    if next_match:
        # Not the last chapter
        chunk_end = chapter_start + len(start_match.group(0)) + next_match.start()
        chunk = html_str[chapter_start:chunk_end]
        # Find LAST </div> in chunk = chapter's closing div
        last_div = None
        for m in re.finditer(r'</div>', chunk):
            last_div = m
        if last_div:
            insert_pos = chapter_start + last_div.start()
            return html_str[:insert_pos] + gallery_html + html_str[insert_pos:]
    else:
        # Last chapter (ch10) - find second-to-last </div>
        all_divs = list(re.finditer(r'</div>', html_str[chapter_start:]))
        if len(all_divs) >= 2:
            target = all_divs[-2]
            insert_pos = chapter_start + target.start()
            return html_str[:insert_pos] + gallery_html + html_str[insert_pos:]

    log(f"  אזהרה: לא הצלחתי להכניס לפרק {chapter_id}")
    return html_str


def process_book_html(html_str, mapping_data, lang='he'):
    """
    Apply the gallery injections to a book HTML string (HE or EN).
    Only 'gallery' placement images are added (inline are already in book_data.js).
    """
    # Group gallery images by chapter
    galleries = {ch: [] for ch in CHAPTER_ORDER}
    for entry in mapping_data['mapping']:
        if entry['placement'] == 'gallery':
            ch = entry['chapter_id']
            if ch in galleries:
                alt = entry['alt_en'] if lang == 'en' else entry['alt_he']
                galleries[ch].append((entry['filename'], alt))

    milestone_set = set()
    total_chapters = len(CHAPTER_ORDER)
    processed = 0

    for ch in CHAPTER_ORDER:
        images = galleries.get(ch, [])
        if images:
            if ch == 'prologue':
                title = GALLERY_TITLE_HE_PROLOGUE if lang == 'he' else GALLERY_TITLE_EN_PROLOGUE
            else:
                title = GALLERY_TITLE_HE if lang == 'he' else GALLERY_TITLE_EN
            gallery = make_gallery_html(images, title)
            html_str = inject_gallery(html_str, ch, gallery)
            log(f"  {ch}: הוספו {len(images)} תמונות לגלריה")

        processed += 1
        report_progress(processed, total_chapters, milestone_set)

    return html_str


def validate_result(html_str, mapping_data, lang='he'):
    """Validate that the expected number of images is present."""
    expected_g42 = len([e for e in mapping_data['mapping'] if e['image_set'] == 'g42'])
    expected_g45 = len([e for e in mapping_data['mapping'] if e['image_set'] == 'g45'])
    expected_wedding = len([e for e in mapping_data['mapping'] if e['image_set'] == 'wedding'])

    actual_g42 = len(re.findall(r'images/book_images/book_g42_', html_str))
    actual_g45 = len(re.findall(r'images/book_images/book_g45_', html_str))
    actual_wedding = len(re.findall(r'images/book_images/wedding', html_str))

    log(f"\nולידציה ({lang.upper()}):")
    log(f"  g42:     {actual_g42:3d} (צפוי: {expected_g42})")
    log(f"  g45:     {actual_g45:3d} (צפוי: {expected_g45})")
    log(f"  wedding: {actual_wedding:3d} (צפוי: {expected_wedding})")
    log(f"  סה\"כ:   {actual_g42 + actual_g45 + actual_wedding:3d} (צפוי: 151)")

    return actual_g42 + actual_g45 + actual_wedding


def main():
    parser = argparse.ArgumentParser(description="Rebuild book_data.js with all 151 images from mapping")
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate without writing output file')
    parser.add_argument('--mapping', default=DEFAULT_MAPPING,
                        help=f'Path to mapping JSON (default: {DEFAULT_MAPPING})')
    parser.add_argument('--input', default=DEFAULT_INPUT,
                        help=f'Path to input book_data.js (default: {DEFAULT_INPUT})')
    parser.add_argument('--output', default=DEFAULT_OUTPUT,
                        help=f'Path to output file (default: {DEFAULT_OUTPUT})')
    args = parser.parse_args()

    log_path = setup_log_file()

    log("=" * 60)
    log("rebuild_book_images.py — שחזור תמונות הספר")
    log("=" * 60)
    log(f"Mapping: {args.mapping}")
    log(f"Input:   {args.input}")
    log(f"Output:  {args.output}")
    log(f"Dry-run: {args.dry_run}")
    log(f"Log:     {log_path}")
    log("=" * 60)

    # ─── שלב 1: קריאת קובץ המיפוי ───────────────────────────────────
    log("\n[1/4] קורא קובץ מיפוי...")
    if not os.path.exists(args.mapping):
        log(f"שגיאה: קובץ המיפוי {args.mapping} לא נמצא")
        sys.exit(1)

    with open(args.mapping, 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)

    log(f"  נטענו {len(mapping_data['mapping'])} רישומי תמונות")
    log(f"  גרסה: {mapping_data['meta']['version']}")
    log(f"  תאריך מקור: {mapping_data['meta']['date']}")

    # ─── שלב 2: קריאת book_data.js ──────────────────────────────────
    log("\n[2/4] קורא book_data.js...")
    if not os.path.exists(args.input):
        log(f"שגיאה: קובץ הקלט {args.input} לא נמצא")
        sys.exit(1)

    with open(args.input, 'r', encoding='utf-8') as f:
        bd = f.read()
    log(f"  קובץ נטען: {len(bd):,} bytes")

    # ─── שלב 3: עיבוד HE ו-EN ───────────────────────────────────────
    log("\n[3/4] מעבד את BOOK_HTML (עברית)...")
    he_match = re.search(r'(var BOOK_HTML = ")(.*?)(";\s*\nvar BOOK_HTML_EN)', bd, re.DOTALL)
    if not he_match:
        log("שגיאה: לא נמצא BOOK_HTML בקובץ")
        sys.exit(1)
    he_str = he_match.group(2)
    he_str_new = process_book_html(he_str, mapping_data, lang='he')
    he_count = validate_result(he_str_new, mapping_data, lang='he')

    log("\n[3/4] מעבד את BOOK_HTML_EN (אנגלית)...")
    en_match = re.search(r'(var BOOK_HTML_EN = ")(.*?)(";\s*\nvar BOOK_RECIPE_PHOTOS)', bd, re.DOTALL)
    if not en_match:
        log("שגיאה: לא נמצא BOOK_HTML_EN בקובץ")
        sys.exit(1)
    en_str = en_match.group(2)
    en_str_new = process_book_html(en_str, mapping_data, lang='en')
    en_count = validate_result(en_str_new, mapping_data, lang='en')

    # ─── שלב 4: שמירת תוצאה ─────────────────────────────────────────
    log("\n[4/4] בונה קובץ פלט...")
    new_bd = (bd[:he_match.start(2)] + he_str_new +
              bd[he_match.end(2):en_match.start(2)] + en_str_new +
              bd[en_match.end(2):])
    log(f"  גודל סופי: {len(new_bd):,} bytes")

    if args.dry_run:
        log("  --dry-run פעיל - לא נכתב קובץ")
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(new_bd)
        log(f"  נשמר: {args.output}")

    # ─── סיכום ─────────────────────────────────────────────────────
    log("\n" + "=" * 60)
    log("סיכום:")
    log(f"  HE: {he_count} תמונות")
    log(f"  EN: {en_count} תמונות")
    log(f"  קובץ פלט: {args.output}" + (" (dry-run, לא נשמר)" if args.dry_run else ""))
    log("=" * 60)

    if he_count != 151:
        log(f"\nאזהרה: HE מכיל {he_count} תמונות במקום 151!")
        sys.exit(2)

    log("\nהסקריפט הסתיים בהצלחה.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
