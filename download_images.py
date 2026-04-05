#!/usr/bin/env python3
"""
download_images.py — ספר הבישול של פרלה בן ארוש ז"ל
מוריד תמונה ייחודית לכל 1,014 מתכונים.
אסטרטגיה: 1) Wikimedia Commons  2) og:image מקור  3) loremflickr fallback
הפעלה: python download_images.py
"""
import os,re,sys,json,time,threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("pip install requests"); sys.exit(1)

# ── Config ────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
DATA_SRC   = SCRIPT_DIR/"data.js" if (SCRIPT_DIR/"data.js").exists() else SCRIPT_DIR/"index.html"
IMG_DIR    = SCRIPT_DIR/"images"
LOG_FILE   = SCRIPT_DIR/"download_images.log"
PROXY      = None   # 'http://pac.gov.il:8080'
DELAY      = 1.0
OVERWRITE  = False
WORKERS    = 3
TIMEOUT    = 20

IMG_DIR.mkdir(exist_ok=True)
lock   = threading.Lock()
logs   = []
stats  = {"ok":0,"skip":0,"fail":0}

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    with lock: logs.append(line)
    print(line, flush=True)

# ── Hebrew → Wikimedia search terms ──────────────────────────
WIKI_MAP = {
    "חרירה":"Harira","ביסארה":"Bissara","עדשים":"Lentil soup",
    "בורשט":"Borscht","מטבוחה":"Matbucha","זעלוק":"Zaalouk",
    "טבולה":"Tabbouleh","חומוס":"Hummus","במיה":"Okra stew",
    "כרובית":"Cauliflower roasted","קישוא ממולא":"Stuffed courgette",
    "קציצות":"Kefta moroccan","גפילטע פיש":"Gefilte fish",
    "צ׳ולנט":"Cholent","חמין":"Dafina moroccan",
    "קובה סלק":"Kibbeh beetroot","קובה":"Kibbeh","דולמה":"Dolma",
    "עוף לימון":"Chicken preserved lemons","חריימה":"Chraime",
    "סרדינים":"Sardines chermoula","מופלטה":"Mofletah",
    "כעב הגזאל":"Kaab el ghzal","שלדה":"Chebakia",
    "ספינג׳":"Sfenj moroccan","בריואט":"Briouat almond",
    "חרוסת":"Charoset","תה נענע":"Moroccan mint tea",
    "גספאצ׳ו":"Gazpacho","פאייה":"Paella","אמפנדה":"Empanada",
    "אלבונדיגס":"Albondigas","בורקס":"Borek pastry",
    "מסגוף":"Masgouf grilled fish","גורמה סבזי":"Ghormeh sabzi",
    "קוקו סבזי":"Kuku sabzi","פסנג׳ן":"Fesenjan",
    "פלאפל":"Falafel","שקשוקה":"Shakshuka","מג׳דרה":"Mujaddara",
    "שוורמה":"Shawarma","סביח":"Sabich","ג׳חנון":"Jachnun",
    "לחוח":"Lahoh","זחוק":"Zhug yemeni","הילבה":"Hilbeh",
}

CAT_KW = {
    "soups":"moroccan,soup,bowl","salads":"moroccan,salad,mezze",
    "veg":"moroccan,vegetable,stew","meat":"moroccan,meat,tagine",
    "chick":"moroccan,chicken,tagine","fish":"moroccan,fish,spiced",
    "hol":"moroccan,holiday,festive","des":"moroccan,pastry,sweets",
    "span":"sephardic,spanish,food","iraq":"iraqi,jewish,food",
    "kurd":"kurdish,jewish,food","ashk":"ashkenazi,jewish,food",
    "yem":"yemeni,jewish,food","pers":"persian,jewish,food",
    "buk":"bukharian,jewish,rice","tun":"tunisian,jewish,food",
    "isr":"israeli,food,modern","turk":"turkish,jewish,food",
}

def make_sess():
    s = requests.Session()
    if PROXY: s.proxies={"http":PROXY,"https":PROXY}
    s.mount("https://",HTTPAdapter(max_retries=Retry(3,backoff_factor=1,status_forcelist=[429,500,502,503])))
    s.headers["User-Agent"]="PerlaCookbook/1.0"
    return s

