---
title: "Eanes ISD & Recapture — Replication Code"
excerpt: "Python build script and source-cited data for the Southbound 35 explainer on how Texas school finance recapture (Robin Hood) works, using Eanes ISD as the case study."
collection: portfolio
category: replication
permalink: /portfolio/eanes-recapture/
---

Build script for the figures in the Southbound 35 post [**Eanes ISD and Robin Hood: How Recapture Actually Works**]({{ '/posts/2026/06/eanes-recapture/' | relative_url }}). Five charts: where each Eanes M&O dollar goes, statewide recapture totals 2005–2023, top Chapter 49 payers, per-pupil M&O collected vs. net, and the Tier 1 / Golden Pennies / Copper Pennies structure.

- **Source:** [github.com/scottlangford2/southbound-35/tree/main/posts/eanes-recapture](https://github.com/scottlangford2/southbound-35/tree/main/posts/eanes-recapture)
- **Data:** TEA Recapture annual summaries; TEA School District Funding (SDF) reports; Eanes ISD adopted budgets; HB 3 (86R, 2019)

Run:

```bash
pip install -r requirements.txt
python build_figures.py
```

Outputs five PNGs into the website's `images/eanes/` directory.
