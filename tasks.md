# SensoryArch AI — Geliştirme Görev Listesi (PRD v1.0’dan)

Kaynak: `c:\Users\Doğa YÜKSEL\Desktop\prd.md.ini`

## Kapsam (PRD’den)
- **Veri girişi**: 2D görsel, panoramik fotoğraf, 3D model (MVP’de önce 2D).
- **Analiz**: ışık kaynakları, yansıma noktaları, karmaşık görsel paternler.
- **Görselleştirme**: “yüksek uyaran” bölgeleri için heatmap.
- **Skor**: “erişilebilirlik skoru”.
- **Öneriler**: riskli bölgeler için iyileştirme tavsiyeleri.
- **KPI**: tek analiz < 30 sn.

---

## Faz 0 — Proje temeli ve kararlar (1 gün)
- [ ] **Teknoloji seçimi (MVP)**  
  - **Karar**: Frontend `Next.js` (React), Backend `Python + Flask` (tek servis), CV `OpenCV`  
  - **Done**: Repo klasör yapısı ve çalıştırma komutları tanımlı.
- [ ] **MVP kapsam kilidi**  
  - **MVP**: yalnızca **2D görsel** yükleme → analiz → heatmap → skor → öneriler  
  - **Ertelenenler**: panoramik/3D, çoklu hassasiyet simülasyon filtreleri (UH2), kullanıcı hesapları
  - **Done**: `tasks.md` içindeki “MVP” etiketli işler net.
- [ ] **Çıktı formatı tasarımı (API sözleşmesi)**  
  - **Analiz çıktısı**: `heatmap_image` (base64 veya URL), `score` (0–100), `risk_regions[]`, `recommendations[]`, `timing_ms`
  - **Done**: JSON şeması bu dosyada netleşmiş.

---

## Faz 1 — Backend (MVP) (2–4 gün)

### 1.1 API iskeleti
- [ ] **`POST /analyze` endpoint’i** (multipart image upload)  
  - **Done**: JPG/PNG kabul ediyor, dosya boyutu sınırı var, hata mesajları tutarlı.
- [ ] **Sağlık kontrolü ve versiyon** (`GET /health`, `GET /version`)  
  - **Done**: servis ayakta mı ve sürüm görülebiliyor.

### 1.2 Görüntü analizi (heuristic tabanlı MVP)
- [ ] **Işık kaynağı/Parlaklık haritası çıkarımı**  
  - **Öneri**: HSV/V kanalında threshold + morfoloji ile parlak bölgeler
  - **Done**: parlak bölgeler “risk mask” üretip döndürüyor.
- [ ] **Yansıma (specular highlight) tespiti (basit yaklaşım)**  
  - **Öneri**: yüksek parlaklık + düşük doygunluk (S) bölgeleri
  - **Done**: ayrı bir risk katmanı olarak hesaplanıyor.
- [ ] **Karmaşık görsel patern tespiti (texture/edge yoğunluğu)**  
  - **Öneri**: Canny edge density / Laplacian variance / Gabor (basit metrik)
  - **Done**: patern yoğunluğu bir “uyaran” metriğine katkı sağlıyor.
- [ ] **Birleşik “uyaran” skoru haritası**  
  - **Done**: normalize edilmiş tek ısı haritası (0–1) üretiliyor.

### 1.3 Heatmap üretimi + bölgeler
- [ ] **Heatmap overlay görseli üretimi**  
  - **Done**: orijinal görsel üzerine saydam heatmap bind edilip PNG döndürülüyor.
- [ ] **Riskli bölge çıkarımı (bounding box/contour)**  
  - **Done**: `risk_regions[]` alanında en az: `id`, `bbox`, `severity`, `type` (light/reflection/pattern) var.

### 1.4 Erişilebilirlik skoru (0–100)
- [ ] **Skor tanımı ve ağırlıklandırma (MVP)**  
  - **Örnek**: \(score = 100 - (w1*light + w2*reflection + w3*pattern)\)  
  - **Done**: skor deterministik, aynı girdiye aynı sonuç.
