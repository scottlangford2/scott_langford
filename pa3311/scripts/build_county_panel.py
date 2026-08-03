#!/usr/bin/env python3
"""
build_county_panel.py
=====================================================================
Build a Texas COUNTY x PRESIDENTIAL-YEAR panel.

Unit of observation : Texas county (254) x presidential election year
Years               : 2000, 2004, 2008, 2012, 2016, 2020, 2024
Join key            : 5-digit county FIPS as zero-padded string ("48xxx")

Reproducible build from local raw files in ./_raw_county/ (plus the
CBSA crosswalk in ./_raw/). No values are ever fabricated: when a
variable cannot be cleanly constructed for a given year it is left
blank (NaN) and documented in CODEBOOK_county_panel.md.

Outputs:
  - TX_County_Political_Panel_2000_2024.csv
  - TX_County_Political_Panel_2000_2024.xlsx (Data + Codebook + Summary)
  - CODEBOOK_county_panel.md  (written separately)

Author: built for PA 3311 / PS 3315 / PA 5312 course datasets.
"""

import os
import zipfile
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "_raw_county")
RAW2 = os.path.join(BASE, "_raw")

# --- Auto-download raw sources if missing (one-command reproducible from scratch) ---
import urllib.request
_C = "https://www2.census.gov/programs-surveys/popest/datasets"
_SOURCES = {
    os.path.join(RAW, "medsl_2000_2016.csv"): "https://raw.githubusercontent.com/MEDSL/county-returns/master/countypres_2000-2016.csv",
    os.path.join(RAW, "tonmcg_2020.csv"): "https://raw.githubusercontent.com/tonmcg/US_County_Level_Election_Results_08-24/master/2020_US_County_Level_Presidential_Results.csv",
    os.path.join(RAW, "tonmcg_2024.csv"): "https://raw.githubusercontent.com/tonmcg/US_County_Level_Election_Results_08-24/master/2024_US_County_Level_Presidential_Results.csv",
    os.path.join(RAW, "pep_alldata_2020_2024_tx.csv"): f"{_C}/2020-2024/counties/asrh/cc-est2024-alldata-48.csv",
    os.path.join(RAW, "pep_alldata_2010_2020_tx.csv"): f"{_C}/2010-2020/counties/asrh/CC-EST2020-ALLDATA-48.csv",
    os.path.join(RAW, "pep_sexracehisp_2000_2010.csv"): f"{_C}/2000-2010/intercensal/county/co-est00int-sexracehisp.csv",
    os.path.join(RAW, "pep_agesex_2020_2024_tx.csv"): f"{_C}/2020-2024/counties/asrh/cc-est2024-agesex-48.csv",
    os.path.join(RAW, "pep_agesex_2010_2020_tx.csv"): f"{_C}/2010-2020/counties/asrh/CC-EST2020-AGESEX-48.csv",
    os.path.join(RAW, "ers_income_unemp.csv"): "https://www.ers.usda.gov/media/5497/unemployment-and-median-household-income-for-the-united-states-states-and-counties-2000-23.csv",
    os.path.join(RAW, "ers_education.csv"): "https://www.ers.usda.gov/media/5495/educational-attainment-for-adults-age-25-and-older-for-the-united-states-states-and-counties-1970-2023.csv",
    os.path.join(RAW, "ers_poverty.csv"): "https://www.ers.usda.gov/media/5496/poverty-estimates-for-the-united-states-states-and-counties-2023.csv",
    os.path.join(RAW, "gaz.zip"): "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_counties_national.zip",
    os.path.join(RAW2, "cbsa_list1_2023.xlsx"): "https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx",
}
def _ensure_raw():
    os.makedirs(RAW, exist_ok=True); os.makedirs(RAW2, exist_ok=True)
    for path, url in _SOURCES.items():
        if not os.path.exists(path):
            print("  downloading", os.path.basename(path), "...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=300) as r, open(path, "wb") as f:
                f.write(r.read())
_ensure_raw()

ELECTION_YEARS = [2000, 2004, 2008, 2012, 2016, 2020, 2024]

CSV_OUT = os.path.join(BASE, "TX_County_Political_Panel_2000_2024.csv")
XLSX_OUT = os.path.join(BASE, "TX_County_Political_Panel_2000_2024.xlsx")

FINAL_COLS = [
    "fips", "county", "year", "metro_status", "cbsa_type",
    "population", "voting_age_pop", "total_votes", "rep_votes", "dem_votes",
    "rep_two_party_share", "margin_rep", "turnout_vap",
    "pct_hispanic", "pct_black", "pct_white_nh", "median_age", "pop_density",
    "median_household_income", "unemployment_rate", "pct_bachelors_plus",
    "poverty_rate",
]


def fips5(x):
    """Coerce any FIPS-like value to a 5-digit zero-padded string, or NaN."""
    if pd.isna(x):
        return np.nan
    try:
        return str(int(float(x))).zfill(5)
    except (ValueError, TypeError):
        s = str(x).strip()
        return s.zfill(5) if s.isdigit() else np.nan


# ===========================================================================
# 1. SCAFFOLD  (254 TX counties x 7 years)
#    The authoritative county list comes from the Census PEP files (which
#    carry the canonical county names); we build the frame after loading.
# ===========================================================================

# ===========================================================================
# 2. POLITICAL  (votes)
# ===========================================================================
def load_political():
    """Return tidy (fips, year, total_votes, rep_votes, dem_votes)."""
    # --- MIT Election Lab, 2000-2016 (long) ---------------------------------
    med = pd.read_csv(
        os.path.join(RAW, "medsl_2000_2016.csv"),
        usecols=["year", "state", "office", "party",
                 "candidatevotes", "totalvotes", "FIPS"],
    )
    med = med[(med["state"] == "Texas") & (med["office"] == "President")].copy()
    med["fips"] = med["FIPS"].apply(fips5)

    rep = (med[med["party"] == "republican"]
           .groupby(["year", "fips"])["candidatevotes"].sum()
           .rename("rep_votes"))
    dem = (med[med["party"] == "democrat"]
           .groupby(["year", "fips"])["candidatevotes"].sum()
           .rename("dem_votes"))
    # totalvotes is constant within county-year; take max defensively
    tot = (med.groupby(["year", "fips"])["totalvotes"].max()
           .rename("total_votes"))
    med_out = pd.concat([rep, dem, tot], axis=1).reset_index()

    # --- tonmcg wide, 2020 & 2024 ------------------------------------------
    frames = [med_out]
    for yr, fn in [(2020, "tonmcg_2020.csv"), (2024, "tonmcg_2024.csv")]:
        t = pd.read_csv(os.path.join(RAW, fn), dtype={"county_fips": str})
        t = t[t["state_name"] == "Texas"].copy()
        t["fips"] = t["county_fips"].apply(fips5)
        t["year"] = yr
        t = t.rename(columns={"votes_gop": "rep_votes",
                              "votes_dem": "dem_votes"})
        frames.append(t[["year", "fips", "total_votes",
                         "rep_votes", "dem_votes"]])

    pol = pd.concat(frames, ignore_index=True)

    # Derived two-party measures
    tp = pol["rep_votes"] + pol["dem_votes"]
    pol["rep_two_party_share"] = np.where(tp > 0, pol["rep_votes"] / tp, np.nan)
    pol["dem_two_party_share"] = 1 - pol["rep_two_party_share"]
    pol["margin_rep"] = pol["rep_two_party_share"] - pol["dem_two_party_share"]
    return pol


# ===========================================================================
# 3. DEMOGRAPHICS  (population, race/Hispanic shares)
#    cc-est layout for 2010-2024; co-est2000 race-by-origin for 2000-2008.
# ===========================================================================
def _ccest_demo(path, year_code_map):
    """Parse a cc-est ALLDATA file (AGEGRP==0) into per-year demo shares."""
    cols = ["STATE", "COUNTY", "CTYNAME", "YEAR", "AGEGRP", "TOT_POP",
            "BA_MALE", "BA_FEMALE", "NHWA_MALE", "NHWA_FEMALE",
            "H_MALE", "H_FEMALE"]
    d = pd.read_csv(path, usecols=cols)
    d = d[d["AGEGRP"] == 0].copy()
    rows = []
    for elec_year, code in year_code_map.items():
        sub = d[d["YEAR"] == code].copy()
        sub["fips"] = (sub["STATE"].astype(int).astype(str).str.zfill(2)
                       + sub["COUNTY"].astype(int).astype(str).str.zfill(3))
        sub["year"] = elec_year
        sub["population"] = sub["TOT_POP"]
        sub["pct_hispanic"] = 100 * (sub["H_MALE"] + sub["H_FEMALE"]) / sub["TOT_POP"]
        sub["pct_black"] = 100 * (sub["BA_MALE"] + sub["BA_FEMALE"]) / sub["TOT_POP"]
        sub["pct_white_nh"] = 100 * (sub["NHWA_MALE"] + sub["NHWA_FEMALE"]) / sub["TOT_POP"]
        rows.append(sub[["fips", "year", "CTYNAME", "population",
                         "pct_hispanic", "pct_black", "pct_white_nh"]])
    return pd.concat(rows, ignore_index=True)


def _coest2000_demo(path, years):
    """
    Parse the co-est2000 race-by-origin national file (latin-1) for TX.
    Dimensions: SEX (0=both,1=M,2=F); ORIGIN (0=total,1=not-Hisp,2=Hisp);
    RACE (0=total, 1=White alone, 2=Black alone, 3=AIAN, 4=Asian, 5=NHPI, 6=2+).
    Population total      : SEX0, ORIGIN0, RACE0
    Hispanic              : SEX0, ORIGIN2, RACE0
    Black (alone, any orig): SEX0, ORIGIN0, RACE2
    White non-Hispanic    : SEX0, ORIGIN1, RACE1
    Yearly population columns: POPESTIMATE2000 ... POPESTIMATE2010.
    """
    d = pd.read_csv(path, encoding="latin-1")
    d = d[d["STATE"] == 48].copy()
    d["fips"] = (d["STATE"].astype(int).astype(str).str.zfill(2)
                 + d["COUNTY"].astype(int).astype(str).str.zfill(3))

    def slc(sex, origin, race):
        return d[(d["SEX"] == sex) & (d["ORIGIN"] == origin) & (d["RACE"] == race)]

    tot = slc(0, 0, 0).set_index("fips")
    his = slc(0, 2, 0).set_index("fips")
    blk = slc(0, 0, 2).set_index("fips")
    wnh = slc(0, 1, 1).set_index("fips")
    name = tot["CTYNAME"]

    rows = []
    for y in years:
        col = f"POPESTIMATE{y}"
        pop = tot[col]
        rec = pd.DataFrame({
            "fips": pop.index,
            "year": y,
            "CTYNAME": name.values,
            "population": pop.values,
            "pct_hispanic": 100 * his[col].reindex(pop.index).values / pop.values,
            "pct_black": 100 * blk[col].reindex(pop.index).values / pop.values,
            "pct_white_nh": 100 * wnh[col].reindex(pop.index).values / pop.values,
        })
        rows.append(rec)
    return pd.concat(rows, ignore_index=True)


def load_demographics():
    # 2020-2024 file: YEAR code 2->2020, 6->2024
    d2024 = _ccest_demo(
        os.path.join(RAW, "pep_alldata_2020_2024_tx.csv"),
        {2020: 2, 2024: 6})
    # 2010-2020 file: YEAR code 4->2012, 8->2016 (cc-est2020 coding)
    d2016 = _ccest_demo(
        os.path.join(RAW, "pep_alldata_2010_2020_tx.csv"),
        {2012: 4, 2016: 8})
    # 2000-2010 file: race-by-origin wide
    d2008 = _coest2000_demo(
        os.path.join(RAW, "pep_sexracehisp_2000_2010.csv"),
        [2000, 2004, 2008])
    return pd.concat([d2008, d2016, d2024], ignore_index=True)


# ===========================================================================
# 4. VOTING-AGE POPULATION + MEDIAN AGE
#    Clean 18+ only available for 2012,2016,2020,2024 (cc-est agesex).
#    The 2000-2010 agesex file uses 5-year bins that straddle 18, so a
#    clean 18+ cannot be derived -> left blank for 2000/2004/2008.
# ===========================================================================
def _agesex(path, year_code_map):
    cols = ["STATE", "COUNTY", "YEAR", "AGE18PLUS_TOT", "MEDIAN_AGE_TOT"]
    d = pd.read_csv(path, usecols=cols)
    rows = []
    for elec_year, code in year_code_map.items():
        sub = d[d["YEAR"] == code].copy()
        sub["fips"] = (sub["STATE"].astype(int).astype(str).str.zfill(2)
                       + sub["COUNTY"].astype(int).astype(str).str.zfill(3))
        sub["year"] = elec_year
        sub["voting_age_pop"] = sub["AGE18PLUS_TOT"]
        sub["median_age"] = sub["MEDIAN_AGE_TOT"]
        rows.append(sub[["fips", "year", "voting_age_pop", "median_age"]])
    return pd.concat(rows, ignore_index=True)


def load_agesex():
    a2024 = _agesex(os.path.join(RAW, "pep_agesex_2020_2024_tx.csv"),
                    {2020: 2, 2024: 6})
    a2016 = _agesex(os.path.join(RAW, "pep_agesex_2010_2020_tx.csv"),
                    {2012: 4, 2016: 8})
    # 2000/2004/2008: voting_age_pop intentionally left blank (see codebook).
    return pd.concat([a2016, a2024], ignore_index=True)


# ===========================================================================
# 5. GEOGRAPHY  (land area for density)  +  CBSA metro status
# ===========================================================================
def load_land():
    zpath = os.path.join(RAW, "gaz.zip")
    with zipfile.ZipFile(zpath) as z:
        member = "2023_Gaz_counties_national.txt"
        with z.open(member) as fh:
            g = pd.read_csv(fh, sep="\t", dtype=str, encoding="latin-1")
    g.columns = [c.strip() for c in g.columns]
    g["fips"] = g["GEOID"].apply(fips5)
    g = g[g["GEOID"].str.startswith("48")].copy()
    g["aland_sqmi"] = pd.to_numeric(g["ALAND_SQMI"], errors="coerce")
    return g[["fips", "aland_sqmi"]]


def load_cbsa():
    df = pd.read_excel(os.path.join(RAW2, "cbsa_list1_2023.xlsx"), header=2)
    df = df[pd.to_numeric(df["FIPS State Code"], errors="coerce") == 48].copy()
    df["fips"] = ("48" + pd.to_numeric(df["FIPS County Code"])
                  .astype(int).astype(str).str.zfill(3))
    mm = df["Metropolitan/Micropolitan Statistical Area"].fillna("")
    df["metro_status"] = np.where(mm.str.contains("Metropolitan"),
                                  "Metro", "Non-Metro")
    df["cbsa_type"] = np.where(
        mm.str.contains("Metropolitan"), "Metropolitan",
        np.where(mm.str.contains("Micropolitan"), "Micropolitan", "Neither"))
    return df[["fips", "metro_status", "cbsa_type"]].drop_duplicates("fips")


# ===========================================================================
# 6. SOCIOECONOMIC  (USDA ERS, long Attribute/Value)
# ===========================================================================
def _ers_year_series(path, fips_col, prefix, encoding="latin-1"):
    """Return dict[year:int] -> Series(fips -> value) for Attribute == prefix_YYYY."""
    d = pd.read_csv(path, dtype=str, encoding=encoding)
    d = d.rename(columns={fips_col: "FIPS_Code"})
    d = d[d["FIPS_Code"].str.startswith("48", na=False)].copy()
    d["fips"] = d["FIPS_Code"].apply(fips5)
    out = {}
    for attr, grp in d.groupby("Attribute"):
        if attr.startswith(prefix):
            tail = attr[len(prefix):]
            if tail.isdigit() and len(tail) == 4:
                yr = int(tail)
                vals = pd.to_numeric(grp["Value"].str.replace(",", "", regex=False),
                                     errors="coerce")
                out[yr] = pd.Series(vals.values, index=grp["fips"].values)
    return out


def _nearest_earlier(series_by_year, target):
    """Pick the value-series for the latest available year <= target."""
    avail = sorted([y for y in series_by_year if y <= target])
    if not avail:
        return None, None
    y = avail[-1]
    return y, series_by_year[y]


def load_income_unemp():
    inc = _ers_year_series(os.path.join(RAW, "ers_income_unemp.csv"),
                           "FIPS_Code", "Median_Household_Income_")
    une = _ers_year_series(os.path.join(RAW, "ers_income_unemp.csv"),
                           "FIPS_Code", "Unemployment_rate_")
    rows = []
    src = {}
    for y in ELECTION_YEARS:
        iy, iser = _nearest_earlier(inc, y)
        uy, user = _nearest_earlier(une, y)
        src[y] = {"income_year": iy, "unemp_year": uy}
        idx = (iser.index if iser is not None else
               (user.index if user is not None else []))
        rec = pd.DataFrame({"fips": list(idx), "year": y})
        rec["median_household_income"] = (iser.reindex(idx).values
                                          if iser is not None else np.nan)
        rec["unemployment_rate"] = (user.reindex(idx).values
                                    if user is not None else np.nan)
        rows.append(rec)
    return pd.concat(rows, ignore_index=True), src


def load_education():
    """
    ACS-period bachelor's. Available periods: 1990, 2000, 2008-12, 2019-23.
    Map each election year to the nearest available period (by its end year).
    """
    d = pd.read_csv(os.path.join(RAW, "ers_education.csv"),
                    dtype=str, encoding="latin-1")
    d = d.rename(columns={"FIPS Code": "FIPS_Code"})
    d = d[d["FIPS_Code"].str.startswith("48", na=False)].copy()
    d["fips"] = d["FIPS_Code"].apply(fips5)
    prefix = "Percent of adults with a bachelor's degree or higher, "
    periods = {}  # end_year -> (label, Series)
    for attr, grp in d.groupby("Attribute"):
        if attr.startswith(prefix):
            label = attr[len(prefix):]
            end = int(label.split("-")[-1]) if "-" in label else int(label)
            # two-digit ACS end ("2008-12") -> 2012
            if "-" in label:
                a, b = label.split("-")
                end = int(a[:2] + b) if len(b) == 2 else int(b)
            vals = pd.to_numeric(grp["Value"], errors="coerce")
            periods[end] = (label, pd.Series(vals.values, index=grp["fips"].values))

    rows, src = [], {}
    end_years = sorted(periods)
    for y in ELECTION_YEARS:
        # nearest period by absolute distance of end-year, ties -> earlier
        best = min(end_years, key=lambda e: (abs(e - y), e))
        label, ser = periods[best]
        src[y] = label
        rec = pd.DataFrame({"fips": ser.index, "year": y,
                            "pct_bachelors_plus": ser.values})
        rows.append(rec)
    return pd.concat(rows, ignore_index=True), src


def load_poverty():
    """
    SAIPE poverty: only a single recent year (PCTPOVALL_2023) is present.
    Attach poverty_rate ONLY to the nearest election year (2024); all
    other years left blank (documented). No back-filling.
    """
    d = pd.read_csv(os.path.join(RAW, "ers_poverty.csv"),
                    dtype=str, encoding="latin-1")
    d = d[d["FIPS_Code"].str.startswith("48", na=False)].copy()
    d["fips"] = d["FIPS_Code"].apply(fips5)
    pov = d[d["Attribute"] == "PCTPOVALL_2023"].copy()
    pov_year = 2023
    ser = pd.Series(pd.to_numeric(pov["Value"], errors="coerce").values,
                    index=pov["fips"].values)
    # attach to nearest election year (latest <= or nearest overall)
    target = min(ELECTION_YEARS, key=lambda y: abs(y - pov_year))
    rec = pd.DataFrame({"fips": ser.index, "year": target,
                        "poverty_rate": ser.values})
    return rec, {"poverty_year": pov_year, "attached_to": target}


# ===========================================================================
# 7. ASSEMBLE
# ===========================================================================
def main():
    print("Loading sources...")
    pol = load_political()
    demo = load_demographics()
    age = load_agesex()
    land = load_land()
    cbsa = load_cbsa()
    inc_unemp, inc_src = load_income_unemp()
    edu, edu_src = load_education()
    pov, pov_src = load_poverty()

    # --- canonical county list / scaffold from demographics -----------------
    names = (demo[["fips", "CTYNAME"]].dropna().drop_duplicates("fips")
             .set_index("fips")["CTYNAME"])
    all_fips = sorted(names.index)
    assert len(all_fips) == 254, f"Expected 254 counties, got {len(all_fips)}"

    scaffold = pd.MultiIndex.from_product(
        [all_fips, ELECTION_YEARS], names=["fips", "year"]).to_frame(index=False)
    scaffold["county"] = scaffold["fips"].map(names).str.replace(
        " County", "", regex=False)

    df = scaffold.copy()

    # merge political
    df = df.merge(
        pol[["year", "fips", "total_votes", "rep_votes", "dem_votes",
             "rep_two_party_share", "margin_rep"]],
        on=["fips", "year"], how="left")

    # merge demographics (drop name col; scaffold already has county)
    df = df.merge(
        demo[["fips", "year", "population",
              "pct_hispanic", "pct_black", "pct_white_nh"]],
        on=["fips", "year"], how="left")

    # merge agesex
    df = df.merge(age, on=["fips", "year"], how="left")

    # geography (constant): density = population / land
    df = df.merge(land, on="fips", how="left")
    df["pop_density"] = df["population"] / df["aland_sqmi"]

    # cbsa (constant)
    df = df.merge(cbsa, on="fips", how="left")
    df["metro_status"] = df["metro_status"].fillna("Non-Metro")
    df["cbsa_type"] = df["cbsa_type"].fillna("Neither")

    # socioeconomic
    df = df.merge(inc_unemp, on=["fips", "year"], how="left")
    df = df.merge(edu, on=["fips", "year"], how="left")
    df = df.merge(pov, on=["fips", "year"], how="left")

    # turnout
    df["turnout_vap"] = np.where(
        df["voting_age_pop"] > 0, df["total_votes"] / df["voting_age_pop"], np.nan)

    # --- rounding -----------------------------------------------------------
    for c in ["rep_two_party_share", "margin_rep", "turnout_vap"]:
        df[c] = df[c].round(4)
    for c in ["pct_hispanic", "pct_black", "pct_white_nh",
              "unemployment_rate", "pct_bachelors_plus", "poverty_rate"]:
        df[c] = df[c].round(1)
    df["median_age"] = df["median_age"].round(1)
    df["pop_density"] = df["pop_density"].round(1)
    df["median_household_income"] = df["median_household_income"].round(0)

    # integer-ish columns kept nullable
    for c in ["population", "voting_age_pop", "total_votes",
              "rep_votes", "dem_votes", "median_household_income"]:
        df[c] = df[c].astype("Float64").round(0).astype("Int64")

    df = df[FINAL_COLS].sort_values(["fips", "year"]).reset_index(drop=True)

    # =======================================================================
    # 8. VALIDATION
    # =======================================================================
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)
    print(f"Rows: {len(df)}  (ideal 254 x 7 = 1778)")

    # missing year x county
    full = pd.MultiIndex.from_product([all_fips, ELECTION_YEARS],
                                      names=["fips", "year"])
    have = pd.MultiIndex.from_frame(df[["fips", "year"]])
    missing = full.difference(have)
    print(f"Missing (county,year) cells: {len(missing)}")
    if len(missing):
        print(list(missing)[:20])

    # share / turnout ranges
    bad_share = df[(df["rep_two_party_share"].notna())
                   & ((df["rep_two_party_share"] <= 0)
                      | (df["rep_two_party_share"] > 1))]
    bad_turn = df[(df["turnout_vap"].notna())
                  & ((df["turnout_vap"] <= 0) | (df["turnout_vap"] > 1))]
    print(f"rep_two_party_share outside (0,1]: {len(bad_share)}")
    print(f"turnout_vap outside (0,1]: {len(bad_turn)}")
    if len(bad_turn):
        print(bad_turn[["fips", "county", "year", "turnout_vap",
                        "total_votes", "voting_age_pop"]].to_string(index=False))
    assert len(bad_share) == 0, "rep_two_party_share out of range!"

    # spot checks
    print("\n--- Spot checks ---")
    print("Largest population row (should be Harris 48201):")
    print(df.loc[df["population"].idxmax(),
                 ["fips", "county", "year", "population"]].to_dict())
    print("\nSmallest population row (should be Loving 48301):")
    print(df.loc[df["population"].idxmin(),
                 ["fips", "county", "year", "population"]].to_dict())
    print("\nLoving County (48301) all years:")
    print(df[df["fips"] == "48301"][["year", "population",
          "total_votes", "rep_two_party_share"]].to_string(index=False))
    print("\nTravis County (48453) 2020 (expect big votes, share < 0.5):")
    print(df[(df["fips"] == "48453") & (df["year"] == 2020)][
        ["county", "year", "total_votes", "rep_two_party_share",
         "turnout_vap"]].to_string(index=False))
    print("\nHarris County (48201) all years:")
    print(df[df["fips"] == "48201"][["year", "population", "total_votes",
          "rep_two_party_share", "turnout_vap"]].to_string(index=False))

    # coverage by year
    print("\n--- Coverage (% non-missing) by year ---")
    cov = (df.groupby("year").apply(
        lambda g: (g.notna().mean() * 100).round(1), include_groups=False))
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 50)
    print(cov[[c for c in FINAL_COLS if c not in ("fips", "county", "year")]]
          .T.to_string())

    # =======================================================================
    # 9. WRITE OUTPUTS
    # =======================================================================
    df.to_csv(CSV_OUT, index=False)
    print(f"\nWrote {CSV_OUT}")

    write_xlsx(df, cov, inc_src, edu_src, pov_src)
    print(f"Wrote {XLSX_OUT}")

    return df, inc_src, edu_src, pov_src


