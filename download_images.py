#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_images.py — Perla Ben-Harrosh z"l Cookbook
====================================================
סקריפט מאוחד: הורדת תמונות + ניקוי כפילויות (dedup) — הכל בריצה אחת.

שלב 1 — Download:
  מוריד תמונות ל-1,014 מתכונים מקוריים + 40 לא-כשרים = 1,054 סה"כ.
  מקורות בסדר עדיפות: עברית-ראשון → TheMealDB → Wikimedia →
                         Openverse → Unsplash → DuckDuckGo → Loremflickr
  בטוח מפני תלייה: socket timeout גלובלי, Ctrl+C = יציאה מיידית.

שלב 2 — Dedup (ניקוי כפילויות דינמי):
  סורק את תיקיית images/ לפי גודל קובץ.
  כל קבוצת קבצים עם גודל זהה = תמונה כפולה.
  מחליף כפילויות ב-Hard Link לקובץ הקנוני — אפס מקום נוסף,
  כל מתכון ממשיך לראות r-{id}.jpg שלו ללא שינוי באתר.

Usage:
    python download_images.py                    # הורדה + dedup (ברירת מחדל)
    python download_images.py --skip-download    # רק dedup
    python download_images.py --skip-dedup       # רק הורדה
    python download_images.py --dry-run          # תצוגה מקדימה של dedup
    python download_images.py --overwrite        # הורד מחדש גם קיימות

Requirements:
    pip install requests

Log: SCRIPT_DIR/logs/download_images_YYYY-MM-DD_HH.MM.log
"""
import os, re, sys, time, signal, socket, argparse
from datetime import datetime
from pathlib import Path

# ── Fix Windows PowerShell: UTF-8 encoding + Hebrew RTL display ─────────────
# Problem: PowerShell is an LTR terminal. Hebrew is stored in logical order
# (memory: right-to-left) but printed left-to-right, making it look reversed.
#
# Solution: pure-Python BiDi visual-order conversion — no external libraries.
# Each Hebrew character-run is reversed before printing so that when the LTR
# terminal reads left-to-right, a Hebrew reader sees it correctly right-to-left.
# The LOG FILE always receives the original, unreversed Hebrew.
# ─────────────────────────────────────────────────────────────────────────────

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.system('chcp 65001 >nul 2>&1')

# Hebrew Unicode ranges used for character classification
_HE_SET = frozenset(
    'אבגדהוזחטיכלמנסעפצקרשתךםןףץ'   # base letters
    'ׁׂ׳״'                            # marks / punctuation
)

def _he(ch: str) -> bool:
    """True if ch is a Hebrew character."""
    return ch in _HE_SET or '\u0591' <= ch <= '\u05c7' or '\ufb1d' <= ch <= '\ufb4f'

def _bidi_for_console(text: str) -> str:
    """
    Convert Hebrew logical-order text to visual order for an LTR terminal.

    Splits the string into alternating runs of Hebrew and non-Hebrew.
    Each Hebrew run is reversed character-by-character so that when the
    LTR terminal prints left-to-right, a Hebrew reader reading right-to-left
    sees the correct word order.

    Pure Python, no external packages required.
    Log file is NOT affected — only the console print uses this.
    """
    if not any(_he(c) for c in text):
        return text          # no Hebrew → nothing to fix

    # ── Segment into Hebrew / Non-Hebrew runs ──────────────────────
    segs: list[tuple[bool, list[str]]] = []   # (is_hebrew, chars)
    cur_he   = None
    cur_buf: list[str] = []

    for ch in text:
        ch_he = _he(ch)
        # Spaces are "neutral" — continue the current run type
        if ch == ' ' and cur_he is not None:
            ch_he = cur_he
        if ch_he != cur_he:
            if cur_buf:
                segs.append((cur_he, cur_buf))
            cur_he  = ch_he
            cur_buf = [ch]
        else:
            cur_buf.append(ch)
    if cur_buf:
        segs.append((cur_he, cur_buf))

    # ── Rebuild: reverse each Hebrew run ──────────────────────────
    out: list[str] = []
    for is_he, chars in segs:
        if is_he:
            out.append(''.join(reversed(chars)))
        else:
            out.append(''.join(chars))

    return ''.join(out)

# ── global socket timeout BEFORE any import of requests/urllib3 ──
# This is the only reliable way to prevent hung network calls on Windows.
socket.setdefaulttimeout(5)

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
LOG_DIR     = Path(r"C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook\logs") if sys.platform == 'win32' else SCRIPT_DIR / "logs"
_ts         = datetime.now().strftime("%Y-%m-%d_%H.%M")
LOG_FILE    = LOG_DIR / f"download_images_{_ts}.log"

# Proxy for network requests only.  None = no proxy
PROXY       = "http://pac.gov.il:8080"

DELAY       = 0.4    # seconds between recipes (rate limiting)
NET_TIMEOUT = 4      # seconds per network request  (< socket global timeout=8)
OVERWRITE   = True  # True = overwrite existing images

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
_size_index: dict = {}   # size→Path; built in main() for dedup
def _sigint(sig, frame):
    print("\n\n[!] Ctrl+C — exiting...", flush=True)
    os._exit(0)   # immediate hard exit — no cleanup, no hang
signal.signal(signal.SIGINT, _sigint)

# ── log — writes to file immediately after each call ──
def log(msg: str) -> None:
    """
    Write msg to console (BiDi-fixed for Windows) and to the log file (original).
    """
    ts   = time.strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"                    # log file — original Hebrew

    # Console — apply BiDi visual-order fix on Windows
    if sys.platform == 'win32':
        console_msg  = _bidi_for_console(msg)
    else:
        console_msg  = msg
    console_line = f"[{ts}] {console_msg}"

    try:
        print(console_line, flush=True)
    except UnicodeEncodeError:
        # Last-resort ASCII fallback
        print(f"[{ts}] {msg.encode('ascii', 'replace').decode()}", flush=True)
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
    Never hangs thanks to socket.setdefaulttimeout(5)."""
    sp, sd = get_sess()
    hdrs = API_HDRS if api else HDRS
    for sess in [sd, sp]:
        try:
            r = sess.get(url, timeout=(3, 6), stream=stream,
                         allow_redirects=True, headers=hdrs)
            if r.status_code == 200:
                return r
        except Exception:
            continue
    return None

