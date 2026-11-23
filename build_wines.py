"""Wine pages: /wines/ and /wines/<id>/ in every language, plus the full sitemap.

Called from build.py. Text lives in i18n/wines.<lang>.json; shared facts live here.
"""
import html
import json
import os

E = lambda s: html.escape(str(s), quote=True)

ORDER = ["rkatsiteli", "mtsvane", "khikhvi", "tavkveri", "rkatsiteli-mtsvane"]
STYLE = {"rkatsiteli": "amber", "mtsvane": "amber", "khikhvi": "amber", "tavkveri": "red", "rkatsiteli-mtsvane": "blend"}
# vintage, skins (n, unit), qvevri (n, unit), alcohol, bottles   (Roni Selects tech sheets)
SPECS = {
    "rkatsiteli": [("2022", (4, "m"), (3, "m"), "13%", 800), ("2020", (6, "m"), (6, "m"), "13%", 900)],
    "mtsvane": [("2022", (6, "m"), (3, "m"), "12.8%", 400), ("2021", (6, "m"), (8, "m"), "12%", 360), ("2019", (6, "m"), (6, "m"), "12.3%", 360)],
    "khikhvi": [("2024", (4, "m"), (3, "m"), "14.75%", 600), ("2022", (4, "m"), (3, "m"), "15%", 300), ("2021", (12, "m"), (2, "m"), "12%", 400)],
    "tavkveri": [("2020", (45, "d"), (9, "m"), "12.6%", 180)],
    "rkatsiteli-mtsvane": [("2024", (3, "m"), (4, "m"), "12%", 800)],
}
HERO = {"rkatsiteli": "rkatsiteli-2019", "mtsvane": "mtsvane-2017", "khikhvi": "khikhvi-tasting", "tavkveri": "tavkveri-2019", "rkatsiteli-mtsvane": "zaza-27-cellar"}
PHOTOS = {
    "rkatsiteli": ["rkatsiteli-2016", "lineup"],
    "mtsvane": ["mtsvane-2017-glasses", "vineyard-canopy"],
    "khikhvi": ["khikhvi-2018", "shops/more-khikhvi-2019"],
    "tavkveri": ["tavkveri-2017", "tavkveri-2018"],
    "rkatsiteli-mtsvane": ["lineup", "vineyard-canopy"],
}
# name: (sm w, h, lg w, h) ; single-file images use None for sm
IMG = {
    "rkatsiteli-2019": (593, 800, 740, 998), "rkatsiteli-2016": (640, 800, 1080, 1350), "lineup": (800, 800, 1169, 1169),
    "mtsvane-2017": (716, 800, 1074, 1200), "mtsvane-2017-glasses": (800, 800, 1080, 1080), "vineyard-canopy": (800, 800, 1440, 1440),
    "khikhvi-tasting": (640, 800, 1080, 1350), "khikhvi-2018": (494, 614, 494, 614), "shops/more-khikhvi-2019": (None, None, 471, 640),
    "tavkveri-2019": (600, 800, 740, 987), "tavkveri-2017": (640, 800, 957, 1196), "tavkveri-2018": (768, 768, 768, 768),
    "zaza-27-cellar": (800, 530, 1080, 716),
}
NAV = [("story", "Story"), ("wines", "Wines"), ("qvevri", "Qvevri"), ("press", "Press"), ("find", "Find"), ("contact", "Contact")]
LANG_NAME = {"en": "English", "ka": "ქართული", "ja": "日本語", "es": "Español", "fr": "Français"}
MAIL = "mailto:zazabery@gmail.com"
COLON = {"fr": "\u00a0:", "ja": "："}
IG = "https://www.instagram.com/dasabami/"


def img_tag(name, alt, sizes, eager=False, cls=""):
    smw, smh, lgw, lgh = IMG[name]
    if smw is None:
        src = f"/assets/img/{name}.webp"
        srcset = ""
    else:
        src = f"/assets/img/{name}-lg.webp"
        srcset = f' srcset="/assets/img/{name}-sm.webp {smw}w, /assets/img/{name}-lg.webp {lgw}w" sizes="{sizes}"'
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{src}"{srcset} width="{lgw}" height="{lgh}"{load} alt="{E(alt)}">'


