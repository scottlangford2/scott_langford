---
title: 'The Hays Discount, Five Years Later'
date: 2026-04-21
permalink: /posts/2026/04/hays-discount/
related: false
tags:
  - Hays County
  - Texas
  - housing
  - public finance
---

Two weeks ago [the Hays County growth post][growth] put a single
number at the center of the story: $135,000 — the gap, in the ZHVI
release then current, between the median home in Travis County and
the median home in Hays County. That was the rough math a family is
doing when they pull off I-35 in Buda or Kyle instead of continuing
north.

Two caveats, right at the top. First, Zillow revises the series every
month. The most recent release puts the same gap at about $107K — a
real narrowing over the intervening weeks, not a coding error. Second,
a dollar-gap snapshot is only one reading of the affordability
pressure. The *percentage* premium of Travis over Hays is the
migration-relevant object, and the shape of that premium over time is
what this post is actually about.

This post is the answer, with three upgrades over the napkin version: a
triangulated price series so we aren't relying on one dataset, a full
PITI monthly cost so we aren't pretending property taxes and
homeowners' insurance don't exist, and proper statistics on the
"constant premium" claim. The full code and a data manifest with
checksums are in the [replication folder][repl] — anyone who wants to
rerun the analysis on a fresh Zillow release should get the same
numbers.

## Everyone Rode the Same Wave

Start with levels. The Zillow Home Value Index for Travis, Williamson,
and Hays rose sharply through 2021 and early 2022, peaked inside a few
months of each other in mid-2022, and has been grinding lower since.
The ordering that makes the growth story work — Travis on top, Hays at
the bottom — never breaks.

![Central Texas home values, 2020 → present](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_levels.png)

## The Dollar Gap Bulged, Then Pulled Back

Subtract, and the absolute Travis-over-Hays gap ran from about $93K at
the start of 2020, peaked near $157K in June 2022, and has ground
back down to $107K as of the March 2026 release. Williamson tracks
the same shape at a smaller magnitude — never more than about $47K
over Hays, currently about $34K.

![Absolute gap over Hays, 2020 → present](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_absolute.png)

That $50K peak-to-today swing in the Travis-Hays gap is not small.
If you stopped here you might conclude that Hays's relative advantage
eroded during the pandemic boom and then fully recovered. You would
be reading the wrong statistic.

## Triangulate Before Concluding

Before leaning too hard on one series, it's worth asking whether a
different source tells a different story. ZHVI is an index of home
*values* derived from Zillow's own estimates. The Federal Housing
Finance Agency publishes a repeat-sales index (HPI) that uses only
arms-length transaction pairs and is therefore immune to compositional
drift — an important concern in a fast-growing county where the typical
home this year is newer, bigger, and further out than last year's.
Realtor.com publishes median *listing* prices, which reflect what's on
the market rather than what's traded.

Three series, one qualitative answer:

![Three sources, one invariant](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_triangulation.png)

Levels differ, but all three tell the same story about the *premium*
of Travis over Hays: it does not trend. That convergence across
methodologies is the closest we get to a robustness certificate
without running the whole analysis twice.

## How Constant Is "Constant"?

Eyeballing a flat line is not a statistical claim. Three tests on the
premium ratio — and the tests contradict the easy reading:

- **Mean and HAC confidence interval.** The full-window mean is
  **≈ 31.7 %**, with a 95 % Newey–West confidence interval of
  **[30.2, 33.1]** — roughly 3 percentage points wide. That is the
  band the series has traded in, averaged over the whole window; it
  does not say the series stays inside it at every date.
- **AR(1) persistence.** The ratio's first-order autocorrelation is
  **≈ 0.996**. Monthly movements are almost entirely persistent —
  shocks to the premium do not dissipate on any reasonable monthly
  timescale. That is consistent with a slow-moving relative-price
  level, not with a stationary oscillation around a fixed mean.
- **Quandt–Andrews sup-F unknown-break test.** Against a null of a
  single constant mean, the test returns **sup-F = 198.6 at December
  2021** — more than fifty times the 5 % critical value of 3.84. The
  test emphatically rejects constancy. The series ran hot through
  2020 – mid-2021, peaking near **38 %**, and has been reverting
  toward the low 30s ever since.

![Premium statistics](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_relative_stats.png)

