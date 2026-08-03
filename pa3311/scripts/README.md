# Dataset build scripts — PA 3311 / PS 3315

Reproducible code that generates the course datasets in [`../data/`](../data).

| Script | Output | Description |
|---|---|---|
| `build_panel.py` | `TX_City_Sales_Panel_2013_2024.csv` / `.xlsx` | **Primary spine.** Annual city-year panel (1,180 Texas cities × 2013–2024): sales-tax allocation, taxable sales, business outlets, sales-tax rate, plus time-invariant county / metro flag / 2022 reference population. |
| `build_dataset.py` | `TX_City_Finance_2022.csv` / `.xlsx` | Cross-section supplement (one row per city, 2022) that **adds debt and property/total taxes** from the Census of Governments. |

See [`../data/CODEBOOK.md`](../data/CODEBOOK.md) for full variable definitions, sources, and the module-by-module usage map.

## Data sources (all free, no API key)
- **Texas Comptroller** open data (`data.texas.gov`): sales-tax allocation (`vfba-b57j`), quarterly taxable sales + outlets (`7z4d-yf2c`), city–county rate (`53pa-m7sm`).
- **U.S. Census Bureau, 2022 Census of Governments** — Survey of Local Government Finances individual unit file (full enumeration; downloaded automatically to `_raw/`).

## Run
```bash
pip install pandas requests openpyxl
cd scripts
python3 build_panel.py     # builds the panel
python3 build_dataset.py   # builds the 2022 cross-section (with debt)
python3 validate.py        # 19 integrity checks on both outputs (exit 0 = all pass)
```

Data provenance and licensing: see [`../data/DATA_SOURCES.md`](../data/DATA_SOURCES.md).
Each script downloads the Census file to `scripts/_raw/` on first run and writes its CSV/XLSX to the current directory. The canonical copies committed to the repo live in [`../data/`](../data); local rebuild outputs are git-ignored.
