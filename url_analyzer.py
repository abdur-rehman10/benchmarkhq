"""
BenchmarkHQ URL Analyzer
=========================
Adds a /analyze-url endpoint that uses GPT-4o to detect features on a website.

Flow:
  1. User pastes URL on contribute page → clicks "Analyze with AI"
  2. API fetches the page HTML
  3. GPT-4o analyzes HTML against the industry's feature list
  4. Returns which features were detected (with confidence)
  5. Frontend auto-checks the detected features

Add to your api.py:
  from url_analyzer import register_analyzer_routes
  register_analyzer_routes(app, benchmark_data)
  
  Where benchmark_data is your loaded benchmark dict.

Requires:
  OPENAI_API_KEY env var on Railway
  pip install httpx openai
"""

import json
import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import asyncio

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


async def fetch_page_html(url: str, timeout: int = 15) -> str:
    """Fetch a webpage's HTML content."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            # Return first 15000 chars of HTML (enough for GPT-4o to analyze)
            return resp.text[:15000]
        except httpx.TimeoutException:
            return ""
        except httpx.HTTPStatusError as e:
            return f"<!-- HTTP {e.response.status_code} -->"
        except Exception:
            return ""


async def analyze_with_gpt4o(url: str, html: str, features: dict, industry_name: str) -> dict:
    """Send URL + HTML + feature list to GPT-4o for analysis."""
    
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Build feature list for the prompt
    feature_list = []
    for fid, fdata in features.items():
        cls = fdata.get("classification", "OPTIONAL")
        pct = fdata.get("percentage", 0)
        feature_list.append(f"- {fid} ({cls}, {pct}% adoption)")
    
    features_text = "\n".join(feature_list)
    
    prompt = f"""Analyze this {industry_name} website and determine which features are present.

URL: {url}

Here is the HTML of the page (first 15000 chars):
```html
{html[:12000]}
```

Here are the features to check for. For each one, respond YES if you can confirm it exists on this website (either from the HTML above or from your knowledge of this website if it's well-known), or NO if you cannot confirm it:

{features_text}

Respond ONLY with a JSON object in this exact format, no other text:
{{
  "detected_features": ["feature_id_1", "feature_id_2", ...],
  "not_detected": ["feature_id_3", ...],
  "confidence": "high" or "medium" or "low",
  "notes": "Brief note about the analysis"
}}

Be thorough but honest. If the HTML doesn't show a feature clearly and you don't know the site well, mark it as not_detected. For well-known websites (Amazon, Google, etc.), you can use your knowledge to supplement what's visible in the HTML."""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a website feature analyst. You examine websites and identify which features they have. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 4000
    }
    
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            
            content = data["choices"][0]["message"]["content"]
            
            # Clean markdown fences if present
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError:
            return {
                "detected_features": [],
                "not_detected": list(features.keys()),
                "confidence": "low",
                "notes": "Failed to parse AI response"
            }
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"GPT-4o analysis failed: {str(e)}")


def register_analyzer_routes(app: FastAPI, get_benchmark_func=None):
    """
    Register the /analyze-url endpoint.
    
    get_benchmark_func: a function that takes an industry key and returns benchmark data dict.
                        If None, will try to fetch from the API itself.
    """
    
    @app.post("/analyze-url")
    async def analyze_url(request: Request):
        """
        Analyze a URL against an industry benchmark using GPT-4o.
        
        Body: {"url": "https://example.com", "industry": "ecommerce_usa"}
        Returns: {"detected_features": [...], "confidence": "high/medium/low", ...}
        """
        try:
            body = await request.json()
        except:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        url = body.get("url", "").strip()
        industry = body.get("industry", "").strip()
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        if not industry:
            raise HTTPException(status_code=400, detail="Industry is required")
        if not url.startswith("http"):
            url = "https://" + url
        
        # Get benchmark data for this industry
        benchmark = None
        if get_benchmark_func:
            benchmark = get_benchmark_func(industry)
        
        if not benchmark:
            # Try fetching from our own API
            async with httpx.AsyncClient(timeout=10) as client:
                try:
                    api_base = os.environ.get("API_URL", "http://localhost:8000")
                    resp = await client.get(f"{api_base}/benchmark/{industry}")
                    if resp.status_code == 200:
                        benchmark = resp.json()
                except:
                    pass
        
        if not benchmark or "features" not in benchmark:
            raise HTTPException(status_code=404, detail=f"Industry '{industry}' not found")
        
        features = benchmark["features"]
        industry_name = benchmark.get("name", industry)
        
        # Step 1: Fetch the page HTML
        html = await fetch_page_html(url)
        
        if not html:
            # Even without HTML, GPT-4o can analyze well-known sites
            html = f"<!-- Could not fetch HTML for {url}. Analyze based on your knowledge of this website. -->"
        
        # Step 2: Analyze with GPT-4o
        result = await analyze_with_gpt4o(url, html, features, industry_name)
        
        # Step 3: Enrich the response with feature details
        detected = result.get("detected_features", [])
        not_detected = result.get("not_detected", [])
        
        enriched_detected = []
        for fid in detected:
            if fid in features:
                enriched_detected.append({
                    "id": fid,
                    "classification": features[fid].get("classification", ""),
                    "percentage": features[fid].get("percentage", 0)
                })
            else:
                enriched_detected.append({"id": fid})
        
        enriched_missing = []
        for fid in not_detected:
            if fid in features:
                enriched_missing.append({
                    "id": fid,
                    "classification": features[fid].get("classification", ""),
                    "percentage": features[fid].get("percentage", 0)
                })
        
        # Calculate a score
        total = len(features)
        found = len(detected)
        score = round((found / total) * 100) if total > 0 else 0
        
        return {
            "url": url,
            "industry": industry,
            "industry_name": industry_name,
            "score": score,
            "detected_features": enriched_detected,
            "missing_features": enriched_missing,
            "detected_count": found,
            "total_features": total,
            "confidence": result.get("confidence", "medium"),
            "notes": result.get("notes", ""),
            "analysis_source": "gpt-4o"
        }


# Standalone test
if __name__ == "__main__":
    app = FastAPI()
    register_analyzer_routes(app)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
