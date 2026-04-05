#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Purpose (Hebrew per project convention):
# הורדת 132 תמונות קטגוריה לאתר ספר הבישול של פרלה בן ארוש זל.
# כל קטגוריה מורידה תמונה אחת בלבד ממקורה ב-Wikipedia.
# תמונות המתכונים משתמשות ישירות בתמונת הקטגוריה שלהן.
# אין יותר קבצים כפולים (-1 ו-2 זהים).
#
# Run : python download_images.py
# Test: DRY_RUN = True
# ---------------------------------------------------------------

# ─────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────
DRY_RUN   = False
PROXY_URL = "http://pac.gov.il:8080"   # set "" to disable

# Seconds to wait between downloads (respect Wikimedia rate limits)
DELAY     = 5.0     # 5 sec between each image download
RETRY_429 = 30.0    # wait 30 sec after a 429 (rate limit hit)
MAX_RETRY = 2       # retries per image

# ─────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────
import os, sys, json, time, re, logging, urllib.request
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
LOGS_DIR   = os.path.join(BASE_DIR, "logs")
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR,   exist_ok=True)

# ─────────────────────────────────────────────────────────────────
#  LOG FILE  (DD-MM-YYYY_HH.MM.log)
# ─────────────────────────────────────────────────────────────────
_log_path = os.path.join(LOGS_DIR, datetime.now().strftime("%d-%m-%Y_%H.%M") + ".log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.FileHandler(_log_path, encoding="utf-8"),
              logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("perla_images")

# ─────────────────────────────────────────────────────────────────
#  PROXY
# ─────────────────────────────────────────────────────────────────
if PROXY_URL:
    urllib.request.install_opener(
        urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": PROXY_URL, "https": PROXY_URL})
        )
    )
    log.info(f"Proxy: {PROXY_URL}")

# ─────────────────────────────────────────────────────────────────
#  HTTP HEADERS
# ─────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
    "Accept"     : "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection" : "keep-alive",
}
WIKI_HEADERS = {
    "User-Agent": "PerlaCookbook/1.0 (personal use; contact: cookbook@example.com)",
    "Accept"    : "application/json",
}

