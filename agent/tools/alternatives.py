"""
Safer Alternatives database — engine-verified via scripts/build_alternatives.py
Last verified: 2026-04-13
"""

PRODUCT_TYPES = [
    "moisturizer",
    "shampoo_conditioner",
    "sunscreen",
    "body_wash",
    "foundation",
    "lip_product",
    "eye_makeup",
    "deodorant",
    "serum_toner",
    "baby_product",
]

PRODUCT_TYPE_LABELS = {
    "moisturizer":         "Moisturizer",
    "shampoo_conditioner": "Shampoo / Conditioner",
    "sunscreen":           "Sunscreen",
    "body_wash":           "Body Wash",
    "foundation":          "Foundation",
    "lip_product":         "Lip Product",
    "eye_makeup":          "Eye Makeup",
    "deodorant":           "Deodorant",
    "serum_toner":         "Serum / Toner",
    "baby_product":        "Baby Product",
}

ALL_15 = [
    "parabens", "phthalates", "pfas", "benzophenones", "siloxanes", "fragrance",
    "toluene", "formaldehyde_releasers", "heavy_metals", "hydroquinone",
    "ethanolamines", "bha_bht", "coal_tar", "triclosan", "dioxane",
]

# Each entry schema:
#   name, brand, verified, scan_date, verdict, toxicant_count,
#   avoids (list of toxicant keys NOT detected), detected (list of keys found),
#   amazon_url, amazon_in_url, flipkart_url, sponsored

