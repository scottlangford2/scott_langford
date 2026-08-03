#!/usr/bin/env python3
"""Build TX_City_Sales_Panel_2013_2024.{csv,xlsx} — annual city-year panel (PRIMARY spine).

Long format, one row per city-year (2013-2024), all Texas cities.
Sources (all free, no API key):
  - TX Comptroller data.texas.gov: vfba-b57j (annual sales-tax allocation),
    7z4d-yf2c (taxable sales + business outlets, 2016+), 53pa-m7sm (sales-tax rate)
  - Census 2022 Census of Governments directory (county, county FIPS, 2022 reference population)
  - OMB/Census CBSA delineation (metro/micropolitan classification)
  - BLS CPI-U annual averages (constant-2024-dollar columns)
Run from Datasets/:  python3 build_panel.py
Requires: pandas, requests, openpyxl. Downloads source files to _raw/ on first run.
"""
import io, os, re, zipfile, requests, pandas as pd

UA = {"User-Agent": "Mozilla/5.0"}
YEARS = (2013, 2024)
RAW = "_raw"
COG_ZIP, COG_URL = f"{RAW}/cog2022.zip", "https://www2.census.gov/programs-surveys/gov-finances/tables/2022/2022_Individual_Unit_File.zip"
CBSA_XLSX, CBSA_URL = f"{RAW}/cbsa_list1_2023.xlsx", "https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx"

# BLS CPI-U, U.S. city average, all items, annual average (1982-84=100)
CPI = {2013: 232.957, 2014: 236.736, 2015: 237.017, 2016: 240.007, 2017: 245.120, 2018: 251.107,
       2019: 255.657, 2020: 258.811, 2021: 270.970, 2022: 292.655, 2023: 304.702, 2024: 313.689}
CPI_BASE = CPI[2024]

def matchkey(s):
    """Robust city-name join key: drop county qualifiers, SAINT->ST, strip non-alphanumerics."""
    s = re.sub(r"\([^)]*\)", "", str(s).upper()).replace("SAINT", "ST")
    return re.sub(r"[^A-Z0-9]", "", s)

def fetch(path, url):
    os.makedirs(RAW, exist_ok=True)
    if not os.path.exists(path):
        open(path, "wb").write(requests.get(url, headers=UA, timeout=300).content)

