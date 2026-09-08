#!/usr/bin/env python3
"""
transform_catalog.py — one-off/rerunnable importer that merges verified rows
from raw-source/runsonyourbattery_final_master_catalog.csv into
src/data/catalog.json, WITHOUT touching any existing hand-verified platform
or product row.

Rules applied (per 2026-09-08 build-site pass, see chat/PRD):
  - Only CSV rows with record_type=PRODUCT and
    verification_status in {CORRECTED_KNOWN_PLATFORM_ERROR,
    IMPORTED_NEEDS_PERIODIC_RECHECK} are imported.
    RESEARCH_CANDIDATE_OFFICIAL_PAGE_NOT_RESOLVED rows are skipped (unverified
    candidates, not published per PRD "rows without verified fit are not
    published").
  - Raw battery_platform/brand strings are canonicalized into a fixed slug
    map (many raw strings -> one real platform), including folding
    alliance-based EU brands (P4A, AMPShare, CAS, PXC/Parkside X20V Team)
    into one platform per alliance, since the whole point of those alliances
    is cross-brand battery interchangeability.
  - Ryobi US (TTI-licensed, existing `ryobi-18v-one`) is NOT extended into
    UK/DE/FR/IT/ES: live-checked uk.ryobitools.eu on 2026-09-08 confirms a
    UK/EU Ryobi ONE+ system exists but its licensee footer text is
    ambiguous/inconsistent with the historically-cited Positec split, and no
    CSV row is sourced from the UK site specifically — so per PRD "an
    unpopulated region key means not yet verified, hide rather than show
    with a broken/unsafe claim", Ryobi US stays US-only this pass.
  - CSV market_us/uk/de/fr/it/es flags are ~99% blank (unusable), so region
    availability per platform is assigned via a hand-built ruleset based on
    brand/alliance knowledge (see REGION_RULES below), erring toward US-only
    when EU availability isn't reasonably certain.
  - Existing product `affiliate` blocks are left untouched (flat shape). New
    rows get the same flat `affiliate` shape (US link) PLUS a sibling
    `affiliate_regions` map capturing any other regional links the CSV had,
    for future use once per-region link swapping is wired up. Not consumed
    by any component yet — safe, additive, non-breaking.
"""
import csv
import json
import re
from collections import defaultdict, OrderedDict

ROOT = "/Users/i42492/Library/CloudStorage/OneDrive-VeriskAnalytics/Desktop/passive websites projects/sites/runs-on-your-battery-finder"
CSV_PATH = f"{ROOT}/raw-source/runsonyourbattery_final_master_catalog.csv"
CATALOG_PATH = f"{ROOT}/src/data/catalog.json"

USABLE_STATUSES = {"CORRECTED_KNOWN_PLATFORM_ERROR", "IMPORTED_NEEDS_PERIODIC_RECHECK"}

