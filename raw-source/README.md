# Raw source material

This folder holds the **owner-supplied raw material** the `/build-site` skill shapes into
`src/data/catalog.json` — it is not read by Astro at build time, it's provenance: what the dataset and
links were derived from, kept next to the site that used it.

Drop files directly in this folder (no subfolders) — typically **one CSV per refresh** with both the
product/platform/category/fit data *and* its buy link in the same row, but a markdown/PDF/notes file or
a separate links list works too if that's what's easiest to hand over.

Keep the original files here even after they're absorbed into `catalog.json`, so a future refresh can
diff against what was last used.
