"""
BenchmarkHQ — SaaS Industry Benchmark Scraper v1.0
====================================================
Scans 600 SaaS products across 20 categories.
Checks 50 public-facing quality signals per product.

Setup: Same as e-commerce scraper
  pip3 install playwright beautifulsoup4 openai pyyaml
  playwright install chromium
  export OPENAI_API_KEY=sk-...

Usage:
  python3 saas_scraper.py --list
  python3 saas_scraper.py --industry project_management
  python3 saas_scraper.py --industry crm --sites 5
  python3 saas_scraper.py --all
  python3 saas_scraper.py --all --sites 10
"""

import argparse, json, os, subprocess, shutil, sys, time
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4o"
LIGHTHOUSE_AVAILABLE = shutil.which("lighthouse") is not None
BROWSER_TIMEOUT = 30000
JS_RENDER_WAIT = 5000
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
DELAY_BETWEEN_SITES = 3

INDUSTRIES = {
    "project_management": {
        "name": "Project Management SaaS",
        "category": "Productivity",
        "sites": [
            {"name": "Asana", "url": "https://asana.com"},
            {"name": "Monday.com", "url": "https://monday.com"},
            {"name": "ClickUp", "url": "https://clickup.com"},
            {"name": "Jira", "url": "https://www.atlassian.com/software/jira"},
            {"name": "Linear", "url": "https://linear.app"},
            {"name": "Trello", "url": "https://trello.com"},
            {"name": "Basecamp", "url": "https://basecamp.com"},
            {"name": "Wrike", "url": "https://www.wrike.com"},
            {"name": "Smartsheet", "url": "https://www.smartsheet.com"},
            {"name": "Notion", "url": "https://www.notion.so"},
            {"name": "Teamwork", "url": "https://www.teamwork.com"},
            {"name": "Todoist", "url": "https://todoist.com"},
            {"name": "Height", "url": "https://height.app"},
            {"name": "Hive", "url": "https://hive.com"},
            {"name": "Zoho Projects", "url": "https://www.zoho.com/projects/"},
            {"name": "Airtable", "url": "https://airtable.com"},
            {"name": "Shortcut", "url": "https://shortcut.com"},
            {"name": "Plane", "url": "https://plane.so"},
            {"name": "Nifty", "url": "https://niftypm.com"},
            {"name": "MeisterTask", "url": "https://www.meistertask.com"},
            {"name": "Freedcamp", "url": "https://freedcamp.com"},
            {"name": "ProofHub", "url": "https://www.proofhub.com"},
            {"name": "Quire", "url": "https://quire.io"},
            {"name": "Taskade", "url": "https://taskade.com"},
            {"name": "Ora", "url": "https://ora.pm"},
            {"name": "Paymo", "url": "https://www.paymo.com"},
            {"name": "Workzone", "url": "https://www.workzone.com"},
            {"name": "Celoxis", "url": "https://www.celoxis.com"},
            {"name": "Backlog", "url": "https://backlog.com"},
            {"name": "Flow", "url": "https://www.getflow.com"},
        ],
    },
    "crm": {
        "name": "CRM SaaS",
        "category": "Sales",
        "sites": [
            {"name": "Salesforce", "url": "https://www.salesforce.com"},
            {"name": "HubSpot CRM", "url": "https://www.hubspot.com/products/crm"},
            {"name": "Pipedrive", "url": "https://www.pipedrive.com"},
            {"name": "Zoho CRM", "url": "https://www.zoho.com/crm/"},
            {"name": "Freshsales", "url": "https://www.freshworks.com/crm/sales/"},
            {"name": "Close", "url": "https://www.close.com"},
            {"name": "Copper", "url": "https://www.copper.com"},
            {"name": "Insightly", "url": "https://www.insightly.com"},
            {"name": "Nimble", "url": "https://www.nimble.com"},
            {"name": "Streak", "url": "https://www.streak.com"},
            {"name": "Monday Sales CRM", "url": "https://monday.com/crm"},
            {"name": "Nutshell", "url": "https://www.nutshell.com"},
            {"name": "Capsule", "url": "https://capsulecrm.com"},
            {"name": "Less Annoying CRM", "url": "https://www.lessannoyingcrm.com"},
            {"name": "Agile CRM", "url": "https://www.agilecrm.com"},
            {"name": "Bitrix24", "url": "https://www.bitrix24.com"},
            {"name": "SugarCRM", "url": "https://www.sugarcrm.com"},
            {"name": "Keap", "url": "https://keap.com"},
            {"name": "Folk", "url": "https://www.folk.app"},
            {"name": "Attio", "url": "https://attio.com"},
            {"name": "Twenty", "url": "https://twenty.com"},
            {"name": "Affinity", "url": "https://www.affinity.co"},
            {"name": "Salesflare", "url": "https://salesflare.com"},
            {"name": "Teamleader", "url": "https://www.teamleader.eu"},
            {"name": "Vtiger", "url": "https://www.vtiger.com"},
            {"name": "Really Simple Systems", "url": "https://www.reallysimplesystems.com"},
            {"name": "Freshworks CRM", "url": "https://www.freshworks.com/crm/"},
            {"name": "Microsoft Dynamics", "url": "https://dynamics.microsoft.com"},
            {"name": "Oracle CX", "url": "https://www.oracle.com/cx/"},
            {"name": "SAP CRM", "url": "https://www.sap.com/products/crm.html"},
        ],
    },
    "customer_support": {
        "name": "Customer Support SaaS",
        "category": "Support",
        "sites": [
            {"name": "Zendesk", "url": "https://www.zendesk.com"},
            {"name": "Intercom", "url": "https://www.intercom.com"},
            {"name": "Freshdesk", "url": "https://www.freshworks.com/freshdesk/"},
            {"name": "Help Scout", "url": "https://www.helpscout.com"},
            {"name": "Crisp", "url": "https://crisp.chat"},
            {"name": "LiveChat", "url": "https://www.livechat.com"},
            {"name": "Tidio", "url": "https://www.tidio.com"},
            {"name": "Tawk.to", "url": "https://www.tawk.to"},
            {"name": "Drift", "url": "https://www.drift.com"},
            {"name": "HubSpot Service", "url": "https://www.hubspot.com/products/service"},
            {"name": "Kayako", "url": "https://kayako.com"},
            {"name": "Zoho Desk", "url": "https://www.zoho.com/desk/"},
            {"name": "Groove", "url": "https://www.groovehq.com"},
            {"name": "Front", "url": "https://front.com"},
            {"name": "Gladly", "url": "https://www.gladly.com"},
            {"name": "Kustomer", "url": "https://www.kustomer.com"},
            {"name": "Re:amaze", "url": "https://www.reamaze.com"},
            {"name": "Hiver", "url": "https://hiverhq.com"},
            {"name": "Gorgias", "url": "https://www.gorgias.com"},
            {"name": "Olark", "url": "https://www.olark.com"},
            {"name": "JivoChat", "url": "https://www.jivochat.com"},
            {"name": "Chatwoot", "url": "https://www.chatwoot.com"},
            {"name": "Papercups", "url": "https://papercups.io"},
            {"name": "Chatra", "url": "https://chatra.io"},
            {"name": "Helpjuice", "url": "https://helpjuice.com"},
            {"name": "Document360", "url": "https://document360.com"},
            {"name": "Freshchat", "url": "https://www.freshworks.com/live-chat-software/"},
            {"name": "Dixa", "url": "https://www.dixa.com"},
            {"name": "Richpanel", "url": "https://richpanel.com"},
            {"name": "Comm100", "url": "https://www.comm100.com"},
        ],
    },
    "email_marketing": {
        "name": "Email Marketing SaaS",
        "category": "Marketing",
        "sites": [
            {"name": "Mailchimp", "url": "https://mailchimp.com"},
            {"name": "ConvertKit", "url": "https://convertkit.com"},
            {"name": "Klaviyo", "url": "https://www.klaviyo.com"},
            {"name": "Brevo", "url": "https://www.brevo.com"},
            {"name": "ActiveCampaign", "url": "https://www.activecampaign.com"},
            {"name": "Drip", "url": "https://www.drip.com"},
            {"name": "MailerLite", "url": "https://www.mailerlite.com"},
            {"name": "GetResponse", "url": "https://www.getresponse.com"},
            {"name": "AWeber", "url": "https://www.aweber.com"},
            {"name": "Constant Contact", "url": "https://www.constantcontact.com"},
            {"name": "Campaign Monitor", "url": "https://www.campaignmonitor.com"},
            {"name": "Moosend", "url": "https://moosend.com"},
            {"name": "Omnisend", "url": "https://www.omnisend.com"},
            {"name": "Sender", "url": "https://www.sender.net"},
            {"name": "Benchmark Email", "url": "https://www.benchmarkemail.com"},
            {"name": "Mailjet", "url": "https://www.mailjet.com"},
            {"name": "SendGrid", "url": "https://sendgrid.com"},
            {"name": "Postmark", "url": "https://postmarkapp.com"},
            {"name": "Customer.io", "url": "https://customer.io"},
            {"name": "Iterable", "url": "https://iterable.com"},
            {"name": "Sendinblue", "url": "https://www.sendinblue.com"},
            {"name": "Flodesk", "url": "https://flodesk.com"},
            {"name": "Beehiiv", "url": "https://www.beehiiv.com"},
            {"name": "Buttondown", "url": "https://buttondown.com"},
            {"name": "Substack", "url": "https://substack.com"},
            {"name": "Ghost", "url": "https://ghost.org"},
            {"name": "Resend", "url": "https://resend.com"},
            {"name": "Loops", "url": "https://loops.so"},
            {"name": "Plunk", "url": "https://www.useplunk.com"},
            {"name": "EmailOctopus", "url": "https://emailoctopus.com"},
        ],
    },
    "analytics": {
        "name": "Analytics & BI SaaS",
        "category": "Data",
        "sites": [
            {"name": "Mixpanel", "url": "https://mixpanel.com"},
            {"name": "Amplitude", "url": "https://amplitude.com"},
            {"name": "PostHog", "url": "https://posthog.com"},
            {"name": "Heap", "url": "https://www.heap.io"},
            {"name": "Pendo", "url": "https://www.pendo.io"},
            {"name": "Hotjar", "url": "https://www.hotjar.com"},
            {"name": "FullStory", "url": "https://www.fullstory.com"},
            {"name": "Plausible", "url": "https://plausible.io"},
            {"name": "Fathom", "url": "https://usefathom.com"},
            {"name": "Matomo", "url": "https://matomo.org"},
            {"name": "Datadog", "url": "https://www.datadoghq.com"},
            {"name": "Grafana", "url": "https://grafana.com"},
            {"name": "Metabase", "url": "https://www.metabase.com"},
            {"name": "Looker", "url": "https://looker.com"},
            {"name": "Tableau", "url": "https://www.tableau.com"},
            {"name": "Power BI", "url": "https://powerbi.microsoft.com"},
            {"name": "Sisense", "url": "https://www.sisense.com"},
            {"name": "Mode", "url": "https://mode.com"},
            {"name": "Chartio", "url": "https://chartio.com"},
            {"name": "Klipfolio", "url": "https://www.klipfolio.com"},
            {"name": "Geckoboard", "url": "https://www.geckoboard.com"},
            {"name": "Databox", "url": "https://databox.com"},
            {"name": "Whatagraph", "url": "https://whatagraph.com"},
            {"name": "June", "url": "https://www.june.so"},
            {"name": "LogRocket", "url": "https://logrocket.com"},
            {"name": "Clarity", "url": "https://clarity.microsoft.com"},
            {"name": "Smartlook", "url": "https://www.smartlook.com"},
            {"name": "Lucky Orange", "url": "https://www.luckyorange.com"},
            {"name": "Mouseflow", "url": "https://mouseflow.com"},
            {"name": "Countly", "url": "https://count.ly"},
        ],
    },
    "accounting": {
        "name": "Accounting & Finance SaaS",
        "category": "Finance",
        "sites": [
            {"name": "QuickBooks", "url": "https://quickbooks.intuit.com"},
            {"name": "Xero", "url": "https://www.xero.com"},
            {"name": "FreshBooks", "url": "https://www.freshbooks.com"},
            {"name": "Wave", "url": "https://www.waveapps.com"},
            {"name": "Zoho Books", "url": "https://www.zoho.com/books/"},
            {"name": "Sage", "url": "https://www.sage.com"},
            {"name": "Bench", "url": "https://bench.co"},
            {"name": "Brex", "url": "https://www.brex.com"},
            {"name": "Ramp", "url": "https://ramp.com"},
            {"name": "Mercury", "url": "https://mercury.com"},
            {"name": "Stripe Atlas", "url": "https://stripe.com/atlas"},
            {"name": "Pilot", "url": "https://pilot.com"},
            {"name": "Gusto", "url": "https://gusto.com"},
            {"name": "Bill.com", "url": "https://www.bill.com"},
            {"name": "Expensify", "url": "https://www.expensify.com"},
            {"name": "Harvest", "url": "https://www.getharvest.com"},
            {"name": "Toggl Track", "url": "https://toggl.com/track/"},
            {"name": "Deel", "url": "https://www.deel.com"},
            {"name": "Remote", "url": "https://remote.com"},
            {"name": "Papaya Global", "url": "https://www.papayaglobal.com"},
            {"name": "Tipalti", "url": "https://tipalti.com"},
            {"name": "Chargebee", "url": "https://www.chargebee.com"},
            {"name": "Recurly", "url": "https://recurly.com"},
            {"name": "Paddle", "url": "https://www.paddle.com"},
            {"name": "Lemon Squeezy", "url": "https://www.lemonsqueezy.com"},
            {"name": "Baremetrics", "url": "https://baremetrics.com"},
            {"name": "ProfitWell", "url": "https://www.profitwell.com"},
            {"name": "ChartMogul", "url": "https://chartmogul.com"},
            {"name": "Stripe Billing", "url": "https://stripe.com/billing"},
            {"name": "PayPal Business", "url": "https://www.paypal.com/business"},
        ],
    },
    "hr_people": {
        "name": "HR & People SaaS",
        "category": "HR",
        "sites": [
            {"name": "BambooHR", "url": "https://www.bamboohr.com"},
            {"name": "Gusto HR", "url": "https://gusto.com"},
            {"name": "Rippling", "url": "https://www.rippling.com"},
            {"name": "Deel HR", "url": "https://www.deel.com"},
            {"name": "Remote HR", "url": "https://remote.com"},
            {"name": "Personio", "url": "https://www.personio.com"},
            {"name": "Bob", "url": "https://www.hibob.com"},
            {"name": "Oyster", "url": "https://www.oysterhr.com"},
            {"name": "Lattice", "url": "https://lattice.com"},
            {"name": "Culture Amp", "url": "https://www.cultureamp.com"},
            {"name": "15Five", "url": "https://www.15five.com"},
            {"name": "Workday", "url": "https://www.workday.com"},
            {"name": "Namely", "url": "https://www.namely.com"},
            {"name": "Paycor", "url": "https://www.paycor.com"},
            {"name": "Paylocity", "url": "https://www.paylocity.com"},
            {"name": "ADP", "url": "https://www.adp.com"},
            {"name": "Greenhouse", "url": "https://www.greenhouse.com"},
            {"name": "Lever", "url": "https://www.lever.co"},
            {"name": "Ashby", "url": "https://www.ashbyhq.com"},
            {"name": "Breezy HR", "url": "https://breezy.hr"},
            {"name": "JazzHR", "url": "https://www.jazzhr.com"},
            {"name": "Workable", "url": "https://www.workable.com"},
            {"name": "Leapsome", "url": "https://www.leapsome.com"},
            {"name": "Charlie HR", "url": "https://www.charliehr.com"},
            {"name": "Factorial", "url": "https://factorialhr.com"},
            {"name": "Kenjo", "url": "https://www.kenjo.io"},
            {"name": "Sage HR", "url": "https://www.sage.com/en-gb/hr/"},
            {"name": "Zoho People", "url": "https://www.zoho.com/people/"},
            {"name": "Keka", "url": "https://www.keka.com"},
            {"name": "GreytHR", "url": "https://www.greythr.com"},
        ],
    },
    "design_creative": {
        "name": "Design & Creative SaaS",
        "category": "Design",
        "sites": [
            {"name": "Figma", "url": "https://www.figma.com"},
            {"name": "Canva", "url": "https://www.canva.com"},
            {"name": "Adobe Creative Cloud", "url": "https://www.adobe.com/creativecloud.html"},
            {"name": "Sketch", "url": "https://www.sketch.com"},
            {"name": "Framer", "url": "https://www.framer.com"},
            {"name": "Penpot", "url": "https://penpot.app"},
            {"name": "InVision", "url": "https://www.invisionapp.com"},
            {"name": "Miro", "url": "https://miro.com"},
            {"name": "FigJam", "url": "https://www.figma.com/figjam/"},
            {"name": "Whimsical", "url": "https://whimsical.com"},
            {"name": "Excalidraw", "url": "https://excalidraw.com"},
            {"name": "Lucidchart", "url": "https://www.lucidchart.com"},
            {"name": "Lottie", "url": "https://lottiefiles.com"},
            {"name": "Spline", "url": "https://spline.design"},
            {"name": "Rive", "url": "https://rive.app"},
            {"name": "Pitch", "url": "https://pitch.com"},
            {"name": "Beautiful.ai", "url": "https://www.beautiful.ai"},
            {"name": "Gamma", "url": "https://gamma.app"},
            {"name": "Remove.bg", "url": "https://www.remove.bg"},
            {"name": "Photoroom", "url": "https://www.photoroom.com"},
            {"name": "Runway", "url": "https://runwayml.com"},
            {"name": "Midjourney", "url": "https://www.midjourney.com"},
            {"name": "Pika", "url": "https://pika.art"},
            {"name": "Descript", "url": "https://www.descript.com"},
            {"name": "Loom", "url": "https://www.loom.com"},
            {"name": "Capcut", "url": "https://www.capcut.com"},
            {"name": "Veed.io", "url": "https://www.veed.io"},
            {"name": "Riverside", "url": "https://riverside.fm"},
            {"name": "Storybook", "url": "https://storybook.js.org"},
            {"name": "Zeplin", "url": "https://zeplin.io"},
        ],
    },
    "developer_tools": {
        "name": "Developer Tools SaaS",
        "category": "Engineering",
        "sites": [
            {"name": "GitHub", "url": "https://github.com"},
            {"name": "GitLab", "url": "https://about.gitlab.com"},
            {"name": "Vercel", "url": "https://vercel.com"},
            {"name": "Netlify", "url": "https://www.netlify.com"},
            {"name": "Railway", "url": "https://railway.app"},
            {"name": "Render", "url": "https://render.com"},
            {"name": "Supabase", "url": "https://supabase.com"},
            {"name": "PlanetScale", "url": "https://planetscale.com"},
            {"name": "Neon", "url": "https://neon.tech"},
            {"name": "Cloudflare", "url": "https://www.cloudflare.com"},
            {"name": "Fly.io", "url": "https://fly.io"},
            {"name": "DigitalOcean", "url": "https://www.digitalocean.com"},
            {"name": "Heroku", "url": "https://www.heroku.com"},
            {"name": "AWS Amplify", "url": "https://aws.amazon.com/amplify/"},
            {"name": "Firebase", "url": "https://firebase.google.com"},
            {"name": "Sentry", "url": "https://sentry.io"},
            {"name": "LaunchDarkly", "url": "https://launchdarkly.com"},
            {"name": "Postman", "url": "https://www.postman.com"},
            {"name": "Insomnia", "url": "https://insomnia.rest"},
            {"name": "Docker Hub", "url": "https://hub.docker.com"},
            {"name": "Snyk", "url": "https://snyk.io"},
            {"name": "SonarQube", "url": "https://www.sonarsource.com/products/sonarqube/"},
            {"name": "CircleCI", "url": "https://circleci.com"},
            {"name": "Buildkite", "url": "https://buildkite.com"},
            {"name": "Terraform Cloud", "url": "https://www.hashicorp.com/products/terraform"},
            {"name": "Pulumi", "url": "https://www.pulumi.com"},
            {"name": "Upstash", "url": "https://upstash.com"},
            {"name": "Turso", "url": "https://turso.tech"},
            {"name": "Convex", "url": "https://www.convex.dev"},
            {"name": "Replit", "url": "https://replit.com"},
        ],
    },
    "communication": {
        "name": "Communication & Chat SaaS",
        "category": "Collaboration",
        "sites": [
            {"name": "Slack", "url": "https://slack.com"},
            {"name": "Microsoft Teams", "url": "https://www.microsoft.com/en-us/microsoft-teams/group-chat-software"},
            {"name": "Discord", "url": "https://discord.com"},
            {"name": "Zoom", "url": "https://zoom.us"},
            {"name": "Google Meet", "url": "https://meet.google.com"},
            {"name": "Lark", "url": "https://www.larksuite.com"},
            {"name": "Twist", "url": "https://twist.com"},
            {"name": "Rocket.Chat", "url": "https://www.rocket.chat"},
            {"name": "Mattermost", "url": "https://mattermost.com"},
            {"name": "Element", "url": "https://element.io"},
            {"name": "Zulip", "url": "https://zulip.com"},
            {"name": "Pumble", "url": "https://pumble.com"},
            {"name": "Chanty", "url": "https://www.chanty.com"},
            {"name": "Flock", "url": "https://www.flock.com"},
            {"name": "Wire", "url": "https://wire.com"},
            {"name": "Signal", "url": "https://signal.org"},
            {"name": "Webex", "url": "https://www.webex.com"},
            {"name": "GoTo Meeting", "url": "https://www.goto.com/meeting"},
            {"name": "Around", "url": "https://www.around.co"},
            {"name": "Whereby", "url": "https://whereby.com"},
            {"name": "Gather", "url": "https://www.gather.town"},
            {"name": "Loom", "url": "https://www.loom.com"},
            {"name": "Tandem", "url": "https://tandem.chat"},
            {"name": "Vowel", "url": "https://www.vowel.com"},
            {"name": "Krisp", "url": "https://krisp.ai"},
            {"name": "Otter.ai", "url": "https://otter.ai"},
            {"name": "Fireflies.ai", "url": "https://fireflies.ai"},
            {"name": "tl;dv", "url": "https://tldv.io"},
            {"name": "Grain", "url": "https://grain.com"},
            {"name": "Claap", "url": "https://www.claap.io"},
        ],
    },
    "ecommerce_platforms": {
        "name": "E-commerce Platform SaaS",
        "category": "Commerce",
        "sites": [
            {"name": "Shopify", "url": "https://www.shopify.com"},
            {"name": "BigCommerce", "url": "https://www.bigcommerce.com"},
            {"name": "WooCommerce", "url": "https://woocommerce.com"},
            {"name": "Squarespace", "url": "https://www.squarespace.com"},
            {"name": "Wix eCommerce", "url": "https://www.wix.com/ecommerce/website"},
            {"name": "Ecwid", "url": "https://www.ecwid.com"},
            {"name": "Gumroad", "url": "https://gumroad.com"},
            {"name": "Lemon Squeezy", "url": "https://www.lemonsqueezy.com"},
            {"name": "Sellfy", "url": "https://sellfy.com"},
            {"name": "Podia", "url": "https://www.podia.com"},
            {"name": "Thinkific", "url": "https://www.thinkific.com"},
            {"name": "Teachable", "url": "https://teachable.com"},
            {"name": "Kajabi", "url": "https://kajabi.com"},
            {"name": "Payhip", "url": "https://payhip.com"},
            {"name": "Ko-fi", "url": "https://ko-fi.com"},
            {"name": "Paddle", "url": "https://www.paddle.com"},
            {"name": "FastSpring", "url": "https://fastspring.com"},
            {"name": "Snipcart", "url": "https://snipcart.com"},
            {"name": "Medusa", "url": "https://medusajs.com"},
            {"name": "Saleor", "url": "https://saleor.io"},
            {"name": "Commercetools", "url": "https://commercetools.com"},
            {"name": "Magento", "url": "https://business.adobe.com/products/magento/magento-commerce.html"},
            {"name": "PrestaShop", "url": "https://prestashop.com"},
            {"name": "OpenCart", "url": "https://www.opencart.com"},
            {"name": "Volusion", "url": "https://www.volusion.com"},
            {"name": "3dcart", "url": "https://www.shift4shop.com"},
            {"name": "Webflow Ecommerce", "url": "https://webflow.com/ecommerce"},
            {"name": "ThriveCart", "url": "https://thrivecart.com"},
            {"name": "SamCart", "url": "https://www.samcart.com"},
            {"name": "Whop", "url": "https://whop.com"},
        ],
    },
    "marketing_automation": {
        "name": "Marketing Automation SaaS",
        "category": "Marketing",
        "sites": [
            {"name": "HubSpot Marketing", "url": "https://www.hubspot.com/products/marketing"},
            {"name": "Marketo", "url": "https://www.marketo.com"},
            {"name": "Pardot", "url": "https://www.salesforce.com/products/marketing-cloud/"},
            {"name": "ActiveCampaign", "url": "https://www.activecampaign.com"},
            {"name": "Customer.io", "url": "https://customer.io"},
            {"name": "Iterable", "url": "https://iterable.com"},
            {"name": "Braze", "url": "https://www.braze.com"},
            {"name": "Ortto", "url": "https://ortto.com"},
            {"name": "Autopilot", "url": "https://www.autopilothq.com"},
            {"name": "Drip", "url": "https://www.drip.com"},
            {"name": "Mailchimp", "url": "https://mailchimp.com"},
            {"name": "Omnisend", "url": "https://www.omnisend.com"},
            {"name": "Klaviyo", "url": "https://www.klaviyo.com"},
            {"name": "Segment", "url": "https://segment.com"},
            {"name": "RudderStack", "url": "https://www.rudderstack.com"},
            {"name": "Mixpanel", "url": "https://mixpanel.com"},
            {"name": "Intercom", "url": "https://www.intercom.com"},
            {"name": "Drift", "url": "https://www.drift.com"},
            {"name": "Unbounce", "url": "https://unbounce.com"},
            {"name": "Instapage", "url": "https://instapage.com"},
            {"name": "Leadpages", "url": "https://www.leadpages.com"},
            {"name": "OptinMonster", "url": "https://optinmonster.com"},
            {"name": "Privy", "url": "https://www.privy.com"},
            {"name": "Typeform", "url": "https://www.typeform.com"},
            {"name": "Jotform", "url": "https://www.jotform.com"},
            {"name": "SurveyMonkey", "url": "https://www.surveymonkey.com"},
            {"name": "Tally", "url": "https://tally.so"},
            {"name": "Zapier", "url": "https://zapier.com"},
            {"name": "Make", "url": "https://www.make.com"},
            {"name": "n8n", "url": "https://n8n.io"},
        ],
    },
    "cybersecurity": {
        "name": "Cybersecurity SaaS",
        "category": "Security",
        "sites": [
            {"name": "Cloudflare", "url": "https://www.cloudflare.com"},
            {"name": "CrowdStrike", "url": "https://www.crowdstrike.com"},
            {"name": "SentinelOne", "url": "https://www.sentinelone.com"},
            {"name": "1Password", "url": "https://1password.com"},
            {"name": "Dashlane", "url": "https://www.dashlane.com"},
            {"name": "Bitwarden", "url": "https://bitwarden.com"},
            {"name": "LastPass", "url": "https://www.lastpass.com"},
            {"name": "Okta", "url": "https://www.okta.com"},
            {"name": "Auth0", "url": "https://auth0.com"},
            {"name": "Clerk", "url": "https://clerk.com"},
            {"name": "Snyk", "url": "https://snyk.io"},
            {"name": "Drata", "url": "https://drata.com"},
            {"name": "Vanta", "url": "https://www.vanta.com"},
            {"name": "Lacework", "url": "https://www.lacework.com"},
            {"name": "Wiz", "url": "https://www.wiz.io"},
            {"name": "Orca Security", "url": "https://orca.security"},
            {"name": "Palo Alto Networks", "url": "https://www.paloaltonetworks.com"},
            {"name": "Fortinet", "url": "https://www.fortinet.com"},
            {"name": "Sophos", "url": "https://www.sophos.com"},
            {"name": "NordVPN Business", "url": "https://nordlayer.com"},
            {"name": "Tailscale", "url": "https://tailscale.com"},
            {"name": "Twingate", "url": "https://www.twingate.com"},
            {"name": "Teleport", "url": "https://goteleport.com"},
            {"name": "HashiCorp Vault", "url": "https://www.hashicorp.com/products/vault"},
            {"name": "Doppler", "url": "https://www.doppler.com"},
            {"name": "Infisical", "url": "https://infisical.com"},
            {"name": "GitGuardian", "url": "https://www.gitguardian.com"},
            {"name": "Socket", "url": "https://socket.dev"},
            {"name": "Semgrep", "url": "https://semgrep.dev"},
            {"name": "Aikido Security", "url": "https://www.aikido.dev"},
        ],
    },
    "nocode_lowcode": {
        "name": "No-Code / Low-Code SaaS",
        "category": "Development",
        "sites": [
            {"name": "Bubble", "url": "https://bubble.io"},
            {"name": "Webflow", "url": "https://webflow.com"},
            {"name": "Airtable", "url": "https://airtable.com"},
            {"name": "Zapier", "url": "https://zapier.com"},
            {"name": "Make", "url": "https://www.make.com"},
            {"name": "Retool", "url": "https://retool.com"},
            {"name": "Glide", "url": "https://www.glideapps.com"},
            {"name": "Softr", "url": "https://www.softr.io"},
            {"name": "Appsmith", "url": "https://www.appsmith.com"},
            {"name": "Tooljet", "url": "https://www.tooljet.com"},
            {"name": "Budibase", "url": "https://budibase.com"},
            {"name": "Noloco", "url": "https://noloco.io"},
            {"name": "Stacker", "url": "https://www.stackerhq.com"},
            {"name": "Directual", "url": "https://www.directual.com"},
            {"name": "Adalo", "url": "https://www.adalo.com"},
            {"name": "FlutterFlow", "url": "https://flutterflow.io"},
            {"name": "Thunkable", "url": "https://thunkable.com"},
            {"name": "Bravo Studio", "url": "https://www.bfrapp.com"},
            {"name": "Draftbit", "url": "https://draftbit.com"},
            {"name": "Tilda", "url": "https://tilda.cc"},
            {"name": "Carrd", "url": "https://carrd.co"},
            {"name": "Framer", "url": "https://www.framer.com"},
            {"name": "Typedream", "url": "https://typedream.com"},
            {"name": "Super", "url": "https://super.so"},
            {"name": "Coda", "url": "https://coda.io"},
            {"name": "Rows", "url": "https://rows.com"},
            {"name": "Tally", "url": "https://tally.so"},
            {"name": "Typeform", "url": "https://www.typeform.com"},
            {"name": "Jotform", "url": "https://www.jotform.com"},
            {"name": "n8n", "url": "https://n8n.io"},
        ],
    },
    "ai_ml_platforms": {
        "name": "AI & ML Platform SaaS",
        "category": "AI",
        "sites": [
            {"name": "OpenAI", "url": "https://openai.com"},
            {"name": "Anthropic", "url": "https://www.anthropic.com"},
            {"name": "Google AI Studio", "url": "https://aistudio.google.com"},
            {"name": "Hugging Face", "url": "https://huggingface.co"},
            {"name": "Replicate", "url": "https://replicate.com"},
            {"name": "Stability AI", "url": "https://stability.ai"},
            {"name": "Cohere", "url": "https://cohere.com"},
            {"name": "Jasper", "url": "https://www.jasper.ai"},
            {"name": "Copy.ai", "url": "https://www.copy.ai"},
            {"name": "Writer", "url": "https://writer.com"},
            {"name": "Grammarly", "url": "https://www.grammarly.com"},
            {"name": "Otter.ai", "url": "https://otter.ai"},
            {"name": "Descript", "url": "https://www.descript.com"},
            {"name": "Runway", "url": "https://runwayml.com"},
            {"name": "Midjourney", "url": "https://www.midjourney.com"},
            {"name": "ElevenLabs", "url": "https://elevenlabs.io"},
            {"name": "Synthesia", "url": "https://www.synthesia.io"},
            {"name": "Perplexity", "url": "https://www.perplexity.ai"},
            {"name": "You.com", "url": "https://you.com"},
            {"name": "Cursor", "url": "https://www.cursor.com"},
            {"name": "Replit AI", "url": "https://replit.com"},
            {"name": "Tabnine", "url": "https://www.tabnine.com"},
            {"name": "Codeium", "url": "https://codeium.com"},
            {"name": "Sourcegraph", "url": "https://sourcegraph.com"},
            {"name": "LangChain", "url": "https://www.langchain.com"},
            {"name": "LlamaIndex", "url": "https://www.llamaindex.ai"},
            {"name": "Pinecone", "url": "https://www.pinecone.io"},
            {"name": "Weaviate", "url": "https://weaviate.io"},
            {"name": "Weights & Biases", "url": "https://wandb.ai"},
            {"name": "Scale AI", "url": "https://scale.com"},
        ],
    },
    "scheduling": {
        "name": "Scheduling & Booking SaaS",
        "category": "Productivity",
        "sites": [
            {"name": "Calendly", "url": "https://calendly.com"},
            {"name": "Cal.com", "url": "https://cal.com"},
            {"name": "Acuity", "url": "https://acuityscheduling.com"},
            {"name": "TidyCal", "url": "https://tidycal.com"},
            {"name": "SavvyCal", "url": "https://savvycal.com"},
            {"name": "YouCanBookMe", "url": "https://youcanbook.me"},
            {"name": "Doodle", "url": "https://doodle.com"},
            {"name": "Reclaim", "url": "https://reclaim.ai"},
            {"name": "Clockwise", "url": "https://www.getclockwise.com"},
            {"name": "Motion", "url": "https://www.usemotion.com"},
            {"name": "Fantastical", "url": "https://flexibits.com/fantastical"},
            {"name": "Amelia", "url": "https://wpamelia.com"},
            {"name": "SimplyBook", "url": "https://simplybook.me"},
            {"name": "Setmore", "url": "https://www.setmore.com"},
            {"name": "Square Appointments", "url": "https://squareup.com/appointments"},
            {"name": "Fresha", "url": "https://www.fresha.com"},
            {"name": "Booksy", "url": "https://booksy.com"},
            {"name": "Mindbody", "url": "https://www.mindbodyonline.com"},
            {"name": "Vagaro", "url": "https://www.vagaro.com"},
            {"name": "Appointlet", "url": "https://www.appointlet.com"},
            {"name": "Hubspot Meetings", "url": "https://www.hubspot.com/products/sales/schedule-meeting"},
            {"name": "Zcal", "url": "https://zcal.co"},
            {"name": "Koalendar", "url": "https://koalendar.com"},
            {"name": "OnceHub", "url": "https://www.oncehub.com"},
            {"name": "Picktime", "url": "https://www.picktime.com"},
            {"name": "Bookafy", "url": "https://bookafy.com"},
            {"name": "Appointy", "url": "https://www.appointy.com"},
            {"name": "10to8", "url": "https://10to8.com"},
            {"name": "Woven", "url": "https://woven.com"},
            {"name": "Rally", "url": "https://rallly.co"},
        ],
    },
    "social_media": {
        "name": "Social Media Management SaaS",
        "category": "Marketing",
        "sites": [
            {"name": "Hootsuite", "url": "https://www.hootsuite.com"},
            {"name": "Buffer", "url": "https://buffer.com"},
            {"name": "Sprout Social", "url": "https://sproutsocial.com"},
            {"name": "Later", "url": "https://later.com"},
            {"name": "Publer", "url": "https://publer.io"},
            {"name": "SocialBee", "url": "https://socialbee.com"},
            {"name": "Metricool", "url": "https://metricool.com"},
            {"name": "Iconosquare", "url": "https://www.iconosquare.com"},
            {"name": "Agorapulse", "url": "https://www.agorapulse.com"},
            {"name": "Loomly", "url": "https://www.loomly.com"},
            {"name": "Planable", "url": "https://planable.io"},
            {"name": "ContentStudio", "url": "https://contentstudio.io"},
            {"name": "SocialPilot", "url": "https://www.socialpilot.co"},
            {"name": "Sendible", "url": "https://www.sendible.com"},
            {"name": "Tailwind", "url": "https://www.tailwindapp.com"},
            {"name": "CoSchedule", "url": "https://coschedule.com"},
            {"name": "Sprinklr", "url": "https://www.sprinklr.com"},
            {"name": "Khoros", "url": "https://khoros.com"},
            {"name": "Brandwatch", "url": "https://www.brandwatch.com"},
            {"name": "Mention", "url": "https://mention.com"},
            {"name": "Brand24", "url": "https://brand24.com"},
            {"name": "Awario", "url": "https://awario.com"},
            {"name": "Talkwalker", "url": "https://www.talkwalker.com"},
            {"name": "Keyhole", "url": "https://keyhole.co"},
            {"name": "Dash Hudson", "url": "https://www.dashhudson.com"},
            {"name": "Emplifi", "url": "https://emplifi.io"},
            {"name": "Feedhive", "url": "https://www.feedhive.com"},
            {"name": "Hypefury", "url": "https://hypefury.com"},
            {"name": "Repurpose.io", "url": "https://repurpose.io"},
            {"name": "Typefully", "url": "https://typefully.com"},
        ],
    },
    "documentation": {
        "name": "Documentation & Knowledge Base SaaS",
        "category": "Knowledge",
        "sites": [
            {"name": "Notion", "url": "https://www.notion.so"},
            {"name": "Confluence", "url": "https://www.atlassian.com/software/confluence"},
            {"name": "GitBook", "url": "https://www.gitbook.com"},
            {"name": "ReadMe", "url": "https://readme.com"},
            {"name": "Mintlify", "url": "https://mintlify.com"},
            {"name": "Docusaurus", "url": "https://docusaurus.io"},
            {"name": "Archbee", "url": "https://www.archbee.com"},
            {"name": "Slite", "url": "https://slite.com"},
            {"name": "Tettra", "url": "https://tettra.com"},
            {"name": "Guru", "url": "https://www.getguru.com"},
            {"name": "Slab", "url": "https://slab.com"},
            {"name": "BookStack", "url": "https://www.bookstackapp.com"},
            {"name": "Outline", "url": "https://www.getoutline.com"},
            {"name": "Coda", "url": "https://coda.io"},
            {"name": "Almanac", "url": "https://almanac.io"},
            {"name": "Nuclino", "url": "https://www.nuclino.com"},
            {"name": "Scribe", "url": "https://scribehow.com"},
            {"name": "Tango", "url": "https://www.tango.us"},
            {"name": "Loom", "url": "https://www.loom.com"},
            {"name": "Trainual", "url": "https://trainual.com"},
            {"name": "Process Street", "url": "https://www.process.st"},
            {"name": "Whale", "url": "https://usewhale.io"},
            {"name": "Helpjuice", "url": "https://helpjuice.com"},
            {"name": "Document360", "url": "https://document360.com"},
            {"name": "KnowledgeOwl", "url": "https://www.knowledgeowl.com"},
            {"name": "HelpDocs", "url": "https://www.helpdocs.io"},
            {"name": "Zendesk Guide", "url": "https://www.zendesk.com/service/help-center/"},
            {"name": "Intercom Articles", "url": "https://www.intercom.com/help-center"},
            {"name": "Freshdesk KB", "url": "https://www.freshworks.com/freshdesk/knowledge-base/"},
            {"name": "Notion Wiki", "url": "https://www.notion.so/product/wikis"},
        ],
    },
    "cloud_storage": {
        "name": "Cloud Storage & Files SaaS",
        "category": "Storage",
        "sites": [
            {"name": "Dropbox", "url": "https://www.dropbox.com"},
            {"name": "Google Drive", "url": "https://drive.google.com"},
            {"name": "Box", "url": "https://www.box.com"},
            {"name": "OneDrive", "url": "https://www.microsoft.com/en-us/microsoft-365/onedrive/online-cloud-storage"},
            {"name": "pCloud", "url": "https://www.pcloud.com"},
            {"name": "Sync.com", "url": "https://www.sync.com"},
            {"name": "Tresorit", "url": "https://tresorit.com"},
            {"name": "MEGA", "url": "https://mega.io"},
            {"name": "iCloud", "url": "https://www.icloud.com"},
            {"name": "Backblaze", "url": "https://www.backblaze.com"},
            {"name": "Wasabi", "url": "https://wasabi.com"},
            {"name": "Cloudinary", "url": "https://cloudinary.com"},
            {"name": "Uploadcare", "url": "https://uploadcare.com"},
            {"name": "Filestack", "url": "https://www.filestack.com"},
            {"name": "WeTransfer", "url": "https://wetransfer.com"},
            {"name": "Internxt", "url": "https://internxt.com"},
            {"name": "Filen", "url": "https://filen.io"},
            {"name": "Nextcloud", "url": "https://nextcloud.com"},
            {"name": "ownCloud", "url": "https://owncloud.com"},
            {"name": "Seafile", "url": "https://www.seafile.com"},
            {"name": "Egnyte", "url": "https://www.egnyte.com"},
            {"name": "Citrix ShareFile", "url": "https://www.sharefile.com"},
            {"name": "Hightail", "url": "https://www.hightail.com"},
            {"name": "Canto", "url": "https://www.canto.com"},
            {"name": "Bynder", "url": "https://www.bynder.com"},
            {"name": "Brandfolder", "url": "https://brandfolder.com"},
            {"name": "Air", "url": "https://air.inc"},
            {"name": "Playbook", "url": "https://www.playbook.com"},
            {"name": "Notion", "url": "https://www.notion.so"},
            {"name": "Loom Library", "url": "https://www.loom.com"},
        ],
    },
    "forms_surveys": {
        "name": "Forms & Surveys SaaS",
        "category": "Data Collection",
        "sites": [
            {"name": "Typeform", "url": "https://www.typeform.com"},
            {"name": "Jotform", "url": "https://www.jotform.com"},
            {"name": "Tally", "url": "https://tally.so"},
            {"name": "Google Forms", "url": "https://docs.google.com/forms"},
            {"name": "SurveyMonkey", "url": "https://www.surveymonkey.com"},
            {"name": "Paperform", "url": "https://paperform.co"},
            {"name": "Fillout", "url": "https://www.fillout.com"},
            {"name": "Reform", "url": "https://www.reform.app"},
            {"name": "Formbricks", "url": "https://formbricks.com"},
            {"name": "OpinionX", "url": "https://www.opinionx.co"},
            {"name": "Qualtrics", "url": "https://www.qualtrics.com"},
            {"name": "Alchemer", "url": "https://www.alchemer.com"},
            {"name": "Formstack", "url": "https://www.formstack.com"},
            {"name": "Wufoo", "url": "https://www.wufoo.com"},
            {"name": "Cognito Forms", "url": "https://www.cognitoforms.com"},
            {"name": "123FormBuilder", "url": "https://www.123formbuilder.com"},
            {"name": "Zoho Forms", "url": "https://www.zoho.com/forms/"},
            {"name": "Microsoft Forms", "url": "https://forms.office.com"},
            {"name": "HubSpot Forms", "url": "https://www.hubspot.com/products/marketing/forms"},
            {"name": "Gravity Forms", "url": "https://www.gravityforms.com"},
            {"name": "WPForms", "url": "https://wpforms.com"},
            {"name": "Formidable", "url": "https://formidableforms.com"},
            {"name": "Feathery", "url": "https://www.feathery.io"},
            {"name": "Tripetto", "url": "https://tripetto.com"},
            {"name": "Youform", "url": "https://youform.io"},
            {"name": "Screeb", "url": "https://screeb.app"},
            {"name": "Hotjar Surveys", "url": "https://www.hotjar.com/surveys/"},
            {"name": "Survicate", "url": "https://survicate.com"},
            {"name": "Delighted", "url": "https://delighted.com"},
            {"name": "AskNicely", "url": "https://www.asknicely.com"},
        ],
    },
}