ALTERNATIVES_DB = {

    "moisturizer": [
        {"brand": "Minimalist", "name": "10% Niacinamide Face Moisturizer", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Minimalist+Niacinamide+Moisturizer", "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Niacinamide+Moisturizer", "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Niacinamide+Moisturizer", "sponsored": False},
        {"brand": "Minimalist", "name": "Peptide Moisturizer SPF 30", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Minimalist+Peptide+Moisturizer+SPF+30", "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Peptide+Moisturizer+SPF+30", "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Peptide+Moisturizer+SPF+30", "sponsored": False},
        {"brand": "Dr. Sheth's", "name": "Ceramide & Vitamin C Moisturizer", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Dr+Sheth+Ceramide+Vitamin+C+Moisturizer", "amazon_in_url": "https://www.amazon.in/s?k=Dr+Sheth+Ceramide+Vitamin+C+Moisturizer", "flipkart_url": "https://www.flipkart.com/search?q=Dr+Sheth+Ceramide+Vitamin+C+Moisturizer", "sponsored": False},
        {"brand": "Dot & Key", "name": "Water Drench Hyaluronic Moisturizer", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Dot+Key+Water+Drench+Hyaluronic+Moisturizer", "amazon_in_url": "https://www.amazon.in/s?k=Dot+Key+Water+Drench+Hyaluronic+Moisturizer", "flipkart_url": "https://www.flipkart.com/search?q=Dot+Key+Water+Drench+Hyaluronic+Moisturizer", "sponsored": False},
    ],

    "shampoo_conditioner": [
        {"brand": "Minimalist", "name": "2% Salicylic Acid Shampoo", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Minimalist+2%25+Salicylic+Acid+Shampoo", "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Salicylic+Acid+Shampoo", "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Salicylic+Acid+Shampoo", "sponsored": False},
        {"brand": "WOW", "name": "Apple Cider Vinegar Shampoo", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=WOW+Apple+Cider+Vinegar+Shampoo", "amazon_in_url": "https://www.amazon.in/s?k=WOW+Apple+Cider+Vinegar+Shampoo", "flipkart_url": "https://www.flipkart.com/search?q=WOW+Apple+Cider+Vinegar+Shampoo", "sponsored": False},
        {"brand": "Plum", "name": "Olive & Macadamia Healthy Hydration Shampoo", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Plum+Olive+Macadamia+Shampoo", "amazon_in_url": "https://www.amazon.in/s?k=Plum+Olive+Macadamia+Shampoo", "flipkart_url": "https://www.flipkart.com/search?q=Plum+Olive+Macadamia+Shampoo", "sponsored": False},
        {"brand": "mCaffeine", "name": "Coffee Shampoo", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=mCaffeine+Coffee+Shampoo", "amazon_in_url": "https://www.amazon.in/s?k=mCaffeine+Coffee+Shampoo", "flipkart_url": "https://www.flipkart.com/search?q=mCaffeine+Coffee+Shampoo", "sponsored": False},
        {"brand": "Himalaya", "name": "Gentle Daily Care Protein Shampoo", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Himalaya+Gentle+Daily+Care+Protein+Shampoo", "amazon_in_url": "https://www.amazon.in/s?k=Himalaya+Gentle+Daily+Care+Protein+Shampoo", "flipkart_url": "https://www.flipkart.com/search?q=Himalaya+Gentle+Daily+Care+Protein+Shampoo", "sponsored": False},
        {"brand": "The Ordinary", "name": "Sulphate-Free Cleanser for Hair & Body", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=The+Ordinary+Sulphate+Free+Cleanser", "amazon_in_url": "https://www.amazon.in/s?k=The+Ordinary+Sulphate+Free+Cleanser", "flipkart_url": "https://www.flipkart.com/search?q=The+Ordinary+Sulphate+Free+Cleanser", "sponsored": False},
    ],

    "sunscreen": [
        {"brand": "Minimalist", "name": "SPF 50 Sunscreen", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Minimalist+SPF+50+Sunscreen", "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+SPF+50+Sunscreen", "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+SPF+50+Sunscreen", "sponsored": False},
        {"brand": "Dot & Key", "name": "Mineral Matte Sunscreen SPF 50", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Dot+Key+Mineral+Matte+Sunscreen+SPF+50", "amazon_in_url": "https://www.amazon.in/s?k=Dot+Key+Mineral+Matte+Sunscreen+SPF+50", "flipkart_url": "https://www.flipkart.com/search?q=Dot+Key+Mineral+Matte+Sunscreen+SPF+50", "sponsored": False},
        {"brand": "Plum", "name": "Green Tea Renewed Clarity SPF 35", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Plum+Green+Tea+Sunscreen+SPF+35", "amazon_in_url": "https://www.amazon.in/s?k=Plum+Green+Tea+Sunscreen+SPF+35", "flipkart_url": "https://www.flipkart.com/search?q=Plum+Green+Tea+Sunscreen+SPF+35", "sponsored": False},
        {"brand": "The Derma Co", "name": "1% Hyaluronic Sunscreen SPF 50", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=The+Derma+Co+Hyaluronic+Sunscreen+SPF+50", "amazon_in_url": "https://www.amazon.in/s?k=The+Derma+Co+Hyaluronic+Sunscreen+SPF+50", "flipkart_url": "https://www.flipkart.com/search?q=The+Derma+Co+Hyaluronic+Sunscreen+SPF+50", "sponsored": False},
        {"brand": "Re'equil", "name": "Oxybenzone & OMC Free Sunscreen SPF 50", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Re+equil+Oxybenzone+Free+Sunscreen+SPF+50", "amazon_in_url": "https://www.amazon.in/s?k=Re+equil+Oxybenzone+Free+Sunscreen+SPF+50", "flipkart_url": "https://www.flipkart.com/search?q=Re+equil+Oxybenzone+Free+Sunscreen+SPF+50", "sponsored": False},
    ],

    "body_wash": [
        {"brand": "Himalaya", "name": "Moisturizing Aloe Vera Body Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Himalaya+Moisturizing+Aloe+Vera+Body+Wash", "amazon_in_url": "https://www.amazon.in/s?k=Himalaya+Moisturizing+Aloe+Vera+Body+Wash", "flipkart_url": "https://www.flipkart.com/search?q=Himalaya+Moisturizing+Aloe+Vera+Body+Wash", "sponsored": False},
        {"brand": "Mamaearth", "name": "Ubtan Body Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Mamaearth+Ubtan+Body+Wash", "amazon_in_url": "https://www.amazon.in/s?k=Mamaearth+Ubtan+Body+Wash", "flipkart_url": "https://www.flipkart.com/search?q=Mamaearth+Ubtan+Body+Wash", "sponsored": False},
        {"brand": "WOW", "name": "Skin Charge Body Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=WOW+Skin+Charge+Body+Wash", "amazon_in_url": "https://www.amazon.in/s?k=WOW+Skin+Charge+Body+Wash", "flipkart_url": "https://www.flipkart.com/search?q=WOW+Skin+Charge+Body+Wash", "sponsored": False},
        {"brand": "Plum", "name": "BodyLovin' Vanilla Vibes Body Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Plum+BodyLovin+Vanilla+Vibes+Body+Wash", "amazon_in_url": "https://www.amazon.in/s?k=Plum+BodyLovin+Vanilla+Body+Wash", "flipkart_url": "https://www.flipkart.com/search?q=Plum+BodyLovin+Vanilla+Body+Wash", "sponsored": False},
        {"brand": "mCaffeine", "name": "Coffee Body Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=mCaffeine+Coffee+Body+Wash", "amazon_in_url": "https://www.amazon.in/s?k=mCaffeine+Coffee+Body+Wash", "flipkart_url": "https://www.flipkart.com/search?q=mCaffeine+Coffee+Body+Wash", "sponsored": False},
        {"brand": "CeraVe", "name": "Hydrating Cleanser Body Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=CeraVe+Hydrating+Body+Wash", "amazon_in_url": "https://www.amazon.in/s?k=CeraVe+Hydrating+Body+Wash", "flipkart_url": "https://www.flipkart.com/search?q=CeraVe+Hydrating+Body+Wash", "sponsored": False},
        {"brand": "Cetaphil", "name": "Gentle Skin Cleanser Body Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Cetaphil+Gentle+Skin+Cleanser+Body+Wash", "amazon_in_url": "https://www.amazon.in/s?k=Cetaphil+Gentle+Skin+Cleanser+Body+Wash", "flipkart_url": "https://www.flipkart.com/search?q=Cetaphil+Gentle+Skin+Cleanser+Body+Wash", "sponsored": False},
        {"brand": "Vanicream", "name": "Gentle Body Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Vanicream+Gentle+Body+Wash", "amazon_in_url": "https://www.amazon.in/s?k=Vanicream+Gentle+Body+Wash", "flipkart_url": "https://www.flipkart.com/search?q=Vanicream+Gentle+Body+Wash", "sponsored": False},
    ],

    "foundation": [
        {"brand": "BareMinerals", "name": "ORIGINAL Foundation SPF 15", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=BareMinerals+ORIGINAL+Foundation+SPF+15", "amazon_in_url": "https://www.amazon.in/s?k=BareMinerals+ORIGINAL+Foundation", "flipkart_url": "https://www.flipkart.com/search?q=BareMinerals+ORIGINAL+Foundation", "sponsored": False},
        {"brand": "100% Pure", "name": "Fruit Pigmented Full Coverage Water Foundation", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=100+Pure+Fruit+Pigmented+Water+Foundation", "amazon_in_url": "https://www.amazon.in/s?k=100+Pure+Fruit+Pigmented+Water+Foundation", "flipkart_url": "https://www.flipkart.com/search?q=100+Pure+Fruit+Pigmented+Water+Foundation", "sponsored": False},
        {"brand": "W3LL PEOPLE", "name": "Bio Correct Full Coverage Foundation", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=W3LL+PEOPLE+Bio+Correct+Foundation", "amazon_in_url": "https://www.amazon.in/s?k=W3LL+PEOPLE+Bio+Correct+Foundation", "flipkart_url": "https://www.flipkart.com/search?q=W3LL+PEOPLE+Bio+Correct+Foundation", "sponsored": False},
        {"brand": "Kjaer Weis", "name": "Invisible Touch Liquid Foundation", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Kjaer+Weis+Invisible+Touch+Foundation", "amazon_in_url": "https://www.amazon.in/s?k=Kjaer+Weis+Invisible+Touch+Foundation", "flipkart_url": "https://www.flipkart.com/search?q=Kjaer+Weis+Invisible+Touch+Foundation", "sponsored": False},
    ],

    "lip_product": [
        {"brand": "mCaffeine", "name": "Coffee Lip Balm", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=mCaffeine+Coffee+Lip+Balm", "amazon_in_url": "https://www.amazon.in/s?k=mCaffeine+Coffee+Lip+Balm", "flipkart_url": "https://www.flipkart.com/search?q=mCaffeine+Coffee+Lip+Balm", "sponsored": False},
        {"brand": "Biotique", "name": "Natural Lip Butter", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Biotique+Natural+Lip+Butter", "amazon_in_url": "https://www.amazon.in/s?k=Biotique+Natural+Lip+Butter", "flipkart_url": "https://www.flipkart.com/search?q=Biotique+Natural+Lip+Butter", "sponsored": False},
        {"brand": "ILIA", "name": "Color Block Lipstick", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=ILIA+Color+Block+Lipstick", "amazon_in_url": "https://www.amazon.in/s?k=ILIA+Color+Block+Lipstick", "flipkart_url": "https://www.flipkart.com/search?q=ILIA+Color+Block+Lipstick", "sponsored": False},
        {"brand": "RMS Beauty", "name": "Wild With Desire Lipstick", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=RMS+Beauty+Wild+With+Desire+Lipstick", "amazon_in_url": "https://www.amazon.in/s?k=RMS+Beauty+Wild+With+Desire+Lipstick", "flipkart_url": "https://www.flipkart.com/search?q=RMS+Beauty+Wild+With+Desire+Lipstick", "sponsored": False},
        {"brand": "Burt's Bees", "name": "Lip Butter", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Burt%27s+Bees+Lip+Butter", "amazon_in_url": "https://www.amazon.in/s?k=Burts+Bees+Lip+Butter", "flipkart_url": "https://www.flipkart.com/search?q=Burts+Bees+Lip+Butter", "sponsored": False},
        {"brand": "100% Pure", "name": "Fruit Pigmented Cocoa Butter Matte Lipstick", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=100+Pure+Fruit+Pigmented+Cocoa+Butter+Lipstick", "amazon_in_url": "https://www.amazon.in/s?k=100+Pure+Fruit+Pigmented+Lipstick", "flipkart_url": "https://www.flipkart.com/search?q=100+Pure+Fruit+Pigmented+Lipstick", "sponsored": False},
        {"brand": "EltaMD", "name": "UV Lip Balm SPF 36", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=EltaMD+UV+Lip+Balm+SPF+36", "amazon_in_url": "https://www.amazon.in/s?k=EltaMD+UV+Lip+Balm+SPF+36", "flipkart_url": "https://www.flipkart.com/search?q=EltaMD+UV+Lip+Balm+SPF+36", "sponsored": False},
    ],

    # eye_makeup: 0 verified in 2026-04-13 run — iron oxide CI numbers false-positive
    # as coal tar in current engine. Chip appears in UI; no alternatives shown.

    "deodorant": [
        {"brand": "Himalaya", "name": "Sensitive Skin Deodorant Roll-On", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Himalaya+Sensitive+Skin+Deodorant", "amazon_in_url": "https://www.amazon.in/s?k=Himalaya+Sensitive+Skin+Deodorant", "flipkart_url": "https://www.flipkart.com/search?q=Himalaya+Sensitive+Skin+Deodorant", "sponsored": False},
        {"brand": "Bella Vita", "name": "Organic Deo Spray", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Bella+Vita+Organic+Deo+Spray", "amazon_in_url": "https://www.amazon.in/s?k=Bella+Vita+Organic+Deo+Spray", "flipkart_url": "https://www.flipkart.com/search?q=Bella+Vita+Organic+Deo+Spray", "sponsored": False},
        {"brand": "Native", "name": "Sensitive Deodorant", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Native+Sensitive+Deodorant", "amazon_in_url": "https://www.amazon.in/s?k=Native+Sensitive+Deodorant", "flipkart_url": "https://www.flipkart.com/search?q=Native+Sensitive+Deodorant", "sponsored": False},
        {"brand": "Schmidt's", "name": "Sensitive Skin Deodorant", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Schmidt%27s+Sensitive+Skin+Deodorant", "amazon_in_url": "https://www.amazon.in/s?k=Schmidts+Sensitive+Deodorant", "flipkart_url": "https://www.flipkart.com/search?q=Schmidts+Sensitive+Deodorant", "sponsored": False},
        {"brand": "Lume", "name": "Whole Body Deodorant", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Lume+Whole+Body+Deodorant", "amazon_in_url": "https://www.amazon.in/s?k=Lume+Whole+Body+Deodorant", "flipkart_url": "https://www.flipkart.com/search?q=Lume+Whole+Body+Deodorant", "sponsored": False},
        {"brand": "Each & Every", "name": "Natural Aluminum-Free Deodorant", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Each+Every+Natural+Aluminum+Free+Deodorant", "amazon_in_url": "https://www.amazon.in/s?k=Each+Every+Natural+Deodorant", "flipkart_url": "https://www.flipkart.com/search?q=Each+Every+Natural+Deodorant", "sponsored": False},
    ],

    "serum_toner": [
        {"brand": "Minimalist", "name": "2% Salicylic Acid Serum", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Minimalist+2%25+Salicylic+Acid+Serum", "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Salicylic+Acid+Serum", "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Salicylic+Acid+Serum", "sponsored": False},
        {"brand": "Minimalist", "name": "10% Niacinamide Serum", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Minimalist+10%25+Niacinamide+Serum", "amazon_in_url": "https://www.amazon.in/s?k=Minimalist+Niacinamide+Serum", "flipkart_url": "https://www.flipkart.com/search?q=Minimalist+Niacinamide+Serum", "sponsored": False},
        {"brand": "Dr. Sheth's", "name": "Vitamin C & Hyaluronic Acid Serum", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Dr+Sheth+Vitamin+C+Hyaluronic+Acid+Serum", "amazon_in_url": "https://www.amazon.in/s?k=Dr+Sheth+Vitamin+C+Serum", "flipkart_url": "https://www.flipkart.com/search?q=Dr+Sheth+Vitamin+C+Serum", "sponsored": False},
        {"brand": "The Derma Co", "name": "2% Kojic Acid Face Serum", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=The+Derma+Co+Kojic+Acid+Face+Serum", "amazon_in_url": "https://www.amazon.in/s?k=The+Derma+Co+Kojic+Acid+Serum", "flipkart_url": "https://www.flipkart.com/search?q=The+Derma+Co+Kojic+Acid+Serum", "sponsored": False},
        {"brand": "Dot & Key", "name": "Cica & Ceramide Repair Serum", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Dot+Key+Cica+Ceramide+Repair+Serum", "amazon_in_url": "https://www.amazon.in/s?k=Dot+Key+Cica+Ceramide+Serum", "flipkart_url": "https://www.flipkart.com/search?q=Dot+Key+Cica+Ceramide+Serum", "sponsored": False},
        {"brand": "The Inkey List", "name": "Niacinamide Serum", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=The+Inkey+List+Niacinamide+Serum", "amazon_in_url": "https://www.amazon.in/s?k=The+Inkey+List+Niacinamide+Serum", "flipkart_url": "https://www.flipkart.com/search?q=The+Inkey+List+Niacinamide+Serum", "sponsored": False},
        {"brand": "Kiehl's", "name": "Clearly Corrective Dark Spot Solution", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Kiehl%27s+Clearly+Corrective+Dark+Spot+Solution", "amazon_in_url": "https://www.amazon.in/s?k=Kiehls+Clearly+Corrective+Dark+Spot", "flipkart_url": "https://www.flipkart.com/search?q=Kiehls+Clearly+Corrective+Dark+Spot", "sponsored": False},
        {"brand": "Dermalogica", "name": "Biolumin-C Serum", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Dermalogica+Biolumin-C+Serum", "amazon_in_url": "https://www.amazon.in/s?k=Dermalogica+Biolumin+C+Serum", "flipkart_url": "https://www.flipkart.com/search?q=Dermalogica+Biolumin+C+Serum", "sponsored": False},
    ],

    "baby_product": [
        {"brand": "Himalaya Baby", "name": "Baby Lotion", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Himalaya+Baby+Lotion", "amazon_in_url": "https://www.amazon.in/s?k=Himalaya+Baby+Lotion", "flipkart_url": "https://www.flipkart.com/search?q=Himalaya+Baby+Lotion", "sponsored": False},
        {"brand": "Mamaearth Baby", "name": "Gentle Cleansing Shampoo", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Mamaearth+Baby+Gentle+Cleansing+Shampoo", "amazon_in_url": "https://www.amazon.in/s?k=Mamaearth+Baby+Gentle+Shampoo", "flipkart_url": "https://www.flipkart.com/search?q=Mamaearth+Baby+Gentle+Shampoo", "sponsored": False},
        {"brand": "Sebamed Baby", "name": "Baby Lotion", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Sebamed+Baby+Lotion", "amazon_in_url": "https://www.amazon.in/s?k=Sebamed+Baby+Lotion", "flipkart_url": "https://www.flipkart.com/search?q=Sebamed+Baby+Lotion", "sponsored": False},
        {"brand": "Mother Sparsh", "name": "Plant-Powered Natural Baby Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Mother+Sparsh+Plant+Powered+Baby+Wash", "amazon_in_url": "https://www.amazon.in/s?k=Mother+Sparsh+Plant+Powered+Baby+Wash", "flipkart_url": "https://www.flipkart.com/search?q=Mother+Sparsh+Plant+Powered+Baby+Wash", "sponsored": False},
        {"brand": "Vanicream Baby", "name": "Free & Clear Baby Wash", "verified": True, "scan_date": "2026-04-13", "verdict": "clean", "toxicant_count": 0, "avoids": ALL_15, "detected": [], "amazon_url": "https://www.amazon.com/s?k=Vanicream+Baby+Free+Clear+Baby+Wash", "amazon_in_url": "https://www.amazon.in/s?k=Vanicream+Baby+Free+Clear+Baby+Wash", "flipkart_url": "https://www.flipkart.com/search?q=Vanicream+Baby+Free+Clear+Baby+Wash", "sponsored": False},
    ],
}


def get_alternatives(product_type: str | None, detected_toxicant_keys: list) -> list:
    """
    Return up to 5 verified alternatives for the given product type.

    - If no product_type or type not in DB: return []
    - If scan was clean (no detected toxicants): return top 3 for browsing
    - Otherwise: filter to products that avoid the detected toxicants,
      sort by overlap count desc (sponsored first when monetisation is on)
    """
    if not product_type or product_type not in ALTERNATIVES_DB:
        return []

    pool = ALTERNATIVES_DB[product_type]
    detected_set = set(detected_toxicant_keys or [])

    if not detected_set:
        return pool[:3]

    candidates = []
    for alt in pool:
        overlap = set(alt["avoids"]) & detected_set
        if overlap:
            candidates.append((alt, len(overlap)))

    # Sort: sponsored desc (future), then overlap count desc
    candidates.sort(key=lambda x: (-int(x[0]["sponsored"]), -x[1]))
    return [a for a, _ in candidates[:5]]
