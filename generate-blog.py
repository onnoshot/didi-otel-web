#!/usr/bin/env python3
"""DİDİ Otel — blog üretici.
/blog/ index + /blog/<slug>/index.html üretir. Article + BreadcrumbList + FAQPage schema,
GEO/AEO uyumlu (answer-first, soru H2, tablo, iç linkler). Idempotent.
"""
import os, json, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://sapancadidiotel.com"
IMG = "/assets/web/editorial"

GA = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-C8D22FPDET"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-C8D22FPDET');
</script>'''

NAV = '''<nav class="nav scr-force" id="nav">
<a href="/" class="nav-logo" aria-label="DİDİ Otel Sapanca"><img class="logo-w" src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><img class="logo-n" src="/assets/brand/adidilogo-navy.png" alt="" aria-hidden="true"></a>
<div class="nav-links">
<a href="/#odalar">Odalar</a><a href="/#mare">Mare Gastro</a><a href="/#konum">Konum</a><a href="/blog/">Blog</a><a href="/#iletisim">İletişim</a>
</div>
<div class="nav-right">
<a href="tel:+902645921212" class="btn btn-line">0264 592 12 12</a>
<a href="https://sapancadidiotel.com/reservation/book" class="btn btn-fill">Rezervasyon</a>
<button class="burger" id="burger" aria-label="Menü"><span></span><span></span><span></span></button>
</div>
</nav>
<div class="mob" id="mob">
<a href="/#odalar">Odalar</a><a href="/#mare">Mare Gastro</a><a href="/#konum">Konum</a><a href="/blog/">Blog</a><a href="/#iletisim">İletişim</a>
<a href="https://sapancadidiotel.com/reservation/book" style="color:var(--green)">Rezervasyon Yap →</a>
</div>'''

FOOT = '''<footer class="foot"><div class="wrap">
<div class="foot-grid">
<div><img src="/assets/brand/adidilogo.png" alt="DİDİ Otel Sapanca"><p>Kırkpınar Sapanca'da göl ve dağ manzaralı butik konaklama. Konforlu ve unutulmaz bir deneyim için doğru adres.</p></div>
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
</script>'''

CTA = ('<div class="art-cta"><h3>Sapanca\'da doğanın içinde bir kaçış</h3>'
 '<p>DİDİ Otel Sapanca — Kırkpınar\'da göl ve dağ manzaralı butik konaklama.</p>'
 '<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">'
 '<a href="https://sapancadidiotel.com/reservation/book" class="btn btn-fill">Müsaitliği Gör</a>'
 '<a href="/#odalar" class="btn btn-line" style="border-color:rgba(255,255,255,.4);color:#fff">Odaları İncele</a></div></div>')

# ── POSTS ──
POSTS = [
{
 "slug":"sapancada-gezilecek-yerler","cat":"Gezi Rehberi","img":"otel-havuz","date":"2026-07-01",
 "title":"Sapanca'da Gezilecek Yerler: Göl, Maşukiye ve Kartepe Rehberi",
 "desc":"Sapanca'da gezilecek yerler; Sapanca Gölü, Uzunkum Parkı, Maşukiye şelalesi, Kartepe ve Poyrazlar Gölü. Doğa içinde bir hafta sonu için eksiksiz rehber.",
 "lead":"Sapanca'da gezilecek yerlerin başında Sapanca Gölü, Uzunkum Parkı, Maşukiye şelalesi, Poyrazlar Gölü ve Kartepe gelir. İstanbul'a yaklaşık 1,5 saat mesafedeki Sapanca, göl kıyısı yürüyüşlerinden dağ manzaralı doğa rotalarına kadar dört mevsim keşfedilecek bir destinasyondur.",
 "body":"""
<h2>Sapanca Gölü ve göl kıyısı</h2>
<p>Bölgenin kalbi <strong>Sapanca Gölü</strong>'dür. Göl çevresi yaklaşık 16 kilometre uzunluğundadır ve bisiklet turu, yürüyüş, tekne ve kano için idealdir. Göl kıyısındaki <strong>Uzunkum Parkı</strong>, ilçenin en güzel manzaralarına sahip dinlenme alanlarından biridir; gün batımında göl kenarında yürüyüş yapmak Sapanca'nın klasik deneyimlerindendir.</p>
<h2>Maşukiye ve şelaleler</h2>
<p>Sapanca'ya yaklaşık 20 dakika mesafedeki <strong>Maşukiye</strong>, yemyeşil doğası, şelaleleri ve alabalık tesisleriyle ünlüdür. Şelalenin su debisi ilkbaharda, karların erimesiyle en yüksek seviyeye ulaşır. Maşukiye ayrıca göl manzarasına çıkan <strong>Sapanca Teleferik</strong> hattına da yakındır.</p>
<h2>Kartepe Kayak Merkezi</h2>
<p>Samanlı Dağları'nın zirvesindeki <strong>Kartepe Kayak Merkezi</strong>, Sapanca'dan yaklaşık 30 dakika uzaklıktadır. Kışın kayak ve telesiyej ile Sapanca Gölü manzarası, yazın ise serin bir yayla havası sunar.</p>
<h2>Poyrazlar Gölü ve Mahmudiye</h2>
<p>Sapanca Gölü'nün yanındaki <strong>Poyrazlar Gölü</strong>, sessiz ve sakin atmosferiyle su kuşlarını ve doğayı gözlemlemek isteyenler için idealdir. Osmanlı döneminden kalma tarihî yapılara ev sahipliği yapan <strong>Mahmudiye köyü</strong> ise doğayla iç içe huzurlu bir moladır.</p>
<h3>Yakın çevre mesafeleri</h3>
<table><thead><tr><th>Yer</th><th>Sapanca'dan</th></tr></thead><tbody>
<tr><td>Sapanca Gölü / Uzunkum Parkı</td><td>~5 km</td></tr>
<tr><td>Maşukiye (şelale, alabalık)</td><td>~20 dk</td></tr>
<tr><td>Kartepe Kayak Merkezi</td><td>~30 dk</td></tr>
<tr><td>Poyrazlar Gölü</td><td>~15 dk</td></tr></tbody></table>
<p>Tüm bu noktalara kısa mesafede olan <a href="/#konum">DİDİ Otel Sapanca</a>, Kırkpınar'da göl ve dağ manzaralı konumuyla gezileriniz için ideal bir merkez olur.</p>
""",
 "faq":[("Sapanca'da mutlaka görülmesi gereken yer neresidir?","Sapanca Gölü ve göl kıyısındaki Uzunkum Parkı, ilçenin simgesidir. Ayrıca 20 dakika mesafedeki Maşukiye şelaleleri ve 30 dakikadaki Kartepe öne çıkar."),
        ("Sapanca'yı bir günde gezmek mümkün mü?","Göl kıyısı ve yakın çevre bir günde görülebilir; ancak Maşukiye ve Kartepe'yi de eklemek isteyenler için en az bir gece konaklama önerilir."),
        ("Sapanca hangi şehre yakındır?","Sapanca, İstanbul'a yaklaşık 1,5 saat, Sakarya merkeze ise 15 kilometre mesafededir.")],
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
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in [article_ld(p),crumb_ld(p),faq_ld(p)])
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
<link rel="icon" type="image/png" href="/assets/brand/adidilogo.png">
{lds}
<link rel="stylesheet" href="/css/site.css?v=5">
</head>
<body>
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
<link rel="icon" type="image/png" href="/assets/brand/adidilogo.png">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(crumb,ensure_ascii=False)}</script>
<link rel="stylesheet" href="/css/site.css?v=5">
</head>
<body>
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
