"""
BenchmarkHQ API — v2.0
======================
Serves industry benchmark data with built-in usage tracking.

Endpoints:
  GET  /                    → API info
  GET  /industries          → List all industries
  GET  /benchmark/{key}     → Get benchmark for an industry
  GET  /benchmark/{key}/features → Get feature list only
  POST /check               → Check features against benchmark
  GET  /stats               → API usage statistics (admin)
"""

import json, os, glob, time
from datetime import datetime, date
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="BenchmarkHQ API",
    description="Open-source industry benchmarks for web development. 42+ industries, 900+ websites analyzed.",
    version="2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# USAGE TRACKING
# ============================================================

STATS_FILE = "data/api_stats.json"

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "total_requests": 0,
        "first_request": None,
        "endpoints": {},
        "daily": {},
        "industries_queried": {},
        "checks_performed": 0,
        "unique_ips": [],
    }

def save_stats(stats):
    try:
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2, default=str)
    except:
        pass

stats = load_stats()

@app.middleware("http")
async def track_usage(request: Request, call_next):
    global stats

    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000)

    # Track request
    path = request.url.path
    today = str(date.today())
    ip = request.client.host if request.client else "unknown"

    stats["total_requests"] = stats.get("total_requests", 0) + 1

    if not stats.get("first_request"):
        stats["first_request"] = datetime.now().isoformat()

    # Endpoint counts
    if path not in stats.get("endpoints", {}):
        stats["endpoints"][path] = 0
    stats["endpoints"][path] += 1

    # Daily counts
    if today not in stats.get("daily", {}):
        stats["daily"][today] = {"requests": 0, "unique_ips": []}
    stats["daily"][today]["requests"] += 1
    if ip not in stats["daily"][today].get("unique_ips", []):
        stats["daily"][today]["unique_ips"].append(ip)

    # Track unique IPs (keep last 1000)
    if ip not in stats.get("unique_ips", []):
        stats["unique_ips"] = stats.get("unique_ips", [])
        stats["unique_ips"].append(ip)
        if len(stats["unique_ips"]) > 1000:
            stats["unique_ips"] = stats["unique_ips"][-1000:]

    # Track industry queries
    if path.startswith("/benchmark/"):
        industry = path.replace("/benchmark/", "").replace("/features", "")
        if industry not in stats.get("industries_queried", {}):
            stats["industries_queried"][industry] = 0
        stats["industries_queried"][industry] += 1

    # Save every 10 requests
    if stats["total_requests"] % 10 == 0:
        save_stats(stats)

    return response


# ============================================================
# LOAD BENCHMARK DATA
# ============================================================

benchmarks = {}

