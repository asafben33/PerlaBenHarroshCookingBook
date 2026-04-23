"""
מטרת הסקריפט:
ספריית עזר משותפת לסקריפטים add_recipe.py ו-edit_recipe.py.
מספקת פונקציות לקריאה/כתיבה בטוחה של data.js, איתור מתכונים לפי ID,
הוספה/החלפה/מחיקה של מתכונים, וולידציה, לוגים, וממשק CLI בעברית.

Shared utilities for the Perla Cookbook recipe CLI scripts.
All code is in English; all user-facing text is in Hebrew (UTF-8).
"""

# ============================================================
# recipe_utils.py
# Shared library for add_recipe.py / edit_recipe.py
# ============================================================

import os
import re
import sys
import shutil
import datetime
import builtins
from pathlib import Path

# -----------------------------------------------------------
# Absolute project root — all scripts resolve paths from here
# -----------------------------------------------------------
PROJECT_ROOT    = Path(__file__).resolve().parent.parent
DEFAULT_DATA_JS = PROJECT_ROOT / 'data.js'
DEFAULT_LOG_DIR = PROJECT_ROOT / 'logs'

# -----------------------------------------------------------
# Windows terminal UTF-8 fix (for Hebrew rendering in cmd/PS)
# -----------------------------------------------------------
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# =============================================================
# RTL FIX — Hebrew bidirectional text for non-BiDi terminals
# =============================================================
# Windows CMD, PowerShell, and even Windows Terminal do NOT implement
# the Unicode Bidirectional Algorithm for program output. Hebrew
# strings printed via Python appear "mirrored" to a Hebrew reader.
# The fix: pre-reverse Hebrew runs before printing, so when the
# terminal draws the chars LTR without BiDi, the visual order
# matches what a Hebrew reader expects when scanning RTL.
# -----------------------------------------------------------
# Auto-detect: enabled on Windows by default; can be disabled
# via configure_rtl_fix(False) or --no-rtl-fix CLI flag.
# -----------------------------------------------------------
RTL_FIX_ENABLED = (sys.platform == 'win32')

_ANSI_RE = re.compile(r'\x1b\[[0-9;]*[mK]')

def _is_heb(ch):
    """True if char is in Hebrew Unicode blocks."""
    if not ch:
        return False
    code = ord(ch)
    return (0x0590 <= code <= 0x05FF) or (0xFB1D <= code <= 0xFB4F)

# Neutrals: punctuation/spaces that may appear inside a Hebrew sentence.
_HEB_NEUTRALS = set(' \t,.;:!?־—–…"\'״׳()[]{}\u2013\u2014\u00AB\u00BB/')

def _is_heb_neutral(ch):
    return ch in _HEB_NEUTRALS

def _rtl_fix_core(text):
    """
    Reverse Hebrew runs (incl. internal neutrals) in plain text.
    Leaves LTR-only runs (English/digits) intact.
    """
    if not text:
        return text
    n = len(text)
    out = []
    i = 0
    while i < n:
        if not _is_heb(text[i]):
            out.append(text[i])
            i += 1
            continue
        # Start of Hebrew run
        run_start = i
        last_heb = i
        j = i
        while j < n:
            ch = text[j]
            if _is_heb(ch):
                last_heb = j
                j += 1
            elif _is_heb_neutral(ch):
                # Peek past the neutral cluster
                k = j + 1
                while k < n and _is_heb_neutral(text[k]):
                    k += 1
                if k >= n:
                    # End of string: include trailing neutrals in the run
                    last_heb = k - 1
                    j = k
                elif _is_heb(text[k]):
                    # Gap between Hebrew words — include the neutrals
                    j = k
                elif text[k].isascii() and text[k].isalnum():
                    # Latin/digit follows — exclude the trailing neutrals
                    break
                else:
                    # Other non-Latin (control char, symbol) — include up to it
                    last_heb = k - 1
                    j = k
            else:
                break
        out.append(text[run_start:last_heb + 1][::-1])
        i = last_heb + 1
    return ''.join(out)