# ---------------------------------------------------------------------------
# Canonical platform slug per (brand, battery_platform) combo seen in the CSV.
# ---------------------------------------------------------------------------
PLATFORM_MAP = {
    ("DeWalt", "DeWalt 20V MAX"): "dewalt-20v-max",
    ("DeWalt", "DeWalt 20V MAX / 18V XR"): "dewalt-20v-max",
    ("Milwaukee", "Milwaukee M12"): "milwaukee-m12",
    ("Milwaukee", "M12"): "milwaukee-m12",
    ("Milwaukee", "Milwaukee M18"): "milwaukee-m18",
    ("Milwaukee", "Milwaukee MX FUEL"): "milwaukee-mx-fuel",
    ("Makita", "Makita LXT 18V"): "makita-18v-lxt",
    ("Makita", "Makita XGT 40V max"): "makita-40v-xgt",
    ("Ryobi", "Ryobi 18V ONE+"): "ryobi-18v-one",
    ("Ryobi", "Ryobi ONE+ 18V"): "ryobi-18v-one",
    ("Ryobi", "Ryobi 40V"): "ryobi-40v",
    ("Ryobi", "Ryobi USB Lithium"): "ryobi-usb-lithium",
    ("Ryobi", "USB Lithium"): "ryobi-usb-lithium",
    ("HART", "HART 20V"): "hart-20v",
    ("Craftsman", "Craftsman V20"): "craftsman-v20",
    ("WORX", "WORX PowerShare 20V"): "worx-powershare-20v",
    ("Greenworks", "Greenworks 24V"): "greenworks-24v",
    ("Greenworks", "Greenworks 24V / 40V"): "greenworks-24v",
    ("Bauer", "Bauer 20V"): "bauer-20v",
    ("Kobalt", "Kobalt 24V MAX"): "kobalt-24v-max",
    ("Masterforce", "Masterforce 20V"): "masterforce-20v",
    ("Hercules", "Hercules 20V"): "hercules-20v",
    ("Black+Decker", "Black+Decker 20V MAX"): "black-decker-20v-max",
    ("Metabo HPT", "Metabo HPT MultiVolt"): "metabo-hpt-multivolt",
    ("SKIL", "SKIL PWRCORE 20V"): "skil-pwrcore-20v",
    ("RIDGID", "RIDGID 18V"): "ridgid-18v",
    ("FLEX", "FLEX 24V"): "flex-24v",
    ("Festool", "Festool 18V"): "festool-18v",
    ("Hilti", "Hilti Nuron 22V"): "hilti-nuron-22v",
    ("Karcher", "Karcher Battery Power 18V"): "karcher-battery-power-18v",
    ("EGO", "EGO POWER+ 56V"): "ego-power-plus-56v",
    ("STIHL", "STIHL AK System"): "stihl-ak-system",
    ("STIHL", "STIHL AP System"): "stihl-ap-system",
    ("STIHL", "STIHL AS System"): "stihl-as-system",
    ("Stanley FATMAX", "Stanley FATMAX V20"): "stanley-fatmax-v20",
    ("Bosch Professional", "Bosch Professional 18V / AMPShare"): "bosch-professional-18v",
    ("Einhell", "Einhell Power X-Change"): "einhell-power-x-change",
    ("AEG", "AEG PRO18V"): "aeg-pro18v",
    ("SCANGRIP", "SCANGRIP CONNECT"): "scangrip-connect",
    # P4A alliance -> one platform
    ("Bosch DIY", "Bosch DIY P4A"): "bosch-p4a",
    ("Bosch Home Appliances", "Bosch Home Appliances P4A"): "bosch-p4a",
    ("Gardena", "Gardena P4A"): "bosch-p4a",
    ("GLORIA", "GLORIA P4A"): "bosch-p4a",
    ("HK Audio", "HK Audio P4A"): "bosch-p4a",
    ("LEDVANCE", "LEDVANCE P4A"): "bosch-p4a",
    ("STEINEL", "STEINEL P4A"): "bosch-p4a",
    ("Wagner", "Wagner P4A"): "bosch-p4a",
    # AMPShare alliance -> one platform (Bosch Professional stays its own platform)
    ("AAT", "AAT / AMPShare"): "ampshare-18v",
    ("Ledlenser", "Ledlenser / AMPShare"): "ampshare-18v",
    ("MATO", "MATO / AMPShare"): "ampshare-18v",
    ("MESTO", "MESTO / AMPShare"): "ampshare-18v",
    ("PerfectPro", "PerfectPro / AMPShare"): "ampshare-18v",
    ("SONLUX", "SONLUX / AMPShare"): "ampshare-18v",
    ("SuitX", "SuitX / AMPShare"): "ampshare-18v",
    ("Titan", "Titan / AMPShare"): "ampshare-18v",
    ("Wagner", "Wagner / AMPShare"): "ampshare-18v",
    ("brennenstuhl", "brennenstuhl / AMPShare"): "ampshare-18v",
    ("STEINEL", "STEINEL / AMPShare"): "ampshare-18v",
    # CAS alliance -> one platform
    ("Birchmeier", "Birchmeier / CAS"): "cas-18v",
    ("Cleanfix", "Cleanfix / CAS"): "cas-18v",
    ("Ghibli", "Ghibli / CAS"): "cas-18v",
    ("Haaga", "Haaga / CAS"): "cas-18v",
    ("STEINEL", "STEINEL / CAS"): "cas-18v",
    ("Starmix", "Starmix / CAS"): "cas-18v",
    ("pulsFOG", "pulsFOG / CAS"): "cas-18v",
    # Parkside X20V Team (PXC, Lidl-exclusive) -> one platform
    ("BS Rollen", "BS Rollen / PXC"): "parkside-x20v-team",
    ("Blickle", "Blickle / PXC"): "parkside-x20v-team",
    ("CS Instruments", "CS Instruments / PXC"): "parkside-x20v-team",
    ("Clesana", "Clesana / PXC"): "parkside-x20v-team",
    ("HEISSNER", "HEISSNER / PXC"): "parkside-x20v-team",
    ("doppler", "doppler / PXC"): "parkside-x20v-team",
    ("Parkside", "Parkside X20V Team"): "parkside-x20v-team",
}