def img_url(site, name):
    smw = IMG[name][0]
    return f"{site}assets/img/{name}.webp" if smw is None else f"{site}assets/img/{name}-lg.webp"


class Ctx:
    def __init__(self, root, site, langs, locale, version):
        self.root, self.site, self.locale, self.v = root, site, locale, version
        self.all_langs = list(langs)
        # a language gets wine pages once i18n/wines.<lang>.json exists
        self.langs = [l for l in langs if os.path.exists(os.path.join(root, "i18n", f"wines.{l}.json"))]
        self.W = {l: json.load(open(os.path.join(root, "i18n", f"wines.{l}.json"), encoding="utf-8")) for l in self.langs}
        self.M = {}
        for l in self.langs:
            p = os.path.join(root, "i18n", f"{l}.json")
            self.M[l] = json.load(open(p, encoding="utf-8")).get("strings", {}) if l != "en" else {}

    def pre(self, lang):
        return "/" if lang == "en" else f"/{lang}/"

    def url(self, lang, path=""):
        return self.site.rstrip("/") + self.pre(lang) + path

    def main(self, lang, s):
        return self.M[lang].get(s, s)


def head(c, lang, path, title, desc, ld):
    U = c.W[lang]["ui"]
    alts = "\n".join(f'  <link rel="alternate" hreflang="{l}" href="{c.url(l, path)}">' for l in c.langs)
    og_alt = "\n".join(f'  <meta property="og:locale:alternate" content="{c.locale[l]}">' for l in c.langs if l != lang)
    return f"""<!doctype html>
<html lang="{lang}" prefix="og: https://ogp.me/ns#">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{E(title)}</title>
  <meta name="description" content="{E(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="{c.url(lang, path)}">
{alts}
  <link rel="alternate" hreflang="x-default" href="{c.url('en', path)}">
  <meta name="geo.region" content="GE-KK">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Dasabami">
  <meta property="og:title" content="{E(title)}">
  <meta property="og:description" content="{E(desc)}">
  <meta property="og:url" content="{c.url(lang, path)}">
  <meta property="og:locale" content="{c.locale[lang]}">
{og_alt}
  <meta property="og:image" content="{c.site}assets/brand/og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#f5f4f1" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#0a0a0b" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/assets/brand/favicon-32.png" sizes="32x32" type="image/png">
  <link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css?v={c.v}">
  <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
  </script>
</head>
<body class="wine-page">
<a class="sr-only" href="#main">{E(U['skip'])}</a>
"""


def nav(c, lang, path):
    U = c.W[lang]["ui"]
    home = c.pre(lang)
    links = "".join(f'<li><a href="{home}#{a}">{E(c.main(lang, lbl))}</a></li>' for a, lbl in NAV)
    opts = "\n".join(
        f'        <li><a href="{c.pre(l)}{path}" hreflang="{l}" lang="{l}"{" aria-current=\"page\"" if l == lang else ""}>{LANG_NAME[l]}</a></li>'
        for l in c.langs)
    return f"""<header class="nav glass" id="nav">
  <a class="brand" href="{home}" aria-label="Dasabami">DASABAMI <small>დასაბამი</small></a>
  <nav aria-label="Primary"><ul class="nav-links">{links}</ul></nav>
  <div class="nav-actions">
    <details class="lang" id="lang">
      <summary aria-label="{E(U['language'])}"><svg class="globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg><span class="lang-current">{lang.upper()}</span><svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary>
      <ul class="lang-menu">
{opts}
      </ul>
    </details>
    <a class="btn btn-primary nav-mail" href="{MAIL}?subject=Dasabami%20wine">{E(c.main(lang, 'Email'))}</a>
  </div>
</header>
"""


