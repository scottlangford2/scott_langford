# PA 3311 / PS 3315 — Course Spine Datasets (Codebook)

Two related files. **Use the panel as the primary course dataset.**

| File | Shape | Has debt? | Best for |
|---|---|---|---|
| **`TX_City_Sales_Panel_2013_2024.xlsx`** ⭐ primary | long panel, city × year | no | trends, growth, paired/repeated comparisons, COVID shock, plus all cross-sectional methods on a single-year slice |
| `TX_City_Finance_2022.xlsx` supplement | cross-section, one row per city | **yes** | the regression/OVB module if you want a debt outcome (single year) |

---

## PRIMARY: `TX_City_Sales_Panel_2013_2024`
**Unit:** Texas city × year. **13,930 rows; 1,180 cities; years 2013–2024.** Long format (one row per city per year).

### Sources (all free, no API key)
- **Texas Comptroller, data.texas.gov** — Sales Tax Allocation (`vfba-b57j`, annual sum of monthly payments), Quarterly Sales Tax Historical (`7z4d-yf2c`, taxable sales + outlets, 2016+), City–County Comparison (`53pa-m7sm`, local rate).
- **Census 2022 Census of Governments directory** — `county`, `metro_status`, and a **2022 reference population** (time-invariant).

### Variables
| Variable | Description | Units | Notes |
|---|---|---|---|
| `city` | City name | — | |
| `county` | County | — | time-invariant |
| `metro_status` | Metro (in a Metropolitan Statistical Area) vs. Non-Metro | category | time-invariant; OMB/Census CBSA 2023 |
| `cbsa_type` | Metropolitan / Micropolitan / Neither | category | time-invariant; OMB/Census CBSA 2023 |
| `population_2022_ref` | 2022 reference population | persons | **fixed across years** — denominator only |
| `year` | Calendar year | 2013–2024 | |
| `sales_tax_alloc` | Sales-tax allocation payments | $/yr | 2013–2024 |
| `sales_tax_alloc_per_capita` | alloc / 2022 ref population | $ | |
| `sales_tax_alloc_real2024` | allocation in constant 2024 dollars | $/yr | CPI-U deflated |
| `sales_tax_alloc_per_capita_real2024` | real (2024$) allocation per capita | $ | derived |
| `taxable_sales` | Total taxable sales | $/yr | **2016+ only** (blank 2013–15) |
| `taxable_sales_per_capita` | taxable_sales / 2022 ref population | $ | 2016+ |
| `business_outlets` | Avg. active business outlets (quarterly mean) | count | 2016+ |
| `sales_tax_rate` | Local sales-tax rate | percent | |
| `has_edc` | 1 if the city operates a Type A and/or Type B economic-development corporation (EDC) sales tax | 0/1 | TX Comptroller EDC reports (see below) |
| `edc_type` | `A`, `B`, `A&B`, or blank (none) | category | TX Comptroller EDC reports |
| `edc_first_report_year` | Earliest fiscal year the city appears in EDC report data — **left-censored proxy** for adoption, not a clean date | year | TX Comptroller EDC reports |

**Economic-development sales tax (`has_edc`, `edc_type`, `edc_first_report_year`) — Case A.** Source: Texas Comptroller *EDC Report Data* ("big table," data.texas.gov `d4dd-rd43`, annual EDC reports FY1997–present). 637 of 1,180 panel cities operate an EDC (B = 369, A&B = 190, A = 78). **Use `has_edc`/`edc_type` as a cross-sectional treatment** (EDC vs. non-EDC cities). **Caveat:** EDC reporting began in FY1997, so `edc_first_report_year` is left-censored at 1997 — by 1998 some 384 Texas cities had *already* adopted (TEDC). Most adoption therefore predates this 2013–2024 panel (only ~45 cities first report in 2013+), so the column does **not** support a clean adoption-date difference-in-differences; a credible adoption-date DiD would require an open-records request to the Comptroller for per-jurisdiction tax effective dates. Rebuild with `scripts/add_edc.py`. (4A/Type A authorized 1989; 4B/Type B 1991.)

`metro_status` and `cbsa_type` use the official **OMB / Census CBSA delineation (2023)**: a city is *Metro* if its county belongs to a Metropolitan Statistical Area, *Non-Metro* otherwise (Micropolitan or neither). `cbsa_type` keeps the full three-way distinction.

### Panel notes / teaching points
- **Mostly balanced:** 1,143 of 1,180 cities have all 12 years; the rest incorporated or began receiving allocations mid-period (unbalanced panel — a real teaching point).
- **`population_2022_ref` is fixed at 2022**, so per-capita values change only through the numerator. Free annual city population isn't available without the Census API; flagged as a deliberate simplification.
- **Taxable sales/outlets begin in 2016**, so 2013–2015 are blank for those columns.
- **2020 shows the COVID demand shock** in most cities — a great motivating example (e.g., Austin allocation dips 2019→2020 then surges).

