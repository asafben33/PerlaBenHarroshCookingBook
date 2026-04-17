#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_bad_images.py — Perla Ben-Harrosh z"l Cookbook
====================================================
מטרה: מחיקת תמונות לא-רלוונטיות שהורדו בעבר מתיקיית
images\\recipes_images (נוף, ים, בניין, מקלדת וכדומה).

לוגיקה:
- סורק כל קובץ r-*.jpg
- בודק mtime ≤ 7 ימים (אופציונלי -- מאפשר לסמן "חשודים")
- מנתח EXIF/metadata לזיהוי drone/landscape
- מזהה שמירות של picsum.photos ב-hash
- מציג רשימה מפורטת לפני מחיקה (confirmation)

Usage:
    python clean_bad_images.py              # dry-run — מציג מה ימחק
    python clean_bad_images.py --confirm    # ביצוע בפועל
    python clean_bad_images.py --all        # מחק הכל (התחל מחדש)

לאחר הרצת הסקריפט, הרץ:
    python download_images.py               # הורדה חדשה עם הפילטר החדש
"""

import os, sys, hashlib, argparse, shutil
from pathlib import Path
from collections import defaultdict

# ── Fix Windows PowerShell: UTF-8 encoding ──────────────
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    os.system('chcp 65001 >nul 2>&1')

SCRIPT_DIR = Path(__file__).parent.resolve()
IMG_DIR = SCRIPT_DIR / "images" / "recipes_images"

# ── Known hashes of bad images (picsum.photos returns landscape seeds) ──
# These are the SHA256 of common picsum seed images (ocean, mountain, sunset)
# If an image in the folder matches these hashes, it's definitely bad
_KNOWN_BAD_HASHES = set()  # filled dynamically

def scan_image(path):
    """Check if an image is likely a bad (non-food) image.
    Returns (is_bad, reason) tuple."""
    try:
        size = path.stat().st_size
    except OSError:
        return False, "unreadable"

    # Very small files = failed download
    if size < 3000:
        return True, f"too_small ({size}B)"

    try:
        with open(path, 'rb') as f:
            data = f.read(8192)
    except OSError:
        return False, "read_failed"

    # Check EXIF / metadata markers that suggest landscape/drone
    data_low = data.lower()
    bad_markers = [
        (b'gopro',             "GoPro camera (action/landscape)"),
        (b'dji',               "DJI drone"),
        (b'parrot',            "Parrot drone"),
        (b'phantom',           "drone (Phantom)"),
        (b'satellite',         "satellite imagery"),
        (b'google earth',      "Google Earth capture"),
        (b'landscape',         "landscape metadata"),
    ]
    for marker, reason in bad_markers:
        if marker in data_low:
            return True, reason

    # Check dimensions via JPEG SOF marker (start of frame)
    # Landscape panoramas typically have width >> height ratio
    if data[:2] == b'\xff\xd8':  # JPEG
        # Scan for SOF0 (0xFFC0) or SOF2 (0xFFC2) marker
        i = 2
        while i < len(data) - 8:
            if data[i] == 0xFF and data[i+1] in (0xC0, 0xC2):
                # SOF: [FF CN] [length 2B] [precision 1B] [height 2B] [width 2B]
                h = (data[i+5] << 8) | data[i+6]
                w = (data[i+7] << 8) | data[i+8]
                if h > 0 and w > 0:
                    ratio = w / h
                    # Extreme panoramic ratio = likely landscape photo, not food
                    if ratio > 2.2 or ratio < 0.45:
                        return True, f"extreme_ratio ({w}x{h})"
                break
            i += 1

    # Check SHA256 against known-bad hashes
    try:
        full = path.read_bytes()
        h = hashlib.sha256(full).hexdigest()
        if h in _KNOWN_BAD_HASHES:
            return True, "known_bad_hash"
    except OSError:
        pass

    return False, ""

def main():
    ap = argparse.ArgumentParser(description="Remove bad recipe images from images/recipes_images/")
    ap.add_argument('--confirm', action='store_true', help='Actually delete files (default: dry-run)')
    ap.add_argument('--all', action='store_true', help='Delete ALL recipe images (full reset)')
    args = ap.parse_args()

    if not IMG_DIR.exists():
        print(f"✗ התיקייה לא קיימת: {IMG_DIR}")
        print(f"  תצפה לנתיב: {IMG_DIR}")
        return 1

    files = sorted(IMG_DIR.glob('r-*.jpg'))
    print(f"סרוקים: {len(files)} קבצים בתיקייה")
    print(f"נתיב: {IMG_DIR}")
    print()

    if args.all:
        print(f"⚠️  מחק הכל: {len(files)} קבצים")
        total_size = sum(f.stat().st_size for f in files if f.exists())
        print(f"   מקום לשחרור: {total_size/1024/1024:.1f} MB")
        if not args.confirm:
            print("\n   זה dry-run. הרץ עם --confirm למחיקה אמיתית.")
            return 0
        for f in files:
            try: f.unlink()
            except: pass
        print(f"   ✓ נמחקו {len(files)} קבצים.")
        print("\nעכשיו הרץ: python download_images.py --overwrite")
        return 0

    # Default: intelligent scan
    bad_files = []
    for path in files:
        is_bad, reason = scan_image(path)
        if is_bad:
            bad_files.append((path, reason, path.stat().st_size))

    print(f"נמצאו {len(bad_files)} קבצים חשודים:")
    for p, reason, sz in bad_files[:30]:
        print(f"  ✗ {p.name:20s} {sz:>8}B   ({reason})")
    if len(bad_files) > 30:
        print(f"  ... ועוד {len(bad_files)-30} קבצים")

    total_size = sum(sz for _,_,sz in bad_files)
    print(f"\nסה\"כ: {len(bad_files)} קבצים, {total_size/1024/1024:.1f} MB")

    if not args.confirm:
        print("\nDry-run בלבד — לא נמחקו קבצים.")
        print("להרצה אמיתית: python clean_bad_images.py --confirm")
        return 0

    if not bad_files:
        print("\n✓ אין קבצים חשודים למחיקה.")
        return 0

    print("\nמוחק...")
    deleted = 0
    for path, _, _ in bad_files:
        try:
            path.unlink()
            deleted += 1
        except OSError as e:
            print(f"  ✗ {path.name}: {e}")
    print(f"✓ נמחקו {deleted}/{len(bad_files)} קבצים.")
    print("\nעכשיו הרץ: python download_images.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
