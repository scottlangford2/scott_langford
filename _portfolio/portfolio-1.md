---
title: "RFP Scraper"
excerpt: "Automated grant and RFP monitoring system that scrapes 19 federal, state, and local procurement portals, scores opportunities using researcher profiles, and delivers personalized weekly digests to a 24-member research team.<br/><a href='https://scottlangford2.github.io/research-scraper/'>Live Dashboard</a>"
collection: portfolio
---

An automated pipeline that monitors 19 procurement and grant sources — including SAM.gov, Grants.gov, NSF, NIH RePORTER, and state-level portals across 20 states — for research funding opportunities relevant to a multi-university team of public administration scholars.

**Key features:**

- **Research-profile-aware scoring:** Builds researcher profiles from OpenAlex publications, NIH and NSF grant histories, and co-author networks. Scores each RFP using a weighted composite of topic similarity (TF-IDF), concept overlap, co-author expertise, agency familiarity, and keyword match.
- **Personalized weekly digests:** Each of 24 team members across 10 universities receives their top-ranked RFPs, sorted by relevance to their specific research profile.
- **Interactive dashboard:** Real-time summary of scrape results with source breakdowns, keyword match rates, and top funding recipients.
- **Fully automated:** Scheduled daily scrapes and Monday morning email delivery via launchd.

**Built with:** Python, Playwright, scikit-learn, OpenAlex API, NIH RePORTER API, NSF Awards API, Apache Parquet

[GitHub Repository](https://github.com/scottlangford2/research-scraper) | [Live Dashboard](https://scottlangford2.github.io/research-scraper/)