def rtl_fix(text):
    """
    Reverse Hebrew substrings for non-BiDi terminals, preserving ANSI codes.
    Splits the string at ANSI escape sequences, applies the core fix to each
    content segment, leaves ANSI segments untouched.
    """
    if not text or not RTL_FIX_ENABLED:
        return text
    if isinstance(text, (bytes, bytearray)):
        return text
    if not isinstance(text, str):
        text = str(text)

    # Fast path: no ANSI codes
    if '\x1b' not in text:
        return _rtl_fix_core(text)

    out = []
    last = 0
    for m in _ANSI_RE.finditer(text):
        if m.start() > last:
            out.append(_rtl_fix_core(text[last:m.start()]))
        out.append(m.group(0))   # ANSI passes through unchanged
        last = m.end()
    if last < len(text):
        out.append(_rtl_fix_core(text[last:]))
    return ''.join(out)

def configure_rtl_fix(enabled):
    """Explicitly enable/disable rtl_fix (overrides platform default)."""
    global RTL_FIX_ENABLED
    RTL_FIX_ENABLED = bool(enabled)

# -----------------------------------------------------------
# Monkey-patch print() and input() to apply rtl_fix transparently.
# Safe: only affects modules that import recipe_utils (i.e., our scripts).
# -----------------------------------------------------------
_orig_print = builtins.print
_orig_input = builtins.input

def _rtl_print(*args, **kwargs):
    if RTL_FIX_ENABLED:
        args = tuple(rtl_fix(a) if isinstance(a, str) else a for a in args)
    _orig_print(*args, **kwargs)

def _rtl_input(prompt=''):
    if RTL_FIX_ENABLED and isinstance(prompt, str):
        prompt = rtl_fix(prompt)
    return _orig_input(prompt)

builtins.print = _rtl_print
builtins.input = _rtl_input

# -----------------------------------------------------------
# Categories — mirror of CATS array in data.js
# -----------------------------------------------------------
CATEGORIES = [
    ('soups',     'מרקים'),
    ('salads',    'סלטים'),
    ('veg',       'תבשילי ירקות'),
    ('meat',      'בשר וקציצות'),
    ('chick',     'עוף ושבת'),
    ('fish',      'דגים'),
    ('hol',       'חגים ומועדים'),
    ('des',       'קינוחים ומאפים'),
    ('span',      'מורשת ספרד'),
    ('iraq',      'עיראק'),
    ('kurd',      'כורדיסטן'),
    ('ashk',      'אשכנז'),
    ('yem',       'תימן'),
    ('pers',      'פרס'),
    ('buk',       'בוכרה'),
    ('tun',       'טוניסיה'),
    ('isr',       'מטבח ישראלי'),
    ('turk',      'יהדות טורקיה'),
    ('nonkosher', 'מתכונים לא כשרים'),
]

CATEGORY_IDS  = [c[0] for c in CATEGORIES]
CATEGORY_DICT = dict(CATEGORIES)

DIFFICULTIES = ['קל', 'בינוני', 'מתקדם']  # v8.2: was 'קשה' but data.js uses 'מתקדם' across all 1054 recipes

