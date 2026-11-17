#!/usr/bin/env python3
"""DİDİ Otel — İngilizce blog üretici (idempotent).
Girdi : generate-blog.py (TR veri: görseller, tarih, related) + blog_en/<slug>.json (EN çeviri)
Çıktı : en/blog/index.html + en/blog/<slug>/index.html
TR çıktıya dokunmaz. TR yazılara hreflang'ı generate-blog.py ekler (blog_en/*.json varlığına göre).
"""
import os, re, json, html, importlib.util

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("gb", f"{ROOT}/generate-blog.py")
gb = importlib.util.module_from_spec(spec); spec.loader.exec_module(gb)
SITE, IMG = gb.SITE, gb.IMG
TR_BY = {p["slug"]: p for p in gb.POSTS}
SLUGS = sorted(f[:-5] for f in os.listdir(f"{ROOT}/blog_en") if f.endswith(".json"))
EN = {s: json.load(open(f"{ROOT}/blog_en/{s}.json", encoding="utf-8")) for s in SLUGS}
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

WA = "https://wa.me/905331350888?text=Merhaba%2C%20D%C4%B0D%C4%B0%20Otel%20Sapanca%20i%C3%A7in%20rezervasyon%20yapmak%20istiyorum."
en_url = lambda s: f"{SITE}/en/blog/{s}/"
tr_url = lambda s: f"{SITE}/blog/{s}/"

def fmt_date(d):
    y, m, day = d.split("-"); return f"{int(day)} {MONTHS[int(m)-1]} {y}"

# ── dil değiştirici (en/index.html ile aynı görünüm) ──
_en_home = open(f"{ROOT}/en/index.html", encoding="utf-8").read()
LANGSW_CSS = re.search(r"<style>\.langsw\{.*?</style>", _en_home, re.S).group(0)
def langsw(tr_href):
    items = (f'<a href="{tr_href}" class="">🇹🇷 Türkçe</a><a href="#" class="on">🇬🇧 English</a>'
             f'<a href="{SITE}/ru/" class="">🇷🇺 Русский</a><a href="{SITE}/ar/" class="">🇸🇦 العربية</a><a href="{SITE}/de/" class="">🇩🇪 Deutsch</a>')
    return (LANGSW_CSS + '<div class="langsw" id="langsw"><button class="langsw-btn" onclick="document.getElementById(\'langsw\').classList.toggle(\'open\')" aria-label="Language / Dil">🇬🇧 EN'
            '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></button>'
            f'<div class="langsw-menu">{items}</div></div>'
            '<script>document.addEventListener("click",function(e){var s=document.getElementById("langsw");if(s&&!s.contains(e.target))s.classList.remove("open")})</script>')
def moblangs(tr_href):
    return ('<div class="mob-langs">' + f'<a href="{tr_href}" class="">🇹🇷 Türkçe</a><a href="#" class="on">🇬🇧 English</a>'
            f'<a href="{SITE}/ru/" class="">🇷🇺 Русский</a><a href="{SITE}/ar/" class="">🇸🇦 العربية</a><a href="{SITE}/de/" class="">🇩🇪 Deutsch</a></div>')

def nav(tr_href):
    links = '<a href="/en/odalar/">Rooms</a><a href="/en/#deneyim">Experience</a><a href="/en/#mare">Mare Gastro</a><a href="/en/#konum">Location</a><a href="/en/blog/">Blog</a><a href="/en/#iletisim">Contact</a>'
    return f'''<nav class="nav scr-force" id="nav">
<a href="/en/" class="nav-logo" aria-label="DİDİ Otel Sapanca"><img class="logo-w" src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><img class="logo-n" src="/assets/brand/adidilogo-navy.png" alt="" aria-hidden="true"></a>
<div class="nav-links">
{links}
</div>
<div class="nav-right">{langsw(tr_href)}
<a href="tel:+905331350888" class="btn btn-line" dir="ltr">0533 135 08 88</a>
<a href="{WA}" class="btn btn-fill">Book Now</a>
<button class="burger" id="burger" aria-label="Menu"><span></span><span></span><span></span></button>
</div>
</nav>
<div class="mob" id="mob">{moblangs(tr_href)}
{links}
<a href="{WA}" style="color:var(--green)">Book Now →</a>
</div>'''

