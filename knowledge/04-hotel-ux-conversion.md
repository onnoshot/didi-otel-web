# Lüks Otel UX, Dönüşüm & İçerik (uygulanacak)

2026 yönü: "quiet luxury" — kısıtlama, mahremiyet, niyet. Misafir oda değil hikaye/dönüşüm alır.
Site: sakin, ferah, hızlı, tek aksiyona götürür → doğrudan rezervasyon. Hedef dönüşüm: top-quartile butik %4-5.

## Bilgi Mimarisi (çok sayfa + sinematik uzun anasayfa)
```
/ Anasayfa (hikaye scroll + sticky booking bar)
/odalar → /odalar/[oda-tipi] (5 oda, her biri detay sayfa)
/mare (restoran: konsept, menü, atmosfer, rezervasyon)
/otel (hakkında: hikaye, bina, havuz, cabana, bahçe, kahvaltı)
/galeri (kategorili lightbox)
/cevre (konum/Sapanca: harita, mesafe, çevre deneyim)
/teklifler (doğrudan-özel paket + en iyi fiyat garantisi)
/iletisim (harita, tel, WhatsApp, form)
footer: KVKK, şartlar, iptal politikası, erişilebilirlik
```

## Top 10 dönüşüm/UX must
1. Booking CTA above-fold + her yerde sticky (~%22 checkout artışı)
2. Mobil-first, LCP <2.0s — AVIF/WebP hero fetchpriority=high, asla lazy; trafiğin %60-65 mobil
3. En iyi fiyat garantisi + spesifik doğrudan-özel avantaj (kahvaltı, geç çıkış, upgrade) booking bar yanında
4. Yatay haftalık date picker + taban fiyat + hızlı preset (mobilde %4-8 artış)
5. Oda + fiyat seçimini tek ekrana indir (en büyük friction kazancı)
6. Sadece gerçek profesyonel foto, kategorili WebP/AVIF lightbox (dönüşüm +%15-25); stok foto güveni öldürür
7. Tek-dokunuş WhatsApp + tel, gerçek insan adı/foto, dakikalar içinde yanıt (TR/Arap pazarı kritik)
8. CTA yanında trust kümesi: Google/TripAdvisor puanı, misafir foto, iptal metni, ödeme rozeti
9. WCAG 2.2 AA + Arapça gerçek RTL: görünür focus, klavye/lightbox nav, reduced-motion, 24px target, foto üstü scrim kontrast
10. Quiet-luxury metin, çevrilmiş değil yerelleştirilmiş; TR ana, kısa zarif ton, bağlama özel CTA

## Anasayfa scroll sırası
1 Hero+value prop+booking · 2 his (1-2 cümle hikaye+imza görsel) · 3 odalar teaser (5 tip) · 4 MARE teaser · 5 havuz/cabana/kahvaltı anları · 6 göl&dağ/Sapanca konum · 7 yorumlar+puan şeridi (booking CTA yanında) · 8 doğrudan rezervasyon teklifi+fiyat garantisi · 9 footer WhatsApp/tel/harita
Mikro-animasyon: Aman/Six Senses tarzı yavaş, sakin, meditatif — asla meşgul/cafcaflı.

## Oda sunumu
İndeks kart: lead foto 16:9, ad+manzara etiketi, kapasite ikon, yatak, m², 3-4 ikon amenity, gerçek tarih-fiyatı (statik "X'den" zayıf), CTA "Bu Odayı Seç".
Detay: kategorili lightbox galeri, ikon+metin tam amenity, kapasite/yatak/m²/kat/manzara, inline fiyat+seç, iptal politikası okunur paragraf, ilgili odalar, kalıcı CTA.

## MARE restoran: güçlü hero, tek-tık menü+iştah açıcı foto, atmosfer galeri+kısa konsept, native rezervasyon (WhatsApp/tel/form), oda sayfalarından cross-link.

## Trust: review puanları (Google/TripAdvisor/Booking), gerçek foto, ödül/basın, konum kanıtı (harita/adres/mesafe), iptal+ödeme rozeti. Spesifik dürüst metin > superlatif. Sahte "2 kişi bakıyor" YOK; gerçek "son 2 oda" varsa.

## Mikrocopy (TR/EN)
Müsaitliği Gör/Check Availability · Bu Odayı Seç/Select This Room · En İyi Fiyatı Doğrudan Bizden · Bize WhatsApp'tan Yazın · MARE'de Yer Ayırtın · Size Özel Teklifleri Görün · Atmosferi Keşfedin · Didi'nin Hikayesi · "Ücretsiz iptal · Anında onay" · value prop: "Göl ve orman arasında sakin bir kaçış"

## Çok dil: TR ana; EN/AR/DE/RU tam yerelleştir (çeviri değil transcreation, özellikle AR/RU). Toggle: Türkçe/English/العربية/Deutsch/Русский. Marka adları sabit.
## Erişilebilirlik: kontrast 4.5:1 (foto üstü scrim), görünür focus (WCAG 2.2), tam klavye, açıklayıcı alt, reduced-motion, 24px target, AR dir=rtl + logical props.
