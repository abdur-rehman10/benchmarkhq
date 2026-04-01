"""
BenchmarkHQ — Layer 2 Inside-Product SaaS Scanner
===================================================
Logs into SaaS products and checks 30 inside-product checkpoints.
Handles two-step logins (email first, then password on new screen).

Usage:
  python3 layer2_scraper.py --product "Asana" \
    --login-url "https://app.asana.com/-/login" \
    --email "you@email.com" --password 'yourpass' \
    --dashboard-url "https://app.asana.com/home" \
    --category "project_management"
"""

import argparse, json, os, sys, time, base64
from datetime import datetime
from playwright.sync_api import sync_playwright

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o"
BROWSER_TIMEOUT = 30000


def take_screenshots(page, output_dir, name, label):
    paths = {}
    vp_path = os.path.join(output_dir, f"{name}_{label}_viewport.png")
    page.screenshot(path=vp_path, full_page=False)
    paths["viewport"] = vp_path
    try:
        full_path = os.path.join(output_dir, f"{name}_{label}_full.png")
        page.screenshot(path=full_path, full_page=True, timeout=10000)
        paths["full"] = full_path
    except:
        pass
    return paths


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def find_field(page, selectors):
    for sel in selectors:
        try:
            if page.locator(sel).count() > 0:
                return page.locator(sel).first
        except:
            continue
    return None


