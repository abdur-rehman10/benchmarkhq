"""
BenchmarkHQ — Layer 2 Deep Product Scanner v4.0
=================================================
Logs into SaaS products, explores 15+ sections,
takes comprehensive screenshots, and checks against
the full 155-feature PM Benchmark Framework.

Based on deep research of 15 PM tools, industry reports,
and market analysis (2025-2026).

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

# ============================================================
# 155-FEATURE PM BENCHMARK CHECKLIST
# Organized by category, with tier classification
# ============================================================

PM_FEATURES = {
    "task_management": {
        "label": "Task Management (28 features)",
        "features": {
            # Universal (18)
            "task_creation": {"name": "Task creation", "tier": "Universal"},
            "rich_text_description": {"name": "Rich text descriptions", "tier": "Universal"},
            "subtasks": {"name": "Subtasks (1 level)", "tier": "Universal"},
            "task_assignment": {"name": "Single assignee", "tier": "Universal"},
            "due_dates": {"name": "Due dates & start dates", "tier": "Universal"},
            "priority_levels": {"name": "Priority levels", "tier": "Universal"},
            "custom_statuses": {"name": "Custom statuses", "tier": "Universal"},
            "task_dependencies": {"name": "Task dependencies (FS)", "tier": "Universal"},
            "recurring_tasks": {"name": "Recurring tasks", "tier": "Universal"},
            "task_templates": {"name": "Task templates", "tier": "Universal"},
            "custom_fields": {"name": "Custom fields", "tier": "Universal"},
            "tags_labels": {"name": "Tags & labels", "tier": "Universal"},
            "file_attachments": {"name": "File attachments", "tier": "Universal"},
            "checklists": {"name": "Checklists within tasks", "tier": "Universal"},
            "task_linking": {"name": "Task linking & relationships", "tier": "Universal"},
            "task_cloning": {"name": "Task cloning/duplication", "tier": "Universal"},
            "bulk_actions": {"name": "Bulk actions", "tier": "Universal"},
            "task_comments": {"name": "Comments & threaded discussions", "tier": "Universal"},
            # Standard (8)
            "nested_subtasks": {"name": "Nested subtasks (multi-level)", "tier": "Standard"},
            "multi_assignees": {"name": "Multiple assignees", "tier": "Standard"},
            "assigned_comments": {"name": "Assigned comments", "tier": "Standard"},
            "activity_history": {"name": "Activity history", "tier": "Standard"},
            "milestones": {"name": "Milestones", "tier": "Standard"},
            "story_points": {"name": "Story points", "tier": "Standard"},
            "time_estimates": {"name": "Time estimates", "tier": "Standard"},
            "custom_task_types": {"name": "Custom task types (Bug/Story/Epic)", "tier": "Standard"},
            # Advanced (1)
            "formula_fields": {"name": "Calculated formula fields", "tier": "Advanced"},
            # Cutting-edge (1)
            "ai_task_suggestions": {"name": "AI-generated task suggestions", "tier": "Cutting-edge"},
        }
    },
    "views_visualization": {
        "label": "Views & Visualization (17 features)",
        "features": {
            "list_view": {"name": "List / Table view", "tier": "Universal"},
            "kanban_board": {"name": "Kanban board view", "tier": "Universal"},
            "calendar_view": {"name": "Calendar view", "tier": "Universal"},
            "table_spreadsheet": {"name": "Table / Spreadsheet view", "tier": "Universal"},
            "dashboard_view": {"name": "Dashboard view", "tier": "Universal"},
            "form_view": {"name": "Form view", "tier": "Universal"},
            "activity_feed": {"name": "Activity feed", "tier": "Universal"},
            "gantt_timeline": {"name": "Gantt / Timeline view", "tier": "Standard"},
            "workload_view": {"name": "Workload / Capacity view", "tier": "Standard"},
            "whiteboard_view": {"name": "Whiteboard view", "tier": "Standard"},
            "document_view": {"name": "Built-in document editor", "tier": "Standard"},
            "chart_view": {"name": "Chart / Analytics view", "tier": "Standard"},
            "embed_view": {"name": "Embed view", "tier": "Standard"},
            "saved_custom_views": {"name": "Saved / Custom views", "tier": "Standard"},
            "backlog_view": {"name": "Backlog view", "tier": "Standard"},
            "mind_map_view": {"name": "Mind map view", "tier": "Cutting-edge"},
            "map_view": {"name": "Map / Geolocation view", "tier": "Cutting-edge"},
        }
    },
    "collaboration": {
        "label": "Collaboration (14 features)",
        "features": {
            "at_mentions": {"name": "@mentions", "tier": "Universal"},
            "file_sharing": {"name": "File sharing", "tier": "Universal"},
            "guest_access": {"name": "Guest / External access", "tier": "Universal"},
            "email_integration": {"name": "Email integration", "tier": "Universal"},
            "notification_controls": {"name": "Notification controls", "tier": "Universal"},
            "comment_reactions": {"name": "Comment reactions / Emoji", "tier": "Universal"},
            "real_time_coediting": {"name": "Real-time co-editing", "tier": "Standard"},
            "proofing_annotation": {"name": "Proofing & annotation", "tier": "Standard"},
            "built_in_chat": {"name": "Built-in team chat", "tier": "Standard"},
            "approval_workflows": {"name": "Approval workflows", "tier": "Standard"},
            "project_status_updates": {"name": "Project status updates", "tier": "Standard"},
            "native_video_calls": {"name": "Native video calls", "tier": "Cutting-edge"},
            "ai_meeting_notes": {"name": "AI meeting notetaker", "tier": "Cutting-edge"},
            "shared_inbox": {"name": "Shared inbox / Requests", "tier": "Standard"},
        }
    },
    "resource_time": {
        "label": "Resource & Time Management (12 features)",
        "features": {
            "time_tracking": {"name": "Built-in time tracking", "tier": "Standard"},
            "timesheets": {"name": "Timesheet management", "tier": "Standard"},
            "billable_nonbillable": {"name": "Billable vs non-billable hours", "tier": "Standard"},
            "workload_management": {"name": "Workload management", "tier": "Standard"},
            "capacity_planning": {"name": "Capacity planning", "tier": "Advanced"},
            "resource_allocation": {"name": "Resource allocation", "tier": "Advanced"},
            "utilization_reports": {"name": "Utilization reports", "tier": "Advanced"},
            "budget_tracking": {"name": "Budget tracking", "tier": "Advanced"},
            "cost_management": {"name": "Cost management", "tier": "Advanced"},
            "work_schedules": {"name": "Work schedules", "tier": "Advanced"},
            "skill_based_matching": {"name": "Skill-based resource matching", "tier": "Cutting-edge"},
            "asset_scheduling": {"name": "Asset & equipment scheduling", "tier": "Cutting-edge"},
        }
    },
    "reporting_analytics": {
        "label": "Reporting & Analytics (15 features)",
        "features": {
            "custom_dashboards": {"name": "Custom dashboards", "tier": "Universal"},
            "prebuilt_reports": {"name": "Pre-built reports", "tier": "Universal"},
            "custom_charts": {"name": "Custom charts", "tier": "Universal"},
            "export_reports": {"name": "Export reports (PDF/CSV/Excel)", "tier": "Universal"},
            "real_time_refresh": {"name": "Real-time data refresh", "tier": "Universal"},
            "project_health_score": {"name": "Project health scoring (RAG)", "tier": "Standard"},
            "portfolio_view": {"name": "Portfolio / Multi-project view", "tier": "Standard"},
            "burndown_chart": {"name": "Burndown / Burnup charts", "tier": "Standard"},
            "velocity_chart": {"name": "Velocity chart", "tier": "Standard"},
            "time_reports": {"name": "Time tracking reports", "tier": "Standard"},
            "cumulative_flow": {"name": "Cumulative flow diagram", "tier": "Advanced"},
            "scheduled_reports": {"name": "Scheduled report delivery", "tier": "Advanced"},
            "budget_reports": {"name": "Budget vs actual reports", "tier": "Advanced"},
            "workflow_metrics": {"name": "Workflow metrics (cycle time, lead time)", "tier": "Advanced"},
            "ai_insights": {"name": "AI-powered insights", "tier": "Cutting-edge"},
        }
    },
    "automation": {
        "label": "Automation (10 features)",
        "features": {
            "simple_rules": {"name": "Simple automation rules", "tier": "Universal"},
            "automation_templates": {"name": "Automation templates", "tier": "Universal"},
            "multi_step_automations": {"name": "Multi-step automations", "tier": "Standard"},
            "cross_tool_automations": {"name": "Cross-tool automations", "tier": "Standard"},
            "scheduled_automations": {"name": "Scheduled/cron automations", "tier": "Standard"},
            "webhook_triggers": {"name": "Webhook triggers", "tier": "Standard"},
            "automation_log": {"name": "Automation run history / log", "tier": "Standard"},
            "conditional_logic": {"name": "Conditional logic (if/then/else)", "tier": "Advanced"},
            "ai_automation_builder": {"name": "AI natural language automation", "tier": "Cutting-edge"},
            "autonomous_ai_agents": {"name": "Autonomous AI agents", "tier": "Cutting-edge"},
        }
    },
    "agile_methodology": {
        "label": "Agile & Methodology (12 features)",
        "features": {
            "sprint_management": {"name": "Sprint management", "tier": "Standard"},
            "backlog_grooming": {"name": "Backlog management & grooming", "tier": "Standard"},
            "sprint_planning": {"name": "Sprint planning view", "tier": "Standard"},
            "epics": {"name": "Epics / Initiatives", "tier": "Standard"},
            "wip_limits": {"name": "WIP limits", "tier": "Standard"},
            "release_management": {"name": "Release management", "tier": "Standard"},
            "okrs_goals": {"name": "OKRs / Goals", "tier": "Standard"},
            "critical_path": {"name": "Critical path analysis", "tier": "Advanced"},
            "baseline_tracking": {"name": "Baseline tracking", "tier": "Advanced"},
            "earned_value": {"name": "Earned value management", "tier": "Advanced"},
            "roadmap": {"name": "Roadmap view", "tier": "Standard"},
            "safe_support": {"name": "SAFe framework support", "tier": "Cutting-edge"},
        }
    },
    "documents_knowledge": {
        "label": "Documents & Knowledge (8 features)",
        "features": {
            "templates_library": {"name": "Templates library", "tier": "Universal"},
            "embedded_content": {"name": "Embedded external content", "tier": "Universal"},
            "built_in_docs": {"name": "Built-in document editor", "tier": "Standard"},
            "wiki_knowledge_base": {"name": "Wiki / Knowledge base", "tier": "Standard"},
            "version_history": {"name": "Version history for docs", "tier": "Standard"},
            "meeting_notes": {"name": "Meeting note templates", "tier": "Standard"},
            "ai_content_generation": {"name": "AI content generation", "tier": "Cutting-edge"},
            "ai_cross_stack_search": {"name": "AI cross-stack search", "tier": "Cutting-edge"},
        }
    },
    "integrations_platform": {
        "label": "Integrations & Platform (12 features)",
        "features": {
            "slack_integration": {"name": "Slack integration", "tier": "Universal"},
            "google_integration": {"name": "Google Workspace integration", "tier": "Universal"},
            "microsoft_integration": {"name": "Microsoft 365 integration", "tier": "Universal"},
            "zapier_make": {"name": "Zapier / Make connection", "tier": "Universal"},
            "mobile_ios": {"name": "Mobile app (iOS)", "tier": "Universal"},
            "mobile_android": {"name": "Mobile app (Android)", "tier": "Universal"},
            "import_export": {"name": "Import / Export data", "tier": "Universal"},
            "rest_api": {"name": "REST API access", "tier": "Standard"},
            "github_integration": {"name": "GitHub / GitLab integration", "tier": "Standard"},
            "webhooks": {"name": "Webhooks", "tier": "Standard"},
            "desktop_app": {"name": "Desktop app", "tier": "Standard"},
            "graphql_api": {"name": "GraphQL API", "tier": "Advanced"},
        }
    },
    "admin_security": {
        "label": "Admin & Security (14 features)",
        "features": {
            "role_permissions": {"name": "Role-based permissions", "tier": "Universal"},
            "team_management": {"name": "Team management", "tier": "Universal"},
            "two_factor_auth": {"name": "Two-factor authentication", "tier": "Universal"},
            "data_encryption": {"name": "Data encryption (rest + transit)", "tier": "Universal"},
            "soc2": {"name": "SOC 2 Type II", "tier": "Universal"},
            "iso27001": {"name": "ISO 27001", "tier": "Universal"},
            "gdpr": {"name": "GDPR compliance", "tier": "Universal"},
            "custom_roles": {"name": "Custom roles (granular RBAC)", "tier": "Advanced"},
            "saml_sso": {"name": "SAML SSO", "tier": "Advanced"},
            "scim_provisioning": {"name": "SCIM user provisioning", "tier": "Advanced"},
            "audit_log": {"name": "Audit log", "tier": "Advanced"},
            "ip_allowlisting": {"name": "IP allowlisting", "tier": "Advanced"},
            "data_residency": {"name": "Data residency options", "tier": "Advanced"},
            "hipaa": {"name": "HIPAA compliance", "tier": "Advanced"},
        }
    },
    "ux_design_quality": {
        "label": "UX & Design Quality (13 features)",
        "features": {
            "drag_and_drop": {"name": "Drag and drop", "tier": "Universal"},
            "quick_add_task": {"name": "Quick add task", "tier": "Universal"},
            "global_search": {"name": "Global search", "tier": "Universal"},
            "responsive_mobile_web": {"name": "Responsive mobile web", "tier": "Universal"},
            "onboarding_tour": {"name": "Onboarding tour / walkthrough", "tier": "Standard"},
            "empty_states": {"name": "Helpful empty states", "tier": "Standard"},
            "dark_mode": {"name": "Dark mode", "tier": "Standard"},
            "keyboard_shortcuts": {"name": "Keyboard shortcuts", "tier": "Standard"},
            "command_palette": {"name": "Command palette (Cmd+K)", "tier": "Standard"},
            "customizable_sidebar": {"name": "Customizable sidebar", "tier": "Standard"},
            "skeleton_loading": {"name": "Skeleton / Loading states", "tier": "Standard"},
            "undo_redo": {"name": "Undo / Redo support", "tier": "Standard"},
            "offline_mode": {"name": "Offline mode", "tier": "Advanced"},
        }
    },
}

def get_total_features():
    total = 0
    for cat in PM_FEATURES.values():
        total += len(cat["features"])
    return total

def build_feature_prompt():
    """Build the feature checklist section of the AI prompt."""
    lines = []
    for cat_key, cat_data in PM_FEATURES.items():
        lines.append(f"\n{cat_data['label']}:")
        for fid, fdata in cat_data["features"].items():
            lines.append(f"  {fid} - {fdata['name']} [{fdata['tier']}]")
    return "\n".join(lines)

def get_all_feature_ids():
    ids = []
    for cat in PM_FEATURES.values():
        ids.extend(cat["features"].keys())
    return ids


# ============================================================
# BROWSER HELPERS
# ============================================================

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

def screenshot(page, output_dir, name, label):
    path = os.path.join(output_dir, f"{name}_{label}.png")
    page.screenshot(path=path, full_page=False)
    return path

def try_click(page, selectors, timeout=4000):
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                loc.first.click()
                page.wait_for_timeout(timeout)
                return True
        except:
            continue
    return False


# ============================================================
# LOGIN ENGINE (handles 2-step flows)
# ============================================================

def login(page, login_url, email, password):
    email_sels = [
        'input[type="email"]', 'input[name="email"]', 'input[name="username"]',
        'input[id="email"]', 'input[id="username"]', 'input[id="login_email"]',
        'input[placeholder*="email" i]', 'input[autocomplete="email"]',
        'input[autocomplete="username"]',
    ]
    pw_sels = [
        'input[type="password"]', 'input[name="password"]',
        'input[id="password"]', 'input[placeholder*="password" i]',
        'input[autocomplete="current-password"]',
    ]

    page.goto(login_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
    page.wait_for_timeout(3000)

    # Email
    email_field = find_field(page, email_sels)
    if not email_field:
        email_field = page.locator('input:visible').first
    email_field.click()
    email_field.fill(email)
    page.wait_for_timeout(500)
    page.keyboard.press("Enter")
    page.wait_for_timeout(5000)

    # Password (may be on new screen)
    pw_field = None
    for attempt in range(5):
        pw_field = find_field(page, pw_sels)
        if pw_field:
            break
        page.wait_for_timeout(2000)

    if pw_field:
        pw_field.click()
        pw_field.fill(password)
        page.wait_for_timeout(500)
        page.keyboard.press("Enter")
        page.wait_for_timeout(10000)
        return True
    return False


# ============================================================
# DEEP PRODUCT EXPLORATION
# ============================================================

def explore_product(page, dashboard_url, output_dir, safe_name):
    screenshots = {}
    pages_visited = []

    def capture(label, description):
        path = screenshot(page, output_dir, safe_name, label)
        screenshots[label] = path
        pages_visited.append({"label": label, "description": description, "url": page.url, "title": page.title()})
        print(f"    [{label}] {description}")

    def go_home():
        if dashboard_url:
            try:
                page.goto(dashboard_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
                page.wait_for_timeout(3000)
            except:
                pass

    print("\n  --- Deep exploration ---")

    # 1. Dashboard
    if dashboard_url:
        page.goto(dashboard_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
        page.wait_for_timeout(5000)
    capture("01_dashboard", "Main dashboard / Home")

    # 2. Try creating a task (check task creation flow)
    print("  Looking for task creation...")
    if try_click(page, [
        'button:has-text("Add task")', 'button:has-text("New task")', 'button:has-text("Create")',
        'button[aria-label*="add" i]', 'button[aria-label*="create" i]', 'button[aria-label*="new" i]',
        'a:has-text("New task")', '[data-testid*="create"]', '[data-testid*="add-task"]',
    ]):
        capture("02_task_creation", "Task creation dialog/form")
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
    go_home()

    # 3. Board/Kanban view
    print("  Looking for Board view...")
    if try_click(page, [
        'button:has-text("Board")', 'a:has-text("Board")', '[data-testid*="board"]',
        'button[aria-label*="board" i]', 'a[href*="board"]',
    ]):
        capture("03_board_view", "Kanban / Board view")
    go_home()

    # 4. Timeline/Gantt view
    print("  Looking for Timeline view...")
    if try_click(page, [
        'button:has-text("Timeline")', 'a:has-text("Timeline")', 'button:has-text("Gantt")',
        'a:has-text("Gantt")', '[data-testid*="timeline"]', 'a[href*="timeline"]',
    ]):
        capture("04_timeline", "Timeline / Gantt view")
    go_home()

    # 5. Calendar view
    print("  Looking for Calendar view...")
    if try_click(page, [
        'button:has-text("Calendar")', 'a:has-text("Calendar")', '[data-testid*="calendar"]',
        'a[href*="calendar"]',
    ]):
        capture("05_calendar", "Calendar view")
    go_home()

    # 6. Dashboard/Reporting
    print("  Looking for Reporting...")
    if try_click(page, [
        'a:has-text("Reporting")', 'a:has-text("Reports")', 'a:has-text("Dashboard")',
        'a:has-text("Analytics")', 'a[href*="report"]', 'a[href*="dashboard"]',
        'a[href*="analytics"]',
    ]):
        capture("06_reporting", "Reporting / Analytics page")
    go_home()

    # 7. Goals / OKRs
    print("  Looking for Goals...")
    if try_click(page, [
        'a:has-text("Goals")', 'a:has-text("OKR")', 'a:has-text("Objectives")',
        'a[href*="goal"]', 'a[href*="okr"]',
    ]):
        capture("07_goals", "Goals / OKR page")
    go_home()

    # 8. Portfolios
    print("  Looking for Portfolios...")
    if try_click(page, [
        'a:has-text("Portfolio")', 'a:has-text("Portfolios")', 'a:has-text("Programs")',
        'a[href*="portfolio"]', 'a[href*="program"]',
    ]):
        capture("08_portfolio", "Portfolio / Program view")
    go_home()

    # 9. Team / Members
    print("  Looking for Team...")
    if try_click(page, [
        'a:has-text("Team")', 'a:has-text("Members")', 'a:has-text("People")',
        'a[href*="team"]', 'a[href*="member"]', 'a[href*="people"]',
    ]):
        capture("09_team", "Team / Members page")
    go_home()

    # 10. Settings
    print("  Looking for Settings...")
    if try_click(page, [
        'a[href*="settings"]', 'a[href*="account"]', 'a[href*="admin"]',
        'a:has-text("Settings")', 'button:has-text("Settings")',
        '[data-testid*="settings"]', '[aria-label*="Settings"]',
    ]):
        capture("10_settings", "Settings / Admin page")
    go_home()

    # 11. Integrations
    print("  Looking for Integrations...")
    if try_click(page, [
        'a:has-text("Integration")', 'a:has-text("Apps")', 'a:has-text("Connect")',
        'a[href*="integration"]', 'a[href*="apps"]',
    ]):
        capture("11_integrations", "Integrations / Apps page")
    go_home()

    # 12. Automations / Rules
    print("  Looking for Automations...")
    if try_click(page, [
        'a:has-text("Automation")', 'a:has-text("Rules")', 'a:has-text("Workflows")',
        'a[href*="automat"]', 'a[href*="rule"]', 'a[href*="workflow"]',
        'button:has-text("Automate")',
    ]):
        capture("12_automations", "Automations / Rules page")
    go_home()

    # 13. Templates
    print("  Looking for Templates...")
    if try_click(page, [
        'a:has-text("Template")', 'a[href*="template"]',
        'button:has-text("Template")',
    ]):
        capture("13_templates", "Templates gallery")
    go_home()

    # 14. Inbox / Notifications
    print("  Looking for Inbox...")
    if try_click(page, [
        'a:has-text("Inbox")', 'a:has-text("Notification")',
        'a[href*="inbox"]', 'a[href*="notification"]',
        '[aria-label*="notification" i]', '[aria-label*="inbox" i]',
    ]):
        capture("14_inbox", "Inbox / Notifications")
    go_home()

    # 15. Help / Support
    print("  Looking for Help...")
    if try_click(page, [
        'a:has-text("Help")', 'button:has-text("Help")', 'a:has-text("Support")',
        'a[href*="help"]', '[aria-label*="help" i]',
    ]):
        capture("15_help", "Help / Support section")
    go_home()

    # 16. Cmd+K command palette
    print("  Testing Cmd+K...")
    try:
        page.keyboard.press("Meta+k")
        page.wait_for_timeout(2000)
        capture("16_cmdk", "Command palette (Cmd+K)")
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    except:
        pass

    # 17. Try keyboard shortcut ?
    print("  Testing ? shortcuts...")
    try:
        page.keyboard.press("?")
        page.wait_for_timeout(1500)
        capture("17_shortcuts", "Keyboard shortcuts dialog")
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    except:
        pass

    # 18. Mobile responsiveness
    print("  Testing mobile view...")
    try:
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(2000)
        capture("18_mobile", "Mobile responsive view")
        page.set_viewport_size({"width": 1280, "height": 720})
    except:
        pass

    # 19-21. Explore 3 sidebar links we haven't visited
    print("  Exploring additional pages...")
    nav_links = []
    for sel in ['nav a[href]', 'aside a[href]', '[role="navigation"] a[href]', '.sidebar a[href]']:
        try:
            links = page.locator(sel)
            for i in range(min(links.count(), 20)):
                href = links.nth(i).get_attribute("href") or ""
                text = links.nth(i).inner_text().strip()[:40]
                if href and text:
                    nav_links.append({"href": href, "text": text})
        except:
            continue

    visited_keywords = ["settings", "team", "member", "report", "dashboard", "goal",
                        "portfolio", "integration", "automat", "template", "inbox",
                        "notification", "help", "login", "logout", "signout", "calendar",
                        "timeline", "board"]
    explored = 0
    for link in nav_links[:15]:
        if explored >= 3:
            break
        href = link["href"].lower()
        if any(kw in href for kw in visited_keywords):
            continue
        try:
            full_url = link["href"] if link["href"].startswith("http") else f"{page.url.split('/')[0]}//{page.url.split('/')[2]}{link['href']}"
            page.goto(full_url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
            page.wait_for_timeout(3000)
            capture(f"19_extra_{explored+1}", f"Extra: {link['text']}")
            explored += 1
        except:
            continue

    print(f"\n  Total screenshots: {len(screenshots)}")
    return screenshots, pages_visited


# ============================================================
# AI ANALYSIS WITH 155-FEATURE CHECKLIST
# ============================================================

def analyze_with_ai(product_name, category, screenshots, pages_visited):
    from openai import OpenAI
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY not set"}

    client = OpenAI(api_key=OPENAI_API_KEY)
    feature_checklist = build_feature_prompt()
    total = get_total_features()
    pages_summary = "\n".join([f"  - {p['label']}: {p['description']} ({p['url'][:80]})" for p in pages_visited])

    prompt = f"""You are a senior product analyst for BenchmarkHQ conducting the most comprehensive PM tool analysis ever done.

