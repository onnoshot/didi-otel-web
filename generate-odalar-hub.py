#!/usr/bin/env python3
"""DİDİ Otel — Odalar & Suitler HUB üretici (5 dil: tr/en/ru/ar/de).
/odalar/ (+ /en/odalar/ ...) — app-hissiyatlı, mobil-öncelikli, filtreli,
'hangi oda size uygun' rehberli, tam schema (ItemList/FAQ/Breadcrumb) landing.
Oda içeriği i18n/rooms_i18n.json, arayüz i18n/{lang}.json'dan gelir. Idempotent.
"""
import os, glob, re, html, json

ROOT = os.path.dirname(os.path.abspath(__file__))
I18N = f"{ROOT}/i18n"
_strip = lambda t: re.sub(r"<[^>]+>", "", t)
SITE = "https://www.sapancadidiotel.com"
WA = "905331350888"

LANGS = ["tr", "en", "ru", "ar", "de"]
LOCALE = {"tr": "tr_TR", "en": "en_US", "ru": "ru_RU", "ar": "ar_SA", "de": "de_DE"}
LANGNAME = {"tr": "Türkçe", "en": "English", "ru": "Русский", "ar": "العربية", "de": "Deutsch"}
FLAG = {"tr": "🇹🇷", "en": "🇬🇧", "ru": "🇷🇺", "ar": "🇸🇦", "de": "🇩🇪"}
RTL = {"ar"}

UI = {l: json.load(open(f"{I18N}/{l}.json", encoding="utf-8")) for l in LANGS}
ROOMS_I18N = json.load(open(f"{I18N}/rooms_i18n.json", encoding="utf-8"))

ROOMS_META = [
 {"slug": "king-suit", "folder": "king-suit"},
 {"slug": "junior-suit", "folder": "junior-suit"},
 {"slug": "superior", "folder": "superior"},
 {"slug": "aile", "folder": "family"},
 {"slug": "triple", "folder": "triple"},
]
CAP_BY_SLUG = {"king-suit": 2, "junior-suit": 2, "superior": 2, "aile": 4, "triple": 3}
# filtre etiketleri (oda -> nitelikler)
ROOM_TAGS = {
 "king-suit": ["couple", "jacuzzi", "view"],
 "junior-suit": ["couple"],
 "superior": ["couple", "view"],
 "aile": ["family", "view"],
 "triple": ["group", "view"],
}
BASE_AM_KEYS = ["amenity_klima", "amenity_tv_uydu", "amenity_wifi", "amenity_minibar",
                "amenity_su_isitici", "amenity_sac_kurutma", "amenity_dusakabin", "amenity_banyo_malzeme"]

GA = '''<link rel="preconnect" href="https://www.googletagmanager.com"><link rel="preconnect" href="https://connect.facebook.net" crossorigin>
<link rel="dns-prefetch" href="https://www.google-analytics.com"><link rel="dns-prefetch" href="https://www.facebook.com">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-C8D22FPDET"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-C8D22FPDET');</script>
<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','1475183377973476');fbq('track','PageView');</script>
<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=1475183377973476&ev=PageView&noscript=1"/></noscript>'''

# ── SVG ikonları (oda özelliği adına göre) ──
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
 "heart":'<path d="M12 21C5 15.5 3 12 3 8.5A4.5 4.5 0 0 1 12 6a4.5 4.5 0 0 1 9 2.5C21 12 19 15.5 12 21z"/>',
 "check":'<path d="M20 6 9 17l-5-5"/>',
}
def _svg(k, w="1.7"):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round">{_IC.get(k,_IC["check"])}</svg>'
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
    return sorted({re.match(r'(\d+)', os.path.basename(f)).group(1)
                   for f in glob.glob(f"{base}/*.jpg") if re.match(r'\d+\.jpg', os.path.basename(f))})

def picture(folder, n, sizes, alt="", lazy=True, w=1280, h=960):
    p = f"/assets/web/rooms/{folder}/{n}"
    lo = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
    return (f'<picture><source type="image/avif" srcset="{p}-800.avif 800w,{p}-1280.avif 1280w" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{p}-800.webp 800w,{p}-1280.webp 1280w" sizes="{sizes}">'
            f'<img src="{p}.jpg" {lo} width="{w}" height="{h}" alt="{html.escape(alt)}"></picture>')

