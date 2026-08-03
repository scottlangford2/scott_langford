# NSW Demonstration — Codebook (Case C)

The **National Supported Work (NSW) Demonstration** was a randomized evaluation (mid-1970s) of a subsidized transitional-employment program for severely disadvantaged workers. These files are the widely used **Dehejia–Wahba public extract** (the "NSW-DW" sample with 1974 earnings), retrieved from Robert Dehejia's data page (users.nber.org/~rdehejia/data). Public, free, no registration.

## Files
| File | Rows | What it is |
|---|---|---|
| `NSW_experimental.csv` / `.xlsx` | 445 | The **randomized** sample: program (treat=1, n=185) vs. randomized control (treat=0, n=260). Use this for the true experimental effect. |
| `NSW_observational_cps.csv` | 16,177 | The program group (treat=1, n=185) plus a **non-experimental** comparison group drawn from the Current Population Survey (treat=0). Use this to show how a naive observational comparison misleads. |

## Variables
| Variable | Description | Units |
|---|---|---|
| `treat` | 1 = NSW program participant, 0 = comparison/control | indicator |
| `age` | Age at enrollment | years |
| `educ` | Years of schooling | years |
| `black` | 1 = Black | indicator |
| `hispanic` | 1 = Hispanic | indicator |
| `married` | 1 = married | indicator |
| `nodegree` | 1 = no high-school degree | indicator |
| `re74` | Real earnings, 1974 (pre-program) | $ |
| `re75` | Real earnings, 1975 (pre-program) | $ |
| `re78` | Real earnings, 1978 (post-program; the outcome) | $ |

## The headline results (reproduce these in Excel)
- **Experimental** (`NSW_experimental`): treated 1978 earnings $6,349 vs. control $4,555 → **effect = +$1,794**.
- **Observational** (`NSW_observational_cps`): treated vs. the CPS comparison group → **−$8,498** — the sign flips. This is the classic demonstration that selection bias defeats naive comparisons (LaLonde 1986; Dehejia & Wahba 1999).

*Real, public-domain research data. Source: Dehejia & Wahba (1999, JASA); LaLonde (1986, AER).*
