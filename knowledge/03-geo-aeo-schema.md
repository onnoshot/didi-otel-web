# GEO/AEO + Structured Data (uygulanacak)

SEO = 10 mavi linkte sırala. GEO/AEO = AI'ın cevabı yazarken ALINTILADIĞI kaynak ol.
Üç kaldıraç: (1) makine-okur facts (schema+tablo), (2) answer-first içerik, (3) trust/authority.

## Top 10 GEO/AEO aksiyonu
1. Anasayfada **Hotel JSON-LD** (`@type:Hotel`, LodgingBusiness DEĞİL): address, geo, amenityFeature, starRating(Rating), checkin/out, containsPlace→HotelRoom(bed+occupancy)
2. **MARE için Restaurant + Menu JSON-LD**, `containedInPlace`→hotel, servesCuisine, acceptsReservations, MenuSection/MenuItem
3. Sayfaları **answer-first** yaz: soru-tipi H2, cevap ilk ~200 kelimede, zamir yerine tam entity adı
4. **Factual tablolar**: havalimanı/merkez mesafe+süre, oda tipleri (m²/yatak/kapasite)
5. **FAQ sayfası + FAQPage schema** (gerçek sorular: check-in, mesafe, evcil, otopark, yemek)
6. **/llms.txt + /llms-full.txt** (factual, hype yok, fiyat yok → linkle)
7. **robots.txt tüm AI crawler'lara izin**: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, Claude-User, PerplexityBot, Google-Extended, Applebot, bingbot, CCBot, meta-externalagent, Amazonbot
8. **Organization + WebSite + BreadcrumbList** + `sameAs` (GBP, TripAdvisor, Instagram, Booking)
9. **Kendi entity'nde star aggregateRating YAYINLAMA** (self-serving = Google yıldız yok + ceza riski); review'ları 3.parti platformlara bırak, sameAs ile bağla
10. **E-E-A-T + tazelik**: dolu GBP, 3.parti mention, named-author, "son güncelleme" tarihi, HTTPS, şeffaf politika, facts'i SSR et (JS arkasına gizleme)

## Hotel JSON-LD iskelet (anahtar alanlar)
@type:Hotel, name, url, logo, image[], description, telephone, email, priceRange, currenciesAccepted,
starRating:{@type:Rating,ratingValue:5}, checkinTime:"14:00", checkoutTime:"12:00", numberOfRooms,
address:PostalAddress(Sapanca/Sakarya/54600/TR), geo:GeoCoordinates(40.6906,30.2628), hasMap,
amenityFeature:[LocationFeatureSpecification{name,value:true}...] (WiFi, Havuz, Restoran, Göl Manzarası, Otopark, Kahvaltı, Toplantı Salonu, Bar),
makesOffer:Offer(TRY fiyat), containsPlace:[HotelRoom{name,description,occupancy:QuantitativeValue,bed:BedDetails{typeOfBed,numberOfBeds},amenityFeature}],
sameAs:[instagram, facebook, tripadvisor, google maps]
→ search.google.com/test/rich-results + validator.schema.org ile doğrula.

## Restaurant (MARE) JSON-LD
@type:Restaurant, @id .../mare#restaurant, servesCuisine:[Akdeniz/Deniz Ürünleri/Fine Dining], priceRange,
acceptsReservations, containedInPlace:{@id hotel}, openingHoursSpecification, hasMenu:Menu→hasMenuSection→hasMenuItem(name,description,offers,suitableForDiet)

## Diğer schema: FAQPage (gerçek Q&A), BreadcrumbList, Organization+WebSite(SearchAction), ImageObject (hero/galeri caption+creator)

## llms.txt formatı
H1=isim, blockquote özet, H2 bölümler `- [Başlık](url): not`. Hype/fiyat/gizli veri YOK.
Bölümler: About, Rooms&Suites, MARE Restaurant, Havuz&Spa, Location&Directions, FAQ, Contact, Policies.
llms-full.txt = aynı yapı + her sayfanın tam düz-metin gövdesi inline.

## İçerik yapısı (AI extraction)
- Soru-tipi H2 (gerçek sorgular)
- Cevap ilk 1-2 cümlede
- Tablolar (mesafe, oda)
- Tam entity adı ("[Otel]'deki MARE restoranı, Sapanca")
- Semantik HTML (h1-h3, table, ul, address, time), facts SSR
- Her passage tek başına anlamlı

## AI motoru kaynak seçer: entity netliği, structured facts, authority/E-E-A-T, tazelik, kaynak çeşitliliği, extractability
