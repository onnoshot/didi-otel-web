#!/usr/bin/env python3
"""DİDİ Otel Sapanca — çok-dilli anasayfa üretici.
Tek kaynak: i18n/source.html (Türkçe şablon) + i18n/{tr,en,ru,ar,de}.json
Üretir: kök /index.html (TR, değişmez konum) + /en/ /ru/ /ar/ /de/ index.html.
Idempotent: her çalıştırmada sıfırdan üretir. Rezervasyon/iletişim WhatsApp
mesajları KASITLI olarak Türkçe kalır (personel her zaman Türkçe okur).
"""
import json, re, os

ROOT = os.path.dirname(os.path.abspath(__file__))       # .../i18n
PROJ = os.path.dirname(ROOT)                              # proje kökü
SITE = "https://www.sapancadidiotel.com"
LANGS = ["tr", "en", "ru", "ar", "de"]
OUT_LANGS = ["en", "ru", "ar", "de"]                       # tr kökte kalır
LOCALE   = {"tr": "tr_TR", "en": "en_US", "ru": "ru_RU", "ar": "ar_SA", "de": "de_DE"}
JSLOCALE = {"tr": "tr-TR", "en": "en-US", "ru": "ru-RU", "ar": "ar-SA", "de": "de-DE"}
LANGNAME = {"tr": "Türkçe", "en": "English", "ru": "Русский", "ar": "العربية", "de": "Deutsch"}
FLAG     = {"tr": "🇹🇷", "en": "🇬🇧", "ru": "🇷🇺", "ar": "🇸🇦", "de": "🇩🇪"}
RTL = {"ar"}

strings = {l: json.load(open(f"{ROOT}/{l}.json", encoding="utf-8")) for l in LANGS}
tr = strings["tr"]
src = open(f"{ROOT}/source.html", encoding="utf-8").read()

def lang_url(l):
    return f"{SITE}/" if l == "tr" else f"{SITE}/{l}/"

# ── 1. WhatsApp mesajlarını üreten JS bloklarını koru (personel her zaman Türkçe okur) ──
m = re.search(r"window\.resvSend=function\(\)\{.*?\};", src, re.S)
RESV_SEND = m.group(0)
src = src.replace(RESV_SEND, "@@RESVSEND@@")

m2 = re.search(r"function sendWA\(e\)\{.*?return false;\}", src, re.S)
SEND_WA = m2.group(0)
src = src.replace(SEND_WA, "@@SENDWA@@")

# ── 2. hreflang + dil değiştirici işaretçileri ──
src = re.sub(r'(<link rel="canonical"[^>]*>)', r"\1\n@@HREFLANG@@", src, count=1)
src = src.replace('<div class="nav-right">', '<div class="nav-right">@@LANGSW@@', 1)
src = re.sub(r'(<div class="mob" id="mob">)', r"\1@@MOBLANGS@@", src, count=1)

# ── 3. Tokenizasyon (uzun→kısa, &amp;/& toleranslı) ──
template = src
notfound = []
for key, s in sorted(tr.items(), key=lambda kv: -len(kv[1])):
    token = "@@%s@@" % key
    placed = False
    for cand in (s, s.replace("&amp;", "&"), s.replace("&", "&amp;")):
        if cand and cand in template:
            template = template.replace(cand, token)
            placed = True
            break
    if not placed:
        notfound.append((key, s))

if notfound:
    print("⚠️  Bulunamayan src (token uygulanmadı):")
    for k, s in notfound:
        print("   ", k, "=>", repr(s[:70]))

# ── 4. hreflang bloğu (tüm sayfalarda aynı) ──
hreflang = "\n".join(
    ['<link rel="alternate" hreflang="%s" href="%s">' % (("tr" if l == "tr" else l), lang_url(l)) for l in LANGS]
    + ['<link rel="alternate" hreflang="x-default" href="%s/">' % SITE]
)