def home_url(lang):
    return f"{SITE}/" if lang == "tr" else f"{SITE}/{lang}/"
def room_url(lang, slug):
    return f"{home_url(lang)}odalar/{slug}/"
def hub_url(lang):
    return f"{home_url(lang)}odalar/"

# ── HUB arayüz metinleri (chrome) ──
HUB = {
 "tr": {"title":"Odalar & Suitler | DİDİ Otel Sapanca — Göl ve Orman Arasında",
   "desc":"DİDİ Otel Sapanca odaları ve suitleri: King Suit (oda içi jakuzi), Junior Suit, Superior (Fransız balkon), Aile ve Triple. Göl ile orman arasında, aracısız en uygun fiyat.",
   "kick":"Konaklama","h1_1":"Odalar &","h1_2":"Suitler",
   "sub":"Beş özenle tasarlanmış oda tipi — çiftlerden ailelere, jakuzili süitten bağlantılı aile odasına. Hepsi göl ile orman arasında, aracısız en uygun fiyatla.",
   "s1":"5 oda tipi","s2":"Göl + orman","s3":"Aracısız en iyi fiyat",
   "filters":{"all":"Tümü","couple":"2 Kişilik","family":"Aile","group":"3 Kişilik","jacuzzi":"Jakuzili","view":"Manzaralı"},
   "match_kick":"Kişiye Özel","match_h2":"Hangi oda size uygun?","match_lead":"Kiminle geldiğinize göre en doğru seçim:",
   "personas":[("heart","Çift & Balayı","Oda içi jakuzi, salon ve doğa manzarasıyla en özel kaçamak.","king-suit"),
     ("view","Manzara Sevenler","Fransız balkon ve göl/bahçe manzarasıyla aydınlık bir oda.","superior"),
     ("users","Aileler","Bağlantılı iki oda, iki banyo — bir arada ama mahremiyetli.","aile"),
     ("bed","Gruplar / 3 Kişi","Üç kişilik ferah düzen ve bahçe manzaralı balkon.","triple")],
   "amen_kick":"Standart","amen_h2":"Her odada dahil",
   "resbar":"Aracısız en iyi fiyat","see_room":"Odayı incele"},
 "en": {"title":"Rooms & Suites | DİDİ Hotel Sapanca — Between Lake and Forest",
   "desc":"DİDİ Hotel Sapanca rooms and suites: King Suite (in-room jacuzzi), Junior Suite, Superior (French balcony), Family and Triple. Between lake and forest, best direct price.",
   "kick":"Stay","h1_1":"Rooms &","h1_2":"Suites",
   "sub":"Five thoughtfully designed room types — from couples to families, from a jacuzzi suite to a connected family room. All between lake and forest, at the best direct price.",
   "s1":"5 room types","s2":"Lake + forest","s3":"Best direct price",
   "filters":{"all":"All","couple":"For 2","family":"Family","group":"For 3","jacuzzi":"Jacuzzi","view":"View"},
   "match_kick":"Tailored","match_h2":"Which room suits you?","match_lead":"The right choice based on who you travel with:",
   "personas":[("heart","Couples & Honeymoon","In-room jacuzzi, lounge and nature views for the most special escape.","king-suit"),
     ("view","View Lovers","A bright room with a French balcony and lake/garden view.","superior"),
     ("users","Families","Two connected rooms, two bathrooms — together yet private.","aile"),
     ("bed","Groups / 3 Guests","A spacious three-person layout with a garden-view balcony.","triple")],
   "amen_kick":"Standard","amen_h2":"Included in every room",
   "resbar":"Best direct price","see_room":"View room"},
 "ru": {"title":"Номера и сюиты | Отель DİDİ Сапанджа — Между озером и лесом",
   "desc":"Номера и сюиты отеля DİDİ Сапанджа: King Suite (джакузи в номере), Junior Suite, Superior (французский балкон), семейный и трёхместный. Между озером и лесом, лучшая прямая цена.",
   "kick":"Проживание","h1_1":"Номера и","h1_2":"сюиты",
   "sub":"Пять продуманных типов номеров — от пар до семей, от сюита с джакузи до смежного семейного номера. Все между озером и лесом, по лучшей прямой цене.",
   "s1":"5 типов номеров","s2":"Озеро + лес","s3":"Лучшая прямая цена",
   "filters":{"all":"Все","couple":"На 2","family":"Семья","group":"На 3","jacuzzi":"Джакузи","view":"С видом"},
   "match_kick":"Индивидуально","match_h2":"Какой номер вам подходит?","match_lead":"Правильный выбор в зависимости от компании:",
   "personas":[("heart","Пары и медовый месяц","Джакузи в номере, гостиная и виды на природу для особого отдыха.","king-suit"),
     ("view","Любителям видов","Светлый номер с французским балконом и видом на озеро/сад.","superior"),
     ("users","Семьям","Два смежных номера, две ванные — вместе и уединённо.","aile"),
     ("bed","Группы / 3 гостя","Просторная планировка на троих с балконом в сад.","triple")],
   "amen_kick":"Стандарт","amen_h2":"Включено в каждом номере",
   "resbar":"Лучшая прямая цена","see_room":"Смотреть номер"},
 "ar": {"title":"الغرف والأجنحة | فندق ديدي سبانجا — بين البحيرة والغابة",
   "desc":"غرف وأجنحة فندق ديدي سبانجا: كينغ سويت (جاكوزي داخل الغرفة)، جونيور سويت، سوبيريور (شرفة فرنسية)، عائلية وثلاثية. بين البحيرة والغابة، أفضل سعر مباشر.",
   "kick":"الإقامة","h1_1":"الغرف","h1_2":"والأجنحة",
   "sub":"خمسة أنواع غرف مصممة بعناية — من الأزواج إلى العائلات، من جناح بجاكوزي إلى غرفة عائلية متصلة. جميعها بين البحيرة والغابة، بأفضل سعر مباشر.",
   "s1":"5 أنواع غرف","s2":"بحيرة + غابة","s3":"أفضل سعر مباشر",
   "filters":{"all":"الكل","couple":"لشخصين","family":"عائلية","group":"لثلاثة","jacuzzi":"جاكوزي","view":"إطلالة"},
   "match_kick":"مخصص","match_h2":"أي غرفة تناسبك؟","match_lead":"الاختيار الأنسب حسب رفقتك:",
   "personas":[("heart","الأزواج وشهر العسل","جاكوزي داخل الغرفة وصالة وإطلالات طبيعية لأجمل عطلة.","king-suit"),
     ("view","محبو الإطلالة","غرفة مضيئة بشرفة فرنسية وإطلالة على البحيرة/الحديقة.","superior"),
     ("users","العائلات","غرفتان متصلتان وحمامان — معاً مع الخصوصية.","aile"),
     ("bed","المجموعات / 3 ضيوف","تصميم رحب لثلاثة أشخاص مع شرفة تطل على الحديقة.","triple")],
   "amen_kick":"قياسي","amen_h2":"متوفر في كل غرفة",
   "resbar":"أفضل سعر مباشر","see_room":"عرض الغرفة"},
 "de": {"title":"Zimmer & Suiten | DİDİ Hotel Sapanca — Zwischen See und Wald",
   "desc":"Zimmer und Suiten des DİDİ Hotel Sapanca: King Suite (Jacuzzi im Zimmer), Junior Suite, Superior (französischer Balkon), Familie und Triple. Zwischen See und Wald, bester Direktpreis.",
   "kick":"Aufenthalt","h1_1":"Zimmer &","h1_2":"Suiten",
   "sub":"Fünf sorgfältig gestaltete Zimmertypen — von Paaren bis Familien, von der Jacuzzi-Suite bis zum verbundenen Familienzimmer. Alle zwischen See und Wald, zum besten Direktpreis.",
   "s1":"5 Zimmertypen","s2":"See + Wald","s3":"Bester Direktpreis",
   "filters":{"all":"Alle","couple":"Für 2","family":"Familie","group":"Für 3","jacuzzi":"Jacuzzi","view":"Aussicht"},
   "match_kick":"Individuell","match_h2":"Welches Zimmer passt zu Ihnen?","match_lead":"Die richtige Wahl je nach Begleitung:",
   "personas":[("heart","Paare & Flitterwochen","Jacuzzi im Zimmer, Wohnbereich und Naturblick für die schönste Auszeit.","king-suit"),
     ("view","Aussichtsliebhaber","Ein helles Zimmer mit französischem Balkon und See-/Gartenblick.","superior"),
     ("users","Familien","Zwei verbundene Zimmer, zwei Bäder — zusammen und doch privat.","aile"),
     ("bed","Gruppen / 3 Gäste","Großzügige Aufteilung für drei mit Gartenbalkon.","triple")],
   "amen_kick":"Standard","amen_h2":"In jedem Zimmer inklusive",
   "resbar":"Bester Direktpreis","see_room":"Zimmer ansehen"},
}

