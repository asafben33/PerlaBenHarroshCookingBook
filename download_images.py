#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Purpose (Hebrew per project convention):
# הורדת תמונות אוכל רלוונטיות לאתר ספר הבישול של פרלה בן ארוש זל.
# כל תמונה מתאימה לסוג האוכל של המתכון:
# חרירה -> תמונת חרירה, קוסקוס -> תמונת קוסקוס, טאג׳ין -> טאג׳ין.
# מקור: Wikipedia REST API — תמונות אמיתיות, ללא תשלום.
#
# Run : python download_images.py
# Test: set DRY_RUN = True to simulate without downloading
# ---------------------------------------------------------------

# ─────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────
DRY_RUN   = False                       # Set True to simulate without writing to disk
PROXY_URL = "http://pac.gov.il:8080"   # Set "" to disable proxy

# ─────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────
import os
import sys
import json
import time
import shutil
import logging
import re
import urllib.request
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
LOGS_DIR   = os.path.join(BASE_DIR, "logs")

# ─────────────────────────────────────────────────────────────────
#  LOG FILE — created before execution starts
#  Format: DD-MM-YYYY_HH.MM.log
# ─────────────────────────────────────────────────────────────────
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR,   exist_ok=True)

_log_filename = datetime.now().strftime("%d-%m-%Y_%H.%M") + ".log"
_log_path     = os.path.join(LOGS_DIR, _log_filename)

