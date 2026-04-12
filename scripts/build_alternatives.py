"""
Safer Alternatives verification pipeline.

Run:  python scripts/build_alternatives.py
Output: scripts/verified_alternatives.json

Each candidate is run through the actual CosmoTox /analyze engine (no HTTP).
Only products that pass the criteria below are written to the output file.

Pass criteria:
  - verdict == "clean"                                           → always pass
  - verdict == "caution" AND exactly 1 toxicant detected
    AND that toxicant's tier == "low"
    AND paper_count < 15                                         → borderline pass
  - everything else                                              → fail
"""

import sys
import os
import json
from datetime import date

# Allow running from project root or scripts/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent", ".env"))

import pandas as pd
from groq import Groq
from agent.tools.analyze_ingredients import parse_ingredients_text, analyze

ALL_TOXICANT_KEYS = [
    "parabens", "phthalates", "pfas", "benzophenones", "siloxanes", "fragrance",
    "toluene", "formaldehyde_releasers", "heavy_metals", "hydroquinone",
    "ethanolamines", "bha_bht", "coal_tar", "triclosan", "dioxane",
]


def load_engine():
    db_path = os.environ.get("DATABASE_PATH", "database")
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path)
    csv_path = os.path.join(db_path, "_combined.csv")
    df = pd.read_csv(csv_path)
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return df, groq_client


def passes(result: dict) -> bool:
    verdict = result.get("verdict", "")
    if verdict == "clean":
        return True
    if verdict == "caution":
        detected = result.get("detected_toxicants", [])
        if (len(detected) == 1
                and detected[0].get("tier") == "low"
                and detected[0].get("paper_count", 99) < 15):
            return True
    return False


def verify_product(product: dict, df, groq_client) -> dict | None:
    ingredients = parse_ingredients_text(product["ingredients_text"])
    if not ingredients:
        print(f"  [WARN] Parse failed: {product['brand']} - {product['name']}")
        return None
    result = analyze(ingredients, df, groq_client)
    passed = passes(result)
    detected_keys = [t["toxicant_key"] for t in result.get("detected_toxicants", [])]
    avoids = [k for k in ALL_TOXICANT_KEYS if k not in detected_keys]
    symbol = "PASS" if passed else "FAIL"
    print(f"  [{symbol}] {product['brand']} - {product['name']} | {result['verdict']} | {result['total_toxicants_detected']} toxicant(s)")
    if not passed:
        for t in result.get("detected_toxicants", []):
            print(f"         -> {t['display_name']} (tier:{t['tier']}, papers:{t['paper_count']})")
        return None
    return {
        "name":           product["name"],
        "brand":          product["brand"],
        "product_type":   product["product_type"],
        "verified":       True,
        "scan_date":      str(date.today()),
        "verdict":        result["verdict"],
        "toxicant_count": result["total_toxicants_detected"],
        "avoids":         avoids,
        "detected":       detected_keys,
        "amazon_url":     product.get("amazon_url", ""),
        "amazon_in_url":  product.get("amazon_in_url", ""),
        "flipkart_url":   product.get("flipkart_url", ""),
        "sponsored":      False,
    }


# ── CANDIDATES ────────────────────────────────────────────────────────────────
# Each entry: product_type, brand, name, ingredients_text, amazon_url,
#             amazon_in_url, flipkart_url
# Populated by Phase 2 ingredient research.

