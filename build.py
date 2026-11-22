#!/usr/bin/env python3
"""Build the multilingual Dasabami site.

index.html (English) is the source. This script:
  * regenerates the SEO head block, JSON-LD and i18n blob inside index.html
  * writes translated copies to ka/, ja/, es/, fr/ using i18n/<lang>.json

Run:  python3 build.py
"""
import html
import json
import os
import re
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://dasabami.co/"
LANGS = ["en", "ka", "ja", "es", "fr"]
LOCALE = {"en": "en_US", "ka": "ka_GE", "ja": "ja_JP", "es": "es_ES", "fr": "fr_FR"}
EMAIL = "zazabery@gmail.com"
IG = "https://www.instagram.com/dasabami/"
OG_IMAGE = SITE + "assets/brand/og-image.jpg"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
TR_ATTRS = {"alt", "aria-label", "placeholder", "title", "data-credit"}  # data-credit: press photo credits shown by main.js


def url_for(lang):
    return SITE if lang == "en" else f"{SITE}{lang}/"


def load(lang):
    with open(os.path.join(ROOT, "i18n", f"{lang}.json"), encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------- facts
WINES = [
    # name, category, grape label, skins, qvevri, abv, bottles
    ("Rkatsiteli–Mtsvane 2024", "amber", "80% Rkatsiteli, 20% Mtsvane", (3, "m"), (4, "m"), "12%", 800),
    ("Khikhvi 2024", "amber", "Khikhvi", (4, "m"), (3, "m"), "14.75%", 600),
    ("Khikhvi 2022", "amber", "Khikhvi", (4, "m"), (3, "m"), "15%", 300),
    ("Mtsvane 2022", "amber", "Mtsvane", (6, "m"), (3, "m"), "12.8%", 400),
    ("Rkatsiteli 2022", "amber", "Rkatsiteli", (4, "m"), (3, "m"), "13%", 800),
    ("Khikhvi 2021", "amber", "Khikhvi", (12, "m"), (2, "m"), "12%", 400),
    ("Mtsvane 2021", "amber", "Mtsvane", (6, "m"), (8, "m"), "12%", 360),
    ("Rkatsiteli 2020", "amber", "Rkatsiteli", (6, "m"), (6, "m"), "13%", 900),
    ("Tavkveri 2020", "red", "Tavkveri", (45, "d"), (9, "m"), "12.6%", 180),
    ("Mtsvane 2019", "amber", "Mtsvane", (6, "m"), (6, "m"), "12.3%", 360),
]

VENUES = [
    ("Store", "27 Wine Cellar & Shop", "27 Mikheil Zandukeli St", "Tbilisi", "GE", "https://www.instagram.com/27.wine.cellar.shop/"),
    ("BarOrPub", "Sulico Wine Bar", "27 Mikheil Zandukeli St", "Tbilisi", "GE", "https://www.raisin.digital/en/explore/georgia/tbilisi/venues/sulico-wine-bar-and-restaurant-26353/"),
    ("BarOrPub", "DADI Wine Bar & Shop", "4 Shalva Dadiani St", "Tbilisi", "GE", "https://www.raisin.digital/en/explore/georgia/tbilisi/venues/dadi-8565/"),
    ("BarOrPub", "G.Vino", None, "Tbilisi", "GE", "https://www.instagram.com/g.vino_tbilisi/"),
    ("BarOrPub", "Vino Underground", None, "Tbilisi", "GE", "https://www.instagram.com/vinounderground/"),
    ("Organization", "Roni Selects (US importer)", None, "Los Angeles", "US", "https://www.roniselects.com/georgia-producers/dasabami"),
    ("BarOrPub", "The Punch Down, Oakland", None, "Oakland", "US", "https://www.instagram.com/thepunchdown/"),
    ("BarOrPub", "The Punch Down, Sebastopol", None, "Sebastopol", "US", "https://www.instagram.com/thepunchdownsebastopol/"),
    ("Store", "Proper Natural Wine", None, "London", "GB", "https://www.instagram.com/propernaturalwine/"),
    ("Restaurant", "Tre Tjenere", None, "Bornholm", "DK", "https://www.instagram.com/tretjenerebornholm/"),
    ("Store", "MORE Natural Wine", None, "Berlin", "DE", "https://morenaturalwine.com/products/dasabami-khikhui-2019"),
    ("Store", "Hop Burns & Black", None, "London", "GB", "https://www.hopburnsblack.co.uk/products/dasabamirkatsiteliorange201612750ml"),
    ("Store", "The Cellar d'Or", "136 E State St", "Ithaca, NY", "US", "https://thecellardor.com/dasabami-rkatsiteli-2022-750ml/"),
    ("Store", "Grand Wine Cellar", None, "Syosset, NY", "US", "https://www.grandwinecellar.com/products/dasabami-rkatsiteli"),
    ("Store", "Flatiron Wines San Francisco", "2 New Montgomery St", "San Francisco", "US", "https://sf.flatiron-wines.com/collections/dasabami"),
]

SAME_AS = [
    IG,
    "https://nwa.ge/en/profiles/about/295/dasabami",
    "https://www.raisin.digital/en/explore/georgia/kvemo-kartli/natural-winemakers/zaza-darsavelidze-dasabami-7403/",
    "https://www.vivino.com/en/wineries/dasabami",
    "https://www.roniselects.com/georgia-producers/dasabami",
    "https://www.winesgeorgia.com/domaine/dasabami/",
]

MENTIONS = [
    ("Book", "Tasting Georgia: A Food and Wine Journey in the Caucasus", "Carla Capalbo", "2017", "https://app.ckbk.com/section/tast81250c02s001ss014"),
    ("Article", "Vino Underground: Wine Heaven", "Paul Rimple", "2015", "https://culinarybackstreets.com/stories/tbilisi/vino-underground-2"),
    ("WebPage", "Dasabami on Raisin (community reviews)", None, None, "https://www.raisin.digital/en/explore/georgia/kvemo-kartli/natural-winemakers/zaza-darsavelidze-dasabami-7403/wines/"),
    ("WebPage", "Dasabami on Vivino (3.8 from 222 ratings)", None, None, "https://www.vivino.com/en/wineries/dasabami"),
    ("WebPage", "Roni Selects: Dasabami producer page and tech sheets", None, None, "https://www.roniselects.com/georgia-producers/dasabami"),
    ("WebPage", "Natural Wine Association: Dasabami vineyard registry", None, None, "https://nwa.ge/en/profiles/view/295/dasabami"),
]


def jsonld(lang, T):
    L = T["ld"]
    u = url_for(lang)
    wid = SITE + "#winery"
    unit = {"m": L["months"], "d": L["days"]}
    products = []
    for name, cat, grape, skins, qv, abv, n in WINES:
        products.append({
            "@type": "Product", "name": f"Dasabami {name}",
            "category": L["amber_wine"] if cat == "amber" else L["red_wine"],
            "brand": {"@id": wid}, "manufacturer": {"@id": wid}, "countryOfOrigin": "GE",
            "keywords": L["keywords"],
            "additionalProperty": [
                {"@type": "PropertyValue", "name": L["grape"], "value": grape},
                {"@type": "PropertyValue", "name": L["maceration"], "value": f"{skins[0]} {unit[skins[1]]}"},
                {"@type": "PropertyValue", "name": L["aged_qvevri"], "value": f"{qv[0]} {unit[qv[1]]}"},
                {"@type": "PropertyValue", "name": L["abv"], "value": abv},
                {"@type": "PropertyValue", "name": L["production"], "value": f"{n} {L['bottles']}"},
                {"@type": "PropertyValue", "name": L["yeast"], "value": L["ambient"]},
                {"@type": "PropertyValue", "name": L["added_so2"], "value": L["none"]},
            ],
        })
    venues = []
    for i, (typ, name, street, city, cc, link) in enumerate(VENUES, 1):
        addr = {"@type": "PostalAddress", "addressLocality": city, "addressCountry": cc}
        if street:
            addr["streetAddress"] = street
        venues.append({"@type": "ListItem", "position": i, "item": {"@type": typ, "name": name, "address": addr, "url": link}})
    mentions = []
    for typ, name, author, year, link in MENTIONS:
        m = {"@type": typ, "name": name, "url": link}
        if author:
            m["author"] = {"@type": "Person", "name": author}
        if year:
            m["datePublished"] = year
        mentions.append(m)
    mentions.append({"@id": SITE + "#amber-georgia-berlin-2026"})
    graph = [
        {"@type": "WebSite", "@id": SITE + "#website", "url": SITE, "name": "Dasabami",
         "alternateName": ["დასაბამი", "Dasabami Wine Cellar", "ダサバミ"],
         "inLanguage": LANGS, "publisher": {"@id": wid}},
        {"@type": "WebPage", "@id": u + "#webpage", "url": u, "name": T["meta"]["title"],
         "description": T["meta"]["description"], "keywords": L["keywords"], "inLanguage": lang,
         "isPartOf": {"@id": SITE + "#website"}, "about": {"@id": wid}, "mainEntity": {"@id": wid},
         "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + "assets/img/vineyard-sun-lg.webp", "width": 1440, "height": 1440},
         "dateModified": "2026-11-22"},
        {"@type": ["Winery", "Organization"], "@id": wid, "name": "Dasabami", "legalName": "Dasabami Wine Cellar",
         "alternateName": ["დასაბამი", "Dasabami Wine Cellar", "Dasabami Winery", "ダサバミ"],
         "description": L["winery_description"], "slogan": L["slogan"], "keywords": L["keywords"],
         "url": SITE, "logo": SITE + "assets/brand/logo-512.png",
         "image": [SITE + "assets/img/hero-zaza-lg.webp", SITE + "assets/img/old-vine-lg.webp", SITE + "assets/img/vineyard-sun-lg.webp"],
         "email": EMAIL, "foundingLocation": {"@type": "Place", "name": "Tamarisi, Kvemo Kartli, Georgia"},
         "address": {"@type": "PostalAddress", "addressLocality": "Tamarisi", "addressRegion": "Kvemo Kartli", "addressCountry": "GE"},
         "areaServed": ["GE", "US", "GB", "DE", "DK", "JP", "ES", "FR"],
         "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "email": EMAIL, "url": IG},
         "employee": {"@id": SITE + "#zaza"},
         "knowsAbout": L["knows_about"],
         "memberOf": {"@type": "Organization", "name": "Natural Wine Association (Georgia)", "url": "https://nwa.ge/"},
         "makesOffer": {"@id": SITE + "#wines"},
         "sameAs": SAME_AS, "subjectOf": mentions},
        {"@type": "Person", "@id": SITE + "#zaza", "name": "Zaza Darsavelidze", "alternateName": ["ზაზა დარსაველიძე", "ザザ・ダルサヴェリゼ"],
         "jobTitle": L["job_title"], "description": L["person_description"], "worksFor": {"@id": wid}, "email": EMAIL,
         "homeLocation": {"@type": "Place", "name": "Tamarisi, Kvemo Kartli, Georgia"},
         "image": SITE + "assets/img/hero-zaza-lg.webp"},
        {"@type": "OfferCatalog", "@id": SITE + "#wines", "name": L["catalog_name"], "itemListElement": products},
        {"@type": "ItemList", "@id": SITE + "#where-to-find", "name": L["where_name"], "itemListElement": venues},
        {"@type": "Event", "@id": SITE + "#amber-georgia-berlin-2026", "name": "Amber Georgia Berlin 2026",
         "description": L["event_description"], "startDate": "2026-11-28",
         "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
         "location": {"@type": "Place", "name": "Berlin", "address": {"@type": "PostalAddress", "addressLocality": "Berlin", "addressCountry": "DE"}},
         "organizer": {"@type": "Organization", "name": "Amber Georgia", "url": "https://ambergeorgia.com/"},
         "image": SITE + "assets/img/zaza-portrait-lg.webp", "url": "https://ambergeorgia.com/en/event/1-berlin-2026"},
        {"@type": "FAQPage", "@id": u + "#faq", "inLanguage": lang,
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in T["faq"]]},
    ]
    body = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return f'  <script type="application/ld+json">\n{body}\n  </script>'


