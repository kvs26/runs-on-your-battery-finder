/**
 * catalog.mjs — dataset accessors shared by the tool island + long-tail routes.
 * Swap catalog.json per site; this shape (platforms / categories / products) is
 * what the template's demo pages expect. Loaded at build via getStaticPaths().
 */
import catalog from '../data/catalog.json';

export const platforms = catalog.platforms;
export const categories = catalog.categories;
export const products = catalog.products;

export function platformBySlug(slug) {
  return platforms.find((p) => p.slug === slug);
}
export function categoryBySlug(slug) {
  return categories.find((c) => c.slug === slug);
}

/** Products for a given platform × category. */
export function productsFor(platformSlug, categorySlug) {
  return products.filter((p) => p.platform === platformSlug && p.category === categorySlug);
}

/** Every platform × category pair that actually has ≥1 product (long-tail routes). */
export function platformCategoryPairs() {
  const pairs = [];
  for (const pl of platforms) {
    for (const cat of categories) {
      if (productsFor(pl.slug, cat.slug).length > 0) pairs.push({ platform: pl, category: cat });
    }
  }
  return pairs;
}

/** Human label + CSS class for a fit type (plain language). */
export const FIT = {
  native: { label: 'Made for it', badge: 'badge--ok' },
  direct: { label: 'Fits as-is', badge: 'badge--fit' },
  adapter: { label: 'Needs adapter', badge: 'badge--warn' },
};

/** Region toggle: internal code -> full display name (PRD: display full country names). */
export const REGIONS = [
  { code: 'US', name: 'United States' },
  { code: 'UK', name: 'United Kingdom' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'IT', name: 'Italy' },
  { code: 'ES', name: 'Spain' },
];

/** Platforms actually sold in a given region code (falls back to all platforms if region is falsy). */
export function platformsForRegion(regionCode) {
  if (!regionCode) return platforms;
  return platforms.filter((p) => Array.isArray(p.regions) && p.regions.includes(regionCode));
}
