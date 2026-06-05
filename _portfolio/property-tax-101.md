---
title: "Property Tax Mechanics 101 — Replication Code"
excerpt: "Python build script and source-cited data for the Southbound 35 explainer on how a Texas property tax bill is assembled."
collection: portfolio
category: replication
permalink: /portfolio/property-tax-101/
---

Build script for the figures in the Southbound 35 post [**How a Texas Property Tax Bill is Built**]({{ '/posts/2026/06/property-tax-101/' | relative_url }}). Five charts: the bill-component waterfall, state effective-rate ranking, statewide levy growth before and after SB 2, the taxing-unit count by county type, and the M&O versus I&S split of the school district rate.

- **Source:** [github.com/scottlangford2/southbound-35/tree/main/posts/property-tax-101](https://github.com/scottlangford2/southbound-35/tree/main/posts/property-tax-101)
- **Data:** Texas Comptroller (Biennial Property Tax Report), Tax Foundation (state effective rates), Texas Education Agency (school tax rate summaries), Comptroller Truth-in-Taxation worksheets

Run:

```bash
pip install -r requirements.txt
python build_figures.py
```

Outputs five PNGs into the website's `images/property-tax/` directory.
