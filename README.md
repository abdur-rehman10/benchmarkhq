# BenchmarkHQ

**Open-source industry benchmarks for web development.**

We analyzed **329 e-commerce websites across 19 countries** to create the first machine-readable, frequency-based industry benchmark for web applications.

## What is this?

Every industry has unwritten standards — features that users expect, UX patterns that work, performance targets that matter. We measured them.

For each country, we studied the top 30 e-commerce websites using automated scraping (Playwright) and AI analysis (GPT-4o). Every feature was classified based on how many of the top sites have it:

| Classification | Frequency | Meaning |
|---|---|---|
| **CRITICAL** | 85-100% | Users expect this. Missing = app feels broken |
| **REQUIRED** | 65-84% | Most competitors have it. Missing = disadvantage |
| **RECOMMENDED** | 40-64% | Becoming standard. Include if resources allow |
| **NICE_TO_HAVE** | 15-39% | Differentiator, not expected |
| **INNOVATIVE** | <15% | Cutting-edge, rare |

## Countries Covered

| Country | Sites Analyzed | Critical Features |
|---|---|---|
| 🇺🇸 USA | 16 | 41 |
| 🇬🇧 United Kingdom | 18 | 39 |
| 🇦🇺 Australia | 17 | 39 |
| 🇧🇷 Brazil | 16 | 44 |
| 🇫🇷 France | 16 | 37 |
| 🇮🇳 India | 13 | 41 |
| 🇨🇳 China | 22 | 34 |
| 🇨🇦 Canada | 13 | 30 |
| 🇲🇽 Mexico | 12 | 24 |
| 🇦🇷 Argentina | 22 | 16 |
| 🇷🇺 Russia | 13 | 18 |
| 🇳🇱 Netherlands | 23 | 29 |
| 🇵🇱 Poland | 22 | 37 |
| 🇹🇷 Turkiye | 22 | 27 |
| 🇸🇦 Saudi Arabia | 17 | 26 |
| 🇦🇪 UAE | 16 | 29 |
| 🇶🇦 Qatar | 15 | 26 |
| 🇵🇰 Pakistan | 23 | 14 |
| 🇪🇸 Spain | 13 | 26 |

**Total: 329 sites analyzed, 855 feature data points**

## Data Format

Each country has a `benchmark.yaml` file and a `frequency_analysis.json` file:
data/
├── ecommerce_usa/
│   └── 2026-03-31/
│       ├── benchmark.yaml           # The benchmark file
│       ├── frequency_analysis.json  # Detailed frequency data
│       ├── complete_results.json    # Raw data for all sites
│       └── [site].json              # Individual site data
├── ecommerce_uk/
│   └── ...
└── ...

## How Benchmarks Are Created

1. **Automated scraping** — Playwright visits each website, extracts page structure (navigation, buttons, forms, images, headings, inputs, accessibility attributes)
2. **AI analysis** — GPT-4o analyzes the structure AND uses its knowledge of each website to detect 45 features
3. **Frequency calculation** — Count how many of the top sites have each feature
4. **Classification** — Assign CRITICAL/REQUIRED/RECOMMENDED based on frequency thresholds

## Features Tracked (45 per site)

Search & discovery, user accounts, product display, cart & checkout, reviews & ratings, personalization, order management, customer support, accessibility & compliance, design patterns.

## Use Cases

- **Developers**: Check if your app has all industry-standard features
- **Product managers**: Plan features based on what competitors actually have
- **AI coding tools**: Verify that AI-generated apps meet industry standards
- **Agencies**: Show clients what "complete" looks like with data

## Contributing

We welcome contributions! You can:
- Propose new features to track
- Add new countries or industries
- Report inaccuracies in the data
- Improve the scraping methodology

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

- **Benchmark data**: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)
- **Scraper code**: MIT License

## Built By

BenchmarkHQ — Making product quality measurable.
