"""
CosmoTox Product Scanner — FastAPI Backend
Run with: python3 -m uvicorn agent.api:app --host 0.0.0.0 --port 8000
"""

import os
import uuid
from contextlib import asynccontextmanager

import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from groq import Groq
from pydantic import BaseModel, field_validator

from agent.auth.dependencies import get_current_user
from agent.auth.supabase_client import get_supabase
from agent.tools.analyze_ingredients import analyze, parse_ingredients_text

# ── Environment ───────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "database")
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")

# ── Load database once at startup ─────────────────────────────────────────────
def load_database(db_path: str) -> pd.DataFrame:
    combined_path = os.path.join(db_path, "_combined.csv")
    if not os.path.exists(combined_path):
        raise FileNotFoundError(f"_combined.csv not found at: {combined_path}")
    df = pd.read_csv(combined_path, dtype=str).fillna("")
    df = df[df["relevant"].str.strip().str.lower() == "yes"].copy()
    return df

# ── App state ─────────────────────────────────────────────────────────────────
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set in .env")
    app_state["df"]   = load_database(DATABASE_PATH)
    app_state["groq"] = Groq(api_key=GROQ_API_KEY)
    print(f"[CosmoTox] Database loaded: {len(app_state['df'])} relevant papers")
    yield
    app_state.clear()

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="CosmoTox Scanner API", lifespan=lifespan)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ── Request models ────────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    ingredients_text: str

class OcrRequest(BaseModel):
    image_base64: str
    mime_type: str = "image/jpeg"

    @field_validator("image_base64")
    @classmethod
    def check_image_size(cls, v: str) -> str:
        if len(v) > 20_000_000:  # ~15 MB decoded
            raise ValueError("Image too large — max 15 MB")
        return v

class CompareProductItem(BaseModel):
    name: str
    ingredients_text: str

class CompareRequest(BaseModel):
    products: list[CompareProductItem]

class WatchlistBody(BaseModel):
    watchlist_type: str  # "toxicant" or "organ"

# ── Helpers ───────────────────────────────────────────────────────────────────
def _log_scan(user_id: str, scan_type: str, product_name: str | None,
              analysis: dict, compare_group_id: str | None = None) -> None:
    """Write one row to Supabase scan_history. Errors are non-fatal."""
    try:
        sb = get_supabase()
        row = {
            "user_id": user_id,
            "scan_type": scan_type,
            "product_name": product_name,
            "verdict": analysis.get("verdict"),
            "toxicant_count": analysis.get("total_toxicants_detected", 0),
            "paper_count": analysis.get("total_relevant_papers", 0),
            "top_toxicants": [t["toxicant_key"] for t in analysis.get("detected_toxicants", [])],
        }
        if compare_group_id:
            row["compare_group_id"] = compare_group_id
        sb.table("scan_history").insert(row).execute()
    except Exception as e:
        print(f"[CosmoTox] scan_history log failed (non-fatal): {e}")

# ── Public endpoints ──────────────────────────────────────────────────────────

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "papers_loaded": len(app_state.get("df", [])),
    }

# ── Auth-gated endpoints ──────────────────────────────────────────────────────

@app.post("/ocr-ingredients")
def ocr_ingredients(body: OcrRequest, current_user: dict = Depends(get_current_user)):
    groq_client = app_state["groq"]

    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{body.mime_type};base64,{body.image_base64}"
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "This is a photo of a cosmetic product label. "
                            "Extract only the ingredients list as a comma-separated string. "
                            "Return only the ingredients, nothing else. "
                            "If you cannot find an ingredients list, reply with NONE."
                        ),
                    },
                ],
            }
        ],
        max_tokens=1024,
    )

    extracted = response.choices[0].message.content.strip()
    if not extracted or extracted.upper() == "NONE":
        raise HTTPException(status_code=400, detail="Could not extract ingredient list from image.")

    return {"ingredients_text": extracted}


@app.post("/analyze")
def analyze_ingredients(body: AnalyzeRequest, current_user: dict = Depends(get_current_user)):
    df           = app_state["df"]
    groq_client  = app_state["groq"]

    ingredients = parse_ingredients_text(body.ingredients_text)
    if not ingredients:
        raise HTTPException(status_code=400, detail="Could not parse any ingredients from the text.")

    result = analyze(ingredients, df, groq_client)
    _log_scan(current_user["id"], "manual", None, result)

    return {"error": None, "product": None, "analysis": result}