# ============================================================
# SAAS-SPECIFIC AI PROMPT
# ============================================================

def get_saas_prompt(site_data, industry_name):
    s = site_data.get("structure", {})
    return f"""Analyze this {industry_name} website for BenchmarkHQ SaaS Benchmark.
Website: {site_data['name']} ({site_data['url']})

PAGE STRUCTURE:
- Title: {s.get('title','N/A')}
- Navigation: {json.dumps(s.get('nav_items',[])[:15])}
- Buttons: {json.dumps(s.get('buttons',[])[:20])}
- Forms: {json.dumps(s.get('forms',[]))}
- Headings: {json.dumps(s.get('headings',[]))}
- Inputs: {json.dumps(s.get('inputs',[])[:15])}
- Footer: {json.dumps(s.get('footer_links',[])[:20])}
- Search: {s.get('has_search_input',False)} | Images: {s.get('images_count',0)} (alt: {s.get('images_with_alt',0)})
- Lang: {s.get('has_lang_attr',False)} | ARIA: {s.get('aria_labels_count',0)} | OG: {s.get('has_og_tags',False)}
- Scripts: {s.get('scripts_count',0)} | Links: {s.get('links_count',0)}

IMPORTANT: Use your knowledge of {site_data['name']} in addition to the HTML data. Mark Y if you KNOW the product has something even if not visible in this snippet.

Check these 50 SaaS quality signals (Y/N/U):

PRICING & BUSINESS MODEL:
pricing_page, transparent_pricing, free_trial, free_tier, multiple_tiers, enterprise_tier, annual_discount, feature_comparison_table

MARKETING SITE:
customer_logos, case_studies, product_screenshots, video_demo, integrations_page, blog, changelog, status_page, about_page, careers_page

TRUST & SECURITY:
security_page, soc2_mentioned, gdpr_mentioned, iso27001_mentioned, privacy_policy, terms_of_service, cookie_consent, dpa_available

DEVELOPER EXPERIENCE:
api_documentation, developer_portal, sdk_available, webhooks_support, api_playground, code_examples, openapi_spec, github_presence

ONBOARDING:
signup_no_creditcard, social_signup, interactive_demo, templates_available, onboarding_video, roi_calculator

SUPPORT:
help_center, live_chat, community_forum, contact_page, sla_published

PRODUCT AVAILABILITY:
ios_app, android_app, desktop_app, browser_extension, multi_language

Return ONLY valid JSON:
{{"features":{{"pricing_page":"Y","transparent_pricing":"Y",...all 50}},"navigation_pattern":"top_nav|sidebar|mega_menu","design_quality_1_to_10":8,"notable_features":["..."],"confidence":"high|medium|low"}}"""


