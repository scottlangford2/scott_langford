---
title: "I-35 Austin–San Antonio Corridor — Replication Code"
excerpt: "Python build script and source-cited data for the Southbound 35 history of the I-35 corridor between Austin and San Antonio."
collection: portfolio
category: replication
permalink: /portfolio/i35-austin-sa/
---

Build script for the figures in the Southbound 35 post [**Eighty Miles: A Short History of the I-35 Corridor Between Austin and San Antonio**]({{ '/posts/2026/06/i35-austin-sa/' | relative_url }}). Five charts: 1950–2020 population trajectory for the five corridor counties, decadal growth rates, a schematic map of the corridor, recent TxDOT AADT counts, and real GDP indexed to 2001.

- **Source:** [github.com/scottlangford2/southbound-35/tree/main/posts/i35-austin-sa](https://github.com/scottlangford2/southbound-35/tree/main/posts/i35-austin-sa)
- **Data:** U.S. Census Decennial 1950–2020; ACS 2023; TxDOT STARS; U.S. Bureau of Economic Analysis regional GDP

Run:

```bash
pip install -r requirements.txt
python build_figures.py
```

Outputs five PNGs into the website's `images/i35/` directory.