PLATFORM_NAMES = {
    "milwaukee-mx-fuel": ("Milwaukee MX FUEL", "Milwaukee"),
    "makita-40v-xgt": ("Makita 40V max XGT", "Makita"),
    "ryobi-40v": ("Ryobi 40V", "Ryobi"),
    "ryobi-usb-lithium": ("Ryobi USB Lithium", "Ryobi"),
    "bauer-20v": ("Bauer 20V", "Bauer"),
    "kobalt-24v-max": ("Kobalt 24V MAX", "Kobalt"),
    "masterforce-20v": ("Masterforce 20V", "Masterforce"),
    "hercules-20v": ("Hercules 20V", "Hercules"),
    "black-decker-20v-max": ("Black+Decker 20V MAX", "Black+Decker"),
    "metabo-hpt-multivolt": ("Metabo HPT MultiVolt", "Metabo HPT"),
    "skil-pwrcore-20v": ("SKIL PWRCORE 20V", "SKIL"),
    "ridgid-18v": ("RIDGID 18V", "RIDGID"),
    "flex-24v": ("FLEX 24V", "FLEX"),
    "festool-18v": ("Festool 18V", "Festool"),
    "hilti-nuron-22v": ("Hilti Nuron 22V", "Hilti"),
    "karcher-battery-power-18v": ("Karcher Battery Power 18V", "Karcher"),
    "ego-power-plus-56v": ("EGO POWER+ 56V", "EGO"),
    "stihl-ak-system": ("STIHL AK System", "STIHL"),
    "stihl-ap-system": ("STIHL AP System", "STIHL"),
    "stihl-as-system": ("STIHL AS System", "STIHL"),
    "stanley-fatmax-v20": ("Stanley FATMAX V20", "Stanley FATMAX"),
    "bosch-professional-18v": ("Bosch Professional 18V", "Bosch Professional"),
    "einhell-power-x-change": ("Einhell Power X-Change", "Einhell"),
    "aeg-pro18v": ("AEG PRO18V", "AEG"),
    "scangrip-connect": ("SCANGRIP CONNECT", "SCANGRIP"),
    "bosch-p4a": ("Bosch Power for All 18V (P4A)", "Power for All Alliance"),
    "ampshare-18v": ("AMPShare 18V", "AMPShare Alliance"),
    "cas-18v": ("Cordless Alliance System (CAS) 18V", "CAS Alliance"),
    "parkside-x20v-team": ("Parkside X20V Team", "Parkside"),
}

US_ONLY = {
    "hart-20v", "craftsman-v20", "greenworks-24v", "bauer-20v", "kobalt-24v-max",
    "masterforce-20v", "hercules-20v", "black-decker-20v-max", "metabo-hpt-multivolt",
    "skil-pwrcore-20v", "ridgid-18v", "flex-24v", "ryobi-18v-one", "ryobi-40v",
    "milwaukee-mx-fuel",
}
ALL_SIX = {
    "dewalt-20v-max", "milwaukee-m18", "milwaukee-m12", "makita-18v-lxt", "makita-40v-xgt",
    "worx-powershare-20v", "festool-18v", "hilti-nuron-22v", "ego-power-plus-56v",
    "stihl-ak-system", "stihl-ap-system", "stihl-as-system", "karcher-battery-power-18v",
    "bosch-professional-18v", "ryobi-usb-lithium",
}
UK_DE_FR_IT_ES = {
    "einhell-power-x-change", "aeg-pro18v", "bosch-p4a", "ampshare-18v", "cas-18v",
    "parkside-x20v-team", "scangrip-connect",
}
UK_ONLY = {"stanley-fatmax-v20"}

def regions_for(slug):
    if slug in US_ONLY:
        return ["US"]
    if slug in ALL_SIX:
        return ["US", "UK", "DE", "FR", "IT", "ES"]
    if slug in UK_DE_FR_IT_ES:
        return ["UK", "DE", "FR", "IT", "ES"]
    if slug in UK_ONLY:
        return ["UK"]
    return ["US"]

FIT_MAP = {
    "Native": "native",
    "Alliance-native": "direct",
    "Third-party adapter": "adapter",
}

CATEGORY_MAP = {
    "Vacuums": ("vacuums", "Vacuums"),
    "Fans": ("fans", "Fans"),
    "Lighting": ("lights", "Lights"),
    "Inflation": ("inflators", "Inflators"),
    "Inflation / cleanup": ("inflators", "Inflators"),
    "Inflation / lighting": ("inflators", "Inflators"),
    "Audio": ("speakers", "Speakers & radios"),
    "Power output": ("power-inverters", "Power inverters"),
    "Pressure cleaning": ("pressure-washers", "Pressure washers"),
    "Specialty": ("specialty", "Specialty"),
    "Food / drink": ("food-drink", "Food & drink"),
    "Water / pumps": ("water-pumps", "Water & pumps"),
    "Mobility": ("mobility", "Mobility"),
    "Cleaning": ("cleaning", "Cleaning"),
    "Cleanup": ("cleaning", "Cleaning"),
    "Sprayers": ("sprayers", "Sprayers"),
    "Tools / OPE": ("outdoor-power-equipment", "Outdoor power equipment"),
    "Cold storage": ("coolers", "Coolers & cold storage"),
    "Outdoor lifestyle": ("outdoor-lifestyle", "Outdoor lifestyle"),
    "Pest control": ("pest-control", "Pest control"),
    "Inspection": ("inspection", "Inspection cameras"),
    "Wearables": ("wearables", "Wearables"),
}

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s

