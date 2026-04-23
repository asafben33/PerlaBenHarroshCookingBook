#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_media.py - Perla Ben-Harrosh z"l Cookbook  (v1.0)
=============================================================================
Unified media orchestrator.

Combines two existing scripts:
  * download_images.py (v6.1.1) - download/clean/dedup/alias recipe images
  * find_videos.py     (v1.0)   - search YouTube and inject vid: into data.js

This script provides:
  1. Interactive hierarchical menu (main menu + submenus)
  2. Recommended execution order ("classic pipeline")
  3. Direct CLI dispatch:
        python download_media.py images [args...]
        python download_media.py videos [args...]
        python download_media.py menu              (default)
        python download_media.py pipeline          (recommended flow)

All capabilities of the two source scripts are preserved - download_media.py
acts purely as an orchestrator that runs them as subprocesses with the right
flags. No filter logic is duplicated; the source scripts remain the single
source of truth.

Log: SCRIPT_DIR/logs/download_media_DD-MM-YYYY_HH.log
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


# Hebrew-safe console on Windows PowerShell (preserves UTF-8 for child output).
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.system('chcp 65001 >nul 2>&1')


SCRIPT_DIR     = Path(__file__).resolve().parent
PROJECT_ROOT   = SCRIPT_DIR.parent
IMAGES_SCRIPT  = SCRIPT_DIR / 'download_images.py'
VIDEOS_SCRIPT  = SCRIPT_DIR / 'find_videos.py'
LOG_DIR        = PROJECT_ROOT / 'logs'

VERSION = "1.0"