# ============================================================
# SCRAPING ENGINE (same as e-commerce scraper)
# ============================================================

def scrape_website(url, output_dir, name):
    result = {"name": name, "url": url, "scanned_at": datetime.now().isoformat(), "screenshots": {}, "structure": {}, "errors": []}
    viewports = {"desktop": {"width": 1280, "height": 720}, "mobile": {"width": 375, "height": 812}}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for vp_name, vp_size in viewports.items():
            try:
                ctx = browser.new_context(viewport=vp_size, user_agent=USER_AGENT)
                page = ctx.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
                page.wait_for_timeout(JS_RENDER_WAIT)
                ss_path = os.path.join(output_dir, f"{name}_{vp_name}.png")
                page.screenshot(path=ss_path, full_page=False)
                result["screenshots"][vp_name] = ss_path
                if vp_name == "desktop":
                    soup = BeautifulSoup(page.content(), "html.parser")
                    nav = soup.find("nav") or soup.find("header")
                    nav_links = nav.find_all("a")[:20] if nav else []
                    footer = soup.find("footer")
                    footer_links = footer.find_all("a")[:20] if footer else []
                    buttons = soup.find_all("button")
                    ctas = soup.find_all("a", class_=lambda c: c and any(w in str(c).lower() for w in ["btn","button","cta"]))
                    result["structure"] = {
                        "title": page.title(), "url_final": page.url,
                        "nav_items": [{"text":a.get_text(strip=True)[:50],"href":a.get("href","")[:100]} for a in nav_links],
                        "buttons": [b.get_text(strip=True)[:50] for b in (buttons+ctas)[:30] if b.get_text(strip=True)],
                        "forms": [{"action":f.get("action","")[:100],"method":f.get("method",""),"fields":[{"type":i.get("type","text"),"name":i.get("name",""),"placeholder":i.get("placeholder","")[:50]} for i in f.find_all(["input","select","textarea"])[:10]]} for f in soup.find_all("form")[:5]],
                        "links_count": len(soup.find_all("a")), "images_count": len(soup.find_all("img")),
                        "images_with_alt": len([i for i in soup.find_all("img") if i.get("alt")]),
                        "headings": [{"level":l,"text":h.get_text(strip=True)[:80]} for l in range(1,4) for h in soup.find_all(f"h{l}")[:5]],
                        "inputs": [{"type":i.get("type","text"),"name":i.get("name",""),"placeholder":i.get("placeholder","")[:50]} for i in soup.find_all("input")[:20]],
                        "footer_links": [a.get_text(strip=True)[:50] for a in footer_links if a.get_text(strip=True)],
                        "has_search_input": bool(soup.find("input",attrs={"type":"search"}) or soup.find("input",attrs={"placeholder":lambda p:p and "search" in p.lower()})),
                        "has_lang_attr": bool(soup.find("html",attrs={"lang":True})),
                        "aria_labels_count": len(soup.find_all(attrs={"aria-label":True})),
                        "has_og_tags": bool(soup.find("meta",property="og:title")),
                        "meta_description": (soup.find("meta",attrs={"name":"description"}) or {}).get("content","")[:200] if soup.find("meta",attrs={"name":"description"}) else "",
                        "scripts_count": len(soup.find_all("script")),
                    }
                ctx.close()
            except Exception as e:
                result["errors"].append(f"{vp_name}: {str(e)[:200]}")
        browser.close()
    return result


