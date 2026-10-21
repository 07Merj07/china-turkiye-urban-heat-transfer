# Processed reference tables

`CityInfo_with_Country.csv` is generated from the included `CityInfo.csv` and country mapping using an exact `UrbanId` join. Rebuild it with `python scripts/build_city_mapping.py`. Rows without an explicit country mapping remain blank.
