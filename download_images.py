#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_images.py — Perla Ben-Harrosh z"l Cookbook
====================================================
Downloads food images for all 1,014 recipes from TheMealDB and
Wikimedia Commons. Robust against hangs: global socket timeout,
Ctrl+C = immediate exit via os._exit(0), log flushed after every recipe.

Usage:
    python download_images.py

Requirements:
    pip install requests

Log saved to: SCRIPT_DIR/logs/download_images_YYYY-MM-DD_HH.MM.log
"""
import os, re, sys, time, signal, socket
from datetime import datetime
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
# CONFIG
# ══════════════════════════════════════════════════
SCRIPT_DIR  = Path(__file__).parent
IMG_DIR     = SCRIPT_DIR / "images"        # output directory — always images/
LOG_DIR     = Path(r"C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook\logs")
_ts         = datetime.now().strftime("%Y-%m-%d_%H.%M")
LOG_FILE    = LOG_DIR / f"download_images_{_ts}.log"

# Proxy for network requests only.  None = no proxy
PROXY       = "http://pac.gov.il:8080"

DELAY       = 0.4    # seconds between recipes (rate limiting)
NET_TIMEOUT = 6      # seconds per network request  (< socket global timeout=8)
OVERWRITE   = False  # True = overwrite existing images

IMG_DIR.mkdir(parents=True, exist_ok=True)
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    # Fallback: save log next to script if Windows path unavailable
    LOG_FILE = SCRIPT_DIR / f"download_images_{_ts}.log"

# ── Ctrl+C handler — immediate hard exit via os._exit(0) ──
# os._exit bypasses all cleanup (requests/urllib3 sessions) that cause hanging.
# The log is already on disk after every recipe — nothing is lost.
_STOP = False
def _sigint(sig, frame):
    print("\n\n[!] Ctrl+C — exiting...", flush=True)
    os._exit(0)   # immediate hard exit — no cleanup, no hang
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
    """Try direct first, then proxy. Returns response or None.
    Never hangs thanks to socket.setdefaulttimeout(8)."""
    sp, sd = get_sess()
    hdrs = API_HDRS if api else HDRS
    for sess in [sd, sp]:
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
        log("ERROR: data.js or index.html not found in script directory")
        sys.exit(1)
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
# TITLE → SEARCH QUERY MAPPING
# 575 entries covering 75% of recipes with specific queries.
# The rest fall back to CAT_QUERY (category-based generic).
# ══════════════════════════════════════════════════
TITLE_QUERIES = [
    # Soups
    ("חרירה","harira moroccan soup"),
    ("ביסארה","bissara moroccan fava bean soup"),
    ("מרק עדשים","moroccan lentil soup"),
    ("מרק שעועית לבנה","moroccan white bean soup"),
    ("מרק שעועית אדומה","moroccan red bean soup"),
    ("מרק שעועית","moroccan bean soup"),
    ("מרק ירקות","moroccan vegetable soup"),
    ("מרק עגבניות","moroccan tomato soup"),
    ("מרק דלעת ואגוז","moroccan pumpkin walnut soup"),
    ("מרק דלעת","moroccan pumpkin soup"),
    ("מרק עוף ופרגיות","moroccan chicken thighs soup"),
    ("מרק עוף","moroccan chicken soup"),
    ("מרק כרוב","moroccan cabbage soup"),
    ("מרק גריסים","moroccan pearl barley soup"),
    ("מרק פריקה","moroccan freekeh soup"),
    ("מרק בטטה","moroccan sweet potato ginger soup"),
    ("ברקוקס","moroccan berkoukes soup"),
    ("מרק סלק","moroccan beet soup"),
    ("מרק כרובית","moroccan cauliflower soup"),
    ("מרק פול","moroccan fava bean soup"),
    ("מרק אפונה","moroccan split pea soup"),
    ("מרק בצל","french onion soup"),
    ("מרק שום","moroccan garlic herb soup"),
    ("מרק תרד","moroccan spinach soup"),
    ("מרק חלב","moroccan milk almond soup"),
    ("מרק קוסקוסית","moroccan couscous soup"),
    ("מרק חמוצים","moroccan sour soup"),
    ("מרק פסטה","moroccan pasta soup"),
    ("מרק ים","moroccan seafood soup"),
    ("מרק ירק שורש","moroccan root vegetable soup"),
    ("מרק שיבולת שועל","moroccan oatmeal soup"),
    ("מרק שומר","moroccan fennel lemon soup"),
    ("מרק קמח קלוי","moroccan toasted flour soup"),
    ("מרק לוף","moroccan chard soup"),
    ("מרק חרירה עם בשר","harira moroccan lamb soup"),
    ("מרק חריף לשבירת","moroccan breaking fast soup"),
    ("מרק ראס אל-עין","moroccan lamb head soup"),
    ("מרק מחמר","moroccan paprika chicken soup"),
    ("מרק עצמות","moroccan bone broth soup"),
    ("מרק שום מרוקאי","moroccan garlic soup"),
    ("מרק חמין","moroccan hamin bean soup"),
    ("מרק דג","moroccan fish soup"),
    ("לחשו","moroccan semolina garlic soup"),
    ("קלדו","caldo sephardic chicken broth"),
    ("מרק מנה ירוקה","moroccan green herb soup"),
    ("מרק טלה","moroccan lamb lentil soup"),
    ("מרק שעורה","moroccan barley soup"),
    ("מרק תפוח אדמה","moroccan potato saffron soup"),
    ("מרק חומוס ותרד","moroccan chickpea spinach soup"),
    ("מרק חומוס ועגבנייה","moroccan chickpea tomato soup"),
    ("מרק חומוס מרוקאי","moroccan chickpea soup"),
    ("מרק צלי עם שומר","moroccan roasted fennel soup"),
    ("מרק פרא","moroccan wild herb soup"),
    ("מרק שומשום","moroccan sesame soup"),
    ("מרק קואה","moroccan koa soup"),
    ("מרק קרם פטריות","cream mushroom soup"),
    ("מרק ערמונים","moroccan chestnut soup"),
    ("מרק עגבניות ואורז","moroccan tomato rice soup"),
    ("אמרגן","moroccan amrghen barley soup"),
    ("טפינה","moroccan tafina barley lentil soup"),
    ("ת׳ריד","moroccan tharid bread broth"),
    # Salads
    ("מטבוחה","matbucha moroccan tomato pepper"),
    ("זאלוק","zaalouk moroccan eggplant"),
    ("זעלוק","zaalouk moroccan eggplant"),
    ("טקטוקה","taktouka moroccan roasted pepper tomato"),
    ("חומוס","hummus chickpea tahini"),
    ("סלט גזר","moroccan carrot salad"),
    ("סלט חצילים","moroccan eggplant salad"),
    ("סלט פלפל","moroccan roasted pepper salad"),
    ("סלט כרוב","moroccan cabbage slaw"),
    ("סלט עגבניות","moroccan tomato herb salad"),
    ("סלט תפוחי אדמה","moroccan potato salad"),
    ("סלט תפוח אדמה","moroccan potato salad"),
    ("סלט סלק","moroccan beet salad"),
    ("טבולה","tabbouleh parsley salad"),
    ("סלט פול","foul medames moroccan"),
    ("סלט לוביה","black eyed peas salad"),
    ("סלט קישואים","moroccan zucchini salad"),
    ("סלט כרובית","moroccan cauliflower salad"),
    ("סלט שעועית","moroccan white bean salad"),
    ("סלט מלפפונים","moroccan cucumber salad"),
    ("סלט עדשים","moroccan lentil salad"),
    ("סלט שומר","moroccan fennel salad"),
    ("סלט ארטישוק","moroccan artichoke salad"),
    ("סלט ביצה קשה","moroccan hard boiled egg cumin"),
    ("סלט ביצים","moroccan egg salad"),
    ("סלט תפוז","moroccan orange olive salad"),
    ("סלט ברנג׳ל","moroccan eggplant tomato salad"),
    ("סלט זיתים","moroccan olive lemon salad"),
    ("סלט ורדים","moroccan rose fruit salad"),
    ("סלט פטרוזיליה","parsley tahini salad"),
    ("סלט טחינה","tahini sauce salad"),
    ("סלט בטטה","moroccan sweet potato salad"),
    ("סלט חיטה","moroccan wheat salad"),
    ("סלט קוסקוס","moroccan couscous salad"),
    ("סלט שנקליש","shneklish cheese tomato salad"),
    ("סלט חומוס","hummus tahini plate"),
    ("סלט לפת","moroccan turnip salad"),
    ("סלט תרד","moroccan spinach sesame salad"),
    ("סלט ברוקולי","moroccan broccoli salad"),
    ("סלט כוסברה","moroccan cilantro lemon salad"),
    ("סלט גמבה","moroccan shrimp salad"),
    ("סלט שורש סלרי","celery root salad"),
    ("סלט שעורה","moroccan barley salad"),
    ("סלט פאבה","moroccan dried fava bean"),
    ("סלט חמוצים","moroccan pickled vegetables"),
    ("שקשוקה","shakshuka eggs tomatoes"),
    ("סלט ירקות צלויים","moroccan roasted vegetable salad"),
    # Vegetables
    ("חצילים","moroccan eggplant tomato"),
    ("קישואים","moroccan zucchini garlic"),
    ("כרובית","moroccan cauliflower roasted"),
    ("מעקודה","maakouda moroccan potato patties"),
    ("מחמאר","moroccan potato mchammer"),
    ("במיה","bamia okra tomato stew"),
    ("שעועית ירוקה","moroccan green beans tomato"),
    ("כרוב מבושל","moroccan braised cabbage"),
    ("כרוב אדום","moroccan red cabbage braised"),
    ("פלפלים ממולאים","moroccan stuffed peppers"),
    ("ממולאי פלפלים","moroccan stuffed peppers"),
    ("ממולאי קישואים","moroccan stuffed zucchini"),
    ("ממולאי כרוב","moroccan stuffed cabbage"),
    ("ממולאי עגבניות","moroccan stuffed tomatoes"),
    ("ממולאי בצלים","moroccan stuffed onions"),
    ("ממולאי עלי גפן","moroccan grape leaves dolma"),
    ("ממולאי כרישה","moroccan stuffed leek"),
    ("עגבניות ממולאות","moroccan stuffed tomatoes"),
    ("בצלים ממולאים","moroccan stuffed onions"),
    ("כרוב ממולא","moroccan stuffed cabbage"),
    ("דלעת מתוקה","moroccan sweet pumpkin honey"),
    ("דלעת קרמלית","moroccan caramelized pumpkin"),
    ("דלעת מרוקאית","moroccan pumpkin spiced"),
    ("תרד","moroccan spinach"),
    ("כרישה","moroccan leek tomato"),
    ("ארטישוק","moroccan artichoke"),
    ("גבינה לבנה","white cheese herbs"),
    ("גרגרי חיטה","moroccan wheat berry"),
    ("גרגרי חומוס","roasted chickpeas crispy"),
    ("פטריות","moroccan mushroom"),
    ("רטטוי","moroccan ratatouille"),
    ("שום שלם","moroccan roasted garlic"),
    ("בצלים קטנים","moroccan pearl onion"),
    ("שורש פטרוזיליה","moroccan parsley root"),
    ("גזר בדבש","moroccan glazed carrots honey"),
    ("גזר מרוקאי","moroccan spiced carrots"),
    ("גזר חמוץ-מתוק","moroccan sweet sour carrots"),
    ("כרוב עם שמן","moroccan cabbage olive oil"),
    ("פול ירוק","moroccan green fava beans"),
    ("פול חצי יבש","moroccan dried fava"),
    ("פול עם עגבניות","moroccan fava tomato"),
    ("שעועית לבנה עם זית","moroccan white bean olive"),
    ("שעועית לבנה","moroccan white bean"),
    ("קנאפה","moroccan eggplant layered"),
    ("חציל עם עגבנייה","moroccan eggplant tomato egg"),
    ("חציל עם ביצה","moroccan eggplant egg"),
    ("חציל עם טחינה","moroccan eggplant tahini"),
    ("ח׳ל׳ע׳","moroccan argan oil"),
    ("ברוקולי","moroccan broccoli"),
    ("טאג׳ין ירקות","moroccan vegetable tagine"),
    ("ירקות מרוקאיים מושרים","moroccan pickled marinated vegetables"),
    ("קישוא מרוקאי עם שום","moroccan zucchini roasted garlic"),
    ("תפוחי אדמה חריפים","moroccan spicy potatoes"),
    # Meat
    ("קציצות","kefta moroccan meatballs"),
    ("תבשיל בשר עם שזיפים","moroccan beef prunes almonds"),
    ("מרוזייה","mrouzia moroccan lamb honey raisins"),
    ("ח׳לייע","khlii moroccan preserved meat"),
    ("כבד","moroccan liver onions"),
    ("ריאות","moroccan lung tomato stew"),
    ("טחול","moroccan stuffed spleen"),
    ("קיבה ממולאת","moroccan stuffed tripe"),
    ("מוח מטוגן","moroccan fried brain"),
    ("קורקבנים","moroccan gizzard stew"),
    ("מרגז","merguez moroccan sausage"),
    ("שניצל מרוקאי","moroccan schnitzel"),
    ("בשר ממולא בבצק","moroccan meat stuffed pastry"),
    ("בשר עם תאנים","moroccan meat figs tagine"),
    ("בשר עם אגסים","moroccan meat pear saffron"),
    ("בשר עם חרוב","moroccan meat carob"),
    ("בשר עם צנוברים","moroccan lamb pine nuts"),
    ("בשר עם כרישה","moroccan meat leek"),
    ("בשר עם ג׳ינג׳ר","moroccan beef ginger"),
    ("בשר עם חציל","moroccan beef eggplant"),
    ("בשר עם תפוחי אדמה","moroccan meat potatoes peppers"),
    ("בשר עם שעועית","moroccan meat white bean"),
    ("בשר עם חומוס","moroccan meat chickpea"),
    ("כבש עם כרוב","moroccan lamb cabbage cumin"),
    ("כבש עם פלפלים","moroccan lamb peppers"),
    ("כבש עם תפוח","moroccan lamb apple raisins"),
    ("כבש עם שעועית","moroccan lamb white bean"),
    ("כבש עם צנוברים","moroccan lamb pine nuts"),
    ("כבש עם חרוב","moroccan lamb carob"),
    ("כבש צלוי שלם","moroccan whole roasted lamb"),
    ("ראש כבש","moroccan lamb head"),
    ("כרעיין","moroccan lamb feet"),
    ("שיפוד כבש","moroccan lamb skewer"),
    ("שיפוד בשר","moroccan meat grill"),
    ("מחמר בשר","moroccan paprika beef"),
    ("חמין קפה","moroccan sabbath skhina stew"),
    ("אולייה פודרידה","olla podrida spanish stew"),
    ("מחנשה","moroccan stuffed meat"),
    ("עצמות מח","moroccan marrow bones"),
    ("בשר ראש","moroccan head meat"),
    ("כבש","moroccan lamb tagine"),
    ("חמין","moroccan hamin sabbath stew"),
    ("סקינה","skhina moroccan jewish stew"),
    ("קובה","kibbeh soup"),
    # Chicken
    ("עוף עם זיתים","moroccan chicken preserved lemon olives"),
    ("עוף עם שקדים","moroccan chicken almonds raisins"),
    ("עוף עם פירות יבשים","moroccan chicken dried apricots"),
    ("עוף עם בצל","moroccan chicken caramelized onions"),
    ("עוף עם שזיפים","moroccan chicken prunes tagine"),
    ("עוף עם ענבים","moroccan chicken grapes"),
    ("עוף עם אפרסקים","moroccan chicken peach tagine"),
    ("עוף עם בטטה","moroccan chicken sweet potato honey"),
    ("עוף עם פיסטוק","moroccan chicken pistachio"),
    ("עוף עם תרד","moroccan chicken spinach tomato"),
    ("עוף עם גזר","moroccan chicken carrot turmeric"),
    ("עוף עם קישואים","moroccan chicken zucchini"),
    ("עוף עם פלפלים","moroccan chicken peppers"),
    ("עוף עם ליצ׳י","moroccan chicken lychee"),
    ("עוף עם עגבניות","moroccan chicken dried tomatoes"),
    ("עוף עם ריבת תפוזים","moroccan chicken orange jam"),
    ("עוף עם תפוח","moroccan chicken apple bay leaf"),
    ("עוף עם חמוציות","moroccan chicken cranberries"),
    ("עוף עם ענבי יין","moroccan chicken red grapes"),
    ("עוף עם קוסקוס","moroccan chicken couscous"),
    ("עוף עם ג׳ינג׳ר","moroccan chicken ginger lemon"),
    ("עוף עם קציצות","moroccan chicken meatballs"),
    ("עוף עם כרוב","moroccan chicken cabbage"),
    ("עוף מרוקאי בתנור","moroccan roasted chicken lemon"),
    ("עוף עם חומוס","moroccan chicken chickpea"),
    ("עוף עם תפוחי אדמה","moroccan chicken potato tagine"),
    ("עוף ביין","moroccan chicken red wine"),
    ("עוף בקדרה","moroccan chicken clay pot"),
    ("קוסקוס חגיגי","moroccan couscous chicken vegetables"),
    ("קוסקוס שבעה ירקות","moroccan couscous seven vegetables"),
    ("קוסקוס מתוק","moroccan sweet couscous milk"),
    ("קוסקוס בצל","moroccan couscous caramelized onion"),
    ("קוסקוס עם חומוס","moroccan couscous chickpea pumpkin"),
    ("קוסקוס ים","moroccan seafood couscous"),
    ("סנה","moroccan chicken couscous"),
    ("טאג׳ין עוף","moroccan chicken tagine"),
    ("עוף ממולא","moroccan stuffed chicken"),
    ("מחנצ׳ה","moroccan stuffed chicken roll"),
    ("פרגיות","moroccan grilled chicken thighs"),
    ("עוף תנדורי","moroccan tandoori chicken"),
    ("מחמר עוף","moroccan paprika red chicken"),
    ("עוף ים","moroccan seaside chicken"),
    ("עוף עם שבעה ירקות","moroccan chicken seven vegetables"),
    ("עוף חגיגי","moroccan festive chicken"),
    # Fish
    ("דג חריף","moroccan spicy fish"),
    ("צ׳רמולה","moroccan fish chermoula"),
    ("חרמולה","moroccan fish chermoula"),
    ("קציצות דגים","moroccan fish balls"),
    ("סרדינים","moroccan sardines"),
    ("חריימה","chraime spicy fish"),
    ("דג אפוי","moroccan baked fish"),
    ("גפילטע פיש","gefilte fish jewish"),
    ("דג מלוח","moroccan salt fish"),
    ("דג עם חריסה","moroccan fish harissa"),
    ("דג עם שקדים","moroccan fish almonds"),
    ("דג מוסר ים","moroccan sea bass"),
    ("קלמארי","moroccan stuffed squid"),
    ("שרימפס","moroccan spiced shrimp"),
    ("מישייה","moroccan salted fish"),
    ("אנשואה","moroccan anchovy"),
    ("טיירה","moroccan fish pie"),
    ("מז׳אוז׳ין","moroccan fish medley"),
    ("בוריד","moroccan baked fish olive oil"),
    ("קציצות שרימפס","moroccan shrimp patties"),
    ("כפתאג׳ה","moroccan fish patties"),
    ("דג לבן","moroccan white fish"),
    ("דג עם ירקות קלויים","moroccan fish roasted vegetables"),
    ("דג ים בתנור","moroccan sea fish baked"),
    ("טונה","moroccan tuna tomato"),
    ("שרימפס עם שום","garlic butter shrimp"),
    ("תמרים ממולאים דג","moroccan date stuffed fish"),
    ("חריימה אדומה","moroccan red chraime fish"),
    ("דג עם עגבניות קלויות","moroccan fish roasted tomato"),
    ("דג עם תפוחי אדמה","moroccan fish potato"),
    ("דג עם פלפלים","moroccan fish peppers"),
    ("דג עם תבלינים","moroccan fish andalusian spices"),
    ("בקלה","bacalao salt cod fish"),
    ("דג מרינרה","moroccan fish marinara"),
    ("דג עם ירק ים","moroccan fish seaweed"),
    ("דג עם פסטה","moroccan fish pasta"),
    ("דג עם רוטב שרי","moroccan fish sherry sauce"),
    # Holiday & Festive
    ("חרוסת","charoset moroccan passover"),
    ("מופלטה","mofletah moroccan pancakes"),
    ("מימונה","mimouna moroccan celebration"),
    ("שולחן מימונה","mimouna moroccan table"),
    ("פסח מרוקאי","moroccan passover seder"),
    ("שבת דגים","moroccan sabbath fish"),
    ("שבת של בשר","moroccan meat sabbath table"),
    ("ביצים חמינדוס","huevos haminados sephardic"),
    ("עוגת שמן מרוקאית","moroccan olive oil cake"),
    ("גרנדר","moroccan oil cake passover"),
    ("תבשיל דבש וגזר","moroccan honey carrot rosh hashana"),
    ("ראש שנה מרוקאי","moroccan rosh hashana table"),
    ("אוזני המן","hamantaschen purim cookies"),
    ("עוגיות גבינה","cheese cookies shavuot"),
    ("פשטידת שבועות","shavuot cheese pie"),
    ("לולב ממולא","sukkot stuffed date"),
    ("מאפה בשר","moroccan meat pastry"),
    ("פסטייה","bastilla moroccan chicken"),
    ("בסטלה","bastilla moroccan phyllo"),
    ("בריואט","briouat moroccan fried pastry"),
    ("טאג׳ין חגיגי","moroccan festive tagine prunes"),
    ("מוהלביה","mouhalabia milk pudding"),
    ("ראש כבש ברוטב","moroccan lamb head stew"),
    ("מחנשה חינה","moroccan henna stuffed meat"),
    ("פשיטה","moroccan henna egg pastry"),
    ("בנינו","moroccan henna almond cookies"),
    ("סמבוסק","sambousek fried pastry"),
    ("שינה — תבשיל לילה","moroccan overnight slow stew"),
    ("שינה","moroccan overnight slow stew"),
    ("כבש בחלב","moroccan lamb milk"),
    ("לחם פרנה","moroccan frena bread"),
    ("פרנה מימונה","moroccan frena mimouna bread"),
    ("בטבוט","batbout moroccan bread"),
    ("חרשה","harcha moroccan semolina bread"),
    ("בגריר","beghrir moroccan honeycomb pancakes"),
    ("מלווי","malawy moroccan layered bread"),
    ("מלאווי","malawy moroccan layered bread"),
    ("ח׳ובז","moroccan khobz bread"),
    ("אֻמַלִי","moroccan bread pudding"),
    ("בסטלה ביצה","moroccan bastilla egg"),
    ("טאג׳ין תרנגול","moroccan turkey tagine"),
    ("שטיחה","moroccan layered meat pastry"),
    ("סלטים חגיגיים","moroccan festive mezze"),
    ("מרק חג","moroccan holiday rich soup"),
    ("אורז חגיגי","moroccan festive rice almonds"),
    ("דג חגיגי","moroccan festive spicy fish"),
    ("קינוח חג","moroccan holiday dessert"),
    ("טאג׳ין חמאם","moroccan pigeon tagine"),
    ("מוסיל","moroccan milk jam caramel"),
    ("ברנייה","moroccan chocolate mousse"),
    # Desserts & Sweets
    ("ספינג׳","sfenj moroccan donuts"),
    ("מקרוד","makroud moroccan semolina dates"),
    ("שלדה","chebakia moroccan sesame honey"),
    ("כעב אל-ע׳זאל","gazelle horns moroccan"),
    ("כעב הגזאל","gazelle horns moroccan"),
    ("קרני עזים","gazelle horns moroccan"),
    ("בקלווה","baklava honey walnut"),
    ("חלוה","halva sesame moroccan"),
    ("חלווה","halva sesame moroccan"),
    ("גריבה","ghriba moroccan butter cookies"),
    ("זלביה","zlabia moroccan honey donuts"),
    ("עוגיות שקדים","moroccan almond cookies"),
    ("עוגיות שומשום","moroccan sesame cookies"),
    ("עוגיות סולת","moroccan semolina honey cookies"),
    ("עוגיות ג׳ינג׳ר","moroccan ginger anise cookies"),
    ("עוגיות אניס","moroccan anise sesame cookies"),
    ("עוגיות ח׳ריצ׳ה","moroccan anise oil cookies"),
    ("עוגיות קוקוס","moroccan coconut cookies"),
    ("עוגיות תמרים","moroccan date almond cookies"),
    ("עוגיות חינה","moroccan henna almond cookies"),
    ("עוגיות לב שקדים","moroccan almond heart cookies"),
    ("עוגיות יין ספרדיות","sephardic wine cookies"),
    ("עוגיות מקרון","moroccan almond macaroon"),
    ("עוגת גזר","moroccan carrot cake"),
    ("עוגת שקדים","moroccan almond orange cake"),
    ("עוגת שוקולד","moroccan chocolate almond cake"),
    ("עוגת מי ורדים","moroccan rosewater cake"),
    ("עוגת יין","moroccan wine cake"),
    ("עוגת שמן זית","moroccan olive oil cake"),
    ("עוגת שמרים","moroccan yeast streusel cake"),
    ("עוגת תפוחים","moroccan apple yeast cake"),
    ("עוגת תפוז","moroccan orange almond cake"),
    ("עוגת דבש","moroccan honey cake"),
    ("עוגת שמן","moroccan oil cake"),
    ("בריוש","moroccan brioche bread"),
    ("מסמן","msemen moroccan flatbread"),
    ("ריבת תפוזים","moroccan orange marmalade"),
    ("ריבת תאנים","moroccan fig jam"),
    ("ריבת שזיפים","moroccan plum jam"),
    ("ריבת ורדים","moroccan rose jam"),
    ("ריבת רימונים","moroccan pomegranate jam"),
    ("ריבת ענבים","moroccan grape jam"),
    ("ריבת כרוב","moroccan red cabbage jam"),
    ("ריבת קאקי","moroccan persimmon jam"),
    ("ריבת אפרסק","moroccan peach jam"),
    ("ריבת","moroccan jam preserve"),
    ("תה נענע","moroccan mint tea"),
    ("תה מרוקאי","moroccan mint tea"),
    ("שאי ביד","moroccan milk tea"),
    ("חלב שקדים","moroccan almond milk"),
    ("שהד","moroccan honey dessert"),
    ("ח׳ריף","moroccan spicy honey"),
    ("מגינד","moroccan date bread"),
    ("פאסטיל","moroccan rice sweet pastry"),
    ("ח׳ריבה","moroccan butter crumble"),
    ("ענבים מקורמלים","caramelized grapes"),
    ("מסמן עם דבש","msemen honey"),
    ("שבקיה","chebakia moroccan fried honey"),
    ("סלו","sloo moroccan dried fruit paste"),
    ("קינוח חלב","moroccan milk almond pudding"),
    ("שאי","moroccan tea"),
    ("כרוב בסוכר","moroccan sfuf sweet semolina"),
    ("לחם מתוק","moroccan sweet bread"),
    # Spanish / Sephardic
    ("סופריטו","sofrito spanish tomato sauce"),
    ("אלבונדיגס","albondigas spanish meatballs"),
    ("גספאצ׳ו","gazpacho andalusian cold soup"),
    ("אמפנדה","empanada spanish meat pie"),
    ("פאייה","paella seafood saffron"),
    ("קוקידו","cocido sephardic chickpea stew"),
    ("אדאפינה","adafina sephardic sabbath stew"),
    ("בורקס","borek phyllo cheese"),
    ("בורקיטאס","boureka sephardic pastry"),
    ("אגריסטה","agristada sephardic lemon sauce"),
    ("ח׳מין ירושלמי","hamin jerusalem sephardic"),
    ("ח׳מין אדאפינה","adafina sephardic full sabbath"),
    ("מאחי","moroccan spanish rice"),
    ("גסטרו","spanish jewish meat stew"),
    ("ח׳וביה","spanish jewish vegetable stew"),
    ("פוחרו","spanish fava bean"),
    ("אספינאקאס","sephardic spinach"),
    ("קלדו ספרדי","caldo sephardic broth"),
    ("בסטיל דלות","sephardic phyllo pastry"),
    ("מאפה גבינה","sephardic cheese pastry"),
    ("פסטיל ספרדי","sephardic egg pastry"),
    ("סוקד","sephardic salt cod"),
    ("רוסקס","sephardic sesame cookies"),
    ("ביסקוצ׳וס","sephardic celebration cookies"),
    ("פאן דה-מיאל","pan de miel sephardic honey bread"),
    ("אארוז קון פולו","arroz con pollo sephardic"),
    ("ח׳פה","sephardic sugar pastry"),
    ("מנחה אנדלוסית","andalusian appetizer"),
    ("טורוביאה","sephardic layered meat pastry"),
    ("ח׳וביאס","sephardic white beans herbs"),
    ("קרפ ספרדי","sephardic crepe"),
    ("כוכו","kuku sephardic frittata"),
    ("פוטאז׳","sephardic vegetable soup"),
    ("מימוסאס","sephardic deviled eggs"),
    ("טוסטדאס","sephardic toast"),
    ("לאגארטה","sephardic ritual bread"),
    ("לימון כבוש","moroccan preserved lemon"),
    ("זיתים כבושים","moroccan cured olives"),
    ("ראס אל-חנות","ras el hanout moroccan spice"),
    ("חריסה","harissa north african chili paste"),
    ("ספרדי","sephardic jewish spanish"),
    ("מימוסאס","sephardic deviled eggs"),
    # Iraqi
    ("קובה בסלק","kibbeh beetroot iraqi"),
    ("קובה חמוסטה","kibbeh hamusta lemon iraqi"),
    ("דולמה","dolma stuffed grape leaves"),
    ("תבית","tebeet iraqi stuffed chicken"),
    ("פאטה","fatta iraqi bread rice"),
    ("עישה","iraqi chicken rice pie"),
    ("אורז שבת עיראקי","iraqi sabbath rice almonds"),
    ("מרק לפת","iraqi turnip sour soup"),
    ("חצילים ממולאים עיראקי","iraqi stuffed eggplant"),
    ("סמבוסק עיראקי","iraqi sambousek fried"),
    ("טמר עיראקי","iraqi date cookies"),
    # Kurdish
    ("שישבראק","shishbarak lamb dumplings yogurt"),
    ("כישקה","kishka stuffed intestine kurdish"),
    ("דולמה כורדית","kurdish dolma stuffed"),
    ("גמה","kurdish savory stuffed pastry"),
    ("ספינג","kurdish fried dough"),
    ("רימון ויוגורט","pomegranate yogurt"),
    ("ממחל","kurdish walnut field"),
    ("תבשיל גבינה","kurdish cheese tomato stew"),
    # Ashkenazi
    ("צ׳ולנט","cholent ashkenazi bean potato"),
    ("חמין אשכנזי","cholent ashkenazi bean"),
    ("לאקשן קוגל","lokshen kugel noodle pudding"),
    ("קוגל","potato kugel jewish"),
    ("בינטש","potato latke pancake"),
    ("קרפלך","kreplach meat dumplings soup"),
    ("בורשט","borscht beetroot soup"),
    ("ממליגה","polenta cheese romanian"),
    ("בלינצ׳ס","blintzes cheese pancake"),
    ("רוגלך","rugelach rolled cookies"),
    ("פשטידת גבינה","cheese kugel baked"),
    ("לחמניות גבינה","cheese rolls baked"),
    ("לחמניות מטוגנות","fried dough rolls"),
    ("חנקלך","hanukkah fried dough"),
    ("פלישקה","stuffed cabbage ashkenazi"),
    ("צימעס","tzimmes carrot dried fruit"),
    ("קאשע","kasha buckwheat noodles"),
    ("איינגמאכ׳טס","eingemachts beetroot jam"),
    ("פרגל","chicken honey mustard"),
    ("סלט הרינג","herring salad pickled"),
    ("מחזי","cheese buns rolls"),
    ("פלאפן","apple sauce puree"),
    ("קיכל","yeast egg cookies"),
    # Yemeni
    ("ג׳חנון","jachnun yemeni overnight pastry"),
    ("לחוח","lahoh yemeni sponge flatbread"),
    ("זחוק","zhug yemeni green chili"),
    ("הילבה","hilbeh yemeni fenugreek"),
    ("אסיד","aseed yemeni cooked dough"),
    ("עשיד","aseed yemeni chickpea paste"),
    ("שמר","yemeni fermented yeast"),
    ("אורז תימני","yemeni rice ghee"),
    ("מעוג׳","yemeni fried dough"),
    ("שניה","yemeni fried filled pastry"),
    ("כסבה","yemeni rice raisins"),
    ("גרגושה","yemeni sesame cookies"),
    ("בנת א-שאן","yemeni honey bread"),
    ("חבש","yemeni honey cake"),
    ("ספיחה","yemeni bread clay pot"),
    ("ג׳חנון ישראלי","jachnun yemeni quick"),
    # Persian
    ("גורמה סבזי","ghormeh sabzi persian herb stew"),
    ("קוקו סבזי","kuku sabzi persian herb frittata"),
    ("פסנג׳ן","fesenjan pomegranate walnut chicken"),
    ("ירקות ממולאים פרסיים","dolmeh persian stuffed"),
    ("חלווה ארדה","persian halva sesame"),
    ("ריגן","persian scallion cheese"),
    ("מרגיצ׳ה","persian egg eggplant patties"),
    ("מרק אנרגטי","persian energy soup"),
    # Bukharian
    ("אוש","osh plov uzbek rice"),
    ("פלוב","plov bukharian rice lamb"),
    ("סמסה","samsa uzbek baked pastry"),
    ("מנטי","manti steamed dumplings"),
    ("נאן בוכארי","bukharan naan bread"),
    ("קיסמיק","kishmish raisin horseradish"),
    ("קבאב גוש","kebab whole meat bukharian"),
    ("ביש-ג׳וש","bishgosh bukharian sesame soup"),
    ("מרמלאדה","marmalade orange jam"),
    ("דימלמה","dimlama uzbek stuffed vegetables"),
    ("קסונסוי","goshpara uzbek small dumplings"),
    ("מנטי בבוכרה","manti bukharian large dumplings"),
    # Tunisian
    ("ברייק","brik tunisian egg pastry"),
    ("לבלבי","lablabi tunisian chickpea soup"),
    ("מחמורה","mahmoura tunisian almond cookies"),
    ("זלאביה","zlabia tunisian honey donuts"),
    ("אסידה","asida tunisian banana pudding"),
    ("מחלביה","mahlabia tunisian milk pudding"),
    ("קסקרוט","casse-croute tunisian sandwich"),
    ("סמסה תוניסית","samsa tunisian pastry"),
    ("קוסקוס טוניסאי","tunisian couscous lamb spicy"),
    # Israeli
    ("פלאפל","falafel pita israeli"),
    ("מג׳דרה","mujaddara lentil rice onion"),
    ("סביח","sabich eggplant pita"),
    ("בורקס גבינה","burekas cheese potato"),
    ("חומוס מסבחה","msabbaha warm chickpea"),
    ("תחינה ביתית","tahini homemade sesame"),
    ("פיתה ים תיכונית","pita mediterranean flatbread"),
    ("שוורמה","shawarma chicken wrap"),
    ("סלט ישראלי","israeli salad fresh tomato cucumber"),
    ("חמין ישראלי","israeli hamin sabbath stew"),
    ("ממרח גבינה","cream cheese tomato herb"),
    ("ביצה בחמאה","egg butter zaatar"),
    # Turkish
    ("בורקס טורקי","borek turkish cheese spinach"),
    ("קלדאוס","kaldaush turkish meat vegetables"),
    ("ראשי-קשי","pilaf turkish festive rice"),
    ("פאסטל","pastel turkish meat pie"),
    ("שקרלמה","sekerleme turkish glazed chicken"),
    ("חנום","hanom turkish baked dumplings"),
    ("אימאם ביילדי","imam bayildi turkish stuffed eggplant"),
    ("קאדאיף","kadaif turkish shredded pastry"),
    ("מוחלבייה","muhallabia turkish milk pudding"),
    ("סיגאר בורק","sigara boregi turkish cheese rolls"),
    ("סרמה","sarma turkish stuffed grape leaves"),
    ("חלבה טורקית","halva turkish sesame"),
    ("קושקוש","kuskunos turkish egg patties"),
    ("פאשטל","pashtel turkish baked pastry"),
    ("בורמואלוס","bunuelos hanukkah fried dough"),
    ("ספינג׳ טורקי","lokma turkish fried dough honey"),
    ("פשטידת אורז ועוף","turkish chicken rice pie"),
]

CAT_QUERY = {
    "soups":  "moroccan spiced soup bowl",
    "salads": "moroccan fresh salad plate",
    "veg":    "moroccan vegetable dish",
    "meat":   "moroccan meat tagine stew",
    "chick":  "moroccan chicken tagine",
    "fish":   "moroccan fish dish",
    "hol":    "moroccan festive holiday food",
    "des":    "moroccan sweets pastry",
    "span":   "sephardic jewish spanish recipe",
    "iraq":   "iraqi jewish food",
    "kurd":   "kurdish food dish",
    "ashk":   "ashkenazi jewish food",
    "yem":    "yemeni food dish",
    "pers":   "persian food dish",
    "buk":    "bukharian uzbek food",
    "tun":    "tunisian food dish",
    "isr":    "israeli food dish",
    "turk":   "turkish food dish",
}

# Ingredient-based fallback
INGR_FALLBACK = [
    ("בקר",     "moroccan beef stew"),
    ("עגל",     "moroccan veal tagine"),
    ("בשר",     "moroccan meat stew"),
    ("כבש",     "moroccan lamb stew"),
    ("עוף",     "moroccan chicken dish"),
    ("פרגית",   "moroccan chicken thigh"),
    ("דג",      "moroccan fish dish"),
    ("תפוחי אדמה","moroccan potato dish"),
    ("אורז",    "moroccan rice dish"),
    ("פסטה",    "moroccan pasta dish"),
    ("קמח",     "moroccan flour bread"),
    ("גבינה",   "moroccan cheese dish"),
    ("שמן זית", "mediterranean olive oil"),
    ("ג׳ינג׳ר", "moroccan ginger spiced"),
    ("דלעת",    "moroccan pumpkin dish"),
    ("ים-תיכוני","mediterranean dish"),
]

def build_query(recipe):
    ingrs = recipe.get("ingr", [])[:4]
    title = recipe["title"]
    cat   = recipe["cat"]
    for kw, q in TITLE_QUERIES:
        if kw in title:
            return q
    # Ingredient-based fallback
    for kw, q in INGR_FALLBACK:
        if kw in title or any(kw in i for i in ingrs):
            return q
    return CAT_QUERY.get(cat, "moroccan jewish food dish")

# ══════════════════════════════════════════════════
# IMAGE SOURCES
# ══════════════════════════════════════════════════

def source_mealdb(query):
    """TheMealDB free API — real food photos, fast."""
    _, sd = get_sess()
    words = query.split()[:2]
    from urllib.parse import quote_plus
    try:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={quote_plus(' '.join(words))}"
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
    """Wikimedia Commons — max 2 API calls per recipe."""
    sp, sd = get_sess()
    from urllib.parse import quote_plus
    for sess in [sd, sp]:
        try:
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
            chosen = None
            for res in results:
                t = res.get("title", "")
                if not t.startswith("File:"):
                    continue
                tl = t.lower()
                if not any(e in tl for e in [".jpg", ".jpeg", ".png"]):
                    continue
                if any(b in tl for b in ["map","flag","logo","diagram","icon","symbol"]):
                    continue
                chosen = t
                break
            if not chosen:
                continue
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
                ii   = pg.get("imageinfo", [{}])[0]
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
            if data[:2] == b'\xff\xd8' or data[:4] == b'\x89PNG':
                dest.write_bytes(data)
                return True
            if "image" in ct and len(data) > 10_000:
                dest.write_bytes(data)
                return True
        except Exception:
            continue
    return False

# ══════════════════════════════════════════════════
# MAIN
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
    log("Perla Ben-Harrosh z\"l Cookbook — Image Downloader")
    log("=" * 55)
    log(f"Recipes: {total} | Existing: {already} | OVERWRITE={OVERWRITE}")
    log(f"Output dir: {IMG_DIR}")
    log(f"Log file:   {LOG_FILE}")
    log(f"Socket timeout: {socket.getdefaulttimeout()}s | Net timeout: {NET_TIMEOUT}s")
    log(f"Sources: TheMealDB -> Wikimedia Commons")
    log(f"Ctrl+C will exit immediately (log already saved per recipe)")
    log("=" * 55)

    ok_count = skip_count = fail_count = mealdb_count = wiki_count = 0

    for i, recipe in enumerate(recipes):
        if _STOP:
            log("Stop requested.")
            break

        rid   = recipe["id"]
        title = recipe["title"]
        cat   = recipe["cat"]
        dest  = IMG_DIR / f"r-{rid}.jpg"

        if dest.exists() and not OVERWRITE:
            skip_count += 1
            if skip_count <= 5 or skip_count % 50 == 0:
                log(f"  >> [{i+1:4d}/{total}] skip [{rid}]")
            continue

        query = build_query(recipe)
        log(f"  >> [{i+1:4d}/{total}] [{rid:8s}] {title[:28]:28s} -> \"{query[:35]}\"")

        saved  = False
        source = "?"

        if not saved:
            url = source_mealdb(query)
            if url and download_and_save(url, dest):
                saved = True; source = "mealdb"; mealdb_count += 1

        if not saved:
            url = source_wikimedia_single(query)
            if url and download_and_save(url, dest):
                saved = True; source = "wiki"; wiki_count += 1

        if saved:
            ok_count += 1
            log(f"  OK [{rid}] {source}")
        else:
            fail_count += 1
            log(f"  FAIL [{rid}] no image found")

        done = i + 1
        pct  = done * 100 // total
        if pct % 10 == 0 and done > 0 and done < total:
            log(f"\n  -- {pct}% ({done}/{total})  ok={ok_count}  skip={skip_count}  fail={fail_count}  [mealdb={mealdb_count} wiki={wiki_count}]\n")

        time.sleep(DELAY)

    log("=" * 55)
    log(f"Done: ok={ok_count}  skip={skip_count}  fail={fail_count}")
    log(f"  TheMealDB: {mealdb_count}  Wikimedia: {wiki_count}")
    log(f"Output dir: {IMG_DIR}")
    log(f"Log file:   {LOG_FILE}")
    log("=" * 55)

if __name__ == "__main__":
    main()
