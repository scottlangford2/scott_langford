#!/usr/bin/env python3
"""Validate the PA 3311 / PS 3315 spine datasets after a rebuild.

Asserts invariants so an upstream source change can't silently corrupt the data.
Run from Datasets/:  python3 validate.py    (exit 0 = all pass, 1 = a check failed)
"""
import sys
import pandas as pd

CHECKS = []
def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), detail))

# ---------- Panel ----------
p = pd.read_csv("TX_City_Sales_Panel_2013_2024.csv")
check("panel: 1,000-1,300 cities", 1000 <= p["city"].nunique() <= 1300, f"{p['city'].nunique()} cities")
check("panel: 12,000-15,000 rows", 12000 <= len(p) <= 15000, f"{len(p)} rows")
check("panel: years 2013-2024 contiguous", sorted(p["year"].unique()) == list(range(2013, 2025)))
check("panel: no duplicate city-year", p.duplicated(["city", "year"]).sum() == 0, f"{p.duplicated(['city','year']).sum()} dups")
check("panel: no negative allocation", (p["sales_tax_alloc"].dropna() >= 0).all())
check("panel: sales_tax_rate in [0.25, 2.0]", p["sales_tax_rate"].dropna().between(0.25, 2.0).all())
check("panel: metro_status values valid", set(p["metro_status"].dropna().unique()) <= {"Metro", "Non-Metro"})
check("panel: cbsa_type values valid", set(p["cbsa_type"].dropna().unique()) <= {"Metropolitan", "Micropolitan", "Neither"})
check("panel: attr match >= 95%", p["metro_status"].notna().mean() >= 0.95, f"{p['metro_status'].notna().mean()*100:.1f}%")
check("panel: real >= nominal pre-2024", (p[p.year < 2024]["sales_tax_alloc_real2024"].dropna() >=
                                          p[p.year < 2024]["sales_tax_alloc"].dropna()).mean() > 0.99)
check("panel: Houston & Austin present", {"HOUSTON", "AUSTIN"} <= set(p["city"].str.upper()))
check("panel: taxable_sales only 2016+", p[p.year < 2016]["taxable_sales"].notna().sum() == 0)

# ---------- Cross-section ----------
c = pd.read_csv("TX_City_Finance_2022.csv")
check("cross: ~1,200 cities", 1100 <= len(c) <= 1300, f"{len(c)} rows")
check("cross: no negative debt", (c["total_debt_os"] >= 0).all())
check("cross: total_debt = lt + st", ((c["lt_debt_os"] + c["st_debt_os"] - c["total_debt_os"]).abs() < 1).all())
check("cross: population > 0", (c["population"] > 0).all())
check("cross: debt_per_capita = debt/pop", ((c["total_debt_os"] / c["population"] - c["debt_per_capita"]).abs() < 1).all())
check("cross: growth finite (no inf)", c["salestax_growth_19_23_pct"].replace([float("inf"), float("-inf")], pd.NA).equals(c["salestax_growth_19_23_pct"]))
check("cross: metro split plausible", 600 <= (c["metro_status"] == "Metro").sum() <= 800, f"{(c['metro_status']=='Metro').sum()} metro")

# ---------- Report ----------
passed = sum(1 for _, ok, _ in CHECKS if ok)
for name, ok, detail in CHECKS:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
print(f"\n{passed}/{len(CHECKS)} checks passed.")
sys.exit(0 if passed == len(CHECKS) else 1)
