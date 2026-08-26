#!/usr/bin/env python3
"""DİDİ Otel — oda detay sayfası üretici (5 dil: tr/en/ru/ar/de).
Her oda + dil için index.html üretir (paylaşılan css/site.css).
Galeriyi assets/web/rooms/<folder>/ içindeki görsellerden kurar. Idempotent.
Metinler i18n/{lang}.json (ortak arayüz) + i18n/rooms_i18n.json (oda içerikleri) içinden gelir.
"""
import os, glob, re, html, json
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
I18N = f"{ROOT}/i18n"
_strip = lambda t: re.sub(r"<[^>]+>", "", t)
SITE = "https://www.sapancadidiotel.com"

LANGS = ["tr", "en", "ru", "ar", "de"]
LOCALE   = {"tr": "tr_TR", "en": "en_US", "ru": "ru_RU", "ar": "ar_SA", "de": "de_DE"}
LANGNAME = {"tr": "Türkçe", "en": "English", "ru": "Русский", "ar": "العربية", "de": "Deutsch"}
FLAG     = {"tr": "🇹🇷", "en": "🇬🇧", "ru": "🇷🇺", "ar": "🇸🇦", "de": "🇩🇪"}
RTL = {"ar"}

UI = {l: json.load(open(f"{I18N}/{l}.json", encoding="utf-8")) for l in LANGS}
ROOMS_I18N = json.load(open(f"{I18N}/rooms_i18n.json", encoding="utf-8"))

ROOMS_META = [
 {"slug": "king-suit", "folder": "king-suit", "id": 4},
 {"slug": "junior-suit", "folder": "junior-suit", "id": 5},
 {"slug": "superior", "folder": "superior", "id": 6},
 {"slug": "aile", "folder": "family", "id": 7},
 {"slug": "triple", "folder": "triple", "id": 8},
]
SLUGS = [m["slug"] for m in ROOMS_META]
CAP_BY_SLUG = {"king-suit": 2, "junior-suit": 2, "superior": 2, "aile": 4, "triple": 3}

BASE_AM_KEYS = ["amenity_klima", "amenity_tv_uydu", "amenity_wifi", "amenity_minibar",
                "amenity_su_isitici", "amenity_sac_kurutma", "amenity_dusakabin", "amenity_banyo_malzeme"]

GA = '''<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-N68CWMCH');</script>
<!-- End Google Tag Manager -->'''
TRACK = '''<!-- DataLayer events -->
<script>(function(){var dl=window.dataLayer=window.dataLayer||[];function region(el){if(el.closest('#mob')||el.closest('.mob'))return'hamburger';if(el.closest('#nav')||el.closest('nav'))return'header';if(el.closest('footer'))return'footer';if(el.closest('.resv-modal'))return'reservation_form';if(el.closest('.resbar'))return'sticky_bar';if(el.closest('.cta-sec')||el.closest('.cta'))return'cta';if(el.closest('.hhero')||el.closest('.hero')||el.closest('.rhero'))return'hero';if(el.closest('#iletisim')||el.closest('.contact'))return'contact';if(el.closest('#mare'))return'mare';if(el.closest('.hcard')||el.closest('.rdetail')||el.closest('.rside'))return'room';if(el.closest('.wa'))return'float';return'page';}function menuName(href,txt){href=(href||'').toLowerCase();var m=[['iletisim','iletisim'],['konum','konum'],['blog','blog'],['deneyim','deneyim'],['galeri','galeri'],['mare','mare'],['odalar','odalar']];for(var i=0;i<m.length;i++)if(href.indexOf(m[i][0])>=0)return m[i][1];return(txt||'').trim().toLowerCase().slice(0,40);}document.addEventListener('click',function(e){var a=e.target.closest('a,button');if(!a)return;var href=a.getAttribute('href')||'',hl=href.toLowerCase(),onc=a.getAttribute('onclick')||'';if(onc.indexOf('resvOpen')>=0){dl.push({event:'availability_check',event_label:region(a)});return;}if(hl.indexOf('wa.me')>=0||hl.indexOf('whatsapp')>=0||(a.classList&&a.classList.contains('btn-wa'))||/whatsapp/i.test(a.textContent||'')){dl.push({event:'whatsapp_click',event_label:region(a)});return;}if(hl.indexOf('tel:')===0){dl.push({event:'phone_click',event_label:region(a)});return;}if(a.tagName==='A'&&(a.closest('.nav-links')||a.closest('#mob')||a.closest('footer'))){dl.push({event:'menu_click',event_label:region(a),element:menuName(href,a.textContent)});return;}},true);})();</script>'''
CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg>'