def detect_features_with_ai(site_data, industry_name):
    from openai import OpenAI
    if not OPENAI_API_KEY: return {"error": "OPENAI_API_KEY not set"}
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    prompt = get_saas_prompt(site_data, industry_name)
    try:
        resp = client.chat.completions.create(model=OPENAI_MODEL, messages=[{"role":"user","content":prompt}], temperature=0.1, max_tokens=2000)
        text = resp.choices[0].message.content
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
            text = text.strip()
        return json.loads(text)
    except json.JSONDecodeError: return {"raw_response": text[:500], "error": "JSON parse failed"}
    except Exception as e: return {"error": str(e)[:300]}


def calculate_frequencies(all_results):
    good = [r for r in all_results if r.get("structure",{}).get("images_count",0)>3 or len(r.get("structure",{}).get("nav_items",[]))>2 or len(r.get("structure",{}).get("buttons",[]))>2]
    if not good: good = all_results
    feats = {}
    for site in good:
        for k,v in site.get("ai_analysis",{}).get("features",{}).items():
            if k not in feats: feats[k]={"Y":0,"N":0,"U":0,"total":0}
            feats[k]["total"]+=1
            if v=="Y": feats[k]["Y"]+=1
            elif v=="N": feats[k]["N"]+=1
            else: feats[k]["U"]+=1
    bench = {}
    for k,c in feats.items():
        t=c["Y"]+c["N"]
        f=round(c["Y"]/t*100) if t>0 else 0
        cls="CRITICAL" if f>=85 else "REQUIRED" if f>=65 else "RECOMMENDED" if f>=40 else "NICE_TO_HAVE" if f>=15 else "INNOVATIVE"
        bench[k]={"present_count":c["Y"],"absent_count":c["N"],"uncertain_count":c["U"],"total_sites":c["total"],"total_good_sites":len(good),"frequency_percent":f,"classification":cls}
    return dict(sorted(bench.items(),key=lambda x:x[1]["frequency_percent"],reverse=True))


