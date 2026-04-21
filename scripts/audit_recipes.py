"""
מטרת הסקריפט:
סקריפט ביקורת אוטומטי לכל המתכונים ב-data.js של אתר ספר הבישול של פרלה ז"ל.
סורק את כל 1,054 המתכונים ומסמן בעיות מכניות (שדות חסרים, שלבים קצרים,
כמויות מעורפלות, טקסט placeholder, כפילויות וכו') — ומייצר 3 סוגי דוחות:
JSON (למעבד אוטומטי), Markdown (לקריאה אנושית), ו-CSV (לטריאז' בגיליון).

**הסקריפט אינו מתקן מתכונים אוטומטית.** הוא רק מסמן לטריאז' ידני.
תיקון מתכונים ספציפיים ייעשה ב-edit_recipe.py אחד אחד.

Automated audit script for 1,054 recipes in data.js.
Scans for mechanical issues (missing fields, short steps, vague quantities,
placeholder text, duplicates, etc.) and produces 3 report types:
JSON (machine-readable), Markdown (human summary), CSV (spreadsheet triage).

**This script does NOT auto-fix recipes.** It only flags issues for human triage.
Fixing specific recipes is done one-at-a-time via edit_recipe.py.

Usage:
  python audit_recipes.py                       # Live scan + reports in ./audit_reports/
  python audit_recipes.py --dry-run             # Scan only, print summary; no files written
  python audit_recipes.py --only-category soups # Audit one category only
  python audit_recipes.py --severity high       # Only high-severity issues
  python audit_recipes.py --data ../data.js     # Custom data.js path
"""

# ============================================================
# audit_recipes.py — automated recipe quality audit
# ============================================================

import argparse
import csv
import datetime
import json
import os
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path

# Ensure local imports work even when run from a different directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from recipe_utils import (
    CATEGORIES, CATEGORY_DICT, DIFFICULTIES,
    Logger, load_data_js, scan_all_recipes, extract_recipe_fields,
    find_recipe_bounds,
    hdr, ok, warn, err, dim,
    configure_rtl_fix,
    PROJECT_ROOT, DEFAULT_DATA_JS,
)

# ============================================================
# Constants — audit thresholds and patterns
# ============================================================

# Default thresholds (can be overridden via CLI)
DEFAULT_MIN_INGR = 3        # Recipes with < 3 ingredients are suspect
DEFAULT_MIN_STEPS = 2       # Recipes with < 2 steps are suspect
DEFAULT_MIN_STEP_LEN = 20   # Steps shorter than 20 chars are suspect (stubs)
DEFAULT_MIN_DESC_LEN = 30   # Descriptions shorter than 30 chars are suspect
DEFAULT_MIN_MEM_LEN = 20    # Memory notes shorter than 20 chars are suspect

# Time validation (in minutes)
MIN_REASONABLE_TIME = 5     # Less than 5 min for a full recipe is suspect
# v8.2: raised from 720 (12hr) to 4320 (72hr) to accommodate legitimate
# brining/curing/fermentation times in Moroccan/Spanish/Yemeni traditional
# recipes (salted fish, pickled vegetables, wine yeast, etc.)
MAX_REASONABLE_TIME = 4320  # More than 72 hours is suspect

# Serving validation
MIN_REASONABLE_SERV = 1
MAX_REASONABLE_SERV = 50

# Placeholder / TODO patterns (Hebrew + English) — require explicit markers, not bare words
PLACEHOLDER_PATTERNS = [
    r'\bTODO\b',
    r'\bFIXME\b',
    r'\bXXX\b',
    r'\bTBD\b',
    r'(?:^|\s)\[\s*(?:לעדכן|לתקן|להשלים|חסר|TODO|FIXME)\s*\]',  # [לעדכן] markers
    r'(?:^|\s)(?:לעדכן|לתקן|להשלים):\s',                          # "לעדכן: " prefix
    r'\?\?\?\?',  # 4+ question marks
    r'X{4,}',     # XXXX sequences
]

# Vague ingredient quantity patterns
VAGUE_QUANTITY_PATTERNS = [
    r'^חופן$',           # Bare "handful" with no size
    r'^לטעם$',           # "To taste" only (fine sometimes, flagged for review)
    r'^כמות$',           # Bare "amount"
    r'^מספר$',           # Bare "number"
    r'^קצת$',            # Bare "a little"
    r'^גדול$',           # Bare "large" with no unit
    r'^בינוני$',         # Bare "medium" with no unit
    r'^קטן$',            # Bare "small" with no unit
    r'^לפי הצורך$',      # "As needed" with no guidance
]