def seo_head(lang, T):
    M = T["meta"]
    e = lambda s: html.escape(s, quote=True)
    rel = "" if lang == "en" else "../"
    out = [
        f"  <title>{e(M['title'])}</title>",
        f'  <meta name="description" content="{e(M["description"])}">',
        f'  <meta name="keywords" content="{e(M["keywords"])}">',
        '  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        '  <meta name="author" content="Dasabami Wine Cellar">',
        '  <meta name="application-name" content="Dasabami">',
        f'  <link rel="canonical" href="{url_for(lang)}">',
    ]
    for l in LANGS:
        out.append(f'  <link rel="alternate" hreflang="{l}" href="{url_for(l)}">')
    out += [
        f'  <link rel="alternate" hreflang="x-default" href="{SITE}">',
        f'  <link rel="sitemap" type="application/xml" href="{rel}sitemap.xml">',
        f'  <link rel="alternate" type="text/plain" title="LLM summary" href="{rel}llms.txt">',
        f'  <link rel="me" href="{IG}">',
        '  <meta name="geo.region" content="GE-KK">',
        '  <meta name="geo.placename" content="Tamarisi, Marneuli Municipality, Kvemo Kartli, Georgia">',
        '  <meta property="og:type" content="website">',
        '  <meta property="og:site_name" content="Dasabami">',
        f'  <meta property="og:title" content="{e(M["og_title"])}">',
        f'  <meta property="og:description" content="{e(M["og_description"])}">',
        f'  <meta property="og:url" content="{url_for(lang)}">',
        f'  <meta property="og:locale" content="{LOCALE[lang]}">',
    ]
    for l in LANGS:
        if l != lang:
            out.append(f'  <meta property="og:locale:alternate" content="{LOCALE[l]}">')
    out += [
        f'  <meta property="og:image" content="{OG_IMAGE}">',
        '  <meta property="og:image:width" content="1200">',
        '  <meta property="og:image:height" content="630">',
        f'  <meta property="og:image:alt" content="{e(M["og_image_alt"])}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{e(M["og_title"])}">',
        f'  <meta name="twitter:description" content="{e(M["og_description"])}">',
        f'  <meta name="twitter:image" content="{OG_IMAGE}">',
        f'  <meta name="twitter:image:alt" content="{e(M["og_image_alt"])}">',
    ]
    return "\n".join(out)


