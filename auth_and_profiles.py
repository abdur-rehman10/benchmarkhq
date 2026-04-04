"""
BenchmarkHQ Auth & Profile System
===================================
Adds GitHub + Google OAuth, user profiles, contributor credit.

New endpoints:
  GET  /auth/github           - Start GitHub OAuth
  GET  /auth/github/callback  - GitHub OAuth callback
  GET  /auth/google           - Start Google OAuth
  GET  /auth/google/callback  - Google OAuth callback
  GET  /auth/me               - Get current user (requires JWT)
  GET  /profile/{username}    - Public contributor profile (JSON)
  GET  /contributors          - Leaderboard / top contributors
  GET  /contributors/{username}/badge - Shareable badge image data

Setup required:
  1. Create GitHub OAuth App: github.com/settings/developers
     - Homepage URL: https://benchmarkhq.site
     - Callback URL: https://api.benchmarkhq.site/auth/github/callback
  2. Create Google OAuth credentials: console.cloud.google.com
     - Authorized redirect: https://api.benchmarkhq.site/auth/google/callback
  3. Set env vars on Railway:
     GITHUB_CLIENT_ID=...
     GITHUB_CLIENT_SECRET=...
     GOOGLE_CLIENT_ID=...
     GOOGLE_CLIENT_SECRET=...
     JWT_SECRET=<random-32-char-string>

Dependencies (add to requirements.txt):
  PyJWT>=2.8
  httpx>=0.27
"""

import sqlite3
import json
import os
import jwt
import time
import secrets
import hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request, Query, Depends
from fastapi.responses import RedirectResponse, JSONResponse
import httpx

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
JWT_SECRET = os.environ.get("JWT_SECRET", "benchmarkhq-dev-secret-change-me")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "benchmarkhq2026")

SITE_URL = os.environ.get("SITE_URL", "https://benchmarkhq.site")
API_URL = os.environ.get("API_URL", "https://api.benchmarkhq.site")

DB_PATH = os.environ.get("CONTRIB_DB", "contributions.db")