FOOT = gb.FOOT
for a, b in [
 ("Kırkpınar Sapanca'da göl ve orman arasında butik bir konaklama. Sapanca'nın tek klorsuz havuzu ve Mare Gastro restoranıyla.",
  "A boutique stay between the lake and the forest in Kırkpınar, Sapanca — with Sapanca's only chlorine-free pool and Mare Gastro restaurant."),
 ('<h5>Sayfalar</h5><ul><li><a href="/#odalar">Odalar</a></li><li><a href="/#mare">Mare Gastro</a></li><li><a href="/#konum">Konum</a></li><li><a href="/blog/">Blog</a></li><li><a href="/#galeri">Galeri</a></li></ul>',
  '<h5>Pages</h5><ul><li><a href="/en/odalar/">Rooms</a></li><li><a href="/en/#mare">Mare Gastro</a></li><li><a href="/en/#konum">Location</a></li><li><a href="/en/blog/">Blog</a></li><li><a href="/en/#galeri">Gallery</a></li></ul>'),
 ("<h5>İletişim</h5>", "<h5>Contact</h5>"), (">Yol Tarifi<", ">Directions<"),
 ("UniqBee Dijital Medya Ajansı", "UniqBee Digital Media Agency"),
 ('DİDİ Otel, <a href="https://otelyonet.com.tr/" target="_blank" rel="noopener">Otelyonet</a> sistemleri ile yönetilmektedir.',
  'DİDİ Hotel is managed with <a href="https://otelyonet.com.tr/" target="_blank" rel="noopener">Otelyonet</a> systems.'),
 ("© 2026 DİDİ Otel Sapanca. Tüm hakları saklıdır.", "© 2026 DİDİ Hotel Sapanca. All rights reserved."),
]:
    assert a in FOOT, a[:40]; FOOT = FOOT.replace(a, b)
FOOT = FOOT.replace('href="https://wa.me/905331350888?text=Merhaba%2C%20bilgi%20almak%20istiyorum."', 'href="https://wa.me/905331350888?text=Merhaba%2C%20bilgi%20almak%20istiyorum."')

CTA = ('<div class="art-cta"><h3>A quiet escape in nature, in Sapanca</h3>'
 '<p>DİDİ Otel Sapanca — a boutique stay between the lake and the forest in Kırkpınar.</p>'
 '<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">'
 f'<a href="{WA}" class="btn btn-fill">Check Availability</a>'
 '<a href="/en/odalar/" class="btn btn-line" style="border-color:rgba(255,255,255,.4);color:#fff">Explore Rooms</a></div>'
 '<p style="margin:18px 0 0;font-size:14px">Reservations by phone: <a href="tel:+902645921212" style="color:#fff" dir="ltr">0264 592 12 12</a> · WhatsApp: <a href="https://wa.me/905331350888" style="color:#fff" dir="ltr">0533 135 08 88</a></p></div>')

# ── içerik dönüşümleri ──
def fix_links(h):
    def blog(m):
        s = m.group(1); return f'href="/en/blog/{s}/"' if s in EN else m.group(0)
    h = re.sub(r'href="/blog/([^"/]+)/"', blog, h)
    h = h.replace('href="/blog/"', 'href="/en/blog/"')
    h = re.sub(r'href="/(#[a-z]+)"', r'href="/en/\1"', h)
    h = h.replace('href="/#odalar"', 'href="/en/odalar/"')
    h = re.sub(r'href="/odalar/', 'href="/en/odalar/', h)
    return h