def generate_yaml(key, data, freqs, results):
    import yaml
    b={"metadata":{"industry":key,"name":data["name"],"category":data.get("category",""),"version":"1.0.0","generated_at":datetime.now().isoformat(),"sites_analyzed":len(results),"sites":[r["name"] for r in results]},"features":{"critical":[],"required":[],"recommended":[],"nice_to_have":[],"innovative":[]}}
    for k,d in freqs.items():
        e={"id":k,"frequency":f"{d['present_count']}/{d['total_good_sites']}","percent":d["frequency_percent"]}
        c=d["classification"].lower()
        if c in b["features"]: b["features"][c].append(e)
    return yaml.dump(b,default_flow_style=False,sort_keys=False,allow_unicode=True)


def scan_industry(key, max_sites=30):
    d=INDUSTRIES[key]; sites=d["sites"][:max_sites]
    print(f"\n{'='*60}\n  BenchmarkHQ SaaS — {d['name']}\n  Category: {d.get('category','')} | Sites: {len(sites)} | Model: {OPENAI_MODEL}\n{'='*60}\n")
    date_str=datetime.now().strftime("%Y-%m-%d"); base=f"data/{key}/{date_str}"; ss=f"{base}/screenshots"; os.makedirs(ss,exist_ok=True)
    results=[]
    for i,site in enumerate(sites):
        print(f"[{i+1}/{len(sites)}] {site['name']} ({site['url']})")
        sd=scrape_website(site["url"],ss,site["name"].lower().replace(" ","_").replace("&","and").replace(".",""))
        if sd["errors"]: print(f"  ⚠ {sd['errors'][0][:80]}")
        st=sd.get("structure",{});print(f"  Structure: nav={len(st.get('nav_items',[]))} btn={len(st.get('buttons',[]))} img={st.get('images_count',0)}")
        sd["ai_analysis"]=detect_features_with_ai(sd,d["name"])
        f=sd["ai_analysis"].get("features",{});y=sum(1 for v in f.values() if v=="Y");n=sum(1 for v in f.values() if v=="N")
        print(f"  AI: {y} present, {n} absent")
        results.append(sd)
        sf=f"{base}/{site['name'].lower().replace(' ','_').replace('&','and').replace('.','')}.json"
        with open(sf,"w") as fh: json.dump(sd,fh,indent=2,default=str)
        time.sleep(DELAY_BETWEEN_SITES)
    freqs=calculate_frequencies(results)
    for cn in ["CRITICAL","REQUIRED","RECOMMENDED"]:
        items=[k for k,v in freqs.items() if v["classification"]==cn]
        if items:
            print(f"\n  {cn} ({len(items)}):")
            for k in items: print(f"    {k}: {freqs[k]['frequency_percent']}%")
    with open(f"{base}/frequency_analysis.json","w") as f: json.dump(freqs,f,indent=2)
    y=generate_yaml(key,d,freqs,results)
    with open(f"{base}/benchmark.yaml","w") as f: f.write(y)
    with open(f"{base}/complete_results.json","w") as f: json.dump(results,f,indent=2,default=str)
    print(f"\n  DONE → {base}/ | Features: {len(freqs)}")
    return base


