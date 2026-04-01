"""
BenchmarkHQ API v1.0
Serves industry benchmark data from scanned results.
"""

import json
import glob
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BenchmarkHQ API",
    description="Open-source industry benchmarks for web development",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_all_data():
    """Load all frequency analysis data from disk."""
    industries = {}
    for path in sorted(glob.glob("data/*/*/frequency_analysis.json")):
        parts = path.split("/")
        industry_key = parts[1]
        date = parts[2]

        # Only keep the latest date for each industry
        if industry_key not in industries or date > industries[industry_key]["date"]:
            with open(path) as f:
                freq_data = json.load(f)

            # Load benchmark yaml metadata if exists
            yaml_path = path.replace("frequency_analysis.json", "benchmark.yaml")
            metadata = {}
            if os.path.exists(yaml_path):
                import yaml
                with open(yaml_path) as f:
                    benchmark = yaml.safe_load(f)
                    metadata = benchmark.get("metadata", {})

            industries[industry_key] = {
                "date": date,
                "metadata": metadata,
                "features": freq_data,
            }

    return industries


DATA = load_all_data()


@app.get("/")
def root():
    return {
        "name": "BenchmarkHQ API",
        "version": "1.0.0",
        "industries": len(DATA),
        "endpoints": [
            "GET /industries",
            "GET /benchmark/{industry}",
            "GET /benchmark/{industry}/features",
            "GET /benchmark/{industry}/features?level=critical",
            "POST /check",
        ],
    }


@app.get("/industries")
def list_industries():
    """List all available industries with metadata."""
    result = []
    for key, val in DATA.items():
        features = val["features"]
        critical = sum(1 for v in features.values() if v["classification"] == "CRITICAL")
        required = sum(1 for v in features.values() if v["classification"] == "REQUIRED")
        recommended = sum(1 for v in features.values() if v["classification"] == "RECOMMENDED")

        result.append({
            "key": key,
            "name": val["metadata"].get("name", key),
            "country": val["metadata"].get("country", ""),
            "language": val["metadata"].get("language", ""),
            "currency": val["metadata"].get("currency", ""),
            "last_updated": val["date"],
            "sites_analyzed": val["metadata"].get("sites_analyzed", 0),
            "total_features": len(features),
            "critical": critical,
            "required": required,
            "recommended": recommended,
        })

    return {"count": len(result), "industries": result}


@app.get("/benchmark/{industry}")
def get_benchmark(industry: str):
    """Get the full benchmark for an industry."""
    if industry not in DATA:
        raise HTTPException(status_code=404, detail=f"Industry '{industry}' not found. Use /industries to see available options.")

    val = DATA[industry]
    features = val["features"]

    grouped = {"critical": [], "required": [], "recommended": [], "nice_to_have": [], "innovative": []}
    for key, feat in features.items():
        entry = {
            "id": key,
            "frequency_percent": feat["frequency_percent"],
            "present_in": feat["present_count"],
            "total_sites": feat["total_good_sites"],
            "classification": feat["classification"],
        }
        cls = feat["classification"].lower()
        if cls in grouped:
            grouped[cls].append(entry)

    return {
        "industry": industry,
        "metadata": val["metadata"],
        "last_updated": val["date"],
        "feature_counts": {k: len(v) for k, v in grouped.items()},
        "features": grouped,
    }


@app.get("/benchmark/{industry}/features")
def get_features(
    industry: str,
    level: str = Query(None, description="Filter by level: critical, required, recommended, nice_to_have, innovative"),
):
    """Get features for an industry, optionally filtered by classification level."""
    if industry not in DATA:
        raise HTTPException(status_code=404, detail=f"Industry '{industry}' not found.")

    features = DATA[industry]["features"]
    result = []

    for key, feat in features.items():
        if level and feat["classification"].lower() != level.lower():
            continue
        result.append({
            "id": key,
            "frequency_percent": feat["frequency_percent"],
            "present_in": feat["present_count"],
            "total_sites": feat["total_good_sites"],
            "classification": feat["classification"],
        })

    result.sort(key=lambda x: x["frequency_percent"], reverse=True)

    return {
        "industry": industry,
        "filter": level or "all",
        "count": len(result),
        "features": result,
    }


@app.post("/check")
def check_app(body: dict):
    """
    Check an app against an industry benchmark.

    Send:
    {
        "industry": "ecommerce_usa",
        "features": ["product_search", "shopping_cart", "login_signup"]
    }

    Returns a score and list of missing features.
    """
    industry = body.get("industry", "")
    app_features = body.get("features", [])

    if industry not in DATA:
        raise HTTPException(status_code=404, detail=f"Industry '{industry}' not found.")

    if not app_features:
        raise HTTPException(status_code=400, detail="'features' list is required.")

    features = DATA[industry]["features"]

    # Calculate score
    critical = {k: v for k, v in features.items() if v["classification"] == "CRITICAL"}
    required = {k: v for k, v in features.items() if v["classification"] == "REQUIRED"}
    recommended = {k: v for k, v in features.items() if v["classification"] == "RECOMMENDED"}

    app_features_set = set(f.lower().strip() for f in app_features)

    critical_met = [k for k in critical if k in app_features_set]
    critical_missing = [k for k in critical if k not in app_features_set]
    required_met = [k for k in required if k in app_features_set]
    required_missing = [k for k in required if k not in app_features_set]
    recommended_met = [k for k in recommended if k in app_features_set]
    recommended_missing = [k for k in recommended if k not in app_features_set]

    # Score: critical features worth 2 points, required 1 point, recommended 0.5
    max_score = len(critical) * 2 + len(required) * 1 + len(recommended) * 0.5
    earned = len(critical_met) * 2 + len(required_met) * 1 + len(recommended_met) * 0.5
    score = round(earned / max_score * 100) if max_score > 0 else 0

    return {
        "industry": industry,
        "score": score,
        "summary": {
            "critical": {"met": len(critical_met), "total": len(critical), "missing": critical_missing},
            "required": {"met": len(required_met), "total": len(required), "missing": required_missing},
            "recommended": {"met": len(recommended_met), "total": len(recommended), "missing": recommended_missing},
        },
        "features_submitted": len(app_features),
        "verdict": "EXCELLENT" if score >= 90 else "GOOD" if score >= 75 else "NEEDS WORK" if score >= 50 else "INCOMPLETE",
    }


if __name__ == "__main__":
    import uvicorn
    print(f"\nLoaded {len(DATA)} industries")
    print("Starting BenchmarkHQ API at http://localhost:8000")
    print("API docs at http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
