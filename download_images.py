#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Purpose (Hebrew):
# הורדת תמונות מתכונים מאתרי המקור — themediterraneandish.com,
# taste-of-maroc.com, myjewishlearning.com, jewishfoodsociety.org.
# לכל כתובת מקור, מחלץ את og:image (תמונה ראשית של הדף),
# שומר אותה כ-r-{id}.jpg לכל מתכון המשתמש בכתובת זו.
# אם לא נמצאת תמונה — הקובץ לא נוצר ואפשר להוסיף ידנית.
# ---------------------------------------------------------------

# ── Configuration ─────────────────────────────────────────────
DRY_RUN   = False             # True = simulate only, no downloads
PROXY_URL = "http://pac.gov.il:8080"

DELAY      = 4.0   # seconds between page fetches (rate limiting)
TIMEOUT    = 20    # HTTP timeout per request
MAX_RETRY  = 2     # retries on 429 / 5xx
RETRY_WAIT = 25.0  # seconds to wait after 429

# ── Imports ───────────────────────────────────────────────────
import os, sys, re, time, json, logging, urllib.request, urllib.error
from html.parser import HTMLParser
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
IMG    = os.path.join(BASE, "images")
LOGS   = os.path.join(BASE, "logs")
os.makedirs(IMG,  exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

# ── Logging ────────────────────────────────────────────────────
_log_file = os.path.join(LOGS, datetime.now().strftime("%d-%m-%Y_%H.%M") + ".log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(_log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("perla_images")

# ── Proxy ──────────────────────────────────────────────────────
if PROXY_URL:
    urllib.request.install_opener(
        urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": PROXY_URL, "https": PROXY_URL})
        )
    )
    log.info(f"Proxy: {PROXY_URL}")

# ── HTTP Headers ───────────────────────────────────────────────
PAGE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
IMG_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}

# ── SOURCE URL → RECIPE IDs MAPPING ───────────────────────────
# Built from the src: field in each recipe object in index.html / recipes.js.
# 130 unique source URLs covering all 1,014 recipes.
# Run  build_src_map.py  to regenerate if recipes change.


