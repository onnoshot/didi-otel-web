#!/usr/bin/env python3
"""DİDİ Otel — oda detay sayfası üretici.
Her oda için /odalar/<slug>/index.html üretir (paylaşılan css/site.css).
Galeriyi assets/web/rooms/<folder>/ içindeki görsellerden kurar. Idempotent.
"""
import os, glob, re, html
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
_strip = lambda t: re.sub(r"<[^>]+>","",t)
SITE = "https://www.sapancadidiotel.com"

ROOMS = [
 {"slug":"king-suit","folder":"king-suit","name":"King Suit Oda","id":4,"cap":2,"capt":"2 Misafir","bed":"King Yatak","tag":"En Geniş Süit",
  "desc":["King Suit, otelimizin en geniş ve en ayrıcalıklı süitidir. En belirgin farkı, odanın içinde konumlanan <strong>serbest duran jakuzi/küveti</strong>; king yatağın hemen yanında keyifli bir dinlenme deneyimi sunar. Ferah bir oturma salonu, kavisli koltuk ve balkona açılan doğa manzarasıyla adeta bir daire konforunda.",
          "Oda içi jakuzi, geniş oturma alanı ve yağmurlamalı ayrı duşuyla King Suit; balayı, yıldönümü ve kendinize özel zaman ayırmak istediğiniz anlar için idealdir. Diğer odalardan farkı: en geniş metrekare, oda içi küvet ve salon düzeni."],
  "extra":["Oda İçi Jakuzi / Küvet","Geniş Oturma Salonu","Balkon ve Doğa Manzarası","Yağmurlamalı Ayrı Duş"]},
 {"slug":"junior-suit","folder":"junior-suit","name":"Junior Suit Oda","id":5,"cap":2,"capt":"2 Misafir","bed":"King Yatak","tag":"Süit",
  "desc":["Junior Suit, king yatağı ve şık bir <strong>oturma köşesiyle</strong> konfor ile zarafeti bir araya getirir. İki koltuk ve küçük bir masadan oluşan dinlenme köşesi, kahvenizi manzara eşliğinde yudumlamak için ideal bir alan yaratır.",
          "Balkonu ve sıcak tonlu tasarımıyla Junior Suit, King Suit'e göre daha kompakt ama süit konforunu koruyan bir seçenektir. Banyosunda yağmurlamalı duş bulunur (King Suit'teki oda içi jakuzi bu odada yer almaz)."],
  "extra":["Şık Oturma Köşesi","Balkon","Yağmurlamalı Duş"]},
 {"slug":"superior","folder":"superior","name":"Superior Oda","id":6,"cap":2,"capt":"2 Misafir","bed":"Çift Kişilik Yatak","tag":"Manzaralı Oda",
  "desc":["Superior oda, konforlu ve aydınlık atmosferiyle dinlendirici bir konaklama sunar. En öne çıkan özelliği <strong>Fransız balkonu ve göl/bahçe manzarası</strong>; sabah perdeleri araladığınızda doğanın içinde uyanırsınız.",
          "Süit düzeni olmadan konforlu bir konaklama arayanlar için idealdir. Banyosunda modern yağmurlamalı duş bulunur. King ve Junior Suit'ten farkı: oturma salonu/köşesi yerine sade ve şık bir oda düzeni sunar."],
  "extra":["Fransız Balkon","Göl / Bahçe Manzarası","Yağmurlamalı Duş"]},
 {"slug":"aile","folder":"family","name":"Aile Odası","id":7,"cap":4,"capt":"4 Misafir","bed":"Bağlantılı 2 Oda","tag":"Aile",
  "desc":["Aile Odası, <strong>birbirine bağlanan iki ayrı odadan</strong> oluşur ve dört misafir için tasarlanmıştır. Bağlantılı yapısı sayesinde hem bir aradalığı hem de mahremiyeti aynı anda yaşarsınız; ebeveynler ve çocuklar için ayrı alanlar sunar.",
          "İki banyosu, orman manzaralı balkonu ve ferah düzeniyle çocuklu aileler ve birlikte seyahat eden gruplar için en uygun seçenektir. Diğer odalardan farkı: tek oda değil, bağlantılı iki oda ve iki banyo."],
  "extra":["Bağlantılı 2 Oda","2 Ayrı Banyo","Orman Manzaralı Balkon"]},
 {"slug":"triple","folder":"triple","name":"Triple Oda","id":8,"cap":3,"capt":"3 Misafir","bed":"Üç Kişilik Düzen","tag":"Oda",
  "desc":["Triple oda, üç misafir için tek mekânda ferah ve konforlu bir düzen sunar. <strong>Bahçe manzaralı balkonu</strong> ve oturma köşesiyle, arkadaş grupları ve üç kişilik aileler için pratik ve keyifli bir seçenektir.",
          "Aile Odası'ndan farkı: bağlantılı iki oda değil, üç yatak düzenine sahip tek geniş odadır. Konforlu, aydınlık ve doğayla iç içe."],
  "extra":["Üç Kişilik Ferah Düzen","Bahçe Manzaralı Balkon","Oturma Alanı"]},
]
GA = '''<link rel="preconnect" href="https://www.googletagmanager.com"><link rel="preconnect" href="https://connect.facebook.net" crossorigin>
<link rel="dns-prefetch" href="https://www.google-analytics.com"><link rel="dns-prefetch" href="https://www.facebook.com">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-C8D22FPDET"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-C8D22FPDET');
</script>
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '1475183377973476');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=1475183377973476&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->'''
BASE_AM = ["Klima","LCD TV + Uydu","Ücretsiz WiFi","Minibar","Su Isıtıcısı","Saç Kurutma Makinesi","Duşakabin","Banyo Malzemeleri"]
CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg>'

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

