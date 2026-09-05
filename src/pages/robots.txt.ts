import type { APIRoute } from 'astro';
import { SITE, absUrl } from '../lib/site.config.mjs';

// robots.txt with an absolute Sitemap: line (research/03 §2). @astrojs/sitemap
// emits sitemap-index.xml at the site root.
export const GET: APIRoute = () => {
  const body = `User-agent: *
Allow: /

Sitemap: ${absUrl('/sitemap-index.xml')}
`;
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};

export const prerender = true;
void SITE;