# ─────────────────────────────────────────────────────────────────
#  WIKIPEDIA ARTICLE → ONE IMAGE PER CATEGORY
#  Only {gkey}-1.jpg is created.
#  Recipes use getImages() in the JS to reference this same file.
# ─────────────────────────────────────────────────────────────────
WIKI_ARTICLES = {
    "almond_cookie": "Almond_biscuit",
    "apple_cake": "Apple_cake",
    "baklava": "Baklava",
    "bamia": "Okra",
    "bean_salad": "Bean_salad",
    "bean_soup": "Bean_soup",
    "beet_salad": "Beetroot",
    "beghrir": "Beghrir",
    "borscht": "Borscht",
    "bourekas": "Burekas",
    "bread_rolls": "Bread_roll",
    "brik": "Brik",
    "briouats": "Briouat",
    "cabbage_salad": "Coleslaw",
    "cake": "Cake",
    "carrot_dish": "Carrot",
    "carrot_salad": "Carrot_salad",
    "catalan_cream": "Crema_catalana",
    "cauliflower_dish": "Cauliflower",
    "cauliflower_salad": "Cauliflower",
    "cheese_kugel": "Kugel",
    "chermoula_fish": "Chermoula",
    "chicken_fruit": "Chicken",
    "chicken_lemon": "Moroccan_cuisine",
    "chicken_roast": "Roast_chicken",
    "chicken_soup": "Chicken_soup",
    "chicken_spiced": "Chicken_tikka_masala",
    "chicken_stew": "Chicken_stew",
    "chicken_vegetables": "Chicken_stew",
    "chocolate_cake": "Chocolate_cake",
    "cholent": "Cholent",
    "cookies": "Cookie",
    "couscous": "Couscous",
    "dafina": "Dafina",
    "dates": "Date_palm",
    "dessert_pastry": "Pastry",
    "dolma": "Dolma",
    "donut": "Doughnut",
    "dumpling": "Dumpling",
    "egg_salad": "Egg_salad",
    "eggplant_dish": "Eggplant",
    "eggplant_salad": "Baba_ghanoush",
    "falafel": "Falafel",
    "fish_baked": "Baked_fish",
    "fish_balls": "Gefilte_fish",
    "fish_grilled": "Grilled_fish",
    "fish_soup": "Bouillabaisse",
    "fish_tagine": "Tajine",
    "flatbread": "Flatbread",
    "fritters": "Fritter",
    "garlic_confit": "Confit_of_garlic",
    "gazelle_horns": "Kaab_el_ghzal",
    "gazpacho": "Gazpacho",
    "gefilte": "Gefilte_fish",
    "ghormeh": "Ghormeh_sabzi",
    "grain_soup": "Jareesh",
    "green_beans": "Green_bean",
    "green_salad": "Green_salad",
    "halva": "Halva",
    "harira": "Harira_(food)",
    "harissa": "Harissa",
    "herb_soup": "Herb_soup",
    "hummus": "Hummus",
    "jachnun": "Jachnun",
    "jam": "Fruit_preserve",
    "kadaif": "Kanafeh",
    "kebab": "Kebab",
    "kefta": "Kofta",
    "kubba": "Kibbeh",
    "kuku_sabzi": "Kuku_(dish)",
    "lahoh": "Lahoh",
    "lamb_roasted": "Roast_lamb",
    "lamb_soup": "Lamb_stew",
    "lamb_stew": "Lamb_stew",
    "leek_dish": "Leek",
    "lentil_salad": "Lentil",
    "lentil_soup": "Lentil_soup",
    "liver_dish": "Liver_(food)",
    "mansaf": "Mansaf",
    "matbucha": "Matbucha",
    "meat_stew": "Beef_stew",
    "merguez": "Merguez",
    "milk_dessert": "Blancmange",
    "mofletah": "Mofletta",
    "moroccan_bread": "Khobz",
    "msemen": "Msemen",
    "mujaddara": "Mujaddara",
    "mushroom_dish": "Mushroom",
    "mushroom_soup": "Cream_of_mushroom_soup",
    "offal_dish": "Offal",
    "olives": "Olive",
    "onion_soup": "Onion_soup",
    "orange_salad": "Orange_(fruit)",
    "paella": "Paella",
    "pasta_dish": "Pasta",
    "pastilla": "Bastilla",
    "pickles": "Pickling",
    "pita": "Pita",
    "plov": "Plov",
    "polenta_dish": "Polenta",
    "potato_dish": "Potato",
    "potato_salad": "Potato_salad",
    "preserved_lemon": "Preserved_lemon",
    "pumpkin_dish": "Pumpkin",
    "pumpkin_soup": "Pumpkin_soup",
    "rice_dish": "Pilaf",
    "rice_pudding": "Rice_pudding",
    "roasted_pepper": "Roasted_peppers",
    "roasted_veg": "Vegetable",
    "rugelach": "Rugelach",
    "salad_israeli": "Israeli_salad",
    "samsa": "Samsa_(food)",
    "sardines": "Sardine",
    "schnitzel": "Schnitzel",
    "sfenj": "Sfenj",
    "shakshuka": "Shakshouka",
    "shawarma": "Shawarma",
    "shebakia": "Chebakia",
    "shrimp_dish": "Prawn",
    "sofrito": "Sofrito",
    "spice_blend": "Ras_el_hanout",
    "spinach_dish": "Spinach",
    "stuffed_meat": "Stuffed_meat",
    "stuffed_veg": "Stuffed_peppers",
    "sweet_pastry": "Pastry",
    "sweet_potato_dish": "Sweet_potato",
    "tabbouleh": "Tabbouleh",
    "tagine": "Tajine",
    "tahini": "Tahini",
    "tea": "Maghrebi_mint_tea",
    "tomato_soup": "Tomato_soup",
    "tuna_dish": "Tuna",
    "tzimmes": "Tzimmes",
    "veg_soup": "Vegetable_soup",
    "white_beans": "Navy_bean",
    "yogurt_dip": "Tzatziki",
    "zaalouk": "Zaalouk",
    "zucchini_dish": "Zucchini",
}