# Known holiday tags (from HOLIDAY_TAGS in data.js)
KNOWN_HOLIDAYS = {
    'shabbat', 'rosh', 'kippur', 'pesach', 'mimouna',
    'hanukkah', 'purim', 'shavuot', 'sukkot', 'henna'
}

# Severity levels
SEVERITY_HIGH = 'high'     # Missing required fields, duplicates - breaks UI
SEVERITY_MEDIUM = 'medium' # Content issues - reduces recipe quality
SEVERITY_LOW = 'low'       # Minor - nice to have

# Progress milestones (percent)
PROGRESS_MILESTONES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


# ============================================================
# Issue class — one flagged problem per instance
# ============================================================

class Issue:
    """A single audit finding on one recipe."""
    __slots__ = ('recipe_id', 'cat', 'title', 'severity', 'code', 'field', 'detail')

    def __init__(self, recipe_id, cat, title, severity, code, field, detail):
        self.recipe_id = recipe_id
        self.cat = cat
        self.title = title
        self.severity = severity
        self.code = code         # Short machine-readable code (e.g., "missing_field")
        self.field = field       # Which field has the issue ("ingr", "time", etc.)
        self.detail = detail     # Human-readable detail in Hebrew

    def to_dict(self):
        return {
            'id':       self.recipe_id,
            'cat':      self.cat,
            'title':    self.title,
            'severity': self.severity,
            'code':     self.code,
            'field':    self.field,
            'detail':   self.detail,
        }

    def to_csv_row(self):
        return [
            self.recipe_id,
            self.cat,
            self.title,
            self.severity,
            self.code,
            self.field,
            self.detail,
        ]


# ============================================================
# Individual audit check functions
# ============================================================

def _time_to_minutes(time_str):
    """Parse 'time' field (e.g., '30 דקות', '1.5 שעות') to minutes, or None."""
    if not time_str:
        return None
    s = time_str.strip()
    # Hours
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:שעה|שעות|שע\'?)', s)
    if m:
        return int(float(m.group(1)) * 60)
    # Minutes
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:דק\'?|דקות|דקה)', s)
    if m:
        return int(float(m.group(1)))
    # Just a number — assume minutes
    m = re.search(r'^(\d+)$', s)
    if m:
        return int(m.group(1))
    return None


def _serv_to_number(serv_str):
    """Parse 'serv' field (e.g., '4 מנות', 'ל-6 אנשים') to int, or None.

    v8.2: Some recipes (preserves, spreads, condiments) intentionally use
    descriptive servings like "צנצנת גדולה" or "כלי קטן" because they're
    measured by container, not by individual portions. These return a sentinel
    value (-1) instead of None, so they pass validation without flagging.
    """
    if not serv_str:
        return None
    # Numeric extraction first
    m = re.search(r'(\d+)', serv_str)
    if m:
        return int(m.group(1))
    # Whitelist of valid container-based descriptors (preserves, spreads, condiments)
    container_descriptors = (
        'צנצנת', 'כלי', 'קופסה', 'בקבוק', 'כד',     # containers
        'מנה אחת', 'יחיד', 'קערה',                    # single-portion descriptors
        'מנה שמירה', 'גרניש', 'תבלין',               # preservation/garnish/seasoning batches
    )
    if any(desc in serv_str for desc in container_descriptors):
        return -1  # sentinel: valid non-numeric serving descriptor
    return None


def _has_hebrew(text):
    """Check if text contains any Hebrew characters."""
    if not text:
        return False
    return any(0x0590 <= ord(c) <= 0x05FF for c in text)


def _is_placeholder(text):
    """Check if text contains TODO/FIXME-style placeholder markers."""
    if not text:
        return False
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def check_required_fields(r):
    """HIGH: Required fields must be present and non-empty."""
    issues = []
    required = ['title', 'desc', 'time', 'serv', 'diff']
    for field in required:
        if not r.get(field) or not r[field].strip():
            issues.append(('missing_field', field, f'שדה "{field}" חסר או ריק'))
    # ingr and steps are lists
    if not r.get('ingr'):
        issues.append(('missing_field', 'ingr', 'רשימת מרכיבים ריקה לחלוטין'))
    if not r.get('steps'):
        issues.append(('missing_field', 'steps', 'רשימת שלבים ריקה לחלוטין'))
    return issues