def i18n_blob(lang, T):
    data = dict(T.get("js", {}))
    data["lang"] = lang
    data["base"] = "" if lang == "en" else "../"
    if lang != "en":
        data["faq"] = [a for _, a in T["faq"]]
    return "<script>window.DASABAMI_I18N = " + json.dumps(data, ensure_ascii=False) + ";</script>"


def replace_block(src, name, content):
    pat = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    if pat.search(src):
        return pat.sub(lambda m: m.group(1) + "\n" + content + "\n  " + m.group(3), src, count=1)
    single = f"<!-- {name} -->"
    assert single in src, name
    return src.replace(single, f"<!-- {name}:START -->\n{content}\n<!-- {name}:END -->", 1)


# ----------------------------------------------------------------- translate
class Translator(HTMLParser):
    def __init__(self, strings, lang):
        super().__init__(convert_charrefs=True)
        self.s = strings
        self.lang = lang
        self.out = []
        self.raw = 0  # inside script/style

    def tr(self, text):
        key = " ".join(text.split())
        if key and key in self.s:
            lead = text[: len(text) - len(text.lstrip())]
            trail = text[len(text.rstrip()):]
            return lead + self.s[key] + trail
        return text

    def fix_path(self, k, v):
        if self.lang == "en" or v is None:
            return v
        if k in ("src", "href", "data-full", "poster"):
            if v.startswith(("assets/", "site.webmanifest", "sitemap.xml", "llms.txt", "llms-full.txt")):
                return "../" + v
        if k == "srcset":
            return re.sub(r"(^|,\s*)assets/", r"\1../assets/", v)
        return v

    def attrs(self, tag, attrs):
        d = dict(attrs)
        parts = []
        for k, v in attrs:
            if tag == "html" and k == "lang":
                v = self.lang
            if k in TR_ATTRS and v:
                v = self.tr(v)
            v = self.fix_path(k, v)
            if tag == "a" and k == "href" and "data-lang" in d:
                target = d["data-lang"]
                base = "" if self.lang == "en" else "../"
                v = (base or "./") if target == "en" else f"{base}{target}/"
            parts.append(k if v is None else f'{k}="{html.escape(v, quote=True)}"')
        if tag == "a" and d.get("data-lang") == self.lang:
            parts.append('aria-current="page"')
        return (" " + " ".join(parts)) if parts else ""

    def handle_decl(self, decl):
        self.out.append(f"<!{decl}>")

    def handle_starttag(self, tag, attrs):
        self.out.append(f"<{tag}{self.attrs(tag, attrs)}>")
        if tag in ("script", "style"):
            self.raw += 1

    def handle_startendtag(self, tag, attrs):
        self.out.append(f"<{tag}{self.attrs(tag, attrs)}>")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.raw = max(0, self.raw - 1)
        if tag not in VOID:
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if self.raw:
            self.out.append(data)
        else:
            self.out.append(html.escape(self.tr(data), quote=False))

    def handle_comment(self, data):
        self.out.append(f"<!--{data}-->")