def load_data():
    """Load all benchmark data from data/ directory."""
    global benchmarks
    benchmarks = {}

    # SaaS category name mapping
    saas_names = {
        "accounting": "Accounting & Finance SaaS",
        "ai_ml_platforms": "AI & ML Platform SaaS",
        "analytics": "Analytics & BI SaaS",
        "cloud_storage": "Cloud Storage & Files SaaS",
        "communication": "Communication & Chat SaaS",
        "crm": "CRM SaaS",
        "customer_support": "Customer Support SaaS",
        "cybersecurity": "Cybersecurity SaaS",
        "design_creative": "Design & Creative SaaS",
        "developer_tools": "Developer Tools SaaS",
        "documentation": "Documentation & Knowledge Base SaaS",
        "ecommerce_platforms": "E-commerce Platform SaaS",
        "email_marketing": "Email Marketing SaaS",
        "forms_surveys": "Forms & Surveys SaaS",
        "hr_people": "HR & People SaaS",
        "marketing_automation": "Marketing Automation SaaS",
        "nocode_lowcode": "No-Code / Low-Code SaaS",
        "project_management": "Project Management SaaS",
        "scheduling": "Scheduling & Booking SaaS",
        "social_media": "Social Media Management SaaS",
    }

    # E-commerce country mapping
    ecom_countries = {
        "ecommerce_usa": ("E-commerce USA", "United States", "en", "USD"),
        "ecommerce_uk": ("E-commerce UK", "United Kingdom", "en", "GBP"),
        "ecommerce_canada": ("E-commerce Canada", "Canada", "en", "CAD"),
        "ecommerce_australia": ("E-commerce Australia", "Australia", "en", "AUD"),
        "ecommerce_france": ("E-commerce France", "France", "fr", "EUR"),
        "ecommerce_brazil": ("E-commerce Brazil", "Brazil", "pt", "BRL"),
        "ecommerce_india": ("E-commerce India", "India", "en", "INR"),
        "ecommerce_china": ("E-commerce China", "China", "zh", "CNY"),
        "ecommerce_mexico": ("E-commerce Mexico", "Mexico", "es", "MXN"),
        "ecommerce_argentina": ("E-commerce Argentina", "Argentina", "es", "ARS"),
        "ecommerce_russia": ("E-commerce Russia", "Russia", "ru", "RUB"),
        "ecommerce_spain": ("E-commerce Spain", "Spain", "es", "EUR"),
        "ecommerce_netherlands": ("E-commerce Netherlands", "Netherlands", "nl", "EUR"),
        "ecommerce_poland": ("E-commerce Poland", "Poland", "pl", "PLN"),
        "ecommerce_turkiye": ("E-commerce Turkiye", "Turkiye", "tr", "TRY"),
        "ecommerce_saudi": ("E-commerce Saudi Arabia", "Saudi Arabia", "ar", "SAR"),
        "ecommerce_uae": ("E-commerce UAE", "United Arab Emirates", "en", "AED"),
        "ecommerce_qatar": ("E-commerce Qatar", "Qatar", "en", "QAR"),
        "ecommerce_pakistan": ("E-commerce Pakistan", "Pakistan", "en", "PKR"),
    }

    # Load all frequency analysis files
    for freq_file in glob.glob("data/*/2*/frequency_analysis.json"):
        parts = freq_file.split("/")
        key = parts[1]  # e.g., 'crm', 'ecommerce_usa', 'news_pakistan'

        try:
            with open(freq_file) as f:
                data = json.load(f)
        except:
            continue

        if not data:
            continue

        # Determine metadata
        first = list(data.values())[0]
        sites = first.get("total_good_sites", first.get("total_sites", 0))
        total_features = len(data)
        critical = sum(1 for v in data.values() if v["classification"] == "CRITICAL")
        required = sum(1 for v in data.values() if v["classification"] == "REQUIRED")
        recommended = sum(1 for v in data.values() if v["classification"] == "RECOMMENDED")

        # Get latest timestamp from directory name
        ts_dir = parts[2] if len(parts) > 2 else ""
        last_updated = f"20{ts_dir[:2]}-{ts_dir[2:4]}-{ts_dir[4:6]}" if len(ts_dir) >= 6 else "2026-04-01"

        meta = {
            "name": key,
            "country": "",
            "language": "",
            "currency": "",
            "category": "general",
        }

        # E-commerce metadata
        if key in ecom_countries:
            name, country, lang, currency = ecom_countries[key]
            meta.update({"name": name, "country": country, "language": lang, "currency": currency, "category": "ecommerce"})
        # SaaS metadata
        elif key in saas_names:
            meta.update({"name": saas_names[key], "category": "saas"})
        # News metadata
        elif key.startswith("news_"):
            country_key = key.replace("news_", "")
            meta.update({"name": f"News & Media - {country_key.replace('_', ' ').title()}", "category": "news"})

        benchmarks[key] = {
            "key": key,
            "meta": meta,
            "last_updated": last_updated,
            "sites_analyzed": sites,
            "total_features": total_features,
            "critical": critical,
            "required": required,
            "recommended": recommended,
            "features": data,
        }

    print(f"Loaded {len(benchmarks)} industries")

load_data()


# ============================================================
# API MODELS
# ============================================================

class CheckRequest(BaseModel):
    industry: str
    features: List[str]


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "name": "BenchmarkHQ API",
        "version": "2.0",
        "description": "Open-source industry benchmarks for web development",
        "industries": len(benchmarks),
        "docs": "https://api.benchmarkhq.site/docs",
        "github": "https://github.com/abdur-rehman10/benchmarkhq",
        "website": "https://benchmarkhq.site",
    }


@app.get("/industries")
def list_industries(category: Optional[str] = None):
    """List all available industries. Optionally filter by category: ecommerce, saas, news"""
    industries = []
    for key, data in sorted(benchmarks.items()):
        if category and data["meta"].get("category") != category:
            continue
        industries.append({
            "key": key,
            "name": data["meta"]["name"],
            "category": data["meta"].get("category", "general"),
            "country": data["meta"]["country"],
            "language": data["meta"]["language"],
            "currency": data["meta"]["currency"],
            "last_updated": data["last_updated"],
            "sites_analyzed": data["sites_analyzed"],
            "total_features": data["total_features"],
            "critical": data["critical"],
            "required": data["required"],
            "recommended": data["recommended"],
        })
    return {"count": len(industries), "industries": industries}