def contact_footer(c, lang):
    U = c.W[lang]["ui"]
    home = c.pre(lang)
    return f"""<section class="section contact" aria-label="{E(U['contact_eyebrow'])}">
  <div class="wrap" data-reveal>
    <span class="eyebrow" style="display:block;margin-bottom:18px">{E(U['contact_eyebrow'])}</span>
    <a class="big-mail" href="{MAIL}?subject=Dasabami%20wine">{E(U['contact_title'])}</a>
    <p class="lede">{E(U['contact_text'])}</p>
    <div class="contact-actions">
      <a class="btn btn-primary" href="{MAIL}?subject=Dasabami%20wine"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 7l9 6 9-6"/></svg> {E(U['send_email'])}</a>
      <button class="btn btn-glass" id="copy-email" type="button" data-copied="{E(U['copied'])}" data-failed="{E(U['copy_failed'])}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="1"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg> {E(U['copy'])}</button>
      <a class="btn btn-glass" href="{IG}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg> @dasabami</a>
    </div>
  </div>
</section>
</main>
<footer class="footer">
  <div class="wrap">
    <div class="footer-grid">
      <p class="big">Dasabami<br><span>{E(c.main(lang, 'the beginning.'))}</span></p>
      <nav aria-label="Footer">
        <a href="{home}wines/">{E(U['all_wines'])}</a>
        <a href="{MAIL}?subject=Dasabami%20wine">{E(U['email_us'])}</a>
        <a href="{IG}" target="_blank" rel="noopener">Instagram</a>
        <a href="{home}">{E(U['back_home'])}</a>
      </nav>
    </div>
    <p class="fine">{E(U['footer_line'])}</p>
  </div>
</footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script src="/assets/js/wine.js?v={c.v}" defer></script>
</body>
</html>
"""


def style_label(U, wid):
    return {"amber": U["style_amber"], "red": U["style_red"], "blend": U["style_blend"]}[STYLE[wid]]


def specs_html(c, lang, wid):
    U = c.W[lang]["ui"]
    unit = {"m": U["months"], "d": U["days"]}
    cards = []
    for i, (yr, skins, qv, abv, n) in enumerate(SPECS[wid]):
        sv = skins[0] / 12 if skins[1] == "m" else skins[0] / 360
        red = " red" if STYLE[wid] == "red" else ""
        cards.append(f"""    <article class="spec{red}" data-reveal style="--delay:{i*90}ms">
      <h3 class="spec-name">{yr}</h3><span class="spec-yr">{E(c.W[lang]['wines'][wid]['name'])}</span>
      <dl>
        <div><dt>{E(U['on_skins'])}</dt><dd><b>{skins[0]}</b>{E(unit[skins[1]])}</dd><span class="meter" style="--v:{min(sv,1):.3f}"></span></div>
        <div><dt>{E(U['in_qvevri'])}</dt><dd><b>{qv[0]}</b>{E(unit[qv[1]])}</dd><span class="meter" style="--v:{min(qv[0]/12,1):.3f}"></span></div>
        <div><dt>{E(U['alcohol'])}</dt><dd><b>{abv.rstrip('%')}</b>%</dd></div>
        <div><dt>{E(U['bottles'])}</dt><dd><b>{n}</b></dd><span class="meter" style="--v:{min(n/900,1):.3f}"></span></div>
      </dl>
    </article>""")
    return "\n".join(cards)


def wine_ld(c, lang, wid, w):
    U = c.W[lang]["ui"]
    u = c.url(lang, f"wines/{wid}/")
    pid = c.site + f"wines/{wid}/#wine"
    props = [
        {"@type": "PropertyValue", "name": U["f_grape"], "value": w["facts"]["grape"]},
        {"@type": "PropertyValue", "name": U["f_vines"], "value": w["facts"]["vines"]},
        {"@type": "PropertyValue", "name": U["f_vessel"], "value": U["vessel_value"]},
        {"@type": "PropertyValue", "name": U["f_skins"], "value": w["facts"]["skins"]},
        {"@type": "PropertyValue", "name": U["f_lot"], "value": w["facts"]["lot"]},
        {"@type": "PropertyValue", "name": "Added SO2", "value": "None"},
    ]
    imgs = [img_url(c.site, HERO[wid])] + [img_url(c.site, p) for p in PHOTOS[wid]]
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": u + "#webpage", "url": u, "name": w["title"], "description": w["description"], "inLanguage": lang,
         "isPartOf": {"@id": c.site + "#website"}, "about": {"@id": pid}, "breadcrumb": {"@id": u + "#breadcrumb"},
         "primaryImageOfPage": imgs[0], "dateModified": "2026-11-23"},
        {"@type": "BreadcrumbList", "@id": u + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Dasabami", "item": c.url(lang)},
            {"@type": "ListItem", "position": 2, "name": U["wines"], "item": c.url(lang, "wines/")},
            {"@type": "ListItem", "position": 3, "name": w["name"], "item": u}]},
        {"@type": "Product", "@id": pid, "name": f"Dasabami {w['name']}", "alternateName": f"Dasabami {w['geo']}",
         "description": w["lede"], "image": imgs, "url": u, "category": style_label(U, wid),
         "brand": {"@type": "Brand", "name": "Dasabami"}, "manufacturer": {"@id": c.site + "#winery"},
         "countryOfOrigin": "GE", "additionalProperty": props},
        {"@type": "FAQPage", "@id": u + "#faq", "inLanguage": lang,
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in w["faq"]]},
    ]}


