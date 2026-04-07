"""
Core analysis engine.

Takes a list of parsed ingredient strings, matches them against the INCI
mapping, queries the research database for evidence, generates LLM summaries,
and returns a structured analysis result.
"""

import os
import re
import time
from collections import Counter


def parse_ingredients_text(raw: str) -> list:
    """
    Parse a raw ingredient string like:
      "Aqua, Glycerin, Fragrance (Linalool, Limonene), Methylparaben*"
    into a flat, lowercased, cleaned list:
      ["aqua", "glycerin", "fragrance", "linalool", "limonene", "methylparaben"]
    """
    if not raw:
        return []
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

import pandas as pd

from agent.tools.inci_mapping import TOXICANT_INCI_MAP, TOXICANT_DISPLAY, SHORT_SYNONYMS


# Tier-adjusted verdict thresholds.
# "high"   = ingredient in top third of list  (highest concentration)
# "medium" = ingredient in middle third
# "low"    = ingredient in bottom third (trace amount)
TIER_THRESHOLDS = {
    "high":   {"concerning": 10,  "caution": 1},
    "medium": {"concerning": 25,  "caution": 1},
    "low":    {"concerning": 50,  "caution": 10},
}


def match_toxicants(ingredients: list) -> dict:
    """
    Match a list of lowercased ingredient strings against all 15 toxicant categories.
    Tracks each match's position in the ingredient list to derive a concentration tier.

    Returns:
        {
          toxicant_key: {
            "matches":       [list of matched ingredient strings],
            "best_position": int (1-indexed, earliest/highest-concentration match),
            "list_length":   int,
            "tier":          "high" | "medium" | "low",
          }
        }
    """
    matched = {}
    list_length = max(len(ingredients), 1)  # guard against empty list

    for toxicant_key, synonyms in TOXICANT_INCI_MAP.items():
        hit_positions = []  # list of (0-based index, ingredient string)

        for idx, ingredient in enumerate(ingredients):
            ingredient_lower = ingredient.lower()
            found = False
            for synonym in synonyms:
                if synonym in SHORT_SYNONYMS:
                    # Word-boundary regex to avoid false positives (e.g. "bha" in "alpha")
                    pattern = r'\b' + re.escape(synonym) + r'\b'
                    if re.search(pattern, ingredient_lower):
                        found = True
                else:
                    if synonym in ingredient_lower or ingredient_lower in synonym:
                        found = True
                if found:
                    break
            if found:
                hit_positions.append((idx, ingredient))

        if hit_positions:
            best_idx = min(pos for pos, _ in hit_positions)  # earliest = highest concentration
            best_position = best_idx + 1  # convert to 1-indexed

            ratio = best_position / list_length
            if ratio <= 0.33:
                tier = "high"
            elif ratio <= 0.66:
                tier = "medium"
            else:
                tier = "low"

            matched[toxicant_key] = {
                "matches": [ing for _, ing in hit_positions],
                "best_position": best_position,
                "list_length": list_length,
                "tier": tier,
            }

    return matched


