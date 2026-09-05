# House Template — the site-factory canonical scaffold

A themeable, static **Astro** template (ticket 10 of `site-factory-v1`). It is the factory's reusable
asset: to start a new site, **copy this folder into `sites/<slug>/`** (its own independent git repo,
gitignored by the harness) and edit one config file.

Realises the design decisions in
[`.scratch/site-factory-v1/issues/09-house-template.md`](../../.scratch/site-factory-v1/issues/09-house-template.md)
— one themeable base + layout modes + skin palette — on the stack picked in
[ticket 08](../../.scratch/site-factory-v1/issues/08-pick-stack.md) (Astro, `output: 'static'`,
vanilla-JS islands).

## Quick start

```bash
cd factory/house-template
npm install
npm run dev      # http://localhost:4321
npm run build    # -> dist/  (static, deploy to Cloudflare Pages)
npm run preview
```

## Standing up a new site

1. Copy `factory/house-template/` → `sites/<slug>/`.
2. Edit **`src/lib/site.config.mjs`** — the only file you must touch:
   - identity (`url`, `name`, `tagline`), `skin`, `layoutMode`, nav/footer.
   - monetization + analytics stay **off** until launch (see below).
3. Replace `src/data/catalog.json` with your dataset (same `platforms/categories/products` shape, or
   adapt the pages).
4. Drop real brand assets into `public/` (`favicon.svg`, `og-cover.png`, `logo.png`, `fonts/*.woff2`).
5. `npm install && npm run build`, then wire GitHub → Cloudflare Pages (ticket 06 checklist).

## What's in the box

| Area | Where | Notes |
|---|---|---|
| Base app-shell layout (dir 08) | `src/layouts/Layout.astro` | sidebar rail + main pane, skip link, landmarks |
| Layout modes (list / grid, dir 08 vs 05) | `SITE.layoutMode` + `.results--list/grid` | one flag, same components |
| Tool-hero variant (dir 02) | `src/pages/calculator.astro` + `.tool-hero` | centered tool + right rail hole |
| Token / skin system (2-layer ramps) | `src/styles/tokens.css` | neutral default + editorial/technical/dark/playful; dark-mode via role re-point |
| Base + component styles | `src/styles/base.css` | references role tokens only |
| Brand fonts (CWV-safe) | `tokens.css` + `public/fonts/` | self-hosted variable WOFF2 + metric-matched fallback, `font-display: optional` + preload |
| Logo | `Header.astro` | inline-SVG `currentColor` mark, recolors per skin |
| SEO baseline (ticket 03) | `src/lib/seo.mjs`, `BaseHead.astro` | canonical, OG/Twitter, `WebApplication`/`BreadcrumbList`/`ItemList`/`Organization`/`WebSite` JSON-LD; no FAQPage |
| Sitemap + robots | `@astrojs/sitemap`, `src/pages/robots.txt.ts` | build step |
| Page set | `src/pages/` | tool, long-tail `[platform]/[category]`, methodology, FAQ, About, Contact, Privacy, Disclosure |
| Ad holes (ticket 04) | `src/components/AdSlot.astro` | reserved-space, off by default |
| Affiliate holes (ticket 05) | `src/components/AffiliateLink.astro` | data-driven, `rel="sponsored nofollow"`, off by default |
| Consent scaffold + analytics slot | `Layout.astro`, `BaseHead.astro` | inert until a provider is set |

## Skins

Set `SITE.skin` to `neutral` (default), `editorial`, `technical`, `dark`, or `playful`. A skin overrides
**only** the Layer-1 color ramps (and optionally radius/display font) in `tokens.css`; no markup or
component CSS changes. Light/dark is a separate axis: `SITE.enableDarkModeToggle` adds a header toggle
that re-points the same semantic roles (no extra skin needed).

## Turning on monetization (post-launch, zero re-architecting)

- **Ads:** set `SITE.monetization.ads.enabled = true` and `adsensePublisherId`. Reserved `AdSlot`
  boxes fill in place — no reflow. Update `public/ads.txt`.
- **Affiliate:** set `SITE.monetization.affiliate.enabled = true`, then flip each dataset row's
  `affiliate.affiliate_enabled` and set `affiliate_url`. Off rows render as plain text.
- **Analytics:** set `SITE.analytics.provider` (`cloudflare` recommended — cookieless, no consent
  banner) and `token`.

## Conventions this template assumes (factory-wide)

- Astro `output: 'static'`, no SSR adapter.
- Islands are **vanilla JS** by default (the two `<script>` blocks in `index.astro` and
  `calculator.astro`). Reach for Preact only if a tool crosses a genuine interdependent-reactive-state
  threshold (ticket 08).
- Never invent search/CPC/traffic/revenue numbers; dataset entries are hand-verified.
