---
title: "Research RFP Scraper"
excerpt: "Automated pipeline that scrapes 30 federal, state, and foundation funding sources across all 50 states, scores opportunities against researcher profiles using a five-signal composite trained on an institutional research corpus, and delivers personalized weekly digests to subscribers across multiple universities."
collection: portfolio
---

An automated pipeline that aggregates federal, state, local, and foundation funding opportunities from 30 sources across all 50 states. The scraper classifies RFPs by research keywords, extracts key terms via NLP, and scores relevance against individual researcher profiles using an institutional training corpus. Personalized weekly email digests are delivered to subscribers across multiple universities.

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
5. **Score** relevance using a five-signal weighted composite calibrated by an institutional training corpus
6. **Generate** an HTML dashboard with interactive state coverage map
7. **Push** the dashboard to GitHub Pages

## Relevance Scoring

Each subscriber has a research profile built from OpenAlex, NIH RePORTER, and NSF Awards data. The TF-IDF vectorizer is trained on 100,000 faculty publications from 565 US universities, providing calibrated vocabulary weights across the full breadth of research domains. The relevance scorer uses a weighted composite:

- **Topic similarity (35%)** --- TF-IDF cosine similarity, trained on institutional corpus
- **Concept overlap (25%)** --- Score-weighted matching with concept-to-term expansion from 35,000+ OpenAlex concepts
- **Co-author expertise (15%)** --- Collaboration-depth-weighted concept overlap from top co-authors
- **Agency familiarity (10%)** --- Graduated scoring: personal grants > institutional funders (11,000+ funders)
- **Keyword match (15%)** --- Max of exact substring fraction and TF-IDF semantic similarity

## Links

- [Live Dashboard](https://scottlangford2.github.io/research-scraper/)
- [GitHub Repository](https://github.com/scottlangford2/research-scraper)