def build():
    src_path = os.path.join(ROOT, "index.html")
    with open(src_path, encoding="utf-8") as f:
        src = f.read()
    en = load("en")
    src = replace_block(src, "SEO", seo_head("en", en))
    src = replace_block(src, "JSONLD", jsonld("en", en))
    src = replace_block(src, "I18N", i18n_blob("en", en))
    # language links on the English page
    src = re.sub(r'(<a href="[^"]*" hreflang="en" lang="en" data-lang="en")(?! aria-current)', r'\1 aria-current="page"', src)
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(src)
    print("en  ->", src_path)

    for lang in LANGS[1:]:
        T = load(lang)
        t = Translator(T["strings"], lang)
        page = src.replace(' aria-current="page"', "")
        t.feed(page)
        out = "".join(t.out)
        out = replace_block(out, "SEO", seo_head(lang, T))
        out = replace_block(out, "JSONLD", jsonld(lang, T))
        out = replace_block(out, "I18N", i18n_blob(lang, T))
        out = out.replace('<span class="lang-current">EN</span>', f'<span class="lang-current">{lang.upper()}</span>', 1)
        missing = [s for s in json.load(open(os.path.join(ROOT, "i18n", "_strings.en.json"), encoding="utf-8")) if s not in T["strings"]]
        os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
        dest = os.path.join(ROOT, lang, "index.html")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"{lang}  -> {dest}  ({len(T['strings'])} strings, {len(missing)} kept in English)")


if __name__ == "__main__":
    build()
