# Dasabami — website

Static, dependency-free site for Dasabami (დასაბამი), the family qvevri wine cellar of Zaza Darsavelidze in Tamarisi, Kvemo Kartli, Georgia.

## Structure

```
index.html            single page: hero, story, wines, tech specs, qvevri, press, gallery, find, FAQ, contact
404.html              not-found page (GitHub Pages)
assets/css/style.css  design system (glass, motion, dark mode)
assets/js/main.js     scroll motion, wine filter/sheet, quotes, lightbox, countdown, cellar guide
assets/img/           WebP photos, -sm (800px) and -lg (up to 1600px)
assets/brand/         favicon, app icons, logo, Open Graph share image
robots.txt            allows search engines and AI crawlers, points to the sitemap
sitemap.xml           page + image sitemap
llms.txt              short fact sheet for AI assistants (llmstxt.org format)
llms-full.txt         complete plain-text fact sheet for AI assistants
site.webmanifest      app manifest
```

## Run locally

```bash
python3 -m http.server 4317
```

Then open http://localhost:4317.

## SEO / GEO

- JSON-LD in `index.html`: WebSite, WebPage, Winery/Organization, Person (Zaza), OfferCatalog of wines with tech specs, Event (Amber Georgia Berlin), FAQPage.
- Open Graph and Twitter cards with `assets/brand/og-image.jpg` (1200×630).
- Visible FAQ and an “at a glance” fact list mirror the structured data, so search engines and AI answers get the same facts.
- `robots.txt` explicitly allows AI search crawlers; `llms.txt` and `llms-full.txt` summarize the facts.

### Site URL

All absolute URLs use `https://morrticia.github.io/DasabamiWeb/` (GitHub Pages for this repo). When a custom domain is set up (for example `dasabami.ge`), replace it everywhere:

```bash
grep -rl "morrticia.github.io/DasabamiWeb/" . | xargs sed -i '' "s#https://morrticia.github.io/DasabamiWeb/#https://dasabami.ge/#g"
```

Note: `robots.txt` and `llms.txt` are only read at the root of a domain, so they take full effect once the site has its own domain. Until then, submit `sitemap.xml` in Google Search Console and Bing Webmaster Tools.

## Content notes

- Founded by Zaza’s father; vineyard about 70 years old (from the family).
- Tech specs come from the US importer’s (Roni Selects) tech sheets.
- Press: only the Culinary Backstreets line is a direct quote; the other items are attributed summaries that link to their sources.
- Photos from tagged Instagram posts belong to the people who posted them; ask before public launch.
