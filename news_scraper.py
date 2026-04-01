"""
BenchmarkHQ — News & Media Benchmark Scraper
==============================================
Scrapes news websites and analyzes 151 features across 16 categories.
Uses Playwright for screenshots + GPT-4o for AI analysis.

Usage:
  # Scan one country
  python3 news_scraper.py --country usa

  # Scan all Tier 1 countries
  python3 news_scraper.py --tier 1

  # Scan all countries
  python3 news_scraper.py --all

  # Scan a single site
  python3 news_scraper.py --site bbc.co.uk/news --country uk
"""

import argparse, json, os, sys, time, base64, re
from datetime import datetime
from playwright.sync_api import sync_playwright

# Import country lists
from news_countries import TIER1_COUNTRIES, TIER2_COUNTRIES, get_all_countries

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o"

NEWS_FEATURES_PROMPT = """You are a senior digital media analyst for BenchmarkHQ. Analyze this news/media website's public-facing features.

Check ALL of these features (Y/N/P for partial):

ARTICLE EXPERIENCE:
- article_headline: Clear H1 headline on articles
- article_byline: Author name visible
- article_date: Publication date shown
- article_updated: "Last updated" timestamp
- article_reading_time: Estimated reading time shown
- article_body_typography: Body text ≥16px, good line-height, ~700px width
- article_images: Images with captions in articles
- article_image_alt: Alt text on images
- article_categories: Section/category label on articles
- article_tags: Topic tags linking to tag pages
- related_articles: Related/recommended stories section
- article_pagination: Full article on single page (no "next page")
- print_version: Print-friendly version available
- font_size_controls: A+/A- text size buttons
- reading_mode: Distraction-free reading mode
- text_to_speech: Audio article / listen button
- article_comments_count: Comment count displayed
- correction_notice: Correction notices visible on articles

HOMEPAGE & NAVIGATION:
- homepage_hero: Prominent hero/lead story area
- section_navigation: Section nav (News, Business, Sports, Opinion)
- mega_menu: Dropdown mega menu
- breadcrumbs: Breadcrumb navigation on articles
- trending_section: Trending / Most Read section
- breaking_news_banner: Breaking news banner
- editors_picks: Editor's picks section
- topic_pages: Dedicated topic landing pages
- section_pages: Full section landing pages
- archive_access: Searchable article archive
- sticky_header: Sticky header on scroll
- back_to_top: Back to top button
- hamburger_mobile: Mobile hamburger menu
- footer_navigation: Comprehensive footer
- logo_home_link: Logo links to homepage

SEARCH:
- site_search: Search bar on the site
- search_suggestions: Autocomplete suggestions
- search_filters: Filter by date/section/author
- search_results_quality: Results with snippets and thumbnails
- search_accessible: Search available from all pages
- advanced_search: Advanced search page

MONETIZATION:
- paywall_type: What type? (hard/soft/metered/registration/none)
- subscription_page: Subscription pricing page
- free_articles: Free article allowance visible
- subscription_tiers: Multiple subscription plans
- student_discount: Student pricing
- gift_subscription: Gift subscription option
- free_registration: Free account option
- donation_support: Donation/Support button
- corporate_plans: Corporate/group plans
- cancel_easy: Cancellation info visible
- trial_offer: Free trial available
- micropayments: Single article purchase

ADVERTISING:
- display_ads: Display advertising present
- ad_labeling: Ads labeled as "Advertisement"
- native_content_labeling: Sponsored content clearly labeled
- ad_density_reasonable: Ads don't overwhelm content
- no_intrusive_popups: No full-screen blocking ads
- ad_free_option: Ad-free subscription tier
- video_autoplay_muted: Video ads muted by default
- ad_blocker_notice: Ad blocker detection notice

NEWSLETTER & EMAIL:
- newsletter_signup: Newsletter signup form
- multiple_newsletters: Multiple newsletter options
- newsletter_archive: Past newsletters viewable
- newsletter_preview: Newsletter preview/sample
- rss_feed: RSS feed available
- email_article: Email article sharing
- push_notifications_web: Web push notification prompt

COMMENTS & COMMUNITY:
- comment_system: Comment section on articles
- comment_moderation: Moderation visible
- comment_login_required: Login required to comment
- community_guidelines: Published commenting rules
- letters_editor: Letters to editor section
- reader_submissions: Submit tips/stories
- user_profiles: Commenter profiles

SOCIAL & SHARING:
- share_buttons: Social share buttons on articles
- copy_link: Copy link button
- whatsapp_share: WhatsApp share button
- telegram_share: Telegram share button
- social_media_links: Social profile links
- embed_article: Embed article option
- share_count: Share count displayed
- share_quote: Select and share quote

MULTIMEDIA:
- video_player: Video content/player
- live_video: Live streaming
- photo_galleries: Photo galleries
- infographics: Infographics/data viz
- interactive_content: Interactive features
- podcast_section: Podcast section
- video_captions: Video captions available
- video_section: Dedicated video hub
- data_journalism: Data journalism section
- vertical_video: Short-form vertical video

MOBILE & PERFORMANCE:
- responsive_design: Responsive mobile layout
- mobile_app_links: App download links
- fast_page_load: Fast loading (<3s feel)
- lazy_loading: Lazy loading images
- image_optimization: WebP/AVIF images
- core_web_vitals: Good performance feel
- amp_pages: AMP version exists
- pwa_features: PWA install option
- mobile_touch_targets: Adequate touch targets
- no_horizontal_scroll: No horizontal overflow

ACCESSIBILITY:
- semantic_html: Proper semantic HTML
- heading_hierarchy: Logical heading order
- color_contrast: Sufficient contrast
- keyboard_navigation: Keyboard navigable
- focus_indicators: Visible focus indicators
- skip_navigation: Skip to content link
- alt_text_images: Alt text on images
- video_captions_a11y: Video captions
- accessibility_statement: Accessibility page
- high_contrast_mode: High contrast option

TRUST & TRANSPARENCY:
- about_page: About us page
- editorial_policy: Editorial/Ethics policy
- corrections_policy: Corrections policy
- author_pages: Author profile pages
- contact_info: Contact information
- ownership_disclosure: Ownership disclosed
- fact_check_labels: Fact-check labels
- funding_transparency: Funding disclosed
- masthead: Masthead/editorial team page
- reader_rep: Ombudsman/reader representative

PERSONALIZATION:
- save_bookmark: Save/bookmark articles
- reading_history: Reading history
- topic_following: Follow topics
- personalized_feed: Personalized homepage
- dark_mode: Dark mode option
- cookie_preferences: Granular cookie controls
- notification_preferences: Notification settings
- reading_list: Curated reading lists
- content_recommendations: AI recommendations section

LANGUAGE & LOCALIZATION:
- language_switcher: Language switcher
- rtl_support: RTL layout support
- regional_editions: Regional editions
- local_time: Local timezone display
- local_currency: Local currency in articles
- auto_translate: Auto-translate option

LEGAL & COMPLIANCE:
- privacy_policy: Privacy policy page
- cookie_consent: Cookie consent banner
- terms_of_use: Terms of use page
- gdpr_compliance: GDPR data request
- ccpa_compliance: CCPA opt-out (US sites)
- copyright_notice: Copyright notice
- content_licensing: Licensing info

SEO & TECHNICAL:
- og_tags: Open Graph meta tags
- twitter_cards: Twitter card meta tags
- structured_data: Schema.org structured data
- canonical_urls: Canonical URL tags
- xml_sitemap: XML sitemap
- https: HTTPS everywhere
- robots_txt: Robots.txt file
- favicon: Favicon present

Return ONLY valid JSON:
{
  "features": {
    "article_headline": "Y",
    ... (ALL feature IDs with Y/N/P)
  },
  "paywall_type": "none|hard|soft|metered|registration|freemium",
  "monetization_model": "ad-supported|subscription|donation|public-funded|mixed",
  "site_type": "newspaper|tv-broadcast|digital-native|magazine|wire-service|blog|government",
  "scores": {
    "article_experience": 8,
    "navigation": 8,
    "visual_design": 7,
    "mobile_experience": 8,
    "ad_experience": 6,
    "accessibility": 5,
    "trust_signals": 7,
    "multimedia": 6
  },
  "notable": ["key observation 1", "key observation 2", "key observation 3"]
}"""


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def scrape_site(page, url, output_dir, safe_name):
    """Take homepage + article screenshots."""
    screenshots = []
    full_url = f"https://{url}" if not url.startswith("http") else url

    # Homepage
    try:
        page.goto(full_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
        hp_path = os.path.join(output_dir, f"{safe_name}_homepage.png")
        page.screenshot(path=hp_path, full_page=False)
        screenshots.append(hp_path)

        # Scroll down for more homepage content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
        page.wait_for_timeout(1000)
        hp2_path = os.path.join(output_dir, f"{safe_name}_homepage_mid.png")
        page.screenshot(path=hp2_path, full_page=False)
        screenshots.append(hp2_path)

        # Footer
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        ft_path = os.path.join(output_dir, f"{safe_name}_footer.png")
        page.screenshot(path=ft_path, full_page=False)
        screenshots.append(ft_path)
    except Exception as e:
        print(f"    Homepage error: {str(e)[:100]}")
        return screenshots, str(e)[:200]

    # Find and visit an article
    try:
        article_link = None
        for sel in ['article a[href]', 'h2 a[href]', 'h3 a[href]', '.story a[href]', '.headline a[href]']:
            links = page.locator(sel)
            if links.count() > 0:
                for i in range(min(links.count(), 10)):
                    href = links.nth(i).get_attribute("href") or ""
                    text = links.nth(i).inner_text().strip()
                    if len(text) > 20 and not href.endswith(('.jpg', '.png', '.mp4')):
                        article_link = href
                        break
            if article_link:
                break

        if article_link:
            if not article_link.startswith("http"):
                base = f"https://{url.split('/')[0]}"
                article_link = base + article_link if article_link.startswith("/") else base + "/" + article_link

            page.goto(article_link, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Article top
            art_path = os.path.join(output_dir, f"{safe_name}_article_top.png")
            page.screenshot(path=art_path, full_page=False)
            screenshots.append(art_path)

            # Article mid (scroll to body)
            page.evaluate("window.scrollTo(0, 600)")
            page.wait_for_timeout(1000)
            art2_path = os.path.join(output_dir, f"{safe_name}_article_body.png")
            page.screenshot(path=art2_path, full_page=False)
            screenshots.append(art2_path)

            # Article bottom (comments, related)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.8)")
            page.wait_for_timeout(1000)
            art3_path = os.path.join(output_dir, f"{safe_name}_article_bottom.png")
            page.screenshot(path=art3_path, full_page=False)
            screenshots.append(art3_path)
    except Exception as e:
        print(f"    Article error: {str(e)[:100]}")

    return screenshots, None


def analyze_with_ai(site_url, country_name, language, screenshots):
    """Send screenshots to GPT-4o for 151-feature analysis."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    content = [{"type": "text", "text": f"""Website: {site_url}
Country: {country_name}
Language: {language}

I'm sending {len(screenshots)} screenshots (homepage top/mid/footer + article top/body/bottom).

{NEWS_FEATURES_PROMPT}"""}]

    for path in screenshots:
        if os.path.exists(path):
            b64 = encode_image(path)
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "low"}})

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": content}],
            temperature=0.1, max_tokens=4000,
        )
        text = resp.choices[0].message.content
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
            text = text.strip()
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "JSON parse failed", "raw": text[:500]}
    except Exception as e:
        return {"error": str(e)[:300]}


def compute_frequency(results):
    """Compute feature frequency analysis from all site results."""
    feature_counts = {}
    good_sites = [r for r in results if "features" in r.get("ai_analysis", {})]

    for result in good_sites:
        features = result["ai_analysis"]["features"]
        for fid, val in features.items():
            if fid not in feature_counts:
                feature_counts[fid] = {"present": 0, "absent": 0, "partial": 0, "total": 0}
            feature_counts[fid]["total"] += 1
            if val == "Y":
                feature_counts[fid]["present"] += 1
            elif val == "N":
                feature_counts[fid]["absent"] += 1
            elif val == "P":
                feature_counts[fid]["partial"] += 1

    frequency = {}
    for fid, counts in feature_counts.items():
        total = counts["total"]
        if total == 0:
            continue
        pct = round((counts["present"] + counts["partial"] * 0.5) / total * 100)
        if pct >= 80:
            classification = "CRITICAL"
        elif pct >= 50:
            classification = "REQUIRED"
        elif pct >= 25:
            classification = "RECOMMENDED"
        else:
            classification = "OPTIONAL"
        frequency[fid] = {
            "present": counts["present"],
            "partial": counts["partial"],
            "absent": counts["absent"],
            "total_sites": total,
            "total_good_sites": len(good_sites),
            "percentage": pct,
            "classification": classification,
        }

    return frequency


def scan_country(country_key, country_data):
    """Scan all sites for one country."""
    name = country_data["name"]
    language = country_data["language"]
    sites = country_data["sites"]
    tier = country_data.get("tier", 2)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = f"data/news_{country_key}/{ts}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  NEWS BENCHMARK: {name}")
    print(f"  Language: {language} | Tier: {tier} | Sites: {len(sites)}")
    print(f"{'='*60}")

    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

        for i, site in enumerate(sites, 1):
            safe = re.sub(r'[^a-z0-9]', '_', site.lower())[:40]
            print(f"\n  [{i}/{len(sites)}] {site}")

            page = context.new_page()
            screenshots, error = scrape_site(page, site, output_dir, safe)
            page.close()

            if error:
                print(f"    SKIP: {error[:80]}")
                results.append({"site": site, "error": error})
                continue

            print(f"    Screenshots: {len(screenshots)}")

            if not OPENAI_API_KEY:
                results.append({"site": site, "screenshots": len(screenshots)})
                continue

            analysis = analyze_with_ai(site, name, language, screenshots)
            features = analysis.get("features", {})
            y = sum(1 for v in features.values() if v == "Y")
            p = sum(1 for v in features.values() if v == "P")
            print(f"    Features: {y} present, {p} partial")

            if analysis.get("notable"):
                for note in analysis["notable"][:2]:
                    print(f"    → {note}")

            results.append({
                "site": site, "country": name, "language": language,
                "screenshots": len(screenshots), "ai_analysis": analysis,
            })

            # Small delay to avoid rate limits
            time.sleep(1)

        browser.close()

    # Save results
    results_path = os.path.join(output_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Compute frequency
    frequency = compute_frequency(results)
    freq_path = os.path.join(output_dir, "frequency_analysis.json")
    with open(freq_path, "w") as f:
        json.dump(frequency, f, indent=2)

    good = sum(1 for r in results if "features" in r.get("ai_analysis", {}))
    total_features = len(frequency)
    critical = sum(1 for v in frequency.values() if v["classification"] == "CRITICAL")

    print(f"\n{'='*60}")
    print(f"  DONE: {name}")
    print(f"  Sites: {good}/{len(sites)} analyzed")
    print(f"  Features: {total_features} | Critical: {critical}")
    print(f"  Results: {results_path}")
    print(f"{'='*60}")

    return {
        "country": country_key, "name": name,
        "sites_total": len(sites), "sites_analyzed": good,
        "features": total_features, "critical": critical,
        "status": "success",
    }


def main():
    p = argparse.ArgumentParser(description="BenchmarkHQ News & Media Scraper")
    p.add_argument("--country", help="Scan one country (e.g., usa, uk, pakistan)")
    p.add_argument("--tier", type=int, help="Scan all countries in tier (1 or 2)")
    p.add_argument("--all", action="store_true", help="Scan all countries")
    p.add_argument("--site", help="Scan a single site")
    a = p.parse_args()

    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not set. Screenshots only, no AI analysis.")

    all_countries = get_all_countries()
    summary = []

    if a.site:
        country_key = a.country or "single"
        country_data = all_countries.get(country_key, {"name": "Unknown", "language": "en", "sites": [a.site]})
        if a.site not in country_data.get("sites", []):
            country_data = {"name": "Single Site", "language": "en", "sites": [a.site], "tier": 0}
        result = scan_country(country_key, country_data)
        summary.append(result)

    elif a.country:
        if a.country not in all_countries:
            print(f"Country '{a.country}' not found. Available: {', '.join(sorted(all_countries.keys()))}")
            sys.exit(1)
        result = scan_country(a.country, all_countries[a.country])
        summary.append(result)

    elif a.tier:
        source = TIER1_COUNTRIES if a.tier == 1 else TIER2_COUNTRIES
        for key, data in source.items():
            data["tier"] = a.tier
            result = scan_country(key, data)
            summary.append(result)

    elif a.all:
        for key, data in all_countries.items():
            result = scan_country(key, data)
            summary.append(result)

    else:
        print("Usage:")
        print("  python3 news_scraper.py --country usa")
        print("  python3 news_scraper.py --tier 1")
        print("  python3 news_scraper.py --all")
        print("  python3 news_scraper.py --site bbc.co.uk/news --country uk")
        sys.exit(0)

    # Save summary
    if summary:
        os.makedirs("data", exist_ok=True)
        with open("data/news_scan_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        total_sites = sum(s["sites_analyzed"] for s in summary)
        print(f"\n{'#'*60}")
        print(f"  NEWS & MEDIA BENCHMARK COMPLETE")
        print(f"  Countries: {len(summary)}")
        print(f"  Sites analyzed: {total_sites}")
        print(f"{'#'*60}")


if __name__ == "__main__":
    main()