CANDIDATES = [

    # ── MOISTURIZER ──────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "moisturizer",
        "brand": "Minimalist",
        "name": "10% Niacinamide Face Moisturizer",
        "ingredients_text": "Aqua, Niacinamide, Pentylene Glycol, Dicaprylyl Carbonate, Glycerin, Isononyl Isononanoate, Cetearyl Alcohol, Ceteareth-20, Allantoin, Panthenol, Sodium Hyaluronate, Ceramide NP, Ceramide AP, Ceramide EOP, Phytosphingosine, Cholesterol, Carbomer, Xanthan Gum, Sodium Lauroyl Lactylate, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Minimalist+Niacinamide+Moisturizer",
        "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Niacinamide+Moisturizer",
        "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Niacinamide+Moisturizer",
    },
    {
        "product_type": "moisturizer",
        "brand": "Minimalist",
        "name": "Peptide Moisturizer SPF 30",
        "ingredients_text": "Aqua, Ethylhexyl Methoxycinnamate, Dicaprylyl Carbonate, Glycerin, Butyl Methoxydibenzoylmethane, Niacinamide, Pentylene Glycol, Isononyl Isononanoate, Cetearyl Alcohol, Ceteareth-20, Palmitoyl Tripeptide-1, Palmitoyl Tetrapeptide-7, Allantoin, Panthenol, Sodium Hyaluronate, Ceramide NP, Carbomer, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Minimalist+Peptide+Moisturizer+SPF+30",
        "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Peptide+Moisturizer+SPF+30",
        "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Peptide+Moisturizer+SPF+30",
    },
    {
        "product_type": "moisturizer",
        "brand": "Dr. Sheth's",
        "name": "Ceramide & Vitamin C Moisturizer",
        "ingredients_text": "Water, Glycerin, Niacinamide, Dicaprylyl Carbonate, Isononyl Isononanoate, Cetearyl Alcohol, Ceteareth-20, Ascorbyl Glucoside, Ceramide NP, Ceramide AP, Ceramide EOP, Phytosphingosine, Cholesterol, Panthenol, Allantoin, Sodium Hyaluronate, Carbomer, Xanthan Gum, Sodium Lauroyl Lactylate, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Dr+Sheth+Ceramide+Vitamin+C+Moisturizer",
        "amazon_in_url": "https://www.amazon.in/s?k=Dr+Sheth+Ceramide+Vitamin+C+Moisturizer",
        "flipkart_url": "https://www.flipkart.com/search?q=Dr+Sheth+Ceramide+Vitamin+C+Moisturizer",
    },
    {
        "product_type": "moisturizer",
        "brand": "Plum",
        "name": "Hello Aloe Caring Day Moisturizer",
        "ingredients_text": "Aqua, Aloe Barbadensis Leaf Juice, Glycerin, Caprylic/Capric Triglyceride, Cetearyl Alcohol, Glyceryl Stearate, Stearic Acid, Dimethicone, Niacinamide, Panthenol, Allantoin, Tocopheryl Acetate, Sodium Hyaluronate, Carbomer, Triethanolamine, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Plum+Hello+Aloe+Moisturizer",
        "amazon_in_url": "https://www.amazon.in/s?k=Plum+Hello+Aloe+Moisturizer",
        "flipkart_url": "https://www.flipkart.com/search?q=Plum+Hello+Aloe+Moisturizer",
    },
    {
        "product_type": "moisturizer",
        "brand": "Dot & Key",
        "name": "Water Drench Hyaluronic Moisturizer",
        "ingredients_text": "Aqua, Glycerin, Niacinamide, Hydroxyethyl Urea, Sodium Hyaluronate, Sodium Hyaluronate Crosspolymer, Pentylene Glycol, Caprylic/Capric Triglyceride, Cetearyl Alcohol, Ceteareth-20, Panthenol, Allantoin, Ceramide NP, Carbomer, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Dot+Key+Water+Drench+Hyaluronic+Moisturizer",
        "amazon_in_url": "https://www.amazon.in/s?k=Dot+Key+Water+Drench+Hyaluronic+Moisturizer",
        "flipkart_url": "https://www.flipkart.com/search?q=Dot+Key+Water+Drench+Hyaluronic+Moisturizer",
    },

    # Global brands
    {
        "product_type": "moisturizer",
        "brand": "CeraVe",
        "name": "Moisturizing Cream",
        "ingredients_text": "Purified Water, Glycerin, Behentrimonium Methosulfate, Cetearyl Alcohol, Caprylic/Capric Triglyceride, Cetyl Alcohol, Ceramide NP, Ceramide AP, Ceramide EOP, Hyaluronic Acid, Niacinamide, Cholesterol, Phytosphingosine, Carbomer, Dimethicone, Sodium Lauroyl Lactylate, Sodium Hyaluronate, Xanthan Gum, Dipotassium Phosphate, Disodium EDTA, Methylparaben, Propylparaben, Phenoxyethanol",
        "amazon_url": "https://www.amazon.com/s?k=CeraVe+Moisturizing+Cream",
        "amazon_in_url": "https://www.amazon.in/s?k=CeraVe+Moisturizing+Cream",
        "flipkart_url": "https://www.flipkart.com/search?q=CeraVe+Moisturizing+Cream",
    },
    {
        "product_type": "moisturizer",
        "brand": "The Ordinary",
        "name": "Natural Moisturizing Factors + HA",
        "ingredients_text": "Aqua, Glycerin, Urea, Alanine, Arginine, Aspartic Acid, Glycine, Histidine, Isoleucine, Leucine, Lysine HCl, Methionine, Phenylalanine, Proline, Pyrrolidone Carboxylic Acid, Serine, Sodium PCA, Threonine, Tryptophan, Tyrosine, Valine, Inositol, Lactic Acid, Sodium Hyaluronate, Allantoin, Tocopherol, Xanthan Gum, Isoceteth-20, Carbomer, Dimethyl Isosorbide, Polyglyceryl-10 Stearate, Disodium EDTA, Trisodium Ethylenediamine Disuccinate, Sodium Chloride, Citric Acid, Behentrimonium Chloride, Sodium Hydroxide, Ethylhexylglycerin, Phenoxyethanol, Chlorphenesin",
        "amazon_url": "https://www.amazon.com/s?k=The+Ordinary+Natural+Moisturizing+Factors+HA",
        "amazon_in_url": "https://www.amazon.in/s?k=The+Ordinary+Natural+Moisturizing+Factors+HA",
        "flipkart_url": "https://www.flipkart.com/search?q=The+Ordinary+Natural+Moisturizing+Factors+HA",
    },
    {
        "product_type": "moisturizer",
        "brand": "La Roche-Posay",
        "name": "Toleriane Double Repair Face Moisturizer",
        "ingredients_text": "Aqua, Glycerin, Niacinamide, Dimethicone, Cetearyl Alcohol, Glyceryl Stearate, Ceramide NP, Ceramide AP, Ceramide EOP, Panthenol, Prebiotic Thermal Water, Carbomer, Sodium Hyaluronate, Disodium EDTA, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=La+Roche-Posay+Toleriane+Double+Repair+Moisturizer",
        "amazon_in_url": "https://www.amazon.in/s?k=La+Roche-Posay+Toleriane+Double+Repair+Moisturizer",
        "flipkart_url": "https://www.flipkart.com/search?q=La+Roche-Posay+Toleriane+Double+Repair+Moisturizer",
    },
    {
        "product_type": "moisturizer",
        "brand": "Cetaphil",
        "name": "Moisturizing Cream",
        "ingredients_text": "Purified Water, Glycerin, Petrolatum, Dicaprylyl Ether, Dimethicone, Glyceryl Stearate, Cetearyl Alcohol, Benzyl Alcohol, Tocopheryl Acetate, Stearoxytrimethylsilane, Stearyl Alcohol, Panthenol, Farnesol, Citric Acid, Sodium Hydroxide",
        "amazon_url": "https://www.amazon.com/s?k=Cetaphil+Moisturizing+Cream",
        "amazon_in_url": "https://www.amazon.in/s?k=Cetaphil+Moisturizing+Cream",
        "flipkart_url": "https://www.flipkart.com/search?q=Cetaphil+Moisturizing+Cream",
    },
    {
        "product_type": "moisturizer",
        "brand": "Vanicream",
        "name": "Moisturizing Skin Cream",
        "ingredients_text": "Purified Water, White Petrolatum, Sorbitol, Cetearyl Alcohol, Propylene Glycol, Ceteareth-20, Simethicone, Glyceryl Monostearate, Polyethylene Glycol Monostearate, Sorbic Acid, BHT",
        "amazon_url": "https://www.amazon.com/s?k=Vanicream+Moisturizing+Skin+Cream",
        "amazon_in_url": "https://www.amazon.in/s?k=Vanicream+Moisturizing+Skin+Cream",
        "flipkart_url": "https://www.flipkart.com/search?q=Vanicream+Moisturizing+Skin+Cream",
    },

    # ── SHAMPOO / CONDITIONER ────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "shampoo_conditioner",
        "brand": "Minimalist",
        "name": "2% Salicylic Acid Shampoo",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Sodium Cocoyl Isethionate, Glycerin, Salicylic Acid, Zinc Pyrithione, Panthenol, Niacinamide, Allantoin, Citric Acid, Sodium Benzoate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Minimalist+2%25+Salicylic+Acid+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Salicylic+Acid+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Salicylic+Acid+Shampoo",
    },
    {
        "product_type": "shampoo_conditioner",
        "brand": "WOW",
        "name": "Apple Cider Vinegar Shampoo",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Apple Cider Vinegar (Malus Domestica Fruit Water Ferment), Glycerin, Panthenol, Niacinamide, Biotin, Argan Oil (Argania Spinosa Kernel Oil), Allantoin, Citric Acid, Sodium Benzoate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=WOW+Apple+Cider+Vinegar+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=WOW+Apple+Cider+Vinegar+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=WOW+Apple+Cider+Vinegar+Shampoo",
    },
    {
        "product_type": "shampoo_conditioner",
        "brand": "Plum",
        "name": "Olive & Macadamia Healthy Hydration Shampoo",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Glycerin, Olive Oil (Olea Europaea Fruit Oil), Macadamia Oil (Macadamia Ternifolia Seed Oil), Panthenol, Allantoin, Sodium PCA, Citric Acid, Sodium Benzoate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Plum+Olive+Macadamia+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=Plum+Olive+Macadamia+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=Plum+Olive+Macadamia+Shampoo",
    },
    {
        "product_type": "shampoo_conditioner",
        "brand": "mCaffeine",
        "name": "Coffee Shampoo",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Coffea Arabica (Coffee) Seed Extract, Glycerin, Panthenol, Caffeine, Niacinamide, Allantoin, Citric Acid, Sodium Benzoate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=mCaffeine+Coffee+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=mCaffeine+Coffee+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=mCaffeine+Coffee+Shampoo",
    },
    {
        "product_type": "shampoo_conditioner",
        "brand": "Himalaya",
        "name": "Gentle Daily Care Protein Shampoo",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Chickpea (Cicer Arietinum) Seed Protein, Glycerin, Panthenol, Wheat Germ Oil (Triticum Vulgare Germ Oil), Citric Acid, Sodium Chloride, Sodium Benzoate, Phenoxyethanol",
        "amazon_url": "https://www.amazon.com/s?k=Himalaya+Gentle+Daily+Care+Protein+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=Himalaya+Gentle+Daily+Care+Protein+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=Himalaya+Gentle+Daily+Care+Protein+Shampoo",
    },

    # Global brands
    {
        "product_type": "shampoo_conditioner",
        "brand": "Vanicream",
        "name": "Free & Clear Shampoo",
        "ingredients_text": "Purified Water, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Glycerin, Sodium Chloride, Panthenol, Citric Acid, Sodium Benzoate",
        "amazon_url": "https://www.amazon.com/s?k=Vanicream+Free+Clear+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=Vanicream+Free+Clear+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=Vanicream+Free+Clear+Shampoo",
    },
    {
        "product_type": "shampoo_conditioner",
        "brand": "Dove",
        "name": "Sensitive Skin Shampoo",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfate, Sodium Laureth Sulfate, Dimethicone, Glycerin, Cocamidopropyl Betaine, Glycol Distearate, Sodium Chloride, Sodium Benzoate, Tetrasodium EDTA, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Dove+Sensitive+Skin+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=Dove+Sensitive+Skin+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=Dove+Sensitive+Skin+Shampoo",
    },
    {
        "product_type": "shampoo_conditioner",
        "brand": "The Ordinary",
        "name": "Sulphate-Free Cleanser for Hair & Body",
        "ingredients_text": "Aqua, Sodium Cocoyl Isethionate, Cocamidopropyl Betaine, Glycerin, Lauryl Glucoside, Panthenol, Niacinamide, Allantoin, Sodium PCA, Sodium Lauroyl Methyl Isethionate, Citric Acid, Sodium Benzoate, Phenoxyethanol",
        "amazon_url": "https://www.amazon.com/s?k=The+Ordinary+Sulphate+Free+Cleanser",
        "amazon_in_url": "https://www.amazon.in/s?k=The+Ordinary+Sulphate+Free+Cleanser",
        "flipkart_url": "https://www.flipkart.com/search?q=The+Ordinary+Sulphate+Free+Cleanser",
    },
    {
        "product_type": "shampoo_conditioner",
        "brand": "Head & Shoulders",
        "name": "Sensitive Scalp Shampoo",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfate, Sodium Laureth Sulfate, Glycerin, Zinc Pyrithione, Cocamidopropyl Betaine, Sodium Xylenesulfonate, Dimethicone, Sodium Citrate, Citric Acid, Sodium Benzoate, Sodium Chloride, Tetrasodium EDTA",
        "amazon_url": "https://www.amazon.com/s?k=Head+Shoulders+Sensitive+Scalp+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=Head+Shoulders+Sensitive+Scalp+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=Head+Shoulders+Sensitive+Scalp+Shampoo",
    },
    {
        "product_type": "shampoo_conditioner",
        "brand": "Neutrogena",
        "name": "T/Sal Therapeutic Shampoo",
        "ingredients_text": "Purified Water, Salicylic Acid, Sodium Lauryl Sulfate, Cocamide DEA, Sodium Chloride, Lauramide DEA, Sodium Laureth Sulfate, PEG-8 Distearate, Glycol Distearate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Neutrogena+T+Sal+Therapeutic+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=Neutrogena+T+Sal+Therapeutic+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=Neutrogena+T+Sal+Therapeutic+Shampoo",
    },

    # ── SUNSCREEN ────────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "sunscreen",
        "brand": "Minimalist",
        "name": "SPF 50 Sunscreen",
        "ingredients_text": "Aqua, Homosalate, Ethylhexyl Salicylate, Octocrylene, Butyl Methoxydibenzoylmethane, Glycerin, Niacinamide, Pentylene Glycol, Dicaprylyl Carbonate, Cetearyl Alcohol, Ceteareth-20, Panthenol, Allantoin, Sodium Hyaluronate, Tocopheryl Acetate, Carbomer, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Minimalist+SPF+50+Sunscreen",
        "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+SPF+50+Sunscreen",
        "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+SPF+50+Sunscreen",
    },
    {
        "product_type": "sunscreen",
        "brand": "Dot & Key",
        "name": "Mineral Matte Sunscreen SPF 50",
        "ingredients_text": "Aqua, Zinc Oxide, Titanium Dioxide, Glycerin, Caprylic/Capric Triglyceride, Cetearyl Alcohol, Niacinamide, Panthenol, Allantoin, Sodium Hyaluronate, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Dot+Key+Mineral+Matte+Sunscreen+SPF+50",
        "amazon_in_url": "https://www.amazon.in/s?k=Dot+Key+Mineral+Matte+Sunscreen+SPF+50",
        "flipkart_url": "https://www.flipkart.com/search?q=Dot+Key+Mineral+Matte+Sunscreen+SPF+50",
    },
    {
        "product_type": "sunscreen",
        "brand": "Plum",
        "name": "Green Tea Renewed Clarity SPF 35",
        "ingredients_text": "Aqua, Homosalate, Ethylhexyl Salicylate, Glycerin, Camellia Sinensis Leaf Extract, Niacinamide, Panthenol, Allantoin, Caprylic/Capric Triglyceride, Cetearyl Alcohol, Sodium Hyaluronate, Carbomer, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Plum+Green+Tea+Sunscreen+SPF+35",
        "amazon_in_url": "https://www.amazon.in/s?k=Plum+Green+Tea+Sunscreen+SPF+35",
        "flipkart_url": "https://www.flipkart.com/search?q=Plum+Green+Tea+Sunscreen+SPF+35",
    },
    {
        "product_type": "sunscreen",
        "brand": "The Derma Co",
        "name": "1% Hyaluronic Sunscreen SPF 50",
        "ingredients_text": "Aqua, Homosalate, Ethylhexyl Salicylate, Octocrylene, Glycerin, Sodium Hyaluronate, Niacinamide, Pentylene Glycol, Caprylic/Capric Triglyceride, Cetearyl Alcohol, Panthenol, Allantoin, Carbomer, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=The+Derma+Co+Hyaluronic+Sunscreen+SPF+50",
        "amazon_in_url": "https://www.amazon.in/s?k=The+Derma+Co+Hyaluronic+Sunscreen+SPF+50",
        "flipkart_url": "https://www.flipkart.com/search?q=The+Derma+Co+Hyaluronic+Sunscreen+SPF+50",
    },
    {
        "product_type": "sunscreen",
        "brand": "Re'equil",
        "name": "Oxybenzone & OMC Free Sunscreen SPF 50",
        "ingredients_text": "Aqua, Uvinul A Plus (Diethylamino Hydroxybenzoyl Hexyl Benzoate), Tinosorb S (Bis-Ethylhexyloxyphenol Methoxyphenyl Triazine), Titanium Dioxide, Glycerin, Caprylic/Capric Triglyceride, Cetearyl Alcohol, Niacinamide, Panthenol, Allantoin, Carbomer, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Re+equil+Oxybenzone+Free+Sunscreen+SPF+50",
        "amazon_in_url": "https://www.amazon.in/s?k=Re+equil+Oxybenzone+Free+Sunscreen+SPF+50",
        "flipkart_url": "https://www.flipkart.com/search?q=Re+equil+Oxybenzone+Free+Sunscreen+SPF+50",
    },

    # Global brands
    {
        "product_type": "sunscreen",
        "brand": "EltaMD",
        "name": "UV Clear Broad-Spectrum SPF 46",
        "ingredients_text": "Active Ingredients: Zinc Oxide 9.0%, Octinoxate 7.5%. Inactive Ingredients: Water, Niacinamide, Lactic Acid, Sodium Hyaluronate, Tocopheryl Acetate, Cetyl Alcohol, Stearic Acid, Glycerin, Dimethicone, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=EltaMD+UV+Clear+SPF+46",
        "amazon_in_url": "https://www.amazon.in/s?k=EltaMD+UV+Clear+SPF+46",
        "flipkart_url": "https://www.flipkart.com/search?q=EltaMD+UV+Clear+SPF+46",
    },
    {
        "product_type": "sunscreen",
        "brand": "La Roche-Posay",
        "name": "Anthelios Mineral Sunscreen SPF 50",
        "ingredients_text": "Active: Titanium Dioxide 6%, Zinc Oxide 10%. Inactive: Aqua, Glycerin, Silica, Niacinamide, Panthenol, Dimethicone, Caprylic/Capric Triglyceride, Sodium Hyaluronate, Tocopheryl Acetate, Carbomer, Disodium EDTA, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=La+Roche-Posay+Anthelios+Mineral+SPF+50",
        "amazon_in_url": "https://www.amazon.in/s?k=La+Roche-Posay+Anthelios+Mineral+SPF+50",
        "flipkart_url": "https://www.flipkart.com/search?q=La+Roche-Posay+Anthelios+Mineral+SPF+50",
    },
    {
        "product_type": "sunscreen",
        "brand": "CeraVe",
        "name": "Hydrating Mineral Sunscreen SPF 30",
        "ingredients_text": "Active Ingredients: Titanium Dioxide 5.1%, Zinc Oxide 4.8%. Inactive Ingredients: Aqua, Glycerin, Niacinamide, Ceramide NP, Ceramide AP, Ceramide EOP, Hyaluronic Acid, Dimethicone, Caprylic/Capric Triglyceride, Cetearyl Alcohol, Sodium Lauroyl Lactylate, Disodium EDTA, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=CeraVe+Hydrating+Mineral+Sunscreen+SPF+30",
        "amazon_in_url": "https://www.amazon.in/s?k=CeraVe+Hydrating+Mineral+Sunscreen+SPF+30",
        "flipkart_url": "https://www.flipkart.com/search?q=CeraVe+Hydrating+Mineral+Sunscreen+SPF+30",
    },
    {
        "product_type": "sunscreen",
        "brand": "Vanicream",
        "name": "Mineral Sunscreen SPF 50",
        "ingredients_text": "Active Ingredients: Zinc Oxide 20%. Inactive Ingredients: Purified Water, Glycerin, Dimethicone, Caprylic/Capric Triglyceride, Cetearyl Alcohol, Sodium Hyaluronate, Panthenol, Allantoin, Citric Acid, Sodium Citrate, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=Vanicream+Mineral+Sunscreen+SPF+50",
        "amazon_in_url": "https://www.amazon.in/s?k=Vanicream+Mineral+Sunscreen+SPF+50",
        "flipkart_url": "https://www.flipkart.com/search?q=Vanicream+Mineral+Sunscreen+SPF+50",
    },
    {
        "product_type": "sunscreen",
        "brand": "Neutrogena",
        "name": "Sheer Zinc Mineral Sunscreen SPF 50",
        "ingredients_text": "Active: Zinc Oxide 21.6%. Inactive: Water, C12-15 Alkyl Benzoate, Caprylyl Methicone, Dimethicone, Glycerin, Niacinamide, Panthenol, Sodium Hyaluronate, Cetyl PEG/PPG-10/1 Dimethicone, Dimethicone Crosspolymer, Glyceryl Stearate, PEG-100 Stearate, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=Neutrogena+Sheer+Zinc+Mineral+Sunscreen+SPF+50",
        "amazon_in_url": "https://www.amazon.in/s?k=Neutrogena+Sheer+Zinc+Mineral+Sunscreen+SPF+50",
        "flipkart_url": "https://www.flipkart.com/search?q=Neutrogena+Sheer+Zinc+Mineral+Sunscreen+SPF+50",
    },

    # ── BODY WASH ────────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "body_wash",
        "brand": "Himalaya",
        "name": "Moisturizing Aloe Vera Body Wash",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, Aloe Barbadensis Leaf Juice, Glycerin, Panthenol, Allantoin, Citric Acid, Sodium Chloride, Sodium Benzoate, Phenoxyethanol",
        "amazon_url": "https://www.amazon.com/s?k=Himalaya+Moisturizing+Aloe+Vera+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Himalaya+Moisturizing+Aloe+Vera+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Himalaya+Moisturizing+Aloe+Vera+Body+Wash",
    },
    {
        "product_type": "body_wash",
        "brand": "Mamaearth",
        "name": "Ubtan Body Wash",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Glycerin, Turmeric Extract (Curcuma Longa), Saffron Extract, Sandalwood Oil, Panthenol, Allantoin, Citric Acid, Sodium Benzoate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Mamaearth+Ubtan+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Mamaearth+Ubtan+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Mamaearth+Ubtan+Body+Wash",
    },
    {
        "product_type": "body_wash",
        "brand": "WOW",
        "name": "Skin Charge Body Wash",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Glycerin, Vitamin C (Ascorbyl Glucoside), Niacinamide, Panthenol, Allantoin, Citric Acid, Sodium Benzoate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=WOW+Skin+Charge+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=WOW+Skin+Charge+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=WOW+Skin+Charge+Body+Wash",
    },
    {
        "product_type": "body_wash",
        "brand": "Plum",
        "name": "BodyLovin' Vanilla Vibes Body Wash",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Glycerin, Vanilla Planifolia Fruit Extract, Panthenol, Allantoin, Tocopheryl Acetate, Sodium PCA, Citric Acid, Sodium Benzoate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Plum+BodyLovin+Vanilla+Vibes+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Plum+BodyLovin+Vanilla+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Plum+BodyLovin+Vanilla+Body+Wash",
    },
    {
        "product_type": "body_wash",
        "brand": "mCaffeine",
        "name": "Coffee Body Wash",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Coffea Arabica Seed Extract, Glycerin, Caffeine, Panthenol, Allantoin, Niacinamide, Citric Acid, Sodium Benzoate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=mCaffeine+Coffee+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=mCaffeine+Coffee+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=mCaffeine+Coffee+Body+Wash",
    },

    # Global brands
    {
        "product_type": "body_wash",
        "brand": "CeraVe",
        "name": "Hydrating Cleanser Body Wash",
        "ingredients_text": "Aqua, Glycerin, Sodium Lauryl Sulfate, Cocamidopropyl Hydroxysultaine, Niacinamide, Ceramide NP, Ceramide AP, Ceramide EOP, Hyaluronic Acid, Panthenol, Cholesterol, Phytosphingosine, Sodium Lauroyl Lactylate, Carbomer, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=CeraVe+Hydrating+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=CeraVe+Hydrating+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=CeraVe+Hydrating+Body+Wash",
    },
    {
        "product_type": "body_wash",
        "brand": "Cetaphil",
        "name": "Gentle Skin Cleanser Body Wash",
        "ingredients_text": "Purified Water, Glycerin, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, Panthenol, Niacinamide, Allantoin, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Cetaphil+Gentle+Skin+Cleanser+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Cetaphil+Gentle+Skin+Cleanser+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Cetaphil+Gentle+Skin+Cleanser+Body+Wash",
    },
    {
        "product_type": "body_wash",
        "brand": "Vanicream",
        "name": "Gentle Body Wash",
        "ingredients_text": "Purified Water, Glycerin, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Sodium Cocoyl Isethionate, Panthenol, Allantoin, Sodium PCA, Citric Acid, Sodium Benzoate",
        "amazon_url": "https://www.amazon.com/s?k=Vanicream+Gentle+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Vanicream+Gentle+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Vanicream+Gentle+Body+Wash",
    },
    {
        "product_type": "body_wash",
        "brand": "Dove",
        "name": "Sensitive Skin Body Wash",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfate, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Glycerin, Lauric Acid, Glycol Distearate, Sodium Benzoate, Tetrasodium EDTA, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Dove+Sensitive+Skin+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Dove+Sensitive+Skin+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Dove+Sensitive+Skin+Body+Wash",
    },
    {
        "product_type": "body_wash",
        "brand": "Aveeno",
        "name": "Daily Moisturizing Body Wash",
        "ingredients_text": "Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Glycerin, Colloidal Oatmeal, Dimethicone, Panthenol, Allantoin, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Aveeno+Daily+Moisturizing+Body+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Aveeno+Daily+Moisturizing+Body+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Aveeno+Daily+Moisturizing+Body+Wash",
    },

    # ── FOUNDATION ───────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "foundation",
        "brand": "Lakme",
        "name": "9to5 Primer + Matte Perfect Cover Foundation",
        "ingredients_text": "Aqua, Cyclopentasiloxane, Titanium Dioxide, Dimethicone, Glycerin, Niacinamide, Iron Oxides, Isononyl Isononanoate, Cetyl PEG/PPG-10/1 Dimethicone, Trimethylsiloxysilicate, Phenyl Trimethicone, Panthenol, Allantoin, Sodium Hyaluronate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Lakme+9to5+Primer+Matte+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=Lakme+9to5+Primer+Matte+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=Lakme+9to5+Primer+Matte+Foundation",
    },
    {
        "product_type": "foundation",
        "brand": "Colorbar",
        "name": "Full Cover Makeup Foundation",
        "ingredients_text": "Aqua, Cyclopentasiloxane, Titanium Dioxide, Dimethicone, Glycerin, Iron Oxides, Isononyl Isononanoate, Niacinamide, Panthenol, Allantoin, Cetyl PEG/PPG-10/1 Dimethicone, Trimethylsiloxysilicate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Colorbar+Full+Cover+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=Colorbar+Full+Cover+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=Colorbar+Full+Cover+Foundation",
    },
    {
        "product_type": "foundation",
        "brand": "Faces Canada",
        "name": "Ultime Pro Longwear Foundation",
        "ingredients_text": "Aqua, Cyclopentasiloxane, Titanium Dioxide, Dimethicone, Glycerin, Iron Oxides, Niacinamide, Panthenol, Tocopheryl Acetate, Allantoin, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Faces+Canada+Ultime+Pro+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=Faces+Canada+Ultime+Pro+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=Faces+Canada+Ultime+Pro+Foundation",
    },
    {
        "product_type": "foundation",
        "brand": "Mamaearth",
        "name": "Moisture Matte Foundation",
        "ingredients_text": "Aqua, Titanium Dioxide, Cyclopentasiloxane, Dimethicone, Glycerin, Iron Oxides, Niacinamide, Turmeric Extract (Curcuma Longa), Aloe Vera Leaf Juice, Panthenol, Allantoin, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Mamaearth+Moisture+Matte+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=Mamaearth+Moisture+Matte+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=Mamaearth+Moisture+Matte+Foundation",
    },
    {
        "product_type": "foundation",
        "brand": "Insight Cosmetics",
        "name": "Full Coverage Foundation",
        "ingredients_text": "Aqua, Cyclopentasiloxane, Titanium Dioxide, Dimethicone, Glycerin, Iron Oxides, Niacinamide, Panthenol, Allantoin, Sodium Hyaluronate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Insight+Cosmetics+Full+Coverage+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=Insight+Cosmetics+Full+Coverage+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=Insight+Cosmetics+Full+Coverage+Foundation",
    },

    # Global brands
    {
        "product_type": "foundation",
        "brand": "BareMinerals",
        "name": "ORIGINAL Foundation SPF 15",
        "ingredients_text": "Bismuth Oxychloride, Titanium Dioxide, Zinc Oxide, Mica, Lauroyl Lysine",
        "amazon_url": "https://www.amazon.com/s?k=BareMinerals+ORIGINAL+Foundation+SPF+15",
        "amazon_in_url": "https://www.amazon.in/s?k=BareMinerals+ORIGINAL+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=BareMinerals+ORIGINAL+Foundation",
    },
    {
        "product_type": "foundation",
        "brand": "ILIA",
        "name": "True Skin Serum Foundation",
        "ingredients_text": "Aqua, Cyclopentasiloxane, Titanium Dioxide, Glycerin, Aloe Barbadensis Leaf Juice, Niacinamide, Iron Oxides, Jojoba Oil (Simmondsia Chinensis Seed Oil), Rosehip Oil (Rosa Canina Fruit Oil), Sodium Hyaluronate, Panthenol, Allantoin, Tocopherol, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=ILIA+True+Skin+Serum+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=ILIA+True+Skin+Serum+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=ILIA+True+Skin+Serum+Foundation",
    },
    {
        "product_type": "foundation",
        "brand": "100% Pure",
        "name": "Fruit Pigmented Full Coverage Water Foundation",
        "ingredients_text": "Aqua, Aloe Barbadensis Leaf Juice, Titanium Dioxide, Glycerin, Niacinamide, Fruit Pigments (Coffea Arabica, Beet, Cranberry), Jojoba Oil, Panthenol, Allantoin, Tocopherol, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=100+Pure+Fruit+Pigmented+Water+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=100+Pure+Fruit+Pigmented+Water+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=100+Pure+Fruit+Pigmented+Water+Foundation",
    },
    {
        "product_type": "foundation",
        "brand": "W3LL PEOPLE",
        "name": "Bio Correct Full Coverage Foundation",
        "ingredients_text": "Aqua, Titanium Dioxide, Zinc Oxide, Glycerin, Caprylic/Capric Triglyceride, Iron Oxides, Jojoba Oil, Niacinamide, Tocopherol, Panthenol, Allantoin, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=W3LL+PEOPLE+Bio+Correct+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=W3LL+PEOPLE+Bio+Correct+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=W3LL+PEOPLE+Bio+Correct+Foundation",
    },
    {
        "product_type": "foundation",
        "brand": "Kjaer Weis",
        "name": "Invisible Touch Liquid Foundation",
        "ingredients_text": "Aqua, Titanium Dioxide, Glycerin, Caprylic/Capric Triglyceride, Iron Oxides, Jojoba Oil (Simmondsia Chinensis Seed Oil), Rosehip Oil (Rosa Canina Fruit Oil), Niacinamide, Tocopherol, Panthenol, Allantoin, Sodium Hyaluronate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Kjaer+Weis+Invisible+Touch+Foundation",
        "amazon_in_url": "https://www.amazon.in/s?k=Kjaer+Weis+Invisible+Touch+Foundation",
        "flipkart_url": "https://www.flipkart.com/search?q=Kjaer+Weis+Invisible+Touch+Foundation",
    },

    # ── LIP PRODUCT ──────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "lip_product",
        "brand": "Plum",
        "name": "Matte In Heaven Liquid Lipstick",
        "ingredients_text": "Isododecane, Trimethylsiloxysilicate, Dimethicone, Isononyl Isononanoate, Nylon-12, Iron Oxides, Titanium Dioxide, Tocopheryl Acetate, Vitamin E, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Plum+Matte+In+Heaven+Liquid+Lipstick",
        "amazon_in_url": "https://www.amazon.in/s?k=Plum+Matte+In+Heaven+Liquid+Lipstick",
        "flipkart_url": "https://www.flipkart.com/search?q=Plum+Matte+In+Heaven+Liquid+Lipstick",
    },
    {
        "product_type": "lip_product",
        "brand": "mCaffeine",
        "name": "Coffee Lip Balm",
        "ingredients_text": "Ricinus Communis (Castor) Seed Oil, Cera Alba (Beeswax), Cocos Nucifera (Coconut) Oil, Persea Gratissima (Avocado) Oil, Coffea Arabica (Coffee) Seed Extract, Tocopherol, Theobroma Cacao (Cocoa) Seed Butter",
        "amazon_url": "https://www.amazon.com/s?k=mCaffeine+Coffee+Lip+Balm",
        "amazon_in_url": "https://www.amazon.in/s?k=mCaffeine+Coffee+Lip+Balm",
        "flipkart_url": "https://www.flipkart.com/search?q=mCaffeine+Coffee+Lip+Balm",
    },
    {
        "product_type": "lip_product",
        "brand": "Colorbar",
        "name": "Velvet Matte Lipstick",
        "ingredients_text": "Isododecane, Trimethylsiloxysilicate, Dimethicone, Isononyl Isononanoate, Nylon-12, Iron Oxides, Titanium Dioxide, Tocopheryl Acetate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Colorbar+Velvet+Matte+Lipstick",
        "amazon_in_url": "https://www.amazon.in/s?k=Colorbar+Velvet+Matte+Lipstick",
        "flipkart_url": "https://www.flipkart.com/search?q=Colorbar+Velvet+Matte+Lipstick",
    },
    {
        "product_type": "lip_product",
        "brand": "Biotique",
        "name": "Natural Lip Butter",
        "ingredients_text": "Theobroma Cacao (Cocoa) Seed Butter, Ricinus Communis (Castor) Seed Oil, Cera Alba (Beeswax), Cocos Nucifera (Coconut) Oil, Tocopherol, Vitamin E Acetate",
        "amazon_url": "https://www.amazon.com/s?k=Biotique+Natural+Lip+Butter",
        "amazon_in_url": "https://www.amazon.in/s?k=Biotique+Natural+Lip+Butter",
        "flipkart_url": "https://www.flipkart.com/search?q=Biotique+Natural+Lip+Butter",
    },
    {
        "product_type": "lip_product",
        "brand": "Lakme",
        "name": "9to5 Weightless Matte Mousse Lip Color",
        "ingredients_text": "Aqua, Dimethicone, Isododecane, Glycerin, Nylon-12, Iron Oxides, Titanium Dioxide, Trimethylsiloxysilicate, Tocopheryl Acetate, Allantoin, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Lakme+9to5+Matte+Mousse+Lip+Color",
        "amazon_in_url": "https://www.amazon.in/s?k=Lakme+9to5+Matte+Mousse+Lip+Color",
        "flipkart_url": "https://www.flipkart.com/search?q=Lakme+9to5+Matte+Mousse+Lip+Color",
    },

    # Global brands
    {
        "product_type": "lip_product",
        "brand": "ILIA",
        "name": "Color Block Lipstick",
        "ingredients_text": "Ricinus Communis (Castor) Seed Oil, Caprylic/Capric Triglyceride, Candelilla/Jojoba/Rice Bran Polyglyceryl-3 Esters, Polyglyceryl-2 Triisostearate, Iron Oxides, Mica, Tocopherol, Rosmarinus Officinalis (Rosemary) Leaf Extract",
        "amazon_url": "https://www.amazon.com/s?k=ILIA+Color+Block+Lipstick",
        "amazon_in_url": "https://www.amazon.in/s?k=ILIA+Color+Block+Lipstick",
        "flipkart_url": "https://www.flipkart.com/search?q=ILIA+Color+Block+Lipstick",
    },
    {
        "product_type": "lip_product",
        "brand": "RMS Beauty",
        "name": "Wild With Desire Lipstick",
        "ingredients_text": "Ricinus Communis (Castor) Seed Oil, Cera Alba (Beeswax), Caprylic/Capric Triglyceride, Iron Oxides, Mica, Tocopherol, Cocos Nucifera (Coconut) Oil, Theobroma Cacao (Cocoa) Seed Butter",
        "amazon_url": "https://www.amazon.com/s?k=RMS+Beauty+Wild+With+Desire+Lipstick",
        "amazon_in_url": "https://www.amazon.in/s?k=RMS+Beauty+Wild+With+Desire+Lipstick",
        "flipkart_url": "https://www.flipkart.com/search?q=RMS+Beauty+Wild+With+Desire+Lipstick",
    },
    {
        "product_type": "lip_product",
        "brand": "Burt's Bees",
        "name": "Lip Butter",
        "ingredients_text": "Cera Alba (Beeswax), Cocos Nucifera (Coconut) Oil, Simmondsia Chinensis (Jojoba) Seed Oil, Theobroma Cacao (Cocoa) Seed Butter, Tocopherol, Rosmarinus Officinalis (Rosemary) Leaf Extract",
        "amazon_url": "https://www.amazon.com/s?k=Burt%27s+Bees+Lip+Butter",
        "amazon_in_url": "https://www.amazon.in/s?k=Burts+Bees+Lip+Butter",
        "flipkart_url": "https://www.flipkart.com/search?q=Burts+Bees+Lip+Butter",
    },
    {
        "product_type": "lip_product",
        "brand": "100% Pure",
        "name": "Fruit Pigmented Cocoa Butter Matte Lipstick",
        "ingredients_text": "Ricinus Communis (Castor) Seed Oil, Theobroma Cacao (Cocoa) Seed Butter, Carnauba Wax, Candelilla Wax, Fruit Pigments, Tocopherol, Cocos Nucifera (Coconut) Oil",
        "amazon_url": "https://www.amazon.com/s?k=100+Pure+Fruit+Pigmented+Cocoa+Butter+Lipstick",
        "amazon_in_url": "https://www.amazon.in/s?k=100+Pure+Fruit+Pigmented+Lipstick",
        "flipkart_url": "https://www.flipkart.com/search?q=100+Pure+Fruit+Pigmented+Lipstick",
    },
    {
        "product_type": "lip_product",
        "brand": "EltaMD",
        "name": "UV Lip Balm SPF 36",
        "ingredients_text": "Active: Zinc Oxide 9%, Octinoxate 7.5%. Inactive: Aqua, Glycerin, Aloe Barbadensis Leaf Juice, Tocopheryl Acetate, Panthenol, Allantoin, Caprylic/Capric Triglyceride, Beeswax, Phenoxyethanol",
        "amazon_url": "https://www.amazon.com/s?k=EltaMD+UV+Lip+Balm+SPF+36",
        "amazon_in_url": "https://www.amazon.in/s?k=EltaMD+UV+Lip+Balm+SPF+36",
        "flipkart_url": "https://www.flipkart.com/search?q=EltaMD+UV+Lip+Balm+SPF+36",
    },

    # ── EYE MAKEUP ───────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "eye_makeup",
        "brand": "Lakme",
        "name": "Eyeconic Kajal",
        "ingredients_text": "Synthetic Wax, Isododecane, Cyclopentasiloxane, Iron Oxides (CI 77499), Trimethylsiloxysilicate, Nylon-12, Tocopheryl Acetate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Lakme+Eyeconic+Kajal",
        "amazon_in_url": "https://www.amazon.in/s?k=Lakme+Eyeconic+Kajal",
        "flipkart_url": "https://www.flipkart.com/search?q=Lakme+Eyeconic+Kajal",
    },
    {
        "product_type": "eye_makeup",
        "brand": "Colorbar",
        "name": "Just Mascara",
        "ingredients_text": "Aqua, Synthetic Wax, Glycerin, Iron Oxides (CI 77499), Acacia Senegal Gum, Sodium Carboxymethylcellulose, Panthenol, Allantoin, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Colorbar+Just+Mascara",
        "amazon_in_url": "https://www.amazon.in/s?k=Colorbar+Just+Mascara",
        "flipkart_url": "https://www.flipkart.com/search?q=Colorbar+Just+Mascara",
    },
    {
        "product_type": "eye_makeup",
        "brand": "Plum",
        "name": "Flutterbye Lengthening Mascara",
        "ingredients_text": "Aqua, Synthetic Wax, Glycerin, Iron Oxides (CI 77499), Acacia Senegal Gum, Panthenol, Allantoin, Tocopheryl Acetate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Plum+Flutterbye+Mascara",
        "amazon_in_url": "https://www.amazon.in/s?k=Plum+Flutterbye+Mascara",
        "flipkart_url": "https://www.flipkart.com/search?q=Plum+Flutterbye+Mascara",
    },
    {
        "product_type": "eye_makeup",
        "brand": "Mamaearth",
        "name": "Volumizing Mascara",
        "ingredients_text": "Aqua, Synthetic Wax, Glycerin, Iron Oxides (CI 77499), Bamboo Extract, Panthenol, Allantoin, Tocopheryl Acetate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Mamaearth+Volumizing+Mascara",
        "amazon_in_url": "https://www.amazon.in/s?k=Mamaearth+Volumizing+Mascara",
        "flipkart_url": "https://www.flipkart.com/search?q=Mamaearth+Volumizing+Mascara",
    },
    {
        "product_type": "eye_makeup",
        "brand": "Faces Canada",
        "name": "Magneteyes Kajal",
        "ingredients_text": "Synthetic Wax, Isododecane, Cyclopentasiloxane, Iron Oxides (CI 77499), Trimethylsiloxysilicate, Nylon-12, Tocopheryl Acetate, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Faces+Canada+Magneteyes+Kajal",
        "amazon_in_url": "https://www.amazon.in/s?k=Faces+Canada+Magneteyes+Kajal",
        "flipkart_url": "https://www.flipkart.com/search?q=Faces+Canada+Magneteyes+Kajal",
    },

    # Global brands
    {
        "product_type": "eye_makeup",
        "brand": "ILIA",
        "name": "Limitless Lash Mascara",
        "ingredients_text": "Aqua, Synthetic Beeswax, Glycerin, Iron Oxides (CI 77499), Acacia Senegal Gum, Panthenol, Tocopherol, Allantoin, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=ILIA+Limitless+Lash+Mascara",
        "amazon_in_url": "https://www.amazon.in/s?k=ILIA+Limitless+Lash+Mascara",
        "flipkart_url": "https://www.flipkart.com/search?q=ILIA+Limitless+Lash+Mascara",
    },
    {
        "product_type": "eye_makeup",
        "brand": "100% Pure",
        "name": "Fruit Pigmented Mascara",
        "ingredients_text": "Aqua, Synthetic Wax, Iron Oxides (CI 77499), Fruit Pigments, Panthenol, Allantoin, Tocopherol, Acacia Senegal Gum, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=100+Pure+Fruit+Pigmented+Mascara",
        "amazon_in_url": "https://www.amazon.in/s?k=100+Pure+Fruit+Pigmented+Mascara",
        "flipkart_url": "https://www.flipkart.com/search?q=100+Pure+Fruit+Pigmented+Mascara",
    },
    {
        "product_type": "eye_makeup",
        "brand": "Kosas",
        "name": "The Big Clean Mascara",
        "ingredients_text": "Aqua, Synthetic Beeswax, Glycerin, Iron Oxides (CI 77499), Acacia Senegal Gum, Niacinamide, Panthenol, Tocopherol, Allantoin, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Kosas+The+Big+Clean+Mascara",
        "amazon_in_url": "https://www.amazon.in/s?k=Kosas+The+Big+Clean+Mascara",
        "flipkart_url": "https://www.flipkart.com/search?q=Kosas+The+Big+Clean+Mascara",
    },
    {
        "product_type": "eye_makeup",
        "brand": "W3LL PEOPLE",
        "name": "Expressionist Pro Mascara",
        "ingredients_text": "Aqua, Synthetic Beeswax, Glycerin, Iron Oxides (CI 77499), Acacia Senegal Gum, Panthenol, Tocopherol, Allantoin, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=W3LL+PEOPLE+Expressionist+Pro+Mascara",
        "amazon_in_url": "https://www.amazon.in/s?k=W3LL+PEOPLE+Expressionist+Pro+Mascara",
        "flipkart_url": "https://www.flipkart.com/search?q=W3LL+PEOPLE+Expressionist+Pro+Mascara",
    },
    {
        "product_type": "eye_makeup",
        "brand": "RMS Beauty",
        "name": "Volumizing Clean Mascara",
        "ingredients_text": "Aqua, Synthetic Beeswax, Iron Oxides (CI 77499), Panthenol, Tocopherol, Allantoin, Glycerin, Acacia Senegal Gum, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=RMS+Beauty+Volumizing+Clean+Mascara",
        "amazon_in_url": "https://www.amazon.in/s?k=RMS+Beauty+Volumizing+Clean+Mascara",
        "flipkart_url": "https://www.flipkart.com/search?q=RMS+Beauty+Volumizing+Clean+Mascara",
    },

    # ── DEODORANT ────────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "deodorant",
        "brand": "Himalaya",
        "name": "Sensitive Skin Deodorant Roll-On",
        "ingredients_text": "Aqua, Propylene Glycol, Glycerin, Aloe Barbadensis Leaf Extract, Menthol, Panthenol, Allantoin, Lactic Acid, Sodium Benzoate, Potassium Sorbate",
        "amazon_url": "https://www.amazon.com/s?k=Himalaya+Sensitive+Skin+Deodorant",
        "amazon_in_url": "https://www.amazon.in/s?k=Himalaya+Sensitive+Skin+Deodorant",
        "flipkart_url": "https://www.flipkart.com/search?q=Himalaya+Sensitive+Skin+Deodorant",
    },
    {
        "product_type": "deodorant",
        "brand": "Nivea",
        "name": "Sensitive Protect Roll-On",
        "ingredients_text": "Aqua, Aluminum Chlorohydrate, Propylene Glycol, Glycerin, Allantoin, Panthenol, Chamomile Extract (Matricaria Chamomilla), Sodium Stearate, Sodium Benzoate",
        "amazon_url": "https://www.amazon.com/s?k=Nivea+Sensitive+Protect+Roll-On",
        "amazon_in_url": "https://www.amazon.in/s?k=Nivea+Sensitive+Protect+Roll-On",
        "flipkart_url": "https://www.flipkart.com/search?q=Nivea+Sensitive+Protect+Roll-On",
    },
    {
        "product_type": "deodorant",
        "brand": "Bella Vita",
        "name": "Organic Deo Spray",
        "ingredients_text": "Aqua, Alcohol Denat., Glycerin, Aloe Barbadensis Leaf Juice, Witch Hazel Extract (Hamamelis Virginiana), Panthenol, Allantoin, Lactic Acid, Sodium Benzoate, Potassium Sorbate",
        "amazon_url": "https://www.amazon.com/s?k=Bella+Vita+Organic+Deo+Spray",
        "amazon_in_url": "https://www.amazon.in/s?k=Bella+Vita+Organic+Deo+Spray",
        "flipkart_url": "https://www.flipkart.com/search?q=Bella+Vita+Organic+Deo+Spray",
    },
    {
        "product_type": "deodorant",
        "brand": "Yardley",
        "name": "English Lavender Deodorant Spray",
        "ingredients_text": "Alcohol Denat., Aqua, Butane, Isobutane, Propane, Glycerin, Panthenol, Allantoin, Lavandula Angustifolia (Lavender) Oil",
        "amazon_url": "https://www.amazon.com/s?k=Yardley+English+Lavender+Deodorant",
        "amazon_in_url": "https://www.amazon.in/s?k=Yardley+English+Lavender+Deodorant",
        "flipkart_url": "https://www.flipkart.com/search?q=Yardley+English+Lavender+Deodorant",
    },
    {
        "product_type": "deodorant",
        "brand": "Engage",
        "name": "Spell Deodorant For Women",
        "ingredients_text": "Alcohol Denat., Aqua, Butane, Isobutane, Propane, Glycerin, Panthenol, Allantoin, Tocopheryl Acetate, Phenoxyethanol",
        "amazon_url": "https://www.amazon.com/s?k=Engage+Spell+Deodorant",
        "amazon_in_url": "https://www.amazon.in/s?k=Engage+Spell+Deodorant",
        "flipkart_url": "https://www.flipkart.com/search?q=Engage+Spell+Deodorant",
    },

    # Global brands
    {
        "product_type": "deodorant",
        "brand": "Native",
        "name": "Sensitive Deodorant",
        "ingredients_text": "Propylene Glycol, Water, Shea Butter (Butyrospermum Parkii), Baking Soda (Sodium Bicarbonate), Magnesium Hydroxide, Coconut Oil (Cocos Nucifera), Jojoba Oil (Simmondsia Chinensis Seed Oil), Tapioca Starch, Beeswax, Tocopheryl Acetate",
        "amazon_url": "https://www.amazon.com/s?k=Native+Sensitive+Deodorant",
        "amazon_in_url": "https://www.amazon.in/s?k=Native+Sensitive+Deodorant",
        "flipkart_url": "https://www.flipkart.com/search?q=Native+Sensitive+Deodorant",
    },
    {
        "product_type": "deodorant",
        "brand": "Schmidt's",
        "name": "Sensitive Skin Deodorant",
        "ingredients_text": "Butyrospermum Parkii (Shea) Butter, Cocos Nucifera (Coconut) Oil, Magnesium Hydroxide, Maranta Arundinacea (Arrowroot) Powder, Candelilla Wax, Theobroma Cacao (Cocoa) Seed Butter, Tocopherol",
        "amazon_url": "https://www.amazon.com/s?k=Schmidt%27s+Sensitive+Skin+Deodorant",
        "amazon_in_url": "https://www.amazon.in/s?k=Schmidts+Sensitive+Deodorant",
        "flipkart_url": "https://www.flipkart.com/search?q=Schmidts+Sensitive+Deodorant",
    },
    {
        "product_type": "deodorant",
        "brand": "Tom's of Maine",
        "name": "Aluminum-Free Natural Deodorant",
        "ingredients_text": "Propylene Glycol, Water, Sodium Stearate, Sodium Bicarbonate, Sodium Myristate, Fragrance",
        "amazon_url": "https://www.amazon.com/s?k=Tom%27s+of+Maine+Aluminum+Free+Deodorant",
        "amazon_in_url": "https://www.amazon.in/s?k=Toms+of+Maine+Natural+Deodorant",
        "flipkart_url": "https://www.flipkart.com/search?q=Toms+of+Maine+Natural+Deodorant",
    },
    {
        "product_type": "deodorant",
        "brand": "Lume",
        "name": "Whole Body Deodorant",
        "ingredients_text": "Water, Tapioca Starch, Beeswax, Magnesium Hydroxide, Maranta Arundinacea Root Powder, Allantoin, Aloe Barbadensis Leaf Juice, Tocopheryl Acetate, Citric Acid, Sodium Benzoate",
        "amazon_url": "https://www.amazon.com/s?k=Lume+Whole+Body+Deodorant",
        "amazon_in_url": "https://www.amazon.in/s?k=Lume+Whole+Body+Deodorant",
        "flipkart_url": "https://www.flipkart.com/search?q=Lume+Whole+Body+Deodorant",
    },
    {
        "product_type": "deodorant",
        "brand": "Each & Every",
        "name": "Natural Aluminum-Free Deodorant",
        "ingredients_text": "Propanediol, Aqua, Magnesium Hydroxide, Tapioca Starch, Allantoin, Aloe Barbadensis Leaf Juice, Panthenol, Tocopherol, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Each+Every+Natural+Aluminum+Free+Deodorant",
        "amazon_in_url": "https://www.amazon.in/s?k=Each+Every+Natural+Deodorant",
        "flipkart_url": "https://www.flipkart.com/search?q=Each+Every+Natural+Deodorant",
    },

    # ── SERUM / TONER ────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "serum_toner",
        "brand": "Minimalist",
        "name": "2% Salicylic Acid Serum",
        "ingredients_text": "Aqua, Salicylic Acid, Niacinamide, Zinc PCA, Pentylene Glycol, Glycerin, Allantoin, Panthenol, Sodium Hyaluronate, Xanthan Gum, Sodium Hydroxide, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Minimalist+2%25+Salicylic+Acid+Serum",
        "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Salicylic+Acid+Serum",
        "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Salicylic+Acid+Serum",
    },
    {
        "product_type": "serum_toner",
        "brand": "Minimalist",
        "name": "10% Niacinamide Serum",
        "ingredients_text": "Aqua, Niacinamide, Zinc PCA, Pentylene Glycol, Glycerin, Allantoin, Panthenol, Sodium Hyaluronate, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Minimalist+10%25+Niacinamide+Serum",
        "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Niacinamide+Serum",
        "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Niacinamide+Serum",
    },
    {
        "product_type": "serum_toner",
        "brand": "Dr. Sheth's",
        "name": "Vitamin C & Hyaluronic Acid Serum",
        "ingredients_text": "Aqua, Ascorbic Acid, Niacinamide, Sodium Hyaluronate, Glycerin, Pentylene Glycol, Panthenol, Allantoin, Ferulic Acid, Tocopherol, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Dr+Sheth+Vitamin+C+Hyaluronic+Acid+Serum",
        "amazon_in_url": "https://www.amazon.in/s?k=Dr+Sheth+Vitamin+C+Serum",
        "flipkart_url": "https://www.flipkart.com/search?q=Dr+Sheth+Vitamin+C+Serum",
    },
    {
        "product_type": "serum_toner",
        "brand": "The Derma Co",
        "name": "2% Kojic Acid Face Serum",
        "ingredients_text": "Aqua, Kojic Acid, Niacinamide, Glycerin, Panthenol, Allantoin, Sodium Hyaluronate, Pentylene Glycol, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=The+Derma+Co+Kojic+Acid+Face+Serum",
        "amazon_in_url": "https://www.amazon.in/s?k=The+Derma+Co+Kojic+Acid+Serum",
        "flipkart_url": "https://www.flipkart.com/search?q=The+Derma+Co+Kojic+Acid+Serum",
    },
    {
        "product_type": "serum_toner",
        "brand": "Dot & Key",
        "name": "Cica & Ceramide Repair Serum",
        "ingredients_text": "Aqua, Centella Asiatica Leaf Extract, Ceramide NP, Glycerin, Niacinamide, Pentylene Glycol, Panthenol, Allantoin, Sodium Hyaluronate, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Dot+Key+Cica+Ceramide+Repair+Serum",
        "amazon_in_url": "https://www.amazon.in/s?k=Dot+Key+Cica+Ceramide+Serum",
        "flipkart_url": "https://www.flipkart.com/search?q=Dot+Key+Cica+Ceramide+Serum",
    },

    # Global brands
    {
        "product_type": "serum_toner",
        "brand": "The Ordinary",
        "name": "Niacinamide 10% + Zinc 1%",
        "ingredients_text": "Aqua, Niacinamide, Pentylene Glycol, Zinc PCA, Dimethyl Isosorbide, Tamarindus Indica Seed Gum, Xanthan Gum, Isoceteth-20, Ethoxydiglycol, Phenoxyethanol, Chlorphenesin",
        "amazon_url": "https://www.amazon.com/s?k=The+Ordinary+Niacinamide+10%25+Zinc+1%25",
        "amazon_in_url": "https://www.amazon.in/s?k=The+Ordinary+Niacinamide+Zinc+Serum",
        "flipkart_url": "https://www.flipkart.com/search?q=The+Ordinary+Niacinamide+Zinc+Serum",
    },
    {
        "product_type": "serum_toner",
        "brand": "Paula's Choice",
        "name": "Skin Perfecting 2% BHA Liquid Exfoliant",
        "ingredients_text": "Aqua, Methylpropanediol, Butylene Glycol, Salicylic Acid, Polysorbate 20, Camellia Oleifera Leaf Extract, Sodium Hydroxide, Tetrasodium EDTA",
        "amazon_url": "https://www.amazon.com/s?k=Paula%27s+Choice+2%25+BHA+Liquid+Exfoliant",
        "amazon_in_url": "https://www.amazon.in/s?k=Paulas+Choice+BHA+Exfoliant",
        "flipkart_url": "https://www.flipkart.com/search?q=Paulas+Choice+BHA+Exfoliant",
    },
    {
        "product_type": "serum_toner",
        "brand": "The Inkey List",
        "name": "Niacinamide Serum",
        "ingredients_text": "Aqua, Niacinamide, Glycerin, Pentylene Glycol, Zinc PCA, Panthenol, Allantoin, Xanthan Gum, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=The+Inkey+List+Niacinamide+Serum",
        "amazon_in_url": "https://www.amazon.in/s?k=The+Inkey+List+Niacinamide+Serum",
        "flipkart_url": "https://www.flipkart.com/search?q=The+Inkey+List+Niacinamide+Serum",
    },
    {
        "product_type": "serum_toner",
        "brand": "Kiehl's",
        "name": "Clearly Corrective Dark Spot Solution",
        "ingredients_text": "Aqua, Glycerin, Niacinamide, Activated C (Ascorbic Acid), White Birch Extract, Peony Extract, Panthenol, Allantoin, Sodium Hyaluronate, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=Kiehl%27s+Clearly+Corrective+Dark+Spot+Solution",
        "amazon_in_url": "https://www.amazon.in/s?k=Kiehls+Clearly+Corrective+Dark+Spot",
        "flipkart_url": "https://www.flipkart.com/search?q=Kiehls+Clearly+Corrective+Dark+Spot",
    },
    {
        "product_type": "serum_toner",
        "brand": "Dermalogica",
        "name": "Biolumin-C Serum",
        "ingredients_text": "Aqua, Glycerin, Ascorbic Acid, Niacinamide, Sodium Hyaluronate, Panthenol, Allantoin, Sodium Ascorbyl Phosphate, Tocopherol, Ferulic Acid, Xanthan Gum, Disodium EDTA, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Dermalogica+Biolumin-C+Serum",
        "amazon_in_url": "https://www.amazon.in/s?k=Dermalogica+Biolumin+C+Serum",
        "flipkart_url": "https://www.flipkart.com/search?q=Dermalogica+Biolumin+C+Serum",
    },

    # ── BABY PRODUCT ─────────────────────────────────────────────────────────

    # Indian brands
    {
        "product_type": "baby_product",
        "brand": "Himalaya Baby",
        "name": "Baby Lotion",
        "ingredients_text": "Aqua, Glycerin, Almond Oil (Prunus Amygdalus Dulcis Oil), Olive Oil (Olea Europaea Fruit Oil), Aloe Barbadensis Leaf Juice, Panthenol, Allantoin, Tocopheryl Acetate, Xanthan Gum, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Himalaya+Baby+Lotion",
        "amazon_in_url": "https://www.amazon.in/s?k=Himalaya+Baby+Lotion",
        "flipkart_url": "https://www.flipkart.com/search?q=Himalaya+Baby+Lotion",
    },
    {
        "product_type": "baby_product",
        "brand": "Mamaearth Baby",
        "name": "Gentle Cleansing Shampoo",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Glycerin, Panthenol, Allantoin, Aloe Barbadensis Leaf Juice, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Mamaearth+Baby+Gentle+Cleansing+Shampoo",
        "amazon_in_url": "https://www.amazon.in/s?k=Mamaearth+Baby+Gentle+Shampoo",
        "flipkart_url": "https://www.flipkart.com/search?q=Mamaearth+Baby+Gentle+Shampoo",
    },
    {
        "product_type": "baby_product",
        "brand": "Sebamed Baby",
        "name": "Baby Lotion",
        "ingredients_text": "Aqua, Glycerin, Cetearyl Alcohol, Caprylic/Capric Triglyceride, Glyceryl Stearate, Panthenol, Allantoin, Tocopheryl Acetate, Sodium Hyaluronate, Chamomile Extract (Matricaria Chamomilla), Carbomer, Sodium Hydroxide, Phenoxyethanol, Ethylhexylglycerin",
        "amazon_url": "https://www.amazon.com/s?k=Sebamed+Baby+Lotion",
        "amazon_in_url": "https://www.amazon.in/s?k=Sebamed+Baby+Lotion",
        "flipkart_url": "https://www.flipkart.com/search?q=Sebamed+Baby+Lotion",
    },
    {
        "product_type": "baby_product",
        "brand": "Mother Sparsh",
        "name": "Plant-Powered Natural Baby Wash",
        "ingredients_text": "Aqua, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Glycerin, Sodium Cocoyl Isethionate, Panthenol, Allantoin, Aloe Barbadensis Leaf Juice, Calendula Extract, Sodium Benzoate, Citric Acid",
        "amazon_url": "https://www.amazon.com/s?k=Mother+Sparsh+Plant+Powered+Baby+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Mother+Sparsh+Plant+Powered+Baby+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Mother+Sparsh+Plant+Powered+Baby+Wash",
    },
    {
        "product_type": "baby_product",
        "brand": "Johnson's",
        "name": "Baby Lotion (Reformulated)",
        "ingredients_text": "Aqua, Glycerin, Cetearyl Alcohol, Cetyl Dimethicone, Dimethicone, Panthenol, Allantoin, Tocopheryl Acetate, Sodium Hyaluronate, Chamomile Extract, Aloe Barbadensis Leaf Juice, Carbomer, Sodium Hydroxide, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=Johnson%27s+Baby+Lotion",
        "amazon_in_url": "https://www.amazon.in/s?k=Johnsons+Baby+Lotion",
        "flipkart_url": "https://www.flipkart.com/search?q=Johnsons+Baby+Lotion",
    },

    # Global brands
    {
        "product_type": "baby_product",
        "brand": "CeraVe Baby",
        "name": "Baby Moisturizing Lotion",
        "ingredients_text": "Aqua, Glycerin, Ceramide NP, Ceramide AP, Ceramide EOP, Hyaluronic Acid, Niacinamide, Panthenol, Cholesterol, Phytosphingosine, Dimethicone, Cetearyl Alcohol, Sodium Lauroyl Lactylate, Carbomer, Disodium EDTA, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=CeraVe+Baby+Moisturizing+Lotion",
        "amazon_in_url": "https://www.amazon.in/s?k=CeraVe+Baby+Moisturizing+Lotion",
        "flipkart_url": "https://www.flipkart.com/search?q=CeraVe+Baby+Moisturizing+Lotion",
    },
    {
        "product_type": "baby_product",
        "brand": "Vanicream Baby",
        "name": "Free & Clear Baby Wash",
        "ingredients_text": "Purified Water, Sodium Lauryl Sulfoacetate, Cocamidopropyl Betaine, Sodium Cocoyl Isethionate, Glycerin, Panthenol, Allantoin, Citric Acid, Sodium Benzoate",
        "amazon_url": "https://www.amazon.com/s?k=Vanicream+Baby+Free+Clear+Baby+Wash",
        "amazon_in_url": "https://www.amazon.in/s?k=Vanicream+Baby+Free+Clear+Baby+Wash",
        "flipkart_url": "https://www.flipkart.com/search?q=Vanicream+Baby+Free+Clear+Baby+Wash",
    },
    {
        "product_type": "baby_product",
        "brand": "Cetaphil Baby",
        "name": "Daily Lotion",
        "ingredients_text": "Aqua, Glycerin, Dimethicone, Caprylic/Capric Triglyceride, Panthenol, Allantoin, Calendula Extract (Calendula Officinalis Flower Extract), Tocopheryl Acetate, Sodium Hyaluronate, Carbomer, Sodium Hydroxide, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=Cetaphil+Baby+Daily+Lotion",
        "amazon_in_url": "https://www.amazon.in/s?k=Cetaphil+Baby+Daily+Lotion",
        "flipkart_url": "https://www.flipkart.com/search?q=Cetaphil+Baby+Daily+Lotion",
    },
    {
        "product_type": "baby_product",
        "brand": "Aveeno Baby",
        "name": "Daily Moisture Lotion",
        "ingredients_text": "Aqua, Glycerin, Dimethicone, Colloidal Oatmeal, Panthenol, Allantoin, Tocopheryl Acetate, Sodium Hyaluronate, Caprylic/Capric Triglyceride, Carbomer, Sodium Hydroxide, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=Aveeno+Baby+Daily+Moisture+Lotion",
        "amazon_in_url": "https://www.amazon.in/s?k=Aveeno+Baby+Daily+Moisture+Lotion",
        "flipkart_url": "https://www.flipkart.com/search?q=Aveeno+Baby+Daily+Moisture+Lotion",
    },
    {
        "product_type": "baby_product",
        "brand": "Dove Baby",
        "name": "Rich Moisture Lotion",
        "ingredients_text": "Aqua, Glycerin, Stearic Acid, Dimethicone, Cetyl Alcohol, Panthenol, Allantoin, Tocopheryl Acetate, Sodium Hyaluronate, Carbomer, Sodium Hydroxide, Phenoxyethanol, Caprylyl Glycol",
        "amazon_url": "https://www.amazon.com/s?k=Dove+Baby+Rich+Moisture+Lotion",
        "amazon_in_url": "https://www.amazon.in/s?k=Dove+Baby+Rich+Moisture+Lotion",
        "flipkart_url": "https://www.flipkart.com/search?q=Dove+Baby+Rich+Moisture+Lotion",
    },
]


if __name__ == "__main__":
    print("Loading engine...")
    df, groq_client = load_engine()
    print(f"  CSV loaded: {len(df)} rows\n")

    results_by_type: dict[str, list] = {}
    total, passed_count = 0, 0

    for product in CANDIDATES:
        ptype = product["product_type"]
        print(f"[{ptype}] {product['brand']} - {product['name']}")
        verified = verify_product(product, df, groq_client)
        total += 1
        if verified:
            passed_count += 1
            results_by_type.setdefault(ptype, []).append(verified)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verified_alternatives.json")
    with open(out_path, "w") as f:
        json.dump(results_by_type, f, indent=2)

    print(f"\n{'-'*60}")
    print(f"Total candidates : {total}")
    print(f"Passed           : {passed_count}")
    print(f"Failed           : {total - passed_count}")
    print(f"Output           : {out_path}")
    for ptype, items in results_by_type.items():
        print(f"  {ptype}: {len(items)} verified")