def restore_figs(tr_body, en_body, slug):
    figs = re.findall(r"<figure>.*?</figure>", tr_body, re.S)
    toks = list(re.finditer(r"<FIG\b([^>]*)>(.*?)</FIG>", en_body, re.S))
    assert len(figs) == len(toks), (slug, len(figs), len(toks))
    out, last = [], 0
    for fg, t in zip(figs, toks):
        attrs, cap = t.group(1), t.group(2)
        if "yt-facade" in fg:
            ti = re.search(r'title="(.*?)"', attrs, re.S).group(1)
            fg = re.sub(r'data-title="[^"]*"', f'data-title="{ti}"', fg)
            fg = re.sub(r'aria-label="[^"]*"', f'aria-label="Play video: {ti}"', fg)
            fg = re.sub(r'(<img [^>]*?)alt="[^"]*"', lambda m: f'{m.group(1)}alt="{ti} — video preview"', fg)
        else:
            al = re.search(r'alt="(.*?)"\s*$', attrs.strip(), re.S).group(1)
            fg = re.sub(r'(<img [^>]*?)alt="[^"]*"', lambda m: f'{m.group(1)}alt="{al}"', fg)
        fg = re.sub(r"<figcaption>.*?</figcaption>", "", fg, flags=re.S)
        if cap.strip(): fg = fg.replace("</figure>", f"<figcaption>{cap}</figcaption></figure>")
        out.append(en_body[last:t.start()]); out.append(fg); last = t.end()
    out.append(en_body[last:])
    return "".join(out)

def plain(t): return html.unescape(re.sub(r"<[^>]+>", " ", t))

def read_time(lead, body): return max(3, round(len(plain(lead + " " + body).split()) / 200))

def ld_dumps(x): return f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'

def hreflang(tr, en):
    return (f'<link rel="alternate" hreflang="tr" href="{tr}">\n<link rel="alternate" hreflang="en" href="{en}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{tr}">')