def login_and_scan(product_name, login_url, email, password, dashboard_url, category, output_dir):
    safe_name = product_name.lower().replace(" ", "_").replace(".", "")
    os.makedirs(output_dir, exist_ok=True)

    result = {
        "product": product_name, "category": category,
        "login_url": login_url, "dashboard_url": dashboard_url,
        "scanned_at": datetime.now().isoformat(),
        "screenshots": {}, "pages_visited": [], "errors": [],
    }

    print(f"\n{'='*60}")
    print(f"  Layer 2 Scan: {product_name}")
    print(f"  Login: {login_url}")
    print(f"{'='*60}\n")

    email_selectors = [
        'input[type="email"]', 'input[name="email"]', 'input[name="username"]',
        'input[id="email"]', 'input[id="username"]', 'input[id="login_email"]',
        'input[placeholder*="email" i]', 'input[placeholder*="Email"]',
        'input[autocomplete="email"]', 'input[autocomplete="username"]',
    ]
    pw_selectors = [
        'input[type="password"]', 'input[name="password"]',
        'input[id="password"]', 'input[id="login_password"]',
        'input[placeholder*="password" i]', 'input[autocomplete="current-password"]',
    ]

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # === STEP 1: Open login page ===
        print("[1/7] Opening login page...")
        try:
            page.goto(login_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
            page.wait_for_timeout(3000)
            result["screenshots"]["login_page"] = take_screenshots(page, output_dir, safe_name, "01_login")
            print(f"  Loaded: {page.title()}")
        except Exception as e:
            result["errors"].append(f"Login page: {str(e)[:200]}")
            print(f"  ERROR: {str(e)[:100]}")
            browser.close()
            return result

        # === STEP 2: Enter email ===
        print("[2/7] Entering email...")
        try:
            email_field = find_field(page, email_selectors)
            if email_field:
                email_field.click()
                email_field.fill(email)
                print(f"  Email filled: {email}")
                page.wait_for_timeout(500)
                page.keyboard.press("Enter")
                print("  Pressed Enter")
                page.wait_for_timeout(5000)
                print(f"  URL after email: {page.url}")
            else:
                fallback = page.locator('input:visible').first
                fallback.fill(email)
                page.keyboard.press("Enter")
                page.wait_for_timeout(5000)
                print("  Email entered via fallback")
        except Exception as e:
            result["errors"].append(f"Email: {str(e)[:200]}")
            print(f"  ERROR: {str(e)[:100]}")

        # === STEP 3: Enter password (may be on new screen) ===
        print("[3/7] Looking for password field...")
        try:
            pw_field = None
            for attempt in range(5):
                pw_field = find_field(page, pw_selectors)
                if pw_field:
                    print(f"  Password field found (attempt {attempt+1})")
                    break
                print(f"  Waiting... (attempt {attempt+1}/5)")
                page.wait_for_timeout(2000)

            if pw_field:
                pw_field.click()
                pw_field.fill(password)
                print("  Password filled")
                page.wait_for_timeout(500)
                page.keyboard.press("Enter")
                print("  Pressed Enter to login")
                page.wait_for_timeout(10000)
                print(f"  URL after login: {page.url}")
            else:
                print("  WARNING: Password field not found after 5 attempts")
                result["errors"].append("Password field not found")
        except Exception as e:
            result["errors"].append(f"Password: {str(e)[:200]}")
            print(f"  ERROR: {str(e)[:100]}")

        # === STEP 4: Navigate to dashboard ===
        print("[4/7] Capturing dashboard...")
        try:
            if dashboard_url and "login" in page.url.lower():
                page.goto(dashboard_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
                page.wait_for_timeout(5000)
            elif dashboard_url and dashboard_url != page.url:
                page.goto(dashboard_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
                page.wait_for_timeout(5000)

            result["screenshots"]["dashboard"] = take_screenshots(page, output_dir, safe_name, "02_dashboard")
            result["pages_visited"].append({"name": "dashboard", "url": page.url, "title": page.title()})
            print(f"  Dashboard: {page.title()}")
            print(f"  URL: {page.url}")
        except Exception as e:
            result["errors"].append(f"Dashboard: {str(e)[:200]}")
            print(f"  ERROR: {str(e)[:100]}")

        # === STEP 5: Find and capture settings ===
        print("[5/7] Looking for settings...")
        try:
            settings_selectors = [
                'a[href*="settings"]', 'a[href*="account"]', 'a[href*="preferences"]',
                'a[href*="admin"]', 'a[href*="profile"]',
                'button:has-text("Settings")', 'a:has-text("Settings")',
                '[data-testid*="settings"]', '[aria-label*="Settings"]',
            ]
            settings_found = False
            for sel in settings_selectors:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0:
                        loc.first.click()
                        page.wait_for_timeout(4000)
                        result["screenshots"]["settings"] = take_screenshots(page, output_dir, safe_name, "03_settings")
                        result["pages_visited"].append({"name": "settings", "url": page.url, "title": page.title()})
                        settings_found = True
                        print(f"  Settings: {page.url}")
                        break
                except:
                    continue
            if not settings_found:
                print("  Settings not found via links")

            # Go back to dashboard
            if dashboard_url:
                page.goto(dashboard_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
                page.wait_for_timeout(3000)
        except Exception as e:
            print(f"  Settings error: {str(e)[:100]}")

        # === STEP 6: Test Cmd+K ===
        print("[6/7] Testing Cmd+K...")
        try:
            page.keyboard.press("Meta+k")
            page.wait_for_timeout(2000)
            result["screenshots"]["cmd_k"] = take_screenshots(page, output_dir, safe_name, "04_cmdk")
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            print("  Cmd+K captured")
        except:
            print("  Cmd+K skipped")

        # === STEP 7: Mobile viewport test ===
        print("[7/7] Testing mobile responsiveness...")
        try:
            page.set_viewport_size({"width": 375, "height": 812})
            page.wait_for_timeout(2000)
            result["screenshots"]["mobile"] = take_screenshots(page, output_dir, safe_name, "05_mobile")
            page.set_viewport_size({"width": 1280, "height": 720})
            print("  Mobile screenshot captured")
        except:
            print("  Mobile test skipped")

        # Save cookies
        cookies = context.cookies()
        cookies_path = os.path.join(output_dir, f"{safe_name}_cookies.json")
        with open(cookies_path, "w") as f:
            json.dump(cookies, f, indent=2)
        result["cookies_saved"] = cookies_path
        print(f"\n  Cookies saved: {cookies_path}")

        browser.close()

    return result


def analyze_with_ai(result, output_dir):
    from openai import OpenAI
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY not set"}

    print("\n[AI] Analyzing screenshots with GPT-4o Vision...")
    client = OpenAI(api_key=OPENAI_API_KEY)

    content = [{"type": "text", "text": f"""Analyze this SaaS product's INSIDE EXPERIENCE for BenchmarkHQ.
Product: {result['product']} (Category: {result['category']})
Pages visited: {json.dumps(result['pages_visited'])}

Screenshots are from INSIDE the product after login. Check these 30 inside-product signals (Y/N/U):

DASHBOARD & NAVIGATION:
sidebar_navigation, global_search, breadcrumb_navigation, command_palette_cmdk, notification_center, dark_mode_toggle, keyboard_shortcuts, dashboard_customizable

ONBOARDING:
welcome_tour, checklist_progress_tracker, sample_data_preloaded, empty_state_design, tooltip_coach_marks, time_to_value_fast

SETTINGS & ADMIN:
user_profile_settings, team_user_management, role_based_permissions, billing_management, api_key_management, data_export, audit_log

UX QUALITY:
skeleton_loading_states, useful_error_messages, undo_redo_support, realtime_updates, responsive_inside_app, keyboard_accessible

COLLABORATION:
invite_team_members, comments_mentions, sharing_public_links

IMPORTANT: Also use your knowledge of {result['product']}. Mark Y if you KNOW the product has a feature even if it's not visible in the screenshots.

Return ONLY valid JSON:
{{"features":{{"sidebar_navigation":"Y",...all 30}},"overall_ux_score_1_to_10":8,"onboarding_quality_1_to_10":7,"design_system_quality_1_to_10":8,"notable_observations":["list","of","things"]}}"""}]

    screenshot_count = 0
    for label, paths in result.get("screenshots", {}).items():
        vp = paths.get("viewport")
        if vp and os.path.exists(vp):
            b64 = encode_image(vp)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}
            })
            screenshot_count += 1

    print(f"  Sending {screenshot_count} screenshots to GPT-4o...")

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": content}],
            temperature=0.1, max_tokens=2000,
        )
        text = resp.choices[0].message.content
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
            text = text.strip()
        analysis = json.loads(text)
        features = analysis.get("features", {})
        y = sum(1 for v in features.values() if v == "Y")
        n = sum(1 for v in features.values() if v == "N")
        print(f"  Features: {y} present, {n} absent")
        print(f"  UX Score: {analysis.get('overall_ux_score_1_to_10', '?')}/10")
        print(f"  Onboarding: {analysis.get('onboarding_quality_1_to_10', '?')}/10")
        print(f"  Design System: {analysis.get('design_system_quality_1_to_10', '?')}/10")
        if analysis.get("notable_observations"):
            print(f"  Notable: {', '.join(analysis['notable_observations'][:3])}")
        return analysis
    except json.JSONDecodeError:
        print(f"  JSON parse error")
        return {"raw_response": text[:500], "error": "JSON parse failed"}
    except Exception as e:
        print(f"  ERROR: {str(e)[:200]}")
        return {"error": str(e)[:300]}


