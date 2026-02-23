---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

Education
======
* Ph.D in Public Policy, University of North Carolina, Chapel Hill, 2022
* M.S. in Biochemistry and Biophysics, University of North Carolina, Chapel Hill, 2016
* B.S. in Chemistry, University of North Carolina, Wilmington, 2012

Work Experience
======
* 2025-Present: Assistant Professor
  * Texas State University
  * Department of Political Science, MPA Program
* 2022-2025: Post-Doctoral Research Fellow
  * Arizona State University
  * School of Public Affairs

Grants & Funding
======
* Kenan Institute for Private Enterprise, University of North Carolina at Chapel Hill, $10,000
* Contract, Town of Clayton, $65,000

Technical Skills
======
* STATA, Tableau, ArcGIS, Qualtrics, LaTeX, R, Python

Professional Memberships
======
* Association for Public Policy Analysis and Management (APPAM)
* American Political Science Association (APSA)
* American Society for Public Administration (ASPA)

Publications
======
{% for category in site.research_category %}
<h3>{{ category[1].title }}</h3>
  <ul>{% for post in site.research reversed %}{% if post.category == category[0] %}
    {% include archive-single-cv.html %}
  {% endif %}{% endfor %}</ul>
{% endfor %}

Teaching
======
  <ul>{% for post in site.teaching reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