def wine_page(c, lang, wid):
    U = c.W[lang]["ui"]
    w = c.W[lang]["wines"][wid]
    path = f"wines/{wid}/"
    home = c.pre(lang)
    out = [head(c, lang, path, w["title"], w["description"], wine_ld(c, lang, wid, w)), nav(c, lang, path)]
    facts = [(U["f_grape"], w["facts"]["grape"]), (U["f_style"], style_label(U, wid)), (U["f_vines"], w["facts"]["vines"]),
             (U["f_vessel"], U["vessel_value"]), (U["f_skins"], w["facts"]["skins"]), (U["f_lot"], w["facts"]["lot"])]
    facts_html = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in facts)
    hero_alt = w["alts"].get(HERO[wid], w["name"])
    out.append(f"""<main id="main">
<section class="wp-hero">
  <div class="wrap wp-hero-grid">
    <div class="wp-hero-copy wp-in">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="{home}">Dasabami</a><span aria-hidden="true">/</span><a href="{home}wines/">{E(U['wines'])}</a><span aria-hidden="true">/</span><span aria-current="page">{E(w['name'])}</span></nav>
      <span class="eyebrow">{E(style_label(U, wid))}</span>
      <h1 class="h-display{' long' if len(w['name']) > 12 else ''}">{E(w['name'])}</h1>
      <span class="geo">{E(c.W['en']['wines'][wid]['name'] if lang == 'ka' else w['geo'])}</span>
      <p class="lede">{E(w['lede'])}</p>
      <div class="hero-ctas wp-ctas">
        <a class="btn btn-primary" href="{MAIL}?subject={E('Dasabami ' + w['name'])}">{E(U['write_to_us'])}</a>
        <a class="btn btn-glass" href="{home}wines/">{E(U['all_wines'])}</a>
      </div>
    </div>
    <figure class="wp-hero-media wp-in">{img_tag(HERO[wid], hero_alt, "(max-width: 900px) 100vw, 45vw", eager=True)}</figure>
  </div>
</section>

<section class="wrap wp-facts" aria-label="{E(U['facts_title'])}" data-reveal>
  <dl>{facts_html}</dl>
</section>

<section class="section wrap wp-prose">
  <article data-reveal>
    <span class="eyebrow">{E(U['grape_title'])}</span>
    {''.join(f'<p>{E(p)}</p>' for p in w['grape'])}
  </article>
  <article data-reveal>
    <span class="eyebrow">{E(U['ours_title'])}</span>
    {''.join(f'<p>{E(p)}</p>' for p in w['ours'])}
  </article>
</section>
""")
    # vintages
    out.append(f"""<section class="wp-vintages" aria-label="{E(U['vintages_title'])}">
  <div class="wrap"><h2 class="h-section wp-h2" data-reveal>{E(U['vintages_title'])}</h2></div>
  <div class="specs">
{specs_html(c, lang, wid)}
  </div>
  <div class="wrap">
    <p class="source">{E(U['source'])}</p>
    {f'<p class="wp-earlier"><b>{E(U["earlier_title"])}{COLON.get(lang, ":")}</b> {E(w["earlier"])}</p>' if w.get('earlier') else ''}
  </div>
</section>
""")
    # photos
    figs = []
    for p in PHOTOS[wid]:
        cap = w.get("captions", {}).get(p, "")
        figs.append(f'<figure data-reveal>{img_tag(p, w["alts"].get(p, ""), "(max-width: 720px) 100vw, 50vw")}{f"<figcaption>{E(cap)}</figcaption>" if cap else ""}</figure>')
    out.append(f'<section class="wp-photos" aria-label="Photos">{"".join(figs)}</section>\n')
    # said
    if w.get("said"):
        items = []
        for s in w["said"]:
            cls = "quote" if s["quote"] else "quote is-note"
            items.append(f"""<figure class="{cls}" data-reveal><blockquote>{E(s['text'])}</blockquote><figcaption><strong>{E(s['by'])}</strong><a href="{E(s['url'])}" target="_blank" rel="noopener">{E(U['read'])} ↗</a></figcaption></figure>""")
        out.append(f"""<section class="section press wp-said">
  <div class="wrap">
    <span class="eyebrow">{E(U['said_title'])}</span>
    <div class="wp-said-grid">{''.join(items)}</div>
  </div>
</section>
""")
    # faq
    faq = "".join(f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><div class="a"><p>{E(a)}</p></div></details>' for i, (q, a) in enumerate(w["faq"]))
    out.append(f"""<section class="section wrap faq-grid wp-faq">
  <div class="faq-aside" data-reveal><span class="eyebrow">{E(U['faq_title'])}</span><h2 class="h-section wp-h2" style="margin-top:14px">{E(w['name'])}</h2></div>
  <div class="faq" data-reveal>{faq}</div>
</section>
""")
    # other wines
    cards = []
    for o in ORDER:
        if o == wid:
            continue
        ow = c.W[lang]["wines"][o]
        cards.append(f'<a class="wp-other" href="{home}wines/{o}/" data-reveal>{img_tag(HERO[o], ow["alts"].get(HERO[o], ow["name"]), "(max-width: 720px) 50vw, 25vw")}<span><b>{E(ow["name"])}</b><small>{E(style_label(U, o))}</small></span></a>')
    out.append(f"""<section class="section wp-others-wrap">
  <div class="wrap"><h2 class="h-section wp-h2" data-reveal>{E(U['other_title'])}</h2></div>
  <div class="wp-others">{''.join(cards)}</div>
</section>
""")
    out.append(contact_footer(c, lang))
    return "".join(out)


def hub_page(c, lang):
    U = c.W[lang]["ui"]
    H = c.W[lang]["hub"]
    home = c.pre(lang)
    u = c.url(lang, "wines/")
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": u + "#webpage", "url": u, "name": H["title"], "description": H["description"], "inLanguage": lang,
         "isPartOf": {"@id": c.site + "#website"}, "about": {"@id": c.site + "#winery"}, "breadcrumb": {"@id": u + "#breadcrumb"},
         "mainEntity": {"@type": "ItemList", "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": c.url(lang, f"wines/{w}/"), "name": f"Dasabami {c.W[lang]['wines'][w]['name']}"}
             for i, w in enumerate(ORDER)]}},
        {"@type": "BreadcrumbList", "@id": u + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Dasabami", "item": c.url(lang)},
            {"@type": "ListItem", "position": 2, "name": U["wines"], "item": u}]},
    ]}
    cards = []
    for w in ORDER:
        ww = c.W[lang]["wines"][w]
        cards.append(f"""<a class="wp-card" href="{home}wines/{w}/" data-reveal>
  <span class="wp-card-img">{img_tag(HERO[w], ww['alts'].get(HERO[w], ww['name']), '(max-width: 720px) 100vw, 33vw')}</span>
  <span class="wp-card-body"><span class="eyebrow">{E(style_label(U, w))}</span><b>{E(ww['name'])}</b><i>{E(c.W['en']['wines'][w]['name'] if lang == 'ka' else ww['geo'])}</i><span>{E(ww['lede'])}</span><em>{E(U['more'].format(name=ww['name']) if '{name}' in U['more'] else U['more'] + ' ' + ww['name'])} →</em></span>
</a>""")
    return (head(c, lang, "wines/", H["title"], H["description"], ld) + nav(c, lang, "wines/") + f"""<main id="main">
<section class="wp-hero wp-hub-hero">
  <div class="wrap wp-in">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{home}">Dasabami</a><span aria-hidden="true">/</span><span aria-current="page">{E(U['wines'])}</span></nav>
    <span class="eyebrow">{E(H['eyebrow'])}</span>
    <h1 class="h-display">{E(H['h1'])}</h1>
    <p class="lede" style="max-width:720px">{E(H['lede'])}</p>
  </div>
</section>
<section class="wp-cards">{''.join(cards)}</section>
""" + contact_footer(c, lang))