def _call_with_timeout(fn, timeout_sec=12):
    """Run fn() in a daemon thread; return result or None on timeout."""
    import threading
    result = [None]
    error  = [None]
    def _worker():
        try:
            result[0] = fn()
        except Exception as e:
            error[0] = e
    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=timeout_sec)
    if t.is_alive():
        return None   # timed out — thread abandoned (daemon=True auto-dies)
    if error[0]:
        return None
    return result[0]

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
    ("מרק זנגביל","moroccan ginger lemon soup"),
    ("מרק כוסמין","moroccan spelt soup"),
    ("זמיתה","moroccan toasted flour olive soup"),
    ("מרק תירס מרוקאי","moroccan corn vegetable soup"),
    ("מרק חבושים","moroccan quince lamb soup"),
    ("מרק שחלים","moroccan watercress soup"),
    ("מרק ראס מרוקאי","moroccan lamb head soup"),
    ("מרק כוסברה","moroccan cilantro lemon soup"),
    ("מרק זנגביל ולימון","moroccan ginger lemon broth"),
    ("מרק חרירה בשר","moroccan harira lamb soup"),
    ("מרק טלה עם עגבניות","moroccan lamb tomato broth"),
    ("מרק פסטה מרוקאי","moroccan pasta vegetable soup"),
    ("מרק בצל מרוקאי","moroccan onion butter soup"),
    ("מרק שחלים ולמון","moroccan watercress lemon"),
    ("מרק מרוקאי חריף","moroccan spicy red soup"),
    ("מרק שורש","moroccan root vegetable soup"),
    ("מרק עדשים עיראקי","iraqi lentil soup"),
    ("מרק קוסקוס","tunisian couscous chorba"),
    ("מרק מלוקיה","molokhia turkish soup"),
    ("מרק ירק אשכנזי","ashkenazi vegetable soup"),
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
    ("שאקשוקה מרוקאית","shakshuka moroccan eggs tomato"),
    ("סלט ורמיצ׳לי","moroccan cold vermicelli salad"),
    ("סלט זחלוק חציל","zaalouk eggplant moroccan"),
    ("סלט חציל ורימון","moroccan eggplant pomegranate salad"),
    ("סלט ח׳וביזה","moroccan mallow herb salad"),
    ("סלט חסה ועגבנייה","moroccan lettuce tomato salad"),
    ("סלט מלפפון ולבן","moroccan cucumber yogurt salad"),
    ("סלט גבינה ועגבנייה","moroccan cheese tomato salad"),
    ("סלט שעועית אדומה","moroccan red kidney bean salad"),
    ("סלט חיטה מרוקאית","moroccan wheat berry salad"),
    ("סלט תפוז ורימון","moroccan orange pomegranate salad"),
    ("סלט פול ורוזמרין","moroccan fava rosemary salad"),
    ("סלט חצי שנה","moroccan harvest salad"),
    ("סלט ביצה ועשבים","moroccan egg herb salad"),
    ("סלט ירקות מרוקאי","moroccan mixed vegetable salad"),
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
    ("סלט שעועית אדומה","moroccan red kidney bean salad"),
    ("גזר עם שמן אגוז","moroccan carrot walnut oil"),
    ("שעועית אדומה עם אורז","moroccan red bean rice"),
    ("בצלצלים מקורמלים","moroccan caramelized pearl onions"),
    ("בצלצלים במרינרה","moroccan onion marinara"),
    ("שושנת יריחו","moroccan jericho rose desert vegetable"),
    ("ירקות מרוקאיים חריפים","moroccan spicy roasted vegetables"),
    ("ירקות ממולאים מרוקאיים","moroccan stuffed mixed vegetables"),
    ("כרוב בחמאה ועשבים","moroccan cabbage herb butter"),
    ("תרד עם ביצה","moroccan spinach egg"),
    ("קישוא עם ביצים","moroccan zucchini scrambled eggs"),
    ("דלעת עם צימוקים","moroccan pumpkin raisins sweet"),
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
    ("מרק חרירה בשר","moroccan harira lamb soup"),
    ("בשר בקר עם ג׳ינג׳ר טרי","moroccan beef fresh ginger"),
    ("בשר עם ירקות ים-תיכוניים","moroccan beef mediterranean vegetables"),
    ("קדרה מרוקאית","moroccan beef clay pot"),
    ("ראגו מרוקאי","moroccan meat ragu sauce"),
    ("לחמג׳ון מרוקאי","moroccan lahmacun meat flatbread"),
    ("עצמות עוף בציר","moroccan chicken bone broth"),
    ("בשר עם זיתים","moroccan meat olive tagine"),
    ("מוח עגל ברוטב","moroccan veal brain sauce"),
    ("בשר עם תבלינים ספרדיים","moroccan sephardic spiced beef"),
    ("קציצות בשר ספרדיות","moroccan sephardic meatball"),
    ("בשר ממולא","moroccan stuffed meat"),
    ("כבש עם מעי","moroccan lamb intestine"),
    ("תבשיל כרוב ובשר","kurdish cabbage meat stew"),
    ("עמוחה","amoucha tunisian hot peppers"),
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
    ("עוף ממשמש","moroccan chicken apricot tagine"),
    ("עוף עם ב׳לחה","moroccan chicken spice sauce"),
    ("דיגה","moroccan chicken black sauce"),
    ("עוף עם מחמצות","moroccan chicken pickled lemon"),
    ("עוף עם שומר ולמון","moroccan chicken fennel lemon"),
    ("כנפיים מרוקאיות","moroccan spiced chicken wings"),
    ("עוף עם ביצה קשה","moroccan chicken hard egg tagine"),
    ("עוף עם שמיר ולמון","moroccan chicken dill lemon"),
    ("עוף עם פירות הדר","moroccan chicken citrus tagine"),
    ("עוף ביין לבן","moroccan chicken white wine"),
    ("עוף בפפריקה עם ירקות","moroccan paprika chicken"),
    ("עוף עם קינמון ורימון","moroccan chicken cinnamon pomegranate"),
    ("עוף עם בצל ועגבניות","moroccan chicken onion tomato"),
    ("עוף עם חמוצי לימון","moroccan chicken preserved lemon tagine"),
    ("עצמות עוף בציר","moroccan chicken bone broth"),
    ("דמפוכת עוף כורדי","kurdish chicken dumplings"),
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
    ("בניקה","moroccan fish pie pastry"),
    ("דג מרוקאי עם כרשה","moroccan fish leek"),
    ("דג ממולא בתמרים","moroccan stuffed fish dates"),
    ("כבלייה","moroccan fish first course"),
    ("דג עם ורדים ירוקים","moroccan fish green pepper"),
    ("דג מרוקאי עם כרכום","moroccan fish turmeric"),
    ("ג׳לה","moroccan cold fish jelly"),
    ("מקרל אפוי","moroccan baked mackerel"),
    ("דג עם רוטב ירוק","moroccan fish green herb sauce"),
    ("דג עם כוסברה ולימון","moroccan fish cilantro lemon"),
    ("פשטידת דג","moroccan fish pie baked"),
    ("דג שלם בתנור","moroccan whole baked fish"),
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
    ("טאג׳ין בקר עם דלעת","moroccan beef pumpkin tagine"),
    ("טאג׳ין כרוב","moroccan cabbage lamb tagine"),
    ("טאג׳ין עגל עם ירקות","moroccan veal vegetable tagine"),
    ("כוסות בצק","moroccan pastry cups"),
    ("פסה","moroccan layered bread pasha"),
    ("טאג׳ין עגל ואנשובי","moroccan veal anchovy tagine"),
    ("כאב אל-ע׳זאל ורד","moroccan rose gazelle horn"),
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
    ("בוזה","moroccan wheat pudding booza"),
    ("ח׳מירו","moroccan oil cookies"),
    ("עוגיות אפרסמון","moroccan persimmon cookies"),
    ("ספנג׳ מגלגל","moroccan rolled sfenj doughnuts"),
    ("עוגת אגסים","moroccan pear cake"),
    ("כדורי שוקולד מרוקאיים","moroccan chocolate date balls"),
    ("עוגיות לוז","moroccan hazelnut cookies"),
    ("פנה קוטה מרוקאית","moroccan panna cotta rose"),
    ("חלבה מרוקאית","moroccan halva semolina"),
    ("מוס שוקולד","moroccan chocolate mousse"),
    ("עוגת תבלינים","moroccan spice cake"),
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
    ("פסטיל ביצה","sephardic egg pastry"),
    ("פסטלון","sephardic matzah pie passover"),
    ("קבב מרוקאי-ספרדי","moroccan sephardic kebab grilled"),
    ("מנחה","sephardic afternoon meal"),
    ("פשטיל ירקות","sephardic vegetable pastry"),
    ("תורוניה","turron nougat spanish sephardic"),
    ("פוצ׳רוס","puchero spanish sephardic stew"),
    ("פישבולה","sephardic oil cookies"),
    ("קרמה קטלנה","crema catalana custard dessert"),
    ("קוקידו — קדרת שבת","cocido sephardic shabbat stew"),
    ("קלאמרס","calamari squid sephardic"),
    ("טיירה דה פשקה","tirade pesah sephardic fish"),
    ("מנחה ספרדית","sephardic afternoon meal"),
    ("ביסקוצ׳ו שקדים","sephardic almond biscotti"),
    ("סוקראט","sephardic pancakes crepes"),
    ("ח׳יקה","sephardic sausage charcuterie"),
    ("קוקה ספרדית","coca sephardic savory tart"),
    ("סופריטו בסיסי","sofrito basic spanish sauce"),
    ("סאינה","sephardic pickled vegetables"),
    ("אייולי מרוקאי","aioli moroccan sephardic garlic"),
    ("פטאטאס ברבאס","patatas bravas sephardic potatoes"),
    ("טורטייה ספרדית","tortilla espanola potato omelette"),
    ("פאן קון טומאטה","pan con tomate sephardic bread tomato"),
    ("ח׳מון קון מלון","jamon melon sephardic appetizer"),
    ("סלמוריחו","salmorejo cold tomato soup sephardic"),
    ("חוקינוס ספרדיים","choukinos sephardic zucchini"),
    ("ביסקוצ׳ו בורצ׳ו","sephardic wine cake borchu"),
    ("פאן דה-מוארטוס","pan de muertos sephardic bread"),
    ("חמין אדאפינה שלם","adafina complete shabbat sephardic"),
    ("פסקאדו קון אגוודה","pescado escabeche sephardic vinegar fish"),
    ("אלמנדיגאס קון מולו","albondigas salsa almendras sephardic"),
    ("אורוז קון לצ׳ה","arroz con leche sephardic rice pudding"),
    ("בורקיטאס דה קאלאבאסה","boureka pumpkin sephardic hanukkah"),
    ("הואבוס אמאדוס","huevos hamados sephardic eggs tomato"),
    ("לוקסן קון לצ׳ה","loksen leche sephardic noodle milk"),
    ("לומברדה","lombarda red cabbage sephardic festive"),
    ("טרמסוס","tramsos lupini beans sephardic"),
    ("קרפ ספרדי-מרוקאי","crepe sephardic moroccan"),
    ("ח׳פה בסוכר","jafet sugar fried sephardic"),
    ("אורוז קון פולו","arroz con pollo sephardic chicken rice"),
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
    ("תמר הינדי","tamarind drink iraqi"),
    ("חלבה עיראקית בסולת","iraqi halva semolina"),
    ("תבולה עיראקית","iraqi tabolah salad"),
    ("מסגוף","masgoof iraqi grilled fish"),
    ("בסטורמה עם ביצים","basturma eggs iraqi"),
    ("ג׳אג׳יק","cacik yogurt cucumber iraqi"),
    ("כבב עיראקי בסיר","iraqi kebab pot stew"),
    ("קיימה","kima iraqi minced meat peas"),
    ("מרק עדשים עיראקי","iraqi lentil soup"),
    ("כבוב עיראקי","iraqi grilled kebab"),
    ("ג׳אג׳יק","tzatziki yogurt cucumber turkish"),
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
    ("דמפוכת עוף כורדי","kurdish chicken dumplings"),
    ("יוגורט מבושל כורדי עם שום","kurdish cooked yogurt garlic"),
    ("כבוב כורדי בתבנית","kurdish baked kebab tray"),
    ("ירגה","yareh kurdish yogurt wheat"),
    ("חביתה כורדית עם עשבים","kurdish herb frittata"),
    ("תבשיל כרוב ובשר","kurdish cabbage meat stew"),
    ("פיטה כורדית","kurdish pita clay oven"),
    ("אורז עם ירקות שורש","kurdish rice root vegetables"),
    ("שישבראק","shishbarak lamb dumplings yogurt"),
    ("כישקה","kishka stuffed intestine kurdish"),
    ("דולמה כורדית","kurdish dolma stuffed"),
    ("גמה","kurdish savory stuffed pastry"),
    ("ספינג","kurdish fried dough"),
    ("רימון ויוגורט","pomegranate yogurt"),
    ("ממחל","kurdish walnut field"),
    ("תבשיל גבינה","kurdish cheese tomato stew"),
    # Ashkenazi
    ("מנדלברוט","mandelbrot almond biscotti jewish"),
    ("גאלחד","galchad pickled cabbage sauerkraut"),
    ("שניצל אשכנזי","schnitzel ashkenazi breaded"),
    ("מרק ירק אשכנזי","ashkenazi vegetable soup"),
    ("לאקסנין קופ","lokshen kop noodle head ashkenazi"),
    ("ביסמארק","bismarck pretzel roll ashkenazi"),
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
    ("מצוב","matzoob yemeni round couscous"),
    ("ביצה תימנית בחרדל","yemeni egg mustard"),
    ("תרייד","thareed yemeni bread sauce"),
    ("ביניות","binyat yemeni braised vegetables"),
    ("מאנסף","mansaf lamb yogurt rice yemeni"),
    ("קדיד","qadid yemeni dried salted meat"),
    ("אל-פת","al-fatt yemeni round bread"),
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
    ("ג׳ווארי","jowari persian grain porridge"),
    ("אשׂ-ה-רשׂ-תה","ash reshteh persian herb noodle soup"),
    ("מרגי","morgh persian saffron chicken"),
    ("פלאו","polo persian rice classic"),
    ("כבב קובידה","koobideh persian ground kebab"),
    ("תורשי","torshi persian pickled vegetables"),
    ("שיר-ברנג׳","shir berenj persian rice pudding"),
    ("אשׂ-ה-גוש׳","ash ghoosht persian walnut lentil soup"),
    ("כוכו אחר","kuku persian egg vegetable"),
    ("חשׂ-ה-בישׁ","khash-e-bish persian"),
    ("גורמה סבזי","ghormeh sabzi persian herb stew"),
    ("קוקו סבזי","kuku sabzi persian herb frittata"),
    ("פסנג׳ן","fesenjan pomegranate walnut chicken"),
    ("ירקות ממולאים פרסיים","dolmeh persian stuffed"),
    ("חלווה ארדה","persian halva sesame"),
    ("ריגן","persian scallion cheese"),
    ("מרגיצ׳ה","persian egg eggplant patties"),
    ("מרק אנרגטי","persian energy soup"),
    # Bukharian
    ("מרק שחלים","moroccan watercress soup"),
    ("מרק שחלים ולמון","moroccan watercress lemon"),
    ("מסטאבה","mastaba bukharian bread sesame"),
    ("שורבה","shorba bukharian soup"),
    ("ירוגי","yurogi bukharian vegetable salad"),
    ("חשפוש","khashpush bukharian stuffed"),
    ("שישלק","shashlik bukharian skewer"),
    ("חלים","halim bukharian semolina halva"),
    ("שיפטה","shafta bukharian rolls"),
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
    ("כפתאג׳י","kafteji tunisian fried vegetable"),
    ("לחם תוניסי","tunisian bread khobz"),
    ("מרק קוסקוס","tunisian couscous chorba"),
    ("מחמרה","mahamera tunisian spicy egg"),
    ("מקרונה","tunisian pasta sauce"),
    ("פטחה","fatcha tunisian bread meat"),
    ("עמוחה","amoucha tunisian hot peppers"),
    ("מרזגן","merzeguen tunisian pickles"),
    ("זלביה תוניסית","zalabia tunisian honey donuts"),
    ("הרישה","hrissa tunisian hot paste"),
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

    # Israeli street food & modern
    ("פלאפל ירושלמי","jerusalem falafel crispy tahini"),
    ("חומוס ביתי","hummus homemade creamy"),
    ("חומוס מסבחה","msabbaha warm chickpea lemon"),
    ("שקשוקה ירושלמית","shakshuka jerusalem eggs tomatoes"),
    ("מג׳דרה","mujaddara lentil rice crispy onion"),
    ("שוורמה עוף","shawarma chicken wrap laffa"),
    ("בורקס גבינה ביתי","burekas cheese homemade phyllo"),
    ("סלט ישראלי","israeli chopped salad tomato cucumber"),
    ("מנסף ישראלי","mansaf lamb yogurt rice"),
    ("עוף בפול ירוק","chicken green fava beans israeli"),
    ("פיתה ביתית","pita bread homemade israeli"),
    ("תחינה ביתית","tahini homemade sesame"),
    ("כבד קצוץ","chopped liver onion jewish"),
    ("עוף שוק מרינד","chicken thigh lemon garlic marinade"),
    ("אורז אדום","red rice vermicelli israeli"),
    ("קציצות בשר ורוטב","meatballs tomato sauce israeli"),
    ("ג׳חנון ישראלי","jachnun israeli quick overnight"),
    ("קרמבו ביתי","krembo chocolate marshmallow israeli"),
    ("פיתה ים תיכונית","pita mediterranean flatbread"),
    ("לחמניות שמרים","yeast rolls seeds bread"),
    ("סלט טחינה ופלפל","tahini roasted pepper salad"),
    ("ביצה בחמאה עם זעתר","fried egg butter zaatar"),
    ("עוגת שוקולד חוקית","chocolate cake israeli moist"),
    ("תרד עם ביצים","spinach eggs israeli style"),
    ("ממרח גבינה עם עגבניות","cream cheese tomato spread"),
    ("חמין ישראלי","hamin cholent israeli sabbath"),
    ("גזפצ׳ו ישראלי","gazpacho israeli cold soup"),
    ("עוגיות קוקוס","coconut cookies israeli"),
    ("עוגת תפוחים ישראלית","apple cake israeli cinnamon"),
    ("עוגיות הקפה","coffee chocolate cookies israeli"),
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
    ("ג׳אג׳יק","cacik yogurt cucumber iraqi"),
    ("מנדה","manda turkish fish dumplings"),
    ("ג׳אג׳יק","tzatziki yogurt cucumber turkish"),
    ("מרק מלוקיה","molokhia turkish soup"),
    ("בריאם","briam turkish roasted vegetables"),
    ("כבב איסטנבול","istanbul kebab turkish"),
    ("אורז פילאף","pilaf turkish rice"),
    ("מוסקה טורקית","moussaka turkish eggplant meat"),
    ("בקלאוה טורקית","baklava turkish honey walnut"),
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
    # ── Additional entries fixing bad substring matches (2026-04 audit) ──
    ("ריג׳לה",           "moroccan purslane salad"),
    ("פיתה מרוקאית",     "moroccan pita bread round"),
    ("פיתה ים תיכונית",  "pita mediterranean flatbread"),
    ("פיתה ביתית",       "pita bread homemade"),
    ("כרובית חרמולה",    "moroccan cauliflower chermoula"),
    ("כרובית מרוקאי",    "moroccan cauliflower roasted"),
    ("כרובית צלויה",     "moroccan cauliflower roasted"),
    ("כרובית חריפה",     "moroccan spicy cauliflower"),
    ("כרובית",           "moroccan cauliflower roasted"),
    ("לחמניות שמרים",    "yeast rolls seeds bread"),
    ("לחמניות גבינה",    "cheese rolls baked"),
    ("לחמניות",          "moroccan bread rolls"),
    ("דג בחלב שקדים",    "moroccan fish almond milk"),
    ("חלב שקדים",        "moroccan almond milk drink"),
    ("מקרל ממרוח",       "moroccan grilled mackerel"),
    ("מקרל אפוי",        "moroccan baked mackerel"),
    ("מקרל",             "moroccan mackerel fish"),
    ("אסידה",            "asida north african porridge"),
    ("ביצר",             "tunisian vegetables harissa"),
    ("כבדה",             "moroccan liver spicy"),
    ("שחשוקה",           "shakshuka eggs tomatoes"),
    ("ממולאי ריקוטה",    "stuffed pasta ricotta spinach"),
    ("ריקוטה",           "ricotta stuffed vegetable"),
    ("מקרונה תוניסית",   "tunisian pasta sauce"),
    ("סלט פולנטה",       "moroccan polenta salad"),
    ("פולנטה",           "polenta cheese dish"),
    ("פסטיל — ביצה",     "sephardic egg pastry"),
    ("פסטיל ספרדי",      "sephardic egg pastry"),
    ("סביחה",            "sabich eggplant pita"),
    ("ספינג׳",           "sfenj moroccan donuts"),
    ("ספנג׳",            "sfenj moroccan donuts"),
    ("מרק קוסקוסית",     "moroccan couscous soup"),

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
    "isr":    "israeli street food modern falafel hummus",
    "turk":   "turkish food dish",
    "nonkosher": "moroccan seafood shellfish dish"
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
    ("שרימפס",  "seafood shrimp dish"),
    ("קלמארי",  "calamari squid dish"),
    ("תפוחי אדמה","moroccan potato dish"),
    ("אורז",    "moroccan rice dish"),
    ("פסטה",    "moroccan pasta dish"),
    ("קמח",     "moroccan flour bread"),
    ("גבינה",   "cheese dairy dish"),
    ("שמן זית", "mediterranean olive oil"),
    ("ג׳ינג׳ר", "moroccan ginger spiced"),
    ("דלעת",    "moroccan pumpkin dish"),
    ("חומוס",   "chickpea hummus dish"),
    ("עדשים",   "lentil dish"),
    ("שעועית",  "bean dish stew"),
]

