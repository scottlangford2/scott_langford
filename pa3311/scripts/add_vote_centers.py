#!/usr/bin/env python3
"""
add_vote_centers.py  -- operationalize Case B (countywide vote centers).

Adds two columns to TX_County_Political_Panel_2000_2024.csv:
  vote_center_adopt_year : first year the county participated in the Texas
                           Countywide Polling Place Program (CWPP); blank if
                           the county had not adopted as of the data.
  vote_center            : time-varying treatment indicator, 1 if the election
                           year >= the county's adoption year, else 0.

Also writes vote_center_adoption.csv (the county -> adoption-year lookup with
the first-participation election date and the source SoS report).

SOURCE / PROVENANCE
-------------------
First-participation election dates are chained from the Texas Secretary of
State's biennial reports under Tex. Elec. Code sec. 43.007(j) ("Report to the
Nth Legislature ... Countywide Polling Place Program"), 83rd-88th Legislatures,
plus the current CWPP approved-county page for 2023-2026 entrants:
  https://www.sos.state.tx.us/elections/laws/countywide-polling-place-program.shtml
  https://www.sos.texas.gov/elections/laws/report-to-legislature.shtml
Program history: pilot 2006 (HB 758, 79th Leg.); made permanent 2009 (HB 719,
81st Leg.). Academic corroboration of the early pilots: Stein & Vonnahme; and
Cortina & Rottinghaus (2019), Research & Politics, doi:10.1177/2053168019864224.

CAVEAT (teaching dataset): the county->year pairs were transcribed from the SoS
report pages; for research-grade use, re-verify each date against the original
report PDFs. "Adoption year" = first election of participation (the SoS also
tracks a separate, slightly later "successful designation" date).
"""
import pandas as pd, os

PANEL = "TX_County_Political_Panel_2000_2024.csv"

