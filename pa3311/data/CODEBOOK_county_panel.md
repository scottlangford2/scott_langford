# TX_County_Political_Panel_2000_2024 — Codebook

**Unit of observation:** Texas county × presidential-election year.
**Coverage:** all **254 counties** × **7 elections** (2000, 2004, 2008, 2012, 2016, 2020, 2024) = **1,778 rows**.
**Role in course:** the **second spine dataset** — a political-science companion (for PS 3315) to the city sales-tax panel. Same methods (descriptives, t-tests, regression) on political/socioeconomic outcomes.
**Join key:** 5-digit county FIPS (`fips`, zero-padded string, Texas = `48xxx`).

## Variables
| Variable | Description | Units | Source |
|---|---|---|---|
| `fips` | County FIPS (5-digit) | — | — |
| `county` | County name | — | Census |
| `year` | Presidential election year | 2000–2024 | — |
| `metro_status` | Metro vs. Non-Metro | category | OMB/Census CBSA 2023 |
| `cbsa_type` | Metropolitan / Micropolitan / Neither | category | OMB/Census CBSA 2023 |
| `population` | Total population (that year) | persons | Census PEP |
| `voting_age_pop` | Voting-age population (18+) | persons | Census PEP (2012–2024 only) |
| `total_votes` | Total presidential votes cast | votes | MIT Election Lab / county returns |
| `rep_votes` | Republican presidential votes | votes | MIT Election Lab / county returns |
| `dem_votes` | Democratic presidential votes | votes | MIT Election Lab / county returns |
| `rep_two_party_share` | rep / (rep + dem) | proportion | derived |
| `margin_rep` | rep_two_party_share − dem_two_party_share | proportion | derived |
| `turnout_vap` | total_votes / voting_age_pop | proportion | derived (2012–2024 only) |
| `pct_hispanic` | % Hispanic (any race) | percent | Census PEP |
| `pct_black` | % Black alone | percent | Census PEP |
| `pct_white_nh` | % White, non-Hispanic | percent | Census PEP |
| `median_age` | Median age | years | Census PEP (2012–2024 only) |
| `pop_density` | population / land area (sq mi) | per sq mi | derived (Census Gazetteer 2023 land area) |
| `unemployment_rate` | Unemployment rate (that year) | percent | USDA ERS (BLS LAUS) |
| `pct_bachelors_plus` | % adults 25+ with a bachelor's+ | percent | USDA ERS (nearest ACS period) |
| `median_household_income` | Median household income (that year) | $ | Census SAIPE |
| `poverty_rate` | Poverty rate, all ages (that year) | percent | Census SAIPE |
| `vote_center_adopt_year` | First year the county participated in the Texas Countywide Polling Place Program (vote centers); blank = not adopted as of the data | year | TX Secretary of State (see below) |
| `vote_center` | Time-varying treatment indicator: 1 if the election `year` ≥ `vote_center_adopt_year`, else 0 | 0/1 | derived |

## Sources (all free; no API key)
- **Political:** MIT Election Lab county presidential returns — 2000–2016 via the official MEDSL `county-returns` GitHub mirror; 2020 & 2024 via the `tonmcg` county-results GitHub repo. (Canonical dataset: Harvard Dataverse `doi:10.7910/DVN/VOQCHQ`, which is guestbook-gated; the GitHub mirrors carry the same returns.)
- **Demographic:** U.S. Census **Population Estimates Program** (county, by year) — population, voting-age (18+), race/ethnicity, median age — across the 2000–2010, 2010–2020, and 2020–2024 vintages. Land area from the Census **County Gazetteer (2023)**. Metro status from the **OMB/Census CBSA delineation (2023)**.
- **Socioeconomic:** **Census SAIPE** (median household income + poverty rate, by year); **USDA ERS** county data sets (unemployment by year, from BLS LAUS; educational attainment by nearest ACS period).
- **Vote centers (`vote_center*`):** Texas **Secretary of State**, Countywide Polling Place Program (CWPP). First-participation election dates are chained from the SoS biennial reports under Tex. Elec. Code §43.007(j) (83rd–88th Legislatures, covering 2006–2022) plus the current CWPP approved-county page for 2023–2026 entrants. Program history: pilot 2006 (HB 758); permanent 2009 (HB 719). The 100-county lookup is `data/vote_center_adoption.csv`; rebuild with `scripts/add_vote_centers.py`. Academic background: Stein & Vonnahme; Cortina & Rottinghaus (2019), *Research & Politics*, doi:10.1177/2053168019864224.

## Year-code decodings used (Census PEP)
- 2020–2024 files (`cc-est2024-*`): YEAR `2`=2020, `6`=2024.
- 2010–2020 files (`CC-EST2020-*`): YEAR `4`=2012, `8`=2016 (1=Apr-2010 census, 2=Jul-2010, 3=2011, …).
- 2000–2010 intercensal files: used for 2000/2004/2008 population, race, and ethnicity.

## Limitations (teaching points — documented, never fabricated)
1. **Turnout, voting-age population, and median age exist only for 2012–2024.** The 2000–2010 PEP age file uses 5-year bins that straddle age 18, so a clean 18+ count (the turnout denominator) can't be derived for 2000/2004/2008. Those cells are blank.
2. **`turnout_vap` exceeds 1.0 in 4 micro-county rows** (Loving 48301, McMullen 48311, in 2020 & 2024). These are *faithful*, not bugs — a known artifact of PEP population estimates for counties of a few dozen people. Retained as-is; a good outlier/measurement-error lesson.
3. **`pct_bachelors_plus`** uses the **nearest** ERS/ACS education period (only a few periods exist), so some election years share a value.
4. **`pop_density`** uses 2023 land area for all years (land area is ~stable; only the current Gazetteer vintage was used).
5. Demographic shares are stitched from **mixed PEP vintages** at the decade boundaries; small discontinuities can occur around 2010/2020.
6. **`vote_center_adopt_year` is a teaching dataset.** The county→year pairs were transcribed from the SoS §43.007(j) report *pages* (not the raw PDF tables); for research-grade use, re-verify each date against the original report PDFs. "Adoption year" = first election of participation (the SoS also tracks a separate, slightly later "successful designation" date). 100 of 254 counties had adopted as of the data (cumulative: 45 by 2016, 77 by 2020, 99 by 2024).

## How it powers the course (PS 3315 angle)
- Descriptives/distributions: turnout, partisan share, income, poverty across the 254 counties.
- Independent t-test: turnout or Republican share, **Metro vs. Non-Metro** counties.
- Paired t-test: a county's turnout or partisan share, **2016 vs. 2020** (or 2020 vs. 2024).
- Regression: turnout ~ median income / % bachelor's; partisan share ~ demographics (with an omitted-variable-bias discussion).
- Trends: partisan realignment and turnout change 2000 → 2024.
- **Causal designs (PA 5312 Case B):** `vote_center` is a staggered, time-varying treatment — supports **difference-in-differences** (adopters vs. not-yet/never-adopters) and **interrupted time series** (a county's turnout before/after its own adoption year). Caution: 2020's pandemic turnout surge and adopter self-selection confound a naive 2×2 (it gives roughly −1.7 pts for 2017–2020 adopters), which is itself a teachable point.

Built 2026-06-02. Reproduce with `build_county_panel.py` (political + demographic), then `add_saipe.py` (income + poverty), then `add_vote_centers.py` (vote-center treatment variables). Raw inputs in `_raw_county/`.
