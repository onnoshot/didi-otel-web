# Teknik SEO + Core Web Vitals 2026 (uygulanacak checklist)

Lüks otel statik site | Vercel | TR/EN/AR/DE/RU (AR = RTL). Tümü p75 yeşil hedefi.

## CWV hedefleri (p75)
- LCP ≤ 2.5s · INP ≤ 200ms · CLS ≤ 0.1

## Top 12 must-do
1. 3 metrik de p75 yeşil — PageSpeed ile her şablonu mobil+masaüstü doğrula
2. Hero/LCP görseli: AVIF, `fetchpriority="high"`, preload, ASLA `loading=lazy`
3. Her img/video/iframe'de `width`+`height` (veya `aspect-ratio`) → CLS sıfır
4. `<picture>` AVIF→WebP→JPEG + srcset/sizes, 3-4 genişlik; alt-fold `loading=lazy decoding=async`
5. Hero video asla LCP olmasın: preload poster, `preload=none`, YouTube için façade
6. Self-host subset WOFF2 (Latin/Arabic/Cyrillic `unicode-range`), `font-display:swap`, fallback metric override
7. Tüm JS defer, critical CSS inline, galeri/harita/booking lazy-init → INP korur
8. Çift yönlü hreflang cluster (tr/en/ar/de/ru + x-default) her sayfada; dil başına self-canonical
9. `<html lang>` doğru + Arapça `dir="rtl"`; logical CSS props (margin-inline-start vb.) ile otomatik mirror
10. Çok dilli sitemap.xml `xhtml:link` alternates; allow-all robots.txt + Sitemap satırı
11. Local SEO: LodgingBusiness/Hotel JSON-LD + geo meta + NAP tutarlılık + GBP; Sapanca/Sakarya kelimeler 5 dilde
12. vercel.json: cleanUrls + tutarlı trailingSlash + hashed asset'lerde immutable 1yıl cache, HTML must-revalidate

## Kritik snippet'ler

### LCP preload
```html
<link rel="preload" as="image" fetchpriority="high" href="/img/hero-1600.avif" type="image/avif"
  imagesrcset="/img/hero-800.avif 800w,/img/hero-1600.avif 1600w" imagesizes="100vw">
```
### Responsive picture
```html
<picture>
 <source type="image/avif" srcset="/img/x-800.avif 800w,/img/x-1600.avif 1600w" sizes="(max-width:768px) 100vw,50vw">
 <source type="image/webp" srcset="/img/x-800.webp 800w,/img/x-1600.webp 1600w" sizes="(max-width:768px) 100vw,50vw">
 <img src="/img/x-1600.jpg" width="1600" height="1067" loading="lazy" decoding="async" alt="...">
</picture>
```
### Font subsetting (unicode-range Latin+TR / Arabic / Cyrillic), preload sadece above-fold dil
### hreflang cluster (her sayfada, kendisi+diğerleri+x-default), Arapça `dir=rtl`
### Vercel headers
```json
{"cleanUrls":true,"trailingSlash":true,
 "headers":[{"source":"/(.*)\\.(woff2|avif|webp|jpg|png|svg|css|js)","headers":[{"key":"Cache-Control","value":"public, max-age=31536000, immutable"}]},
 {"source":"/(.*)\\.html","headers":[{"key":"Cache-Control","value":"public, max-age=0, must-revalidate"}]}]}
```
### geo meta (Sapanca ~40.69, 30.26; TR-54)
```html
<meta name="geo.region" content="TR-54"><meta name="geo.placename" content="Sapanca, Sakarya">
<meta name="geo.position" content="40.69;30.26"><meta name="ICBM" content="40.69, 30.26">
```

## Title pattern: `Sayfa | Marka | Sapanca` (≤60ch). Her sayfa tek H1, breadcrumb + BreadcrumbList JSON-LD.

## ♻️ REPO İÇİ HAZIR PATTERN (klonla)
`mare-gastro-web/` zaten Sapanca, çok dilli (TR/EN/AR/RU), i18n pipeline ile:
- `mare-gastro-web/sitemap.xml`, `robots.txt`
- `mare-gastro-web/i18n/` (source.html + tr/en/ar/ru JSON → build_i18n.py)
- `mare-gastro-web/{tr,en,ar,ru}/index.html`
→ Bu pipeline'ı baz al; **DE (Almanca) ağacı ekle** ve her hreflang/sitemap'e `de` ekle.
→ MARE Gastro gerçek bir kardeş marka (maregastro.com) — restoran bölümü için doğrulandı.