PRODUCT: {product_name}
CATEGORY: {category}

PAGES EXPLORED (screenshots attached):
{pages_summary}

I'm sending you {len(screenshots)} screenshots from INSIDE the product after login. Analyze EVERYTHING.

YOUR TASK: Check ALL 155 features below. For each one, mark:
  Y = Present (confirmed from screenshots OR your knowledge of {product_name})
  N = Not present
  U = Uncertain / Can't determine

IMPORTANT: Use BOTH the screenshots AND your expert knowledge of {product_name}. If you KNOW {product_name} has a feature (like Asana has Goals, or Jira has sprints) mark it Y even if that specific page wasn't captured.

COMPLETE 155-FEATURE CHECKLIST:
{feature_checklist}

ALSO EVALUATE THESE QUALITY DIMENSIONS (1-10 scale):

1. overall_ux_score - Overall user experience quality
2. navigation_quality - How intuitive is the navigation structure
3. visual_design - Design system consistency and polish
4. onboarding_quality - How well does it guide new users
5. information_density - How well it balances content vs whitespace
6. accessibility_score - Keyboard nav, contrast, screen reader support
7. performance_impression - Does it feel fast and responsive
8. customization_depth - How deeply can users customize the tool
9. automation_power - How sophisticated are the automations
10. methodology_flexibility - How well does it support multiple PM methods

