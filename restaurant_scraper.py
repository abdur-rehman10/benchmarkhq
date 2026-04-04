"""
BenchmarkHQ — Restaurant & Food Website Scraper
=================================================
Scans restaurant chain websites using Playwright + GPT-4o Vision.
Checks 98 features across 10 categories.

Usage:
  python3 restaurant_scraper.py --country usa
  python3 restaurant_scraper.py --country uk
  python3 restaurant_scraper.py --tier 1
  python3 restaurant_scraper.py --tier 2
"""

import os, sys, json, time, argparse, base64, re, signal
from datetime import datetime
from pathlib import Path
from threading import Thread, Event
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

# Allow Ctrl+C to work
signal.signal(signal.SIGINT, signal.default_int_handler)

# Check dependencies
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install: pip install playwright && playwright install chromium")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("Install: pip install openai")
    sys.exit(1)

from restaurant_countries import COUNTRIES

# ============================================================
# FEATURE CHECKLIST
# ============================================================

FEATURES = {
    # Essential Info (12)
    "restaurant_name": "Restaurant/Brand name and logo visible",
    "address_location": "Physical address displayed",
    "phone_number": "Phone number displayed (clickable)",
    "opening_hours": "Opening hours/business hours shown",
    "email_contact": "Email or contact form available",
    "google_maps": "Embedded map showing location",
    "multiple_locations": "Store locator for multiple locations",
    "about_page": "About us / Our story page",
    "directions_parking": "Directions or parking info",
    "dress_code": "Dress code information (fine dining)",
    "private_dining": "Private dining / events info",
    "careers_page": "Careers / Jobs page",
    # Menu (14)
    "menu_online": "Online menu viewable as HTML (not just PDF)",
    "menu_pdf": "Menu available as PDF download",
    "menu_prices": "Prices displayed on menu items",
    "menu_photos": "Food photos shown on menu",
    "menu_categories": "Menu organized into categories (starters, mains, etc.)",
    "menu_descriptions": "Dish descriptions with ingredients",
    "dietary_info": "Dietary labels (vegetarian, vegan, GF, halal)",
    "allergen_info": "Allergen information available",
    "nutritional_info": "Nutritional/calorie information",
    "seasonal_menu": "Seasonal or special menu highlighted",
    "drinks_menu": "Separate drinks/wine/cocktail menu",
    "kids_menu": "Kids/children menu",
    "menu_search": "Menu search or filter functionality",
    "menu_customization": "Customize/build your own meal option",
    # Online Ordering (12)
    "online_ordering": "Online ordering system available",
    "delivery_option": "Delivery option available",
    "pickup_option": "Pickup/collection option",
    "third_party_links": "Links to Uber Eats, DoorDash, Deliveroo, etc.",
    "cart_system": "Shopping cart functionality",
    "order_tracking": "Order tracking feature",
    "multiple_payment": "Multiple payment methods accepted",
    "order_scheduling": "Schedule order for later date/time",
    "minimum_order": "Minimum order amount displayed",
    "delivery_fee": "Delivery fee shown transparently",
    "promo_codes": "Promo/discount code field",
    "reorder": "Reorder previous orders feature",
    # Reservations (8)
    "reservation_system": "Online reservation/booking system",
    "reservation_widget": "Reservation widget (OpenTable, Resy, etc.)",
    "party_size": "Party size selector",
    "date_time_picker": "Date and time picker for booking",
    "special_requests": "Special requests text field",
    "confirmation_email": "Booking confirmation shown",
    "waitlist": "Waitlist option when fully booked",
    "group_booking": "Large group / event booking",
    # Visual & Branding (10)
    "hero_image": "Large hero image or video on homepage",
    "food_photography": "Professional food photography",
    "interior_photos": "Restaurant interior/ambiance photos",
    "photo_gallery": "Dedicated photo gallery section",
    "video_content": "Video content (promo, chef, food prep)",
    "virtual_tour": "Virtual tour or 360° view",
    "consistent_branding": "Consistent brand colors and fonts",
    "favicon": "Favicon present in browser tab",
    "chef_profile": "Chef or team profile section",
    "awards_press": "Awards, Michelin stars, or press mentions",
    # Social & Engagement (10)
    "social_links": "Social media links (Instagram, Facebook, etc.)",
    "instagram_feed": "Embedded Instagram feed",
    "reviews_testimonials": "Customer reviews or testimonials",
    "review_platform_links": "Links to Google/Yelp/TripAdvisor reviews",
    "newsletter_signup": "Newsletter or email signup form",
    "blog_news": "Blog or news section",
    "share_buttons": "Social sharing buttons",
    "user_generated_content": "User-generated content (customer photos)",
    "loyalty_program": "Loyalty or rewards program",
    "gift_cards": "Gift cards or vouchers for sale",
    # Special Services (8)
    "catering": "Catering services offered",
    "takeaway_menu": "Separate takeaway/takeout menu",
    "meal_kits": "Meal kits or cook-at-home option",
    "merchandise": "Merchandise or branded products for sale",
    "cooking_classes": "Cooking classes or experiences",
    "franchise_info": "Franchise information page",
    "app_download": "Mobile app download links",
    "wifi_info": "WiFi availability mentioned",
    # Mobile & Performance (8)
    "responsive_design": "Responsive mobile design",
    "fast_loading": "Fast page load (under 3 seconds)",
    "click_to_call": "Click-to-call phone number",
    "click_to_map": "Click-to-navigate map link",
    "lazy_loading": "Lazy loading for images",
    "optimized_images": "Optimized images (WebP format)",
    "mobile_ordering": "Mobile-friendly ordering flow",
    "pwa_features": "PWA or add-to-homescreen support",
    # Accessibility (8)
    "alt_text_images": "Alt text on food images",
    "keyboard_navigation": "Keyboard navigable",
    "color_contrast": "Sufficient color contrast",
    "privacy_policy": "Privacy policy page",
    "cookie_consent": "Cookie consent banner",
    "terms_conditions": "Terms and conditions page",
    "language_options": "Multi-language support",
    "accessibility_statement": "Accessibility statement",
    # SEO & Technical (8)
    "og_tags": "Open Graph meta tags present",
    "structured_data": "Schema.org Restaurant structured data",
    "google_business": "Google Business Profile integration",
    "https": "HTTPS enabled",
    "xml_sitemap": "XML sitemap exists",
    "local_seo": "Local SEO optimization",
    "canonical_urls": "Canonical URL tags",
    "page_titles": "Descriptive unique page titles",
}