# ── özellik/donanım ikonları (SVG, stroke=currentColor) ──
_IC = {
 "jakuzi":'<path d="M4 12h16v4a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z"/><path d="M6 12V6.5A2.5 2.5 0 0 1 8.5 4A2.5 2.5 0 0 1 11 6.5"/><path d="M3 16h18"/><path d="M8 20l-1 1.5M16 20l1 1.5"/>',
 "sofa":'<path d="M4 11V8.5A2.5 2.5 0 0 1 6.5 6h11A2.5 2.5 0 0 1 20 8.5V11"/><path d="M3 12.5A2.5 2.5 0 0 1 5.5 10h13a2.5 2.5 0 0 1 2.5 2.5V17H3z"/><path d="M6 17v2M18 17v2"/>',
 "door":'<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M12 3v18M4 12h16"/>',
 "view":'<path d="m3 17 4-6 4 5 3-4 7 6"/><circle cx="7.5" cy="6.5" r="2"/>',
 "shower":'<path d="M4 4h5a4 4 0 0 1 4 4"/><circle cx="17" cy="5.5" r="2.5"/><path d="M13 12v.5M16 12v.5M19 12v.5M14 15.5v.5M17 15.5v.5M15 19v.5M18 19v.5"/>',
 "link":'<path d="M9 12h6"/><path d="M8 8H6.5a3.5 3.5 0 0 0 0 7H8M16 8h1.5a3.5 3.5 0 0 1 0 7H16"/>',
 "bath":'<path d="M4 12h16v4a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z"/><path d="M6 12V6.5A2.5 2.5 0 0 1 8.5 4A2.5 2.5 0 0 1 11 6.5"/><path d="M3 16h18"/>',
 "climate":'<path d="M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h9a3 3 0 1 1-3 3"/>',
 "tv":'<rect x="2" y="4" width="20" height="14" rx="2"/><path d="M8 21h8M12 18v3"/>',
 "wifi":'<path d="M5 12.55a11 11 0 0 1 14 0M8.5 16.4a5 5 0 0 1 7 0M2 8.82a15 15 0 0 1 20 0"/><circle cx="12" cy="20" r="1" fill="currentColor" stroke="none"/>',
 "fridge":'<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M6 10h12M10 6v.5M10 14v.5"/>',
 "kettle":'<path d="M5 11h11l.8 7a2 2 0 0 1-2 2.2H6.2A2 2 0 0 1 4.2 18z"/><path d="M16 12.5h3.3l-1-4.5H15"/><path d="M9 7.5c0-1.2 1-1.2 1-2.2"/>',
 "dryer":'<path d="M3 8.5A4.5 4.5 0 0 1 7.5 4h5l5.5 2.2v3.6L12.5 12h-5A4.5 4.5 0 0 1 3 8.5z"/><path d="M10 12v4.5A2.5 2.5 0 0 0 12.5 19"/><circle cx="7.5" cy="8.2" r="1"/>',
 "soap":'<rect x="8" y="9" width="8" height="12" rx="2"/><path d="M10 9V6.5a2 2 0 0 1 4 0V9M11 4h2"/>',
 "bed":'<path d="M2 8v11M22 13v6M2 14h20v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4"/><path d="M6 10V8.5A1.5 1.5 0 0 1 7.5 7h3V11"/>',
 "users":'<circle cx="9" cy="8" r="3.2"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16.5 5.2a3.2 3.2 0 0 1 0 5.6M21.5 20a6.5 6.5 0 0 0-4.5-6.2"/>',
 "star":'<path d="M12 3l2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.9 6.7 19l1-5.8L3.5 9.2l5.9-.9z"/>',
 "check":'<path d="M20 6 9 17l-5-5"/>',
}
def _svg(k, w="1.7"):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round">{_IC.get(k,_IC["check"])}</svg>'
# anahtar kelime -> ikon (öncelik sırası) — HER ZAMAN TR metne göre eşleştirilir (dil bağımsız ikon seçimi için)
_MAP = [("jakuzi","jakuzi"),("küvet","jakuzi"),("bağlant","link"),
        ("oturma","sofa"),("salon","sofa"),("köşe","sofa"),("ferah","sofa"),("düzen","sofa"),
        ("fransız","door"),("balkon","door"),("manzara","view"),("göl","view"),("orman","view"),
        ("duş","shower"),("duşakabin","shower"),("banyo malzeme","soap"),("malzeme","soap"),("banyo","bath"),
        ("klima","climate"),("tv","tv"),("wifi","wifi"),("minibar","fridge"),
        ("ısıt","kettle"),("su ","kettle"),("saç","dryer"),("kurutma","dryer"),
        ("yatak","bed"),("king","bed"),("kişi","users"),("misafir","users")]