### How this single file powers each module
- **Descriptives & graphs:** filter to one year (e.g., 2024) → skewed distributions of `sales_tax_alloc_per_capita`, histograms, mean vs. median, outliers.
- **z-scores & probability:** standardize per-capita sales tax within a year.
- **Hypothesis testing / CIs:** mean per-capita sales tax with a confidence interval (one year).
- **Independent-samples t-test:** per-capita sales tax for **Metro vs. Non-Metro** (one year); or per-capita taxable sales for **EDC vs. non-EDC** cities (`has_edc`) — a Case A treatment comparison (note the skew: EDC median \$24k vs. \$10k, but means not significantly different — a selection/skew lesson).
- **Paired-samples t-test:** `sales_tax_alloc` **2019 vs. 2023** (or 2019 vs. 2020, COVID) — same cities, two years.
- **Correlation & simple regression:** `sales_tax_alloc` ~ `taxable_sales` (one year).
- **Multiple regression + OVB:** `sales_tax_alloc` ~ `business_outlets` (simple) → add `taxable_sales` (watch the coefficient move).
- **Trends/growth (panel bonus):** plot one city over time; compute year-over-year growth; compare metro vs. non-metro recovery after 2020.
- **Final project:** students pose their own question from the panel.

> In Excel, get a single-year cross-section with **Data → Filter** on `year`, or a **PivotTable**.

---

## SUPPLEMENT: `TX_City_Finance_2022` (has debt)
Cross-section, one row per city (N=1,202), 2022. Carries the same `city`/`county`/`county_fips`/`place_fips`/`metro_status`/`cbsa_type`/`population` keys as the panel, and adds variables not available annually:
`property_tax`, `gen_sales_tax`, `total_taxes`, `tax_per_capita`, `lt_debt_os`, `st_debt_os`, `total_debt_os`, `debt_per_capita` — from the **U.S. Census 2022 Census of Governments** individual unit file (amounts in dollars; debt = long-term `49U` + short-term `64V`). Use this if you want a **debt** outcome for the regression/OVB module. **No fund balance** exists in any free source (so the literal Chapter 8 fund-balance variable can't be reproduced). ~30% of small cities carry $0 debt (real; good for discussing zeros/skew).

---

## Summary statistics (auto-generated)

*All dollar amounts in nominal dollars unless marked real. Heavy right-skew (mean ≫ median) throughout — itself a teaching point.*

### Panel — all 13,930 city-years (2013–2024)

| Variable | N | Mean | Median | SD | Min | Max | Miss % |
|---|--:|--:|--:|--:|--:|--:|--:|
| `population_2022_ref` | 13,556 | 19,034 | 2,156 | 107,119 | 17.00 | 2,316,120 | 2.7 |
| `sales_tax_alloc` | 13,930 | 5,498,823 | 377,731 | 29,634,183 | 0.00 | 892,880,233 | 0.0 |
| `sales_tax_alloc_per_capita` | 13,556 | 277 | 186 | 444 | 0.00 | 10,908 | 2.7 |
| `sales_tax_alloc_real2024` | 13,930 | 6,525,292 | 453,392 | 34,867,811 | 0.00 | 919,215,192 | 0.0 |
| `sales_tax_alloc_per_capita_real2024` | 13,556 | 327 | 226 | 514 | 0.00 | 12,306 | 2.7 |
| `taxable_sales` | 10,185 | 715,260,722 | 33,057,331 | 5,469,363,149 | 0.00 | 176,329,806,398 | 26.9 |
| `taxable_sales_per_capita` | 9,965 | 26,235 | 15,672 | 51,071 | 0.00 | 1,333,056 | 28.5 |
| `business_outlets` | 10,185 | 1,215 | 172 | 7,146 | 0.00 | 204,181 | 26.9 |
| `sales_tax_rate` | 13,930 | 1.50 | 1.50 | 0.38 | 0.25 | 2.00 | 0.0 |

### Cross-section — 1,202 cities (2022)

| Variable | N | Mean | Median | SD | Min | Max | Miss % |
|---|--:|--:|--:|--:|--:|--:|--:|
| `population` | 1,202 | 17,951 | 1,996 | 103,974 | 17.00 | 2,316,120 | 0.0 |
| `property_tax` | 1,202 | 10,126,994 | 776,000 | 71,589,100 | 0.00 | 1,600,416,000 | 0.0 |
| `total_taxes` | 1,202 | 18,629,405 | 1,559,000 | 121,032,274 | 0.00 | 2,865,310,000 | 0.0 |
| `tax_per_capita` | 1,202 | 1,441 | 580 | 4,286 | 0.00 | 45,058 | 0.0 |
| `total_debt_os` | 1,202 | 70,346,737 | 754,000 | 669,647,368 | 0.00 | 13,110,985,000 | 0.0 |
| `debt_per_capita` | 1,202 | 1,285 | 514 | 2,244 | 0.00 | 45,153 | 0.0 |
| `sales_tax_rate` | 1,142 | 1.53 | 1.50 | 0.38 | 0.25 | 2.00 | 5.0 |
| `taxable_sales` | 1,113 | 850,681,910 | 42,284,512 | 6,251,606,120 | 0.00 | 166,330,315,878 | 7.4 |
| `sales_tax_alloc_2019` | 1,139 | 5,436,515 | 385,415 | 28,713,041 | 0.00 | 698,992,968 | 5.2 |
| `sales_tax_alloc_2023` | 1,139 | 7,459,625 | 553,017 | 37,755,001 | 1,371 | 892,880,233 | 5.2 |
| `salestax_growth_19_23_pct` | 1,130 | 55.92 | 44.45 | 82.45 | -72.60 | 1,781 | 6.0 |

The same tables ship as a **Summary** worksheet inside each `.xlsx`, alongside a **Codebook** worksheet of these definitions.

---
Built `2026-06-01`. Rebuild: `python3 build_panel.py` (primary) and `python3 build_dataset.py` (supplement). Each auto-downloads its source files (Census finance zip + OMB CBSA file) to `_raw/`.