def langsw(cur):
    opts = "".join('<a href="%s" class="%s" hreflang="%s">%s %s</a>' % (hub_url(l), "on" if l == cur else "", l, FLAG[l], LANGNAME[l]) for l in LANGS)
    return f'<div class="langsw"><button class="langsw-btn" id="langBtn" aria-haspopup="true" aria-expanded="false">{FLAG[cur]} <span>{LANGNAME[cur]}</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg></button><div class="langsw-menu" id="langMenu">{opts}</div></div>'

def mob_langs(cur):
    return '<div class="mob-langs">' + "".join('<a href="%s" class="%s">%s %s</a>' % (hub_url(l), "on" if l == cur else "", FLAG[l], LANGNAME[l]) for l in LANGS) + '</div>'

def nav_html(lang):
    d = UI[lang]; wa = "Merhaba%2C%20rezervasyon%20yapmak%20istiyorum."
    return f'''<nav class="nav" id="nav">
<a href="{home_url(lang)}" class="nav-logo" aria-label="DİDİ Otel Sapanca"><img class="logo-w" src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><img class="logo-n" src="/assets/brand/adidilogo-navy.png" alt="" aria-hidden="true"></a>
<div class="nav-links">
<a href="{hub_url(lang)}" aria-current="page">{d["nav_odalar"]}</a><a href="{home_url(lang)}#deneyim">{d["nav_deneyim"]}</a><a href="{home_url(lang)}#mare">Mare Gastro</a><a href="{home_url(lang)}#konum">{d["nav_konum"]}</a><a href="{home_url(lang)}#iletisim">{d["nav_iletisim"]}</a>
</div>
<div class="nav-right">{langsw(lang)}
<a href="tel:+905331350888" class="btn btn-line" dir="ltr">0533 135 08 88</a>
<a href="https://wa.me/{WA}?text={wa}" class="btn btn-fill">{d["nav_rezervasyon"]}</a>
<button class="burger" id="burger" aria-label="{d["nav_menu_aria"]}"><span></span><span></span><span></span></button>
</div>
</nav>
<div class="mob" id="mob">{mob_langs(lang)}
<a href="{hub_url(lang)}">{d["nav_odalar"]}</a><a href="{home_url(lang)}#deneyim">{d["nav_deneyim"]}</a><a href="{home_url(lang)}#mare">Mare Gastro</a><a href="{home_url(lang)}#konum">{d["nav_konum"]}</a><a href="{home_url(lang)}#iletisim">{d["nav_iletisim"]}</a>
<a href="https://wa.me/{WA}?text={wa}" style="color:var(--green)">{d["mob_rez_yap"]}</a>
</div>'''