# -----------------------------------------------------------
# ANSI colors (fall back silently if terminal doesn't support)
# -----------------------------------------------------------
class C:
    RESET  = '\033[0m'
    BOLD   = '\033[1m'
    DIM    = '\033[2m'
    RED    = '\033[91m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    BLUE   = '\033[94m'
    CYAN   = '\033[96m'
    GRAY   = '\033[90m'

def _color(code, text):
    return f"{code}{text}{C.RESET}"

def hdr(text):   return _color(C.BOLD + C.CYAN, text)
def ok(text):    return _color(C.GREEN, text)
def warn(text):  return _color(C.YELLOW, text)
def err(text):   return _color(C.RED, text)
def dim(text):   return _color(C.GRAY, text)

# -----------------------------------------------------------
# Logger — writes to file with DD-MM-YYYY_HH.MM timestamped name
# Also mirrors INFO/WARN/ERROR lines to console.
# -----------------------------------------------------------
class Logger:
    def __init__(self, script_name, log_dir='logs'):
        ts = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M')
        Path(log_dir).mkdir(exist_ok=True)
        self.path = Path(log_dir) / f"{script_name}_{ts}.log"
        self._fh = open(self.path, 'w', encoding='utf-8')
        self.info(f"=== Log started: {script_name} at {ts} ===")

    def _write(self, level, msg):
        line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {level}: {msg}"
        self._fh.write(line + '\n')
        self._fh.flush()

    def info(self, msg):  self._write('INFO',  msg)
    def warn(self, msg):  self._write('WARN',  msg); print(warn('[WARN] ' + msg))
    def error(self, msg): self._write('ERROR', msg); print(err('[FAIL] ' + msg))
    def step(self, msg):  self._write('STEP',  msg)

    def progress(self, pct, label):
        bar = '█' * (pct // 5) + '░' * (20 - pct // 5)
        print(f"  [{bar}] {pct:3d}%  {label}")
        self._write('PROG', f"{pct}% — {label}")

    def close(self):
        self.info("=== Log closed ===")
        self._fh.close()

# -----------------------------------------------------------
# Safe input helpers (Ctrl+C → clean exit)
# -----------------------------------------------------------
def ask(prompt, default='', required=False, validator=None, allow_empty_for_skip=False):
    """
    Prompt for input. Returns stripped string.
    - If default: shown in brackets; empty answer returns default.
    - If required: re-asks until non-empty.
    - If validator: callable(str) -> bool; re-asks on False.
    """
    while True:
        try:
            suffix = f" [{default}]" if default else ''
            raw = input(f"  {prompt}{suffix}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print('\n' + warn('בוטל על ידי המשתמש.'))
            sys.exit(1)

        if not raw and default:
            return default
        if not raw and allow_empty_for_skip:
            return ''
        if not raw and required:
            print(err('  שדה חובה — נא להזין ערך.'))
            continue
        if validator and raw and not validator(raw):
            print(err('  ערך לא תקין — נסה שוב.'))
            continue
        return raw

def ask_yes_no(prompt, default='n'):
    """Hebrew yes/no prompt (כ/ל)."""
    hint = 'כ/ל' if default == 'y' else 'כ/ל'
    while True:
        try:
            raw = input(f"  {prompt} ({hint}) [{default}]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print('\n' + warn('בוטל.'))
            sys.exit(1)
        if not raw:
            raw = default
        if raw in ('y', 'yes', 'כ', 'כן'):
            return True
        if raw in ('n', 'no', 'ל', 'לא'):
            return False
        print(err('  תשובה לא ברורה. כ = כן, ל = לא'))

def ask_choice(prompt, options, default_idx=None):
    """
    options: list of (value, label) tuples
    Returns selected value.
    """
    print(f"\n  {hdr(prompt)}")
    for i, (val, lbl) in enumerate(options, 1):
        marker = '●' if i - 1 == default_idx else ' '
        print(f"    {marker} {i:2d}. {val:<10s} — {lbl}")
    while True:
        try:
            raw = input(f"  הבחירה שלך [1-{len(options)}]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print('\n' + warn('בוטל.'))
            sys.exit(1)
        if not raw and default_idx is not None:
            return options[default_idx][0]
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(options):
                return options[n - 1][0]
        print(err(f'  יש להזין מספר בין 1 ל-{len(options)}.'))

# -----------------------------------------------------------
# data.js read/write with backup
# -----------------------------------------------------------
def load_data_js(path='data.js'):
    """Read data.js as UTF-8 text. Raises FileNotFoundError if missing."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"data.js not found at: {p.absolute()}")
    return p.read_text(encoding='utf-8')

def save_data_js(text, path='data.js', dry_run=False, logger=None):
    """
    Save text to data.js atomically, with a timestamped backup.
    If dry_run: writes to <path>.dryrun instead of overwriting.
    Returns the backup path (or dry-run path) for reporting.
    """
    p = Path(path)

    if dry_run:
        out = p.with_suffix('.js.dryrun')
        out.write_text(text, encoding='utf-8')
        if logger: logger.info(f"DRY-RUN output written to {out}")
        return out

    # Backup first
    ts = datetime.datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
    backup = p.with_suffix(f'.js.bak_{ts}')
    shutil.copy2(p, backup)
    if logger: logger.info(f"Backup created: {backup}")

    # Atomic write (write to tmp, then rename)
    tmp = p.with_suffix('.js.tmp')
    tmp.write_text(text, encoding='utf-8')
    tmp.replace(p)
    if logger: logger.info(f"Wrote {len(text):,} chars to {p}")
    return backup

# -----------------------------------------------------------
# Recipe parsing — locate and extract from data.js
# -----------------------------------------------------------
def find_recipe_bounds(text, recipe_id):
    """
    Locate the exact [start, end) slice of a recipe object in data.js.
    End includes the trailing comma (if any) and optionally one newline.
    Returns (start, end) or None if not found.
    """
    pattern = "{id:'" + recipe_id + "'"
    start = text.find(pattern)
    if start == -1:
        return None

    depth = 0
    in_str = False
    str_ch = None
    i = start
    n = len(text)

    while i < n:
        ch = text[i]
        if in_str:
            if ch == '\\' and i + 1 < n:
                i += 2
                continue
            if ch == str_ch:
                in_str = False
        else:
            if ch in ("'", '"'):
                in_str = True
                str_ch = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    if end < n and text[end] == ',':
                        end += 1
                    # Include one trailing newline if present
                    if end < n and text[end] == '\n':
                        end += 1
                    return (start, end)
        i += 1
    return None

def scan_all_recipes(text):
    """
    Return list of dicts: [{id, cat, title, offset}, ...]
    Used for search/list in edit_recipe.py.
    """
    recipes = []
    # Match {id:'...',cat:'...' — the consistent opening pattern
    for m in re.finditer(r"\{id:'([^']+)',cat:'([^']+)'", text):
        rid = m.group(1)
        cat = m.group(2)
        # Search title within next 800 chars
        window = text[m.end(): m.end() + 800]
        t = re.search(r"title:'((?:[^'\\]|\\.)*)'", window)
        title = t.group(1) if t else '?'
        recipes.append({
            'id':     rid,
            'cat':    cat,
            'title':  title,
            'offset': m.start(),
        })
    return recipes

def extract_recipe_fields(block_text):
    """
    Parse a single recipe JS object literal into a Python dict.
    Handles simple string fields + ingr/steps arrays.
    Returns a dict or raises ValueError on bad input.
    """
    def _field(name, text, default=None):
        # name:'value'  — value may contain escaped quotes (\')
        m = re.search(r"\b" + re.escape(name) + r":\s*'((?:[^'\\]|\\.)*)'", text)
        if m:
            return m.group(1).replace("\\'", "'")
        return default

    def _array_of_pairs(name, key_a, key_b, text):
        """Extract `name:[{key_a:'x',key_b:'y'},...]` → list of (x, y)."""
        # Find "name:["
        marker = name + ':['
        idx = text.find(marker)
        if idx == -1:
            return []
        # Find matching closing ']'
        depth = 0
        in_str = False
        str_ch = None
        j = idx + len(marker) - 1  # points at '['
        start_body = j + 1
        i = j
        n = len(text)
        while i < n:
            ch = text[i]
            if in_str:
                if ch == '\\' and i + 1 < n:
                    i += 2
                    continue
                if ch == str_ch:
                    in_str = False
            else:
                if ch in ("'", '"'):
                    in_str = True
                    str_ch = ch
                elif ch == '[':
                    depth += 1
                elif ch == ']':
                    depth -= 1
                    if depth == 0:
                        body = text[start_body: i]
                        break
            i += 1
        else:
            return []
        # Parse body: sequence of {key_a:'...',key_b:'...'}
        pairs = []
        pattern = (
            r"\{" + re.escape(key_a) + r":'((?:[^'\\]|\\.)*)'"
            r"\s*,\s*" + re.escape(key_b) + r":'((?:[^'\\]|\\.)*)'\s*\}"
        )
        for m in re.finditer(pattern, body):
            a = m.group(1).replace("\\'", "'")
            b = m.group(2).replace("\\'", "'")
            pairs.append((a, b))
        return pairs

    r = {
        'id':    _field('id',    block_text, ''),
        'cat':   _field('cat',   block_text, ''),
        'badge': _field('badge', block_text, ''),
        'title': _field('title', block_text, ''),
        'desc':  _field('desc',  block_text, ''),
        'time':  _field('time',  block_text, ''),
        'serv':  _field('serv',  block_text, ''),
        'diff':  _field('diff',  block_text, ''),
        'img':   _field('img',   block_text, ''),
        'src':   _field('src',   block_text, ''),
        'vid':   _field('vid',   block_text, ''),
        'mem':   _field('mem',   block_text, ''),
        'tip':   _field('tip',   block_text, ''),
        'ingr':  _array_of_pairs('ingr',  'q', 'i', block_text),
        'steps': _array_of_pairs('steps', 't', 's', block_text),
    }
    if not r['id'] or not r['cat']:
        raise ValueError("Failed to parse recipe: missing id or cat.")
    return r

# -----------------------------------------------------------
# Recipe serialization — dict → formatted JS text block
# -----------------------------------------------------------
def _esc(s):
    """Escape single quotes for JS string literal."""
    if s is None:
        return ''
    return str(s).replace('\\', '\\\\').replace("'", "\\'")

def format_recipe(r):
    """
    Build a JS recipe object literal matching the existing data.js style.
    Input dict fields: id, cat, badge, title, desc, time, serv, diff, img,
                       src, vid, mem, tip, ingr (list of (q,i)), steps (list of (t,s)).
    Empty optional fields are omitted.
    """
    out = []
    out.append("{id:'" + _esc(r['id']) + "',cat:'" + _esc(r['cat']) + "',")

    if r.get('badge'):
        out[-1] += "badge:'" + _esc(r['badge']) + "',"
    out[-1] += "title:'" + _esc(r['title']) + "',"

    # Second line: desc
    if r.get('desc'):
        out.append(" desc:'" + _esc(r['desc']) + "',")

    # Third line: time, serv, diff, img
    third = []
    if r.get('time'): third.append("time:'" + _esc(r['time']) + "'")
    if r.get('serv'): third.append("serv:'" + _esc(r['serv']) + "'")
    if r.get('diff'): third.append("diff:'" + _esc(r['diff']) + "'")
    if r.get('img'):  third.append("img:'"  + _esc(r['img'])  + "'")
    if third:
        out.append(' ' + ','.join(third) + ',')

    # Optional src/vid
    if r.get('src'):
        out.append(" src:'" + _esc(r['src']) + "',")
    if r.get('vid'):
        out.append(" vid:'" + _esc(r['vid']) + "',")

    # Memory
    if r.get('mem'):
        out.append(" mem:'" + _esc(r['mem']) + "',")

    # Ingredients
    if r.get('ingr'):
        out.append(' ingr:[')
        for q, i in r['ingr']:
            out.append("  {q:'" + _esc(q) + "',i:'" + _esc(i) + "'},")
        out.append(' ],')

    # Steps
    if r.get('steps'):
        out.append(' steps:[')
        for t, s in r['steps']:
            out.append("  {t:'" + _esc(t) + "',s:'" + _esc(s) + "'},")
        out.append(' ],')

    # Tip (must be last, no trailing comma on object close)
    if r.get('tip'):
        out.append(" tip:'" + _esc(r['tip']) + "'")
        out[-1] = out[-1]  # already last
        body = '\n'.join(out) + '},\n'
    else:
        # Remove trailing comma of last line, close object
        if out[-1].endswith(','):
            out[-1] = out[-1][:-1]
        body = '\n'.join(out) + '},\n'

    return body

# -----------------------------------------------------------
# High-level operations
# -----------------------------------------------------------
def inject_recipe(text, recipe_dict):
    """
    Insert a new recipe just before the closing `\n];\n` of the R array.
    Returns new text.
    """
    close_marker = '\n];\n'
    idx = text.rfind(close_marker)
    if idx == -1:
        # Try alternate endings
        close_marker = '\n];'
        idx = text.rfind(close_marker)
        if idx == -1:
            raise ValueError("Cannot locate closing `];` of recipe array in data.js")

    new_block = format_recipe(recipe_dict)
    # Ensure blank line before the new recipe for readability
    before = text[:idx]
    after  = text[idx:]
    if not before.endswith('\n\n'):
        if before.endswith('\n'):
            before = before + '\n'
        else:
            before = before + '\n\n'
    return before + new_block + after

def replace_recipe(text, recipe_id, new_recipe_dict):
    """Replace an existing recipe block in-place by ID."""
    bounds = find_recipe_bounds(text, recipe_id)
    if bounds is None:
        raise ValueError(f"Recipe ID '{recipe_id}' not found in data.js")
    start, end = bounds
    new_block = format_recipe(new_recipe_dict)
    return text[:start] + new_block + text[end:]

def delete_recipe(text, recipe_id):
    """Remove a recipe block entirely by ID."""
    bounds = find_recipe_bounds(text, recipe_id)
    if bounds is None:
        raise ValueError(f"Recipe ID '{recipe_id}' not found in data.js")
    start, end = bounds
    return text[:start] + text[end:]

def suggest_next_id(text, cat):
    """
    Suggest next numeric ID for a category.
    E.g., if cat='soups' and existing are s1..s42 → returns 's43'.
    Uses the same prefix convention as existing data.
    """
    prefix_map = {
        'soups':  's',
        'salads': 'sa',
        'veg':    'v',
        'meat':   'm',
        'chick':  'c',
        'fish':   'f',
        'hol':    'h',
        'des':    'd',
        'span':   'sp',
        'iraq':   'ir',
        'kurd':   'ku',
        'ashk':   'as',
        'yem':    'ye',
        'pers':   'pe',
        'buk':    'bu',
        'tun':    'tu',
        'isr':    'is',
        'turk':   'tr',
        'nonkosher': 'nk',
    }
    prefix = prefix_map.get(cat, cat[:2])
    # Find max numeric suffix among ids starting with prefix + digits
    pattern = re.compile(r"id:'" + re.escape(prefix) + r"(\d+)'")
    nums = [int(m.group(1)) for m in pattern.finditer(text)]
    next_n = (max(nums) + 1) if nums else 1
    return f"{prefix}{next_n}"

def id_exists(text, recipe_id):
    """Check if ID already used anywhere in data.js."""
    return ("id:'" + recipe_id + "'") in text

def title_exists(text, title):
    """Check if exact title already exists (duplicate prevention)."""
    # Escape for regex
    pat = r"title:'" + re.escape(title) + r"'"
    return bool(re.search(pat, text))

# -----------------------------------------------------------
# Pretty printing for previews
# -----------------------------------------------------------
def print_recipe_summary(r, prefix='  '):
    print(f"{prefix}{hdr('מזהה')}:      {r.get('id','?')}")
    print(f"{prefix}{hdr('קטגוריה')}:   {r.get('cat','?')}  ({CATEGORY_DICT.get(r.get('cat'), '?')})")
    if r.get('badge'):
        print(f"{prefix}{hdr('תג')}:        {r['badge']}")
    print(f"{prefix}{hdr('כותרת')}:     {r.get('title','?')}")
    if r.get('desc'):
        desc = r['desc'][:80] + ('…' if len(r['desc']) > 80 else '')
        print(f"{prefix}{hdr('תיאור')}:     {desc}")
    print(f"{prefix}{hdr('זמן')}:       {r.get('time','-')}  |  "
          f"{hdr('מנות')}: {r.get('serv','-')}  |  "
          f"{hdr('קושי')}: {r.get('diff','-')}")
    if r.get('mem'):
        mem = r['mem'][:100] + ('…' if len(r['mem']) > 100 else '')
        print(f"{prefix}{hdr('זיכרון')}:    {dim(mem)}")
    print(f"{prefix}{hdr('מרכיבים')}:   {len(r.get('ingr', []))}")
    print(f"{prefix}{hdr('שלבים')}:     {len(r.get('steps', []))}")
    if r.get('tip'):
        tip = r['tip'][:80] + ('…' if len(r['tip']) > 80 else '')
        print(f"{prefix}{hdr('טיפ')}:       {dim(tip)}")