# Hebrew letter set for word-boundary detection
_HE_LETTERS = frozenset('אבגדהוזחטיכלמנסעפצקרשתךםןףץ')

def _he_word_boundary(s, idx, kw_len):
    """Return True if kw at position idx in s is NOT a substring of a longer Hebrew word."""
    before = s[idx - 1] if idx > 0 else ' '
    after  = s[idx + kw_len] if idx + kw_len < len(s) else ' '
    return (before not in _HE_LETTERS) and (after not in _HE_LETTERS)

# Pre-sort TITLE_QUERIES by key length descending (longer/more specific first)
# This prevents "כרוב" matching inside "כרובית", "ג׳לה" inside "ריג׳לה", etc.
_TQ_SORTED = sorted(TITLE_QUERIES, key=lambda x: -len(x[0]))
_IF_SORTED  = sorted(INGR_FALLBACK, key=lambda x: -len(x[0]))

def build_query(recipe):
    """Build an English image-search query for a recipe.

    Uses word-boundary–aware matching so that shorter Hebrew keys
    (e.g. 'כרוב') do NOT accidentally match longer words (e.g. 'כרובית').
    Keys are tried longest-first so the most-specific match wins.
    """
    ingrs = recipe.get("ingr", [])[:4]
    title = recipe["title"]
    cat   = recipe["cat"]

    # 1. TITLE match — word-boundary aware, longest key first
    for kw, q in _TQ_SORTED:
        idx = title.find(kw)
        if idx >= 0 and _he_word_boundary(title, idx, len(kw)):
            return q

    # 2. Ingredient-based fallback — also longest-first
    for kw, q in _IF_SORTED:
        if _he_word_boundary(title + ' ', title.find(kw) if kw in title else -1, len(kw))                 and kw in title:
            return q
        if any(kw in i for i in ingrs):
            return q

    # 3. Category default
    return CAT_QUERY.get(cat, "moroccan jewish food dish")

