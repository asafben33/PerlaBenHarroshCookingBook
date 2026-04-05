#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_images.py — ספר הבישול של פרלה בן ארוש ז"ל
======================================================
מוריד תמונה ספציפית לכל מתכון בדיוק:
 - תמונה של המנה המוגמרת
 - אם לא נמצא: תמונה של המרכיבים העיקריים

מקורות (לפי עדיפות):
  1. TheMealDB API   — 300+ תמונות מנות אמיתיות, ללא מפתח
  2. Wikimedia Commons API — חיפוש לפי שם המנה באנגלית
  3. Open Food Images  — DuckDuckGo Images API (ללא מפתח, ציבורי)
  4. Unsplash via URL  — חיפוש תמונות אוכל ספציפי לפי שאילתה

הפעלה: python download_images.py
דרישות: pip install requests
"""
import os, re, sys, time, json, threading, hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from urllib.parse import quote_plus

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    print("pip install requests"); sys.exit(1)

# ══════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════
SCRIPT_DIR = Path(__file__).parent
DATA_SRC   = next((SCRIPT_DIR/f for f in ("data.js","index.html") if (SCRIPT_DIR/f).exists()), None)
IMG_DIR    = SCRIPT_DIR / "images"          # ← תמיד images/ בלבד, לא images/spam/
LOG_FILE   = SCRIPT_DIR / "download_images.log"

PROXY      = "http://pac.gov.il:8080"
DELAY      = 0.3                             # שניות בין הורדות
OVERWRITE  = True                           # True = דרוס קיים; False = דלג
WORKERS    = 2                               # threads — נמוך יותר כדי לא להיתקע
TIMEOUT    = 15
IMG_DIR.mkdir(parents=True, exist_ok=True)

lock  = threading.Lock()
logs  = []
stats = dict(ok=0, skip=0, fail=0, mealdb=0, wiki=0, ddg=0)

def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with lock: logs.append(line)
    print(line, flush=True)

# ══════════════════════════════════════════════════════
# מילון עברית→אנגלית מקיף לשמות מנות
# ══════════════════════════════════════════════════════
HE2EN = {
    # ─ מרקים ─────────────────────────────────────────
    "חרירה":"harira moroccan soup",
    "ביסארה":"moroccan fava bean soup",
    "מרק עדשים":"lentil soup",
    "מרק שעועית":"bean soup",
    "מרק עוף":"chicken soup",
    "מרק ירקות":"moroccan vegetable soup",
    "מרק עגבניות":"tomato soup",
    "מרק דלעת":"pumpkin soup",
    "בורשט":"borscht beet soup",
    "מרק בצל":"french onion soup",
    "מרק פטריות":"mushroom cream soup",
    "מרק פול":"fava bean soup moroccan",
    "לחשו":"moroccan semolina garlic soup",
    "מרק מחמר":"moroccan red chicken soup",
    "מרק קובה":"kubbe soup",
    # ─ סלטים ─────────────────────────────────────────
    "מטבוחה":"matbucha moroccan tomato pepper",
    "זאלוק":"zaalouk moroccan eggplant",
    "זעלוק":"zaalouk moroccan eggplant",
    "טקטוקה":"taktouka moroccan pepper tomato",
    "טבולה":"tabbouleh parsley",
    "חומוס":"hummus chickpea",
    "סלט גזר":"moroccan carrot salad",
    "סלט כרוב":"moroccan coleslaw salad",
    "סלט עגבניות":"moroccan tomato salad",
    "סלט תפוחי אדמה":"potato salad moroccan",
    "סלט סלק":"beet salad",
    "פול":"fava bean salad",
    "לוביה":"black eyed peas salad",
    "שנקליש":"shanklish cheese salad",
    "סלט תפוז":"orange olive moroccan salad",
    "סלט פלפל":"roasted pepper salad moroccan",
    # ─ ירקות ──────────────────────────────────────────
    "חצילים ברוטב":"moroccan eggplant tomato",
    "קישואים":"zucchini moroccan",
    "כרובית":"roasted cauliflower chermoula",
    "מעקודה":"moroccan potato patties",
    "במיה":"okra tomato stew",
    "שעועית ירוקה":"green beans tomato moroccan",
    "כרוב מבושל":"moroccan braised cabbage",
    "פלפל ממולא":"moroccan stuffed peppers",
    "דלעת מתוקה":"moroccan sweet pumpkin",
    "תרד":"spinach chickpea moroccan",
    "שעועית לבנה":"white bean stew moroccan",
    "ארטישוק":"artichoke stew moroccan",
    # ─ בשר ────────────────────────────────────────────
    "קציצות בקר":"moroccan beef meatballs kefta",
    "קציצות עם חומוס":"meatballs hummus moroccan",
    "תבשיל בשר עם שזיפים":"moroccan lamb plums almonds",
    "בשר ראש":"moroccan head meat",
    "חמין אשכנזי":"cholent ashkenazi",
    "חמין":"dafina moroccan cholent",
    "סקינה":"skhina moroccan sabbath",
    "מרוזייה":"mrouzia moroccan lamb honey",
    "כבד":"chopped liver moroccan",
    "ח׳לייע":"khlii preserved moroccan meat",
    "כבש":"moroccan lamb tagine",
    # ─ עוף ────────────────────────────────────────────
    "עוף עם זיתים ולימון":"moroccan chicken preserved lemon olives",
    "עוף עם שקדים וצימוקים":"moroccan chicken almonds raisins",
    "עוף עם פירות יבשים":"moroccan chicken dried fruits",
    "עוף עם בצל":"moroccan chicken caramelized onions",
    "עוף עם שזיפים":"moroccan chicken prunes",
    "עוף עם כורכום":"moroccan chicken turmeric",
    "עוף ביין":"moroccan chicken red wine braised",
    "קוסקוס חגיגי":"moroccan couscous chicken friday",
    "קוסקוס":"moroccan couscous",
    "טאג׳ין עוף":"chicken tagine moroccan",
    "טאג׳ין כבש":"lamb tagine moroccan",
    "מחמר":"mahmar moroccan chicken paprika",
    "שוורמה":"chicken shawarma",
    # ─ דגים ──────────────────────────────────────────
    "דג חריף":"spicy moroccan fish",
    "דג עם צ׳רמולה":"fish chermoula moroccan",
    "קציצות דגים":"moroccan fish balls",
    "סרדינים":"sardines moroccan",
    "חריימה":"chraime spicy fish libyan",
    "דג מלוח":"salted preserved fish moroccan",
    "שמורא":"preserved fish moroccan",
    "גפילטע פיש":"gefilte fish jewish",
    # ─ חגים ───────────────────────────────────────────
    "עוף חגיגי עם פירות יבשים":"moroccan chicken dried fruits festive",
    "מאפה בשר":"moroccan meat pastry",
    "טאג׳ין חגיגי עם שזיפים":"moroccan lamb tagine plums almonds",
    "סלטים חגיגיים":"moroccan mezze salads festive",
    "חרוסת":"charoset passover moroccan",
    "מימונה":"mimouna moroccan celebration",
    # ─ קינוחים ────────────────────────────────────────
    "מופלטה":"mofletah moroccan pancake",
    "ספינג׳":"sfenj moroccan donuts",
    "מקרוד":"makroud moroccan semolina dates",
    "עוגיות שקדים":"moroccan almond cookies",
    "עוגיות אניס":"moroccan anise sesame cookies",
    "שלדה":"chebakia moroccan sesame honey",
    "כעב הגזאל":"gazelle horns almond pastry",
    "בריואט":"briouat moroccan fried pastry",
    "תה נענע":"moroccan mint tea glass",
    "עוגת תפוז":"moroccan orange almond cake",
    "ריבה":"moroccan jam preserve",
    "חלוה":"halva sesame sweet",
    "בקלווה":"baklava honey walnut",
    # ─ ספרדי ──────────────────────────────────────────
    "סופריטו":"sofrito spanish sauce",
    "אלבונדיגס":"albondigas spanish meatballs",
    "גספאצ׳ו":"gazpacho cold soup andalusian",
    "אמפנדה":"empanada spanish baked",
    "אארוז עם עוף":"arroz con pollo spanish",
    "פאייה":"paella seafood spanish",
    "בורקס":"borek phyllo pastry",
    # ─ עיראקי ─────────────────────────────────────────
    "קובה בסלק":"kibbeh beetroot soup iraqi",
    "קובה חמוסטה":"kibbeh hamusta lemon soup iraqi",
    "קובה":"kibbeh Iraqi",
    "דולמה":"dolma stuffed vegetables",
    "תמר הינדי":"tamarind drink Iraqi",
    "מסגוף":"masgouf grilled fish Tigris Iraqi",
    "תבית":"tebeet Iraqi stuffed chicken rice",
    # ─ כורדי ──────────────────────────────────────────
    "קובה קדרה":"kibbeh cream Kurdish",
    "שישבראק":"shishbarak dumplings yogurt",
    "כישקה":"kishka stuffed Kurdish",
    "דמפוכת עוף":"Kurdish chicken pot",
    # ─ אשכנזי ─────────────────────────────────────────
    "חמין אשכנזי":"cholent ashkenazi bean potato",
    "לאקשן קוגל":"noodle kugel baked jewish",
    "קוגל תפוח אדמה":"potato kugel jewish",
    "בינטש":"potato latke pancake",
    "קרפלך":"kreplach meat dumplings soup",
    "כבד קצוץ":"chopped liver jewish",
    "בורשט":"borscht beet soup eastern european",
    # ─ תימני ──────────────────────────────────────────
    "ג׳חנון":"jachnun yemeni pastry",
    "לחוח":"lahoh yemeni sponge pancake",
    "זחוק":"zhug yemeni green hot sauce",
    "הילבה":"hilbeh yemeni fenugreek paste",
    "מרק עצמות תימני":"yemeni bone broth soup",
    "כסבה":"kusba yemeni rice raisins",
    # ─ פרסי ───────────────────────────────────────────
    "גורמה סבזי":"ghormeh sabzi persian herb stew",
    "קוקו סבזי":"kuku sabzi persian herb frittata",
    "פסנג׳ן":"fesenjan pomegranate walnut duck",
    "ג׳ווארי":"ash reshteh persian noodle soup",
    "ירקות ממולאים פרסיים":"dolmeh persian stuffed vegetables",
    # ─ בוכארי ─────────────────────────────────────────
    "אוש":"plov osh uzbek rice lamb",
    "פלוב":"plov uzbek rice carrots",
    "סמסה":"samsa baked pastry meat",
    "מנטי":"manti steamed dumplings",
    "נאן בוכארי":"bukharian naan bread",
    # ─ טוניסאי ────────────────────────────────────────
    "ברייק":"brik tunisian egg pastry",
    "חריסה":"harissa tunisian chili paste",
    "קוסקוס טוניסאי":"tunisian couscous lamb",
    "מחמורה":"mahmoura tunisian almond cookies",
    "מלצוניה":"tunisian spiced fish",
    "לבלבי":"lablabi tunisian chickpea",
    # ─ טורקי ──────────────────────────────────────────
    "בורקס טורקי":"borek turkish cheese spinach",
    "קלדאוס":"caldeirada turkish fish stew",
    "מנדה":"Turkish fish patties",
    "אגריסטה":"agristada turkish lemon chicken",
    "בורמואלוס":"Turkish hanukkah fritters",
    # ─ ישראלי ─────────────────────────────────────────
    "פלאפל":"falafel pita Israeli street food",
    "חומוס ביתי":"hummus Israeli",
    "שקשוקה":"shakshuka eggs tomato Israeli",
    "מג׳דרה":"mujaddara lentils rice crispy onion",
    "שוורמה עוף":"chicken shawarma wrap",
    "סביח":"sabich eggplant pita Israeli",
    "מג׳דרה":"mujaddara lentil rice onion",
}

# TheMealDB — מנות מאומתות עם תמונות אמיתיות
MEALDB_QUERIES = {
    "harira":"Harira", "couscous":"Couscous", "chicken lemon":"Moroccan Chicken",
    "shakshuka":"Shakshuka", "hummus":"Hummus", "falafel":"Falafel",
    "shawarma":"Chicken Shawarma", "mujaddara":"Mujaddara", "tabbouleh":"Tabbouleh",
    "gazpacho":"Gazpacho", "paella":"Seafood Paella", "lentil soup":"Red Lentil Soup",
    "kefta":"Kofta Curry", "cholent":"Cholent", "ghormeh":"Ghormeh Sabzi",
    "fesenjan":"Fesenjan", "kibbeh":"Kibbeh", "dolma":"Dolmades",
    "jachnun":"Jachnun", "gefilte":"Gefilte Fish", "chraime":"Chraime",
    "albondigas":"Albondigas", "empanada":"Empanadas", "borek":"Borek",
    "baklava":"Baklava", "brik":"Brik", "plov":"Plov", "manti":"Manti",
    "borscht":"Borscht", "sfenj":"Sfenj", "mofletah":"Mofletah",
}

# ══════════════════════════════════════════════════════
# SESSION
# ══════════════════════════════════════════════════════
HDRS = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept":"image/webp,image/apng,image/*,*/*;q=0.8",
}
_sp = _sd = None

def get_sessions():
    global _sp, _sd
    if _sp is None:
        def mk(proxy=None):
            s = requests.Session()
            if proxy: s.proxies={"http":proxy,"https":proxy}
            s.mount("https://", HTTPAdapter(max_retries=Retry(2,backoff_factor=0.5,status_forcelist=[429,500,502,503])))
            s.verify = False
            s.headers.update(HDRS)
            return s
        _sp = mk(PROXY)
        _sd = mk(None)
    return _sp, _sd

def safe_get(url, sp, sd, stream=False, timeout=None):
    """Try proxy then direct. Returns response or None."""
    t = timeout or TIMEOUT
    for sess in [sp, sd]:
        try:
            r = sess.get(url, timeout=t, stream=stream, allow_redirects=True)
            if r.status_code == 200:
                return r
        except Exception:
            continue
    return None

# ══════════════════════════════════════════════════════
# RECIPE PARSER
# ══════════════════════════════════════════════════════
def parse_recipes():
    if not DATA_SRC:
        log("ERROR: data.js or index.html not found"); sys.exit(1)
    src = DATA_SRC.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"id:'([^']+)',\s*cat:'([^']+)'[^;{]*?title:'([^']+)'[^;{]*?(?:ingr:\[([^\]]{0,400})\])?", src, re.DOTALL):
        ingr_raw = m.group(4) or ""
        ingr_names = re.findall(r"i:'([^']+)'", ingr_raw)[:5]
        out.append({"id":m.group(1),"cat":m.group(2),"title":m.group(3),"ingr":ingr_names})
    return out

# ══════════════════════════════════════════════════════
# QUERY BUILDER — title + ingr → English search query
# ══════════════════════════════════════════════════════
CAT_EN = {
    "soups":"moroccan soup","salads":"moroccan salad mezze",
    "veg":"moroccan vegetable dish","meat":"moroccan meat tagine",
    "chick":"moroccan chicken","fish":"moroccan spiced fish",
    "hol":"moroccan festive food","des":"moroccan pastry sweets",
    "span":"sephardic spanish jewish food","iraq":"iraqi jewish food",
    "kurd":"kurdish jewish food","ashk":"ashkenazi jewish food",
    "yem":"yemeni jewish food","pers":"persian jewish food",
    "buk":"bukharian uzbek rice plov","tun":"tunisian jewish food",
    "isr":"israeli food","turk":"turkish jewish borek",
}

def build_query(recipe):
    """Build precise English food search query from Hebrew title + ingredients."""
    title = recipe["title"]
    cat   = recipe["cat"]
    ingr  = recipe.get("ingr", [])

    # 1. Direct dictionary lookup
    for he, en in HE2EN.items():
        if he in title:
            return en

    # 2. Partial keyword matching
    kw_map = [
        ("קציצות","kefta meatballs moroccan"),("עוף","moroccan chicken"),
        ("כבש","moroccan lamb tagine"),("דג","moroccan fish"),
        ("מרק","moroccan soup"),("סלט","moroccan salad"),
        ("תבשיל","moroccan stew"),("עוגיות","moroccan cookies"),
        ("לחם","moroccan bread"),("אורז","moroccan rice dish"),
        ("קוסקוס","couscous moroccan"),("פסטה","pasta"),
        ("חצילים","eggplant moroccan"),("עגבניות","tomato moroccan dish"),
        ("גזר","carrot moroccan"),("כרובית","cauliflower dish"),
        ("פלפל","pepper stuffed moroccan"),("תרד","spinach dish"),
        ("שעועית","bean stew moroccan"),("חומוס","chickpea hummus"),
        ("ביצים","eggs shakshuka"),("גבינה","cheese pastry"),
        ("שקדים","almond pastry moroccan"),("דבש","honey moroccan"),
        ("שזיפים","lamb prunes moroccan tagine"),("זיתים","olives moroccan"),
        ("לימון","lemon preserved moroccan"),("טאג׳ין","tagine moroccan"),
    ]
    for he, en in kw_map:
        if he in title:
            return en

    # 3. Use category + first ingredient
    cat_en = CAT_EN.get(cat, "moroccan jewish food")
    if ingr:
        return f"{cat_en} {ingr[0]}"
    return cat_en

# ══════════════════════════════════════════════════════
# SOURCE 1: TheMealDB
# ══════════════════════════════════════════════════════
def try_mealdb(query, sp, sd):
    """Search TheMealDB for food image. Returns URL or None."""
    # Check if any keyword matches our MEALDB_QUERIES mapping
    q_lower = query.lower()
    meal_name = None
    for kw, name in MEALDB_QUERIES.items():
        if kw in q_lower:
            meal_name = name
            break
    if not meal_name:
        # Try first two words of query
        meal_name = " ".join(query.split()[:2])

    try:
        r = safe_get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={quote_plus(meal_name)}", sp, sd, timeout=8)
        if r:
            meals = (r.json().get("meals") or [])
            if meals:
                thumb = meals[0].get("strMealThumb","")
                if thumb:
                    return thumb  # direct HD image URL
    except Exception:
        pass
    return None

# ══════════════════════════════════════════════════════
# SOURCE 2: Wikimedia Commons API
# ══════════════════════════════════════════════════════
def try_wikimedia(query, sp, sd):
    """Search Wikimedia Commons. Returns image URL or None."""
    try:
        r = safe_get(
            "https://commons.wikimedia.org/w/api.php",
            sp, sd, timeout=10
        )
        # Need to pass params directly
        for sess in [sp, sd]:
            try:
                resp = sess.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params={"action":"query","list":"search",
                            "srsearch":f"{query} food dish recipe",
                            "srnamespace":6,"srlimit":8,"format":"json"},
                    timeout=10, verify=False
                )
                if resp.status_code != 200: continue
                results = resp.json().get("query",{}).get("search",[])
                for res in results:
                    title = res.get("title","")
                    if not title.startswith("File:"): continue
                    tl = title.lower()
                    # Skip non-food images
                    if any(skip in tl for skip in ["map","flag","diagram","logo","icon","symbol","portrait","building"]): continue
                    if not any(ext in tl for ext in [".jpg",".jpeg",".png"]): continue
                    # Get actual URL
                    r2 = sess.get(
                        "https://commons.wikimedia.org/w/api.php",
                        params={"action":"query","titles":title,"prop":"imageinfo",
                                "iiprop":"url|size|mime","iiurlwidth":400,"format":"json"},
                        timeout=10, verify=False
                    )
                    if r2.status_code != 200: continue
                    for pg in r2.json().get("query",{}).get("pages",{}).values():
                        ii = pg.get("imageinfo",[{}])[0]
                        url  = ii.get("thumburl") or ii.get("url","")
                        mime = ii.get("mime","")
                        sz   = ii.get("size",0)
                        if url and "image" in mime and 5000 < sz < 8*1024*1024:
                            return url
                break
            except Exception:
                continue
    except Exception:
        pass
    return None

# ══════════════════════════════════════════════════════
# SOURCE 3: DuckDuckGo Image Search (unofficial, no key)
# ══════════════════════════════════════════════════════
def try_ddg(query, sp, sd):
    """Use DuckDuckGo instant answer API for images. Returns URL or None."""
    try:
        # DDG image search — get vqd token first
        search_url = f"https://duckduckgo.com/?q={quote_plus(query+' food recipe photo')}&iax=images&ia=images"
        for sess in [sd]:  # use direct only for DDG
            try:
                r = sess.get(search_url, timeout=8, verify=False,
                             headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"})
                if r.status_code != 200: continue
                vqd = re.search(r'vqd="([^"]+)"', r.text)
                if not vqd: continue
                # Fetch image results
                r2 = sess.get(
                    "https://duckduckgo.com/i.js",
                    params={"l":"us-en","o":"json","q":query+" food recipe",
                            "vqd":vqd.group(1),"f":",,,,,","p":"1"},
                    timeout=8, verify=False,
                    headers={"Referer":"https://duckduckgo.com/",
                             "Accept":"application/json",
                             "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
                )
                if r2.status_code != 200: continue
                results = r2.json().get("results",[])
                for res in results:
                    img_url = res.get("image","")
                    # Filter: must be from trusted food sites
                    trusted = ["wikimedia","themealdb","allrecipes","foodnetwork",
                               "bonappetit","food52","seriouseats","epicurious",
                               "cooking.nytimes","bbcgoodfood","wikipedia"]
                    if any(t in img_url.lower() for t in trusted):
                        # Verify it's actually an image
                        rimg = sess.get(img_url, timeout=5, stream=True, verify=False)
                        if rimg.status_code == 200 and "image" in rimg.headers.get("Content-Type",""):
                            return img_url
                    # Even untrusted — just take first that looks like food
                    if img_url and any(kw in img_url.lower() for kw in ["food","recipe","cook","meal","dish"]):
                        return img_url
            except Exception:
                continue
    except Exception:
        pass
    return None

# ══════════════════════════════════════════════════════
# DOWNLOAD & VALIDATE
# ══════════════════════════════════════════════════════
def download_image(url, dest, sp, sd):
    """Download and validate image. Returns True if saved successfully."""
    for sess in [sp, sd]:
        try:
            r = sess.get(url, timeout=TIMEOUT, stream=True, allow_redirects=True)
            if r.status_code != 200: continue
            ct = r.headers.get("Content-Type","")
            if "image" not in ct and "jpeg" not in ct and "jpg" not in ct: continue
            data = b"".join(r.iter_content(8192))
            # Basic validation: must be > 5KB and start with JPEG/PNG/GIF magic bytes
            if len(data) < 5000: continue
            magic = data[:4]
            is_img = (magic[:2] == b'\xff\xd8' or      # JPEG
                      magic[:4] == b'\x89PNG' or        # PNG
                      magic[:3] == b'GIF')               # GIF
            if not is_img:
                # Accept if Content-Type says image
                if "image" in ct and len(data) > 10000:
                    is_img = True
            if is_img:
                dest.write_bytes(data)
                return True
        except Exception:
            continue
    return False

# ══════════════════════════════════════════════════════
# PROCESS ONE RECIPE
# ══════════════════════════════════════════════════════
def process_recipe(recipe, idx):
    rid, cat, title = recipe["id"], recipe["cat"], recipe["title"]
    dest = IMG_DIR / f"r-{rid}.jpg"

    if dest.exists() and not OVERWRITE:
        with lock: stats["skip"] += 1
        return True

    sp, sd = get_sessions()
    query  = build_query(recipe)
    log(f"  [{rid:8s}] {title[:30]:30s} → \"{query[:40]}\"")

    # ── Source 1: TheMealDB ─────────────────────────
    img_url = try_mealdb(query, sp, sd)
    if img_url and download_image(img_url, dest, sp, sd):
        with lock: stats["ok"] += 1; stats["mealdb"] += 1
        log(f"  ✓ mealdb [{rid}]")
        time.sleep(DELAY)
        return True
    time.sleep(0.1)

    # ── Source 2: Wikimedia Commons ─────────────────
    img_url = try_wikimedia(query, sp, sd)
    if img_url and download_image(img_url, dest, sp, sd):
        with lock: stats["ok"] += 1; stats["wiki"] += 1
        log(f"  ✓ wiki   [{rid}]")
        time.sleep(DELAY)
        return True
    time.sleep(0.1)

    # ── Source 3: DuckDuckGo ─────────────────────────
    img_url = try_ddg(query, sp, sd)
    if img_url and download_image(img_url, dest, sp, sd):
        with lock: stats["ok"] += 1; stats["ddg"] += 1
        log(f"  ✓ ddg    [{rid}]")
        time.sleep(DELAY)
        return True

    # ── All failed ───────────────────────────────────
    with lock: stats["fail"] += 1
    log(f"  ✗ FAIL   [{rid}] {title[:30]}")
    time.sleep(DELAY)
    return False

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    recipes = parse_recipes()
    total   = len(recipes)
    already = sum(1 for r in recipes if (IMG_DIR/f"r-{r['id']}.jpg").exists() and not OVERWRITE)

    log("=" * 60)
    log(f"ספר הבישול של פרלה בן ארוש ז\"ל — הורדת תמונות")
    log("=" * 60)
    log(f"מתכונים: {total} | קיימים: {already} | לורדה: {total-already}")
    log(f"תיקייה: {IMG_DIR}")
    log(f"מקורות: TheMealDB → Wikimedia Commons → DuckDuckGo")
    log(f"WORKERS={WORKERS} | TIMEOUT={TIMEOUT}s | OVERWRITE={OVERWRITE}")
    log("=" * 60)
    log("")
    log("לביטול: Ctrl+C (יישמר הלוג ומה שהורד)")
    log("")

    get_sessions()   # init sessions once

    done = 0
    milestones = set(range(10, 101, 10))

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(process_recipe, r, i): r["id"]
                   for i, r in enumerate(recipes)}
        try:
            for f in as_completed(futures, timeout=3600):
                done += 1
                pct = done * 100 // total
                if pct in milestones:
                    milestones.discard(pct)
                    with lock:
                        log(f"\n  ── {pct}% ({done}/{total}) "
                            f"✓{stats['ok']}  ⏭{stats['skip']}  ✗{stats['fail']}  "
                            f"[mealdb={stats['mealdb']} wiki={stats['wiki']} ddg={stats['ddg']}]\n")
        except KeyboardInterrupt:
            log("\nעצירה ידנית — שומר לוג...")
            pool.shutdown(wait=False)

    log("=" * 60)
    log(f"סיום: ✓{stats['ok']}  ⏭{stats['skip']}  ✗{stats['fail']}")
    log(f"  TheMealDB: {stats['mealdb']}  Wikimedia: {stats['wiki']}  DDG: {stats['ddg']}")
    log(f"תיקייה: {IMG_DIR}")
    log("=" * 60)
    LOG_FILE.write_text("\n".join(logs), encoding="utf-8")
    log(f"לוג: {LOG_FILE}")

if __name__ == "__main__":
    main()
