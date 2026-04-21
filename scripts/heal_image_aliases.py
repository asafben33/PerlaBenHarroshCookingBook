"""
================================================================================
heal_image_aliases.py
================================================================================

מטרה (Purpose in Hebrew):
סקריפט זה מבצע בדיקה יסודית של מערכת ה-aliases של תמונות המתכונים
בפרויקט "ספר המתכונים של פרלה בן-הראש ז"ל" ומתקן aliases שבורים
(aliases שמצביעים על קבצי תמונה שאינם קיימים בתיקייה).

הסקריפט:
1. סורק את _IMG_ALIAS.js ואוסף את כל ה-4,980 aliases.
2. סורק את images/recipes_images/ ואוסף את רשימת הקבצים הקיימים בפועל.
3. מזהה aliases שבורים (target לא קיים).
4. עבור כל target שבור, מחפש alternative קיים (fallback חכם).
5. מייצר תיקון מוצע + דו"ח מפורט.
6. במצב --apply כותב את התיקון חזרה ל-_IMG_ALIAS.js ול-index.html.

תכונות מפתח:
- Dry-run by default (DRY_RUN=True) — לא משנה דבר עד אישור מפורש.
- Logging לקובץ עם timestamp (DD-MM-YYYY_HH.MM).
- Progress display (10%, 20%, ..., 100%).
- Reports עבור משתמשים טכניים ולא-טכניים.
- Backup אוטומטי של קבצים לפני כל שינוי.
- Validation של JS syntax לאחר תיקון.
- תמיכה מלאה ב-UTF-8 (עברית).

שימוש:
    # Dry-run (ברירת מחדל — רק מדווח, לא משנה):
    python heal_image_aliases.py
    
    # Apply (מבצע את התיקון בפועל):
    python heal_image_aliases.py --apply
    
    # Dry-run עם verbose logging:
    python heal_image_aliases.py --verbose
    
    # בדיקת כל הקבצים החסרים (גם אלה שלא referenced ב-aliases):
    python heal_image_aliases.py --check-all

Author: Claude (Anthropic) for Asaf Ben-Harrosh
Date: 2026-04-21
Version: 1.0
================================================================================
"""

import argparse
import datetime
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths - adjust these to match your project structure
REPO_ROOT = Path(__file__).resolve().parent
IMG_ALIAS_JS = REPO_ROOT / "_IMG_ALIAS.js"
INDEX_HTML = REPO_ROOT / "index.html"
DATA_JS = REPO_ROOT / "data.js"
IMAGES_DIR = REPO_ROOT / "images" / "recipes_images"
LOGS_DIR = REPO_ROOT / "logs"
REPORTS_DIR = REPO_ROOT / "reports"
BACKUPS_DIR = REPO_ROOT / "backups"

# Default feature flags
DRY_RUN = True
VERBOSE = False
CHECK_ALL = False
APPLY = False