In plain English: the premium is not a constant. It spent roughly a
year elevated during the pandemic boom and has been grinding back down
for the four years since. What is stable, loosely, is the *range* —
the premium has lived between roughly 29 % and 38 % throughout, never
collapsing toward zero and never running above 40 %. A range is still
a useful object for a migration decision. It just isn't a point.

## Real Dollars, Not Just Nominal

The second napkin-version simplification was quoting the gap in
nominal dollars. CPI rose roughly 20 % over the window. In Jan-2020
dollars the peak gap is smaller, and the narrowing from peak to today
is less severe: some of the "contraction" was just general inflation.

![Real vs. nominal gap](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_real_nominal.png)

Not a big correction, but it moves the story from "the gap is closing"
to "the gap is approximately where it was in real terms."

## Rates Did Most of the Work — Until You Count Everything

The first draft claimed "rates did the work": financing $100K at 3 %
cost $420/month; financing $135K at 7 % costs $890; the monthly cost of
the gap more than doubled even as the absolute gap narrowed.

That's still directionally right, but it ignores the rest of the
monthly bill. Three components that matter:

- **Property tax.** Travis's effective rate (county + city + ISD + ESD)
  runs about 1.8 % of value. Hays's runs closer to 2.1 %, and many
  Hays neighborhoods sit inside a MUD or PID on top of that. On the
  *gap* itself, a higher Travis price means a higher Travis tax bill —
  adding to the cost of choosing north.
- **Homeowners insurance.** TDI data show Hays households paying
  modestly more than Travis households — wildfire and hail exposure
  east of the Balcones escarpment. That partially offsets the extra
  Travis tax bill.
- **MUD / PID assessments.** Many new Hays subdivisions carry a MUD
  rate of $0.75–$1.00 per $100 AV on top of everything else. Travis's
  mid-tier stock is mostly inside the City of Austin, where MUDs are
  rare. Choosing Travis typically means escaping the MUD.

Stacking these together, the full PITI monthly-cost gap looks like
this:

![PITI decomposition](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_piti.png)

Two notes. First, at today's rates the P&I gap alone overstates the
total cost of choosing Travis by roughly $150/month once MUD and
insurance offsets are credited — not a trivial difference for a family
running an affordability calculation. Second, the rate-driven doubling
of the P&I gap is still the largest single force; the full PITI gap
roughly doubled over the window even after offsets.

So: *rates did most of the work, but not all of it.*

## Does the Picture Survive Robustness Checks?

Two honest worry points for the headline premium.

**Is this about the top of the market?** Maybe Travis's "median" is
pulled up by a Westlake-and-Tarrytown shelf a typical migrator never
considers. ZHVI's tiered series lets us check directly. The three
tiers run in the expected order — top (~34 %) > mid (~32 %) > bottom
(~23 %) — and all three are positive and persistent. The story
weakens at the bottom of the market: a first-time buyer shopping in
the 0-to-33rd percentile gets a smaller relative discount moving to
Hays (23 %) than a mid-tier buyer does (32 %). That dependence on tier
is real, and it would be wrong to claim "the premium is identical at
every price point." But the premium is positive and economically
meaningful across the whole distribution, not a Westlake artifact.

![Robustness across ZHVI tiers](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_tiers.png)

**Is this an Austin-specific oddity?** To test whether a core-over-
edge premium is a general Texas metro phenomenon or something
Austin-specific, compare to the DFW pair most analogous to Travis/
Hays: Collin County (the wealthier core suburb) over Denton County
(the faster-growing edge). Collin *is* more expensive than Denton,
consistent with the pattern — but only by about **9 %** on average,
and that premium has been drifting upward toward roughly 10 %. The
magnitude is nowhere near Austin's.

![Austin vs. DFW](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_out_of_metro.png)

So the *existence* of a core-over-edge premium looks general. Its
*size* — and in particular the Austin-scale ~30 % number — does not.
Hays County's growth story runs on an unusually large affordability
arbitrage, not on a universal one. The DFW edge (Denton) is almost as
expensive as its core (Collin). The Austin edge (Hays) is not.

## Does the Gap Actually Drive Migration?