# ══════════════════════════════════════════════════
# IMAGE SOURCES — 5 sources in cascade
# ══════════════════════════════════════════════════

def _best_keywords(query, n=3):
    """Return the n most descriptive words from the query."""
    STOP = {"food","dish","recipe","plate","meal","with","and","the","in","a"}
    words = [w for w in query.lower().split() if w not in STOP and len(w) > 2]
    return " ".join(words[:n])



def source_hebrew_first(recipe_title, query_en):
    """Search images using Hebrew recipe title first (Israeli/Hebrew sources priority).

    Strategy:
    1. Wikimedia Commons with Hebrew title + 'מאכל' / 'אוכל'
    2. Hebrew Wikipedia food category images
    3. Wikimedia with Hebrew title alone
    Falls back to None so cascade continues to English sources.
    """
    _, sd = get_sess()
    from urllib.parse import quote_plus

    # Build Hebrew search variants (limit to 2 for speed)
    he_queries = [
        recipe_title + " מאכל",          # title + "food" in Hebrew
        recipe_title,                      # title alone
    ]

    for q in he_queries:
        try:
            r = sd.get(
                "https://commons.wikimedia.org/w/api.php",
                params={"action":"query","list":"search",
                        "srsearch": q, "srnamespace": 6,
                        "srlimit": 3, "format": "json",
                        "uselang": "he"},   # Hebrew UI — biases results
                timeout=NET_TIMEOUT, verify=False, headers=API_HDRS)
            if r.status_code != 200:
                continue
            results = r.json().get("query", {}).get("search", [])
            for res in results:
                t = res.get("title", "")
                if not t.startswith("File:"):
                    continue
                tl = t.lower()
                if not any(e in tl for e in [".jpg", ".jpeg", ".png"]):
                    continue
                if any(b in tl for b in ["map", "flag", "logo", "diagram",
                                          "icon", "symbol", "person", "portrait",
                                          "flag", "coat_of_arms"]):
                    continue
                # Fetch image URL
                r2 = sd.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params={"action":"query","titles":t,"prop":"imageinfo",
                            "iiprop":"url|size|mime","iiurlwidth":600,"format":"json"},
                    timeout=NET_TIMEOUT, verify=False, headers=API_HDRS)
                if r2.status_code != 200:
                    continue
                for pg in r2.json().get("query",{}).get("pages",{}).values():
                    ii = pg.get("imageinfo", [{}])[0]
                    url  = ii.get("thumburl") or ii.get("url", "")
                    mime = ii.get("mime", "")
                    sz   = ii.get("size", 0)
                    if url and "image" in mime and 3000 < sz < 12_000_000:
                        return url
        except Exception:
            continue
    return None