def soql(rid, params):
    r = requests.get(f"https://data.texas.gov/resource/{rid}.csv", params=params, headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

def clean_city(n):
    n = n.strip()
    for suf in (" CITY", " TOWN", " VILLAGE"):
        if n.endswith(suf):
            return n[:-len(suf)].strip()
    return n

def cbsa_map():
    fetch(CBSA_XLSX, CBSA_URL)
    d = pd.read_excel(CBSA_XLSX, header=2, dtype=str)
    d = d[d["FIPS State Code"] == "48"]
    short = {"Metropolitan Statistical Area": "Metropolitan", "Micropolitan Statistical Area": "Micropolitan"}
    return {r["FIPS County Code"]: short.get(r["Metropolitan/Micropolitan Statistical Area"], "Neither")
            for _, r in d.iterrows()}

VARDEFS = [
    ("city", "City name", "—", "Comptroller"),
    ("county", "County", "—", "Census; time-invariant"),
    ("metro_status", "Metro (Metropolitan Statistical Area) vs. Non-Metro", "category", "OMB/Census CBSA 2023; time-invariant"),
    ("cbsa_type", "Metropolitan / Micropolitan / Neither", "category", "OMB/Census CBSA 2023; time-invariant"),
    ("population_2022_ref", "2022 reference population (fixed across years)", "persons", "Census 2022; denominator only"),
    ("year", "Calendar year", "2013-2024", ""),
    ("sales_tax_alloc", "Sales-tax allocation payments (nominal)", "$/yr", "Comptroller; 2013-2024"),
    ("sales_tax_alloc_per_capita", "alloc / 2022 ref population (nominal)", "$", "derived"),
    ("sales_tax_alloc_real2024", "Sales-tax allocation in constant 2024 dollars", "$/yr", "derived; CPI-U deflated"),
    ("sales_tax_alloc_per_capita_real2024", "Real (2024$) allocation per capita", "$", "derived"),
    ("taxable_sales", "Total taxable sales (nominal)", "$/yr", "Comptroller; 2016+ only"),
    ("taxable_sales_per_capita", "taxable_sales / 2022 ref population", "$", "derived; 2016+"),
    ("business_outlets", "Avg. active business outlets (quarterly mean)", "count", "Comptroller; 2016+"),
    ("sales_tax_rate", "Local sales-tax rate", "percent", "Comptroller"),
]

def write_xlsx(df, path, sheet):
    cb = pd.DataFrame(VARDEFS, columns=["Variable", "Description", "Units", "Source"])
    num = df.select_dtypes("number").drop(columns=["year"], errors="ignore")
    summ = num.describe().T
    summ["missing_%"] = (df[num.columns].isna().mean() * 100).round(1)
    summ = summ.round(2).reset_index().rename(columns={"index": "Variable"})
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        df.to_excel(xl, index=False, sheet_name=sheet)
        cb.to_excel(xl, index=False, sheet_name="Codebook")
        summ.to_excel(xl, index=False, sheet_name="Summary (all years)")

# ---- 1. Annual sales-tax allocation (backbone) ----
alloc = soql("vfba-b57j", {"$select": "city,report_year,sum(net_payment_this_period) as sales_tax_alloc",
             "$where": f"report_year>={YEARS[0]} and report_year<={YEARS[1]}", "$group": "city,report_year", "$limit": 50000})
alloc = alloc.rename(columns={"report_year": "year"})
alloc["key"] = alloc["city"].map(matchkey)

# ---- 2. Taxable sales (annual sum) + outlets (avg of quarterly totals), 2016+ ----
q = soql("7z4d-yf2c", {"$select": "name,year,qtr,sum(taxable) as q_taxable,sum(outlets) as q_outlets",
         "$where": f"type='City' and year>=2016 and year<={YEARS[1]}", "$group": "name,year,qtr", "$limit": 50000})
ts = q.groupby(["name", "year"]).agg(taxable_sales=("q_taxable", "sum"), business_outlets=("q_outlets", "mean")).reset_index()
ts["business_outlets"] = ts["business_outlets"].round().astype("Int64")
ts["key"] = ts["name"].map(matchkey)
ts = ts.drop(columns=["name"]).drop_duplicates(["key", "year"])  # avoid merge fan-out on shared keys

# ---- 3. Sales-tax rate per city-year ----
rate = soql("53pa-m7sm", {"$select": "city,report_year,max(current_rate) as sales_tax_rate",
            "$where": f"report_year>={YEARS[0]} and report_year<={YEARS[1]}", "$group": "city,report_year", "$limit": 50000})
rate = rate.rename(columns={"report_year": "year"})
rate["key"] = rate["city"].map(matchkey)
rate = rate.drop(columns=["city"]).drop_duplicates(["key", "year"])  # avoid merge fan-out on shared keys

# ---- 4. Time-invariant attributes (Census directory + CBSA) ----
fetch(COG_ZIP, COG_URL)
with zipfile.ZipFile(COG_ZIP) as z:
    pid_lines = z.read([n for n in z.namelist() if "PID" in n][0]).decode("latin-1").splitlines()
CB = cbsa_map()
rows = []
for ln in pid_lines:
    gid = ln[0:12]
    if gid[0:2] != "48" or gid[2:3] != "2":
        continue
    cfips3 = gid[3:6]
    rows.append((clean_city(ln[12:76]), ln[76:111].strip().title(),
                 pd.to_numeric(ln[116:125].strip(), errors="coerce"), CB.get(cfips3, "Neither")))
attr = pd.DataFrame(rows, columns=["city", "county", "population_2022_ref", "cbsa_type"])
attr["metro_status"] = attr["cbsa_type"].map(lambda t: "Metro" if t == "Metropolitan" else "Non-Metro")
attr["key"] = attr["city"].map(matchkey)
attr = attr.drop(columns=["city"]).drop_duplicates("key")

# ---- 5. Assemble long panel ----
p = (alloc.merge(ts, on=["key", "year"], how="left").merge(rate, on=["key", "year"], how="left").merge(attr, on="key", how="left"))
p["sales_tax_alloc_per_capita"] = p["sales_tax_alloc"] / p["population_2022_ref"]
p["taxable_sales_per_capita"] = p["taxable_sales"] / p["population_2022_ref"]
defl = p["year"].map(CPI).rdiv(CPI_BASE)  # CPI_BASE / CPI[year]
p["sales_tax_alloc_real2024"] = p["sales_tax_alloc"] * defl
p["sales_tax_alloc_per_capita_real2024"] = p["sales_tax_alloc_per_capita"] * defl

# round dollar columns to whole dollars; rate to 2 dp
for c in ["sales_tax_alloc", "sales_tax_alloc_per_capita", "sales_tax_alloc_real2024",
          "sales_tax_alloc_per_capita_real2024", "taxable_sales", "taxable_sales_per_capita"]:
    p[c] = p[c].round(0)
p["sales_tax_rate"] = p["sales_tax_rate"].round(2)

cols = [v[0] for v in VARDEFS]
p = p[cols].sort_values(["city", "year"]).reset_index(drop=True)
p.to_csv("TX_City_Sales_Panel_2013_2024.csv", index=False)
write_xlsx(p, "TX_City_Sales_Panel_2013_2024.xlsx", "Panel")
matched = p["metro_status"].notna().mean() * 100
print(f"Built panel: {len(p)} city-year rows, {p['city'].nunique()} cities, years {p['year'].min()}-{p['year'].max()}, {len(cols)} cols.")
print(f"metro/attr match: {matched:.1f}% | metro split:", p.drop_duplicates('city')['metro_status'].value_counts(dropna=False).to_dict())