NAV = '''<nav class="nav" id="nav">
<a href="/" class="nav-logo" aria-label="DİDİ Otel Sapanca"><img class="logo-w" src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><img class="logo-n" src="/assets/brand/adidilogo-navy.png" alt="" aria-hidden="true"></a>
<div class="nav-links">
<a href="/#odalar">Odalar</a><a href="/#deneyim">Deneyim</a><a href="/#mare">Mare Gastro</a><a href="/#konum">Konum</a><a href="/#iletisim">İletişim</a>
</div>
<div class="nav-right">
<a href="tel:+905331350888" class="btn btn-line">0533 135 08 88</a>
<a href="https://wa.me/905331350888?text=Merhaba%2C%20D%C4%B0D%C4%B0%20Otel%20Sapanca%20i%C3%A7in%20rezervasyon%20yapmak%20istiyorum." class="btn btn-fill">Rezervasyon</a>
<button class="burger" id="burger" aria-label="Menü"><span></span><span></span><span></span></button>
</div>
</nav>
<div class="mob" id="mob">
<a href="/#odalar">Odalar</a><a href="/#deneyim">Deneyim</a><a href="/#mare">Mare Gastro</a><a href="/#konum">Konum</a><a href="/#iletisim">İletişim</a>
<a href="https://wa.me/905331350888?text=Merhaba%2C%20D%C4%B0D%C4%B0%20Otel%20Sapanca%20i%C3%A7in%20rezervasyon%20yapmak%20istiyorum." style="color:var(--green)">Rezervasyon Yap →</a>
</div>'''

FOOT = '''<footer class="foot"><div class="wrap">
<div class="foot-grid">
<div><img src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><p>Kırkpınar Sapanca'da göl ve orman arasında butik bir konaklama. Sapanca'nın tek klorsuz havuzu ve Mare Gastro restoranıyla.</p></div>
<div><h5>Sayfalar</h5><ul><li><a href="/#odalar">Odalar</a></li><li><a href="/#deneyim">Deneyim</a></li><li><a href="/#mare">Mare Gastro</a></li><li><a href="/#konum">Konum</a></li><li><a href="/#galeri">Galeri</a></li></ul></div>
<div><h5>İletişim</h5><ul><li><a href="tel:+902645921212">0264 592 12 12</a></li><li><a href="https://wa.me/905331350888">WhatsApp</a></li><li><a href="mailto:info@sapancadidiotel.com">info@sapancadidiotel.com</a></li><li><a href="https://www.google.com/maps/dir/?api=1&destination=K%C4%B1rkp%C4%B1nar+Sapanca%2C+Sakarya" target="_blank" rel="noopener">Yol Tarifi</a></li></ul></div>
</div>
<div class="foot-credits"><span>Bu web sitesi <a href="https://uniqbee.com" target="_blank" rel="noopener">Uniqbee</a> tarafından hazırlanmıştır.</span><span>DİDİ Otel, <a href="https://otelyonet.com.tr/" target="_blank" rel="noopener">Otelyonet</a> sistemleri ile yönetilmektedir.</span></div>
<div class="foot-bot"><span>© 2026 DİDİ Otel Sapanca. Tüm hakları saklıdır.</span><span>Kırkpınar · Sapanca · Sakarya</span></div>
</div></footer>
<a class="wa" href="https://wa.me/905331350888?text=Merhaba%2C%20bilgi%20almak%20istiyorum." target="_blank" rel="noopener" aria-label="WhatsApp"><svg viewBox="0 0 24 24"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.7.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.5-.7-2.5-1.3-3.5-3-.3-.5.3-.4.8-1.4.1-.2 0-.4 0-.5 0-.1-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5 1.9.8 2.6.9 3.5.7.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3zM12 2a10 10 0 0 0-8.6 15l-1.4 5 5.2-1.4A10 10 0 1 0 12 2z"/></svg></a>
<div class="lb" id="lb"><button class="x" id="lbX" aria-label="Kapat">×</button><button class="pv" id="lbPrev" aria-label="Önceki">‹</button><img id="lbImg" src="" alt=""><button class="nx" id="lbNext" aria-label="Sonraki">›</button></div>'''

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