def head(title, desc, canon, og_type, og_img, tr, extra=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
{gb.GA}
<title>{html.escape(title, quote=False)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#F5F1EA">
<link rel="canonical" href="{canon}">
{hreflang(tr, canon)}
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/assets/brand/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
{extra}
<link rel="stylesheet" href="/css/site.css?v=13">
{gb.BLOG_CSS}
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N68CWMCH"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
{gb.TRACK}
'''

def related(slug):
    tr = TR_BY[slug]
    rel = [s for s in tr.get("related", []) if s in EN and s != slug]
    rel += [s for s in SLUGS if s != slug and s not in rel and TR_BY[s]["cat"] == tr["cat"]]
    rel += [s for s in sorted(SLUGS, key=lambda x: TR_BY[x].get("mod", TR_BY[x]["date"]), reverse=True) if s != slug and s not in rel]
    return rel[:3]

def build_post(slug):
    t, e = TR_BY[slug], EN[slug]
    body = fix_links(restore_figs(t["body"], e["body"], slug))
    body = gb.wrap_tables(body)
    lead = fix_links(e["lead"])
    seo_title = e["seo_title"]
    og_img = f"{SITE}{IMG}/{t['img']}-1280.webp"
    mod = t.get("mod", t["date"])
    art = {"@context": "https://schema.org", "@type": "Article", "headline": e["title"], "description": e["desc"],
           "image": og_img, "datePublished": t["date"], "dateModified": mod,
           "author": {"@type": "Organization", "name": "DİDİ Otel Sapanca", "url": f"{SITE}/en/"},
           "publisher": {"@type": "Organization", "name": "DİDİ Otel Sapanca", "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/brand/adidilogo.png"}},
           "mainEntityOfPage": {"@type": "WebPage", "@id": en_url(slug)}, "inLanguage": "en"}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/en/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/en/blog/"},
        {"@type": "ListItem", "position": 3, "name": e["title"]}]}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "en", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in e["faq"]]}
    lds = [art, crumb, faq]
    if e.get("extra_ld"):
        x = dict(e["extra_ld"]); x.setdefault("inLanguage", "en"); lds.append(x)
    faq_html = "".join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in e["faq"])
    src_html = ('<section class="art-src"><h2>Sources</h2><ol>' + "".join(
        f'<li><a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(l)}</a></li>' for l, u in e["sources"]) + '</ol></section>') if e.get("sources") else ""
    upd = f'<span class="art-upd">Updated: {fmt_date(mod)}</span>' if mod != t["date"] else ""
    rel_html = "".join(
        f'<a href="/en/blog/{o}/" class="bcard"><div class="bcard-img">' + gb.pic(TR_BY[o]["img"], "33vw", alt=EN[o]["title"]) +
        f'</div><div class="bcard-body"><div class="cat">{html.escape(EN[o]["cat"])}</div><h3>{EN[o]["title"]}</h3></div></a>' for o in related(slug))
    yt_js = gb.YT_JS if "yt-facade" in body else ""
    page = head(seo_title, e["desc"], en_url(slug), "article", og_img, tr_url(slug), "\n".join(ld_dumps(x) for x in lds)) + f'''{nav(tr_url(slug))}
<article>
<header class="art-hero">
{gb.pic(t["img"], "100vw", alt=e["img_alt"], eager=True)}
<div class="art-hero-c">
<div class="cat">{html.escape(e["cat"])}</div>
<h1>{e["title"]}</h1>
<div class="art-meta"><span>{fmt_date(t["date"])}</span>{upd}<span>{read_time(lead, body)} min read</span><span>Sapanca</span></div>
</div>
</header>
<div class="article">
<div class="art-body">
<p class="lead-p">{lead}</p>
{body}
{src_html}
{CTA}
<section class="art-faq">
<h2>Frequently Asked Questions</h2>
{faq_html}
</section>
</div>
</div>
</article>
<section class="sec exp"><div class="wrap">
<div class="rev" style="margin-bottom:30px"><div class="kick">Blog</div><h2 class="dh">More <b>articles</b></h2></div>
<div class="blog-grid">{rel_html}</div>
</div></section>
{FOOT}
{gb.JS}
{yt_js}
</body>
</html>'''
    d = f"{ROOT}/en/blog/{slug}"; os.makedirs(d, exist_ok=True)
    open(f"{d}/index.html", "w", encoding="utf-8").write(page)

def build_index():
    order = sorted(SLUGS, key=lambda s: TR_BY[s].get("mod", TR_BY[s]["date"]), reverse=True)
    cards = "".join(
        f'<a href="/en/blog/{s}/" class="bcard rev"><div class="bcard-img">' + gb.pic(TR_BY[s]["img"], "(max-width:640px) 100vw,(max-width:960px) 50vw,33vw", alt=EN[s]["title"]) +
        f'</div><div class="bcard-body"><div class="cat">{html.escape(EN[s]["cat"])}</div><h3>{EN[s]["title"]}</h3><p>{html.escape(EN[s]["desc"])}</p><span class="more">Read more →</span></div></a>'
        for s in order)
    title = "Sapanca Travel & Stay Guide — Blog | DİDİ Otel Sapanca"
    desc = "Sapanca travel guide in English: getting there, lake activities, Kartepe and Maşukiye routes, local food, seasonal tips and stay advice from DİDİ Otel."
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "DİDİ Otel Sapanca Blog", "url": f"{SITE}/en/blog/", "inLanguage": "en",
          "description": "Sapanca travel guides, stay tips and nearby routes.",
          "blogPost": [{"@type": "BlogPosting", "headline": EN[s]["title"], "url": en_url(s), "datePublished": TR_BY[s]["date"], "dateModified": TR_BY[s].get("mod", TR_BY[s]["date"]), "inLanguage": "en"} for s in order]}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/en/"}, {"@type": "ListItem", "position": 2, "name": "Blog"}]}
    page = head(title, desc, f"{SITE}/en/blog/", "website", f"{SITE}{IMG}/otel-havuz-1280.webp", f"{SITE}/blog/", ld_dumps(ld) + "\n" + ld_dumps(crumb)) + f'''{nav(SITE + "/blog/")}
<section class="blog-hero"><div class="wrap">
<div class="kick" style="justify-content:center">DİDİ Otel Sapanca</div>
<h1 class="dh">Sapanca Travel &amp; Stay Guide</h1>
<p class="lead" style="max-width:56ch;margin:20px auto 0">Travel guides, nearby routes, seasonal advice and stay tips for anyone planning a trip to Sapanca.</p>
</div></section>
<section class="sec" style="padding-top:20px"><div class="wrap">
<div class="blog-grid">{cards}</div>
</div></section>
{FOOT}
{gb.JS}
</body>
</html>'''
    os.makedirs(f"{ROOT}/en/blog", exist_ok=True)
    open(f"{ROOT}/en/blog/index.html", "w", encoding="utf-8").write(page)

if __name__ == "__main__":
    for s in SLUGS: build_post(s)
    build_index()
    print(f"✓ en/blog/ index + {len(SLUGS)} posts")
