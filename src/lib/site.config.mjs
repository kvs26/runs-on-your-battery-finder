/**
 * ============================================================================
 * PER-SITE CONFIG — the one file you edit to stand up a new site.
 * ============================================================================
 * Everything the house template needs to know about *this* site lives here:
 * identity, the active skin, the layout mode, monetization switches, and nav.
 * No component or layout markup changes between sites — only these values.
 *
 * Imported by astro.config.mjs (for `site`) and every layout/component.
 */

export const SITE = {
  // --- Identity ---------------------------------------------------------
  /** Production origin, no trailing slash. Drives canonical/OG/sitemap URLs. */
  url: 'https://runsonyourbattery.com',
  /** Short brand name — the wordmark text and the <title> suffix. */
  name: 'Runs on Your Battery',
  /** One-line positioning statement, used in default meta descriptions + hero. */
  tagline: 'Find gadgets that run on the power-tool battery you already own',
  /** Two-letter language for <html lang>. */
  lang: 'en',
  /** Locale for og:locale. */
  locale: 'en_US',

  // --- Theme ------------------------------------------------------------
  /** Active skin: 'neutral' | 'editorial' | 'technical' | 'dark' | 'playful'. */
  skin: 'neutral',
  /**
   * Directory/tool results layout:
   *   'list' — results-list (spec/tool niches)
   *   'grid' — card-grid   (image/product niches)
   * One flag, same tokens + components.
   */
  layoutMode: 'list',
  /**
   * Allow visitors to toggle light/dark. Dark mode re-points the same semantic
   * roles to the opposite end of each ramp (no separate skin needed).
   */
  enableDarkModeToggle: true,

  // --- Organization (JSON-LD Organization + WebSite) --------------------
  organization: {
    /** Path (from site root) to a raster logo for Organization.logo JSON-LD. */
    logo: '/logo.png',
    /** Optional social profile URLs for Organization.sameAs. */
    sameAs: /** @type {string[]} */ ([]),
  },

  /** Default social-share image (absolute path from site root). 1200x630. */
  ogImage: '/og-cover.png',

  // --- Navigation -------------------------------------------------------
  /** Primary header nav. */
  nav: [
    { label: 'Home', href: '/' },
    { label: 'How we check', href: '/methodology' },
    { label: 'FAQ', href: '/faq' },
    { label: 'About', href: '/about' },
    { label: 'Contact', href: '/contact' },
  ],

  /** Footer link groups (trust/E-E-A-T + legal interlink). */
  footer: [
    {
      heading: 'Site',
      links: [
        { label: 'Home', href: '/' },
        { label: 'How we check', href: '/methodology' },
        { label: 'FAQ', href: '/faq' },
      ],
    },
    {
      heading: 'Trust',
      links: [
        { label: 'About', href: '/about' },
        { label: 'Contact', href: '/contact' },
      ],
    },
    {
      heading: 'Legal',
      links: [
        { label: 'Privacy', href: '/privacy' },
        { label: 'Affiliate disclosure', href: '/disclosure' },
      ],
    },
  ],

  // --- Monetization holes (OFF by default; flip on post-launch) ----------
  // Ticket 04 (ads) + ticket 05 (affiliate). Turning these on must never
  // reflow the page — slots reserve their space whether filled or not.
  monetization: {
    ads: {
      /** Master switch. false = reserved-but-empty slots (ticket 04). */
      enabled: false,
      /** AdSense publisher id, e.g. 'ca-pub-XXXXXXXXXXXXXXXX'. */
      adsensePublisherId: '',
    },
    affiliate: {
      /** Master switch. false = affiliate links render as plain text/hidden. */
      enabled: false,
      /** FTC disclosure line shown near affiliate links / in the footer. */
      disclosure:
        'As an Amazon Associate we earn from qualifying purchases. Links may be affiliate links.',
    },
  },

  // --- Analytics (single insertion point; ticket 04) --------------------
  analytics: {
    /** 'none' | 'cloudflare' | 'plausible' | 'ga4'. */
    provider: 'none',
    /** Cloudflare Web Analytics token, or Plausible domain, or GA4 measurement id. */
    token: '',
  },
};

/** Absolute URL helper: joins SITE.url with a root-relative path. */
export function absUrl(path = '/') {
  const base = SITE.url.replace(/\/$/, '');
  return `${base}${path.startsWith('/') ? path : `/${path}`}`;
}
