"""
Fetch cosmetic product data by barcode.

Fallback chain:
  1. Open Beauty Facts  (cosmetics-focused)
  2. Open Food Facts    (broader coverage, same API format)
  3. Go-UPC             (wide retail coverage, free, no key)

If all three fail, returns status="not_found".
"""

import re
import requests

OBF_URL  = "https://world.openbeautyfacts.org/api/v0/product/{barcode}.json"
OFF_URL  = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
GOUPC_URL = "https://go-upc.com/api/v1/code/{barcode}"
TIMEOUT  = 8


# ── Ingredient parser (shared) ────────────────────────────────────────────────

def parse_ingredients_text(raw: str) -> list:
    """
    Parse a raw ingredient string like:
      "Aqua, Glycerin, Fragrance (Linalool, Limonene), Methylparaben*"
    into a flat, lowercased, cleaned list:
      ["aqua", "glycerin", "fragrance", "linalool", "limonene", "methylparaben"]
    """
    if not raw:
        return []

    # Expand parenthetical sub-ingredients before splitting on commas
    raw = re.sub(r'\(([^)]+)\)', lambda m: ', ' + m.group(1), raw)

    items = []
    for item in raw.split(','):
        item = item.strip()
        item = re.sub(r'[\[\]{}]', '', item)
        item = item.rstrip('*').rstrip('0123456789').strip()
        item = item.lower()
        if len(item) > 1:
            items.append(item)

    return items


# ── Empty result template ─────────────────────────────────────────────────────

def _empty(barcode: str) -> dict:
    return {
        "status": "error",
        "product_name": "",
        "brand": "",
        "ingredients_text": "",
        "ingredients_list": [],
        "image_url": "",
        "barcode": barcode.strip(),
        "error_message": "",
        "source": "",
    }


# ── Source 1: Open Beauty Facts ───────────────────────────────────────────────

def _fetch_open_facts(barcode: str, url_template: str, source_name: str) -> dict:
    """Shared fetcher for Open Beauty Facts and Open Food Facts (identical API)."""
    result = _empty(barcode)
    result["source"] = source_name
    try:
        response = requests.get(url_template.format(barcode=barcode.strip()), timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        result["error_message"] = f"{source_name}: request timed out."
        return result
    except requests.exceptions.ConnectionError:
        result["error_message"] = f"{source_name}: connection error."
        return result
    except Exception as e:
        result["error_message"] = f"{source_name}: {e}"
        return result

    if data.get("status") == 0:
        result["status"] = "not_found"
        return result

    product = data.get("product", {})
    result["product_name"] = product.get("product_name", "").strip()
    result["brand"]        = product.get("brands", "").strip()
    result["image_url"]    = product.get("image_front_url", "").strip()

    ingredients_text = (
        product.get("ingredients_text_en", "")
        or product.get("ingredients_text", "")
        or ""
    ).strip()

    if not ingredients_text:
        result["status"] = "no_ingredients"
        return result

    result["status"] = "ok"
    result["ingredients_text"] = ingredients_text
    result["ingredients_list"] = parse_ingredients_text(ingredients_text)
    return result


# ── Source 3: Go-UPC ──────────────────────────────────────────────────────────

def _fetch_go_upc(barcode: str) -> dict:
    """
    Go-UPC free API — broader retail coverage.
    Returns product name and sometimes a description that may contain ingredients.
    No API key required for basic lookups.
    """
    result = _empty(barcode)
    result["source"] = "Go-UPC"
    try:
        response = requests.get(
            GOUPC_URL.format(barcode=barcode.strip()),
            timeout=TIMEOUT,
            headers={"User-Agent": "CosmoTox/1.0 (cosmetic ingredient scanner)"},
        )
        if response.status_code == 404:
            result["status"] = "not_found"
            return result
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        result["error_message"] = "Go-UPC: request timed out."
        return result
    except requests.exceptions.ConnectionError:
        result["error_message"] = "Go-UPC: connection error."
        return result
    except Exception as e:
        result["error_message"] = f"Go-UPC: {e}"
        return result

    product = data.get("product") or {}
    if not product:
        result["status"] = "not_found"
        return result

    result["product_name"] = (product.get("name") or "").strip()
    result["brand"]        = (product.get("brand") or "").strip()
    result["image_url"]    = (product.get("imageUrl") or "").strip()

    # Go-UPC may carry ingredients in the description field
    description = (product.get("description") or "").strip()
    ingredients_text = ""

    # Heuristic: if description contains comma-separated INCI-like words, treat as ingredients
    if description and description.count(',') >= 3:
        ingredients_text = description

    if not ingredients_text:
        # Product found but no ingredients available
        result["status"] = "no_ingredients"
        return result

    result["status"] = "ok"
    result["ingredients_text"] = ingredients_text
    result["ingredients_list"] = parse_ingredients_text(ingredients_text)
    return result


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_by_barcode(barcode: str) -> dict:
    """
    Look up a cosmetic product by barcode.
    Tries three sources in order:
      1. Open Beauty Facts
      2. Open Food Facts
      3. Go-UPC

    Returns a dict with keys:
        status           — "ok" | "not_found" | "no_ingredients" | "error"
        product_name     — str
        brand            — str
        ingredients_text — str (raw label text)
        ingredients_list — list[str] (parsed, lowercased)
        image_url        — str
        barcode          — str
        error_message    — str (only when status == "error")
        source           — str (which database returned the result)
    """
    barcode = barcode.strip()

    # 1. Open Beauty Facts
    result = _fetch_open_facts(barcode, OBF_URL, "Open Beauty Facts")
    if result["status"] == "ok":
        return result

    # 2. Open Food Facts
    result2 = _fetch_open_facts(barcode, OFF_URL, "Open Food Facts")
    if result2["status"] == "ok":
        return result2

    # 3. Go-UPC
    result3 = _fetch_go_upc(barcode)
    if result3["status"] in ("ok", "no_ingredients"):
        return result3

    # All failed — return not_found
    final = _empty(barcode)
    final["status"] = "not_found"
    final["source"] = "all sources"
    return final