def foot_html(lang):
    d = UI[lang]
    return f'''<footer class="foot"><div class="wrap">
<div class="foot-grid">
<div><img src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><p>{d["foot_desc"]}</p></div>
<div><h5>{d["foot_sayfalar"]}</h5><ul><li><a href="{hub_url(lang)}">{d["nav_odalar"]}</a></li><li><a href="{home_url(lang)}#deneyim">{d["nav_deneyim"]}</a></li><li><a href="{home_url(lang)}#mare">Mare Gastro</a></li><li><a href="{home_url(lang)}#konum">{d["nav_konum"]}</a></li><li><a href="{home_url(lang)}#galeri">{d["gal_kick"]}</a></li></ul></div>
<div><h5>{d["nav_iletisim"]}</h5><ul><li><a href="tel:+902645921212" dir="ltr">0264 592 12 12</a></li><li><a href="https://wa.me/{WA}">WhatsApp</a></li><li><a href="mailto:info@sapancadidiotel.com">info@sapancadidiotel.com</a></li></ul></div>
</div>
<div class="foot-credits"><span>{d["foot_credit1"]}</span><span>{d["foot_credit2"]}</span></div>
<div class="foot-bot"><span>{d["foot_rights"]}</span><span>Kırkpınar · Sapanca · Sakarya</span></div>
</div></footer>'''

