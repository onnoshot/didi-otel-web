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
<div><h5>İletişim</h5><ul><li><a href="tel:+902645921212">0264 592 12 12</a></li><li><a href="https://wa.me/905331350888">WhatsApp</a></li><li><a href="mailto:info@sapancadidiotel.com">info@sapancadidiotel.com</a></li><li><a href="https://www.google.com/maps/dir/?api=1&destination=K%C4%B1rkp%C4%B1nar+Sapanca%2C+Sakarya" target="_blank" rel="noopener">Yol Tarifi</a></li></ul></div>
</div>
<div class="foot-credits"><span>Bu web sitesi <a href="https://uniqbee.com" target="_blank" rel="noopener">Uniqbee</a> tarafından hazırlanmıştır.</span><span>DİDİ Otel, <a href="https://otelyonet.com.tr/" target="_blank" rel="noopener">Otelyonet</a> sistemleri ile yönetilmektedir.</span></div>
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
 '<a href="/#odalar" class="btn btn-line" style="border-color:rgba(255,255,255,.4);color:#fff">Odaları İncele</a></div></div>')

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
 "slug":"sapancada-gezilecek-yerler","cat":"Gezi Rehberi","img":"otel-havuz","date":"2026-07-01",
 "title":"Sapanca'da Gezilecek Yerler: Göl, Maşukiye ve Kartepe Rehberi",
 "desc":"Sapanca'da gezilecek yerler: Sapanca Gölü, Uzunkum Parkı, Maşukiye şelalesi, Sapanca Teleferik, Kartepe ve Poyrazlar Gölü. Mesafeler, mevsimler, yeme-içme ve konaklama önerileriyle eksiksiz gezi rehberi.",
 "lead":"Sapanca'da gezilecek yerlerin başında Sapanca Gölü ve Uzunkum Parkı, Maşukiye şelaleleri, Sapanca Teleferik, Kartepe ve Poyrazlar Gölü gelir. İstanbul'a yaklaşık 1,5 saat mesafedeki Sapanca, göl kıyısı yürüyüşlerinden dağ manzaralı doğa rotalarına kadar dört mevsim keşfedilecek bir destinasyondur. Aşağıda bu duraklara olan mesafeleri, hangi mevsimde ne yapılacağını ve gezinizi kuracağınız ideal merkezi bir arada bulacaksınız.</p><p>Tüm bu noktalara birkaç dakika mesafedeki göl kıyısı mahallesi <strong>Kırkpınar</strong>, gezinizi kurmak için en pratik başlangıç noktasıdır; <a href=\"/#konum\">DİDİ Otel Sapanca</a> tam da burada, göl ile orman arasında yer alır.",
 "body":"""
<h2>Sapanca'da gezilecek yerler: kısa bakış</h2>
<p>Sapanca, İstanbul ve Kocaeli'den kısa sürede ulaşılan bir doğa kaçamağıdır. İlçenin merkezinde <strong>Sapanca Gölü</strong>, çevresinde ise şelaleler, teleferik, dağ zirveleri ve saklı göller yer alır. Aşağıdaki başlıca durakların hepsi, gölün en sakin kıyısı olan <a href="/#konum">Kırkpınar'daki konumumuza</a> yarım saatlik bir sürüş mesafesindedir.</p>
<div class="stat-row rev">
<div class="stat-card"><span class="stat-num" data-count="1,5">0</span><span class="stat-label">saat İstanbul'dan</span></div>
<div class="stat-card"><span class="stat-num" data-count="45">0</span><span class="stat-label">km² Sapanca Gölü</span></div>
<div class="stat-card"><span class="stat-num" data-count="20">0</span><span class="stat-label">dakika Maşukiye'ye</span></div>
<div class="stat-card"><span class="stat-num" data-count="4">0</span><span class="stat-label">mevsim keşif</span></div>
</div>
<h2>Sapanca Gölü ve Uzunkum Parkı</h2>
<p>Bölgenin kalbi <strong>Sapanca Gölü</strong>'dür. Yaklaşık 45 km² yüzölçümüyle Türkiye'nin sevilen tatlı su göllerinden biridir ve kıyısı bisiklet turu, yürüyüş, tekne ve kano için idealdir. Göl kıyısındaki <strong>Uzunkum Parkı</strong>, ilçenin en güzel manzaralarına sahip dinlenme ve piknik alanlarından biridir; gün batımında göl kenarında yürüyüş yapmak Sapanca'nın klasik deneyimlerindendir.</p>
<p>Gölde yapılabilecekler için <a href="/blog/sapanca-golu-aktiviteler/">Sapanca Gölü aktiviteleri</a> rehberimize, en güzel kareleri yakalamak için ise <a href="/blog/sapancada-fotograf-gun-batimi-noktalari/">fotoğraf ve gün batımı noktaları</a> yazımıza göz atabilirsiniz.</p>
<h2>Maşukiye: şelaleler ve alabalık vadisi</h2>
<p>Sapanca'ya yaklaşık <strong>20 dakika</strong> mesafedeki <strong>Maşukiye</strong>, yemyeşil doğası, şelaleleri ve dere kenarındaki alabalık tesisleriyle ünlüdür. Şelalelerin su debisi ilkbaharda, karların erimesiyle en yüksek seviyeye ulaşır; yaz aylarında ise serin dere kenarları öne çıkar. Rota önerileri için <a href="/blog/masukiye-kartepe-gezi/">Maşukiye ve Kartepe gezi rehberimize</a> bakabilirsiniz.</p>
<h2>Sapanca Teleferik ile Mahmudiye'ye çıkış</h2>
<p><strong>Sapanca Teleferik</strong>, göl seviyesinden ormanın içine yükselen yaklaşık 1,5 kilometrelik bir hattır. Alt istasyon, <a href="/#konum">DİDİ Otel'in de bulunduğu Kırkpınar Mahallesi'nde</a>; üst istasyon ise seyir teraslı <strong>Mahmudiye</strong>'dedir. Kabinlerden Sapanca Gölü'nü kuşbakışı izlemek, ilçenin en sevilen deneyimlerinden biridir. Güncel bilet, saat ve mevsim önerileri için <a href="/blog/sapanca-teleferik-rehberi/">Sapanca Teleferik rehberimizi</a> inceleyin. Otelimiz teleferiğin alt istasyonuyla aynı mahallede olduğu için bu geziye yürüyüş mesafesinde başlayabilirsiniz.</p>
<h2>Kartepe: dört mevsim dağ keyfi</h2>
<p>Samanlı Dağları'nın zirvesindeki <strong>Kartepe Kayak Merkezi</strong>, Sapanca'dan yaklaşık <strong>30 dakika</strong> uzaklıktadır. Kışın kayak ve telesiyej ile Sapanca Gölü manzarası, yazın ise serin bir yayla havası ve yürüyüş parkurları sunar. Hangi ayda gitmenin daha keyifli olacağını <a href="/blog/sapanca-hangi-mevsim-gidilir/">Sapanca hangi mevsim gidilir</a> yazımızda ayrıntılı anlattık.</p>
<h2>Poyrazlar Gölü ve gizli köşeler</h2>
<p>Kalabalıktan uzaklaşmak isteyenler için Sapanca'ya yaklaşık <strong>15 dakika</strong> mesafedeki <strong>Poyrazlar Gölü Tabiat Parkı</strong>, kamp, tekne turu, olta balıkçılığı ve kuş gözlemi için idealdir. Osmanlı dokusunu koruyan <strong>Mahmudiye</strong> köyünün pazarları da doğayla iç içe huzurlu bir moladır. Ayrıntılar için <a href="/blog/poyrazlar-golu-mahmudiye-gizli-koseler/">Poyrazlar Gölü ve gizli köşeler</a> rehberimize bakın.</p>
<h2>Kırkpınar: gölün en sakin kıyısı</h2>
<p>Yukarıdaki durakların tamamına en yakın nokta, gölün kuzey kıyısındaki <strong>Kırkpınar Mahallesi</strong>'dir. Sessiz, yeşil ve göl manzaralı bu mahalle, hem teleferiğin alt istasyonuna hem de göl kıyısına yürüme mesafesindedir. <a href="/#konum">DİDİ Otel Sapanca</a> tam burada; <a href="/blog/sapancada-havuzlu-otel/">Sapanca'nın tek klorsuz havuzu</a>, göl ve orman manzaralı <a href="/odalar/">oda tipleri</a> ve bahçedeki restoranıyla gezinizin merkezi olur.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="doga">Doğa severler</button><button data-tab="cift">Çiftler</button><button data-tab="aile">Aileler</button></div>
<div class="itin-panel on" data-tab="doga"><p>Göl kıyısında sabah yürüyüşü, Maşukiye'de şelale ve alabalık molası, ardından <a href="/blog/sapanca-teleferik-rehberi/">teleferikle</a> Mahmudiye seyir terasına çıkış. Enerjiniz varsa ikinci gün Poyrazlar Gölü'nde tekne turu ekleyin. Konaklama için <a href="/blog/sapancada-havuzlu-otel/">havuzlu bir otel</a> seçmek, gün sonunda dinlenmenizi kolaylaştırır.</p></div>
<div class="itin-panel" data-tab="cift"><p>Göl kenarında gün batımı yürüyüşü, teleferikte panoramik manzara ve akşam <a href="/#mare">Mare Gastro</a>'da göl havasında bir yemek. İki kişilik özel bir kaçamak için <a href="/blog/sapancada-romantik-hafta-sonu/">romantik hafta sonu</a> ve <a href="/blog/sapancada-balayi-ozel-gunler/">balayı</a> rehberlerimiz size ilham verir.</p></div>
<div class="itin-panel" data-tab="aile"><p>Çocuklarla Uzunkum Parkı'nda piknik, Maşukiye'de alabalık, Poyrazlar'da kamp ve doğa yürüyüşü ideal bir kombinasyondur. Geniş aile odaları ve havuz için <a href="/blog/ailecek-sapanca-tatili/">ailecek Sapanca tatili</a> yazımıza göz atın.</p></div>
</div>
<h2>Sapanca'da nerede yemek yenir?</h2>
<p>Gezi kadar keyifli bir başka konu da yeme-içmedir. Güne zengin bir serpme kahvaltıyla başlayıp akşamı göl havasında bir yemekle kapatmak, Sapanca'nın klasik ritmidir. Otel bahçesindeki <a href="/#mare"><strong>Mare Gastro</strong></a>, taze deniz ürünleri ve Akdeniz mutfağını zarif bir atmosferde sunar. Sabah kahvaltısından akşam yemeğine öneriler için <a href="/blog/sapancada-kahvalti-ve-yemek/">Sapanca'da kahvaltı ve yemek</a> rehberimize bakabilirsiniz.</p>
<h2>Sapanca gezi kontrol listesi</h2>
<p>Aşağıdaki listeden gezinizde yapmak istediklerinizi işaretleyin — seçimleriniz tarayıcınızda kaydedilir.</p>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/8</b></div>
<div class="spot-check" data-key="gezilecek-yerler">
<label><input type="checkbox"><span><b>Sapanca Gölü kıyısında yürüyüş</b><span>Uzunkum Parkı'nda göl kenarında bir tur atın.</span></span></label>
<label><input type="checkbox"><span><b>Maşukiye'de şelale ve alabalık</b><span>Dere kenarındaki bir tesiste öğle yemeği yiyin.</span></span></label>
<label><input type="checkbox"><span><b>Sapanca Teleferik yolculuğu</b><span>Kırkpınar'dan binip Mahmudiye seyir terasına çıkın.</span></span></label>
<label><input type="checkbox"><span><b>Kartepe'de dağ havası</b><span>Kışın kayak, yazın yürüyüş parkurlarını deneyin.</span></span></label>
<label><input type="checkbox"><span><b>Poyrazlar Gölü'nde doğa</b><span>Tekne turu, olta balıkçılığı ya da kuş gözlemi yapın.</span></span></label>
<label><input type="checkbox"><span><b>Gün batımında fotoğraf</b><span>Göl kıyısında altın saat karelerini yakalayın.</span></span></label>
<label><input type="checkbox"><span><b>Mare Gastro'da akşam yemeği</b><span>Bahçede göl havasında bir yemekle günü tamamlayın.</span></span></label>
<label><input type="checkbox"><span><b>Klorsuz havuzda dinlenme</b><span>Gün sonunda otelin havuzunda bir mola verin.</span></span></label>
</div>
<h3>Yakın çevre mesafeleri</h3>
<p>Aşağıdaki süreler, gölün kuzey kıyısındaki <a href="/#konum">Kırkpınar / DİDİ Otel</a> konumundan verilmiştir.</p>
<table><thead><tr><th>Yer</th><th>Mesafe</th></tr></thead><tbody>
<tr><td>Sapanca Gölü / Uzunkum Parkı</td><td>~5 km</td></tr>
<tr><td>Sapanca Teleferik alt istasyonu</td><td>Aynı mahalle (yürüme mesafesi)</td></tr>
<tr><td>Maşukiye (şelale, alabalık)</td><td>~20 dk</td></tr>
<tr><td>Kartepe Kayak Merkezi</td><td>~30 dk</td></tr>
<tr><td>Poyrazlar Gölü</td><td>~15 dk</td></tr>
<tr><td>İstanbul</td><td>~1,5 saat</td></tr>
<tr><td>Sabiha Gökçen Havalimanı</td><td>~1 saat</td></tr></tbody></table>
<p>Sapanca'ya ulaşımın ayrıntıları için <a href="/blog/sapancaya-nasil-gidilir/">Sapanca'ya nasıl gidilir</a> yazımızı, gününüzü saat saat planlamak için <a href="/blog/sapancada-1-gunluk-2-gunluk-gezi-plani/">1 ve 2 günlük gezi planımızı</a> inceleyebilirsiniz.</p>
<h2>Sapanca'da nerede kalınır?</h2>
<p>Tüm bu noktalara kısa mesafede olan <a href="/#konum">DİDİ Otel Sapanca</a>, <a href="/#odalar">göl ve orman manzaralı odaları</a>, <a href="/blog/sapancada-havuzlu-otel/">Sapanca'nın tek klorsuz havuzu</a> ve <a href="/#mare">Mare Gastro</a> restoranıyla gezileriniz için ideal bir merkez olur. Misafir deneyimlerini <a href="/blog/didi-otel-sapanca-misafir-yorumlari/">misafir yorumları</a> sayfamızda, rezervasyon adımlarını ise <a href="/blog/didi-otel-nereden-rezervasyon-yapilir/">nereden rezervasyon yapılır</a> yazımızda bulabilirsiniz. Müsaitlik ve güncel fiyatlar için <a href="https://wa.me/905331350888?text=Merhaba%2C%20Sapanca%20gezisi%20i%C3%A7in%20D%C4%B0D%C4%B0%20Otel%27de%20konaklama%20yapmak%20istiyorum.">WhatsApp'tan</a> bize ulaşabilirsiniz.</p>
""",
 "extra_ld":{"@context":"https://schema.org","@type":"ItemList","name":"Sapanca'da gezilecek yerler","itemListElement":[
   {"@type":"ListItem","position":1,"item":{"@type":"TouristAttraction","name":"Sapanca Gölü","description":"İstanbul'a yaklaşık 1,5 saat mesafede, yürüyüş, bisiklet ve tekne için ideal tatlı su gölü.","address":{"@type":"PostalAddress","addressLocality":"Sapanca","addressRegion":"Sakarya","addressCountry":"TR"}}},
   {"@type":"ListItem","position":2,"item":{"@type":"TouristAttraction","name":"Uzunkum Parkı","description":"Sapanca Gölü kıyısında piknik ve gün batımı yürüyüşü için sevilen dinlenme alanı."}},
   {"@type":"ListItem","position":3,"item":{"@type":"TouristAttraction","name":"Maşukiye","description":"Sapanca'ya 20 dakika mesafede şelaleleri ve alabalık tesisleriyle ünlü doğa vadisi."}},
   {"@type":"ListItem","position":4,"item":{"@type":"TouristAttraction","name":"Sapanca Teleferik","description":"Kırkpınar'dan Mahmudiye seyir terasına göl manzaralı 1,5 km'lik teleferik hattı."}},
   {"@type":"ListItem","position":5,"item":{"@type":"TouristAttraction","name":"Kartepe Kayak Merkezi","description":"Samanlı Dağları'nda kışın kayak, yazın yürüyüş sunan dağ merkezi; Sapanca'ya 30 dakika."}},
   {"@type":"ListItem","position":6,"item":{"@type":"TouristAttraction","name":"Poyrazlar Gölü Tabiat Parkı","description":"Sapanca'ya 15 dakika mesafede kamp, tekne turu ve kuş gözlemi için sakin bir tabiat parkı."}}
 ]},
 "faq":[("Sapanca'da mutlaka görülmesi gereken yer neresidir?","Sapanca Gölü ve göl kıyısındaki Uzunkum Parkı ilçenin simgesidir. Ayrıca 20 dakika mesafedeki Maşukiye şelaleleri, Kırkpınar'dan kalkan Sapanca Teleferik ve 30 dakikadaki Kartepe öne çıkar."),
        ("Sapanca'yı bir günde gezmek mümkün mü?","Göl kıyısı, teleferik ve Maşukiye bir günde rahatça görülebilir; Kartepe ve Poyrazlar Gölü'nü de eklemek isteyenler için en az bir gece konaklama önerilir. Saat saat plan için 1 ve 2 günlük gezi planımıza bakabilirsiniz."),
        ("Sapanca hangi şehre yakındır?","Sapanca, İstanbul'a yaklaşık 1,5 saat, Sabiha Gökçen Havalimanı'na yaklaşık 1 saat, Sakarya merkeze ise 15 kilometre mesafededir."),
        ("Sapanca gezisi için nerede kalmak avantajlıdır?","Gölün en sakin kıyısı olan Kırkpınar, göl kıyısına ve teleferiğin alt istasyonuna yürüme mesafesindedir. DİDİ Otel Sapanca bu mahallede yer alır ve tüm başlıca duraklara yarım saat içindedir."),
        ("Sapanca çocuklu aileler için uygun mu?","Evet. Uzunkum Parkı'nda piknik, Maşukiye'de alabalık, Poyrazlar Gölü'nde doğa yürüyüşü ve otel havuzu çocuklu aileler için keyifli bir kombinasyon oluşturur."),
        ("Sapanca hangi mevsimde gezilir?","Sapanca dört mevsim gezilebilir; ilkbaharda şelaleler gürler, yazın göl ve havuz, sonbaharda renkli orman, kışın ise Kartepe'de kar öne çıkar."),
        ("Sapanca'da akşam nerede yemek yenir?","Otel bahçesindeki Mare Gastro, taze deniz ürünleri ve Akdeniz mutfağını göl havasında sunar; gün boyu gezdikten sonra akşam yemeği için pratik bir seçenektir.")],
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
 "slug":"sapancaya-nasil-gidilir","cat":"Ulaşım","img":"dis-cephe","date":"2026-07-03",
 "title":"Sapanca'ya Nasıl Gidilir? Ulaşım ve Yol Rehberi",
 "desc":"Sapanca'ya İstanbul, Ankara ve havalimanlarından ulaşım; otoyol, tren ve mesafe bilgileri. DİDİ Otel Sapanca konumu ve yol tarifi.",
 "lead":"Sapanca'ya en pratik ulaşım, TEM otoyolu üzerinden araçla sağlanır. İstanbul'dan yaklaşık 1,5 saat, Sabiha Gökçen Havalimanı'ndan yaklaşık 95 kilometre mesafededir. Tren ile de ulaşım mümkündür.",
 "body":"""
<h2>Araçla Sapanca'ya nasıl gidilir?</h2>
<p>En yaygın yöntem TEM otoyoludur. İstanbul yönünden gelenler <strong>Sapanca gişelerinden</strong> çıkış yapar. <a href="/#konum">DİDİ Otel Sapanca</a>, bu gişelere yalnızca 500 metre, Sapanca merkeze ise 3 kilometre mesafededir.</p>
<h2>Havalimanından mesafe</h2>
<p>Sabiha Gökçen Havalimanı'ndan Sapanca yaklaşık 95 kilometredir. Havalimanına inen misafirler araç kiralayarak veya transferle kısa sürede otele ulaşabilir.</p>
<h2>Trenle ulaşım</h2>
<p>Sapanca, tren hattı üzerinde yer alır ve gar merkeze yakındır. Toplu taşımayla gelenler için tren keyifli bir alternatiftir; ancak göl çevresi ve yakın noktalar için araç konforu önerilir.</p>
<h3>Mesafeler</h3>
<table><thead><tr><th>Nereden</th><th>Mesafe</th></tr></thead><tbody>
<tr><td>İstanbul (TEM)</td><td>~1,5 saat</td></tr>
<tr><td>Otoyol Sapanca gişeleri</td><td>500 m</td></tr>
<tr><td>Sapanca merkez</td><td>3 km</td></tr>
<tr><td>Sakarya merkez</td><td>15 km</td></tr>
<tr><td>Sabiha Gökçen Havalimanı</td><td>~95 km</td></tr></tbody></table>
<p>Yol tarifi için <a href="https://www.google.com/maps/dir/?api=1&destination=K%C4%B1rkp%C4%B1nar+Sapanca%2C+Sakarya" target="_blank" rel="noopener">Google Haritalar üzerinden rota</a> alabilirsiniz.</p>
""",
 "faq":[("İstanbul'dan Sapanca kaç saat sürer?","TEM otoyolu üzerinden yaklaşık 1,5 saat sürer."),
        ("Sapanca'ya trenle gidilir mi?","Evet, Sapanca tren hattı üzerindedir ve gar merkeze yakındır."),
        ("En yakın havalimanı hangisidir?","Sabiha Gökçen Havalimanı, Sapanca'ya yaklaşık 95 kilometre mesafeyle en yakın havalimanıdır.")],
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
 "slug":"sapanca-golu-aktiviteler","cat":"Aktiviteler","img":"havuz2","date":"2026-07-08",
 "title":"Sapanca Gölü Çevresinde Aktiviteler: Bisiklet, Tekne, Yürüyüş",
 "desc":"Sapanca Gölü çevresinde yapılacaklar; 16 km bisiklet turu, tekne ve kano, göl kıyısı yürüyüşü ve doğa rotaları.",
 "lead":"Sapanca Gölü çevresi yaklaşık 16 kilometre uzunluğundadır ve bisiklet turu, tekne gezisi, kano ve göl kıyısı yürüyüşü için idealdir. Doğa yürüyüşü ve orman rotaları da bölgenin sevilen aktiviteleri arasındadır.",
 "body":"""
<h2>Göl çevresinde bisiklet</h2>
<p>Yaklaşık 16 kilometrelik göl çevresi, bisiklet turu için popüler bir rotadır. Göl manzarası eşliğinde sakin bir sürüş, doğayla iç içe keyifli bir aktivitedir.</p>
<h2>Tekne ve kano</h2>
<p>Göl üzerinde tekne gezisi ve kano, suyla iç içe bir deneyim sunar. Sabahın erken saatleri ve gün batımı, göl üzerinde en huzurlu zamanlardır.</p>
<h2>Yürüyüş ve doğa rotaları</h2>
<p>Göl kıyısı yürüyüşleri ve orman patikaları her seviyeye uygundur. Adrenalin sevenler için bölgede rehberli <strong>ATV</strong> turları da düzenlenir.</p>
<h3>Aktivite özeti</h3>
<ul>
<li>Göl çevresi bisiklet turu (~16 km)</li>
<li>Tekne gezisi ve kano</li>
<li>Göl kıyısı ve orman yürüyüşü</li>
<li>Rehberli ATV turları</li>
</ul>
<p>Gün boyu aktivitenin ardından <a href="/#odalar">otelde dinlenmek</a> ve bahçede sakin bir akşam, günü tamamlar.</p>
""",
 "faq":[("Sapanca Gölü çevresinde bisiklet sürülür mü?","Evet. Yaklaşık 16 kilometrelik göl çevresi bisiklet turu için popüler bir rotadır."),
        ("Sapanca Gölü'nde tekne gezisi var mı?","Göl üzerinde tekne gezisi ve kano gibi su aktiviteleri yapılabilir."),
        ("Sapanca'da doğa yürüyüşü için rota var mı?","Göl kıyısı ve orman patikaları her seviyeye uygun yürüyüş rotaları sunar.")],
},
{
 "slug":"sapancada-kahvalti-ve-yemek","cat":"Lezzet","img":"kahvalti","date":"2026-07-09",
 "title":"Sapanca'da Kahvaltı ve Göl Manzaralı Yemek Keyfi",
 "desc":"Sapanca'da kahvaltı ve göl manzaralı yemek; zengin serpme kahvaltı ve bahçede Akdeniz mutfağı sunan Mare Gastro restoranı.",
 "lead":"Sapanca'da güne zengin bir serpme kahvaltıyla başlamak ve akşam göl havasında bir yemek yemek, bölgenin en sevilen deneyimlerindendir. DİDİ Otel bahçesindeki Mare Gastro, taze deniz ürünleri ve Akdeniz mutfağını zarif bir atmosferde sunar.",
 "body":"""
<h2>Zengin serpme kahvaltı</h2>
<p>Sapanca kahvaltısı, yöresel lezzetlerle donatılan zengin bir sofra anlamına gelir. DİDİ Otel'de tüm konaklamalara <strong>serpme kahvaltı</strong> dahildir; güne göl havasında keyifli bir başlangıç yapılır.</p>
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
 "faq":[("DİDİ Otel'de kahvaltı dahil mi?","Evet, tüm konaklamalara zengin serpme kahvaltı dahildir."),
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
<p><a href="/#odalar">DİDİ Otel Sapanca</a>, Kırkpınar'da açık havuz, geniş bahçe, serpme kahvaltı ve <a href="/#mare">Mare Gastro</a> restoranıyla konforlu bir konaklama sunar. Suit odalardan aile odalarına kadar farklı ihtiyaçlara uygun seçenekler bulunur.</p>
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
 "slug":"sapanca-teleferik-rehberi","cat":"Teleferik","img":"ONN09422","date":"2026-08-13",
 "title":"Sapanca Teleferik Rehberi: Fiyatlar, Saatler ve Kırkpınar'dan Kalkan Hat",
 "desc":"Sapanca Teleferik güncel bilet fiyatları, çalışma saatleri, Kırkpınar-Mahmudiye hattı ve DİDİ Otel'e yakınlığı. Ziyaret öncesi bilmeniz gereken her şey.",
 "lead":"Sapanca Teleferik, Kırkpınar'daki alt istasyondan Mahmudiye Mahallesi'ndeki üst istasyona 1,5 kilometrelik bir hatla göl ve orman manzarasını gökyüzünden izletir. Yolculuk yaklaşık 10 dakika sürer; güncel tam bilet gidiş-dönüş 450 TL, öğrenci bileti 300 TL'dir.",
 "body":"""
<h2>Sapanca Teleferik nedir, nereden nereye gidiyor?</h2>
<p><strong>Sapanca Teleferik</strong>, Samanlı Dağları'nın eteğinde, göl seviyesinden ormanın içine yükselen 1,5 kilometrelik bir hattır. Alt istasyon <strong>Kırkpınar</strong>'da — DİDİ Otel'in de bulunduğu mahalledir — üst istasyon ise <strong>Mahmudiye Mahallesi</strong>'ndedir. Hatta 36 panoramik cam kabin hizmet verir, her kabin 8 kişi taşır ve sistem saatte yaklaşık 1500 yolcu kapasitesine sahiptir.</p>
<div class="stat-row rev">
<div class="stat-card"><span class="stat-num" data-count="1,5">0</span><span class="stat-label">km hat uzunluğu</span></div>
<div class="stat-card"><span class="stat-num" data-count="10">0</span><span class="stat-label">dakika yolculuk</span></div>
<div class="stat-card"><span class="stat-num" data-count="36">0</span><span class="stat-label">panoramik kabin</span></div>
<div class="stat-card"><span class="stat-num" data-count="450">0</span><span class="stat-label">TL tam bilet (gidiş-dönüş)</span></div>
</div>
<h2>Bilet fiyatları ve çalışma saatleri</h2>
<p>Biletler yalnızca gişeden, alındığı gün için satılır; online satış bulunmuyor.</p>
<table><thead><tr><th>Bilet / Bilgi</th><th>Detay</th></tr></thead><tbody>
<tr><td>Tam bilet (gidiş-dönüş)</td><td>450 TL</td></tr>
<tr><td>Öğrenci bileti (gidiş-dönüş)</td><td>300 TL</td></tr>
<tr><td>0-6 yaş, gazi, 1. derece şehit yakını</td><td>Ücretsiz</td></tr>
<tr><td>Çalışma saatleri</td><td>Her gün 11:00 – 20:00</td></tr>
</tbody></table>
<h2>Üst istasyonda neler var?</h2>
<p>Mahmudiye Mahallesi'ndeki üst istasyon, orman içinde bir seyir terasıyla Sapanca Gölü'nü kuşbakışı izletir; hatıra fotoğrafı için tam sırasıdır. Çevresinde kafeterya, restoran ve ATV safari gibi aktiviteler de yer alır. Buradan devam ederek <a href="/blog/poyrazlar-golu-mahmudiye-gizli-koseler/">Mahmudiye'nin köy pazarlarını</a> da keşfedebilirsiniz.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="yaz">Yazın gidenler için</button><button data-tab="kis">Kışın gidenler için</button></div>
<div class="itin-panel on" data-tab="yaz"><p>Yaz aylarında hat, yemyeşil ormanın üzerinden geçerken göl suyu güneşte parıldar; akşamüzeri saatlerde ışık en yumuşak halini alır ve fotoğraf için idealdir.</p></div>
<div class="itin-panel" data-tab="kis"><p>Kış aylarında Samanlı Dağları'nın karlı zirveleri ve zaman zaman bulut denizinin üzerinde süzülme hissi öne çıkar; sert rüzgar ve hava koşullarına bağlı sefer iptalleri olabileceğinden gitmeden önce hava durumunu kontrol etmek faydalıdır.</p></div>
</div>
<h2>DİDİ Otel'den teleferiğe nasıl gidilir?</h2>
<p>Teleferiğin alt istasyonu, <a href="/#konum">DİDİ Otel Sapanca</a>'nın da bulunduğu Kırkpınar mahallesinde yer alır. Bu da onu, otelde konaklayan misafirler için en kolay ulaşılan Sapanca aktivitelerinden biri yapar. Gün içinde teleferik turunun ardından akşamı bahçedeki <a href="/#mare">Mare Gastro</a>'da göl havasında bir yemekle tamamlayabilirsiniz.</p>
<h3>Ziyaret ipuçları</h3>
<ul>
<li>En sakin saatler hafta içi sabah ve öğleden sonranın ilk saatleridir; hafta sonları gişe önünde kısa bir bekleme olabilir.</li>
<li>Yükseklikte rüzgar hissedilebilir; ince bir mont almanızı öneririz.</li>
<li>Fotoğraf çekmek isteyenler kabinde pencereye yakın oturmayı tercih edebilir.</li>
</ul>
""",
 "faq":[("Sapanca Teleferik nereden kalkıyor?","Alt istasyon Kırkpınar'dadır — DİDİ Otel Sapanca'nın da bulunduğu mahalle. Üst istasyon ise Mahmudiye Mahallesi'ndedir."),
        ("Sapanca Teleferik bilet fiyatı ne kadar?","Tam bilet gidiş-dönüş 450 TL, öğrenci bileti 300 TL'dir. 0-6 yaş, gazi ve 1. derece şehit yakınları ücretsiz biner."),
        ("Teleferik yolculuğu kaç dakika sürüyor?","Hat 1,5 kilometre uzunluğundadır ve yolculuk ortalama 10 dakika sürer."),
        ("Sapanca Teleferik hangi saatlerde çalışıyor?","Haftanın her günü 11:00 ile 20:00 arasında hizmet verir.")],
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
<div class="tl-step"><div class="tl-time">09:00</div><h4>DİDİ Otel'de serpme kahvaltı</h4><p>Güne göl manzarasına karşı zengin bir kahvaltıyla başlayın.</p></div>
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
 "slug":"sapancada-ne-yenir","cat":"Lezzet","img":"mare-ic","date":"2026-08-26",
 "title":"Sapanca'da Ne Yenir? Yöresel Lezzetler ve Restoran Rehberi",
 "desc":"Sapanca'da ne yenir? Kiremitte alabalık, Adapazarı ıslama köfte, Çerkez mutfağı ve göl manzaralı serpme kahvaltı. Öne çıkan restoranlar ve DİDİ Otel'de Mare Gastro rehberi.",
 "lead":"Sapanca'da ne yeneceğinizin kısa cevabı: kiremitte pişen taze alabalık, Adapazarı'nın tarihi ıslama köftesi, Çerkez mutfağının isli peyniri ve Çerkez tavuğu, bir de göl manzaralı zengin serpme kahvaltı. Sakarya ve Çerkez mutfaklarının buluştuğu bölge, doğa kadar sofrasıyla da bir gezi sebebidir. Aşağıda mutlaka tatmanız gereken lezzetleri, öne çıkan adresleri ve otelimizin bahçesindeki <a href=\"/#mare\">Mare Gastro</a>'yu bir arada bulacaksınız.",
 "body":"""
<h2>Sapanca mutfağı: Çerkez ve Sakarya lezzetlerinin buluşması</h2>
<p>Sapanca ve çevresi; göl balıkçılığı, bereketli Sakarya ovası ve bölgeye yerleşen Çerkez topluluklarının mutfağıyla şekillenir. Bu yüzden sofrada hem taze alabalık, hem sulu esnaf yemekleri, hem de Kafkas kökenli özel tatlar bir arada bulunur.</p>
<h2>Kiremitte alabalık: bölgenin imza lezzeti</h2>
<p><strong>Kiremitte alabalık</strong>, Sapanca ve özellikle <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a> vadisinin simge yemeğidir. Dere kenarındaki tesislerde, tereyağıyla kiremit üzerinde pişirilen alabalık neredeyse her menüde bulunur; yanında mısır ekmeği ve taze yeşilliklerle servis edilir.</p>
<h2>Islama köfte: 1900'lerden gelen tat</h2>
<p>Adapazarı'nın tarihi lezzeti <strong>ıslama köfte</strong>, özel sosuna batırılmış ekmekle servis edilen ve 1900'lerden beri yörenin baş tacı olan bir esnaf klasiğidir. Sapanca çarşısında ve çevre lokantalarda kolayca bulunur.</p>
<h2>Çerkez mutfağı: isli peynir ve Çerkez tavuğu</h2>
<p>Kafkas mutfağının izini taşıyan <strong>Çerkez tavuğu</strong> (cevizli soğuk meze) ve <strong>isli peynir</strong>, bölgenin en özel tatlarındandır. Zengin bir Çerkez kahvaltısında ayrıca barbunya ezmesi, cevizli fasulye, karalahana ezmesi, taze fasulye turşusu ve mısır ekmeği gibi lezzetler de sofraya gelir.</p>
<h2>Göl manzaralı serpme kahvaltı</h2>
<p>Sapanca'nın klasiklerinden biri de güne göl kenarında <strong>zengin bir serpme kahvaltıyla</strong> başlamaktır. Köy peyniri, ev reçelleri, bal-kaymak ve sıcak hamur işleri eşliğinde göl havası, kahvaltıyı başlı başına bir deneyime dönüştürür. Ayrıntılar için <a href="/blog/sapancada-kahvalti-ve-yemek/">Sapanca'da kahvaltı ve yemek</a> rehberimize bakabilirsiniz.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="sabah">Sabah</button><button data-tab="ogle">Öğle</button><button data-tab="aksam">Akşam</button></div>
<div class="itin-panel on" data-tab="sabah"><p>Göl kenarında serpme kahvaltı ya da köy usulü Çerkez kahvaltısı. Bal-kaymak, sıcak gözleme ve demli çayla güne yavaş bir başlangıç yapın.</p></div>
<div class="itin-panel" data-tab="ogle"><p>Maşukiye vadisinde dere kenarında kiremitte alabalık ya da çarşıda tarihi ıslama köfte. Hafif bir öğle için iki klasik.</p></div>
<div class="itin-panel" data-tab="aksam"><p>Akşamı göl havasında, taze deniz ürünleri ve Akdeniz mutfağıyla otel bahçesindeki <a href="/#mare">Mare Gastro</a>'da tamamlayın.</p></div>
</div>
<h2>Sapanca'da öne çıkan yeme-içme adresleri</h2>
<p>Bölgede uzun yıllardır bilinen ve yöresel lezzetleriyle öne çıkan bazı adresler:</p>
<table><thead><tr><th>Mekan</th><th>Öne çıkan</th></tr></thead><tbody>
<tr><td>Fitos Cafe</td><td>Ev yapımı mantı, samimi atmosfer</td></tr>
<tr><td>Çiftlik Restoran</td><td>Çerkez kahvaltısı, ızgara et ve alabalık</td></tr>
<tr><td>İstanbuldere Alabalık Evi</td><td>Göletler arasında, doğal ortamda taze alabalık</td></tr>
<tr><td>Eker Lokantası</td><td>1976'dan beri esnaf lokantası; ıslama köfte ve günlük sulu yemekler</td></tr>
</tbody></table>
<p>Bu adresler bölgenin lezzet kültürünü keşfetmek için güzel duraklardır; menü ve çalışma saatleri zamanla değişebileceğinden gitmeden önce teyit etmenizi öneririz.</p>
<h2>Otelde göl manzaralı akşam yemeği: Mare Gastro</h2>
<p>Gün boyu gezdikten sonra dışarı çıkmadan zarif bir akşam yemeği isteyenler için, otel bahçesindeki <a href="/#mare"><strong>Mare Gastro</strong></a> öne çıkar. Taze deniz ürünleri ve Akdeniz mutfağını göl havasında, havuz kenarındaki masalarda sunar. <a href="/blog/sapancada-romantik-hafta-sonu/">Romantik bir akşam</a> ya da özel bir kutlama için ideal bir ortamdır. Yer ayırtmak için <a href="https://wa.me/905331350888?text=Mare%20Gastro%27da%20yer%20ay%C4%B1rtmak%20istiyorum.">WhatsApp'tan</a> ulaşabilirsiniz.</p>
<h2>Tatmadan dönmeyin: lezzet kontrol listesi</h2>
<p>Aşağıdaki listeden tattıklarınızı işaretleyin — seçimleriniz tarayıcınızda kaydedilir.</p>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="ne-yenir">
<label><input type="checkbox"><span><b>Kiremitte alabalık</b><span>Maşukiye vadisinde dere kenarında.</span></span></label>
<label><input type="checkbox"><span><b>Islama köfte</b><span>Sapanca/Adapazarı'nın tarihi lezzeti.</span></span></label>
<label><input type="checkbox"><span><b>Çerkez tavuğu ve isli peynir</b><span>Kafkas mutfağının imzası.</span></span></label>
<label><input type="checkbox"><span><b>Göl manzaralı serpme kahvaltı</b><span>Güne yavaş bir başlangıç.</span></span></label>
<label><input type="checkbox"><span><b>Mare Gastro'da akşam yemeği</b><span>Deniz ürünleri, göl havası.</span></span></label>
<label><input type="checkbox"><span><b>Yöresel reçel ve köy ürünleri</b><span>Mahmudiye pazarından.</span></span></label>
</div>
<p>Nerede kalacağınıza karar verirken lezzet de önemliyse, göl kıyısındaki konumu ve kendi restoranıyla <a href="/#konum">DİDİ Otel Sapanca</a> gezinizi hem doğa hem sofra açısından merkeze alır.</p>
""",
 "extra_ld":{"@context":"https://schema.org","@type":"ItemList","name":"Sapanca'da yöresel lezzetler","itemListElement":[
   {"@type":"ListItem","position":1,"item":{"@type":"Thing","name":"Kiremitte alabalık","description":"Maşukiye vadisinde tereyağıyla kiremit üzerinde pişirilen taze alabalık."}},
   {"@type":"ListItem","position":2,"item":{"@type":"Thing","name":"Islama köfte","description":"Adapazarı'nın 1900'lerden gelen, özel soslu ekmekle servis edilen köfte klasiği."}},
   {"@type":"ListItem","position":3,"item":{"@type":"Thing","name":"Çerkez tavuğu","description":"Kafkas mutfağından cevizli soğuk tavuk mezesi."}},
   {"@type":"ListItem","position":4,"item":{"@type":"Thing","name":"İsli peynir","description":"Çerkez mutfağının tütsülenmiş özel peyniri."}},
   {"@type":"ListItem","position":5,"item":{"@type":"Thing","name":"Serpme kahvaltı","description":"Göl manzarası eşliğinde köy peyniri, reçeller ve sıcak hamur işleriyle zengin kahvaltı."}}
 ]},
 "faq":[("Sapanca'nın meşhur yemeği nedir?","Sapanca denince akla ilk kiremitte alabalık gelir. Ayrıca Adapazarı ıslama köftesi, Çerkez tavuğu ve isli peynir gibi Kafkas lezzetleri bölgenin öne çıkan tatlarıdır."),
        ("Islama köfte nedir?","Özel sosuna batırılmış ekmekle servis edilen, Adapazarı yöresine ait ve 1900'lerden gelen bir köfte çeşididir."),
        ("Sapanca'da alabalık nerede yenir?","Alabalık en lezzetli haliyle Maşukiye vadisindeki dere kenarı tesislerinde, kiremitte pişirilerek servis edilir."),
        ("Sapanca'da kahvaltı nerede yapılır?","Göl kenarındaki mekanlarda serpme kahvaltı ya da köy usulü Çerkez kahvaltısı tercih edilir; konaklayanlar için DİDİ Otel'de göl havasında serpme kahvaltı sunulur."),
        ("Sapanca'da akşam yemeği için nereyi önerirsiniz?","Otel bahçesindeki Mare Gastro, taze deniz ürünleri ve Akdeniz mutfağını göl havasında sunar; gün boyu gezdikten sonra dışarı çıkmadan zarif bir akşam yemeği için idealdir."),
        ("Sapanca'da vejetaryen seçenek bulunur mu?","Evet. Çerkez mutfağının cevizli fasulye, barbunya ezmesi, karalahana ve turşu gibi zengin sebze mezeleri ile kahvaltı sofraları vejetaryenler için bol seçenek sunar."),
        ("Mare Gastro nedir?","DİDİ Otel Sapanca bahçesinde yer alan, taze deniz ürünleri ve Akdeniz mutfağı sunan göl manzaralı restorandır.")],
},
{
 "slug":"sapanca-evlilik-teklifi-organizasyon","cat":"Özel Günler","img":"havuz-loca","date":"2026-08-26",
 "title":"Sapanca'da Evlilik Teklifi ve Özel Gün Organizasyonu",
 "desc":"Sapanca'da evlilik teklifi, yıldönümü ve doğum günü için göl manzaralı fikirler. Mare Gastro'da rezervasyonda belirtilirse pasta, mum ışığı ve masa süslemesi gibi özel gün dokunuşları.",
 "lead":"Sapanca, İstanbul'a yaklaşık 1,5 saat mesafede; göl ve orman manzarasıyla evlilik teklifi ve özel kutlamalar için en romantik adreslerden biridir. Gün batımında göl kıyısı, sessiz bir bahçe köşesi ya da <a href=\"/#mare\">Mare Gastro</a>'da göl havasında özel bir masa, unutulmaz bir an için doğal bir sahne sunar. Mare Gastro'da <strong>rezervasyonunuz sırasında belirtmeniz halinde</strong> pasta, mum ışığı ve masa süslemesi gibi özel gün dokunuşları hazırlanabilir.",
 "body":"""
<h2>Neden Sapanca'da evlilik teklifi?</h2>
<p>Sapanca'yı özel anlar için ideal kılan üç şey var: İstanbul ve çevresine <a href="/blog/sapancaya-nasil-gidilir/">yakınlığı</a>, göl ve orman manzarasının sunduğu doğal romantizm ve dört mevsim değişen atmosferi. Kalabalık bir salona gerek kalmadan, doğanın içinde samimi ve zarif bir kutlama kurmak mümkündür.</p>
<h2>Nerede teklif edilir? En romantik köşeler</h2>
<p>Göl kıyısında <strong>gün batımı</strong>, otel bahçesinde sessiz bir köşe ya da havuz kenarındaki loca; her biri teklif anı için farklı bir hava sunar. <a href="/blog/sapancada-fotograf-gun-batimi-noktalari/">Gün batımı ve fotoğraf noktaları</a> rehberimiz, anı ölümsüzleştirmek için en iyi ışığı yakalamanıza yardımcı olur.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="teklif">Evlilik teklifi</button><button data-tab="yildonumu">Yıldönümü</button><button data-tab="dogumgunu">Doğum günü</button></div>
<div class="itin-panel on" data-tab="teklif"><p>Gün batımında göl kıyısı ya da Mare Gastro'da göl havasında baş başa bir akşam yemeği. Rezervasyonunuzda belirtirseniz masaya pasta, mum ışığı ve süsleme dokunuşu eklenebilir.</p></div>
<div class="itin-panel" data-tab="yildonumu"><p>Göl kıyısında bir yürüyüş ve Mare Gastro'da özel bir akşam yemeği; pasta ve mum ışığıyla yıl dönümünüze zarif bir dokunuş katın.</p></div>
<div class="itin-panel" data-tab="dogumgunu"><p>Mare Gastro'da göl havasında bir doğum günü sofrası; önceden belirtmeniz halinde pasta ve masa süslemesi hazırlanabilir.</p></div>
</div>
<h2>Mare Gastro'da özel gün dokunuşları</h2>
<p>Özel gününüzü unutulmaz kılmak için <a href="/#mare">Mare Gastro</a>'da <strong>rezervasyonunuz sırasında belirtmeniz halinde</strong> pasta, mum ışığı ve masa süslemesi gibi özel gün dokunuşları hazırlanabilir. Böylece göl havasında, hazırlığı sizin yerinize yapılmış zarif bir kutlama masası sizi bekler.</p>
<p>Talebinizi önceden iletmeniz, hazırlığın eksiksiz yapılabilmesi için önemlidir. Tarih ayırtmak ve dokunuşları belirtmek için Mare Gastro rezervasyonunuz sırasında ya da <a href="https://wa.me/905331350888?text=Mare%20Gastro%27da%20%C3%B6zel%20g%C3%BCn%20i%C3%A7in%20rezervasyon%20yapmak%20istiyorum.">WhatsApp'tan</a> bize iletebilirsiniz.</p>
<h2>Kusursuz bir sürpriz için hatırlatma listesi</h2>
<p>Planınızı netleştirmek için aşağıdaki adımları işaretleyin — seçimleriniz tarayıcınızda kaydedilir.</p>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/6</b></div>
<div class="spot-check" data-key="evlilik-teklifi">
<label><input type="checkbox"><span><b>Tarih ve saati belirleyin</b><span>Gün batımı saatleri en romantik ışığı verir.</span></span></label>
<label><input type="checkbox"><span><b>Mekanı seçin</b><span>Göl kıyısı, bahçe köşesi ya da havuz locası.</span></span></label>
<label><input type="checkbox"><span><b>Pasta, mum ve süsleme</b><span>Mare rezervasyonunda belirtin, masaya hazırlansın.</span></span></label>
<label><input type="checkbox"><span><b>Özel bir akşam yemeği</b><span>Mare Gastro'da göl havasında baş başa.</span></span></label>
<label><input type="checkbox"><span><b>Fotoğraf/an kaydı</b><span>Anı yakalayacak bir plan yapın.</span></span></label>
<label><input type="checkbox"><span><b>Konaklamayı ayırtın</b><span>Özel gecenizi otelde tamamlayın.</span></span></label>
</div>
<h2>En iyi zaman ve mevsim</h2>
<p>Göl kıyısı teklifleri için en etkileyici an, gün batımından yaklaşık bir saat öncesidir. Mevsim olarak sonbaharın altın rengi ve ilkbaharın yeşili öne çıkar; ayrıntılar için <a href="/blog/sapanca-hangi-mevsim-gidilir/">Sapanca hangi mevsim gidilir</a> yazımıza bakabilirsiniz. Balayı planlayanlar ise <a href="/blog/sapancada-balayi-ozel-gunler/">balayı rehberimizden</a> ilham alabilir.</p>
<p>Doğanın içinde, göl kıyısında özel bir an için <a href="/#konum">DİDİ Otel Sapanca</a> size sakin ve zarif bir sahne sunar.</p>
""",
 "faq":[("Sapanca'da özel gün için düzenleme yapıyor musunuz?","Evet. Mare Gastro'da rezervasyonunuz sırasında belirtmeniz halinde pasta, mum ışığı ve masa süslemesi gibi özel gün dokunuşları hazırlanabilir."),
        ("Ne kadar önceden haber vermeliyim?","Pasta ve süsleme hazırlığının eksiksiz yapılabilmesi için talebinizi mümkün olduğunca erken, rezervasyonunuz sırasında iletmeniz idealdir."),
        ("Teklif için en romantik nokta neresi?","Göl kıyısında gün batımı, otel bahçesindeki sessiz köşeler ve havuz kenarındaki loca en çok tercih edilen noktalardır."),
        ("Evlilik teklifi için en iyi saat hangisi?","Gün batımından yaklaşık bir saat önce; altın saat ışığı hem atmosfer hem fotoğraf için en güzel anı sunar."),
        ("Yıldönümü ve doğum günü kutlaması da yapılıyor mu?","Evet, evlilik teklifinin yanı sıra yıldönümü, doğum günü ve sürpriz kutlamalar da kişiye özel olarak düzenlenebilir."),
        ("Kutlama sonrası konaklama mümkün mü?","Elbette; özel gününüzü göl manzaralı bir odada konaklayarak tamamlayabilirsiniz.")],
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
        ("Kahvaltı konaklamaya dahil mi?","DİDİ Otel'de göl havasında serpme kahvaltı sunulur; güncel koşullar için rezervasyon sırasında teyit alabilirsiniz."),
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
 "slug":"sapanca-mi-abant-mi-bolu-mu","cat":"Karşılaştırma","img":"otel-havuz","date":"2026-08-26",
 "title":"Sapanca mı Abant mı Bolu mu? Hafta Sonu Kaçamağı Karşılaştırması",
 "desc":"Sapanca mı Abant mı Bolu mu? İstanbul'a mesafe, en iyi mevsim ve kime uygun olduğu karşılaştırmalı. En yakın doğa kaçamağı Sapanca; uzun tatil için Abant ve Bolu.",
 "lead":"Sapanca mı Abant mı Bolu mu sorusunun kısa cevabı: İstanbul'a en yakın ve dört mevsim erişilebilir seçenek <strong>Sapanca</strong>'dır (yaklaşık 1,5–2 saat). <strong>Abant</strong> ve <strong>Bolu</strong> daha uzaktır (yaklaşık 3,5–4 saat) ve özellikle sonbaharda öne çıkar. Günübirlik ya da kısa bir hafta sonu için Sapanca; daha uzun, planlı bir tatil için Abant veya Bolu mantıklıdır.",
 "body":"""
<h2>Bir bakışta karşılaştırma</h2>
<p>Üç destinasyon da doğayla iç içe kaçamaklar sunar; ama mesafe, mevsim ve tempo farklıdır. Aşağıdaki tablo, hangisinin size uygun olduğunu hızlıca görmenizi sağlar.</p>
<table><thead><tr><th>Destinasyon</th><th>İstanbul'dan</th><th>Öne çıkan</th><th>Kime uygun</th></tr></thead><tbody>
<tr><td>Sapanca</td><td>~1,5–2 saat (~135 km)</td><td>Göl, Maşukiye, teleferik, dört mevsim</td><td>Kısa kaçamak, çiftler, aileler</td></tr>
<tr><td>Abant</td><td>~4 saat (~227 km)</td><td>Göl, sonbahar renkleri, at arabası</td><td>Uzun hafta sonu, doğa yürüyüşü</td></tr>
<tr><td>Bolu (Gölcük/Yedigöller)</td><td>~3,5 saat</td><td>Tabiat parkları, orman rotaları</td><td>Doğa ve kamp tutkunları</td></tr>
</tbody></table>
<h2>Sapanca: İstanbul'a en yakın doğa</h2>
<p>Sapanca'nın en büyük avantajı erişimidir: otoyol ya da <a href="/blog/sapancaya-nasil-gidilir/">trenle</a> kısa sürede ulaşılır, hatta yarım günlük bir kaçamağa bile imkan tanır. Göl kıyısı, <a href="/blog/masukiye-kartepe-gezi/">Maşukiye şelaleleri</a>, <a href="/blog/sapanca-teleferik-rehberi/">teleferik</a> ve Kartepe ile dört mevsim keşif sunar. Ayrıntılar için <a href="/blog/sapancada-gezilecek-yerler/">Sapanca'da gezilecek yerler</a> rehberimize bakın.</p>
<h2>Abant: sonbaharın başkenti</h2>
<p>Abant Gölü, özellikle sonbaharda sarı-turuncu yapraklarıyla görsel bir şölen sunar. Göl çevresinde yürüyüş, bisiklet ve at arabası turları popülerdir; ancak İstanbul'a yaklaşık 4 saat mesafede olduğu için en az bir gece konaklama gerektirir.</p>
<h2>Bolu: orman ve tabiat parkları</h2>
<p>Bolu; Gölcük Tabiat Parkı ve Yedigöller gibi orman içi rotalarıyla doğa ve kamp tutkunlarına hitap eder. Bolu merkeze yaklaşık 13 km mesafedeki Gölcük her mevsim farklı bir güzellik sunar; yine de İstanbul'dan uzaklığı Sapanca'ya göre daha fazladır.</p>
<div class="itin-wrap rev">
<div class="itin-tabs"><button class="on" data-tab="kisa">Kısa hafta sonu</button><button data-tab="uzun">Uzun tatil</button><button data-tab="sonbahar">Sonbahar</button></div>
<div class="itin-panel on" data-tab="kisa"><p>Bir gece ya da günübirlik plan yapıyorsanız, İstanbul'a yakınlığıyla Sapanca açık ara en pratik seçenektir; yolda geçen zamanı doğada geçirirsiniz.</p></div>
<div class="itin-panel" data-tab="uzun"><p>2–3 gecelik daha yavaş bir tatil planlıyorsanız Abant ya da Bolu'nun orman rotaları da değerlendirilebilir; uzun yol bu durumda anlam kazanır.</p></div>
<div class="itin-panel" data-tab="sonbahar"><p>Sonbahar renkleri Abant'ta zirve yapar; ancak Sapanca'da da göl çevresi ve Maşukiye sonbaharda oldukça etkileyicidir ve çok daha yakındır.</p></div>
</div>
<h2>Neden çoğu gezgin Sapanca'yı seçiyor?</h2>
<p>Kısa sürede ulaşılması, dört mevsim açık olması, göl + dağ + şelale çeşitliliğini bir arada sunması ve konaklama seçeneklerinin bolluğu Sapanca'yı özellikle İstanbul çevresi için en pratik doğa kaçamağı yapar. Göl kıyısında konaklamak isteyenler için <a href="/#konum">DİDİ Otel Sapanca</a>, <a href="/blog/sapancada-havuzlu-otel/">klorsuz havuzu</a> ve <a href="/#mare">Mare Gastro</a> restoranıyla sakin bir merkez sunar. Nerede kalacağınıza karar verirken <a href="/blog/sapanca-nerede-kalinir-bolge-rehberi/">bölge rehberimize</a> de bakabilirsiniz.</p>
<h2>Karar verirken kontrol listesi</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="karsilastirma">
<label><input type="checkbox"><span><b>Ne kadar yolculuk kabulüm var?</b><span>Kısa yol için Sapanca öne çıkar.</span></span></label>
<label><input type="checkbox"><span><b>Kaç gece kalacağım?</b><span>Bir gece için Sapanca, uzun tatil için Abant/Bolu.</span></span></label>
<label><input type="checkbox"><span><b>Hangi mevsim gidiyorum?</b><span>Sonbahar Abant'ta zirve; Sapanca dört mevsim.</span></span></label>
<label><input type="checkbox"><span><b>Göl mü orman mı istiyorum?</b><span>Sapanca göl + dağ; Bolu orman.</span></span></label>
<label><input type="checkbox"><span><b>Aktivite çeşitliliği önemli mi?</b><span>Sapanca teleferik, şelale, kayak bir arada.</span></span></label>
</div>
""",
 "faq":[("Sapanca mı Abant mı daha iyi?","İstanbul'a yakınlık ve dört mevsim erişim istiyorsanız Sapanca (~1,5–2 saat) daha avantajlıdır. Sonbahar renkleri ve daha uzun, sakin bir tatil önceliğinizse Abant (~4 saat) tercih edilebilir."),
        ("İstanbul'a en yakın doğa kaçamağı hangisi?","Üç destinasyon arasında İstanbul'a en yakın olan Sapanca'dır; yaklaşık 135 km ve 1,5–2 saat mesafededir."),
        ("Kışın hangisi daha iyi?","Kar ve kayak isteyenler için Sapanca'ya 30 dakika mesafedeki Kartepe güçlü bir seçenektir; Bolu ve Abant da karlı manzaralar sunar ancak daha uzaktır."),
        ("Çiftler için hangisi uygun?","Sapanca, göl kıyısı, teleferik ve butik konaklamalarıyla kısa romantik kaçamaklar için çok elverişlidir; Abant da sonbaharda romantik bir seçenektir."),
        ("Sapanca'nın en büyük avantajı nedir?","Kısa sürede ulaşılması, dört mevsim açık olması ve göl, şelale, teleferik ile dağ aktivitelerini bir arada sunmasıdır.")],
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
<div class="tl-step"><div class="tl-time">09:00</div><h4>DİDİ Otel'de serpme kahvaltı</h4><p>Güne göl manzarasına karşı zengin bir kahvaltıyla başlayın.</p></div>
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
 "slug":"kuzuluk-kaplicalari-rehberi","cat":"Termal","img":"havuz1","date":"2026-08-26",
 "title":"Kuzuluk Kaplıcaları: Termal ve Şifa Rehberi",
 "desc":"Kuzuluk kaplıcaları rehberi: Sapanca yakınında şifalı termal sular, wellness ve dinlenme. Sapanca gezisine termal mola eklemek isteyenler için konum, öneriler ve konaklama.",
 "lead":"Kuzuluk kaplıcaları, şifalı termal sularıyla yüzyıllardır bilinen, Sapanca'ya yaklaşık 45 dakika mesafedeki bir wellness durağıdır. Doğa gezisine dinlendirici bir termal mola eklemek, özellikle sonbahar ve kış aylarında bölgenin en keyifli deneyimlerinden biridir.",
 "body":"""
<h2>Kuzuluk kaplıcaları nedir?</h2>
<p>Sakarya'nın Akyazı ilçesine bağlı <strong>Kuzuluk</strong>, mineralce zengin termal sularıyla bilinen bir kaplıca bölgesidir. Şifalı olduğuna inanılan sıcak suları, stresi atmak ve dinlenmek isteyenler için yüzyıllardır tercih edilir. Bölgedeki termal tesisler, kür ve dinlenme odaklı bir wellness deneyimi sunar.</p>
<h2>Kimler için ideal?</h2>
<p>Yoğun bir tempodan uzaklaşmak, doğa gezisini bir wellness molasıyla dengelemek isteyenler için Kuzuluk ideal bir duraktır. Özellikle <a href="/blog/sapancada-kisin-gezilecek-yerler/">kış aylarında</a> soğuk havada sıcak termal sular ayrı bir keyif verir. Çiftler için de <a href="/blog/sapancada-romantik-hafta-sonu/">romantik bir hafta sonuna</a> dinlendirici bir dokunuş ekler.</p>
<h2>Sapanca gezisine nasıl eklenir?</h2>
<p>Kuzuluk, Sapanca'ya yaklaşık 45 dakika mesafededir ve günübirlik rahatça ziyaret edilebilir. Göl kıyısında konaklayıp gündüz termal bir mola vermek, iki farklı deneyimi tek bir tatilde birleştirmenin pratik yoludur. Rota planı için <a href="/blog/sapanca-3-gun-uzun-hafta-sonu-plani/">3 günlük gezi planımıza</a> bakabilirsiniz.</p>
<h2>Termal mola için ipuçları</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="kuzuluk">
<label><input type="checkbox"><span><b>Mayo ve havlu</b><span>Termal havuzlar için hazırlıklı olun.</span></span></label>
<label><input type="checkbox"><span><b>Bol su için</b><span>Termal sonrası vücut su kaybeder.</span></span></label>
<label><input type="checkbox"><span><b>Süreyi abartmayın</b><span>Sıcak suda uzun kalmaktan kaçının.</span></span></label>
<label><input type="checkbox"><span><b>Sağlık durumunuzu değerlendirin</b><span>Gerekirse hekiminize danışın.</span></span></label>
<label><input type="checkbox"><span><b>Dönüş için dinlenme</b><span>Termal sonrası biraz dinlenerek yola çıkın.</span></span></label>
</div>
<p>Termalin ardından göl kıyısındaki <a href="/#konum">DİDİ Otel Sapanca</a>'da dinlenip günü <a href="/#mare">Mare Gastro</a>'da tamamlayabilirsiniz. Bölgedeki diğer doğa duraklarını <a href="/blog/sapancada-gezilecek-yerler/">gezilecek yerler</a> rehberimizde bulabilirsiniz.</p>
""",
 "faq":[("Kuzuluk kaplıcaları nerede?","Sakarya'nın Akyazı ilçesine bağlı Kuzuluk'ta, Sapanca'ya yaklaşık 45 dakika mesafededir."),
        ("Kuzuluk kaplıcaları neye iyi gelir?","Mineralce zengin termal sularının dinlendirici ve rahatlatıcı olduğuna inanılır; kesin sağlık bilgisi için hekiminize danışmanız önerilir."),
        ("Kuzuluk Sapanca'dan günübirlik gezilir mi?","Evet, yaklaşık 45 dakika mesafede olduğu için göl kıyısında konaklayıp gündüz termal bir mola vermek mümkündür."),
        ("Termal için en iyi mevsim hangisi?","Sonbahar ve kış aylarında soğuk havada sıcak termal sular ayrı bir keyif verir; ancak dört mevsim ziyaret edilebilir.")],
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
 "slug":"istanbuldan-trenle-sapanca","cat":"Ulaşım","img":"dis-cephe","date":"2026-08-26",
 "title":"İstanbul'dan Sapanca'ya Trenle ve Araçsız Ulaşım",
 "desc":"İstanbul'dan Sapanca'ya trenle nasıl gidilir? YHT, Ada Ekspresi ve Marmaray ile araçsız ulaşım seçenekleri, süreler ve istasyondan transfer önerileri.",
 "lead":"İstanbul'dan Sapanca'ya araçsız ulaşmanın en pratik yolu trendir. Pendik veya Söğütlüçeşme'den kalkan Yüksek Hızlı Tren (YHT) ile yaklaşık 1,5 saatte, Gebze aktarmalı Ada Ekspresi ile daha ekonomik biçimde Sapanca'ya ulaşabilirsiniz. Sapanca garı merkeze çok yakındır; oradan kısa bir transferle göl kıyısı mahallelerine geçilir.",
 "body":"""
<h2>Trenle Sapanca: seçenekler</h2>
<p>İstanbul'dan Sapanca'ya trenle iki ana yol vardır. En hızlısı, Pendik veya Söğütlüçeşme istasyonlarından kalkan <strong>Yüksek Hızlı Tren (YHT)</strong> ile yaklaşık 1,5 saatlik yolculuktur. Daha ekonomik seçenek ise Marmaray ile Gebze'ye geçip oradan <strong>Ada Ekspresi</strong> bölgesel trenine binmektir.</p>
<h3>Ulaşım seçenekleri özeti</h3>
<table><thead><tr><th>Seçenek</th><th>Güzergah</th><th>Yaklaşık süre</th></tr></thead><tbody>
<tr><td>YHT</td><td>Pendik / Söğütlüçeşme → Sapanca</td><td>~1,5 saat</td></tr>
<tr><td>Ada Ekspresi</td><td>Gebze → Sapanca (Marmaray aktarmalı)</td><td>Ekonomik, aktarmalı</td></tr>
<tr><td>Otobüs / özel araç</td><td>TEM otoyolu</td><td>~1,5–2 saat</td></tr>
</tbody></table>
<h2>Ada Ekspresi ile ekonomik yol</h2>
<p>Ada Ekspresi, Pendik–Adapazarı arasında Sapanca dahil birçok durakta hizmet verir ve gün içinde karşılıklı seferler yapar. Bilet fiyatları oldukça uygundur; bu nedenle özellikle günübirlik ve bütçe dostu geziler için tercih edilir. Güncel sefer saatlerini yolculuktan önce kontrol etmeniz önerilir.</p>
<h2>Sapanca garından sonra</h2>
<p>Sapanca tren garı ilçe merkezine çok yakındır; garın çıkışından kısa bir taksi ya da transferle göl kıyısına ve <a href="/blog/sapanca-nerede-kalinir-bolge-rehberi/">Kırkpınar gibi göl kıyısı mahallelerine</a> ulaşabilirsiniz. Araçsız gelenler için konaklama yerinin transfer sunup sunmadığını sormak pratiktir. Ulaşımın tüm ayrıntıları için <a href="/blog/sapancaya-nasil-gidilir/">Sapanca'ya nasıl gidilir</a> rehberimize bakabilirsiniz.</p>
<h2>Araçsız gezi ipuçları</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="trenle-sapanca">
<label><input type="checkbox"><span><b>Bilet ve sefer saatini kontrol edin</b><span>YHT ve Ada Ekspresi saatlerini önceden bakın.</span></span></label>
<label><input type="checkbox"><span><b>Marmaray aktarmasını planlayın</b><span>Gebze bağlantısını hesaba katın.</span></span></label>
<label><input type="checkbox"><span><b>Gardan transfer</b><span>Taksi ya da otel transferini ayarlayın.</span></span></label>
<label><input type="checkbox"><span><b>Hafif bagaj</b><span>Aktarmalı yolculukta pratiklik sağlar.</span></span></label>
<label><input type="checkbox"><span><b>Dönüş saatini not edin</b><span>Son sefer saatini kaçırmayın.</span></span></label>
</div>
<p>Göl kıyısına yakın konaklamak araçsız gezginler için avantajlıdır; <a href="/#konum">DİDİ Otel Sapanca</a> göl kıyısındaki Kırkpınar'da yer alır. Ulaşım ve transfer için <a href="https://wa.me/905331350888?text=Sapanca%27ya%20araçs%C4%B1z%20ula%C5%9F%C4%B1m%20ve%20transfer%20hakk%C4%B1nda%20bilgi%20almak%20istiyorum.">WhatsApp'tan</a> bilgi alabilirsiniz.</p>
""",
 "faq":[("İstanbul'dan Sapanca'ya trenle nasıl gidilir?","Pendik veya Söğütlüçeşme'den YHT ile yaklaşık 1,5 saatte; alternatif olarak Marmaray ile Gebze'ye geçip Ada Ekspresi ile Sapanca'ya ulaşılır."),
        ("Sapanca'ya araçsız gidilebilir mi?","Evet. Tren (YHT ve Ada Ekspresi) araçsız ulaşım için pratik ve ekonomik seçeneklerdir; gardan kısa bir transferle göl kıyısına geçilir."),
        ("Sapanca tren garı merkeze yakın mı?","Evet, gar ilçe merkezine çok yakındır; kısa bir taksi ya da transferle göl kıyısı mahallelerine ulaşılır."),
        ("Ada Ekspresi nedir?","Pendik–Adapazarı arasında Sapanca dahil birçok durakta hizmet veren, uygun fiyatlı bölgesel tren hattıdır."),
        ("YHT ile Sapanca ne kadar sürer?","Pendik veya Söğütlüçeşme'den yaklaşık 1,5 saat sürer.")],
},
{
 "slug":"sapanca-macera-parki-zipline","cat":"Aktivite","img":"ONN09440","date":"2026-08-26",
 "title":"Sapanca Macera Parkı, Zipline ve Adrenalin Aktiviteleri",
 "desc":"Sapanca ve Maşukiye'de macera parkı, zipline, dev salıncak ve ip parkuru gibi adrenalin aktiviteleri. Aileler ve gençler için heyecanlı bir gün rehberi.",
 "lead":"Sapanca ve Maşukiye çevresi, zipline, dev salıncak, tırmanma duvarı ve ip parkurlarıyla adrenalin arayanlar için zengin bir açık hava sahasıdır. Farklı zorluk seviyeleri sayesinde hem çocuklar hem de yetişkinler için uygun aktiviteler bulunur; doğa gezisine heyecan katmak isteyen aileler ve gençler için ideal bir gündür.",
 "body":"""
<h2>Sapanca'da macera aktiviteleri</h2>
<p>Sapanca ve <a href="/blog/masukiye-kartepe-gezi/">Maşukiye</a> sınırındaki macera parklarında <strong>zipline</strong>, <strong>dev salıncak</strong>, <strong>tırmanma duvarı</strong>, ip parkurları ve zaman zaman paintball ile çim kayağı gibi aktiviteler sunulur. Ormanın içinde, farklı zorluk seviyelerinde kurulan parkurlar her yaş grubuna hitap eder.</p>
<h2>Zipline ve dev salıncak</h2>
<p>Bölgenin en popüler aktivitesi, ağaçların ve vadinin üzerinden geçen <strong>zipline</strong> hatlarıdır. Yüksekten hız ve manzarayı bir arada yaşatan bu deneyim, dev salıncak ile birlikte adrenalin sevenlerin favorisidir. Güvenlik ekipmanları ve rehber eşliğinde yapıldığı için ilk kez deneyenler için de uygundur.</p>
<h2>Ailece ve gençlerle</h2>
<p>Macera parkları, çocuklar için daha alçak ve güvenli parkurlar da sunduğundan ailecek keyifli bir gün geçirmek mümkündür. Doğa yürüyüşü ve piknikle birleştirildiğinde tam günlük bir program çıkar. Çocuklu aileler için diğer öneriler <a href="/blog/ailecek-sapanca-tatili/">ailecek Sapanca tatili</a> rehberimizde yer alır.</p>
<h2>Gitmeden önce</h2>
<div class="spot-progress rev"><span>İlerleme</span><div class="track"><i></i></div><b>0/5</b></div>
<div class="spot-check" data-key="macera-parki">
<label><input type="checkbox"><span><b>Rahat ve kapalı ayakkabı</b><span>Parkurlar için gereklidir.</span></span></label>
<label><input type="checkbox"><span><b>Yaş ve boy sınırlarını sorun</b><span>Bazı aktivitelerde sınır olabilir.</span></span></label>
<label><input type="checkbox"><span><b>Güvenlik brifingine katılın</b><span>Rehber yönergelerini dinleyin.</span></span></label>
<label><input type="checkbox"><span><b>Su ve yedek kıyafet</b><span>Aktif bir gün için hazırlıklı olun.</span></span></label>
<label><input type="checkbox"><span><b>Rezervasyon / çalışma saati</b><span>Yoğun günlerde önceden teyit alın.</span></span></label>
</div>
<p>Heyecanlı bir günün ardından göl kıyısındaki <a href="/#konum">DİDİ Otel Sapanca</a>'da <a href="/blog/sapancada-havuzlu-otel/">klorsuz havuzda</a> dinlenip akşamı <a href="/#mare">Mare Gastro</a>'da tamamlayabilirsiniz. Bölgedeki diğer duraklar için <a href="/blog/sapancada-gezilecek-yerler/">gezilecek yerler</a> rehberimize bakın.</p>
""",
 "faq":[("Sapanca'da zipline var mı?","Evet, Sapanca ve Maşukiye çevresindeki macera parklarında zipline, dev salıncak ve ip parkuru gibi aktiviteler bulunur."),
        ("Macera parkları çocuklar için uygun mu?","Evet, birçok park çocuklar için daha alçak ve güvenli parkurlar sunar; yaş ve boy sınırlarını önceden sormak faydalıdır."),
        ("Zipline güvenli mi?","Aktiviteler güvenlik ekipmanları ve rehber eşliğinde yapılır; yönergelere uyulduğunda ilk kez deneyenler için de uygundur."),
        ("Macera aktiviteleri için ne giymeli?","Rahat, kapalı ayakkabı ve hareket ettiren kıyafetler önerilir; yanınıza su ve yedek kıyafet almanız iyi olur.")],
},
]

def slug_url(s): return f"{SITE}/blog/{s}/"

def article_ld(p):
    return {"@context":"https://schema.org","@type":"Article",
      "headline":p["title"],"description":p["desc"],
      "image":f"{SITE}{IMG}/{p['img']}-1280.webp",
      "datePublished":p["date"],"dateModified":p["date"],
      "author":{"@type":"Organization","name":"DİDİ Otel Sapanca"},
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
    return (f'<picture><source type="image/avif" srcset="{b}-800.avif 800w,{b}-1280.avif 1280w,{b}-1920.avif 1920w" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{b}-800.webp 800w,{b}-1280.webp 1280w,{b}-1920.webp 1920w" sizes="{sizes}">'
            f'<img src="{b}.jpg" {lo} width="1280" height="720" alt="{alt}" class="{cls}"></picture>')

def read_time(p):
    words=len(p["lead"].split())+len(p["body"].split())
    return max(3, round(words/180))

def fmt_date(d):
    y,m,day=d.split("-"); months=["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    return f"{int(day)} {months[int(m)-1]} {y}"

def build_post(p, others):
    faq_html = "".join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q,a in p["faq"])
    rel = [x for x in others if x["slug"]!=p["slug"]][:3]
    rel_html = "".join(
      f'<a href="/blog/{o["slug"]}/" class="bcard"><div class="bcard-img">'+pic(o["img"],"33vw",alt=o["title"])+
      f'</div><div class="bcard-body"><div class="cat">{o["cat"]}</div><h3>{o["title"]}</h3></div></a>' for o in rel)
    schemas = [article_ld(p),crumb_ld(p),faq_ld(p)]
    if p.get("extra_ld"): schemas.append(p["extra_ld"])
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in schemas)
    page = f'''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
{GA}
<title>{p["title"]} | DİDİ Otel Sapanca</title>
<meta name="description" content="{html.escape(p["desc"])}">
<meta name="theme-color" content="#F5F1EA">
<link rel="canonical" href="{slug_url(p["slug"])}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(p["title"])}">
<meta property="og:description" content="{html.escape(p["desc"])}">
<meta property="og:url" content="{slug_url(p["slug"])}">
<meta property="og:image" content="{SITE}{IMG}/{p['img']}-1280.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/assets/brand/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
{lds}
<link rel="stylesheet" href="/css/site.css?v=10">
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
{pic(p["img"],"100vw",alt=p["title"],eager=True)}
<div class="art-hero-c">
<div class="cat">{p["cat"]}</div>
<h1>{p["title"]}</h1>
<div class="art-meta"><span>{fmt_date(p["date"])}</span><span>{read_time(p)} dk okuma</span><span>Sapanca</span></div>
</div>
</header>
<div class="article">
<div class="art-body">
<p class="lead-p">{p["lead"]}</p>
{p["body"]}
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
</body>
</html>'''
    outdir=f'{ROOT}/blog/{p["slug"]}'
    os.makedirs(outdir,exist_ok=True)
    open(f'{outdir}/index.html','w',encoding='utf-8').write(page)

def build_index():
    cards="".join(
      f'<a href="/blog/{p["slug"]}/" class="bcard rev"><div class="bcard-img">'+pic(p["img"],"(max-width:640px) 100vw,(max-width:960px) 50vw,33vw",alt=p["title"])+
      f'</div><div class="bcard-body"><div class="cat">{p["cat"]}</div><h3>{p["title"]}</h3><p>{p["desc"]}</p><span class="more">Devamını oku →</span></div></a>'
      for p in POSTS)
    ld={"@context":"https://schema.org","@type":"Blog","name":"DİDİ Otel Sapanca Blog","url":f"{SITE}/blog/",
        "description":"Sapanca gezi rehberi, konaklama önerileri ve yakın çevre rotaları.",
        "blogPost":[{"@type":"BlogPosting","headline":p["title"],"url":slug_url(p["slug"]),"datePublished":p["date"]} for p in POSTS]}
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
<link rel="stylesheet" href="/css/site.css?v=10">
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