def write_xlsx(df, cov, inc_src, edu_src, pov_src):
    codebook_rows = [
        ("fips", "5-digit county FIPS code (string, zero-padded; TX='48xxx')",
         "Census/derived join key"),
        ("county", "County name", "Census PEP CTYNAME"),
        ("year", "Presidential election year", "constructed"),
        ("metro_status", "Metro / Non-Metro", "OMB CBSA delineation (Feb 2023)"),
        ("cbsa_type", "Metropolitan / Micropolitan / Neither", "OMB CBSA (2023)"),
        ("population", "Total resident population (July 1 estimate)", "Census PEP"),
        ("voting_age_pop", "Population 18+ (blank for 2000/2004/2008)", "Census PEP agesex"),
        ("total_votes", "Total presidential votes cast", "MEDSL / tonmcg"),
        ("rep_votes", "Republican presidential votes", "MEDSL / tonmcg"),
        ("dem_votes", "Democratic presidential votes", "MEDSL / tonmcg"),
        ("rep_two_party_share", "rep/(rep+dem), 4 dp", "derived"),
        ("margin_rep", "rep share - dem share (two-party), 4 dp", "derived"),
        ("turnout_vap", "total_votes / voting_age_pop, 4 dp (blank 2000-2008)", "derived"),
        ("pct_hispanic", "% Hispanic (any race), 1 dp", "Census PEP"),
        ("pct_black", "% Black alone (any ethnicity), 1 dp", "Census PEP"),
        ("pct_white_nh", "% White, non-Hispanic alone, 1 dp", "Census PEP"),
        ("median_age", "Median age, years (blank 2000-2008)", "Census PEP agesex"),
        ("pop_density", "population / land area sq mi (2023 land area)", "Census Gazetteer"),
        ("median_household_income", "Median household income $ (2024<-2022 only)", "USDA ERS"),
        ("unemployment_rate", "Annual unemployment rate %, 1 dp", "USDA ERS / BLS LAUS"),
        ("pct_bachelors_plus", "% adults 25+ with bachelor's+, nearest ACS period", "USDA ERS / ACS"),
        ("poverty_rate", "% all-ages in poverty (2024 only, SAIPE 2023)", "USDA ERS / SAIPE"),
    ]
    cb = pd.DataFrame(codebook_rows, columns=["variable", "description", "source"])

    # Summary sheet: numeric describe + coverage
    num = df.select_dtypes(include=["number", "Int64", "Float64"]).astype("float")
    summary = num.describe().T.round(2).reset_index().rename(
        columns={"index": "variable"})

    with pd.ExcelWriter(XLSX_OUT, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="Panel", index=False)
        cb.to_excel(xw, sheet_name="Codebook", index=False)
        summary.to_excel(xw, sheet_name="Summary", index=False)
        cov_out = cov[[c for c in FINAL_COLS
                       if c not in ("fips", "county", "year")]].T
        cov_out.reset_index().rename(columns={"index": "variable"}).to_excel(
            xw, sheet_name="Coverage", index=False)
        # Force the FIPS join key to display as zero-padded text (not numeric).
        ws = xw.sheets["Panel"]
        for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
            for cell in row:
                cell.number_format = "@"
                cell.value = str(cell.value).zfill(5)


if __name__ == "__main__":
    main()
