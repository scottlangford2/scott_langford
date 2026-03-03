---
title: "Research RFP Scraper"
excerpt: "Automated pipeline that scrapes 30 federal, state, and foundation funding sources across all 50 states, scores opportunities against researcher profiles using NLP, and delivers personalized weekly digests to 28 subscribers across 16 universities."
collection: portfolio
---

An automated pipeline that aggregates federal, state, local, and foundation funding opportunities from 30 sources across all 50 states. The scraper classifies RFPs by research keywords, extracts key terms via NLP, and delivers personalized weekly email digests to 28 subscribers across 16 universities based on their research profiles.

## Sources

The pipeline currently scrapes **30 sources** organized into three tiers:

**Federal (8):** SAM.gov, Grants.gov, SBIR.gov, NIH RePORTER, NSF Awards, Federal Register, USAspending.gov, ProPublica Nonprofits

**State & Local (9):** Socrata open data portals, BidNet, DemandStar, BuySpeed, JAGGAER, 43 state procurement portals, Texas ESBD, North Carolina eVP, New York NYSCR

**Foundations & Aggregators (13):** Regulations.gov, Robert Wood Johnson Foundation, Russell Sage Foundation, Arnold Ventures, Spencer Foundation, W.T. Grant Foundation, Joyce Foundation, APSA, SSRC, Philanthropy News Digest, Candid, Pivot-RP, OpenGrants

## Pipeline

Each run follows a seven-step pipeline:

1. **Scrape** all 30 sources via REST APIs, HTML parsing, and headless browser automation
2. **Deduplicate** via SHA-256 hashing
3. **Classify** against 226 keyword phrases (deductive)
4. **Extract** key terms via RAKE NLP (inductive)
5. **Score** relevance using a weighted composite of TF-IDF topic similarity, concept overlap, co-author expertise, agency familiarity, and keyword match
6. **Generate** an HTML dashboard with interactive state coverage map
7. **Push** the dashboard to GitHub Pages

## Relevance Scoring

Each subscriber has a research profile built from OpenAlex, NIH RePORTER, and NSF Awards data. The relevance scorer uses a weighted composite:

- Topic similarity (TF-IDF cosine) --- 35%
- Concept overlap (Jaccard) --- 25%
- Co-author expertise --- 15%
- Agency familiarity --- 10%
- Keyword match fraction --- 15%

## Links

- [Live Dashboard](https://scottlangford2.github.io/research-scraper/)
- [GitHub Repository](https://github.com/scottlangford2/research-scraper)