def check_category_valid(r):
    """HIGH: Category must be a known one."""
    if r.get('cat') not in CATEGORY_DICT:
        return [('bad_category', 'cat', f'קטגוריה לא ידועה: "{r.get("cat")}"')]
    return []


def check_difficulty_valid(r):
    """MEDIUM: Difficulty must be one of the known values."""
    diff = r.get('diff', '').strip()
    if diff and diff not in DIFFICULTIES:
        return [('bad_difficulty', 'diff',
                 f'ערך קושי לא תקני: "{diff}" (מותר: {", ".join(DIFFICULTIES)})')]
    return []


def check_ingr_count(r, min_ingr):
    """MEDIUM: Too-few ingredients is suspect."""
    ingr_list = r.get('ingr', [])
    if 0 < len(ingr_list) < min_ingr:
        return [('few_ingredients', 'ingr',
                 f'רק {len(ingr_list)} מרכיבים (מומלץ לפחות {min_ingr})')]
    return []


def check_steps_count(r, min_steps):
    """MEDIUM: Too-few steps is suspect."""
    steps_list = r.get('steps', [])
    if 0 < len(steps_list) < min_steps:
        return [('few_steps', 'steps',
                 f'רק {len(steps_list)} שלבים (מומלץ לפחות {min_steps})')]
    return []


def check_step_lengths(r, min_step_len):
    """MEDIUM: Very short steps likely indicate stubs."""
    issues = []
    for idx, (_t, step_text) in enumerate(r.get('steps', []), start=1):
        if step_text and len(step_text) < min_step_len:
            issues.append(('short_step', f'steps[{idx}]',
                           f'שלב {idx} קצר מאוד ({len(step_text)} תווים): "{step_text[:40]}"'))
    return issues


def check_desc_length(r, min_desc_len):
    """LOW: Very short description."""
    desc = r.get('desc', '')
    if desc and len(desc) < min_desc_len:
        return [('short_desc', 'desc',
                 f'תיאור קצר מאוד ({len(desc)} תווים)')]
    return []


def check_mem_present(r, min_mem_len):
    """LOW: Memory note is valuable for memorial cookbook — flag if missing or stub."""
    mem = r.get('mem', '')
    if not mem or not mem.strip():
        return [('missing_mem', 'mem', 'הערת זיכרון (mem) חסרה')]
    if len(mem.strip()) < min_mem_len:
        return [('short_mem', 'mem',
                 f'הערת זיכרון קצרה מאוד ({len(mem.strip())} תווים)')]
    return []


def check_tip_present(r):
    """LOW: Tip is optional but valuable — flag if missing (info only)."""
    tip = r.get('tip', '')
    if not tip or not tip.strip():
        return [('missing_tip', 'tip', 'טיפ (tip) חסר')]
    return []


def check_vague_quantities(r):
    """MEDIUM: Bare vague quantity words without specifics."""
    issues = []
    for idx, (qty, ingr_name) in enumerate(r.get('ingr', []), start=1):
        if not qty:
            issues.append(('empty_quantity', f'ingr[{idx}]',
                           f'כמות ריקה ל-"{ingr_name}"'))
            continue
        qty_stripped = qty.strip()
        for pat in VAGUE_QUANTITY_PATTERNS:
            if re.match(pat, qty_stripped):
                issues.append(('vague_quantity', f'ingr[{idx}]',
                               f'כמות מעורפלת: "{qty_stripped}" (עבור "{ingr_name}")'))
                break
    return issues


def check_time_reasonable(r):
    """LOW: Very short or very long time values are suspect."""
    minutes = _time_to_minutes(r.get('time', ''))
    if minutes is None:
        return [('unparseable_time', 'time',
                 f'לא הצלחתי לפענח את ערך הזמן: "{r.get("time", "")}"')]
    issues = []
    if minutes < MIN_REASONABLE_TIME:
        issues.append(('suspicious_time', 'time',
                       f'זמן קצר מאוד: {minutes} דקות ({r.get("time", "")})'))
    elif minutes > MAX_REASONABLE_TIME:
        issues.append(('suspicious_time', 'time',
                       f'זמן ארוך מאוד: {minutes} דקות ({r.get("time", "")})'))
    return issues


