# Yerelde / Google Colab'da Çalıştırma — Türkçe Rehber

## 1. Yeni proje klasörünü oluştur

`Urban_Heat_Transfer_GitHub_Ready.zip` dosyasını bilgisayarında **yeni bir konuma** çıkart. Örneğin `Masaüstü\GitHubProject\urban-heat-transfer`. Eski `urban-heat-transfer` klasörünün üstüne çıkartma; orijinal dosyaların aynen kalsın.

## 2. Gerekli 80 kaynak CSV'yi yeni projeye kopyala

Windows PowerShell'de yeni proje klasörünü aç ve şunu çalıştır:

```powershell
.\scripts\copy_required_uhi_files.ps1 -Source "C:\Users\Mertc\OneDrive\Masaüstü\urban-heat-transfer\data\UHII_dataset"
```

Bu örnek, daha önce kontrol ettiğin mevcut kaynak klasörünü kullanır. Yol farklıysa `-Source` değerini gerçek kaynak klasörüne göre değiştir. Başarılı olursa `BAŞARILI: 80 / 80` yazar. Kaynak klasörde hiçbir dosya silinmez, taşınmaz veya yeniden adlandırılmaz. Kopyalama yalnızca yeni projedeki `data/raw/UHII_dataset/` klasörüne yapılır.

## 3. Kaynakları denetle

Yeni proje klasöründe:

```powershell
python .\scripts\audit_uhi_sources.py
```

80 dosya bulunmalı; her dosyada `UrbanId` ve `Intensity_MEA` olmalı; `UrbanId` tekrarı olmamalı. Rapor `data/audit_reports/uhi_source_inventory.csv` dosyasına yazılır. Sadece beş sample dosyasını denetlemek tam araştırmaya hazır olduğumuzu kanıtlamaz.

## 4. Şehir-ülke eşleştirmesini test et

```powershell
python .\scripts\build_city_mapping.py
python .\scripts\check_extreme_values.py
python -m unittest discover -s tests -v
python .\scripts\check_notebook_syntax.py
```

`data/processed/CityInfo_with_Country.csv` yeniden oluşturulur. Aykırı değer kontrolü yalnızca inceleme işareti üretir; hiçbir UHII değeri otomatik silinmez. Eşleşmeyen global şehirlerin ülkesi boş kalır; en yakın şehre göre ülke tahmini yapılmaz.

## 5. Projeyi Google Drive'a yükle

Yeni `urban-heat-transfer` klasörünün tamamını Google Drive'da **MyDrive** içine yükle. Klasör adını `urban-heat-transfer` olarak koru. `data/raw/UHII_dataset/` içindeki 80 CSV, Colab'ın erişebileceği bu klasörde bulunmalıdır; bu dosyalar GitHub'a commit edilmeyecektir.

## 6. Notebook'ları sırayla çalıştır

Google Colab'da Drive'daki proje klasöründen şu sırayla açıp çalıştır:

1. `notebooks/01_Phase2_Core_Final.ipynb`
2. `notebooks/02_External_Features_Final.ipynb`
3. `notebooks/03_Transfer_Experiments_Final.ipynb`

İlk notebook'un ilk hücresinde `Project directory`, `Dataset folder` ve `Outputs` yollarını gör. Beklenen `.../urban-heat-transfer/data/raw/UHII_dataset` yolu görünmüyorsa devam etme.

## 7. Gizli erişim bilgileri

`02_External_Features_Final.ipynb` için Google Colab **Secrets** bölümüne şunları ekle:

- `NASA_EARTHDATA_USERNAME`
- `NASA_EARTHDATA_PASSWORD`
- `CDS_API_KEY`

Bunları notebook hücresine, GitHub'a veya README'ye yazma. Eski draft notebook'larda erişim bilgileri görünmüş olabileceğinden, paylaşımdan önce eski erişim anahtarlarını iptal edip yenile.

## 8. Final doğrulaması

Üç notebook da tamamlandıktan sonra Colab'da yeni bir kod hücresine bunu yaz:

```python
!python /content/drive/MyDrive/urban-heat-transfer/scripts/phase2_validate_outputs.py --project-dir /content/drive/MyDrive/urban-heat-transfer
```

`GO` olmadan tam 2001–2020 sonuçlarını nihai sunma. `NO-GO` çıkarsa `outputs/phase2_outputs/audit_reports/` ve `docs/PHASE2_FINAL_AUDIT.md` dosyalarını incele. Tam veri akışının henüz çalıştırılmadığını unutma.