def get_toxicant_evidence(df: pd.DataFrame, toxicant_key: str) -> dict:
    """
    Query the database DataFrame for evidence on a specific toxicant.
    df should already be filtered to relevant == "yes" rows.

    Returns aggregated evidence dict.
    """
    # Match rows where toxicant column contains this key (word boundary)
    pattern = r'\b' + re.escape(toxicant_key) + r'\b'
    mask = df["toxicant"].str.contains(pattern, regex=True, case=False, na=False)
    subset = df[mask]

    paper_count = len(subset)

    # Aggregate health effects
    effect_counter = Counter()
    for val in subset.get("health_effects", pd.Series(dtype=str)).fillna(""):
        for e in str(val).split("|"):
            e = e.strip()
            if e and e.lower() not in ("unspecified", ""):
                effect_counter[e] += 1
    top_effects = [e for e, _ in effect_counter.most_common(5)]

    # Aggregate organs
    organ_counter = Counter()
    for val in subset.get("organs", pd.Series(dtype=str)).fillna(""):
        for o in str(val).split("|"):
            o = o.strip()
            if o and o.lower() not in ("unspecified", ""):
                organ_counter[o] += 1
    top_organs = [o for o, _ in organ_counter.most_common(5)]

    # Sample up to 5 relevance_reason excerpts, spread across dataset for variety
    reasons_series = subset["relevance_reason"].fillna("").str.strip()
    reasons = [r for r in reasons_series.tolist() if r]
    if len(reasons) > 5:
        step = max(1, len(reasons) // 5)
        sample_reasons = [reasons[i * step] for i in range(5)]
    else:
        sample_reasons = reasons[:5]

    return {
        "toxicant_key": toxicant_key,
        "paper_count": paper_count,
        "top_effects": top_effects,
        "top_organs": top_organs,
        "sample_reasons": sample_reasons,
    }


def generate_toxicant_summary(display_name: str, matched_ingredients: list,
                               evidence: dict, groq_client, tier: str = "high") -> str:
    """
    Call Groq llama-3.1-8b-instant to generate a 2-sentence plain-English
    consumer summary for a detected toxicant.

    Returns "" on any failure — the UI renders without it rather than crashing.
    """
    is_dioxane = evidence["toxicant_key"] == "dioxane"
    dioxane_note = (
        "\nNote: 1,4-dioxane is a manufacturing byproduct — it is not added directly. "
        "The matched ingredients are ethoxylated compounds that can contain it as a contaminant."
        if is_dioxane else ""
    )

    tier_note = (
        "\nNote: This ingredient appears near the end of the ingredient list, suggesting it is "
        "present at a low concentration. Most studies cited may have used higher doses than "
        "what a typical consumer would encounter from this product."
        if tier == "low" else ""
    )

    prompt = f"""You are a consumer health advisor. Write exactly 2 sentences in plain English about the ingredient concern below.
Do not use academic language. Do not say "consult a doctor" or "studies show" or "research indicates".
Just state the concern clearly and directly.{dioxane_note}{tier_note}

Ingredient category: {display_name}
Found in this product as: {', '.join(matched_ingredients)}
Peer-reviewed research papers in database: {evidence['paper_count']}
Top documented health effects: {', '.join(evidence['top_effects']) or 'not specified'}
Top organs/systems affected: {', '.join(evidence['top_organs']) or 'not specified'}

Two-sentence plain-language summary:"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


def compute_verdict(detected: list) -> str:
    """
    Determines overall product verdict based on detected toxicants.

    Thresholds are tier-adjusted — a trace ingredient requires more evidence
    before being flagged as concerning:
      high tier:   concerning >= 10 papers,  caution >= 1
      medium tier: concerning >= 25 papers,  caution >= 1
      low tier:    concerning >= 50 papers,  caution >= 10

    Returns "concerning", "caution", or "clean".
    """
    if not detected:
        return "clean"

    for t in detected:
        tier = t.get("tier", "high")
        if t["paper_count"] >= TIER_THRESHOLDS[tier]["concerning"]:
            return "concerning"

    for t in detected:
        tier = t.get("tier", "high")
        if t["paper_count"] >= TIER_THRESHOLDS[tier]["caution"]:
            return "caution"

    return "clean"


def analyze(ingredients: list, df: pd.DataFrame, groq_client) -> dict:
    """
    Main entry point. Runs the full pipeline.

    Args:
        ingredients   — list of lowercased ingredient strings from the product
        df            — pre-loaded and pre-filtered (_combined.csv, relevant=="yes")
        groq_client   — instantiated Groq client

    Returns:
        Full analysis result dict.
    """
    if not ingredients:
        return {
            "status": "error",
            "error_message": "No ingredients provided.",
            "verdict": "clean",
            "total_toxicants_detected": 0,
            "total_relevant_papers": 0,
            "detected_toxicants": [],
            "unmatched_ingredients": [],
        }

    # Step 1: match ingredients to toxicant categories (with position tracking)
    matched = match_toxicants(ingredients)

    # Step 2: build evidence + LLM summary for each detected toxicant
    detected = []
    flagged_ingredients = set()

    for toxicant_key, match_info in matched.items():
        matched_ingredients = match_info["matches"]
        tier = match_info["tier"]
        best_position = match_info["best_position"]
        list_length = match_info["list_length"]

        flagged_ingredients.update(matched_ingredients)
        display_name = TOXICANT_DISPLAY.get(toxicant_key, toxicant_key)
        evidence = get_toxicant_evidence(df, toxicant_key)

        # Add small delay between Groq calls to stay under 30 RPM free tier
        if detected:
            time.sleep(0.5)

        llm_summary = generate_toxicant_summary(
            display_name, matched_ingredients, evidence, groq_client, tier=tier
        )

        detected.append({
            "toxicant_key": toxicant_key,
            "display_name": display_name,
            "matched_ingredients": matched_ingredients,
            "tier": tier,
            "best_position": best_position,
            "list_length": list_length,
            "paper_count": evidence["paper_count"],
            "top_effects": evidence["top_effects"],
            "top_organs": evidence["top_organs"],
            "sample_reasons": evidence["sample_reasons"],
            "llm_summary": llm_summary,
        })

    # Sort by paper count descending (most evidence first)
    detected.sort(key=lambda x: x["paper_count"], reverse=True)

    unmatched = [i for i in ingredients if i not in flagged_ingredients]
    total_papers = sum(t["paper_count"] for t in detected)

    return {
        "status": "ok",
        "error_message": "",
        "verdict": compute_verdict(detected),
        "total_toxicants_detected": len(detected),
        "total_relevant_papers": total_papers,
        "detected_toxicants": detected,
        "unmatched_ingredients": unmatched,
        "all_ingredients": ingredients,
    }
