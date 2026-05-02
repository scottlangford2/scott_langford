---
title: 'Did LIV Golfers Get Worse After They Defected?'
date: 2026-04-30
permalink: /posts/2026/04/liv-defectors-majors/
categories:
  - sports
tags:
  - data analysis
  - sports
  - golf
  - causal inference
related: false
---

Since 2022, more than thirty PGA Tour pros have left for the Saudi-backed LIV
Golf league, lured by guaranteed contracts reportedly worth tens or hundreds
of millions of dollars. The complaint from those who stayed has been blunt:
LIV's 54-hole, no-cut, shotgun-start format is "exhibition golf," and players
who take the money will get rusty. The defectors say the opposite — that the
lighter schedule lets them practice harder and play fresher. So who's right?

The clean way to ask the question is to look at the four times a year when
defectors and stayers play the same course in the same field on the same
days: the majors. I scraped every round of every men's major from 2018
through the 2026 Masters from Wikipedia — 31 tournaments, ~17,500
player-rounds — and ran a difference-in-differences regression. Each
defector's strokes-versus-the-field is compared, before vs. after they
signed with LIV, against the same shift among comparable stayers in the
same rounds. Because every player is being compared to the same field on
the same day, course difficulty and field strength cancel out.

The headline answer is: **on average, defectors got about half a stroke per
round worse — but the average hides almost everything interesting.** Once
you split by player type, the story is much sharper.

## The story is in the heterogeneity

Splitting the 30 defectors into three buckets — *stars* (pre-defection
scoring at least 1.5 strokes better than the major field, on average),
*older* (38+ at defection, not stars), and *journeymen* (everyone else) —
gives this:

![Effect by player type](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/liv-defectors-majors/heterogeneity.png)

The stars — Brooks Koepka, Cameron Smith, Dustin Johnson, Jon Rahm, Louis
Oosthuizen, Patrick Reed, and Pat Perez — got dramatically worse:
**+1.58 strokes per round at majors** (SE 0.33), large enough that the
95% CI clears zero by a wide margin. Translated to a 4-round major, that's
roughly the difference between contending and missing the cut. The older
defectors and the journeymen, by contrast, are statistically
indistinguishable from no effect (and the journeyman point estimate is
actually *negative*).

The popular narrative — "LIV makes you rusty" — turns out to apply
specifically to the players who arrived at LIV at the top of their game.
Older defectors were declining anyway; journeymen weren't good enough at
majors for LIV to obviously hurt their relative standing.

## How robust is the average effect?

The aggregate +0.48 stroke estimate holds up across specifications:

![Spec comparison](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/liv-defectors-majors/spec_comparison.png)

Adding age + age² (to net out normal aging) barely moves the estimate.
Restricting to all four rounds pulls it down slightly to +0.40; R3+R4 only
gives +0.29. Most importantly, when I build a *matched* control group —
three nearest-neighbor stayers per defector, matched on pre-period skill,
age, and major appearances — the estimate falls to **+0.25 strokes**
(SE 0.32). That last spec is the cleanest read because it compares each
defector to a handful of stayers who looked very similar pre-2022. Across
all five specs the standard errors are wide enough that we can't reject
zero, but every point estimate sits to the right of it.

## Cuts

A separate outcome — the probability of making the cut at a major —
points the same way:

![Cut rates pre vs. post](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/liv-defectors-majors/cut_rates.png)

Each dot is one defector; the dashed line is "no change." Most dots sit
below the line. The DiD estimate is a **−7.9 percentage point** drop in
cut probability after defection (SE 5.6). The visual standouts are Phil
Mickelson (73% → 36%), Bubba Watson (69% → 25%), Dustin Johnson (76% →
60%), and Cameron Smith (84% → 54%).

Cut rates are tricky for a different reason: many defectors lost OWGR
points and major exemptions over time, so the post-period cut rate is
conditional on still getting *into* the major. Defectors who kept showing
up were positively selected on quality, which biases the apparent decline
*downward*. A simple Lee-style bound, trimming the top of the post-period
distribution to match the appearance rate, says the true effect on cuts
could be anywhere from a small drop (−6.9pp) to a much larger one
(−57.8pp). The point estimate is the optimistic end of that range.

## Bryson DeChambeau is a real counterexample

The clear exception to the "stars got worse" story is Bryson DeChambeau,
who became a one-man rebuttal to the rust narrative — and won the 2024 US
Open as a LIV member.

![DeChambeau time series](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/liv-defectors-majors/dechambeau.png)

His scoring has been *better* relative to major fields after the move
than before. He's classified as a journeyman in my buckets only because
he was injured and underperforming in the year right before he signed; if
you'd asked anyone in 2020 (the year he won the US Open the first time),
"star" would have been the obvious bucket. So the existence-proof is
real: LIV play does not, by itself, prevent peak major performance.
Whatever is hurting Brooks Koepka and Cameron Smith is not just "fewer
rounds against good players."

## What this doesn't tell us

A few honest caveats:

- **Major-eligibility selection.** The post-period sample is selected on
  still being *invited* to majors — which positively selects on play. The
  Lee bound on cuts says this could matter a lot.
- **Pre-trend issue.** A formal event study (in [the
  appendix](/posts/2026/04/liv-defectors-majors-appendix/)) shows
  defectors were unusually *good* three majors before they signed, which
  fails a parallel-trends test. The matched-control spec is partly
  designed around this; it gives the smallest estimate (+0.25).
- **Mechanism.** I can't tell from this whether the decline is from less
  competitive play, fewer rounds per year, different course types on LIV,
  or something psychological. Strokes-gained data (which LIV doesn't
  publish) would be needed to decompose.
- **Small post-period for late defectors.** Tyrrell Hatton, who shows up
  as the biggest *improver*, has played only nine majors as a LIV member.

## Bottom line

The popular "LIV makes you rusty" claim is **mostly true for the stars** —
Brooks, Smith, DJ, Rahm, Oosthuizen, Reed — who got noticeably worse at
majors after defecting, by an amount large enough to materially affect
their results. It's **not really true for everyone else**: the older and
journeyman defectors look indistinguishable from how they'd have done
anyway. And **DeChambeau is a real existence proof** that the right
player can be a peak major performer while playing only LIV golf the rest
of the year.

If you want one number, it's: among defectors who were elite before they
left, expect about **1.5 fewer strokes of edge per round at majors**,
going from "regularly contend" to "regularly make the cut and finish
mid-pack." If you're an older or middling defector, the major-tournament
evidence is consistent with no real change.

---

*See the [appendix](/posts/2026/04/liv-defectors-majors-appendix/) for
the formal event study, the full per-defector breakdown, and the
round-distribution view. Code, scraped data, and all figures are in the
[replication package](https://github.com/scottlangford2/southbound-35/tree/main/posts/liv-defectors-majors).*
