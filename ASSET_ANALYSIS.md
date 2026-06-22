# Foto Analizi — Kullanıcı Görselleri (YeniSecilen-Editorial)

Toplam: **15 editorial PNG** (yüksek çöz., ~2048px) + **50 oda iç çekimi** (`d1–d50.jpg`) + **1 dış cephe** (`d0.png`) + **logo** (`adidilogo.png`, 1850×720).
Hepsi `didi-otel-web/assets/` altına kopyalandı: `editorial/`, `photos/`, `brand/`.

## Editorial set (kahraman/atmosfer adayları)

| Dosya | İçerik | Kullanım |
|-------|--------|----------|
| **ONN09422** | **Otel dış cephesi + turkuaz havuz + palmiyeler + mavi gökyüzü** | ⭐ HERO — scroll-scrub video kaynağı (kullanıcı önerisi, onaylandı) |
| ONN09446 | Dış cephe + palmiye bahçesi (yan açı) | Hakkımızda / hero alt |
| ONN09451 | Bahçe yolu, uzakta havuz | Konum/bahçe bölümü, parallax |
| ONN09461 | Havuz + şezlong + şemsiye, begonvil çerçeve | Havuz bölümü hero |
| ONN09464 | Havuz + şezlong (begonvil ön plan) | Havuz galeri |
| ONN09440 | Bahçe cabana — beyaz perdeli loca/oturma | Bahçe & dinlenme bölümü |
| ONN09442 | Cabana daybed sırası (beyaz minderli) | Atmosfer / scroll |
| ONN09357 | **MARE** lacivert tente/tabela | Restoran bölümü kimliği |
| ONN09327 | Restoranda iki misafir, kadeh tokuşturma | MARE yaşam tarzı |
| ONN09335 | Şarap kadehleri "şerefe" + tabaklar | MARE yaşam tarzı |
| ONN09337 | Masa, beyaz perde, kadeh tokuşturma | MARE yaşam tarzı |
| ONN09378 | Üstten masa düzeni, çok tabaklı | MARE menü/sofra |
| ONN09382 | Közde et tabağı (gurme) | MARE menü |
| ONN09399 | Gurme tabak yakın çekim | MARE menü |
| ONN09447 | Beyaz bankta gri British kedi | Karakter/marka detayı (footer/about'ta sıcak dokunuş) |

## Oda iç çekimleri (`photos/d*.jpg`, 50 adet)
Profesyonel oda fotoğrafları: yataklar, suit oturma alanları, banyolar, detaylar.
Sıcak ışık, koyu ahşap + krem + bej paleti — markanın bakır/charcoal yönüyle birebir uyumlu.
→ Oda tipi sayfalarının ve bento galeri ızgarasının ana kaynağı. (Hangi foto hangi oda tipi —
oda sayfalarını kurarken eski site eşleşmesi + görsel içerikle eşleştirilecek.)

## ⚠️ Dikkat: "MARE" restoran kimliği
Editorial yemek çekimlerinde **MARE** markası görünüyor; bu, otelin sahasındaki restoran gibi
duruyor (aynı havuz/bahçe ONN09422 ile örtüşüyor). Sitede "MARE Restaurant — DİDİ Otel'in
restoranı" olarak ayrı, gelişmiş bir bölüm/sayfa olarak işlenecek. (Kullanıcı doğrularsa
maregastro.com ile ilişki/menü bağlantısı eklenebilir.)

## Hero / scroll-video planı
- Kaynak: **ONN09422** (otel + havuz). Higgsfield ile yavaş sinematik kamera hareketi (push-in / hafif
  parallax, su yansıması, bulut akışı) → 4–8 sn loop video.
- Scroll-scrub: hero bölümü pinlenip video `currentTime` scroll'a bağlanır (Apple ürün sayfası hissi).
- Ek scroll-video adayları: havuz (ONN09461), cabana (ONN09440), MARE atmosfer (ONN09327).

## Varsayımlar (otonom ilerleme — düzeltebilirsiniz)
1. Çok sayfalı site: Anasayfa · Odalar (+her oda detay) · MARE Restoran · Havuz & Bahçe · Galeri · Konum · Hakkımızda · İletişim · SSS.
2. Rezervasyon CTA'ları: mevcut OTELYONET `reservation/book` + WhatsApp (ikisi de).
3. Family/Triple fiyatı sitede yok → "WhatsApp'tan güncel fiyat".
4. Deploy: önce ayrı Vercel önizleme adresi; canlı domain değiştirilmez (siz onaylayınca).
5. 5 dil korunur (TR ana; AR için RTL).
