#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_videos.py — Perla Ben-Harrosh z"l Cookbook  (v1.0)
=======================================================================
מטרת הסקריפט (עברית):
  סריקה אוטומטית של data.js וזיהוי מתכונים שאין להם קישור וידאו (vid:).
  עבור כל מתכון כזה — חיפוש בYouTube באמצעות שם המתכון + "מתכון" בעברית
  ולחילופין באנגלית, ושמירה של קישור YouTube הראשון שמתקבל.

  עדיפות:
    1. חיפוש עברית: "מתכון ל" + שם המתכון
    2. חיפוש אנגלית: "recipe " + transliterated name (במידה ויש)

  הסקריפט תומך באותו proxy auto-detection של download_images.py.
  Output: data.js מעודכן עם vid: 'https://www.youtube.com/watch?v=XXX' לכל מתכון
  שבו נמצא וידאו רלוונטי. אם לא נמצא — שדה ה-vid לא נוסף.

עדכוני אינדקס (v1.0):
  • תואם data.js v8.4 (1054 מתכונים)
  • משתמש ב-MENU_STRUCTURE v8.0 (מרוקו\\ספרד מאוחד, 9 עדות, 0 בעיות בביקורת)

Usage:
    python find_videos.py                          # מצב dry-run אוטומטי לפני קוד אמיתי
    python find_videos.py --dry-run                # רק סקירה, לא משנה data.js
    python find_videos.py --apply                  # מבצע שינויים ב-data.js
    python find_videos.py --apply --max 50         # מגביל ל-50 מתכונים בלבד (בדיקה)
    python find_videos.py --apply --only soups     # מגביל לקטגוריה אחת
    python find_videos.py --apply --overwrite      # מחליף vid: גם אם כבר קיים
    python find_videos.py --no-proxy               # ללא proxy
    python find_videos.py --proxy URL              # proxy ידני

