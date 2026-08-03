#!/usr/bin/env python3
"""
add_edc.py  -- operationalize Case A (economic-development sales tax).

Adds, to BOTH city datasets, an indicator of whether a city operates a Type A
and/or Type B economic-development corporation (EDC) sales tax, plus a
(left-censored) first-report-year proxy:

  has_edc                : 1 if the city ever filed a Type A or Type B EDC report, else 0
  edc_type               : 'A', 'B', 'A&B', or '' (none)
  edc_first_report_year  : earliest fiscal year the city appears in the EDC
                           report data (PROXY for adoption; see CAVEAT)

SOURCE
------
Texas Comptroller, Economic Development Corporation Report Data ("EDC data big
table"), data.texas.gov resource d4dd-rd43 (annual EDC reports, FY 1997-present):
  https://data.texas.gov/dataset/EDC-data-big-table/d4dd-rd43
Program authority: Development Corporation Act (1979); Section 4A / Type A sales
tax authorized 1989; Section 4B / Type B authorized 1991
  https://comptroller.texas.gov/economy/development/sales-tax/edc/

CAVEAT (read before using the year)
-----------------------------------
EDC annual reporting was only mandated starting FY1997, so `edc_first_report_year`
is LEFT-CENSORED at 1997: a city that adopted its tax in 1989-1996 shows 1997.
By July 1998, 384 Texas cities had already adopted an economic-development sales
tax (TEDC). Therefore:
  * Use `has_edc` / `edc_type` as a CROSS-SECTIONAL treatment (EDC vs. non-EDC
    cities) for group comparisons and regression.
  * Do NOT treat `edc_first_report_year` as a clean adoption date for a panel
    difference-in-differences: most adoption predates this 2013-2024 panel and/or
    the 1997 reporting floor. Only ~46 cities first report in 2013+ (a thin,
    selected set). A credible adoption-date DiD would require an open-records
    request to the Comptroller for per-jurisdiction tax effective dates.
"""
import pandas as pd, re, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "_raw_city"); os.makedirs(RAW, exist_ok=True)
EDC_CSV = os.path.join(RAW, "edc_big_table_d4dd-rd43.csv")
EDC_URL = "https://data.texas.gov/api/views/d4dd-rd43/rows.csv?accessType=DOWNLOAD"
PANEL = os.path.join(HERE, "TX_City_Sales_Panel_2013_2024.csv")
CROSS = os.path.join(HERE, "TX_City_Finance_2022.csv")

def norm(s):
    if pd.isna(s): return ""
    s = str(s).upper().strip()
    s = re.sub(r"\.", "", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\bSAINT\b", "ST", s)
    return s

def fetch():
    if not os.path.exists(EDC_CSV):
        req = urllib.request.Request(EDC_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(EDC_CSV, "wb") as f:
            f.write(r.read())
    return pd.read_csv(EDC_CSV, dtype=str)

def city_edc_table():
    e = fetch()
    e["Fiscal Year"] = pd.to_numeric(e["Fiscal Year"], errors="coerce")
    e["cnorm"] = e["EDC City"].map(norm)
    e = e[e.cnorm != ""]
    def typ(s):
        a = any("A" in t for t in s); b = any("B" in t for t in s)
        return "A&B" if (a and b) else "A" if a else "B" if b else ""
    g = e.groupby("cnorm").agg(
        edc_type=("EDC Type Code", lambda x: typ([t for t in x.dropna()])),
        edc_first_report_year=("Fiscal Year", "min"),
    )
    g["edc_first_report_year"] = g["edc_first_report_year"].astype("Int64")
    return g

def apply_to(path, city_col, g):
    d = pd.read_csv(path)
    key = d[city_col].map(norm)
    d["has_edc"] = key.isin(g.index).astype(int)
    d["edc_type"] = key.map(g["edc_type"]).fillna("")
    d["edc_first_report_year"] = key.map(g["edc_first_report_year"]).astype("Int64")
    d.to_csv(path, index=False)
    return d, key

def main():
    g = city_edc_table()
    g.reset_index().rename(columns={"cnorm": "city_norm"}).to_csv(
        os.path.join(HERE, "city_edc.csv"), index=False)
    dp, kp = apply_to(PANEL, "city", g)
    dc, kc = apply_to(CROSS, "city", g)
    np_cities = dp.drop_duplicates("city")
    print("EDC table: %d cities (Type A and/or B), FY1997-2024." % len(g))
    print("PANEL  (%s): %d/%d cities have an EDC; types: %s"
          % (os.path.basename(PANEL), np_cities.has_edc.sum(),
             np_cities.city.nunique(), np_cities.edc_type.value_counts().to_dict()))
    print("CROSS  (%s): %d/%d cities have an EDC"
          % (os.path.basename(CROSS), dc.has_edc.sum(), len(dc)))
    print("first_report_year >= 2013 (within panel): %d cities (left-censored proxy)"
          % (g.edc_first_report_year >= 2013).sum())
    print("Wrote city_edc.csv; added has_edc / edc_type / edc_first_report_year to both files.")

if __name__ == "__main__":
    main()