DESIGN OBSERVATIONS:
- color_scheme: describe the primary color palette
- typography: describe the font choices and hierarchy
- animation_quality: describe transitions and micro-interactions
- layout_pattern: describe the overall layout (sidebar + main, etc)

STRATEGIC ANALYSIS:
- strengths: list 5+ things this product does exceptionally well
- weaknesses: list 5+ things this product is missing or does poorly
- best_for: what user segment is this tool ideal for
- not_ideal_for: what user segment should avoid this tool
- competitive_position: how does it compare to competitors
- unique_differentiators: what makes this product unique in the market
- pricing_tier_assessment: what pricing tier does the feature set justify

Return ONLY valid JSON with this EXACT structure:
{{
  "features": {{
    "task_creation": "Y",
    "rich_text_description": "Y",
    ... (ALL {total} feature IDs)
  }},
  "scores": {{
    "overall_ux_score": 8,
    "navigation_quality": 8,
    "visual_design": 8,
    "onboarding_quality": 7,
    "information_density": 7,
    "accessibility_score": 7,
    "performance_impression": 8,
    "customization_depth": 7,
    "automation_power": 7,
    "methodology_flexibility": 8
  }},
  "design": {{
    "color_scheme": "...",
    "typography": "...",
    "animation_quality": "...",
    "layout_pattern": "..."
  }},
  "analysis": {{
    "strengths": ["..."],
    "weaknesses": ["..."],
    "best_for": "...",
    "not_ideal_for": "...",
    "competitive_position": "...",
    "unique_differentiators": ["..."],
    "pricing_tier_assessment": "..."
  }},
  "tier_summary": {{
    "universal_present": 0,
    "universal_total": 0,
    "standard_present": 0,
    "standard_total": 0,
    "advanced_present": 0,
    "advanced_total": 0,
    "cutting_edge_present": 0,
    "cutting_edge_total": 0
  }}
}}"""

    content = [{"type": "text", "text": prompt}]
    img_count = 0
    for label in sorted(screenshots.keys()):
        path = screenshots[label]
        if os.path.exists(path):
            b64 = encode_image(path)
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}})
            img_count += 1

    print(f"\n[AI] Sending {img_count} screenshots to GPT-4o for {total}-feature analysis...")

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": content}],
            temperature=0.1, max_tokens=6000,
        )
        text = resp.choices[0].message.content
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
            text = text.strip()
        analysis = json.loads(text)

        # Print results
        features = analysis.get("features", {})
        scores = analysis.get("scores", {})
        design = analysis.get("design", {})
        strat = analysis.get("analysis", {})

        y = sum(1 for v in features.values() if v == "Y")
        n = sum(1 for v in features.values() if v == "N")
        u = sum(1 for v in features.values() if v == "U")

        # Count by tier
        tier_counts = {"Universal": [0,0], "Standard": [0,0], "Advanced": [0,0], "Cutting-edge": [0,0]}
        for cat in PM_FEATURES.values():
            for fid, fdata in cat["features"].items():
                tier = fdata["tier"]
                tier_counts[tier][1] += 1
                if features.get(fid) == "Y":
                    tier_counts[tier][0] += 1

        print(f"\n  {'='*55}")
        print(f"  {product_name} — BENCHMARK RESULTS")
        print(f"  {'='*55}")
        print(f"\n  Features: {y}/{total} present ({n} absent, {u} uncertain)")
        print(f"  Score: {round(y/total*100)}%")
        print(f"\n  By tier:")
        for tier, (present, total_t) in tier_counts.items():
            pct = round(present/total_t*100) if total_t > 0 else 0
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"    {tier:15s} {present:3d}/{total_t:3d} ({pct:3d}%) {bar}")

        print(f"\n  Quality scores:")
        for k, v in scores.items():
            print(f"    {k:30s} {v}/10")

        if strat.get("strengths"):
            print(f"\n  Strengths:")
            for s in strat["strengths"][:5]:
                print(f"    + {s}")
        if strat.get("weaknesses"):
            print(f"\n  Weaknesses:")
            for w in strat["weaknesses"][:5]:
                print(f"    - {w}")
        if strat.get("best_for"):
            print(f"\n  Best for: {strat['best_for']}")
        if strat.get("competitive_position"):
            print(f"  Position: {strat['competitive_position'][:200]}")

        return analysis
    except json.JSONDecodeError:
        print(f"  JSON parse error")
        return {"raw_response": text[:1000], "error": "JSON parse failed"}
    except Exception as e:
        print(f"  ERROR: {str(e)[:300]}")
        return {"error": str(e)[:300]}


# ============================================================
# MAIN
# ============================================================

def main():
    p = argparse.ArgumentParser(description="BenchmarkHQ Layer 2 — 155-Feature Deep PM Scanner v4.0")
    p.add_argument("--product", required=True, help="Product name (e.g., Asana)")
    p.add_argument("--login-url", required=True, help="Login page URL")
    p.add_argument("--email", required=True, help="Login email")
    p.add_argument("--password", required=True, help="Login password")
    p.add_argument("--dashboard-url", default="", help="Dashboard URL after login")
    p.add_argument("--category", default="project_management", help="SaaS category")
    a = p.parse_args()

    if not OPENAI_API_KEY:
        print("ERROR: export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    safe_name = a.product.lower().replace(" ", "_").replace(".", "")
    output_dir = f"data/layer2/{a.category}/{safe_name}"
    os.makedirs(output_dir, exist_ok=True)

    total_features = get_total_features()

    print(f"\n{'#'*60}")
    print(f"  BenchmarkHQ Layer 2 — Deep Product Scan v4.0")
    print(f"  Product: {a.product}")
    print(f"  Category: {a.category}")
    print(f"  Benchmark: {total_features} features across {len(PM_FEATURES)} categories")
    print(f"{'#'*60}")

    result = {
        "product": a.product, "category": a.category,
        "login_url": a.login_url, "dashboard_url": a.dashboard_url,
        "scanned_at": datetime.now().isoformat(),
        "benchmark_version": "4.0",
        "total_features_checked": total_features,
        "errors": [],
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Login
        print("\n[LOGIN] Logging in...")
        success = login(page, a.login_url, a.email, a.password)
        if success:
            print(f"  Logged in! URL: {page.url}")
        else:
            print("  WARNING: Login may have failed")
            result["errors"].append("Login may have failed")

        # Deep exploration
        print("\n[EXPLORE] Scanning product sections...")
        screenshots, pages_visited = explore_product(page, a.dashboard_url, output_dir, safe_name)
        result["screenshots"] = {k: os.path.basename(v) for k, v in screenshots.items()}
        result["pages_visited"] = pages_visited

        # Save cookies
        cookies = context.cookies()
        cookies_path = os.path.join(output_dir, f"{safe_name}_cookies.json")
        with open(cookies_path, "w") as f:
            json.dump(cookies, f, indent=2)
        result["cookies_saved"] = cookies_path

        browser.close()

    # AI Analysis
    result["ai_analysis"] = analyze_with_ai(a.product, a.category, screenshots, pages_visited)

    # Calculate summary
    features = result.get("ai_analysis", {}).get("features", {})
    y = sum(1 for v in features.values() if v == "Y")

    result["summary"] = {
        "features_present": y,
        "features_total": total_features,
        "score_percent": round(y / total_features * 100) if total_features > 0 else 0,
        "screenshots_taken": len(screenshots),
        "pages_explored": len(pages_visited),
    }

    # Save
    result_path = os.path.join(output_dir, "layer2_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"\n{'#'*60}")
    print(f"  COMPLETE: {a.product}")
    print(f"  Score: {y}/{total_features} ({result['summary']['score_percent']}%)")
    print(f"  Screenshots: {len(screenshots)}")
    print(f"  Pages explored: {len(pages_visited)}")
    print(f"  Results: {result_path}")
    print(f"  Cookies saved for future re-scans")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()
