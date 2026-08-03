#!/usr/bin/env python3
"""Rebuild TX_City_Finance_2022.{csv,xlsx} — the PA 3311 / PS 3315 debt cross-section.

One row per Texas city (2022). Adds debt + property/total taxes that aren't available annually.
Sources (all free, no API key):
  - Census 2022 Census of Governments, Individual Unit File (population, taxes, debt)
  - Texas Comptroller data.texas.gov: vfba-b57j, 53pa-m7sm, 7z4d-yf2c
  - OMB/Census CBSA delineation (metro/micropolitan classification)
Run from Datasets/:  python3 build_dataset.py
Requires: pandas, requests, openpyxl. Downloads source files to _raw/ on first run.
"""
import io, os, re, zipfile, requests, pandas as pd

UA = {"User-Agent": "Mozilla/5.0"}
RAW = "_raw"
COG_ZIP, COG_URL = f"{RAW}/cog2022.zip", "https://www2.census.gov/programs-surveys/gov-finances/tables/2022/2022_Individual_Unit_File.zip"
CBSA_XLSX, CBSA_URL = f"{RAW}/cbsa_list1_2023.xlsx", "https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx"

def matchkey(s):
    """Robust city-name join key: drop county qualifiers, SAINT->ST, strip non-alphanumerics."""
    s = re.sub(r"\([^)]*\)", "", str(s).upper()).replace("SAINT", "ST")
    return re.sub(r"[^A-Z0-9]", "", s)

def fetch(path, url):
    os.makedirs(RAW, exist_ok=True)
    if not os.path.exists(path):
        open(path, "wb").write(requests.get(url, headers=UA, timeout=300).content)

def soql(rid, params):
    r = requests.get(f"https://data.texas.gov/resource/{rid}.csv", params=params, headers=UA, timeout=180)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

def clean_city(n):
    n = n.strip()
    for suf in (" CITY", " TOWN", " VILLAGE"):
        if n.endswith(suf):
            return n[:-len(suf)].strip()
    return n

def cbsa_map():
    """county FIPS (3-digit, TX) -> 'Metropolitan'/'Micropolitan' (else 'Neither')."""
    fetch(CBSA_XLSX, CBSA_URL)
    d = pd.read_excel(CBSA_XLSX, header=2, dtype=str)
    d = d[d["FIPS State Code"] == "48"]
    short = {"Metropolitan Statistical Area": "Metropolitan", "Micropolitan Statistical Area": "Micropolitan"}
    return {r["FIPS County Code"]: short.get(r["Metropolitan/Micropolitan Statistical Area"], "Neither")
            for _, r in d.iterrows()}

VARDEFS = [
    ("city", "City name", "—", "Census"),
    ("county", "County", "—", "Census"),
    ("county_fips", "5-digit county FIPS code", "—", "from Census ID"),
    ("place_fips", "5-digit Census place FIPS code", "—", "Census"),
    ("metro_status", "Metro (in a Metropolitan Statistical Area) vs. Non-Metro", "category", "OMB/Census CBSA 2023"),
    ("cbsa_type", "Metropolitan / Micropolitan / Neither", "category", "OMB/Census CBSA 2023"),
    ("population", "Population", "persons", "Census directory (2020-based)"),
    ("property_tax", "Property tax revenue (item T01)", "$", "Census"),
    ("gen_sales_tax", "General sales tax revenue (item T09)", "$", "Census"),
    ("total_taxes", "All tax revenue (sum of T-codes)", "$", "Census"),
    ("tax_per_capita", "total_taxes / population", "$", "derived"),
    ("lt_debt_os", "Long-term debt outstanding, end of FY (item 49U)", "$", "Census"),
    ("st_debt_os", "Short-term debt outstanding, end of FY (item 64V)", "$", "Census"),
    ("total_debt_os", "Total debt outstanding (lt + st)", "$", "derived"),
    ("debt_per_capita", "total_debt_os / population", "$", "derived"),
    ("sales_tax_rate", "Local sales-tax rate", "percent", "Comptroller"),
    ("taxable_sales", "Total taxable sales, 2022", "$", "Comptroller"),
    ("taxable_sales_per_capita", "taxable_sales / population", "$", "derived"),
    ("business_outlets", "Number of business outlets, 2022", "count", "Comptroller"),
    ("sales_tax_alloc_2019", "Sales-tax allocation payments, 2019", "$", "Comptroller"),
    ("sales_tax_alloc_2023", "Sales-tax allocation payments, 2023", "$", "Comptroller"),
    ("salestax_growth_19_23_pct", "% change in allocation, 2019->2023", "percent", "derived"),
]

def write_xlsx(df, path, sheet, title):
    cb = pd.DataFrame(VARDEFS, columns=["Variable", "Description", "Units", "Source"])
    num = df.select_dtypes("number")
    summ = num.describe().T
    summ["missing_%"] = (df[num.columns].isna().mean() * 100).round(1)
    summ = summ.round(2).reset_index().rename(columns={"index": "Variable"})
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        df.to_excel(xl, index=False, sheet_name=sheet)
        cb.to_excel(xl, index=False, sheet_name="Codebook")
        summ.to_excel(xl, index=False, sheet_name="Summary")

