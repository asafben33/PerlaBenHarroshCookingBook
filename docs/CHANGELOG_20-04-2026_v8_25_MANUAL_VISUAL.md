# CHANGELOG — v8.25 Manual Visual Image Mapping

**Date:** 2026-04-20  
**Version:** v8.25 (manual visual mapping revision)  
**Scope:** Complete overhaul of image-to-chapter mapping based on true manual visual identification of all 151 book images.

---

## Summary

Completely replaced the previous deterministic filename-based image mapping with **manual visual identification** of each of the 151 book images. Every image was individually reviewed and assigned to a chapter based on its **actual visual content**, not on filename ranges or any algorithm.

---

## What Changed

### Method Change
- **Before (v8.25 initial):** Images were assigned to chapters based on filename patterns (e.g. g42_016-030 → ch1, g42_031-050 → ch3, etc.).
- **After (v8.25 manual visual):** Every image was opened and visually inspected. The chapter was chosen based on the actual content visible in the image (e.g. an image showing police uniform goes to ch9 "במדים", an image showing snow in Jerusalem goes to ch6 "ירושלים", etc.).

### Key Visual Identifications

**Major discoveries from manual review:**
- `g42_027`: tombstone of Samuel Ben-Harrosh (Pinchas's grandfather, died Sept 1937)
- `g42_063`: official bride portrait of Perla on wedding day
- `g42_065`: Perla + Pinchas official wedding couple portrait
- `g42_066`, `g42_071`: Pinchas in IDF officer uniform
- `g42_083`: certificate of honor from Police Retirees Association (Dec 2012) — confirms Pinchas's police service
- `g42_085`: Pinchas in formal police uniform
- `g42_089`: Perla in rare Jerusalem snow
- `g42_092-094`: paintings actually painted BY Pinchas — Pinchas was an artist
- `g42_095`: **complete family portrait — Perla with all 5 children** (Simi, Yehuda, Sammy, Ilan, Asaf)
- `g45_050`: Perla at Ramchal's tomb in Tiberias (pilgrimage)
- `g45_062`: Perla + Pinchas riding elephant — Thailand/India trip
- `g45_068`: traditional Moroccan wedding — return to roots
- `g45_015`: young grandson in "MY DAD IS A SUPER HERO" shirt
- `g45_020`: granddaughter in IDF uniform

### Final Chapter Distribution (Manual Visual)

| Chapter | Inline | Gallery | Total |
|---|---|---|---|
| prologue | 0 | 1 | 1 |
| ch1 — שורשים באדמת מרוקו | 6 | 1 | 7 |
| ch2 — מעגל השנה | 2 | 3 | 5 |
| ch3 — מרוקו של ילדותי | 9 | 8 | 17 |
| ch4 — כמיהה ציונית | 3 | 5 | 8 |
| ch5 — אל הדרור | 2 | 2 | 4 |
| ch6 — ימים ראשונים בירושלים | 1 | 6 | 7 |
| ch7 — סיפורה של פרלה | 3 | 5 | 8 |
| ch8 — בית ומשפחה | 2 | 9 | 11 |
| ch9 — במדים | 4 | 9 | 13 |
| ch10 — המבט לעבר | 2 | 68 | 70 |
| **TOTAL** | **34** | **117** | **151** |

*Note: ch10 is image-heavy because most of the g45 images are later-life photos (grandchildren, trips, grandchild weddings, portraits of the elderly couple, art by Pinchas, return trips to Morocco).*

---

## Files Changed

| File | Purpose | Size |
|---|---|---|
| `IMAGE_MAPPING_v8_25.json` | Authoritative image-to-chapter mapping with manual visual identification | 79,417 bytes |
| `IMAGE_MAPPING_v8_25.csv` | Same data in Excel-friendly format | 34,397 bytes |
| `book_data.js` | Rebuilt from JSON with new visual mappings, valid JS | 228,444 bytes |
| `book_images.zip` | All 151 image files (unchanged) | 17.5 MB |
| `rebuild_book_images.py` | Script to regenerate book_data.js from JSON | 14,287 bytes |

### Supporting Documentation
- `IMAGE_MAPPING_README.md` — Human-readable docs
- `DEPLOYMENT_v8_25.md` — Step-by-step deployment guide

---

## Technical Notes

### Alt Text Fix
Initial build produced invalid JS due to Hebrew gershayim (straight double quotes) in alt text (e.g. `צה"ל`, `ז"ל`). Solution: stripped `"` and `\` chars from alt texts in JSON before rebuild. Final book_data.js validates as proper JavaScript.

### Validation
- HE section: 78 g42 + 72 g45 + 1 wedding = **151 images** ✓
- `node -c book_data.js` passes with no errors ✓
- All 151 entries carry `identification_method: "manual_visual_review"` ✓

---

## Deployment Commands (PowerShell, run one at a time)

```powershell
cd C:\Users\isasaf\Assi-ProjectsWorkFolder\PerlaBenHarroshCookingBook

# Backup current state (optional but recommended)
Copy-Item book_data.js book_data.js.v8.25-pre-visual.bak -Force
Copy-Item IMAGE_MAPPING_v8_25.json IMAGE_MAPPING_v8_25.json.pre-visual.bak -Force

# Copy new files from Downloads
Copy-Item "$env:USERPROFILE\Downloads\book_data.js" "." -Force
Copy-Item "$env:USERPROFILE\Downloads\IMAGE_MAPPING_v8_25.json" "." -Force
Copy-Item "$env:USERPROFILE\Downloads\IMAGE_MAPPING_v8_25.csv" "." -Force
Copy-Item "$env:USERPROFILE\Downloads\CHANGELOG_20-04-2026_v8_25_MANUAL_VISUAL.md" "." -Force

# Commit and push
git add book_data.js IMAGE_MAPPING_v8_25.json IMAGE_MAPPING_v8_25.csv CHANGELOG_20-04-2026_v8_25_MANUAL_VISUAL.md
git commit -m "v8.25 revision: replace deterministic image mapping with manual visual identification of all 151 images"
git push origin main
```

**CRITICAL:** Hard refresh required after deployment (Ctrl+Shift+R).

---

## Verification Checklist (after deployment)

1. ✅ Visit https://perlabenharrosh-cookingbook.netlify.app/
2. ✅ Hard refresh (Ctrl+Shift+R)
3. ✅ Open book reader — verify all 151 images load
4. ✅ Spot-check: ch9 "במדים" should contain Pinchas in IDF/police uniforms
5. ✅ Spot-check: ch10 should contain family portraits, grandchildren, trips, Pinchas's paintings
6. ✅ Spot-check: ch2 "מעגל השנה" should contain Purim/Sukkot images
7. ✅ Spot-check: prologue should contain wedding.jpg

---

## DO NOT (Warnings)

- Do NOT regenerate book_data.js without using the v8.25 manual visual JSON
- Do NOT revert to filename-based deterministic mapping
- Do NOT add quote characters (`"`, `\`) to alt text — they break JS string escaping
- All future image additions should update IMAGE_MAPPING_v8_25.json and re-run `rebuild_book_images.py`