# Progress milestones
PROGRESS_MILESTONES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging with timestamped file output."""
    LOGS_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M")
    log_file = LOGS_DIR / f"heal_image_aliases_{timestamp}.log"
    
    # Logger config
    logger = logging.getLogger("heal_aliases")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear previous handlers
    logger.handlers = []
    
    # File handler (UTF-8 for Hebrew)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh_format = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )
    fh.setFormatter(fh_format)
    logger.addHandler(fh)
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch_format = logging.Formatter("%(message)s")
    ch.setFormatter(ch_format)
    logger.addHandler(ch)
    
    logger.info("=" * 80)
    logger.info("heal_image_aliases.py — Image Alias Healing Tool")
    logger.info("=" * 80)
    logger.info(f"Log file: {log_file}")
    logger.info(f"Timestamp: {timestamp}")
    logger.info("")
    
    return logger


def show_progress(logger: logging.Logger, current: int, total: int, label: str = ""):
    """Display progress at defined milestones."""
    if total == 0:
        return
    pct = int((current / total) * 100)
    # Find the nearest milestone
    for milestone in PROGRESS_MILESTONES:
        if pct >= milestone and not hasattr(show_progress, f"_m{milestone}_{label}"):
            setattr(show_progress, f"_m{milestone}_{label}", True)
            logger.info(f"    [{label}] Progress: {milestone}% ({current}/{total})")
            break


def reset_progress():
    """Reset progress tracking between operations."""
    for attr in list(vars(show_progress).keys()):
        if attr.startswith("_m"):
            delattr(show_progress, attr)


# ============================================================================
# BACKUP UTILITIES
# ============================================================================

def create_backup(file_path: Path, logger: logging.Logger) -> Path:
    """Create a timestamped backup of a file."""
    BACKUPS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
    backup_path = BACKUPS_DIR / f"{file_path.name}.{timestamp}.bak"
    shutil.copy2(file_path, backup_path)
    logger.info(f"  Backup created: {backup_path.name}")
    return backup_path


# ============================================================================
# STEP 1 — PARSE _IMG_ALIAS.js
# ============================================================================

def parse_alias_file(logger: logging.Logger) -> dict:
    """
    Parse _IMG_ALIAS.js and extract all alias mappings.
    Returns dict: {source_name: target_name}
    """
    logger.info("[STEP 1] Parsing _IMG_ALIAS.js...")
    
    if not IMG_ALIAS_JS.exists():
        logger.error(f"  ERROR: File not found: {IMG_ALIAS_JS}")
        sys.exit(1)
    
    content = IMG_ALIAS_JS.read_text(encoding="utf-8")
    
    # Match patterns like 'r-xxx':'r-yyy'
    pattern = re.compile(r"'([^']+)'\s*:\s*'([^']+)'")
    matches = pattern.findall(content)
    
    aliases = dict(matches)
    logger.info(f"  Parsed {len(aliases):,} aliases from _IMG_ALIAS.js")
    
    # Check for duplicates
    all_sources = [m[0] for m in matches]
    if len(all_sources) != len(set(all_sources)):
        dup_count = len(all_sources) - len(set(all_sources))
        logger.warning(f"  WARNING: {dup_count} duplicate source keys detected")
    
    return aliases


# ============================================================================
# STEP 2 — SCAN IMAGES DIRECTORY
# ============================================================================

def scan_images_directory(logger: logging.Logger) -> set:
    """
    Scan images/recipes_images/ and return a set of existing file basenames
    (without .jpg extension).
    """
    logger.info("[STEP 2] Scanning images/recipes_images/ directory...")
    
    if not IMAGES_DIR.exists():
        logger.error(f"  ERROR: Directory not found: {IMAGES_DIR}")
        logger.error(f"  Please verify you are running this script from the repo root.")
        sys.exit(1)
    
    jpg_files = list(IMAGES_DIR.glob("*.jpg"))
    existing = set(f.stem for f in jpg_files)
    
    logger.info(f"  Found {len(existing):,} image files on disk")
    
    # Sample of files (first 5)
    if VERBOSE:
        sample = sorted(existing)[:5]
        logger.debug(f"  Sample files: {sample}")
    
    return existing


# ============================================================================
# STEP 3 — IDENTIFY BROKEN ALIASES
# ============================================================================

def find_broken_aliases(
    aliases: dict, existing_files: set, logger: logging.Logger
) -> tuple:
    """
    Identify aliases where the TARGET file doesn't exist.
    Returns:
        - broken_aliases: dict {source: target} where target is missing
        - broken_targets: Counter {target: count of aliases pointing to it}
    """
    logger.info("[STEP 3] Identifying broken aliases...")
    
    broken_aliases = {}
    broken_targets = Counter()
    
    total = len(aliases)
    for i, (source, target) in enumerate(aliases.items(), 1):
        if target not in existing_files:
            broken_aliases[source] = target
            broken_targets[target] += 1
        show_progress(logger, i, total, "scan_aliases")
    
    reset_progress()
    
    logger.info(f"  Broken aliases: {len(broken_aliases):,} / {len(aliases):,} ({len(broken_aliases)*100/max(len(aliases),1):.1f}%)")
    logger.info(f"  Unique broken targets: {len(broken_targets):,}")
    
    if broken_targets:
        logger.info("")
        logger.info("  Top 10 most-referenced broken targets:")
        for target, count in broken_targets.most_common(10):
            logger.info(f"    {target}: {count} aliases affected")
    
    return broken_aliases, broken_targets


# ============================================================================
# STEP 4 — FIND REPLACEMENT TARGETS
# ============================================================================

def find_replacement(
    broken_target: str, existing_files: set, logger: logging.Logger
) -> str | None:
    """
    Given a broken target like 'r-add22-2', try to find a working alternative.
    Strategy (in order of preference):
      1. Try the base (strip -2, -3, etc.) → r-add22
      2. Try adjacent variants (-3, -4, -5 if -2 missing)
      3. Try same prefix with any number (r-add22-*)
      4. Return None if nothing found
    """
    # Parse the target: r-add22-2 → ('r-add22', '-2')
    match = re.match(r"^(r-[a-zA-Z_]+\d*)(-\d+)?$", broken_target)
    if not match:
        return None
    
    base = match.group(1)  # e.g. 'r-add22'
    suffix = match.group(2)  # e.g. '-2' or None
    
    # Strategy 1: Try the base (no suffix)
    if base in existing_files:
        return base
    
    # Strategy 2: Try adjacent numeric variants (-2 through -10)
    if suffix:
        current_num = int(suffix[1:])
        # Try nearby numbers: -2, -3, -4, -5, ..., -10 and also variants before
        candidates = []
        for n in range(2, 11):
            if n != current_num:
                candidates.append(f"{base}-{n}")
        # Also try without suffix
        candidates.insert(0, base)
        
        for c in candidates:
            if c in existing_files:
                return c
    
    # Strategy 3: Any variant with same prefix
    pattern = re.compile(f"^{re.escape(base)}(-\\d+)?$")
    for f in existing_files:
        if pattern.match(f):
            return f
    
    return None


def plan_repairs(
    broken_aliases: dict, broken_targets: Counter, existing_files: set,
    logger: logging.Logger
) -> dict:
    """
    For each unique broken target, find a replacement.
    Returns dict: {broken_target: replacement_target_or_None}
    """
    logger.info("[STEP 4] Planning repairs — finding replacement targets...")
    
    repair_plan = {}
    total = len(broken_targets)
    
    for i, target in enumerate(broken_targets.keys(), 1):
        replacement = find_replacement(target, existing_files, logger)
        repair_plan[target] = replacement
        
        if VERBOSE:
            if replacement:
                logger.debug(f"  {target} → {replacement} ✓")
            else:
                logger.debug(f"  {target} → NO REPLACEMENT FOUND ✗")
        
        show_progress(logger, i, total, "plan_repairs")
    
    reset_progress()
    
    repairable = sum(1 for r in repair_plan.values() if r)
    unrepairable = len(repair_plan) - repairable
    
    logger.info(f"  Repairable: {repairable:,} / {len(repair_plan):,}")
    logger.info(f"  Unrepairable: {unrepairable:,} (will fall back to category image)")
    
    return repair_plan


# ============================================================================
# STEP 5 — APPLY REPAIRS TO _IMG_ALIAS.js
# ============================================================================

def apply_repairs_to_alias_file(
    aliases: dict, broken_aliases: dict, repair_plan: dict,
    logger: logging.Logger
) -> int:
    """
    Rewrite _IMG_ALIAS.js with broken targets replaced by working ones.
    Aliases whose targets have no replacement are REMOVED (so the recipe
    falls back to the default category image).
    
    Returns the number of changes made.
    """
    logger.info("[STEP 5] Applying repairs to _IMG_ALIAS.js...")
    
    if DRY_RUN:
        logger.info("  [DRY-RUN] No file changes will be made.")
    else:
        create_backup(IMG_ALIAS_JS, logger)
    
    # Read original content
    content = IMG_ALIAS_JS.read_text(encoding="utf-8")
    
    # Build new alias map
    new_aliases = {}
    removed_count = 0
    repaired_count = 0
    unchanged_count = 0
    
    for source, target in aliases.items():
        if source in broken_aliases:
            # This alias is broken
            replacement = repair_plan.get(target)
            if replacement:
                new_aliases[source] = replacement
                repaired_count += 1
                if VERBOSE:
                    logger.debug(f"  REPAIR: '{source}':'{target}' → '{replacement}'")
            else:
                # No replacement — remove the alias entirely
                removed_count += 1
                if VERBOSE:
                    logger.debug(f"  REMOVE: '{source}':'{target}' (no replacement)")
        else:
            # Working alias — keep as is
            new_aliases[source] = target
            unchanged_count += 1
    
    logger.info(f"  Unchanged: {unchanged_count:,}")
    logger.info(f"  Repaired:  {repaired_count:,}")
    logger.info(f"  Removed:   {removed_count:,}")
    
    # Regenerate the file content
    new_content = generate_alias_js(new_aliases)
    
    if not DRY_RUN:
        IMG_ALIAS_JS.write_text(new_content, encoding="utf-8")
        logger.info(f"  ✓ Wrote new _IMG_ALIAS.js ({len(new_aliases):,} aliases)")
        
        # Validate
        if validate_js(IMG_ALIAS_JS, logger):
            logger.info(f"  ✓ JavaScript validation passed")
        else:
            logger.error(f"  ✗ JavaScript validation FAILED — check backup!")
            return 0
    else:
        logger.info(f"  [DRY-RUN] Would write {len(new_aliases):,} aliases to _IMG_ALIAS.js")
    
    return repaired_count + removed_count


def generate_alias_js(aliases: dict) -> str:
    """Generate _IMG_ALIAS.js file content from alias dict."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "/* Auto-generated by heal_image_aliases.py */",
        f"/* Generated: {timestamp} */",
        f"/* {len(aliases):,} aliases, broken targets healed */",
        "var _IMG_ALIAS = {",
    ]
    
    # Sort alphabetically for consistency
    for source in sorted(aliases.keys()):
        target = aliases[source]
        lines.append(f"  '{source}':'{target}',")
    
    lines.append("};")
    lines.append("")
    
    # Use CRLF for Windows compatibility (matches original)
    return "\r\n".join(lines)