def sitemap(c):
    home_imgs = [
        ("hero-zaza-lg.webp", "Winemaker Zaza Darsavelidze in the Dasabami vineyard, Tamarisi, Georgia"),
        ("old-vine-lg.webp", "A 70-year-old vine in the Dasabami vineyard"),
        ("zaza-cat-lg.webp", "Zaza Darsavelidze on the vine pergola"),
        ("red-grapes-lg.webp", "An old Racha grape variety with a family name, in November after the harvest"),
        ("rkatsiteli-2019-lg.webp", "Dasabami Rkatsiteli 2019 amber qvevri wine"),
        ("tavkveri-2019-lg.webp", "Dasabami Tavkveri 2019 red qvevri wine"),
        ("mtsvane-2017-lg.webp", "Dasabami Mtsvane 2017 amber wine"),
        ("khikhvi-2018-lg.webp", "Dasabami Khikhvi 2018 amber wine"),
        ("tavkveri-2017-lg.webp", "Dasabami Tavkveri 2017 dry red wine"),
        ("vineyard-sun-lg.webp", "The Dasabami vineyard in Lower Kartli"),
        ("winter-pruning-lg.webp", "Pruning old vines by hand in winter, Tamarisi"),
        ("zaza-cellar-lg.webp", "Zaza Darsavelidze pouring Dasabami in Tbilisi"),
    ]
    paths = [("", True)] + [("wines/", False)] + [(f"wines/{w}/", False) for w in ORDER]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for path, is_home in paths:
        langs = c.all_langs if is_home else c.langs
        for lang in langs:
            out.append("  <url>")
            out.append(f"    <loc>{c.url(lang, path)}</loc>")
            for l in langs:
                out.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{c.url(l, path)}"/>')
            out.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{c.url("en", path)}"/>')
            out.append("    <lastmod>2026-11-23</lastmod>")
            out.append(f"    <changefreq>{'weekly' if is_home else 'monthly'}</changefreq>")
            out.append(f"    <priority>{'1.0' if is_home and lang == 'en' else ('0.9' if is_home else '0.8')}</priority>")
            imgs = []
            if is_home and lang == "en":
                imgs = [(f"{c.site}assets/img/{f}", t) for f, t in home_imgs]
            elif path.startswith("wines/") and path != "wines/" and lang == "en":
                wid = path.split("/")[1]
                w = c.W["en"]["wines"][wid]
                imgs = [(img_url(c.site, n), w["alts"].get(n, w["name"])) for n in [HERO[wid]] + PHOTOS[wid]]
            for src, t in imgs:
                out.append(f"    <image:image><image:loc>{src}</image:loc><image:title>{E(t)}</image:title></image:image>")
            out.append("  </url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def build_wines(root, site, langs, locale, version):
    c = Ctx(root, site, langs, locale, version)
    n = 0
    for lang in c.langs:
        base = root if lang == "en" else os.path.join(root, lang)
        d = os.path.join(base, "wines")
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(hub_page(c, lang)); n += 1
        for wid in ORDER:
            wd = os.path.join(d, wid)
            os.makedirs(wd, exist_ok=True)
            open(os.path.join(wd, "index.html"), "w", encoding="utf-8").write(wine_page(c, lang, wid)); n += 1
    open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8").write(sitemap(c))
    print(f"wine pages: {n} written for {', '.join(c.langs)}; sitemap updated")