def main():
    p=argparse.ArgumentParser(description="BenchmarkHQ SaaS Scraper v1.0")
    p.add_argument("--industry",help="Industry key (e.g. project_management, crm)")
    p.add_argument("--all",action="store_true",help="Scan ALL 20 SaaS categories")
    p.add_argument("--list",action="store_true",help="List available categories")
    p.add_argument("--sites",type=int,default=30,help="Max sites per category")
    a=p.parse_args()
    if a.list:
        print("\nSaaS categories:\n")
        for k,d in INDUSTRIES.items(): print(f"  {k:25s} {d['name']:40s} ({len(d['sites'])} sites)")
        print(f"\nTotal: {len(INDUSTRIES)} categories, {sum(len(d['sites']) for d in INDUSTRIES.values())} products")
        return
    if not OPENAI_API_KEY: print("ERROR: export OPENAI_API_KEY=sk-..."); sys.exit(1)
    if a.all:
        total=sum(len(d["sites"][:a.sites]) for d in INDUSTRIES.values())
        print(f"\n{'#'*60}\n  SCANNING ALL {len(INDUSTRIES)} SAAS CATEGORIES ({total} products)\n{'#'*60}")
        res={}
        for k in INDUSTRIES:
            try: res[k]={"status":"success","output":scan_industry(k,a.sites)}
            except Exception as e: print(f"\n  ERROR {k}: {e}"); res[k]={"status":"error","error":str(e)}
        os.makedirs("data",exist_ok=True)
        with open("data/saas_scan_summary.json","w") as f: json.dump(res,f,indent=2)
        ok=sum(1 for r in res.values() if r["status"]=="success")
        print(f"\n{'#'*60}\n  ALL DONE! {ok}/{len(INDUSTRIES)} successful\n{'#'*60}\n")
    elif a.industry:
        if a.industry not in INDUSTRIES: print(f"Unknown: {a.industry}. Use --list"); sys.exit(1)
        scan_industry(a.industry,a.sites)
    else: p.print_help()

if __name__=="__main__": main()
