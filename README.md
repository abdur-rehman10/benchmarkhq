# BenchmarkHQ

**Open-source industry benchmarks for web development.**

We analyzed 900+ websites across 42 industries to create machine-readable quality standards. The data tells you what features your industry expects — based on frequency analysis of real websites, not opinions.

🌐 **Website:** [benchmarkhq.site](https://benchmarkhq.site)
📡 **API:** [api.benchmarkhq.site](https://api.benchmarkhq.site/docs)
📖 **Blog:** [benchmarkhq.site/blog](https://benchmarkhq.site/blog/)

## Quick Start

```bash
# List all 42 industries
curl https://api.benchmarkhq.site/industries

# Get benchmark for any industry
curl https://api.benchmarkhq.site/benchmark/ecommerce_usa

# Check your site against the benchmark
curl -X POST https://api.benchmarkhq.site/check \
  -H "Content-Type: application/json" \
  -d '{"industry": "crm", "features": ["free_trial", "api_docs", "sso"]}'
```

No signup. No API key. Free and open.

## What's Covered

### E-commerce (19 Countries)

| Country | Sites | Critical Features |
|---------|-------|-------------------|
| 🇺🇸 USA | 30 | 41 |
| 🇬🇧 UK | 30 | 39 |
| 🇧🇷 Brazil | 30 | 44 |
| 🇮🇳 India | 30 | 41 |
| 🇫🇷 France | 30 | 37 |
| 🇩🇪 Germany | 30 | 37 |
| 🇨🇳 China | 30 | 34 |
| 🇦🇺 Australia | 30 | 39 |

Plus: Canada, Mexico, Argentina, Spain, Netherlands, Poland, Russia, Türkiye, Saudi Arabia, UAE, Qatar, Pakistan

### SaaS (20 Categories)

| Category | Sites | Critical |
|----------|-------|----------|
| Project Management | 27 | 22 |
| CRM | 27 | 16 |
| Developer Tools | 30 | 28 |
| Cybersecurity | 29 | 26 |
| Marketing Automation | 28 | 29 |
| No-Code / Low-Code | 29 | 23 |

Plus: Analytics, Customer Support, Email Marketing, HR, Accounting, Design, Communication, Documentation, Cloud Storage, Social Media, Scheduling, Forms, AI/ML Platforms, E-commerce Platforms

### News & Media (147 Countries) — In Progress 🔄

1,730 news websites across 147 countries, checked against 151 features.

## How It Works

1. **Research** — Custom feature checklist per industry
2. **Crawl** — Playwright visits 30 sites per market, takes screenshots
3. **Analyze** — GPT-4o Vision identifies features from screenshots
4. **Classify** — Frequency analysis: 80%+ = CRITICAL, 50-79% = REQUIRED, 25-49% = RECOMMENDED, <25% = OPTIONAL

## Feature Classification

| Classification | Threshold | Meaning |
|---------------|-----------|---------|
| **CRITICAL** | 80%+ of sites | Your users expect this. Must have. |
| **REQUIRED** | 50-79% | Most competitors have it. Should have. |
| **RECOMMENDED** | 25-49% | Nice to have. Differentiator. |
| **OPTIONAL** | <25% | Rare. Only if it fits your product. |

## GitHub Action

Add benchmark checking to your CI/CD:

```yaml
name: Benchmark Check
on: [pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: abdur-rehman10/benchmarkhq@main
        with:
          industry: ecommerce_usa
          features: search_bar,product_reviews,cart,checkout
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/industries` | List all available industries |
| GET | `/benchmark/{key}` | Get benchmark for an industry |
| GET | `/benchmark/{key}/features` | Get feature list only |
| POST | `/check` | Check your features against benchmark |

Interactive docs: [api.benchmarkhq.site/docs](https://api.benchmarkhq.site/docs)

## Tech Stack

| Component | Technology | Cost |
|-----------|------------|------|
| Scraping | Playwright (Python) | Free |
| AI Analysis | GPT-4o Vision | ~$0.01/site |
| API | FastAPI | Free |
| Hosting | Railway | $5/month |
| Website | GitHub Pages | Free |

## License

- **Code:** MIT
- **Data:** Creative Commons BY-SA 4.0

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new industries, countries, or improving data quality.

## Links

- [Website](https://benchmarkhq.site)
- [API Docs](https://api.benchmarkhq.site/docs)
- [Blog](https://benchmarkhq.site/blog/)
- [All Industries](https://api.benchmarkhq.site/industries)