PROMPT_TEMPLATE = """You are analyzing a restaurant/food chain website. Based on the screenshots provided, determine which features are present.

For each feature below, respond with ONLY a JSON object where keys are feature IDs and values are:
- "Y" if the feature is clearly present
- "N" if the feature is clearly absent
- "P" if partially present or unclear

FEATURES TO CHECK:
{features}

IMPORTANT:
- Only mark "Y" if you can clearly see evidence in the screenshots
- For menu features, check if an actual menu is displayed on the site
- For ordering features, check if there's a way to order food online
- For reservation features, check if there's a booking system
- Check footer for social links, legal pages, and contact info
- Respond with ONLY the JSON object, no other text
"""


def take_screenshots(page, url, output_dir, site_name):
    """Take screenshots of restaurant website pages."""
    screenshots = []
    clean = re.sub(r'[^a-zA-Z0-9]', '_', site_name)

    try:
        page.goto(f"https://{url}", timeout=20000, wait_until="domcontentloaded")
        time.sleep(2)

        # Dismiss cookie/popup
        for selector in ["[class*='accept']", "[class*='cookie'] button", "[id*='accept']", "button:has-text('Accept')", "button:has-text('OK')", "button:has-text('Got it')"]:
            try:
                btn = page.query_selector(selector)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(0.5)
                    break
            except:
                pass

        # Homepage top
        path = f"{output_dir}/{clean}_homepage.png"
        page.screenshot(path=path, full_page=False)
        screenshots.append(path)

        # Homepage mid (scroll down)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.4)")
        time.sleep(1)
        path = f"{output_dir}/{clean}_homepage_mid.png"
        page.screenshot(path=path, full_page=False)
        screenshots.append(path)

        # Footer
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        path = f"{output_dir}/{clean}_footer.png"
        page.screenshot(path=path, full_page=False)
        screenshots.append(path)

        # Try to find and visit menu page
        for menu_text in ["Menu", "Our Menu", "Food Menu", "See Menu", "View Menu"]:
            try:
                link = page.query_selector(f"a:has-text('{menu_text}')")
                if link and link.is_visible():
                    link.click(timeout=5000)
                    time.sleep(2)
                    path = f"{output_dir}/{clean}_menu.png"
                    page.screenshot(path=path, full_page=False)
                    screenshots.append(path)

                    # Scroll menu page
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.3)")
                    time.sleep(1)
                    path = f"{output_dir}/{clean}_menu_mid.png"
                    page.screenshot(path=path, full_page=False)
                    screenshots.append(path)
                    break
            except:
                pass

        # Try to find order page
        for order_text in ["Order", "Order Online", "Order Now", "Start Order", "Delivery"]:
            try:
                link = page.query_selector(f"a:has-text('{order_text}')")
                if link and link.is_visible():
                    link.click(timeout=5000)
                    time.sleep(2)
                    path = f"{output_dir}/{clean}_order.png"
                    page.screenshot(path=path, full_page=False)
                    screenshots.append(path)
                    break
            except:
                pass

    except KeyboardInterrupt:
        print(f"\n    ⛔ Interrupted!")
        raise

    except Exception as e:
        print(f"    ⚠ Screenshot error: {e}")
        if not screenshots:
            try:
                page.goto(f"http://{url}", timeout=20000, wait_until="domcontentloaded")
                time.sleep(2)
                path = f"{output_dir}/{clean}_homepage.png"
                page.screenshot(path=path, full_page=False)
                screenshots.append(path)
            except:
                pass

    return screenshots


