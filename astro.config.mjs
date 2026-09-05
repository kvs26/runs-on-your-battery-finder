// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { SITE } from './src/lib/site.config.mjs';

// Ticket 08: static output, no SSR adapter. Ticket 03: sitemap generated at build.
// `site` is the production origin; every canonical / OG / sitemap URL derives from it.
// Change it (and src/lib/site.config.mjs) per site — nothing else needs editing to re-point.
export default defineConfig({
  site: SITE.url,
  output: 'static',
  trailingSlash: 'ignore',
  integrations: [
    sitemap(),
  ],
  build: {
    // Keep asset URLs stable + long-cacheable (Cloudflare Pages immutable headers).
    assets: '_assets',
  },
});