# ── 5. Dil değiştirici (minimal, bayraklı dropdown — nav-right'ta) ──
LANGSW_CSS = (
    '<style>'
    '.langsw{position:relative;display:flex;align-items:center}'
    '.langsw-btn{display:flex;align-items:center;gap:6px;background:transparent;border:1px solid rgba(255,255,255,.35);'
    'color:#fff;font-family:var(--sf);font-size:12.5px;letter-spacing:.02em;padding:8px 12px;border-radius:100px;'
    'cursor:pointer;transition:background .3s var(--ease),border-color .3s var(--ease)}'
    '.nav.scr .langsw-btn{border-color:var(--line);color:var(--ink)}'
    '.langsw-btn:hover{background:rgba(255,255,255,.14)}'
    '.nav.scr .langsw-btn:hover{background:var(--bone)}'
    '.langsw-btn .chev{width:9px;height:9px;opacity:.7;transition:transform .3s var(--ease)}'
    '.langsw.open .chev{transform:rotate(180deg)}'
    '.langsw-menu{position:absolute;top:calc(100% + 10px);right:0;min-width:168px;background:var(--paper);'
    'border:1px solid var(--line);border-radius:14px;padding:6px;opacity:0;visibility:hidden;transform:translateY(-6px);'
    'transition:all .28s var(--ease);z-index:220;box-shadow:0 20px 50px rgba(26,25,22,.16)}'
    '.langsw.open .langsw-menu{opacity:1;visibility:visible;transform:translateY(0)}'
    '.langsw-menu a{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:9px;color:var(--ink);'
    'text-decoration:none;font-size:13.5px;letter-spacing:.01em;transition:background .2s}'
    '.langsw-menu a:hover{background:var(--bone)}'
    '.langsw-menu a.on{color:var(--green);font-weight:500}'
    '[dir=rtl] .langsw-menu{right:auto;left:0}'
    '.mob-langs{display:flex;flex-wrap:wrap;gap:8px;padding:18px 34px 4px;border-top:1px solid var(--line2)}'
    '.mob-langs a{display:flex;align-items:center;gap:7px;font-size:13.5px;color:var(--ink2);text-decoration:none;'
    'padding:8px 13px;border:1px solid var(--line);border-radius:100px}'
    '.mob-langs a.on{color:var(--green);border-color:var(--green)}'
    '</style>'
)

def langsw(cur):
    items = "".join(
        '<a href="%s" class="%s">%s %s</a>' % (lang_url(l), "on" if l == cur else "", FLAG[l], LANGNAME[l])
        for l in LANGS
    )
    return (
        LANGSW_CSS +
        '<div class="langsw" id="langsw">'
        '<button class="langsw-btn" onclick="document.getElementById(\'langsw\').classList.toggle(\'open\')" aria-label="Language / Dil">'
        + FLAG[cur] + ' ' + cur.upper() +
        '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>'
        '</button>'
        '<div class="langsw-menu">' + items + '</div>'
        '</div>'
        '<script>document.addEventListener("click",function(e){var s=document.getElementById("langsw");if(s&&!s.contains(e.target))s.classList.remove("open")})</script>'
    )

def mob_langs(cur):
    return '<div class="mob-langs">' + "".join(
        '<a href="%s" class="%s">%s %s</a>' % (lang_url(l), "on" if l == cur else "", FLAG[l], LANGNAME[l]) for l in LANGS
    ) + '</div>'

# ── 6. Her dil için üret ──
for l in LANGS:
    out = template
    d = strings[l]
    out = out.replace("@@HREFLANG@@", hreflang)
    out = out.replace("@@LANGSW@@", langsw(l))
    out = out.replace("@@MOBLANGS@@", mob_langs(l))
    out = out.replace("@@RESVSEND@@", RESV_SEND)
    out = out.replace("@@SENDWA@@", SEND_WA)
    for key, val in d.items():
        out = out.replace("@@%s@@" % key, val)

    leftover = re.findall(r"@@[\w]+@@", out)
    if leftover:
        print("⚠️  [%s] yerine konmayan token:" % l, set(leftover))

    # <html lang / dir>
    if l in RTL:
        out = out.replace('<html lang="tr">', '<html lang="%s" dir="rtl">' % l, 1)
    elif l != "tr":
        out = out.replace('<html lang="tr">', '<html lang="%s">' % l, 1)

    # canonical + og:url + JSON-LD "url" (bare-root exact matches only)
    out = out.replace('href="%s/"' % SITE, 'href="%s"' % lang_url(l))
    out = out.replace('content="%s/"' % SITE, 'content="%s"' % lang_url(l))
    out = out.replace('"url":"%s/"' % SITE, '"url":"%s"' % lang_url(l))
    out = out.replace('content="tr_TR"', 'content="%s"' % LOCALE[l])
    out = out.replace("'tr-TR'", "'%s'" % JSLOCALE[l])
    out = out.replace('"inLanguage":"tr"', '"inLanguage":"%s"' % l)
    if l != "tr":
        out = out.replace('href="/odalar/', 'href="/%s/odalar/' % l)

    outdir = PROJ if l == "tr" else f"{PROJ}/{l}"
    os.makedirs(outdir, exist_ok=True)
    open(f"{outdir}/index.html", "w", encoding="utf-8").write(out)

    # JS doğrulama (inline script'ler, ld+json ve src hariç) — node varsa
    import subprocess
    bad = 0
    for sc in re.findall(r'<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>(.*?)</script>', out, re.S):
        if not sc.strip():
            continue
        open("/tmp/_didi_i18n_chk.js", "w").write(sc)
        try:
            if subprocess.run(["node", "--check", "/tmp/_didi_i18n_chk.js"], capture_output=True).returncode != 0:
                bad += 1
        except FileNotFoundError:
            bad = -1
            break
    flag = "  ⚠️ JS HATASI!" if bad > 0 else ("" if bad == 0 else "  (node yok, JS doğrulanmadı)")
    print("✓ %s/index.html  (%d bytes)%s" % (outdir.replace(PROJ, "") or "/", len(out), flag))

print("\nTamam. Diller:", ", ".join(LANGS))