def check_serv_reasonable(r):
    """LOW: Very small or very large serving counts."""
    serv = _serv_to_number(r.get('serv', ''))
    if serv is None:
        return [('unparseable_serv', 'serv',
                 f'לא הצלחתי לפענח את מספר המנות: "{r.get("serv", "")}"')]
    if serv == -1:
        return []  # v8.2: valid container-based descriptor (jar/bowl/etc.)
    if serv < MIN_REASONABLE_SERV or serv > MAX_REASONABLE_SERV:
        return [('suspicious_serv', 'serv',
                 f'מספר מנות חריג: {serv} ({r.get("serv", "")})')]
    return []


def check_placeholder_text(r):
    """MEDIUM: Detect TODO/FIXME/לעדכן markers in any text field."""
    issues = []
    for field in ['title', 'desc', 'mem', 'tip']:
        val = r.get(field, '')
        if _is_placeholder(val):
            issues.append(('placeholder_text', field,
                           f'שדה "{field}" מכיל טקסט placeholder: "{val[:60]}"'))
    # Check in steps too
    for idx, (_t, step_text) in enumerate(r.get('steps', []), start=1):
        if _is_placeholder(step_text):
            issues.append(('placeholder_text', f'steps[{idx}]',
                           f'שלב {idx} מכיל placeholder: "{step_text[:60]}"'))
    # Check in ingr
    for idx, (qty, ingr_name) in enumerate(r.get('ingr', []), start=1):
        if _is_placeholder(qty) or _is_placeholder(ingr_name):
            issues.append(('placeholder_text', f'ingr[{idx}]',
                           f'מרכיב {idx} מכיל placeholder: "{qty} {ingr_name}"'))
    return issues


def check_hebrew_content(r):
    """MEDIUM: Recipe should have Hebrew in text fields (title, desc at minimum)."""
    issues = []
    for field in ['title', 'desc']:
        val = r.get(field, '')
        if val and not _has_hebrew(val):
            issues.append(('no_hebrew', field,
                           f'שדה "{field}" אינו מכיל עברית: "{val[:60]}"'))
    return issues


def check_image_path(r):
    """LOW: Image should match r-{id}.jpg convention (informational)."""
    img = r.get('img', '')
    recipe_id = r.get('id', '')
    if img and recipe_id:
        expected_pattern = f'r-{recipe_id}.'
        if expected_pattern not in img and 'cat-' not in img:
            return [('image_naming', 'img',
                     f'שם קובץ לא תואם לקונבנציה: "{img}" (צפוי: r-{recipe_id}.jpg)')]
    return []


# ============================================================
# Main audit loop
# ============================================================

# Severity ranking — used to organize output by severity
CODE_SEVERITY = {
    'missing_field':      SEVERITY_HIGH,
    'bad_category':       SEVERITY_HIGH,
    'duplicate_id':       SEVERITY_HIGH,
    'placeholder_text':   SEVERITY_MEDIUM,
    'bad_difficulty':     SEVERITY_MEDIUM,
    'few_ingredients':    SEVERITY_MEDIUM,
    'few_steps':          SEVERITY_MEDIUM,
    'short_step':         SEVERITY_MEDIUM,
    'empty_quantity':     SEVERITY_MEDIUM,
    'vague_quantity':     SEVERITY_MEDIUM,
    'no_hebrew':          SEVERITY_MEDIUM,
    'short_desc':         SEVERITY_LOW,
    'missing_mem':        SEVERITY_LOW,
    'short_mem':          SEVERITY_LOW,
    'missing_tip':        SEVERITY_LOW,
    'unparseable_time':   SEVERITY_LOW,
    'suspicious_time':    SEVERITY_LOW,
    'unparseable_serv':   SEVERITY_LOW,
    'suspicious_serv':    SEVERITY_LOW,
    'image_naming':       SEVERITY_LOW,
}


def audit_single_recipe(r, cfg):
    """Run all checks on a single recipe. Return list of Issue objects."""
    all_issues = []
    rid = r.get('id', '?')
    cat = r.get('cat', '?')
    title = r.get('title', '?')

    check_funcs = [
        lambda: check_required_fields(r),
        lambda: check_category_valid(r),
        lambda: check_difficulty_valid(r),
        lambda: check_ingr_count(r, cfg['min_ingr']),
        lambda: check_steps_count(r, cfg['min_steps']),
        lambda: check_step_lengths(r, cfg['min_step_len']),
        lambda: check_desc_length(r, cfg['min_desc_len']),
        lambda: check_mem_present(r, cfg['min_mem_len']),
        lambda: check_tip_present(r) if cfg['include_tip_check'] else [],
        lambda: check_vague_quantities(r),
        lambda: check_time_reasonable(r),
        lambda: check_serv_reasonable(r),
        lambda: check_placeholder_text(r),
        lambda: check_hebrew_content(r),
        lambda: check_image_path(r) if cfg['include_image_check'] else [],
    ]

    for fn in check_funcs:
        try:
            for (code, field, detail) in fn():
                sev = CODE_SEVERITY.get(code, SEVERITY_LOW)
                all_issues.append(Issue(rid, cat, title, sev, code, field, detail))
        except Exception as e:
            all_issues.append(Issue(rid, cat, title, SEVERITY_LOW,
                                    'audit_error', '*',
                                    f'שגיאה בבדיקה: {e}'))
    return all_issues


