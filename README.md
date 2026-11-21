# AmazonDealHunter

Amazon ürünleri için fiyat takibi ve indirim alarmı altyapısı.

> **Durum:** Bu depo çalışan bir başlangıç projesidir. SQLite fiyat geçmişi, indirim hesaplama ve isteğe bağlı Telegram bildirimi içerir. Amazon'dan otomatik ürün verisi çekmek için sağlayıcı adaptörü henüz tamamlanmamıştır; demo verisiyle çalışır. Amazon'un kullanım koşullarına ve erişim kurallarına uygun bir veri kaynağı/adaptör eklenmeden canlı Amazon taraması yaptığı iddia edilmez.

## Özellikler

- Ürünlerin fiyatlarını SQLite veritabanında saklama
- Önceki fiyatla karşılaştırıp indirim yüzdesini hesaplama
- İsteğe bağlı Telegram bot bildirimi
- JSON dosyasından demo ürün verisi okuma
- Amazon Türkiye gibi farklı mağazalar için genişletilebilir sağlayıcı arayüzü

## Kurulum

Python 3.10 veya üzeri gerekir.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

`.env.example` dosyasını `.env` olarak kopyalayın. Telegram bildirimi için bot token'ı ve sohbet kimliğini girin. Ardından:

```bash
python -m src.main --input data/products.example.json
```

Telegram ayarları boş bırakılırsa uygulama terminale çıktı verir.

## Ürün JSON biçimi

```json
[
  {
    "asin": "B0EXAMPLE01",
    "title": "Örnek ürün",
    "url": "https://www.amazon.com.tr/dp/B0EXAMPLE01",
    "price": 1299.90,
    "currency": "TRY",
    "store": "amazon.com.tr"
  }
]
```

## Yol haritası

- [x] SQLite fiyat geçmişi
- [x] İndirim yüzdesi hesaplama
- [x] Telegram bildirim altyapısı
- [x] Demo veri sağlayıcısı
- [ ] Amazon kullanım koşullarına uygun canlı veri sağlayıcısı
- [ ] Hedef fiyat ve minimum indirim eşikleri
- [ ] Zamanlanmış periyodik kontrol
- [ ] Almanya, ABD ve Japonya mağazaları için adaptörler

## Güvenli kullanım

CAPTCHA, oturum açma, erişim kısıtlaması veya diğer güvenlik önlemlerini aşmaya yönelik bir mekanizma içermez. Canlı veri entegrasyonu, ilgili mağazanın izin verdiği API veya veri erişim yöntemi üzerinden yapılmalıdır.

## Lisans

MIT
