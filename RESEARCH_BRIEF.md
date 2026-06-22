# DİDİ Otel Sapanca — Yeni Web Sitesi · Araştırma & Görev Süreci

**Tarih:** 2026-06-22 · **Kaynak site:** https://sapancadidiotel.com
**Hedef:** Apple liquid-glass estetiğinde, scroll ile hareket eden video bölümleri olan,
otelin tüm olanaklarını/odalarını/konumunu detaylıca anlatan premium tek sayfa + alt sayfalar.
**Deploy:** static → GitHub → Vercel (mevcut pipeline ile aynı).

---

## 1. Otel Künyesi

| Alan | Bilgi |
|------|-------|
| Ad | DİDİ Otel Sapanca (Didi Butik Otel) |
| Konsept | Doğa içinde butik konaklama; geniş yeşil bahçe, göl + dağ manzarası |
| Konum | Kırkpınar Mevkii, Sapanca / Sakarya — Sapanca'nın en nezih bölgesi, göl kıyısına yakın |
| Mesafeler | Sapanca merkez 3 km · İstanbul-Ankara otoyolu Sapanca gişeleri 500 m · Sakarya merkez 15 km · Sabiha Gökçen Havalimanı 95 km |
| Slogan | "Sapanca'da Unutulmaz Bir Konaklama" |
| Diller | TR · EN · AR · DE · RU (5 dil — yeni sitede de korunmalı) |

### İletişim
- Sabit: **0264 592 12 12**
- Cep / WhatsApp: **+90 533 135 08 88** → `https://wa.me/905331350888`
- Adres: Kırkpınar Sapanca, Sakarya
- Yol tarifi: `google.com/maps/dir/?api=1&destination=Kırkpınar+Sapanca,+Sakarya`
- Bülten kaydı (e-posta) ve "En İyi Fiyat Garantisi" doğrudan rezervasyon vurgusu mevcut.

---

## 2. Odalar (5 tip)

| Oda | Kapasite | Gecelik | İndirilen foto | Slug |
|-----|----------|---------|----------------|------|
| KING SUIT ODA | 2 kişi | 12.000 ₺ | 19 | `king-suit` |
| JUNIOR SUIT ODA | 2 kişi | 10.000 ₺ | 15 | `junior-suit` |
| SUPERIOR ODA | 2 kişi | 6.000 ₺ | 20 | `superior` |
| FAMILY ODA (Bağlantılı) | 4 kişi | (fiyat sitede yok) | 19 | `family` |
| Triple Room | 3 kişi | (fiyat sitede yok) | 6 | `triple` |

> Not: Eski isimlendirme özensiz ("ODA .", "Bağlantılı Oda ."). Yeni sitede temiz,
> başlık-stili adlar kullanılacak (örn. "King Suite", "Junior Suite", "Superior", "Aile Odası", "Triple").
> Manzara seçenekleri: bahçe / havuz / göl manzaralı odalar mevcut.

### Oda donanımı (genel)
Halı zemin, oturma alanı, gardırop, klima, LCD TV + uydu, ücretsiz WiFi, su ısıtıcısı (kettle),
minibar, saç kurutma, duşakabin, banyo malzemeleri.

---

## 3. Olanaklar / İmkanlar

- **Zengin serpme kahvaltı** (tüm misafirlere dahil — yorumlarda en çok övülen)
- **Sezonluk açık havuz** (doğayla baş başa)
- **Restoran** — gün boyu sıcak/soğuk yemek
- **Bar** — içecek servisi
- **Oda servisi**
- **Toplantı salonu** — kurumsal toplantı/seminer/özel etkinlik; saatlik/günlük kiralama, teknik altyapı
- Geniş yeşil bahçe, göl ve dağ manzarası
- Misafir yorumlarında öne çıkanlar: temizlik, yenilik, lokasyon, güler yüzlü/ilgili personel

---

## 4. Mevcut Site Analizi

- Teknoloji: Laravel + Tailwind + Alpine.js, "OTELYONET" otel yönetim sistemi (rezervasyon backend).
- Mevcut palet: **copper/bakır `#B87333`** (hover `#9A5E28`), charcoal `#212121`, krem `#FAFAF9`, font DM Sans.
- Rezervasyon motoru `reservation/book?room=ID` üzerinden OTELYONET'e bağlı → yeni statik sitede
  rezervasyon CTA'ları bu URL'lere veya WhatsApp'a yönlendirilecek (backend'i biz tutmuyoruz).
- Hero "videosu" yok; tek bir slider PNG var. **Gerçek video, referans görsellerden Higgsfield ile üretilecek.**

---

