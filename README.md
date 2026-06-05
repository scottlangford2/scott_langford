# W. Scott Langford — academic website

Source for [**scottlangford2.github.io/scott_langford**](https://scottlangford2.github.io/scott_langford/) — the personal academic site of W. Scott Langford, Assistant Professor of Public Administration at Texas State University. Built on Jekyll using a customized fork of the [**academicpages**](https://academicpages.github.io/) theme (itself a fork of Minimal Mistakes).

## What's here

- **Research, CV, teaching, talks** — standard academic site sections, generated from Markdown in `_research/`, `_pages/cv.md`, `_teaching/`, and `_talks/`.
- **Southbound 35** — a blog on Texas public finance and economic development (the I-35 corridor), published Mondays at 5 AM Central. Posts live in `_posts/`, with replication code under [`_portfolio/`](https://scottlangford2.github.io/scott_langford/portfolio/).
- **Self-hosted mailer** — see `mailer/` in the companion [`southbound-35`](https://github.com/scottlangford2/southbound-35) repo. Sends each subscriber an individual email (no BCC) the morning a post goes live.

## How to cite

A [`CITATION.cff`](./CITATION.cff) is included; GitHub will render a "Cite this repository" button in the right sidebar.

## Design

The site uses a custom v5 design language layered over academicpages via [`_includes/head/custom.html`](./_includes/head/custom.html):

- **Type:** Spectral (serif body), DM Sans (uppercase section labels)
- **Palette:** Texas State maroon `#501214`, bright gold `#D7BD8A`, cream `#faf8f5`, ink `#1a1a1a`
- **Layout:** right-rail author sidebar (flipped from theme default via `flex-direction: row-reverse`), 720px column, justified body, hairline section dividers with gold dots, print stylesheet

The mockup that established the design language lives at [`/sample-html/`](./sample-html/index.html).

## Local development

```bash
bundle install
bundle exec jekyll serve
```

The site is served by GitHub Pages on push. A scheduled GitHub Actions workflow rebuilds at 5 AM CT Mondays so future-dated posts publish on time (`future: false` + empty-commit trigger; see `.github/workflows/`).

## Credits

Theme adapted from [academicpages/academicpages.github.io](https://github.com/academicpages/academicpages.github.io) (MIT license). All site content © W. Scott Langford unless otherwise noted.