def build(r):
    nums = imgs_for(r["folder"])
    hero = picture(r["folder"], nums[0], "100vw", alt=r["name"], lazy=False, w=1280, h=960)
    am = BASE_AM + r.get("extra",[])
    amli = "".join(f'<li>{CHECK_SVG}{a}</li>' for a in am)
    gal = "".join(f'<a data-lb="/assets/web/rooms/{r["folder"]}/{n}.jpg">'
                  + picture(r["folder"], n, "(max-width:560px) 100vw,(max-width:960px) 50vw,33vw", alt=f'{r["name"]} - {i+1}')
                  + '</a>' for i,n in enumerate(nums))
    desc = "".join(f'<p class="lead">{d}</p>' for d in r["desc"])
    others = [x for x in ROOMS if x["slug"]!=r["slug"]]
    ocards = "".join(f'<a href="/odalar/{o["slug"]}/" class="ocard">'
                     + picture(o["folder"], imgs_for(o["folder"])[0], "25vw", alt=o["name"])
                     + f'<span>{o["name"]}</span></a>' for o in others)
    ld = {
      "@context":"https://schema.org","@type":"HotelRoom","name":r["name"],
      "url":f'{SITE}/odalar/{r["slug"]}/',
      "description":_strip(r["desc"][0]),
      "occupancy":{"@type":"QuantitativeValue","minValue":1,"maxValue":r["cap"]},
      "bed":{"@type":"BedDetails","typeOfBed":r["bed"]},
      "amenityFeature":[{"@type":"LocationFeatureSpecification","name":a,"value":True} for a in am],
      "containedInPlace":{"@id":f"{SITE}/#hotel"},
      "image":f'{SITE}/assets/web/rooms/{r["folder"]}/{nums[0]}-1280.webp'}
    import json
    crumb_ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Anasayfa","item":f"{SITE}/"},
        {"@type":"ListItem","position":2,"name":"Odalar","item":f"{SITE}/#odalar"},
        {"@type":"ListItem","position":3,"name":r["name"]}]}
    title = f'{r["name"]} | DİDİ Otel Sapanca'
    desc_meta = f'{r["name"]} — DİDİ Otel Sapanca. {_strip(r["desc"][0])[:120]}'
    page = f'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
{GA}
<title>{title}</title>
<meta name="description" content="{html.escape(desc_meta)}">
<meta name="theme-color" content="#F5F1EA">
<link rel="canonical" href="{SITE}/odalar/{r["slug"]}/">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc_meta)}">
<meta property="og:url" content="{SITE}/odalar/{r["slug"]}/">
<meta property="og:image" content="{SITE}/assets/web/rooms/{r["folder"]}/{nums[0]}-1280.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/assets/brand/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(crumb_ld,ensure_ascii=False)}</script>
<link rel="stylesheet" href="/css/site.css?v=9">
</head>
<body>
<div class="prog" id="prog" style="display:none"></div>
{NAV}
<header class="rhero">
{hero}
<div class="rhero-c">
<div class="crumb"><a href="/">Anasayfa</a> · <a href="/#odalar">Odalar</a> · {r["name"]}</div>
<h1 class="thin">{r["name"]}</h1>
<div class="rmeta-row"><span>{r["capt"]}</span><span>{r["bed"]}</span><span>{r["tag"]}</span></div>
</div>
</header>

<section class="sec"><div class="wrap rdetail">
<div class="rdesc rev">
<div class="kick">Oda Detayı</div>
{desc}
</div>
<aside class="rside rev">
<h3>Oda Donanımı</h3>
<ul class="amlist">{amli}</ul>
<a href="https://wa.me/905331350888?text={quote('Merhaba, DİDİ Otel Sapanca '+r["name"]+' için rezervasyon yapmak istiyorum.')}" class="btn btn-fill">Bu Odayı Seç</a>
<div class="note">Güncel fiyat ve müsaitlik için</div>
</aside>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
<div class="rev" style="margin-bottom:40px"><div class="kick">Galeri</div><h2 class="dh">{r["name"]} <b>Görselleri</b></h2></div>
<div class="rgal">{gal}</div>
</div></section>

<section class="sec exp"><div class="wrap">
<div class="rev" style="margin-bottom:8px"><div class="kick">Diğer Odalar</div><h2 class="dh">Diğer konaklama <b>seçenekleri</b></h2></div>
<div class="others rev">{ocards}</div>
</div></section>

{FOOT}
{JS}
</body>
</html>'''
    outdir = f'{ROOT}/odalar/{r["slug"]}'
    os.makedirs(outdir, exist_ok=True)
    open(f'{outdir}/index.html','w',encoding='utf-8').write(page)
    return len(nums)

if __name__=="__main__":
    for r in ROOMS:
        n=build(r)
        print(f'✓ /odalar/{r["slug"]}/  ({n} foto)')
    print("Tamam.")