## 5. İndirilen Asset Envanteri (`assets/`)

`./download-assets.sh` (idempotent) ile **88 görsel**, 0 hata, ~272 MB:
- `assets/rooms/<slug>/` — 5 oda tipi, toplam 79 foto (çoğu 2368×1776; en iyiler **4240×2832** — hero/video için ideal)
- `assets/gallery/` — 9 (otel geneli + slider + ayar görseli)
- `assets/brand/` — (boş; logo kullanıcıdan/siteden alınacak)
- `assets/hero/`, `assets/video/` — üretilecek varlıklar için

**Eksik / kullanıcıdan beklenenler:** dış cephe & bahçe, havuz, kahvaltı/restoran, göl manzarası,
toplantı salonu, gece/atmosfer çekimleri, logo (vektör/yüksek çöz). → Telegram'dan gelecek.

---

## 6. Yeni Site — Tasarım Yönü

- **Estetik:** Apple-minimal + liquid glass. Koyu sinematik zemin, sıcak bakır aksan (markanın mevcut `#B87333`'ü korunur), off-white tipografi.
- **Tipografi:** serif display (Playfair tarzı) + geometrik grotesk; büyük `clamp()` başlıklar.
- **Liquid glass:** `backdrop-filter: blur+saturate`, 1px yarı saydam kenarlıklar, iç highlight + derin gölge, arkada animasyonlu bulanık gradyan "aurora" küreler, ince grain.
- **Scroll-driven video (asıl fark):** referans görsellerden üretilen kısa loop videolar, scroll ilerledikçe oynatılan/sabitlenen (pin + scrub) sinematik bölümler — Apple ürün sayfası hissi. `scroll-experience` skill + Higgsfield.
- **Bölümler:** preloader → glass nav (+ tam ekran mobil menü, 5 dil) → hero (video/Ken-Burns) → konum & mesafeler → olanaklar (havuz/kahvaltı/restoran/bar/toplantı) → odalar (filtreli bento + lightbox galeri) → scroll-video atmosfer bölümleri → galeri → rezervasyon/fiyat garantisi bandı → iletişim (glass form → WhatsApp/tel/mailto + harita) → footer.
- **SEO:** JSON-LD `Hotel`/`LodgingBusiness`, OG etiketleri, semantik başlıklar, 5 dil hreflang.
- **Mobil:** üst düzey responsive, `prefers-reduced-motion` saygısı.

---

## 7. Görev Süreci (Fazlar)

1. ✅ **Araştırma** — site + web; odalar, olanaklar, konum, iletişim, görseller.
2. ✅ **Çalışma alanı + asset scrape** — `didi-otel-web/`, 88 görsel indirildi.
3. ⏳ **Kullanıcı görselleri (Hermes/Telegram)** — dış cephe, havuz, kahvaltı, göl, toplantı, logo. *Beklemede.*
4. **Tasarım sistemi** — `:root` token'ları, liquid-glass bileşenleri, tipografi.
5. **İskelet + içerik** — `index.html` + `css/styles.css` + `js/data.js` (odalar/galeri/olanaklar tek kaynak) + `js/main.js`.
6. **Scroll-video bölümleri** — Higgsfield ile en iyi görsellerden loop video üretimi + scroll-scrub entegrasyonu (Hermes ajanla birlikte üretim/onay).
7. **Çoklu viewport screenshot QA** — masaüstü + 390px mobil + lightbox; `node --check` JS doğrulama.
8. **Deploy** — GitHub → Vercel.

---

## 8. Hermes Ajan Koordinasyonu

- Kanal: **Telegram DM — Onno** (`agent:main:telegram:dm:7904534693`, hedef `telegram:7904534693`).
- Kullanıcı eksik fotoğrafları (Madde 5) Telegram'dan gönderecek → `attachments_fetch` ile alınıp `assets/` altına yerleştirilecek.
- Video üretim sürecinde (Higgsfield) ara çıktılar onay için Hermes üzerinden paylaşılabilir.

---

## 9. Kullanıcıdan Beklenen Karar/Girdiler

1. Eksik fotoğraflar (özellikle **dış cephe, havuz, kahvaltı/restoran, göl manzarası, toplantı salonu**) + **logo**.
2. Family/Triple oda **gecelik fiyatları** (sitede yok).
3. Rezervasyon CTA'ları: mevcut OTELYONET motoruna mı (`/reservation/book`) yoksa sadece WhatsApp/telefona mı yönlensin?
4. Domain: yeni site `sapancadidiotel.com`'un yerine mi geçecek, yoksa ayrı bir Vercel adresinde önizleme mi?