def source_mealdb(query):
    """TheMealDB free API — real food photos, fast."""
    _, sd = get_sess()
    from urllib.parse import quote_plus
    # Try original query first, then simplified
    for q in [query, _best_keywords(query, 2)]:
        try:
            url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={quote_plus(q)}"
            r = sd.get(url, timeout=NET_TIMEOUT, verify=False, headers=API_HDRS)
            if r.status_code == 200:
                meals = r.json().get("meals") or []
                if meals:
                    thumb = meals[0].get("strMealThumb", "")
                    if thumb and thumb.startswith("http"):
                        return thumb
        except Exception:
            pass
    return None


def source_wikimedia_single(query):
    """Wikimedia Commons API — encyclopedic food photos."""
    sp, sd = get_sess()
    from urllib.parse import quote_plus
    for sess in [sd, sp]:
        for q in [query, _best_keywords(query, 2)]:
            try:
                r = sess.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params={"action":"query","list":"search",
                            "srsearch":f"{q} food","srnamespace":6,
                            "srlimit":8,"format":"json"},
                    timeout=NET_TIMEOUT, verify=False, headers=API_HDRS)
                if r.status_code != 200: continue
                results = r.json().get("query",{}).get("search",[])
                chosen = None
                for res in results:
                    t = res.get("title","")
                    if not t.startswith("File:"): continue
                    tl = t.lower()
                    if not any(e in tl for e in [".jpg",".jpeg",".png"]): continue
                    if any(b in tl for b in ["map","flag","logo","diagram",
                                              "icon","symbol","person","portrait"]): continue
                    chosen = t; break
                if not chosen: continue
                r2 = sess.get(
                    "https://commons.wikimedia.org/w/api.php",
                    params={"action":"query","titles":chosen,"prop":"imageinfo",
                            "iiprop":"url|size|mime","iiurlwidth":600,"format":"json"},
                    timeout=NET_TIMEOUT, verify=False, headers=API_HDRS)
                if r2.status_code != 200: continue
                for pg in r2.json().get("query",{}).get("pages",{}).values():
                    ii = pg.get("imageinfo",[{}])[0]
                    url = ii.get("thumburl") or ii.get("url","")
                    mime = ii.get("mime","")
                    sz   = ii.get("size",0)
                    if url and "image" in mime and 3000 < sz < 12_000_000:
                        return url
            except Exception:
                continue
    return None