def audit_all_recipes(recipes_meta, data_text, cfg, logger):
    """
    Run audit on all recipes. Yields milestone progress.
    Returns: (all_issues, stats).
    """
    all_issues = []
    stats = {
        'total':          0,
        'with_issues':    0,
        'issues_by_sev':  {SEVERITY_HIGH: 0, SEVERITY_MEDIUM: 0, SEVERITY_LOW: 0},
        'issues_by_code': Counter(),
        'issues_by_cat':  defaultdict(int),
    }

    # Check for duplicate IDs first (global check)
    id_counts = Counter(r['id'] for r in recipes_meta)
    duplicates = {rid for rid, c in id_counts.items() if c > 1}
    for rid in duplicates:
        # Emit one issue per duplicate instance
        for r in recipes_meta:
            if r['id'] == rid:
                iss = Issue(rid, r['cat'], r['title'], SEVERITY_HIGH,
                            'duplicate_id', 'id',
                            f'מזהה כפול: "{rid}" מופיע יותר מפעם אחת ב-data.js')
                all_issues.append(iss)

    if duplicates:
        logger.warn(f'[!] נמצאו {len(duplicates)} מזהים כפולים: {", ".join(sorted(duplicates))}')

    # Per-recipe checks
    total = len(recipes_meta)
    stats['total'] = total
    next_milestone_idx = 0

    for i, meta in enumerate(recipes_meta):
        # Filter by category if requested
        if cfg['only_category'] and meta['cat'] != cfg['only_category']:
            continue

        # Extract full recipe
        try:
            bounds = find_recipe_bounds(data_text, meta['id'])
            if not bounds:
                logger.warn(f'  [skip] לא הצלחתי לאתר גבולות של המתכון {meta["id"]}')
                continue
            block_text = data_text[bounds[0]:bounds[1]]
            r = extract_recipe_fields(block_text)
        except Exception as e:
            iss = Issue(meta['id'], meta['cat'], meta['title'], SEVERITY_HIGH,
                        'parse_error', '*',
                        f'שגיאת פענוח: {e}')
            all_issues.append(iss)
            continue

        # Run all checks on this recipe
        issues = audit_single_recipe(r, cfg)
        all_issues.extend(issues)
        if issues:
            stats['with_issues'] += 1
            stats['issues_by_cat'][meta['cat']] += 1

        # Progress milestones
        pct = int((i + 1) / total * 100)
        while (next_milestone_idx < len(PROGRESS_MILESTONES) and
               pct >= PROGRESS_MILESTONES[next_milestone_idx]):
            logger.info(f'  ... התקדמות: {PROGRESS_MILESTONES[next_milestone_idx]}% ({i+1}/{total})')
            next_milestone_idx += 1

    # Aggregate stats on all issues
    for iss in all_issues:
        stats['issues_by_sev'][iss.severity] += 1
        stats['issues_by_code'][iss.code] += 1

    return all_issues, stats


# ============================================================
# Report generation
# ============================================================

def _timestamp_suffix():
    """DD-MM-YYYY_HH.MM format per project preferences."""
    return datetime.datetime.now().strftime('%d-%m-%Y_%H.%M')


def write_json_report(issues, stats, out_path, logger):
    """Machine-readable JSON report."""
    data = {
        'generated_at': datetime.datetime.now().isoformat(timespec='seconds'),
        'version':      'audit_recipes.py v1.0',
        'stats':        {
            'total_recipes':       stats['total'],
            'recipes_with_issues': stats['with_issues'],
            'issues_total':        len(issues),
            'issues_by_severity':  dict(stats['issues_by_sev']),
            'issues_by_code':      dict(stats['issues_by_code']),
            'issues_by_category':  dict(stats['issues_by_cat']),
        },
        'issues': [iss.to_dict() for iss in issues],
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f'[✓] דו"ח JSON נכתב: {out_path}')