- [ ] **Skor kalibrasyon parametreleri** (config üzerinden)  
  - **Done**: ağırlıklar/threshold’lar kod değişmeden ayarlanabiliyor.

### 1.5 Öneri motoru (kural tabanlı MVP)
- [ ] **Risk tipine göre öneri şablonları**  
  - **Light**: ışık sıcaklığı/armatür difüzör, parlamayı azaltma  
  - **Reflection**: mat boya, yansımasız malzeme, parlak yüzey azaltma  
  - **Pattern**: daha sade doku/kontrast düzenleme
  - **Done**: `recommendations[]` içinde her bölgeye en az 1 öneri.

### 1.6 Performans (KPI < 30 sn)
- [ ] **Zaman ölçümü** (request başına `timing_ms`)  
  - **Done**: API çıktı JSON’unda süre var.
- [ ] **Görüntü boyutlandırma stratejisi**  
  - **Done**: büyük görsellerde analiz otomatik yeniden ölçekleyerek 30 sn hedefini destekliyor.

---

## Faz 2 — Frontend (MVP) (2–4 gün)

### 2.1 Yükleme deneyimi
- [ ] **Yükleme ekranı** (drag & drop + dosya seç)  
  - **Done**: yalnızca JPG/PNG kabul; progress/loading durumu var.
- [ ] **Analiz başlatma + hata durumları**  
  - **Done**: ağ hatası/format hatası/limit hatası kullanıcıya anlaşılır.

### 2.2 Sonuç ekranı (interaktif)
- [ ] **Heatmap görüntüleme** (orijinal/overlay toggle)  
  - **Done**: kullanıcı heatmap’i aç/kapat yapabiliyor.
- [ ] **Erişilebilirlik skoru bileşeni**  
  - **Done**: 0–100 skor, açıklama metni ve “ne anlama gelir” kısa ipucu.
- [ ] **Risk bölgesi listesi + seçince vurgulama**  
  - **Done**: listeden seçilen bölge görselde highlight oluyor.
- [ ] **Öneriler paneli** (bölge bazlı)  
  - **Done**: öneriler okunabilir, kopyalanabilir.

---

## Faz 3 — Doğrulama, kalite, teslim (1–3 gün)
- [ ] **Örnek veri seti oluşturma** (10–20 görsel)  
  - **Done**: farklı ışık/parlama/doku örnekleri var.
- [ ] **Smoke test senaryoları**  
  - **Done**: en az: yükle→analiz→sonuç; hatalı dosya; büyük dosya.
- [ ] **Basit metrikler**  
  - **Done**: günlük sayım: istek sayısı, ortalama `timing_ms`, hata oranı.
- [ ] **Kullanım dokümantasyonu** (README)  
  - **Done**: local çalıştırma, environment değişkenleri, örnek API isteği.

---

## Faz 4 — PRD’deki ileri özellikler (MVP sonrası)
- [ ] **Panoramik fotoğraf desteği**  
  - **Done**: equirectangular pano yükleme + analiz pipeline uyumu.
- [ ] **3D model desteği** (format seçimi: glTF/obj)  
  - **Done**: basit render → 2D analiz veya 3D düzeyinde analiz stratejisi belirlenmiş.
- [ ] **Duyusal hassasiyet simülasyon filtreleri (UH2)**  
  - **Done**: en az 2 profil (örn. “ışığa hassas”, “görsel paterne hassas”) ve görsel filtre.
- [ ] **Rapor çıktısı (PDF/Paylaşım linki)**  
  - **Done**: skor, heatmap, bölgeler, öneriler tek raporda.

---

## API Çıktı Taslağı (MVP)
```json
{
  "score": 0,
  "timing_ms": 0,
  "heatmap_image": "data:image/png;base64,...",
  "risk_regions": [
    {
      "id": "r1",
      "type": "light",
      "severity": 0.0,
      "bbox": { "x": 0, "y": 0, "w": 0, "h": 0 }
    }
  ],
  "recommendations": [
    {
      "region_id": "r1",
      "title": "Parlamayı azaltın",
      "actions": ["Mat boya kullanın", "Difüzör ekleyin"]
    }
  ]
}
```


