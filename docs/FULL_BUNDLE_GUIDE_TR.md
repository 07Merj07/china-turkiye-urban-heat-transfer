# Tek Paket Rehberi (Türkçe)

## Bu ZIP nedir?
Bu, tek ana proje klasörü içinde hem GitHub'a uygun çalışma dosyalarını hem de görüşmede gönderilmiş tarihî çıktı/yerel veri arşivini bir araya getiren pakettir. Proje kökü `urban-heat-transfer/` klasörüdür.

## Neler var?
- `notebooks/`: Tanu'nun üç final notebook'u.
- `src/`, `scripts/`, `tests/`: şehir eşleştirme, kaynak dosya denetimi, veri hazırlığı ve doğrulama kodları.
- `data/reference/`, `data/processed/`, `data/external_features/`: CityInfo, yeniden üretilebilir şehir-ülke eşleştirmesi ve kanonik mapping.
- `data/sample_uhi/`: beş örnek `Mod2_Nig` dosyası; bunlar 80 dosyanın yerine geçmez.
- `archive/historical_artifacts/`: eski target audit'leri, eski Phase 2 çıktıları, AMod2 örnekleri ve eski dış özellik tabloları. Bunlar arşivdir, yeni sonuç değildir.
- `archive/large_local_snapshots_not_active/`: iki farklı içerik grubundan ERA5 dosyası. Kaynak kökeni doğrulanmadığı için aktif girdi sayılmaz.

## 80 kaynak dosyasını projeye alma
Bilgisayarındaki asıl `UHII_dataset` klasöründe 80/80 gerekli dosyanın bulunduğunu PowerShell kontrolüyle bildirdin. Bu dosyaların tümünün baytları sohbete yüklenmediği için bu ZIP'e 80'inin tamamı gömülü değildir; beş örnek dosya eklenmiştir.

1. ZIP'i çıkar.
2. `urban-heat-transfer` klasörünü aç.
3. Adres çubuğuna `powershell` yazıp Enter'a bas.
4. Şu komutu çalıştır: `\.\scripts\copy_required_uhi_files.ps1`

Betik, mevcut OneDrive Masaüstü veri yolunu bulup yalnızca tam adı `Mod2_Nig_YYYY_{6,7,8,22}.csv` olan 80 dosyayı `data/raw/UHII_dataset/` içine kopyalar. Kaynakları silmez/yeniden adlandırmaz; aynı isimli hedef içerikleri farklıysa kopyalamayı durdurur. `AMod2` dosyaları hedef veri olarak kullanılmaz.

## GitHub'a hangi bölüm yüklenmeli?
GitHub deposuna `urban-heat-transfer/` kökündeki çalışma projesi yüklenir; `archive/`, `data/raw/UHII_dataset/`, NetCDF, ZIP ve üretilmiş sonuç dosyaları `.gitignore` ile Git dışında tutulur. Bunların hepsi bu yerel ZIP'te korunuyor ama normal GitHub commit'ine eklenmez. GitHub normal Git'te 100 MiB'den büyük tek dosyaları engeller ve büyük depolarda Git LFS/haricî depolama düşünülmelidir.

## Çok önemli sınır
Tüm 2001–2020 gerçek veri akışı ve canlı NASA/CDS indirmeleri henüz baştan sona çalıştırılıp onaylanmış değildir. Eski model performans CSV'leri nihai araştırma sonucu değildir. Üç notebook sırayla çalıştırılmalı ve `scripts/phase2_validate_outputs.py` gerçek çıktı klasöründe `GO` vermeden araştırma tamamlandı denmemelidir.

## GitHub durumu
Bu ZIP henüz `https://github.com/07Merj07/china-turkiye-urban-heat-transfer` adresine yüklenmiş veya commit edilmiş değildir. Gerçek uzak depoyu okuyup güncellemek için GitHub hesabı bağlantısı/izinleri gerekir.
