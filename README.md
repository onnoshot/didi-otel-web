# DİDİ Otel Sapanca — Web Sitesi

Kırkpınar Sapanca'daki DİDİ Otel için premium, statik (build gerektirmeyen) tanıtım sitesi.
Apple/SF-Pro estetiği, otomatik-oynayan tanıtım videosu hero, lüks zincir-otel yapısı.

- **Canlı:** https://didi-otel-web.vercel.app
- **Teknoloji:** Saf HTML + CSS + vanilla JS (framework yok, derleme yok). Görseller AVIF/WebP.
- **Deploy:** Statik dosyalar → GitHub → Vercel.

---

## Hızlı Başlangıç (yerel önizleme)

Depoyu klonlayın ve herhangi bir statik sunucuyla açın — kurulum/paket gerektirmez:

```bash
git clone https://github.com/onnoshot/didi-otel-web.git
cd didi-otel-web
python3 -m http.server 8000
# tarayıcıda: http://localhost:8000
```

Depo, sitenin **çalışması için gereken tüm dosyaları** içerir (optimize görseller, video, css). Ek bir adım yoktur.

---

## Deploy (Vercel)

İki yoldan biri:

**A) GitHub'a bağlı otomatik deploy (önerilen)**
1. Vercel'de "New Project" → bu GitHub deposunu seçin.
2. Framework Preset: **Other** (statik). Build command / output ayarı gerekmez.
3. Deploy. `main` dalına her push otomatik yayına gider.

**B) CLI ile**
```bash
npm i -g vercel
vercel --prod
```

Yönlendirme/cache/güvenlik başlıkları `vercel.json` içinde tanımlıdır (temiz URL'ler, `.css/.js` için `must-revalidate`, görsel/video için uzun cache).

Kendi domainine bağlarken: `index.html` ve alt sayfalardaki `canonical` / `og:url` / schema URL'lerini (`https://sapancadidiotel.com`) yeni domainle güncelleyin; `sitemap.xml`, `robots.txt`, `llms.txt` içindeki alan adını da değiştirin.

---

## Dizin Yapısı

```
index.html                 Ana sayfa (tek dosya, kritik CSS hariç stiller css/site.css'te)
css/site.css               Tüm sitenin paylaşılan tasarım sistemi
odalar/<slug>/index.html   Oda detay sayfaları (generate-rooms.py ile üretilir)
assets/
  brand/                   Logo (beyaz + lacivert)
  video/                   hero-loop.mp4 (hero tanıtım videosu, sessiz/loop), hero-poster.jpg
  web/                     Siteye giden optimize görseller (AVIF/WebP/JPG, çoklu genişlik)
    editorial/  rooms/<oda>/  gallery/  photos/
generate-rooms.py          Oda sayfası üretici (idempotent)
optimize-images.py         Orijinal görselleri web boyutlarına indirger (AVIF/WebP/JPG)
robots.txt sitemap.xml llms.txt   SEO / AI-arama (GEO/AEO)
vercel.json                Vercel yapılandırması
```

> Not: `assets/editorial/`, `assets/photos/`, `assets/rooms/` içindeki **orijinal yüksek-çözünürlük** dosyalar `.gitignore`'dadır (yalnızca yerelde tutulur; siteye giden optimize sürümleri `assets/web/`'te commit'lidir). Orijinaller yalnızca görselleri yeniden üretmek için gereklidir.

---

## İçerik Güncelleme

**Oda sayfaları** — metin/oda verisi `generate-rooms.py` içindeki `ROOMS` listesinde. Düzenledikten sonra:
```bash
python3 generate-rooms.py
```

**Görsel ekleme/yenileme** — orijinali ilgili `assets/<grup>/` klasörüne koyup:
```bash
python3 optimize-images.py editorial   # veya: rooms gallery photos all
```
(AVIF+WebP çoklu genişlik + JPG fallback üretir. Pillow gerekir: `pip install pillow`.)

**CSS değişikliği sonrası önbellek** — `css/site.css` linkindeki `?v=N` sürümünü artırın (tüm HTML'lerde). `vercel.json` zaten CSS'i `must-revalidate` yapar; sürüm artırımı garanti için.

---

## Analytics

Google Analytics 4 (gtag.js) tüm sayfaların `<head>`'ine gömülüdür.
**Ölçüm Kimliği:** `G-C8D22FPDET` — değiştirmek için `index.html` ve `generate-rooms.py` (GA sabiti) içindeki kimliği güncelleyip oda sayfalarını yeniden üretin.

---

## Notlar

- **Rezervasyon:** CTA'lar mevcut OTELYONET motoruna (`sapancadidiotel.com/reservation/book`) ve WhatsApp'a (`wa.me/905331350888`) yönlenir; site rezervasyon backend'i tutmaz.
- **İletişim:** 0264 592 12 12 · 0533 135 08 88 (aynı numara WhatsApp hattı).
- **Restoran:** "Mare Gastro" (otel bahçesindeki restoran).
- **Künye:** Uniqbee (uniqbee.com) tarafından hazırlanmıştır; otel Otelyonet (otelyonet.com.tr) ile yönetilir.
- **Sıradaki (planlı):** ayrı MARE/galeri/konum/hakkımızda/SSS sayfaları ve 5 dil (TR/EN/AR-RTL/DE/RU).
- **Erişilebilirlik/performans:** `prefers-reduced-motion` desteklenir (video yerine poster gösterilir); LCP posteri preload'lu; hero videosu sessiz + `faststart` (hızlı açılır).