def write_csv_report(issues, out_path, logger):
    """Spreadsheet-friendly CSV (UTF-8 BOM for Excel)."""
    with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'category', 'title', 'severity', 'code', 'field', 'detail'])
        for iss in issues:
            writer.writerow(iss.to_csv_row())
    logger.info(f'[✓] דו"ח CSV נכתב: {out_path}')


def write_markdown_report(issues, stats, out_path, cfg, logger):
    """Human-readable markdown summary."""
    lines = []
    lines.append('# דו"ח ביקורת אוטומטי — ספר הבישול של פרלה ז"ל')
    lines.append('')
    lines.append(f'**נוצר:** {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}')
    lines.append(f'**סקריפט:** `audit_recipes.py v1.0`')
    lines.append(f'**קובץ מקור:** `{cfg["data_path"]}`')
    if cfg['only_category']:
        lines.append(f'**פילטר קטגוריה:** {cfg["only_category"]} ({CATEGORY_DICT.get(cfg["only_category"], "?")})')
    lines.append('')
    lines.append('## סיכום כללי')
    lines.append('')
    lines.append(f'- **סה"כ מתכונים שנסרקו:** {stats["total"]}')
    lines.append(f'- **מתכונים עם בעיות כלשהן:** {stats["with_issues"]} ({100*stats["with_issues"]/max(stats["total"],1):.1f}%)')
    lines.append(f'- **סה"כ בעיות שסומנו:** {len(issues)}')
    lines.append('')
    lines.append('## חלוקה לפי חומרה')
    lines.append('')
    lines.append('| חומרה | מספר בעיות | תיאור |')
    lines.append('|---|---|---|')
    lines.append(f'| 🔴 HIGH   | {stats["issues_by_sev"][SEVERITY_HIGH]} | שדות חובה חסרים, כפילויות — שובר ממשק |')
    lines.append(f'| 🟡 MEDIUM | {stats["issues_by_sev"][SEVERITY_MEDIUM]} | בעיות תוכן — מפחית איכות |')
    lines.append(f'| 🟢 LOW    | {stats["issues_by_sev"][SEVERITY_LOW]} | זוטות — נחמד לתקן |')
    lines.append('')

    # Issues by code
    lines.append('## חלוקה לפי סוג בעיה')
    lines.append('')
    lines.append('| קוד | חומרה | מספר מופעים |')
    lines.append('|---|---|---|')
    for code, count in stats['issues_by_code'].most_common():
        sev = CODE_SEVERITY.get(code, SEVERITY_LOW)
        emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(sev, '')
        lines.append(f'| `{code}` | {emoji} {sev} | {count} |')
    lines.append('')

    # Issues by category
    lines.append('## חלוקה לפי קטגוריה')
    lines.append('')
    lines.append('| קטגוריה | מתכונים עם בעיות |')
    lines.append('|---|---|')
    for cat_id in sorted(stats['issues_by_cat'], key=lambda c: -stats['issues_by_cat'][c]):
        lbl = CATEGORY_DICT.get(cat_id, cat_id)
        lines.append(f'| {cat_id} ({lbl}) | {stats["issues_by_cat"][cat_id]} |')
    lines.append('')

    # Top-N issues by severity
    by_sev = defaultdict(list)
    for iss in issues:
        by_sev[iss.severity].append(iss)

    for sev, label, emoji in [
        (SEVERITY_HIGH,   'בעיות דחופות — HIGH',   '🔴'),
        (SEVERITY_MEDIUM, 'בעיות תוכן — MEDIUM',   '🟡'),
        (SEVERITY_LOW,    'זוטות — LOW',           '🟢'),
    ]:
        sev_issues = by_sev[sev]
        if not sev_issues:
            continue
        lines.append(f'## {emoji} {label} ({len(sev_issues)} בעיות)')
        lines.append('')
        # Show up to 50 per severity (full list is in CSV/JSON)
        shown = sev_issues[:50]
        for iss in shown:
            lines.append(f'- **[{iss.recipe_id}]** `{iss.cat}` — *{iss.title}*')
            lines.append(f'  - `{iss.code}` ({iss.field}): {iss.detail}')
        if len(sev_issues) > 50:
            lines.append(f'')
            lines.append(f'*...ועוד {len(sev_issues) - 50} בעיות ברמה זו. הרשימה המלאה ב-CSV/JSON.*')
        lines.append('')

    lines.append('---')
    lines.append('')
    lines.append('## הוראות המשך')
    lines.append('')
    lines.append('1. **תיקון High:** השתמש ב-`edit_recipe.py --id <ID>` לתיקון מתכון אחד בכל פעם.')
    lines.append('2. **טריאז\' Medium:** פתח את ה-CSV ב-Excel/Sheets, מיין לפי `code`, וטפל בקבוצה.')
    lines.append('3. **Low:** טפל לפי הצורך — אלה לא חוסמות שום דבר.')
    lines.append('')
    lines.append('**הערה:** הסקריפט *אינו* מתקן אוטומטית. כל תיקון ייעשה ידנית דרך `edit_recipe.py`.')
    lines.append('')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    logger.info(f'[✓] דו"ח Markdown נכתב: {out_path}')