def source_openverse(query):
    """Openverse CC image API — free open-licensed food photos.
    No API key needed for basic searches."""
    _, sd = get_sess()
    from urllib.parse import quote_plus
    for q in [query, _best_keywords(query, 3)]:
        try:
            r = sd.get(
                "https://api.openverse.org/v1/images/",
                params={"q": q, "license_type": "commercial,modification",
                        "mature": "false", "page_size": 10, "format": "json"},
                timeout=NET_TIMEOUT, verify=False, headers={
                    **API_HDRS,
                    "Accept": "application/json",
                })
            if r.status_code != 200: continue
            results = r.json().get("results", [])
            for res in results:
                url = res.get("url", "")
                # Prefer images with food-related tags
                tags = [t.get("name","").lower() for t in res.get("tags",[])]
                food_score = sum(1 for t in tags if t in
                    {"food","cooking","meal","dish","cuisine","recipe",
                     "moroccan","jewish","mediterranean","bread","soup"})
                if url and url.startswith("http") and food_score > 0:
                    return url
        except Exception:
            pass
    return None


def source_unsplash_search(query):
    """Wikipedia article images — reliable, free, high-quality food photos."""
    _, sd = get_sess()
    from urllib.parse import quote_plus
    kw = _best_keywords(query, 3)
    try:
        # Search English Wikipedia for articles matching the query
        r = sd.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":kw + " food",
                    "srlimit":"5","format":"json"},
            timeout=NET_TIMEOUT, verify=False, headers=API_HDRS)
        if r.status_code != 200: return None
        results = r.json().get("query",{}).get("search",[])
        for res in results:
            title = res.get("title","")
            # Get page images
            r2 = sd.get(
                "https://en.wikipedia.org/w/api.php",
                params={"action":"query","titles":title,"prop":"pageimages",
                        "piprop":"original","format":"json"},
                timeout=NET_TIMEOUT, verify=False, headers=API_HDRS)
            if r2.status_code != 200: continue
            for pg in r2.json().get("query",{}).get("pages",{}).values():
                img = pg.get("original",{}).get("source","")
                if img and any(e in img.lower() for e in [".jpg",".jpeg",".png"]):
                    return img
    except Exception:
        pass
    return None


def source_foodimages_scrape(query):
    """Scrape food image from a DuckDuckGo image search as last resort."""
    _, sd = get_sess()
    from urllib.parse import quote_plus
    kw = _best_keywords(query, 3) + " food recipe"
    try:
        # DuckDuckGo image search — parses JSON from their API
        vqd_r = sd.get(
            f"https://duckduckgo.com/?q={quote_plus(kw)}&iax=images&ia=images",
            timeout=NET_TIMEOUT, verify=False, headers={
                **API_HDRS,
                "Accept": "text/html",
            })
        if vqd_r.status_code != 200: return None
        # Extract vqd token
        vqd_m = re.search(r'vqd=([0-9-]+)', vqd_r.text) or re.search(r'"vqd":"([^"]+)"', vqd_r.text)
        if not vqd_m: return None
        vqd = vqd_m.group(1)
        img_r = sd.get(
            "https://duckduckgo.com/i.js",
            params={"l":"us-en","o":"json","q":kw,"vqd":vqd,"f":",,,,,","p":"1"},
            timeout=NET_TIMEOUT, verify=False, headers={
                **API_HDRS,
                "Referer": "https://duckduckgo.com/",
            })
        if img_r.status_code != 200: return None
        results = img_r.json().get("results", [])
        for res in results[:5]:
            url = res.get("image","")
            w, h = res.get("width",0), res.get("height",0)
            if url and w >= 300 and h >= 200:
                return url
    except Exception:
        pass
    return None


def source_loremflickr(query, recipe_id):
    """Loremflickr CDN — consistent placeholder images per recipe ID."""
    from urllib.parse import quote_plus
    kw = quote_plus(_best_keywords(query, 3))
    lock = abs(hash(recipe_id)) % 10000 + 1
    return f"https://loremflickr.com/600/400/{kw}?lock={lock}"


def find_youtube_video(title, query):
    """Return YouTube search URL — PRIORITY: Hebrew (Israeli) first.
    1st choice: Hebrew title + מתכון  
    2nd choice: Hebrew + English term
    3rd choice: English recipe name
    """
    from urllib.parse import quote_plus
    # Priority 1: Hebrew recipe name + מתכון keyword
    # This surfaces Israeli cooking channels first (Miri Tzahi, Keshef HaTvuot, etc.)
    return f"https://www.youtube.com/results?search_query={quote_plus(title + ' מתכון')}"


def build_youtube_urls(title, query):
    """All YouTube search URLs in priority order for Hebrew/Israeli content."""
    from urllib.parse import quote_plus
    return [
        "https://www.youtube.com/results?search_query=" + quote_plus(title + " מתכון"),
        "https://www.youtube.com/results?search_query=" + quote_plus(title + " " + query),
        "https://www.youtube.com/results?search_query=" + quote_plus(query + " recipe"),
    ]