HUB_CSS = open(f"{ROOT}/css/_odalar_hub.css").read() if os.path.exists(f"{ROOT}/css/_odalar_hub.css") else ""

def hreflang_block(lang):
    lines = ['<link rel="alternate" hreflang="%s" href="%s">' % (l, hub_url(l)) for l in LANGS]
    lines.append('<link rel="alternate" hreflang="x-default" href="%s">' % hub_url("tr"))
    return "\n".join(lines)

def build(lang):
    d = UI[lang]; h = HUB[lang]
    wa = "Merhaba%2C%20rezervasyon%20yapmak%20istiyorum."
    hero_img = picture("king-suit", imgs_for("king-suit")[0], "100vw", alt=h["h1_1"] + " " + h["h1_2"], lazy=False)

    # oda kartları
    cards = ""
    for m in ROOMS_META:
        slug, folder = m["slug"], m["folder"]
        r = ROOMS_I18N[lang][slug]; r_tr = ROOMS_I18N["tr"][slug]
        nums = imgs_for(folder)
        img = picture(folder, nums[0], "(max-width:640px) 100vw,(max-width:1024px) 50vw,33vw", alt=r["name"])
        feats = "".join(f'<span class="hcf">{feat_icon(tr_e)}{loc_e}</span>' for tr_e, loc_e in list(zip(r_tr["extra"], r["extra"]))[:3])
        tags = " ".join(ROOM_TAGS[slug])
        cards += f'''<article class="hcard rev" data-tags="{tags}">
<a href="{room_url(lang, slug)}" class="hcard-img" aria-label="{html.escape(r["name"])}">{img}<span class="hcard-badge">{_svg("star")}{r["tag"]}</span></a>
<div class="hcard-b">
<h3>{r["name"]}</h3>
<div class="hcard-meta"><span>{_svg("users")}{r["capt"]}</span><span>{_svg("bed")}{r["bed"]}</span></div>
<div class="hcard-feats">{feats}</div>
<div class="hcard-cta"><a href="{room_url(lang, slug)}" class="btn btn-line">{d["btn_incele"]}</a><a href="https://wa.me/{WA}?text={wa}" class="btn btn-fill">{d["btn_bu_odayi_sec"]}</a></div>
</div></article>'''

    # filtre çipleri
    fk = ["all", "couple", "family", "group", "jacuzzi", "view"]
    chips = "".join(f'<button class="fchip{" on" if k=="all" else ""}" data-f="{k}">{h["filters"][k]}</button>' for k in fk)

    # kişiye özel rehber
    personas = ""
    for ic, t, dd, slug in h["personas"]:
        rn = ROOMS_I18N[lang][slug]["name"]
        personas += f'''<a href="{room_url(lang, slug)}" class="mcard rev">
<div class="mcard-ic">{_svg(ic)}</div><div class="mcard-t">{t}</div><div class="mcard-d">{dd}</div>
<div class="mcard-go">{rn} {_svg("check")}</div></a>'''

    # her odada dahil (amenities)
    amen = "".join(f'<div class="ham-it">{feat_icon(UI["tr"][k])}<span>{d[k]}</span></div>' for k in BASE_AM_KEYS)

    # trust çipleri
    tchips = "".join(f'<span class="tchip">{_svg("check")}{d[k]}</span>' for k in ["chip_temizlik","chip_personel","chip_konum","chip_kahvalti"])

    # SSS
    faqs = [(d["faq_q1"], d["faq_a1"]), (d["faq_q2"], d["faq_a2"]), (d["faq_q3"], d["faq_a3"])]
    faq_html = "".join(f'<details class="faq-item"><summary>{q}{_svg("check")}</summary><p>{a}</p></details>' for q, a in faqs)

    # schema
    itemlist = {"@context":"https://schema.org","@type":"ItemList","name":h["h1_1"]+" "+h["h1_2"],
      "itemListElement":[{"@type":"ListItem","position":i+1,"url":room_url(lang, m["slug"]),
        "name":ROOMS_I18N[lang][m["slug"]]["name"]} for i, m in enumerate(ROOMS_META)]}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":d["room_breadcrumb_anasayfa"],"item":home_url(lang)},
      {"@type":"ListItem","position":2,"name":d["nav_odalar"],"item":hub_url(lang)}]}
    faqld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
      {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q, a in faqs]}

    lang_attr = f'lang="{lang}" dir="rtl"' if lang in RTL else f'lang="{lang}"'
    page = f'''<!DOCTYPE html>
<html {lang_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
{GA}
<title>{html.escape(h["title"])}</title>
<meta name="description" content="{html.escape(h["desc"])}">
<meta name="theme-color" content="#F5F1EA">
<link rel="canonical" href="{hub_url(lang)}">
{hreflang_block(lang)}
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(h["title"])}">
<meta property="og:description" content="{html.escape(h["desc"])}">
<meta property="og:url" content="{hub_url(lang)}">
<meta property="og:image" content="{SITE}/assets/web/rooms/king-suit/{imgs_for("king-suit")[0]}-1280.webp">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/assets/brand/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(itemlist, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(crumb, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faqld, ensure_ascii=False)}</script>
<link rel="stylesheet" href="/css/site.css?v=11">
<style>{HUB_CSS}</style>
</head>
<body>
{nav_html(lang)}

<header class="hhero">
<div class="hhero-bg">{hero_img}</div>
<div class="hhero-c">
<div class="crumb"><a href="{home_url(lang)}">{d["room_breadcrumb_anasayfa"]}</a> · {d["nav_odalar"]}</div>
<div class="hkick">{h["kick"]}</div>
<h1 class="hh1"><span>{h["h1_1"]}</span><span>{h["h1_2"]}</span></h1>
<p class="hsub">{h["sub"]}</p>
<div class="hstats"><span>{_svg("bed")}{h["s1"]}</span><span>{_svg("view")}{h["s2"]}</span><span>{_svg("star")}{h["s3"]}</span></div>
</div>
<div class="hscroll" aria-hidden="true"><span class="d"></span></div>
</header>

<section class="sec hub-rooms"><div class="wrap">
<div class="fbar rev" role="tablist" aria-label="{d["nav_odalar"]}">{chips}</div>
<div class="hgrid" id="hgrid">{cards}</div>
<p class="hempty" id="hempty" hidden>—</p>
</div></section>

<section class="sec match-sec"><div class="wrap">
<div class="rev" style="text-align:center;max-width:640px;margin:0 auto 40px">
<div class="kick" style="justify-content:center">{h["match_kick"]}</div>
<h2 class="dh">{h["match_h2"]}</h2>
<p class="lead" style="margin-top:12px">{h["match_lead"]}</p></div>
<div class="mgrid">{personas}</div>
</div></section>

<section class="sec amen-sec"><div class="wrap">
<div class="rev" style="text-align:center;margin-bottom:34px"><div class="kick" style="justify-content:center">{h["amen_kick"]}</div><h2 class="dh">{h["amen_h2"]}</h2></div>
<div class="hamen rev">{amen}</div>
</div></section>

<section class="sec trust-sec"><div class="wrap rev">
<div class="tcard">
<div class="tstars">{_svg("star")}{_svg("star")}{_svg("star")}{_svg("star")}{_svg("star")}</div>
<div class="kick" style="justify-content:center">{d["trust_kick"]}</div>
<h2 class="dh" style="max-width:20ch;margin:8px auto 0">{d["trust_h2"]}</h2>
<p class="lead" style="max-width:52ch;margin:14px auto 20px">{d["trust_lead"]}</p>
<div class="tchips">{tchips}</div>
<a href="https://www.google.com/search?q=DİDİ+Otel+Sapanca" target="_blank" rel="noopener" class="btn btn-line" style="margin-top:22px;border-color:var(--line);color:var(--ink)">{d["trust_google_cta"]}</a>
</div>
</div></section>

<section class="sec faq-sec"><div class="wrap">
<div class="rev" style="max-width:760px;margin:0 auto">
<div class="kick">SSS</div><h2 class="dh" style="margin-bottom:26px">{d["faq_q1"][:0] or ""}{"Sıkça sorulanlar" if lang=="tr" else ("FAQ" if lang in ("en","de") else ("Часто задаваемые" if lang=="ru" else "الأسئلة الشائعة"))}</h2>
<div class="faq-list">{faq_html}</div></div>
</div></section>

<section class="sec cta-sec"><div class="wrap rev" style="text-align:center">
<div class="kick" style="justify-content:center">{d["cta_kick"]}</div>
<h2 class="dh" style="color:#fff;max-width:20ch;margin:0 auto 16px">{d["cta_h2"]}</h2>
<p class="lead" style="color:rgba(255,255,255,.85);max-width:48ch;margin:0 auto 30px">{d["cta_lead"]}</p>
<div class="cta-btns"><a href="https://wa.me/{WA}?text={wa}" class="btn btn-fill">{d["btn_wa_yazin"]}</a>
<a href="tel:+905331350888" class="btn btn-line" dir="ltr">0533 135 08 88</a></div>
</div></section>

{foot_html(lang)}

<div class="resbar"><div class="resbar-in"><div class="resbar-t"><b>{h["resbar"]}</b><span>{d["nav_odalar"]} · DİDİ Otel</span></div>
<a href="https://wa.me/{WA}?text={wa}" class="btn btn-fill">{d["nav_rezervasyon"]}</a></div></div>

<a class="wa" href="https://wa.me/{WA}?text=Merhaba%2C%20bilgi%20almak%20istiyorum." target="_blank" rel="noopener" aria-label="WhatsApp"><svg viewBox="0 0 24 24"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.7.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.5-.7-2.5-1.3-3.5-3-.3-.5.3-.4.8-1.4.1-.2 0-.4 0-.5 0-.1-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5 1.9.8 2.6.9 3.5.7.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3zM12 2a10 10 0 0 0-8.6 15l-1.4 5 5.2-1.4A10 10 0 1 0 12 2z"/></svg></a>

<script>
(function(){{
var nav=document.getElementById('nav');addEventListener('scroll',function(){{nav.classList.toggle('scr',scrollY>40);}},{{passive:true}});
var burger=document.getElementById('burger'),mob=document.getElementById('mob');
burger.addEventListener('click',function(){{burger.classList.toggle('x');mob.classList.toggle('open');document.body.style.overflow=mob.classList.contains('open')?'hidden':'';}});
mob.querySelectorAll('a').forEach(function(a){{a.addEventListener('click',function(){{burger.classList.remove('x');mob.classList.remove('open');document.body.style.overflow='';}});}});
var lb=document.getElementById('langBtn');
if(lb){{var ls=lb.closest('.langsw');lb.addEventListener('click',function(e){{e.stopPropagation();ls.classList.toggle('open');lb.setAttribute('aria-expanded',ls.classList.contains('open'));}});document.addEventListener('click',function(){{ls.classList.remove('open');}});}}
var io=new IntersectionObserver(function(es,o){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('in');o.unobserve(e.target);}}}});}},{{threshold:.12,rootMargin:'0px 0px -6% 0px'}});
document.querySelectorAll('.rev').forEach(function(el){{io.observe(el);}});
// filtre
var chips=document.querySelectorAll('.fchip'),cards=document.querySelectorAll('.hcard'),empty=document.getElementById('hempty');
chips.forEach(function(c){{c.addEventListener('click',function(){{
  chips.forEach(function(x){{x.classList.remove('on');}});c.classList.add('on');
  var f=c.getAttribute('data-f'),shown=0;
  cards.forEach(function(card){{var ok=f==='all'||(' '+card.getAttribute('data-tags')+' ').indexOf(' '+f+' ')>=0;
    card.style.display=ok?'':'none';if(ok)shown++;}});
  empty.hidden=shown>0;
}});}});
}})();
</script>
</body>
</html>'''
    outdir = f"{ROOT}/odalar" if lang == "tr" else f"{ROOT}/{lang}/odalar"
    os.makedirs(outdir, exist_ok=True)
    open(f"{outdir}/index.html", "w", encoding="utf-8").write(page)
    return len(page)

if __name__ == "__main__":
    for l in LANGS:
        n = build(l)
        print(f"✓ {'/' if l=='tr' else '/'+l+'/'}odalar/  ({n} bytes)")
    print("Tamam.")