# ============================================================
# CLI entry point
# ============================================================

def parse_args():
    p = argparse.ArgumentParser(
        description='סקריפט ביקורת אוטומטי למתכונים ב-data.js.'
    )
    p.add_argument('--data', default=str(DEFAULT_DATA_JS),
                   help='נתיב ל-data.js (ברירת מחדל: PROJECT_ROOT/data.js)')
    p.add_argument('-n', '--dry-run', action='store_true',
                   help='הרצה ללא כתיבת קבצים — רק סיכום ל-stdout')
    p.add_argument('--out-dir', default=str(PROJECT_ROOT / 'audit_reports'),
                   help='תיקיית פלט לדוחות (ברירת מחדל: PROJECT_ROOT/audit_reports/)')
    p.add_argument('--only-category',
                   help='סריקה של קטגוריה יחידה בלבד (למשל: soups)')
    p.add_argument('--severity', choices=['high', 'medium', 'low', 'all'], default='all',
                   help='סנן פלט לפי חומרה (ברירת מחדל: all)')
    p.add_argument('--min-ingr', type=int, default=DEFAULT_MIN_INGR,
                   help=f'סף מינימלי למרכיבים (ברירת מחדל: {DEFAULT_MIN_INGR})')
    p.add_argument('--min-steps', type=int, default=DEFAULT_MIN_STEPS,
                   help=f'סף מינימלי לשלבים (ברירת מחדל: {DEFAULT_MIN_STEPS})')
    p.add_argument('--min-step-len', type=int, default=DEFAULT_MIN_STEP_LEN,
                   help=f'אורך מינימלי לשלב (ברירת מחדל: {DEFAULT_MIN_STEP_LEN} תווים)')
    p.add_argument('--min-desc-len', type=int, default=DEFAULT_MIN_DESC_LEN,
                   help=f'אורך מינימלי לתיאור (ברירת מחדל: {DEFAULT_MIN_DESC_LEN} תווים)')
    p.add_argument('--min-mem-len', type=int, default=DEFAULT_MIN_MEM_LEN,
                   help=f'אורך מינימלי להערת זיכרון (ברירת מחדל: {DEFAULT_MIN_MEM_LEN} תווים)')
    p.add_argument('--skip-tip-check', action='store_true',
                   help='דלג על בדיקת שדה tip (מפחית רעש)')
    p.add_argument('--include-image-check', action='store_true',
                   help='הפעל בדיקת שמות קבצי תמונות (ברירת מחדל: כבוי — הרוץ-טיים מתעלם מ-r.img)')
    p.add_argument('--no-rtl-fix', action='store_true',
                   help='בטל את ה-RTL fix (עבור טרמינלים שתומכים ב-BiDi)')
    return p.parse_args()