Requirements: pip install requests
Log: SCRIPT_DIR/logs/find_videos_DD-MM-YYYY_HH.MM.log
"""
import os, re, sys, json, time, signal, argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from urllib.error import URLError

# ── Hebrew RTL fix for Windows PowerShell ──
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.system('chcp 65001 >nul 2>&1')

SCRIPT_DIR    = Path(__file__).resolve().parent
PROJECT_ROOT  = SCRIPT_DIR.parent
DATA_FILE     = PROJECT_ROOT / 'data.js'
LOG_DIR       = PROJECT_ROOT / 'logs'

_STOP = False

def _sigint(sig, frame):
    global _STOP
    _STOP = True
    print("\n[!] Ctrl+C — finishing current recipe and exiting safely...", flush=True)

signal.signal(signal.SIGINT, _sigint)

LOG_FILE = None

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    if LOG_FILE:
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
        except Exception:
            pass


# ══════════════════════════════════════════════════════════
# Proxy auto-detection (same as download_images.py)
# ══════════════════════════════════════════════════════════
PROXY = None

def _setup_proxy(args):
    """Apply proxy: --no-proxy, --proxy, or auto-detect from environment."""
    global PROXY
    if getattr(args, 'no_proxy', False):
        PROXY = None
        log("[proxy] mode: --no-proxy (direct connection)")
        return
    if getattr(args, 'proxy', None):
        PROXY = args.proxy
        log(f"[proxy] mode: --proxy {PROXY}")
        return
    # Try environment first
    for var in ('HTTPS_PROXY', 'HTTP_PROXY', 'https_proxy', 'http_proxy'):
        v = os.environ.get(var)
        if v:
            PROXY = v
            log(f"[proxy] from env {var}: {PROXY}")
            return
    # Try proxy_config.txt (left by download_images.py auto-detection)
    cfg = PROJECT_ROOT / 'proxy_config.txt'
    if cfg.exists():
        try:
            txt = cfg.read_text(encoding='utf-8').strip()
            if txt:
                PROXY = txt.split('\n')[0].strip()
                log(f"[proxy] from proxy_config.txt: {PROXY}")
                return
        except Exception:
            pass
    # Israeli government default
    PROXY = "http://proxy.gov.il:8080"
    log(f"[proxy] default fallback: {PROXY}")


def _http_get(url, timeout=10):
    """Fetch URL via configured proxy. Returns response text or None on error."""
    try:
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "he,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        if PROXY:
            from urllib.request import ProxyHandler, build_opener
            opener = build_opener(ProxyHandler({'http': PROXY, 'https': PROXY}))
            r = opener.open(req, timeout=timeout)
        else:
            r = urlopen(req, timeout=timeout)
        return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None


# ══════════════════════════════════════════════════════════
# YouTube video search
# ══════════════════════════════════════════════════════════
def search_youtube_video(title_he, title_en_query=None):
    """Search YouTube and extract the FIRST video ID from results.

    Returns: 'https://www.youtube.com/watch?v=XXXXXX' or None.

    Strategy:
      1. Search Hebrew: "מתכון ל" + title_he
      2. If no result: Search English: title_en_query + " recipe"

    YouTube's HTML response embeds video IDs in JSON within the page.
    We extract them via regex (no API key needed, works against the public page).
    """
    queries = []
    if title_he:
        # Strip recipe word if present (avoid double "מתכון מתכון")
        clean = title_he.replace('מתכון ל', '').replace('מתכון', '').strip()
        queries.append("מתכון ל" + clean if clean else title_he)
    if title_en_query:
        queries.append(title_en_query + " recipe")

    for q in queries:
        url = "https://www.youtube.com/results?search_query=" + quote_plus(q)
        html = _http_get(url, timeout=10)
        if not html:
            continue

        # YouTube embeds video IDs in patterns like:
        #   {"videoRenderer":{"videoId":"abc123XYZ-_"
        # We grab the FIRST organic result, skipping ads and shorts where possible.
        ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)

        # Filter out Shorts (we want full recipes, not 15-second clips).
        # Shorts have a separate "shortsLockupViewModel" pattern.
        shorts = set(re.findall(r'shortsLockupViewModel.*?"videoId":"([a-zA-Z0-9_-]{11})"', html))

        # Get first non-Shorts video
        for vid in ids:
            if vid not in shorts:
                # Extra sanity: ID must be 11 chars alphanumeric/_/- (YouTube spec)
                if len(vid) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', vid):
                    return f"https://www.youtube.com/watch?v={vid}"

        # If only Shorts exist, return the first Short anyway (better than nothing)
        if ids:
            return f"https://www.youtube.com/watch?v={ids[0]}"

    return None


# ══════════════════════════════════════════════════════════
# data.js parsing & updating
# ══════════════════════════════════════════════════════════
def parse_recipes_from_data():
    """Extract list of recipe dicts from data.js.

    Uses regex parsing (data.js is JS, not JSON, so we can't json.load).
    Returns list of dicts with: id, cat, title, vid (if exists).
    """
    if not DATA_FILE.exists():
        log(f"[!] data.js not found at: {DATA_FILE}")
        sys.exit(1)

    src = DATA_FILE.read_text(encoding='utf-8')
    # Locate each recipe object and balance braces
    pattern = re.compile(r"\{id:'([^']+)',cat:'(\w+)'", re.MULTILINE)
    recipes = []
    for m in pattern.finditer(src):
        rid, cat = m.group(1), m.group(2)
        start = m.start()
        depth = 0
        end = start
        for i, c in enumerate(src[start:], start):
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        block = src[start:end]
        # Extract title
        t = re.search(r"title:'([^']+)'", block)
        # Extract existing vid (if any)
        v = re.search(r"vid:'([^']+)'", block)
        recipes.append({
            'id': rid,
            'cat': cat,
            'title': t.group(1) if t else '',
            'vid': v.group(1) if v else None,
            'block_start': start,
            'block_end': end,
        })
    return recipes


def update_data_js_with_vid(recipe_id, video_url, dry_run=True):
    """Update data.js: add or replace vid: field for given recipe id.

    Strategy:
      - Read full file
      - Find recipe by id
      - If vid: already exists → replace its value
      - If not → insert vid:'URL' before the closing brace
      - Write back if not dry_run
    """
    src = DATA_FILE.read_text(encoding='utf-8')

    # Find this recipe's block
    m = re.search(rf"\{{id:'{re.escape(recipe_id)}'", src)
    if not m:
        return False, "recipe not found"

    start = m.start()
    depth = 0
    end = start
    for i, c in enumerate(src[start:], start):
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    block = src[start:end]
    new_vid_str = f"vid:'{video_url}'"

    if "vid:'" in block:
        # Replace existing
        new_block = re.sub(r"vid:'[^']*'", new_vid_str, block, count=1)
    else:
        # Insert before closing brace.
        # Pattern: ...,tip:'...'} → ...,tip:'...',vid:'...'}
        # Or:     ...,steps:[...]} → ...,steps:[...],vid:'...'}
        # Insert just before final `}`:
        new_block = block[:-1].rstrip()
        if not new_block.endswith(','):
            new_block += ','
        new_block += new_vid_str + '}'

    new_src = src[:start] + new_block + src[end:]

    if not dry_run:
        # Backup first run only
        backup = SCRIPT_DIR / 'data.js.before-find-videos.bak'
        if not backup.exists():
            backup.write_text(src, encoding='utf-8')
        DATA_FILE.write_text(new_src, encoding='utf-8')

    return True, "ok"


# ══════════════════════════════════════════════════════════
# Main loop
# ══════════════════════════════════════════════════════════
def main():
    global LOG_FILE
    parser = argparse.ArgumentParser(
        description="find_videos.py v1.0 — חיפוש קישורי וידאו ל-1054 מתכונים",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "דוגמאות:\n"
            "  python find_videos.py --dry-run         # סקירה בלבד (default)\n"
            "  python find_videos.py --apply           # החל שינויים ב-data.js\n"
            "  python find_videos.py --apply --max 20  # רק 20 מתכונים (לבדיקה)\n"
            "  python find_videos.py --apply --only soups   # רק קטגוריית soups\n"
            "  python find_videos.py --apply --overwrite    # החלף קישורים קיימים\n"
        )
    )
    parser.add_argument("--dry-run",   action="store_true",
                        help="סקירה בלבד — לא משנה את data.js (default אם --apply לא צוין)")
    parser.add_argument("--apply",     action="store_true",
                        help="באמת לעדכן את data.js")
    parser.add_argument("--max",       type=int, default=None,
                        help="מספר מקסימלי של מתכונים לעיבוד (None = הכל)")
    parser.add_argument("--only",      type=str, default=None, metavar="CAT",
                        help="עיבוד רק של קטגוריה ספציפית (soups/salads/iraq וכו')")
    parser.add_argument("--overwrite", action="store_true",
                        help="עדכן vid: גם אם כבר קיים")
    parser.add_argument("--no-proxy",  action="store_true",
                        help="ללא proxy")
    parser.add_argument("--proxy",     type=str, default=None,
                        help="proxy ידני")
    parser.add_argument("--delay",     type=float, default=2.0,
                        help="שניות המתנה בין חיפושים (להימנע מ-rate limit)")
    args = parser.parse_args()

    # Default: dry-run if --apply not set
    if not args.apply:
        args.dry_run = True

    # Init log
    ts = datetime.now().strftime('%d-%m-%Y_%H.%M')
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE = LOG_DIR / f"find_videos_{ts}.log"

    log("=" * 60)
    log("find_videos.py v1.0 — Perla Ben-Harrosh z\"l Cookbook")
    log("=" * 60)
    mode = "DRY-RUN (no changes)" if args.dry_run else "APPLY (writing to data.js)"
    log(f"Mode: {mode}")
    log(f"Data file: {DATA_FILE}")
    log(f"Log file: {LOG_FILE}")
    if args.only:    log(f"Filter: only category '{args.only}'")
    if args.max:     log(f"Limit: max {args.max} recipes")
    if args.overwrite: log(f"Mode: OVERWRITE existing vid:")
    log(f"Delay between searches: {args.delay}s")
    log("=" * 60)

    _setup_proxy(args)

    # Parse all recipes
    log("\n[1/3] Parsing data.js...")
    recipes = parse_recipes_from_data()
    log(f"  Found {len(recipes)} recipes")

    # Filter
    targets = []
    for r in recipes:
        if args.only and r['cat'] != args.only:
            continue
        if r['vid'] and not args.overwrite:
            continue
        targets.append(r)

    log(f"  Targets (no existing vid OR --overwrite): {len(targets)}")
    if args.max:
        targets = targets[:args.max]
        log(f"  After --max {args.max}: {len(targets)}")
    log("")

    # Search loop
    log(f"[2/3] Searching YouTube for {len(targets)} recipes...")
    log(f"  Estimated time: {len(targets) * (args.delay + 2):.0f}s "
        f"({len(targets) * (args.delay + 2) / 60:.1f} min)")
    log("")

    found = 0
    not_found = 0
    errors = 0
    updates = []  # list of (rid, video_url) tuples

    for i, r in enumerate(targets):
        if _STOP:
            log("[!] Stopping per Ctrl+C")
            break

        title = r['title']
        # Build English query from title (simple - just use category)
        cat_to_en = {
            'soups': 'moroccan soup', 'salads': 'moroccan salad',
            'veg': 'moroccan vegetable', 'fish': 'moroccan fish',
            'meat': 'moroccan meat', 'chick': 'moroccan chicken',
            'hol': 'moroccan jewish holiday', 'des': 'moroccan dessert',
            'span': 'spanish jewish', 'iraq': 'iraqi jewish',
            'kurd': 'kurdish jewish', 'ashk': 'ashkenazi jewish',
            'yem': 'yemenite jewish', 'pers': 'persian jewish',
            'buk': 'bukharian jewish', 'tun': 'tunisian jewish',
            'isr': 'israeli', 'turk': 'turkish jewish',
            'nonkosher': 'recipe',
        }
        en_query = cat_to_en.get(r['cat'], 'recipe')

        log(f"  [{i+1:4d}/{len(targets)}] [{r['id']:8s}] {title[:50]}")
        try:
            t0 = time.time()
            video_url = search_youtube_video(title, en_query)
            elapsed = time.time() - t0
            if video_url:
                log(f"             → {video_url} ({elapsed:.1f}s)")
                found += 1
                updates.append((r['id'], video_url))
            else:
                log(f"             → no video found ({elapsed:.1f}s)")
                not_found += 1
        except Exception as e:
            log(f"             → ERROR: {e}")
            errors += 1

        # Rate limit
        if i < len(targets) - 1:
            time.sleep(args.delay)

    log("")
    log(f"[3/3] Search results:")
    log(f"  Found:     {found}")
    log(f"  Not found: {not_found}")
    log(f"  Errors:    {errors}")
    log(f"  Total processed: {found + not_found + errors}")

    # Apply updates
    if args.dry_run:
        log("")
        log("=" * 60)
        log("DRY-RUN: no changes made to data.js.")
        log(f"To apply: rerun with --apply")
        log("=" * 60)
    elif updates:
        log("")
        log(f"Applying {len(updates)} updates to data.js...")
        applied = 0
        failed = 0
        for rid, vurl in updates:
            ok, reason = update_data_js_with_vid(rid, vurl, dry_run=False)
            if ok:
                applied += 1
            else:
                failed += 1
                log(f"  [!] {rid}: {reason}")
        log(f"Applied:  {applied}")
        log(f"Failed:   {failed}")
        log("")
        log("=" * 60)
        log(f"data.js backup saved to: data.js.before-find-videos.bak")
        log(f"To revert: copy backup over data.js")
        log("=" * 60)
    else:
        log("\nNo updates to apply.")

    log("")
    log(f"Done. Log: {LOG_FILE}")


if __name__ == '__main__':
    main()
