# Codebook — Perry Preschool Outcomes (Case E)

**What this file is.** A small table of the *real, published* headline outcomes of the HighScope Perry Preschool Study, taken from the official age-40 report (Schweinhart, Montie, Xiang, Barnett, Belfield, and Nores, *Lifetime Effects: The High/Scope Perry Preschool Study Through Age 40*, HighScope Press, 2005). It is **aggregate published data**, not participant-level microdata — the study's individual records are restricted-use and are not distributed here. Every percentage below is a figure reported in the official study; the whole-child counts are the integers those percentages imply given the known group sizes.

**The study.** From 1962 to 1967 the HighScope Educational Research Foundation (a nonprofit) ran a preschool program in Ypsilanti, Michigan, for 123 low-income children judged to be at high risk of school failure. Children were **randomly assigned** to a program group (n = 58) or a no-program comparison group (n = 65) and followed for decades. Because *n* is small and outcomes are mostly yes/no, the natural analyses are two-proportion comparisons, risk differences, and a cost-benefit calculation — all reproducible in Excel from the table below.

## Columns

| Column | Meaning |
|---|---|
| `outcome` | The measured outcome (all binary: the person either did or did not meet it). |
| `measure_age` | Participant age at which the outcome was measured (40, or 5 for the IQ measure). |
| `program_pct` | Percent of the program group (n = 58) meeting the outcome — **as published**. |
| `program_n` | Program group size (58). |
| `program_count` | Whole-child count implied by `program_pct` × 58, rounded. |
| `comparison_pct` | Percent of the no-program group (n = 65) meeting the outcome — **as published**. |
| `comparison_n` | Comparison group size (65). |
| `comparison_count` | Whole-child count implied by `comparison_pct` × 65, rounded. |
| `source` | Citation for the published figure. |

## Other real published figures (not in the table)

- **High school graduation, females only:** 84% (program) vs. 32% (comparison). The female-subgroup denominators are not published here, so no counts are given.
- **Median annual earnings at 40:** $20,800 (program) vs. $15,300 (comparison).
- **Cost-benefit (Schweinhart et al. 2005; constant 2000 dollars, 3% discount rate):** about **$16.14 returned to society per $1 invested** ($244,812 in benefits on a $15,166 per-child investment); about **$12.90 per $1 to the public**, of which roughly 88% ($171,473) came from reduced crime. An earlier age-27 analysis reported $7.16 per $1.
- **Independent reanalysis (Heckman, Moon, Pinto, Savelyev, and Yavitz 2010, *Journal of Public Economics* 94:114–128; NBER Working Paper 16180):** an estimated **7–10% annual social rate of return**, roughly **$7–$12 per $1**, computed with standard errors that account for small-sample and randomization issues.

## Want real downloadable microdata?

Perry's participant-level records are restricted. For a genuinely public, downloadable small-N early-childhood file, use the **Carolina Abecedarian Project (ICPSR / Child and Family Data Archive, Study 4091**, DOI 10.3886/ICPSR04091.v2; free account, public-use files, n ≈ 111). Its cost-benefit ratio (≈ 7.3; internal rate of return ≈ 13.7%) is reported by García, Heckman, Leaf, and Prados (2020, *Journal of Political Economy*; NBER 22993).