# -------------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_auth_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            email TEXT,
            avatar_url TEXT,
            provider TEXT NOT NULL,
            provider_id TEXT NOT NULL,
            bio TEXT DEFAULT '',
            website TEXT DEFAULT '',
            joined_at TEXT NOT NULL,
            last_login TEXT,
            role TEXT DEFAULT 'contributor',
            is_verified INTEGER DEFAULT 0,
            contribution_count INTEGER DEFAULT 0,
            approved_count INTEGER DEFAULT 0
        );
        
        CREATE UNIQUE INDEX IF NOT EXISTS idx_provider 
            ON users(provider, provider_id);
        
        CREATE TABLE IF NOT EXISTS contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            industry TEXT,
            url TEXT,
            data TEXT NOT NULL,
            confidence_score INTEGER DEFAULT 0,
            has_screenshots INTEGER DEFAULT 0,
            contributor_name TEXT,
            contributor_email TEXT,
            status TEXT DEFAULT 'pending',
            review_notes TEXT,
            submitted_at TEXT NOT NULL,
            reviewed_at TEXT,
            ip_hash TEXT,
            duplicate_of INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_contrib_status 
            ON contributions(status);
        CREATE INDEX IF NOT EXISTS idx_contrib_user 
            ON contributions(user_id);
        CREATE INDEX IF NOT EXISTS idx_contrib_industry_url 
            ON contributions(industry, url);
    """)
    conn.commit()
    conn.close()

init_auth_db()

# -------------------------------------------------------------------
# JWT HELPERS
# -------------------------------------------------------------------

def create_token(user_id: int, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "exp": int(time.time()) + 86400 * 30,  # 30 days
        "iat": int(time.time())
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return verify_token(auth[7:])

async def get_optional_user(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        return verify_token(auth[7:])
    except:
        return None

# -------------------------------------------------------------------
# QUALITY CHECKS (moved from contributions_api.py)
# -------------------------------------------------------------------

def run_quality_checks(data: dict, conn, user=None) -> dict:
    checks = {
        "url_valid": False,
        "url_https": False,
        "duplicate": False,
        "duplicate_id": None,
        "has_screenshots": data.get("has_screenshots", False),
        "authenticated_user": user is not None,
        "feature_count": 0,
        "flags": []
    }
    
    url = data.get("url", "")
    if url:
        checks["url_valid"] = url.startswith("http://") or url.startswith("https://")
        checks["url_https"] = url.startswith("https://")
        if not checks["url_valid"]:
            checks["flags"].append("Invalid URL format")
    
    if url and data.get("industry"):
        existing = conn.execute(
            """SELECT id, status FROM contributions 
               WHERE url = ? AND industry = ? AND type = ? 
               AND submitted_at > datetime('now', '-30 days')
               ORDER BY submitted_at DESC LIMIT 1""",
            (url, data["industry"], data["type"])
        ).fetchone()
        if existing:
            checks["duplicate"] = True
            checks["duplicate_id"] = existing["id"]
            checks["flags"].append(f"Duplicate of #{existing['id']}")
    
    if data.get("type") == "review":
        features = data.get("features_found", [])
        checks["feature_count"] = len(features)
        total = data.get("features_total", 0)
        if len(features) < 3:
            checks["flags"].append("Very few features checked")
        if total > 0 and len(features) == total:
            checks["flags"].append("ALL features checked — suspicious")
    
    if data.get("type") == "feature":
        if not data.get("description"):
            checks["flags"].append("No description")
        examples = data.get("example_sites", "")
        if len(str(examples).strip()) < 10:
            checks["flags"].append("Few example websites")
    
    # Calculate confidence
    score = 0
    if checks["authenticated_user"]: score += 25  # authenticated = big boost
    if checks["has_screenshots"]: score += 25
    if checks["url_https"]: score += 10
    if not checks["duplicate"]: score += 10
    if checks["feature_count"] >= 5: score += 10
    if checks["feature_count"] >= 10: score += 10
    if len(checks["flags"]) == 0: score += 10
    checks["confidence_score"] = min(score, 100)
    
    return checks

# -------------------------------------------------------------------
# REGISTER ALL ROUTES
# -------------------------------------------------------------------

def register_auth_routes(app: FastAPI):

    # ---------------------------------------------------------------
    # GITHUB OAUTH
    # ---------------------------------------------------------------
    
    @app.get("/auth/github")
    async def github_login(redirect: str = Query(f"{SITE_URL}/contribute.html")):
        state = secrets.token_urlsafe(16)
        params = {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": f"{API_URL}/auth/github/callback",
            "scope": "user:email",
            "state": f"{state}|{redirect}"
        }
        url = "https://github.com/login/oauth/authorize?" + "&".join(f"{k}={v}" for k,v in params.items())
        return RedirectResponse(url)
    
    @app.get("/auth/github/callback")
    async def github_callback(code: str, state: str = ""):
        redirect_to = state.split("|", 1)[1] if "|" in state else f"{SITE_URL}/contribute.html"
        
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_res = await client.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code
                },
                headers={"Accept": "application/json"}
            )
            token_data = token_res.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                return RedirectResponse(f"{redirect_to}?auth_error=github_failed")
            
            # Get user info
            user_res = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            gh_user = user_res.json()
            
            # Get primary email
            email_res = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            emails = email_res.json()
            primary_email = next(
                (e["email"] for e in emails if e.get("primary")),
                gh_user.get("email", "")
            ) if isinstance(emails, list) else ""
        
        # Create or update user
        conn = get_db()
        existing = conn.execute(
            "SELECT id, username FROM users WHERE provider = 'github' AND provider_id = ?",
            (str(gh_user["id"]),)
        ).fetchone()
        
        username = gh_user.get("login", "").lower()
        display_name = gh_user.get("name") or username
        avatar = gh_user.get("avatar_url", "")
        now = datetime.utcnow().isoformat()
        
        if existing:
            user_id = existing["id"]
            username = existing["username"]
            conn.execute(
                "UPDATE users SET last_login = ?, avatar_url = ?, display_name = ? WHERE id = ?",
                (now, avatar, display_name, user_id)
            )
        else:
            # Ensure unique username
            base_username = username
            counter = 1
            while conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
                username = f"{base_username}{counter}"
                counter += 1
            
            conn.execute(
                """INSERT INTO users (username, display_name, email, avatar_url, provider, provider_id, joined_at, last_login)
                   VALUES (?, ?, ?, ?, 'github', ?, ?, ?)""",
                (username, display_name, primary_email, avatar, str(gh_user["id"]), now, now)
            )
            user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        conn.commit()
        conn.close()
        
        token = create_token(user_id, username)
        sep = "&" if "?" in redirect_to else "?"
        return RedirectResponse(f"{redirect_to}{sep}token={token}&username={username}")
    
    # ---------------------------------------------------------------
    # GOOGLE OAUTH
    # ---------------------------------------------------------------
    
    @app.get("/auth/google")
    async def google_login(redirect: str = Query(f"{SITE_URL}/contribute.html")):
        state = secrets.token_urlsafe(16) + "|" + redirect
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": f"{API_URL}/auth/google/callback",
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account"
        }
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join(f"{k}={v}" for k,v in params.items())
        return RedirectResponse(url)
    
    @app.get("/auth/google/callback")
    async def google_callback(code: str, state: str = ""):
        redirect_to = state.split("|", 1)[1] if "|" in state else f"{SITE_URL}/contribute.html"
        
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{API_URL}/auth/google/callback"
                }
            )
            token_data = token_res.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                return RedirectResponse(f"{redirect_to}?auth_error=google_failed")
            
            user_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            g_user = user_res.json()
        
        conn = get_db()
        existing = conn.execute(
            "SELECT id, username FROM users WHERE provider = 'google' AND provider_id = ?",
            (str(g_user["id"]),)
        ).fetchone()
        
        display_name = g_user.get("name", "")
        email = g_user.get("email", "")
        avatar = g_user.get("picture", "")
        now = datetime.utcnow().isoformat()
        
        # Generate username from email or name
        base_username = email.split("@")[0].lower() if email else display_name.lower().replace(" ", "")
        base_username = "".join(c for c in base_username if c.isalnum() or c == "_")[:20]
        username = base_username
        
        if existing:
            user_id = existing["id"]
            username = existing["username"]
            conn.execute(
                "UPDATE users SET last_login = ?, avatar_url = ?, display_name = ? WHERE id = ?",
                (now, avatar, display_name, user_id)
            )
        else:
            counter = 1
            while conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
                username = f"{base_username}{counter}"
                counter += 1
            
            conn.execute(
                """INSERT INTO users (username, display_name, email, avatar_url, provider, provider_id, joined_at, last_login)
                   VALUES (?, ?, ?, ?, 'google', ?, ?, ?)""",
                (username, display_name, email, avatar, str(g_user["id"]), now, now)
            )
            user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        conn.commit()
        conn.close()
        
        token = create_token(user_id, username)
        sep = "&" if "?" in redirect_to else "?"
        return RedirectResponse(f"{redirect_to}{sep}token={token}&username={username}")
    
    # ---------------------------------------------------------------
    # USER ENDPOINTS
    # ---------------------------------------------------------------
    
    @app.get("/auth/me")
    async def get_me(request: Request):
        user = await get_current_user(request)
        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user["sub"],)).fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get contribution stats
        stats = conn.execute(
            """SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending
               FROM contributions WHERE user_id = ?""",
            (user["sub"],)
        ).fetchone()
        
        industries = conn.execute(
            """SELECT DISTINCT industry FROM contributions 
               WHERE user_id = ? AND status = 'approved' AND industry != ''""",
            (user["sub"],)
        ).fetchall()
        
        conn.close()
        
        return {
            "id": row["id"],
            "username": row["username"],
            "display_name": row["display_name"],
            "avatar_url": row["avatar_url"],
            "provider": row["provider"],
            "joined_at": row["joined_at"],
            "bio": row["bio"],
            "role": row["role"],
            "stats": {
                "total_contributions": stats["total"] or 0,
                "approved": stats["approved"] or 0,
                "pending": stats["pending"] or 0,
                "industries": [r["industry"] for r in industries]
            }
        }
    
    @app.post("/auth/update-profile")
    async def update_profile(request: Request):
        user = await get_current_user(request)
        data = await request.json()
        
        conn = get_db()
        allowed_fields = {"bio", "website", "display_name"}
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [user["sub"]]
            conn.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
            conn.commit()
        
        conn.close()
        return {"status": "updated"}
    
    # ---------------------------------------------------------------
    # PUBLIC PROFILE
    # ---------------------------------------------------------------
    
    @app.get("/profile/{username}")
    async def get_profile(username: str):
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        
        if not user:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Contribution stats
        stats = conn.execute(
            """SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) as approved
               FROM contributions WHERE user_id = ?""",
            (user["id"],)
        ).fetchone()
        
        # Industries contributed to (approved only)
        industries = conn.execute(
            """SELECT industry, COUNT(*) as cnt FROM contributions 
               WHERE user_id = ? AND status = 'approved' AND industry != ''
               GROUP BY industry ORDER BY cnt DESC""",
            (user["id"],)
        ).fetchall()
        
        # Recent approved contributions
        recent = conn.execute(
            """SELECT type, industry, url, submitted_at FROM contributions 
               WHERE user_id = ? AND status = 'approved'
               ORDER BY submitted_at DESC LIMIT 10""",
            (user["id"],)
        ).fetchall()
        
        # Calculate badge level
        approved = stats["approved"] or 0
        if approved >= 50: level = "gold"
        elif approved >= 20: level = "silver"
        elif approved >= 5: level = "bronze"
        elif approved >= 1: level = "contributor"
        else: level = "new"
        
        conn.close()
        
        return {
            "username": user["username"],
            "display_name": user["display_name"],
            "avatar_url": user["avatar_url"],
            "bio": user["bio"],
            "website": user["website"],
            "provider": user["provider"],
            "joined_at": user["joined_at"],
            "badge_level": level,
            "stats": {
                "total_contributions": stats["total"] or 0,
                "approved_contributions": approved,
                "industries_count": len(industries),
                "industries": [{"name": r["industry"], "count": r["cnt"]} for r in industries]
            },
            "recent_contributions": [dict(r) for r in recent],
            "share_text": f"I'm a {level} contributor to @BenchmarkHQ! {approved} approved contributions across {len(industries)} industries. Help build web development standards: benchmarkhq.site/contribute.html"
        }
    
    # ---------------------------------------------------------------
    # CONTRIBUTORS LEADERBOARD
    # ---------------------------------------------------------------
    
    @app.get("/contributors")
    async def leaderboard(limit: int = Query(20)):
        conn = get_db()
        rows = conn.execute(
            """SELECT u.username, u.display_name, u.avatar_url, u.joined_at,
                      COUNT(c.id) as total,
                      SUM(CASE WHEN c.status='approved' THEN 1 ELSE 0 END) as approved,
                      COUNT(DISTINCT c.industry) as industries
               FROM users u
               LEFT JOIN contributions c ON c.user_id = u.id
               GROUP BY u.id
               HAVING approved > 0
               ORDER BY approved DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
        conn.close()
        
        return {
            "contributors": [
                {
                    "rank": i + 1,
                    "username": r["username"],
                    "display_name": r["display_name"],
                    "avatar_url": r["avatar_url"],
                    "approved_contributions": r["approved"],
                    "industries": r["industries"],
                    "badge_level": "gold" if r["approved"] >= 50 else "silver" if r["approved"] >= 20 else "bronze" if r["approved"] >= 5 else "contributor"
                }
                for i, r in enumerate(rows)
            ]
        }
    
    # ---------------------------------------------------------------
    # SUBMIT CONTRIBUTION (authenticated version)
    # ---------------------------------------------------------------
    
    @app.post("/contribute")
    async def submit_contribution(request: Request):
        data = await request.json()
        
        if data.get("type") not in ("review", "website", "feature"):
            raise HTTPException(status_code=400, detail="Invalid contribution type")
        
        # Get user if authenticated
        user = await get_optional_user(request)
        user_id = user["sub"] if user else None
        
        # Rate limit by IP
        client_ip = request.client.host if request.client else "unknown"
        ip_hash = hashlib.sha256(f"{client_ip}_bhq".encode()).hexdigest()[:16]
        
        conn = get_db()
        
        # Rate limit: 10/hour for anon, 50/hour for authenticated
        rate_limit = 50 if user else 10
        recent = conn.execute(
            "SELECT COUNT(*) as cnt FROM contributions WHERE ip_hash = ? AND submitted_at > datetime('now', '-1 hour')",
            (ip_hash,)
        ).fetchone()
        if recent["cnt"] >= rate_limit:
            conn.close()
            raise HTTPException(status_code=429, detail="Too many submissions. Please wait.")
        
        # Quality checks
        checks = run_quality_checks(data, conn, user)
        
        store_data = {k: v for k, v in data.items() if not k.startswith("_")}
        store_data["quality_checks"] = checks
        
        # Get contributor info from user profile if authenticated
        contributor_name = ""
        contributor_email = ""
        if user_id:
            u = conn.execute("SELECT display_name, email FROM users WHERE id = ?", (user_id,)).fetchone()
            if u:
                contributor_name = u["display_name"]
                contributor_email = u["email"] or ""
        else:
            contributor_name = data.get("contributor_name", "")
            contributor_email = data.get("contributor_email", "")
        
        conn.execute(
            """INSERT INTO contributions 
               (user_id, type, industry, url, data, confidence_score, has_screenshots,
                contributor_name, contributor_email, status, submitted_at, ip_hash, duplicate_of)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)""",
            (
                user_id,
                data["type"],
                data.get("industry", ""),
                data.get("url", ""),
                json.dumps(store_data),
                checks["confidence_score"],
                1 if checks["has_screenshots"] else 0,
                contributor_name,
                contributor_email,
                data.get("submitted_at", datetime.utcnow().isoformat()),
                ip_hash,
                checks.get("duplicate_id")
            )
        )
        conn.commit()
        
        submission_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Update user contribution count
        if user_id:
            conn.execute(
                "UPDATE users SET contribution_count = contribution_count + 1 WHERE id = ?",
                (user_id,)
            )
            conn.commit()
        
        conn.close()
        
        return {
            "status": "submitted",
            "id": submission_id,
            "confidence_score": checks["confidence_score"],
            "flags": checks["flags"],
            "authenticated": user is not None,
            "message": "Your contribution is in the review queue."
        }
    
    # ---------------------------------------------------------------
    # ADMIN: Approve/Reject (updates user stats)
    # ---------------------------------------------------------------
    
    @app.post("/admin/contributions/{cid}/approve")
    async def approve(cid: int, key: str = Query(...), notes: str = Query("")):
        if key != ADMIN_KEY:
            raise HTTPException(status_code=403, detail="Invalid key")
        
        conn = get_db()
        row = conn.execute("SELECT * FROM contributions WHERE id = ?", (cid,)).fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404)
        
        conn.execute(
            "UPDATE contributions SET status='approved', reviewed_at=?, review_notes=? WHERE id=?",
            (datetime.utcnow().isoformat(), notes, cid)
        )
        
        # Update user's approved count
        if row["user_id"]:
            conn.execute(
                "UPDATE users SET approved_count = approved_count + 1 WHERE id = ?",
                (row["user_id"],)
            )
        
        conn.commit()
        conn.close()
        return {"status": "approved", "id": cid}
    
    @app.post("/admin/contributions/{cid}/reject")
    async def reject(cid: int, key: str = Query(...), notes: str = Query("")):
        if key != ADMIN_KEY:
            raise HTTPException(status_code=403, detail="Invalid key")
        
        conn = get_db()
        conn.execute(
            "UPDATE contributions SET status='rejected', reviewed_at=?, review_notes=? WHERE id=?",
            (datetime.utcnow().isoformat(), notes, cid)
        )
        conn.commit()
        conn.close()
        return {"status": "rejected", "id": cid}
    
    # ---------------------------------------------------------------
    # ADMIN: List contributions + stats
    # ---------------------------------------------------------------
    
    @app.get("/admin/contributions")
    async def list_contributions(
        key: str = Query(...), status: str = Query("pending"),
        limit: int = Query(50), offset: int = Query(0)
    ):
        if key != ADMIN_KEY:
            raise HTTPException(status_code=403)
        
        conn = get_db()
        rows = conn.execute(
            """SELECT c.*, u.username, u.display_name as user_display, u.avatar_url as user_avatar
               FROM contributions c
               LEFT JOIN users u ON u.id = c.user_id
               WHERE c.status = ?
               ORDER BY c.confidence_score DESC, c.has_screenshots DESC, c.submitted_at DESC
               LIMIT ? OFFSET ?""",
            (status, limit, offset)
        ).fetchall()
        
        total = conn.execute(
            "SELECT COUNT(*) as cnt FROM contributions WHERE status = ?", (status,)
        ).fetchone()["cnt"]
        conn.close()
        
        return {"contributions": [dict(r) for r in rows], "total": total}
    
    @app.get("/admin/contribution-stats")
    async def contribution_stats(key: str = Query(...)):
        if key != ADMIN_KEY:
            raise HTTPException(status_code=403)
        
        conn = get_db()
        stats = {}
        for s in ["pending", "approved", "rejected"]:
            stats[s] = conn.execute(
                "SELECT COUNT(*) as cnt FROM contributions WHERE status = ?", (s,)
            ).fetchone()["cnt"]
        stats["total"] = sum(stats.values())
        stats["total_users"] = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()["cnt"]
        stats["with_screenshots"] = conn.execute(
            "SELECT COUNT(*) as cnt FROM contributions WHERE has_screenshots = 1"
        ).fetchone()["cnt"]
        stats["authenticated_submissions"] = conn.execute(
            "SELECT COUNT(*) as cnt FROM contributions WHERE user_id IS NOT NULL"
        ).fetchone()["cnt"]
        
        top_industries = conn.execute(
            """SELECT industry, COUNT(*) as cnt FROM contributions 
               WHERE industry != '' GROUP BY industry ORDER BY cnt DESC LIMIT 10"""
        ).fetchall()
        stats["top_industries"] = [{"industry": r["industry"], "count": r["cnt"]} for r in top_industries]
        
        top_contributors = conn.execute(
            """SELECT u.username, u.display_name, u.avatar_url, COUNT(c.id) as cnt
               FROM contributions c JOIN users u ON u.id = c.user_id
               GROUP BY c.user_id ORDER BY cnt DESC LIMIT 5"""
        ).fetchall()
        stats["top_contributors"] = [dict(r) for r in top_contributors]
        
        stats["last_7_days"] = conn.execute(
            "SELECT COUNT(*) as cnt FROM contributions WHERE submitted_at > datetime('now', '-7 days')"
        ).fetchone()["cnt"]
        
        conn.close()
        return stats

    # ---------------------------------------------------------------
    # ADMIN DASHBOARD (HTML - updated with user info)
    # ---------------------------------------------------------------
    
    @app.get("/admin", response_class=HTMLResponse)
    async def admin_dashboard(key: str = Query("")):
        if key != ADMIN_KEY:
            return HTMLResponse(content="""<!DOCTYPE html><html><head><title>Admin</title>
            <style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#0C0C0E;color:#E8E6E3}
            .box{background:#141416;padding:40px;border-radius:12px;border:1px solid #222;text-align:center;max-width:400px}
            input{width:100%;padding:12px;background:#1A1A1E;border:1px solid #333;border-radius:8px;color:#E8E6E3;font-size:14px;margin:16px 0;outline:none}
            button{padding:12px 32px;background:#C4A46C;color:#0C0C0E;border:none;border-radius:8px;font-weight:600;cursor:pointer}</style></head>
            <body><div class="box"><h2>Admin</h2>
            <form onsubmit="event.preventDefault();location.href='/admin?key='+document.getElementById('k').value">
            <input id="k" type="password" placeholder="Admin key" autofocus><button type="submit">Enter</button></form></div></body></html>""")
        
        # Full admin dashboard HTML (same as before but with user columns)
        return HTMLResponse(content=f"""<!DOCTYPE html><html><head><title>Admin - BenchmarkHQ</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,sans-serif;background:#0C0C0E;color:#E8E6E3;line-height:1.6}}
.top{{padding:16px 24px;border-bottom:1px solid #222;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;background:rgba(12,12,14,.95);backdrop-filter:blur(10px);z-index:10}}
.top h1{{font-size:18px}}.top h1 span{{color:#C4A46C}}.top a{{color:#8A8A8D;font-size:13px;text-decoration:none}}
.wrap{{max-width:1100px;margin:0 auto;padding:24px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:24px}}
.stat{{background:#141416;border:1px solid #222;border-radius:10px;padding:14px}}
.stat-l{{font-size:11px;color:#8A8A8D;text-transform:uppercase;letter-spacing:.05em;margin-bottom:2px}}
.stat-v{{font-size:22px;font-weight:500}}
.tabs{{display:flex;gap:6px;margin-bottom:18px}}
.tab{{padding:8px 16px;border:1px solid #222;border-radius:6px;background:#141416;color:#8A8A8D;font-size:13px;cursor:pointer}}
.tab.active{{border-color:#C4A46C;color:#C4A46C}}
.card{{background:#141416;border:1px solid #222;border-radius:10px;padding:16px;margin-bottom:10px}}
.card-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}}
.badge{{font-size:11px;padding:2px 8px;border-radius:10px;font-weight:500}}
.t-review{{background:rgba(91,142,201,.15);color:#5B8EC9}}
.t-website{{background:rgba(92,176,138,.15);color:#5CB08A}}
.t-feature{{background:rgba(212,136,58,.15);color:#D4883A}}
.score{{font-family:monospace;font-size:12px;padding:2px 8px;border-radius:10px;border:1px solid #333}}
.user-row{{display:flex;align-items:center;gap:8px;margin-bottom:6px}}
.user-row img{{width:24px;height:24px;border-radius:50%}}
.user-row span{{font-size:13px;font-weight:500}}
.meta{{font-size:12px;color:#8A8A8D}}
.flag{{display:inline-block;font-size:11px;padding:2px 8px;border-radius:4px;background:rgba(199,95,95,.12);color:#C75F5F;margin:2px 4px 2px 0}}
.feats{{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}}
.ft{{font-size:11px;padding:2px 8px;border-radius:4px;background:#1A1A1E;color:#8A8A8D}}
.actions{{display:flex;gap:8px;margin-top:12px;padding-top:12px;border-top:1px solid #222}}
.ni{{flex:1;padding:8px;background:#1A1A1E;border:1px solid #333;border-radius:6px;color:#E8E6E3;font-size:13px;outline:none}}
.btn{{padding:8px 18px;border-radius:6px;border:none;font-size:13px;font-weight:500;cursor:pointer}}
.btn-a{{background:rgba(92,176,138,.15);color:#5CB08A;border:1px solid rgba(92,176,138,.3)}}
.btn-r{{background:rgba(199,95,95,.1);color:#C75F5F;border:1px solid rgba(199,95,95,.2)}}
.empty{{text-align:center;padding:60px;color:#5A5A5D}}
.ss{{display:inline-flex;align-items:center;gap:4px;font-size:11px;padding:2px 8px;border-radius:4px;background:rgba(196,164,108,.12);color:#C4A46C;margin-left:6px}}
</style></head><body>
<div class="top"><h1>Benchmark<span>HQ</span> Admin</h1><a href="/">Back to site</a></div>
<div class="wrap">
<div class="stats" id="sg"></div>
<div class="tabs">
<div class="tab active" onclick="load('pending',this)">Pending</div>
<div class="tab" onclick="load('approved',this)">Approved</div>
<div class="tab" onclick="load('rejected',this)">Rejected</div>
</div>
<div id="list"></div>
</div>
<script>
const K='{ADMIN_KEY}';
async function loadStats(){{try{{const r=await(await fetch(`/admin/contribution-stats?key=${{K}}`)).json();document.getElementById('sg').innerHTML=`
<div class="stat"><div class="stat-l">Pending</div><div class="stat-v" style="color:#D4883A">${{r.pending}}</div></div>
<div class="stat"><div class="stat-l">Approved</div><div class="stat-v" style="color:#5CB08A">${{r.approved}}</div></div>
<div class="stat"><div class="stat-l">Rejected</div><div class="stat-v" style="color:#C75F5F">${{r.rejected}}</div></div>
<div class="stat"><div class="stat-l">Users</div><div class="stat-v">${{r.total_users}}</div></div>
<div class="stat"><div class="stat-l">Authenticated</div><div class="stat-v">${{r.authenticated_submissions}}</div></div>
<div class="stat"><div class="stat-l">Last 7 days</div><div class="stat-v">${{r.last_7_days}}</div></div>
`}}catch(e){{}}}}
async function load(s,el){{if(el){{document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));el.classList.add('active')}}
const L=document.getElementById('list');L.innerHTML='<div class="empty">Loading...</div>';
try{{const r=await(await fetch(`/admin/contributions?key=${{K}}&status=${{s}}`)).json();
if(!r.contributions.length){{L.innerHTML=`<div class="empty">No ${{s}} contributions</div>`;return}}
L.innerHTML=r.contributions.map(c=>{{const d=JSON.parse(c.data||'{{}}');const ch=d.quality_checks||{{}};const fl=ch.flags||[];const ff=d.features_found||[];
const tc={{'review':'t-review','website':'t-website','feature':'t-feature'}}[c.type]||'';
let det='';
if(c.type==='review')det=`<div class="feats">${{ff.slice(0,12).map(f=>`<span class="ft">${{f.replace(/_/g,' ')}}</span>`).join('')}}${{ff.length>12?`<span class="ft">+${{ff.length-12}}</span>`:''}}</div>`;
else if(c.type==='website')det=`<div class="meta" style="margin-top:6px">${{d.reason||''}}</div>`;
else det=`<div class="meta" style="margin-top:6px"><b>${{d.feature_name||''}}</b>: ${{d.description||''}}</div>`;
const userHtml=c.username?`<div class="user-row"><img src="${{c.user_avatar||''}}" onerror="this.style.display='none'"><span>${{c.user_display||c.username}}</span><span class="meta">@${{c.username}}</span></div>`:`<div class="meta">Anonymous ${{c.contributor_name?'('+c.contributor_name+')':''}}</div>`;
const ss=c.has_screenshots?'<span class="ss">Screenshots</span>':'';
const acts=s==='pending'?`<div class="actions"><input class="ni" id="n${{c.id}}" placeholder="Notes"><button class="btn btn-a" onclick="act(${{c.id}},'approve')">Approve</button><button class="btn btn-r" onclick="act(${{c.id}},'reject')">Reject</button></div>`:`<div class="meta" style="margin-top:8px">${{c.review_notes?'Notes: '+c.review_notes:''}}</div>`;
return`<div class="card"><div class="card-top"><div><span class="badge ${{tc}}">${{c.type}}</span>${{ss}}<span class="meta" style="margin-left:8px">${{new Date(c.submitted_at).toLocaleDateString()}}</span></div><span class="score" style="color:${{c.confidence_score>=60?'#5CB08A':c.confidence_score>=30?'#D4883A':'#C75F5F'}}">${{c.confidence_score}}</span></div>${{userHtml}}<div style="font-size:14px;font-weight:500;word-break:break-all">${{c.url||d.feature_name||'-'}}</div><div class="meta">${{c.industry||'all'}}</div>${{fl.length?`<div>${{fl.map(f=>`<span class="flag">${{f}}</span>`).join('')}}</div>`:''}}${{det}}${{acts}}</div>`}}).join('')
}}catch(e){{L.innerHTML=`<div class="empty">Error: ${{e.message}}</div>`}}}}
async function act(id,a){{const n=document.getElementById('n'+id)?.value||'';
try{{const r=await fetch(`/admin/contributions/${{id}}/${{a}}?key=${{K}}&notes=${{encodeURIComponent(n)}}`,{{method:'POST'}});if(r.ok){{load('pending');loadStats()}}}}catch(e){{}}}}
loadStats();load('pending');
</script></body></html>""")


# -------------------------------------------------------------------
# INTEGRATION INSTRUCTIONS
# -------------------------------------------------------------------
#
# In your api.py, add:
#
#   from auth_and_profiles import register_auth_routes
#   register_auth_routes(app)
#
# Add to requirements.txt:
#   PyJWT>=2.8
#   httpx>=0.27
#
# Set environment variables on Railway:
#   GITHUB_CLIENT_ID=...
#   GITHUB_CLIENT_SECRET=...
#   GOOGLE_CLIENT_ID=...
#   GOOGLE_CLIENT_SECRET=...
#   JWT_SECRET=<any-random-32-char-string>
#
# -------------------------------------------------------------------