# ─────────────────────────────────────────────────────────────────
#  PROGRESS REPORTER
# ─────────────────────────────────────────────────────────────────
def report_progress(i, total, ok, skip, fail):
    pct = int(i / total * 100)
    ms  = (pct // 10) * 10
    if ms > 0 and ms not in report_progress._done:
        report_progress._done.add(ms)
        log.info(f"--- {ms:3d}% ---  {i}/{total}  OK={ok} SKIP={skip} FAIL={fail}")
report_progress._done = set()

# ─────────────────────────────────────────────────────────────────
#  WIKIPEDIA THUMBNAIL RESOLVER
# ─────────────────────────────────────────────────────────────────
def wiki_thumbnail(article):
    """Return thumbnail URL from Wikipedia REST API, or None."""
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + article
    try:
        req = urllib.request.Request(url, headers=WIKI_HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        if "thumbnail" in data:
            src = data["thumbnail"]["source"]
            # Resize to 400px to reduce rate-limit risk
            src = re.sub(r"/\d+px-", "/400px-", src)
            return src
        return None
    except Exception as e:
        log.warning(f"  Wikipedia API [{article}]: {e}")
        return None

# ─────────────────────────────────────────────────────────────────
#  DOWNLOAD ONE IMAGE
# ─────────────────────────────────────────────────────────────────
def download_one(fname, url, dest):
    """Download url → dest.  Returns 'ok' | 'skip' | 'fail'."""
    if os.path.exists(dest) and os.path.getsize(dest) >= 5_000:
        return "skip"
    if DRY_RUN:
        log.info(f"  DRY-RUN {fname}")
        return "ok"
    for attempt in range(1, MAX_RETRY + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=25) as r:
                data = r.read()
            if len(data) < 5_000:
                raise ValueError(f"Too small ({len(data)} B)")
            with open(dest, "wb") as f:
                f.write(data)
            return "ok"
        except Exception as e:
            err = str(e)
            if "429" in err and attempt < MAX_RETRY:
                log.warning(f"  429 on {fname} — waiting {RETRY_429}s (attempt {attempt}/{MAX_RETRY})")
                time.sleep(RETRY_429)
            else:
                log.error(f"  FAIL {fname} — {e}")
                return "fail"
    return "fail"

# ─────────────────────────────────────────────────────────────────
#  MAIN — download ONE file per G key
# ─────────────────────────────────────────────────────────────────
def main():
    total = len(WIKI_ARTICLES)
    log.info("=" * 60)
    log.info("Perla Ben Arosh Cookbook — Image Downloader")
    log.info(f"Mode  : {'DRY-RUN' if DRY_RUN else 'LIVE'}")
    log.info(f"Files : {total} category images  (one per food type)")
    log.info(f"Note  : Recipes use getImages() in JS to reuse category images")
    log.info(f"Note  : No duplicate -2 files created")
    log.info(f"Delay : {DELAY}s between downloads  |  {RETRY_429}s on 429")
    log.info(f"Log   : {_log_path}")
    log.info("=" * 60)

    url_cache = {}   # article → resolved image URL (skip re-resolving duplicates)
    ok = fail = skip = 0

    for i, (gkey, article) in enumerate(WIKI_ARTICLES.items(), 1):
        fname = gkey.replace("_", "-") + "-1.jpg"
        dest  = os.path.join(IMAGES_DIR, fname)

        log.info(f"[{i:3d}/{total}] {gkey} → Wikipedia:{article}")

        # Resolve thumbnail URL (cache to avoid duplicate API calls)
        if article in url_cache:
            img_url = url_cache[article]
            log.info(f"  (reusing resolved URL for {article})")
        else:
            img_url = wiki_thumbnail(article)
            if img_url:
                url_cache[article] = img_url
            else:
                log.warning(f"  No thumbnail for {article!r} — skipping")
                fail += 1
                report_progress(i, total, ok, skip, fail)
                continue

        # Download
        result = download_one(fname, img_url, dest)
        if result == "ok":
            ok += 1
            size = os.path.getsize(dest) // 1024 if not DRY_RUN else 0
            log.info(f"  OK    {fname} ({size} KB)")
        elif result == "skip":
            skip += 1
            log.info(f"  SKIP  {fname} (already exists)")
        else:
            fail += 1

        report_progress(i, total, ok, skip, fail)
        time.sleep(DELAY)   # pause every download — respect rate limits

    log.info("=" * 60)
    log.info(f"SUMMARY  OK={ok}  SKIP={skip}  FAIL={fail}  Total={total}")
    if fail:
        log.warning(f"{fail} failed — re-run to retry (existing files are skipped).")
    log.info(f"Log: {_log_path}")
    log.info("=" * 60)

if __name__ == "__main__":
    main()
