# Region & platform notes

Site-specific facts and decisions for the multi-region (US + UK/DE/FR/IT/ES) build. Read this before
populating or refreshing `src/data/catalog.json`. Full rationale lives in the PRD at
`pipeline/power-tool-battery-compat/ideas/runs-on-your-battery-finder/prd.md`.

## Regions

- Covered regions: **US, UK, DE, FR, IT, ES** (six). These codes are **internal only** — used for the
  dataset `regions[]` values, the `affiliate` per-region map keys, and the `localStorage` value. The
  toggle **shows visitors full country names**: United States, United Kingdom, Germany, France, Italy,
  Spain.
- **Client-side region toggle, same URLs.** One set of `[platform]/[category]` pages; a toggle
  (default `US`, persisted in `localStorage`) swaps each row's buy link to the matching Amazon
  marketplace and hides platforms not sold in the selected region. No `/uk/…` or `/de/…` routes, no
  IP geolocation.
- **No site-copy translation.** Nav, methodology, FAQ, and product notes stay English-only. The toggle
  changes buy links and platform visibility only.
- **No price/currency display.** The catalog stores buy links only, never a price — so the toggle only
  swaps the marketplace link, no GBP/EUR formatting needed.

## Platform equivalence — CRITICAL

- **Ryobi is a hard exception. Never merge US and UK/EU Ryobi.** Ryobi ONE+ in the US (and Canada/
  Australia) is licensed to **TTI**; Ryobi in the UK/EU is licensed to **Positec** — same brand name,
  **physically incompatible** battery packs. Model them as two separate platform slugs (e.g.
  `ryobi-18v-one` for US/TTI and `ryobi-one-eu` for UK/EU/Positec). Source EU/UK Ryobi data only from
  Positec-line listings/spec pages; never assume US/TTI compatibility carries over. Getting this wrong
  publishes exactly the unsafe compatibility claim this site exists to prevent.
- **DeWalt stays one platform.** US "20V MAX" is badged "**XR 18V**" in the UK/EU, but it's the same
  manufacturer and same battery interface — keep a single slug (`dewalt-20v-max`) with a `region_note`
  documenting the badge difference.
- **Watch for other same-name / different-licensee splits.** This pattern is not unique to Ryobi.
  Verify any brand's EU/UK licensee before assuming US rows apply.
- **US-only house brands** (HART, Craftsman, Bauer, Kobalt, and any others confirmed US-only) get
  `regions: ["US"]` and are hidden outside the US region. Confirm WORX Power Share and Greenworks 24V
  regional availability during the EU data pass rather than assuming.

## Schema notes

- Each platform entry gains `regions: string[]` (subset of the six region codes) marking where it's
  sold.
- Each product's `affiliate` field becomes a per-region map
  (`{ US: {…}, UK: {…}, DE: {…}, FR: {…}, IT: {…}, ES: {…} }`), each entry with its own
  `asin` / `affiliate_url` / `affiliate_enabled` / `requires_disclosure`.
- A region key is added only once a real, verified buy link exists for that region. An unpopulated
  region key = "not yet verified there," and the row is hidden (not shown broken) when that region is
  selected.

## Buy links vs affiliate links

- **A buy link is not an affiliate link.** Each row's `affiliate_url` is just the best available
  outbound product link — Amazon listing/search **or** a manufacturer/retailer product page (Home
  Depot, milwaukeetool.com, worx.com, greenworkstools.com, etc.) when that's more precise. A non-Amazon
  link is a **permanent valid value**, not a placeholder to swap for Amazon later.
- **Affiliate monetization is off entirely right now** — all links render as plain outbound links,
  `SITE.monetization.affiliate.enabled = false`, no row's `affiliate_enabled` set.
- When affiliate is eventually turned on it is **Amazon-only**: only Amazon links get affiliate tagging
  + FTC disclosure; manufacturer/retailer links always stay plain outbound links.

## Monetization

- Amazon Associates runs a **separate program per marketplace** (US / UK / DE / FR / IT / ES), each with
  its own signup and tracking id. Prepare per-region Amazon `affiliate_url`/`asin` data now, but keep
  `SITE.monetization.affiliate.enabled = false` everywhere until accounts are set up. US commission
  rates (Tools/Home Improvement/Lawn & Garden/Outdoors 3.00%, Kitchen 4.50%) do **not** necessarily
  match UK/EU rates.

## Validation status

- Demand for UK/DE/FR/IT/ES is **unvalidated.** The dossier's SERP/AIO evidence (dated 2026-09-01,
  expired 2026-09-29) is US/Google.com only. No re-probe has been run for EU/UK query variants; treat
  EU traffic potential as an open question until a follow-up scout/validate pass covers those markets.
