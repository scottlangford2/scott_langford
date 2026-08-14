---
layout: archive
title: "Data"
permalink: /data/
author_profile: true
---

{% include base_path %}

Most of what American local governments and nonprofits disclose is technically public and practically unusable. A city's annual financial report is a PDF. Its council deliberations are minutes, agendas, and video. A nonprofit's finances are a scanned return. Each document is available to anyone who asks for that one document — and almost none of it can be read across thousands of organizations at once, which is what answering an empirical question actually requires.

So I build the datasets my research needs out of those records. Two are in active use.

## Local government meeting text

A corpus of the documentary record of American local government — agendas, minutes, staff reports, and meeting transcripts — assembled from the platforms cities and counties publish through, including Legistar, Granicus, CivicPlus, eSCRIBE, PrimeGov, CivicClerk, and Municode Meetings.

The corpus currently holds roughly **2.1 million records**, of which about **178,000 are substantial meeting documents** of 750 words or more. It is built from roughly 4,600 verified government portals, discovered by fingerprinting real municipal websites rather than guessing at URLs.

Coverage is deliberately measured rather than assumed. Only a minority of the roughly 35,000 U.S. municipalities publish through any discoverable meeting-text platform at all, and platform adoption tracks population and staff capacity — which makes the gap a finding in its own right about who leaves a searchable public record and who does not. Every analysis carries the corresponding selection weights.

## Local government financial statements

A panel of city and county finances built by machine extraction from Annual Comprehensive Financial Reports — the audited statements governments publish each year and almost no one reads comparably.

Existing sources for this kind of question are coarse and lagged. ACFRs are annual, detailed, and specific to the reporting government, which makes them the right instrument for asking what a shock actually does to a balance sheet: which funds absorb it, what happens to unrestricted net position, and how long the effect persists. The panel is linked to hazard and property-value data for that purpose.

## Access

Both datasets are in active use and being documented for publication; methods papers describing their construction, coverage, and validation are in progress. Once those are out, the derived data will be released to the extent the underlying sources permit.

Some inputs cannot be redistributed. Hazard-loss data used in several projects comes from a licensed subscription source and is not mine to share; the public-record documents and the code that assembles them are a different matter. If you are working on something these would help with, [get in touch](mailto:scottlangford@txstate.edu) — I would rather they get used than sit on a drive.

## Replication

Code and data for published work are on the [replication]({{ '/replication/' | relative_url }}) page.