Prices are a pressure, not a flow. The Hays migration story has
assumed that the price gap is the forcing function; IRS Statistics of
Income county-to-county migration data let us at least sketch the
correlation. Annual in-migration to Hays (exemptions, origin ≠ Hays)
plotted against the prior-year average Travis → Hays gap:

![Migration response](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/migration_response.png)

With only five years of SOI releases and one lag consumed, this is
illustrative, not inferential — the standard errors are large enough
to swallow any coefficient we report. Still, the slope has the sign
the story would predict. A post with real identification, not just
correlation, would need IV on rates or a shift-share pulling gap
variation out of metro-wide price movements. That is a bigger post.

## What This Adds Up To

The first version of this analysis made three claims, all roughly
right, none of them quite rigorous:

1. The absolute gap is volatile and has narrowed from peak.
2. The percentage premium is constant.
3. Rates drove the monthly cost of the gap.

The rigorous version updates each:

1. The absolute nominal gap did narrow from peak — from $157K in
   June 2022 to about $107K now, a $50K round-trip. The *real* gap
   (CPI-deflated) is closer to flat. Both framings survive
   triangulation across Zillow, FHFA, and Realtor.
2. The premium is *not* constant. It rose from about 32 % at the
   start of 2020 to a peak near 38 % in mid-2021, and has been
   drifting back down toward 29 % since. The Quandt sup-F rejects the
   constant-mean null decisively. What is stable is the *range* — the
   premium has lived between roughly 29 and 38 percent throughout.
   For a migration decision a range is still usable; it just isn't a
   point estimate.
3. The P&I story is the dominant story, but once you include the
   Hays-specific MUD and insurance surcharges and the Travis-specific
   property-tax premium, the full PITI gap is roughly $150/month
   smaller than P&I alone suggests at today's rates. The doubling
   still happens. It's just a smaller double.

And the cross-metro comparison reframes the claim one more time: the
Austin core-over-edge premium is unusually large. DFW's Collin-over-
Denton analog runs at about 9 %. Whatever is driving Hays's growth is
specifically about Austin's price structure, not a general Texas
suburbanization force.

None of which changes the punchline: the migration pressure that
built Hays County over the last fifteen years hasn't eased. If
anything, at 7 % rates it's heavier on a monthly-payment basis than
it was when rates were at 3 %.

## Limitations

A short, honest list of what this analysis does *not* do.

- **County medians hide city variation.** Kyle ≠ Dripping Springs ≠
  San Marcos. A city-level analog is a next post.
- **The PITI property-tax and insurance estimates are point values
  with known dispersion.** Effective rates vary by ISD and by city by
  ±0.2 percentage points. A full sensitivity pass is in
  `analysis.breakeven_tax()` (stubbed but not yet rendered as a
  figure). The MUD assumption (Hays has one, Travis doesn't) holds
  for mid-tier median addresses; fringe Travis addresses can carry
  MUDs too.
- **The migration regression is correlational with n = 3.** Do not
  read a policy elasticity out of it.
- **All price series are nominal-dollar, pre-tax.** A household with
  capital-gains-exclusion considerations on an Austin sale will face
  a different math than the stylized first-time buyer implicit above.

---

## Sources

Zillow Home Value Index (all homes, tiered mid / bottom / top, SA,
smoothed, county). Zillow median price per square foot. FHFA House
Price Index, all-transactions, county (quarterly). Realtor.com median
listing price (FRED). Freddie Mac Primary Mortgage Market Survey 30-
year fixed rate (FRED: `MORTGAGE30US`). BLS CPI-U All items (FRED:
`CPIAUCSL`). IRS Statistics of Income county-to-county migration
inflows, 2019–2023. Texas Comptroller Truth-in-Taxation for effective
property tax rates. Texas Department of Insurance 2024 Home Insurance
Price Comparison for annual premiums.

Replication code, data manifest, and per-file checksums:
[southbound-35/posts/affordability-gap][repl].

[growth]: {{ site.baseurl }}/posts/2026/04/hays-county-growth/
[projections]: {{ site.baseurl }}/posts/2026/04/hays-county-projections/
[repl]: https://github.com/scottlangford2/southbound-35/tree/main/posts/affordability-gap

## Disclosure

This blog post was written with the assistance of Claude (Anthropic).
Claude helped with data research, code, and drafting. All analysis and
editorial judgment are the author's.