def main():
    args = parse_args()
    if args.no_rtl_fix:
        configure_rtl_fix(False)

    # Setup logger — Logger takes script_name and builds logs/{name}_{ts}.log itself
    logger = Logger('audit_recipes')

    # Helper wrappers — Logger.info doesn't print to stdout; we also want console output
    def log_info(msg, console=True):
        logger.info(msg)
        if console:
            print(msg)

    def log_head(msg):
        logger.info(msg)
        print(hdr(msg))

    log_head('═══════════════════════════════════════════════════════════')
    log_head(f'  audit_recipes.py v1.0 — ביקורת מתכונים    ({datetime.datetime.now().strftime("%d/%m/%Y %H:%M")})')
    log_head('═══════════════════════════════════════════════════════════')
    log_info('')
    log_info(f'  קובץ נתונים: {args.data}')
    log_info(f'  יעד דוחות:   {args.out_dir}')
    log_info(f'  סף מרכיבים:  {args.min_ingr}')
    log_info(f'  סף שלבים:    {args.min_steps}')
    log_info(f'  סף אורך שלב: {args.min_step_len} תווים')
    if args.only_category:
        log_info(f'  פילטר קטגוריה: {args.only_category}')
    if args.dry_run:
        log_info(warn('  *** Dry-run mode — לא ייכתבו קבצי דוח ***'))
    log_info('')

    # Load data.js
    try:
        data_text = load_data_js(args.data)
    except FileNotFoundError:
        logger.error(f'לא נמצא קובץ: {args.data}')
        logger.close()
        return 2
    except Exception as e:
        logger.error(f'שגיאה בקריאת {args.data}: {e}')
        logger.close()
        return 2

    # Scan all recipe IDs
    log_info(dim('  סורק את כל המתכונים ב-data.js...'))
    recipes_meta = scan_all_recipes(data_text)
    log_info(f'  נמצאו {len(recipes_meta)} מתכונים.')
    log_info('')

    if not recipes_meta:
        logger.error('לא נמצאו מתכונים לסרוק.')
        logger.close()
        return 1

    # Validate only-category arg
    if args.only_category:
        if args.only_category not in CATEGORY_DICT:
            logger.error(f'קטגוריה לא ידועה: {args.only_category}')
            log_info(f'  קטגוריות זמינות: {", ".join(cat for cat, _ in CATEGORIES)}')
            logger.close()
            return 2

    # Configure audit
    cfg = {
        'data_path':           args.data,
        'min_ingr':            args.min_ingr,
        'min_steps':           args.min_steps,
        'min_step_len':        args.min_step_len,
        'min_desc_len':        args.min_desc_len,
        'min_mem_len':         args.min_mem_len,
        'only_category':       args.only_category,
        'include_tip_check':   not args.skip_tip_check,
        'include_image_check': args.include_image_check,
    }

    # Build a LoggerProxy that prints info to console for the audit loop
    class LoggerProxy:
        def info(self, m):  log_info(m)
        def warn(self, m):  logger.warn(m)
        def error(self, m): logger.error(m)
    logger_proxy = LoggerProxy()

    # Run audit
    log_head('  מתחיל ביקורת...')
    issues, stats = audit_all_recipes(recipes_meta, data_text, cfg, logger_proxy)
    log_info(ok('  ✓ הביקורת הושלמה.'))
    log_info('')

    # Filter by severity if requested
    if args.severity != 'all':
        issues = [i for i in issues if i.severity == args.severity]
        log_info(f'  סונן לחומרה "{args.severity}": {len(issues)} בעיות נשארו.')
        log_info('')

    # Print summary to console
    log_head('═══ סיכום ═══')
    log_info(f'  סה"כ מתכונים:           {stats["total"]}')
    log_info(f'  מתכונים עם בעיות:       {stats["with_issues"]}')
    log_info(f'  סה"כ בעיות סומנו:       {len(issues)}')
    log_info('')
    log_info(f'  🔴 HIGH   (חובה לתקן): {stats["issues_by_sev"][SEVERITY_HIGH]:>5}')
    log_info(f'  🟡 MEDIUM (תוכן):       {stats["issues_by_sev"][SEVERITY_MEDIUM]:>5}')
    log_info(f'  🟢 LOW    (זוטות):      {stats["issues_by_sev"][SEVERITY_LOW]:>5}')
    log_info('')

    top_codes = stats['issues_by_code'].most_common(10)
    if top_codes:
        log_head('  10 סוגי הבעיות הנפוצים:')
        for code, cnt in top_codes:
            sev = CODE_SEVERITY.get(code, SEVERITY_LOW)
            log_info(f'    [{sev:<6}] {code:<25} {cnt}')
        log_info('')

    # Write reports (unless dry-run)
    if args.dry_run:
        log_info(warn('  Dry-run: לא נכתבו קבצי דוח.'))
    else:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(exist_ok=True)
        ts = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M')
        base = f'audit_report_{ts}'
        json_path = out_dir / f'{base}.json'
        csv_path  = out_dir / f'{base}.csv'
        md_path   = out_dir / f'{base}.md'

        write_json_report(issues, stats, json_path, logger_proxy)
        write_csv_report(issues, csv_path, logger_proxy)
        write_markdown_report(issues, stats, md_path, cfg, logger_proxy)

    log_info('')
    log_head('═══════════════════════════════════════════════════════════')
    log_info(ok(f'[✓] הביקורת הסתיימה. לוג: {logger.path}'))
    log_head('═══════════════════════════════════════════════════════════')
    logger.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