def analyze_with_gpt4o(client, screenshots, site_name):
    """Send screenshots to GPT-4o Vision for analysis."""
    features_text = "\n".join(f"- {fid}: {fdesc}" for fid, fdesc in FEATURES.items())
    prompt = PROMPT_TEMPLATE.format(features=features_text)

    content = [{"type": "text", "text": prompt}]
    for ss in screenshots[:8]:  # Max 8 screenshots
        try:
            with open(ss, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "low"}
            })
        except:
            pass

    if len(content) < 2:
        return None

    try:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            max_tokens=3000,
            temperature=0.1,
        )
        resp = future.result(timeout=120)  # Hard 120s timeout
        executor.shutdown(wait=False)
        text = resp.choices[0].message.content.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except KeyboardInterrupt:
        print(f"\n    ⛔ Interrupted!")
        raise
    except FuturesTimeout:
        print(f"    ⚠ GPT-4o TIMEOUT for {site_name} (>120s)")
        return None
    except Exception as e:
        print(f"    ⚠ GPT-4o error for {site_name}: {e}")
        return None


def frequency_analysis(results):
    """Calculate feature frequencies across all analyzed sites."""
    feature_counts = {}
    good_sites = [s for s in results if s.get("features")]

    for fid in FEATURES:
        yes = sum(1 for s in good_sites if s.get("features", {}).get(fid) == "Y")
        partial = sum(1 for s in good_sites if s.get("features", {}).get(fid) == "P")
        total = len(good_sites)
        present = yes + (partial * 0.5)
        pct = round(present / total * 100) if total > 0 else 0

        if pct >= 80:
            cls = "CRITICAL"
        elif pct >= 50:
            cls = "REQUIRED"
        elif pct >= 25:
            cls = "RECOMMENDED"
        else:
            cls = "OPTIONAL"

        feature_counts[fid] = {
            "description": FEATURES[fid],
            "yes": yes,
            "partial": partial,
            "no": total - yes - (partial if partial <= total - yes else 0),
            "total_good_sites": total,
            "percentage": pct,
            "classification": cls,
        }

    return feature_counts


