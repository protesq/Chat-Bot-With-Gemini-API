# 🤖 Gemini AI Chat Bot

Google Gemini API kullanan modern PyQt5 tabanlı sohbet uygulaması.

## ✨ Özellikler

- 🎨 Modern dark tema arayüz
- 💬 Gerçek zamanlı AI sohbeti
- 📝 Sohbet geçmişi kaydetme/yükleme
- 🧵 Asenkron mesaj işleme
- 🔄 Otomatik geçmiş yükleme
- 🌐 Türkçe arayüz

## 🛠️ Kurulum

### Gereksinimler

```bash
pip install PyQt5 google-generativeai
```

### API Key Alma

1. [Google AI Studio](https://aistudio.google.com/apikey?hl=tr) adresine git
2. Google hesabınla giriş yap
3. "Create API Key" butonuna tıkla
4. Yeni proje oluştur veya mevcut projeyi seç
5. API key'i kopyala
6. `gui_bot.py` dosyasında 49. satırdaki `self.api_key` değerini değiştir:

```python
self.api_key = "YOUR_API_KEY_HERE"
```

## 🚀 Kullanım

```bash
python gui_bot.py
```

### Temel Kullanım

1. Uygulamayı başlat
2. Alt kısımdaki metin kutusuna mesajını yaz
3. Enter'a bas veya "Gönder" butonuna tıkla
4. Bot yanıtını bekle

### Menü Özellikleri

- **📁 Dosya** → **💾 Geçmişi Kaydet**: Sohbeti JSON olarak kaydet
- **📁 Dosya** → **📂 Geçmişi Yükle**: Kaydedilmiş sohbeti yükle
- **📁 Dosya** → **🧹 Geçmişi Temizle**: Mevcut sohbeti sil
- **❓ Yardım** → **ℹ️ Hakkında**: Uygulama bilgileri

## 📁 Dosya Yapısı

- `gui_bot.py` - Ana uygulama dosyası
- `sohbet_gecmisi.json` - Otomatik kaydedilen sohbet geçmişi

## ⚙️ Yapılandırma

### Model Değiştirme

`gui_bot.py` dosyasında 51. satır:

```python
self.model = "gemini-2.5-flash"  # veya "gemini-pro"
```

### Geçmiş Limiti

30. satırda son kaç mesajın gönderileceğini ayarlayabilirsin:

```python
for item in self.history[-5:]  # Son 5 mesaj
```

## 🔒 Güvenlik

- API key'ini kaynak kodda saklama
- Ortam değişkeni kullan:

```python
import os
self.api_key = os.getenv('GEMINI_API_KEY')
```

## 🐛 Sorun Giderme

**API Key Hatası**: API key'inin doğru ve aktif olduğundan emin ol
**Import Hatası**: `pip install PyQt5 google-generativeai` komutunu çalıştır
**Encoding Hatası**: Dosya UTF-8 olarak kaydedildiğinden emin ol

## 📝 Notlar

- Uygulama kapanırken geçmiş otomatik kaydedilir
- Maximum 5 önceki mesaj context olarak gönderilir
- Tüm sohbetler `sohbet_gecmisi.json` dosyasında saklanır 