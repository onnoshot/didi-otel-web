#!/usr/bin/env python3
"""DİDİ Otel — blog üretici.
/blog/ index + /blog/<slug>/index.html üretir. Article + BreadcrumbList + FAQPage schema,
GEO/AEO uyumlu (answer-first, soru H2, tablo, iç linkler). Idempotent.
"""
import os, json, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.sapancadidiotel.com"
IMG = "/assets/web/editorial"

GA = '''<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-N68CWMCH');</script>
<!-- End Google Tag Manager -->'''

TRACK = '''<!-- DataLayer events -->
<script>(function(){var dl=window.dataLayer=window.dataLayer||[];function region(el){if(el.closest('#mob')||el.closest('.mob'))return'hamburger';if(el.closest('#nav')||el.closest('nav'))return'header';if(el.closest('footer'))return'footer';if(el.closest('.resv-modal'))return'reservation_form';if(el.closest('.resbar'))return'sticky_bar';if(el.closest('.cta-sec')||el.closest('.cta'))return'cta';if(el.closest('.hhero')||el.closest('.hero')||el.closest('.rhero'))return'hero';if(el.closest('#iletisim')||el.closest('.contact'))return'contact';if(el.closest('#mare'))return'mare';if(el.closest('.hcard')||el.closest('.rdetail')||el.closest('.rside'))return'room';if(el.closest('.wa'))return'float';return'page';}function menuName(href,txt){href=(href||'').toLowerCase();var m=[['iletisim','iletisim'],['konum','konum'],['blog','blog'],['deneyim','deneyim'],['galeri','galeri'],['mare','mare'],['odalar','odalar']];for(var i=0;i<m.length;i++)if(href.indexOf(m[i][0])>=0)return m[i][1];return(txt||'').trim().toLowerCase().slice(0,40);}document.addEventListener('click',function(e){var a=e.target.closest('a,button');if(!a)return;var href=a.getAttribute('href')||'',hl=href.toLowerCase(),onc=a.getAttribute('onclick')||'';if(onc.indexOf('resvOpen')>=0){dl.push({event:'availability_check',event_label:region(a)});return;}if(hl.indexOf('wa.me')>=0||hl.indexOf('whatsapp')>=0||(a.classList&&a.classList.contains('btn-wa'))||/whatsapp/i.test(a.textContent||'')){dl.push({event:'whatsapp_click',event_label:region(a)});return;}if(hl.indexOf('tel:')===0){dl.push({event:'phone_click',event_label:region(a)});return;}if(a.tagName==='A'&&(a.closest('.nav-links')||a.closest('#mob')||a.closest('footer'))){dl.push({event:'menu_click',event_label:region(a),element:menuName(href,a.textContent)});return;}},true);})();</script>'''

NAV = '''<nav class="nav scr-force" id="nav">
<a href="/" class="nav-logo" aria-label="DİDİ Otel Sapanca"><img class="logo-w" src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><img class="logo-n" src="/assets/brand/adidilogo-navy.png" alt="" aria-hidden="true"></a>
<div class="nav-links">
<a href="/#odalar">Odalar</a><a href="/#mare">Mare Gastro</a><a href="/#konum">Konum</a><a href="/blog/">Blog</a><a href="/#iletisim">İletişim</a>
</div>
<div class="nav-right">
<a href="tel:+905331350888" class="btn btn-line">0533 135 08 88</a>
<a href="https://wa.me/905331350888?text=Merhaba%2C%20D%C4%B0D%C4%B0%20Otel%20Sapanca%20i%C3%A7in%20rezervasyon%20yapmak%20istiyorum." class="btn btn-fill">Rezervasyon</a>
<button class="burger" id="burger" aria-label="Menü"><span></span><span></span><span></span></button>
</div>
</nav>
<div class="mob" id="mob">
<a href="/#odalar">Odalar</a><a href="/#mare">Mare Gastro</a><a href="/#konum">Konum</a><a href="/blog/">Blog</a><a href="/#iletisim">İletişim</a>
<a href="https://wa.me/905331350888?text=Merhaba%2C%20D%C4%B0D%C4%B0%20Otel%20Sapanca%20i%C3%A7in%20rezervasyon%20yapmak%20istiyorum." style="color:var(--green)">Rezervasyon Yap →</a>
</div>'''

FOOT = '''<footer class="foot"><div class="wrap">
<div class="foot-grid">
<div><img src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><p>Kırkpınar Sapanca'da göl ve orman arasında butik bir konaklama. Sapanca'nın tek klorsuz havuzu ve Mare Gastro restoranıyla.</p></div>
<div><h5>Sayfalar</h5><ul><li><a href="/#odalar">Odalar</a></li><li><a href="/#mare">Mare Gastro</a></li><li><a href="/#konum">Konum</a></li><li><a href="/blog/">Blog</a></li><li><a href="/#galeri">Galeri</a></li></ul></div>
<div><h5>İletişim</h5><ul><li><a href="tel:+902645921212">0264 592 12 12</a></li><li><a href="https://wa.me/905331350888">WhatsApp</a></li><li><a href="mailto:info@sapancadidiotel.com">info@sapancadidiotel.com</a></li><li><a href="https://www.google.com/maps/dir/?api=1&destination=40.7002438%2C30.222254" target="_blank" rel="noopener">Yol Tarifi</a></li></ul></div>
</div>
<div class="foot-credits"><a class="foot-madeby" href="https://uniqbee.com" target="_blank" rel="noopener"><img class="mb-ico" src="/assets/brand/uniqbee.svg" alt="UniqBee" width="22" height="22"><span class="mb-name">UniqBee Dijital Medya Ajansı</span></a><span class="foot-managed">DİDİ Otel, <a href="https://otelyonet.com.tr/" target="_blank" rel="noopener">Otelyonet</a> sistemleri ile yönetilmektedir.</span></div>
<div class="foot-bot"><span>© 2026 DİDİ Otel Sapanca. Tüm hakları saklıdır.</span><span>Kırkpınar · Sapanca · Sakarya</span></div>
</div></footer>
<a class="wa" href="https://wa.me/905331350888?text=Merhaba%2C%20bilgi%20almak%20istiyorum." target="_blank" rel="noopener" aria-label="WhatsApp"><svg viewBox="0 0 24 24"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.7.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.5-.7-2.5-1.3-3.5-3-.3-.5.3-.4.8-1.4.1-.2 0-.4 0-.5 0-.1-.7-1.6-.9-2.2-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5 1.9.8 2.6.9 3.5.7.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3zM12 2a10 10 0 0 0-8.6 15l-1.4 5 5.2-1.4A10 10 0 1 0 12 2z"/></svg></a>'''

JS = '''<script>
const nav=document.getElementById('nav');addEventListener('scroll',()=>nav.classList.toggle('scr',scrollY>40),{passive:true});
const burger=document.getElementById('burger'),mob=document.getElementById('mob');
if(burger){burger.addEventListener('click',()=>{burger.classList.toggle('x');mob.classList.toggle('open');document.body.style.overflow=mob.classList.contains('open')?'hidden':''});
mob.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{burger.classList.remove('x');mob.classList.remove('open');document.body.style.overflow=''}));}
const io=new IntersectionObserver((es,o)=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');o.unobserve(e.target)}}),{threshold:.12,rootMargin:'0px 0px -7% 0px'});
document.querySelectorAll('.rev').forEach(el=>io.observe(el));
document.querySelectorAll('.itin-tabs').forEach(tabs=>{
const wrap=tabs.closest('.itin-wrap');if(!wrap)return;
tabs.querySelectorAll('button').forEach(btn=>btn.addEventListener('click',()=>{
tabs.querySelectorAll('button').forEach(b=>b.classList.remove('on'));btn.classList.add('on');
const k=btn.dataset.tab;wrap.querySelectorAll('.itin-panel').forEach(p=>p.classList.toggle('on',p.dataset.tab===k));
}));
});
const cio=new IntersectionObserver((es,o)=>es.forEach(e=>{
if(!e.isIntersecting)return;
const el=e.target,raw=el.dataset.count,end=parseFloat(raw.replace(',','.')),dec=(raw.split(/[.,]/)[1]||'').length,dur=1100,t0=performance.now();
const step=t=>{const p=Math.min(1,(t-t0)/dur),v=end*(1-Math.pow(1-p,3));el.textContent=v.toFixed(dec).replace('.',',');if(p<1)requestAnimationFrame(step);else el.textContent=raw;};
requestAnimationFrame(step);o.unobserve(el);
}),{threshold:.5});
document.querySelectorAll('.stat-num[data-count]').forEach(el=>cio.observe(el));
document.querySelectorAll('.spot-check').forEach(list=>{
const key='didi-check-'+(list.dataset.key||'x'),boxes=[...list.querySelectorAll('input[type=checkbox]')];
let saved=[];try{saved=JSON.parse(localStorage.getItem(key)||'[]')}catch(e){}
boxes.forEach((b,i)=>{if(saved.includes(i))b.checked=true});
const holder=list.parentElement.querySelector('.spot-progress'),bar=holder&&holder.querySelector('b'),track=holder&&holder.querySelector('.track i');
const upd=()=>{const n=boxes.filter(b=>b.checked).length;if(bar)bar.textContent=n+'/'+boxes.length;if(track)track.style.width=(n/boxes.length*100)+'%';
try{localStorage.setItem(key,JSON.stringify(boxes.map((b,i)=>b.checked?i:null).filter(x=>x!==null)))}catch(e){}};
boxes.forEach(b=>b.addEventListener('change',upd));upd();
});
</script>'''

CTA = ('<div class="art-cta"><h3>Sapanca\'da doğanın içinde bir kaçış</h3>'
 '<p>DİDİ Otel Sapanca — Kırkpınar\'da göl ile orman arasında butik bir konaklama.</p>'
 '<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">'
 '<a href="https://wa.me/905331350888?text=Merhaba%2C%20D%C4%B0D%C4%B0%20Otel%20Sapanca%20i%C3%A7in%20rezervasyon%20yapmak%20istiyorum." class="btn btn-fill">Müsaitliği Gör</a>'
 '<a href="/#odalar" class="btn btn-line" style="border-color:rgba(255,255,255,.4);color:#fff">Odaları İncele</a></div>'
 '<p style="margin:18px 0 0;font-size:14px">Telefonla rezervasyon: <a href="tel:+902645921212" style="color:#fff">0264 592 12 12</a> · WhatsApp: <a href="https://wa.me/905331350888" style="color:#fff">0533 135 08 88</a></p></div>')

# Blog'a özel küçük stil eklemeleri (site.css'e dokunmadan): tablo sarmalayıcı, figür,
# kaynak listesi, YouTube facade, özet kutusu; kategori etiketlerinde büyük harf yok.
BLOG_CSS = '''<style>
.bcard .cat,.art-hero-c .cat,.kick{text-transform:none;letter-spacing:.04em}
.art-body .tbl{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:8px 0 24px}
.art-body .tbl table{margin:0;min-width:520px}
.art-body .tbl td:last-child{white-space:normal}
.art-body .tbl td,.art-body .tbl th{vertical-align:top}
.art-body .tbl td:last-child,.art-body .tbl th:last-child{text-align:left;color:inherit}
.art-body .tldr{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:0 0 28px;font-size:16px}
.art-body .tldr b{display:block;font-size:13px;letter-spacing:.04em;color:var(--green);margin-bottom:6px}
.art-body .tldr ul{margin:0 0 0 18px}
.art-body figure{margin:26px 0}
.art-body figure img{width:100%;height:auto;border-radius:12px;display:block}
.art-body figcaption{font-size:13.5px;color:var(--ink2);margin-top:8px;line-height:1.5}
.art-body .note{font-size:14px;color:var(--ink2);border-left:2px solid var(--sand);padding:4px 0 4px 14px;margin:0 0 22px}
.art-src{margin-top:30px;padding-top:22px;border-top:1px solid var(--line);font-size:14px}
.art-src h2{font-size:18px!important;margin:0 0 10px!important}
.art-src ol{margin:0 0 0 20px}.art-src li{margin-bottom:6px;overflow-wrap:anywhere}
.yt-facade{position:relative;display:block;width:100%;aspect-ratio:16/9;border:0;padding:0;border-radius:12px;overflow:hidden;background:#111;cursor:pointer}
.yt-facade img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.88}
.yt-facade .play{position:absolute;left:50%;top:50%;width:68px;height:48px;margin:-24px 0 0 -34px;background:rgba(0,0,0,.72);border-radius:12px}
.yt-facade .play::after{content:"";position:absolute;left:27px;top:14px;border-style:solid;border-width:10px 0 10px 17px;border-color:transparent transparent transparent #fff}
.yt-facade iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.art-upd{opacity:.9}
</style>'''

YT_JS = '''<script>document.querySelectorAll('.yt-facade').forEach(function(b){b.addEventListener('click',function(){var id=b.dataset.id,f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+id+'?autoplay=1&rel=0';f.title=b.dataset.title||'YouTube video';f.allow='accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture';f.allowFullscreen=true;b.innerHTML='';b.appendChild(f);},{once:true});});</script>'''

def _variants(base_fs):
    """Diskte gerçekten bulunan genişlikleri döndürür (olmayan srcset'leri yazmamak için)."""
    return [w for w in (480,800,1280,1920) if os.path.exists(f"{base_fs}-{w}.webp")]

def fig(path, alt, cap="", sizes="(max-width:900px) 100vw,760px"):
    """Gövde içi figür. path: '/assets/web/editorial/ONN09461' gibi uzantısız taban yol."""
    ws = _variants(ROOT + path)
    av = ",".join(f"{path}-{w}.avif {w}w" for w in ws if os.path.exists(f"{ROOT}{path}-{w}.avif"))
    wb = ",".join(f"{path}-{w}.webp {w}w" for w in ws)
    big = max([w for w in ws if w <= 1280] or ws)
    src = f"{path}-{big}.webp"
    cap_html = f"<figcaption>{cap}</figcaption>" if cap else ""
    return (f'<figure><picture>'
            + (f'<source type="image/avif" srcset="{av}" sizes="{sizes}">' if av else '')
            + f'<source type="image/webp" srcset="{wb}" sizes="{sizes}">'
            f'<img src="{src}" loading="lazy" decoding="async" width="1280" height="720" alt="{html.escape(alt)}"></picture>{cap_html}</figure>')

def yt(vid, title, cap=""):
    """Hafif YouTube facade: tıklanana kadar yalnızca küçük resim yüklenir (youtube-nocookie)."""
    cap_html = f"<figcaption>{cap}</figcaption>" if cap else ""
    t = html.escape(title)
    return (f'<figure><button type="button" class="yt-facade" data-id="{vid}" data-title="{t}" aria-label="Videoyu oynat: {t}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" loading="lazy" decoding="async" width="480" height="360" alt="{t} — video önizlemesi">'
            f'<span class="play" aria-hidden="true"></span></button>{cap_html}</figure>')

# ── POSTS ──
POSTS = [
{
 "slug":"didi-otel-uniqbee-web-sitesi-hikayesi","cat":"Perde Arkası","img":"lobi","date":"2026-08-26",
 "title":"Web Sitemizi Neden ve Nasıl Yeniledik? UniqBee İle Dijital Dönüşüm Hikayemiz",
 "desc":"DİDİ Otel Sapanca olarak web sitemizi UniqBee ile nasıl yeniden kurduğumuzu anlatıyoruz: 6 dilli yapı, app-hissiyatlı odalar hub'ı, şifreli admin paneli ve bu süreçte neden bu ajansla çalışmaktan bu kadar memnun olduğumuz.",
 "lead":"Kısa cevap: web sitemizi <a href=\"https://uniqbee.com\" target=\"_blank\" rel=\"noopener\">UniqBee</a> ile sıfırdan yeniden kurduk çünkü eski sitemiz artık ne uluslararası misafirlerimize doğru dilde konuşabiliyordu ne de rezervasyonu kolaylaştırıyordu. Bugün 6 dilli, app hissiyatlı bir <a href=\"/odalar/\">oda hub'ı</a> ve şifreli bir yönetim paneline sahip bir sitemiz var; bu yazıda süreci kendi ağzımızdan, adım adım anlatıyoruz.",
 "body":"""
<h2>İhtiyacımız neydi?</h2>
<p>DİDİ Otel Sapanca olarak birkaç yıldır büyüyen bir misafir kitlesine hizmet veriyoruz; hem yurt içinden hem de Orta Doğu ve Avrupa'dan gelen misafirlerimiz var. Eski web sitemiz görsel olarak fena değildi ama üç temel sorunu vardı: tek dilliydi, mobilde rezervasyon adımları kafa karıştırıcıydı ve oda tiplerini karşılaştırmak neredeyse imkansızdı. Bir misafirimiz WhatsApp'tan "kaç kişilik oda var, göl mü orman mı manzara, fiyat farkı ne" diye tek tek soruyordu — bu bilgilerin sitede net olması gerektiğini biliyorduk.</p>
<p>Kısacası ihtiyacımız şuydu: çok dilli, modern, mobilde hızlı ve rezervasyon dönüşümü yüksek bir site. Bunu kendi imkanlarımızla değil, otelcilik dışında dijital tarafın uzmanı bir ekiple yapmak istedik.</p>
<h2>UniqBee ile süreç nasıl işledi?</h2>
<p>Araştırmamız sırasında birkaç ajansla görüştük ama <a href="https://uniqbee.com" target="_blank" rel="noopener">UniqBee</a> ile ilk toplantıdan itibaren fark hemen belli oldu: bize genel geçer bir şablon satmadılar, önce otelimizi, misafir profilimizi ve Kırkpınar'daki konumumuzu anlamaya çalıştılar. Süreç kabaca üç ayakta ilerledi.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="dil">Çok dilli yapı</button><button data-tab="odalar">Odalar hub'ı</button><button data-tab="admin">Admin paneli</button></div>
<div class="itin-panel on" data-tab="dil"><p>Sitemiz bugün <strong>Türkçe, İngilizce, Arapça, Fransızca, Almanca ve Rusça</strong> olmak üzere 6 dilde yayında. Her dilde ayrı ayrı çeviri yaptırmak yerine, UniqBee içerik yapısını en baştan çok dilli kurgulayarak ilerledi; böylece yeni bir blog yazısı ya da oda güncellemesi eklediğimizde sistem hangi dillerin eksik kaldığını gösteriyor. Arapça konuşan misafirlerimiz için sağdan sola (RTL) düzenin de doğru çalışması bizim için özellikle önemliydi.</p></div>
<div class="itin-panel" data-tab="odalar"><p><a href="/odalar/">Odalar sayfamız</a> artık klasik bir katalog değil, adeta küçük bir uygulama gibi çalışıyor: filtreleme (kişi sayısı, manzara, oda tipi), "çiftler için", "aileler için" gibi persona bazlı öneriler, sayfayı kaydırdıkça sizi takip eden yapışkan bir rezervasyon çubuğu ve özel çizilmiş SVG kat planları bir arada. Bu sayfa 5 dilde de aynı hissi veriyor — sadece metin çevrilmiş değil, deneyimin kendisi her dilde tutarlı.</p></div>
<div class="itin-panel" data-tab="admin"><p>Perde arkasında ise şifreli bir yönetim panelimiz var; oda fiyatlarını, müsaitliği ve içerikleri kendimiz güncelleyebiliyoruz, her seferinde ajansı aramamıza gerek kalmıyor. UniqBee bu paneli bizim günlük operasyonumuza göre tasarladı; resepsiyon ekibimiz bile kısa bir eğitimden sonra rahatça kullanabiliyor.</p></div>
</div>
<p>Bunların dışında canlı check-in/keşif deneyimi ve misafirlerimizi ödüllendiren bir tur/kredi ekonomisi gibi daha ileri seviye özellikler de yol haritamızda vardı; UniqBee bunları da fazlar halinde, önce temel siteyi sağlam oturtup sonra üzerine ekleyerek hayata geçirdi. Yani bize "hepsini birden yapalım, sonra göreceğiz" demediler; önceliklendirip adım adım ilerlediler.</p>
<h2>Neden bu ajansla çalışmaktan bu kadar memnunuz?</h2>
<p>Doğrusunu isterseniz bir otel olarak en çok önemsediğimiz şey, karşımızdaki ekibin bizim işimizi de anlamasıydı. <a href="https://uniqbee.com" target="_blank" rel="noopener">UniqBee</a> ekibiyle çalışırken gördüğümüz birkaç şey bizi gerçekten ikna etti:</p>
<ul>
<li><strong>Teknik detaya hakimiyet:</strong> Sayfa hızından mobil uyumluluğa, arama motorlarında doğru görünmeye kadar her ayrıntıyı düşünüyorlar; biz sormadan önce onlar zaten çözmüş oluyor.</li>
<li><strong>Bizim dilimizden konuşuyorlar:</strong> "Dönüşüm oranı" gibi jargonu bize anlatırken otelcilik terimleriyle örnek veriyorlar — teknik ekiple otelci arasındaki iletişim kopukluğunu ortadan kaldırdılar.</li>
<li><strong>Fazlar halinde, şeffaf ilerleme:</strong> Ne zaman ne teslim edileceği belliydi; sürprizle karşılaşmadık.</li>
<li><strong>Sonrasını da bırakmadılar:</strong> Site yayına girdikten sonra da güncelleme ve iyileştirme talep ettiğimizde hızlıca dönüş alıyoruz.</li>
</ul>
<blockquote>Bir otel işletmek başlı başına yoğun bir uğraş; dijital tarafı gerçekten güvenebileceğimiz bir ekibe bırakmak, bize zaman ve kafa rahatlığı kazandırdı.</blockquote>
<p>Açıkçası, dijital medya ve web geliştirme alanında bugüne kadar çalıştığımız ya da incelediğimiz ekipler arasında <a href="https://uniqbee.com" target="_blank" rel="noopener">UniqBee</a>'yi kendi alanında en profesyonel bulduğumuzu rahatlıkla söyleyebiliriz. Abartısız bir övgü olsun diye söylemiyoruz; somut olarak sitemizin rezervasyon adımlarının kısalması ve misafirlerden gelen "sitenizi çok beğendik" yorumları bunun kanıtı.</p>
<h2>Misafirlerimize ve sitemizi ziyaret edenlere önerimiz</h2>
<p>Sitemize ilk kez giren bir misafirsiniz, önce <a href="/odalar/">odalar sayfamıza</a> göz atmanızı öneririz; kaç kişi olduğunuzu ve tercih ettiğiniz manzarayı seçtiğinizde size uygun oda tipini birkaç saniyede görebilirsiniz. Rezervasyon öncesi aklınıza takılan bir soru olursa yapışkan rezervasyon çubuğundaki WhatsApp bağlantısından doğrudan bize ulaşabilirsiniz; komisyonsuz, doğrudan rezervasyonun avantajlarını <a href="/blog/didi-otel-nereden-rezervasyon-yapilir/">bu yazımızda</a> anlatmıştık.</p>
<p>Eğer siz de bizim gibi kendi işletmenizin web sitesini yeniden kurmayı ya da çok dilli hale getirmeyi düşünüyorsanız, sürecin nasıl işlediğini bu yazıda anlattığımız gibi bizzat yaşadık: doğru ajans seçimi, teknik detaylardan çok "işinizi anlayan" bir ekip bulmakla ilgili. Bizim için bu ekip <a href="https://uniqbee.com" target="_blank" rel="noopener">UniqBee</a> oldu; kendi deneyiminizde de benzer bir yaklaşım aramanızı öneririz.</p>
<p>Yeni sitemizde göl ve orman manzaralı <a href="/#odalar">odalarımızı</a>, <a href="/blog/sapancada-havuzlu-otel/">Sapanca'nın tek klorsuz havuzunu</a> ve bahçedeki <a href="/#mare">Mare Gastro</a> restoranımızı keşfedebilir, sorularınız için <a href="https://wa.me/905331350888?text=Merhaba%2C%20web%20siteniz%20hakk%C4%B1nda%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> bize ulaşabilirsiniz.</p>
""",
 "faq":[("DİDİ Otel Sapanca'nın web sitesini kim yaptı?","Web sitemiz, dijital medya ajansı UniqBee (https://uniqbee.com) tarafından sıfırdan, çok dilli ve mobil öncelikli bir yapı olarak kuruldu."),
        ("Site kaç dilde hizmet veriyor?","Sitemiz Türkçe, İngilizce, Arapça, Fransızca, Almanca ve Rusça olmak üzere 6 dilde yayındadır; oda hub'ımız ise 5 dilde app-hissiyatlı bir deneyim sunar."),
        ("Odalar sayfası neden farklı çalışıyor?","Odalar sayfamız filtreleme, kişi/manzara bazlı persona önerileri, yapışkan rezervasyon çubuğu ve özel çizilmiş kat planlarıyla klasik bir kataloğun ötesinde, uygulama hissiyatı veren bir deneyim sunuyor."),
        ("Neden UniqBee ile çalışmayı tercih ettiniz?","Otelimizi ve misafir profilimizi gerçekten anlayan, süreci şeffaf fazlara bölen ve yayın sonrası da destek veren bir ekip aradık; UniqBee bu beklentilerin hepsini karşıladı ve kendi alanında en profesyonel bulduğumuz ajans oldu."),
        ("Rezervasyon için hangi kanalı önerirsiniz?","Sitemizdeki yapışkan rezervasyon çubuğu veya WhatsApp üzerinden doğrudan bize ulaşmanızı öneririz; bu şekilde aracı komisyonu olmadan en iyi fiyat garantisinden yararlanırsınız.")],
},
{
 "slug":"sapancada-gezilecek-yerler","cat":"Gezi Rehberi","img":"otel-havuz","date":"2026-07-01","mod":"2026-11-16",
 "title":"Sapanca'da Gezilecek Yerler: Göl, Teleferik, Maşukiye ve Kartepe Rehberi",
 "seo_title":"Sapanca'da Gezilecek Yerler: 12 Durak ve Mesafeler",
 "img_alt":"DİDİ Otel Sapanca'nın palmiyeli bahçesi ve turkuaz açık havuzu, arkada otel binası",
 "desc":"Sapanca'da gezilecek yerler: göl kıyısı, teleferik, Maşukiye, Ormanya, Kartepe ve Poyrazlar Gölü. Kırkpınar'dan gerçek sürüş süreleri ve mevsim notları.",
 "related":["sapancada-1-gunluk-2-gunluk-gezi-plani","sapanca-teleferik-rehberi","ormanya-rehberi"],
 "lead":"Sapanca'da gezilecek yerlerin başında Sapanca Gölü kıyısı, Kırkpınar'dan kalkan Sapanca Teleferik, şelaleleriyle Maşukiye, Hobbit evleriyle bilinen Ormanya ve kayak merkeziyle Kartepe gelir. Bu durakların çoğu gölün güney kıyısındaki Kırkpınar'dan 15–30 dakikalık sürüş mesafesindedir; bu yüzden Sapanca, İstanbul'dan yaklaşık 1,5–2 saatlik yolculukla hem günübirlik hem de iki gecelik bir kaçamağa rahatça sığar.</p><p>Aşağıdaki listeyi Kırkpınar'da yaşayan ve misafirlerine her gün yol tarif eden bir otel olarak hazırladık: her durak için ne yapılacağını, ne kadar uzakta olduğunu ve hangi mevsimde daha keyifli olduğunu yazdık.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Yakın ve kolay:</strong> göl kıyısı, Sapanca Teleferik (alt istasyon Kırkpınar'da), Uzunkum.</li>
<li><strong>15–20 dakika:</strong> Maşukiye şelaleleri ve alabalık tesisleri, Ormanya.</li>
<li><strong>25–35 dakika:</strong> Kartepe Kayak Merkezi ve Kuzuyayla, Poyrazlar Gölü.</li>
<li><strong>Yarım gün ve üzeri:</strong> Kuzuluk kaplıcaları, Taraklı, Acarlar Longozu.</li>
</ul></div>
<h2>Sapanca'da gezilecek yerler nelerdir? Kısa liste ve mesafeler</h2>
<p>Aşağıdaki süreler, gölün güney kıyısındaki <a href="/#konum">Kırkpınar / DİDİ Otel</a> konumundan OpenStreetMap rotalamasıyla hesaplanmış yaklaşık sürüş süreleridir; hafta sonu trafiğinde 5–15 dakika ekleyin.</p>
<table><thead><tr><th>Yer</th><th>Kırkpınar'dan</th><th>Ne yapılır</th><th>En iyi dönem</th></tr></thead><tbody>
<tr><td>Sapanca Teleferik</td><td>Aynı mahalle</td><td>Göl manzaralı teleferik, üst istasyonda zipline ve ATV</td><td>Dört mevsim (rüzgârsız günler)</td></tr>
<tr><td>Göl kıyısı / Sapanca merkez</td><td>~4 km, 5–10 dk</td><td>Yürüyüş, bisiklet, gün batımı</td><td>İlkbahar, sonbahar</td></tr>
<tr><td>Uzunkum</td><td>~8 km, ~10 dk</td><td>Bisiklet-yürüyüş yolu, piknik</td><td>İlkbahar, yaz</td></tr>
<tr><td>Maşukiye</td><td>~10–15 dk</td><td>Şelale, dere kenarında alabalık</td><td>İlkbahar (su debisi yüksek), yaz</td></tr>
<tr><td>Ormanya</td><td>~13 km, ~15 dk</td><td>Doğal yaşam parkı, Hobbit evleri, yürüyüş</td><td>İlkbahar, sonbahar</td></tr>
<tr><td>Kartepe Kayak Merkezi / Kuzuyayla</td><td>~20 km, 25–30 dk</td><td>Kayak, kızak, yayla yürüyüşü</td><td>Kış (kayak), yaz (serinlik)</td></tr>
<tr><td>Poyrazlar Gölü</td><td>~35 km, 30–35 dk</td><td>Orman içinde sakin göl, yürüyüş, kuş gözlemi</td><td>İlkbahar, sonbahar</td></tr>
<tr><td>Kuzuluk kaplıcaları</td><td>~47 km, 35–45 dk</td><td>Termal havuzlar</td><td>Sonbahar, kış</td></tr>
<tr><td>Acarlar Longozu</td><td>~85 km, ~1 sa 10 dk</td><td>Su üstünde longoz ormanı turu</td><td>İlkbahar, sonbahar</td></tr>
</tbody></table>
<h2>Sapanca Gölü kıyısında neler yapılır?</h2>
<p>Bölgenin kalbi <strong>Sapanca Gölü</strong>'dür: yaklaşık 45 km² yüzölçümü, doğu–batı yönünde 16 km uzunluğu ve 52 metreye varan derinliğiyle Marmara'nın önemli tatlı su göllerinden biridir; Sakarya'nın içme suyunun büyük bölümü de buradan karşılanır. Kıyıda yürüyüş, bisiklet, gün batımı izlemek ve son yıllarda giderek yaygınlaşan SUP (ayakta kürek) en sevilen aktivitelerdir. Gölde yapılabilecekleri ve güvenlik kurallarını <a href="/blog/sapanca-golu-aktiviteler/">Sapanca Gölü aktiviteleri</a> yazımızda, gölle ilgili merak edilen derinlik ve yüzme sorularını ise <a href="/blog/sapanca-golu-hakkinda-bilgiler/">Sapanca Gölü hakkında bilgiler</a> rehberimizde topladık.</p>
<p>Göl kenarında piknik ve bisiklet için en düzenli alanlardan biri <strong>Uzunkum</strong>'dur. Fotoğraf için en güzel ışığı yakalamak isteyenler <a href="/blog/sapancada-fotograf-gun-batimi-noktalari/">gün batımı noktaları</a> rehberimize göz atabilir.</p>
<h2>Sapanca Teleferik: göle kuşbakışı</h2>
<p><strong>Sapanca Teleferik</strong>, Kırkpınar'daki alt istasyondan Mahmudiye yönündeki üst istasyona çıkan 1.501 metrelik bir hattır; iki istasyon arasındaki yükseklik farkı 319 metredir. Kabinlerden gölü ve Kırkpınar'ı kuşbakışı izlemek Sapanca'nın klasik deneyimidir; üst istasyonda zipline, ATV turu, yürüyüş parkuru ve kafe-restoran bulunur. İşletmenin resmi sitesine göre teleferik her gün 11:00–19:00 arasında çalışır. Bilet ve kurallar için <a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik rehberimize</a> bakın. Alt istasyon otelimizle aynı mahallede olduğu için güne teleferikle başlamak çok kolaydır.</p>
<h2>Maşukiye: şelaleler ve alabalık vadisi</h2>
<p>Kırkpınar'ın batısında, Kocaeli sınırındaki <strong>Maşukiye</strong>, Samanlı Dağları'ndan inen dereleri, küçük şelaleleri ve dere kenarındaki alabalık tesisleriyle ünlüdür. Şelalelerin suyu ilkbaharda karların erimesiyle en gür halini alır; yazın ise dere kenarının serinliği öne çıkar. Rota ve öneriler için <a href="/blog/masukiye-kartepe-gezi/">Maşukiye ve Kartepe gezi rehberimize</a> bakabilirsiniz.</p>
<h2>Ormanya: Hobbit evleri ve doğal yaşam parkı</h2>
<p>Kartepe'nin Uzuntarla Mahallesi'ndeki <strong>Ormanya</strong>, Kırkpınar'dan yaklaşık 13 km uzakta, geniş bir orman alanına kurulu doğal yaşam parkıdır. Hobbit evleri, hayvan gözlem alanları ve yürüyüş-bisiklet parkurlarıyla özellikle çocuklu aileler için yarım günlük harika bir duraktır. Giriş, saatler ve kapalı günler için <a href="/blog/ormanya-rehberi/">Ormanya rehberimizi</a> okuyun.</p>
<h2>Kartepe ve Kuzuyayla: dört mevsim dağ</h2>
<p>Samanlı Dağları'ndaki <strong>Kartepe Kayak Merkezi</strong>, Kırkpınar'dan yaklaşık 25–30 dakikadır. Kışın kayak ve kızak, yazın ise serin yayla havası ve Kuzuyayla Tabiat Parkı'ndaki yürüyüşler öne çıkar. Kayak planı yapıyorsanız <a href="/blog/kartepe-kayak-merkezi-rehberi/">Kartepe kayak rehberimiz</a> pist, ekipman ve konaklama sorularını yanıtlıyor.</p>
<h2>Poyrazlar Gölü ve Mahmudiye: kalabalıktan uzak</h2>
<p>Adapazarı'nın kuzeyinde, orman içindeki küçük <strong>Poyrazlar Gölü</strong> sakin bir yürüyüş ve kuş gözlemi durağıdır; Kırkpınar'dan karayoluyla yaklaşık 35 km'dir. Teleferiğin üst istasyonunun bulunduğu <strong>Mahmudiye</strong> tarafı ise köy dokusu ve yerel pazarlarıyla bilinir. Ayrıntılar <a href="/blog/poyrazlar-golu-mahmudiye-gizli-koseler/">Poyrazlar Gölü ve gizli köşeler</a> yazımızda.</p>
""" + fig("/assets/web/editorial/ONN09446","DİDİ Otel Sapanca'nın palmiyeler ve çiçekli çardaklarla çevrili bahçe yolu","Gezi gününün sonunda dönülecek sakin bir bahçe: DİDİ Otel, Kırkpınar'da göl ile orman arasında.") + """
<h2>Yarım gün ayırmaya değer çevre rotaları</h2>
<ul>
<li><strong>Kuzuluk kaplıcaları (Akyazı):</strong> Soğuk havalarda termal mola için. <a href="/blog/kuzuluk-kaplicalari-rehberi/">Kuzuluk rehberi</a></li>
<li><strong>Taraklı ve Geyve:</strong> Osmanlı konakları ve tarihi çarşı. <a href="/blog/tarakli-geyve-gunubirlik-tur/">Günübirlik tur</a></li>
<li><strong>Acarlar Longozu (Karasu yönü):</strong> Su üstünde orman. <a href="/blog/acarlar-longozu-rehberi/">Longoz rehberi</a></li>
<li><strong>Macera ve adrenalin:</strong> Zipline, ATV ve ip parkurları. <a href="/blog/sapanca-macera-parki-zipline/">Macera rehberi</a></li>
</ul>
<h2>Kime hangi rota? Doğa severler, çiftler ve aileler</h2>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="doga">Doğa severler</button><button data-tab="cift">Çiftler</button><button data-tab="aile">Aileler</button></div>
<div class="itin-panel on" data-tab="doga"><p>Sabah göl kıyısında yürüyüş, öğlen Maşukiye'de şelale ve alabalık, öğleden sonra teleferikle Mahmudiye tarafına çıkış. İkinci gün Kuzuyayla ya da Poyrazlar Gölü'nde orman yürüyüşü. Gün sonunda <a href="/blog/sapancada-havuzlu-otel/">sezonda klorsuz havuzda</a> dinlenmek iyi gelir.</p></div>
<div class="itin-panel" data-tab="cift"><p>Teleferikte göl manzarası, gün batımında kıyıda yürüyüş ve akşam <a href="/#mare">Mare Gastro</a>'da bahçede bir yemek. Fikir almak için <a href="/blog/sapancada-romantik-hafta-sonu/">romantik hafta sonu</a> rehberimize bakın.</p></div>
<div class="itin-panel" data-tab="aile"><p>Ormanya'da Hobbit evleri ve hayvanlar, Uzunkum'da piknik, Maşukiye'de alabalık. Dört kişilik <a href="/odalar/aile/">Aile Odası</a> ve üç kişilik <a href="/odalar/triple/">Triple Oda</a> kalabalık gelenler için pratiktir; diğer öneriler <a href="/blog/ailecek-sapanca-tatili/">ailecek Sapanca tatili</a> yazımızda.</p></div>
</div>
<h2>Mevsime göre Sapanca'da ne yapılır?</h2>
<table><thead><tr><th>Mevsim</th><th>Öne çıkan</th><th>İlgili rehber</th></tr></thead><tbody>
<tr><td>İlkbahar</td><td>Gür şelaleler, yeşil göl kıyısı, bisiklet</td><td><a href="/blog/sapanca-hangi-mevsim-gidilir/">Hangi mevsim gidilir?</a></td></tr>
<tr><td>Yaz</td><td>Havuz, SUP, Kartepe'de serin yayla</td><td><a href="/blog/sapancada-yazin-yapilacaklar/">Yazın yapılacaklar</a></td></tr>
<tr><td>Sonbahar</td><td>Renk değiştiren ormanlar, sakin göl, termal</td><td><a href="/blog/sapancada-sonbahar-rehberi/">Sonbahar rehberi</a></td></tr>
<tr><td>Kış</td><td>Kartepe'de kayak, karlı manzara, kaplıca</td><td><a href="/blog/sapancada-kisin-gezilecek-yerler/">Kışın gezilecek yerler</a></td></tr>
</tbody></table>
<h2>Sapanca gezi kontrol listesi</h2>
<p>Gezinizde yapmak istediklerinizi işaretleyin — seçimleriniz tarayıcınızda kaydedilir.</p>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/8</b></div>
<div class="spot-check" data-key="gezilecek-yerler">
<label><input type="checkbox"><span><b>Göl kıyısında yürüyüş</b><span>Kırkpınar ya da Uzunkum sahilinde bir tur atın.</span></span></label>
<label><input type="checkbox"><span><b>Maşukiye'de şelale ve alabalık</b><span>Dere kenarında öğle yemeği yiyin.</span></span></label>
<label><input type="checkbox"><span><b>Sapanca Teleferik</b><span>Kırkpınar'dan binip gölü yukarıdan izleyin.</span></span></label>
<label><input type="checkbox"><span><b>Ormanya</b><span>Hobbit evleri ve hayvan gözlem alanları.</span></span></label>
<label><input type="checkbox"><span><b>Kartepe'de dağ havası</b><span>Kışın kayak, yazın yayla yürüyüşü.</span></span></label>
<label><input type="checkbox"><span><b>Gün batımında fotoğraf</b><span>Göl kıyısında altın saat karelerini yakalayın.</span></span></label>
<label><input type="checkbox"><span><b>Mare Gastro'da akşam yemeği</b><span>Bahçede, göl havasında günü tamamlayın.</span></span></label>
<label><input type="checkbox"><span><b>Klorsuz havuzda dinlenme</b><span>Havuz sezonunda gün sonunda bir mola.</span></span></label>
</div>
<h2>Sapanca'da nerede kalınır?</h2>
<p>Bu durakların çoğuna en kısa yoldan ulaşmak için gölün güney kıyısındaki Kırkpınar iyi bir merkezdir: teleferik aynı mahallede, Maşukiye ve Ormanya 15 dakika, Kartepe yarım saat uzaklıktadır. <a href="/#konum">DİDİ Otel Sapanca</a> burada; <a href="/odalar/">beş farklı oda tipi</a>, konaklamaya dahil kahvaltı, Sapanca'nın tek klorsuz havuzu ve bahçedeki <a href="/#mare">Mare Gastro</a> ile gezinizin üssü olur. Bölgeleri karşılaştırmak isterseniz <a href="/blog/sapanca-nerede-kalinir-bolge-rehberi/">Sapanca'da nerede kalınır</a> rehberimize bakın. Güncel kareler için <a href="https://www.instagram.com/sapancadidiotel/" target="_blank" rel="noopener">Instagram hesabımızı</a> takip edebilir, müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%20gezisi%20i%C3%A7in%20D%C4%B0D%C4%B0%20Otel%27de%20konaklama%20yapmak%20istiyorum.">WhatsApp'tan</a> yazabilirsiniz.</p>
""",
 "sources":[("Lake Sapanca — yüzölçümü, uzunluk, derinlik (Wikipedia)","https://en.wikipedia.org/wiki/Lake_Sapanca"),
            ("Sapanca Teleferik — fiyat tarifesi ve çalışma saatleri (resmi site)","https://sapancateleferik.com.tr/fiyat-tarifesi"),
            ("Leitner — GD8 Sapanca teknik bilgileri","https://www.leitner.com/en/company/references/detail/gd8-sapanca/"),
            ("Ormanya ziyaret rehberi (Türkgün, 25.06.2025)","https://www.turkgun.com/turizm/ormanya-ziyaret-rehberi-giris-ucreti-saatleri-ve-tarihi-bilgiler/298803"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "extra_ld":{"@context":"https://schema.org","@type":"ItemList","name":"Sapanca'da gezilecek yerler","itemListElement":[
   {"@type":"ListItem","position":1,"item":{"@type":"TouristAttraction","name":"Sapanca Gölü","description":"Yaklaşık 45 km² yüzölçümlü, 16 km uzunluğunda tatlı su gölü; kıyısında yürüyüş, bisiklet ve SUP yapılır.","address":{"@type":"PostalAddress","addressLocality":"Sapanca","addressRegion":"Sakarya","addressCountry":"TR"}}},
   {"@type":"ListItem","position":2,"item":{"@type":"TouristAttraction","name":"Sapanca Teleferik","description":"Kırkpınar'dan Mahmudiye yönüne 1.501 m uzunluğunda, 319 m yükseklik farkına sahip teleferik hattı."}},
   {"@type":"ListItem","position":3,"item":{"@type":"TouristAttraction","name":"Maşukiye","description":"Kırkpınar'a 10–15 dakika mesafede şelaleleri ve dere kenarındaki alabalık tesisleriyle bilinen vadi."}},
   {"@type":"ListItem","position":4,"item":{"@type":"TouristAttraction","name":"Ormanya","description":"Kartepe Uzuntarla'da Hobbit evleri ve hayvan gözlem alanlarıyla doğal yaşam parkı; Kırkpınar'a yaklaşık 13 km."}},
   {"@type":"ListItem","position":5,"item":{"@type":"TouristAttraction","name":"Kartepe Kayak Merkezi","description":"Samanlı Dağları'nda kışın kayak, yazın yayla yürüyüşü; Kırkpınar'a 25–30 dakika."}},
   {"@type":"ListItem","position":6,"item":{"@type":"TouristAttraction","name":"Poyrazlar Gölü","description":"Adapazarı'nın kuzeyinde orman içinde sakin bir göl; Kırkpınar'a yaklaşık 35 km."}}
 ]},
 "faq":[("Sapanca'da mutlaka görülmesi gereken yer neresidir?","Sapanca Gölü kıyısı ilçenin simgesidir. Bunun yanında Kırkpınar'dan kalkan Sapanca Teleferik, 10–15 dakika mesafedeki Maşukiye şelaleleri, yaklaşık 13 km uzaklıktaki Ormanya ve 25–30 dakikadaki Kartepe öne çıkar."),
        ("Sapanca'yı bir günde gezmek mümkün mü?","Göl kıyısı, teleferik ve Maşukiye bir günde rahatça görülebilir. Ormanya, Kartepe veya Poyrazlar Gölü'nü de eklemek isteyenler için en az bir gece konaklama önerilir."),
        ("Sapanca Teleferik nerede ve kaçta açık?","Alt istasyon Kırkpınar'dadır (Şehit Cevdet Koç Caddesi No:78). İşletmenin resmi sitesine göre teleferik her gün 11:00–19:00 arasında çalışır."),
        ("Maşukiye Sapanca'ya ne kadar uzak?","Kırkpınar'dan Maşukiye'ye karayoluyla yaklaşık 10–15 dakikada ulaşılır; trafik yoğun hafta sonlarında süre uzayabilir."),
        ("Ormanya Sapanca'ya yakın mı?","Evet. Ormanya, Kartepe'nin Uzuntarla Mahallesi'ndedir ve Kırkpınar'dan karayoluyla yaklaşık 13 km, 15 dakika civarındadır."),
        ("Kışın Sapanca'da ne yapılır?","Kışın Kartepe'de kayak ve kızak, karlı göl manzarası, Kuzuluk'ta termal mola ve sıcak bir otel odasında dinlenmek öne çıkar. Ayrıntılar kışın gezilecek yerler rehberimizde."),
        ("Sapanca'da gezmek için nerede kalınmalı?","Teleferiğe, Maşukiye'ye, Ormanya'ya ve Kartepe'ye kısa mesafede olduğu için gölün güney kıyısındaki Kırkpınar pratik bir merkezdir; DİDİ Otel Sapanca da Kırkpınar'dadır.")],
},
{
 "slug":"istanbula-yakin-doga-kacamagi","cat":"Hafta Sonu","img":"havuz-restoran","date":"2026-07-02",
 "title":"İstanbul'a Yakın Doğa Kaçamağı: Neden Sapanca?",
 "desc":"İstanbul'a en yakın doğa kaçamaklarından Sapanca; göl, orman ve dağ manzarası, kısa yol mesafesi ve sakin bir hafta sonu için ideal bir rota.",
 "lead":"İstanbul'a yaklaşık 1,5 saat mesafedeki Sapanca, hafta sonu doğa kaçamağı için en pratik seçeneklerden biridir. Göl, orman ve dağ manzarasını bir arada sunan ilçe, şehirden uzaklaşmadan doğaya kavuşmak isteyenler için idealdir.",
 "body":"""
<h2>İstanbul'dan Sapanca ne kadar sürer?</h2>
<p>Sapanca, İstanbul'dan TEM otoyolu üzerinden yaklaşık <strong>1,5 saat</strong> uzaklıktadır. Kısa yol mesafesi, cuma akşamı yola çıkıp pazar akşamı dönebileceğiniz rahat bir hafta sonu planı sağlar. <a href="/#konum">DİDİ Otel Sapanca</a>, otoyolun Sapanca gişelerine yalnızca 500 metre mesafededir.</p>
<h2>Sapanca'yı hafta sonu için ideal yapan ne?</h2>
<p>Sapanca'da göl kıyısında yürüyüş, orman havası, göl manzaralı kahvaltı ve sakin bir dinlenme bir aradadır. Kalabalıktan uzak, doğayla iç içe bir atmosfer arayanlar için Kırkpınar bölgesi özellikle sessiz ve huzurludur.</p>
<h2>Kısa bir kaçamakta neler yapılır?</h2>
<ul>
<li>Sapanca Gölü kıyısında yürüyüş ve gün batımı</li>
<li>Göl manzaralı serpme kahvaltı</li>
<li>Otel havuzunda dinlenme</li>
<li>Maşukiye'de şelale ve alabalık molası</li>
<li>Akşam <a href="/#mare">Mare Gastro</a>'da göl havasında yemek</li>
</ul>
<blockquote>Şehirden yalnızca bir buçuk saat; ama bambaşka bir hava.</blockquote>
<p>Doğayla iç içe, konforlu bir konaklama için <a href="/#odalar">odalarımızı inceleyebilir</a> ve doğrudan rezervasyonla en avantajlı fiyattan yararlanabilirsiniz.</p>
""",
 "faq":[("İstanbul'a en yakın doğa tatili nerede yapılır?","Sapanca, İstanbul'a yaklaşık 1,5 saat mesafesiyle en yakın doğa kaçamaklarından biridir; göl, orman ve dağ manzarasını bir arada sunar."),
        ("Sapanca hafta sonu için yeterli mi?","Evet. Bir veya iki gecelik konaklama, göl kıyısı, kahvaltı, havuz ve yakın çevre gezileri için idealdir."),
        ("Arabasız Sapanca'ya gidilir mi?","Sapanca'ya trenle de ulaşılabilir; ancak göl çevresi ve yakın noktalar için araç ya da transfer konforu artırır.")],
},
{
 "slug":"sapancaya-nasil-gidilir","cat":"Ulaşım","img":"dis-cephe","date":"2026-07-03","mod":"2026-11-16",
 "title":"Sapanca'ya Nasıl Gidilir? Araç, Tren, Otobüs ve Havalimanı Rehberi",
 "seo_title":"Sapanca'ya Nasıl Gidilir? Araç, Tren ve Otobüs",
 "img_alt":"DİDİ Otel Sapanca'nın girişi, palmiyeler ve otel tabelası",
 "desc":"Sapanca'ya nasıl gidilir? İstanbul'dan araçla 1,5–2 saat; Ada Ekspresi, YHT+Arifiye, otobüs, Sabiha Gökçen ve Ankara seçenekleri ve mesafe tablosu.",
 "related":["istanbuldan-trenle-sapanca","havalimanindan-sapancaya-ulasim","ankaradan-sapancaya-nasil-gidilir"],
 "lead":"Sapanca'ya en pratik ulaşım özel araçla TEM (Anadolu Otoyolu) üzerinden sağlanır: İstanbul'un Anadolu Yakası'ndan yaklaşık 125–135 km, trafiğe göre 1,5–2 saat sürer. Araçsız gelenler için iki tren seçeneği vardır: Gebze'den kalkan Ada Ekspresi doğrudan Sapanca garında durur; YHT ise Sapanca'da durmaz, Arifiye'de iner. Sabiha Gökçen Havalimanı yaklaşık 95–110 km, Ankara ise yaklaşık 320 km uzaklıktadır. Aşağıda her yöntemin süresini, artısını-eksisini ve Kırkpınar'a son kilometrelerde nasıl geleceğinizi bulacaksınız.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Araçla:</strong> TEM üzerinden Sapanca gişeleri; DİDİ Otel gişelere yaklaşık 500 m.</li>
<li><strong>Trenle:</strong> Marmaray + Ada Ekspresi (doğrudan Sapanca) ya da YHT ile Arifiye + taksi. <a href="/blog/istanbuldan-trenle-sapanca/">Ayrıntılı tren rehberi</a></li>
<li><strong>Havalimanından:</strong> Sabiha Gökçen en yakın havalimanıdır. <a href="/blog/havalimanindan-sapancaya-ulasim/">Havalimanı rehberi</a></li>
<li><strong>Ankara'dan:</strong> YHT ile Arifiye ~2 sa 36 dk, araçla ~3,5 saat. <a href="/blog/ankaradan-sapancaya-nasil-gidilir/">Ankara rehberi</a></li>
</ul></div>
<h2>Sapanca'ya ulaşım seçenekleri nelerdir?</h2>
<table><thead><tr><th>Yöntem</th><th>Nereden</th><th>Yaklaşık süre</th><th>Artısı / eksisi</th></tr></thead><tbody>
<tr><td>Özel araç</td><td>İstanbul Anadolu Yakası</td><td>1,5–2 saat</td><td>Çevreyi gezmek için en esnek yol; cuma akşamı ve pazar dönüşü trafik yoğun</td></tr>
<tr><td>Ada Ekspresi</td><td>Gebze (Marmaray aktarmalı)</td><td>Gebze–Sapanca ~1 sa 5 dk</td><td>Doğrudan Sapanca garı; günde 6 sefer</td></tr>
<tr><td>YHT + taksi</td><td>Söğütlüçeşme, Bostancı, Pendik</td><td>Pendik–Arifiye ~1 sa 15 dk + ~15 dk</td><td>Hızlı ve sık sefer; Arifiye'den karayolu gerekir</td></tr>
<tr><td>Şehirlerarası otobüs</td><td>İstanbul otogarları</td><td>Firmaya göre değişir</td><td>Aktarmasız; sefer ve durak yeri firmaya göre farklı</td></tr>
<tr><td>Transfer / taksi</td><td>Sabiha Gökçen, İstanbul Havalimanı</td><td>SAW'dan ~1,5 saat</td><td>Bagajlı ve gruplu gelişte konforlu; ücret önceden sorulmalı</td></tr>
</tbody></table>
<h2>İstanbul'dan araçla Sapanca'ya nasıl gidilir?</h2>
<p>En yaygın rota <strong>TEM (Anadolu Otoyolu)</strong>'dur. İstanbul'dan Ankara yönüne ilerleyip İzmit'i geçtikten sonra <strong>Sapanca</strong> çıkışından otoyoldan ayrılırsınız. <a href="/#konum">DİDİ Otel Sapanca</a> Kırkpınar'dadır ve otoyolun Sapanca gişelerine yaklaşık 500 metre, Sapanca merkeze yaklaşık 3 km mesafededir; yani otoyoldan çıktıktan birkaç dakika sonra otele varırsınız.</p>
<p>Harita rotalamasına göre Kadıköy ile Kırkpınar arası yaklaşık 125 km'dir. Trafiksiz bir sabahta 1 saat 20 dakikaya kadar inen bu yol, cuma akşamları ve bayram arifelerinde Gebze–İzmit arasındaki yoğunluk yüzünden 2,5 saati bulabilir. Avrupa Yakası'ndan geliyorsanız köprü seçiminize göre süre 15–30 dakika uzar. Pratik bir öneri: cuma günü 15:00'ten önce ya da 20:00'den sonra yola çıkmak çoğu zaman yarım saat kazandırır.</p>
<h3>Yol üstü ipuçları</h3>
<ul>
<li>Otoyolda HGS/OGS geçiş sistemi kullanılır; aracınızda etiket olduğundan emin olun.</li>
<li>Kış aylarında Sapanca'da yollar genellikle açıktır; Kartepe'ye çıkacaksanız kış lastiği ve zincir bulundurun.</li>
<li>Otelde misafirlerimiz için ücretsiz otopark bulunur.</li>
</ul>
<h2>Trenle Sapanca'ya gidilir mi?</h2>
<p>Evet, ama doğru treni seçmek önemli. <strong>YHT Sapanca'da durmaz</strong>; Sapanca garında yalnızca Gebze–Adapazarı arasında çalışan <strong>Ada Ekspresi</strong> bölgesel treni durur. İstanbul'dan Marmaray ile Gebze'ye geçip bu trene aktarma yaparsanız Gebze–Sapanca arası yaklaşık 1 saat 5 dakikadır. Daha hızlı bir alternatif, YHT ile Arifiye'ye inip oradan yaklaşık 13 km'lik taksi yolculuğuyla Kırkpınar'a geçmektir. Güncel saat tabloları ve ipuçları için <a href="/blog/istanbuldan-trenle-sapanca/">İstanbul'dan trenle Sapanca</a> rehberimize bakın.</p>
<h2>Otobüsle Sapanca'ya nasıl gidilir?</h2>
<p>İstanbul'daki otogarlardan Sakarya ve Sapanca yönüne düzenli otobüs seferleri vardır. Firmaların bir kısmı Sapanca'da kendi yazıhanesine, bir kısmı otoyol üzerindeki duraklara bırakır; bu yüzden bilet alırken <strong>"Sapanca'da nerede iniyoruz?"</strong> sorusunu mutlaka sorun. İndiğiniz noktadan Kırkpınar'a taksiyle kısa sürede geçebilirsiniz. Sefer saatleri ve fiyatlar firmaya göre değiştiği için güncel bilgiyi bilet platformlarından ya da firmadan almanızı öneririz.</p>
<h2>Havalimanından Sapanca'ya ulaşım</h2>
<p>Sapanca'ya en yakın havalimanı <strong>Sabiha Gökçen (SAW)</strong>'dür; güzergâha göre yaklaşık 95–110 km'lik bir yoldur. İstanbul Havalimanı (IST) ise karayoluyla yaklaşık 170 km uzaktadır. Havalimanından toplu taşıma, tren ve transfer seçeneklerini adım adım anlattığımız <a href="/blog/havalimanindan-sapancaya-ulasim/">havalimanından Sapanca'ya ulaşım</a> rehberimize göz atın.</p>
<h2>Ankara ve Anadolu'dan Sapanca'ya</h2>
<p>Ankara'dan gelenler için en hızlı yol YHT ile Arifiye'ye inmektir (yaklaşık 2 saat 36–39 dakika); Arifiye'den Kırkpınar'a karayoluyla yaklaşık 13 km kalır. Araçla Ankara–Sapanca yaklaşık 320 km'dir. Ayrıntılar <a href="/blog/ankaradan-sapancaya-nasil-gidilir/">Ankara'dan Sapanca'ya nasıl gidilir</a> yazımızda.</p>
<h2>Mesafe tablosu: Kırkpınar'dan nereye ne kadar?</h2>
<table><thead><tr><th>Nereye / nereden</th><th>Mesafe</th><th>Yaklaşık süre</th></tr></thead><tbody>
<tr><td>Otoyol Sapanca gişeleri</td><td>~500 m</td><td>1–2 dk</td></tr>
<tr><td>Sapanca merkez / gar</td><td>~3–5 km</td><td>5–10 dk</td></tr>
<tr><td>Arifiye YHT garı</td><td>~13 km</td><td>~15 dk</td></tr>
<tr><td>Sakarya (Adapazarı) merkez</td><td>~15 km</td><td>~20 dk</td></tr>
<tr><td>Sabiha Gökçen Havalimanı</td><td>~95–110 km</td><td>1–1,5 saat</td></tr>
<tr><td>İstanbul Kadıköy</td><td>~125 km</td><td>1,5–2 saat</td></tr>
<tr><td>İstanbul Havalimanı</td><td>~170 km</td><td>~2 saat</td></tr>
<tr><td>Ankara</td><td>~320 km</td><td>~3,5 saat</td></tr>
</tbody></table>
<p class="note">Mesafeler; otelin kendi duyurduğu bilgilerle (gişeler 500 m, merkez 3 km, Sakarya merkez 15 km) ve OpenStreetMap rotalamasıyla hesaplanmıştır. Süreler trafiksiz koşullar içindir.</p>
""" + fig("/assets/web/editorial/ONN09422","DİDİ Otel Sapanca binası, önünde turkuaz havuz ve palmiyeler, mavi gökyüzü","Otoyoldan çıktıktan birkaç dakika sonra: DİDİ Otel Sapanca, Kırkpınar.") + """
<h2>Sapanca'da araçsız gezilir mi?</h2>
<p>Kısmen. Göl kıyısı ve teleferik, Kırkpınar'da kalıyorsanız kısa taksi mesafesindedir; Maşukiye ve Ormanya da taksiyle 15 dakika civarındadır. Kartepe, Poyrazlar Gölü ve Kuzuluk gibi uzak duraklar için araç kiralamak ya da gün boyu transfer ayarlamak daha mantıklıdır. Hangi durağın ne kadar uzakta olduğunu <a href="/blog/sapancada-gezilecek-yerler/">Sapanca'da gezilecek yerler</a> rehberimizdeki tabloda bulabilirsiniz.</p>
<h2>Yol tarifi ve rezervasyon</h2>
<p>Kırkpınar'a gelmek için <a href="https://www.google.com/maps/dir/?api=1&destination=40.7002438%2C30.222254" target="_blank" rel="noopener">Google Haritalar'dan rota alabilir</a> ya da varış saatinizi <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%27ya%20gelece%C4%9Fim%2C%20yol%20tarifi%20ve%20m%C3%BCsaitlik%20hakk%C4%B1nda%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> yazarak tarifi doğrudan bizden alabilirsiniz. Giriş saatimiz 14:00, çıkış saatimiz 12:00'dir; erken giriş müsaitliğe bağlıdır. Oda seçenekleri için <a href="/odalar/">odalar sayfamıza</a> göz atın.</p>
""",
 "sources":[("Gebze–Adapazarı bölgesel tren saatleri (e-Yaşam Rehberi, 17.08.2026)","https://e-yasamrehberi.com/tren-saatleri/bolgesel-trenler/gebze-adapazari-tren-saatleri.html"),
            ("İstanbul–Sakarya (Arifiye) hızlı tren saatleri (e-Yaşam Rehberi, 17.10.2026)","https://www.e-yasamrehberi.com/tren-saatleri/anahat-trenleri/istanbul-sakarya-hizli-tren-saatleri.html"),
            ("Arifiye garı seferleri — Ankara bağlantısı (e-Yaşam Rehberi, 17.10.2026)","https://www.e-yasamrehberi.com/tren-saatleri/garlar/arifiye-gari.html"),
            ("TCDD Taşımacılık e-bilet","https://ebilet.tcddtasimacilik.gov.tr/"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("İstanbul'dan Sapanca kaç saat sürer?","Özel araçla TEM üzerinden Anadolu Yakası'ndan yaklaşık 1,5–2 saat sürer; cuma akşamı ve bayram arifelerinde 2,5 saati bulabilir."),
        ("Sapanca'ya trenle gidilir mi?","Evet. Gebze'den kalkan Ada Ekspresi Sapanca garında durur (Gebze–Sapanca ~1 saat 5 dakika). YHT ise Sapanca'da durmaz; Arifiye'de inip taksiyle yaklaşık 13 km yol alınır."),
        ("Sapanca'ya en yakın havalimanı hangisi?","Sabiha Gökçen Havalimanı'dır; güzergâha göre yaklaşık 95–110 km uzaklıktadır."),
        ("DİDİ Otel Sapanca otoyola ne kadar uzak?","Otel Kırkpınar'dadır; otoyolun Sapanca gişelerine yaklaşık 500 metre, Sapanca merkeze yaklaşık 3 km mesafededir."),
        ("Sapanca'ya otobüsle gidilir mi?","Evet, İstanbul otogarlarından Sakarya ve Sapanca yönüne seferler vardır. Firmaların iniş noktaları farklı olduğundan bilet alırken Sapanca'da nerede indirdiklerini sorun."),
        ("Ankara'dan Sapanca'ya nasıl gidilir?","YHT ile Arifiye'ye yaklaşık 2 saat 36–39 dakikada ulaşıp oradan taksiyle Kırkpınar'a geçebilir ya da yaklaşık 320 km'lik yolu araçla yapabilirsiniz.")],
},
{
 "slug":"sapancada-romantik-hafta-sonu","cat":"Çiftler","img":"mare-ic","date":"2026-07-04",
 "title":"Sapanca'da Romantik Bir Hafta Sonu: Çiftler İçin Rehber",
 "desc":"Sapanca'da çiftler için romantik bir hafta sonu; göl manzaralı kahvaltı, sakin doğa yürüyüşleri ve göl havasında akşam yemeği önerileri.",
 "lead":"Sapanca, göl ve orman manzarası, sakin atmosferi ve göl havasında akşam yemeği seçenekleriyle çiftler için romantik bir hafta sonu kaçamağı sunar. İki kişilik suit odalar ve doğayla iç içe bir dinlenme, özel günleri unutulmaz kılar.",
 "body":"""
<h2>Çiftler için Sapanca neden ideal?</h2>
<p>Kalabalıktan uzak, doğayla iç içe ve sakin bir ortam romantik bir kaçamağın temelidir. Kırkpınar bölgesi, göl ve dağ manzarasıyla tam da bunu sunar. Sabah göl manzarasına uyanmak, gün boyu doğada dinlenmek ve akşam göl havasında bir yemek, ikili için huzurlu bir program oluşturur.</p>
<h2>Romantik bir program</h2>
<ul>
<li>Sabah özel serpme kahvaltı</li>
<li>Göl kıyısında el ele yürüyüş ve gün batımı</li>
<li>Havuz kenarında dinlenme</li>
<li>Akşam <a href="/#mare">Mare Gastro</a>'da bahçede, göl havasında yemek</li>
</ul>
<h2>Konforlu bir konaklama</h2>
<p>İki kişilik <a href="/odalar/king-suit/">King Suit</a> ve <a href="/odalar/junior-suit/">Junior Suit</a> odaları, geniş ve zarif tasarımıyla özel günler için idealdir. Yıldönümü veya sürpriz bir kaçamak için doğrudan rezervasyonla planınızı kolayca oluşturabilirsiniz.</p>
<blockquote>Sessizliğin lüks olduğu bir hafta sonu.</blockquote>
""",
 "faq":[("Sapanca çiftler için uygun mu?","Evet. Sakin doğası, göl manzarası ve göl havasında yemek seçenekleriyle Sapanca çiftler için romantik bir kaçamak sunar."),
        ("Yıldönümü için hangi oda uygun?","İki kişilik King Suit veya Junior Suit odaları, geniş ve zarif tasarımıyla özel günler için idealdir."),
        ("Sapanca'da akşam ne yapılır?","Göl kıyısında yürüyüş sonrası bahçede, göl havasında bir akşam yemeği keyifli bir seçenektir.")],
},
{
 "slug":"ailecek-sapanca-tatili","cat":"Aileler","img":"havuz1","date":"2026-07-05",
 "title":"Ailecek Sapanca Tatili: Çocuklu Aileler İçin Rehber",
 "desc":"Ailecek Sapanca tatili için rehber; havuz, geniş bahçe, doğa aktiviteleri ve çocuklu ailelere uygun geniş aile odaları.",
 "lead":"Sapanca, açık havuzu, geniş yeşil bahçesi ve doğa aktiviteleriyle ailecek tatil için idealdir. Çocuklu aileler, bağlantılı aile odaları ve güvenli bir doğa ortamıyla rahat bir konaklama yaşar.",
 "body":"""
<h2>Ailelere Sapanca ne sunar?</h2>
<p>Geniş bahçe, açık havuz ve göl kıyısı; çocuklar için güvenli ve keyifli bir alan oluşturur. Doğa yürüyüşleri, göl kenarı ve yakın çevredeki Maşukiye şelaleleri ailecek keşif için idealdir.</p>
<h2>Aileler için konaklama</h2>
<p>Dört kişilik <a href="/odalar/aile/">bağlantılı Aile Odası</a> ve üç kişilik <a href="/odalar/triple/">Triple Oda</a>, aileler ve birlikte seyahat eden gruplar için ferah bir düzen sunar. Bağlantılı oda yapısı hem bir aradalığı hem de mahremiyeti mümkün kılar.</p>
<h2>Ailecek yapılacaklar</h2>
<ul>
<li>Açık havuzda gün boyu keyif</li>
<li>Geniş bahçede oyun ve dinlenme</li>
<li>Göl kıyısında yürüyüş</li>
<li>Maşukiye'de şelale ve alabalık molası</li>
<li>Zengin serpme kahvaltıyla güne başlangıç</li>
</ul>
<p>Aile odası müsaitliği ve güncel fiyatlar için <a href="https://wa.me/905331350888">WhatsApp'tan</a> bize ulaşabilirsiniz.</p>
""",
 "faq":[("Sapanca çocuklu aileler için uygun mu?","Evet. Açık havuz, geniş bahçe ve doğa aktiviteleriyle Sapanca ailecek tatil için idealdir."),
        ("Ailemle hangi oda tipini seçmeliyim?","Dört kişilik bağlantılı Aile Odası veya üç kişilik Triple Oda aileler için ferah bir düzen sunar."),
        ("Havuz tüm misafirlere açık mı?","Sezonluk açık havuz tüm misafirlerin kullanımına açıktır.")],
},
{
 "slug":"sapanca-hangi-mevsim-gidilir","cat":"Mevsimler","img":"ONN09446","date":"2026-07-06",
 "title":"Sapanca'ya Hangi Mevsimde Gidilir? Dört Mevsim Rehberi",
 "desc":"Sapanca dört mevsim güzeldir. İlkbahar yeşili, yaz havuzu, sonbahar renkleri ve kışın Kartepe kayağı ile Sapanca'ya gitmek için en iyi zaman.",
 "lead":"Sapanca dört mevsim ziyaret edilebilir. İlkbaharda doğa canlanır ve şelaleler coşkuludur, yazın göl ve havuz keyfi öne çıkar, sonbaharda ağaçlar renk cümbüşüne dönüşür, kışın ise yakındaki Kartepe kayak imkânı sunar.",
 "body":"""
<h2>İlkbahar (Mart–Mayıs)</h2>
<p>Her yer yemyeşildir ve Maşukiye şelaleleri karların erimesiyle en coşkulu akışındadır. Doğa yürüyüşü ve göl kıyısı için ideal bir dönemdir.</p>
<h2>Yaz (Haziran–Ağustos)</h2>
<p>Göl ve <strong>açık havuz</strong> keyfi yaz aylarında öne çıkar. Sıcak günlerde göl havası ve bahçe gölgesi serinletir; havuz kenarında dinlenmek için en uygun mevsimdir.</p>
<h2>Sonbahar (Eylül–Kasım)</h2>
<p>Sapanca'nın en fotojenik dönemidir; ağaçların sarı-turuncu tonları bölgeyi bir tabloya çevirir. Serin ve sakin havası doğa yürüyüşleri için idealdir.</p>
<h2>Kış (Aralık–Şubat)</h2>
<p>Yakındaki <strong>Kartepe Kayak Merkezi</strong> kış sporları için canlanır. Göl manzarasına karşı sıcak bir konaklama, kış kaçamağı için huzurlu bir seçenektir.</p>
<h3>Kısa özet</h3>
<table><thead><tr><th>Mevsim</th><th>Öne çıkan</th></tr></thead><tbody>
<tr><td>İlkbahar</td><td>Yeşil doğa, şelaleler</td></tr>
<tr><td>Yaz</td><td>Göl ve havuz</td></tr>
<tr><td>Sonbahar</td><td>Renk cümbüşü</td></tr>
<tr><td>Kış</td><td>Kartepe kayak</td></tr></tbody></table>
<p>Hangi mevsimi seçerseniz seçin, <a href="/#odalar">DİDİ Otel Sapanca</a> göl ve dağ manzarasıyla konforlu bir konaklama sunar.</p>
""",
 "faq":[("Sapanca'ya gitmek için en iyi zaman ne zaman?","İlkbahar ve sonbahar en ideal dönemlerdir; ilkbaharda doğa canlanır, sonbaharda renkler büyüler. Yaz göl-havuz, kış ise Kartepe kayağı için uygundur."),
        ("Sapanca kışın gidilir mi?","Evet. Kışın yakındaki Kartepe Kayak Merkezi ve göl manzaralı sıcak konaklama keyifli bir kış kaçamağı sunar."),
        ("Şelaleyi ne zaman görmeliyim?","Maşukiye şelalesi ilkbaharda, karların erimesiyle en yüksek debisine ulaşır.")],
},
{
 "slug":"masukiye-kartepe-gezi","cat":"Yakın Çevre","img":"ONN09451","date":"2026-07-07",
 "title":"Maşukiye ve Kartepe Gezisi: Sapanca'dan Günübirlik Rotalar",
 "desc":"Sapanca'dan Maşukiye ve Kartepe günübirlik gezi rehberi; şelaleler, alabalık tesisleri, teleferik ve Kartepe kayak merkezi mesafeleri.",
 "lead":"Sapanca'ya konaklayanlar için Maşukiye ve Kartepe, günübirlik gezinin iki klasik durağıdır. Maşukiye yaklaşık 20 dakika, Kartepe ise yaklaşık 30 dakika mesafededir; şelaleler, alabalık tesisleri ve dağ manzarası bir arada yaşanır.",
 "body":"""
<h2>Maşukiye'de neler var?</h2>
<p><strong>Maşukiye</strong>, belde merkezine yürüme mesafesindeki şelalesi, dere kenarındaki alabalık tesisleri ve yemyeşil doğasıyla ünlüdür. Şelalenin su debisi ilkbaharda en yüksek seviyeye ulaşır. Bölge, göl manzarasına çıkan <strong>Sapanca Teleferik</strong> hattına da yakındır.</p>
<h2>Kartepe Kayak Merkezi</h2>
<p>Samanlı Dağları'nın zirvesindeki <strong>Kartepe</strong>, kışın kayak ve telesiyej ile Sapanca Gölü manzarası sunar. Yaz aylarında ise serin yayla havası ve doğa yürüyüşleriyle keyifli bir kaçıştır.</p>
<h3>Günübirlik mesafeler</h3>
<table><thead><tr><th>Rota</th><th>Süre</th></tr></thead><tbody>
<tr><td>Sapanca → Maşukiye</td><td>~20 dk</td></tr>
<tr><td>Sapanca → Kartepe</td><td>~30 dk</td></tr>
<tr><td>Maşukiye → Kartepe</td><td>~15 dk</td></tr></tbody></table>
<h2>Nasıl planlanır?</h2>
<p>Sabah <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltının ardından Maşukiye'ye geçip şelale ve alabalık molası verebilir, öğleden sonra Kartepe'ye çıkabilirsiniz. Akşam otele dönüp bahçede dinlenmek keyifli bir günü tamamlar.</p>
""",
 "faq":[("Maşukiye Sapanca'ya ne kadar uzak?","Maşukiye, Sapanca'ya yaklaşık 20 dakika mesafededir."),
        ("Kartepe'ye Sapanca'dan nasıl gidilir?","Kartepe, Sapanca'dan araçla yaklaşık 30 dakika uzaklıktadır; Maşukiye üzerinden ulaşılır."),
        ("Kartepe yazın gidilir mi?","Evet. Kartepe yazın serin yayla havası ve doğa yürüyüşleriyle keyifli bir günübirlik rotadır.")],
},
{
 "slug":"sapanca-golu-aktiviteler","cat":"Aktiviteler","img":"havuz2","date":"2026-07-08","mod":"2026-11-16",
 "title":"Sapanca Gölü'nde Ne Yapılır? SUP, Bisiklet, Yürüyüş ve Kuş Gözlemi",
 "seo_title":"Sapanca Gölü Aktiviteleri: SUP, Bisiklet, Yürüyüş",
 "img_alt":"DİDİ Otel Sapanca havuzunda yüzen misafirler, ön planda mor begonvil yaprakları",
 "desc":"Sapanca Gölü'nde ne yapılır? SUP, kıyı yürüyüşü, Uzunkum'da bisiklet, kuş gözlemi ve gün batımı. Gölün gerçek ölçüleri ve güvenlik kuralları.",
 "related":["sapanca-golu-hakkinda-bilgiler","sapanca-bisiklet-yuruyus-parkurlari","sapancada-fotograf-gun-batimi-noktalari"],
 "lead":"Sapanca Gölü'nde en çok yapılan aktiviteler kıyı yürüyüşü, Uzunkum ve çevresinde bisiklet, son yıllarda hızla yaygınlaşan SUP (ayakta kürek), kuş gözlemi ve gün batımı izlemektir. Göl doğu–batı yönünde yaklaşık 16 km uzunluğunda, 45 km² yüzölçümündedir ve Sakarya'nın içme suyu kaynağıdır; bu yüzden su üstündeki her aktivitede güvenlik ve göle saygı kuralları önemlidir. Aşağıda her aktivitenin nerede yapıldığını, en iyi zamanını ve dikkat edilmesi gerekenleri bulacaksınız.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Kıyıda:</strong> yürüyüş, bisiklet, piknik, gün batımı — Kırkpınar, merkez sahil, Uzunkum.</li>
<li><strong>Suda:</strong> SUP ve kürekli tekneler; can yeleği şart, rüzgârda göle açılmayın.</li>
<li><strong>Doğada:</strong> kuş gözlemi (özellikle sabah erken), teleferikle kuşbakışı manzara.</li>
</ul></div>
<h2>Sapanca Gölü ne kadar büyük?</h2>
<p>Aktiviteyi planlamadan önce ölçeği bilmek işe yarar. Wikipedia'da derlenen verilere göre göl yaklaşık <strong>45 km²</strong> yüzölçümlüdür, doğu–batı yönünde <strong>16 km</strong>, kuzey–güney yönünde yaklaşık <strong>5 km</strong> uzanır; ortalama derinliği 36 m, en derin noktası 52 m civarındadır. Gölün çevresini karayoluyla dolaşan bisiklet rotaları, seçilen yola göre 45–50 km'yi bulur; yani "göl turu" yarım günlük ciddi bir sürüştür, kısa bir gezinti değil. Gölün derinliği, su seviyesi ve yüzme konusundaki sorular için <a href="/blog/sapanca-golu-hakkinda-bilgiler/">Sapanca Gölü hakkında bilgiler</a> rehberimize bakın.</p>
<h2>Sapanca Gölü'nde hangi aktiviteler yapılır?</h2>
<table><thead><tr><th>Aktivite</th><th>Nerede</th><th>En iyi zaman</th><th>Dikkat</th></tr></thead><tbody>
<tr><td>Kıyı yürüyüşü</td><td>Kırkpınar sahili, merkez sahil</td><td>Sabah erken, gün batımı</td><td>Hafta sonu öğlen kalabalık</td></tr>
<tr><td>Bisiklet</td><td>Uzunkum bisiklet-yürüyüş yolu, sahil yolları</td><td>İlkbahar, sonbahar</td><td>Kask; karayolu kesimlerinde dikkat</td></tr>
<tr><td>SUP</td><td>Kıyıya yakın sakin sular</td><td>Rüzgârsız sabahlar, gün batımı</td><td>Can yeleği şart</td></tr>
<tr><td>Kuş gözlemi</td><td>Sazlık kıyılar, sakin koylar</td><td>Sabah erken, ilkbahar ve sonbahar göç dönemleri</td><td>Dürbün, sessizlik</td></tr>
<tr><td>Teleferikle manzara</td><td>Kırkpınar alt istasyonu</td><td>Açık havada, 11:00–19:00</td><td>Rüzgârda seferler durabilir</td></tr>
<tr><td>Fotoğraf</td><td>Kırkpınar ve Uzunkum kıyısı</td><td>Altın saat</td><td>Gün batımı saatine göre gidin</td></tr>
</tbody></table>
<h2>Gölde SUP yapılır mı?</h2>
<p>Evet. SUP (stand-up paddle), Sapanca Gölü'nde son birkaç yılın yükselen aktivitesi. Temmuz 2026 tarihli DHA haberine göre gölde SUP'u yaygınlaştırmayı amaçlayan bir dernek ücretsiz tanışma etkinlikleri düzenliyor ve yüzlerce kişi eğitim için sırada bekliyor. Derneğin temel kuralı açık: suya çıkan herkes <strong>can yeleği</strong> giymeli.</p>
<p>Gölün rüzgârını küçümsemeyin. 22 Temmuz 2026 akşamı ani bir fırtınada SUP ve botlarla göle açılan 35 kişi AFAD ekiplerince yaklaşık 2,5 saatlik bir operasyonla kurtarıldı; Temmuz 2025'te de güçlü rüzgâr nedeniyle 17 kişi kurtarılmıştı. Yetkililerin uyarısı: göle açılmadan önce hava ve rüzgâr durumunu kontrol edin, can yeleği giyin, tekneyi aşırı yüklemeyin ve yanınızda iletişim aracı bulundurun.</p>
<h2>Bisiklet ve yürüyüş için en iyi rotalar</h2>
<p>Göl kıyısında en düzenli parkur, belediyenin Uzunkum'daki bisiklet ve yürüyüş yoludur; piknik alanlarıyla birlikte ailelerin favorisidir. Sakarya Büyükşehir Belediyesi, göl çevresindeki bisiklet yolu ağını genişletmeye yönelik çalışmalar yürütüyor; güncel durumu belediyenin duyurularından takip edebilirsiniz. Kırkpınar'dan başlayan kısa sahil turları, kahvaltı sonrası bir saatlik yürüyüş için idealdir. Parkur ayrıntıları <a href="/blog/sapanca-bisiklet-yuruyus-parkurlari/">bisiklet ve yürüyüş parkurları</a> yazımızda.</p>
<h2>Sapanca Gölü'nde kuş gözlemi</h2>
<p>Göl, su kuşları için önemli bir yaşam alanıdır. Wikipedia'da gölde görülen türler arasında küresel ölçekte koruma statüsü olan <strong>pasbaş patka</strong> (Ferruginous duck, "neredeyse tehdit altında") ve <strong>dikkuyruk</strong> (White-headed duck, "tehlike altında") sayılıyor. Sabahın ilk saatlerinde, sazlıkların olduğu sakin kıyılarda dürbünle bekleyen biri için göl bambaşka bir yüzünü gösterir. Kuş gözlemi meraklıları için <a href="/blog/acarlar-longozu-rehberi/">Acarlar Longozu</a> da yarım günlük güzel bir ektir.</p>
""" + fig("/assets/web/editorial/ONN09461","DİDİ Otel Sapanca'da açık havuz, şemsiyeli şezlonglar ve palmiyeler, önde begonvil çiçekleri","Göl gününün ardından: sezonda Sapanca'nın tek klorsuz havuzunda serinlemek.") + """
<h2>Göle saygı: içme suyu kaynağında nelere dikkat edilmeli?</h2>
<p>Sapanca Gölü, Sakarya'nın içme suyunun büyük bölümünü karşılar ve Kocaeli'ye de su verir. Son yıllarda kuraklık nedeniyle su seviyesi düştü; SASKİ kıyıdaki kaçak iskele ve yapıları kaldırma, kıyı temizliği ve bilim kurulu eşliğinde koruma çalışmaları yürütüyor. Ziyaretçi olarak yapabileceklerimiz basit:</p>
<ul>
<li>Kıyıda çöp bırakmayın; mangal ve ateş için yalnızca belirlenmiş alanları kullanın.</li>
<li>Göle sabun, şampuan ya da kimyasal karıştıracak hiçbir şey yapmayın.</li>
<li>Sazlık ve kuş yuvalama alanlarına yaklaşmayın.</li>
</ul>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="ilk">İlkbahar</button><button data-tab="yaz">Yaz</button><button data-tab="son">Sonbahar–kış</button></div>
<div class="itin-panel on" data-tab="ilk"><p>Bisiklet ve kuş gözlemi için en iyi dönem. Kıyılar yeşil, hava serin.</p></div>
<div class="itin-panel" data-tab="yaz"><p>SUP ve gün batımı sezonu. Rüzgârsız sabahları seçin; öğle sıcağında gölgede kalın. Ayrıntılar <a href="/blog/sapancada-yazin-yapilacaklar/">yazın yapılacaklar</a> rehberinde.</p></div>
<div class="itin-panel" data-tab="son"><p>Sakin göl, sisli sabahlar ve renkli ormanlar. Yürüyüş ve fotoğraf için harika; suya çıkmak için hava çoğu zaman fazla serin ve rüzgârlı. <a href="/blog/sapancada-sonbahar-rehberi/">Sonbahar rehberi</a></p></div>
</div>
<h2>Göl aktivitesi kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="gol-aktivite">
<label><input type="checkbox"><span><b>Rüzgâr ve hava tahmini</b><span>Suya çıkmadan önce mutlaka bakın.</span></span></label>
<label><input type="checkbox"><span><b>Can yeleği</b><span>SUP ve teknede pazarlıksız.</span></span></label>
<label><input type="checkbox"><span><b>Şarjlı telefon</b><span>Su geçirmez kılıfla.</span></span></label>
<label><input type="checkbox"><span><b>Güneş koruması ve su</b><span>Yazın gölde güneş yansıması güçlüdür.</span></span></label>
<label><input type="checkbox"><span><b>Çöpünüzü geri getirin</b><span>Göl bir içme suyu kaynağı.</span></span></label>
</div>
<h2>Göl gününden sonra nerede dinlenilir?</h2>
<p>Gölün güney kıyısındaki Kırkpınar'da yer alan <a href="/#konum">DİDİ Otel Sapanca</a>, sahile ve teleferiğe kısa mesafededir. Havuz sezonunda Sapanca'nın tek klorsuz havuzu, bahçede cabanalar ve akşam <a href="/#mare">Mare Gastro</a> ile göl gününü tamamlayabilirsiniz. Müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%20G%C3%B6l%C3%BC%20gezisi%20i%C3%A7in%20konaklama%20yapmak%20istiyorum.">WhatsApp'tan</a> yazın ya da <a href="/odalar/">odaları inceleyin</a>.</p>
""",
 "sources":[("Lake Sapanca — ölçüler, su kullanımı ve kuş türleri (Wikipedia)","https://en.wikipedia.org/wiki/Lake_Sapanca"),
            ("Sapanca Gölü'nde popülerleşen spor dalı: SUP (DHA, 02.07.2026)","https://www.dha.com.tr/foto-galeri/sapanca-golunde-populerlesen-spor-dali-sup-2902453"),
            ("Sapanca Gölü'nde fırtınaya yakalanan 35 kişi kurtarıldı (GZT, 23.07.2026)","https://www.gzt.com/gundem/sapanca-golunde-firtinaya-yakalanan-35-kisi-afad-ekiplerince-kurtarildi-4243982"),
            ("Sapanca Gölü'nde 2 saatte 17 kişi boğulmaktan kurtarıldı (Hürriyet, 06.07.2025)","https://www.hurriyet.com.tr/gundem/sapanca-golunde-2-saatte-17-kisi-bogulmaktan-kurtarildi-42867077"),
            ("Sapanca Gölü kıyılarında kaçak iskele kaldırma süreci (Sakarya Büyükşehir Belediyesi)","https://sakarya.bel.tr/tr/Haber/sapanca-golunun-kiyilarinda-kacak-iskele-kaldirma-surecinin-ikinci-etabi-basladi/26199")],
 "faq":[("Sapanca Gölü'nde ne yapılır?","Kıyı yürüyüşü, Uzunkum ve çevresinde bisiklet, SUP, kuş gözlemi, gün batımı fotoğrafı ve Kırkpınar'dan kalkan teleferikle göle kuşbakışı bakmak en sevilen aktivitelerdir."),
        ("Sapanca Gölü'nün çevresi kaç km?","Göl doğu–batı yönünde yaklaşık 16 km uzunluğunda ve 45 km² yüzölçümündedir. Çevresini karayoluyla dolaşan bisiklet rotaları seçilen yola göre 45–50 km'yi bulur."),
        ("Sapanca Gölü'nde SUP yapılabilir mi?","Evet, SUP gölde giderek yaygınlaşıyor. Can yeleği giymek şarttır ve rüzgârlı havada göle açılmamak gerekir; 2025 ve 2026 yazlarında ani rüzgârda kurtarma operasyonları yapıldı."),
        ("Sapanca Gölü'nde bisiklet nerede sürülür?","En düzenli parkur Uzunkum'daki belediye bisiklet ve yürüyüş yoludur; Kırkpınar ve merkez sahilde kısa turlar da yapılabilir."),
        ("Sapanca Gölü'nde hangi kuşlar görülür?","Göl su kuşları için önemli bir yaşam alanıdır; koruma statüsündeki pasbaş patka ve dikkuyruk da gölde kaydedilen türler arasındadır."),
        ("Göl aktiviteleri için en iyi mevsim hangisi?","Bisiklet ve kuş gözlemi için ilkbahar ve sonbahar, SUP ve gün batımı için yaz aylarının rüzgârsız sabahları en uygun zamanlardır.")],
},
{
 "slug":"sapancada-kahvalti-ve-yemek","cat":"Lezzet","img":"kahvalti","date":"2026-07-09",
 "title":"Sapanca'da Kahvaltı ve Göl Manzaralı Yemek Keyfi",
 "desc":"Sapanca'da kahvaltı ve göl manzaralı yemek; zengin serpme kahvaltı ve bahçede Akdeniz mutfağı sunan Mare Gastro restoranı.",
 "lead":"Sapanca'da güne zengin bir serpme kahvaltıyla başlamak ve akşam göl havasında bir yemek yemek, bölgenin en sevilen deneyimlerindendir. DİDİ Otel bahçesindeki Mare Gastro, taze deniz ürünleri ve Akdeniz mutfağını zarif bir atmosferde sunar.",
 "body":"""
<h2>Zengin serpme kahvaltı</h2>
<p>Sapanca kahvaltısı, yöresel lezzetlerle donatılan zengin bir sofra anlamına gelir. DİDİ Otel'de konaklamaya kahvaltı dahildir; kahvaltı Mare Gastro'da tabak kahvaltı olarak servis edilir, <strong>serpme kahvaltı</strong> ise fiyat farkıyla sunulur; güne göl havasında keyifli bir başlangıç yapılır.</p>
<h2>Mare Gastro: bahçede Akdeniz sofrası</h2>
<p>Otelin bahçesindeki <a href="/#mare"><strong>Mare Gastro</strong></a>, taze deniz ürünleri ve Akdeniz mutfağının seçkin lezzetlerini sunar. Havuz kenarındaki masalar ve göl havası, akşam yemeğini keyifli bir deneyime dönüştürür.</p>
<h2>Akşam yemeği için ipuçları</h2>
<ul>
<li>Gün batımı saatleri bahçe terasında en keyiflisidir</li>
<li>Deniz ürünleri ve Akdeniz lezzetleri öne çıkar</li>
<li>Rezervasyonla yerinizi önceden ayırtabilirsiniz</li>
</ul>
<p>Mare Gastro'da yer ayırtmak için <a href="https://wa.me/905331350888?text=Mare%20Gastro%20rezervasyonu%20yapmak%20istiyorum.">WhatsApp'tan</a> ulaşabilirsiniz.</p>
""",
 "faq":[("DİDİ Otel'de kahvaltı dahil mi?","Evet, tüm konaklamalara tabak kahvaltı dahildir; kahvaltı otel bahçesindeki Mare Gastro'da servis edilir. Serpme kahvaltı isteyen misafirlerimize fiyat farkıyla sunulur."),
        ("Mare Gastro nerede?","Mare Gastro, DİDİ Otel'in bahçesindedir ve göl havasında Akdeniz mutfağı sunar."),
        ("Restoran rezervasyonu gerekiyor mu?","Yoğun dönemlerde yerinizi güvence altına almak için rezervasyon önerilir; WhatsApp'tan ayırtabilirsiniz.")],
},
{
 "slug":"kirkpinar-sapanca-konaklama","cat":"Konaklama","img":"lobi","date":"2026-07-10",
 "title":"Kırkpınar Sapanca: Sessiz ve Doğa İçinde Konaklama Rehberi",
 "desc":"Kırkpınar Sapanca konaklama rehberi; Sapanca Gölü kıyısındaki sessiz mahalle, göl-dağ manzarası ve butik otel konforu.",
 "lead":"Kırkpınar, Sapanca Gölü kıyısındaki sessiz ve doğa içindeki mahallelerden biridir. Kalabalıktan uzak, göl ve dağ manzarasına açılan konumuyla huzurlu bir konaklama arayanlar için idealdir.",
 "body":"""
<h2>Kırkpınar nerede?</h2>
<p><strong>Kırkpınar</strong>, Sapanca Gölü kıyısında, ilçenin en nezih bölgelerinden biridir. İstanbul-Ankara otoyoluna yakınlığı sayesinde ulaşımı kolay; buna rağmen doğayla iç içe ve sakindir.</p>
<h2>Neden Kırkpınar'da konaklamalı?</h2>
<ul>
<li>Göl ve dağ manzarası</li>
<li>Kalabalıktan uzak, sessiz atmosfer</li>
<li>Otoyola 500 metre, merkeze 3 kilometre yakınlık</li>
<li>Maşukiye ve Kartepe gibi noktalara kısa mesafe</li>
</ul>
<h2>Butik otel konforu</h2>
<p><a href="/#odalar">DİDİ Otel Sapanca</a>, Kırkpınar'da açık havuz, geniş bahçe, konaklamaya dahil kahvaltı ve <a href="/#mare">Mare Gastro</a> restoranıyla konforlu bir konaklama sunar. Suit odalardan aile odalarına kadar farklı ihtiyaçlara uygun seçenekler bulunur.</p>
<blockquote>Her şeye yakın, gürültüden uzak.</blockquote>
""",
 "faq":[("Kırkpınar Sapanca'nın neresinde?","Kırkpınar, Sapanca Gölü kıyısında, ilçenin en nezih ve sakin bölgelerinden biridir."),
        ("Kırkpınar otoyola yakın mı?","Evet, İstanbul-Ankara otoyolu Sapanca gişelerine yaklaşık 500 metre mesafededir."),
        ("Kırkpınar'da hangi olanaklar var?","DİDİ Otel Sapanca; açık havuz, geniş bahçe, serpme kahvaltı ve Mare Gastro restoranı gibi olanaklar sunar.")],
},
{
 "slug":"sapancada-havuzlu-otel","cat":"Olanaklar","img":"ONN09461","date":"2026-07-11",
 "title":"Sapanca'da Havuzlu Otel Keyfi: Yazın Serinleme Rehberi",
 "desc":"Sapanca'da havuzlu otel; sezonluk açık havuz, bahçe cabanaları ve şezlonglar ile yaz aylarında doğa içinde serinleme keyfi.",
 "lead":"Sapanca'da havuzlu bir otel, yaz aylarında doğa içinde serinlemenin en keyifli yoludur. DİDİ Otel'in sezonluk açık havuzu, begonvillerle çevrili bahçesi ve şezlonglarıyla gün boyu dinlenmek için idealdir.",
 "body":"""
<h2>Sezonluk açık havuz</h2>
<p>DİDİ Otel'in <strong>açık havuzu</strong>, sıcak yaz günlerinde göl havası eşliğinde serinlemek için idealdir. Havuz çevresindeki şezlonglar ve bahçe gölgesi, gün boyu konforlu bir dinlenme sunar.</p>
<h2>Bahçe ve cabanalar</h2>
<p>Beyaz perdeli bahçe cabanaları, gölgeli ve özel dinlenme köşeleridir. Begonvillerle çevrili bahçe, doğayla iç içe huzurlu bir atmosfer yaratır.</p>
<h2>Havuz keyfini tamamlayan olanaklar</h2>
<ul>
<li>Sabah zengin serpme kahvaltı</li>
<li>Havuz kenarında gün boyu dinlenme</li>
<li>Akşam <a href="/#mare">Mare Gastro</a>'da göl havasında yemek</li>
</ul>
<p>Yaz döneminde havuzlu konforlu bir konaklama için <a href="/#odalar">odalarımızı inceleyin</a> ve doğrudan rezervasyonla en avantajlı fiyattan yararlanın.</p>
""",
 "faq":[("DİDİ Otel'in havuzu var mı?","Evet, sezonluk açık havuz tüm misafirlerin kullanımına açıktır."),
        ("Havuz hangi aylarda açık?","Açık havuz sezonluk olup yaz aylarında hizmet verir."),
        ("Bahçede dinlenme alanı var mı?","Evet, begonvillerle çevrili bahçede beyaz perdeli cabanalar ve şezlonglar bulunur.")],
},
{
 "slug":"sapancada-balayi-ozel-gunler","cat":"Özel Günler","img":"mare-ic","date":"2026-07-12",
 "title":"Sapanca'da Balayı ve Özel Günler İçin Konaklama",
 "desc":"Sapanca'da balayı ve özel günler için konaklama; göl manzaralı suit odalar, sakin doğa ve göl havasında akşam yemeği.",
 "lead":"Sapanca, göl ve orman manzarası, sakin atmosferi ve göl havasında akşam yemeği seçenekleriyle balayı ve özel günler için huzurlu bir seçenektir. Geniş suit odalar ve doğayla iç içe bir dinlenme, anı unutulmaz kılar.",
 "body":"""
<h2>Balayı için Sapanca</h2>
<p>Kalabalıktan uzak, doğayla iç içe ve sakin bir ortam; balayı için önemli bir tercih sebebidir. Sapanca'nın göl ve dağ manzarası, çift için huzurlu ve romantik bir başlangıç sunar.</p>
<h2>Özel günler için oda önerisi</h2>
<p>Geniş ve zarif <a href="/odalar/king-suit/">King Suit</a> ve <a href="/odalar/junior-suit/">Junior Suit</a> odaları, balayı, yıldönümü ve doğum günü gibi özel günler için idealdir.</p>
<h2>Anıyı tamamlayan detaylar</h2>
<ul>
<li>Göl manzarasına uyanmak</li>
<li>Bahçede, göl havasında akşam yemeği (<a href="/#mare">Mare Gastro</a>)</li>
<li>Havuz ve bahçede sakin bir dinlenme</li>
</ul>
<p>Özel gününüz için taleplerinizi <a href="https://wa.me/905331350888">WhatsApp'tan</a> paylaşabilir, planınızı birlikte oluşturabiliriz.</p>
""",
 "faq":[("Sapanca balayı için uygun mu?","Evet. Sakin doğası, göl manzarası ve romantik atmosferiyle Sapanca balayı için huzurlu bir seçenektir."),
        ("Balayı için hangi oda önerilir?","Geniş ve zarif King Suit veya Junior Suit odaları özel günler için idealdir."),
        ("Özel gün için talepte bulunabilir miyim?","Evet, özel gün taleplerinizi WhatsApp üzerinden paylaşabilirsiniz.")],
},
{
 "slug":"didi-otel-nereden-rezervasyon-yapilir","cat":"Rezervasyon","img":"dis-cephe","date":"2026-07-14",
 "title":"DİDİ Otel Sapanca'da Nereden Rezervasyon Yapılır?",
 "desc":"DİDİ Otel Sapanca; Etstur, Tatilbudur, Otelz, Airbnb gibi kanallarda listelenir. Hangi kanaldan rezervasyon yapmalısınız ve doğrudan rezervasyonun farkı nedir?",
 "lead":"DİDİ Otel Sapanca'yı ararken karşınıza birden fazla platform çıkabilir. Hangisinin güncel, hangisinin avantajlı olduğunu bilmek fiyat ve müsaitlik konusunda zaman kazandırır.",
 "body":"""
<h2>DİDİ Otel Sapanca'yı nerede bulabilirsiniz?</h2>
<p>DİDİ Otel Sapanca, kendi web sitesinin yanı sıra <strong>Etstur, Tatilbudur, Otelz, Enuygun, Airbnb, Trivago, Expedia</strong> ve <strong>Kayak</strong> gibi platformlarda da listelenir. TripAdvisor üzerinden de fiyat karşılaştırması yapılabilir. Bu kanalların her biri farklı bir kitleye ulaşır, ama hepsinde geçerli tek kural şudur: en güncel fiyat ve müsaitlik bilgisi doğrudan otelden alınır.</p>
<h2>Booking.com'da arıyorsanız</h2>
<p>Sık karşılaştığımız bir soru: "DİDİ Otel Sapanca Booking.com'da var mı?" Şu an için hayır — otel bu platform üzerinden satışa açık değil. Booking.com'da arayıp bulamayan misafirlerimiz, aşağıdaki kanallardan biri ya da doğrudan WhatsApp üzerinden rezervasyon yapabilir.</p>
<h2>Kanal karşılaştırması</h2>
<table><thead><tr><th>Kanal</th><th>Ne zaman tercih edilir</th></tr></thead><tbody>
<tr><td>Doğrudan (WhatsApp/telefon)</td><td>En iyi fiyat garantisi, komisyonsuz, anında onay</td></tr>
<tr><td>Etstur, Tatilbudur, Otelz, Enuygun</td><td>Taksit seçenekleri, kampanya kodları</td></tr>
<tr><td>Airbnb</td><td>Oda bazlı arama ve platform içi mesajlaşma alışkanlığı</td></tr>
<tr><td>Trivago, Expedia, Kayak, TripAdvisor</td><td>Fiyat karşılaştırma, uluslararası misafirler</td></tr>
</tbody></table>
<h2>Neden doğrudan rezervasyon daha avantajlı?</h2>
<p>Online seyahat acenteleri, otellerden konaklama başına genellikle %15 ile %30 arasında değişen bir komisyon alır. Bu maliyet er ya da geç fiyata yansır. DİDİ Otel Sapanca'da <strong>doğrudan WhatsApp üzerinden</strong> yapılan rezervasyonlarda aracı komisyonu olmadığı için en iyi fiyat garantisi uygulanır; ayrıca oda tercihi, geç check-out veya özel gün talebi gibi konularda doğrudan otelle konuşmuş olursunuz.</p>
<h2>Nasıl doğrudan rezervasyon yapılır?</h2>
<p>Anasayfadaki <a href="/#rezervasyon">rezervasyon adımlarını</a> kullanarak tarih, oda tipi ve misafir sayınızı seçip son adımda WhatsApp üzerinden anında onay alabilirsiniz. Dilerseniz doğrudan <a href="tel:+902645921212">0264 592 12 12</a> numaralı hattı da arayabilirsiniz.</p>
""",
 "faq":[("DİDİ Otel Sapanca Booking.com'da mı?","Hayır, otel şu an Booking.com üzerinden satışa açık değildir. Etstur, Tatilbudur, Otelz, Airbnb, Trivago, Expedia, Kayak veya doğrudan WhatsApp üzerinden rezervasyon yapılabilir."),
        ("Hangi platformlardan rezervasyon yapılabilir?","Etstur, Tatilbudur, Otelz, Enuygun, Airbnb, Trivago, Expedia ve Kayak'ta listelenir; en güncel fiyat için doğrudan otel önerilir."),
        ("Doğrudan rezervasyon neden daha avantajlı?","Aracı komisyonu olmadığı için en iyi fiyat garantisi uygulanır ve oda/tarih tercihleriniz doğrudan otelle netleşir."),
        ("Rezervasyon değişikliği nasıl yapılır?","WhatsApp (0533 135 08 88) veya telefonla (0264 592 12 12) otelle doğrudan iletişime geçebilirsiniz.")],
},
{
 "slug":"didi-otel-sapanca-misafir-yorumlari","cat":"Misafir Deneyimi","img":"resepsiyon1","date":"2026-07-15",
 "title":"DİDİ Otel Sapanca Yorumları: Misafirler Ne Diyor?",
 "desc":"TripAdvisor ve Google'daki gerçek misafir yorumlarına göre DİDİ Otel Sapanca'nın öne çıkan artıları ve rezervasyon öncesi dikkat edilmesi gereken noktalar.",
 "lead":"Bir oteli seçmeden önce oradan geçmiş misafirlerin ne dediğine bakmak en doğal adımdır. TripAdvisor ve Google Haritalar'daki yorumlar, DİDİ Otel Sapanca hakkında oldukça tutarlı bir tablo çiziyor.",
 "body":"""
<h2>Genel puan ve izlenim</h2>
<p>DİDİ Otel Sapanca, TripAdvisor'da ortalama <strong>4/5</strong> puanla değerlendiriliyor ve Sapanca'daki oteller arasında istikrarlı bir sırada yer alıyor. Google Haritalar ve rezervasyon platformlarındaki yorumlar da benzer bir görünüm sunuyor: temiz odalar, ilgili personel ve göle yakın sakin bir konum.</p>
<h2>Misafirlerin en çok övdüğü noktalar</h2>
<ul>
<li><strong>Temizlik</strong> — oda ve ortak alanların temizliği hemen her yorumda öne çıkıyor.</li>
<li><strong>Personel ilgisi</strong> — resepsiyon ve servis ekibinin sıcak, yardımsever tutumu sık sık vurgulanıyor.</li>
<li><strong>Konum</strong> — Sapanca Gölü'ne yürüme mesafesi ve Kırkpınar'ın sakin dokusu beğeniliyor.</li>
<li><strong>Kahvaltı</strong> — zengin serpme kahvaltı, güne iyi bir başlangıç olarak anılıyor.</li>
</ul>
<h2>Dürüst olalım: nelere dikkat etmeli</h2>
<p>Otelin ana cadde üzerindeki konumu, bazı yorumlara yol trafiği sesi olarak yansımış. Sessizliğe önem veren misafirler, rezervasyon sırasında bahçeye veya havuza bakan bir oda talep edebilir — bu tercihinizi WhatsApp'tan rezervasyon yaparken belirtmeniz yeterli.</p>
<h2>Güncel yorumları nereden okuyabilirsiniz?</h2>
<p>Doğrulanmış ve güncel misafir yorumlarına <a href="https://www.tripadvisor.com/Hotel_Review-g612463-d4068817-Reviews-Didi_Otel_Sapanca-Sapanca_Sakarya_Province.html" target="_blank" rel="noopener">TripAdvisor</a> ve Google Haritalar üzerinden ulaşabilirsiniz. Siz de konaklamanızın ardından deneyiminizi paylaşarak sonraki misafirlere yol gösterebilirsiniz.</p>
""",
 "faq":[("DİDİ Otel Sapanca'nın puanı kaç?","TripAdvisor'da ortalama 4/5 civarındadır; Sapanca'daki oteller arasında istikrarlı bir sırada yer alır."),
        ("En çok hangi konular övülüyor?","Temizlik, personel ilgisi, göle yakın sakin konum ve zengin kahvaltı öne çıkan konulardır."),
        ("Odalarda gürültü oluyor mu?","Bazı misafirler ana cadde trafiğinden söz etmiştir; bahçeye veya havuza bakan odalar daha sessizdir, rezervasyonda talep edilebilir."),
        ("Güncel yorumları nereden okuyabilirim?","TripAdvisor ve Google Haritalar üzerindeki DİDİ Otel Sapanca sayfalarından güncel yorumlara ulaşabilirsiniz.")],
},
{
 "slug":"sapanca-teleferik-rehberi","cat":"Teleferik","img":"ONN09422","date":"2026-08-13","mod":"2026-11-16",
 "title":"Sapanca Teleferik Rehberi: Bilet Fiyatı, Saatler ve Kırkpınar'dan Kalkan Hat",
 "seo_title":"Sapanca Teleferik 2026: Fiyat, Saatler ve Ulaşım",
 "img_alt":"DİDİ Otel Sapanca binası ve önündeki turkuaz havuz, palmiyeler ve bulutlu mavi gökyüzü",
 "desc":"Sapanca Teleferik bilet fiyatı (tam 450 TL, öğrenci 300 TL), 11:00–19:00 saatleri, Kırkpınar'dan 1.501 m'lik hat ve üst istasyonda zipline, ATV.",
 "related":["sapanca-macera-parki-zipline","sapancada-gezilecek-yerler","sapancada-fotograf-gun-batimi-noktalari"],
 "lead":"Sapanca Teleferik, Kırkpınar'daki alt istasyondan Mahmudiye yönündeki üst istasyona çıkan <strong>1.501 metrelik</strong> bir hattır ve gölü kuşbakışı izletir. İşletmenin resmi fiyat tarifesine göre (16 Kasım 2026'da kontrol edildi) <strong>tam bilet gidiş-dönüş 450 TL, öğrenci bileti 300 TL</strong>; tesis her gün <strong>11:00–19:00</strong> arasında açık. Biletler yalnızca gişede satılıyor, online satış yok. Üst istasyonda zipline, ATV safari ve yürüyüş parkurları bulunuyor.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Hat:</strong> 1.501 m uzunluk, 319 m yükseklik farkı, 36 kabin (8 kişilik).</li>
<li><strong>Fiyat:</strong> Tam 450 TL, öğrenci 300 TL (gidiş-dönüş). Tek yön bilet de satılır.</li>
<li><strong>Saat:</strong> Her gün 11:00–19:00. <strong>Telefon:</strong> 444 6 345.</li>
<li><strong>Adres:</strong> Kırkpınar Hasanpaşa, Şehit Cevdet Koç Caddesi No:78, Sapanca.</li>
</ul></div>
<h2>Sapanca Teleferik nereden nereye gidiyor?</h2>
<p><strong>Sapanca Teleferik</strong>, gölün güney kıyısındaki Kırkpınar'dan başlayıp Samanlı Dağları'nın eteğinde Mahmudiye yönüne yükselir. Hattı kuran Leitner'in referans sayfasına göre sistem 2023'te hizmete girdi; hat uzunluğu 1.501 metre, iki istasyon arasındaki yükseklik farkı 319 metre. 9 direk üzerinde 36 kabin çalışır, her kabin 8 kişiliktir ve sistemin taşıma kapasitesi saatte 1.513 yolcudur.</p>
<p>Kabinler saniyede 5 metre hızla ilerler; bu hızla 1.501 metre yaklaşık 5 dakikada alınır. Biniş-iniş ve istasyon yavaşlamalarıyla birlikte tek yön yolculuk birkaç dakika daha uzun sürer. Yukarı çıkarken arkanızda kalan göl manzarası için kabinin göle bakan tarafına oturun.</p>
<h2>Sapanca Teleferik bilet fiyatı ne kadar?</h2>
<table><thead><tr><th>Bilet / koşul</th><th>Resmi tarifedeki bilgi</th></tr></thead><tbody>
<tr><td>Tam bilet (gidiş-dönüş)</td><td>450 TL</td></tr>
<tr><td>Öğrenci bileti (gidiş-dönüş)</td><td>300 TL — geçerli öğrenci kimliği ile</td></tr>
<tr><td>Tek yön</td><td>Tek yön kullanım için ayrı bilet satılır</td></tr>
<tr><td>Ücretsiz</td><td>Gaziler, gazi eşleri ve birinci derece şehit yakınları</td></tr>
<tr><td>Çocuklar</td><td>Tarifede 2020 ve sonrası doğumlular ayrıca belirtilmiş; güncel uygulamayı gişede sorun</td></tr>
<tr><td>Bisiklet</td><td>Kişi biletine ek olarak bisiklet için ayrı ücret alınır</td></tr>
<tr><td>Satış ve geçerlilik</td><td>Yalnızca gişede; online satış yok; bilet alındığı gün boyunca geçerli</td></tr>
</tbody></table>
<p class="note">Fiyatlar ve koşullar Sapanca Teleferik'in resmi fiyat tarifesi sayfasından 16 Kasım 2026'da alınmıştır. İşletme fiyatları dönem dönem güncelleyebilir; grup fiyatları için işletmeyle iletişime geçin.</p>
<h3>Fiyat geçmişi neden önemli?</h3>
<p>Teleferik bilet fiyatı 2023'teki açılıştan bu yana birkaç kez güncellendi; internette hâlâ eski fiyatları gösteren sayfalar dolaşıyor. Bu yüzden yalnızca işletmenin kendi sayfasındaki tarifeye güvenmenizi ve büyük bir grupla gidecekseniz önceden aramanızı öneririz.</p>
<h2>Teleferik hangi saatlerde çalışıyor?</h2>
<p>Resmi siteye göre tesis her gün <strong>11:00–19:00</strong> arasında hizmet veriyor. Teleferikler güçlü rüzgârda güvenlik nedeniyle durdurulabilir; özellikle kış aylarında ve fırtına uyarısı olan günlerde yola çıkmadan önce <strong>444 6 345</strong>'i aramak, boşuna gitmenizi önler. Hafta sonu öğleden sonra gişe önünde sıra oluşabilir; açılışa yakın saatlerde gitmek genellikle daha rahattır.</p>
<h2>Üst istasyonda neler var?</h2>
<p>İşletmenin sitesinde üst istasyon alanının olanakları şöyle sıralanıyor: <strong>zipline</strong>, <strong>ATV safari</strong>, <strong>trekking</strong> parkurları, <strong>bungalov</strong> konaklama ve göl manzaralı <strong>kafe-restoran</strong>. Zipline ve ATV ücretleri teleferik biletine dahil değildir. Macera aktivitelerinin ayrıntılarını <a href="/blog/sapanca-macera-parki-zipline/">Sapanca zipline ve ATV rehberimizde</a> anlattık. Mahmudiye tarafının köy dokusu ve pazarları için <a href="/blog/poyrazlar-golu-mahmudiye-gizli-koseler/">Mahmudiye ve gizli köşeler</a> yazımıza bakabilirsiniz.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="yaz">İlkbahar–yaz</button><button data-tab="son">Sonbahar</button><button data-tab="kis">Kış</button></div>
<div class="itin-panel on" data-tab="yaz"><p>Orman yemyeşil, göl parlak. Öğle sıcağından kaçmak için 11:00'deki açılışta binip üstte yürüyüş yapın. Gün batımı haziranda 20:30 civarında olduğu için yaz aylarında kapanıştan önce gün batımını kabinden göremezsiniz; ışık yine de akşamüstü en yumuşak halindedir.</p></div>
<div class="itin-panel" data-tab="son"><p>Ekim sonundan itibaren ormanlar sararıp kızarır; renkli yamaçların üzerinden süzülmek için en güzel dönem budur. Kasımda gün batımı 17:40 civarına çekildiği için kapanıştan önce batan güneşi yukarıdan izleyebilirsiniz. Ayrıntılar <a href="/blog/sapancada-sonbahar-rehberi/">sonbahar rehberimizde</a>.</p></div>
<div class="itin-panel" data-tab="kis"><p>Karlı günlerde Samanlı Dağları'nın zirveleri ve sisli göl ayrı bir manzara sunar. Rüzgâr nedeniyle sefer durdurulabileceğinden mutlaka önceden arayın; kalın bir mont alın.</p></div>
</div>
""" + fig("/assets/web/editorial/ONN09451","DİDİ Otel Sapanca bahçesinde palmiyeler ve çiçeklerle çevrili, havuza uzanan yürüyüş yolu","Teleferiğin alt istasyonuyla aynı mahallede: DİDİ Otel'in Kırkpınar'daki bahçesi.") + """
<h2>DİDİ Otel'den teleferiğe nasıl gidilir?</h2>
<p>Teleferiğin alt istasyonu, <a href="/#konum">DİDİ Otel Sapanca</a>'nın da bulunduğu Kırkpınar Hasanpaşa'dadır; otelden kısa bir mesafede, araçla birkaç dakikalık yoldur. Kahvaltıdan sonra 11:00'deki açılışa yetişip öğlene kadar üst istasyonda vakit geçirebilir, öğleden sonrayı göl kıyısında ya da sezonda havuzda tamamlayabilirsiniz. Akşam için bahçedeki <a href="/#mare">Mare Gastro</a> sizi dışarı çıkmadan ağırlar. Tam yol tarifini resepsiyonumuzdan alabilirsiniz.</p>
<h2>Teleferik günü için örnek plan</h2>
<table><thead><tr><th>Saat</th><th>Plan</th></tr></thead><tbody>
<tr><td>09:00</td><td>Otelde kahvaltı</td></tr>
<tr><td>11:00</td><td>Teleferik açılışı — sırasız biniş</td></tr>
<tr><td>11:15–13:30</td><td>Üst istasyonda yürüyüş, isteyene zipline / ATV</td></tr>
<tr><td>14:00</td><td>Maşukiye'de dere kenarında öğle yemeği (~15 dk)</td></tr>
<tr><td>17:00</td><td>Göl kıyısında gün batımı yürüyüşü</td></tr>
<tr><td>19:30</td><td>Mare Gastro'da akşam yemeği</td></tr>
</tbody></table>
<h3>Ziyaret ipuçları</h3>
<ul>
<li>Bilet yalnızca gişede satılır; yanınızda kart ya da nakit bulundurun.</li>
<li>Öğrenciyseniz o yıla ait vizeli öğrenci kimliğinizi unutmayın.</li>
<li>Üst istasyonda hava aşağıdan daha serin ve rüzgârlıdır; ince bir mont alın.</li>
<li>Bisikletle çıkacaksanız ek ücreti ve kabine alım koşullarını gişede sorun.</li>
</ul>
<p>Gezinin geri kalanını planlamak için <a href="/blog/sapancada-gezilecek-yerler/">Sapanca'da gezilecek yerler</a> rehberimize, konaklama için <a href="/odalar/">oda seçeneklerimize</a> göz atın ya da <a href="https://wa.me/905331350888?text=Merhaba%2C%20teleferik%20gezisi%20i%C3%A7in%20Sapanca%27da%20konaklama%20yapmak%20istiyorum.">WhatsApp'tan</a> müsaitlik sorun.</p>
""",
 "sources":[("Sapanca Teleferik — fiyat tarifesi (resmi site, 16.11.2026'da kontrol edildi)","https://sapancateleferik.com.tr/fiyat-tarifesi"),
            ("Sapanca Teleferik — ana sayfa, çalışma saatleri ve iletişim","https://sapancateleferik.com.tr/"),
            ("Leitner — GD8 Sapanca referans sayfası (teknik özellikler)","https://www.leitner.com/en/company/references/detail/gd8-sapanca/")],
 "faq":[("Sapanca Teleferik nereden kalkıyor?","Alt istasyon Kırkpınar Hasanpaşa'da, Şehit Cevdet Koç Caddesi No:78 adresindedir; hat Mahmudiye yönündeki üst istasyona çıkar. DİDİ Otel Sapanca da Kırkpınar'dadır."),
        ("Sapanca Teleferik bilet fiyatı ne kadar?","İşletmenin resmi tarifesine göre (16 Kasım 2026) tam bilet gidiş-dönüş 450 TL, öğrenci bileti 300 TL'dir. Gaziler, gazi eşleri ve birinci derece şehit yakınları ücretsizdir."),
        ("Sapanca Teleferik hangi saatlerde çalışıyor?","Resmi siteye göre her gün 11:00–19:00 arasında hizmet verir. Güçlü rüzgârda seferler durdurulabilir; gitmeden önce 444 6 345'i arayabilirsiniz."),
        ("Teleferik bileti online alınabilir mi?","Hayır. Resmi tarifeye göre online satış yoktur; biletler alt istasyondaki gişeden satılır ve alındığı gün boyunca geçerlidir."),
        ("Teleferik yolculuğu kaç dakika sürüyor?","Hat 1.501 metredir ve kabinler saniyede 5 metre hızla ilerler; saf yolculuk yaklaşık 5 dakikadır, biniş-iniş ile tek yön birkaç dakika daha uzun sürer."),
        ("Üst istasyonda ne var?","İşletmenin sitesine göre üst istasyonda zipline, ATV safari, trekking parkurları, bungalov ve göl manzaralı kafe-restoran bulunur. Bu aktiviteler teleferik biletine dahil değildir.")],
},
{
 "slug":"tarakli-geyve-gunubirlik-tur","cat":"Günübirlik","img":"ONN09440","date":"2026-08-14",
 "title":"Taraklı ve Geyve: Sapanca'dan Günübirlik Tarihi Kasaba Turu",
 "desc":"Sapanca'ya 45 dakika mesafedeki Taraklı'nın 700 yıllık çınarları, Osmanlı konakları ve Geyve'nin kiraz bahçeleri; günübirlik tarihi kasaba turu rehberi.",
 "lead":"Sapanca'ya araçla yaklaşık 45 dakika mesafedeki Taraklı, üç katlı Osmanlı konakları ve 700 yıllık çınar ağaçlarıyla zamanda geriye bir yolculuk sunar. Aynı günde Geyve'ye uğrayarak günübirlik bir tarih ve doğa rotası tamamlanabilir.",
 "body":"""
<h2>Taraklı nerede, Sapanca'ya ne kadar uzak?</h2>
<p><strong>Taraklı</strong>, Sapanca'ya karayoluyla yaklaşık <strong>45 dakika</strong> mesafededir. Sakarya'nın en iyi korunmuş tarihi kasabalarından biri olan Taraklı'da, 120 tescilli konağın yer aldığı bölge SİT alanı ilan edilmiştir.</p>
<h2>Taraklı'da görülmesi gerekenler</h2>
<p>Dar taş sokaklarda yürürken karşınıza çıkan üç katlı ahşap-kerpiç konaklar, Osmanlı şehir dokusunun günümüze kalan en canlı örneklerindendir. Kasabanın simgesi haline gelen 700 yıllık çınar ağaçları, meydanlarda gölge sağlar. Gezinin sonunda Taraklı'ya özgü <strong>uhut tatlısını</strong> denemeden dönmeyin.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="tarakli">Taraklı'da</button><button data-tab="geyve">Geyve'de</button></div>
<div class="itin-panel on" data-tab="tarakli"><p>Tescilli konaklar arasında yürüyüş, küçük el sanatları dükkanları, yöresel uhut tatlısı ve çınar ağaçlarının gölgesinde bir çay molası — Taraklı'nın klasik günübirlik programıdır.</p></div>
<div class="itin-panel" data-tab="geyve"><p>Taraklı'ya yaklaşık 15 dakika mesafedeki Geyve, özellikle ilkbahar ve yaz aylarında kiraz bahçeleriyle bilinir; Sakarya Nehri kıyısında kısa bir yürüyüş rotayı tamamlar.</p></div>
</div>
<h2>Günübirlik rota nasıl planlanır?</h2>
<table><thead><tr><th>Güzergah</th><th>Süre</th></tr></thead><tbody>
<tr><td>DİDİ Otel → Taraklı</td><td>~45 dk</td></tr>
<tr><td>Taraklı → Geyve</td><td>~15 dk</td></tr>
<tr><td>Geyve → DİDİ Otel (dönüş)</td><td>~35-45 dk</td></tr>
</tbody></table>
<p>Sabah erken bir kahvaltıyla yola çıkmak, her iki kasabayı da rahat bir tempoda gezip akşam üzeri Sapanca'ya dönmek için yeterli zamanı sağlar.</p>
<h2>Ne zaman gidilmeli?</h2>
<p>Geyve'nin kiraz bahçeleri için <strong>Nisan-Haziran</strong> arası, Taraklı'nın çınar ağaçlarının en gösterişli renklerini görmek için ise <strong>sonbahar</strong> ayları önerilir.</p>
<p>Erken çıkış için <a href="/#odalar">DİDİ Otel'de</a> zengin bir serpme kahvaltı yapıp yola çıkabilir, akşam dönüşünüzde <a href="/#mare">Mare Gastro</a>'da güne veda edebilirsiniz.</p>
""",
 "faq":[("Taraklı, Sapanca'ya kaç km / kaç dakika uzaklıkta?","Taraklı, Sapanca'ya karayoluyla yaklaşık 45 dakika mesafededir."),
        ("Taraklı'da ne yenir?","Kasabaya özgü uhut tatlısı ve yöresel ev yemekleri denenmesi gereken lezzetlerdir."),
        ("Geyve, Sapanca'ya uzak mı?","Geyve, Sapanca'ya yaklaşık 32-34 km ve 35-45 dakika mesafededir; Taraklı'ya ise yaklaşık 15 dakikadır."),
        ("Taraklı ve Geyve bir günde gezilir mi?","Evet, sabah erken bir çıkışla her iki kasaba da günübirlik olarak rahatça gezilebilir.")],
},
{
 "slug":"poyrazlar-golu-mahmudiye-gizli-koseler","cat":"Doğa","img":"ONN09442","date":"2026-08-15",
 "title":"Poyrazlar Gölü ve Mahmudiye: Sapanca'nın Gizli Kalmış Doğa Köşeleri",
 "desc":"Sapanca'ya yaklaşık 15 dakika mesafedeki Poyrazlar Gölü Tabiat Parkı ve Mahmudiye Mahallesi; kamp, ATV, tekne turu ve yöresel ürünlerle keşfedilecek sakin rotalar.",
 "lead":"Sapanca'nın en bilinen duraklarının biraz dışına çıkmak isteyenler için Poyrazlar Gölü ve Mahmudiye Mahallesi, kalabalıktan uzak, doğayla baş başa iki adres sunar. Poyrazlar Gölü Tabiat Parkı'nda kamp ve su aktiviteleri, Mahmudiye'de ise köy pazarları ve teleferik manzarası bir arada yaşanır.",
 "body":"""
<h2>Poyrazlar Gölü Tabiat Parkı</h2>
<p>2011 yılında tabiat parkı olarak tescillenen <strong>Poyrazlar Gölü</strong>, Adapazarı sınırları içinde, Sapanca'ya yaklaşık <strong>15 dakika</strong> mesafededir. Gölü ve ormanı bir arada sunan park, çadır ve karavan kampı için elverişli alanlarıyla özellikle Adapazarı ve İzmit'ten gelenlerin gözde mesire yeridir. Restoran ve büfe imkanlarının yanında kamp ateşi ve mangal serbesttir.</p>
<h2>Poyrazlar'da neler yapılır?</h2>
<p>Aşağıdaki listeden gezerken denemek istediklerinizi işaretleyin — ilerlemeniz tarayıcınızda kaydedilir.</p>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/7</b></div>
<div class="spot-check" data-key="poyrazlar">
<label><input type="checkbox"><span><b>Göl kıyısında kamp ateşi</b><span>Çadır veya karavanınızı kurup yıldızlar altında bir gece geçirin.</span></span></label>
<label><input type="checkbox"><span><b>ATV safari turu</b><span>Ormanlık patikalarda rehberli ATV turlarına katılın.</span></span></label>
<label><input type="checkbox"><span><b>Tekne ile göl turu</b><span>Suyun üzerinden gölü ve çevresini farklı bir açıdan görün.</span></span></label>
<label><input type="checkbox"><span><b>At sırtında göl çevresi</b><span>At binme alanında kısa bir tur yapın.</span></span></label>
<label><input type="checkbox"><span><b>Olta balıkçılığı</b><span>Sakin bir öğleden sonra için olta atın.</span></span></label>
<label><input type="checkbox"><span><b>Kuş gözlemi</b><span>Park sınırlarında 150'den fazla kuş türü yaşıyor.</span></span></label>
<label><input type="checkbox"><span><b>Piknik alanında mola</b><span>Gölge veren ağaçların altında bir piknik molası verin.</span></span></label>
</div>
<h2>Mahmudiye Mahallesi: köy pazarları ve teleferik manzarası</h2>
<p><strong>Mahmudiye</strong>, hem sakin bir köy dokusu hem de <a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a>'in üst istasyonuna ev sahipliği yapmasıyla dikkat çeker. Köyde kurulan küçük pazarlarda tarhana, köy peyniri, ceviz reçeli ve doğal zeytinyağı gibi ev yapımı ürünler bulunur.</p>
<h3>Mesafe özeti</h3>
<table><thead><tr><th>Nereden nereye</th><th>Süre</th></tr></thead><tbody>
<tr><td>DİDİ Otel → Poyrazlar Gölü</td><td>~15 dk</td></tr>
<tr><td>DİDİ Otel (Kırkpınar) → Mahmudiye</td><td>Teleferikle ~10 dk</td></tr>
</tbody></table>
<p>Gün boyu doğada geçirdiğiniz zamanın ardından <a href="/#odalar">DİDİ Otel'in</a> havuzunda dinlenip akşamı <a href="/#mare">Mare Gastro</a>'da tamamlayabilirsiniz.</p>
""",
 "faq":[("Poyrazlar Gölü nerede?","Adapazarı sınırları içinde, Sapanca'ya yaklaşık 15 dakika mesafededir."),
        ("Poyrazlar Gölü'nde kamp yapılabilir mi?","Evet, park içinde belirlenmiş alanlarda çadır ve karavan kampı yapılabilir."),
        ("Mahmudiye'de ne satın alınır?","Tarhana, köy peyniri, ceviz reçeli ve doğal zeytinyağı gibi ev yapımı ürünler bulunur."),
        ("Mahmudiye'ye nasıl gidilir?","Karayoluyla ya da Kırkpınar'dan kalkan Sapanca Teleferik ile ulaşılabilir.")],
},
{
 "slug":"sapancada-fotograf-gun-batimi-noktalari","cat":"Fotoğraf","img":"havuz-loca","date":"2026-08-16",
 "title":"Sapanca'da Fotoğraf ve Gün Batımı İçin En Güzel Noktalar",
 "desc":"Sapanca'da fotoğraf çekmek için en güzel noktalar; Uzunkum Parkı gün batımı, teleferik seyir terası, Maşukiye şelalesi ve DİDİ Otel bahçesi.",
 "lead":"Sapanca'yı kareye sığdırmak isteyenler için ilçenin en fotojenik noktaları göl kıyısından dağ zirvelerine kadar uzanır. İşte gün doğumundan gün batımına, Sapanca'da fotoğraf için en güzel köşeler.",
 "body":"""
<div class="spot-cards rev">
<div class="spot-card"><span class="tag">Gün batımı</span><h4>Uzunkum Parkı</h4><p>Göl kıyısındaki iskele ve ağaçlar, gün batımında altın rengine bürünür; Sapanca'nın en klasik karesidir.</p></div>
<div class="spot-card"><span class="tag">Kuşbakışı</span><h4>Teleferik seyir terası</h4><p>Mahmudiye'deki üst istasyonun terasından, tüm göl ve ormanın kuşbakışı görüntüsü çekilir.</p></div>
<div class="spot-card"><span class="tag">İlkbahar sabahı</span><h4>Maşukiye şelalesi</h4><p>Karların erimesiyle en coşkulu debisine ulaşan şelale, sabah ışığında uzun pozlama için idealdir.</p></div>
<div class="spot-card"><span class="tag">Kış / bulut denizi</span><h4>Kartepe zirvesi</h4><p>Kış aylarında bulutların üzerinde kalan zirve, dramatik manzara fotoğrafları için öne çıkar.</p></div>
<div class="spot-card"><span class="tag">Sabah / kuş gözlem</span><h4>Poyrazlar Gölü kıyısı</h4><p>Sisli sabahlarda göl yüzeyi ve kuş sürüleri, doğa fotoğrafçıları için sakin bir kare sunar.</p></div>
<div class="spot-card"><span class="tag">Altın saat</span><h4>DİDİ Otel bahçe ve havuz</h4><p>Begonvillerle çevrili bahçe ve havuz, akşamüzeri ışığında oteldeyken bile fotoğraf çekmenizi sağlar.</p></div>
</div>
<h2>Gün batımı için en iyi nokta: Uzunkum Parkı</h2>
<p>Sapanca Gölü kıyısındaki <strong>Uzunkum Parkı</strong>, güneşin gölün üzerine batışını izlemek için ilçenin en sevilen noktasıdır. Iskele, sandalyeler ve ağaçların silueti kareye derinlik katar.</p>
<h2>Kuşbakışı kareler için: teleferik seyir terası</h2>
<p><a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a> ile çıkılan Mahmudiye'deki seyir terası, gölü ve Kırkpınar'ı tepeden gösteren nadir bir açı sunar; öğleden sonra ışığı en net görüntüyü verir.</p>
<h3>En iyi çekim saatleri</h3>
<table><thead><tr><th>Nokta</th><th>Önerilen saat</th></tr></thead><tbody>
<tr><td>Uzunkum Parkı</td><td>Gün batımına ~1 saat kala</td></tr>
<tr><td>Teleferik seyir terası</td><td>Öğleden sonra, berrak havada</td></tr>
<tr><td>Maşukiye şelalesi</td><td>Sabah erken, ilkbahar</td></tr>
<tr><td>DİDİ Otel bahçe/havuz</td><td>Akşamüzeri altın saat</td></tr>
</tbody></table>
<p>Kareleri toplamaya otelden başlamak isterseniz, <a href="/#odalar">bahçe ve havuz alanı</a> günün her saatinde objektife hazırdır; akşam da <a href="/#mare">Mare Gastro</a>'nun ışıklı terası kendine has bir atmosfer sunar.</p>
""",
 "faq":[("Sapanca'da gün batımı nereden izlenir?","Göl kıyısındaki Uzunkum Parkı, gün batımını izlemek için ilçenin en bilinen noktasıdır."),
        ("Kuşbakışı Sapanca fotoğrafı nereden çekilir?","Sapanca Teleferik'in Mahmudiye'deki üst istasyonundaki seyir terasından çekilebilir."),
        ("Sapanca'da en fotojenik doğa noktası hangisi?","Göl kıyısının yanı sıra Maşukiye şelalesi ve kış aylarında Kartepe zirvesi öne çıkar."),
        ("Otel içinde fotoğraf çekilecek bir alan var mı?","Evet, DİDİ Otel'in begonvillerle çevrili bahçesi ve havuzu, özellikle akşamüzeri ışığında fotojeniktir.")],
},
{
 "slug":"sapancada-1-gunluk-2-gunluk-gezi-plani","cat":"Gezi Planı","img":"ONN09464","date":"2026-08-17",
 "title":"Sapanca'da 1 Günlük ve 2 Günlük Gezi Planı: Saat Saat Rota",
 "desc":"Sapanca'da bir gün ve iki gün için saat saat gezi planı; göl kıyısı, Sapanca Teleferik, Maşukiye, Poyrazlar Gölü ve DİDİ Otel'de konaklama önerileriyle hazır rota.",
 "lead":"Sapanca'da vaktiniz ister bir gün ister bir hafta sonu olsun, doğru sırayla planlanmış bir rota her durağı gezinin tadını kaçırmadan görmenizi sağlar. İşte DİDİ Otel'den başlayan, saat saat hazırlanmış 1 günlük ve 2 günlük Sapanca gezi planı.",
 "body":"""
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="g1">1 Gün</button><button data-tab="g2">2 Gün</button></div>
<div class="itin-panel on" data-tab="g1">
<div class="timeline">
<div class="tl-step"><div class="tl-time">09:00</div><h4>DİDİ Otel'de kahvaltı</h4><p>Güne göl manzarasına karşı zengin bir kahvaltıyla başlayın.</p></div>
<div class="tl-step"><div class="tl-time">10:30</div><h4>Sapanca Gölü kıyısı ve Uzunkum Parkı</h4><p>Göl kıyısında kısa bir yürüyüş yapın, isterseniz bisiklet kiralayın.</p></div>
<div class="tl-step"><div class="tl-time">12:00</div><h4>Maşukiye'de şelale ve alabalık molası</h4><p>Şelaleyi görüp dere kenarındaki bir alabalık tesisinde öğle yemeği yiyin.</p></div>
<div class="tl-step"><div class="tl-time">14:30</div><h4><a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a> ile Mahmudiye'ye çıkış</h4><p>Kırkpınar'dan biner, seyir terasında göl manzarasının tadını çıkarırsınız.</p></div>
<div class="tl-step"><div class="tl-time">16:30</div><h4>Otelde havuz kenarında dinlenme</h4><p>DİDİ Otel'in havuzunda ve bahçesinde güne mola verin.</p></div>
<div class="tl-step"><div class="tl-time">19:30</div><h4><a href="/#mare">Mare Gastro</a>'da akşam yemeği</h4><p>Bahçede, göl havasında bir akşam yemeğiyle günü tamamlayın.</p></div>
</div>
</div>
<div class="itin-panel" data-tab="g2">
<h4 style="margin:0 0 10px;font-weight:600">1. Gün</h4>
<p style="margin-bottom:22px">Yukarıdaki 1 günlük programın aynısını takip edebilir, akşam erken bir saatte otele dönebilirsiniz.</p>
<h4 style="margin:0 0 10px;font-weight:600">2. Gün</h4>
<div class="timeline">
<div class="tl-step"><div class="tl-time">09:30</div><h4>Kahvaltı sonrası <a href="/blog/poyrazlar-golu-mahmudiye-gizli-koseler/">Poyrazlar Gölü</a></h4><p>Kamp alanında yürüyüş, tekne turu ya da olta balıkçılığı deneyin.</p></div>
<div class="tl-step"><div class="tl-time">13:00</div><h4>Öğle molası ve dönüş</h4><p>Poyrazlar'da hafif bir öğle yemeğinin ardından Sapanca'ya dönün.</p></div>
<div class="tl-step"><div class="tl-time">14:30</div><h4>İsteğe bağlı: <a href="/blog/tarakli-geyve-gunubirlik-tur/">Taraklı ve Geyve</a> turu</h4><p>Zaman ve enerji uygunsa günübirlik tarihi kasaba turuna çıkabilirsiniz.</p></div>
<div class="tl-step"><div class="tl-time">19:00</div><h4>Otele dönüş, Mare Gastro'da veda yemeği</h4><p>İki günlük rotayı bahçede göl havasında bir akşam yemeğiyle kapatın.</p></div>
</div>
</div>
</div>
<h2>Nerede kalmalı?</h2>
<p>Her iki rota da <a href="/#odalar">DİDİ Otel Sapanca</a>'yı merkez alır: Kırkpınar'daki konumu göl kıyısına, Maşukiye'ye, teleferiğe ve Poyrazlar Gölü'ne kısa mesafededir. İki kişilik <a href="/odalar/king-suit/">King Suit</a>'ten dört kişilik <a href="/odalar/aile/">Aile Odası</a>'na kadar farklı ihtiyaçlara uygun seçenekler bulunur.</p>
<h2>İpucu</h2>
<p>Yoğun hafta sonlarında teleferik gişesinde kısa bir bekleme olabileceğinden, günü göl kıyısı ve Maşukiye ile başlayıp teleferiği öğleden sonraya bırakmak rotanın akışını daha rahat tutar.</p>
""",
 "faq":[("Sapanca'da 1 günde neler gezilir?","Göl kıyısı ve Uzunkum Parkı, Maşukiye şelalesi ve Sapanca Teleferik, bir günde rahatça gezilebilecek üç ana duraktır."),
        ("2 günlük Sapanca gezisinde nerede kalınmalı?","Kırkpınar'daki DİDİ Otel Sapanca, göl kıyısı, Maşukiye, teleferik ve Poyrazlar Gölü'ne kısa mesafesiyle iki günlük rota için merkezi bir seçenektir."),
        ("Sapanca gezisine en iyi başlangıç saati nedir?","Kahvaltının ardından 09:00-10:00 arası yola çıkmak, günü teleferik ve akşam yemeğine kadar rahat bir tempoda planlamanızı sağlar."),
        ("Rotaya ekleme yapılabilir mi?","Evet, 2. güne Poyrazlar Gölü'nün yanı sıra Taraklı ve Geyve günübirlik tarihi turu da eklenebilir.")],
},
{
 "slug":"sapancada-ne-yenir","cat":"Lezzet","img":"kahvalti","date":"2026-08-26","mod":"2026-11-16",
 "title":"Sapanca'da Ne Yenir? Yöresel Lezzetler ve Nerede Tadılır",
 "seo_title":"Sapanca'da Ne Yenir? 8 Yöresel Lezzet Rehberi",
 "img_alt":"Beyaz örtülü masada çay, peynirler, reçeller, sucuklu yumurta ve hamur işleriyle serpme kahvaltı",
 "desc":"Sapanca'da ne yenir? Tescilli ıslama köfte, Abhaz peyniri, kabak tatlısı, Maşukiye'de alabalık ve Çerkez mezeleri; ne, nerede tadılır tablosuyla.",
 "related":["sapancada-kahvalti-ve-yemek","masukiye-kartepe-gezi","sapancada-gezilecek-yerler"],
 "lead":"Sapanca'da ne yeneceğinin kısa cevabı: coğrafi işaretli <strong>Adapazarı ıslama köftesi</strong>, dere kenarında pişen <strong>alabalık</strong>, Çerkez ve Abhaz mutfağından gelen <strong>Abhaz peyniri</strong> ile cevizli mezeler, tatlıda ise yine tescilli <strong>Adapazarı kabak tatlısı</strong>. Güne göl havasında uzun bir serpme kahvaltıyla başlamak da bölgenin değişmez alışkanlığıdır. Aşağıda her lezzetin ne olduğunu, nerede aranacağını ve hangisinin resmi coğrafi işaret tescili olduğunu kaynaklarıyla birlikte bulacaksınız.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Tescilli lezzetler:</strong> Adapazarı ıslama köftesi (2013), Sakarya Abhaz peyniri ve Adapazarı kabak tatlısı (2021).</li>
<li><strong>Alabalık:</strong> Maşukiye'de dere kenarındaki tesislerde; Kırkpınar'a 10–15 dakika.</li>
<li><strong>Kahvaltı:</strong> Göl kıyısında serpme kahvaltı ya da köy usulü Çerkez kahvaltısı.</li>
</ul></div>
<h2>Sapanca mutfağını ne şekillendirir?</h2>
<p>Sapanca ve çevresinin sofrası üç kaynaktan beslenir: bereketli Sakarya ovasının sebze-meyvesi, göl ve dağ derelerinin balığı, bir de 19. yüzyılda Kafkasya'dan bölgeye yerleşen Çerkez ve Abhaz toplulukların mutfak kültürü. Balkanlardan gelen göçmenlerin izleri de özellikle Adapazarı'nın esnaf yemeklerinde görülür. Bu yüzden aynı gün içinde cevizli bir Çerkez mezesi, ızgara köfte ve dere alabalığı yemek burada hiç şaşırtıcı değildir.</p>
<h2>Sapanca'da tadılması gereken 8 lezzet</h2>
<table><thead><tr><th>Lezzet</th><th>Nedir?</th><th>Nerede aranır?</th></tr></thead><tbody>
<tr><td>Islama köfte</td><td>Izgara köfte; yanında kemik suyuyla ıslatılmış, salçalı-tereyağlı ekmek</td><td>Sapanca çarşısı ve Adapazarı'ndaki köfteciler</td></tr>
<tr><td>Alabalık</td><td>Izgara, tava ya da kiremitte pişirilen dere alabalığı</td><td>Maşukiye'de dere kenarı tesisleri</td></tr>
<tr><td>Abhaz peyniri</td><td>Abhaz ve Çerkez sofralarından gelen yöresel peynir</td><td>Köy kahvaltıları, yerel pazarlar</td></tr>
<tr><td>Çerkez tavuğu</td><td>Didiklenmiş tavuk, cevizli sos</td><td>Yöresel lokantalar, kahvaltı ve meze sofraları</td></tr>
<tr><td>Cevizli mezeler</td><td>Barbunya, fasulye ve karalahana ile cevizli ezmeler</td><td>Çerkez kahvaltıları</td></tr>
<tr><td>Kabak tatlısı</td><td>Adapazarı kabağıyla yapılan şerbetli fırın tatlısı</td><td>Sonbahar ve kış aylarında lokantalar ve tatlıcılar</td></tr>
<tr><td>Serpme kahvaltı</td><td>Peynirler, reçeller, bal-kaymak, sıcak hamur işleri</td><td>Göl kıyısındaki kahvaltı mekânları ve oteller</td></tr>
<tr><td>Köy ürünleri</td><td>Reçel, bal, yufka, mevsim meyvesi</td><td>Mahmudiye ve çevre köylerin pazarları</td></tr>
</tbody></table>
<h2>Adapazarı ıslama köftesi neden özel?</h2>
<p>Islama köfte, Sakarya'nın en bilinen lezzetidir ve resmi olarak tescillidir: Türk Patent ve Marka Kurumu kayıtlarında <strong>"Adapazarı Islama Köftesi"</strong>, Sakarya Ticaret ve Sanayi Odası'nın başvurusuyla <strong>8 Ocak 2013</strong>'te mahreç işareti olarak tescil edilmiştir. Tescil belgesine göre onu ayırt eden en önemli özellik, köfteyle birlikte sunulan ve kemik suyuyla ıslatılıp ızgarada ısıtılan bayat ekmektir. Basında yer alan anlatıma göre lezzet, 1900'lü yıllarda Balkanlardan gelen göçmenlerin bayat ekmeği değerlendirme alışkanlığından doğmuştur.</p>
<p>Sapanca merkezinde, Rüstempaşa'daki Mimar Sinan Caddesi üzerinde köfte ve esnaf yemeği sunan lokantalar bulunur; bunlardan Eker Lokantası, yemek rehberlerinde ıslama köftesiyle anılan adreslerden biridir. Adapazarı merkezde ise ıslama köfte salonları çok daha yaygındır.</p>
<h2>Sapanca'da alabalık nerede yenir?</h2>
<p>Alabalık için bölgenin klasik adresi, Kırkpınar'a yaklaşık 10–15 dakika uzaklıktaki <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'dir. Samanlı Dağları'ndan inen derelerin kenarına kurulu tesislerde alabalık ızgara, tava ya da kiremitte pişirilir; yanında genellikle mısır ekmeği ve mevsim salatası gelir. Hafta sonları öğle saatlerinde yoğun olabildiği için erken bir öğle yemeği planlamak iyi fikir.</p>
<h2>Çerkez ve Abhaz mutfağından ne yenir?</h2>
<p><strong>Sakarya Abhaz peyniri</strong> ve <strong>Adapazarı kabak tatlısı</strong>, 2021'de Sakarya Ticaret ve Sanayi Odası'nın başvurusuyla coğrafi işaret aldı. Çerkez mutfağının <strong>Çerkez tavuğu</strong>, cevizli fasulye ve barbunya ezmesi gibi mezeleri ise köy usulü kahvaltılarda ve yöresel lokantalarda karşınıza çıkar. Vejetaryenler için bu mezeler zengin bir seçenek sunar.</p>
""" + fig("/assets/web/editorial/ONN09378","Ahşap masada yeşillikli ve soslu mezeler, meze tabakları ve çatal bıçaklar, üstten görünüm","Paylaşmalık mezelerle uzun bir sofra, Sapanca'da akşamların vazgeçilmezi.") + """
<h2>Sapanca'da kahvaltı kültürü</h2>
<p>Hafta sonu Sapanca'ya gelenlerin çoğu güne göl havasında, saatlerce süren bir serpme kahvaltıyla başlar: köy peynirleri, ev reçelleri, bal-kaymak, sıcak hamur işleri ve demli çay. Kırkpınar'ın göl kıyısındaki çınar gölgeli bahçeler bu kültürün en bilinen adreslerindendir. Konaklayan misafirlerimiz için <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur). Kahvaltı ve yemek planı için <a href="/blog/sapancada-kahvalti-ve-yemek/">Sapanca'da kahvaltı ve yemek</a> rehberimize bakabilirsiniz.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="sabah">Sabah</button><button data-tab="ogle">Öğle</button><button data-tab="aksam">Akşam</button></div>
<div class="itin-panel on" data-tab="sabah"><p>Serpme kahvaltı ya da Çerkez kahvaltısı; Abhaz peyniri ve cevizli mezeleri deneyin.</p></div>
<div class="itin-panel" data-tab="ogle"><p>Maşukiye'de dere kenarında alabalık ya da çarşıda ıslama köfte. Tatlıya kabak tatlısı.</p></div>
<div class="itin-panel" data-tab="aksam"><p>Gezi dönüşü dışarı çıkmak istemeyenler için otel bahçesindeki <a href="/#mare">Mare Gastro</a>; menü ve rezervasyon bilgisi için <a href="https://maregastro.com" target="_blank" rel="noopener">maregastro.com</a>.</p></div>
</div>
<h2>Lezzet kontrol listesi</h2>
<p>Tattıklarınızı işaretleyin — seçimleriniz tarayıcınızda kaydedilir.</p>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="ne-yenir">
<label><input type="checkbox"><span><b>Islama köfte</b><span>Tescilli Adapazarı lezzeti.</span></span></label>
<label><input type="checkbox"><span><b>Dere alabalığı</b><span>Maşukiye'de dere kenarında.</span></span></label>
<label><input type="checkbox"><span><b>Abhaz peyniri</b><span>Köy kahvaltısında.</span></span></label>
<label><input type="checkbox"><span><b>Çerkez tavuğu ve cevizli mezeler</b><span>Kafkas mutfağının imzası.</span></span></label>
<label><input type="checkbox"><span><b>Kabak tatlısı</b><span>Özellikle sonbahar ve kışın.</span></span></label>
<label><input type="checkbox"><span><b>Köy ürünleri</b><span>Mahmudiye pazarından reçel ve bal.</span></span></label>
</div>
<h2>Lezzet turu için nerede kalınır?</h2>
<p>Maşukiye'ye, Sapanca çarşısına ve göl kıyısına eşit mesafede bir üs için Kırkpınar idealdir. <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir ve akşam yemeği için bahçedeki Mare Gastro'ya yürüyerek geçebilirsiniz. <a href="/odalar/">Odalarımızı</a> inceleyin ya da müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%27da%20konaklama%20i%C3%A7in%20m%C3%BCsaitlik%20sormak%20istiyorum.">WhatsApp'tan</a> yazın.</p>
""",
 "sources":[("TÜRKPATENT — Adapazarı Islama Köftesi coğrafi işaret tescil belgesi","https://ci.turkpatent.gov.tr/Files/GeographicalSigns/7cb1df9b-6fae-4ba6-aab3-1c6c1f73482e.pdf"),
            ("Sakarya'nın kabak tatlısı ve Abhaz peyniri coğrafi işaret aldı (CNN Türk, 29.04.2021)","https://www.cnnturk.com/yasam/sakaryanin-kabak-tatlisi-ve-abhaz-peyniri-cografi-isaret-aldi-1649231"),
            ("Islama köfte (Wikipedia)","https://en.wikipedia.org/wiki/Islama_k%C3%B6fte"),
            ("Sapanca'daki restoranlar rehberi (Yemek.com)","https://yemek.com/sapanca-mekanlari/")],
 "extra_ld":{"@context":"https://schema.org","@type":"ItemList","name":"Sapanca'da tadılması gereken yöresel lezzetler","itemListElement":[
   {"@type":"ListItem","position":1,"item":{"@type":"Thing","name":"Adapazarı ıslama köftesi","description":"Kemik suyuyla ıslatılmış ekmekle servis edilen köfte; 8 Ocak 2013'te mahreç işareti olarak tescil edildi."}},
   {"@type":"ListItem","position":2,"item":{"@type":"Thing","name":"Alabalık","description":"Maşukiye'de dere kenarındaki tesislerde ızgara, tava ya da kiremitte pişirilen alabalık."}},
   {"@type":"ListItem","position":3,"item":{"@type":"Thing","name":"Sakarya Abhaz peyniri","description":"Abhaz ve Çerkez sofralarından gelen yöresel peynir; 2021'de coğrafi işaret aldı."}},
   {"@type":"ListItem","position":4,"item":{"@type":"Thing","name":"Çerkez tavuğu","description":"Cevizli sosla hazırlanan Kafkas mutfağı mezesi."}},
   {"@type":"ListItem","position":5,"item":{"@type":"Thing","name":"Adapazarı kabak tatlısı","description":"Adapazarı kabağıyla yapılan tatlı; 2021'de coğrafi işaret aldı."}}
 ]},
 "faq":[("Sapanca'nın meşhur yemeği nedir?","Bölgenin en bilinen lezzeti, 2013'te coğrafi işaret tescili alan Adapazarı ıslama köftesidir. Maşukiye'de dere kenarında yenen alabalık, Abhaz peyniri, Çerkez tavuğu ve kabak tatlısı da öne çıkar."),
        ("Islama köfte nedir?","Izgara köftenin yanında kemik suyuyla ıslatılıp ızgarada ısıtılan bayat ekmekle servis edildiği bir Adapazarı yemeğidir; Sakarya Ticaret ve Sanayi Odası adına 8 Ocak 2013'te tescil edilmiştir."),
        ("Sapanca'da alabalık nerede yenir?","Alabalık için en bilinen yer, Kırkpınar'a yaklaşık 10–15 dakika uzaklıktaki Maşukiye'deki dere kenarı tesisleridir."),
        ("Sapanca'da hangi lezzetler coğrafi işaretli?","Adapazarı ıslama köftesi (2013), Sakarya Abhaz peyniri ve Adapazarı kabak tatlısı (2021) coğrafi işaret tescillidir."),
        ("Sapanca'da vejetaryen seçenek bulunur mu?","Evet. Çerkez mutfağının cevizli fasulye, barbunya ve karalahana ezmeleri ile zengin kahvaltı sofraları vejetaryenler için bol seçenek sunar."),
        ("DİDİ Otel'de kahvaltı dahil mi?","Evet. DİDİ Otel Sapanca'da konaklayan misafirlere kahvaltı Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur.")],
},
{
 "slug":"sapanca-evlilik-teklifi-organizasyon","cat":"Özel Günler","img":"havuz-loca","date":"2026-08-26","mod":"2026-11-16",
 "title":"Sapanca'da Evlilik Teklifi: Mekân, Saat ve Hazırlık Rehberi",
 "seo_title":"Sapanca'da Evlilik Teklifi: Mekân ve Saat Rehberi",
 "img_alt":"DİDİ Otel Sapanca'da begonvillerin ardında şemsiyeli şezlonglar ve havuz",
 "desc":"Sapanca'da evlilik teklifi: göl kıyısı ve teleferik fikirleri, aylara göre gün batımı saatleri, Mare Gastro'da rezervasyonda pasta, mum ve masa süslemesi.",
 "related":["sapancada-romantik-hafta-sonu","sapancada-balayi-ozel-gunler","sapancada-fotograf-gun-batimi-noktalari"],
 "lead":"Sapanca'da evlilik teklifi için en etkileyici sahne, gün batımına yakın saatlerde göl kıyısıdır; kasımda güneş 17:40 civarında, haziranda ise 20:30 civarında batar. Teklifi gün içinde yapmak isteyenler için teleferikle çıkılan seyir noktaları, akşam için ise bahçede sakin bir akşam yemeği iyi seçeneklerdir. DİDİ Otel'in bahçesindeki <a href=\"/#mare\">Mare Gastro</a>'da <strong>rezervasyon sırasında belirtirseniz</strong> pasta, mum ışığı ve masa süslemesi hazırlanabilir. Aşağıda mekân seçimini, saat planlamasını ve hazırlık listesini adım adım bulacaksınız.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Nerede:</strong> göl kıyısı (gün batımı), teleferik seyir noktaları (gündüz), otel bahçesi ve Mare Gastro (akşam).</li>
<li><strong>Ne zaman:</strong> gün batımından 45–60 dakika önce; aylara göre saatler aşağıdaki tabloda.</li>
<li><strong>Mare Gastro'da hazırlanabilecekler:</strong> pasta, mum ışığı, masa süslemesi — yalnızca rezervasyonda belirtilirse.</li>
</ul></div>
<h2>Sapanca evlilik teklifi için neden iyi bir yer?</h2>
<p>Sapanca'yı teklif için öne çıkaran şey sahnenin kendiliğinden hazır olması: su, orman ve dağ aynı karede. İstanbul'dan 1,5–2 saatlik mesafe, teklifi "hafta sonu kaçamağı" bahanesiyle sürprize dönüştürmeyi de kolaylaştırır. Kalabalık bir salon ya da büyük bir organizasyon gerekmeden, doğru saatte doğru yerde durmak çoğu zaman yeterlidir.</p>
<h2>Teklif için en romantik yerler nereler?</h2>
<table><thead><tr><th>Yer</th><th>Saat</th><th>Artısı</th><th>Dikkat</th></tr></thead><tbody>
<tr><td>Göl kıyısı (Kırkpınar sahili)</td><td>Gün batımı</td><td>Altın ışık, su yansıması</td><td>Hafta sonu kalabalık olabilir; sakin bir köşe seçin</td></tr>
<tr><td>Teleferik ve üst istasyon</td><td>11:00–19:00 arası</td><td>Gölün kuşbakışı manzarası</td><td>Kabinde başka yolcular olabilir; rüzgârda seferler durabilir</td></tr>
<tr><td>Uzunkum ve göl kenarı parkları</td><td>Sabah ya da gün batımı</td><td>Geniş ve yeşil alanlar</td><td>Piknik günlerinde yoğun</td></tr>
<tr><td>Otel bahçesi ve Mare Gastro</td><td>Akşam yemeği</td><td>Baş başa masa, hazırlanabilen pasta ve mum</td><td>Rezervasyonda önceden belirtin</td></tr>
</tbody></table>
<p>Fotoğraf için en güzel kıyı noktalarını <a href="/blog/sapancada-fotograf-gun-batimi-noktalari/">gün batımı ve fotoğraf noktaları</a> rehberimizde, teleferiğin saat ve bilet bilgilerini <a href="/blog/sapanca-teleferik-rehberi/">teleferik rehberimizde</a> bulabilirsiniz.</p>
<h2>Sapanca'da gün batımı saat kaçta?</h2>
<p>Teklif anını altın saate denk getirmek için aşağıdaki tabloyu kullanın. Saatler, Sapanca koordinatları için standart güneş hesabıyla her ayın 15'i için hesaplanmıştır; ay içinde birkaç dakika oynar.</p>
<table><thead><tr><th>Ay</th><th>Gün batımı</th><th>Teklif için ideal başlangıç</th></tr></thead><tbody>
<tr><td>Ocak</td><td>17:55</td><td>17:00</td></tr>
<tr><td>Şubat</td><td>18:33</td><td>17:40</td></tr>
<tr><td>Mart</td><td>19:05</td><td>18:10</td></tr>
<tr><td>Nisan</td><td>19:37</td><td>18:45</td></tr>
<tr><td>Mayıs</td><td>20:09</td><td>19:15</td></tr>
<tr><td>Haziran</td><td>20:32</td><td>19:40</td></tr>
<tr><td>Temmuz</td><td>20:29</td><td>19:35</td></tr>
<tr><td>Ağustos</td><td>19:58</td><td>19:05</td></tr>
<tr><td>Eylül</td><td>19:10</td><td>18:15</td></tr>
<tr><td>Ekim</td><td>18:20</td><td>17:25</td></tr>
<tr><td>Kasım</td><td>17:42</td><td>16:50</td></tr>
<tr><td>Aralık</td><td>17:33</td><td>16:40</td></tr>
</tbody></table>
<p class="note">Kış aylarında teleferik 19:00'da kapandığı için gün batımını yukarıdan izlemek mümkün; yaz aylarında ise güneş teleferik kapandıktan sonra batar.</p>
<h2>Mare Gastro'da neler hazırlanabilir?</h2>
<p>DİDİ Otel'in bahçesindeki <a href="/#mare">Mare Gastro</a>'da, <strong>rezervasyonunuz sırasında belirtmeniz halinde</strong> şu dokunuşlar hazırlanabilir:</p>
<ul>
<li><strong>Pasta</strong></li>
<li><strong>Mum ışığı</strong></li>
<li><strong>Masa süslemesi</strong></li>
</ul>
<p>Bunların dışında bir talebiniz varsa (ör. belirli bir saat, masa konumu ya da yanınıza alacağınız bir yüzük kutusunun saklanması gibi) rezervasyon sırasında sorun; hangi taleplerin karşılanabileceğini size net olarak söyleriz. Menü ve rezervasyon ayrıntıları için <a href="https://maregastro.com" target="_blank" rel="noopener">maregastro.com</a>'a da bakabilirsiniz.</p>
""" + fig("/assets/web/editorial/ONN09337","Beyaz örtülü masada iki kadeh tokuşturuluyor, arkada beyaz perdeler ve yeşillik","Mare Gastro'da bahçede bir akşam; pasta, mum ve masa süslemesi rezervasyonda belirtilirse hazırlanır.") + """
<h2>Teklif gününü adım adım nasıl planlarsınız?</h2>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="once">1 hafta önce</button><button data-tab="gun">Teklif günü</button><button data-tab="sonra">Sonrası</button></div>
<div class="itin-panel on" data-tab="once"><p>Konaklamayı ve Mare Gastro rezervasyonunu yapın; pasta, mum ve masa süslemesi isteğinizi bu sırada iletin. Hava tahminine bakın ve yağmur ihtimaline karşı B planı (akşam yemeği masası) belirleyin.</p></div>
<div class="itin-panel" data-tab="gun"><p>Öğleden sonra teleferik ya da göl kıyısında yürüyüş; gün batımından 45–60 dakika önce seçtiğiniz kıyı noktasına geçin. Fotoğraf çekecek bir arkadaşınız varsa yerini önceden ayarlayın. Akşam Mare Gastro'da kutlama.</p></div>
<div class="itin-panel" data-tab="sonra"><p>Ertesi sabah uzun bir serpme kahvaltı ve göl kıyısında yürüyüş. Bir gece daha kalmak isterseniz <a href="/blog/sapancada-romantik-hafta-sonu/">romantik hafta sonu</a> rehberimizden program çıkarabilirsiniz.</p></div>
</div>
<h2>Kusursuz bir teklif için hatırlatma listesi</h2>
<p>Adımları işaretleyin — seçimleriniz tarayıcınızda kaydedilir.</p>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="evlilik-teklifi">
<label><input type="checkbox"><span><b>Tarihi ve gün batımı saatini belirleyin</b><span>Yukarıdaki tabloya bakın.</span></span></label>
<label><input type="checkbox"><span><b>Yeri seçin</b><span>Göl kıyısı, teleferik ya da akşam yemeği masası.</span></span></label>
<label><input type="checkbox"><span><b>Pasta, mum ve masa süslemesi</b><span>Mare Gastro rezervasyonunda belirtin.</span></span></label>
<label><input type="checkbox"><span><b>Hava durumu ve B planı</b><span>Yağmurda akşam yemeği masası güvenli seçenek.</span></span></label>
<label><input type="checkbox"><span><b>Anı kaydı</b><span>Fotoğraf çekecek kişiyi önceden ayarlayın.</span></span></label>
<label><input type="checkbox"><span><b>Konaklamayı ayırtın</b><span>Özel geceyi otelde tamamlayın.</span></span></label>
</div>
<h2>Teklif sonrası nerede kalınır?</h2>
<p>Özel geceyi göl ile orman arasında tamamlamak isteyenler için <a href="/#konum">DİDİ Otel Sapanca</a>'nın <a href="/odalar/king-suit/">King Suit</a> ve <a href="/odalar/junior-suit/">Junior Suit</a> odaları çiftler için rahat seçeneklerdir; jakuzili oda seçeneklerini <a href="/blog/sapanca-jakuzili-havuzlu-gol-manzarali-oda/">bu yazımızda</a> anlattık. Tarih ve müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%27da%20evlilik%20teklifi%20i%C3%A7in%20konaklama%20ve%20Mare%20Gastro%20rezervasyonu%20yapmak%20istiyorum.">WhatsApp'tan</a> yazın ya da 0264 592 12 12'yi arayın.</p>
""",
 "sources":[("Sapanca Teleferik — çalışma saatleri (resmi site)","https://sapancateleferik.com.tr/"),
            ("Gün batımı saatleri: NOAA güneş konumu hesabı (Sapanca, 40,69° K / 30,22° D, UTC+3)","https://gml.noaa.gov/grad/solcalc/")],
 "faq":[("Sapanca'da evlilik teklifi için en romantik yer neresi?","Gün batımında göl kıyısı en çok tercih edilen sahnedir. Gündüz için teleferikle çıkılan seyir noktaları, akşam için ise bahçede sakin bir akşam yemeği masası iyi seçeneklerdir."),
        ("Mare Gastro'da özel gün için ne hazırlanıyor?","Rezervasyon sırasında belirtmeniz halinde pasta, mum ışığı ve masa süslemesi hazırlanabilir. Bunların dışındaki talepleri rezervasyonda sormanız gerekir."),
        ("Sapanca'da gün batımı saat kaçta?","Her ayın ortası için yaklaşık olarak: ocak 17:55, mart 19:05, haziran 20:32, eylül 19:10, kasım 17:42, aralık 17:33."),
        ("Ne kadar önceden haber vermeliyim?","Pasta ve süsleme hazırlığının eksiksiz yapılabilmesi için talebinizi mümkün olduğunca erken, rezervasyonunuz sırasında iletmeniz gerekir."),
        ("Teleferikte teklif yapılabilir mi?","Teleferik her gün 11:00–19:00 arasında çalışır ve gölün kuşbakışı manzarasını sunar; ancak kabinlerde başka yolcular olabilir ve rüzgârda seferler durdurulabilir, bu yüzden yedek plan yapın."),
        ("Teklif sonrası konaklama mümkün mü?","Evet. DİDİ Otel Sapanca'da King Suit, Junior Suit ve jakuzili oda seçenekleriyle özel gecenizi otelde tamamlayabilirsiniz.")],
},
{
 "slug":"sapanca-jakuzili-havuzlu-gol-manzarali-oda","cat":"Konaklama","img":"havuz2","date":"2026-08-26",
 "title":"Sapanca'da Jakuzili, Havuzlu ve Göl Manzaralı Oda Rehberi",
 "desc":"Sapanca'da jakuzili, özel havuzlu ve göl manzaralı konaklama seçenekleri: bungalov mu butik otel mi? DİDİ Otel'in jakuzili odaları, klorsuz havuzu ve göl manzaralı farkı.",
 "lead":"Sapanca'da jakuzili, havuzlu ya da göl manzaralı bir oda ararken karşınıza iki ana seçenek çıkar: özel havuzlu/jakuzili bungalovlar ve otel konforu sunan butik oteller. Hangisinin size uygun olduğu; mahremiyet mi yoksa hizmet, kahvaltı ve sosyal olanaklar mı istediğinize bağlıdır. DİDİ Otel Sapanca ise <strong>jakuzili odaları</strong>, <strong>Sapanca'nın tek klorsuz havuzu</strong> ve göl-orman manzaralı odalarıyla bu beklentilerin çoğunu tek çatı altında, otel konforuyla birlikte sunar.",
 "body":"""
<h2>Sapanca'da konaklama tipleri</h2>
<p>Sapanca'da başlıca üç konaklama tarzı öne çıkar: özel havuzlu veya jakuzili <strong>bungalovlar</strong>, hizmet ve sosyal olanak sunan <strong>butik oteller</strong> ve kalabalık gruplar için <strong>villalar</strong>. Doğru seçim; kaç kişi olduğunuza, mahremiyet ve konfor beklentinize göre değişir.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="bungalov">Bungalov / Villa</button><button data-tab="otel">Butik otel</button></div>
<div class="itin-panel on" data-tab="bungalov"><p>Tamamen size ait, dışarıdan görünmeyen bir alan; genellikle özel havuz, jakuzi, şömine ve barbekü. Mahremiyet önceliğinizse ve kendi düzeninizi kurmak istiyorsanız uygundur. Buna karşılık hizmet, kahvaltı ve sosyal olanaklar sınırlı olabilir.</p></div>
<div class="itin-panel" data-tab="otel"><p>Resepsiyon, günlük temizlik, restoran ve zengin kahvaltı gibi otel hizmetleri; bakımlı ortak havuz ve sosyal alanlar. Konfor, güvenlik ve hizmet önceliğinizse butik otel daha rahat bir deneyim sunar.</p></div>
</div>
<h2>"Jakuzili" ve "özel havuzlu" ne beklemeli?</h2>
<p>Piyasada jakuzili ve özel havuzlu seçenekler çoğunlukla bungalov konseptinde sunulur; jakuzi, şömine ve barbekü gibi ayrıntılar çiftler için popülerdir. Fiyatlar sezona ve olanaklara göre değişir; genel olarak bu segment, standart odalara kıyasla daha yüksek bir bütçe gerektirir. Rezervasyon öncesi havuzun açık/kapalı ve ısıtmalı olup olmadığını, jakuzinin oda içi mi ortak mı olduğunu teyit etmek önemlidir.</p>
<h2>DİDİ Otel'in farkı: jakuzili oda, klorsuz havuz ve göl manzarası</h2>
<p>DİDİ Otel Sapanca, göl kıyısındaki sakin <a href="/#konum">Kırkpınar</a> mahallesinde, göl ile orman arasında yer alır. Çiftlerin sıkça aradığı <strong>jakuzili odalar</strong>, otelde bungalov konforunu otel hizmetleriyle birleştirir; böylece hem oda içinde jakuzi keyfini hem de resepsiyon, kahvaltı ve restoran gibi olanakları bir arada yaşarsınız. Bir diğer belirgin farkı ise <a href="/blog/sapancada-havuzlu-otel/"><strong>Sapanca'nın tek klorsuz havuzu</strong></a>dur; klor yerine daha nazik bir arıtma yöntemi kullanıldığı için göz ve cilt yanması yapmaz, özellikle çocuklu aileler ve hassas ciltler için konforludur. Göl ve orman manzaralı <a href="/#odalar">oda tipleri</a>, bahçedeki <a href="/#mare">Mare Gastro</a> restoranı ve butik otel hizmetleriyle mahremiyet ile konforu dengeli bir şekilde bir araya getirir.</p>
<p>Oda tiplerini ve olanakları <a href="/odalar/">oda sayfamızda</a> inceleyebilir, güncel müsaitlik ve fiyatlar için <a href="https://wa.me/905331350888?text=Sapanca%27da%20konaklama%20ve%20oda%20se%C3%A7enekleri%20hakk%C4%B1nda%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> ulaşabilirsiniz.</p>
<h2>Oda seçerken sorulacak sorular</h2>
<p>Doğru odayı seçmek için aşağıdaki başlıkları işaretleyip teyit edin — seçimleriniz tarayıcınızda kaydedilir.</p>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="oda-secimi">
<label><input type="checkbox"><span><b>Havuz klorlu mu, klorsuz mu?</b><span>Klorsuz havuz cilt ve gözü yakmaz.</span></span></label>
<label><input type="checkbox"><span><b>Manzara: göl mü, orman mı?</b><span>Oda yönünü önceden sorun.</span></span></label>
<label><input type="checkbox"><span><b>Kahvaltı dahil mi?</b><span>Serpme kahvaltı olup olmadığını teyit edin.</span></span></label>
<label><input type="checkbox"><span><b>Havuz açık/kapalı ve ısıtmalı mı?</b><span>Mevsime göre kritik bir ayrıntı.</span></span></label>
<label><input type="checkbox"><span><b>Konum: göl kıyısına yakın mı?</b><span>Kırkpınar en sakin kıyıdır.</span></span></label>
<label><input type="checkbox"><span><b>Restoran var mı?</b><span>Dışarı çıkmadan yemek imkanı.</span></span></label>
</div>
<h2>Özetle: size uygun olan hangisi?</h2>
<p>Tam mahremiyet ve tek başına bir alan önceliğinizse bungalov; jakuzi keyfini otel hizmetleri, zengin kahvaltı, klorsuz havuz ve göl manzarasıyla birlikte istiyorsanız DİDİ Otel'in <strong>jakuzili odaları</strong> her iki dünyanın da avantajını sunar. Konaklama bölgelerini karşılaştırmak için <a href="/blog/sapanca-nerede-kalinir-bolge-rehberi/">Sapanca'da nerede kalınır</a> rehberimize de göz atabilirsiniz.</p>
""",
 "faq":[("DİDİ Otel'de jakuzili oda var mı?","Evet, DİDİ Otel Sapanca'da jakuzili odalar bulunur; oda içi jakuzi keyfini otel konforuyla birlikte sunar. Güncel müsaitlik için rezervasyon sırasında teyit alabilirsiniz."),
        ("Sapanca'da havuzlu otel var mı?","Evet. DİDİ Otel Sapanca, bölgenin tek klorsuz havuzuna sahip butik bir oteldir; ayrıca çok sayıda özel havuzlu bungalov seçeneği de bulunur."),
        ("Klorsuz havuz nedir, neden önemlidir?","Klorsuz havuzlarda klor yerine daha nazik bir arıtma yöntemi kullanılır; göz ve cilt yanması yapmadığı için özellikle çocuklu aileler ve hassas ciltler için daha konforludur."),
        ("Sapanca'da bungalov mu otel mi daha iyi?","Mahremiyet ve tek başına bir alan önceliğinizse bungalov; jakuzi keyfini hizmet, kahvaltı ve klorsuz havuzla birlikte istiyorsanız DİDİ Otel'in jakuzili odaları avantajlıdır."),
        ("Göl manzaralı oda bulabilir miyim?","Evet, DİDİ Otel'in göl ve orman manzaralı oda tipleri vardır; rezervasyonda oda yönünü belirtmeniz önerilir."),
        ("Kahvaltı konaklamaya dahil mi?","Evet. DİDİ Otel'de kahvaltı konaklamaya dahildir ve Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur. Güncel koşullar için rezervasyon sırasında teyit alabilirsiniz."),
        ("Fiyatlar ne kadar?","Fiyatlar sezona ve oda tipine göre değişir; güncel müsaitlik ve fiyat için WhatsApp üzerinden bize ulaşabilirsiniz.")],
},
{
 "slug":"sapanca-nerede-kalinir-bolge-rehberi","cat":"Konaklama","img":"dis-cephe","date":"2026-08-26",
 "title":"Sapanca'da Nerede Kalınır? Bölge Bölge Konaklama Rehberi",
 "desc":"Sapanca'da nerede kalınır? Kırkpınar göl kıyısı, Maşukiye doğası, merkez ve Kuzuluk termal bölgeleri karşılaştırması; hangi bölge kime uygun ve DİDİ Otel'in Kırkpınar avantajı.",
 "lead":"Sapanca'da nerede kalınacağının kısa cevabı ne aradığınıza bağlıdır: göl kıyısında sakinlik için <strong>Kırkpınar</strong>, şelale ve doğa için <strong>Maşukiye</strong>, ulaşım kolaylığı için <strong>Sapanca merkez ve göl çevresi</strong>, termal tatil için <strong>Kuzuluk</strong> öne çıkar. Aşağıda her bölgenin kime uygun olduğunu ve gezinizi kurmak için en pratik konumu bulacaksınız.",
 "body":"""
<h2>Sapanca'da konaklama bölgeleri</h2>
<p>Sapanca küçük bir ilçe olsa da, konakladığınız bölge tatilinizin havasını belirler. Göl kıyısının sakin mahalleleri huzur arayanlara, dağ içi Maşukiye doğa ve maceraya, merkez ise hareket ve ulaşım kolaylığına yakın olmak isteyenlere hitap eder.</p>
<h2>Kırkpınar: gölün en sakin kıyısı</h2>
<p><strong>Kırkpınar</strong>, Sapanca Gölü'nün kuzey kıyısında, 1864'te kurulmuş yemyeşil bir mahalledir. Göl kıyısına ve <a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a>'in alt istasyonuna yürüme mesafesindedir; sessiz, doğayla iç içe ve merkeze yakındır. Huzur ve göl manzarası önceliğinizse en ideal bölgedir. <a href="/#konum">DİDİ Otel Sapanca</a> tam burada yer alır. Ayrıntılar için <a href="/blog/kirkpinar-sapanca-konaklama/">Kırkpınar konaklama</a> yazımıza bakabilirsiniz.</p>
<h2>Maşukiye: şelale ve doğa</h2>
<p><a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>, Sapanca'ya yaklaşık 20 dakika mesafede; şelaleleri, alabalık tesisleri ve dağ havasıyla doğa tutkunlarının tercihidir. Orman içinde, dere kenarında bir kaçamak isteyenler için idealdir; buna karşılık göl manzarasından uzaktır.</p>
<h2>Sapanca merkez ve göl çevresi</h2>
<p>Ulaşım kolaylığı ve hareketli bir atmosfer isteyenler için <strong>Sapanca merkez</strong> ve göl çevresi uygundur. Çarşı, restoranlar ve <a href="/blog/sapancaya-nasil-gidilir/">tren istasyonu</a> yakındır; ancak sezon yoğunluğunda daha kalabalık olabilir.</p>
<h2>Kuzuluk: termal tatil</h2>
<p>Şifalı termal sularıyla bilinen <strong>Kuzuluk</strong>, wellness ve dinlenme odaklı bir tatil isteyenler için ayrı bir seçenektir; göl ve merkezden biraz daha uzaktır.</p>
<h3>Bölge karşılaştırması</h3>
<table><thead><tr><th>Bölge</th><th>Kime uygun</th><th>Öne çıkan</th></tr></thead><tbody>
<tr><td>Kırkpınar</td><td>Huzur, çiftler, göl manzarası</td><td>Göl kıyısı + teleferik, sakinlik</td></tr>
<tr><td>Maşukiye</td><td>Doğa ve macera severler</td><td>Şelale, alabalık, dağ havası</td></tr>
<tr><td>Merkez / göl çevresi</td><td>Ulaşım ve hareket isteyenler</td><td>Çarşı, tren, restoranlar</td></tr>
<tr><td>Kuzuluk</td><td>Termal / wellness</td><td>Kaplıca, dinlenme</td></tr>
</tbody></table>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="cift">Çiftler</button><button data-tab="aile">Aileler</button><button data-tab="doga">Doğa</button></div>
<div class="itin-panel on" data-tab="cift"><p>Göl manzarası ve sakinlik için Kırkpınar ideal. <a href="/blog/sapancada-romantik-hafta-sonu/">Romantik bir hafta sonu</a> için göl kıyısı + Mare Gastro akşam yemeği.</p></div>
<div class="itin-panel" data-tab="aile"><p>Çocuklu aileler için klorsuz havuzlu, göl kıyısına yakın bir konaklama pratiktir; <a href="/blog/ailecek-sapanca-tatili/">ailecek Sapanca tatili</a> rehberine bakın.</p></div>
<div class="itin-panel" data-tab="doga"><p>Doğa ve macera önceliğinizse Maşukiye yakını; yine de göl kıyısında kalıp gündüz Maşukiye'ye gitmek en dengeli seçenektir.</p></div>
</div>
<h2>Neden Kırkpınar en pratik merkez?</h2>
<p>Göl kıyısına ve teleferiğe yürüme mesafesinde olması, <a href="/blog/sapancada-gezilecek-yerler/">başlıca durakların tamamına</a> yarım saat içinde ulaşılması ve sessiz doğasıyla Kırkpınar, gezinizi kurmak için en dengeli bölgedir. <a href="/#konum">DİDİ Otel Sapanca</a>; göl ve orman arasında, <a href="/blog/sapancada-havuzlu-otel/">klorsuz havuzu</a> ve <a href="/#mare">Mare Gastro</a> restoranıyla tam da burada konumlanır.</p>
<h2>Bölge seçerken kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="bolge-secimi">
<label><input type="checkbox"><span><b>Göl manzarası önemli mi?</b><span>Kırkpınar / göl kıyısı tercih edin.</span></span></label>
<label><input type="checkbox"><span><b>Sessizlik mi, hareket mi?</b><span>Sakinlik için kıyı mahalleleri.</span></span></label>
<label><input type="checkbox"><span><b>Ulaşım (araçsız) planı</b><span>Merkez ve tren yakınlığını değerlendirin.</span></span></label>
<label><input type="checkbox"><span><b>Duraklarla mesafe</b><span>Teleferik, Maşukiye, göl kıyısı.</span></span></label>
<label><input type="checkbox"><span><b>Otel olanakları</b><span>Klorsuz havuz, kahvaltı, restoran.</span></span></label>
</div>
<p>Konaklama tiplerini (bungalov, jakuzili, havuzlu) karşılaştırmak için <a href="/blog/sapanca-jakuzili-havuzlu-gol-manzarali-oda/">oda rehberimize</a>, güncel müsaitlik için <a href="https://wa.me/905331350888?text=Sapanca%27da%20konaklama%20hakk%C4%B1nda%20bilgi%20almak%20istiyorum.">WhatsApp'a</a> ulaşabilirsiniz.</p>
""",
 "faq":[("Sapanca'da nerede kalmak en iyisi?","Göl manzarası ve sakinlik için Kırkpınar, doğa ve şelale için Maşukiye, ulaşım kolaylığı için merkez, termal tatil için Kuzuluk öne çıkar. Gezinin tamamına yakınlık açısından Kırkpınar en dengeli bölgedir."),
        ("Kırkpınar nerede?","Sapanca Gölü'nün kuzey kıyısında, göl kıyısına ve Sapanca Teleferik'in alt istasyonuna yürüme mesafesindeki sakin bir mahalledir. DİDİ Otel Sapanca burada yer alır."),
        ("Göl kıyısında mı yoksa merkezde mi kalmalı?","Huzur ve göl manzarası istiyorsanız göl kıyısı (Kırkpınar); ulaşım, çarşı ve hareketli bir atmosfer istiyorsanız merkez daha uygundur."),
        ("Aileler için hangi bölge uygun?","Çocuklu aileler için göl kıyısına yakın, klorsuz havuzlu bir konaklama hem güvenli hem konforludur."),
        ("Araçsız gelenler için hangi bölge pratik?","Tren istasyonuna yakınlığı nedeniyle merkez ve göl çevresi pratik olabilir; transfer ile göl kıyısı mahallelerine kolayca ulaşılır."),
        ("Sapanca'nın en sakin bölgesi neresi?","Göl kıyısındaki Kırkpınar, sessizliği ve doğasıyla ilçenin en sakin bölgelerinden biridir.")],
},
{
 "slug":"sapanca-mi-abant-mi-bolu-mu","cat":"Karşılaştırma","img":"otel-havuz","date":"2026-08-26","mod":"2026-11-16",
 "title":"Sapanca mı Abant mı Bolu mu? Hafta Sonu Kaçamağı Karşılaştırması",
 "seo_title":"Sapanca mı Abant mı Bolu mu? Mesafe ve Mevsim Kıyası",
 "img_alt":"DİDİ Otel Sapanca'da palmiyeler arasında turkuaz havuz ve otel binası",
 "desc":"Sapanca mı Abant mı Bolu mu? İstanbul'dan mesafe, rakım, iklim, tren erişimi ve mevsim tek tabloda. Kısa kaçamak için Sapanca, kar için Abant.",
 "related":["istanbula-yakin-doga-kacamagi","sapanca-nerede-kalinir-bolge-rehberi","sapancada-sonbahar-rehberi"],
 "lead":"Sapanca mı Abant mı Bolu mu sorusunun kısa cevabı: İstanbul'a en yakın seçenek <strong>Sapanca</strong>'dır; Anadolu Yakası'ndan yaklaşık 125–135 km ve 1,5–2 saat. <strong>Abant Gölü</strong> yaklaşık 258 km uzaktadır, 1.328 metre rakımdadır ve kışın kar, sonbaharda renk arayanlara hitap eder. <strong>Bolu</strong>'nun Gölcük ve Yedigöller gibi orman rotaları ise 3–4 saatlik yol ister. Bir gecelik kaçamak, tren seçeneği ve göl kıyısında konfor için Sapanca; kar garantisi ve yüksek yayla havası için Abant/Bolu mantıklıdır.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Sapanca:</strong> ~125–135 km, 1,5–2 saat; göl 33 m rakımda, ılıman; trenle de ulaşılır.</li>
<li><strong>Abant:</strong> ~258 km, ~3–3,5 saat; 1.328 m rakımda milli park; kışın karlı, sonbaharda renkli.</li>
<li><strong>Bolu (Gölcük / Yedigöller):</strong> ~260–290 km, 3–4 saat; orman ve tabiat parkı rotaları.</li>
</ul></div>
<h2>Bir bakışta karşılaştırma</h2>
<table><thead><tr><th>Ölçüt</th><th>Sapanca</th><th>Abant</th><th>Bolu (Gölcük / Yedigöller)</th></tr></thead><tbody>
<tr><td>İstanbul'dan mesafe</td><td>~125–135 km</td><td>~258 km</td><td>~260–290 km</td></tr>
<tr><td>Araçla süre</td><td>1,5–2 saat</td><td>~3–3,5 saat</td><td>3–4 saat</td></tr>
<tr><td>Rakım</td><td>Göl ~33 m</td><td>Göl ~1.328 m</td><td>Yayla ve orman, yüksek rakım</td></tr>
<tr><td>Trenle ulaşım</td><td>Var (Ada Ekspresi / YHT+Arifiye)</td><td>Yok (karayolu)</td><td>Yok (karayolu)</td></tr>
<tr><td>Kış</td><td>Ilıman göl; kayak için Kartepe 25–30 dk</td><td>Karlı göl manzarası</td><td>Karlı orman</td></tr>
<tr><td>Öne çıkan</td><td>Göl, teleferik, Maşukiye, Ormanya</td><td>Göl çevresi yürüyüş, sonbahar renkleri</td><td>Tabiat parkları, uzun orman yürüyüşü</td></tr>
<tr><td>Kime uygun</td><td>Bir-iki gecelik kaçamak, çiftler, aileler</td><td>Kar ve yüksek yayla isteyenler</td><td>Doğa yürüyüşü ve fotoğraf tutkunları</td></tr>
</tbody></table>
<p class="note">Mesafeler OpenStreetMap rotalamasıyla Kadıköy'den hesaplanmıştır; Abant için Wikipedia'daki 258 km değeri esas alınmıştır. Süreler trafiksiz koşullar içindir.</p>
<h2>Sapanca: İstanbul'a en yakın göl kaçamağı</h2>
<p>Sapanca'nın en büyük kozu erişimidir. Otoyoldan çıktıktan birkaç dakika sonra göl kıyısındasınız; araç yoksa bile <a href="/blog/istanbuldan-trenle-sapanca/">trenle gelmek</a> mümkün. Bu yakınlık, cuma akşamı yola çıkıp cumartesi sabahını gölde geçirmeyi gerçekçi kılar. Bölgede tek bir "doğa noktası" yok; dar bir çapta pek çok farklı deneyim var:</p>
<ul>
<li><strong>Göl:</strong> yaklaşık 45 km² yüzölçümlü Sapanca Gölü'nde kıyı yürüyüşü, bisiklet, SUP.</li>
<li><strong>Teleferik:</strong> Kırkpınar'dan 1.501 metrelik hatla göle kuşbakışı. <a href="/blog/sapanca-teleferik-rehberi/">Teleferik rehberi</a></li>
<li><strong>Orman ve şelale:</strong> <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a> 10–15 dakika, <a href="/blog/ormanya-rehberi/">Ormanya</a> yaklaşık 15 dakika.</li>
<li><strong>Kar ve kayak:</strong> Kartepe 25–30 dakika. <a href="/blog/kartepe-kayak-merkezi-rehberi/">Kartepe kayak rehberi</a></li>
</ul>
<p>İklim tarafında Sapanca ılımandır: Adapazarı'nın 1991–2020 normallerine göre temmuzda ortalama en yüksek sıcaklık 30 °C civarında, ocakta ortalama en düşük 3,5 °C civarındadır. Bu da Sapanca'yı dört mevsim gidilebilen ama kar garantisi olmayan bir yer yapar.</p>
<h2>Abant: yüksek yaylada göl</h2>
<p>Bolu'nun 34 km güneybatısındaki <strong>Abant Gölü</strong>, 1.328 metre rakımda yer alır ve 10 Haziran 2022'de milli park ilan edilmiştir. Göl çevresindeki yürüyüş yolu, sonbaharda sararan ağaçlar ve kışın karla kaplanan manzarasıyla bilinir. İstanbul'dan yaklaşık 258 km uzakta olduğu için bir gecelik bir kaçamakta yolda geçen süre belirgin şekilde artar; Abant'ı iki gece ve üzeri bir planla düşünmek daha keyiflidir.</p>
<h2>Bolu: Gölcük ve Yedigöller</h2>
<p>Bolu merkezine yakın <strong>Gölcük Tabiat Parkı</strong> ve daha kuzeydeki <strong>Yedigöller</strong>, uzun orman yürüyüşleri ve fotoğraf için tercih edilir. Yedigöller'e giden yolun son kısmı orman yoludur; kış koşullarında erişim zorlaşabilir. İstanbul'dan 3–4 saatlik yolculuk nedeniyle hafta sonu programında yolda geçen süre yine önemli bir pay alır.</p>
""" + fig("/assets/web/editorial/ONN09440","DİDİ Otel Sapanca bahçesinde beyaz perdeli ahşap cabanalar ve yeşil çim","Sapanca'nın avantajı: yolda değil bahçede geçen zaman. DİDİ Otel'in cabanalı bahçesi.") + """
<h2>Hangi mevsimde hangisi daha iyi?</h2>
<table><thead><tr><th>Mevsim</th><th>Sapanca</th><th>Abant</th><th>Bolu</th></tr></thead><tbody>
<tr><td>İlkbahar</td><td>Gür şelaleler, yeşil kıyı</td><td>Serin, yer yer kar kalıntısı</td><td>Orman canlanır</td></tr>
<tr><td>Yaz</td><td>Havuz, SUP, gün batımı</td><td>Serin yayla havası</td><td>Kamp ve yürüyüş</td></tr>
<tr><td>Sonbahar</td><td>Renk değiştiren ormanlar, sakin göl</td><td>Renklerin zirvesi</td><td>Yedigöller fotoğraf sezonu</td></tr>
<tr><td>Kış</td><td>Ilıman göl + Kartepe'de kayak</td><td>Karlı göl</td><td>Karlı orman</td></tr>
</tbody></table>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="kisa">Bir gece</button><button data-tab="uzun">Uzun hafta sonu</button><button data-tab="sonbahar">Sonbahar</button></div>
<div class="itin-panel on" data-tab="kisa"><p>Tek gecelik bir plan yapıyorsanız Sapanca açık ara en pratik seçenektir: dönüş günü bile Maşukiye ya da teleferik için vakit kalır. Örnek akış için <a href="/blog/sapancada-1-gunluk-2-gunluk-gezi-plani/">1 ve 2 günlük plan</a>.</p></div>
<div class="itin-panel" data-tab="uzun"><p>Üç gün varsa iki seçenek mantıklı: ya Sapanca'yı üs yapıp Kartepe, Kuzuluk ve Taraklı'yı eklemek (<a href="/blog/sapanca-3-gun-uzun-hafta-sonu-plani/">3 günlük plan</a>), ya da yola göze alıp Abant/Bolu'ya gitmek.</p></div>
<div class="itin-panel" data-tab="sonbahar"><p>Sonbahar renkleri Abant'ta ünlüdür, ancak Sapanca çevresindeki ormanlar da ekim sonundan itibaren renklenir ve yarı mesafededir. Ayrıntılar <a href="/blog/sapancada-sonbahar-rehberi/">Sapanca sonbahar rehberimizde</a>.</p></div>
</div>
<h2>Neden çoğu İstanbullu hafta sonu için Sapanca'yı seçiyor?</h2>
<p>Yakınlık, tren seçeneği, göl ile dağın iç içe olması ve konaklama çeşitliliği Sapanca'yı İstanbul çevresinin en pratik doğa kaçamağı yapar. Göl kıyısında sakin bir yer arıyorsanız Kırkpınar'daki <a href="/#konum">DİDİ Otel Sapanca</a>; konaklamaya dahil kahvaltı, sezonda Sapanca'nın tek klorsuz havuzu ve bahçedeki <a href="/#mare">Mare Gastro</a> ile size yolda değil doğada geçen bir hafta sonu sunar. Bölgeler arasında kararsızsanız <a href="/blog/sapanca-nerede-kalinir-bolge-rehberi/">Sapanca'da nerede kalınır</a> rehberine bakın.</p>
<h2>Karar verirken kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="karsilastirma">
<label><input type="checkbox"><span><b>Ne kadar yolculuğu göze alıyorum?</b><span>2 saatin altı için Sapanca.</span></span></label>
<label><input type="checkbox"><span><b>Kaç gece kalacağım?</b><span>Bir gece için Sapanca, üç gece ve üzeri için Abant/Bolu da olur.</span></span></label>
<label><input type="checkbox"><span><b>Kar istiyor muyum?</b><span>Kar garantisi için Abant ya da Kartepe.</span></span></label>
<label><input type="checkbox"><span><b>Araçsız mı geleceğim?</b><span>Trenle yalnızca Sapanca'ya kolay ulaşılır.</span></span></label>
<label><input type="checkbox"><span><b>Aktivite çeşitliliği önemli mi?</b><span>Göl, teleferik, şelale ve kayak bir arada: Sapanca.</span></span></label>
</div>
<p>Kararınızı verdiyseniz müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%20hafta%20sonu%20i%C3%A7in%20m%C3%BCsaitlik%20sormak%20istiyorum.">WhatsApp'tan</a> yazabilir ya da <a href="/odalar/">oda tiplerimizi</a> inceleyebilirsiniz.</p>
""",
 "sources":[("Lake Abant — rakım, mesafe, milli park statüsü (Wikipedia)","https://en.wikipedia.org/wiki/Lake_Abant"),
            ("Lake Sapanca — yüzölçümü ve rakım (Wikipedia)","https://en.wikipedia.org/wiki/Lake_Sapanca"),
            ("Adapazarı iklim verileri 1991–2020, MGM kaynaklı (Wikipedia)","https://en.wikipedia.org/wiki/Adapazar%C4%B1"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("Sapanca mı Abant mı daha iyi?","Kısa bir kaçamak ve kolay ulaşım istiyorsanız Sapanca (~1,5–2 saat) daha avantajlıdır. Kar ve yüksek yayla havası önceliğinizse 1.328 m rakımdaki Abant (~258 km) tercih edilebilir."),
        ("İstanbul'a en yakın doğa kaçamağı hangisi?","Üçü arasında İstanbul'a en yakını Sapanca'dır; Anadolu Yakası'ndan yaklaşık 125–135 km ve 1,5–2 saattir."),
        ("Abant İstanbul'a kaç km?","Abant Gölü Milli Parkı İstanbul'a yaklaşık 258 km uzaklıktadır; araçla trafiksiz yaklaşık 3–3,5 saat sürer."),
        ("Kışın hangisi daha iyi?","Karlı göl manzarası için Abant öne çıkar. Sapanca'nın gölü ılımandır ama 25–30 dakika uzaklıktaki Kartepe'de kayak yapılabilir; böylece konforlu bir göl konaklamasıyla karı birleştirebilirsiniz."),
        ("Trenle hangisine gidilebilir?","Üçü arasında trenle doğrudan ulaşılabilen tek yer Sapanca'dır: Ada Ekspresi Sapanca garında durur, YHT ise yakındaki Arifiye'de iner."),
        ("Çiftler için hangisi uygun?","Kısa romantik kaçamaklar için Sapanca'nın göl kıyısı, teleferiği ve butik otelleri pratiktir; daha uzun ve sakin bir plan için Abant da güzel bir seçenektir.")],
},
{
 "slug":"sapanca-3-gun-uzun-hafta-sonu-plani","cat":"Gezi Planı","img":"havuz-restoran","date":"2026-08-26",
 "title":"Sapanca'da 3 Gün: Uzun Hafta Sonu ve Bayram Tatili Planı",
 "desc":"Sapanca'da 3 günlük gezi planı: göl ve teleferik, Maşukiye ve Kartepe, Poyrazlar ve Acarlar Longozu. Uzun hafta sonu ve bayram için saat saat rota; DİDİ Otel merkezli.",
 "lead":"Sapanca'da 3 günlük planın kısa hali: birinci gün göl kıyısı ve teleferik, ikinci gün Maşukiye, Kartepe ve Acarlar Longozu, üçüncü gün Poyrazlar Gölü ve Kuzuluk kaplıcaları. Uzun bir hafta sonu ya da bayram tatili için ideal bu rota, her günü göl kıyısındaki <a href=\"/#konum\">DİDİ Otel Sapanca</a>'da başlatıp bitirir.",
 "body":"""
<h2>3 günde Sapanca: rotanın özeti</h2>
<p>İki günlük plana bir gün daha eklemek, Sapanca'yı acele etmeden keşfetmenizi sağlar. İlk gün göl ve teleferik gibi klasikleri, ikinci gün Kartepe ve Acarlar Longozu gibi çevre rotaları, üçüncü gün ise sakin köşeleri ve termali kapsar. Aşağıdaki plan saat saat düzenlenmiştir; dilediğiniz gibi esnetebilirsiniz. Daha kısa bir ziyaret için <a href="/blog/sapancada-1-gunluk-2-gunluk-gezi-plani/">1 ve 2 günlük plana</a> bakabilirsiniz.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="g1">1. Gün</button><button data-tab="g2">2. Gün</button><button data-tab="g3">3. Gün</button></div>
<div class="itin-panel on" data-tab="g1">
<div class="timeline">
<div class="tl-step"><div class="tl-time">09:00</div><h4>DİDİ Otel'de kahvaltı</h4><p>Güne göl manzarasına karşı zengin bir kahvaltıyla başlayın.</p></div>
<div class="tl-step"><div class="tl-time">10:30</div><h4>Göl kıyısı ve Uzunkum Parkı</h4><p>Göl kenarında yürüyüş, isterseniz bisiklet turu.</p></div>
<div class="tl-step"><div class="tl-time">12:30</div><h4><a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'de alabalık molası</h4><p>Dere kenarında kiremitte alabalık için ideal saat.</p></div>
<div class="tl-step"><div class="tl-time">14:30</div><h4><a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a> ile Mahmudiye</h4><p>Kırkpınar'dan binip seyir terasında göl manzarasının tadını çıkarın.</p></div>
<div class="tl-step"><div class="tl-time">19:30</div><h4><a href="/#mare">Mare Gastro</a>'da akşam yemeği</h4><p>Bahçede göl havasında ilk günü tamamlayın.</p></div>
</div>
</div>
<div class="itin-panel" data-tab="g2">
<div class="timeline">
<div class="tl-step"><div class="tl-time">09:30</div><h4>Kahvaltı sonrası Kartepe'ye çıkış</h4><p>Yazın yürüyüş parkurları, kışın kayak ve telesiyej.</p></div>
<div class="tl-step"><div class="tl-time">13:00</div><h4>Öğle molası</h4><p>Dağ havasında bir öğle yemeği ve dinlenme.</p></div>
<div class="tl-step"><div class="tl-time">15:00</div><h4>Acarlar Longozu'nda kano</h4><p>Su üzerinde, longoz ormanı içinde huzurlu bir gezinti.</p></div>
<div class="tl-step"><div class="tl-time">19:00</div><h4>Otelde havuz ve akşam yemeği</h4><p>Günü <a href="/blog/sapancada-havuzlu-otel/">klorsuz havuzda</a> ve Mare Gastro'da kapatın.</p></div>
</div>
</div>
<div class="itin-panel" data-tab="g3">
<div class="timeline">
<div class="tl-step"><div class="tl-time">09:30</div><h4>Kahvaltı sonrası <a href="/blog/poyrazlar-golu-mahmudiye-gizli-koseler/">Poyrazlar Gölü</a></h4><p>Sessiz doğada tekne turu ya da kısa yürüyüş.</p></div>
<div class="tl-step"><div class="tl-time">12:30</div><h4>Kuzuluk kaplıcaları ya da köy pazarı</h4><p>Termal bir mola ya da Mahmudiye'de yerel ürün alışverişi.</p></div>
<div class="tl-step"><div class="tl-time">15:00</div><h4>İsteğe bağlı: <a href="/blog/tarakli-geyve-gunubirlik-tur/">Taraklı ve Geyve</a></h4><p>Zaman uygunsa günübirlik tarihi kasaba turu.</p></div>
<div class="tl-step"><div class="tl-time">17:00</div><h4>Veda ve dönüş</h4><p>Üç günlük rotayı göl kıyısında son bir molayla tamamlayın.</p></div>
</div>
</div>
</div>
<h2>Bayram ve uzun tatil için notlar</h2>
<p>Bayram ve resmi tatil dönemlerinde Sapanca yoğunlaşır; bu tarihlerde göl kıyısı konaklamaları erken dolar. Uzun bir tatil planlıyorsanız <a href="https://wa.me/905331350888?text=Sapanca%27da%203%20g%C3%BCnl%C3%BCk%20konaklama%20i%C3%A7in%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> önceden tarih ayırtmanız önerilir. Ne yeneceğinizi merak ediyorsanız <a href="/blog/sapancada-ne-yenir/">Sapanca'da ne yenir</a> rehberimiz yol gösterir.</p>
<h2>3 günlük paketleme kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="uc-gun-plan">
<label><input type="checkbox"><span><b>Rahat yürüyüş ayakkabısı</b><span>Göl kıyısı ve doğa yürüyüşleri için.</span></span></label>
<label><input type="checkbox"><span><b>Mayo ve havlu</b><span>Klorsuz havuz keyfi için.</span></span></label>
<label><input type="checkbox"><span><b>Mevsime uygun kıyafet</b><span>Kartepe'de hava serin olabilir.</span></span></label>
<label><input type="checkbox"><span><b>Fotoğraf makinesi / şarj</b><span>Gün batımı ve teleferik kareleri için.</span></span></label>
<label><input type="checkbox"><span><b>Konaklama rezervasyonu</b><span>Bayramda erken ayırtın.</span></span></label>
<label><input type="checkbox"><span><b>Mare Gastro rezervasyonu</b><span>Akşam yemekleri için yer ayırtın.</span></span></label>
</div>
<p>Üç gün boyunca tüm duraklara kısa mesafede olan <a href="/#konum">DİDİ Otel Sapanca</a>, göl kıyısındaki sakin konumuyla rotanızın merkezi olur.</p>
""",
 "faq":[("Sapanca 3 günde neler gezilir?","İlk gün göl kıyısı, Maşukiye ve teleferik; ikinci gün Kartepe ve Acarlar Longozu; üçüncü gün Poyrazlar Gölü ve Kuzuluk kaplıcaları rahatça gezilebilir."),
        ("3 günlük Sapanca gezisinde nerede kalınmalı?","Tüm duraklara kısa mesafedeki Kırkpınar'da, göl kıyısındaki DİDİ Otel Sapanca üç günlük rota için merkezi bir seçenektir."),
        ("Bayramda Sapanca kalabalık olur mu?","Evet, bayram ve resmi tatillerde Sapanca yoğunlaşır ve göl kıyısı konaklamaları erken dolar; erken rezervasyon önerilir."),
        ("Çocuklu aileler için 3 günlük plan uygun mu?","Evet; göl kıyısı, teleferik, havuz ve Poyrazlar doğası çocuklu aileler için keyifli ve dengeli bir tempo sunar."),
        ("Rotaya ekleme yapılabilir mi?","Elbette; üçüncü güne Taraklı ve Geyve günübirlik tarihi turu ya da fotoğraf noktaları eklenebilir.")],
},
{
 "slug":"sapancada-kisin-gezilecek-yerler","cat":"Mevsimler","img":"ONN09446","date":"2026-08-26",
 "title":"Sapanca'da Kışın Gezilecek Yerler ve Kar Keyfi",
 "desc":"Sapanca'da kışın gezilecek yerler: Kartepe'de kayak, karlı göl kıyısı yürüyüşleri, Maşukiye ve Kuzuluk kaplıcaları. Kış tatili için eksiksiz rehber ve konaklama önerisi.",
 "lead":"Sapanca'da kışın gezilecek yerlerin başında Kartepe Kayak Merkezi, karla kaplı göl kıyısı, Maşukiye'nin beyaz vadileri ve Kuzuluk kaplıcaları gelir. Aralık–Şubat arası kar yağışıyla bembeyaz bir tabloya dönüşen bölge, kayaktan termal molalara, karlı yürüyüşlerden göl kıyısında sıcak içeceklere kadar keyifli bir kış kaçamağı sunar.",
 "body":"""
<h2>Kartepe Kayak Merkezi: kışın ilk durağı</h2>
<p>Sapanca'dan yaklaşık <strong>30 dakika</strong> mesafedeki <strong>Kartepe Kayak Merkezi</strong>, kış aylarının en gözde adresidir. Samanlı Dağları'nın zirvesinde kayak, snowboard ve telesiyej ile Sapanca Gölü manzarası bir arada yaşanır. Kar sezonu genellikle Aralık'tan Mart'a kadar sürer. Ayrıntılı rota için <a href="/blog/masukiye-kartepe-gezi/">Maşukiye ve Kartepe gezi</a> rehberimize bakabilirsiniz.</p>
<h2>Karla kaplı göl kıyısı ve Maşukiye</h2>
<p>Kış, göl çevresine ayrı bir sessizlik getirir. Karla kaplanan göl kıyısında yürüyüş yapmak ve <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'nin beyaz vadilerini görmek, kışın en huzurlu deneyimlerindendir. Kar yağışının ardından bölge, fotoğraf için de büyüleyici kareler sunar; en iyi noktalar için <a href="/blog/sapancada-fotograf-gun-batimi-noktalari/">fotoğraf rehberimize</a> göz atın.</p>
<h2>Kuzuluk kaplıcaları: kışın en iyi mola</h2>
<p>Soğuk havada ısınmanın en keyifli yolu, Sapanca'ya yaklaşık 45 dakika mesafedeki <strong>Kuzuluk kaplıcaları</strong>nda şifalı termal sulara girmektir. Kış tatiline dinlendirici bir wellness molası eklemek isteyenler için idealdir.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="aktif">Aktif olanlar</button><button data-tab="huzur">Huzur arayanlar</button></div>
<div class="itin-panel on" data-tab="aktif"><p>Kartepe'de kayak ve snowboard, ardından karlı orman yürüyüşü. Gün sonunda otelde sıcak bir mola ve göl havasında bir akşam yemeği.</p></div>
<div class="itin-panel" data-tab="huzur"><p>Kuzuluk'ta termal, göl kıyısında sakin bir yürüyüş ve şöminemsi bir akşam. Kar manzarasına karşı dinlenmek isteyenler için sakin bir tempo.</p></div>
</div>
<h2>Kışın Sapanca'da nerede kalınır?</h2>
<p>Kış aylarında göl kıyısındaki sakin bir konaklama, hem manzara hem de tüm duraklara yakınlık açısından avantajlıdır. <a href="/#konum">DİDİ Otel Sapanca</a>, Kırkpınar'da göl ile orman arasında, <a href="/#mare">Mare Gastro</a> restoranıyla kışın da sıcak bir kaçış sunar. Konaklama bölgelerini karşılaştırmak için <a href="/blog/sapanca-nerede-kalinir-bolge-rehberi/">nerede kalınır</a> rehberimize, mevsimlere göre plan için <a href="/blog/sapanca-hangi-mevsim-gidilir/">hangi mevsim gidilir</a> yazımıza bakabilirsiniz.</p>
<h2>Kış gezisi kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="kis-gezi">
<label><input type="checkbox"><span><b>Kalın ve su geçirmez giysi</b><span>Kar ve soğuk için katmanlı giyinin.</span></span></label>
<label><input type="checkbox"><span><b>Kaymaz ayakkabı / bot</b><span>Karlı zeminde güvenli yürüyüş.</span></span></label>
<label><input type="checkbox"><span><b>Kartepe kar durumu kontrolü</b><span>Gitmeden hava ve pist durumunu öğrenin.</span></span></label>
<label><input type="checkbox"><span><b>Termal için mayo ve havlu</b><span>Kuzuluk kaplıcaları molası için.</span></span></label>
<label><input type="checkbox"><span><b>Konaklama rezervasyonu</b><span>Kar sezonunda erken ayırtın.</span></span></label>
</div>
""",
 "faq":[("Sapanca'da kışın nereler gezilir?","Kartepe Kayak Merkezi, karla kaplı göl kıyısı ve Uzunkum Parkı, Maşukiye'nin beyaz vadileri ve Kuzuluk kaplıcaları kışın öne çıkan duraklardır."),
        ("Sapanca'ya kar ne zaman yağar?","Kar yağışı genellikle Aralık ile Şubat arasında görülür; Kartepe'de kayak sezonu Mart'a kadar uzayabilir."),
        ("Kartepe Sapanca'ya ne kadar uzaklıkta?","Kartepe Kayak Merkezi, Sapanca'ya yaklaşık 30 dakika mesafededir."),
        ("Kışın Sapanca'da ne yapılır?","Kayak ve snowboard, karlı göl kıyısı yürüyüşleri, Kuzuluk'ta termal mola ve göl havasında sıcak bir akşam yemeği kışın öne çıkan aktivitelerdir."),
        ("Kışın Sapanca'da konaklama önerisi nedir?","Göl kıyısındaki Kırkpınar'da, tüm duraklara yakın DİDİ Otel Sapanca kış tatili için sakin ve merkezi bir seçenektir.")],
},
{
 "slug":"acarlar-longozu-rehberi","cat":"Doğa","img":"ONN09442","date":"2026-08-26",
 "title":"Acarlar Longozu: Kano ve Doğa Keşfi Rehberi",
 "desc":"Acarlar Longozu rehberi: Türkiye'nin en önemli longoz ormanlarından biri; kano ve sandalla su üzerinde doğa turu, kuş gözlemi ve nilüferler. Sapanca'dan günübirlik doğa kaçamağı.",
 "lead":"Acarlar Longozu, su ile ormanın iç içe geçtiği, Türkiye'nin en büyük longoz ormanlarından biridir. Kano ve sandalla su üzerinde sessiz bir gezinti yapabilir, yüzlerce kuş türünü ve su nilüferlerini gözlemleyebilirsiniz. Sapanca'ya yaklaşık bir saat mesafedeki longoz, doğa ve fotoğraf tutkunları için eşsiz bir günübirlik kaçamaktır.",
 "body":"""
<h2>Acarlar Longozu nedir?</h2>
<p><strong>Acarlar Longozu</strong>, taban suyu yüksek, ağaçların suyun içinden yükseldiği nadir bir sulak orman ekosistemidir. Türkiye'nin en büyük longoz ormanlarından biri olarak kabul edilir ve binlerce bitki türü ile yüzlerce kuş türüne ev sahipliği yapar. Su nilüferleri, menekşeler ve renkli bitki örtüsü, longozu adeta bir doğa tablosuna dönüştürür.</p>
<h2>Longozda neler yapılır?</h2>
<p>Longozun en özel deneyimi, <strong>kano veya sandalla</strong> su kanalları boyunca ilerlemektir. Sessiz suyun üzerinde ağaçların arasından geçmek, kuş sesleri eşliğinde huzurlu bir doğa molası sunar. Fotoğraf tutkunları için nilüferler ve kuşlar zengin bir kare çeşitliliği yaratır. Kuş gözlemi meraklıları için ise longoz, sabah erken saatlerde en canlı halindedir.</p>
<h2>Sapanca'dan Acarlar Longozu'na</h2>
<p>Longoz, Sapanca'ya yaklaşık bir saat mesafededir ve rahatça günübirlik gezilebilir. Doğa yürüyüşü ve <a href="/blog/poyrazlar-golu-mahmudiye-gizli-koseler/">Poyrazlar Gölü</a> gibi sakin köşeleri seven gezginler için ideal bir tamamlayıcıdır. Sapanca çevresindeki diğer doğa rotaları için <a href="/blog/sapancada-gezilecek-yerler/">gezilecek yerler</a> rehberimize bakabilirsiniz.</p>
<h3>Gitmeden önce bilinmesi gerekenler</h3>
<table><thead><tr><th>Konu</th><th>Öneri</th></tr></thead><tbody>
<tr><td>En iyi zaman</td><td>İlkbahar ve yaz; sabah erken saatler</td></tr>
<tr><td>Aktivite</td><td>Kano / sandal turu, kuş gözlemi, fotoğraf</td></tr>
<tr><td>Yanınıza alın</td><td>Güneş koruması, su, dürbün, fotoğraf makinesi</td></tr>
<tr><td>Sapanca'dan</td><td>Yaklaşık 1 saat</td></tr>
</tbody></table>
<p>Doğayla iç içe bir günün ardından göl kıyısındaki <a href="/#konum">DİDİ Otel Sapanca</a>'da dinlenip akşamı <a href="/#mare">Mare Gastro</a>'da tamamlayabilirsiniz.</p>
""",
 "faq":[("Acarlar Longozu nerede?","Sakarya'da, Sapanca'ya yaklaşık bir saat mesafede yer alan, su ile ormanın iç içe geçtiği bir sulak orman alanıdır."),
        ("Acarlar Longozu'nda ne yapılır?","Kano ve sandalla su üzerinde doğa turu, kuş gözlemi ve fotoğrafçılık longozun en sevilen aktiviteleridir."),
        ("Longozu gezmek için en iyi zaman nedir?","İlkbahar ve yaz ayları, özellikle sabahın erken saatleri doğanın en canlı olduğu zamanlardır."),
        ("Acarlar Longozu Sapanca'dan günübirlik gezilir mi?","Evet, Sapanca'ya yaklaşık bir saat mesafede olduğu için rahatça günübirlik gezilebilir.")],
},
{
 "slug":"kuzuluk-kaplicalari-rehberi","cat":"Termal","img":"havuz1","date":"2026-08-26","mod":"2026-11-16",
 "title":"Kuzuluk Kaplıcaları Rehberi: Sapanca'dan Termal Mola",
 "seo_title":"Kuzuluk Kaplıcaları: Sapanca'dan Termal Mola Rehberi",
 "img_alt":"DİDİ Otel Sapanca'nın açık havuzu ve palmiyeler",
 "desc":"Kuzuluk kaplıcaları nerede, suyu kaç derece, Sapanca'dan kaç dakika? Akyazı'daki termal kaynak, sağlık uyarıları ve Sapanca + Kuzuluk hafta sonu planı.",
 "related":["sapancada-kisin-gezilecek-yerler","sapancada-yagmurlu-havada-ne-yapilir","sapanca-3-gun-uzun-hafta-sonu-plani"],
 "lead":"Kuzuluk kaplıcaları, Sakarya'nın Akyazı ilçesine bağlı Kuzuluk'ta, Kırkpınar'dan karayoluyla yaklaşık 47 km (35–45 dakika) uzaklıktadır. Akademik bir jeoloji çalışmasına göre kaynağın yüzey sıcaklığı yaklaşık <strong>51 °C</strong>, debisi saniyede 42 litredir; bu sıcak su bölgedeki termal tesislerde havuz ve kabinlere verilir. Sapanca'da konaklayıp bir öğleden sonrayı Kuzuluk'a ayırmak, özellikle sonbahar ve kış hafta sonlarında doğa gezisini dinlendirici bir molayla dengelemenin en pratik yoludur.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Konum:</strong> Kuzuluk, Akyazı / Sakarya — Kırkpınar'dan ~47 km, 35–45 dk.</li>
<li><strong>Su:</strong> Kaynak yüzey sıcaklığı ~51 °C (akademik ölçüm); havuz sıcaklığı tesise göre değişir.</li>
<li><strong>En iyi dönem:</strong> Sonbahar ve kış; yağmurlu günlerin en iyi B planı.</li>
<li><strong>Sağlık:</strong> Kronik rahatsızlığı olanlar ve hamileler önce hekime danışmalı.</li>
</ul></div>
<h2>Kuzuluk kaplıcaları nerede ve Sapanca'dan nasıl gidilir?</h2>
<p>Kuzuluk, Adapazarı'nın doğusunda, Akyazı ilçesine bağlı bir yerleşimdir. Kırkpınar'dan Anadolu Otoyolu (TEM) üzerinden doğuya ilerleyip Akyazı yönüne saparak ulaşırsınız; harita rotalamasına göre yol yaklaşık 47 km ve trafiksiz 35 dakika civarındadır. Hafta sonu öğleden sonraları ve bayramlarda bölgede yoğunluk olabildiği için 45 dakika hesaplamak daha gerçekçidir.</p>
<table><thead><tr><th>Nereden</th><th>Mesafe</th><th>Yaklaşık süre</th></tr></thead><tbody>
<tr><td>Kırkpınar / DİDİ Otel</td><td>~47 km</td><td>35–45 dk</td></tr>
<tr><td>İstanbul (Kadıköy)</td><td>~165 km</td><td>~2–2,5 saat</td></tr>
</tbody></table>
<h2>Kuzuluk'un suyu kaç derece?</h2>
<p>Kuzuluk'un termal suyu üzerine yapılmış bir jeoloji çalışmasında kaynağın yüzeydeki sıcaklığı <strong>51 °C</strong>, debisi ise <strong>saniyede 42 litre</strong> olarak verilir. Tesislerdeki havuz suyu, kaynak suyunun soğutulması ve karıştırılmasıyla kullanıma uygun sıcaklığa getirilir; havuz sıcaklığını gitmeden önce tesise sormanızı öneririz.</p>
<h2>Kuzuluk'ta hangi tesisler var?</h2>
<p>Kuzuluk'ta günübirlik havuz ve kabin hizmeti veren işletmelerin yanı sıra konaklamalı termal oteller de bulunur; örneğin İhlas grubuna ait Kuzuluk Termal bölgedeki bilinen tesislerden biridir. Günübirlik giriş koşulları, fiyatlar ve aile/özel kabin seçenekleri işletmeden işletmeye değiştiği için burada fiyat vermiyoruz; telefonla sormak en sağlıklısıdır.</p>
<h2>Termal sular neye iyi gelir?</h2>
<p>Sıcak suyun kas gerginliğini azalttığı ve rahatlattığı genel olarak bilinir; ancak termal suyun belirli bir hastalığa "iyi geldiği" iddiaları için hekim görüşü esastır. Kalp-damar rahatsızlığı, yüksek tansiyon, hamilelik ya da açık yara gibi durumlarda termal havuza girmeden önce doktorunuza danışın. Sağlıklı yetişkinler için de genel kural aynıdır: sıcak suda bir seferde uzun kalmayın, aralarda dinlenin ve bol su için.</p>
""" + fig("/assets/web/editorial/havuz-restoran","DİDİ Otel Sapanca'da havuz kenarında şemsiyeler ve palmiyeler, ön planda restoran masası","Termal molanın ardından Sapanca'ya dönüş: DİDİ Otel, Kırkpınar.") + """
<h2>Sapanca + Kuzuluk hafta sonu planı</h2>
<table><thead><tr><th>Zaman</th><th>Cumartesi</th><th>Pazar</th></tr></thead><tbody>
<tr><td>Sabah</td><td>Kahvaltı, göl kıyısında yürüyüş</td><td>Kahvaltı, teleferik (11:00'de açılır)</td></tr>
<tr><td>Öğle</td><td>Maşukiye'de alabalık</td><td>Kuzuluk'a hareket (~40 dk)</td></tr>
<tr><td>Öğleden sonra</td><td>Ormanya ya da Kartepe</td><td>Termal havuz ve dinlenme</td></tr>
<tr><td>Akşam</td><td>Mare Gastro'da akşam yemeği</td><td>Kuzuluk'tan doğrudan İstanbul'a dönüş</td></tr>
</tbody></table>
<p>Pazar günü Kuzuluk'u dönüş yoluna koymak mantıklıdır: termal sonrası rahatlamış bir şekilde TEM'e çıkıp İstanbul'a dönebilirsiniz. Daha uzun bir program için <a href="/blog/sapanca-3-gun-uzun-hafta-sonu-plani/">3 günlük plan</a> rehberimize bakın.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="son">Sonbahar</button><button data-tab="kis">Kış</button><button data-tab="yag">Yağmurlu gün</button></div>
<div class="itin-panel on" data-tab="son"><p>Kasımda Sapanca'da gündüz ortalama en yüksek sıcaklık 17 °C civarında; renkli ormanlarda yürüyüşü sıcak bir havuzla bitirmek için ideal. <a href="/blog/sapancada-sonbahar-rehberi/">Sonbahar rehberi</a></p></div>
<div class="itin-panel" data-tab="kis"><p>Kartepe'de kayak sonrası kasları dinlendirmek için Kuzuluk'a uğramak iyi bir kombinasyondur. <a href="/blog/sapancada-kisin-gezilecek-yerler/">Kışın gezilecek yerler</a></p></div>
<div class="itin-panel" data-tab="yag"><p>Yağmur yürüyüş planınızı bozduysa termal havuz en iyi kurtarıcıdır. Diğer fikirler <a href="/blog/sapancada-yagmurlu-havada-ne-yapilir/">yağmurlu havada ne yapılır</a> yazımızda.</p></div>
</div>
<h2>Termal mola için yanınıza alın</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="kuzuluk">
<label><input type="checkbox"><span><b>Mayo, terlik ve bone</b><span>Bazı tesislerde bone istenebilir.</span></span></label>
<label><input type="checkbox"><span><b>Havlu ve yedek kıyafet</b><span>Tesiste kiralık olup olmadığını sorun.</span></span></label>
<label><input type="checkbox"><span><b>Bol su</b><span>Termal sonrası vücut su kaybeder.</span></span></label>
<label><input type="checkbox"><span><b>Kısa seanslar</b><span>Sıcak suda uzun kalmayın, aralarda dinlenin.</span></span></label>
<label><input type="checkbox"><span><b>Sağlık durumunuz</b><span>Kronik rahatsızlık ve hamilelikte önce hekime danışın.</span></span></label>
<label><input type="checkbox"><span><b>Dönüş öncesi dinlenme</b><span>Termal sonrası direksiyona hemen geçmeyin.</span></span></label>
</div>
<h2>Kuzuluk gezisi için nerede kalınır?</h2>
<p>Kuzuluk'u günübirlik bir mola olarak düşünüp asıl konaklamayı göl kıyısında yapmak, iki deneyimi bir arada yaşatır. Kırkpınar'daki <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur), akşam yemeği için bahçedeki <a href="/#mare">Mare Gastro</a> hemen yanınızdadır. Jakuzili oda seçeneklerimizi <a href="/blog/sapanca-jakuzili-havuzlu-gol-manzarali-oda/">bu yazıda</a> anlattık. Müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%20ve%20Kuzuluk%20gezisi%20i%C3%A7in%20konaklama%20yapmak%20istiyorum.">WhatsApp'tan</a> yazabilirsiniz.</p>
""",
 "sources":[("Kuzuluk termal suyu — sıcaklık ve debi ölçümü (DergiPark, akademik makale)","https://dergipark.org.tr/en/download/article-file/4701238"),
            ("Adapazarı iklim verileri 1991–2020, MGM kaynaklı (Wikipedia)","https://en.wikipedia.org/wiki/Adapazar%C4%B1"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("Kuzuluk kaplıcaları nerede?","Sakarya'nın Akyazı ilçesine bağlı Kuzuluk'tadır; Kırkpınar'dan karayoluyla yaklaşık 47 km, 35–45 dakika uzaklıktadır."),
        ("Kuzuluk kaplıcasının suyu kaç derece?","Akademik bir jeoloji çalışmasına göre kaynağın yüzey sıcaklığı yaklaşık 51 °C, debisi saniyede 42 litredir. Havuzlardaki su kullanıma uygun sıcaklığa getirilir; güncel havuz sıcaklığını tesise sorun."),
        ("Kuzuluk kaplıcaları neye iyi gelir?","Sıcak su rahatlatıcı etkisiyle bilinir; ancak belirli hastalıklara iyi geldiği iddiaları için hekim görüşü esastır. Kronik rahatsızlığınız varsa ya da hamileyseniz önce doktorunuza danışın."),
        ("Kuzuluk Sapanca'dan günübirlik gezilir mi?","Evet. 35–45 dakikalık mesafe sayesinde Sapanca'da konaklayıp bir öğleden sonrayı termale ayırabilir ya da pazar günü dönüş yolunda uğrayabilirsiniz."),
        ("Termal için en iyi mevsim hangisi?","Sonbahar ve kış ayları en keyifli dönemdir; yağmurlu günlerde de iyi bir alternatiftir.")],
},
{
 "slug":"sapanca-bisiklet-yuruyus-parkurlari","cat":"Aktivite","img":"ONN09464","date":"2026-08-26",
 "title":"Sapanca Bisiklet ve Doğa Yürüyüşü Parkurları Rehberi",
 "desc":"Sapanca'da bisiklet ve doğa yürüyüşü parkurları: Uzunkum bisiklet-yürüyüş yolu, göl çevresi rotaları ve tabiat parkı patikaları. Kiralama, mesafeler ve öneriler.",
 "lead":"Sapanca'da bisiklet ve doğa yürüyüşü için en popüler rota, göl kıyısı boyunca uzanan engebesiz Uzunkum bisiklet-yürüyüş yoludur. Göl çevresi, tabiat parkı patikaları ve dere kenarı rotalarıyla Sapanca, her seviyeden bisikletçi ve yürüyüşçü için elverişli bir açık hava sahasıdır.",
 "body":"""
<h2>Uzunkum bisiklet ve yürüyüş yolu</h2>
<p>Göl kıyısındaki <strong>Uzunkum</strong> bölgesinde düzenlenen bisiklet ve yürüyüş yolu, engebesiz zemini sayesinde her yaştan ziyaretçi için rahat bir rota sunar. Göl manzarasına karşı pedal çevirmek ya da yürümek, Sapanca'nın en sevilen açık hava aktivitelerindendir. Göl kıyısında bisiklet kiralama noktaları bulunur.</p>
<h2>Göl çevresi ve tabiat parkı rotaları</h2>
<p>Daha uzun bir tur isteyenler göl çevresini takip edebilir; doğa yürüyüşü sevenler ise Sapanca merkeze yakın <strong>Sakarya İl Orman Tabiat Parkı</strong>'nın yürüyüş ve bisiklet parkurlarını tercih edebilir. Bu rotalar, göl manzarası ve orman havasını bir arada sunar. Gölde yapılabilecek diğer aktiviteler için <a href="/blog/sapanca-golu-aktiviteler/">Sapanca Gölü aktiviteleri</a> rehberimize bakın.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="kolay">Başlangıç</button><button data-tab="orta">Orta seviye</button></div>
<div class="itin-panel on" data-tab="kolay"><p>Uzunkum'un düz ve engebesiz yolunda kısa bir bisiklet turu ya da göl kıyısı yürüyüşü; çocuklu aileler için de idealdir.</p></div>
<div class="itin-panel" data-tab="orta"><p>Göl çevresini takip eden daha uzun bir tur ya da tabiat parkı patikalarında doğa yürüyüşü; biraz daha kondisyon ister ama manzara buna değer.</p></div>
</div>
<h2>Ne zaman ve nasıl?</h2>
<p>Bisiklet ve yürüyüş için en keyifli saatler, sabah erken ve akşamüzeridir; yaz aylarında öğle sıcağından kaçınmak konforu artırır. Su, güneş koruması ve rahat bir ayakkabı yeterlidir. Rotanın hemen yanındaki <a href="/#konum">DİDİ Otel Sapanca</a>, göl kıyısındaki konumuyla aktivitelerinize kısa bir başlangıç noktası sunar; günün sonunda <a href="/blog/sapancada-havuzlu-otel/">klorsuz havuzda</a> dinlenebilirsiniz.</p>
<h2>Aktivite kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="bisiklet-yuruyus">
<label><input type="checkbox"><span><b>Rahat ayakkabı / bisiklet kıyafeti</b><span>Uzun rotalar için konforlu seçin.</span></span></label>
<label><input type="checkbox"><span><b>Su ve güneş koruması</b><span>Özellikle yaz aylarında şart.</span></span></label>
<label><input type="checkbox"><span><b>Sabah ya da akşamüzeri planlayın</b><span>Öğle sıcağından kaçının.</span></span></label>
<label><input type="checkbox"><span><b>Bisiklet kiralama noktası</b><span>Göl kıyısında kiralama mevcut.</span></span></label>
<label><input type="checkbox"><span><b>Rota mesafesini ayarlayın</b><span>Seviyenize uygun uzunluk seçin.</span></span></label>
</div>
""",
 "faq":[("Sapanca'da bisiklet nerede sürülür?","Göl kıyısındaki Uzunkum bisiklet-yürüyüş yolu, engebesiz zemini ve göl manzarasıyla en popüler rotadır."),
        ("Sapanca'da bisiklet kiralanabilir mi?","Evet, göl kıyısındaki noktalarda bisiklet kiralama imkanı bulunur."),
        ("Doğa yürüyüşü için nereyi önerirsiniz?","Uzunkum yolu ile göl kıyısı ve Sapanca merkeze yakın Sakarya İl Orman Tabiat Parkı'nın patikaları doğa yürüyüşü için elverişlidir."),
        ("Bisiklet ve yürüyüş için en iyi saat nedir?","Sabah erken ve akşamüzeri saatleri, özellikle yaz aylarında en konforlu zamanlardır.")],
},
{
 "slug":"istanbuldan-trenle-sapanca","cat":"Ulaşım","img":"dis-cephe","date":"2026-08-26","mod":"2026-11-16",
 "title":"İstanbul'dan Sapanca'ya Trenle Ulaşım: Ada Ekspresi, YHT ve Saatler",
 "seo_title":"İstanbul'dan Sapanca'ya Trenle Ulaşım (2026 Saatleri)",
 "img_alt":"DİDİ Otel Sapanca'nın palmiyelerle çevrili dış cephesi ve tabelası",
 "desc":"İstanbul'dan Sapanca'ya trenle nasıl gidilir? YHT Sapanca'da durmaz; Marmaray + Ada Ekspresi ya da YHT ile Arifiye, güncel saatler ve gardan transfer.",
 "related":["sapancaya-nasil-gidilir","havalimanindan-sapancaya-ulasim","ankaradan-sapancaya-nasil-gidilir"],
 "lead":"Kısa cevap: <strong>Yüksek Hızlı Tren (YHT) Sapanca'da durmaz.</strong> İstanbul'dan Sapanca garına aktarmasız inen tek tren, Gebze'den kalkan <strong>Ada Ekspresi</strong> bölgesel trenidir: Marmaray ile Gebze'ye geçip günde 6 seferden birine binerseniz yaklaşık 1 saat 5 dakikada Sapanca'dasınız. Daha hızlı ama aktarmalı seçenek ise YHT ile Arifiye'ye inip oradan 13 km'lik kısa bir taksi yolculuğuyla Kırkpınar'a geçmektir. Aşağıda iki rotanın güncel saatlerini, sürelerini ve gardan otele nasıl geçeceğinizi tablolarla bulacaksınız.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Aktarmasız Sapanca:</strong> Marmaray → Gebze, ardından Ada Ekspresi → Sapanca (Gebze–Sapanca ~1 sa 5 dk, günde 6 sefer).</li>
<li><strong>En hızlı tren:</strong> YHT → Arifiye (Pendik'ten ~1 sa 15 dk, Söğütlüçeşme'den ~1 sa 45 dk), sonra taksiyle ~15 dk.</li>
<li><strong>Gardan otele:</strong> Sapanca garı ile Kırkpınar arası yaklaşık 5 km; taksiyle 7–10 dakika.</li>
<li>Saatler değişebilir; biletten önce <a href="https://ebilet.tcddtasimacilik.gov.tr/" target="_blank" rel="noopener">TCDD e-bilet</a> sistemini kontrol edin.</li>
</ul></div>
<h2>YHT Sapanca'da duruyor mu?</h2>
<p>Hayır. Ankara–İstanbul hızlı tren hattı Sapanca'nın yanından kendi güzergâhıyla geçer ama Sapanca'da durak yapmaz; Sakarya'daki YHT durağı <strong>Arifiye</strong>'dir. Eski haberlerde Sapanca'nın planlanan bir YHT durağı olarak geçmesi bu konuda kafa karıştırıyor; güncel işletmede Sapanca garına yalnızca bölgesel tren uğruyor. Yani "trenle Sapanca" dediğinizde iki gerçekçi yol var: <strong>bölgesel trenle doğrudan Sapanca garına</strong> ya da <strong>YHT ile Arifiye'ye, oradan karayoluyla Sapanca'ya</strong>.</p>
<h2>Hangi tren seçeneği size uygun?</h2>
<table><thead><tr><th>Seçenek</th><th>Güzergâh</th><th>Tren süresi</th><th>Kime uygun</th></tr></thead><tbody>
<tr><td>Ada Ekspresi (bölgesel)</td><td>Marmaray → Gebze → Sapanca garı</td><td>Gebze–Sapanca ~1 sa 5 dk</td><td>Aktarmayı dert etmeyen, doğrudan Sapanca garına inmek isteyenler; bütçe dostu</td></tr>
<tr><td>YHT + taksi</td><td>Söğütlüçeşme / Bostancı / Pendik → Arifiye, ardından ~13 km karayolu</td><td>Pendik–Arifiye ~1 sa 15 dk</td><td>Anadolu Yakası'ndan hızlı gelmek isteyenler, sefer seçeneği arayanlar</td></tr>
<tr><td>Otobüs / özel araç</td><td>TEM veya Kuzey Marmara Otoyolu</td><td>~1,5–2 saat (trafiğe göre)</td><td>Bagajı fazla olanlar, çevreyi araçla gezmek isteyenler</td></tr>
</tbody></table>
<h2>Ada Ekspresi ile Sapanca'ya nasıl gidilir?</h2>
<p>Ada Ekspresi, Gebze ile Adapazarı (Mithatpaşa) arasında çalışan bölgesel trendir ve <strong>Sapanca garında durur</strong>. İstanbul'un herhangi bir noktasından önce <strong>Marmaray</strong> ile hattın doğu ucu olan Gebze'ye gidersiniz; Gebze'de aynı istasyonda Ada Ekspresi'ne aktarma yaparsınız. Ağustos 2026'da yayımlanan tarifeye göre günde 6 sefer var ve Gebze–Sapanca arası her seferde yaklaşık 1 saat 5 dakika sürüyor.</p>
<h3>Gebze → Sapanca kalkış ve varış saatleri</h3>
<table><thead><tr><th>Sefer</th><th>Gebze kalkış</th><th>Sapanca varış</th></tr></thead><tbody>
<tr><td>1</td><td>07:25</td><td>08:30</td></tr>
<tr><td>2</td><td>11:00</td><td>12:05</td></tr>
<tr><td>3</td><td>13:10</td><td>14:15</td></tr>
<tr><td>4</td><td>16:35</td><td>17:40</td></tr>
<tr><td>5</td><td>17:40</td><td>18:45</td></tr>
<tr><td>6</td><td>20:50</td><td>21:55</td></tr>
</tbody></table>
<h3>Sapanca → Gebze dönüş saatleri</h3>
<table><thead><tr><th>Sefer</th><th>Sapanca kalkış</th><th>Gebze varış</th></tr></thead><tbody>
<tr><td>1</td><td>06:27</td><td>07:31</td></tr>
<tr><td>2</td><td>10:13</td><td>11:16</td></tr>
<tr><td>3</td><td>14:14</td><td>15:18</td></tr>
<tr><td>4</td><td>15:47</td><td>16:51</td></tr>
<tr><td>5</td><td>18:43</td><td>19:47</td></tr>
<tr><td>6</td><td>21:23</td><td>22:26</td></tr>
</tbody></table>
<p class="note">Saatler, 17 Ağustos 2026 tarihli tarife derlemesinden alınmıştır (kaynaklar aşağıda). Bölgesel tren saatleri ve fiyatları dönem dönem değişir; yola çıkmadan önce TCDD e-bilet sisteminden ya da 444 82 33 numaralı TCDD çağrı merkezinden teyit edin. Aynı derlemede Gebze–Adapazarı bölgesel bilet fiyatı 230 TL'den başlıyor olarak geçiyor; Sapanca'ya kadar olan ücret bundan farklı olabilir.</p>
<p>Not: Adapazarı şehir merkezindeki tarihi gar, altyapı çalışmaları nedeniyle 3 Eylül 2026'dan bu yana geçici olarak kapalı; trenler Mithatpaşa'ya kadar gidiyor. Bu durum Sapanca'da inecek yolcuları etkilemiyor.</p>
<h2>YHT ile Arifiye üzerinden nasıl gidilir?</h2>
<p>Daha sık sefer ve daha konforlu bir yolculuk istiyorsanız YHT'ye binip <strong>Arifiye</strong>'de inebilirsiniz. İstanbul'daki YHT durakları Halkalı, Bakırköy, Söğütlüçeşme, Bostancı, Pendik ve Gebze'dir. Ekim 2026 tarihli derlemeye göre İstanbul–Arifiye arasında günde 11 YHT seferi bulunuyor; Söğütlüçeşme'den Arifiye'ye yolculuk yaklaşık 1 saat 41–47 dakika, Pendik'ten ise yaklaşık 1 saat 13–18 dakika sürüyor. Ekonomi bileti aynı kaynakta 380 TL'den başlıyor olarak listeleniyor; TCDD dinamik fiyatlama uyguladığı için gün ve saate göre değişir.</p>
<p>Arifiye garından Kırkpınar'a karayoluyla yaklaşık <strong>13 km</strong> var; harita rotalamasına göre trafiksiz 15 dakika civarında. Garın önünden taksiyle geçmek en pratik yoldur. Varış saatinizi bize önceden yazarsanız taksi konusunda yönlendirme yapabiliriz.</p>
<table><thead><tr><th>İstanbul'daki istasyon</th><th>Arifiye'ye yaklaşık süre</th><th>Not</th></tr></thead><tbody>
<tr><td>Söğütlüçeşme</td><td>1 sa 41–47 dk</td><td>Kadıköy tarafından en kolay biniş</td></tr>
<tr><td>Pendik</td><td>1 sa 13–18 dk</td><td>Sabiha Gökçen'e yakın; en kısa süre</td></tr>
<tr><td>Halkalı / Bakırköy</td><td>Daha uzun</td><td>Avrupa Yakası'ndan Marmaray tüneliyle geçen seferler</td></tr>
</tbody></table>
<h2>Sapanca garından otele nasıl geçilir?</h2>
<p>Sapanca garı ilçe merkezinde, göle çok yakındır. Garla <a href="/blog/kirkpinar-sapanca-konaklama/">Kırkpınar</a> arası yaklaşık <strong>5 km</strong>; taksiyle 7–10 dakikada ulaşılır. <a href="/#konum">DİDİ Otel Sapanca</a> Kırkpınar'da, göl ile orman arasında yer alır ve Sapanca merkeze yaklaşık 3 km mesafededir. Gece geç saatte gelecekseniz (ör. 21:55 treni) taksiyi önceden ayarlamanızı öneririz; giriş saatimiz 14:00, çıkış saatimiz 12:00'dir.</p>
""" + fig("/assets/web/editorial/ONN09451","DİDİ Otel Sapanca bahçesinde palmiyeler ve çiçekler arasından havuza uzanan yürüyüş yolu","Trenle gelip arabasız kalanlar için iyi haber: bahçe, havuz ve Mare Gastro aynı yerde, otelden çıkmadan dinlenebilirsiniz.") + """
<h2>Araçsız Sapanca'da neler yapılır?</h2>
<p>Trenle gelmek, Sapanca'yı gezmenize engel değil. Araçsız gezginler için en kolay duraklar şunlar:</p>
<ul>
<li><strong>Sapanca Teleferik:</strong> Alt istasyonu Kırkpınar'dadır; ayrıntılar <a href="/blog/sapanca-teleferik-rehberi/">teleferik rehberimizde</a>.</li>
<li><strong>Göl kıyısı yürüyüşü:</strong> Kırkpınar ve merkez sahil şeridinde yürüyerek ya da bisikletle dolaşabilirsiniz. Rotalar için <a href="/blog/sapanca-bisiklet-yuruyus-parkurlari/">bisiklet ve yürüyüş parkurları</a> yazımıza bakın.</li>
<li><strong>Maşukiye ve Ormanya:</strong> Taksiyle 10–20 dakika mesafede; <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a> ve <a href="/blog/ormanya-rehberi/">Ormanya rehberimiz</a> rota planlamanıza yardımcı olur.</li>
</ul>
<p>Hafta sonunu saat saat planlamak isterseniz <a href="/blog/sapancada-1-gunluk-2-gunluk-gezi-plani/">1 ve 2 günlük gezi planımız</a> trenle gelenlere göre de uyarlanabilir.</p>
<h2>Araçsız yolculuk kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="trenle-sapanca">
<label><input type="checkbox"><span><b>Sefer saatini teyit edin</b><span>TCDD e-bilet veya 444 82 33 üzerinden güncel tarifeyi kontrol edin.</span></span></label>
<label><input type="checkbox"><span><b>Rotayı seçin</b><span>Doğrudan Sapanca için Ada Ekspresi, hız için YHT + Arifiye.</span></span></label>
<label><input type="checkbox"><span><b>Marmaray süresini hesaba katın</b><span>Gebze'ye ulaşım bindiğiniz istasyona göre uzun sürebilir.</span></span></label>
<label><input type="checkbox"><span><b>Gardan transferi ayarlayın</b><span>Sapanca garı–Kırkpınar ~5 km, Arifiye–Kırkpınar ~13 km.</span></span></label>
<label><input type="checkbox"><span><b>Hafif bagaj</b><span>Aktarmalı yolculukta büyük fark yaratır.</span></span></label>
<label><input type="checkbox"><span><b>Dönüş treninizi not edin</b><span>Sapanca'dan son bölgesel sefer 21:23 (Ağustos 2026 tarifesi).</span></span></label>
</div>
<h2>Trenle gelenler için konaklama önerisi</h2>
<p>Trenle geldiyseniz her şeyin yakında olduğu bir yerde kalmak işinizi kolaylaştırır. Kırkpınar'daki <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur), bahçedeki <a href="/#mare">Mare Gastro</a>'da akşam yemeği için dışarı çıkmanıza gerek kalmaz ve sezonda Sapanca'nın tek klorsuz havuzunda dinlenebilirsiniz. Çiftler için <a href="/odalar/king-suit/">King Suit</a>, kalabalık gelenler için <a href="/odalar/aile/">Aile Odası</a> öne çıkar. Varış saatinizi ve trenle geleceğinizi <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%27ya%20trenle%20gelece%C4%9Fim%2C%20konaklama%20ve%20gardan%20ula%C5%9F%C4%B1m%20hakk%C4%B1nda%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> yazın, müsaitliği ve gardan nasıl geleceğinizi birlikte netleştirelim.</p>
""",
 "sources":[("Gebze–Adapazarı bölgesel tren saatleri (e-Yaşam Rehberi, 17.08.2026)","https://e-yasamrehberi.com/tren-saatleri/bolgesel-trenler/gebze-adapazari-tren-saatleri.html"),
            ("Adapazarı–Gebze bölgesel tren saatleri (e-Yaşam Rehberi, 17.08.2026)","https://e-yasamrehberi.com/tren-saatleri/bolgesel-trenler/adapazari-gebze-tren-saatleri.html"),
            ("İstanbul–Sakarya (Arifiye) hızlı tren saatleri (e-Yaşam Rehberi, 17.10.2026)","https://www.e-yasamrehberi.com/tren-saatleri/anahat-trenleri/istanbul-sakarya-hizli-tren-saatleri.html"),
            ("TCDD Taşımacılık e-bilet (resmi satış ve güncel saat)","https://ebilet.tcddtasimacilik.gov.tr/"),
            ("Sapanca railway station (Wikipedia)","https://en.wikipedia.org/wiki/Sapanca_railway_station"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("YHT Sapanca'da duruyor mu?","Hayır. Yüksek Hızlı Tren Sapanca'da durmaz; Sakarya'daki YHT durağı Arifiye'dir. Sapanca garına aktarmasız inmek için Gebze'den kalkan Ada Ekspresi bölgesel trenini kullanmanız gerekir."),
        ("İstanbul'dan Sapanca'ya trenle nasıl gidilir?","Marmaray ile Gebze'ye gidip Ada Ekspresi'ne aktarma yaparsınız; Gebze–Sapanca yaklaşık 1 saat 5 dakika sürer. Alternatif olarak YHT ile Arifiye'ye inip oradan yaklaşık 13 km'lik taksi yolculuğuyla Kırkpınar'a geçebilirsiniz."),
        ("Ada Ekspresi Gebze'den saat kaçta kalkıyor?","Ağustos 2026 tarifesine göre Gebze'den 07:25, 11:00, 13:10, 16:35, 17:40 ve 20:50'de olmak üzere günde 6 sefer kalkar. Saatler değişebileceği için TCDD e-bilet sisteminden teyit edin."),
        ("Sapanca'dan İstanbul'a son tren kaçta?","Ağustos 2026 tarifesine göre Sapanca'dan Gebze yönüne son bölgesel tren 21:23'te kalkar ve 22:26'da Gebze'ye varır."),
        ("YHT ile Arifiye'ye kaç saatte gidilir?","Pendik'ten yaklaşık 1 saat 13–18 dakika, Söğütlüçeşme'den yaklaşık 1 saat 41–47 dakika sürer. Arifiye'den Kırkpınar'a karayoluyla yaklaşık 13 km vardır."),
        ("Sapanca garı Kırkpınar'a ne kadar uzak?","Sapanca garı ile Kırkpınar arası yaklaşık 5 km'dir; taksiyle 7–10 dakikada ulaşılır.")],
},
{
 "slug":"sapanca-macera-parki-zipline","cat":"Aktivite","img":"ONN09440","date":"2026-08-26","mod":"2026-11-16",
 "title":"Sapanca'da Zipline, ATV ve Macera Aktiviteleri Rehberi",
 "seo_title":"Sapanca Zipline, ATV ve Macera Parkı Rehberi",
 "img_alt":"DİDİ Otel Sapanca bahçesinde beyaz perdeli cabana sırası",
 "desc":"Sapanca'da zipline nerede? Teleferik üst istasyonunda zipline ve ATV, Maşukiye'de ip parkurları, gölde SUP. Kime uygun, güvenlik ve plan önerileri.",
 "related":["sapanca-teleferik-rehberi","ailecek-sapanca-tatili","sapanca-golu-aktiviteler"],
 "lead":"Sapanca'da zipline yapmak isteyenlerin ilk adresi <strong>Sapanca Teleferik'in üst istasyonudur</strong>: işletmenin resmi sitesine göre teleferikle çıkılan bu alanda zipline, ATV safari ve trekking parkurları bir arada sunuluyor. Bunun dışında Maşukiye ve Kartepe yönündeki orman içi macera parklarında ip parkurları ve dev salıncak gibi aktiviteler, gölde ise son yıllarda hızla yayılan SUP (ayakta kürek) var. Aşağıda hangi aktivitenin nerede olduğunu, kimlere uygun olduğunu ve gitmeden önce nelere dikkat etmeniz gerektiğini derledik.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Zipline + ATV:</strong> Sapanca Teleferik üst istasyonu (alt istasyon Kırkpınar'da, her gün 11:00–19:00).</li>
<li><strong>İp parkuru, dev salıncak:</strong> Maşukiye–Kartepe hattındaki orman içi macera parkları.</li>
<li><strong>Su:</strong> Sapanca Gölü'nde SUP; can yeleği şart, rüzgârlı havada göle açılmayın.</li>
<li>Fiyat, yaş ve kilo sınırları işletmeye göre değişir; gitmeden önce telefonla teyit edin.</li>
</ul></div>
<h2>Sapanca'da zipline nerede yapılır?</h2>
<p>En kolay ulaşılan zipline, <a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a> ile çıkılan üst istasyon alanındadır. İşletmenin resmi sitesinde zipline, ATV safari, trekking, bungalov ve göl manzaralı kafe-restoran aynı alanın olanakları olarak listeleniyor; adres Kırkpınar Hasanpaşa'daki alt istasyon (Şehit Cevdet Koç Caddesi No:78) olarak veriliyor. Yani önce teleferikle 1.501 metrelik hattı çıkıyor, ardından yukarıda aktiviteleri seçiyorsunuz.</p>
<p>Zipline hattının uzunluğu, ücreti ve yaş-kilo sınırları resmi sayfada yayımlanmıyor; teleferik bileti ayrı satılıyor. Gitmeden önce işletmenin <strong>444 6 345</strong> numaralı hattından güncel bilgi almanızı öneririz. Teleferik biletleri yalnızca gişede satılır ve satın alındığı gün boyunca geçerlidir.</p>
<h2>Hangi aktivite kime uygun?</h2>
<table><thead><tr><th>Aktivite</th><th>Nerede</th><th>Kime uygun</th><th>Dikkat</th></tr></thead><tbody>
<tr><td>Zipline</td><td>Teleferik üst istasyonu; bazı orman parkları</td><td>Gençler, yetişkinler, sınırları karşılayan çocuklar</td><td>Yaş/kilo sınırını sorun</td></tr>
<tr><td>ATV safari</td><td>Teleferik üst istasyonu ve çevre parkurlar</td><td>Ehliyet/yaş şartını karşılayan yetişkinler</td><td>Kapalı ayakkabı, toz ve çamur</td></tr>
<tr><td>İp parkuru / dev salıncak</td><td>Maşukiye–Kartepe hattındaki macera parkları</td><td>Aileler, gençler, gruplar</td><td>Hafta sonu sıra olabilir</td></tr>
<tr><td>Trekking</td><td>Teleferik üst istasyonu, Kuzuyayla, Maşukiye</td><td>Herkes</td><td>Yağmur sonrası patika kaygan</td></tr>
<tr><td>SUP</td><td>Sapanca Gölü kıyısı</td><td>Yüzme bilen herkes</td><td>Can yeleği, rüzgâr takibi</td></tr>
<tr><td>Bisiklet</td><td>Göl kıyısı, Uzunkum</td><td>Aileler, çiftler</td><td>Kask, gün ışığında sürüş</td></tr>
</tbody></table>
<h2>Maşukiye ve Kartepe'de macera parkları</h2>
<p>Kırkpınar'dan 10–15 dakika uzaklıktaki <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a> ve Kartepe'ye çıkan yol üzerinde orman içinde kurulu macera parkları bulunur. Bu parklarda genellikle farklı yüksekliklerde ip parkurları, dev salıncak, tırmanma duvarı ve kısa zipline hatları olur; bazı işletmeler paintball gibi grup aktiviteleri de sunar. İşletmeler sık değiştiği ve sezona göre açılıp kapandığı için burada isim vermiyoruz; yol üzerinde tabelaları göreceksiniz, ama gitmeden önce açık olduklarını teyit etmek iyi fikir.</p>
<h2>Sapanca Gölü'nde SUP: yeni favori</h2>
<p>Ayakta kürek (SUP), Sapanca Gölü'nde son birkaç yılda hızla yaygınlaştı. Temmuz 2026 tarihli bir DHA haberine göre gölde SUP'u yaygınlaştırmayı amaçlayan bir dernek ücretsiz tanışma etkinlikleri düzenliyor ve gün batımında onlarca SUP'un aynı anda göle açıldığı etkinlikler yapılıyor. Derneğin vurguladığı kural basit: suya çıkan herkes <strong>can yeleği</strong> giymeli.</p>
<p>Gölün rüzgârı hafife alınmamalı: aynı ay içinde ani bir fırtınada botlar ve SUP'larla açılan 35 kişi AFAD ekiplerince kurtarıldı. Rüzgâr uyarısı varsa kıyıda kalın, kıyıdan uzaklaşmayın ve yanınızda telefon bulundurun. Gölle ilgili diğer aktiviteler için <a href="/blog/sapanca-golu-aktiviteler/">Sapanca Gölü aktiviteleri</a> yazımıza bakın.</p>
""" + fig("/assets/web/editorial/ONN09464","DİDİ Otel Sapanca'da şezlonglar ve şemsiyelerle çevrili açık havuz, önde mor begonvil","Adrenalin dolu bir günün ardından: sezonda DİDİ Otel'in klorsuz havuzu.") + """
<h2>Ailelerle macera günü nasıl planlanır?</h2>
<p>Çocuklarla gidiyorsanız günü ikiye bölmek iyi çalışır: sabah serinliğinde teleferik ve üst istasyonda kısa bir yürüyüş, öğleden sonra ise çocukların boyuna uygun ip parkurları. Bazı aktivitelerde boy, yaş ve kilo sınırı uygulandığı için küçük çocuklarla gelenler önce yalnızca teleferiği planlayıp aktiviteleri yerinde seçebilir. Çocuklu ailelere uygun diğer duraklar (Ormanya, Uzunkum piknik alanı) <a href="/blog/ailecek-sapanca-tatili/">ailecek Sapanca tatili</a> ve <a href="/blog/ormanya-rehberi/">Ormanya rehberimizde</a>.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="aile">Aileler</button><button data-tab="genc">Arkadaş grubu</button><button data-tab="cift">Çiftler</button></div>
<div class="itin-panel on" data-tab="aile"><p>10:30 kahvaltı sonrası teleferik (11:00'de açılır), üst istasyonda yürüyüş; öğlen Maşukiye'de alabalık; öğleden sonra ip parkuru; akşam otelde dinlenme.</p></div>
<div class="itin-panel" data-tab="genc"><p>Teleferik + zipline + ATV aynı alanda; ardından gölde SUP (rüzgârsız saatlerde) ve gün batımı. Kalabalık gruplar için <a href="/odalar/triple/">Triple</a> ve <a href="/odalar/aile/">Aile</a> odaları pratik.</p></div>
<div class="itin-panel" data-tab="cift"><p>Teleferikte göl manzarası, üst istasyonda kısa zipline; akşam <a href="/#mare">Mare Gastro</a>'da bahçede yemek.</p></div>
</div>
<h2>Gitmeden önce kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="macera-parki">
<label><input type="checkbox"><span><b>Kapalı ve rahat ayakkabı</b><span>Zipline, ATV ve parkurlar için şarttır.</span></span></label>
<label><input type="checkbox"><span><b>Yaş, boy ve kilo sınırını sorun</b><span>İşletmeye göre değişir.</span></span></label>
<label><input type="checkbox"><span><b>Hava ve rüzgâr durumu</b><span>Teleferik ve göl aktiviteleri rüzgârdan etkilenir.</span></span></label>
<label><input type="checkbox"><span><b>Nakit ve kart</b><span>Teleferik bileti gişede satılır.</span></span></label>
<label><input type="checkbox"><span><b>Yedek kıyafet ve su</b><span>ATV ve SUP sonrası işe yarar.</span></span></label>
<label><input type="checkbox"><span><b>Güvenlik brifingini dinleyin</b><span>Ekipmanı görevli kontrol etmeden başlamayın.</span></span></label>
</div>
<h2>Macera sonrası nerede dinlenilir?</h2>
<p>Teleferiğin alt istasyonuyla aynı mahallede, Kırkpınar'daki <a href="/#konum">DİDİ Otel Sapanca</a>'da günün yorgunluğunu atabilirsiniz: havuz sezonunda Sapanca'nın tek klorsuz havuzu, bahçede cabanalar ve akşam <a href="/#mare">Mare Gastro</a>. Müsaitlik ve aktivite önerileri için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%27da%20aktivite%20ve%20konaklama%20i%C3%A7in%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> yazabilirsiniz. Bölgedeki diğer duraklar <a href="/blog/sapancada-gezilecek-yerler/">gezilecek yerler</a> rehberimizde.</p>
""",
 "sources":[("Sapanca Teleferik — zipline sayfası (resmi site)","https://sapancateleferik.com.tr/zipline/"),
            ("Sapanca Teleferik — fiyat tarifesi ve bilet koşulları (resmi site)","https://sapancateleferik.com.tr/fiyat-tarifesi"),
            ("Sapanca Gölü'nde popülerleşen spor dalı: SUP (DHA, 02.07.2026)","https://www.dha.com.tr/foto-galeri/sapanca-golunde-populerlesen-spor-dali-sup-2902453"),
            ("Sapanca Gölü'nde fırtınaya yakalanan 35 kişi kurtarıldı (GZT)","https://www.gzt.com/gundem/sapanca-golunde-firtinaya-yakalanan-35-kisi-afad-ekiplerince-kurtarildi-4243982")],
 "faq":[("Sapanca'da zipline var mı?","Evet. Sapanca Teleferik'in üst istasyonunda zipline bulunur; işletmenin resmi sitesine göre aynı alanda ATV safari ve trekking de sunulur. Maşukiye–Kartepe hattındaki bazı macera parklarında da kısa zipline hatları vardır."),
        ("Sapanca zipline fiyatı ne kadar?","Zipline ücreti işletmenin resmi sayfasında yayımlanmıyor ve teleferik biletinden ayrı. Güncel fiyat için Sapanca Teleferik'in 444 6 345 numaralı hattını aramanızı öneririz."),
        ("Teleferik ve zipline hangi saatlerde açık?","Sapanca Teleferik'in resmi sitesine göre tesis her gün 11:00–19:00 arasında hizmet veriyor; hava koşullarına bağlı değişiklikler olabilir."),
        ("Macera aktiviteleri çocuklar için uygun mu?","Birçok parkta çocuklara uygun alçak parkurlar bulunur; ancak zipline ve ATV'de yaş, boy ve kilo sınırları uygulanabilir. Gitmeden önce işletmeye sorun."),
        ("Sapanca Gölü'nde SUP yapılabilir mi?","Evet, SUP gölde giderek yaygınlaşıyor. Can yeleği giymek şarttır; rüzgârlı havada göle açılmayın, çünkü ani fırtınalarda kurtarma operasyonları yaşanmıştır."),
        ("Aktiviteler için ne giymeli?","Kapalı ve kaymayan ayakkabı, hareket ettiren kıyafet ve yedek bir kat giysi alın; ATV ve SUP için ıslanmayı ve çamuru göze alın.")],
},
{
 "slug":"ankaradan-sapancaya-nasil-gidilir","cat":"Ulaşım","img":"resepsiyon1","date":"2026-11-16",
 "title":"Ankara'dan Sapanca'ya Nasıl Gidilir? YHT, Araç ve Otobüs Rehberi",
 "seo_title":"Ankara'dan Sapanca'ya Nasıl Gidilir? YHT ve Araçla",
 "img_alt":"DİDİ Otel Sapanca resepsiyonu, bayraklar ve resepsiyon tezgâhında karşılanan misafir",
 "desc":"Ankara'dan Sapanca'ya en hızlı yol YHT ile Arifiye (~2 sa 37 dk), ardından 13 km taksi. Güncel sefer saatleri, araçla 320 km rota ve hafta sonu planı.",
 "related":["sapancaya-nasil-gidilir","istanbuldan-trenle-sapanca","sapanca-mi-abant-mi-bolu-mu"],
 "lead":"Ankara'dan Sapanca'ya en hızlı ulaşım <strong>Yüksek Hızlı Tren</strong> ile sağlanır: Ankara Garı'ndan kalkan YHT'ler Sakarya'daki <strong>Arifiye</strong> garına yaklaşık <strong>2 saat 36–39 dakikada</strong> varır; YHT Sapanca'da durmaz, Arifiye'den Kırkpınar'a karayoluyla yaklaşık 13 km (taksiyle ~15 dakika) kalır. Özel araçla Ankara–Sapanca yaklaşık <strong>320 km</strong>'dir ve trafiksiz 3,5 saat civarında sürer. Ekim 2026 tarihli tarifeye göre Ankara'dan Arifiye'ye günde 6 YHT seferi bulunuyor.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>YHT:</strong> Ankara → Arifiye ~2 sa 37 dk, günde 6 sefer; Arifiye → Kırkpınar ~13 km.</li>
<li><strong>Araç:</strong> ~320 km, ~3,5 saat; otoyoldan Sapanca çıkışı, otel gişelere ~500 m.</li>
<li><strong>Gece treni:</strong> Ankara Ekspresi 22:00'de kalkar, Arifiye'ye 04:24'te varır.</li>
<li>Saatler değişebilir; <a href="https://ebilet.tcddtasimacilik.gov.tr/" target="_blank" rel="noopener">TCDD e-bilet</a>'ten teyit edin.</li>
</ul></div>
<h2>Ankara'dan Sapanca'ya hangi yolla gidilir?</h2>
<table><thead><tr><th>Yöntem</th><th>Süre</th><th>Artısı</th><th>Eksisi</th></tr></thead><tbody>
<tr><td>YHT + taksi</td><td>~2 sa 37 dk + ~15 dk</td><td>En hızlı; trafik ve yorgunluk yok</td><td>Arifiye'den karayolu gerekir</td></tr>
<tr><td>Özel araç</td><td>~3,5 saat (~320 km)</td><td>Bölgeyi gezmek için esnek</td><td>Bolu Dağı geçişi; kışın hava koşulları</td></tr>
<tr><td>Şehirlerarası otobüs</td><td>Firmaya göre değişir</td><td>Sık sefer, bütçe dostu</td><td>İniş noktası firmaya göre farklı</td></tr>
<tr><td>Ankara Ekspresi (gece)</td><td>~6 sa 24 dk</td><td>Gece yolculuğu</td><td>Arifiye'ye 04:24'te varış</td></tr>
</tbody></table>
<h2>YHT ile Ankara'dan Arifiye'ye: sefer saatleri</h2>
<p>Ankara Garı'ndan Arifiye'ye giden yüksek hızlı trenler Eskişehir, Bilecik ve Bozüyük hattını izleyerek Sakarya'ya ulaşır. Ekim 2026'da güncellenen tarife derlemesine göre seferler şöyle:</p>
<table><thead><tr><th>Sefer</th><th>Ankara Garı kalkış</th><th>Arifiye varış</th></tr></thead><tbody>
<tr><td>YHT</td><td>06:25</td><td>09:03</td></tr>
<tr><td>YHT</td><td>08:40</td><td>11:19</td></tr>
<tr><td>YHT</td><td>10:50</td><td>13:28</td></tr>
<tr><td>YHT</td><td>12:35</td><td>15:11</td></tr>
<tr><td>YHT</td><td>17:25</td><td>20:02</td></tr>
<tr><td>YHT</td><td>18:30</td><td>21:07</td></tr>
<tr><td>Ankara Ekspresi</td><td>22:00</td><td>04:24</td></tr>
</tbody></table>
<p class="note">Saatler 17 Ekim 2026 tarihli e-Yaşam Rehberi derlemesinden alınmıştır. TCDD tarifeyi dönemsel olarak değiştirir ve dinamik fiyatlama uygular; bilet almadan önce TCDD e-bilet sitesinden ya da 444 82 33'ten kontrol edin.</p>
<h3>Cuma akşamı çıkacaklar için</h3>
<p>İşten sonra yola çıkacaksanız 17:25 ve 18:30 seferleri en uygun seçeneklerdir: Arifiye'ye 20:02 ya da 21:07'de iner, taksiyle yaklaşık 15 dakikada Kırkpınar'a ulaşırsınız. Geç varışınızı önceden bildirmeniz yeterli; giriş işlemlerinizi buna göre hazırlarız.</p>
<h2>Arifiye garından Sapanca'ya nasıl geçilir?</h2>
<p>Arifiye garı, Adapazarı–Sapanca yolu üzerindedir. OpenStreetMap rotalamasına göre gar ile Kırkpınar arası yaklaşık <strong>13 km</strong>'dir ve trafiksiz 15 dakika sürer. Seçenekler:</p>
<ul>
<li><strong>Taksi:</strong> En pratik yol; garın önünden doğrudan otele.</li>
<li><strong>Ada Ekspresi:</strong> Gebze–Adapazarı bölgesel treni Arifiye'de de, Sapanca'da da durur. Ancak günde yalnızca 6 sefer olduğundan YHT varışınızla denk gelmesi şansa kalır; Sapanca garından da Kırkpınar'a yaklaşık 5 km yol vardır.</li>
<li><strong>Araç kiralama:</strong> Hafta sonu boyunca Kartepe, Maşukiye ve Kuzuluk'u gezmek istiyorsanız mantıklıdır.</li>
</ul>
<h2>Araçla Ankara'dan Sapanca'ya</h2>
<p>Ankara'dan Sapanca'ya araçla yaklaşık 320 km'lik bir yol vardır ve otoyol üzerinden trafiksiz 3,5 saat civarında sürer. İstanbul yönünde ilerlerken Düzce ve Sakarya'yı geçip <strong>Sapanca</strong> çıkışında otoyoldan ayrılırsınız. <a href="/#konum">DİDİ Otel Sapanca</a>, Kırkpınar'da, otoyolun Sapanca gişelerine yaklaşık 500 metre mesafededir; misafirlerimiz için ücretsiz otopark bulunur.</p>
<ul>
<li>Kış aylarında Bolu Dağı kesiminde kar ve sis olabilir; yola çıkmadan Karayolları'nın yol durumu duyurularına bakın.</li>
<li>Uzun hafta sonlarının ilk gününde otoyolda yoğunluk olur; sabah erken saatler daha rahattır.</li>
<li>Yol üstü mola için Bolu ve Düzce dinlenme tesisleri uygun duraklardır.</li>
</ul>
""" + fig("/assets/web/editorial/lobi","DİDİ Otel Sapanca lobisinde cam kapılar, bahçe manzarası, kitaplık ve oturma grubu","Uzun yolun ardından: DİDİ Otel Sapanca lobisi.") + """
<h2>Otobüsle Ankara'dan Sapanca'ya</h2>
<p>Ankara AŞTİ'den İstanbul ve Sakarya yönüne giden pek çok otobüs firması Sapanca civarından geçer. Bazı firmalar Sapanca'da kendi yazıhanesine, bazıları otoyol üzerindeki bir noktaya, bazıları ise yalnızca Adapazarı otogarına bırakır. Bilet alırken "Sapanca'da nerede iniyorum?" sorusunu mutlaka sorun; indiğiniz noktadan Kırkpınar'a taksiyle kısa sürede geçebilirsiniz.</p>
<h2>Eskişehir'den gelenler için</h2>
<p>Eskişehir de aynı YHT hattı üzerindedir. Tarife derlemesine göre Arifiye–Eskişehir arasında günde 12 sefer bulunuyor ve en kısa yolculuk yaklaşık 1 saat 8 dakika sürüyor; Eskişehir'den bir hafta sonu kaçamağı için Sapanca bu yüzden oldukça yakındır.</p>
<h2>Ankara'dan Sapanca hafta sonu planı</h2>
<table><thead><tr><th>Gün</th><th>Plan</th></tr></thead><tbody>
<tr><td>Cuma</td><td>17:25 YHT → Arifiye 20:02 → otel ~20:20; bahçede akşam yemeği</td></tr>
<tr><td>Cumartesi</td><td>Kahvaltı, <a href="/blog/sapanca-teleferik-rehberi/">teleferik</a>, <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'de alabalık, gün batımında göl kıyısı</td></tr>
<tr><td>Pazar</td><td>Kahvaltı, <a href="/blog/ormanya-rehberi/">Ormanya</a> ya da sahil yürüyüşü, öğleden sonra Arifiye'den dönüş treni</td></tr>
</tbody></table>
<p>Daha ayrıntılı programlar için <a href="/blog/sapancada-1-gunluk-2-gunluk-gezi-plani/">1 ve 2 günlük gezi planı</a> ve <a href="/blog/sapanca-3-gun-uzun-hafta-sonu-plani/">3 günlük plan</a> yazılarımıza bakın. Sapanca'yı Abant ve Bolu ile karşılaştırıyorsanız <a href="/blog/sapanca-mi-abant-mi-bolu-mu/">bu karşılaştırma</a> işinize yarar.</p>
<h2>Hangi seçenek kime daha mantıklı?</h2>
<p>Ankara'dan Sapanca'ya gelirken doğru yöntem, kaç kişi olduğunuza ve Sapanca'da ne yapmak istediğinize bağlıdır.</p>
<ul>
<li><strong>Yalnız ya da çift, kısa hafta sonu:</strong> YHT en mantıklısıdır. Yolda dinlenir, Arifiye'den taksiyle 15 dakikada otelde olursunuz. Sapanca'da teleferik, göl kıyısı ve Maşukiye gibi yakın duraklar taksiyle rahatça gezilir.</li>
<li><strong>Dört kişilik aile:</strong> Bilet sayısı arttıkça kendi aracınızla gelmek hem maliyet hem esneklik açısından öne geçer; çocuklarla Ormanya, Kartepe ve Kuzuluk gibi dağınık noktalara gitmek de araçla kolaylaşır.</li>
<li><strong>Kış hafta sonu:</strong> Bolu Dağı kesiminde kar ve sis ihtimali olduğu için hava koşulları kötüyse YHT güvenli tercihtir; Kartepe'ye çıkmak isterseniz Sapanca'da günlük araç kiralayabilirsiniz.</li>
<li><strong>Bayram ve uzun hafta sonu:</strong> Otoyolda yoğunluk beklenir; YHT biletleri de hızla dolar. Bileti açılır açılmaz almak en iyi stratejidir.</li>
</ul>
<h2>Dönüş yolculuğunu nasıl planlamalı?</h2>
<p>Pazar günü dönüşte iki yaygın hata var: çıkış saatini (12:00) beklemeden odadan erken ayrılıp günü boşa harcamak, ya da son trene yetişmeye çalışırken Arifiye'ye geç kalmak. Çıkıştan sonra eşyalarınızı bırakıp göl kıyısında son bir yürüyüş yapabilir, öğle yemeğini Maşukiye'de yiyip öğleden sonraki bir YHT ile dönebilirsiniz. Arifiye–Ankara dönüş saatlerini mutlaka TCDD e-bilet sisteminden kontrol edin ve gara en az 20–30 dakika erken varın; hafta sonu öğleden sonraları Adapazarı–Sapanca yolunda trafik olabilir.</p>
<h2>Yolculuk kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="ankara-sapanca">
<label><input type="checkbox"><span><b>YHT biletinizi erken alın</b><span>Hafta sonu ve bayram seferleri hızlı dolar.</span></span></label>
<label><input type="checkbox"><span><b>Arifiye'den transfer</b><span>Taksiyle ~15 dk; geç varışta önceden haber verin.</span></span></label>
<label><input type="checkbox"><span><b>Dönüş treni</b><span>Arifiye–Ankara saatlerini TCDD'den kontrol edin.</span></span></label>
<label><input type="checkbox"><span><b>Araçla geliyorsanız</b><span>Kışın Bolu Dağı yol durumuna bakın.</span></span></label>
<label><input type="checkbox"><span><b>Varış saatinizi bildirin</b><span>Giriş 14:00, çıkış 12:00.</span></span></label>
</div>
<h2>Ankara'dan gelenler için konaklama</h2>
<p>Arifiye'ye ve otoyola yakın, ama gölün sakin güney kıyısında bir yer arıyorsanız Kırkpınar idealdir. <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur), bahçede <a href="/#mare">Mare Gastro</a> ve havuz sezonunda Sapanca'nın tek klorsuz havuzu bulunur. Çiftler için <a href="/odalar/king-suit/">King Suit</a>, aileler için <a href="/odalar/aile/">Aile Odası</a> öne çıkar. Tren saatinizi <a href="https://wa.me/905331350888?text=Merhaba%2C%20Ankara%27dan%20YHT%20ile%20Arifiye%27ye%20gelece%C4%9Fim%2C%20konaklama%20i%C3%A7in%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> yazın, varışınızı birlikte planlayalım.</p>
""",
 "sources":[("Arifiye garı — Ankara bağlantılı YHT seferleri (e-Yaşam Rehberi, 17.10.2026)","https://www.e-yasamrehberi.com/tren-saatleri/garlar/arifiye-gari.html"),
            ("TCDD Taşımacılık e-bilet","https://ebilet.tcddtasimacilik.gov.tr/"),
            ("Gebze–Adapazarı bölgesel tren saatleri (e-Yaşam Rehberi)","https://e-yasamrehberi.com/tren-saatleri/bolgesel-trenler/gebze-adapazari-tren-saatleri.html"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("Ankara'dan Sapanca'ya trenle nasıl gidilir?","Ankara Garı'ndan YHT ile Arifiye'ye gidilir (yaklaşık 2 saat 36–39 dakika). YHT Sapanca'da durmaz; Arifiye'den Kırkpınar'a karayoluyla yaklaşık 13 km, taksiyle 15 dakika kalır."),
        ("Ankara'dan Arifiye'ye günde kaç YHT var?","Ekim 2026 tarifesine göre Ankara Garı'ndan Arifiye'ye günde 6 YHT seferi vardır: 06:25, 08:40, 10:50, 12:35, 17:25 ve 18:30. Ayrıca 22:00'de kalkan Ankara Ekspresi bulunur."),
        ("Ankara Sapanca arası kaç km?","Karayoluyla yaklaşık 320 km'dir; otoyol üzerinden trafiksiz yaklaşık 3,5 saat sürer."),
        ("YHT Sapanca'da duruyor mu?","Hayır. Sakarya'daki YHT durağı Arifiye'dir. Sapanca garında yalnızca Gebze–Adapazarı arasında çalışan Ada Ekspresi bölgesel treni durur."),
        ("Arifiye garından Sapanca'ya nasıl gidilir?","En pratik yol taksidir; Arifiye ile Kırkpınar arası yaklaşık 13 km ve 15 dakikadır. Ada Ekspresi de Arifiye'den Sapanca'ya gider, ancak günde 6 sefer olduğu için saatlerin uyması gerekir."),
        ("Eskişehir'den Sapanca'ya ne kadar sürer?","YHT ile Eskişehir–Arifiye en kısa yaklaşık 1 saat 8 dakikadır; Arifiye'den Kırkpınar'a taksiyle yaklaşık 15 dakika eklenir.")],
},
{
 "slug":"havalimanindan-sapancaya-ulasim","cat":"Ulaşım","img":"resepsiyon2","date":"2026-11-16",
 "title":"Havalimanından Sapanca'ya Ulaşım: Sabiha Gökçen ve İstanbul Havalimanı",
 "seo_title":"Sabiha Gökçen'den Sapanca'ya Ulaşım: Tüm Seçenekler",
 "img_alt":"DİDİ Otel Sapanca resepsiyonunda misafiri karşılayan gülümseyen görevli",
 "desc":"Sabiha Gökçen'den Sapanca'ya ~95–110 km: transfer, kiralık araç, otobüs + YHT seçenekleri. İstanbul Havalimanı'ndan ~170 km. Süreler ve ipuçları.",
 "related":["sapancaya-nasil-gidilir","istanbuldan-trenle-sapanca","ankaradan-sapancaya-nasil-gidilir"],
 "lead":"Sapanca'ya en yakın havalimanı <strong>Sabiha Gökçen (SAW)</strong>'dir: güzergâha göre yaklaşık <strong>95–110 km</strong>, karayoluyla trafiksiz 1 saat 15 dakika ile 1,5 saat arası. <strong>İstanbul Havalimanı (IST)</strong> ise yaklaşık <strong>170 km</strong> uzaklıktadır ve trafiksiz 2 saat civarında sürer. Bagajla en konforlu yol önceden ayarlanmış bir transfer ya da kiralık araçtır; bütçe odaklı yolcular için Sabiha Gökçen'den Pendik'e geçip YHT ile Arifiye'ye, oradan taksiyle Kırkpınar'a gelmek de mümkündür.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>SAW → Sapanca:</strong> ~95–110 km; transfer/araçla 1 sa 15 dk – 1,5 saat.</li>
<li><strong>IST → Sapanca:</strong> ~170 km; transfer/araçla ~2 saat (trafiğe göre çok daha uzun olabilir).</li>
<li><strong>Toplu taşıma (SAW):</strong> otobüsle Pendik YHT garı → YHT ile Arifiye (~1 sa 15 dk) → taksiyle ~15 dk.</li>
<li>Gece inişlerinde toplu taşıma seçenekleri azalır; transferi önceden ayarlayın.</li>
</ul></div>
<h2>Hangi havalimanı Sapanca'ya daha yakın?</h2>
<table><thead><tr><th>Havalimanı</th><th>Kırkpınar'a mesafe</th><th>Araçla süre (trafiksiz)</th><th>Not</th></tr></thead><tbody>
<tr><td>Sabiha Gökçen (SAW)</td><td>~95–110 km</td><td>1 sa 15 dk – 1,5 saat</td><td>Anadolu Yakası'nda; Sapanca'ya en yakın</td></tr>
<tr><td>İstanbul Havalimanı (IST)</td><td>~170 km</td><td>~2 saat</td><td>Avrupa Yakası'nın kuzeyinde; köprü ve şehir trafiği</td></tr>
</tbody></table>
<p class="note">Mesafe aralığı, otelin duyurduğu ~95 km değeri ile OpenStreetMap rotalamasının verdiği ~110 km arasındaki güzergâh farkını yansıtır. Süreler trafiksiz koşullar içindir; İstanbul'da akşam saatlerinde ciddi gecikme olabilir.</p>
<h2>Sabiha Gökçen'den Sapanca'ya nasıl gidilir?</h2>
<h3>1. Transfer ya da taksi</h3>
<p>Uçaktan bagajla inip doğrudan otele gitmek istiyorsanız en rahat seçenek önceden ayarlanmış bir transferdir. Havalimanında taksi de bulunur, ancak şehirlerarası bir yolculuk olduğu için ücreti binmeden önce netleştirin. Kalabalık aileler ve gruplar için geniş araçlı transferler kişi başına maliyeti makul seviyeye indirir. Transfer seçenekleri konusunda yardıma ihtiyacınız olursa uçuş bilginizle birlikte bize yazın; size yol gösterelim.</p>
<h3>2. Araç kiralama</h3>
<p>Sabiha Gökçen'de pek çok araç kiralama şirketinin ofisi bulunur. Sapanca'da Kartepe, Maşukiye, Ormanya ve Kuzuluk gibi duraklar birbirine 15–45 dakika mesafede olduğu için araç kiralamak tatil boyunca büyük esneklik sağlar. Otoyolda Sapanca çıkışından ayrıldıktan sonra otel, gişelere yaklaşık 500 metre mesafededir; misafirlerimiz için ücretsiz otopark vardır.</p>
<h3>3. Toplu taşıma: Pendik üzerinden YHT</h3>
<p>Bütçe odaklı ve bagajı hafif yolcular için Sabiha Gökçen'den Pendik YHT garına otobüsle geçmek (İETT'nin havalimanı–Pendik hatları üzerinden) ve oradan YHT ile Arifiye'ye gitmek mümkündür. Ekim 2026 tarihli tarife derlemesine göre Pendik–Arifiye arası YHT ile yaklaşık 1 saat 13–18 dakika sürer. Arifiye garından Kırkpınar'a ise taksiyle yaklaşık 13 km, 15 dakika vardır. Otobüs hat numaralarını ve saatlerini yolculuk öncesinde İETT'nin güncel bilgilerinden kontrol edin.</p>
<h3>4. Şehirlerarası otobüs</h3>
<p>Sakarya merkezli bazı otobüs firmalarının Sabiha Gökçen ile Adapazarı arasında, Sapanca'dan geçen seferleri bulunur. Sefer saatleri ve iniş noktaları firmaya göre değiştiğinden bilet almadan önce firmadan teyit edin.</p>
<table><thead><tr><th>Seçenek (SAW çıkışlı)</th><th>Toplam süre</th><th>Bagaj</th><th>Kime uygun</th></tr></thead><tbody>
<tr><td>Transfer / taksi</td><td>1 sa 15 dk – 1,5 saat</td><td>Rahat</td><td>Aileler, gruplar, gece inişleri</td></tr>
<tr><td>Kiralık araç</td><td>1 sa 15 dk – 1,5 saat</td><td>Rahat</td><td>Bölgeyi gezecekler</td></tr>
<tr><td>Otobüs + YHT + taksi</td><td>Aktarmalara göre 2,5–3,5 saat</td><td>Hafif bagaj</td><td>Bütçe odaklı, yalnız ya da çift yolcular</td></tr>
<tr><td>Şehirlerarası otobüs</td><td>Firmaya göre</td><td>Orta</td><td>Uygun sefer bulanlar</td></tr>
</tbody></table>
<h2>İstanbul Havalimanı'ndan Sapanca'ya nasıl gidilir?</h2>
<p>İstanbul Havalimanı, Sapanca'ya Sabiha Gökçen'e göre belirgin şekilde uzaktır (~170 km) ve yol, İstanbul'un yoğun trafiğinden ve Boğaz geçişinden geçer. Bu nedenle IST'ye inecekseniz önceden ayarlanmış transfer ya da kiralık araç en pratik seçenektir. Toplu taşımayla şehir merkezine geçip Marmaray, YHT veya otobüs kombinasyonlarıyla Sapanca'ya ulaşmak mümkündür, ancak bagajla birden fazla aktarma gerektirir ve uzun sürer. Akşam saatlerinde inen uçuşlar için yolculuğun normal süresinin çok üzerine çıkabileceğini hesaba katın.</p>
""" + fig("/assets/web/editorial/ONN09422","DİDİ Otel Sapanca binası ve önündeki havuz, palmiyeler ve mavi gökyüzü","Havalimanından yaklaşık 1,5 saat sonra: DİDİ Otel Sapanca, Kırkpınar.") + """
<h2>Havalimanı yolculuğu için ipuçları</h2>
<ul>
<li><strong>Uçuş saatinize göre planlayın:</strong> Gece yarısından sonra inen uçuşlarda toplu taşıma seçenekleri azalır.</li>
<li><strong>Varışınızı bildirin:</strong> Giriş saatimiz 14:00'tür; erken ya da geç varışlarınızı önceden bize yazın, odanızı buna göre hazırlayalım (erken giriş müsaitliğe bağlıdır).</li>
<li><strong>Dönüşte pay bırakın:</strong> Sapanca'dan Sabiha Gökçen'e dönüşte, özellikle pazar akşamları, trafik için en az 1 saat ek süre hesaplayın.</li>
<li><strong>Çocuk koltuğu:</strong> Transfer ya da kiralık araçta çocuk koltuğu ihtiyacınızı önceden belirtin.</li>
</ul>
<h2>Yurt dışından gelen misafirler için pratik notlar</h2>
<ul>
<li><strong>Dil:</strong> Web sitemiz Türkçenin yanı sıra İngilizce, Arapça, Almanca ve Rusça olarak da yayında; oda bilgilerini kendi dilinizde inceleyebilirsiniz.</li>
<li><strong>Kiralık araç ve otoyol:</strong> Türkiye'de otoyollarda HGS/OGS ile elektronik geçiş kullanılır. Kiralık aracınızda geçiş etiketi olup olmadığını ve ücretlerin nasıl yansıtılacağını teslim alırken sorun.</li>
<li><strong>İletişim:</strong> Yola çıkmadan önce WhatsApp'tan bize yazmanız en hızlı iletişim yoludur; numaramız +90 533 135 08 88.</li>
<li><strong>Varış saati:</strong> Uzun uçuşların ardından erken saatte gelecekseniz erken giriş için önceden yazın; müsaitliğe göre yardımcı oluruz. Aksi halde eşyalarınızı bırakıp göl kıyısında dolaşabilirsiniz.</li>
<li><strong>Nakit ve kart:</strong> Teleferik gişesi gibi bazı noktalarda yalnızca yerinde satış yapılır; yanınızda kart ve bir miktar nakit bulundurmak işinizi kolaylaştırır.</li>
</ul>
<h2>Dönüş uçuşu için Sapanca'dan ne zaman çıkmalı?</h2>
<p>Sabiha Gökçen'den kalkacak bir iç hat uçuşu için genel kural, uçuştan en az 3 saat önce Sapanca'dan yola çıkmaktır: yaklaşık 1,5 saatlik yol, olası trafik ve havalimanı işlemleri için pay. Dış hat uçuşlarında bu süreyi 4 saate, İstanbul Havalimanı'ndan kalkışlarda ise 4,5–5 saate çıkarmak daha güvenlidir. Pazar akşamları ve bayram dönüşlerinde Gebze–Pendik arasında trafik yoğunlaştığı için bu süreler bile sınırda kalabilir. Toplu taşımayla dönecekseniz Arifiye'den Pendik'e YHT, oradan havalimanına otobüs bağlantısını önceden planlayın.</p>
<h2>Havalimanı yolculuğu kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="havalimani">
<label><input type="checkbox"><span><b>Havalimanını seçin</b><span>Mümkünse Sabiha Gökçen; Sapanca'ya en yakın.</span></span></label>
<label><input type="checkbox"><span><b>Transfer ya da araç</b><span>Önceden ayarlayın, ücreti netleştirin.</span></span></label>
<label><input type="checkbox"><span><b>Toplu taşıma planı</b><span>Pendik YHT ve Arifiye aktarmasının saatlerini kontrol edin.</span></span></label>
<label><input type="checkbox"><span><b>Varış saatinizi bize yazın</b><span>Giriş 14:00, çıkış 12:00.</span></span></label>
<label><input type="checkbox"><span><b>Dönüş için ek süre</b><span>Pazar akşamı trafiği için en az 1 saat.</span></span></label>
</div>
<h2>Havalimanından gelen misafirler için konaklama</h2>
<p>Uzun bir uçuşun ardından otoyoldan çıkar çıkmaz dinlenmek isteyenler için <a href="/#konum">DİDİ Otel Sapanca</a>, Sapanca gişelerine yaklaşık 500 metre mesafededir. Kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur), akşam yemeği için bahçedeki <a href="/#mare">Mare Gastro</a> hemen yanınızdadır ve havuz sezonunda Sapanca'nın tek klorsuz havuzunda dinlenebilirsiniz. Kalabalık aileler için dört kişilik <a href="/odalar/aile/">Aile Odası</a>, çiftler için <a href="/odalar/king-suit/">King Suit</a> öne çıkar. Ulaşım seçeneklerinin tamamı için <a href="/blog/sapancaya-nasil-gidilir/">Sapanca'ya nasıl gidilir</a> rehberimize bakın. Uçuş bilginizi <a href="https://wa.me/905331350888?text=Merhaba%2C%20havaliman%C4%B1ndan%20Sapanca%27ya%20gelece%C4%9Fim%2C%20konaklama%20ve%20ula%C5%9F%C4%B1m%20i%C3%A7in%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> paylaşın, varışınızı birlikte planlayalım.</p>
""",
 "sources":[("İstanbul–Sakarya (Arifiye) hızlı tren saatleri (e-Yaşam Rehberi, 17.10.2026)","https://www.e-yasamrehberi.com/tren-saatleri/anahat-trenleri/istanbul-sakarya-hizli-tren-saatleri.html"),
            ("Sabiha Gökçen Havalimanı ulaşım rehberi (e-Yaşam Rehberi)","https://e-yasamrehberi.com/havaalanlari/sabiha-gokcen-havalimani-ulasim.html"),
            ("İETT — güncel hat ve sefer bilgileri","https://iett.istanbul/"),
            ("TCDD Taşımacılık e-bilet","https://ebilet.tcddtasimacilik.gov.tr/"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("Sabiha Gökçen'den Sapanca kaç km?","Güzergâha göre yaklaşık 95–110 km'dir; transfer ya da araçla trafiksiz 1 saat 15 dakika ile 1,5 saat sürer."),
        ("Sapanca'ya en yakın havalimanı hangisi?","Sabiha Gökçen Havalimanı'dır. İstanbul Havalimanı ise yaklaşık 170 km uzaklıktadır."),
        ("Sabiha Gökçen'den Sapanca'ya toplu taşımayla nasıl gidilir?","Havalimanından otobüsle Pendik YHT garına geçip YHT ile Arifiye'ye gidebilir (Pendik–Arifiye ~1 saat 15 dakika), Arifiye'den Kırkpınar'a taksiyle yaklaşık 15 dakikada ulaşabilirsiniz."),
        ("İstanbul Havalimanı'ndan Sapanca ne kadar sürer?","Yaklaşık 170 km'lik yol trafiksiz 2 saat civarında sürer; İstanbul trafiğine bağlı olarak çok daha uzun sürebilir. Transfer ya da kiralık araç en pratik seçenektir."),
        ("Gece inişlerinde Sapanca'ya nasıl gidilir?","Gece saatlerinde toplu taşıma seçenekleri azaldığı için önceden ayarlanmış bir transfer ya da kiralık araç önerilir."),
        ("DİDİ Otel otoyola yakın mı?","Evet. Otel Kırkpınar'dadır ve otoyolun Sapanca gişelerine yaklaşık 500 metre mesafededir; ücretsiz otopark bulunur.")],
},
{
 "slug":"kartepe-kayak-merkezi-rehberi","cat":"Mevsimler","img":"dis-cephe","date":"2026-11-16",
 "title":"Kartepe Kayak Merkezi Rehberi: Sapanca'da Kalıp Kayak Yapmak",
 "seo_title":"Kartepe Kayak Merkezi: Sapanca'dan Ulaşım ve Rehber",
 "img_alt":"DİDİ Otel Sapanca binasının cephesi ve palmiyeler, alt köşede otel logosu",
 "desc":"Kartepe Kayak Merkezi'ne Sapanca'dan 25–30 dakika. Pistler, lift sistemi, kızak, kış yolu ipuçları, aileler için plan ve göl kıyısında konaklama.",
 "related":["sapancada-kisin-gezilecek-yerler","sapanca-yilbasi-tatili","masukiye-kartepe-gezi"],
 "lead":"Kartepe Kayak Merkezi, İstanbul'a en yakın kayak merkezlerinden biridir ve Sapanca Kırkpınar'dan karayoluyla yaklaşık <strong>20 km, 25–30 dakika</strong> uzaklıktadır. Samanlı Dağları'nda yer alan merkezde farklı zorluk seviyelerinde orman içi pistler, telesiyej ve teleski hatları ile kızak alanları bulunur. Sapanca'da göl kıyısında konaklayıp gündüz kayak yapmak, dağda konaklamaya göre daha geniş akşam ve aktivite seçenekleri sunar. Sezon tarihleri her yıl kar durumuna göre belirlendiği için gitmeden önce pist durumunu mutlaka kontrol edin.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Mesafe:</strong> Kırkpınar → Kartepe Kayak Merkezi ~20 km, 25–30 dk (kış koşullarında daha uzun).</li>
<li><strong>Tesis:</strong> Kaynaklarda 12–17 arası pist, 3 telesiyej ve 2 teleski; kızak alanları ve ekipman kiralama.</li>
<li><strong>Sezon:</strong> Kar yağışına bağlı; açılış ve pist durumunu gitmeden önce kontrol edin.</li>
<li><strong>Yol:</strong> Kış lastiği şart, zincir bulundurun; hafta sonu sabahları erken çıkın.</li>
</ul></div>
<h2>Kartepe Kayak Merkezi nerede, Sapanca'dan nasıl gidilir?</h2>
<p>Kartepe Kayak Merkezi, Kocaeli'nin Kartepe ilçesinde, Samanlı Dağları üzerinde ve Maşukiye'nin güneyinde yer alır. Sapanca'dan gelirken önce <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'ye, oradan dağa tırmanan yola geçilir. OpenStreetMap rotalamasına göre Kırkpınar ile kayak merkezi arası yaklaşık 20 km'dir ve açık bir havada 25–30 dakika sürer. Karlı günlerde, özellikle virajlı son kesimde süre belirgin şekilde uzayabilir.</p>
<table><thead><tr><th>Nereden</th><th>Mesafe</th><th>Yaklaşık süre (açık havada)</th></tr></thead><tbody>
<tr><td>Kırkpınar / DİDİ Otel</td><td>~20 km</td><td>25–30 dk</td></tr>
<tr><td>Maşukiye</td><td>Yol üzerinde</td><td>~15–20 dk</td></tr>
<tr><td>İstanbul (Kadıköy)</td><td>~127 km</td><td>~1,5–2 saat</td></tr>
</tbody></table>
<h2>Kartepe'de kaç pist var? Tesise genel bakış</h2>
<p>Kartepe hakkında internette dolaşan rakamlar birbirini tutmuyor; bu yüzden aşağıdaki tabloyu kaynağı ve tarihiyle birlikte veriyoruz. Pist sayısındaki farklar, hangi pistlerin o sezon açık olduğuna ve sayım biçimine göre değişiyor olabilir.</p>
<table><thead><tr><th>Bilgi</th><th>Kaynakta geçen</th><th>Kaynak</th></tr></thead><tbody>
<tr><td>Pist sayısı</td><td>17 pist, 450–3.200 m uzunlukta</td><td>AA / CNN Türk, Şubat 2021</td></tr>
<tr><td>Pist sayısı (alternatif)</td><td>12 pist, 400–3.500 m</td><td>NTV haberi (tarihsiz)</td></tr>
<tr><td>Lift sistemi</td><td>3 telesiyej, 2 teleski</td><td>AA / CNN Türk 2021; Etstur rehberi</td></tr>
<tr><td>Kızak</td><td>2 kızak alanı</td><td>AA / CNN Türk 2021</td></tr>
<tr><td>Kiralama</td><td>Kayak, snowboard ve kıyafet kiralama, dolap</td><td>AA / CNN Türk 2021</td></tr>
<tr><td>Pist saatleri</td><td>Genel olarak 09:00–17:00</td><td>Etstur rehberi</td></tr>
</tbody></table>
<p class="note">Skipass fiyatları her sezon değişiyor ve resmi bir fiyat listesine ulaşamadık; bu nedenle burada fiyat vermiyoruz. Güncel tarifeyi kayak merkezinin kendi kanallarından öğrenin.</p>
<h2>Kayak sezonu ne zaman başlıyor?</h2>
<p>Kartepe'de sezonun açılışı tamamen kar yağışına bağlıdır; bazı yıllarda aralık ortasında, bazı yıllarda ocakta başlar ve kar durumuna göre mart ayına kadar sürebilir. Sapanca'nın kendisi ılıman olduğu için (Adapazarı'nda ocak ayı ortalama en düşük sıcaklığı 3,5 °C) göl kıyısında kar görmeseniz bile dağda kayak koşulları oluşmuş olabilir. Hafta sonu planı yapmadan önce kayak merkezinin pist durumu duyurularını ve hava tahminini kontrol edin.</p>
<h2>Yeni başlayanlar ve çocuklar için Kartepe</h2>
<p>Orman içinden geçen pistlerin bir kısmı yeni başlayanlara uygundur. İlk kez kayacaksanız tek başınıza piste çıkmak yerine merkezdeki kayak okullarından ders almanızı öneririz; ekipman kiralama da tesiste mümkündür. Kayak yapmayacak çocuklar için kızak alanları en eğlenceli seçenektir. Kalabalık hafta sonlarında kiralama ve lift kuyruklarında bekleme olabileceğinden açılış saatine yakın varmak günü verimli kılar.</p>
""" + fig("/assets/web/photos/d19","Sıcak ışıklı otel odasında ahşap başlıklı çift kişilik yatak, deri koltuklar ve televizyon ünitesi","Kayak dönüşü sıcak bir oda: DİDİ Otel Sapanca'dan bir oda görünümü.") + """
<h2>Sapanca'da kalıp Kartepe'de kaymanın avantajları</h2>
<table><thead><tr><th>Ölçüt</th><th>Dağda kalmak</th><th>Sapanca'da kalmak</th></tr></thead><tbody>
<tr><td>Piste mesafe</td><td>Yürüme mesafesi olabilir</td><td>25–30 dk sürüş</td></tr>
<tr><td>Akşam seçenekleri</td><td>Sınırlı</td><td>Göl kıyısı, restoranlar, Mare Gastro</td></tr>
<tr><td>Kayak yapmayanlar için</td><td>Az alternatif</td><td>Teleferik, Ormanya, Maşukiye, Kuzuluk termal</td></tr>
<tr><td>Ulaşım</td><td>Yalnızca karayolu</td><td>Tren seçeneği de var (Ada Ekspresi)</td></tr>
<tr><td>Kar yağdığında</td><td>Piste yakınsınız ama dönüş yolu zorlaşabilir</td><td>Göl kıyısı ılıman; yol durumuna göre esnek plan yapılır</td></tr>
</tbody></table>
<p>Ailede herkes kayak yapmıyorsa bu fark daha da belirginleşir: biri piste çıkarken diğerleri <a href="/blog/sapanca-teleferik-rehberi/">teleferikle</a> göl manzarasına çıkabilir, <a href="/blog/ormanya-rehberi/">Ormanya</a>'da yürüyüş yapabilir ya da <a href="/blog/kuzuluk-kaplicalari-rehberi/">Kuzuluk</a>'ta termal molası verebilir.</p>
<h2>Örnek kayak hafta sonu</h2>
<table><thead><tr><th>Zaman</th><th>Cumartesi</th><th>Pazar</th></tr></thead><tbody>
<tr><td>07:45</td><td>Erken kahvaltı</td><td>Kahvaltı</td></tr>
<tr><td>08:30</td><td>Kartepe'ye hareket (~30 dk)</td><td>Sahil yürüyüşü ya da teleferik (11:00)</td></tr>
<tr><td>09:00–15:00</td><td>Kayak / kızak</td><td>Maşukiye'de alabalık</td></tr>
<tr><td>16:00</td><td>Otele dönüş, sıcak duş</td><td>Kuzuluk'ta termal ya da dönüş</td></tr>
<tr><td>19:30</td><td>Mare Gastro'da akşam yemeği</td><td>—</td></tr>
</tbody></table>
<h2>Kayak yapmayanlar için Kartepe</h2>
<p>Kartepe'ye gitmek için kayak bilmek gerekmez. Kızak alanları çocuklar ve yetişkinler için en kolay eğlencedir; kar yokken bile Samanlı Dağları'nın zirvesine yakın bölgelerden Sapanca Gölü yönüne açılan manzara yolculuğa değer. Yakınındaki Kuzuyayla Tabiat Parkı, kışın karlı ormanda kısa yürüyüşler, yazın ise serin bir piknik için güzel bir duraktır. Grubunuzda kayak yapanlar ve yapmayanlar varsa, kayakçıları sabah bırakıp diğerleriyle Maşukiye'de dere kenarına inmek ve öğleden sonra yeniden buluşmak pratik bir düzendir.</p>
<h2>Hafta içi mi hafta sonu mu?</h2>
<p>Kayak merkezlerinde en büyük fark kalabalıktır. Hafta sonları ve özellikle sömestr tatili ile yılbaşı haftasında lift kuyrukları, ekipman kiralama ve otopark yoğunlaşır. Hafta içi bir gün ayırabiliyorsanız pistleri çok daha rahat kullanırsınız. Hafta sonu gidecekseniz Sapanca'dan sabah 08:30 civarında çıkıp açılışa yakın varmak, günün en iyi kar koşullarını yakalamanızı da sağlar; öğleden sonra kar yumuşar ve pistler bozulmaya başlar. Dönüşte dağ yolunda karanlığa kalmamak için gün batımı saatini (aralık–ocakta 17:30–18:00 civarı) aklınızda tutun.</p>
<h2>Kış yolu ve kayak çantası kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/7</b></div>
<div class="spot-check" data-key="kartepe-kayak">
<label><input type="checkbox"><span><b>Kış lastiği ve zincir</b><span>Dağ yolunda karlı ve buzlu kesimler olabilir.</span></span></label>
<label><input type="checkbox"><span><b>Pist ve yol durumunu kontrol edin</b><span>Sabah çıkmadan önce.</span></span></label>
<label><input type="checkbox"><span><b>Katmanlı giyim</b><span>Termal içlik, polar, su geçirmez dış katman.</span></span></label>
<label><input type="checkbox"><span><b>Eldiven, bere, gözlük</b><span>Kiralamada her zaman bulunmayabilir.</span></span></label>
<label><input type="checkbox"><span><b>Güneş kremi</b><span>Karda güneş yansıması güçlüdür.</span></span></label>
<label><input type="checkbox"><span><b>Kayak dersi</b><span>İlk kez kayacaksanız önceden ayarlayın.</span></span></label>
<label><input type="checkbox"><span><b>Yedek kuru kıyafet</b><span>Dönüşte arabada işe yarar.</span></span></label>
</div>
<h2>Kartepe için Sapanca'da nerede kalınır?</h2>
<p>Kartepe'ye en kısa yoldan çıkmak için gölün güney kıyısındaki Kırkpınar en pratik konumlardan biridir; Maşukiye yolu buradan başlar. <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur) ve misafirlerimiz için ücretsiz otopark bulunur. Kayak sonrası dinlenmek için <a href="/blog/sapanca-jakuzili-havuzlu-gol-manzarali-oda/">jakuzili oda seçeneklerimize</a>, kalabalık gruplar için <a href="/odalar/aile/">Aile</a> ve <a href="/odalar/triple/">Triple</a> odalarımıza göz atın. Erken kahvaltı ihtiyacınızı rezervasyonda belirtin; müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Kartepe%27de%20kayak%20i%C3%A7in%20Sapanca%27da%20konaklama%20yapmak%20istiyorum.">WhatsApp'tan</a> yazın. Kışın Sapanca'da yapılacak diğer şeyler için <a href="/blog/sapancada-kisin-gezilecek-yerler/">kışın gezilecek yerler</a> rehberimize bakın.</p>
""",
 "sources":[("İstanbul'a 'komşu' kayak merkezi: Kartepe (AA / CNN Türk, 23.02.2021)","https://cnnturk.com/seyahat/istanbula-komsu-kayak-merkezi-kartepe-1624483"),
            ("Kartepe Kayak Merkezi tatil rehberi (Etstur)","https://www.etstur.com/letsgo/kartepe-kayak-merkezi-tatil-rehberi/"),
            ("Adapazarı iklim verileri 1991–2020, MGM kaynaklı (Wikipedia)","https://en.wikipedia.org/wiki/Adapazar%C4%B1"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("Kartepe Kayak Merkezi Sapanca'ya ne kadar uzak?","Sapanca Kırkpınar'dan karayoluyla yaklaşık 20 km'dir; açık havada 25–30 dakika sürer, karlı günlerde süre uzayabilir."),
        ("Kartepe'de kaç pist var?","Kaynaklar farklı rakamlar veriyor: 2021 tarihli AA haberine göre 450–3.200 m uzunluğunda 17 pist, başka bir habere göre 12 pist bulunuyor. Lift sistemi 3 telesiyej ve 2 teleskiden oluşuyor."),
        ("Kartepe'de kayak sezonu ne zaman başlar?","Sezon tarihi kar yağışına bağlıdır; bazı yıllarda aralıkta, bazı yıllarda ocakta açılır. Gitmeden önce kayak merkezinin pist durumu duyurularını kontrol edin."),
        ("Kartepe'de ekipman kiralanabilir mi?","Evet, tesiste kayak, snowboard ve kıyafet kiralama ile dolap hizmeti olduğu belirtiliyor."),
        ("Kartepe'ye giderken zincir gerekir mi?","Karlı ve buzlu günlerde dağ yolunda kış lastiği şarttır; zincir bulundurmanız önerilir."),
        ("Kayak için neden Sapanca'da kalınır?","Kırkpınar'dan Kartepe'ye 25–30 dakikada ulaşılır; göl kıyısında daha geniş akşam seçenekleri, kayak yapmayanlar için teleferik, Ormanya ve termal gibi alternatifler ve tren bağlantısı bulunur.")],
},
{
 "slug":"ormanya-rehberi","cat":"Yakın Çevre","img":"ONN09446","date":"2026-11-16",
 "title":"Ormanya Rehberi: Sapanca'dan 15 Dakikada Hobbit Evleri ve Doğal Yaşam Parkı",
 "seo_title":"Ormanya Rehberi: Giriş, Saatler ve Sapanca'dan Ulaşım",
 "img_alt":"DİDİ Otel Sapanca'nın palmiyeler ve çiçekli çardaklarla çevrili bahçesi",
 "desc":"Ormanya nerede, giriş ücretli mi, saat kaçta açık? Hobbit evleri, yürüyüş parkurları, Sapanca'dan ~13 km ulaşım ve aileler için yarım günlük plan.",
 "related":["ailecek-sapanca-tatili","masukiye-kartepe-gezi","sapancada-gezilecek-yerler"],
 "lead":"Ormanya, Kocaeli'nin Kartepe ilçesine bağlı Uzuntarla Mahallesi'nde, geniş bir orman alanına kurulu doğal yaşam parkıdır. Sapanca Kırkpınar'dan karayoluyla yaklaşık <strong>13 km</strong>, trafiksiz 15 dakika uzaklıktadır. Hobbit evleri, hayvan gözlem alanları ve kilometrelerce yürüyüş-bisiklet parkuruyla özellikle çocuklu aileler için yarım günlük ideal bir duraktır. Basında yer alan bilgilere göre giriş ücretsizdir; saatler mevsime göre değişir ve bazı kaynaklara göre pazartesi günleri bakım nedeniyle ziyaretçi kabul edilmez. Gitmeden önce güncel durumu teyit etmenizi öneririz.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Konum:</strong> Uzuntarla, Kartepe / Kocaeli — Kırkpınar'dan ~13 km, ~15 dk.</li>
<li><strong>Giriş:</strong> Basındaki bilgilere göre ücretsiz; otopark ve kamp alanları ücretli olabilir.</li>
<li><strong>Saatler:</strong> Kaynaklara göre yaklaşık yazın 09:00–20:00, kışın 09:00–17:00; pazartesi kapalı olabilir.</li>
<li><strong>Kime:</strong> Çocuklu aileler, yürüyüşçüler, fotoğraf meraklıları.</li>
</ul></div>
<h2>Ormanya nerede ve Sapanca'dan nasıl gidilir?</h2>
<p>Ormanya, Sapanca Gölü'nün kuzeybatısında, Kartepe ilçesinin Uzuntarla Mahallesi'ndedir. Sapanca'dan gelirken Anadolu Otoyolu (TEM) ya da D-100 üzerinden Kartepe yönüne sapılır; tabelalar sizi parka yönlendirir. OpenStreetMap rotalamasına göre Kırkpınar'dan Ormanya'ya yol yaklaşık 13 km'dir ve trafiksiz 15 dakika sürer. Hafta sonu ve bayram günlerinde park girişinde araç yoğunluğu oluşabildiği için sabah erken saatte gitmek en rahat seçenektir.</p>
<table><thead><tr><th>Nereden</th><th>Mesafe</th><th>Yaklaşık süre</th></tr></thead><tbody>
<tr><td>Kırkpınar / DİDİ Otel</td><td>~13 km</td><td>~15 dk</td></tr>
<tr><td>Maşukiye</td><td>Yakın komşu</td><td>~10 dk</td></tr>
<tr><td>Sapanca Teleferik</td><td>~13 km</td><td>~15 dk</td></tr>
<tr><td>İstanbul (Anadolu Yakası)</td><td>~110–120 km</td><td>~1,5 saat</td></tr>
</tbody></table>
<p>Toplu taşımayla gitmek isteyenler için İzmit merkezden belediye otobüsü ve minibüs seçenekleri olduğu belirtiliyor; Sapanca'dan ise en pratik yol taksi ya da kendi aracınızdır.</p>
<h2>Ormanya'da neler var?</h2>
<p>Basında yer alan rehberlere göre parkın başlıca bölümleri şunlar:</p>
<table><thead><tr><th>Bölüm</th><th>Ne bulursunuz?</th><th>Kime uygun</th></tr></thead><tbody>
<tr><td>Hobbit evleri</td><td>Toprağa gömülü, yuvarlak kapılı minyatür evler</td><td>Çocuklar ve fotoğraf meraklıları</td></tr>
<tr><td>Hayvan gözlem alanları</td><td>Geyik, lama, tavus kuşu gibi türler; çocuk hayvanat bahçesi</td><td>Aileler</td></tr>
<tr><td>Yürüyüş ve bisiklet parkurları</td><td>Zorluk derecesine göre işaretli, toplam ~26 km parkur</td><td>Yürüyüşçüler, bisikletçiler</td></tr>
<tr><td>Eğitim alanları</td><td>Doğa okulu, orman kütüphanesi, böcek oteli</td><td>Okul çağındaki çocuklar</td></tr>
<tr><td>Piknik ve kamp</td><td>Piknik alanları, kamp ve karavan bölümleri</td><td>Günübirlikçiler, kampçılar</td></tr>
</tbody></table>
<p>Parkın büyüklüğü kaynaklarda farklı veriliyor: bazı haberlerde yaklaşık 2.000 dönüm, bazılarında 4.000 dönüm olarak geçiyor. Hangisi olursa olsun, tamamını bir günde gezmek zor; yarım günlük bir planla Hobbit evleri, hayvan alanları ve kısa bir yürüyüş parkurunu rahatça görebilirsiniz.</p>
<h2>Ormanya giriş ücreti var mı?</h2>
<p>2025 tarihli haberlere göre Ormanya'ya giriş ücretsizdir. Otopark için bazı dönemlerde ücret alınabildiği, kamp ve karavan alanlarındaki elektrik-su gibi hizmetlerin ise ücretli olduğu belirtiliyor. Belediye işletmelerinde ücret politikaları değişebildiğinden, gitmeden önce Kocaeli Büyükşehir Belediyesi'nin güncel duyurularına bakmanızı öneririz.</p>
<h2>Ormanya saat kaçta açılıyor, hangi gün kapalı?</h2>
<p>Kaynaklarda verilen saatler mevsime göre şöyle özetlenebilir: yaz aylarında yaklaşık <strong>09:00–20:00</strong>, kış aylarında yaklaşık <strong>09:00–17:00</strong>. Bazı kaynaklar parkın <strong>pazartesi günleri</strong> temizlik ve hayvan bakımı için ziyaretçi kabul etmediğini yazıyor. Pazartesiye denk gelen bir planınız varsa mutlaka önceden teyit edin; hafta sonu planlarında bu bir sorun oluşturmaz.</p>
<p class="note">Saat ve kapalı gün bilgileri basında yer alan rehberlerden derlenmiştir ve resmi bir tarifeye dayanmamaktadır. Kesin bilgi için parkın işletmecisi Kocaeli Büyükşehir Belediyesi'ne başvurun.</p>
""" + fig("/assets/web/editorial/ONN09447","Beyaz ahşap bankta minderin üzerinde dinlenen gri British cinsi kedi","DİDİ Otel'in bahçesinden bir kare: beyaz bankta dinlenen gri kedi.") + """
<h2>Ailelerle Ormanya'da yarım gün nasıl geçer?</h2>
<table><thead><tr><th>Saat</th><th>Plan</th></tr></thead><tbody>
<tr><td>09:00</td><td>Otelde kahvaltı</td></tr>
<tr><td>10:00</td><td>Ormanya'ya hareket (~15 dk)</td></tr>
<tr><td>10:15–11:30</td><td>Hobbit evleri ve hayvan gözlem alanları</td></tr>
<tr><td>11:30–12:30</td><td>Kısa, işaretli bir yürüyüş parkuru</td></tr>
<tr><td>13:00</td><td>Maşukiye'de dere kenarında alabalık (~10 dk)</td></tr>
<tr><td>15:00</td><td>Otele dönüş, dinlenme; yazın havuz</td></tr>
</tbody></table>
<p>Küçük çocuklarla puset kullanılabilecek düz yolları tercih edin; bazı parkurlar eğimli ve yağmur sonrası çamurlu olabilir. Yanınıza su, atıştırmalık ve yedek kıyafet almak iyi fikirdir.</p>
<h2>Hangi mevsimde gitmeli?</h2>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="ilk">İlkbahar</button><button data-tab="yaz">Yaz</button><button data-tab="son">Sonbahar</button><button data-tab="kis">Kış</button></div>
<div class="itin-panel on" data-tab="ilk"><p>Orman yeşillenir, hayvanlar daha hareketlidir; yürüyüş için en keyifli dönem.</p></div>
<div class="itin-panel" data-tab="yaz"><p>Uzun saatler sayesinde sabah ya da akşamüstü gidin; öğle sıcağını Sapanca'da havuzda geçirin.</p></div>
<div class="itin-panel" data-tab="son"><p>Renkli yapraklar ve serin hava. Kış saatlerine geçişte kapanış öne çekilebilir. <a href="/blog/sapancada-sonbahar-rehberi/">Sonbahar rehberi</a></p></div>
<div class="itin-panel" data-tab="kis"><p>Kısa gün ışığı nedeniyle öğleden önce gidin; yağmur sonrası patikalar çamurlu olabilir.</p></div>
</div>
<h2>Ormanya, Maşukiye ve teleferik: tam gün rotası</h2>
<p>Ormanya, Maşukiye ve Sapanca Teleferik birbirine çok yakın olduğu için üçünü tek bir günde birleştirmek mümkündür. Sabah açılışa yakın Ormanya'ya gidip kalabalık başlamadan Hobbit evlerini ve hayvan alanlarını gezin. Öğle yemeğini yaklaşık 10 dakika uzaklıktaki Maşukiye'de dere kenarında yapın. Öğleden sonra Kırkpınar'a dönüp teleferikle göle kuşbakışı bakın; teleferik her gün 11:00–19:00 arasında açıktır. Günü göl kıyısında gün batımı yürüyüşüyle kapatabilirsiniz. Bu rota için toplam sürüş süresi bir saati geçmez; günün büyük kısmını yolda değil doğada geçirirsiniz.</p>
<h2>Ormanya'da fotoğraf ipuçları</h2>
<ul>
<li><strong>Işık:</strong> Orman içinde öğle saatlerinde gölge-güneş kontrastı sert olur; sabah ve akşamüstü ışığı Hobbit evleri için daha yumuşaktır.</li>
<li><strong>Kalabalık:</strong> Hafta sonu öğleden sonra en popüler noktalarda sıra olabilir; boş kareler için erken gidin.</li>
<li><strong>Hayvanlar:</strong> Hayvanları korkutmamak için flaş kullanmayın ve çitlerin dışından çekin.</li>
<li><strong>Mevsim:</strong> İlkbahar yeşili ve sonbahar renkleri parkın en fotojenik dönemleridir.</li>
</ul>
<h2>Ormanya'ya gitmeden önce kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="ormanya">
<label><input type="checkbox"><span><b>Açık olduğu günü teyit edin</b><span>Bazı kaynaklara göre pazartesi kapalı.</span></span></label>
<label><input type="checkbox"><span><b>Erken gidin</b><span>Hafta sonu girişte araç kuyruğu olabilir.</span></span></label>
<label><input type="checkbox"><span><b>Rahat ayakkabı</b><span>Parkurlar toprak ve eğimli olabilir.</span></span></label>
<label><input type="checkbox"><span><b>Su ve atıştırmalık</b><span>Uzun yürüyüşler için.</span></span></label>
<label><input type="checkbox"><span><b>Hayvanları beslemeyin</b><span>Parkın kurallarına uyun.</span></span></label>
<label><input type="checkbox"><span><b>Öğle yemeği planı</b><span>Maşukiye ~10 dakika uzakta.</span></span></label>
</div>
<h2>Ormanya gezisi için Sapanca'da nerede kalınır?</h2>
<p>Ormanya'yı Sapanca gezisine eklemenin en kolay yolu, gölün güney kıyısındaki Kırkpınar'da kalmaktır: Ormanya 15, Maşukiye 10–15 dakika, teleferik ise aynı mahalledir. <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur); dört kişilik <a href="/odalar/aile/">Aile Odası</a> ve üç kişilik <a href="/odalar/triple/">Triple Oda</a> çocuklu aileler için pratik seçeneklerdir. Bahçedeki <a href="/#mare">Mare Gastro</a>'ya saat 15:00'ten sonra çocuk kabul edilmediğini hatırlatalım; çocuklu akşamlar için planınızı buna göre yapın. Ailelere yönelik diğer öneriler <a href="/blog/ailecek-sapanca-tatili/">ailecek Sapanca tatili</a> yazımızda. Müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Ormanya%20ve%20Sapanca%20gezisi%20i%C3%A7in%20aile%20konaklamas%C4%B1%20sormak%20istiyorum.">WhatsApp'tan</a> yazın.</p>
""",
 "sources":[("Ormanya ziyaret rehberi: giriş, saatler ve olanaklar (Türkgün, 25.06.2025)","https://www.turkgun.com/turizm/ormanya-ziyaret-rehberi-giris-ucreti-saatleri-ve-tarihi-bilgiler/298803"),
            ("Ormanya Tabiat Parkı nerede, nasıl gidilir? (Milliyet, 25.09.2020)","https://www.milliyet.com.tr/tatil/ormanya-tabiat-parki-kocaeli-ilinde-nerede-nasil-gidilir-giris-ucreti-ve-adres-bilgileri-6314650"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("Ormanya nerede?","Ormanya, Kocaeli'nin Kartepe ilçesine bağlı Uzuntarla Mahallesi'ndedir. Sapanca Kırkpınar'dan karayoluyla yaklaşık 13 km, trafiksiz 15 dakika uzaklıktadır."),
        ("Ormanya giriş ücreti ne kadar?","2025 tarihli haberlere göre girişler ücretsizdir. Otopark ve kamp-karavan alanlarındaki hizmetler için ücret alınabilir; güncel durumu Kocaeli Büyükşehir Belediyesi'nden teyit edin."),
        ("Ormanya saat kaçta açılıyor?","Kaynaklara göre yaz aylarında yaklaşık 09:00–20:00, kış aylarında yaklaşık 09:00–17:00 arası açıktır. Saatler mevsime göre değişebilir."),
        ("Ormanya pazartesi açık mı?","Bazı kaynaklara göre Ormanya pazartesi günleri temizlik ve hayvan bakımı nedeniyle ziyaretçi kabul etmemektedir. Pazartesi gitmeyi planlıyorsanız önceden teyit edin."),
        ("Ormanya'da ne var?","Hobbit evleri, geyik ve lama gibi hayvanların bulunduğu gözlem alanları, çocuk hayvanat bahçesi, işaretli yürüyüş ve bisiklet parkurları, doğa okulu, piknik ve kamp alanları bulunur."),
        ("Ormanya'yı gezmek ne kadar sürer?","Hobbit evleri, hayvan alanları ve kısa bir yürüyüş için 2–3 saat yeterlidir; parkurların tamamını yürümek isteyenler tam gün ayırmalıdır.")],
},
{
 "slug":"sapanca-golu-hakkinda-bilgiler","cat":"Doğa","img":"ONN09464","date":"2026-11-16",
 "title":"Sapanca Gölü Hakkında: Derinliği, Büyüklüğü ve Yüzülür mü?",
 "seo_title":"Sapanca Gölü: Derinliği, Büyüklüğü ve Yüzülür mü?",
 "img_alt":"Begonvil çiçeklerinin ardından görünen şezlonglar, şemsiyeler ve otel havuzu",
 "desc":"Sapanca Gölü kaç km², kaç metre derin, yüzülür mü? Gölün kimlik kartı, içme suyu ve koruma çalışmaları, su seviyesi, kuşlar ve güvenlik uyarıları.",
 "related":["sapanca-golu-aktiviteler","sapancada-gezilecek-yerler","sapanca-bisiklet-yuruyus-parkurlari"],
 "lead":"Sapanca Gölü, Sakarya ile Kocaeli arasında, deniz seviyesinden yaklaşık <strong>33 metre</strong> yükseklikte uzanan bir tatlı su gölüdür. Yüzölçümü yaklaşık <strong>45 km²</strong>, doğu–batı uzunluğu <strong>16 km</strong>, ortalama derinliği <strong>36 m</strong>, en derin noktası ise yaklaşık <strong>52 m</strong>'dir. Göl, Sakarya'nın içme suyunun yaklaşık yüzde 90'ını karşılar ve Kocaeli'ye de su verir. Gölde yüzme konusunda tek bir ulusal kural yoktur; ancak içme suyu kaynağı olması, ani derinleşen kıyıları ve ani rüzgârları nedeniyle biz misafirlerimize gölde yüzmeyi önermiyoruz. Aşağıda gölle ilgili en çok merak edilenleri kaynaklarıyla topladık.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Büyüklük:</strong> ~45 km² yüzey, 16 × 5 km, ~1,7 km³ su hacmi.</li>
<li><strong>Derinlik:</strong> ortalama 36 m, en derin ~52 m (bazı kaynaklarda 61 m).</li>
<li><strong>Önemi:</strong> Sakarya'nın içme suyunun ~%90'ı; Kocaeli'ye içme, sanayiye kullanma suyu.</li>
<li><strong>Yüzme:</strong> Güncel kuralı yerel yönetimden öğrenin; içme suyu kaynağı ve güvenlik riskleri nedeniyle önermiyoruz.</li>
</ul></div>
<h2>Sapanca Gölü'nün kimlik kartı</h2>
<table><thead><tr><th>Özellik</th><th>Değer</th></tr></thead><tbody>
<tr><td>Konum</td><td>Sakarya ile Kocaeli arasında; kıyıları ağırlıkla Sapanca ve Serdivan'da</td></tr>
<tr><td>Yüzölçümü</td><td>~45 km² (uzun dönem ortalaması 46,9 km²)</td></tr>
<tr><td>Uzunluk / genişlik</td><td>~16 km doğu–batı, ~5 km kuzey–güney</td></tr>
<tr><td>Ortalama derinlik</td><td>~36 m</td></tr>
<tr><td>En derin nokta</td><td>~52 m (kaynağın başka bir bölümünde 61 m)</td></tr>
<tr><td>Su hacmi</td><td>~1,7 km³</td></tr>
<tr><td>Rakım</td><td>Deniz seviyesinden ~33 m</td></tr>
<tr><td>Su seviyesi yönetimi</td><td>Çark Deresi çıkışındaki savakla, planlanan aralık 29,90–31,50 m</td></tr>
<tr><td>Balık çeşitliliği</td><td>11 familyadan 40 tür</td></tr>
</tbody></table>
<p class="note">Değerler Wikipedia'daki "Lake Sapanca" maddesinde derlenen kaynaklardan alınmıştır. Göl alanı ve derinlik, su seviyesine göre yıldan yıla değişir; kuraklık dönemlerinde kıyı çizgisi belirgin şekilde geri çekilebilir.</p>
<h2>Sapanca Gölü kaç metre derin?</h2>
<p>Gölün ortalama derinliği yaklaşık 36 metre, en derin noktası ise yaklaşık 52 metredir; aynı kaynağın başka bir bölümünde 61 metre değeri de geçer. İnternette sık karşılaşılan bir karışıklık, SASKİ'nin duyurduğu "su seviyesi" kotlarının (ör. 31–32 m) derinlik sanılmasıdır. Bu değerler gölün deniz seviyesine göre yüksekliğini, yani kotunu gösterir; derinlikle ilgisi yoktur.</p>
<h2>Sapanca Gölü kaç km²?</h2>
<p>Göl yaklaşık 45 km² yüzölçümüne sahiptir; uzun dönem ortalaması 46,9 km² olarak verilir. Bazı sitelerde geçen "251 km²" rakamı ise gölün kendisini değil, gölü besleyen <strong>su toplama havzasını</strong> ifade eder (kaynakta havza için 251 ve 296 km² değerleri geçer). Gölün çevresini karayoluyla dolaşan rotalar, seçilen yola göre 45–50 km tutar.</p>
<h2>Sapanca Gölü'nde yüzülür mü?</h2>
<p>Bu en çok sorulan soru ve kısa cevabı şu: göl, binlerce kişinin musluğundan akan suyun kaynağıdır ve SASKİ tarafından sıkı bir koruma altında yönetilir. Kıyıda yüzmeye dair kural ve tabelalar bölgeden bölgeye değişebildiği için güncel durumu Sakarya Büyükşehir Belediyesi ve SASKİ'den ya da kıyıdaki uyarı tabelalarından öğrenmelisiniz. Biz misafirlerimize gölde yüzmeyi önermiyoruz; nedenleri:</p>
<ul>
<li><strong>İçme suyu kaynağı:</strong> Güneş kremi, sabun ve benzeri her madde doğrudan içme suyuna karışır.</li>
<li><strong>Ani derinleşme:</strong> Ortalama derinliği 36 m olan bir gölde kıyıdan kısa mesafede derinlik hızla artabilir.</li>
<li><strong>Ani rüzgâr:</strong> 22 Temmuz 2026 akşamı ani bir fırtınada SUP ve botlarla göle açılan 35 kişi AFAD tarafından kurtarıldı; Temmuz 2025'te de güçlü rüzgâr nedeniyle 17 kişi kurtarılmıştı.</li>
<li><strong>Soğuk su:</strong> Yaz dışında su sıcaklığı yüzmeye uygun değildir.</li>
</ul>
<p>Serinlemek istiyorsanız havuz sezonunda otelimizin <a href="/blog/sapancada-havuzlu-otel/">klorsuz havuzunu</a> kullanabilirsiniz; gölün tadını ise kıyıda yürüyerek, bisikletle ya da can yeleğiyle SUP yaparak çıkarabilirsiniz. Ayrıntılar <a href="/blog/sapanca-golu-aktiviteler/">Sapanca Gölü aktiviteleri</a> yazımızda.</p>
""" + fig("/assets/web/editorial/havuz1","DİDİ Otel Sapanca'nın açık havuzu, havuz kenarında şemsiyeler ve palmiyeler, binada otel logosu","Göl yerine havuz: sezonda Sapanca'nın tek klorsuz havuzu.") + """
<h2>Göl neden bu kadar önemli? İçme suyu ve koruma</h2>
<p>Wikipedia'da derlenen bilgilere göre Sapanca Gölü, Sakarya kentinin içme suyunun yaklaşık yüzde 90'ını karşılar, Kocaeli'ye içme suyu ve Tüpraş'a kullanma suyu verir. Son yıllarda yaşanan kuraklık, gölün su seviyesini kayıtların en düşük seviyelerine indirdi; bu nedenle Sakarya Büyükşehir Belediyesi ve SASKİ çeşitli önlemler aldı:</p>
<ul>
<li>Kıyıdaki kaçak iskele ve yapıların kaldırılması,</li>
<li>Göl çevresinde düzenli kıyı temizliği,</li>
<li>Bilim insanlarından oluşan bir kurulun göl yönetimine rehberlik etmesi,</li>
<li>Kayıp-kaçak kontrollerinin sıkılaştırılması ve su çekiminin kontrollü yapılması.</li>
</ul>
<p>Ziyaretçi olarak katkımız basit: kıyıda çöp bırakmamak, mangal ve ateşi yalnızca izin verilen alanlarda yakmak ve göle hiçbir şey karıştırmamak.</p>
<h2>Gölde hangi kuşlar ve balıklar yaşıyor?</h2>
<p>Göl, 11 familyadan 40 balık türüne ev sahipliği yapar. Su kuşları açısından da önemlidir: kaynakta, küresel ölçekte koruma statüsü olan <strong>pasbaş patka</strong> (neredeyse tehdit altında) ve <strong>dikkuyruk</strong> (tehlike altında) gölde kaydedilen türler arasında sayılır. Kuş gözlemi için en iyi zaman, sazlık kıyılarda sabahın ilk saatleri ile ilkbahar ve sonbahar göç dönemleridir.</p>
<h2>Gölü en güzel nereden görürsünüz?</h2>
<table><thead><tr><th>Nokta</th><th>Neden?</th><th>İlgili rehber</th></tr></thead><tbody>
<tr><td>Sapanca Teleferik</td><td>319 m yükselerek göle kuşbakışı</td><td><a href="/blog/sapanca-teleferik-rehberi/">Teleferik rehberi</a></td></tr>
<tr><td>Kırkpınar sahili</td><td>Gün batımında güneyden göle bakış</td><td><a href="/blog/sapancada-fotograf-gun-batimi-noktalari/">Fotoğraf noktaları</a></td></tr>
<tr><td>Uzunkum</td><td>Bisiklet-yürüyüş yolu, piknik</td><td><a href="/blog/sapanca-bisiklet-yuruyus-parkurlari/">Bisiklet ve yürüyüş</a></td></tr>
<tr><td>Mahmudiye tarafı</td><td>Yamaçtan geniş göl manzarası</td><td><a href="/blog/poyrazlar-golu-mahmudiye-gizli-koseler/">Mahmudiye ve gizli köşeler</a></td></tr>
</tbody></table>
<h2>Gölün su seviyesi neden değişiyor?</h2>
<p>Sapanca Gölü'nün seviyesi doğal bir kıyı çizgisiyle sabit durmaz; yağış, buharlaşma ve içme suyu için yapılan çekimle sürekli değişir. Gölün çıkışındaki Çark Deresi üzerindeki savak sayesinde seviye belirli bir aralıkta tutulmaya çalışılır; kaynakta bu planlanan aralık 29,90 ile 31,50 metre kotları arasında verilir. Kurak geçen yıllarda gölün beslendiği dereler zayıflar, buharlaşma artar ve kıyı çizgisi geri çekilir. Son yıllarda yaşanan kuraklıkta seviyenin kayıtların en düşüklerine indiği haberleri bu yüzden çıktı. Seviye haberlerini okurken bir kez daha hatırlatalım: 31–32 metre gibi rakamlar gölün derinliği değil, deniz seviyesine göre yüksekliğidir.</p>
<h2>Mevsimlere göre Sapanca Gölü</h2>
<table><thead><tr><th>Mevsim</th><th>Göl nasıl görünür?</th><th>Ne yapılır?</th></tr></thead><tbody>
<tr><td>İlkbahar</td><td>Dolgun, yeşil kıyılar</td><td>Bisiklet, kuş gözlemi</td></tr>
<tr><td>Yaz</td><td>Parlak, sabahları sakin</td><td>SUP, gün batımı, havuz</td></tr>
<tr><td>Sonbahar</td><td>Sisli sabahlar, renkli yamaçlar</td><td>Yürüyüş, fotoğraf</td></tr>
<tr><td>Kış</td><td>Puslu, ara ara karlı manzara</td><td>Kıyı yürüyüşü, teleferikten manzara</td></tr>
</tbody></table>
<h2>Göl kıyısında kalmak</h2>
<p>Gölü sabahın sisinde ve akşamın altın ışığında görmek için kıyıya yakın kalmak gerekir. <a href="/#konum">DİDİ Otel Sapanca</a>, gölün güney kıyısındaki Kırkpınar'da, göl ile orman arasında yer alır; sahile ve teleferiğe kısa mesafededir. Kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur), akşam yemeği için bahçedeki <a href="/#mare">Mare Gastro</a> hemen yanınızdadır. <a href="/odalar/">Oda seçeneklerimizi</a> inceleyin ya da müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%20G%C3%B6l%C3%BC%20kenar%C4%B1nda%20konaklama%20i%C3%A7in%20m%C3%BCsaitlik%20sormak%20istiyorum.">WhatsApp'tan</a> yazın.</p>
""",
 "sources":[("Lake Sapanca — ölçüler, su kullanımı, balık ve kuş türleri (Wikipedia)","https://en.wikipedia.org/wiki/Lake_Sapanca"),
            ("Sapanca Gölü'nün geleceğine bilim kurulu rehberlik edecek (Sakarya Büyükşehir Belediyesi)","https://sakarya.bel.tr/tr/Haber/sapanca-golunun-gelecegine-‘bilim-kurulu-rehberlik-edecek/25975"),
            ("Sapanca Gölü kıyılarında kaçak iskele kaldırma süreci (Sakarya Büyükşehir Belediyesi)","https://sakarya.bel.tr/tr/Haber/sapanca-golunun-kiyilarinda-kacak-iskele-kaldirma-surecinin-ikinci-etabi-basladi/26199"),
            ("Kuraklığa karşı yeni önlemler: kayıp-kaçak ve kontrollü su çekimi (Sakarya Büyükşehir Belediyesi)","https://sakarya.bel.tr/tr/Haber/kurakligin-olumsuz-etkilerine-karsi-kesintisiz-hizmet-icin-yeni-onlemler-alindi/25144"),
            ("Sapanca Gölü alarm veriyor: su seviyesi tarihin en düşük noktasında (Dünya)","https://www.dunya.com/foto-galeri/yasam/sapanca-golu-alarm-veriyor-su-seviyesi-tarihin-en-dusuk-noktasinda-galeri-807468"),
            ("Sapanca Gölü'nde fırtınaya yakalanan 35 kişi kurtarıldı (GZT, 23.07.2026)","https://www.gzt.com/gundem/sapanca-golunde-firtinaya-yakalanan-35-kisi-afad-ekiplerince-kurtarildi-4243982"),
            ("Sapanca Gölü'nde 2 saatte 17 kişi boğulmaktan kurtarıldı (Hürriyet, 06.07.2025)","https://www.hurriyet.com.tr/gundem/sapanca-golunde-2-saatte-17-kisi-bogulmaktan-kurtarildi-42867077")],
 "faq":[("Sapanca Gölü kaç metre derin?","Ortalama derinliği yaklaşık 36 m, en derin noktası yaklaşık 52 m'dir; bazı kaynaklarda 61 m değeri de geçer. SASKİ'nin duyurduğu 31–32 m gibi değerler derinlik değil, gölün su seviyesi kotudur."),
        ("Sapanca Gölü kaç km²?","Yaklaşık 45 km²'dir (uzun dönem ortalaması 46,9 km²). 251 km² rakamı gölün değil, onu besleyen su toplama havzasının büyüklüğüdür."),
        ("Sapanca Gölü'nde yüzülür mü?","Göl bir içme suyu kaynağıdır ve kurallar bölgeye göre değişebilir; güncel durumu Sakarya Büyükşehir Belediyesi ve SASKİ'den öğrenin. İçme suyu, ani derinleşme ve ani rüzgâr riskleri nedeniyle gölde yüzmeyi önermiyoruz."),
        ("Sapanca Gölü içme suyu mu?","Evet. Göl, Sakarya'nın içme suyunun yaklaşık yüzde 90'ını karşılar; Kocaeli'ye de içme suyu ve sanayiye kullanma suyu verir."),
        ("Sapanca Gölü'nün uzunluğu ne kadar?","Göl doğu–batı yönünde yaklaşık 16 km, kuzey–güney yönünde yaklaşık 5 km uzanır."),
        ("Sapanca Gölü'nde hangi balıklar var?","Gölde 11 familyadan 40 balık türü kaydedilmiştir. Göl ayrıca pasbaş patka ve dikkuyruk gibi koruma statüsündeki su kuşlarına da ev sahipliği yapar.")],
},
{
 "slug":"sapanca-yilbasi-tatili","cat":"Mevsimler","img":"lobi","date":"2026-11-16",
 "title":"Sapanca'da Yılbaşı: 2027'ye Göl Kıyısında Girmek İçin Plan Rehberi",
 "seo_title":"Sapanca'da Yılbaşı 2027: Konaklama ve Plan Rehberi",
 "img_alt":"DİDİ Otel Sapanca lobisi, büyük cam kapılar, kitaplık ve oturma alanı",
 "desc":"Sapanca'da yılbaşı 2027: 31 Aralık perşembe, uzun hafta sonu fırsatı. Aralık hava durumu, Kartepe, teleferik, trafik ipuçları ve oda seçimi.",
 "related":["sapancada-kisin-gezilecek-yerler","kartepe-kayak-merkezi-rehberi","sapancada-romantik-hafta-sonu"],
 "lead":"Sapanca'da yılbaşı tatili için 2026–2027 takvimi oldukça elverişli: <strong>31 Aralık 2026 perşembe</strong>, <strong>1 Ocak 2027 ise cuma</strong> günüdür; yani perşembe-pazar arası üç gecelik bir uzun hafta sonu yapmak mümkün. Aralıkta Sapanca'da gündüz ortalama en yüksek sıcaklık 12 °C civarında, ay boyunca yaklaşık 16 gün yağışlıdır; karlı bir yılbaşı isteyenler için Kartepe 25–30 dakika uzaklıktadır. En kritik iki konu ise erken rezervasyon ve 31 Aralık öğleden sonraki otoyol trafiğidir. Aşağıda yılbaşını Sapanca'da geçirmek için adım adım bir plan bulacaksınız.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Takvim:</strong> 31 Aralık perşembe → 1 Ocak cuma; perşembe–pazar 3 gece mümkün.</li>
<li><strong>Hava:</strong> Aralık ort. 5–12 °C, ~16 yağışlı gün; kar için Kartepe.</li>
<li><strong>Işık:</strong> 31 Aralık'ta gün batımı ~17:41, 1 Ocak'ta gün doğumu ~08:23.</li>
<li><strong>Rezervasyon:</strong> Yılbaşı dönemi koşullarını (minimum gece vb.) önceden sorun; erken davranın.</li>
</ul></div>
<h2>Yılbaşı 2027 hangi güne denk geliyor?</h2>
<p>31 Aralık 2026 perşembe, 1 Ocak 2027 cuma günüdür. Cuma resmi tatil olduğu için çalışanların çoğu perşembe akşamından pazar akşamına kadar dört günlük bir pencere yakalar. Bu da Sapanca için ideal bir senaryo: perşembe öğleden sonra yola çıkıp yılbaşı gecesini otelde geçirebilir, cuma ve cumartesiyi göl, dağ ve termal arasında bölüştürüp pazar günü trafiğe kalmadan dönebilirsiniz.</p>
<table><thead><tr><th>Plan</th><th>Giriş</th><th>Çıkış</th><th>Kime uygun</th></tr></thead><tbody>
<tr><td>Kısa</td><td>31 Aralık perşembe</td><td>1 Ocak cuma</td><td>Yalnızca yılbaşı gecesini kutlamak isteyenler</td></tr>
<tr><td>Dengeli</td><td>31 Aralık perşembe</td><td>2 Ocak cumartesi</td><td>Yılın ilk gününü dinlenerek ve gezerek geçirmek isteyenler</td></tr>
<tr><td>Uzun</td><td>31 Aralık perşembe</td><td>3 Ocak pazar</td><td>Kartepe, Kuzuluk ve Maşukiye'yi de ekleyecekler</td></tr>
</tbody></table>
<h2>Aralık ve ocakta Sapanca'da hava nasıl?</h2>
<p>Sapanca'nın kışı ılımandır; göl kıyısında zaman zaman kar yağar, ancak karlı manzarayı garantilemek için dağa çıkmak gerekir. Türkiye Meteoroloji Genel Müdürlüğü kaynaklı 1991–2020 Adapazarı normalleri şöyle:</p>
<table><thead><tr><th>Ay</th><th>Ort. en yüksek</th><th>Ort. en düşük</th><th>Yağış</th><th>Yağışlı gün</th></tr></thead><tbody>
<tr><td>Aralık</td><td>12,1 °C</td><td>5,3 °C</td><td>109 mm</td><td>~16</td></tr>
<tr><td>Ocak</td><td>10,2 °C</td><td>3,5 °C</td><td>96 mm</td><td>~16</td></tr>
</tbody></table>
<p>Pratik anlamı: yılbaşı haftasında yağmurlu bir güne denk gelme ihtimaliniz yüksek, ama dondurucu soğuk beklemeyin. Karlı manzara istiyorsanız rakımı yüksek <a href="/blog/kartepe-kayak-merkezi-rehberi/">Kartepe</a>'ye çıkmanız gerekir. Yağmurlu günler için fikirler <a href="/blog/sapancada-yagmurlu-havada-ne-yapilir/">yağmurlu havada ne yapılır</a> yazımızda.</p>
<h2>Sapanca'da yılbaşında ne yapılır?</h2>
<h3>Yılın ilk gün doğumu: göl kıyısı</h3>
<p>1 Ocak 2027'de Sapanca'da güneş yaklaşık <strong>08:23</strong>'te doğar. Yılbaşı gecesinden sonra erken kalkmak zor olabilir ama göl kıyısında, sisin içinden yükselen ilk ışığı izlemek yeni yıla güzel bir başlangıçtır. Kırkpınar sahili otele birkaç dakika uzaklıktadır.</p>
<h3>Kartepe'de kar ve kayak</h3>
<p>Kar yağışına bağlı olarak Kartepe Kayak Merkezi'nde sezon genellikle aralık ayında açılır; yılbaşı haftası kayak merkezlerinin en yoğun dönemidir. Pist ve sezon durumunu gitmeden önce mutlaka kontrol edin. Ayrıntılar <a href="/blog/kartepe-kayak-merkezi-rehberi/">Kartepe kayak rehberimizde</a>.</p>
<h3>Teleferikten kış manzarası</h3>
<p><a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a>, resmi sitesine göre her gün 11:00–19:00 arasında açıktır; bayram ve yılbaşı günlerine özel bir uygulama olup olmadığını ve rüzgâr durumunu gitmeden önce 444 6 345'ten sorun. Aralıkta güneş 17:30–17:40 civarında battığı için gün batımını kabinden izleyebilirsiniz.</p>
<h3>Kuzuluk'ta termal mola</h3>
<p>Yılbaşı gecesinin yorgunluğunu atmanın en iyi yollarından biri, 35–45 dakika uzaklıktaki <a href="/blog/kuzuluk-kaplicalari-rehberi/">Kuzuluk kaplıcalarıdır</a>. Tatil günlerinde yoğunluk olabileceği için tesisle önceden konuşun.</p>
<h3>Maşukiye ve Ormanya</h3>
<p>Serin bir öğleden sonra <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'de dere kenarında yürüyüş ya da çocuklarla <a href="/blog/ormanya-rehberi/">Ormanya</a> güzel bir seçenektir. Ormanya'nın kış saatleri daha kısadır ve bazı kaynaklara göre pazartesi günleri kapalıdır; 1–3 Ocak cuma–pazar olduğu için bu sorun yaratmaz, yine de gitmeden önce teyit edin.</p>
""" + fig("/assets/web/editorial/resepsiyon2","DİDİ Otel Sapanca resepsiyonunda bir misafiri karşılayan gülümseyen resepsiyon görevlisi","Yılbaşı gecesi için varış: giriş saatimiz 14:00.") + """
<h2>Yılbaşında İstanbul'dan Sapanca'ya ulaşım</h2>
<p>31 Aralık öğleden sonrası, İstanbul çıkışında yılın en yoğun trafik dilimlerinden biridir. Anadolu Yakası'ndan normalde 1,5–2 saat süren yol bu saatlerde çok daha uzayabilir. Üç öneri:</p>
<ul>
<li><strong>Erken çıkın:</strong> Mümkünse 31 Aralık'ta öğleden önce yola çıkın; otelde giriş saati 14:00'tür.</li>
<li><strong>Treni düşünün:</strong> Gebze'den kalkan Ada Ekspresi doğrudan Sapanca garında durur; saatler için <a href="/blog/istanbuldan-trenle-sapanca/">trenle Sapanca rehberimize</a> bakın. Tatil dönemlerinde sefer saatleri değişebilir, TCDD'den teyit edin.</li>
<li><strong>Dönüşü pazar sabahına alın:</strong> Pazar öğleden sonra dönüş trafiği yoğunlaşır.</li>
</ul>
<h2>Yılbaşı gecesi akşam yemeği</h2>
<p>Yılbaşı gecesini dışarı çıkmadan geçirmek isteyen misafirlerimiz için otel bahçesinde <a href="/#mare">Mare Gastro</a> bulunuyor. Yılbaşı gecesine özel bir menü ya da program olup olmayacağını ve rezervasyon koşullarını <a href="https://maregastro.com" target="_blank" rel="noopener">Mare Gastro</a>'dan ya da konaklama rezervasyonunuz sırasında bizden öğrenebilirsiniz. Özel bir kutlama planlıyorsanız rezervasyonda belirtmeniz halinde pasta, mum ışığı ve masa süslemesi hazırlanabilir.</p>
<h2>Yılbaşı için hangi oda?</h2>
<table><thead><tr><th>Kim geliyor?</th><th>Önerilen oda</th><th>Neden</th></tr></thead><tbody>
<tr><td>Çift</td><td><a href="/odalar/king-suit/">King Suit</a> ya da <a href="/odalar/junior-suit/">Junior Suit</a></td><td>Geniş, sakin; uzun bir kış gecesi için konforlu</td></tr>
<tr><td>Çift, ekstra keyif</td><td>Jakuzili oda</td><td>Soğuk bir günün ardından; ayrıntılar <a href="/blog/sapanca-jakuzili-havuzlu-gol-manzarali-oda/">bu yazıda</a></td></tr>
<tr><td>2 yetişkin + 2 çocuk</td><td><a href="/odalar/aile/">Aile Odası</a> (4 kişi)</td><td>Ailece tek odada</td></tr>
<tr><td>3 arkadaş</td><td><a href="/odalar/triple/">Triple Oda</a> (3 kişi)</td><td>Üç kişilik oda tipi</td></tr>
<tr><td>Çift, pratik konaklama</td><td><a href="/odalar/superior/">Superior</a></td><td>Konforlu ve pratik</td></tr>
</tbody></table>
<h2>Çocuklarla yılbaşı</h2>
<p>Çocuklu aileler için yılbaşını Sapanca'da geçirmenin en büyük avantajı gündüz programının zenginliğidir: Kartepe'de kızak, Ormanya'da Hobbit evleri, teleferik ve göl kıyısında yürüyüş. Akşam planında ise bir noktaya dikkat edin: otel bahçesindeki Mare Gastro'ya <strong>saat 15:00'ten sonra çocuk kabul edilmez</strong>. Çocuklarla akşam yemeğini erken saatte ya da başka bir mekânda planlamak gerekir. Dört kişilik <a href="/odalar/aile/">Aile Odası</a>, kalabalık bir yılbaşı gecesini aynı odada geçirmek isteyen aileler için en rahat seçenektir.</p>
<h2>Yılbaşı gecesi için zaman çizelgesi</h2>
<table><thead><tr><th>Saat</th><th>31 Aralık</th><th>1 Ocak</th></tr></thead><tbody>
<tr><td>Sabah</td><td>İstanbul'dan erken çıkış</td><td>08:23'te gün doğumu (isteyene)</td></tr>
<tr><td>Öğle</td><td>Yolda ya da Maşukiye'de öğle yemeği</td><td>Geç kahvaltı</td></tr>
<tr><td>14:00</td><td>Otele giriş</td><td>Teleferik ya da Kuzuluk</td></tr>
<tr><td>17:41</td><td>Göl kıyısında yılın son gün batımı</td><td>Sahil yürüyüşü</td></tr>
<tr><td>Akşam</td><td>Yılbaşı yemeği (Mare Gastro 00:00'da kapanır, son sipariş 23:00)</td><td>Sakin bir akşam</td></tr>
</tbody></table>
<h2>Yılbaşı rezervasyon kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="yilbasi">
<label><input type="checkbox"><span><b>Tarihleri netleştirin</b><span>Perşembe–cuma, perşembe–cumartesi ya da perşembe–pazar.</span></span></label>
<label><input type="checkbox"><span><b>Yılbaşı koşullarını sorun</b><span>Minimum gece, iptal ve ön ödeme koşulları dönemsel olabilir.</span></span></label>
<label><input type="checkbox"><span><b>Akşam yemeği planı</b><span>Mare Gastro'nun yılbaşı programını önceden öğrenin.</span></span></label>
<label><input type="checkbox"><span><b>Yol planı</b><span>31 Aralık'ta erken çıkış ya da tren.</span></span></label>
<label><input type="checkbox"><span><b>Kış çantası</b><span>Su geçirmez mont, kaymayan ayakkabı, mayo (termal için).</span></span></label>
<label><input type="checkbox"><span><b>Kartepe'ye çıkacaksanız</b><span>Kış lastiği ve zincir.</span></span></label>
</div>
<h2>Sapanca'da yılbaşı için nerede kalınır?</h2>
<p>Yılbaşında konum çok önemlidir: gece dışarıda yol yapmak istemezsiniz. Kırkpınar'daki <a href="/#konum">DİDİ Otel Sapanca</a>, otoyol gişelerine yaklaşık 500 metre, teleferiğe kısa mesafede ve Mare Gastro aynı bahçede olduğu için yılbaşı gecesini tek bir yerde rahatça geçirmenizi sağlar. Kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur); yılın ilk sabahı acele etmeden kahvaltı yapabilirsiniz. Yılbaşı dönemi müsaitliği hızlı dolduğu için tarihleri netleştirir netleştirmez <a href="https://wa.me/905331350888?text=Merhaba%2C%20y%C4%B1lba%C5%9F%C4%B1%20(31%20Aral%C4%B1k%202026)%20i%C3%A7in%20m%C3%BCsaitlik%20ve%20ko%C5%9Fullar%C4%B1%20sormak%20istiyorum.">WhatsApp'tan</a> ya da 0264 592 12 12'den bize ulaşın; o dönemin koşullarını ve fiyatlarını size doğrudan iletelim.</p>
""",
 "sources":[("Adapazarı iklim verileri 1991–2020, MGM kaynaklı (Wikipedia)","https://en.wikipedia.org/wiki/Adapazar%C4%B1"),
            ("Sapanca Teleferik — çalışma saatleri ve iletişim (resmi site)","https://sapancateleferik.com.tr/"),
            ("Gebze–Adapazarı bölgesel tren saatleri (e-Yaşam Rehberi)","https://e-yasamrehberi.com/tren-saatleri/bolgesel-trenler/gebze-adapazari-tren-saatleri.html"),
            ("Gün doğumu ve batımı: NOAA güneş konumu hesabı (Sapanca koordinatları)","https://gml.noaa.gov/grad/solcalc/")],
 "faq":[("2027 yılbaşı hangi güne denk geliyor?","31 Aralık 2026 perşembe, 1 Ocak 2027 cuma günüdür. Perşembe akşamından pazar akşamına kadar dört günlük bir pencere oluşur."),
        ("Sapanca'da yılbaşında kar olur mu?","Göl kıyısında zaman zaman kar yağar ama garanti değildir; aralıkta ortalama en düşük sıcaklık 5,3 °C'dir. Karlı manzara için 25–30 dakika uzaklıktaki Kartepe'ye çıkmak gerekir."),
        ("Yılbaşında Sapanca'da ne yapılır?","Göl kıyısında yılın ilk gün doğumu (1 Ocak'ta ~08:23), Kartepe'de kar ve kayak, teleferikten kış manzarası, Kuzuluk'ta termal mola ve Maşukiye ya da Ormanya'da yürüyüş öne çıkar."),
        ("Yılbaşı rezervasyonu ne zaman yapılmalı?","Yılbaşı dönemi Sapanca'da en yoğun dönemlerden biridir; tarihleri netleştirir netleştirmez rezervasyon yapmanız ve minimum gece gibi dönemsel koşulları sormanız önerilir."),
        ("Yılbaşı gecesi otelde yemek var mı?","DİDİ Otel'in bahçesinde Mare Gastro restoranı bulunur. Yılbaşı gecesine özel menü veya program olup olmadığını rezervasyon sırasında sormanız gerekir."),
        ("31 Aralık'ta İstanbul'dan Sapanca'ya ne kadar sürede gidilir?","Normalde 1,5–2 saat süren yol, 31 Aralık öğleden sonra trafik nedeniyle belirgin şekilde uzayabilir. Öğleden önce çıkmak ya da Ada Ekspresi ile trenle gelmek önerilir.")],
},
{
 "slug":"sapancada-sonbahar-rehberi","cat":"Mevsimler","img":"ONN09451","date":"2026-11-16",
 "title":"Sapanca'da Sonbahar: Ekim–Kasım Gezi Rehberi ve Renk Rotası",
 "seo_title":"Sapanca'da Sonbahar: Ekim–Kasım Gezi Rehberi",
 "img_alt":"DİDİ Otel Sapanca bahçesinde palmiyeler ve çiçekli çalılar arasından uzanan taş yol",
 "desc":"Sapanca'da sonbahar: ekim–kasım hava durumu, yağışlı gün sayısı, renkli orman rotaları (Maşukiye, Kartepe, Ormanya), gün batımı saatleri ve 2 günlük plan.",
 "related":["sapanca-hangi-mevsim-gidilir","kuzuluk-kaplicalari-rehberi","sapancada-yagmurlu-havada-ne-yapilir"],
 "lead":"Sapanca'da sonbahar, yaz kalabalığının çekildiği ve ormanların sararıp kızardığı sakin bir dönemdir. Adapazarı'nın 1991–2020 iklim normallerine göre kasımda gündüz ortalama en yüksek sıcaklık <strong>17 °C</strong>, gece ortalama en düşük <strong>8 °C</strong> civarındadır ve ayın yaklaşık 12 günü yağışlı geçer. Renkler için en iyi pencere ekim sonu ile kasım ortasıdır; en güzel rotalar Maşukiye vadisi, Kartepe'ye çıkan orman yolu, Ormanya ve teleferikten görülen göl kıyısıdır. Kasımda güneş 17:40 civarında battığı için günü erken başlatmak, akşamı ise sıcak bir sofrada ya da termal bir molada bitirmek gerekir.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Ne zaman:</strong> Renkler için ekim sonu – kasım ortası; eylül hâlâ yaz gibidir.</li>
<li><strong>Hava:</strong> Kasım ort. 8–17 °C, ~12 yağışlı gün; yanınıza su geçirmez bir mont alın.</li>
<li><strong>Rota:</strong> Maşukiye, Kartepe yolu ve Kuzuyayla, Ormanya, teleferik, Kırkpınar sahili.</li>
<li><strong>Akşam:</strong> Gün batımı ~17:40; Kuzuluk'ta termal ya da otelde uzun bir akşam yemeği.</li>
</ul></div>
<h2>Sapanca'da sonbaharda hava nasıl?</h2>
<p>Sonbaharın üç ayı birbirinden oldukça farklıdır. Eylül hâlâ yazın devamı gibidir; ekim serinler ve yağışlar başlar; kasım ise serin, nemli ve kısa günlerin ayıdır. Aşağıdaki tablo, Türkiye Meteoroloji Genel Müdürlüğü kaynaklı 1991–2020 Adapazarı normallerinden derlenmiştir; Sapanca, Adapazarı'na yaklaşık 15 km uzaklıkta ve benzer iklime sahiptir.</p>
<table><thead><tr><th>Ay</th><th>Ort. en yüksek</th><th>Ort. en düşük</th><th>Yağış</th><th>Yağışlı gün</th><th>Gün batımı (ayın 15'i)</th></tr></thead><tbody>
<tr><td>Eylül</td><td>27,2 °C</td><td>15,7 °C</td><td>53 mm</td><td>~8</td><td>19:10</td></tr>
<tr><td>Ekim</td><td>22,3 °C</td><td>12,3 °C</td><td>85 mm</td><td>~12</td><td>18:20</td></tr>
<tr><td>Kasım</td><td>17,2 °C</td><td>8,0 °C</td><td>73 mm</td><td>~12</td><td>17:42</td></tr>
</tbody></table>
<p>Bu tablodan çıkan pratik sonuç şu: kasımda her iki günden birinde yağmur ihtimali var ama yağışlar genellikle gün boyu sürmez. Sabah sisli, öğle saatleri ılık, akşamlar serin geçer. Bu yüzden planı esnek tutmak ve bir yağmur B planı hazırlamak iyi olur; fikirler için <a href="/blog/sapancada-yagmurlu-havada-ne-yapilir/">Sapanca'da yağmurlu havada ne yapılır</a> yazımıza bakabilirsiniz.</p>
<h2>Sonbahar renkleri ne zaman başlar?</h2>
<p>Sapanca çevresindeki karışık ormanlarda (kayın, meşe, kestane, gürgen) renk değişimi genellikle ekimin ikinci yarısında başlar, kasımın ilk yarısında en canlı tonlarına ulaşır. Kesin tarih her yıl hava koşullarına göre değişir: sıcak geçen bir ekimde renkler gecikir, erken gelen bir soğuk dalgası süreci hızlandırır. Yüksek kesimler (Kartepe, Kuzuyayla) göl kıyısından önce renklenir; yani kasım ortasında kıyıda hâlâ yeşillik görürken dağ yolunda yapraklar dökülmeye başlamış olabilir.</p>
<h2>Sonbaharda Sapanca'da gezilecek yerler</h2>
<table><thead><tr><th>Yer</th><th>Kırkpınar'dan</th><th>Sonbaharda neden?</th></tr></thead><tbody>
<tr><td>Maşukiye vadisi</td><td>10–15 dk</td><td>Dere boyunca renkli ağaçlar, sisli sabahlar</td></tr>
<tr><td>Kartepe yolu ve Kuzuyayla</td><td>25–30 dk</td><td>Yükseklik arttıkça renk ve manzara değişir</td></tr>
<tr><td>Ormanya</td><td>~15 dk</td><td>Orman içi yürüyüş parkurları, çocuklu aileler için ideal</td></tr>
<tr><td>Sapanca Teleferik</td><td>Aynı mahalle</td><td>Renkli yamaçların üzerinden süzülmek; kasımda gün batımı kapanıştan önce</td></tr>
<tr><td>Kırkpınar ve merkez sahil</td><td>5–10 dk</td><td>Sakin göl, puslu ışık, boş banklar</td></tr>
<tr><td>Poyrazlar Gölü</td><td>30–35 dk</td><td>Orman içinde küçük göl, sessizlik</td></tr>
<tr><td>Kuzuluk kaplıcaları</td><td>35–45 dk</td><td>Serin havada termal mola</td></tr>
</tbody></table>
<h3>Maşukiye: sisli dere boyu</h3>
<p>Sonbaharın en fotojenik sabahları <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'de yaşanır: dere üzerindeki sis, sararan ağaçlar ve öğlene doğru açan güneş. Yağmur sonrası günlerde şelalelerin suyu da artar. Öğle yemeğini dere kenarında alabalıkla yapıp yolu Kartepe'ye doğru uzatabilirsiniz.</p>
<h3>Kartepe yolu ve Kuzuyayla</h3>
<p>Maşukiye'den Kartepe'ye tırmanan yol, sonbaharın en renkli güzergâhlarından biridir. Kuzuyayla Tabiat Parkı'nda kısa bir yürüyüş için kalın bir katman ve su geçirmez ayakkabı alın; yükseklerde hava aşağıya göre belirgin şekilde daha serindir. Kasımın sonuna doğru zirvede ilk kar görülebilir; kayak sezonu için <a href="/blog/kartepe-kayak-merkezi-rehberi/">Kartepe kayak rehberimize</a> bakın.</p>
<h3>Ormanya: aileler için orman yürüyüşü</h3>
<p>Kartepe'nin Uzuntarla Mahallesi'ndeki <a href="/blog/ormanya-rehberi/">Ormanya</a>, sonbaharda serin ve sakin bir yürüyüş sunar. Hobbit evleri ve hayvan gözlem alanları çocuklar için ilgi çekicidir. Kış saatlerine geçişte kapanış saati öne çekildiği için öğleden önce gitmek iyi fikirdir.</p>
<h3>Teleferikle renklerin üzerinden</h3>
<p><a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a> her gün 11:00–19:00 arasında çalışıyor. Kasımda güneş 17:40 civarında battığı için, teleferiğin kapanışından önce gün batımını yukarıdan izlemek mümkün; yaz aylarında bu fırsat yoktur. Rüzgârlı günlerde seferlerin durabileceğini unutmayın.</p>
""" + fig("/assets/web/editorial/ONN09442","DİDİ Otel Sapanca bahçesinde beyaz minderli cabana sırası ve tavanda hasır lambalar","Serin bir sonbahar öğleden sonrası için bahçedeki cabanalar.") + """
<h2>Sonbaharda Sapanca'da ne yenir?</h2>
<p>Sonbahar, Sakarya'nın tescilli lezzeti <strong>Adapazarı kabak tatlısı</strong>nın mevsimidir; bölgede kabağın hasadıyla birlikte tatlıcı vitrinleri dolar. Serin havada sıcak bir ıslama köfte ya da Maşukiye'de dere kenarında alabalık da bu mevsime çok yakışır. Ayrıntılar <a href="/blog/sapancada-ne-yenir/">Sapanca'da ne yenir</a> rehberimizde.</p>
<h2>2 günlük sonbahar planı</h2>
<table><thead><tr><th>Saat</th><th>1. gün</th><th>2. gün</th></tr></thead><tbody>
<tr><td>08:30</td><td>Kahvaltı</td><td>Kahvaltı, kısa sahil yürüyüşü</td></tr>
<tr><td>10:00</td><td>Maşukiye'de sisli dere yürüyüşü</td><td>Ormanya (öğleden önce)</td></tr>
<tr><td>13:00</td><td>Dere kenarında alabalık</td><td>Sapanca çarşısında ıslama köfte</td></tr>
<tr><td>14:30</td><td>Kartepe yolu ve Kuzuyayla</td><td>Kuzuluk'ta termal mola ya da teleferik</td></tr>
<tr><td>17:00</td><td>Teleferik ya da kıyıda gün batımı (~17:40)</td><td>Dönüş yolu</td></tr>
<tr><td>19:30</td><td>Bahçede akşam yemeği</td><td>—</td></tr>
</tbody></table>
<h2>Sonbaharda fotoğraf için en iyi saatler</h2>
<p>Sonbahar ışığı, Sapanca'yı fotoğraflamak için yılın en cömert dönemidir. Ekim ortasında güneş 07:10, kasım ortasında 07:46 civarında doğar; bu saatlerde göl üzerinde sık sık sis oluşur ve Kırkpınar sahilinden bakınca karşı kıyı sisin içinden yavaş yavaş belirir. Öğleden sonra ise güneş alçaldıkça renkli yamaçlar sıcak bir ışıkla aydınlanır. Gün batımı ekimde 18:20, kasımda 17:40 civarındadır; altın saat bundan yaklaşık 45 dakika önce başlar. Yağmur sonrası günler, bulutların arasından sızan ışık ve gürleşen derelerle en dramatik kareleri verir. Hangi noktadan çekeceğinizi <a href="/blog/sapancada-fotograf-gun-batimi-noktalari/">fotoğraf ve gün batımı noktaları</a> rehberimizde bulabilirsiniz.</p>
<h2>Hafta içi sonbahar kaçamağı</h2>
<p>Sonbaharda Sapanca'yı en sakin haliyle görmek isteyenler için hafta içi bir ya da iki gece eşsizdir: Maşukiye'nin dere kenarındaki tesisler, teleferik ve Ormanya hafta sonuna göre çok daha tenhadır, otoyolda da cuma akşamı yoğunluğu yaşanmaz. Uzaktan çalışabiliyorsanız, sabahı göl kıyısında yürüyüşle başlatıp öğleden sonrayı odanızda çalışarak geçirmek ve akşamüstü gün batımına çıkmak, kısa ama dolu bir mola olur. Otelin tamamında ücretsiz Wi-Fi bulunur.</p>
<h2>Sonbahar çantası: yanınıza ne almalı?</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="sonbahar">
<label><input type="checkbox"><span><b>Su geçirmez mont</b><span>Kasımda yaklaşık her iki günden biri yağışlı.</span></span></label>
<label><input type="checkbox"><span><b>Kat kat giyim</b><span>Sabah 8 °C, öğlen 17 °C olabilir.</span></span></label>
<label><input type="checkbox"><span><b>Tabanı kaymayan ayakkabı</b><span>Islak yapraklı patikalar kaygan olur.</span></span></label>
<label><input type="checkbox"><span><b>Mayo</b><span>Kuzuluk'ta termal mola için.</span></span></label>
<label><input type="checkbox"><span><b>Kamera ve yedek batarya</b><span>Sisli sabahlar ve renkli yamaçlar için.</span></span></label>
<label><input type="checkbox"><span><b>Erken başlangıç</b><span>Gün ışığı 17:40 civarında bitiyor.</span></span></label>
</div>
<h2>Sonbaharda Sapanca'da konaklama</h2>
<p>Sonbahar, Sapanca'da yaz sezonuna göre daha sakin bir dönemdir; hafta içi kaçamaklar için özellikle uygundur. Açık havuzlar mevsim dışında olabileceğinden bu dönemde odanın konforu, kahvaltı ve akşam yemeği öne çıkar. Kırkpınar'daki <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur); serin akşamlarda dışarı çıkmak istemezseniz bahçedeki <a href="/#mare">Mare Gastro</a> hemen yanınızdadır. Çiftler için <a href="/blog/sapanca-jakuzili-havuzlu-gol-manzarali-oda/">jakuzili oda seçenekleri</a>, aileler için <a href="/odalar/aile/">Aile Odası</a> sonbahar kaçamağını daha keyifli kılar. Havuzun sezon durumu ve müsaitlik için <a href="https://wa.me/905331350888?text=Merhaba%2C%20sonbaharda%20Sapanca%27da%20konaklama%20i%C3%A7in%20m%C3%BCsaitlik%20sormak%20istiyorum.">WhatsApp'tan</a> bize yazın.</p>
<p>Diğer mevsimleri karşılaştırmak isterseniz <a href="/blog/sapanca-hangi-mevsim-gidilir/">Sapanca'ya hangi mevsimde gidilir</a>, kışı planlıyorsanız <a href="/blog/sapancada-kisin-gezilecek-yerler/">kışın gezilecek yerler</a> yazımıza göz atın.</p>
""",
 "sources":[("Adapazarı iklim verileri 1991–2020, MGM kaynaklı (Wikipedia)","https://en.wikipedia.org/wiki/Adapazar%C4%B1"),
            ("Sapanca Teleferik — çalışma saatleri (resmi site)","https://sapancateleferik.com.tr/"),
            ("Sakarya'nın kabak tatlısı ve Abhaz peyniri coğrafi işaret aldı (CNN Türk, 29.04.2021)","https://www.cnnturk.com/yasam/sakaryanin-kabak-tatlisi-ve-abhaz-peyniri-cografi-isaret-aldi-1649231"),
            ("Gün batımı saatleri: NOAA güneş konumu hesabı (Sapanca koordinatları)","https://gml.noaa.gov/grad/solcalc/"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("Sapanca'ya sonbaharda gidilir mi?","Evet. Sonbahar, yaz kalabalığının çekildiği, ormanların renklendiği sakin bir dönemdir. Renkler için en iyi pencere genellikle ekim sonu ile kasım ortasıdır."),
        ("Kasımda Sapanca'da hava nasıl?","1991–2020 Adapazarı normallerine göre kasımda ortalama en yüksek sıcaklık 17,2 °C, en düşük 8,0 °C'dir; ay boyunca yaklaşık 12 gün yağışlı geçer."),
        ("Sonbaharda Sapanca'da nereler gezilir?","Maşukiye vadisi, Kartepe yolu ve Kuzuyayla, Ormanya, Sapanca Teleferik, Kırkpınar sahili, Poyrazlar Gölü ve termal mola için Kuzuluk öne çıkar."),
        ("Sapanca'da sonbahar renkleri ne zaman görülür?","Genellikle ekimin ikinci yarısında başlar, kasımın ilk yarısında en canlı halini alır. Yüksek kesimler göl kıyısından önce renklenir; tarih her yıl havaya göre değişir."),
        ("Kasımda gün batımı saat kaçta?","Sapanca'da kasım ortasında güneş yaklaşık 17:40'ta batar; teleferik 19:00'a kadar açık olduğu için gün batımını yukarıdan izlemek mümkündür."),
        ("Sonbaharda havuz açık mı?","Açık havuzlar genellikle yaz sezonunda hizmet verir. DİDİ Otel'deki havuzun güncel sezon durumu için WhatsApp'tan bize sorabilirsiniz.")],
},
{
 "slug":"sapancada-toplanti-ve-sirket-etkinligi","cat":"Kurumsal","img":"toplanti-salonu","date":"2026-11-16",
 "title":"Sapanca'da Toplantı ve Şirket Kaçamağı: İstanbul'a Yakın Ekip Buluşması Rehberi",
 "seo_title":"Sapanca'da Toplantı ve Şirket Kaçamağı Rehberi",
 "img_alt":"DİDİ Otel Sapanca toplantı salonunda U düzeninde ahşap masa, siyah sandalyeler ve duvarda ekran",
 "desc":"Sapanca'da şirket toplantısı ve ekip kaçamağı: İstanbul'a 1,5–2 saat, trenle ulaşım, toplantı salonu, takım aktiviteleri ve planlama listesi.",
 "related":["sapancaya-nasil-gidilir","istanbuldan-trenle-sapanca","sapancada-gezilecek-yerler"],
 "lead":"Sapanca, İstanbul'dan 1,5–2 saatlik mesafesi, tren bağlantısı ve göl–orman ortamıyla bir-iki günlük şirket toplantıları ve ekip kaçamakları için en pratik adreslerden biridir. Sabahı toplantı salonunda verimli bir oturumla, öğleden sonrayı teleferik, göl kıyısı yürüyüşü ya da Maşukiye'de bir öğle yemeğiyle geçirmek, ekibe hem iş hem nefes alanı sağlar. DİDİ Otel Sapanca'da göl ile orman arasında, gün ışığı alan bir toplantı salonu bulunur; kapasite, oturma düzeni ve teknik ihtiyaçlarınızı bize yazarsanız size uygun planı birlikte çıkarırız.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Neden Sapanca:</strong> İstanbul'a 1,5–2 saat; Ada Ekspresi ve YHT+Arifiye ile araçsız ulaşım.</li>
<li><strong>Mekân:</strong> Gün ışığı alan toplantı salonu, ücretsiz Wi-Fi ve otopark, bahçede Mare Gastro.</li>
<li><strong>Aktivite:</strong> Teleferik (grup fiyatı için işletmeye yazın), göl kıyısı yürüyüşü, Maşukiye, SUP.</li>
<li><strong>Planlama:</strong> Kişi sayısı, oturma düzeni, ekipman ve yemek saatlerini önceden netleştirin.</li>
</ul></div>
<h2>Şirket toplantısı için neden Sapanca?</h2>
<p>Ekip dışarıda toplanacaksa iki şey kritik: herkesin kolayca gelebilmesi ve ortamın gerçekten "şehirden çıkmış" hissettirmesi. Sapanca ikisini birden sağlar. Anadolu Yakası'ndan yaklaşık 125–135 km'lik yol, sabah 08:00'de yola çıkan bir ekibin 10:00'da toplantıya oturmasını mümkün kılar. Araçsız gelecek çalışanlar için de seçenek var: Gebze'den kalkan Ada Ekspresi doğrudan Sapanca garında durur, YHT ise Arifiye'de iner. Ayrıntılar <a href="/blog/istanbuldan-trenle-sapanca/">trenle Sapanca rehberimizde</a>.</p>
<table><thead><tr><th>Ölçüt</th><th>Sapanca</th><th>Not</th></tr></thead><tbody>
<tr><td>İstanbul'a mesafe</td><td>~125–135 km, 1,5–2 saat</td><td>Cuma akşamı trafiği hesaba katılmalı</td></tr>
<tr><td>Toplu taşıma</td><td>Ada Ekspresi (Gebze–Sapanca ~1 sa 5 dk), YHT + Arifiye</td><td>Saatler TCDD'den teyit edilmeli</td></tr>
<tr><td>Havalimanı</td><td>Sabiha Gökçen ~95–110 km</td><td>Şehir dışından gelen katılımcılar için</td></tr>
<tr><td>Otel–otoyol</td><td>Sapanca gişelerine ~500 m</td><td>Ücretsiz otopark</td></tr>
<tr><td>Aktivite çeşitliliği</td><td>Göl, teleferik, orman, şelale</td><td>15–30 dk içinde</td></tr>
</tbody></table>
<h2>DİDİ Otel'de toplantı salonu nasıl?</h2>
<p>Otelimizin toplantı salonu, geniş pencereleriyle gün ışığı alan, bahçe ve dağ manzaralı bir mekândır. Fotoğraflarda görüldüğü gibi U düzeninde kurulabilen ahşap masalar, duvara monte ekran ve salonun bir köşesinde oturma grubu bulunur. Ücretsiz Wi-Fi tüm otelde hizmet verir.</p>
""" + fig("/assets/web/gallery/02","Toplantı salonunda pencere kenarında koyu masa ve sandalyeler, camın ardında yeşillik ve dağ manzarası","Toplantı arasında göz dinlendiren manzara: salonun pencerelerinden Samanlı Dağları.") + """
<p>Salonun kaç kişiyi hangi düzende ağırlayabileceği, projeksiyon, ses sistemi, flipchart gibi ekipman ihtiyaçları ve kahve arası seçenekleri etkinliğin yapısına göre değişir. Bu yüzden burada sabit bir kapasite vermiyoruz; kişi sayınızı ve programınızı <a href="https://wa.me/905331350888?text=Merhaba%2C%20DİDİ%20Otel%27de%20şirket%20toplantısı%20planlıyoruz%2C%20salon%20ve%20konaklama%20hakkında%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> ya da <a href="mailto:info@sapancadidiotel.com">info@sapancadidiotel.com</a> adresinden iletin, size net bir teklifle dönelim.</p>
<h2>Bir günlük ve iki günlük örnek program</h2>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="bir">Tek gün</button><button data-tab="iki">İki gün / bir gece</button></div>
<div class="itin-panel on" data-tab="bir"><p><strong>08:00</strong> İstanbul'dan hareket · <strong>10:00</strong> karşılama kahvesi · <strong>10:30–13:00</strong> toplantı · <strong>13:00</strong> öğle yemeği · <strong>14:30–16:00</strong> göl kıyısında yürüyüş ya da teleferik · <strong>16:30</strong> kısa kapanış oturumu · <strong>17:30</strong> dönüş.</p></div>
<div class="itin-panel" data-tab="iki"><p><strong>1. gün:</strong> öğleden önce varış, giriş (14:00), öğleden sonra toplantı, akşam bahçede ekip yemeği. <strong>2. gün:</strong> kahvaltı, sabah atölye oturumu, öğle yemeği Maşukiye'de, öğleden sonra teleferik ya da Ormanya, çıkış (12:00) sonrası ekip aktivitesi ve dönüş.</p></div>
</div>
<h2>Ekip aktivitesi için Sapanca'da ne yapılır?</h2>
<table><thead><tr><th>Aktivite</th><th>Süre</th><th>Kalabalık grup için not</th></tr></thead><tbody>
<tr><td><a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik</a></td><td>1,5–2 saat</td><td>Kabinler 8 kişilik; grup fiyatı için işletmeye önceden yazın</td></tr>
<tr><td>Zipline ve ATV</td><td>1–2 saat</td><td>Teleferik üst istasyonunda; yaş ve sağlık koşullarını sorun</td></tr>
<tr><td>Göl kıyısı yürüyüşü</td><td>1 saat</td><td>Ücretsiz, herkes katılabilir</td></tr>
<tr><td><a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'de öğle yemeği</td><td>2 saat</td><td>Hafta sonu kalabalık; rezervasyon önerilir</td></tr>
<tr><td>SUP tanışma</td><td>1–2 saat</td><td>Can yeleği şart; rüzgârsız sabahları tercih edin</td></tr>
<tr><td><a href="/blog/ormanya-rehberi/">Ormanya</a></td><td>2–3 saat</td><td>Doğa yürüyüşü; bazı kaynaklara göre pazartesi kapalı</td></tr>
</tbody></table>
<p>Hareketli aktivitelerin ayrıntıları için <a href="/blog/sapanca-macera-parki-zipline/">zipline ve ATV rehberimize</a>, göl üzerindeki seçenekler için <a href="/blog/sapanca-golu-aktiviteler/">Sapanca Gölü aktiviteleri</a> yazımıza bakın.</p>
<h2>Ekip yemeği ve konaklama</h2>
<p>Toplantının ardından ekibi bir araya getiren şey çoğu zaman akşam yemeğidir. Otel bahçesindeki <a href="/#mare">Mare Gastro</a>, ekip yemekleri için dışarı çıkmadan ulaşılan bir seçenektir; restoran 00:00'da kapanır, son sipariş 23:00'tedir. Grup menüsü ve masa düzeni için ayrıntıları önceden konuşalım. Konaklayan katılımcılar için kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur).</p>
<p>Oda dağılımında <a href="/odalar/superior/">Superior</a> ve <a href="/odalar/junior-suit/">Junior Suit</a> tek ya da çift kişilik konaklamalar için, <a href="/odalar/triple/">Triple</a> üç kişilik paylaşımlar için uygundur. Yöneticiler ya da konuşmacılar için <a href="/odalar/king-suit/">King Suit</a> düşünülebilir. Tüm oda tipleri <a href="/odalar/">odalar sayfamızda</a>.</p>
<h2>Toplantı için hangi mevsim daha uygun?</h2>
<p>Sapanca'da toplantı her mevsim yapılabilir; ancak programın açık hava kısmı mevsime göre değişir. İlkbahar ve sonbahar, ılık hava ve sakin bölge sayesinde açık hava aktiviteleri için en verimli dönemlerdir. Yazın öğle sıcağını salonda geçirip akşamüstünü göl kıyısında değerlendirmek iyi bir dengedir; hafta sonları bölge kalabalık olduğundan hafta içi tarihler daha rahattır. Kış aylarında yağışlı gün sayısı artar; programa kapalı alanda yapılabilecek bir atölye ve bir yağmur planı eklemek gerekir. Yılbaşı, bayramlar ve okul tatilleri bölgenin en yoğun dönemleri olduğundan kurumsal etkinlikler için genellikle bu tarihlerin dışı tercih edilir.</p>
<h2>Hibrit katılım ve dijital ihtiyaçlar</h2>
<p>Katılımcıların bir kısmı uzaktan bağlanacaksa ekran, kamera ve ses düzenini önceden konuşmak önemlidir. Otelin tamamında ücretsiz Wi-Fi bulunur; görüntülü görüşme yapılacak oturumların saatlerini ve gerekli ekipmanı bize önceden iletirseniz salon düzenini buna göre birlikte planlayalım. Yedek olarak bir mobil internet bağlantısı bulundurmak, kritik sunumlarda her zaman iyi bir önlemdir.</p>
<h2>Toplantı planlama kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/8</b></div>
<div class="spot-check" data-key="toplanti">
<label><input type="checkbox"><span><b>Kişi sayısı ve tarih</b><span>Kesinleşmiş katılımcı sayısını iletin.</span></span></label>
<label><input type="checkbox"><span><b>Oturma düzeni</b><span>U düzeni, sınıf ya da toplantı masası.</span></span></label>
<label><input type="checkbox"><span><b>Teknik ihtiyaçlar</b><span>Ekran, ses, mikrofon, flipchart.</span></span></label>
<label><input type="checkbox"><span><b>Kahve araları ve yemekler</b><span>Saatleri programa göre netleştirin.</span></span></label>
<label><input type="checkbox"><span><b>Ulaşım</b><span>Ortak servis mi, tren mi, bireysel araç mı?</span></span></label>
<label><input type="checkbox"><span><b>Oda dağılımı</b><span>Tek/çift/üç kişilik paylaşımlar.</span></span></label>
<label><input type="checkbox"><span><b>Aktivite rezervasyonları</b><span>Teleferik grubu, öğle yemeği yeri.</span></span></label>
<label><input type="checkbox"><span><b>Yağmur planı</b><span>Kasım–ocak arası her iki günden biri yağışlı olabilir.</span></span></label>
</div>
<h2>Teklif almak için</h2>
<p>Sapanca'da bir toplantı, eğitim ya da ekip kaçamağı planlıyorsanız tarih, kişi sayısı ve program taslağınızla bize ulaşın: <a href="tel:+902645921212">0264 592 12 12</a>, <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%27da%20şirket%20toplantısı%20için%20teklif%20almak%20istiyoruz.">WhatsApp</a> ya da <a href="mailto:info@sapancadidiotel.com">info@sapancadidiotel.com</a>. Konumumuz ve ulaşım seçenekleri için <a href="/blog/sapancaya-nasil-gidilir/">Sapanca'ya nasıl gidilir</a> rehberimize bakabilirsiniz.</p>
""",
 "sources":[("Gebze–Adapazarı bölgesel tren saatleri (e-Yaşam Rehberi)","https://e-yasamrehberi.com/tren-saatleri/bolgesel-trenler/gebze-adapazari-tren-saatleri.html"),
            ("Sapanca Teleferik — fiyat tarifesi ve grup bilgisi (resmi site)","https://sapancateleferik.com.tr/fiyat-tarifesi"),
            ("Leitner — GD8 Sapanca (kabin kapasitesi)","https://www.leitner.com/en/company/references/detail/gd8-sapanca/"),
            ("Mesafe ve süre tahminleri: OpenStreetMap / OSRM rotalama","https://www.openstreetmap.org/")],
 "faq":[("Sapanca şirket toplantısı için uygun mu?","Evet. İstanbul'a 1,5–2 saat mesafede olması, tren bağlantısı ve göl–orman ortamı sayesinde bir-iki günlük toplantı ve ekip kaçamakları için pratik bir seçenektir."),
        ("DİDİ Otel'de toplantı salonu var mı?","Evet. Gün ışığı alan, bahçe ve dağ manzaralı bir toplantı salonumuz bulunur; kapasite ve oturma düzeni etkinliğe göre planlanır, ayrıntılar için bizimle iletişime geçin."),
        ("Toplantı katılımcıları Sapanca'ya trenle gelebilir mi?","Evet. Gebze'den kalkan Ada Ekspresi Sapanca garında durur (Gebze–Sapanca ~1 saat 5 dakika); YHT ile gelenler Arifiye'de inip taksiyle yaklaşık 15 dakikada Kırkpınar'a ulaşır."),
        ("Ekip aktivitesi olarak ne yapılabilir?","Teleferik, üst istasyonda zipline ve ATV, göl kıyısı yürüyüşü, Maşukiye'de öğle yemeği, SUP tanışma ve Ormanya gibi seçenekler 15–30 dakika içindedir."),
        ("Toplantı teklifi nasıl alınır?","Tarih, kişi sayısı ve program taslağınızı 0264 592 12 12, WhatsApp (0533 135 08 88) ya da info@sapancadidiotel.com üzerinden iletin.")],
},
{
 "slug":"sapancada-yagmurlu-havada-ne-yapilir","cat":"Mevsimler","img":"ONN09442","date":"2026-11-16",
 "title":"Sapanca'da Yağmurlu Havada Ne Yapılır? 8 Kapalı ve Yarı Kapalı Fikir",
 "seo_title":"Sapanca'da Yağmurlu Havada Ne Yapılır? 8 Fikir",
 "img_alt":"DİDİ Otel Sapanca bahçesinde üstü kapalı, beyaz minderli cabana sırası ve hasır lambalar",
 "desc":"Sapanca'da yağmur yağarsa ne yapılır? Kuzuluk'ta termal, gür Maşukiye şelaleleri, Taraklı, ıslama köfte turu ve otelde dinlenme. Aylara göre yağış tablosu.",
 "related":["kuzuluk-kaplicalari-rehberi","sapancada-sonbahar-rehberi","tarakli-geyve-gunubirlik-tur"],
 "lead":"Sapanca'da yağmurlu bir günde en iyi seçenekler, 35–45 dakika uzaklıktaki Kuzuluk'ta termal havuzlar, yağmur sonrası gürleşen Maşukiye şelalelerine kısa bir yürüyüş, Taraklı'nın tarihi konakları, Sapanca ve Adapazarı'nda ıslama köfte turu ve otelde uzun bir kahvaltının ardından odada dinlenmektir. Adapazarı'nın iklim normallerine göre aralık ve ocakta ayın yaklaşık yarısı yağışlıdır; ama yağışlı bir gün her zaman sabahtan akşama yağmur demek değildir. Bu yüzden iyi bir B planı, Sapanca hafta sonunu kurtarmaya yeter.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Kapalı:</strong> Kuzuluk termal, uzun kahvaltı, jakuzili oda, lezzet turu.</li>
<li><strong>Yarı kapalı:</strong> Taraklı konakları ve çarşısı, kapalı cabanalarda çay.</li>
<li><strong>Yağmur dinince:</strong> Maşukiye şelaleleri, sisli göl kıyısı fotoğrafları.</li>
<li><strong>Kaçının:</strong> Rüzgârlı havada teleferik ve göl aktiviteleri; çamurlu orman patikaları.</li>
</ul></div>
<h2>Sapanca'da hangi aylar daha yağışlı?</h2>
<p>Yağmur ihtimalini bilmek, planı baştan doğru kurmanızı sağlar. Türkiye Meteoroloji Genel Müdürlüğü kaynaklı 1991–2020 Adapazarı normallerine göre ortalama yağışlı gün sayıları şöyle:</p>
<table><thead><tr><th>Ay</th><th>Yağış (mm)</th><th>Ort. yağışlı gün</th><th>Yorum</th></tr></thead><tbody>
<tr><td>Ocak</td><td>96</td><td>~16</td><td>Ayın yarısı yağışlı; B planı şart</td></tr>
<tr><td>Şubat</td><td>80</td><td>~14</td><td>Serin ve nemli</td></tr>
<tr><td>Haziran</td><td>85</td><td>~9</td><td>Kısa yaz sağanakları</td></tr>
<tr><td>Temmuz</td><td>50</td><td>~6</td><td>En kurak dönemlerden</td></tr>
<tr><td>Ağustos</td><td>51</td><td>~6</td><td>En kurak dönemlerden</td></tr>
<tr><td>Eylül</td><td>53</td><td>~8</td><td>Çoğunlukla açık</td></tr>
<tr><td>Ekim</td><td>85</td><td>~12</td><td>Yağışlar başlar</td></tr>
<tr><td>Kasım</td><td>73</td><td>~12</td><td>Her iki günden biri yağmurlu olabilir</td></tr>
<tr><td>Aralık</td><td>109</td><td>~16</td><td>Yılın en yağışlı ayı</td></tr>
</tbody></table>
<h2>Yağmurlu havada Sapanca'da yapılacak 8 şey</h2>
<h3>1. Kuzuluk'ta termal havuz</h3>
<p>Yağmurlu bir günün en iyi kurtarıcısı sıcak sudur. Akyazı'ya bağlı <a href="/blog/kuzuluk-kaplicalari-rehberi/">Kuzuluk kaplıcaları</a>, Kırkpınar'dan yaklaşık 47 km (35–45 dakika) uzaklıktadır; kaynağın yüzey sıcaklığı akademik ölçümlerde yaklaşık 51 °C olarak verilir. Günübirlik havuz ve kabin hizmeti veren tesislerin koşullarını önceden sorun.</p>
<h3>2. Acele etmeden kahvaltı</h3>
<p>Yağmur, acele etmeden kahvaltı etmek için en iyi bahanedir. Misafirlerimiz için kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur); camın ardından yağan yağmuru izlerken ikinci çayı söylemek Sapanca'nın kış ritüellerindendir.</p>
<h3>3. Jakuzili odada dinlenmek</h3>
<p>Islak bir öğleden sonrayı odada geçirmek kayıp değil, plandır. Çiftler için <a href="/blog/sapanca-jakuzili-havuzlu-gol-manzarali-oda/">jakuzili oda seçeneklerimizi</a> anlattığımız yazıya göz atın.</p>
<h3>4. Islama köfte ve kabak tatlısı turu</h3>
<p>Sapanca çarşısında ya da 20 dakikalık mesafedeki Adapazarı'nda, coğrafi işaretli <strong>Adapazarı ıslama köftesi</strong> ve <strong>kabak tatlısı</strong> için sıcak bir lokantaya oturun. Ayrıntılar <a href="/blog/sapancada-ne-yenir/">Sapanca'da ne yenir</a> yazımızda.</p>
<h3>5. Taraklı'nın tarihi konakları</h3>
<p>Ahşap Osmanlı evleri ve tarihi çarşısıyla bilinen Taraklı, yağmurda bile gezilebilecek, yarı kapalı bir rotadır; dar sokaklarda dolaşıp sıcak bir yerde mola vermek kolaydır. Rota ve mesafe için <a href="/blog/tarakli-geyve-gunubirlik-tur/">Taraklı ve Geyve günübirlik tur</a> rehberimize bakın.</p>
<h3>6. Yağmur dinince Maşukiye şelaleleri</h3>
<p>Yağışlı günlerin bir güzel yanı, <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'deki şelalelerin ve derelerin gürleşmesidir. Yağmur dindiğinde kısa ve düz bir yürüyüşle dere kenarına inin; ıslak taşlar ve patikalar kaygan olacağı için tabanı tutan ayakkabı giyin. Ardından dere kenarındaki tesislerde sıcak bir öğle yemeği için çok uygun bir zamandır.</p>
<h3>7. Sisli göl kıyısında fotoğraf</h3>
<p>Yağmur sonrası göl üzerinde oluşan sis ve bulutların arasından sızan ışık, Sapanca'nın en atmosferik karelerini verir. Kırkpınar sahili otele birkaç dakika uzaklıktadır. Hangi saatte nereye gideceğinizi <a href="/blog/sapancada-fotograf-gun-batimi-noktalari/">fotoğraf noktaları</a> rehberimizde bulabilirsiniz.</p>
<h3>8. Bahçede kapalı bir köşede çay ve kitap</h3>
<p>Hafif bir yağmurda bahçedeki üstü kapalı cabanalar ve lobi, kitap okumak ya da sadece yağmuru dinlemek için sakin köşelerdir. Akşam için bahçedeki <a href="/#mare">Mare Gastro</a> sizi dışarı çıkmadan ağırlar.</p>
""" + fig("/assets/web/editorial/lobi","DİDİ Otel Sapanca lobisi, büyük cam kapılardan görünen bahçe, kitaplık ve oturma grubu","Yağmurlu bir öğleden sonra için lobide kitaplı bir köşe.") + """
<h2>Yağmurda nelerden kaçınmalı?</h2>
<table><thead><tr><th>Aktivite</th><th>Neden dikkat?</th><th>Alternatif</th></tr></thead><tbody>
<tr><td>Teleferik</td><td>Güçlü rüzgârda seferler durdurulabilir; bulutta manzara kapanır</td><td>Hava açınca gidin; önce 444 6 345'i arayın</td></tr>
<tr><td>Gölde SUP, tekne</td><td>Ani rüzgâr ve fırtına riski</td><td>Kıyıda yürüyüş, fotoğraf</td></tr>
<tr><td>Orman patikaları</td><td>Çamur ve kaygan zemin</td><td>Asfalt ya da düz sahil yolu</td></tr>
<tr><td>Kartepe yolu</td><td>Sis ve kışın buzlanma</td><td>Kuzuluk termal ya da Taraklı</td></tr>
</tbody></table>
<h2>Yağmurlu gün için örnek plan</h2>
<table><thead><tr><th>Saat</th><th>Plan</th></tr></thead><tbody>
<tr><td>09:30</td><td>Acele etmeden kahvaltı</td></tr>
<tr><td>11:30</td><td>Kuzuluk'a hareket (~40 dk), termal havuz</td></tr>
<tr><td>14:30</td><td>Adapazarı'nda ıslama köfte ve kabak tatlısı</td></tr>
<tr><td>16:30</td><td>Otele dönüş; yağmur dindiyse kısa sahil yürüyüşü</td></tr>
<tr><td>19:30</td><td>Bahçede akşam yemeği</td></tr>
</tbody></table>
<h2>Çocuklarla yağmurlu gün</h2>
<p>Çocuklarla yağmurlu bir günde enerjiyi atacak bir plan şart. Yağmur hafiflediğinde Ormanya'nın düz ve sert zeminli yollarında kısa bir tur, Hobbit evlerinin altında saklambaç ya da Maşukiye'de dere kenarında taş saymak bile iyi gelir; çamura karşı yedek kıyafet ve bot şarttır. Kuzuluk'taki termal tesislerin bazılarında aile havuzları ve kabinler bulunabilir; çocuk kabul koşullarını önceden sorun. Akşam yemeği için bir not: otel bahçesindeki Mare Gastro'ya saat 15:00'ten sonra çocuk kabul edilmez, bu yüzden çocuklu akşam yemeklerini buna göre planlayın.</p>
<h2>Yağmurdan sonra en güzel saatler</h2>
<p>Sapanca'nın en etkileyici manzaraları çoğu zaman yağmurun hemen ardından gelir. Bulutlar dağıldığında göl üzerinde alçak sis tabakaları oluşur, Samanlı Dağları'nın yamaçlarından buhar yükselir ve yıkanmış hava görüş mesafesini artırır. Hava açtığı anda Kırkpınar sahiline inmek ya da rüzgâr sakinse teleferiğe binmek, günün en güzel karelerini yakalamanızı sağlar. Kasım ve aralıkta gün 17:30–17:40 civarında kararır; yağmurun dinmesini beklerken bu saati gözden kaçırmayın.</p>
<h2>Yağmur çantası kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="yagmur">
<label><input type="checkbox"><span><b>Su geçirmez mont ve şemsiye</b><span>Özellikle ekim–ocak arası.</span></span></label>
<label><input type="checkbox"><span><b>Kaymayan ayakkabı</b><span>Şelale ve sahil yolları için.</span></span></label>
<label><input type="checkbox"><span><b>Mayo</b><span>Termal B planı için.</span></span></label>
<label><input type="checkbox"><span><b>Kitap ya da oyun</b><span>Otelde geçecek keyifli saatler için.</span></span></label>
<label><input type="checkbox"><span><b>Hava ve rüzgâr takibi</b><span>Teleferik ve göl planları için.</span></span></label>
</div>
<h2>Yağmurlu havada nerede kalınır?</h2>
<p>Yağmurlu bir hafta sonunda konaklamanın kendisi tatilin büyük kısmı olur: sıcak bir oda, iyi bir kahvaltı ve dışarı çıkmadan ulaşılan bir akşam yemeği. Kırkpınar'daki <a href="/#konum">DİDİ Otel Sapanca</a>'da kahvaltı konaklamaya dahildir (Mare Gastro'da tabak kahvaltı olarak servis edilir; serpme kahvaltı fiyat farkıyla sunulur), <a href="/#mare">Mare Gastro</a> aynı bahçededir; <a href="/odalar/king-suit/">King Suit</a> ve <a href="/odalar/junior-suit/">Junior Suit</a> uzun bir kış öğleden sonrası için geniş ve sakin seçeneklerdir. Hava tahmini sizi kararsız bıraktıysa <a href="https://wa.me/905331350888?text=Merhaba%2C%20hafta%20sonu%20Sapanca%27da%20konaklama%20i%C3%A7in%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> yazın; o günün koşullarına göre öneri verelim. Mevsim planı için <a href="/blog/sapancada-sonbahar-rehberi/">sonbahar</a> ve <a href="/blog/sapancada-kisin-gezilecek-yerler/">kış</a> rehberlerimize de bakabilirsiniz.</p>
""",
 "sources":[("Adapazarı iklim verileri 1991–2020, MGM kaynaklı (Wikipedia)","https://en.wikipedia.org/wiki/Adapazar%C4%B1"),
            ("Kuzuluk termal suyu — sıcaklık ve debi ölçümü (DergiPark)","https://dergipark.org.tr/en/download/article-file/4701238"),
            ("TÜRKPATENT — Adapazarı Islama Köftesi coğrafi işaret tescil belgesi","https://ci.turkpatent.gov.tr/Files/GeographicalSigns/7cb1df9b-6fae-4ba6-aab3-1c6c1f73482e.pdf"),
            ("Sapanca Teleferik — iletişim ve çalışma saatleri (resmi site)","https://sapancateleferik.com.tr/")],
 "faq":[("Sapanca'da yağmurlu havada ne yapılır?","Kuzuluk'ta termal havuz, acele etmeden kahvaltı, jakuzili odada dinlenmek, ıslama köfte ve kabak tatlısı turu, Taraklı'nın tarihi konakları ve yağmur dinince Maşukiye şelaleleri en iyi seçeneklerdir."),
        ("Sapanca'da en yağışlı ay hangisi?","1991–2020 Adapazarı normallerine göre en yağışlı ay ortalama 109 mm ve yaklaşık 16 yağışlı günle aralıktır; temmuz ve ağustos en kurak aylardır."),
        ("Yağmurda teleferiğe binilir mi?","Hafif yağmurda çalışabilir, ancak güçlü rüzgârda seferler güvenlik nedeniyle durdurulabilir ve bulut manzarayı kapatabilir. Gitmeden önce 444 6 345'i arayın."),
        ("Kuzuluk Sapanca'ya ne kadar uzak?","Kırkpınar'dan karayoluyla yaklaşık 47 km, 35–45 dakika uzaklıktadır."),
        ("Yağmurlu havada Sapanca'ya gitmeye değer mi?","Evet. Yağışlı günler her zaman gün boyu yağmurlu geçmez; termal, lezzet turu ve otelde dinlenmeyle iyi bir B planı kurulabilir. Sisli göl manzarası da ayrı bir güzelliktir.")],
},
{
 "slug":"sapancada-yazin-yapilacaklar","cat":"Mevsimler","img":"ONN09461","date":"2026-11-16",
 "title":"Sapanca'da Yazın Yapılacaklar: Havuz, SUP, Yayla ve Gün Batımı",
 "seo_title":"Sapanca'da Yazın Yapılacaklar: 10 Serin Fikir",
 "img_alt":"DİDİ Otel Sapanca'da açık havuz, şemsiyeli şezlonglar ve palmiyeler, önde mor begonviller",
 "desc":"Sapanca'da yazın ne yapılır? Klorsuz havuz, gölde SUP, Maşukiye'de dere serinliği, Kartepe yaylası, teleferik, Ormanya ve gün batımı saatleri.",
 "related":["sapancada-havuzlu-otel","sapanca-golu-aktiviteler","ailecek-sapanca-tatili"],
 "lead":"Sapanca'da yazın yapılacakların başında havuzda serinlemek, sabah erken saatlerde gölde SUP, öğle sıcağında Maşukiye'nin dere kenarına ya da Kartepe'nin serin yaylalarına kaçmak ve 20:30 civarında batan güneşi göl kıyısında izlemek gelir. Adapazarı'nın iklim normallerine göre temmuz ve ağustosta gündüz ortalama en yüksek sıcaklık <strong>30 °C</strong> civarında, yağışlı gün sayısı ise ayda ortalama 6'dır; yani yaz, Sapanca'da uzun ve güneşli günler demektir. Aşağıda sıcak saatleri akıllıca kullanan bir yaz programı bulacaksınız.",
 "body":"""
<div class="tldr"><b>Özet</b><ul>
<li><strong>Sabah:</strong> SUP ya da bisiklet (rüzgârsız saatler), teleferik 11:00'de açılır.</li>
<li><strong>Öğle:</strong> Havuz, Maşukiye'de dere kenarı ya da Kartepe'de serin yayla.</li>
<li><strong>Akşam:</strong> Gün batımı haziran–temmuzda ~20:30, ağustosta ~20:00.</li>
<li><strong>Güvenlik:</strong> Gölde can yeleği; ani rüzgâr uyarılarına dikkat.</li>
</ul></div>
<h2>Yazın Sapanca'da hava nasıl?</h2>
<table><thead><tr><th>Ay</th><th>Ort. en yüksek</th><th>Ort. en düşük</th><th>Yağışlı gün</th><th>Gün batımı (ayın 15'i)</th></tr></thead><tbody>
<tr><td>Haziran</td><td>28,2 °C</td><td>16,9 °C</td><td>~9</td><td>20:32</td></tr>
<tr><td>Temmuz</td><td>30,3 °C</td><td>19,1 °C</td><td>~6</td><td>20:29</td></tr>
<tr><td>Ağustos</td><td>30,5 °C</td><td>19,4 °C</td><td>~6</td><td>19:58</td></tr>
</tbody></table>
<p>Tablo, Türkiye Meteoroloji Genel Müdürlüğü kaynaklı 1991–2020 Adapazarı normallerine dayanır. Gece sıcaklıklarının 17–19 °C civarına inmesi, Sapanca'yı İstanbul'un bunaltıcı yaz gecelerinden kaçmak için cazip kılar; akşamları ince bir hırka yeterlidir. Haziranda ise hâlâ ara ara yağmur görülebilir.</p>
<h2>Sapanca'da yazın yapılacak 10 şey</h2>
<table><thead><tr><th>#</th><th>Ne yapılır?</th><th>Nerede</th><th>En iyi saat</th></tr></thead><tbody>
<tr><td>1</td><td>Havuzda serinlemek</td><td>Otel havuzları</td><td>Öğle–öğleden sonra</td></tr>
<tr><td>2</td><td>SUP</td><td>Göl kıyısı</td><td>Sabah erken</td></tr>
<tr><td>3</td><td>Dere kenarında öğle yemeği</td><td>Maşukiye (10–15 dk)</td><td>12:00–14:00</td></tr>
<tr><td>4</td><td>Serin yayla yürüyüşü</td><td>Kartepe, Kuzuyayla (25–30 dk)</td><td>Öğle sıcağında</td></tr>
<tr><td>5</td><td>Teleferikle göl manzarası</td><td>Kırkpınar</td><td>11:00 açılışta</td></tr>
<tr><td>6</td><td>Zipline ve ATV</td><td>Teleferik üst istasyonu</td><td>Sabah</td></tr>
<tr><td>7</td><td>Ormanya'da Hobbit evleri</td><td>Kartepe (~15 dk)</td><td>Sabah ya da akşamüstü</td></tr>
<tr><td>8</td><td>Göl kıyısında bisiklet</td><td>Uzunkum, sahil</td><td>Sabah ya da akşamüstü</td></tr>
<tr><td>9</td><td>Gün batımı</td><td>Kırkpınar sahili</td><td>~20:00–20:30</td></tr>
<tr><td>10</td><td>Bahçede uzun bir akşam yemeği</td><td>Otel bahçesi</td><td>Gün batımından sonra</td></tr>
</tbody></table>
<h2>Sapanca'da havuzlu otel: yazın en çok aranan</h2>
<p>Göl bir içme suyu kaynağı olduğundan Sapanca'da yazın serinlemenin en güvenli ve keyifli yolu havuzdur. DİDİ Otel Sapanca'nın açık havuzu, Sapanca'nın tek klorsuz havuzu; palmiyeli bahçe, cabanalar ve havuz başı servisiyle yaz günlerinin merkezi. Otelin kendi YouTube kanalında paylaştığı kısa videoda havuz alanı, çocuklar için ayrılmış havuz bölümü, restoran ve bar hizmeti ile bahçedeki localar görülüyor:</p>
""" + yt("bISB3PxKJ-M","Didi Otel Sapanca'da havuz planınız hazır mı?","DİDİ Otel'in resmi YouTube kanalından: havuz, bahçe ve localar (50 sn). Video, tıklayana kadar yüklenmez.") + """
<p>Havuzun özellikleri ve klorsuz sistemin farkı için <a href="/blog/sapancada-havuzlu-otel/">Sapanca'da havuzlu otel</a> yazımıza bakın. Havuz sezonu tarihleri için bize <a href="https://wa.me/905331350888?text=Merhaba%2C%20havuz%20sezonu%20ve%20yaz%20konaklamas%C4%B1%20hakk%C4%B1nda%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> yazabilirsiniz.</p>
<h2>Gölde SUP: sabahın sakin suyu</h2>
<p>Yaz sabahları göl genellikle en sakin halindedir ve SUP için idealdir. Temmuz 2026 tarihli DHA haberine göre gölde SUP'u yaygınlaştıran bir dernek ücretsiz tanışma etkinlikleri düzenliyor. Kurallar basit: can yeleği giyin, kıyıdan fazla uzaklaşmayın ve hava tahminini kontrol edin. 22 Temmuz 2026 akşamı ani bir fırtınada göle açılan 35 kişinin AFAD tarafından kurtarılması, yaz fırtınalarının ne kadar hızlı gelebileceğini gösteriyor. Ayrıntılar <a href="/blog/sapanca-golu-aktiviteler/">Sapanca Gölü aktiviteleri</a> yazımızda.</p>
<h2>Öğle sıcağından kaçış: Maşukiye ve Kartepe</h2>
<p>Sıcağın en yüksek olduğu saatlerde iki iyi kaçış var. <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a>'de dere kenarındaki tesislerde gölgede alabalık yemek, ya da 25–30 dakikalık yolla Samanlı Dağları'na tırmanıp Kartepe ve Kuzuyayla'nın serin havasında yürüyüş yapmak. Rakım yükseldikçe sıcaklık belirgin şekilde düşer; yanınıza ince bir üst almayı unutmayın.</p>
""" + fig("/assets/web/editorial/ONN09440","DİDİ Otel Sapanca bahçesinde beyaz tül perdeli ahşap cabanalar ve minderli oturma alanları","Gölgede bir öğleden sonra: bahçedeki cabanalar.") + """
<h2>Çocuklarla yaz: Ormanya ve macera</h2>
<p>Yaz saatlerinde daha uzun açık olan <a href="/blog/ormanya-rehberi/">Ormanya</a>, Hobbit evleri ve hayvan gözlem alanlarıyla çocukların favorisi. Sabah erken gidip öğleni havuzda geçirmek, sıcak çarpmasından korur. Daha hareketli bir gün için teleferiğin üst istasyonundaki zipline ve ATV seçeneklerini <a href="/blog/sapanca-macera-parki-zipline/">macera rehberimizde</a> anlattık. Ailelere yönelik diğer öneriler <a href="/blog/ailecek-sapanca-tatili/">ailecek Sapanca tatili</a> yazımızda.</p>
<h2>Örnek yaz günü</h2>
<table><thead><tr><th>Saat</th><th>Plan</th></tr></thead><tbody>
<tr><td>07:30</td><td>Gölde SUP ya da sahilde yürüyüş</td></tr>
<tr><td>09:00</td><td>Kahvaltı</td></tr>
<tr><td>11:00</td><td>Teleferik (açılış)</td></tr>
<tr><td>13:00</td><td>Maşukiye'de dere kenarında öğle yemeği</td></tr>
<tr><td>14:30–18:00</td><td>Havuz ve cabana</td></tr>
<tr><td>20:00</td><td>Göl kıyısında gün batımı</td></tr>
<tr><td>21:00</td><td>Bahçede akşam yemeği</td></tr>
</tbody></table>
<h2>Yaz hafta sonu kalabalığından nasıl kaçılır?</h2>
<p>Yaz hafta sonları Sapanca'nın en yoğun dönemidir. Kalabalıktan kaçmanın en etkili yolu saatleri kaydırmaktır: popüler noktalara herkesten önce ya da herkesten sonra gidin. Teleferiğe 11:00 açılışında binmek, Maşukiye'de öğle yemeğini 12:00'den önce yemek ve göl kıyısına gün batımından bir saat önce inmek, aynı yerleri çok daha rahat görmenizi sağlar. Cumartesi öğleden sonrası ve pazar öğle saatleri en kalabalık dilimlerdir; bu saatleri havuz başında ya da bahçede geçirmek akıllıca olur. Mümkünse cuma yerine perşembe gelip pazar sabahı erken dönmek, yolda geçen süreyi de belirgin şekilde kısaltır.</p>
<h2>Yaz akşamları: saatler ve küçük notlar</h2>
<p>Yaz akşamları uzundur; güneş haziran ve temmuzda 20:30 civarında batar ve hava saat 21:00'e kadar aydınlık kalır. Göl ve dere kenarlarında akşamüstü sivrisinek olabileceği için kovucu bulundurun. Otelin bahçesindeki Mare Gastro gece 00:00'a kadar açıktır (son sipariş 23:00); yetişkinler için gün batımından sonra uzun bir akşam yemeği planlamak kolaydır. Çocuklu ailelerin bilmesi gereken bir kural var: Mare Gastro'ya saat 15:00'ten sonra çocuk kabul edilmez.</p>
<h2>Yaz çantası kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="yaz">
<label><input type="checkbox"><span><b>Mayo ve havlu</b><span>Havuz ve SUP için.</span></span></label>
<label><input type="checkbox"><span><b>Güneş kremi ve şapka</b><span>Göl yüzeyi güneşi yansıtır.</span></span></label>
<label><input type="checkbox"><span><b>Sivrisinek kovucu</b><span>Göl ve dere kenarında akşamları işe yarar.</span></span></label>
<label><input type="checkbox"><span><b>İnce hırka</b><span>Geceler 17–19 °C, yaylada daha serin.</span></span></label>
<label><input type="checkbox"><span><b>Kapalı ayakkabı</b><span>Zipline, ATV ve yürüyüş için.</span></span></label>
<label><input type="checkbox"><span><b>Hava ve rüzgâr takibi</b><span>Gölde ani fırtınalara karşı.</span></span></label>
</div>
<h2>Yazın Sapanca'da nerede kalınır?</h2>
<p>Yaz kaçamağında havuz, gölge ve iyi bir kahvaltı belirleyicidir. Kırkpınar'daki <a href="/#konum">DİDİ Otel Sapanca</a>, Sapanca'nın tek klorsuz havuzu, palmiyeli bahçesi, cabanaları ve konaklamaya dahil kahvaltısıyla tam da bunu sunar; yetişkinler için akşam yemeği bahçedeki <a href="/#mare">Mare Gastro</a>'da, birkaç adım ötede (Mare Gastro'ya 15:00'ten sonra çocuk kabul edilmez; restoran 00:00'da kapanır, son sipariş 23:00). Aileler için <a href="/odalar/aile/">Aile Odası</a>, çiftler için <a href="/odalar/king-suit/">King Suit</a> öne çıkar. Yaz hafta sonları erken dolduğu için tarihlerinizi netleştirdiğinizde <a href="https://wa.me/905331350888?text=Merhaba%2C%20yaz%20d%C3%B6neminde%20Sapanca%27da%20konaklama%20i%C3%A7in%20m%C3%BCsaitlik%20sormak%20istiyorum.">WhatsApp'tan</a> yazın. Güncel havuz ve bahçe kareleri için <a href="https://www.instagram.com/sapancadidiotel/" target="_blank" rel="noopener">Instagram hesabımıza</a> göz atabilirsiniz.</p>
""",
 "sources":[("Adapazarı iklim verileri 1991–2020, MGM kaynaklı (Wikipedia)","https://en.wikipedia.org/wiki/Adapazar%C4%B1"),
            ("DİDİ Otel resmi YouTube videosu: havuz ve bahçe","https://www.youtube.com/watch?v=bISB3PxKJ-M"),
            ("Sapanca Gölü'nde popülerleşen spor dalı: SUP (DHA, 02.07.2026)","https://www.dha.com.tr/foto-galeri/sapanca-golunde-populerlesen-spor-dali-sup-2902453"),
            ("Sapanca Gölü'nde fırtınaya yakalanan 35 kişi kurtarıldı (GZT, 23.07.2026)","https://www.gzt.com/gundem/sapanca-golunde-firtinaya-yakalanan-35-kisi-afad-ekiplerince-kurtarildi-4243982"),
            ("Sapanca Teleferik — zipline ve çalışma saatleri (resmi site)","https://sapancateleferik.com.tr/zipline/"),
            ("Gün batımı saatleri: NOAA güneş konumu hesabı (Sapanca koordinatları)","https://gml.noaa.gov/grad/solcalc/")],
 "faq":[("Sapanca'da yazın ne yapılır?","Havuzda serinlemek, sabahları gölde SUP, Maşukiye'de dere kenarında öğle yemeği, Kartepe ve Kuzuyayla'da serin yayla yürüyüşü, teleferik, Ormanya ve göl kıyısında gün batımı yazın en sevilen aktivitelerdir."),
        ("Yazın Sapanca'da hava kaç derece?","1991–2020 Adapazarı normallerine göre temmuz ve ağustosta ortalama en yüksek sıcaklık 30 °C civarında, gece en düşük sıcaklık 19 °C civarındadır."),
        ("Sapanca Gölü'nde yüzülür mü?","Göl bir içme suyu kaynağıdır ve güvenlik riskleri vardır; güncel kuralı yerel yönetimden öğrenin. Serinlemek için havuz, gölün tadını çıkarmak için can yeleğiyle SUP öneriyoruz."),
        ("Yazın Sapanca'da gün batımı kaçta?","Haziran ve temmuz ortasında yaklaşık 20:30, ağustos ortasında yaklaşık 20:00'de güneş batar."),
        ("Sapanca'da havuzlu otel var mı?","Evet. DİDİ Otel Sapanca'nın açık havuzu Sapanca'nın tek klorsuz havuzudur; palmiyeli bahçe ve cabanalarla birlikte yaz sezonunda hizmet verir."),
        ("Yazın çocuklarla Sapanca'da nereye gidilir?","Ormanya, teleferik, Uzunkum'da piknik ve bisiklet, Maşukiye'de dere kenarı ve otel havuzu çocuklu aileler için en uygun seçeneklerdir.")],
},
]

def slug_url(s): return f"{SITE}/blog/{s}/"

def article_ld(p):
    return {"@context":"https://schema.org","@type":"Article",
      "headline":p["title"],"description":p["desc"],
      "image":f"{SITE}{IMG}/{p['img']}-1280.webp",
      "datePublished":p["date"],"dateModified":p.get("mod",p["date"]),
      "author":{"@type":"Organization","name":"DİDİ Otel Sapanca","url":f"{SITE}/"},
      "publisher":{"@type":"Organization","name":"DİDİ Otel Sapanca","logo":{"@type":"ImageObject","url":f"{SITE}/assets/brand/adidilogo.png"}},
      "mainEntityOfPage":{"@type":"WebPage","@id":slug_url(p["slug"])},
      "inLanguage":"tr"}

def crumb_ld(p):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Anasayfa","item":f"{SITE}/"},
      {"@type":"ListItem","position":2,"name":"Blog","item":f"{SITE}/blog/"},
      {"@type":"ListItem","position":3,"name":p["title"]}]}

def faq_ld(p):
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
      {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in p["faq"]]}

def pic(img, sizes, cls="", alt="", eager=False):
    b=f"{IMG}/{img}"
    lo='fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    ws=[w for w in (800,1280,1920) if os.path.exists(f"{ROOT}{b}-{w}.webp")] or [800,1280,1920]
    av=",".join(f"{b}-{w}.avif {w}w" for w in ws); wb=",".join(f"{b}-{w}.webp {w}w" for w in ws)
    return (f'<picture><source type="image/avif" srcset="{av}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{wb}" sizes="{sizes}">'
            f'<img src="{b}.jpg" {lo} width="1280" height="720" alt="{html.escape(alt)}" class="{cls}"></picture>')

def read_time(p):
    import re as _re
    words=len(_re.sub(r"<[^>]+>"," ",p["lead"]+" "+p["body"]).split())
    return max(3, round(words/180))

def fmt_date(d):
    y,m,day=d.split("-"); months=["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    return f"{int(day)} {months[int(m)-1]} {y}"

def related(p, others):
    by = {x["slug"]:x for x in others}
    rel = [by[s] for s in p.get("related",[]) if s in by and s!=p["slug"]]
    pool = [x for x in others if x["slug"]!=p["slug"] and x not in rel and x["slug"]!="didi-otel-uniqbee-web-sitesi-hikayesi"]
    rel += [x for x in pool if x["cat"]==p["cat"]]
    rel += sorted([x for x in pool if x not in rel], key=lambda x:x.get("mod",x["date"]), reverse=True)
    return rel[:3]

def wrap_tables(h):
    return h.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")

def build_post(p, others):
    faq_html = "".join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q,a in p["faq"])
    rel = related(p, others)
    rel_html = "".join(
      f'<a href="/blog/{o["slug"]}/" class="bcard"><div class="bcard-img">'+pic(o["img"],"33vw",alt=o["title"])+
      f'</div><div class="bcard-body"><div class="cat">{o["cat"]}</div><h3>{o["title"]}</h3></div></a>' for o in rel)
    schemas = [article_ld(p),crumb_ld(p),faq_ld(p)]
    if p.get("extra_ld"): schemas.append(p["extra_ld"])
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in schemas)
    upd = f'<span class="art-upd">Güncellendi: {fmt_date(p["mod"])}</span>' if p.get("mod") and p["mod"]!=p["date"] else ""
    src_html = ('<section class="art-src"><h2>Kaynaklar</h2><ol>' + "".join(
        f'<li><a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(l)}</a></li>' for l,u in p["sources"]) + '</ol></section>') if p.get("sources") else ""
    yt_js = YT_JS if "yt-facade" in p["body"] else ""
    page = f'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
{GA}
<title>{html.escape(p.get("seo_title") or (p["title"]+" | DİDİ Otel Sapanca"),quote=False)}</title>
<meta name="description" content="{html.escape(p["desc"])}">
<meta name="theme-color" content="#F5F1EA">
<link rel="canonical" href="{slug_url(p["slug"])}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(p.get("seo_title") or p["title"])}">
<meta property="og:description" content="{html.escape(p["desc"])}">
<meta property="og:url" content="{slug_url(p["slug"])}">
<meta property="og:image" content="{SITE}{IMG}/{p['img']}-1280.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/assets/brand/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
{lds}
<link rel="stylesheet" href="/css/site.css?v=13">
{BLOG_CSS}
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N68CWMCH"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
{TRACK}
{NAV}
<article>
<header class="art-hero">
{pic(p["img"],"100vw",alt=p.get("img_alt",p["title"]),eager=True)}
<div class="art-hero-c">
<div class="cat">{p["cat"]}</div>
<h1>{p["title"]}</h1>
<div class="art-meta"><span>{fmt_date(p["date"])}</span>{upd}<span>{read_time(p)} dk okuma</span><span>Sapanca</span></div>
</div>
</header>
<div class="article">
<div class="art-body">
<p class="lead-p">{p["lead"]}</p>
{wrap_tables(p["body"])}
{src_html}
{CTA}
<section class="art-faq">
<h2>Sıkça Sorulan Sorular</h2>
{faq_html}
</section>
</div>
</div>
</article>
<section class="sec exp"><div class="wrap">
<div class="rev" style="margin-bottom:30px"><div class="kick">Blog</div><h2 class="dh">Diğer <b>yazılar</b></h2></div>
<div class="blog-grid">{rel_html}</div>
</div></section>
{FOOT}
{JS}
{yt_js}
</body>
</html>'''
    outdir=f'{ROOT}/blog/{p["slug"]}'
    os.makedirs(outdir,exist_ok=True)
    open(f'{outdir}/index.html','w',encoding='utf-8').write(page)

def build_index():
    INDEX_ORDER = sorted(POSTS, key=lambda x:x.get("mod",x["date"]), reverse=True)
    cards="".join(
      f'<a href="/blog/{p["slug"]}/" class="bcard rev"><div class="bcard-img">'+pic(p["img"],"(max-width:640px) 100vw,(max-width:960px) 50vw,33vw",alt=p["title"])+
      f'</div><div class="bcard-body"><div class="cat">{p["cat"]}</div><h3>{p["title"]}</h3><p>{p["desc"]}</p><span class="more">Devamını oku →</span></div></a>'
      for p in INDEX_ORDER)
    ld={"@context":"https://schema.org","@type":"Blog","name":"DİDİ Otel Sapanca Blog","url":f"{SITE}/blog/",
        "description":"Sapanca gezi rehberi, konaklama önerileri ve yakın çevre rotaları.",
        "blogPost":[{"@type":"BlogPosting","headline":p["title"],"url":slug_url(p["slug"]),"datePublished":p["date"],"dateModified":p.get("mod",p["date"])} for p in INDEX_ORDER]}
    crumb={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Anasayfa","item":f"{SITE}/"},
      {"@type":"ListItem","position":2,"name":"Blog"}]}
    page=f'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
{GA}
<title>Blog — Sapanca Gezi ve Konaklama Rehberi | DİDİ Otel Sapanca</title>
<meta name="description" content="Sapanca gezi rehberi, göl çevresi aktiviteler, Maşukiye ve Kartepe rotaları, konaklama ve lezzet önerileri. DİDİ Otel Sapanca blog.">
<meta name="theme-color" content="#F5F1EA">
<link rel="canonical" href="{SITE}/blog/">
<meta property="og:type" content="website">
<meta property="og:title" content="Blog — Sapanca Gezi ve Konaklama Rehberi | DİDİ Otel Sapanca">
<meta property="og:description" content="Sapanca gezi rehberi, göl çevresi aktiviteler, konaklama ve lezzet önerileri.">
<meta property="og:url" content="{SITE}/blog/">
<meta property="og:image" content="{SITE}{IMG}/otel-havuz-1280.webp">
<link rel="icon" type="image/svg+xml" href="/assets/brand/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(crumb,ensure_ascii=False)}</script>
<link rel="stylesheet" href="/css/site.css?v=13">
{BLOG_CSS}
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N68CWMCH"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
{TRACK}
{NAV}
<section class="blog-hero"><div class="wrap">
<div class="kick" style="justify-content:center">DİDİ Otel Sapanca</div>
<h1 class="dh">Sapanca Gezi & Konaklama Rehberi</h1>
<p class="lead" style="max-width:56ch;margin:20px auto 0">Sapanca'yı keşfetmek isteyenler için gezi rehberleri, yakın çevre rotaları, mevsim önerileri ve konaklama ipuçları.</p>
</div></section>
<section class="sec" style="padding-top:20px"><div class="wrap">
<div class="blog-grid">{cards}</div>
</div></section>
{FOOT}
{JS}
</body>
</html>'''
    os.makedirs(f"{ROOT}/blog",exist_ok=True)
    open(f"{ROOT}/blog/index.html","w",encoding="utf-8").write(page)

if __name__=="__main__":
    for p in POSTS: build_post(p, POSTS)
    build_index()
    print(f"✓ /blog/ index + {len(POSTS)} yazı üretildi")
    for p in POSTS: print("  /blog/"+p["slug"]+"/")
