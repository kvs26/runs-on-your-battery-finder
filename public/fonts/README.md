# Brand fonts

Drop the site's self-hosted fonts here:

- `brand.woff2` — the variable body font (weights 100–900), Latin-subset, WOFF2 only.
- `brand-display.woff2` — optional heading/display font (weights 400–800).

Both are wired in `src/styles/tokens.css` with a metric-matched system fallback and
`font-display: optional` (body) / `swap` (display), and the body font is `<link rel=preload>`ed
in `src/components/BaseHead.astro`. Because the body font uses `font-display: optional`, a missing
file degrades to the system stack with **zero layout shift** — the template builds and renders fine
without these files, so add them when the brand font is chosen.

After adding a real `brand.woff2`, tune the fallback metrics in the
`@font-face { font-family: 'Brand Sans Fallback' }` block (`size-adjust`, `ascent-override`,
`descent-override`) to match it so the swap shifts nothing. Tools: the fallback-font generator in
your build chain, or measure ascent/descent from the font's `hhea`/`OS/2` tables.
