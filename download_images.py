#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_images.py — ספר הבישול של פרלה בן ארוש ז"ל
======================================================
גרסה מחוזקת: עמידה בפני תקיעות, Ctrl+C עובד תמיד,
לוג נשמר אחרי כל מתכון, timeout גלובלי על כל socket.

הפעלה: python download_images.py
דרישות: pip install requests
"""
import os, re, sys, time, signal, socket
from pathlib import Path

# ── global socket timeout BEFORE any import of requests/urllib3 ──
# This is the only reliable way to prevent hung network calls on Windows.
socket.setdefaulttimeout(8)

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    print("ERROR: pip install requests"); sys.exit(1)

# ══════════════════════════════════════════════════
# CONFIG — ערוך כאן
# ══════════════════════════════════════════════════
SCRIPT_DIR  = Path(__file__).parent
IMG_DIR     = SCRIPT_DIR / "images"          # תיקיית פלט — תמיד images/
LOG_FILE    = SCRIPT_DIR / "./logs/download_images.log"

# פרוקסי לסקריפט ההורדה בלבד.  None = ללא פרוקסי
PROXY       = "http://pac.gov.il:8080"

DELAY       = 0.4    # שניות בין מתכונים (מניעת חסימה)
NET_TIMEOUT = 6      # שניות לכל בקשת רשת  (< socket global timeout=8)
OVERWRITE   = True  # True = דרוס קיימים

IMG_DIR.mkdir(parents=True, exist_ok=True)

# ── Ctrl+C handler — saves log and exits cleanly ──
_STOP = False
def _sigint(sig, frame):
    global _STOP
    _STOP = True
    print("\n\n[!] עצירה — שומר לוג ויוצא...")
signal.signal(signal.SIGINT, _sigint)

# ── log — writes to file immediately after each call ──
def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

# ══════════════════════════════════════════════════
# HTTP sessions — proxy + direct
# ══════════════════════════════════════════════════
HDRS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8",
}
API_HDRS = {
    "User-Agent": HDRS["User-Agent"],
    "Accept": "application/json,text/html,*/*",
}

def _make_sess(proxy=None):
    s = requests.Session()
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    # Only 1 retry — we don't want long waits
    s.mount("https://", HTTPAdapter(max_retries=Retry(1, backoff_factor=0.3,
                                    status_forcelist=[429, 500, 502, 503])))
    s.mount("http://",  HTTPAdapter(max_retries=Retry(1, backoff_factor=0.3)))
    s.verify = False
    s.headers.update(HDRS)
    return s

_sess_proxy  = None
_sess_direct = None

def get_sess():
    global _sess_proxy, _sess_direct
    if _sess_proxy is None:
        _sess_proxy  = _make_sess(PROXY)
        _sess_direct = _make_sess(None)
    return _sess_proxy, _sess_direct

def _get(url, api=False, stream=False):
    """Try proxy first, then direct. Returns response or None.
    Never hangs thanks to socket.setdefaulttimeout(8)."""
    sp, sd = get_sess()
    hdrs = API_HDRS if api else HDRS
    for sess in [sp, sd]:
        try:
            r = sess.get(url, timeout=NET_TIMEOUT, stream=stream,
                         allow_redirects=True, headers=hdrs)
            if r.status_code == 200:
                return r
        except Exception:
            continue
    return None

# ══════════════════════════════════════════════════
# PARSE RECIPES from data.js / index.html
# ══════════════════════════════════════════════════
def parse_recipes():
    src_path = next(
        (SCRIPT_DIR / f for f in ("data.js", "index.html")
         if (SCRIPT_DIR / f).exists()), None
    )
    if not src_path:
        log("ERROR: לא נמצא data.js או index.html"); sys.exit(1)
    src = src_path.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(
        r"id:'([^']+)',\s*cat:'([^']+)'[^;{]*?title:'([^'\n]+)'[^;{]*?(?:ingr:\[([^\]]{0,300})\])?",
        src, re.DOTALL
    ):
        ingr_raw = m.group(4) or ""
        ingrs = re.findall(r"i:'([^']+)'", ingr_raw)[:4]
        out.append({"id": m.group(1), "cat": m.group(2),
                    "title": m.group(3), "ingr": ingrs})
    return out

# ══════════════════════════════════════════════════
# מילון עברית → שאילתת חיפוש אנגלית
# מקיף + מדויק לכל 18 קטגוריות
# ══════════════════════════════════════════════════
TITLE_QUERIES = [
    # מרקים
    ("חרירה",           "harira moroccan soup"),
    ("ביסארה",          "bissara moroccan fava bean soup"),
    ("מרק עדשים",       "moroccan red lentil soup"),
    ("מרק שעועית",      "moroccan white bean soup"),
    ("מרק עוף",         "moroccan chicken soup"),
    ("מרק ירקות",       "moroccan vegetable soup"),
    ("מרק עגבניות",     "moroccan tomato garlic soup"),
    ("מרק דלעת",        "moroccan pumpkin spiced soup"),
    ("מרק פול",         "moroccan fava bean green soup"),
    ("מרק פטריות",      "cream mushroom soup"),
    ("מרק בצל",         "french onion soup"),
    ("בורשט",           "borscht beetroot soup"),
    ("קלדו",            "caldo jewish broth soup"),
    ("לחשו",            "moroccan semolina garlic harissa soup"),
    # סלטים
    ("מטבוחה",          "matbucha moroccan tomato pepper salad"),
    ("זאלוק",           "zaalouk moroccan eggplant salad"),
    ("זעלוק",           "zaalouk moroccan eggplant salad"),
    ("טקטוקה",          "taktouka moroccan roasted pepper tomato"),
    ("חומוס",           "hummus chickpea tahini"),
    ("סלט גזר",         "moroccan cooked carrot salad"),
    ("סלט חצילים",      "moroccan eggplant roasted salad"),
    ("סלט פלפל",        "moroccan roasted pepper salad"),
    ("סלט כרוב",        "moroccan coleslaw cabbage salad"),
    ("סלט עגבניות",     "moroccan tomato herb salad"),
    ("סלט תפוחי אדמה",  "moroccan potato salad"),
    ("סלט סלק",         "moroccan beet salad"),
    ("טבולה",           "tabbouleh parsley salad"),
    ("פול",             "foul medames fava bean salad"),
    ("לוביה",           "black eyed peas salad"),
    # ירקות
    ("חצילים",          "moroccan eggplant tomato stew"),
    ("קישואים",         "moroccan zucchini garlic coriander"),
    ("כרובית",          "moroccan roasted cauliflower chermoula"),
    ("מעקודה",          "maakouda moroccan potato patties"),
    ("במיה",            "bamia okra tomato stew"),
    ("שעועית ירוקה",    "moroccan green beans tomato"),
    ("כרוב מבושל",      "moroccan braised cabbage"),
    ("פלפל ממולא",      "moroccan stuffed peppers rice meat"),
    ("קישוא ממולא",     "moroccan stuffed zucchini"),
    ("דלעת מתוקה",      "moroccan sweet pumpkin honey cinnamon"),
    ("תרד",             "moroccan spinach chickpea"),
    ("שעועית לבנה",     "moroccan white bean stew"),
    ("ארטישוק",         "moroccan artichoke stew"),
    # בשר
    ("קציצות",          "kefta moroccan meatballs tomato egg"),
    ("תבשיל בשר",       "moroccan beef stew prunes almonds"),
    ("כבש",             "moroccan lamb tagine"),
    ("חמין",            "dafina moroccan jewish sabbath stew"),
    ("סקינה",           "skhina moroccan jewish stew"),
    ("מרוזייה",         "mrouzia moroccan lamb honey raisins"),
    ("ח׳לייע",          "khlii moroccan preserved meat"),
    ("כבד",             "moroccan chopped liver onions"),
    ("קובה",            "kibbeh soup iraqi"),
    ("כבש ושזיפים",     "moroccan lamb tagine prunes almonds"),
    # עוף
    ("עוף עם זיתים",    "moroccan chicken preserved lemon olives"),
    ("עוף עם שקדים",    "moroccan chicken almonds raisins"),
    ("עוף עם פירות יבשים","moroccan chicken dried apricots"),
    ("עוף עם בצל",      "moroccan chicken caramelized onions"),
    ("עוף עם שזיפים",   "moroccan chicken prunes tagine"),
    ("עוף ביין",        "moroccan chicken red wine braised"),
    ("קוסקוס",          "moroccan couscous chicken vegetables"),
    ("טאג׳ין עוף",      "chicken tagine moroccan clay pot"),
    ("שוורמה",          "chicken shawarma wrap"),
    ("מחמר",            "mahmar moroccan paprika chicken"),
    # דגים
    ("דג חריף",         "moroccan spicy fish chermoula"),
    ("דג עם צ׳רמולה",   "fish chermoula moroccan baked"),
    ("קציצות דגים",     "moroccan fish balls red sauce"),
    ("סרדינים",         "sardines stuffed chermoula moroccan"),
    ("חריימה",          "chraime spicy fish north african"),
    ("דג אפוי",         "moroccan baked fish vegetables"),
    ("גפילטע פיש",      "gefilte fish jewish poached"),
    # חגים
    ("עוף חגיגי",       "moroccan festive chicken fruit"),
    ("מאפה בשר",        "moroccan meat pastry briouats"),
    ("טאג׳ין חגיגי",    "moroccan festive lamb tagine prunes"),
    ("פסטייה",          "bastilla moroccan chicken pastry"),
    ("חרוסת",           "charoset moroccan passover"),
    ("מימונה",          "mimouna moroccan passover celebration"),
    # קינוחים
    ("מופלטה",          "mofletah moroccan semolina pancakes honey"),
    ("ספינג׳",          "sfenj moroccan donuts fried"),
    ("מקרוד",           "makroud moroccan date semolina cookies"),
    ("עוגיות שקדים",    "moroccan almond cookies"),
    ("שלדה",            "chebakia moroccan sesame honey cookies"),
    ("כעב הגזאל",       "gazelle horns almond pastry moroccan"),
    ("בריואט",          "briouat moroccan fried almond pastry"),
    ("תה נענע",         "moroccan mint tea glass pot"),
    ("עוגת תפוז",       "moroccan orange almond cake"),
    ("בקלווה",          "baklava honey walnut pastry"),
    ("חלוה",            "halva sesame moroccan"),
    # ספרדי
    ("סופריטו",         "sofrito spanish tomato sauce"),
    ("אלבונדיגס",       "albondigas spanish meatballs sauce"),
    ("גספאצ׳ו",         "gazpacho cold soup andalusian"),
    ("אמפנדה",          "empanada spanish baked meat pie"),
    ("פאייה",           "paella seafood saffron rice"),
    ("בורקס",           "borek phyllo cheese spinach"),
    ("קוקידו",          "cocido jewish spanish chickpea stew"),
    ("אדאפינה",         "adafina jewish spanish sabbath stew"),
    # עיראקי
    ("קובה בסלק",       "kibbeh beetroot soup iraqi jewish"),
    ("קובה חמוסטה",     "kibbeh hamusta lemon soup iraqi"),
    ("דולמה",           "dolma stuffed grape leaves vegetables"),
    ("מסגוף",           "masgouf grilled fish tigris iraqi"),
    ("תבית",            "tebeet iraqi stuffed chicken rice"),
    # כורדי
    ("שישבראק",         "shishbarak lamb dumplings yogurt"),
    ("כישקה",           "kishka stuffed intestine kurdish"),
    # אשכנזי
    ("חמין אשכנזי",     "cholent ashkenazi bean potato meat"),
    ("לאקשן קוגל",      "noodle kugel baked jewish"),
    ("קוגל",            "potato kugel jewish"),
    ("בינטש",           "potato latke pancake jewish"),
    ("קרפלך",           "kreplach meat dumplings soup"),
    # תימני
    ("ג׳חנון",          "jachnun yemeni pastry overnight"),
    ("לחוח",            "lahoh yemeni sponge flatbread"),
    ("זחוק",            "zhug yemeni green hot sauce"),
    ("הילבה",           "hilbeh yemeni fenugreek paste"),
    ("מרק עצמות תימני", "yemeni oxtail bone broth soup"),
    # פרסי
    ("גורמה סבזי",      "ghormeh sabzi persian herb stew"),
    ("קוקו סבזי",       "kuku sabzi persian herb frittata"),
    ("פסנג׳ן",          "fesenjan pomegranate walnut chicken"),
    ("ירקות ממולאים פרסיים","dolmeh persian stuffed vegetables"),
    # בוכארי
    ("אוש",             "plov osh uzbek rice lamb carrots"),
    ("פלוב",            "plov uzbek bukharian rice"),
    ("סמסה",            "samsa baked meat pastry uzbek"),
    ("מנטי",            "manti steamed dumplings uzbek"),
    ("נאן בוכארי",      "bukharian naan bread sesame"),
    # טוניסאי
    ("ברייק",           "brik tunisian egg pastry"),
    ("חריסה",           "harissa tunisian chili paste"),
    ("קוסקוס טוניסאי",  "tunisian couscous lamb spicy"),
    ("מחמורה",          "mahmoura tunisian almond cookies"),
    ("לבלבי",           "lablabi tunisian chickpea soup"),
    # טורקי
    ("בורקס טורקי",     "borek turkish cheese spinach filo"),
    ("אגריסטה",         "agristada turkish lemon chicken sauce"),
    # ישראלי
    ("פלאפל",           "falafel pita israeli street food"),
    ("שקשוקה",          "shakshuka eggs tomatoes peppers"),
    ("מג׳דרה",          "mujaddara lentil rice crispy onion"),
    ("סביח",            "sabich eggplant pita israeli"),
    ("בורקס",           "burekas cheese potato Israeli"),
]

CAT_QUERY = {
    "soups":  "moroccan soup bowl spiced",
    "salads": "moroccan mezze salads plate",
    "veg":    "moroccan vegetable stew tagine",
    "meat":   "moroccan lamb beef tagine clay",
    "chick":  "moroccan chicken tagine lemon olives",
    "fish":   "moroccan spiced fish dish",
    "hol":    "moroccan festive holiday food",
    "des":    "moroccan pastry sweets honey",
    "span":   "sephardic spanish jewish dish",
    "iraq":   "iraqi jewish food mezze",
    "kurd":   "kurdish jewish food dish",
    "ashk":   "ashkenazi jewish food deli",
    "yem":    "yemeni jewish food dish",
    "pers":   "persian iranian jewish food",
    "buk":    "uzbek bukharian rice plov",
    "tun":    "tunisian jewish north african food",
    "isr":    "israeli street food modern",
    "turk":   "turkish jewish sephardic food",
}

def build_query(recipe):
    """Title-first exact match, then partial, then category."""
    t = recipe["title"]
    cat = recipe["cat"]

    for kw, q in TITLE_QUERIES:
        if kw in t:
            return q

    # Partial ingredient match
    ingr_text = " ".join(recipe["ingr"])
    if "תפוח אדמה" in ingr_text or "תפ אד" in t:
        return "moroccan potato dish"
    if "שמן זית" in t or "זיתים" in t:
        return "moroccan olive oil dish"
    if "טחינה" in t:
        return "tahini sauce plate"

    return CAT_QUERY.get(cat, "moroccan jewish food dish")

# ══════════════════════════════════════════════════
# IMAGE SOURCES
# ══════════════════════════════════════════════════

def source_mealdb(query):
    """TheMealDB free API — real food photos, very fast."""
    # Try direct (no proxy) first — MealDB is often blocked by gov proxy
    _, sd = get_sess()
    words = query.split()[:2]
    meal_name = " ".join(words)
    try:
        from urllib.parse import quote_plus
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={quote_plus(meal_name)}"
        r = sd.get(url, timeout=NET_TIMEOUT, verify=False, headers=API_HDRS)
        if r.status_code == 200:
            meals = (r.json().get("meals") or [])
            if meals:
                thumb = meals[0].get("strMealThumb", "")
                if thumb:
                    return thumb
    except Exception:
        pass
    return None

def source_wikimedia_single(query):
    """Wikimedia Commons — ONE search call, ONE imageinfo call. Max 2 API calls total."""
    sp, sd = get_sess()
    from urllib.parse import quote_plus
    for sess in [sd, sp]:   # direct first (proxy may block Commons)
        try:
            # Single search call
            r = sess.get(
                "https://commons.wikimedia.org/w/api.php",
                params={
                    "action": "query", "list": "search",
                    "srsearch": f"{query} food",
                    "srnamespace": 6, "srlimit": 5, "format": "json",
                },
                timeout=NET_TIMEOUT, verify=False, headers=API_HDRS,
            )
            if r.status_code != 200:
                continue
            results = r.json().get("query", {}).get("search", [])

            # Pick best result — first .jpg that doesn't look like a diagram
            chosen = None
            for res in results:
                t = res.get("title", "")
                if not t.startswith("File:"): continue
                tl = t.lower()
                if not any(e in tl for e in [".jpg", ".jpeg", ".png"]): continue
                if any(b in tl for b in ["map","flag","logo","diagram","icon","symbol"]): continue
                chosen = t
                break

            if not chosen:
                continue

            # Single imageinfo call
            r2 = sess.get(
                "https://commons.wikimedia.org/w/api.php",
                params={
                    "action": "query", "titles": chosen,
                    "prop": "imageinfo", "iiprop": "url|size|mime",
                    "iiurlwidth": 400, "format": "json",
                },
                timeout=NET_TIMEOUT, verify=False, headers=API_HDRS,
            )
            if r2.status_code != 200:
                continue
            for pg in r2.json().get("query", {}).get("pages", {}).values():
                ii = pg.get("imageinfo", [{}])[0]
                url  = ii.get("thumburl") or ii.get("url", "")
                mime = ii.get("mime", "")
                sz   = ii.get("size", 0)
                if url and "image" in mime and 3000 < sz < 8_000_000:
                    return url
        except Exception:
            continue
    return None

def download_and_save(img_url, dest):
    """Download image and validate magic bytes. Returns True on success."""
    sp, sd = get_sess()
    for sess in [sd, sp]:
        try:
            r = sess.get(img_url, timeout=NET_TIMEOUT, stream=True,
                         allow_redirects=True)
            if r.status_code != 200:
                continue
            ct = r.headers.get("Content-Type", "")
            if "text" in ct or "html" in ct:
                continue
            data = b"".join(r.iter_content(8192))
            if len(data) < 3000:
                continue
            # Validate magic bytes: JPEG or PNG
            if data[:2] == b'\xff\xd8' or data[:4] == b'\x89PNG':
                dest.write_bytes(data)
                return True
            # Accept if Content-Type says image and size is reasonable
            if "image" in ct and len(data) > 10_000:
                dest.write_bytes(data)
                return True
        except Exception:
            continue
    return False

# ══════════════════════════════════════════════════
# MAIN — sequential, interruptible, logging per line
# ══════════════════════════════════════════════════
def main():
    global _STOP

    # Clear log file at start
    LOG_FILE.write_text("", encoding="utf-8")

    recipes = parse_recipes()
    total   = len(recipes)
    already = sum(1 for r in recipes
                  if (IMG_DIR / f"r-{r['id']}.jpg").exists())

    log("=" * 55)
    log(f"ספר הבישול של פרלה בן ארוש ז\"ל — הורדת תמונות")
    log("=" * 55)
    log(f"מתכונים: {total} | קיימים: {already} | OVERWRITE={OVERWRITE}")
    log(f"תיקייה: {IMG_DIR}")
    log(f"Socket timeout: {socket.getdefaulttimeout()}s | Net timeout: {NET_TIMEOUT}s")
    log(f"מקורות: TheMealDB → Wikimedia Commons")
    log(f"Ctrl+C יעצור בין מתכונים ויישמר הלוג")
    log("=" * 55)

    ok_count = skip_count = fail_count = mealdb_count = wiki_count = 0

    for i, recipe in enumerate(recipes):
        if _STOP:
            log("עצירה מבוקשת ע\"י משתמש.")
            break

        rid   = recipe["id"]
        title = recipe["title"]
        cat   = recipe["cat"]
        dest  = IMG_DIR / f"r-{rid}.jpg"

        # Skip existing
        if dest.exists() and not OVERWRITE:
            skip_count += 1
            if skip_count <= 5 or skip_count % 50 == 0:
                log(f"  ⏭ [{i+1:4d}/{total}] skip [{rid}]")
            continue

        query = build_query(recipe)
        log(f"  ▶ [{i+1:4d}/{total}] [{rid:8s}] {title[:28]:28s} → \"{query[:35]}\"")

        saved = False
        source = "?"

        # Source 1: TheMealDB (fast, food-specific)
        if not saved:
            url = source_mealdb(query)
            if url and download_and_save(url, dest):
                saved = True
                source = "mealdb"
                mealdb_count += 1

        # Source 2: Wikimedia Commons (2 API calls max)
        if not saved:
            url = source_wikimedia_single(query)
            if url and download_and_save(url, dest):
                saved = True
                source = "wiki"
                wiki_count += 1

        if saved:
            ok_count += 1
            log(f"  ✓ [{rid}] {source}")
        else:
            fail_count += 1
            log(f"  ✗ [{rid}] נכשל — אין תמונה זמינה")

        # Progress milestones
        done = i + 1
        pct  = done * 100 // total
        if pct % 10 == 0 and done > 0 and done < total:
            log(f"\n  ── {pct}% ({done}/{total})  "
                f"✓{ok_count}  ⏭{skip_count}  ✗{fail_count}  "
                f"[mealdb={mealdb_count} wiki={wiki_count}]\n")

        time.sleep(DELAY)

    log("=" * 55)
    log(f"סיום: ✓{ok_count}  ⏭{skip_count}  ✗{fail_count}")
    log(f"  TheMealDB: {mealdb_count}  Wikimedia: {wiki_count}")
    log(f"תיקייה: {IMG_DIR}")
    log(f"לוג: {LOG_FILE}")
    log("=" * 55)

if __name__ == "__main__":
    main()