def _compute_compare_score(analysis: dict) -> float:
    tier_weights = {"high": 3, "medium": 2, "low": 1}
    score = 0.0
    for t in analysis.get("detected_toxicants", []):
        score += t.get("paper_count", 0) * tier_weights.get(t.get("tier", "low"), 1)
    return score


@app.post("/compare")
def compare_products(body: CompareRequest, current_user: dict = Depends(get_current_user)):
    if len(body.products) < 2:
        raise HTTPException(status_code=400, detail="Please provide at least 2 products to compare.")

    df          = app_state["df"]
    groq_client = app_state["groq"]

    results = []
    for i, item in enumerate(body.products):
        name        = item.name.strip() or f"Product {i + 1}"
        ingredients = parse_ingredients_text(item.ingredients_text)
        if not ingredients:
            results.append({
                "name": name,
                "analysis": {
                    "status": "error",
                    "error_message": "Could not parse ingredients.",
                    "verdict": "clean",
                    "total_toxicants_detected": 0,
                    "total_relevant_papers": 0,
                    "detected_toxicants": [],
                    "unmatched_ingredients": [],
                },
            })
            continue
        try:
            analysis = analyze(ingredients, df, groq_client)
        except Exception as e:
            print(f"[CosmoTox] compare analysis failed for '{name}': {e}")
            analysis = {
                "status": "error", "error_message": str(e),
                "verdict": "clean", "total_toxicants_detected": 0,
                "total_relevant_papers": 0, "detected_toxicants": [],
                "unmatched_ingredients": [],
            }
        results.append({"name": name, "analysis": analysis})

    # Log all products in this compare session, linked by a shared group ID
    group_id = str(uuid.uuid4())
    for r in results:
        _log_scan(current_user["id"], "compare", r["name"], r["analysis"], group_id)

    # Score and rank
    scored       = sorted([(r, _compute_compare_score(r["analysis"])) for r in results], key=lambda x: x[1])
    winner, _    = scored[0]
    winner_verdict = winner["analysis"].get("verdict", "clean")

    # Build recommendation reason
    winner_score = _compute_compare_score(winner["analysis"])
    if winner_score == 0:
        reason = f"{winner['name']} has no detected toxicant concerns."
        others_with_issues = [r for r, s in scored[1:] if s > 0]
        if others_with_issues:
            parts = []
            for r in others_with_issues[:3]:
                toxicants = [t["display_name"] for t in r["analysis"].get("detected_toxicants", [])[:2]]
                if toxicants:
                    parts.append(f"{r['name']} contains {' and '.join(toxicants)}")
            if parts:
                reason += " " + "; ".join(parts) + "."
    else:
        winner_toxicants = [t["display_name"] for t in winner["analysis"].get("detected_toxicants", [])[:2]]
        reason = f"{winner['name']} has the lowest overall toxicant burden"
        if winner_toxicants:
            reason += f", with only {' and '.join(winner_toxicants)} detected"
        reason += "."
        worst, _ = scored[-1]
        if worst["name"] != winner["name"]:
            worst_toxicants = [t["display_name"] for t in worst["analysis"].get("detected_toxicants", [])[:2]]
            if worst_toxicants:
                reason += f" Avoid {worst['name']} — it contains {' and '.join(worst_toxicants)}, among other concerns."

    return {
        "results": results,
        "recommendation": {
            "winner_name": winner["name"],
            "winner_verdict": winner_verdict,
            "reason": reason,
            "scores": [{"name": r["name"], "score": round(s, 1)} for r, s in scored],
        },
    }

# ── Watchlist endpoints ───────────────────────────────────────────────────────

@app.get("/watchlist")
def get_watchlist(current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    res = sb.table("watchlist").select("watchlist_type, key, added_at").eq("user_id", current_user["id"]).execute()
    return {"watchlist": res.data}


@app.post("/watchlist/{key}")
def add_watchlist(key: str, body: WatchlistBody, current_user: dict = Depends(get_current_user)):
    if body.watchlist_type not in ("toxicant", "organ"):
        raise HTTPException(status_code=400, detail="watchlist_type must be 'toxicant' or 'organ'.")
    sb = get_supabase()
    sb.table("watchlist").upsert({
        "user_id": current_user["id"],
        "watchlist_type": body.watchlist_type,
        "key": key,
    }).execute()
    return {"ok": True}


@app.delete("/watchlist/{key}")
def remove_watchlist(key: str, body: WatchlistBody, current_user: dict = Depends(get_current_user)):
    sb = get_supabase()
    sb.table("watchlist").delete().eq("user_id", current_user["id"]).eq("key", key).eq("watchlist_type", body.watchlist_type).execute()
    return {"ok": True}