def log_line(msg):
    """Mirror message to stdout and to a session log file."""
    ts = datetime.now().strftime('%H:%M:%S')
    line = "[" + ts + "] " + msg
    print(line, flush=True)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        session = datetime.now().strftime('%d-%m-%Y_%H')
        logf = LOG_DIR / ("download_media_" + session + ".log")
        with open(logf, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def _verify_scripts():
    """Abort early if either source script is missing."""
    missing = []
    if not IMAGES_SCRIPT.exists():
        missing.append(str(IMAGES_SCRIPT))
    if not VIDEOS_SCRIPT.exists():
        missing.append(str(VIDEOS_SCRIPT))
    if missing:
        print("[!] Missing required scripts:")
        for m in missing:
            print("    - " + m)
        print("    download_media.py requires both scripts present in scripts/.")
        sys.exit(2)


def run_subprocess(script_path, extra_args, title=None):
    """Invoke a child script with the parent's Python, streaming output live.

    Returns the child's return code."""
    cmd = [sys.executable, str(script_path)] + list(extra_args)
    pretty_cmd = ' '.join([Path(cmd[0]).name, Path(cmd[1]).name] + list(extra_args))
    log_line("[run] " + (title or pretty_cmd))
    log_line("[cmd] " + pretty_cmd)
    try:
        result = subprocess.run(cmd, cwd=str(SCRIPT_DIR))
        log_line("[exit] code=" + str(result.returncode))
        return result.returncode
    except FileNotFoundError:
        log_line("[!] Cannot execute: " + cmd[0])
        return 127
    except KeyboardInterrupt:
        log_line("[!] Interrupted by user (Ctrl+C)")
        return 130


def _confirm(prompt, default_yes=True):
    """Prompt yes/no. Accepts English and Hebrew answers."""
    suffix = " [Y/n] " if default_yes else " [y/N] "
    try:
        ans = input(prompt + suffix).strip().lower()
    except KeyboardInterrupt:
        print()
        return False
    if not ans:
        return default_yes
    return ans in ('y', 'yes', 'כ', 'כן', '1')


# ==========================================================================
# Menu actions. Each action maps to one or more subprocess invocations on
# download_images.py or find_videos.py with predefined flag combinations.
# ==========================================================================

def action_images_full_cycle():
    """Stage 1 (clean) -> Stage 2 (download) -> Stage 3 (dedup)."""
    return run_subprocess(IMAGES_SCRIPT, [],
                          title="Images - full cycle (clean -> download -> dedup)")


def action_images_full_cycle_strict():
    return run_subprocess(IMAGES_SCRIPT, ["--strict"],
                          title="Images - full cycle in strict mode (score threshold 60)")


def action_images_full_cycle_inline_alias():
    return run_subprocess(IMAGES_SCRIPT, ["--inline-alias"],
                          title="Images - full cycle + inject alias into index.html")


def action_images_clean_only():
    return run_subprocess(IMAGES_SCRIPT, ["--clean-only"],
                          title="Images - stage 1 only (clean suspicious images)")


def action_images_download_only():
    return run_subprocess(IMAGES_SCRIPT, ["--skip-clean", "--skip-dedup"],
                          title="Images - stage 2 only (download)")


def action_images_dedup_only():
    return run_subprocess(IMAGES_SCRIPT, ["--skip-clean", "--skip-download"],
                          title="Images - stage 3 only (dedup + alias)")


def action_images_aggressive_clean():
    return run_subprocess(IMAGES_SCRIPT, ["--clean-only", "--aggressive-clean"],
                          title="Images - aggressive clean (min-size 5KB, ratio 1.9/0.55)")


def action_images_dry_run():
    return run_subprocess(IMAGES_SCRIPT, ["--dry-run"],
                          title="Images - dry-run preview (no deletions, no writes)")


def action_images_overwrite():
    if not _confirm("This will re-download every existing image. Continue?"):
        return 0
    return run_subprocess(IMAGES_SCRIPT, ["--overwrite"],
                          title="Images - overwrite (force re-download)")


def action_images_reset():
    if not _confirm("DESTRUCTIVE: the entire recipes_images folder will be wiped before download. Continue?"):
        return 0
    return run_subprocess(IMAGES_SCRIPT, ["--reset-images"],
                          title="Images - reset (wipe + download)")


def action_images_custom_min_score():
    try:
        val = input("  Minimum relevance score (default 40, strict=60): ").strip()
        int(val)
    except (ValueError, KeyboardInterrupt):
        print("  Invalid value - cancelled.")
        return 0
    return run_subprocess(IMAGES_SCRIPT, ["--min-score", val],
                          title="Images - full cycle with --min-score " + val)


def action_images_provenance():
    return run_subprocess(IMAGES_SCRIPT, ["--provenance"],
                          title="Images - provenance summary")


def action_proxy_detect_only():
    return run_subprocess(IMAGES_SCRIPT, ["--detect-only"],
                          title="Proxy - detect and save to proxy_config.txt")


def action_proxy_test_all():
    return run_subprocess(IMAGES_SCRIPT, ["--detect-only", "--test-proxy"],
                          title="Proxy - active test of all candidates")


def action_proxy_no_proxy_full_cycle():
    return run_subprocess(IMAGES_SCRIPT, ["--no-proxy"],
                          title="Images - full cycle with --no-proxy")


def action_proxy_manual_full_cycle():
    val = input("  Proxy URL (e.g. http://proxy.gov.il:8080): ").strip()
    if not val:
        print("  Empty - cancelled.")
        return 0
    return run_subprocess(IMAGES_SCRIPT, ["--proxy", val],
                          title="Images - full cycle with manual proxy (" + val + ")")


def action_videos_dry_run():
    return run_subprocess(VIDEOS_SCRIPT, ["--dry-run"],
                          title="Videos - dry-run (survey only, data.js untouched)")


def action_videos_apply_all():
    if not _confirm("This will update data.js with a new vid: on every missing recipe. Continue?"):
        return 0
    return run_subprocess(VIDEOS_SCRIPT, ["--apply"],
                          title="Videos - apply to all recipes missing vid:")


def action_videos_apply_max():
    try:
        n = int(input("  Maximum number of recipes to update (e.g. 50): ").strip())
    except (ValueError, KeyboardInterrupt):
        print("  Invalid value - cancelled.")
        return 0
    return run_subprocess(VIDEOS_SCRIPT, ["--apply", "--max", str(n)],
                          title="Videos - apply with limit of " + str(n) + " recipes")


def action_videos_apply_category():
    cat = input("  Single category (soups, iraq, pers, ...): ").strip()
    if not cat:
        print("  Empty - cancelled.")
        return 0
    return run_subprocess(VIDEOS_SCRIPT, ["--apply", "--only", cat],
                          title="Videos - apply to category '" + cat + "' only")


def action_videos_apply_overwrite():
    if not _confirm("This will also replace existing vid: links on recipes. Continue?"):
        return 0
    return run_subprocess(VIDEOS_SCRIPT, ["--apply", "--overwrite"],
                          title="Videos - apply + overwrite existing links")


def action_images_help():
    return run_subprocess(IMAGES_SCRIPT, ["--help"], title="help - download_images.py")


def action_videos_help():
    return run_subprocess(VIDEOS_SCRIPT, ["--help"], title="help - find_videos.py")


def action_images_custom_args():
    line = input("  Custom flags for download_images.py (e.g. --strict --provenance): ").strip()
    args = line.split() if line else []
    return run_subprocess(IMAGES_SCRIPT, args,
                          title="Images - custom (" + (line or "no flags") + ")")


def action_videos_custom_args():
    line = input("  Custom flags for find_videos.py (e.g. --apply --max 20): ").strip()
    args = line.split() if line else []
    return run_subprocess(VIDEOS_SCRIPT, args,
                          title="Videos - custom (" + (line or "no flags") + ")")


def action_pipeline_recommended():
    """Run the recommended flow, prompting before each step."""
    log_line("")
    log_line("=" * 64)
    log_line("Recommended pipeline - 5 steps")
    log_line("=" * 64)
    steps = [
        ("1/5 - Proxy detection (fast)",
         lambda: run_subprocess(IMAGES_SCRIPT, ["--detect-only"], title="proxy detect")),
        ("2/5 - Clean suspicious images",
         lambda: run_subprocess(IMAGES_SCRIPT, ["--clean-only"], title="clean")),
        ("3/5 - Download missing images",
         lambda: run_subprocess(IMAGES_SCRIPT, ["--skip-clean", "--skip-dedup"], title="download")),
        ("4/5 - Dedup + alias + inject into index.html",
         lambda: run_subprocess(IMAGES_SCRIPT, ["--skip-clean", "--skip-download", "--inline-alias"],
                                title="dedup + inline-alias")),
        ("5/5 - Find videos (dry-run; run with --apply afterwards if results look good)",
         lambda: run_subprocess(VIDEOS_SCRIPT, ["--dry-run"], title="videos dry-run")),
    ]
    for label, fn in steps:
        log_line("")
        log_line(">>> " + label)
        if not _confirm("Proceed with this step?", default_yes=True):
            log_line("Skipped.")
            continue
        rc = fn()
        if rc != 0:
            log_line("[!] Step exited with code=" + str(rc) + ".")
            if _confirm("Stop the pipeline here?", default_yes=False):
                return rc
    log_line("")
    log_line("=" * 64)
    log_line("Pipeline finished.")
    log_line("=" * 64)
    return 0


# ==========================================================================
# Menu structure - hierarchical: main -> submenu -> action.
# Each menu is a list of (key, label, target). Target is either:
#   * callable -> executed immediately
#   * str      -> name of another menu to open (sub-menu)
# ==========================================================================

MAIN_BANNER = """
+----------------------------------------------------------------------+
|  download_media.py v{ver:<5} - central menu for recipe media           |
|  Combines: download_images.py (v6.1.1) + find_videos.py (v1.0)       |
+----------------------------------------------------------------------+

Recommended execution order:
  1) Proxy -> detect-only       (fast, ~10 seconds)
  2) Images -> full cycle        (clean + download + dedup)
  3) Videos -> dry-run           (survey recipes missing vid:)
  4) Videos -> apply             (inject into data.js)

  Press [1] Pipeline to run the full flow automatically with confirmations.
"""

MAIN_MENU = [
    ("1", "Run recommended pipeline (automatic with confirmations)", action_pipeline_recommended),
    ("2", "Images - download_images.py",                             "images"),
    ("3", "Videos - find_videos.py",                                 "videos"),
    ("4", "Proxy",                                                   "proxy"),
    ("5", "Advanced (custom args / help)",                           "advanced"),
]

SUBMENU_IMAGES = [
    ("1", "Full cycle: clean -> download -> dedup  (default)",               action_images_full_cycle),
    ("2", "Full cycle + strict mode (score threshold 60 - maximum precision)", action_images_full_cycle_strict),
    ("3", "Full cycle + inline-alias into index.html",                       action_images_full_cycle_inline_alias),
    ("4", "Single-stage runs...",                                            "images_stages"),
    ("5", "Special modes (aggressive / dry-run / overwrite / reset)",        "images_modes"),
    ("6", "Custom --min-score N",                                            action_images_custom_min_score),
    ("7", "Show provenance summary",                                         action_images_provenance),
]

SUBMENU_IMAGES_STAGES = [
    ("1", "Stage 1 only - clean suspicious images (--clean-only)",           action_images_clean_only),
    ("2", "Stage 2 only - download (skip clean + dedup)",                    action_images_download_only),
    ("3", "Stage 3 only - dedup + alias (skip clean + download)",            action_images_dedup_only),
]

SUBMENU_IMAGES_MODES = [
    ("1", "Aggressive clean (min-size 5KB, ratio 1.9/0.55)",                 action_images_aggressive_clean),
    ("2", "Dry-run preview (no deletions, no writes)",                       action_images_dry_run),
    ("3", "Overwrite - force re-download of existing images",                action_images_overwrite),
    ("4", "Reset - wipe all recipe images and re-download",                  action_images_reset),
]

SUBMENU_VIDEOS = [
    ("1", "Dry-run - survey (no changes to data.js)",                        action_videos_dry_run),
    ("2", "Apply - update data.js with vid: for all missing",                action_videos_apply_all),
    ("3", "Apply --max N - limit number of recipes (for testing)",           action_videos_apply_max),
    ("4", "Apply --only CAT - single category only",                         action_videos_apply_category),
    ("5", "Apply --overwrite - also replace existing vid: links",            action_videos_apply_overwrite),
]

SUBMENU_PROXY = [
    ("1", "detect-only - detect proxy and save to proxy_config.txt",         action_proxy_detect_only),
    ("2", "Active test of all proxy candidates (slower, thorough)",          action_proxy_test_all),
    ("3", "--no-proxy - run full image cycle without proxy",                 action_proxy_no_proxy_full_cycle),
    ("4", "--proxy URL - set manual proxy and run full cycle",               action_proxy_manual_full_cycle),
]

SUBMENU_ADVANCED = [
    ("1", "Run download_images.py with custom flags",                        action_images_custom_args),
    ("2", "Run find_videos.py with custom flags",                            action_videos_custom_args),
    ("3", "Show --help of download_images.py",                               action_images_help),
    ("4", "Show --help of find_videos.py",                                   action_videos_help),
]

MENUS = {
    "main":          ("Main menu",                   MAIN_MENU,             True),
    "images":        ("Images",                      SUBMENU_IMAGES,        False),
    "images_stages": ("Images - single stages",      SUBMENU_IMAGES_STAGES, False),
    "images_modes":  ("Images - special modes",      SUBMENU_IMAGES_MODES,  False),
    "videos":        ("Videos",                      SUBMENU_VIDEOS,        False),
    "proxy":         ("Proxy",                       SUBMENU_PROXY,         False),
    "advanced":      ("Advanced",                    SUBMENU_ADVANCED,      False),
}


def _render_menu(menu_key, breadcrumb):
    title, items, show_banner = MENUS[menu_key]
    if show_banner:
        print(MAIN_BANNER.format(ver=VERSION))
    print("")
    print("-" * 70)
    print("  " + title)
    if breadcrumb:
        print("  path: " + " > ".join(breadcrumb))
    print("-" * 70)
    for key, label, _target in items:
        print("  " + key.rjust(3) + ".  " + label)
    print("")
    if menu_key == "main":
        print("   0.  Quit")
    else:
        print("   b.  Back")
        print("   m.  Main menu")
        print("   0.  Quit")
    print("")


def interactive_menu():
    stack = ["main"]
    breadcrumb = ["main"]

    while stack:
        current = stack[-1]
        _render_menu(current, breadcrumb[1:])

        try:
            choice = input("  choice: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice in ('0', 'q', 'quit', 'exit'):
            log_line("Goodbye.")
            break

        if choice in ('b', 'back'):
            if len(stack) > 1:
                stack.pop()
                breadcrumb.pop()
            continue

        if choice in ('m', 'main'):
            stack = ["main"]
            breadcrumb = ["main"]
            continue

        _title, items, _banner = MENUS[current]
        match = next((it for it in items if it[0] == choice), None)
        if match is None:
            print("  Option '" + choice + "' not found - try again.\n")
            continue

        _key, label, target = match

        if isinstance(target, str):
            stack.append(target)
            breadcrumb.append(MENUS[target][0])
            continue

        rc = target()
        print("")
        if rc not in (0, None):
            print("  (action finished with code " + str(rc) + ")")
        try:
            input("  Press Enter to continue... ")
        except (EOFError, KeyboardInterrupt):
            break
        print("\n")

    return 0


# ==========================================================================
# CLI dispatch
# ==========================================================================
USAGE = """Usage:
    python download_media.py                 # interactive menu
    python download_media.py menu            # interactive menu (same)
    python download_media.py pipeline        # run the recommended pipeline
    python download_media.py images [args]   # forward flags to download_images.py
    python download_media.py videos [args]   # forward flags to find_videos.py
    python download_media.py help            # show this usage + both scripts' help
"""


def main():
    _verify_scripts()

    if len(sys.argv) == 1:
        return interactive_menu()

    sub = sys.argv[1].lower()
    rest = sys.argv[2:]

    if sub in ('menu', 'interactive'):
        return interactive_menu()

    if sub in ('help', '-h', '--help'):
        print(USAGE)
        print("Flags for download_images.py:")
        run_subprocess(IMAGES_SCRIPT, ["--help"], title="")
        print("\nFlags for find_videos.py:")
        run_subprocess(VIDEOS_SCRIPT, ["--help"], title="")
        return 0

    if sub in ('pipeline', 'all', 'recommended'):
        return action_pipeline_recommended()

    if sub in ('images', 'image', 'img', 'photos'):
        return run_subprocess(IMAGES_SCRIPT, rest, title="images " + ' '.join(rest))

    if sub in ('videos', 'video', 'vid', 'youtube'):
        return run_subprocess(VIDEOS_SCRIPT, rest, title="videos " + ' '.join(rest))

    print("[!] Unknown subcommand: '" + sub + "'\n")
    print(USAGE)
    return 2


if __name__ == '__main__':
    try:
        sys.exit(main() or 0)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(130)