def main():
    p = argparse.ArgumentParser(description="BenchmarkHQ Layer 2 — Inside-Product Scanner")
    p.add_argument("--product", required=True, help="Product name")
    p.add_argument("--login-url", required=True, help="Login page URL")
    p.add_argument("--email", required=True, help="Login email")
    p.add_argument("--password", required=True, help="Login password")
    p.add_argument("--dashboard-url", default="", help="Dashboard URL after login")
    p.add_argument("--category", default="saas", help="SaaS category")
    a = p.parse_args()

    if not OPENAI_API_KEY:
        print("ERROR: export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    output_dir = f"data/layer2/{a.category}/{a.product.lower().replace(' ', '_')}"

    result = login_and_scan(a.product, a.login_url, a.email, a.password, a.dashboard_url, a.category, output_dir)
    result["ai_analysis"] = analyze_with_ai(result, output_dir)

    result_path = os.path.join(output_dir, "layer2_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    features = result.get("ai_analysis", {}).get("features", {})
    y = sum(1 for v in features.values() if v == "Y")
    n = sum(1 for v in features.values() if v == "N")

    print(f"\n{'='*60}")
    print(f"  DONE! {result['product']}")
    print(f"  Inside features: {y} present, {n} absent")
    print(f"  Results: {result_path}")
    print(f"  Cookies saved for future re-scans")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
