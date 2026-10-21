# Data directory map

- `raw/UHII_dataset/`: place the exact 80 `Mod2_Nig` source CSVs here locally. They are ignored by Git to avoid publishing a large raw archive.
- `sample_uhi/UHII_dataset/`: five real, explicitly labelled sample files. These do not constitute a complete 2001–2020 input set.
- `reference/CityInfo.csv`: supplied city metadata.
- `external_features/China_Turkiye_city_mapping.csv`: canonical country mapping input and location expected by the Phase 2 notebooks.
- `processed/CityInfo_with_Country.csv`: reproducibly regenerated ID-based country merge.
- `audit_reports/`: merge checks and historical audit summaries. Historical reports are not evidence that the updated Phase 2 run has passed.