def download_and_save(img_url, dest):
    """Download image and validate magic bytes. Returns True on success."""
    sp, sd = get_sess()
    # Handle pre-downloaded data (from source_unsplash_search)
    if isinstance(img_url, tuple) and img_url[0] == "__DATA__":
        data = img_url[1]
        if len(data) > 3000 and (data[:2] == b'\xff\xd8' or data[:4] == b'\x89PNG'):
            # ── Duplicate detection ────────────────────────────────
            file_sz = len(data)
            # Check global size-index (defined in main(), accessed via global)
            global _size_index
            existing = _size_index.get(file_sz)
            if existing and existing != dest:
                # Identical file already on disk — hard-link instead of writing
                try:
                    dest.hardlink_to(existing)   # Python 3.10+
                except AttributeError:
                    os.link(str(existing), str(dest))  # fallback
                except OSError:
                    dest.write_bytes(data)  # fallback: write normally
                # Register in index (dest → existing, same size)
                if file_sz not in _size_index:
                    _size_index[file_sz] = dest
                return True
            # ── Normal write ───────────────────────────────────────
            dest.write_bytes(data)
            _size_index[file_sz] = dest   # register for future dedup
            return True
        return False
    for sess in [sd, sp]:
        try:
            # timeout=(connect, read) — read timeout prevents slow-drip hangs
            r = sess.get(img_url, timeout=(3, 8), stream=False,
                         allow_redirects=True, verify=False)
            if r.status_code != 200: continue
            ct = r.headers.get("Content-Type","")
            if "text" in ct or "html" in ct: continue
            data = r.content
            if len(data) < 3000: continue
            if data[:2] == b'\xff\xd8' or data[:4] == b'\x89PNG' or ("image" in ct and len(data) > 10_000):
                # ── Duplicate detection (same as __DATA__ path) ──
                file_sz = len(data)
                existing = _size_index.get(file_sz)
                if existing and existing != dest:
                    try:
                        dest.hardlink_to(existing)
                    except AttributeError:
                        os.link(str(existing), str(dest))
                    except OSError:
                        dest.write_bytes(data)
                    if file_sz not in _size_index:
                        _size_index[file_sz] = dest
                    return True
                dest.write_bytes(data)
                _size_index[file_sz] = dest
                return True
        except Exception:
            continue
    return False


