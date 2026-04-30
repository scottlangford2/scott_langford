---
title: 'LIV Defectors at the Majors — Appendix'
date: 2026-04-30
permalink: /posts/2026/04/liv-defectors-majors-appendix/
tags:
  - data analysis
  - sports
  - golf
  - causal inference
related: false
---

Supplementary figures and discussion for [Did LIV Golfers Get Worse After
They Defected?](/posts/2026/04/liv-defectors-majors/).

## A1 — Per-defector breakdown

Each defector's average strokes-vs-field at majors, before vs. after
defection (R1+R2 only, so no cut selection):

![Per-defector deltas](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/liv-defectors-majors/player_deltas.png)

Roughly half the defectors got worse and about a third got better, with
the magnitudes among the worst movers (Oosthuizen, Watson, DJ, Grace) far
larger than among the best (Hatton, Westwood, Poulter, Burmester). The
small-sample defectors (Westwood, Poulter, Munoz at n = 2 rounds) are
essentially one major's data and shouldn't be over-read. The "n =" labels
on each bar are post-defection player-rounds in the R1+R2 sample.

The unweighted distribution explains why the regression gives the picture
it does: the worst movers are mostly players who were already very good
(DJ, Smith, Brooks) and slipped a lot, while the improvers are journeymen
or older players whose pre-period bars were already close to the field
mean.

## A2 — Formal event study

Letting the data say *when* the change happened: separate coefficients at
each event time relative to defection, with player FE, major×round FE,
and an age polynomial as controls. Event time t = −1 (the major
immediately before defection) is omitted as the reference period.

![Event study](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/liv-defectors-majors/event_study.png)

The post-defection coefficients (in red) are mostly positive — defectors
are scoring worse relative to the field than they did at t = −1 — but the
confidence intervals are wide and there's no clean step-function jump.
Nothing dramatic happens *exactly* at the defection point; the
post-period averages drift positive over time.

The bigger problem is on the pre-defection side. The leads at t = −2 and
t = −1 sit close to zero (good — that's what parallel trends would
predict), but the t = −3 coefficient is about −1.6 strokes — defectors
were *unusually good* three majors before they signed. The maximum
absolute t-statistic across the pre-period leads is **2.24**, which fails
a conventional parallel-trends test.

Two stories could explain that dip:

1. **Reverse causation in selection.** A strong major run might have
   helped attract LIV's offer (or at least raised the player's
   reservation wage). If players sign during or just after a hot streak,
   the t = −3 to t = −1 window naturally shows above-trend performance,
   and any decline post-signing partly reflects mean reversion.
2. **Noise.** With ~20 players observable at t = −3 and a single major's
   worth of data, a t-stat of 2.24 isn't extraordinary.

The matched-control specification in the main post is partly designed
around this issue. It compares each defector to similar stayers in the
same calendar year, which absorbs much of any reversion-to-mean trend
that's common across the cohort. That spec gives the smallest estimate
(+0.25 strokes), consistent with the idea that some of the headline
+0.48 is mean reversion rather than a LIV effect.

## A3 — Distribution view

For readers who prefer raw distributions to point estimates, here's the
density of defector rounds (R1+R2, full field) before and after defection:

![Distribution of defector rounds](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/liv-defectors-majors/distribution.png)

The pre-LIV distribution (grey) is centered slightly to the left of the
post-LIV distribution (red), and the post-LIV side has a slightly fatter
right tail — more genuine blowup rounds. The means differ by about 0.3
strokes, which is consistent with the regression estimates. The huge
overlap is why the standard errors are wide: a defector's typical round
is well within the noise of any single major.

## A4 — Round-specific effects

The DiD coefficient broken out by round (each is a separate regression
with player FE, major×round FE, and age controls):

| Round | β   | SE   | N rounds |
|-------|-----|------|----------|
| 1     | +0.31 | 0.34 | 2,904 |
| 2     | +0.60 | 0.38 | 2,871 |
| 3     | +0.34 | 0.41 | 1,516 |
| 4     | +0.36 | 0.39 | 1,514 |

There's no obvious "Sunday pressure" story — the effect doesn't ramp up
through the rounds. The R2 estimate is the largest of the four, but the
differences across rounds are within standard-error distance.

## A5 — Sample and definitions

- **Universe.** All four men's major championships from 2018 through the
  2026 Masters: Masters, PGA Championship, US Open, Open Championship.
  31 tournaments, 17,532 player-round observations.
- **Defectors.** Thirty named PGA Tour pros who signed multi-year LIV
  contracts between June 2022 and February 2024. Defection date = first
  LIV event played.
- **Outcome.** Strokes vs. round-field-mean. The "field" is every
  player who posted a score that round; for R3 and R4 that's
  cut-makers only. Lower scores = better.
- **Player typing.** *Star* if average pre-LIV strokes-vs-field
  ≤ −1.5 (so player was scoring at least 1.5 strokes better than the
  major field on average pre-defection). *Older* if 38+ at first LIV
  event, not a star. *Journeyman* otherwise.
- **Birthdates.** Hardcoded for the 30 defectors. For the rest of the
  field (~500 players), scraped from Wikipedia infobox `class="bday"`
  microformat with a few manual corrections for disambiguation errors
  (golfers who shared names with historical figures).

Code and cached data: [southbound-35 / posts /
liv-defectors-majors](https://github.com/scottlangford2/southbound-35/tree/main/posts/liv-defectors-majors).