logging.basicConfig(
    level    = logging.INFO,
    format   = "%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt  = "%H:%M:%S",
    handlers = [
        logging.FileHandler(_log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("perla_images")

# ─────────────────────────────────────────────────────────────────
#  PROXY — installed globally before any HTTP call
# ─────────────────────────────────────────────────────────────────
if PROXY_URL:
    _proxy_handler = urllib.request.ProxyHandler({
        "http" : PROXY_URL,
        "https": PROXY_URL,
    })
    urllib.request.install_opener(
        urllib.request.build_opener(_proxy_handler)
    )
    log.info(f"Proxy configured: {PROXY_URL}")

# ─────────────────────────────────────────────────────────────────
#  HTTP HEADERS
# ─────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent"      : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
    "Accept"          : "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language" : "en-US,en;q=0.9",
    "Accept-Encoding" : "gzip, deflate, br",
    "Connection"      : "keep-alive",
}

WIKI_HEADERS = {
    "User-Agent" : "PerlaCookbook/1.0 (personal cookbook image downloader)",
    "Accept"     : "application/json",
}

DELAY_BETWEEN_REQUESTS = 2.0    # increased to avoid Wikimedia 429
RETRY_WAIT_ON_429      = 8.0    # wait before retrying after 429
MAX_RETRIES            = 3      # max download retries per file
MIN_FILE_SIZE_BYTES    = 5_000

# ─────────────────────────────────────────────────────────────────
#  WIKIPEDIA ARTICLE MAPPING
#  Every G key -> Wikipedia article title for that food type.
#  The script resolves the article thumbnail via Wikipedia REST API.
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
#  RECIPE -> G KEY MAPPING
#  Derived from index.html. Recipe images are copies of their
#  category image, so every recipe shows the correct food photo.
# ─────────────────────────────────────────────────────────────────
GKEY_RECIPES = {
    "almond_cookie": ["d4", "sp9", "dn1", "dn10", "add19", "add46", "ex38", "dv2", "spv5", "dn11", "tn4", "ku27", "pe19", "tn21", "dn17", "dn19"],
    "apple_cake": ["as10", "as28", "is17"],
    "baklava": ["dn8", "iq22", "tr28"],
    "bamia": ["v2"],
    "bean_salad": ["sle18"],
    "bean_soup": ["s3", "sn2", "sn3", "sne1", "sane3", "add3", "add41", "ex5", "ex10", "sw4", "saxx4", "saxx5", "ku5", "as20", "ye25", "sn22", "sn29"],
    "beet_salad": ["sn7", "san1", "bu12"],
    "beghrir": ["hn11"],
    "borscht": ["as3"],
    "bourekas": ["hn14", "spn2", "holf2", "is6", "tn29", "tr1", "tr16", "tr19", "spx5"],
    "bread_rolls": ["ku11", "as24", "as29", "bu20", "is22"],
    "brik": ["fne3", "ex16", "spv3", "tn1"],
    "briouats": ["hn13", "spe4", "spf1", "ku24"],
    "cabbage_salad": ["sa8", "san10", "sle10", "ve1", "vef2", "add38", "ex7", "vv5", "ve21"],
    "cake": ["dne2", "dle2", "def4", "add28", "add37", "dv5", "def7", "spe9", "as15", "ye28", "hn24"],
    "carrot_dish": ["vx1", "dne1", "vef8", "holf1", "ex15", "bu30"],
    "carrot_salad": ["sa4", "sax3", "san7", "sle2", "add22", "ex8", "ve20", "sle19"],
    "catalan_cream": ["fin20"],
    "cauliflower_dish": ["ve4", "add8", "add32", "ve10", "ve14"],
    "cauliflower_salad": ["san2", "rare5", "sle1"],
    "cheese_kugel": ["as17"],
    "chermoula_fish": ["f2", "hn4", "fn1", "add33", "chfx4", "fe7"],
    "chicken_fruit": ["c2", "h1", "ce1", "ce4", "chf2", "chf3", "chf5", "add26", "add35", "add53", "ex27", "cv1", "cw4", "chfx3", "chfx5", "ce7", "ce9", "as19", "pe8", "ce15"],
    "chicken_lemon": ["c1", "hn5", "var4", "add14", "add16", "fin11", "fin26", "cw1", "chfx1", "is15", "ce12", "ce13"],
    "chicken_roast": ["hne3", "ce5", "ex26", "cv4", "cw5", "ce6", "ce8"],
    "chicken_soup": ["s7", "sn8", "se4", "se7", "spe3", "sv9", "iq17", "ye22", "tr4", "tr23", "sn21", "sn27", "sn30"],
    "chicken_spiced": ["cx6", "cne3", "ce2", "chf1", "chf4", "add44", "ex30", "cv3", "chfx2", "ce10", "pe9", "tr12", "ce11", "ce14"],
    "chicken_stew": ["c4", "cx1", "cne1", "cne2", "ex28", "ex29", "fin12", "mv1", "cv5", "cw2", "cw3", "ku2"],
    "chicken_vegetables": ["cx2", "cx3", "cx4", "cx5", "ce3", "add15", "is10"],
    "chocolate_cake": ["dle1", "add36", "dw1", "def9", "is11", "is25"],
    "cholent": ["hv2", "as1", "is28"],
    "cookies": ["dx2", "dx3", "dn7", "spn3", "spn5", "dne3", "hle4", "hle5", "dle3", "def2", "def3", "add18", "ex50", "fin16", "fin19", "hw2", "dw2", "as6", "iq18", "as9", "ye24", "pe23", "bu29", "tn27", "is30", "dn15", "dn16"],
    "couscous": ["c5", "hn16", "hn17", "cne4", "var7", "sf10", "slf1", "hv3", "hw3", "tn3", "ye10", "tn9"],
    "dafina": ["c3", "spn1", "spe1", "spv1", "holfx3", "me11", "spx1"],
    "dates": ["d3", "ex37", "hw5", "dw5", "san19", "iq29", "bu25", "dn18"],
    "dessert_pastry": ["hx5", "ex35", "ex39", "ex42", "ex45", "hw4", "spw3", "def6", "is20"],
    "dolma": ["fin6", "iq4", "pe4", "ku9", "tr27"],
    "donut": ["dn9", "ye6", "as30", "tn19", "tr24"],
    "dumpling": ["ku3", "bu4", "as8", "bu15", "bu21", "tr8"],
    "egg_salad": ["sle21"],
    "eggplant_dish": ["v1", "vne2", "ve3", "rer3", "vw1", "pe16", "pe24", "pe28", "tr13", "tr26", "ve13"],
    "eggplant_salad": ["sa5", "sax2", "sax5", "sane1", "sle9", "add5", "add31", "ex6", "ex9", "slv8", "bu27"],
    "falafel": ["is1"],
    "fish_baked": ["f5", "fx4", "fn2", "spn4", "fe1", "fif2", "add9", "add51", "fv1", "fv3", "fw4", "fif8", "fif9", "as23", "fe14", "fe15"],
    "fish_balls": ["f3", "fx2", "fv2", "fif6", "tr3", "fe12", "fe16"],
    "fish_grilled": ["fn3", "fn6", "fe4", "add24", "ex20", "spv2", "fe10", "spe7"],
    "fish_soup": ["sne2", "sf7"],
    "fish_tagine": ["f1", "fx1", "fx5", "hx4", "fn5", "fne1", "var3", "fe6", "rer5", "fif1", "fif3", "fif4", "holf3", "add10", "ex17", "ex18", "fin7", "fin8", "fv4", "fv5", "fw1", "fw2", "fw5", "fif7", "fif10", "fe8", "fe9", "tn5", "spx2", "fe11"],
    "flatbread": ["ex48", "holfx5", "bu3", "bu6", "ku18", "ye14", "ye26", "ye27", "ye30", "pe25", "bu14", "tn23", "is21"],
    "garlic_confit": ["ve6"],
    "gazelle_horns": ["dn2", "hn19"],
    "gazpacho": ["sp3", "spe6", "is29"],
    "gefilte": ["fin24", "as2"],
    "ghormeh": ["pe1"],
    "grain_soup": ["sx3", "sn1", "sn6", "sne3", "vne8", "rare3", "rer1", "sf2", "add1", "ex2", "ex46", "fin21", "sv5", "sv6", "sw5", "vw4", "saxx3", "sn15", "sn16", "sn17", "ku4", "pe3", "iq24", "ku8", "ku25", "sn20", "sn26"],
    "green_beans": ["v5", "san8", "vne6", "var6", "slw3", "vef12", "ku15", "ye29"],
    "green_salad": ["san4", "san9", "san16", "sle3", "ve5", "slf2", "ex47", "fin3", "fin4", "slv4", "slv6", "slv10", "spnx5", "sle13", "ve12", "bu9", "sle17", "sle22"],
    "halva": ["dn3", "iq6", "pe6", "ku29", "bu16", "tr29"],
    "harira": ["s1", "s8", "hx2", "sn9", "var1", "sf4", "sw1"],
    "harissa": ["sau1", "sau4", "ye5", "tn2"],
    "herb_soup": ["add2", "ex14", "sv1", "sv4", "slw1", "saxx2", "sn19", "pe5", "bu5", "pe11", "tr10", "sn24"],
    "hummus": ["sa9", "sx1", "vn2", "se8", "slf5", "vef5", "add30", "vv1", "is2", "ye11", "tn12", "tn24", "is8", "sn23"],
    "jachnun": ["ye1", "is19"],
    "jam": ["d6", "dn4", "dn5", "dn6", "dne4", "dne5", "hle2", "dle4", "dle5", "rer7", "def1", "add17", "add27", "add55", "fin17", "dv3", "dv4", "dw3", "def8", "def10", "dn12", "dn14", "bu7", "ku22", "as18", "pe27", "bu28", "tr20", "tr22"],
    "kadaif": ["tr21"],
    "kebab": ["rer4", "ex41", "mef6", "ku6", "iq13", "pe12", "bu13", "tn18", "tr17"],
    "kefta": ["m1", "m2", "sp2", "mn5", "mn7", "var5", "me3", "add11", "add13", "fin10", "mv3", "mw4", "me9", "ku13", "ku26", "bu11", "is18", "tr15", "spx3", "me16"],
    "kubba": ["iq1", "iq2", "ku1"],
    "kuku_sabzi": ["pe2"],
    "lahoh": ["ye2"],
    "lamb_roasted": ["mn1", "hle3", "ex23", "ex33", "mv4", "hw1", "ye9", "bu18"],
    "lamb_soup": ["se5", "ex1", "sv3", "ye3", "ye15", "bu8", "sn25"],
    "lamb_stew": ["m3", "mx1", "mx7", "rn7", "mne1", "mne2", "mne4", "rare1", "me2", "mef1", "mef2", "add25", "add43", "fin25", "mw2", "mef7", "mef8", "holfx4", "me7", "me10", "ye20", "pe18", "me12", "me13", "me14"],
    "leek_dish": ["vn1", "mef5", "fin1", "vv3", "vw3"],
    "lentil_salad": ["san5", "sle4", "add49", "slv9", "sle12"],
    "lentil_soup": ["s2", "sn10", "ex4", "sw2", "sn18", "iq30", "pe7", "pe15", "tr14", "hn22"],
    "liver_dish": ["mn2", "ex49", "mef10", "iq20", "ye23", "tn28", "is14"],
    "mansaf": ["ye19", "is9"],
    "matbucha": ["sa1", "sa7", "hx1", "var2", "holf4", "slv1", "slw4", "ku28", "tn16", "is27", "sle16"],
    "meat_stew": ["sp6", "mn4", "spne3", "me1", "mef3", "add52", "ex22", "fin9", "fin18", "mv2", "mw3", "mw5", "iq5", "iq8", "iq14", "ku12", "tn14", "tr2", "me15", "me20"],
    "merguez": ["mn3", "ex24", "fin15", "spw2", "iq9", "tn20", "me18"],
    "mofletah": ["d1", "rare2", "holf5", "spf5", "ex36", "hv4", "spw1", "as14"],
    "moroccan_bread": ["hn9", "hn10", "rare4", "rare10", "rare12", "rer6", "def5", "add29", "add54", "add56", "fin14", "sv10", "hv5", "spnx4", "hn20", "spe10", "ye8", "ye16", "ye21", "bu19", "tn8"],
    "msemen": ["hn12", "rare9", "add45"],
    "mujaddara": ["is4"],
    "mushroom_dish": ["vne7", "ex12", "vef10", "ku20"],
    "mushroom_soup": ["as27"],
    "offal_dish": ["mx2", "mx3", "mx4", "mx5", "mx6", "mn6", "rare8", "mv5", "mw1", "me17"],
    "olives": ["sau3", "rare6", "sle7", "vef11", "sle15"],
    "onion_soup": ["se1", "se9", "sf3", "add50", "ex11", "saxx1", "ku30"],
    "paella": ["sp8"],
    "pasta_dish": ["sf6", "add40", "add42", "sv7", "sanx5", "me6", "as4", "as13", "as26", "bu26", "tn13", "spx7"],
    "pastilla": ["hn15", "ex34", "fin13"],
    "pickles": ["vn8", "ve7", "add47", "fin30", "spw5", "iq16", "iq26", "as16", "pe13", "tn22", "sle23"],
    "pita": ["is12"],
    "plov": ["bu1", "bu23"],
    "polenta_dish": ["as7"],
    "potato_dish": ["vx4", "ve8", "add21", "spnx2", "ve11", "ve17"],
    "potato_salad": ["sa10", "san14", "sle6"],
    "preserved_lemon": ["sau2"],
    "pumpkin_dish": ["v4", "vne1", "ve2", "slw2"],
    "pumpkin_soup": ["s6", "sn5", "se6", "add48", "sw3"],
    "rice_dish": ["sp5", "hx3", "spe5", "ex3", "ex43", "spv4", "spe8", "ye4", "iq10", "iq21", "iq28", "ku21", "ye17", "pe10", "pe17", "pe29", "bu24", "is16", "tr6", "tr25", "tr30"],
    "rice_pudding": ["hle1", "ex40", "fin27", "dw4", "dn13", "iq27", "pe14", "pe26", "pe30", "tn25", "tn30", "tr18", "spx4"],
    "roasted_pepper": ["sa3", "sa6", "sax4", "sane4", "fin5", "tn10", "tn15", "is23", "sle20"],
    "rugelach": ["as22"],
    "salad_israeli": ["is7"],
    "samsa": ["hne4", "bu2", "iq15"],
    "sardines": ["f4", "fx3", "fne2", "fif5", "holfx2", "fe13"],
    "schnitzel": ["mef4", "as21", "pe21"],
    "sfenj": ["d2", "dv1"],
    "shakshuka": ["sp7", "san11", "spne1", "sle8", "rer2", "slf3", "add20", "ex13", "hv1", "vw2", "holfx1", "spnx3", "as5", "ye7", "tn6", "tn7", "is3", "ku16", "ye13", "tn11", "tn17", "tn26", "is24", "tr5", "hn21", "ve15", "hn23", "spx6"],
    "shawarma": ["cv2", "is5"],
    "shebakia": ["dx1"],
    "shrimp_dish": ["fn4", "fe3", "fe5", "add34", "ex19"],
    "sofrito": ["sp1", "spw4"],
    "spinach_dish": ["vx3", "san15", "se2", "spe2", "add23", "vef9", "is26"],
    "stuffed_meat": ["h2", "sp4", "hne2", "me5", "spf3", "ex21", "mef9", "tr9"],
    "stuffed_veg": ["vn4", "vn5", "vn6", "vne3", "vne4", "vne5", "add7", "ex44", "vv2", "vv4", "iq19", "as11", "bu17", "ve19"],
    "sweet_potato_dish": ["san13"],
    "tabbouleh": ["san17", "slf4", "add6", "slv3", "slv7", "slw5", "sanx6", "sanx7", "san18", "sle11", "sle14", "iq7", "iq23"],
    "tagine": ["h3", "hn1", "hn2", "hn3", "hn6", "hn7", "hn8", "mne3", "hne1", "rare7", "vef1", "ex25", "ex31", "ex32", "ve9", "me8", "hn18", "tr11", "ve18", "me19"],
    "tahini": ["san12", "fin23", "slv2", "slv5", "is13"],
    "tea": ["d5", "dx4", "dne6", "fin28", "iq3", "ye12"],
    "tomato_soup": ["s5", "se10", "iq25", "sn28"],
    "tuna_dish": ["fe2", "fw3"],
    "tzimmes": ["as12"],
    "veg_soup": ["s4", "v6", "sx2", "sn4", "sn11", "san6", "vn3", "spne4", "rare11", "se3", "sf1", "sf5", "sf8", "sf9", "spf2", "add4", "add39", "fin2", "fin29", "sv2", "sv8", "iq11", "ku17", "ku23", "as25", "ye18", "bu10", "bu22"],
    "white_beans": ["vx2", "san3", "vn7", "mn8", "sane2", "spne2", "sle5", "me4", "vef3", "vef4", "spf4", "add12", "vw5", "ve16"],
    "yogurt_dip": ["vef6", "fin22", "spnx1", "iq12", "ku10", "ku14", "ku19", "pe20", "pe22", "tr7"],
    "zaalouk": ["sa2"],
    "zucchini_dish": ["v3", "sax1", "vef7", "ku7"],
}


# ─────────────────────────────────────────────────────────────────
#  PROGRESS REPORTER — fires once per 10% milestone
# ─────────────────────────────────────────────────────────────────
def report_progress(current: int, total: int, ok: int, skip: int, fail: int) -> None:
    pct       = int(current / total * 100)
    milestone = (pct // 10) * 10
    if milestone > 0 and milestone not in report_progress._fired:
        report_progress._fired.add(milestone)
        log.info(
            f"--- PROGRESS {milestone:3d}% ---  "
            f"{current}/{total}  |  OK={ok}  SKIP={skip}  FAIL={fail}"
        )

report_progress._fired: set = set()


# ─────────────────────────────────────────────────────────────────
#  WIKIPEDIA IMAGE RESOLVER
#  Calls the Wikipedia REST summary API.
#  Returns the best available thumbnail URL, or None.
# ─────────────────────────────────────────────────────────────────
def resolve_wiki_thumbnail(article_title: str) -> str | None:
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + article_title
    try:
        req = urllib.request.Request(url, headers=WIKI_HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        # Use thumbnail only — originalimage causes 429 rate-limit errors
        if "thumbnail" in data:
            src = data["thumbnail"]["source"]
            # Request width=400 for smaller, faster download
            src = re.sub(r"/\d+px-", "/400px-", src)
            return src
        return None
        return None
    except Exception as exc:
        log.warning(f"  Wikipedia API failed for {article_title!r}: {exc}")
        return None


# ─────────────────────────────────────────────────────────────────
#  IMAGE DOWNLOADER
#  Downloads a single URL and saves to dest.
#  Returns: 'ok' | 'skip' | 'fail'
# ─────────────────────────────────────────────────────────────────
def download_image(label: str, img_url: str, dest: str) -> str:
    if os.path.exists(dest) and os.path.getsize(dest) >= MIN_FILE_SIZE_BYTES:
        return "skip"
    if DRY_RUN:
        log.info(f"  DRY-RUN  {label}")
        return "ok"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(img_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            if len(data) < MIN_FILE_SIZE_BYTES:
                raise ValueError(f"Response too small: {len(data)} bytes")
            with open(dest, "wb") as fh:
                fh.write(data)
            return "ok"
        except Exception as exc:
            err = str(exc)
            if "429" in err and attempt < MAX_RETRIES:
                log.warning(f"  429 on {label} — waiting {RETRY_WAIT_ON_429}s before retry {attempt+1}/{MAX_RETRIES}")
                time.sleep(RETRY_WAIT_ON_429)
                continue
            log.error(f"  FAIL  {label} — {exc}")
            return "fail"
    return "fail"


# ─────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────
def main() -> None:
    total_gkeys   = len(WIKI_ARTICLES)
    total_recipes = sum(len(v) for v in GKEY_RECIPES.values())
    total_files   = (total_gkeys * 2) + (total_recipes * 2)

    log.info("=" * 60)
    log.info("Perla Ben Arosh Cookbook — Food Image Downloader")
    log.info(f"Mode       : {'DRY-RUN' if DRY_RUN else 'LIVE'}")
    log.info(f"Source     : Wikipedia REST API (real food photos)")
    log.info(f"Proxy      : {PROXY_URL or 'none (direct)'}")
    log.info(f"Log file   : {_log_path}")
    log.info(f"Target dir : {IMAGES_DIR}")
    log.info(f"Categories : {total_gkeys}  |  Recipes: {total_recipes}")
    log.info(f"Total files: {total_files}")
    log.info("=" * 60)

    ok = fail = skip = 0
    processed = 0

    # ── PHASE 1: Download one real food image per G key ──────────────
    log.info("")
    log.info("PHASE 1 — Resolving & downloading category images (Wikipedia)")
    log.info("-" * 60)

    gkey_downloaded = {}   # gkey -> local path of downloaded image
    url_to_dest = {}       # img_url -> local path, avoids re-downloading identical images

    for i, (gkey, article) in enumerate(WIKI_ARTICLES.items(), start=1):
        log.info(f"  [{i:3d}/{total_gkeys}] {gkey!r} -> Wikipedia:{article!r}")

        img_url = resolve_wiki_thumbnail(article)
        if not img_url:
            log.warning(f"    No thumbnail for {article!r} — skipping")
            fail += 2
            processed += 2
            report_progress(processed, total_files, ok, skip, fail)
            continue

        # Download ONCE as {gkey}-1.jpg, then copy to {gkey}-2.jpg (no extra download)
        fname1 = gkey.replace("_", "-") + "-1.jpg"
        fname2 = gkey.replace("_", "-") + "-2.jpg"
        dest1  = os.path.join(IMAGES_DIR, fname1)
        dest2  = os.path.join(IMAGES_DIR, fname2)

        # Check if source was already downloaded by a duplicate-article G key
        if img_url in url_to_dest and os.path.exists(url_to_dest[img_url]):
            # Reuse existing file — copy, no download
            src_existing = url_to_dest[img_url]
            for dest, fname in [(dest1, fname1), (dest2, fname2)]:
                if not (os.path.exists(dest) and os.path.getsize(dest) >= MIN_FILE_SIZE_BYTES):
                    if not DRY_RUN:
                        shutil.copy2(src_existing, dest)
                    ok += 1
                    log.info(f"    REUSE {fname} (copy of {os.path.basename(src_existing)})")
                else:
                    skip += 1
                processed += 1
                report_progress(processed, total_files, ok, skip, fail)
            gkey_downloaded[gkey] = dest1
            continue

        # Download -1 from Wikipedia
        result = download_image(fname1, img_url, dest1)
        processed += 1
        if result == "ok":
            ok += 1
            size = os.path.getsize(dest1) // 1024 if not DRY_RUN else 0
            log.info(f"    OK    {fname1} ({size} KB)")
            gkey_downloaded[gkey] = dest1
            url_to_dest[img_url] = dest1
        elif result == "skip":
            skip += 1
            log.info(f"    SKIP  {fname1}")
            gkey_downloaded[gkey] = dest1
            url_to_dest[img_url] = dest1
        else:
            fail += 1
            processed += 1   # count -2 as failed too
            report_progress(processed, total_files, ok, skip, fail)
            continue
        report_progress(processed, total_files, ok, skip, fail)
        time.sleep(DELAY_BETWEEN_REQUESTS)

        # Copy -1 to -2 — identical image, no extra download
        processed += 1
        if not (os.path.exists(dest2) and os.path.getsize(dest2) >= MIN_FILE_SIZE_BYTES):
            if not DRY_RUN:
                shutil.copy2(dest1, dest2)
            ok += 1
            log.info(f"    COPY  {fname2} (from {fname1})")
        else:
            skip += 1
        report_progress(processed, total_files, ok, skip, fail)

    # ── PHASE 2: Copy category images to every recipe file ───────────
    log.info("")
    log.info("PHASE 2 — Copying category images to recipe files")
    log.info("-" * 60)

    for gkey, recipe_ids in GKEY_RECIPES.items():
        src_path = gkey_downloaded.get(gkey)

        if not src_path or not os.path.exists(src_path):
            log.warning(f"  Source for {gkey!r} missing — skipping {len(recipe_ids)} recipes")
            fail    += len(recipe_ids) * 2
            processed += len(recipe_ids) * 2
            report_progress(processed, total_files, ok, skip, fail)
            continue

        for rid in recipe_ids:
            for n in (1, 2):
                dest_fname = f"r-{rid}-{n}.jpg"
                dest_path  = os.path.join(IMAGES_DIR, dest_fname)

                if os.path.exists(dest_path) and os.path.getsize(dest_path) >= MIN_FILE_SIZE_BYTES:
                    skip += 1
                else:
                    if not DRY_RUN:
                        shutil.copy2(src_path, dest_path)
                    ok += 1

                processed += 1
                report_progress(processed, total_files, ok, skip, fail)

        log.info(f"  {gkey:30s} -> {len(recipe_ids):3d} recipes  (from {os.path.basename(src_path)})")

    # ── Summary ───────────────────────────────────────────────────────
    log.info("")
    log.info("=" * 60)
    log.info(f"SUMMARY  Created/verified={ok}  Skipped={skip}  Failed={fail}")
    log.info(f"Total files in ./images/ : {ok + skip}")
    if fail:
        log.warning(f"{fail} file(s) failed — re-run to retry.")
    else:
        log.info("All images downloaded and copied successfully.")
    log.info(f"Log saved: {_log_path}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