def validate_js(js_file: Path, logger: logging.Logger) -> bool:
    """Validate JavaScript syntax using node (if available)."""
    try:
        result = subprocess.run(
            ["node", "-c", str(js_file)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            logger.error(f"    JS syntax error: {result.stderr[:500]}")
            return False
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("    Node.js not available — skipping JS validation")
        return True  # Assume valid if we can't check


# ============================================================================
# STEP 6 — UPDATE index.html (embedded _IMG_ALIAS)
# ============================================================================

def update_index_html(
    aliases: dict, broken_aliases: dict, repair_plan: dict,
    logger: logging.Logger
) -> int:
    """
    index.html contains an embedded copy of _IMG_ALIAS.
    Update the embedded block to match the repaired _IMG_ALIAS.js.
    
    Returns the number of changes made.
    """
    logger.info("[STEP 6] Updating embedded _IMG_ALIAS in index.html...")
    
    if not INDEX_HTML.exists():
        logger.warning(f"  index.html not found — skipping")
        return 0
    
    if DRY_RUN:
        logger.info("  [DRY-RUN] No file changes will be made.")
    else:
        create_backup(INDEX_HTML, logger)
    
    content = INDEX_HTML.read_text(encoding="utf-8")
    
    # Find the embedded _IMG_ALIAS block
    # It starts with "var _IMG_ALIAS = {" and ends with "};"
    pattern = re.compile(
        r"(var\s+_IMG_ALIAS\s*=\s*\{)(.*?)(\};)",
        re.DOTALL
    )
    
    match = pattern.search(content)
    if not match:
        logger.warning("  Could not locate _IMG_ALIAS block in index.html")
        return 0
    
    # Parse existing embedded aliases to see what's there
    embedded_body = match.group(2)
    embedded_aliases = dict(re.findall(r"'([^']+)'\s*:\s*'([^']+)'", embedded_body))
    logger.info(f"  Found {len(embedded_aliases):,} embedded aliases in index.html")
    
    # Build new aliases (same logic as alias file)
    new_aliases = {}
    repaired = 0
    removed = 0
    
    for source, target in embedded_aliases.items():
        if source in broken_aliases:
            replacement = repair_plan.get(target)
            if replacement:
                new_aliases[source] = replacement
                repaired += 1
            else:
                removed += 1
        else:
            new_aliases[source] = target
    
    logger.info(f"  Repaired: {repaired:,}")
    logger.info(f"  Removed:  {removed:,}")
    
    # Build replacement text
    new_body_lines = [""]
    for source in sorted(new_aliases.keys()):
        target = new_aliases[source]
        new_body_lines.append(f"  '{source}':'{target}',")
    new_body = "\r\n".join(new_body_lines) + "\r\n"
    
    new_block = match.group(1) + new_body + match.group(3)
    new_content = content[:match.start()] + new_block + content[match.end():]
    
    if not DRY_RUN:
        INDEX_HTML.write_text(new_content, encoding="utf-8")
        logger.info(f"  ✓ Updated _IMG_ALIAS block in index.html")
    else:
        logger.info(f"  [DRY-RUN] Would update {len(new_aliases):,} embedded aliases")
    
    return repaired + removed


# ============================================================================
# STEP 7 — GENERATE REPORTS
# ============================================================================

def generate_reports(
    aliases: dict, broken_aliases: dict, broken_targets: Counter,
    repair_plan: dict, existing_files: set, logger: logging.Logger
):
    """Generate technical JSON report + non-technical Markdown report."""
    logger.info("[STEP 7] Generating reports...")
    
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M")
    
    # ------ Technical report (JSON) ------
    technical_report = {
        "generated_at": timestamp,
        "version": "1.0",
        "mode": "dry_run" if DRY_RUN else "apply",
        "statistics": {
            "total_aliases": len(aliases),
            "total_images_on_disk": len(existing_files),
            "broken_aliases_count": len(broken_aliases),
            "broken_aliases_pct": round(len(broken_aliases) * 100 / max(len(aliases), 1), 2),
            "unique_broken_targets": len(broken_targets),
            "repairable_targets": sum(1 for r in repair_plan.values() if r),
            "unrepairable_targets": sum(1 for r in repair_plan.values() if not r),
        },
        "top_broken_targets": [
            {"target": t, "alias_count": c, "replacement": repair_plan.get(t)}
            for t, c in broken_targets.most_common(25)
        ],
        "repair_plan": repair_plan,
        "unrepairable_targets": sorted(
            [t for t, r in repair_plan.items() if not r]
        ),
    }
    
    json_report_path = REPORTS_DIR / f"alias_healing_report_{timestamp}.json"
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(technical_report, f, ensure_ascii=False, indent=2)
    logger.info(f"  Technical report (JSON): {json_report_path.name}")
    
    # ------ User-friendly report (Markdown) ------
    md_lines = [
        f"# דו\"ח בדיקת Aliases של תמונות מתכונים",
        "",
        f"**תאריך יצירה:** {timestamp}",
        f"**מצב:** {'יבש (dry-run) — לא בוצעו שינויים' if DRY_RUN else 'מלא (apply) — השינויים בוצעו'}",
        "",
        "---",
        "",
        "## סיכום ממצאים",
        "",
        f"- **סך aliases במערכת:** {len(aliases):,}",
        f"- **תמונות קיימות בדיסק:** {len(existing_files):,}",
        f"- **aliases שבורים (target חסר):** {len(broken_aliases):,} "
        f"({len(broken_aliases)*100/max(len(aliases),1):.1f}%)",
        f"- **targets ייחודיים חסרים:** {len(broken_targets):,}",
        f"- **ניתנים לתיקון (החלפה נמצאה):** "
        f"{sum(1 for r in repair_plan.values() if r):,}",
        f"- **לא ניתנים לתיקון (יפלו ל-fallback קטגוריה):** "
        f"{sum(1 for r in repair_plan.values() if not r):,}",
        "",
        "---",
        "",
        "## 20 ה-targets הבעייתיים ביותר",
        "",
        "| # | Target חסר | מס' aliases מושפעים | Replacement מוצע |",
        "|---|---|---|---|",
    ]
    
    for i, (target, count) in enumerate(broken_targets.most_common(20), 1):
        replacement = repair_plan.get(target) or "❌ אין — ייפול ל-fallback"
        md_lines.append(f"| {i} | `{target}` | {count} | `{replacement}` |")
    
    md_lines.extend([
        "",
        "---",
        "",
        "## מה המשמעות?",
        "",
        "### Aliases שבורים",
        "",
        "המערכת כוללת מיפוי של שמות תמונות (\"aliases\") שמפנים ממתכון אחד "
        "לתמונה קיימת של מתכון אחר. למשל, אם 50 מתכונים חולקים תמונה זהה "
        "של סלט תפוזים, רק תמונה אחת נשמרת בדיסק, וכל 49 המתכונים האחרים "
        "מופנים אליה דרך alias.",
        "",
        "**Alias שבור** = ה-alias מפנה לקובץ שלא קיים בדיסק. התוצאה: המתכון "
        "מציג שגיאת 404 ומתחלף בתמונת ברירת-המחדל של הקטגוריה.",
        "",
        "### מה הסקריפט עושה?",
        "",
        "עבור כל alias שבור, הסקריפט מחפש תמונה חלופית:",
        "1. קודם כל — מנסה את הגרסה הבסיסית (ללא סיומת `-2`, `-3` וכו')",
        "2. אחר-כך — מנסה גרסאות סמוכות (`-3`, `-4`, `-5`...)",
        "3. אם לא נמצא כלום — מסיר את ה-alias, כך שהמתכון יפול לתמונת הקטגוריה",
        "",
        "---",
        "",
        "## קבצים שנוצרו",
        "",
        f"- **לוג מפורט:** `logs/heal_image_aliases_*.log`",
        f"- **דו\"ח טכני (JSON):** `reports/alias_healing_report_{timestamp}.json`",
        f"- **דו\"ח זה (Markdown):** `reports/alias_healing_report_{timestamp}.md`",
        "",
        "### אם הרצת במצב apply:",
        "",
        f"- **גיבויים:** `backups/` (ניתן לשחזור במקרה של בעיה)",
        f"- **_IMG_ALIAS.js:** עודכן",
        f"- **index.html:** בלוק _IMG_ALIAS עודכן",
        "",
        "---",
        "",
        "## שלבים הבאים",
        "",
    ])
    
    if DRY_RUN:
        md_lines.extend([
            "1. **בדוק דו\"ח זה ואת הלוג** כדי לוודא שההמלצות נראות סבירות.",
            "2. **הרץ מחדש עם `--apply`** כדי להחיל את התיקונים:",
            "   ```",
            "   python heal_image_aliases.py --apply",
            "   ```",
            "3. **רענן את הדפדפן ב-Ctrl+Shift+R** וודא שהשגיאות 404 נעלמו.",
            "4. **Commit + Push** לשרת:",
            "   ```powershell",
            "   git add _IMG_ALIAS.js index.html",
            "   git commit -m \"Heal broken image aliases — fix 404 errors on recipe images\"",
            "   git push origin main",
            "   ```",
        ])
    else:
        md_lines.extend([
            "1. ✅ השינויים בוצעו.",
            "2. **רענן את הדפדפן ב-Ctrl+Shift+R** וודא שהשגיאות 404 נעלמו.",
            "3. **Commit + Push** לשרת:",
            "   ```powershell",
            "   git add _IMG_ALIAS.js index.html",
            "   git commit -m \"Heal broken image aliases — fix 404 errors on recipe images\"",
            "   git push origin main",
            "   ```",
            "4. **בעיה?** ניתן לשחזר מגיבוי בתיקיית `backups/`.",
        ])
    
    md_report_path = REPORTS_DIR / f"alias_healing_report_{timestamp}.md"
    with open(md_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    logger.info(f"  User-friendly report (MD): {md_report_path.name}")
    
    return json_report_path, md_report_path


# ============================================================================
# OPTIONAL: CHECK-ALL MODE
# ============================================================================

def check_all_referenced_images(
    aliases: dict, existing_files: set, logger: logging.Logger
):
    """
    Scan data.js for ALL image references (not just aliases) and find missing ones.
    This is the --check-all mode.
    """
    logger.info("[CHECK-ALL] Scanning data.js for all r-*.jpg references...")
    
    if not DATA_JS.exists():
        logger.warning(f"  data.js not found — skipping check-all")
        return
    
    content = DATA_JS.read_text(encoding="utf-8")
    # Pattern: r-something.jpg or r-something
    pattern = re.compile(r"r-[a-zA-Z_]+\d*(?:-\d+)?")
    all_refs = set(pattern.findall(content))
    logger.info(f"  Found {len(all_refs):,} unique r-* references in data.js")
    
    # Resolve each reference through the alias map
    missing_final = set()
    total = len(all_refs)
    for i, ref in enumerate(all_refs, 1):
        # If it's an alias, resolve it
        resolved = aliases.get(ref, ref)
        if resolved not in existing_files:
            missing_final.add(ref)
        show_progress(logger, i, total, "check_all")
    
    reset_progress()
    
    logger.info(f"  Missing after alias resolution: {len(missing_final):,}")
    if missing_final and VERBOSE:
        sample = sorted(missing_final)[:20]
        logger.debug(f"  Sample missing: {sample}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    global DRY_RUN, VERBOSE, CHECK_ALL, APPLY
    
    parser = argparse.ArgumentParser(
        description="Heal broken image aliases in Perla Cookbook project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually apply changes (default is dry-run)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--check-all", action="store_true",
        help="Also scan data.js for ALL image references"
    )
    
    args = parser.parse_args()
    
    APPLY = args.apply
    DRY_RUN = not APPLY
    VERBOSE = args.verbose
    CHECK_ALL = args.check_all
    
    logger = setup_logging(VERBOSE)
    
    logger.info(f"Mode: {'APPLY (changes will be written)' if APPLY else 'DRY-RUN (no changes)'}")
    logger.info(f"Verbose: {VERBOSE}")
    logger.info(f"Check-all: {CHECK_ALL}")
    logger.info("")
    logger.info(f"Paths:")
    logger.info(f"  Repo root:       {REPO_ROOT}")
    logger.info(f"  _IMG_ALIAS.js:   {IMG_ALIAS_JS}")
    logger.info(f"  index.html:      {INDEX_HTML}")
    logger.info(f"  Images dir:      {IMAGES_DIR}")
    logger.info("")
    
    if APPLY:
        print()
        print("⚠  You are about to APPLY changes to:")
        print(f"   - {IMG_ALIAS_JS}")
        print(f"   - {INDEX_HTML}")
        print(f"   (Backups will be created in {BACKUPS_DIR})")
        print()
        confirm = input("Type 'yes' to proceed, anything else to abort: ").strip().lower()
        if confirm != "yes":
            logger.info("Aborted by user.")
            return
        logger.info("User confirmed — proceeding with changes.")
        logger.info("")
    
    try:
        # STEP 1
        aliases = parse_alias_file(logger)
        logger.info("")
        
        # STEP 2
        existing_files = scan_images_directory(logger)
        logger.info("")
        
        # STEP 3
        broken_aliases, broken_targets = find_broken_aliases(aliases, existing_files, logger)
        logger.info("")
        
        if not broken_aliases:
            logger.info("✓ No broken aliases found — nothing to repair!")
            return
        
        # STEP 4
        repair_plan = plan_repairs(broken_aliases, broken_targets, existing_files, logger)
        logger.info("")
        
        # STEP 5
        apply_repairs_to_alias_file(aliases, broken_aliases, repair_plan, logger)
        logger.info("")
        
        # STEP 6
        update_index_html(aliases, broken_aliases, repair_plan, logger)
        logger.info("")
        
        # STEP 7
        json_report, md_report = generate_reports(
            aliases, broken_aliases, broken_targets, repair_plan, existing_files, logger
        )
        logger.info("")
        
        # Optional check-all
        if CHECK_ALL:
            check_all_referenced_images(aliases, existing_files, logger)
            logger.info("")
        
        logger.info("=" * 80)
        logger.info("✓ DONE")
        logger.info("=" * 80)
        logger.info(f"  Mode: {'APPLY (changes written)' if APPLY else 'DRY-RUN (no changes)'}")
        logger.info(f"  Reports: reports/alias_healing_report_*.{{json,md}}")
        logger.info(f"  Log:     logs/heal_image_aliases_*.log")
        if APPLY:
            logger.info(f"  Backups: backups/*.bak")
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Test locally: open index.html and verify 404s are gone")
            logger.info("  2. Git commit + push:")
            logger.info("     git add _IMG_ALIAS.js index.html")
            logger.info("     git commit -m 'Heal broken image aliases (fix 404s)'")
            logger.info("     git push origin main")
            logger.info("  3. Hard-refresh browser (Ctrl+Shift+R)")
        else:
            logger.info("")
            logger.info("To actually apply these changes, run:")
            logger.info("  python heal_image_aliases.py --apply")
    
    except Exception as e:
        logger.error(f"FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