def run_dedup(dry_run: bool = False) -> None:
    """שלב 2 — ניקוי כפילויות דינמי.

    סורק את כל קבצי r-*.jpg לפי SHA256 hash.
    בכל קבוצה עם hash זהה:
      • קנוני  = הקובץ הראשון אלפביתית בקבוצה (נשמר)
      • שאר    = נמחקים ומוחלפים ב-Hard Link לקנוני
    Hard Link = שם נוסף לאותו inode — אפס מקום נוסף.
    """
    from collections import defaultdict
    import hashlib

    log("=" * 60)
    log("שלב 2 — Dedup: ניקוי כפילויות" + (" [DRY RUN]" if dry_run else ""))
    log("=" * 60)

    # ── סרוק את כל הקבצים וקבץ לפי גודל (pre-filter) ──────
    by_size: dict[int, list[Path]] = defaultdict(list)
    for p in sorted(IMG_DIR.glob("r-*.jpg")):
        try:
            sz = p.stat().st_size
            if sz > 0:
                by_size[sz].append(p)
        except OSError:
            pass

    # ── Hash only files with duplicate sizes (optimization) ──
    by_hash: dict[str, list[Path]] = defaultdict(list)
    for sz, paths in by_size.items():
        if len(paths) < 2:
            continue
        for p in paths:
            try:
                h = hashlib.sha256(p.read_bytes()).hexdigest()
                by_hash[h].append(p)
            except OSError:
                pass

    dup_groups   = {h: ps for h, ps in by_hash.items() if len(ps) > 1}
    total_dups   = sum(len(ps) - 1 for ps in dup_groups.values())
    total_bytes  = sum(ps[0].stat().st_size * (len(ps) - 1) for ps in dup_groups.values())

    log(f"קבצים סרוקים  : {sum(len(ps) for ps in by_size.values())}")
    log(f"קבוצות כפולות : {len(dup_groups)} (SHA256)")
    log(f"כפילויות לניקוי: {total_dups}")
    log(f"מקום לשחרור   : {total_bytes / 1024 / 1024:.1f} MB")
    log("")

    if total_dups == 0:
        log("אין כפילויות — לא נדרש ניקוי.")
        log("=" * 60)
        return

    ok_count   = 0
    skip_count = 0
    freed      = 0

    for h, paths in sorted(dup_groups.items(), key=lambda x: -(len(x[1]) - 1)):
        canon = paths[0]          # קנוני = ראשון אלפביתית
        aliases = paths[1:]       # כפילויות
        try:
            sz = canon.stat().st_size
        except OSError:
            sz = 0
        for alias in aliases:
            # SHA256 match guarantees identical content — safe to link
            if dry_run:
                log(f"  DRY   {alias.name:30s} → {canon.name}  ({sz/1024:.0f} KB)")
                ok_count += 1
                freed    += sz
                continue

            try:
                alias.unlink()
                os.link(str(canon), str(alias))   # Hard link
                ok_count += 1
                freed    += sz
            except OSError as e:
                log(f"  FAIL  {alias.name}: {e}")
                skip_count += 1

        # התקדמות ב-25% מהקבוצות
        done = ok_count + skip_count
        if done > 0 and done % max(1, total_dups // 4) < len(aliases):
            pct = done * 100 // total_dups
            log(f"  -- {pct}% ({done}/{total_dups})")

    log("")
    log("=" * 60)
    if dry_run:
        log(f"DRY RUN: {ok_count} כפילויות נמצאו")
        log(f"מקום שישוחרר: {freed / 1024 / 1024:.1f} MB")
        log("הרץ ללא --dry-run להחיל.")
    else:
        log(f"Dedup הושלם: {ok_count} Hard Links נוצרו, {skip_count} דולגו")
        log(f"מקום שוחרר : {freed / 1024 / 1024:.1f} MB")
    log("=" * 60)


# ══════════════════════════════════════════════════
# MAIN — שני שלבים ברצף
# ══════════════════════════════════════════════════
def main():
    global _STOP, OVERWRITE

    # ── ארגומנטים ─────────────────────────────────────────────
    parser = argparse.ArgumentParser(
        description="Perla Cookbook — הורדת תמונות + ניקוי כפילויות",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "דוגמאות:\n"
            "  python download_images.py               # הורדה + dedup\n"
            "  python download_images.py --skip-download  # רק dedup\n"
            "  python download_images.py --skip-dedup     # רק הורדה\n"
            "  python download_images.py --dry-run        # dedup — תצוגה בלבד\n"
            "  python download_images.py --overwrite      # הורד מחדש הכל\n"
        )
    )
    parser.add_argument("--skip-download", action="store_true",
                        help="דלג על שלב ההורדה, הרץ רק dedup")
    parser.add_argument("--skip-dedup",    action="store_true",
                        help="דלג על שלב ה-dedup, הרץ רק הורדה")
    parser.add_argument("--dry-run",       action="store_true",
                        help="Dedup — תצוגה מקדימה בלבד, אין מחיקות")
    parser.add_argument("--overwrite",     action="store_true",
                        help="הורד מחדש גם תמונות קיימות (OVERWRITE=True)")
    parser.add_argument("--no-proxy",      action="store_true",
                        help="התעלם מה-proxy — חיבור ישיר בלבד")
    args = parser.parse_args()

    if args.overwrite:
        OVERWRITE = True
    if args.no_proxy:
        global PROXY
        PROXY = None

    # ── אתחול לוג ────────────────────────────────────────────
    LOG_FILE.write_text("", encoding="utf-8")
    log("=" * 60)
    log("Perla Ben-Harrosh z\"l Cookbook — v3.0 (Download + Dedup)")
    log("=" * 60)
    mode_parts = []
    if not args.skip_download: mode_parts.append("Download")
    if not args.skip_dedup:    mode_parts.append("Dedup" + (" [dry]" if args.dry_run else ""))
    log(f"מצב: {' → '.join(mode_parts) or 'ללא פעולה'}")
    log(f"תמונות: {IMG_DIR}")
    log(f"לוג   : {LOG_FILE}")
    log("=" * 60)

    # ══════════════════════════════════════════════════════════
    # שלב 1 — הורדת תמונות
    # ══════════════════════════════════════════════════════════
    if not args.skip_download:
        recipes = parse_recipes()
        total   = len(recipes)
        already = sum(1 for r in recipes if (IMG_DIR / f"r-{r['id']}.jpg").exists())

        # בנה אינדקס גדלים מקבצים קיימים — למניעת כפילויות בזמן ריצה
        global _size_index
        _size_index = {}
        for _p in IMG_DIR.glob("r-*.jpg"):
            try:
                _sz = _p.stat().st_size
                if _sz > 0 and _sz not in _size_index:
                    _size_index[_sz] = _p
            except OSError:
                pass

        log("")
        log("שלב 1 — הורדת תמונות")
        log("-" * 60)
        log(f"מתכונים: {total} | קיימים: {already} | OVERWRITE={OVERWRITE}")
        log(f"מקורות: Hebrew → TheMealDB → Wikimedia → Openverse → Wikipedia → DDG → Flickr")
        log(f"Ctrl+C = יציאה מיידית")
        log("")

        # ── Quick connectivity check ─────────────────────────────
        log("בודק חיבור רשת...")
        _test_ok = False
        try:
            import urllib.request
            _req = urllib.request.Request(
                "https://commons.wikimedia.org/w/api.php?action=query&meta=siteinfo&format=json",
                headers={"User-Agent": "PerlaCookbook/1.0"})
            _resp = urllib.request.urlopen(_req, timeout=4)
            if _resp.status == 200:
                log("  direct: OK")
                _test_ok = True
        except Exception as _e:
            log(f"  direct: {type(_e).__name__}")
        if not _test_ok:
            log("  WARNING: אין חיבור לרשת — הסקריפט ינסה בכל זאת אבל רוב המקורות ייכשלו.")
            log("  TIP: בדוק proxy, VPN, או חיבור אינטרנט.")
        log("")

        ok_count = skip_count = fail_count = 0
        source_counts: dict = {}
        _dl_start = time.time()

        for i, recipe in enumerate(recipes):
            if _STOP:
                log("עצירה מבוקשת."); break

            rid   = recipe["id"]
            title = recipe["title"]
            cat   = recipe["cat"]
            dest  = IMG_DIR / f"r-{rid}.jpg"

            if dest.exists() and not OVERWRITE:
                skip_count += 1
                if skip_count <= 5 or skip_count % 100 == 0:
                    log(f"  >> [{i+1:4d}/{total}] skip [{rid}]")
                continue

            query = build_query(recipe)
            pct = (i + 1) * 100 // total
            log(f"  >> [{i+1:4d}/{total}] {pct:3d}% [{rid:8s}] {title[:28]:28s} q=\"{query[:30]}\"")

            saved  = False
            source = "?"
            t0 = time.time()

            sources = [
                ("hebrew",    lambda t=title, q=query: source_hebrew_first(t, q)),
                ("mealdb",    lambda q=query: source_mealdb(q)),
                ("wikimedia", lambda q=query: source_wikimedia_single(q)),
                ("openverse", lambda q=query: source_openverse(q)),
                ("wikipedia2",lambda q=query, rid=rid: source_unsplash_search(q)),
                ("ddg",       lambda q=query: source_foodimages_scrape(q)),
                ("flickr",    lambda q=query, rid=rid: source_loremflickr(q, rid)),
            ]

            for si, (src_name, src_fn) in enumerate(sources):
                if saved: break
                # Hard per-recipe timeout: 45s total across all sources
                if time.time() - t0 > 45:
                    log(f"     TIMEOUT — recipe took >45s, skipping remaining sources")
                    break
                t1 = time.time()
                try:
                    # Hard timeout per source: 10s max (prevents infinite hangs)
                    url = _call_with_timeout(src_fn, timeout_sec=10)
                    dt_find = time.time() - t1
                    if url:
                        dl_ok = _call_with_timeout(
                            lambda u=url, d=dest: download_and_save(u, d),
                            timeout_sec=10)
                        dt = time.time() - t1
                        if dl_ok:
                            saved  = True
                            source = src_name
                            source_counts[src_name] = source_counts.get(src_name, 0) + 1
                            log(f"     OK via {src_name} ({dt:.1f}s)")
                        elif dt > 2:
                            log(f"     {src_name}: download failed ({dt:.1f}s)")
                    elif dt_find > 2:
                        log(f"     {src_name}: no result ({dt_find:.1f}s)")
                except Exception as e:
                    dt = time.time() - t1
                    log(f"     {src_name} error ({dt:.1f}s): {type(e).__name__}")

            elapsed = time.time() - t0
            if saved:
                ok_count += 1
            else:
                fail_count += 1
                log(f"     FAIL — all sources exhausted ({elapsed:.0f}s)")

            # ── Progress every 25 recipes or 10% ──
            done = i + 1 - skip_count
            if done > 0 and (done % 25 == 0 or (pct % 10 == 0 and pct > 0)):
                avg_sec = (time.time() - _dl_start) / max(1, done)
                remaining = (total - skip_count - done) * avg_sec
                eta_min = remaining / 60
                src_summary = " ".join(f"{k}={v}" for k, v in sorted(source_counts.items()))
                log(f"\n  === {pct}% ({i+1}/{total}) ok={ok_count} fail={fail_count} | ETA {eta_min:.0f}min | {src_summary} ===\n")

            time.sleep(DELAY)

        log("")
        log("-" * 60)
        log(f"הורדה הושלמה: ok={ok_count}  skip={skip_count}  fail={fail_count}")
        src_str = "  ".join(
            f"{k}={source_counts.get(k,0)}"
            for k in ["hebrew","wikimedia","mealdb","wikipedia2","openverse","ddg"]
        )
        log(f"מקורות: {src_str}")
        log("-" * 60)

    # ══════════════════════════════════════════════════════════
    # שלב 2 — ניקוי כפילויות (dedup דינמי)
    # ══════════════════════════════════════════════════════════
    if not args.skip_dedup:
        log("")
        run_dedup(dry_run=args.dry_run)

    log("")
    log("=" * 60)
    log("הכל הושלם.")
    log(f"לוג: {LOG_FILE}")
    log("=" * 60)

if __name__ == "__main__":
    main()
