# 🎬 Pexels & Pixabay Video İndirici

Belirttiğin konuya göre Pexels ve Pixabay'den otomatik video indiren Python aracı.

---

## 🔧 Kurulum

### 1. Python yükle (3.10+)
https://python.org/downloads

### 2. Gerekli kütüphaneyi yükle
```bash
pip install -r requirements.txt
```

### 3. API Key'lerini al (ÜCRETSİZ)

| Platform | Link | Nasıl? |
|----------|------|--------|
| **Pexels** | https://www.pexels.com/api/ | Kayıt ol → API Key al |
| **Pixabay** | https://pixabay.com/api/docs/ | Kayıt ol → API Key al |

### 4. downloader.py dosyasını aç, en üstteki kısmı düzenle:
```python
PEXELS_API_KEY  = "buraya_pexels_key_yaz"
PIXABAY_API_KEY = "buraya_pixabay_key_yaz"
```

---

## 🚀 Kullanım

```bash
# Temel kullanım – "nature" konusunda her platformdan 100 video
python downloader.py "nature"

# Sadece 50 video indir
python downloader.py "ocean" -n 50

# Sadece Pexels'ten indir
python downloader.py "city" --source pexels

# Sadece Pixabay'den, 30 video, özel klasöre
python downloader.py "dogs" --source pixabay -n 30 -o "kopek_videolari"

# 8 paralel indirme (daha hızlı)
python downloader.py "sunset" -t 8
```

### Tüm seçenekler:
```
python downloader.py --help

  query           Arama konusu
  -n, --count     Kaç video (varsayılan: 100)
  -o, --output    Klasör adı  (varsayılan: indirilenler)
  --source        pexels | pixabay | her ikisi (varsayılan: her ikisi)
  -t, --threads   Paralel indirme sayısı (varsayılan: 4)
```

---

## 📁 Dosya Yapısı

```
video_downloader/
├── downloader.py      ← Ana program
├── requirements.txt   ← Bağımlılıklar
└── README.md          ← Bu dosya

indirilenler/          ← Videolar burada birikir (otomatik oluşur)
├── pexels_12345.mp4
├── pixabay_67890.mp4
└── ...
```

---

## ⚠️ Notlar

- Pexels ve Pixabay API'leri ücretsiz ancak dakika/saat bazlı istek limiti var.
- Pexels: 200 istek/saat
- Pixabay: 100 istek/dakika
- Videolar MP4 formatında, mümkün olan en yüksek kalitede indirilir.
- Daha önce indirilmiş dosyalar tekrar indirilmez (devam özelliği).