def scan_country(country_key):
    """Scan all restaurant sites for a country."""
    if country_key not in COUNTRIES:
        print(f"Unknown country: {country_key}")
        print(f"Available: {', '.join(sorted(COUNTRIES.keys()))}")
        return

    country = COUNTRIES[country_key]
    sites = country["sites"]
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = f"data/restaurant_{country_key}/{ts}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"RESTAURANT BENCHMARK: {country['name']}")
    print(f"Sites: {len(sites)} | Output: {output_dir}")
    print(f"{'='*60}\n")

    client = OpenAI(timeout=120.0)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        
        try:
            for i, site in enumerate(sites, 1):
                print(f"[{i}/{len(sites)}] {site}")

                try:
                    # Fresh page per site — prevents hung pages from affecting next site
                    page = context.new_page()
                    page.set_default_timeout(15000)

                    screenshots = take_screenshots(page, site, output_dir, site)
                    print(f"    📸 {len(screenshots)} screenshots")

                    if screenshots:
                        features = analyze_with_gpt4o(client, screenshots, site)
                        if features:
                            yes = sum(1 for v in features.values() if v == "Y")
                            print(f"    ✅ {yes}/{len(FEATURES)} features detected")
                        else:
                            features = {}
                            print(f"    ⚠ Analysis failed")
                    else:
                        features = {}
                        print(f"    ❌ No screenshots")

                    results.append({
                        "url": site,
                        "screenshots": len(screenshots),
                        "features": features,
                        "timestamp": datetime.now().isoformat(),
                    })

                    try:
                        page.close()
                    except:
                        pass

                except KeyboardInterrupt:
                    print(f"\n\n⛔ Interrupted at site {i}/{len(sites)}: {site}")
                    print(f"Saving {len(results)} partial results...")
                    break
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    results.append({"url": site, "screenshots": 0, "features": {}, "timestamp": datetime.now().isoformat()})
                    try:
                        page.close()
                    except:
                        pass

                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n⛔ Scan interrupted. Saving partial results...")
        finally:
            browser.close()

    # Save results
    with open(f"{output_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Frequency analysis
    freq = frequency_analysis(results)
    with open(f"{output_dir}/frequency_analysis.json", "w") as f:
        json.dump(freq, f, indent=2)

    # Summary
    good = sum(1 for r in results if r.get("features"))
    critical = sum(1 for v in freq.values() if v["classification"] == "CRITICAL")
    required = sum(1 for v in freq.values() if v["classification"] == "REQUIRED")

    print(f"\n{'='*60}")
    print(f"DONE: {country['name']}")
    print(f"Sites analyzed: {good}/{len(sites)}")
    print(f"CRITICAL features: {critical}")
    print(f"REQUIRED features: {required}")
    print(f"Results: {output_dir}")
    print(f"{'='*60}\n")

    # Update scan summary
    update_summary(country_key, country["name"], good, len(sites), critical)


def update_summary(key, name, analyzed, total, critical):
    """Update the restaurant scan summary file."""
    summary_file = "data/restaurant_scan_summary.json"
    summary = []
    if os.path.exists(summary_file):
        try:
            with open(summary_file) as f:
                summary = json.load(f)
        except:
            pass

    entry = {
        "key": key,
        "name": name,
        "sites_analyzed": analyzed,
        "sites_total": total,
        "critical_features": critical,
        "timestamp": datetime.now().isoformat(),
        "status": "success" if analyzed > 0 else "failed",
    }

    summary = [s for s in summary if s["key"] != key]
    summary.append(entry)

    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="BenchmarkHQ Restaurant Scraper")
    parser.add_argument("--country", help="Scan a specific country (e.g., usa, uk, india)")
    parser.add_argument("--tier", type=int, help="Scan all countries in a tier (1=30 sites, 2=10 sites)")
    parser.add_argument("--list", action="store_true", help="List all available countries")
    args = parser.parse_args()

    if args.list:
        tier1 = {k: v for k, v in COUNTRIES.items() if len(v["sites"]) >= 30}
        tier2 = {k: v for k, v in COUNTRIES.items() if len(v["sites"]) < 30}
        print(f"\nTier 1 ({len(tier1)} countries, 30 sites each):")
        for k, v in tier1.items():
            print(f"  {k:20s} {v['name']}")
        print(f"\nTier 2 ({len(tier2)} countries, 10 sites each):")
        for k, v in tier2.items():
            print(f"  {k:20s} {v['name']}")
        return

    if args.country:
        scan_country(args.country)
    elif args.tier == 1:
        for key, data in COUNTRIES.items():
            if len(data["sites"]) >= 30:
                scan_country(key)
    elif args.tier == 2:
        for key, data in COUNTRIES.items():
            if len(data["sites"]) < 30:
                scan_country(key)
    else:
        print("Usage:")
        print("  python3 restaurant_scraper.py --country usa")
        print("  python3 restaurant_scraper.py --tier 1")
        print("  python3 restaurant_scraper.py --tier 2")
        print("  python3 restaurant_scraper.py --list")


if __name__ == "__main__":
    main()