SRC_TO_IDS = {
    'https://www.jewishfoodsociety.org/recipes/dafina': ['c3', 'spn1', 'spe1', 'spv1', 'holfx3', 'me11', 'spx1'],
    'https://www.jewishfoodsociety.org/recipes/egg-salad': ['sle21'],
    'https://www.jewishfoodsociety.org/recipes/fava-bean-soup': ['s3', 'sn2', 'sn3', 'sne1', 'sane3', 'add3', 'add41', 'ex5', 'ex10', 'sw4', 'saxx4', 'saxx5', 'ku5', 'as20', 'ye25', 'sn22', 'sn29'],
    'https://www.jewishfoodsociety.org/recipes/matbucha': ['sa1', 'sa7', 'hx1', 'var2', 'holf4', 'slv1', 'slw4', 'ku28', 'tn16', 'is27', 'sle16'],
    'https://www.jewishfoodsociety.org/recipes/moroccan-beet-salad': ['sn7', 'san1', 'bu12'],
    'https://www.jewishfoodsociety.org/recipes/moroccan-chicken-with-preserved-lemons': ['c1', 'hn5', 'var4', 'add14', 'add16', 'fin11', 'fin26', 'cw1', 'chfx1', 'is15', 'ce12', 'ce13'],
    'https://www.jewishfoodsociety.org/recipes/moroccan-fish-balls': ['f3', 'fx2', 'fv2', 'fif6', 'tr3', 'fe12', 'fe16'],
    'https://www.jewishfoodsociety.org/recipes/moroccan-harira-soup': ['s1', 's8', 'hx2', 'sn9', 'var1', 'sf4', 'sw1'],
    'https://www.myjewishlearning.com/the-nosher/apple-cake-recipe/': ['as10', 'as28', 'is17'],
    'https://www.myjewishlearning.com/the-nosher/borscht-recipe/': ['as3'],
    'https://www.myjewishlearning.com/the-nosher/brik-recipe/': ['fne3', 'ex16', 'spv3', 'tn1'],
    'https://www.myjewishlearning.com/the-nosher/burekas-recipe/': ['hn14', 'spn2', 'holf2', 'is6', 'tn29', 'tr1', 'tr16', 'tr19', 'spx5'],
    'https://www.myjewishlearning.com/the-nosher/cheese-kugel-recipe/': ['as17'],
    'https://www.myjewishlearning.com/the-nosher/harira/': ['add2', 'ex14', 'sv1', 'sv4', 'slw1', 'saxx2', 'sn19', 'pe5', 'bu5', 'pe11', 'tr10', 'sn24'],
    'https://www.myjewishlearning.com/the-nosher/jachnun-recipe/': ['ye1', 'is19'],
    'https://www.myjewishlearning.com/the-nosher/kibbeh-recipe/': ['iq1', 'iq2', 'ku1'],
    'https://www.myjewishlearning.com/the-nosher/lahoh-recipe/': ['ye2'],
    'https://www.myjewishlearning.com/the-nosher/mofleta-recipe/': ['d1', 'rare2', 'holf5', 'spf5', 'ex36', 'hv4', 'spw1', 'as14'],
    'https://www.myjewishlearning.com/the-nosher/moroccan-chicken-bastilla/': ['hn15', 'ex34', 'fin13'],
    'https://www.myjewishlearning.com/the-nosher/moroccan-chopped-liver/': ['mn2', 'ex49', 'mef10', 'iq20', 'ye23', 'tn28', 'is14'],
    'https://www.myjewishlearning.com/the-nosher/moroccan-lamb-soup/': ['se5', 'ex1', 'sv3', 'ye3', 'ye15', 'bu8', 'sn25'],
    'https://www.myjewishlearning.com/the-nosher/rugelach-recipe/': ['as22'],
    'https://www.myjewishlearning.com/the-nosher/samsa-recipe/': ['hne4', 'bu2', 'iq15'],
    'https://www.myjewishlearning.com/the-nosher/schnitzel-recipe/': ['mef4', 'as21', 'pe21'],
    'https://www.myjewishlearning.com/the-nosher/the-history-of-gefilte-fish/': ['fin24', 'as2'],
    'https://www.myjewishlearning.com/the-nosher/the-ultimate-guide-to-cholent/': ['hv2', 'as1', 'is28'],
    'https://www.myjewishlearning.com/the-nosher/tzimmes-recipe/': ['as12'],
    'https://www.taste-of-maroc.com/beghrir-recipe/': ['hn11'],
    'https://www.taste-of-maroc.com/briouats-recipe/': ['hn13', 'spe4', 'spf1', 'ku24'],
    'https://www.taste-of-maroc.com/chebakia-recipe/': ['dx1'],
    'https://www.taste-of-maroc.com/ghriba-recipe/': ['d4', 'sp9', 'dn1', 'dn10', 'add19', 'add46', 'ex38', 'dv2', 'spv5', 'dn11', 'tn4', 'ku27', 'pe19', 'tn21', 'dn17', 'dn19'],
    'https://www.taste-of-maroc.com/harissa-recipe/': ['sau1', 'sau4', 'ye5', 'tn2'],
    'https://www.taste-of-maroc.com/kaab-el-ghzal-recipe/': ['dn2', 'hn19'],
    'https://www.taste-of-maroc.com/moroccan-beef-stew/': ['sp6', 'mn4', 'spne3', 'me1', 'mef3', 'add52', 'ex22', 'fin9', 'fin18', 'mv2', 'mw3', 'mw5', 'iq5', 'iq8', 'iq14', 'ku12', 'tn14', 'tr2', 'me15', 'me20'],
    'https://www.taste-of-maroc.com/moroccan-bread-recipe/': ['hn9', 'hn10', 'rare4', 'rare10', 'rare12', 'rer6', 'def5', 'add29', 'add54', 'add56', 'fin14', 'sv10', 'hv5', 'spnx4', 'hn20', 'spe10', 'ye8', 'ye16', 'ye21', 'bu19', 'tn8'],
    'https://www.taste-of-maroc.com/moroccan-carrot-salad/': ['sa4', 'sax3', 'san7', 'sle2', 'add22', 'ex8', 've20', 'sle19'],
    'https://www.taste-of-maroc.com/moroccan-carrots/': ['vx1', 'dne1', 'vef8', 'holf1', 'ex15', 'bu30'],
    'https://www.taste-of-maroc.com/moroccan-cookies/': ['dx2', 'dx3', 'dn7', 'spn3', 'spn5', 'dne3', 'hle4', 'hle5', 'dle3', 'def2', 'def3', 'add18', 'ex50', 'fin16', 'fin19', 'hw2', 'dw2', 'as6', 'iq18', 'as9', 'ye24', 'pe23', 'bu29', 'tn27', 'is30', 'dn15', 'dn16'],
    'https://www.taste-of-maroc.com/moroccan-couscous-recipe/': ['c5', 'hn16', 'hn17', 'cne4', 'var7', 'sf10', 'slf1', 'hv3', 'hw3', 'tn3', 'ye10', 'tn9'],
    'https://www.taste-of-maroc.com/moroccan-jam-recipe/': ['d6', 'dn4', 'dn5', 'dn6', 'dne4', 'dne5', 'hle2', 'dle4', 'dle5', 'rer7', 'def1', 'add17', 'add27', 'add55', 'fin17', 'dv3', 'dv4', 'dw3', 'def8', 'def10', 'dn12', 'dn14', 'bu7', 'ku22', 'as18', 'pe27', 'bu28', 'tr20', 'tr22'],
    'https://www.taste-of-maroc.com/moroccan-kefta-recipe/': ['m1', 'm2', 'sp2', 'mn5', 'mn7', 'var5', 'me3', 'add11', 'add13', 'fin10', 'mv3', 'mw4', 'me9', 'ku13', 'ku26', 'bu11', 'is18', 'tr15', 'spx3', 'me16'],
    'https://www.taste-of-maroc.com/moroccan-mint-tea-recipe/': ['d5', 'dx4', 'dne6', 'fin28', 'iq3', 'ye12'],
    'https://www.taste-of-maroc.com/moroccan-offal/': ['mx2', 'mx3', 'mx4', 'mx5', 'mx6', 'mn6', 'rare8', 'mv5', 'mw1', 'me17'],
    'https://www.taste-of-maroc.com/moroccan-pastries/': ['hx5', 'ex35', 'ex39', 'ex42', 'ex45', 'hw4', 'spw3', 'def6', 'is20'],
    'https://www.taste-of-maroc.com/moroccan-potato-salad/': ['sa10', 'san14', 'sle6'],
    'https://www.taste-of-maroc.com/moroccan-potatoes/': ['vx4', 've8', 'add21', 'spnx2', 've11', 've17'],
    'https://www.taste-of-maroc.com/moroccan-roast-chicken/': ['cx6', 'cne3', 'ce2', 'chf1', 'chf4', 'add44', 'ex30', 'cv3', 'chfx2', 'ce10', 'pe9', 'tr12', 'ce11', 'ce14'],
    'https://www.taste-of-maroc.com/moroccan-sardines/': ['f4', 'fx3', 'fne2', 'fif5', 'holfx2', 'fe13'],
    'https://www.taste-of-maroc.com/msemen-recipe/': ['hn12', 'rare9', 'add45'],
    'https://www.taste-of-maroc.com/preserved-lemons-recipe/': ['sau2'],
    'https://www.taste-of-maroc.com/sfenj-recipe/': ['d2', 'dv1'],
    'https://www.taste-of-maroc.com/zaalouk-recipe/': ['sa2'],
    'https://www.themediterraneandish.com/baba-ganoush-recipe/': ['sa5', 'sax2', 'sax5', 'sane1', 'sle9', 'add5', 'add31', 'ex6', 'ex9', 'slv8', 'bu27'],
    'https://www.themediterraneandish.com/baked-fish/': ['f5', 'fx4', 'fn2', 'spn4', 'fe1', 'fif2', 'add9', 'add51', 'fv1', 'fv3', 'fw4', 'fif8', 'fif9', 'as23', 'fe14', 'fe15'],
    'https://www.themediterraneandish.com/baked-sweet-potato/': ['san13'],
    'https://www.themediterraneandish.com/baked-zucchini/': ['v3', 'sax1', 'vef7', 'ku7'],
    'https://www.themediterraneandish.com/baklava-recipe/': ['dn8', 'iq22', 'tr28'],
    'https://www.themediterraneandish.com/bamia-recipe/': ['v2'],
    'https://www.themediterraneandish.com/best-hummus-recipe/': ['sa9', 'sx1', 'vn2', 'se8', 'slf5', 'vef5', 'add30', 'vv1', 'is2', 'ye11', 'tn12', 'tn24', 'is8', 'sn23'],
    'https://www.themediterraneandish.com/bread-rolls-recipe/': ['ku11', 'as24', 'as29', 'bu20', 'is22'],
    'https://www.themediterraneandish.com/chermoula-recipe/': ['f2', 'hn4', 'fn1', 'add33', 'chfx4', 'fe7'],
    'https://www.themediterraneandish.com/chicken-shawarma-recipe/': ['cv2', 'is5'],
    'https://www.themediterraneandish.com/chicken-soup-recipe/': ['s7', 'sn8', 'se4', 'se7', 'spe3', 'sv9', 'iq17', 'ye22', 'tr4', 'tr23', 'sn21', 'sn27', 'sn30'],
    'https://www.themediterraneandish.com/chocolate-cake-recipe/': ['dle1', 'add36', 'dw1', 'def9', 'is11', 'is25'],
    'https://www.themediterraneandish.com/creamy-mushroom-soup/': ['as27'],
    'https://www.themediterraneandish.com/crema-catalana-recipe/': ['fin20'],
    'https://www.themediterraneandish.com/dumpling-recipe/': ['ku3', 'bu4', 'as8', 'bu15', 'bu21', 'tr8'],
    'https://www.themediterraneandish.com/easy-seafood-paella-recipe/': ['sp8'],
    'https://www.themediterraneandish.com/falafel-recipe/': ['is1'],
    'https://www.themediterraneandish.com/french-onion-soup/': ['se1', 'se9', 'sf3', 'add50', 'ex11', 'saxx1', 'ku30'],
    'https://www.themediterraneandish.com/gazpacho-recipe/': ['sp3', 'spe6', 'is29'],
    'https://www.themediterraneandish.com/ghormeh-sabzi/': ['pe1'],
    'https://www.themediterraneandish.com/green-beans-recipe/': ['v5', 'san8', 'vne6', 'var6', 'slw3', 'vef12', 'ku15', 'ye29'],
    'https://www.themediterraneandish.com/grilled-fish/': ['fn3', 'fn6', 'fe4', 'add24', 'ex20', 'spv2', 'fe10', 'spe7'],
    'https://www.themediterraneandish.com/halva-recipe/': ['dn3', 'iq6', 'pe6', 'ku29', 'bu16', 'tr29'],
    'https://www.themediterraneandish.com/homemade-flatbread/': ['ex48', 'holfx5', 'bu3', 'bu6', 'ku18', 'ye14', 'ye26', 'ye27', 'ye30', 'pe25', 'bu14', 'tn23', 'is21'],
    'https://www.themediterraneandish.com/homemade-pita-bread/': ['is12'],
    'https://www.themediterraneandish.com/how-to-make-tahini-sauce/': ['san12', 'fin23', 'slv2', 'slv5', 'is13'],
    'https://www.themediterraneandish.com/israeli-salad-recipe/': ['is7'],
    'https://www.themediterraneandish.com/kuku-sabzi/': ['pe2'],
    'https://www.themediterraneandish.com/kunafa-recipe/': ['tr21'],
    'https://www.themediterraneandish.com/leek-recipe/': ['vn1', 'mef5', 'fin1', 'vv3', 'vw3'],
    'https://www.themediterraneandish.com/mansaf-recipe/': ['ye19', 'is9'],
    'https://www.themediterraneandish.com/mediterranean-baked-eggplant/': ['v1', 'vne2', 've3', 'rer3', 'vw1', 'pe16', 'pe24', 'pe28', 'tr13', 'tr26', 've13'],
    'https://www.themediterraneandish.com/mediterranean-fish-soup/': ['sne2', 'sf7'],
    'https://www.themediterraneandish.com/mediterranean-lentil-salad/': ['san5', 'sle4', 'add49', 'slv9', 'sle12'],
    'https://www.themediterraneandish.com/mediterranean-olives/': ['sau3', 'rare6', 'sle7', 'vef11', 'sle15'],
    'https://www.themediterraneandish.com/mediterranean-pasta/': ['sf6', 'add40', 'add42', 'sv7', 'sanx5', 'me6', 'as4', 'as13', 'as26', 'bu26', 'tn13', 'spx7'],
    'https://www.themediterraneandish.com/mediterranean-salad-recipe/': ['san4', 'san9', 'san16', 'sle3', 've5', 'slf2', 'ex47', 'fin3', 'fin4', 'slv4', 'slv6', 'slv10', 'spnx5', 'sle13', 've12', 'bu9', 'sle17', 'sle22'],
    'https://www.themediterraneandish.com/mediterranean-tuna-salad/': ['fe2', 'fw3'],
    'https://www.themediterraneandish.com/merguez-sausage/': ['mn3', 'ex24', 'fin15', 'spw2', 'iq9', 'tn20', 'me18'],
    'https://www.themediterraneandish.com/moroccan-barley-soup/': ['sx3', 'sn1', 'sn6', 'sne3', 'vne8', 'rare3', 'rer1', 'sf2', 'add1', 'ex2', 'ex46', 'fin21', 'sv5', 'sv6', 'sw5', 'vw4', 'saxx3', 'sn15', 'sn16', 'sn17', 'ku4', 'pe3', 'iq24', 'ku8', 'ku25', 'sn20', 'sn26'],
    'https://www.themediterraneandish.com/moroccan-beef-kebabs/': ['rer4', 'ex41', 'mef6', 'ku6', 'iq13', 'pe12', 'bu13', 'tn18', 'tr17'],
    'https://www.themediterraneandish.com/moroccan-chicken-recipe/': ['c2', 'h1', 'ce1', 'ce4', 'chf2', 'chf3', 'chf5', 'add26', 'add35', 'add53', 'ex27', 'cv1', 'cw4', 'chfx3', 'chfx5', 'ce7', 'ce9', 'as19', 'pe8', 'ce15'],
    'https://www.themediterraneandish.com/moroccan-chicken-stew/': ['c4', 'cx1', 'cne1', 'cne2', 'ex28', 'ex29', 'fin12', 'mv1', 'cv5', 'cw2', 'cw3', 'ku2'],
    'https://www.themediterraneandish.com/moroccan-coleslaw/': ['sa8', 'san10', 'sle10', 've1', 'vef2', 'add38', 'ex7', 'vv5', 've21'],
    'https://www.themediterraneandish.com/moroccan-dates/': ['d3', 'ex37', 'hw5', 'dw5', 'san19', 'iq29', 'bu25', 'dn18'],
    'https://www.themediterraneandish.com/moroccan-donuts/': ['dn9', 'ye6', 'as30', 'tn19', 'tr24'],
    'https://www.themediterraneandish.com/moroccan-fish-tagine/': ['f1', 'fx1', 'fx5', 'hx4', 'fn5', 'fne1', 'var3', 'fe6', 'rer5', 'fif1', 'fif3', 'fif4', 'holf3', 'add10', 'ex17', 'ex18', 'fin7', 'fin8', 'fv4', 'fv5', 'fw1', 'fw2', 'fw5', 'fif7', 'fif10', 'fe8', 'fe9', 'tn5', 'spx2', 'fe11'],
    'https://www.themediterraneandish.com/moroccan-lamb-stew/': ['m3', 'mx1', 'mx7', 'rn7', 'mne1', 'mne2', 'mne4', 'rare1', 'me2', 'mef1', 'mef2', 'add25', 'add43', 'fin25', 'mw2', 'mef7', 'mef8', 'holfx4', 'me7', 'me10', 'ye20', 'pe18', 'me12', 'me13', 'me14'],
    'https://www.themediterraneandish.com/moroccan-orange-cake/': ['dne2', 'dle2', 'def4', 'add28', 'add37', 'dv5', 'def7', 'spe9', 'as15', 'ye28', 'hn24'],
    'https://www.themediterraneandish.com/moroccan-pumpkin/': ['v4', 'vne1', 've2', 'slw2'],
    'https://www.themediterraneandish.com/moroccan-rice-pudding/': ['hle1', 'ex40', 'fin27', 'dw4', 'dn13', 'iq27', 'pe14', 'pe26', 'pe30', 'tn25', 'tn30', 'tr18', 'spx4'],
    'https://www.themediterraneandish.com/moroccan-rice/': ['sp5', 'hx3', 'spe5', 'ex3', 'ex43', 'spv4', 'spe8', 'ye4', 'iq10', 'iq21', 'iq28', 'ku21', 'ye17', 'pe10', 'pe17', 'pe29', 'bu24', 'is16', 'tr6', 'tr25', 'tr30'],
    'https://www.themediterraneandish.com/moroccan-shrimp/': ['fn4', 'fe3', 'fe5', 'add34', 'ex19'],
    'https://www.themediterraneandish.com/moroccan-tomato-soup/': ['s5', 'se10', 'iq25', 'sn28'],
    'https://www.themediterraneandish.com/moroccan-vegetable-soup/': ['s4', 'v6', 'sx2', 'sn4', 'sn11', 'san6', 'vn3', 'spne4', 'rare11', 'se3', 'sf1', 'sf5', 'sf8', 'sf9', 'spf2', 'add4', 'add39', 'fin2', 'fin29', 'sv2', 'sv8', 'iq11', 'ku17', 'ku23', 'as25', 'ye18', 'bu10', 'bu22'],
    'https://www.themediterraneandish.com/moroccan-vegetable-tagine-recipe/': ['h3', 'hn1', 'hn2', 'hn3', 'hn6', 'hn7', 'hn8', 'mne3', 'hne1', 'rare7', 'vef1', 'ex25', 'ex31', 'ex32', 've9', 'me8', 'hn18', 'tr11', 've18', 'me19'],
    'https://www.themediterraneandish.com/mujadara-lentils-and-rice/': ['is4'],
    'https://www.themediterraneandish.com/one-pot-mediterranean-chicken/': ['cx2', 'cx3', 'cx4', 'cx5', 'ce3', 'add15', 'is10'],
    'https://www.themediterraneandish.com/pickled-vegetables/': ['vn8', 've7', 'add47', 'fin30', 'spw5', 'iq16', 'iq26', 'as16', 'pe13', 'tn22', 'sle23'],
    'https://www.themediterraneandish.com/plov-recipe/': ['bu1', 'bu23'],
    'https://www.themediterraneandish.com/polenta-recipe/': ['as7'],
    'https://www.themediterraneandish.com/pumpkin-soup/': ['s6', 'sn5', 'se6', 'add48', 'sw3'],
    'https://www.themediterraneandish.com/red-lentil-soup-recipe/': ['s2', 'sn10', 'ex4', 'sw2', 'sn18', 'iq30', 'pe7', 'pe15', 'tr14', 'hn22'],
    'https://www.themediterraneandish.com/roast-leg-of-lamb-recipe/': ['mn1', 'hle3', 'ex23', 'ex33', 'mv4', 'hw1', 'ye9', 'bu18'],
    'https://www.themediterraneandish.com/roasted-cauliflower-recipe/': ['san2', 'rare5', 'sle1', 've4', 'add8', 'add32', 've10', 've14'],
    'https://www.themediterraneandish.com/roasted-chicken/': ['hne3', 'ce5', 'ex26', 'cv4', 'cw5', 'ce6', 'ce8'],
    'https://www.themediterraneandish.com/roasted-garlic-recipe/': ['ve6'],
    'https://www.themediterraneandish.com/roasted-red-peppers/': ['sa3', 'sa6', 'sax4', 'sane4', 'fin5', 'tn10', 'tn15', 'is23', 'sle20'],
    'https://www.themediterraneandish.com/sauteed-mushrooms/': ['vne7', 'ex12', 'vef10', 'ku20'],
    'https://www.themediterraneandish.com/sauteed-spinach-recipe/': ['vx3', 'san15', 'se2', 'spe2', 'add23', 'vef9', 'is26'],
    'https://www.themediterraneandish.com/shakshuka-recipe/': ['sp7', 'san11', 'spne1', 'sle8', 'rer2', 'slf3', 'add20', 'ex13', 'hv1', 'vw2', 'holfx1', 'spnx3', 'as5', 'ye7', 'tn6', 'tn7', 'is3', 'ku16', 'ye13', 'tn11', 'tn17', 'tn26', 'is24', 'tr5', 'hn21', 've15', 'hn23', 'spx6'],
    'https://www.themediterraneandish.com/spanish-sofrito/': ['sp1', 'spw4'],
    'https://www.themediterraneandish.com/stuffed-grape-leaves-recipe/': ['fin6', 'iq4', 'pe4', 'ku9', 'tr27'],
    'https://www.themediterraneandish.com/stuffed-peppers/': ['h2', 'sp4', 'vn4', 'vn5', 'vn6', 'vne3', 'vne4', 'vne5', 'hne2', 'me5', 'spf3', 'add7', 'ex21', 'ex44', 'vv2', 'vv4', 'mef9', 'iq19', 'as11', 'bu17', 'tr9', 've19'],
    'https://www.themediterraneandish.com/tabbouleh-recipe/': ['san17', 'slf4', 'add6', 'slv3', 'slv7', 'slw5', 'sanx6', 'sanx7', 'san18', 'sle11', 'sle14', 'iq7', 'iq23'],
    'https://www.themediterraneandish.com/tzatziki-sauce-recipe/': ['vef6', 'fin22', 'spnx1', 'iq12', 'ku10', 'ku14', 'ku19', 'pe20', 'pe22', 'tr7'],
    'https://www.themediterraneandish.com/white-bean-recipe/': ['vx2', 'san3', 'vn7', 'mn8', 'sane2', 'spne2', 'sle5', 'me4', 'vef3', 'vef4', 'spf4', 'add12', 'vw5', 've16'],
    'https://www.themediterraneandish.com/white-bean-salad/': ['sle18'],
}