# county -> (first_participation_year, first_election_date, source_report)
ADOPT = {
    "Lubbock": (2006, "2006-11-07", "HB 758 pilot / 83rd Leg."),
    "Erath": (2008, "2008", "80th-83rd Leg."),
    "Collin": (2009, "2009-11-03", "83rd Leg."),
    "Galveston": (2009, "2009-11-03", "83rd Leg."),
    "Madison": (2010, "2010-11-02", "83rd Leg."),
    "Gaines": (2011, "2011-11-08", "83rd Leg."),
    "Midland": (2011, "2011-11-08", "83rd Leg."),
    "Travis": (2011, "2011-11-08", "83rd Leg."),
    "Eastland": (2012, "2012-11-06", "83rd Leg."),
    "Floyd": (2012, "2012-11-06", "83rd Leg."),
    "Lampasas": (2012, "2012-11-06", "83rd Leg."),
    "Swisher": (2012, "2012-11-06", "83rd Leg."),
    "Callahan": (2013, "2013-11-05", "84th Leg."),
    "Coryell": (2013, "2013-11-05", "84th Leg."),
    "Grayson": (2013, "2013-11-05", "84th Leg."),
    "Jefferson": (2013, "2013-11-05", "84th Leg."),
    "Randall": (2013, "2013-11-05", "84th Leg."),
    "Victoria": (2013, "2013-11-05", "84th Leg."),
    "Williamson": (2013, "2013-11-05", "84th Leg."),
    "Wharton": (2014, "2014-03-04", "84th Leg."),
    "McLennan": (2014, "2014-11-04", "84th Leg."),
    "Montague": (2014, "2014-11-04", "84th Leg."),
    "Navarro": (2014, "2014-11-04", "84th Leg."),
    "Rusk": (2014, "2014-11-04", "84th Leg."),
    "Taylor": (2014, "2014-11-04", "84th Leg."),
    "Tom Green": (2014, "2014-11-04", "84th Leg."),
    "Brazoria": (2015, "2015-05", "85th Leg."),
    "Aransas": (2015, "2015-11", "85th Leg."),
    "Brazos": (2015, "2015-11", "85th Leg."),
    "Ector": (2015, "2015-11", "85th Leg."),
    "Fort Bend": (2015, "2015-11", "85th Leg."),
    "Hood": (2015, "2015-11", "85th Leg."),
    "Hopkins": (2015, "2015-11", "85th Leg."),
    "Milam": (2015, "2015-11", "85th Leg."),
    "Parker": (2015, "2015-11", "85th Leg."),
    "Potter": (2015, "2015-11", "85th Leg."),
    "Smith": (2015, "2015-11", "85th Leg."),
    "Lee": (2016, "2016-03", "85th Leg."),
    "Palo Pinto": (2016, "2016-03", "85th Leg."),
    "San Jacinto": (2016, "2016-03", "85th Leg."),
    "Young": (2016, "2016-03", "85th Leg."),
    "Medina": (2016, "2016-05", "85th Leg."),
    "Grimes": (2016, "2016-11", "85th Leg."),
    "Nueces": (2016, "2016-11", "85th Leg."),
    "Throckmorton": (2016, "2016-11", "85th Leg."),
    "DeWitt": (2017, "2017-11-07", "86th Leg."),
    "Gregg": (2017, "2017-11-07", "86th Leg."),
    "Guadalupe": (2017, "2017-11-07", "86th Leg."),
    "Hidalgo": (2017, "2017-11-07", "86th Leg."),
    "Jack": (2017, "2017-11-07", "86th Leg."),
    "Kaufman": (2017, "2017-11-07", "86th Leg."),
    "San Patricio": (2017, "2017-11-07", "86th Leg."),
    "Upshur": (2017, "2017-11-07", "86th Leg."),
    "Wichita": (2017, "2017-11-07", "86th Leg."),
    "Deaf Smith": (2018, "2018-03-06", "86th Leg."),
    "Archer": (2018, "2018-11-06", "86th Leg."),
    "Bee": (2019, "2019-05-04", "87th Leg."),
    "Ellis": (2019, "2019-05-04", "87th Leg."),
    "Harris": (2019, "2019-05-04", "87th Leg."),
    "Howard": (2019, "2019-05-04", "87th Leg."),
    "Atascosa": (2019, "2019-11-05", "87th Leg."),
    "Bexar": (2019, "2019-11-05", "87th Leg."),
    "Comal": (2019, "2019-11-05", "87th Leg."),
    "Dallas": (2019, "2019-11-05", "87th Leg."),
    "Hays": (2019, "2019-11-05", "87th Leg."),
    "Henderson": (2019, "2019-11-05", "87th Leg."),
    "Jones": (2019, "2019-11-05", "87th Leg."),
    "Kendall": (2019, "2019-11-05", "87th Leg."),
    "Tarrant": (2019, "2019-11-05", "87th Leg."),
    "Bell": (2020, "2020-03-03", "87th Leg."),
    "Marion": (2020, "2020-03-03", "87th Leg."),
    "Scurry": (2020, "2020-03-03", "87th Leg."),
    "Burnet": (2020, "2020-11-03", "87th Leg."),
    "El Paso": (2020, "2020-11-03", "87th Leg."),
    "Liberty": (2020, "2020-11-03", "87th Leg."),
    "Somervell": (2020, "2020-11-03", "87th Leg."),
    "Walker": (2020, "2020-11-03", "87th Leg."),
    "Angelina": (2021, "2021-11-02", "88th Leg."),
    "Chambers": (2021, "2021-11-02", "88th Leg."),
    "Fisher": (2021, "2021-11-02", "88th Leg."),
    "Polk": (2021, "2021-11-02", "88th Leg."),
    "Rockwall": (2021, "2021-11-02", "88th Leg."),
    "Bastrop": (2022, "2022-03-01", "88th Leg."),
    "Harrison": (2022, "2022-03-01", "88th Leg."),
    "Austin": (2022, "2022-05-07", "88th Leg."),
    "Jim Wells": (2022, "2022-05-07", "88th Leg."),
    "Blanco": (2022, "2022-11-08", "88th Leg."),
    "Bowie": (2022, "2022-11-08", "88th Leg."),
    "Brown": (2022, "2022-11-08", "88th Leg."),
    "Cherokee": (2022, "2022-11-08", "88th Leg."),
    "Webb": (2022, "2022-11-08", "88th Leg."),
    "Orange": (2023, "2023-05-06", "CWPP approved list"),
    "Burleson": (2023, "2023-11-07", "CWPP approved list"),
    "Cass": (2023, "2023-11-07", "CWPP approved list"),
    "Karnes": (2023, "2023-11-07", "CWPP approved list"),
    "Parmer": (2023, "2023-11-07", "CWPP approved list"),
    "Cameron": (2024, "2024-11-05", "CWPP approved list"),
    "Comanche": (2024, "2024-11-05", "CWPP approved list"),
    "Uvalde": (2024, "2024-11-05", "CWPP approved list"),
    "Limestone": (2026, "2026", "CWPP approved list"),
}

def main():
    d = pd.read_csv(PANEL)
    panel_counties = set(d.county.unique())
    missing = [c for c in ADOPT if c not in panel_counties]
    if missing:
        raise SystemExit("Mapping names not found in panel (fix spelling): %s" % missing)

    # lookup CSV
    look = pd.DataFrame(
        [(c, y, fe, src) for c, (y, fe, src) in sorted(ADOPT.items())],
        columns=["county", "vote_center_adopt_year", "first_participation_election", "source_report"],
    )
    look.to_csv("vote_center_adoption.csv", index=False)

    yr = {c: v[0] for c, v in ADOPT.items()}
    d["vote_center_adopt_year"] = d.county.map(yr).astype("Int64")
    d["vote_center"] = ((d.vote_center_adopt_year.notna()) &
                        (d.year >= d.vote_center_adopt_year)).astype(int)
    d.to_csv(PANEL, index=False)

    # coverage report
    n_adopt = len(ADOPT)
    treated_counties = d[d.vote_center == 1].county.nunique()
    print("Panel rows: %d | counties: %d" % (len(d), d.county.nunique()))
    print("Counties with a CWPP adoption year: %d (never-adopted as of data: %d)"
          % (n_adopt, d.county.nunique() - n_adopt))
    print("Counties treated (vote_center=1) in >=1 panel election: %d" % treated_counties)
    print("\nTreated counties by presidential election year:")
    print(d[d.vote_center == 1].groupby("year").county.nunique().to_string())
    print("\nWrote vote_center_adoption.csv (%d counties) and updated %s (+2 cols)."
          % (n_adopt, PANEL))

if __name__ == "__main__":
    main()