# ---- Census finance (parse fixed-width from zip) ----
fetch(COG_ZIP, COG_URL)
with zipfile.ZipFile(COG_ZIP) as z:
    pid_lines = z.read([n for n in z.namelist() if "PID" in n][0]).decode("latin-1").splitlines()
    dat_lines = z.read([n for n in z.namelist() if "DAT" in n][0]).decode("latin-1").splitlines()

CB = cbsa_map()
rows = []
for ln in pid_lines:
    gid = ln[0:12]
    if gid[0:2] != "48" or gid[2:3] != "2":   # Texas, City
        continue
    cfips3 = gid[3:6]
    rows.append((gid, clean_city(ln[12:76]), ln[76:111].strip().title(), "48" + cfips3,
                 ln[111:116].strip(), ln[116:125].strip(), CB.get(cfips3, "Neither")))
pid = pd.DataFrame(rows, columns=["gid", "city", "county", "county_fips", "place_fips", "population", "cbsa_type"])
pid["population"] = pd.to_numeric(pid["population"], errors="coerce")
pid["metro_status"] = pid["cbsa_type"].map(lambda t: "Metro" if t == "Metropolitan" else "Non-Metro")
tx = set(pid["gid"])

from collections import defaultdict
items = defaultdict(dict)
for ln in dat_lines:
    gid = ln[0:12]
    if gid not in tx:
        continue
    try:
        items[gid][ln[12:15]] = float(ln[15:27].strip()) * 1000.0
    except ValueError:
        pass
fin = []
for gid in pid["gid"]:
    d = items.get(gid, {})
    ltd, std = d.get("49U", 0.0), d.get("64V", 0.0)
    fin.append((gid, d.get("T01", 0.0), d.get("T09", 0.0),
                sum(v for c, v in d.items() if c.startswith("T")), ltd, std, ltd + std))
fin = pd.DataFrame(fin, columns=["gid", "property_tax", "gen_sales_tax", "total_taxes", "lt_debt_os", "st_debt_os", "total_debt_os"])
df = pid.merge(fin, on="gid")
df = df[df["population"] > 0].copy()
df["key"] = df["city"].map(matchkey)

# ---- Comptroller ----
alloc = []
for yr in (2019, 2023):
    a = soql("vfba-b57j", {"$select": "city,sum(net_payment_this_period) as v", "$where": f"report_year={yr}", "$group": "city", "$limit": 5000})
    alloc.append(a.rename(columns={"v": f"sales_tax_alloc_{yr}"}))
alloc = alloc[0].merge(alloc[1], on="city", how="outer")
alloc["key"] = alloc["city"].map(matchkey)
alloc = alloc.drop(columns=["city"]).groupby("key", as_index=False).sum(numeric_only=True)
rate = soql("53pa-m7sm", {"$select": "city,current_rate", "$where": "report_year=2024", "$group": "city,current_rate", "$limit": 6000})
rate["key"] = rate["city"].map(matchkey)
rate = rate.drop_duplicates("key")[["key", "current_rate"]].rename(columns={"current_rate": "sales_tax_rate"})
ts = soql("7z4d-yf2c", {"$select": "name,sum(taxable) as taxable_sales,sum(outlets) as business_outlets", "$where": "type='City' AND year=2022", "$group": "name", "$limit": 6000})
ts["key"] = ts["name"].map(matchkey)
ts = ts.drop(columns=["name"]).groupby("key", as_index=False).sum(numeric_only=True)

m = df.merge(alloc, on="key", how="left").merge(rate, on="key", how="left").merge(ts, on="key", how="left")
m["tax_per_capita"] = m["total_taxes"] / m["population"]
m["debt_per_capita"] = m["total_debt_os"] / m["population"]
m["taxable_sales_per_capita"] = m["taxable_sales"] / m["population"]
denom = m["sales_tax_alloc_2019"].where(m["sales_tax_alloc_2019"] > 0)  # avoid divide-by-zero -> NaN
m["salestax_growth_19_23_pct"] = (m["sales_tax_alloc_2023"] - denom) / denom * 100

for c in ["property_tax","gen_sales_tax","total_taxes","tax_per_capita","lt_debt_os","st_debt_os",
          "total_debt_os","debt_per_capita","taxable_sales","taxable_sales_per_capita",
          "sales_tax_alloc_2019","sales_tax_alloc_2023"]:
    m[c] = m[c].round(0)
m["sales_tax_rate"] = m["sales_tax_rate"].round(2)
m["salestax_growth_19_23_pct"] = m["salestax_growth_19_23_pct"].round(1)
cols = [v[0] for v in VARDEFS]
m = m[cols].sort_values("population", ascending=False).reset_index(drop=True)
m.to_csv("TX_City_Finance_2022.csv", index=False)
write_xlsx(m, "TX_City_Finance_2022.xlsx", "TX Cities", "TX City Finance 2022")
print(f"Built TX_City_Finance_2022.{{csv,xlsx}} — {len(m)} cities, {len(cols)} variables.")
print("metro:", m["metro_status"].value_counts().to_dict(), "| cbsa:", m["cbsa_type"].value_counts().to_dict())