# ── og:image extractor ─────────────────────────────────────────
class OGParser(HTMLParser):
    """Extract og:image and twitter:image from HTML <meta> tags."""
    def __init__(self):
        super().__init__()
        self.og_image = None
        self.done = False

    def handle_starttag(self, tag, attrs):
        if self.done or tag != "meta":
            return
        d = dict(attrs)
        prop = d.get("property","") or d.get("name","")
        if prop in ("og:image","og:image:url","twitter:image"):
            url = d.get("content","").strip()
            if url and url.startswith("http"):
                self.og_image = url
                self.done = True


def extract_og_image(page_url):
    """Fetch page HTML and return og:image URL, or None."""
    try:
        req = urllib.request.Request(page_url, headers=PAGE_HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            # Read only first 60KB (meta tags are near top)
            chunk = resp.read(65536).decode("utf-8", errors="replace")
        parser = OGParser()
        parser.feed(chunk)
        return parser.og_image
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise
        log.warning(f"  HTTP {e.code} fetching page: {page_url}")
        return None
    except Exception as e:
        log.warning(f"  Page fetch error: {e}")
        return None


# ── Image downloader ───────────────────────────────────────────
def download_img(img_url, dest_path):
    """Download img_url → dest_path. Returns True on success."""
    try:
        req = urllib.request.Request(img_url, headers=IMG_HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
        if len(data) < 4000:
            log.warning(f"  Image too small ({len(data)} B), skipping")
            return False
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        log.warning(f"  Image download error: {e}")
        return False


# ── progress ───────────────────────────────────────────────────
def report_progress(i, total, ok, skip, fail):
    pct = int(i / total * 100)
    ms  = (pct // 10) * 10
    if ms > 0 and ms not in report_progress._done:
        report_progress._done.add(ms)
        log.info(f"─── {ms:3d}% ───  {i}/{total}  ok={ok}  skip={skip}  fail={fail}")
report_progress._done = set()


# ── Main ───────────────────────────────────────────────────────
def main():
    total_urls   = len(SRC_TO_IDS)
    total_recipes = sum(len(ids) for ids in SRC_TO_IDS.values())

    log.info("=" * 60)
    log.info("Perla Cookbook — Recipe Image Downloader")
    log.info(f"Mode    : {'DRY-RUN' if DRY_RUN else 'LIVE'}")
    log.info(f"Source  : og:image from recipe source pages")
    log.info(f"URLs    : {total_urls} unique source pages")
    log.info(f"Recipes : {total_recipes} total (many share same source URL)")
    log.info(f"Output  : images/r-{{id}}.jpg per recipe")
    log.info(f"No img  : no file created → manual upload enabled in site")
    log.info(f"Delay   : {DELAY}s between fetches | {RETRY_WAIT}s on 429")
    log.info(f"Log     : {_log_file}")
    log.info("=" * 60)

    ok = fail = skip = url_ok = url_fail = 0

    for i, (src_url, recipe_ids) in enumerate(SRC_TO_IDS.items(), 1):
        log.info(f"\n[{i:3d}/{total_urls}] {src_url}")
        log.info(f"  Recipes: {recipe_ids[:5]}{'...' if len(recipe_ids)>5 else ''} ({len(recipe_ids)} total)")

        # Check if ALL recipe images for this URL already exist
        all_exist = all(
            os.path.exists(os.path.join(IMG, f"r-{rid}.jpg")) and
            os.path.getsize(os.path.join(IMG, f"r-{rid}.jpg")) >= 4000
            for rid in recipe_ids
        )
        if all_exist:
            log.info(f"  SKIP  all {len(recipe_ids)} recipe images already exist")
            skip += len(recipe_ids)
            report_progress(i, total_urls, ok, skip, fail)
            continue

        if DRY_RUN:
            log.info(f"  DRY-RUN  would fetch og:image and save {len(recipe_ids)} files")
            ok += len(recipe_ids)
            report_progress(i, total_urls, ok, skip, fail)
            continue

        # Fetch og:image with retry on 429
        og_img_url = None
        for attempt in range(1, MAX_RETRY + 1):
            try:
                og_img_url = extract_og_image(src_url)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < MAX_RETRY:
                    log.warning(f"  429 rate-limit — waiting {RETRY_WAIT}s (attempt {attempt}/{MAX_RETRY})")
                    time.sleep(RETRY_WAIT)
                else:
                    log.error(f"  FAIL page fetch HTTP {e.code}")
                    break

        if not og_img_url:
            log.warning(f"  No og:image found — recipes will show no image (manual upload possible)")
            fail += len(recipe_ids)
            report_progress(i, total_urls, ok, skip, fail)
            time.sleep(DELAY)
            continue

        log.info(f"  og:image: {og_img_url[:80]}")

        # Download image once, then copy to all recipe IDs for this URL
        first_dest = None
        downloaded = False
        for rid in recipe_ids:
            dest = os.path.join(IMG, f"r-{rid}.jpg")
            if os.path.exists(dest) and os.path.getsize(dest) >= 4000:
                log.info(f"    SKIP  r-{rid}.jpg already exists")
                skip += 1
                continue

            if not downloaded:
                # Download the image for the first recipe
                success = download_img(og_img_url, dest)
                if success:
                    downloaded = True
                    first_dest = dest
                    sz = os.path.getsize(dest) // 1024
                    log.info(f"    OK    r-{rid}.jpg ({sz} KB)")
                    ok += 1
                else:
                    log.error(f"    FAIL  r-{rid}.jpg")
                    fail += 1
            else:
                # Copy from first downloaded file
                import shutil
                shutil.copy2(first_dest, dest)
                log.info(f"    COPY  r-{rid}.jpg (from r-{recipe_ids[0]}.jpg)")
                ok += 1

        report_progress(i, total_urls, ok, skip, fail)
        time.sleep(DELAY)

    log.info("\n" + "=" * 60)
    log.info(f"DONE   ok={ok}  skip={skip}  fail={fail}  total={total_recipes}")
    if fail:
        log.info(f"  {fail} recipes have no image — they show nothing in the site.")
        log.info(f"  Use the 'הוסף תמונה' button in each recipe to add manually.")
    log.info(f"Log: {_log_file}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
