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

This post takes the "percentage premium is constant" claim and tests
it properly — mean + HAC confidence interval, AR(1) persistence, and
an unknown-break sup-F test — on ZHVI mid-tier data from 2020 through
March 2026. Two follow-up questions (triangulating the premium across
FHFA and Realtor series, and decomposing the full PITI monthly cost)
are staged in the [replication folder][repl] but not yet rendered in
this post; a subsequent rigor-pass post will fold them in. Everything
here is reproducible on a fresh ZHVI release from the code in that
folder.

## Everyone Rode the Same Wave

Start with levels. The Zillow Home Value Index for Travis, Williamson,
and Hays rose sharply through 2021 and early 2022, peaked inside a few
months of each other in mid-2022, and has been grinding lower since.
The ordering that makes the growth story work — Travis on top, Hays at
the bottom — never breaks.

![Central Texas home values, 2020 → present](https://raw.githubusercontent.com/scottlangford2/scott_langford/claude/add-hays-discount-post-tL4eQ/images/hays-discount/gap_levels.png)

## The Dollar Gap Bulged, Then Pulled Back

Subtract, and the absolute Travis-over-Hays gap ran from about $93K at
the start of 2020, peaked near $157K in June 2022, and has ground
back down to $107K as of the March 2026 release. Williamson tracks
the same shape at a smaller magnitude — never more than about $47K
over Hays, currently about $34K.

![Absolute gap over Hays, 2020 → present](https://raw.githubusercontent.com/scottlangford2/scott_langford/claude/add-hays-discount-post-tL4eQ/images/hays-discount/gap_absolute.png)

That $50K peak-to-today swing in the Travis-Hays gap is not small.
If you stopped here you might conclude that Hays's relative advantage
eroded during the pandemic boom and then fully recovered. You would
be reading the wrong statistic.

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

![Premium statistics](https://raw.githubusercontent.com/scottlangford2/scott_langford/claude/add-hays-discount-post-tL4eQ/images/hays-discount/gap_relative_stats.png)

In plain English: the premium is not a constant. It spent roughly a
year elevated during the pandemic boom and has been grinding back down
for the four years since. What is stable, loosely, is the *range* —
the premium has lived between roughly 29 % and 38 % throughout, never
collapsing toward zero and never running above 40 %. A range is still
a useful object for a migration decision. It just isn't a point.

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

![Robustness across ZHVI tiers](https://raw.githubusercontent.com/scottlangford2/scott_langford/claude/add-hays-discount-post-tL4eQ/images/hays-discount/gap_tiers.png)

**Is this an Austin-specific oddity?** To test whether a core-over-
edge premium is a general Texas metro phenomenon or something
Austin-specific, compare to the DFW pair most analogous to Travis/
Hays: Collin County (the wealthier core suburb) over Denton County
(the faster-growing edge). Collin *is* more expensive than Denton,
consistent with the pattern — but only by about **9 %** on average,
and that premium has been drifting upward toward roughly 10 %. The
magnitude is nowhere near Austin's.

![Austin vs. DFW](https://raw.githubusercontent.com/scottlangford2/scott_langford/claude/add-hays-discount-post-tL4eQ/images/hays-discount/gap_out_of_metro.png)

So the *existence* of a core-over-edge premium looks general. Its
*size* — and in particular the Austin-scale ~30 % number — does not.
Hays County's growth story runs on an unusually large affordability
arbitrage, not on a universal one. The DFW edge (Denton) is almost as
expensive as its core (Collin). The Austin edge (Hays) is not.

## What This Adds Up To

Three findings, all tested on the same ZHVI mid-tier window:

1. **The absolute dollar gap is volatile.** Travis-over-Hays ran
   from $93K at the start of 2020 to $157K in June 2022 and back to
   $107K now — a $50K peak-to-today round-trip. The headline number
   moves month-to-month, revises with each release, and is a poor
   summary of affordability pressure on its own.
2. **The percentage premium is *not* constant.** It rose from about
   32 % in early 2020 to a peak near 38 % in mid-2021 and has been
   reverting toward 29 % since. The Quandt sup-F test rejects the
   constant-mean null decisively (sup-F ≈ 199 at December 2021). What
   *is* stable is the range — the series has lived between roughly
   29 % and 38 % throughout. For a migration decision a range is
   still usable. It just isn't a point estimate.
3. **The premium isn't universal Texas.** Austin's core-over-edge
   premium is ~32 % on average. DFW's closest analog — Collin over
   Denton — is ~9 %. Hays's affordability arbitrage is specifically
   about Austin's price structure, not a general Texas
   suburbanization regularity.

None of which changes the punchline: the migration pressure that
built Hays County over the last fifteen years hasn't eased. The
dollar gap has narrowed and the percentage premium has come off its
peak, but both remain large enough to keep pulling buyers south of
I-35.

## Limitations

A short, honest list of what this post does *not* cover.

- **County medians hide city variation.** Kyle ≠ Dripping Springs ≠
  San Marcos. A city-level analog is a next post.
- **Only one price series is used here.** ZHVI is Zillow's imputed
  value index; it is not a transaction index. FHFA's all-transactions
  HPI and Realtor.com's listing series would be useful cross-checks.
  The replication code pulls them; the cross-check will appear in a
  follow-up post.
- **Monthly cost (PITI) is not analyzed.** The property-tax
  differential, Hays's MUD/PID surcharges, and the mortgage-rate
  series all matter for the real monthly-payment math and are in the
  replication code. A full PITI decomposition is a follow-up post.
- **Migration is not modeled here.** This post documents the *price
  pressure*. The separate question of how county-to-county migration
  flows respond to that pressure will use IRS Statistics of Income
  migration data in a follow-up.
- **All price series are nominal-dollar, pre-tax.** A household with
  capital-gains-exclusion considerations on an Austin sale will face
  different math than the stylized first-time buyer implicit above.

---

## Sources

Zillow Home Value Index (all homes, tiered mid / bottom / top, SA,
smoothed, county level). Counties analyzed: Travis (48453),
Williamson (48491), Hays (48209), Collin (48085), Denton (48121).
Statistical tests (Newey–West HAC standard error of the mean,
AR(1) persistence via OLS, Quandt–Andrews sup-F unknown-break test)
computed in `analysis.py`.

Replication code, data manifest, and per-file checksums:
[southbound-35/posts/affordability-gap][repl].

[growth]: {{ site.baseurl }}/posts/2026/04/hays-county-growth/
[projections]: {{ site.baseurl }}/posts/2026/04/hays-county-projections/
[repl]: https://github.com/scottlangford2/southbound-35/tree/main/posts/affordability-gap

## Disclosure

This blog post was written with the assistance of Claude (Anthropic).
Claude helped with data research, code, and drafting. All analysis and
editorial judgment are the author's.