def parse_recipes():
    src = DATA_SRC.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"id:'([^']+)',\s*cat:'([^']+)'[^;{]*?title:'([^']+)'[^;{]*?(?:src:'([^']*)')?", src, re.DOTALL):
        out.append({"id":m.group(1),"cat":m.group(2),"title":m.group(3),"src":m.group(4) or ""})
    return out

def wikimedia(sess, query):
    try:
        r = sess.get("https://commons.wikimedia.org/w/api.php",
            params={"action":"query","list":"search","srsearch":f"{query} food",
                    "srnamespace":6,"srlimit":5,"format":"json"},timeout=TIMEOUT)
        for res in r.json().get("query",{}).get("search",[]):
            t = res.get("title","")
            if t.startswith("File:") and any(e in t.lower() for e in [".jpg",".jpeg",".png"]):
                r2 = sess.get("https://commons.wikimedia.org/w/api.php",
                    params={"action":"query","titles":t,"prop":"imageinfo",
                            "iiprop":"url|size","iiurlwidth":600,"format":"json"},timeout=TIMEOUT)
                for p in r2.json().get("query",{}).get("pages",{}).values():
                    ii = p.get("imageinfo",[{}])[0]
                    url = ii.get("thumburl") or ii.get("url","")
                    if url and ii.get("size",0) < 4*1024*1024: return url
    except: pass
    return None

def og_img(sess, src_url):
    try:
        r = sess.get(src_url, timeout=TIMEOUT, stream=True)
        html = r.raw.read(32768).decode("utf-8","ignore")
        m = re.search(r'og:image.*?content=["\'](https?://[^"\']+)', html)
        if not m: m = re.search(r'content=["\'](https?://[^"\']+).*?og:image', html)
        return m.group(1) if m else None
    except: return None

def download_one(sess, recipe, idx):
    rid  = recipe["id"]
    dest = IMG_DIR/f"r-{rid}.jpg"
    if dest.exists() and not OVERWRITE:
        with lock: stats["skip"]+=1; return

    title = recipe["title"]
    img_url = None

    # 1. Wikimedia
    for he,en in WIKI_MAP.items():
        if he in title:
            img_url = wikimedia(sess, en)
            if img_url: log(f"  Wikimedia [{rid}] {en}"); break

    # 2. og:image
    if not img_url and recipe.get("src"):
        img_url = og_img(sess, recipe["src"])
        if img_url: log(f"  og:image  [{rid}]")

    # 3. loremflickr
    if not img_url:
        kw = CAT_KW.get(recipe["cat"],"moroccan,food")
        img_url = f"https://loremflickr.com/600/400/{kw}?lock={20000+idx}"
        log(f"  flickr    [{rid}] {recipe['cat']}")

    try:
        r = sess.get(img_url, timeout=TIMEOUT, stream=True)
        r.raise_for_status()
        data = b"".join(r.iter_content(8192))
        if len(data) > 4*1024*1024: raise ValueError("too large")
        dest.write_bytes(data)
        with lock: stats["ok"]+=1
    except Exception as e:
        with lock: stats["fail"]+=1
        log(f"  FAIL [{rid}]: {e}")
    time.sleep(DELAY)

def main():
    recipes = parse_recipes()
    total = len(recipes)
    log(f"=== פרלה בן ארוש ז\"ל — הורדת תמונות ===")
    log(f"סה\"כ מתכונים: {total} | תיקייה: {IMG_DIR}")
    log(f"Proxy: {PROXY or 'none'} | Workers: {WORKERS} | Delay: {DELAY}s")

    sessions = [make_sess() for _ in range(WORKERS)]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(download_one, sessions[i%WORKERS], r, i): r["id"]
                   for i, r in enumerate(recipes)}
        done = 0
        milestones = set(range(10,101,10))
        for f in as_completed(futures):
            done += 1
            pct = done*100//total
            if pct in milestones:
                milestones.discard(pct)
                log(f"  {pct}% ({done}/{total}) ok={stats['ok']} skip={stats['skip']} fail={stats['fail']}")

    log(f"\nסיום — הורד:{stats['ok']}  קיים:{stats['skip']}  שגיאה:{stats['fail']}")
    LOG_FILE.write_text("\n".join(logs), encoding="utf-8")

if __name__=="__main__":
    main()