def feat_icon(tr_name):
    n = tr_name.lower()
    for kw, ic in _MAP:
        if kw in n:
            return _svg(ic)
    return _svg("check", "2")

def imgs_for(folder):
    base = f"{ROOT}/assets/web/rooms/{folder}"
    nums = sorted({re.match(r'(\d+)',os.path.basename(f)).group(1)
                   for f in glob.glob(f"{base}/*.jpg") if re.match(r'\d+\.jpg',os.path.basename(f))})
    return nums

def picture(folder, n, sizes, cls="", alt="", lazy=True, w=1280, h=960):
    p=f"/assets/web/rooms/{folder}/{n}"
    lo='loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
    return (f'<picture><source type="image/avif" srcset="{p}-800.avif 800w,{p}-1280.avif 1280w" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{p}-800.webp 800w,{p}-1280.webp 1280w" sizes="{sizes}">'
            f'<img src="{p}.jpg" {lo} width="{w}" height="{h}" alt="{alt}" class="{cls}"></picture>')

def room_url(lang, slug):
    base = SITE if lang == "tr" else f"{SITE}/{lang}"
    return f"{base}/odalar/{slug}/"

def home_url(lang):
    return f"{SITE}/" if lang == "tr" else f"{SITE}/{lang}/"

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

def langsw(cur, slug):
    items = "".join(
        '<a href="%s" class="%s">%s %s</a>' % (room_url(l, slug), "on" if l == cur else "", FLAG[l], LANGNAME[l])
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

def mob_langs(cur, slug):
    return '<div class="mob-langs">' + "".join(
        '<a href="%s" class="%s">%s %s</a>' % (room_url(l, slug), "on" if l == cur else "", FLAG[l], LANGNAME[l]) for l in LANGS
    ) + '</div>'

def nav_html(lang, slug):
    d = UI[lang]
    wa_text = quote('Merhaba, DİDİ Otel Sapanca için rezervasyon yapmak istiyorum.')
    return f'''<nav class="nav" id="nav">
<a href="{home_url(lang)}" class="nav-logo" aria-label="DİDİ Otel Sapanca"><img class="logo-w" src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><img class="logo-n" src="/assets/brand/adidilogo-navy.png" alt="" aria-hidden="true"></a>
<div class="nav-links">
<a href="{home_url(lang)}odalar/">{d["nav_odalar"]}</a><a href="{home_url(lang)}#deneyim">{d["nav_deneyim"]}</a><a href="{home_url(lang)}#mare">Mare Gastro</a><a href="{home_url(lang)}#konum">{d["nav_konum"]}</a><a href="{home_url(lang)}#iletisim">{d["nav_iletisim"]}</a>
</div>
<div class="nav-right">{langsw(lang, slug)}
<a href="tel:+905331350888" class="btn btn-line" dir="ltr">0533 135 08 88</a>
<a href="https://wa.me/905331350888?text={wa_text}" class="btn btn-fill">{d["nav_rezervasyon"]}</a>
<button class="burger" id="burger" aria-label="{d["nav_menu_aria"]}"><span></span><span></span><span></span></button>
</div>
</nav>
<div class="mob" id="mob">{mob_langs(lang, slug)}
<a href="{home_url(lang)}odalar/">{d["nav_odalar"]}</a><a href="{home_url(lang)}#deneyim">{d["nav_deneyim"]}</a><a href="{home_url(lang)}#mare">Mare Gastro</a><a href="{home_url(lang)}#konum">{d["nav_konum"]}</a><a href="{home_url(lang)}#iletisim">{d["nav_iletisim"]}</a>
<a href="https://wa.me/905331350888?text={wa_text}" style="color:var(--green)">{d["mob_rez_yap"]}</a>
</div>'''

def foot_html(lang):
    d = UI[lang]
    return f'''<footer class="foot"><div class="wrap">
<div class="foot-grid">
<div><img src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><p>{d["foot_desc"]}</p></div>
<div><h5>{d["foot_sayfalar"]}</h5><ul><li><a href="{home_url(lang)}odalar/">{d["nav_odalar"]}</a></li><li><a href="{home_url(lang)}#deneyim">{d["nav_deneyim"]}</a></li><li><a href="{home_url(lang)}#mare">Mare Gastro</a></li><li><a href="{home_url(lang)}#konum">{d["nav_konum"]}</a></li><li><a href="{home_url(lang)}#galeri">{d["gal_kick"]}</a></li></ul></div>
<div><h5>{d["nav_iletisim"]}</h5><ul><li><a href="tel:+902645921212" dir="ltr">0264 592 12 12</a></li><li><a href="https://wa.me/905331350888">WhatsApp</a></li><li><a href="mailto:info@sapancadidiotel.com">info@sapancadidiotel.com</a></li><li><a href="https://www.google.com/maps/dir/?api=1&destination=K%C4%B1rkp%C4%B1nar+Sapanca%2C+Sakarya" target="_blank" rel="noopener">{d["foot_yol_tarifi"]}</a></li></ul></div>
</div>
<div class="foot-credits"><a class="foot-madeby" href="https://uniqbee.com" target="_blank" rel="noopener"><img class="mb-ico" src="/assets/brand/uniqbee.svg" alt="UniqBee" width="22" height="22"><span class="mb-name">{d["foot_credit1"]}</span></a><span class="foot-managed">{d["foot_credit2"]}</span></div>
<div class="foot-bot"><span>{d["foot_rights"]}</span><span>Kırkpınar · Sapanca · Sakarya</span></div>
</div></footer>
<a class="wa" href="https://wa.me/905331350888?text=Merhaba%2C%20bilgi%20almak%20istiyorum." target="_blank" rel="noopener" aria-label="WhatsApp"><svg viewBox="0 0 24 24"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.7.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.5-.7-2.5-1.3-3.5-3-.3-.5.3-.4.8-1.4.1-.2 0-.4 0-.5 0-.1-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5 1.9.8 2.6.9 3.5.7.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3zM12 2a10 10 0 0 0-8.6 15l-1.4 5 5.2-1.4A10 10 0 1 0 12 2z"/></svg></a>
<div class="lb" id="lb"><button class="x" id="lbX" aria-label="{d["aria_kapat"]}">×</button><button class="pv" id="lbPrev" aria-label="{d["aria_onceki"]}">‹</button><img id="lbImg" src="" alt=""><button class="nx" id="lbNext" aria-label="{d["aria_sonraki"]}">›</button></div>'''

JS = '''<script>
const nav=document.getElementById('nav');addEventListener('scroll',()=>nav.classList.toggle('scr',scrollY>40),{passive:true});
const burger=document.getElementById('burger'),mob=document.getElementById('mob');
burger.addEventListener('click',()=>{burger.classList.toggle('x');mob.classList.toggle('open');document.body.style.overflow=mob.classList.contains('open')?'hidden':''});
mob.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{burger.classList.remove('x');mob.classList.remove('open');document.body.style.overflow=''}));
const io=new IntersectionObserver((es,o)=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');o.unobserve(e.target)}}),{threshold:.12,rootMargin:'0px 0px -7% 0px'});
document.querySelectorAll('.rev').forEach(el=>io.observe(el));
const lb=document.getElementById('lb'),lbImg=document.getElementById('lbImg');let items=[],idx=0;
document.querySelectorAll('[data-lb]').forEach(a=>{items.push(a.getAttribute('data-lb'));a.addEventListener('click',e=>{e.preventDefault();idx=items.indexOf(a.getAttribute('data-lb'));show()})});
function show(){lbImg.src=items[idx];lb.classList.add('open');document.body.style.overflow='hidden'}
function close(){lb.classList.remove('open');document.body.style.overflow=''}
function go(d){idx=(idx+d+items.length)%items.length;lbImg.src=items[idx]}
document.getElementById('lbX').addEventListener('click',close);document.getElementById('lbPrev').addEventListener('click',()=>go(-1));document.getElementById('lbNext').addEventListener('click',()=>go(1));
lb.addEventListener('click',e=>{if(e.target===lb)close()});
addEventListener('keydown',e=>{if(!lb.classList.contains('open'))return;if(e.key==='Escape')close();if(e.key==='ArrowRight')go(1);if(e.key==='ArrowLeft')go(-1)});
</script>'''

def hreflang_block(slug):
    lines = ['<link rel="alternate" hreflang="%s" href="%s">' % (l, room_url(l, slug)) for l in LANGS]
    lines.append('<link rel="alternate" hreflang="x-default" href="%s">' % room_url("tr", slug))
    return "\n".join(lines)

def build(meta, lang):
    slug, folder = meta["slug"], meta["folder"]
    r = ROOMS_I18N[lang][slug]
    r_tr = ROOMS_I18N["tr"][slug]
    d = UI[lang]
    nums = imgs_for(folder)
    hero = picture(folder, nums[0], "100vw", alt=r["name"], lazy=False, w=1280, h=960)

    base_am_tr = [UI["tr"][k] for k in BASE_AM_KEYS]
    base_am_loc = [d[k] for k in BASE_AM_KEYS]
    am_pairs = list(zip(base_am_tr, base_am_loc)) + list(zip(r_tr["extra"], r["extra"]))
    amgrid = "".join(f'<div class="am-it">{feat_icon(tr_txt)}<span>{loc_txt}</span></div>' for tr_txt, loc_txt in am_pairs)
    hl = "".join(f'<div class="rhl-card"><div class="rhl-ic">{feat_icon(tr_e)}</div><div class="rhl-t">{loc_e}</div></div>'
                 for tr_e, loc_e in zip(r_tr["extra"], r["extra"]))
    gal = "".join(f'<a data-lb="/assets/web/rooms/{folder}/{n}.jpg">'
                  + picture(folder, n, "(max-width:560px) 100vw,(max-width:960px) 50vw,33vw", alt=f'{r["name"]} - {i+1}')
                  + '</a>' for i, n in enumerate(nums))
    desc = "".join(f'<p class="lead">{p}</p>' for p in r["desc"])
    others = [m for m in ROOMS_META if m["slug"] != slug]
    ocards = "".join(f'<a href="{room_url(lang, o["slug"])}" class="ocard">'
                     + picture(o["folder"], imgs_for(o["folder"])[0], "25vw", alt=ROOMS_I18N[lang][o["slug"]]["name"])
                     + f'<span>{ROOMS_I18N[lang][o["slug"]]["name"]}</span></a>' for o in others)

    ld = {
      "@context": "https://schema.org", "@type": "HotelRoom", "name": r["name"],
      "url": room_url(lang, slug),
      "description": _strip(r["desc"][0]),
      "occupancy": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": CAP_BY_SLUG[slug]},
      "bed": {"@type": "BedDetails", "typeOfBed": r["bed"]},
      "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": a, "value": True} for a in ([d[k] for k in BASE_AM_KEYS] + r["extra"])],
      "containedInPlace": {"@id": f"{SITE}/#hotel"},
      "image": f'{SITE}/assets/web/rooms/{folder}/{nums[0]}-1280.webp',
      "inLanguage": lang}
    crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": d["room_breadcrumb_anasayfa"], "item": home_url(lang)},
        {"@type": "ListItem", "position": 2, "name": d["nav_odalar"], "item": home_url(lang) + "odalar/"},
        {"@type": "ListItem", "position": 3, "name": r["name"]}]}

    title = f'{r["name"]} | DİDİ Otel Sapanca'
    desc_meta = f'{r["name"]} — DİDİ Otel Sapanca. {_strip(r["desc"][0])[:120]}'
    lang_attr = f'lang="{lang}" dir="rtl"' if lang in RTL else f'lang="{lang}"'
    page = f'''<!DOCTYPE html>
<html {lang_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
{GA}
<title>{title}</title>
<meta name="description" content="{html.escape(desc_meta)}">
<meta name="theme-color" content="#F5F1EA">
<link rel="canonical" href="{room_url(lang, slug)}">
{hreflang_block(slug)}
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc_meta)}">
<meta property="og:url" content="{room_url(lang, slug)}">
<meta property="og:image" content="{SITE}/assets/web/rooms/{folder}/{nums[0]}-1280.webp">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/assets/brand/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(crumb_ld,ensure_ascii=False)}</script>
<link rel="stylesheet" href="/css/site.css?v=13">
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N68CWMCH"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
{TRACK}
<div class="prog" id="prog" style="display:none"></div>
{nav_html(lang, slug)}
<header class="rhero">
{hero}
<div class="rhero-c">
<div class="crumb"><a href="{home_url(lang)}">{d["room_breadcrumb_anasayfa"]}</a> · <a href="{home_url(lang)}odalar/">{d["nav_odalar"]}</a> · {r["name"]}</div>
<div class="rtag">{_svg("star")}{r["tag"]}</div>
<h1 class="thin">{r["name"]}</h1>
<div class="rmeta-row"><span>{_svg("users")}{r["capt"]}</span><span>{_svg("bed")}{r["bed"]}</span></div>
</div>
</header>

<section class="sec rhl-sec"><div class="wrap">
<div class="rev" style="text-align:center;margin-bottom:38px"><div class="kick" style="justify-content:center">{d["room_hl_kick"]}</div><h2 class="dh">{d["room_hl_h2"]}</h2></div>
<div class="rhl rev">{hl}</div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap rdetail">
<div class="rdesc rev">
<div class="kick">{d["room_detail_kick"]}</div>
{desc}
<div class="am-title">{d["room_donanim_title"]}</div>
<div class="amgrid">{amgrid}</div>
</div>
<aside class="rside rev">
<div class="rside-facts">
<div class="rf"><span class="rf-ic">{_svg("users")}</span><div><div class="rf-l">{d["room_kapasite"]}</div><div class="rf-v">{r["capt"]}</div></div></div>
<div class="rf"><span class="rf-ic">{_svg("bed")}</span><div><div class="rf-l">{d["room_yatak_duzeni"]}</div><div class="rf-v">{r["bed"]}</div></div></div>
<div class="rf"><span class="rf-ic">{feat_icon(r_tr["extra"][0])}</span><div><div class="rf-l">{d["room_one_cikan"]}</div><div class="rf-v">{r["extra"][0]}</div></div></div>
</div>
<div class="rside-badge">{_svg("star")}{d["room_price_badge"]}</div>
<a href="https://wa.me/905331350888?text={quote('Merhaba, DİDİ Otel Sapanca '+r_tr["name"]+' için rezervasyon yapmak istiyorum.')}" class="btn btn-fill" style="width:100%;justify-content:center">{d["btn_bu_odayi_sec"]}</a>
<div class="note">{d["room_note_wa"]}</div>
</aside>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
<div class="rev" style="margin-bottom:40px"><div class="kick">{d["gal_kick"]}</div><h2 class="dh">{r["name"]} <b>{d["room_gal_h2_suffix"]}</b></h2></div>
<div class="rgal">{gal}</div>
</div></section>

<section class="sec exp"><div class="wrap">
<div class="rev" style="margin-bottom:8px"><div class="kick">{d["room_diger_kick"]}</div><h2 class="dh">{d["room_diger_h2"]}</h2></div>
<div class="others rev">{ocards}</div>
</div></section>

{foot_html(lang)}
{JS}
</body>
</html>'''
    outdir = ROOT if lang == "tr" else f"{ROOT}/{lang}"
    outdir = f"{outdir}/odalar/{slug}"
    os.makedirs(outdir, exist_ok=True)
    open(f'{outdir}/index.html', 'w', encoding='utf-8').write(page)
    return len(nums)

if __name__ == "__main__":
    for meta in ROOMS_META:
        for lang in LANGS:
            n = build(meta, lang)
        print(f'✓ odalar/{meta["slug"]}/  (5 dil, {n} foto)')
    print("Tamam.")