@app.get("/benchmark/{key}")
def get_benchmark(key: str):
    """Get the full benchmark for an industry including all features with classifications."""
    if key not in benchmarks:
        raise HTTPException(status_code=404, detail=f"Industry '{key}' not found. Use /industries to see available options.")

    # Track this query
    if key not in stats.get("industries_queried", {}):
        stats["industries_queried"][key] = 0
    stats["industries_queried"][key] += 1

    data = benchmarks[key]
    return {
        "industry": key,
        "name": data["meta"]["name"],
        "category": data["meta"].get("category", "general"),
        "sites_analyzed": data["sites_analyzed"],
        "total_features": data["total_features"],
        "last_updated": data["last_updated"],
        "features": data["features"],
    }


@app.get("/benchmark/{key}/features")
def get_features(key: str):
    """Get just the feature list with classifications (no raw counts)."""
    if key not in benchmarks:
        raise HTTPException(status_code=404, detail=f"Industry '{key}' not found.")

    features = {}
    for fid, fdata in benchmarks[key]["features"].items():
        features[fid] = {
            "percentage": fdata["percentage"],
            "classification": fdata["classification"],
        }
    return {"industry": key, "features": features}


@app.post("/check")
def check_features(req: CheckRequest):
    """Check your features against an industry benchmark. Returns score and missing features."""
    if req.industry not in benchmarks:
        raise HTTPException(status_code=404, detail=f"Industry '{req.industry}' not found.")

    stats["checks_performed"] = stats.get("checks_performed", 0) + 1

    bench = benchmarks[req.industry]["features"]
    present = set(req.features)

    total_critical = []
    total_required = []
    total_recommended = []
    missing_critical = []
    missing_required = []
    missing_recommended = []

    for fid, fdata in bench.items():
        cls = fdata["classification"]
        if cls == "CRITICAL":
            total_critical.append(fid)
            if fid not in present:
                missing_critical.append(fid)
        elif cls == "REQUIRED":
            total_required.append(fid)
            if fid not in present:
                missing_required.append(fid)
        elif cls == "RECOMMENDED":
            total_recommended.append(fid)
            if fid not in present:
                missing_recommended.append(fid)

    # Score: critical features worth 3 points, required 2, recommended 1
    max_score = len(total_critical) * 3 + len(total_required) * 2 + len(total_recommended) * 1
    your_score = (len(total_critical) - len(missing_critical)) * 3 + \
                 (len(total_required) - len(missing_required)) * 2 + \
                 (len(total_recommended) - len(missing_recommended)) * 1

    score_pct = round(your_score / max_score * 100) if max_score > 0 else 0

    if score_pct >= 90:
        verdict = "EXCELLENT"
    elif score_pct >= 70:
        verdict = "GOOD"
    elif score_pct >= 50:
        verdict = "NEEDS WORK"
    else:
        verdict = "POOR"

    return {
        "industry": req.industry,
        "score": score_pct,
        "verdict": verdict,
        "features_checked": len(req.features),
        "missing_critical": missing_critical,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "summary": {
            "critical": f"{len(total_critical) - len(missing_critical)}/{len(total_critical)}",
            "required": f"{len(total_required) - len(missing_required)}/{len(total_required)}",
            "recommended": f"{len(total_recommended) - len(missing_recommended)}/{len(total_recommended)}",
        }
    }


@app.get("/stats")
def get_stats(key: Optional[str] = None):
    """API usage statistics. Pass ?key=admin_secret for full details."""
    admin_key = os.environ.get("ADMIN_KEY", "benchmarkhq2026")

    # Public stats (always visible)
    public = {
        "total_requests": stats.get("total_requests", 0),
        "industries_available": len(benchmarks),
        "checks_performed": stats.get("checks_performed", 0),
        "uptime_since": stats.get("first_request", "N/A"),
        "top_industries": dict(sorted(
            stats.get("industries_queried", {}).items(),
            key=lambda x: x[1], reverse=True
        )[:10]),
    }

    # Admin stats (with key)
    if key == admin_key:
        public["unique_ips_total"] = len(stats.get("unique_ips", []))
        public["endpoints"] = dict(sorted(
            stats.get("endpoints", {}).items(),
            key=lambda x: x[1], reverse=True
        ))
        public["daily"] = {
            day: {"requests": d["requests"], "unique_visitors": len(d.get("unique_ips", []))}
            for day, d in sorted(stats.get("daily", {}).items(), reverse=True)[:30]
        }

    return public


@app.get("/reload")
def reload_data(key: Optional[str] = None):
    """Reload benchmark data from disk. Requires admin key."""
    admin_key = os.environ.get("ADMIN_KEY", "benchmarkhq2026")
    if key != admin_key:
        raise HTTPException(status_code=403, detail="Admin key required. Use ?key=your_key")
    load_data()
    save_stats(stats)
    return {"status": "reloaded", "industries": len(benchmarks)}


# Save stats on shutdown
import atexit
atexit.register(lambda: save_stats(stats))
