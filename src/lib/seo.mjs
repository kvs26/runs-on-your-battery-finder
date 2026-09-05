/**
 * seo.mjs — reusable JSON-LD + meta builders (research/03-seo-baseline.md).
 * FAQPage JSON-LD intentionally omitted (Google deprecated the rich result,
 * May 2026). Product omitted (site is non-transactional).
 */
import { SITE, absUrl } from './site.config.mjs';

/** `<title>` text: distinctive part first, brand suffix last (Google title-link guidance). */
export function pageTitle(title) {
  return title ? `${title} — ${SITE.name}` : SITE.name;
}

/** Organization node — carries the logo Google shows in Search/Knowledge. */
export function organizationLd() {
  const node = {
    '@type': 'Organization',
    name: SITE.name,
    url: absUrl('/'),
  };
  if (SITE.organization?.logo) node.logo = absUrl(SITE.organization.logo);
  if (SITE.organization?.sameAs?.length) node.sameAs = SITE.organization.sameAs;
  return node;
}

/** WebSite node for the home page. */
export function websiteLd() {
  return {
    '@type': 'WebSite',
    name: SITE.name,
    url: absUrl('/'),
    description: SITE.tagline,
  };
}

/** WebApplication node for a tool page. */
export function webApplicationLd({ name, description, url } = {}) {
  return {
    '@type': 'WebApplication',
    name: name || SITE.name,
    url: url ? absUrl(url) : absUrl('/'),
    applicationCategory: 'UtilitiesApplication',
    operatingSystem: 'Any (web-based)',
    isAccessibleForFree: true,
    offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    ...(description ? { description } : {}),
  };
}

/**
 * BreadcrumbList — items: [{ name, href? }]. Last item's URL is optional
 * (Google guidance); we omit `item` on the final crumb.
 */
export function breadcrumbLd(items = []) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: items.map((it, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: it.name,
      ...(it.href && i < items.length - 1 ? { item: absUrl(it.href) } : {}),
    })),
  };
}

/** ItemList — items: [{ url, name? }] — for directory/listing pages. */
export function itemListLd(items = []) {
  return {
    '@type': 'ItemList',
    itemListElement: items.map((it, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      url: absUrl(it.url),
      ...(it.name ? { name: it.name } : {}),
    })),
  };
}

/** Wrap one or more nodes in a single @graph document. */
export function graph(nodes = []) {
  return {
    '@context': 'https://schema.org',
    '@graph': nodes.filter(Boolean),
  };
}