def main():
    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    prods = [r for r in rows if r["record_type"] == "PRODUCT" and r["verification_status"] in USABLE_STATUSES]
    print(f"Importing {len(prods)} usable rows")

    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f, object_pairs_hook=OrderedDict)

    existing_platform_slugs = {p["slug"] for p in catalog["platforms"]}
    existing_category_slugs = {c["slug"] for c in catalog["categories"]}
    existing_ids = {p["id"] for p in catalog["products"]}

    new_platforms = OrderedDict()
    new_categories = OrderedDict()
    new_products = []
    skipped_unmapped = defaultdict(int)

    for r in prods:
        key = (r["brand"].strip(), r["battery_platform"].strip())
        slug = PLATFORM_MAP.get(key)
        if not slug:
            skipped_unmapped[key] += 1
            continue

        if slug not in existing_platform_slugs and slug not in new_platforms:
            name, brand = PLATFORM_NAMES.get(slug, (slug, r["brand"]))
            new_platforms[slug] = {
                "slug": slug,
                "name": name,
                "brand": brand,
                "regions": regions_for(slug),
            }

        raw_cat = r["gadget_category"].strip()
        cat_slug, cat_name = CATEGORY_MAP.get(raw_cat, (slugify(raw_cat), raw_cat))
        if cat_slug not in existing_category_slugs and cat_slug not in new_categories:
            new_categories[cat_slug] = {"slug": cat_slug, "name": cat_name}

        fit = FIT_MAP.get(r["fit_type"].strip(), "native")

        # id: derive from record_id, fall back to slug of product name
        base_id = r["record_id"].strip() or slugify(r["product_name"])
        pid = slugify(base_id)
        n = 1
        candidate = pid
        while candidate in existing_ids:
            n += 1
            candidate = f"{pid}-{n}"
        existing_ids.add(candidate)

        brand_name = r["brand"].strip()
        pname = r["product_name"].strip()
        full_name = pname if pname.lower().startswith(brand_name.lower()) else f"{brand_name} {pname}".strip()
        model = r["model_sku"].strip()
        if model and model.lower() not in full_name.lower():
            full_name = f"{full_name} ({model})"

        note_parts = []
        if r["adapter_required"].strip() == "YES":
            adapter = r["adapter_brand_model"].strip()
            note_parts.append(
                f"Needs a third-party adapter{' (' + adapter + ')' if adapter else ''} — "
                "this bypasses the battery pack's protection circuitry, so avoid deep discharge."
            )
        elif fit == "direct":
            note_parts.append(f"Alliance-native: a third-party brand product that runs natively on the {r['battery_platform'].strip()} battery, no adapter needed.")
        safety = r["safety_note"].strip()
        if safety:
            note_parts.append(safety)
        notes = r["notes"].strip()
        if notes:
            note_parts.append(notes)
        if not note_parts:
            note_parts.append(f"Imported from research pass; verification status: {r['verification_status'].strip()}.")
        note = " ".join(note_parts)

        us_url = r["amazon_us_direct_url"].strip() or r["amazon_us_search_url"].strip() or r["official_product_url"].strip() or r["fallback_retailer_url"].strip()
        affiliate_regions = {}
        for region, prefix in (("US", "amazon_us"), ("UK", "amazon_uk"), ("DE", "amazon_de"), ("FR", "amazon_fr"), ("IT", "amazon_it"), ("ES", "amazon_es")):
            direct = r[f"{prefix}_direct_url"].strip()
            search = r[f"{prefix}_search_url"].strip()
            asin = r[f"{prefix}_asin"].strip()
            url = direct or search
            if url:
                affiliate_regions[region] = {"asin": asin, "affiliate_url": url}

        product = OrderedDict([
            ("id", candidate),
            ("name", full_name),
            ("platform", slug),
            ("category", cat_slug),
            ("fit", fit),
            ("battery_included", False),
            ("note", note),
            ("affiliate", OrderedDict([
                ("asin", ""),
                ("affiliate_url", us_url),
                ("affiliate_enabled", False),
                ("requires_disclosure", True),
            ])),
        ])
        if affiliate_regions:
            product["affiliate_regions"] = affiliate_regions
        new_products.append(product)

    if skipped_unmapped:
        print("Skipped (no platform mapping):")
        for k, v in skipped_unmapped.items():
            print(" ", k, v)

    catalog["platforms"].extend(new_platforms.values())
    catalog["categories"].extend(new_categories.values())
    catalog["products"].extend(new_products)

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Added {len(new_platforms)} platforms, {len(new_categories)} categories, {len(new_products)} products.")

if __name__ == "__main__":
    main()
