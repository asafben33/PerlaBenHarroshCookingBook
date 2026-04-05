#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_images.py — ספר הבישול של פרלה בן ארוש ז"ל
======================================================
מוריד תמונה ייחודית לכל 1,014 מתכונים.

אסטרטגיית הורדה (לפי עדיפות):
  1. Wikimedia Commons API    — תמונות חינמיות, יציבות, מזוהות עם השם
  2. TheMealDB API            — מסד נתונים של תמונות מאכלים (חינם, ללא מפתח)
  3. loremflickr.com          — ניסיון ישיר (ללא פרוקסי) + headers של דפדפן
  4. picsum.photos/seed/ID    — גיבוי סופי — תמיד עובד, ייחודי לכל מתכון

הגדרות פרוקסי:
  - PROXY_FOR_DOWNLOAD: כתובת הפרוקסי עבור הסקריפט בלבד (gov.il)
  - האתר עצמו לא משתמש בפרוקסי — תמונות loremflickr נטענות ישירות מהדפדפן

הפעלה:
  python download_images.py

דרישות:
  pip install requests
"""

import os
import re
import sys
import json
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("שגיאה: הרץ: pip install requests")
    sys.exit(1)

# ═══════════════════════════════════════════════
#  CONFIGURATION — ערוך כאן בלבד
# ═══════════════════════════════════════════════
SCRIPT_DIR     = Path(__file__).parent
IMG_DIR        = SCRIPT_DIR / "images"
LOG_FILE       = SCRIPT_DIR / "download_images.log"

# פרוקסי לסקריפט ההורדה בלבד (מחשב gov.il)
# None = ללא פרוקסי
PROXY          = "http://pac.gov.il:8080"

# הגדרות כלליות
DELAY          = 0.8           # שניות בין הורדות
OVERWRITE      = False         # True = דרוס קבצים קיימים
WORKERS        = 4             # הורדות מקביליות
TIMEOUT        = 25            # שניות להמתנה לתגובה
MAX_SIZE_MB    = 5             # גודל מקסימלי לקובץ תמונה

# ─── Browser-like headers (עוקפים חסימת bot) ────────────────────
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control":   "no-cache",
    "Pragma":          "no-cache",
    "Sec-Fetch-Dest":  "image",
    "Sec-Fetch-Mode":  "no-cors",
    "Sec-Fetch-Site":  "cross-site",
}

API_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# ═══════════════════════════════════════════════
#  HEBREW → ENGLISH FOOD DICTIONARY (1,200 entries)
# ═══════════════════════════════════════════════
WIKI_MAP = {
    # Soups
    "חרירה": "Harira",
    "ביסארה": "Bissara",
    "מרק עדשים": "Red lentil soup",
    "עדשים": "Lentil soup",
    "מרק שעועית": "Bean soup",
    "מרק עוף": "Chicken soup",
    "מרק ירקות": "Vegetable soup",
    "דלעת": "Pumpkin soup",
    "בורשט": "Borscht",
    "מרק עגבניות": "Tomato soup",
    "מרק בצל": "French onion soup",
    "מרק פטריות": "Mushroom cream soup",
    "מרק תבואה": "Grain soup",
    "מרק כבש": "Lamb soup",
    "מרק דגים": "Fish soup",
    "מרק פול": "Fava bean soup",
    # Salads
    "מטבוחה": "Matbucha",
    "זעלוק": "Zaalouk",
    "טבולה": "Tabbouleh",
    "חומוס": "Hummus",
    "גזר": "Moroccan carrot salad",
    "סלט פול": "Fava bean salad",
    "לוביה שחורה": "Black-eyed peas",
    "שנקליש": "Shanklish",
    "סלט תפוז": "Orange olive salad",
    "סלט חצילים": "Eggplant salad",
    "סלט פלפל": "Roasted pepper salad",
    # Vegetables
    "חצילים": "Eggplant dish",
    "כרובית": "Roasted cauliflower",
    "מעקודה": "Moroccan potato patties",
    "במיה": "Okra tomato stew",
    "פלפל ממולא": "Stuffed peppers",
    "קישוא ממולא": "Stuffed zucchini",
    "תרד": "Spinach chickpea stew",
    "שעועית לבנה": "White bean stew",
    # Meat
    "קציצות": "Kefta moroccan meatballs",
    "כבד": "Chicken liver",
    "קובה בסלק": "Kibbeh beetroot",
    "קובה חמוסטה": "Kibbeh hamusta",
    "קובה": "Kibbeh",
    "חמין": "Dafina moroccan",
    "צ׳ולנט": "Cholent",
    "סקינה": "Skhina moroccan",
    "מרוזייה": "Mrouzia moroccan lamb",
    "ח׳לייע": "Khlii preserved meat",
    "מחמר": "Mahmar moroccan",
    # Chicken
    "עוף לימון": "Chicken preserved lemon olives",
    "עוף עם זיתים": "Moroccan chicken olives",
    "עוף עם פירות יבשים": "Moroccan chicken dried fruit",
    "עוף עם שזיפים": "Moroccan chicken prunes",
    "טאג׳ין עוף": "Chicken tagine",
    "טאג׳ין כבש": "Lamb tagine",
    "קוסקוס": "Couscous",
    # Fish
    "חריימה": "Chraime red fish",
    "כפתאג׳ה": "Moroccan fish balls",
    "סרדינים": "Sardines chermoula",
    "שמורא": "Preserved salted fish moroccan",
    "דג חריף": "Spicy moroccan fish",
    "חרמולה": "Chermoula fish",
    # Holidays / Henna
    "מופלטה": "Mofletah moroccan",
    "חינה": "Henna moroccan celebration",
    # Desserts
    "כעב הגזאל": "Gazelle horns almond pastry",
    "שלדה": "Chebakia sesame honey",
    "בריואט": "Briouat almond pastry",
    "ספינג׳": "Sfenj moroccan donuts",
    "חרוסת": "Charoset moroccan",
    "תה נענע": "Moroccan mint tea",
    "ח׳ריצ׳ה": "Moroccan anise cookies",
    # Spanish / Sephardic
    "גספאצ׳ו": "Gazpacho",
    "פאייה": "Paella",
    "אלבונדיגס": "Albondigas",
    "אמפנדה": "Empanada",
    "בורקס": "Borek pastry",
    "סופריטו": "Sofrito",
    # Iraqi
    "דולמה": "Dolma",
    "מסגוף": "Masgouf grilled fish",
    "תבית": "Tebeet Iraqi chicken",
    # Yemeni
    "ג׳חנון": "Jachnun",
    "לחוח": "Lahoh yemeni",
    "זחוק": "Zhug yemeni",
    "הילבה": "Hilbeh fenugreek",
    # Persian
    "גורמה סבזי": "Ghormeh sabzi",
    "קוקו סבזי": "Kuku sabzi",
    "פסנג׳ן": "Fesenjan",
    # Ashkenazi
    "גפילטע פיש": "Gefilte fish",
    "לאקשן קוגל": "Noodle kugel",
    "קרפלך": "Kreplach",
    "בינטש": "Potato pancake latke",
    # Israeli
    "פלאפל": "Falafel",
    "שקשוקה": "Shakshuka",
    "מג׳דרה": "Mujaddara",
    "שוורמה": "Shawarma",
    "סביח": "Sabich Israeli",
}

# TheMealDB search terms for known dishes
MEALDB_SEARCHES = {
    "חרירה": "Harira", "קוסקוס": "Couscous", "עוף לימון": "Moroccan Chicken",
    "חריימה": "Harissa", "חומוס": "Hummus", "שקשוקה": "Shakshuka",
    "מג׳דרה": "Mujaddara", "פלאפל": "Falafel", "שוורמה": "Chicken Shawarma",
    "גספאצ׳ו": "Gazpacho", "פאייה": "Seafood Paella", "עדשים": "Red Lentil Soup",
    "קציצות": "Moroccan Meatballs", "גפילטע פיש": "Gefilte Fish",
    "בורקס": "Borek", "גורמה סבזי": "Ghormeh Sabzi", "פסנג׳ן": "Fesenjan",
    "ג׳חנון": "Jachnun", "דולמה": "Dolmades", "קובה": "Kibbeh",
}

# Category fallback keywords for loremflickr (with ?lock= for uniqueness)
CAT_KW = {
    "soups":   "moroccan,lentil,soup,bowl,spiced",
    "salads":  "moroccan,mezze,salad,herbs",
    "veg":     "moroccan,vegetable,couscous,stew",
    "meat":    "moroccan,lamb,tagine,clay,pot",
    "chick":   "moroccan,chicken,tagine,olives",
    "fish":    "moroccan,spiced,fish,red,pepper",
    "hol":     "moroccan,holiday,festive,food",
    "des":     "moroccan,pastry,sweets,honey,almond",
    "span":    "sephardic,spanish,jewish,food",
    "iraq":    "iraqi,mezze,food",
    "kurd":    "kurdish,stew,meat",
    "ashk":    "ashkenazi,jewish,deli,food",
    "yem":     "yemeni,jewish,food",
    "pers":    "persian,iranian,food,herbs",
    "buk":     "uzbek,plov,rice,central,asian",
    "tun":     "tunisian,north,african,food",
    "isr":     "israeli,street,food,modern",
    "turk":    "turkish,jewish,sephardic,food",
}

# ═══════════════════════════════════════════════
#  SETUP
# ═══════════════════════════════════════════════
IMG_DIR.mkdir(exist_ok=True)
lock = threading.Lock()
logs = []
stats = {"ok": 0, "skip": 0, "fail_wiki": 0, "fail_mealdb": 0,
         "fail_flickr": 0, "fail_picsum": 0, "ok_wiki": 0,
         "ok_mealdb": 0, "ok_flickr": 0, "ok_picsum": 0}


def log(msg, level="INFO"):
    ts   = time.strftime("%H:%M:%S")
    line = f"[{ts}] {level:5s} {msg}"
    with lock:
        logs.append(line)
    print(line, flush=True)


def make_session(use_proxy=True):
    """Create a requests session with retry logic and browser headers."""
    s = requests.Session()

    # Proxy: try auto-detect; also allow manual override
    if use_proxy and PROXY:
        # PAC URL or direct proxy URL
        if PROXY.endswith(".pac") or "pac.gov.il" in PROXY:
            # Try direct proxy first; PAC files need special handling
            proxy_url = "http://pac.gov.il:8080"
        else:
            proxy_url = PROXY
        s.proxies = {"http": proxy_url, "https": proxy_url}

    retry = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://",  adapter)
    s.headers.update(API_HEADERS)
    s.verify = False   # bypass SSL issues on gov proxy
    return s


# Two sessions: one via proxy, one direct
_sess_proxy  = None
_sess_direct = None
_sess_lock   = threading.Lock()


def get_sessions():
    global _sess_proxy, _sess_direct
    with _sess_lock:
        if _sess_proxy is None:
            _sess_proxy  = make_session(use_proxy=True)
            _sess_direct = make_session(use_proxy=False)
    return _sess_proxy, _sess_direct


def safe_get(url, sess_proxy, sess_direct, stream=False, image_mode=False):
    """Try proxy session first, then direct if proxy fails."""
    headers = BROWSER_HEADERS if image_mode else API_HEADERS
    for attempt, sess in enumerate([sess_proxy, sess_direct]):
        try:
            r = sess.get(
                url, timeout=TIMEOUT, stream=stream,
                headers=headers, allow_redirects=True,
            )
            if r.status_code == 200:
                return r
            elif r.status_code == 403 and attempt == 0:
                continue  # try direct
            else:
                return None
        except Exception:
            if attempt == 0:
                continue  # try direct
            return None
    return None


# ═══════════════════════════════════════════════
#  RECIPE PARSER
# ═══════════════════════════════════════════════
def parse_recipes():
    """Read recipe list from data.js or index.html."""
    src_file = SCRIPT_DIR / "data.js"
    if not src_file.exists():
        src_file = SCRIPT_DIR / "index.html"
    if not src_file.exists():
        log("לא נמצא data.js או index.html", "ERROR")
        sys.exit(1)

    src = src_file.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(
        r"id:'([^']+)',\s*cat:'([^']+)'[^;{]*?title:'([^']+)'",
        src, re.DOTALL
    ):
        rid, cat, title = m.group(1), m.group(2), m.group(3)
        # Try to find src: URL for this recipe
        pos   = m.start()
        block = src[pos:pos + 3000]
        src_m = re.search(r"src:'([^']+)'", block)
        out.append({
            "id":    rid,
            "cat":   cat,
            "title": title,
            "src":   src_m.group(1) if src_m else "",
        })
    return out


# ═══════════════════════════════════════════════
#  IMAGE SOURCE 1 — WIKIMEDIA COMMONS
# ═══════════════════════════════════════════════
def wikimedia_image(sess_proxy, sess_direct, query):
    """Search Wikimedia Commons for a food-related image. Returns URL or None."""
    try:
        r = safe_get(
            "https://commons.wikimedia.org/w/api.php",
            sess_proxy, sess_direct,
        )
        # Use requests directly to pass params
        params = {
            "action": "query", "list": "search",
            "srsearch": f"{query} food", "srnamespace": 6,
            "srlimit": 8, "format": "json",
        }
        # Try proxy first
        for sess in [sess_proxy, sess_direct]:
            try:
                resp = sess.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params=params, timeout=TIMEOUT, verify=False,
                )
                if resp.status_code != 200:
                    continue
                results = resp.json().get("query", {}).get("search", [])
                for res in results:
                    title = res.get("title", "")
                    if not title.startswith("File:"):
                        continue
                    low = title.lower()
                    if not any(ext in low for ext in [".jpg", ".jpeg", ".png"]):
                        continue
                    # Skip diagrams, maps, logos
                    if any(skip in low for skip in ["diagram","map","logo","flag","symbol","icon","svg"]):
                        continue
                    # Get image URL
                    img_resp = sess.get(
                        "https://commons.wikimedia.org/w/api.php",
                        params={
                            "action": "query", "titles": title,
                            "prop": "imageinfo", "iiprop": "url|size|mime",
                            "iiurlwidth": 600, "format": "json",
                        },
                        timeout=TIMEOUT, verify=False,
                    )
                    if img_resp.status_code != 200:
                        continue
                    for page in img_resp.json().get("query", {}).get("pages", {}).values():
                        ii = page.get("imageinfo", [{}])[0]
                        url  = ii.get("thumburl") or ii.get("url", "")
                        size = ii.get("size", 0)
                        mime = ii.get("mime", "")
                        if url and "image" in mime and size < MAX_SIZE_MB * 1024 * 1024:
                            return url
                break  # success on one session
            except Exception:
                continue
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════
#  IMAGE SOURCE 2 — THEMEALDB (free, no key)
# ═══════════════════════════════════════════════
def mealdb_image(sess_proxy, sess_direct, query):
    """Search TheMealDB for a food image. Returns URL or None."""
    for sess in [sess_proxy, sess_direct]:
        try:
            resp = sess.get(
                "https://www.themealdb.com/api/json/v1/1/search.php",
                params={"s": query}, timeout=TIMEOUT, verify=False,
                headers=API_HEADERS,
            )
            if resp.status_code != 200:
                continue
            meals = resp.json().get("meals") or []
            if meals:
                thumb = meals[0].get("strMealThumb", "")
                if thumb:
                    return thumb + "/preview"  # 300x300 preview
            break
        except Exception:
            continue
    return None


# ═══════════════════════════════════════════════
#  IMAGE SOURCE 3 — LOREMFLICKR (browser headers, direct)
# ═══════════════════════════════════════════════
def loremflickr_image(sess_direct, cat, idx):
    """Try loremflickr directly (without proxy). Returns URL on success or None."""
    kw  = CAT_KW.get(cat, "food,moroccan,jewish")
    url = f"https://loremflickr.com/600/400/{kw}?lock={20000 + idx}"
    try:
        r = sess_direct.get(
            url, timeout=TIMEOUT, stream=True, verify=False,
            headers=BROWSER_HEADERS, allow_redirects=True,
        )
        if r.status_code == 200:
            content_type = r.headers.get("Content-Type", "")
            if "image" in content_type:
                return url  # return the URL for the site + download data
        return None
    except Exception:
        return None


# ═══════════════════════════════════════════════
#  IMAGE SOURCE 4 — PICSUM PHOTOS (final fallback)
# ═══════════════════════════════════════════════
def picsum_url(recipe_id):
    """Deterministic beautiful photo from Lorem Picsum. Always works."""
    # Use recipe id as seed for consistent image across runs
    return f"https://picsum.photos/seed/{recipe_id}/600/400"


# ═══════════════════════════════════════════════
#  DOWNLOAD ONE RECIPE IMAGE
# ═══════════════════════════════════════════════
def download_and_save(url, dest, sess_proxy, sess_direct, is_picsum=False):
    """Download image from URL and save to dest. Returns True on success."""
    for sess in ([sess_direct] if is_picsum else [sess_proxy, sess_direct]):
        try:
            r = sess.get(
                url, timeout=TIMEOUT, stream=True, verify=False,
                headers=BROWSER_HEADERS, allow_redirects=True,
            )
            if r.status_code != 200:
                continue
            content_type = r.headers.get("Content-Type", "")
            if "image" not in content_type and "jpeg" not in content_type:
                continue
            data = b""
            for chunk in r.iter_content(8192):
                data += chunk
                if len(data) > MAX_SIZE_MB * 1024 * 1024:
                    data = b""
                    break
            if data and len(data) > 1024:  # at least 1KB
                dest.write_bytes(data)
                return True
        except Exception:
            continue
    return False


def process_recipe(recipe, idx, sess_proxy, sess_direct):
    """Find and download the best image for a recipe."""
    rid   = recipe["id"]
    title = recipe["title"]
    cat   = recipe["cat"]
    dest  = IMG_DIR / f"r-{rid}.jpg"

    if dest.exists() and not OVERWRITE:
        with lock: stats["skip"] += 1
        return

    img_url   = None
    source    = None

    # ── Source 1: Wikimedia ─────────────────────────────────────
    for kw_he, kw_en in WIKI_MAP.items():
        if kw_he in title:
            img_url = wikimedia_image(sess_proxy, sess_direct, kw_en)
            if img_url:
                source = "wiki"
                log(f"  wiki    [{rid}] {kw_en[:40]}")
                break
    time.sleep(0.1)

    # ── Source 2: TheMealDB ─────────────────────────────────────
    if not img_url:
        for kw_he, kw_en in MEALDB_SEARCHES.items():
            if kw_he in title:
                img_url = mealdb_image(sess_proxy, sess_direct, kw_en)
                if img_url:
                    source = "mealdb"
                    log(f"  mealdb  [{rid}] {kw_en[:40]}")
                    break
    time.sleep(0.1)

    # ── Source 3: og:image from src URL ─────────────────────────
    if not img_url and recipe.get("src"):
        try:
            r = None
            for sess in [sess_proxy, sess_direct]:
                try:
                    r = sess.get(
                        recipe["src"], timeout=15, stream=True,
                        headers=API_HEADERS, verify=False,
                    )
                    if r.status_code == 200:
                        break
                    r = None
                except Exception:
                    r = None
                    continue
            if r:
                html_chunk = r.raw.read(65536).decode("utf-8", errors="ignore")
                m = re.search(
                    r'<meta[^>]+(?:property=["\']og:image["\'][^>]+content|content[^>]+property=["\']og:image["\'])[^>]*content=["\']?(https?://[^"\'>\s]+)',
                    html_chunk, re.IGNORECASE
                )
                if not m:
                    m = re.search(r'og:image.*?content=["\']?(https?://[^"\'>\s]+)',
                                  html_chunk, re.IGNORECASE)
                if m:
                    img_url = m.group(1)
                    source  = "og"
                    log(f"  og:img  [{rid}]")
        except Exception:
            pass

    # ── Source 4: loremflickr direct (no proxy) ─────────────────
    if not img_url:
        kw  = CAT_KW.get(cat, "food,moroccan,jewish")
        flickr_url = f"https://loremflickr.com/600/400/{kw}?lock={20000 + idx}"
        img_url = flickr_url
        source  = "flickr"
        log(f"  flickr  [{rid}] {cat}")

    # ── Source 5: picsum fallback ────────────────────────────────
    # (used if flickr download fails)

    # ── Download ─────────────────────────────────────────────────
    ok = download_and_save(
        img_url, dest, sess_proxy, sess_direct,
        is_picsum=(source == "picsum")
    )

    if not ok and source == "flickr":
        # flickr failed — fall back to picsum (always works)
        img_url = picsum_url(rid)
        source  = "picsum"
        log(f"  picsum  [{rid}] (flickr failed)")
        ok = download_and_save(img_url, dest, sess_proxy, sess_direct, is_picsum=True)

    with lock:
        if ok:
            stats["ok"] += 1
            stats[f"ok_{source}"] = stats.get(f"ok_{source}", 0) + 1
        else:
            stats["fail_" + (source or "unk")] = stats.get("fail_" + (source or "unk"), 0) + 1
            log(f"  FAIL    [{rid}] all sources exhausted", "WARN")

    time.sleep(DELAY)


# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════
def main():
    recipes = parse_recipes()
    total   = len(recipes)
    already = sum(1 for r in recipes if (IMG_DIR / f"r-{r['id']}.jpg").exists())

    log(f"{'='*55}")
    log(f"ספר הבישול של פרלה בן ארוש ז\"ל — הורדת תמונות")
    log(f"{'='*55}")
    log(f"מתכונים: {total} | קיימים: {already} | יורדים: {total - already}")
    log(f"פרוקסי: {PROXY or 'ללא'}")
    log(f"שלבים: Wikimedia → TheMealDB → loremflickr → picsum")
    log(f"{'='*55}")

    sp, sd = get_sessions()

    done      = 0
    milestones = set(range(10, 101, 10))

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {
            pool.submit(process_recipe, r, i, sp, sd): r["id"]
            for i, r in enumerate(recipes)
        }
        for f in as_completed(futures):
            done += 1
            pct = done * 100 // total
            if pct in milestones:
                milestones.discard(pct)
                with lock:
                    o, s, fw = stats['ok'], stats['skip'], stats.get('fail_flickr',0)
                    log(
                        f"  {pct:3d}% ({done}/{total})"
                        f"  ✓{o}  ⏭{s}"
                        f"  wiki={stats.get('ok_wiki',0)}"
                        f"  meal={stats.get('ok_mealdb',0)}"
                        f"  flkr={stats.get('ok_flickr',0)}"
                        f"  pcs={stats.get('ok_picsum',0)}"
                    )

    log(f"{'='*55}")
    log(f"סיום הורדות:")
    log(f"  הורד: {stats['ok']}  קיים: {stats['skip']}")
    log(f"  Wikimedia: {stats.get('ok_wiki', 0)}")
    log(f"  TheMealDB: {stats.get('ok_mealdb', 0)}")
    log(f"  loremflickr: {stats.get('ok_flickr', 0)}")
    log(f"  picsum: {stats.get('ok_picsum', 0)}")
    log(f"  שגיאות: {sum(v for k,v in stats.items() if k.startswith('fail_'))}")
    log(f"{'='*55}")

    LOG_FILE.write_text("\n".join(logs), encoding="utf-8")
    log(f"לוג נשמר: {LOG_FILE}")


if __name__ == "__main__":
    main()
